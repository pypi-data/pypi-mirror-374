import numpy as np
import pickle
from pathlib import Path
import torch
from kilosort.io import BinaryFiltered, load_ops
from .lfp import get_binary_file
from .probe import cluster_probe_channels
from .cluster_metrics import get_population
from tqdm import tqdm
from cellworld_npx.utils import bin_recording, format_behavior_data
from replay_trajectory_classification import ClusterlessClassifier, ClusterlessDecoder, Environment, RandomWalk, Uniform, Identity
import os

def group_channel_map(channel_map, n=4):
    #TODO test overlapping groups

    # group each block of channels into groups of n electrodes
    channel_blocks = cluster_probe_channels(channel_map)
    channel_groups = np.zeros(channel_blocks.shape)
    block_length = 0
    group_count = 0
    for b in np.unique(channel_blocks):
        for i,j in enumerate(range(0, (channel_blocks==b).sum(), n)):
            ind = block_length + j
            channel_groups[ind:ind+n] = i + group_count
        group_count = group_count + i + 1
        block_length = block_length + (channel_blocks==b).sum()

    # calculate group COM
    group_com = []
    for c in np.unique(channel_groups):
        group_com.append(channel_map[channel_groups==c, 1:].mean(0))
    group_com = np.vstack(group_com)

    # get four closest channels
    group_channels = []
    for i in range(group_com.shape[0]):
        group_channels.append(np.argsort(np.sum((channel_map[:,1:] - group_com[i,:]) ** 2, axis=1) ** 0.5)[0:n])
    group_channels = np.vstack(group_channels)
    return group_channels, group_com

def assign_spike_groups(spike_positions, group_com, show_progress=True):
    # assign spikes to each electrode group
    distances = np.zeros((group_com.shape[0], spike_positions.shape[0]))
    for i in tqdm(range(group_com.shape[0]), desc='assigning spikes to groups', disable=not show_progress):
        distances[i,:] = np.sum((spike_positions - group_com[i,:]) ** 2, axis=1) ** 0.5
    distances = np.vstack(distances)
    spike_group = np.nanargmin(distances, axis=0)
    return spike_group

def filter_spikes(R):
    # load aligned spikes and behavior
    spike_times, spike_clusters, clust_info = R.get_spikes()
    d = format_behavior_data(R, agent='prey')

    # remove spikes outside of episode times
    episode_times = np.vstack([R.episodes.get('start_time'), R.episodes.get('end_time')]).T
    spike_index = np.zeros(len(spike_times))
    for i in range(episode_times.shape[0]):
        spike_index = spike_index + ((spike_times > episode_times[i,0]) & 
                                    (spike_times < episode_times[i,1]) & 
                                    (spike_times < d['time_stamp'][-1]))
    return spike_times, spike_clusters, spike_index

def extract_spike_template_features(spike_positions, spike_group, amplitudes, templates, spike_templates, group_channels, n=4,
                                    show_progress=False):
    # get spike features per spike
    spike_features = np.zeros((spike_positions.shape[0], n))
    for i in tqdm(range(spike_positions.shape[0]), desc='extracting spike template features', disable=not show_progress):
        spike_features[i,:] = np.max(amplitudes[i] * templates[spike_templates[i],:,group_channels[spike_group[i],:]], axis=1)
    return spike_features

def extract_spike_amplitude_features(spike_positions, spike_group, spike_amps, group_channels, n=4, show_progress=False):
    spike_features = np.zeros((spike_positions.shape[0], n))
    for i in tqdm(range(spike_positions.shape[0]), desc='extracting spike amplitude features', disable=not show_progress):
        spike_features[i,:] = spike_amps[i, group_channels[spike_group[i]]]
    return spike_features

def get_spike_amplitudes(spike_path, show_progress=False):
    # calculate or load spike amplitudes
    results_dir = Path(spike_path)
    fn = results_dir / 'spike_amplitudes.npy'
    if not fn.exists():
        bfile = get_binary_file(spike_path, hp_filter=True, whiten=True, dshift=True)
        spike_times = np.load(results_dir / 'spike_times.npy')
        clu = np.load(results_dir / 'spike_clusters.npy')
        ops = load_ops(results_dir / 'ops.npy')
        spike_amps = np.zeros((len(spike_times), ops['n_chan_bin']))
        for i,t in tqdm(enumerate(spike_times), desc='extracting spike amplitudes', disable=not show_progress, total=len(spike_times)):
            tmin = t - bfile.nt0min
            tmax = t + (bfile.nt - bfile.nt0min) + 1
            if tmin < 0:
                tmin = 0; tmax = bfile.nt + 1
            if tmax > bfile.n_samples:
                tmax = bfile.n_samples; tmin = tmax - bfile.nt - 1
            spike_amps[i,:] = bfile[tmin:tmax].cpu().numpy()[:,ops['nt0min']].astype('float32')
        np.save(fn, spike_amps)
    else:
        if show_progress:
            print(f'loading spike amplitudes from {fn}')
        spike_amps = np.load(fn)

    return spike_amps

def get_multiunits(spike_times, spike_group, spike_features, bins, show_progress=False, check_duplicate_spikes=False):
    spike_bin = np.digitize(spike_times, bins = bins, right=True)
    ugroups = np.unique(spike_group)
    multiunits = np.zeros((len(bins), spike_features.shape[1], len(ugroups)))
    multiunits[:] = np.nan
    if check_duplicate_spikes:
        spike_counts = np.zeros((len(bins), len(ugroups)))
    for i,s in tqdm(enumerate(spike_bin), total=len(spike_bin), desc='adding spike features to multi-unit array', disable=not show_progress):
        multiunits[s-1,:,np.argwhere(ugroups == spike_group[i])] = spike_features[i,:]
        if check_duplicate_spikes:
            spike_counts[s-1, np.argwhere(ugroups == spike_group[i])] += 1
    multiunits = multiunits[:-1,:,:]
    if check_duplicate_spikes:
        return multiunits, spike_counts
    else:
        return multiunits

def get_cv_folds(n_samples, n_folds=10, return_boolean=True):
    cv_runs = []
    run_size = int(np.ceil(n_samples / n_folds))
    for i in range(n_folds):
        train_bool = np.zeros(n_samples, dtype=bool)
        train_ind = [i*run_size, 
                    np.min([(i+1)*run_size, n_samples])]
        train_bool[train_ind[0]:train_ind[1]] = True
        if not return_boolean:
            train = np.argwhere(~train_bool)
            test = np.argwhere(train_bool)
        else:
            train = ~train_bool
            test = train_bool
        cv_runs.append([train, test])
    return cv_runs

def get_spike_groups(R, ops):
    xoffset = [0, 1200]
    channel_maps = R.get_channel_map()
    channel_map = []
    spike_positions = []
    for i, path in enumerate(R.spike_path):
        map = channel_maps[i]
        map[:,1] = map[:,1] + xoffset[i]
        channel_map.append(map)
        spike_positions.append(np.load(os.path.join(path,'spike_positions.npy')) + np.array([xoffset[i], 0]))
    channel_map = np.vstack(channel_map)
    spike_positions = np.vstack(spike_positions)
    group_channels, group_com = group_channel_map(channel_map, n=ops['n'])

    return group_channels, group_com, spike_positions, channel_map


def preprocess_data(R, ops, verbose=False, use_entrance_cam=False):
    print('PREPROCESSING DATA')
    # format behavior
    # d = format_behavior_data(R, agent=ops['agents'])

    # get spike groups
    group_channels, group_com, spike_positions, channel_map = get_spike_groups(R, ops)
    spike_group = assign_spike_groups(spike_positions, group_com, show_progress=verbose)

    # get spike amplitudes (takes a while first time)
    spike_amps = []
    for p in R.spike_path:
        spike_amps.append(get_spike_amplitudes(p, show_progress=verbose))
    spike_amps = np.vstack(spike_amps)

    # # remove out-of-episode spikes
    # spike_times, spike_clusters, spike_index = filter_spikes(R)

    # get spike times
    spike_times, spike_clusters, clusters_info, spike_probe = R.get_spikes()
    spike_index = np.ones(spike_times.shape)

    # remove spikes from noise clusters
    if len(R.population) == 0:
        R.population = get_population(R.spike_path, save=False, overwrite=False)
    good_units = np.argwhere(R.population.get('good_unit'))
    print(f'including spikes from {len(good_units)} single/multi-units with good waveforms')
    good_spikes = np.zeros(spike_clusters.shape)
    for u in good_units:
        good_spikes = good_spikes + (spike_clusters == u)
    spike_index = (spike_index == 1) & (good_spikes == 1)

    # filter spikes
    spike_positions = spike_positions[spike_index == 1]
    spike_times = spike_times[spike_index == 1]
    spike_clusters = spike_clusters[spike_index == 1]
    spike_group = spike_group[spike_index == 1]
    spike_amps = spike_amps[spike_index == 1]

    # extract spike features
    spike_features = extract_spike_amplitude_features(spike_positions, spike_group, spike_amps, group_channels, show_progress=verbose)

    # create multiunit array
    #bins = np.arange(np.nanmin(d['time_stamp']) - (ops['dt']/2), np.nanmax(d['time_stamp']) + (ops['dt']/2), ops['dt'])
    bins = np.arange(np.min(spike_times) - (ops['dt']/2), np.max(spike_times) + (ops['dt']/2), ops['dt'])
    multiunits = get_multiunits(spike_times=spike_times, spike_group=spike_group, spike_features=spike_features, bins=bins, show_progress=verbose)

    # bin the recording
    if not use_entrance_cam:
        binned_data = bin_recording(R, agent=ops['agents'], dt=ops['dt'], skip_spikes=True, 
                                    kalman_filter=ops['kalman_filter'], show_progress=verbose)
    else:
        df = R.merge_entrance_pose()
        binned_data = bin_recording_df(df, bins, show_progress=verbose)
    
    # remove data where agents were not tracked
    column = [i for i in binned_data.columns if 'tracked' in i][0]
    tracked = binned_data[column]==1
    mua = multiunits[tracked,:,:]
    binned_data = binned_data[tracked]

    data = {
        'mua': mua,
        'time': np.array(binned_data['time_stamp']),
        'position': np.vstack(binned_data['prey_location']) * ops['canonical_to_cm'],
        'velocity': np.vstack(binned_data['prey_velocity']) * ops['canonical_to_cm']
    }
    return data, binned_data

def set_ops(dt=0.002, n=4, agents='prey', canonical_to_cm=234, velocity_cutoff=0.1, cv_folds=5, cv_type='fold', kalman_filter=True, bin_size=5, 
            random_walk_var=6, mark_var=24, position_var=6, drop_causal_posterior=True, states=['continuous']):
    
    # ensure correct ordering for classifier
    if 'continuous' in states and 'fragmented' in states and 'stationary' in states:
        states = ['continuous', 'fragmented', 'stationary']
    elif 'continuous' in states and 'fragmented' in states and 'stationary' not in states:
        states = ['continuous', 'fragmented']

    # options
    ops = {
        'dt': dt,                # decoding resolution (ms)
        'n': n,                     # spike features
        'agents': agents,           # agents to include
        'canonical_to_cm': canonical_to_cm,     # convert canonical units to cm
        'velocity_cutoff': velocity_cutoff,     # velocity cutoff for training (cm/s)
        'cv_folds': cv_folds,              # cross validation folds
        'cv_type': cv_type,          # cross validation type ("fold" for fold split, "speed" for speed split)
        'kalman_filter': kalman_filter,      # kalman smooth raw data
        'bin_size': bin_size,              # bin size for rate maps (cm)
        'random_walk_var': random_walk_var,       # variance of movement of transition model (cm)
        'mark_var': mark_var,             # variance of encoding model mark space (~uV)
        'position_var': position_var,           # variance of encoding model position (cm)
        'drop_causal_posterior': drop_causal_posterior,
        'states': states
    }
    return ops

def build_continuous_transitions(ops):
    state_transitions = {'continuous': RandomWalk(movement_var=ops['random_walk_var']),
                         'fragmented': Uniform(),
                         'stationary': Identity()}
    if 'continuous' in ops['states'] and 'fragmented' in ops['states'] and 'stationary' in ops['states']:
        return [
            [RandomWalk(movement_var=ops['random_walk_var']), Uniform(), Identity()],
            [Uniform(), Uniform(), Uniform()],
            [RandomWalk(movement_var=ops['random_walk_var']), Uniform(), Identity()],
            ]
    elif 'continuous' in ops['states'] and 'fragmented' in ops['states'] and 'stationary' not in ops['states']:
        return [
            [RandomWalk(movement_var=ops['random_walk_var']), Uniform()],
            [Uniform(), Uniform()]
            ]
    elif len(ops['states']) == 1:
        return state_transitions[ops['states'][0]]
    else:
        raise AssertionError("ops['states'] must be ['continuous', 'fragmented', 'stationary'], ['continuous', 'fragmented'] or ['continuous'], ['fragmented'], or ['stationary']")
    
def run_decoder(data, ops):
    print('TRAIN/TEST DECODER')
    # cross validation
    if ops['cv_type'] == 'speed':
        # define training and testing index
        moving = np.argwhere(data['velocity'].squeeze() > ops['velocity_cutoff'])
        train = moving[0:int(len(moving)/2)].copy().squeeze()
        test = moving[int(len(moving)/2):].copy().squeeze()
        cv_runs = [train, test]
    else:
        cv_runs = get_cv_folds(data['position'].shape[0], ops['cv_folds'])

    # model setup
    lims = (ops['canonical_to_cm']*0.05, ops['canonical_to_cm']*1.05)
    environment = Environment(place_bin_size=ops['bin_size'], position_range=[lims,lims])
    assert len(ops['states']) == 1, f'For standard decoding there must be one state, not {ops["states"]}, try run_classifier instead...'
    transition_type = build_continuous_transitions(ops)
    clusterless_algorithm = 'multiunit_likelihood_gpu'
    clusterless_algorithm_params = {
        'mark_std': ops['mark_var'],
        'position_std': ops['position_var']
        }
    
    # cv loop
    decoders = []
    results = []
    for fold in tqdm(cv_runs, desc='cross-validation fold'):
        decoder = ClusterlessDecoder(
            environment=environment,
            transition_type=transition_type,
            clusterless_algorithm=clusterless_algorithm,
            clusterless_algorithm_params=clusterless_algorithm_params)

        decoder.fit(data['position'][fold[0],:], data['mua'][fold[0],:,:])
        decoders.append(decoder)

        result = decoder.predict(data['mua'][fold[1],:,:], time=data['time'][fold[1]], use_gpu=True)
        results.append(result)

    # compile across runs
    map_estimate = []
    for r in results:
        post = r.acausal_posterior.stack(position=['x_position', 'y_position'])
        map = post.position[post.argmax('position')]
        map = np.asarray(map.values.tolist())
        map_estimate.append(map)
    map_estimate = np.vstack(map_estimate)
    error = np.linalg.norm(map_estimate - data['position'], axis=1)
    result = {
        'dist_error': error,
        'map_estimate': map_estimate,
        'cv_results': {'decoders': decoders, 'results': results}
        }

    return result

def run_classifier(data, ops, drop_causal_posterior=True):
    print('TRAIN/TEST CLASSIFIER')
    # cross validation
    if ops['cv_type'] == 'speed':
        # define training and testing index
        moving = np.argwhere(data['velocity'].squeeze() > ops['velocity_cutoff'])
        train = moving[0:int(len(moving)/2)].copy().squeeze()
        test = moving[int(len(moving)/2):].copy().squeeze()
        cv_runs = [train, test]
    else:
        cv_runs = get_cv_folds(data['position'].shape[0], ops['cv_folds'])

    # model setup
    environment = Environment(place_bin_size=ops['bin_size'], 
                                position_range=[(0,ops['canonical_to_cm']),(0,ops['canonical_to_cm'])])
    continuous_transition_types = build_continuous_transitions(ops)
    if len(ops['states']) == 1:
        continuous_transition_types = [[continuous_transition_types]]
    clusterless_algorithm = 'multiunit_likelihood_gpu'
    clusterless_algorithm_params = {
        'mark_std': ops['mark_var'],
        'position_std': ops['position_var']
        }

    classifiers = []
    results = []
    for fold in tqdm(cv_runs, desc='cross-validation fold'):
        classifier = ClusterlessClassifier(
            environments=environment,
            continuous_transition_types=continuous_transition_types,
            clusterless_algorithm=clusterless_algorithm,
            clusterless_algorithm_params=clusterless_algorithm_params)
        classifier.fit(data['position'][fold[0],:], data['mua'][fold[0],:,:])
        classifiers.append(classifier)

        result = classifier.predict(data['mua'][fold[1],:,:], time=data['time'][fold[1]], use_gpu=True)
        result['state'] = ops['states']
        if drop_causal_posterior:
            result.drop('causal_posterior')
        results.append(result)
    
    map_estimate = []
    for r in results:
        post = r.acausal_posterior.sum('state').stack(position=['x_position', 'y_position'])
        map = post.position[post.argmax('position')]
        map = np.asarray(map.values.tolist())
        map_estimate.append(map)
    map_estimate = np.vstack(map_estimate)
    error = np.linalg.norm(map_estimate - data['position'], axis=1)
    result = {
        'dist_error': error,
        'map_estimate': map_estimate,
        'cv_results': {'classifiers': classifiers, 'results': results}
        }

    return result

def save_results(fn, result_list:list):
    with open(fn, 'wb') as fid:
        for r in result_list:
            pickle.dump(r, fid)

























# ## misc plotting stuff
def plot_spike_group(group, 
                     spike_group, 
                     spike_probe, 
                     spike_clusters, 
                     spike_positions, 
                     channel_map, 
                     group_channels, 
                     group_com, 
                     window=250):
    probe = np.unique(spike_probe[spike_group==group])[0]
    I = (spike_group == group) & (spike_probe == probe)
    clusters = np.unique(spike_clusters[I])

    plt.plot(channel_map[:,1], channel_map[:,2], 'k.')
    plt.plot(channel_map[group_channels[group,:],1], channel_map[group_channels[group,:],2], 'o')
    for c in clusters:
        plt.plot(spike_positions[I & (spike_clusters==c),0], spike_positions[I & (spike_clusters==c),1], '.', markersize=1)
    plt.xlim(group_com[group,0] - window, group_com[group,0] + window)
    plt.ylim(group_com[group,1] - window, group_com[group,1] + window)
