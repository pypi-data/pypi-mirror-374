from .coverage import *
from .celltile import *
from .cluster_metrics import Cluster
from .probe import get_channel_map, get_probe_sites
from .kalman import kalman_smoother, get_velocity
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.collections import LineCollection
from cellworld import *
from astropy.convolution import convolve
import os
import torch
from scipy.ndimage import gaussian_filter
from scipy.stats import binned_statistic
import pandas as pd
from tqdm import tqdm

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'
np.seterr(divide='ignore', invalid='ignore')

## general functions
def distance(x, y=None, axis=1):
    if y is None:
        return np.linalg.norm(np.diff(x, axis=0), axis=axis)
    else:
        if len(x.shape) < 2:
            x = x[np.newaxis,:]
        assert x.shape[1] == y.shape[1], 'x and y have same number of columns'
        return np.linalg.norm(x - y, axis=axis)
    
def normalize(x, axis=0):
    return (x - np.nanmean(x, axis=axis)) / np.nanstd(x, axis=axis)

def convert_angle(weird_angle):
    '''
    converts cellworld rotation value to normal angle in left-hand coordinate system
    '''
    normal_angles = (90 - weird_angle) % 360
    normal_angles[normal_angles > 180] -= 360
    return normal_angles
# print(convert_angle(np.array([135,180, 270, 0, -10])))

def clean_df_locations(df):
    for c in df.columns:
        if 'location' in c:
            locs = np.vstack(df[c])
            if locs.shape[-1] == 2:
                df[f'{c}_x'] = locs[:,0]
                df[f'{c}_y'] = locs[:,1]
                df.drop(c, axis=1, inplace=True)
    return df


## binning and formatting
def bin_recording(R, dt=0.05, agent='prey', cell_index=None, skip_spikes=False, 
                  kalman_filter=False, show_progress=False, remove_missing_data=True):
    d = format_behavior_data(R, agent=agent, kalman_filter=kalman_filter, show_progress=show_progress)

    # if dt is less than original sampling rate, do interpolation for behavioral data
    mode = 'bin'
    if dt < np.median(np.diff(d['time_stamp'])):
        mode = 'interpolate'
    
    # for each field, bin or interpolate as appropriate
    # ***NOTE: if there is no data in a binned interval and mode=='bin', those frames will be all NaNs
    bins = np.arange(np.nanmin(d['time_stamp']) - (dt/2), np.nanmax(d['time_stamp']) + (dt/2), dt)
    b = {k: [] for k in d.keys()}
    for k in tqdm(d.keys(), disable=not show_progress, desc='binning recording'):
        d[k] = np.array(d[k])
        if (len(d[k].shape) == 1) & (d[k].shape[0] > 0):
            if 'bin' in mode:
                b[k],_,_ = binned_statistic(d['time_stamp'], d[k], bins = bins)
            else:
                b[k] = np.interp(bins[:-1] + dt/2, d['time_stamp'], d[k])
            b[k] = b[k].tolist()
        elif len(d[k].shape) == 2:
            tmp = []
            for i in range(d[k].shape[1]):
                if 'bin' in mode:
                    out,_,_ = binned_statistic(d['time_stamp'], d[k][:,i].squeeze(), bins = bins)
                else:
                    out = np.interp(bins[:-1] + dt/2, d['time_stamp'], d[k][:,i].squeeze())
                tmp.append(out)
            b[k] = np.vstack(tmp).T.tolist()
        else:
            b.pop(k, None)

    if not skip_spikes:
        # bin spikes
        if cell_index is None:
            cell_index = R.clusters_info.KSLabel == 'good'
        good_cells = R.clusters_info[cell_index].cluster_id.values
        spike_times = []
        for u in good_cells:
            spike_times.append(np.array(R.spike_times[R.clusters == u]))
        b['neural_data'] = bin_spikes(spike_times, dt, bins[0], bins[-1])
        if (len(b['neural_data']) - len(b['time_stamp'])) == 1:
            b['neural_data'] = b['neural_data'][:-1,:]
        b['neural_data'] = b['neural_data'].tolist()
        [print(k, len(b[k])) for k in b.keys()]

    return pd.DataFrame.from_dict(b)

def bin_output(outputs, output_times, dt, wdw_start, wdw_end, downsample_factor=1):

    # Downsample output
    # We just take 1 out of every "downsample_factor" values
    if downsample_factor != 1: #Don't downsample if downsample_factor=1
        downsample_idxs = np.arange(0, output_times.shape[0], downsample_factor) #Get the idxs of values we are going to include after downsampling
        outputs = outputs[downsample_idxs,:] #Get the downsampled outputs
        output_times = output_times[downsample_idxs] #Get the downsampled output times

    # Put outputs into bins
    edges = np.arange(wdw_start, wdw_end, dt) #Get edges of time bins
    num_bins = edges.shape[0]-1 #Number of bins
    output_dim = outputs.shape[1] #Number of output features
    outputs_binned = np.empty([num_bins,output_dim]) #Initialize matrix of binned outputs
    #Loop through bins, and get the mean outputs in those bins
    for i in range(num_bins): #Loop through bins
        idxs = np.where((np.squeeze(output_times)>=edges[i]) & (np.squeeze(output_times)<edges[i+1]))[0] #Indices to consider the output signal (when it's in the correct time range)
        for j in range(output_dim): #Loop through output features
            outputs_binned[i,j] = np.nanmean(outputs[idxs,j])

    return outputs_binned

def bin_spikes(spike_times, dt, wdw_start, wdw_end):
    edges = np.arange(wdw_start-dt/2, wdw_end+dt/2, dt) #Get edges of time bins
    num_bins = edges.shape[0]-1 #Number of bins
    num_neurons = len(spike_times) #Number of neurons
    neural_data = np.empty([num_bins,num_neurons]) #Initialize array for binned neural data
    #Count number of spikes in each bin for each neuron, and put in array
    for i in range(num_neurons):
        neural_data[:,i] = np.histogram(spike_times[i], edges)[0]
    #print(neural_data.shape)
    return neural_data



## NPX plotting
def plot_waveforms(dp, u, Nchannels=16, color='tab:blue', scalerx=5, scalery=10, ax=None, type='template', individual=True):

    if ax is None:
        _,ax = plt.subplots(1,1,figsize=(5,7))

    # get waveforms, peak channel
    c = Cluster(dp, u, type=type)
    if (type == 'waveform') & individual:
        c.plot_waveforms(N = Nchannels, color=color, scalerx=scalerx, scalery=scalery, ax=ax)
    else:
        c.plot_cluster(N = Nchannels, color=color, scalerx=scalerx, scalery=scalery, ax=ax)

def plot_probe(dp, ax=None, plot_full_probe='', **kwargs):
    if ax is None:
        _,ax = plt.subplots(1,1,figsize=(5,7))

    #cm = chan_map(dp, y_orig='tip', probe_version='local')
    if plot_full_probe != '':
        if '1' in plot_full_probe:
            offset = 11
        elif '2' in plot_full_probe:
            offset = 8
        else:
            raise ValueError('probe type must be np1/np2')
        x, y, _ = get_probe_sites(type=plot_full_probe, x_offset=offset)
        ax.scatter(x, y, 1, 'grey')
    cm = get_channel_map(os.path.join(dp, '..', '..', 'settings.xml'))
    ax.scatter(cm[:,1], cm[:,2], 1, 'k', **kwargs)
    ax.set_aspect(0.25)
    ax.set_xlim((cm[:,1].min()-50, cm[:,1].max()+50))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    return cm

def plot_unit_loc(dp, u, Nchannels=16, color='tab:blue', ax=None, plot_amp=False, scale=1, type='template', plot_full_probe='', units='um'):
    if ax is None:
        _,ax = plt.subplots(1,1,figsize=(5,10))

    plot_probe(dp, ax=ax, plot_full_probe=plot_full_probe)

    # get waveform
    #waveforms = wvf(dp, u, 300, selection='regular', periods='all')
    c = Cluster(dp, u, type='template')
    waveforms = c.waveforms
    _, n_samples, n_channels = waveforms.shape
    peak_chan_i = np.argmax(np.ptp(waveforms.mean(0), axis=0))
    chStart_i = int(max(peak_chan_i-Nchannels//2, 0))
    chStart_i=int(min(chStart_i, n_channels-Nchannels-1))
    chEnd_i = int(chStart_i+Nchannels) # no lower capping needed as
    assert chEnd_i <= n_channels-1
    chanI = np.arange(chStart_i,chEnd_i)
    data = waveforms[:, :, chStart_i:chEnd_i]

    # get channel map
    #cm=chan_map(dp, y_orig='tip', probe_version='local')
    cm = get_channel_map(os.path.join(dp, '..', '..', 'settings.xml'))
    cm = cm[0:n_channels:]

    amps = np.mean(data,0).max(0) * scale
    ax.scatter(cm[chanI,1], cm[chanI,2], amps, color, alpha=0.75)

    if plot_amp:
        amp_plt = np.max(cm[:,1]) + 20 + (np.mean(waveforms,0).max(0)[0:n_channels] * scale)
        #amp_plt = (amp_plt - amp_plt.min()) / (amp_plt.max() - amp_plt.min()) * 100
        ax.plot(amp_plt, cm[:,2], '.', markersize=2, color=color)
        ax.set_xlim((cm[:,1].min()-20, amp_plt.max()*1.1))
    
    if units == 'mm':
        ax.set_yticklabels([str(int(l/1000)) for l in ax.get_yticks()])


def plot_autocorr(dp, u, cbin=1.0, cwin=100, color='tab:blue', ax=None):
    if ax is None:
        _,ax = plt.subplots(1,1)
    c = Cluster(dp, u, type='template')
    ax = c.plot_acg(color=color, bin=cbin, range=cwin, ax=ax)
    return ax

def plot_cell(dp, u, title='', figsize=(15,10)):
    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(2, 3, width_ratios=[1, 1, 0.5])
    ax0 = plt.subplot(gs[:,0])
    ax1 = plt.subplot(gs[:,1])
    ax2 = plt.subplot(gs[-1])
    plot_unit_loc(dp, u, Nchannels=64, ax=ax0, plot_amp=True)
    plot_waveforms(dp, u, ax=ax1)
    plot_autocorr(dp, u, ax=ax2, figsize=figsize)
    ax2.set_title(title)
    return fig

def cell_title(u, clust_info, fields=['ch', 'depth', 'fr', 'n_spikes', 'KSLabel', 'spatial_decay', 
                                      'spike_width', 'spike_duration', 'waveform_snr', 'presence_ratio', 
                                      'refractory_violations', 'isi_violations', 'good_unit']):
    I = np.where(clust_info.cluster_id == u)[0][0]
    row = clust_info.iloc[I]
    title = [f"cell ID: {row.cluster_id} (index {I})\n"]
    for f in fields:
        if type(row[f]) is str:
            title.append(f"{f}: {row[f]}\n")
        else:
            title.append(f"{f}: {row[f]:3.2f}\n")
    return ''.join(title)





## rate map calculations
def compute_rate_map(spike_times, frame_times, location, occupancy, bins, smooth=None):
    #pos_i = np.digitize(spike_times, frame_times[:-1], right=False)
    pos_i = np.searchsorted(frame_times[:-1], spike_times)
    spike_count = get_histogram2(location[pos_i,0].squeeze(), location[pos_i,1].squeeze(), bins)
    spike_count[occupancy == 0] = 0
    rate_map = spike_count / occupancy
    if smooth is None:
        return rate_map
    else:
        mask = np.isnan(rate_map)
        rate_map[mask] = 0
        rate_map = gaussian_filter(rate_map, sigma=smooth)
        rate_map[mask] = np.nan
        return rate_map

def filter_spikes(spike_times, video_times, clust=[]):
    spikes = []
    if len(clust) > 0:
        clusters = []
    for e in range(video_times.shape[0]):
        I = (spike_times > video_times[e,0]) & (spike_times < video_times[e,1])
        spikes.append(spike_times[I])
        if len(clust) > 0:
            clusters.append(clust[I.squeeze()].squeeze())
    spike_times = np.hstack(spikes)
    if len(clust) > 0:
        clust = np.hstack(clusters)
        return spike_times, clust
    else:
        return spike_times
    
def get_spike_histogram(spike_times, frame_times, include, dt=0.001, use_cuda=False):
    t = np.arange(np.min(frame_times[include]), np.max(frame_times[include]), dt)
    incl = np.interp(t, frame_times, include) > 0.2
    tbins = np.append(t - (dt/2), t[-1] + (dt/2))

    if use_cuda:
        t = torch.from_numpy(t).to(torch.device("cuda:0"))
        incl = torch.from_numpy(incl).to(torch.device("cuda:0"))
        tbins = torch.from_numpy(tbins)
        spikec,_ = torch.histogram(torch.from_numpy(spike_times), bins=tbins)
        spikec = spikec.int().to(torch.device("cuda:0"))
    else:
        spikec,_ = np.histogram(spike_times, bins=tbins)

    return spikec, t, incl

def get_spike_times_from_histogram(spikec, t, use_cuda=False):
    if use_cuda:
        return torch.repeat_interleave(t[spikec > 0], spikec[spikec > 0])
    else:
        return np.repeat(t[spikec > 0], spikec[spikec > 0])

def shift_spiketimes_fast(spike_counts, t, incl, min_shift=5, max_shift=None, dt=None):
    if dt is None:
        dt = (t[-1] - t[0]) / len(t)
    if max_shift is None:
        max_shift = torch.max(t) / 2
    shift = min_shift + torch.randint(low=0, high=int(np.floor(max_shift*1000)), size=(1,1)) / 1000
    sf = spike_counts[incl == 1]; tf = t[incl == 1]
    shiftf = torch.roll(sf, int(shift/dt))
    return get_spike_times_from_histogram(shiftf, tf, use_cuda=True)
    

def shuffle_spiketimes(spike_times, epochs):
    shuffled = []
    assert (len(epochs.shape) == 2) & (epochs.shape[1] == 2), 'ERROR: epochs must be a 2D array with two columns!'
    for i in range(epochs.shape[0]):
        ep_start = epochs[i,0]
        ep_end = epochs[i,1]
        ep_spikes = spike_times[(spike_times >= ep_start) & (spike_times < ep_end)]
        if len(ep_spikes) > 0:
            ep_spikes0 = ep_spikes - ep_start
            ep_duration = ep_end - ep_start
            shuff_spikes = (ep_spikes0 + 5 + np.random.randint(0, np.floor(ep_duration*1000)) / 1000) % ep_duration
            shuff_spikes = shuff_spikes + ep_start
            shuff_spikes.sort()
            assert (~np.any(shuff_spikes < ep_start) & ~np.any(shuff_spikes > ep_end)), 'ERROR: spikes were shuffled outside of epoch boundaries!'
            shuffled.extend(shuff_spikes)
    return shuffled

def shannon_information(rate_map, occupancy, mfr=None, normalize=True, warn=False):
    '''
    shannon_information(rate_map, occupancy, normalize=False)

    calculates the shannon information of a rate map given the occupancy (p(observation)) per bin
    - rate_map: firing rates per bin
    - occupancy: probability of observing the agent in each bin (should sum to 1)
    - mfr: mean firing rate (Hz) of the cell
    - normalization (optional): if False (default), it will return information in bits/s
                                if True, it will return information in bits/spike
    '''
    occ = occupancy / np.nansum(occupancy) # occupancy sums to 1
    if not mfr:
        mfr = np.nansum(rate_map * occ) # mean firing rate according to Skaggs, 1992
    log = np.log2(rate_map / mfr)
    info = np.nansum(rate_map * occ * log)
    if normalize:
        info = info / mfr
    if warn & (info < 0):
        print('WARNING: information less than 0')
    return info, mfr


def spatial_info_perm(spike_times, frame_times, location, occupancy, bins, video_times, 
                      its=500, sig=95, normalize=True, occupancy_cutoff=0.0, mask=None):
    rate_map = compute_rate_map(spike_times, frame_times, location, occupancy, bins)
    occ_mask = (occupancy < occupancy_cutoff) & (occupancy > 0)
    rate_map[occ_mask] = 0
    occupancy[occ_mask] = 0
    if mask is not None:
        rate_map[mask.reshape(rate_map.shape)] = np.nan
        occupancy[mask.reshape(occupancy.shape)] = np.nan
    mean_firing_rate = np.nansum(rate_map * (occupancy / np.nansum(occupancy)))
    true_SI, _ = shannon_information(rate_map, occupancy, mfr=mean_firing_rate, normalize=normalize)

    shuff_SI = []
    shuff_map = []
    for i in range(its):
        shuff_spikes = shuffle_spiketimes(spike_times, video_times)
        rate_map_shuff = compute_rate_map(shuff_spikes, frame_times, location, occupancy, bins)
        ssi, _ = shannon_information(rate_map_shuff, occupancy, mfr=mean_firing_rate, normalize=normalize)
        shuff_SI.append(ssi)
        shuff_map.append(rate_map_shuff)

    percentile = np.percentile(shuff_SI, sig)
    percentile_map = np.percentile(np.stack(shuff_map, axis=2), sig, axis=2)
    return true_SI > percentile, true_SI, shuff_SI, rate_map, mean_firing_rate, percentile_map


def spatial_info_fast(spike_times, frame_times, include, location, occupancy, bins, 
                      its=500, sig=95, normalize=True, occupancy_cutoff=0.0, mask=None, smooth=None, return_shuffle=False):
    spikec, t, incl = get_spike_histogram(spike_times, frame_times, include, dt=0.001, use_cuda=True)
    if spikec[incl].sum() <= 1: # randomly add two spikes with 1 or fewer spikes
        included = np.where(incl.to('cpu')==1)[0]
        I = included[np.random.randint(0, len(included), 2)] 
        spikec[I] = 1
    spiket = get_spike_times_from_histogram(spikec[incl], t[incl], use_cuda=True)
        
    times = frame_times[include]
    rate_map = compute_rate_map(spiket.to('cpu'), times, location, occupancy, bins, smooth=smooth)
    occ_mask = (occupancy < occupancy_cutoff) & (occupancy > 0)
    rate_map[occ_mask] = 0
    occupancy[occ_mask] = 0
    if mask is not None:
        rate_map[mask.reshape(rate_map.shape)] = np.nan
        occupancy[mask.reshape(occupancy.shape)] = np.nan
    mean_firing_rate = np.nansum(rate_map * (occupancy / np.nansum(occupancy)))
    true_SI, _ = shannon_information(rate_map, occupancy, mfr=mean_firing_rate, normalize=normalize)

    shuff_SI = []
    shuff_map = []
    min_shift = 5
    max_shift = int(np.floor(frame_times[-1] - frame_times[0])) - min_shift
    for i in range(its):
        shuff_spikes = shift_spiketimes_fast(spikec, t, incl, dt=0.001, min_shift=min_shift, max_shift=max_shift)
        rate_map_shuff = compute_rate_map(shuff_spikes.to('cpu'), times, location, occupancy, bins, smooth=smooth)
        ssi, _ = shannon_information(rate_map_shuff, occupancy, mfr=mean_firing_rate, normalize=normalize)
        shuff_SI.append(ssi)
        shuff_map.append(rate_map_shuff)

    percentile = np.percentile(shuff_SI, sig)
    percentile_map = np.percentile(np.stack(shuff_map, axis=2), sig, axis=2)
    if return_shuffle:
        return true_SI > percentile, true_SI, shuff_SI, rate_map, mean_firing_rate, percentile_map, shuff_map
    else:
        return true_SI > percentile, true_SI, shuff_SI, rate_map, mean_firing_rate, percentile_map
    
def check_shuffled_spikes(spike_times, frame_times, include):
    spikec, t, incl = get_spike_histogram(spike_times, frame_times, include, dt=0.001, use_cuda=True)
    if spikec[incl].sum() <= 1: # randomly add two spikes with 1 or fewer spikes
        included = np.where(incl.to('cpu')==1)[0]
        I = included[np.random.randint(0, len(included), 2)] 
        spikec[I] = 1
    shuff_spikes = shift_spiketimes_fast(spikec, t, incl, dt=0.001, min_shift=5, max_shift=500)

def get_epochs(x, t, start=None):
    assert len(x) == len(t), f'x must be same length as t'
    if start is None:
        x = np.append(x[0], x)
    else:
        x = np.append(start, x)
    starts = np.argwhere(np.diff(x.astype('int')) > 0).flatten()
    ends = np.argwhere(np.diff(x.astype('int')) < 0).flatten()
    starts, ends = clean_events(starts, ends)
    return np.vstack((t[starts], t[ends])).T

def get_tracked_frames(frames, cutoff=0.05):
    epochs = (np.diff(np.hstack((0, frames, np.inf))) > cutoff).astype(int)
    onsets = np.argwhere(np.diff(epochs) < 0).flatten()
    offsets = np.argwhere(np.diff(epochs) > 0).flatten()
    plt.plot(np.diff(np.hstack((0, frames, np.inf))))
    onsets, offsets = clean_events(onsets, offsets)
    return np.hstack((frames[onsets], frames[offsets])), np.diff(np.hstack((frames[0], frames))) < cutoff



## behavior processing
def align_agents(R, cutoff=0.01):
    data = R.trajectory_dict.copy()
    agents = ('prey', 'predator')
    index = {'prey': [], 'predator': []}
    timestamps = {'prey': np.sort(data['prey']['time_stamp']),
             'predator': np.sort(data['predator']['time_stamp'])}
    times = np.array([len(timestamps['prey']), len(timestamps['predator'])])
    agents = np.array(agents)[np.where((times / np.sum(times)) > cutoff)[0]]
    if len(agents) == 2:
        _, index['prey'], index['predator'] = np.intersect1d(timestamps['prey'], timestamps['predator'], return_indices=True)
    else:
        index[agents[0]] = np.arange(len(data[agents[0]]['velocity']))
        tracked = get_agent_tracked(data[agents[0]]['time_stamp'])
        tracked[tracked == 0] = np.nan
        data[agents[0]]['visible'] = tracked
    d = {'time_stamp': [], 'episode': [], 'visible': [], 
        'prey_location': [], 'prey_velocity': [], 
        'predator_location': [], 'predator_velocity': [],
        'prey_tracked': [], 'predator_tracked': []}
    for k in ('time_stamp', 'episode', 'visible'):
        tmp = []
        for agent in agents:
            tmp.append(data[agent][k][index[agent]])
        assert np.sum(np.diff(np.vstack(tmp),axis=0)) == 0, f'Detected a difference in pred/prey {k}'
        d[k] = tmp[0].squeeze()
    for agent in agents:
        d[f'{agent}_location'] = data[agent]['location'][index[agent]]
        d[f'{agent}_velocity'] = data[agent]['velocity'][index[agent]].squeeze()
        d[f'{agent}_tracked'] = get_agent_tracked(timestamps[agent][index[agent]])
    return d

def align_episode_agents(ep=Episode, cutoff=0.01):
    agents = ('prey', 'predator')
    index = {'prey': [], 'predator': []}
    trajectories = {'prey': ep.where('agent_name', 'prey'),
                    'predator': ep.where('agent_name', 'predator')}
    timestamps = {
        'prey': np.sort(np.array(trajectories['prey'].get('time_stamp'))),
        'predator': np.sort(np.array(trajectories['predator'].get('time_stamp')))
        }
    times = np.array([len(timestamps['prey']), len(timestamps['predator'])])
    agents = np.array(agents)[np.where((times / np.sum(times)) > cutoff)[0]]
    if len(agents) == 2:
        _, index['prey'], index['predator'] = np.intersect1d(timestamps['prey'], timestamps['predator'], return_indices=True)
    else:
        # align to prey by default
        index[agents[0]] = np.arange(len(timestamps[agents[0]]))
        tracked = get_agent_tracked(timestamps[agents[0]])
        tracked[tracked == 0] = np.nan
    d = {'time_stamp': [], 'frame': [], 
        'prey_location': [], 'predator_location': [],
        'prey_tracked': [], 'predator_tracked': []}
    for k in ('time_stamp', 'frame'):
        tmp = []
        for agent in agents:
            tmp.append(np.array(trajectories[agent].get(k)))
        assert np.sum(np.diff(np.vstack(tmp),axis=0)) == 0, f'Detected a difference in pred/prey {k}'
        d[k] = tmp[0].squeeze()
    for agent in agents:
        d[f'{agent}_location'] = np.array(trajectories[agent].get('location'))[index[agent]]
        d[f'{agent}_tracked'] = get_agent_tracked(timestamps[agent][index[agent]])
    return d

def format_behavior_data(R, agent='prey', kalman_filter=False, show_progress=False):
    if agent == 'both':
        d = align_agents(R)
        agent_present = [len(d[f'{a}_location']) for a in ('prey', 'predator')]
        assert (agent_present[0] > 0) | (agent_present[1] > 0), 'no agent data detected'
        agents = ('prey', 'predator')
        for i,a in enumerate(agent_present):
            if a == 0:
                print(f'Specified both agents but agent {agents[i]} not found... removing.')
                del d[f'{agents[i]}_location']; del d[f'{agents[i]}_velocity']

    else:
        assert (agent == 'prey') | (agent == 'predator'), f'agent must be prey or predator'
        d = R.trajectory_dict[agent].copy()
        d[f'{agent}_location'] = d.pop('location')
        d[f'{agent}_velocity'] = d.pop('velocity')
        d[f'{agent}_tracked'] = get_agent_tracked(d['time_stamp'])
        del d['occupancy']; del d['coverage']; del d['bins']; del d['fps']
    if kalman_filter:
        agents = [k.split('_')[0] for k in d.keys() if 'location' in k]
        for agent in agents:
            tracking_epochs = get_epochs(d[f'{agent}_tracked'], d['time_stamp'])
            for e in tqdm(range(tracking_epochs.shape[0]), disable=not show_progress, desc=f'kalman filtering {agent}'):
                I = (d['time_stamp'] >= tracking_epochs[e,0]) & (d['time_stamp'] < tracking_epochs[e,1])
                time = d['time_stamp'].squeeze()[I]
                locs = d[f'{agent}_location'][I,:]
                xs = kalman_smoother(locs, time)
                d[f'{agent}_location'][I,:] = xs
                d[f'{agent}_velocity'][I] = get_velocity(xs, time)
    return d

def get_agent_tracked(t, dt_cutoff=0.2, min_samps=3):
    ts = np.hstack((0,t,np.inf))
    I = (np.diff(ts) < dt_cutoff).astype(int)
    starts = np.where(np.diff(I) > 0)[0]
    stops = np.where(np.diff(I) < 0)[0]
    tracked = np.zeros(t.shape)
    for i in range(len(starts)):
        if stops[i] - starts[i] > min_samps:
            tracked[starts[i]:stops[i]] = 1
    return tracked

def interpolate_short_nans(arr, max_run_length=2, max_delta=np.inf):
    arr = np.array(arr).copy()
    is_nan = np.isnan(arr)
    
    # Identify runs of NaNs
    padded = np.pad(is_nan.astype(int), (1, 1), mode='constant')
    diff = np.diff(padded)

    starts = np.where(diff == 1)[0]
    ends   = np.where(diff == -1)[0]

    for start, end in zip(starts, ends):
        run_length = end - start
        if run_length <= max_run_length:
            # Check boundary conditions
            if start > 0 and end < len(arr):
                left_val = arr[start - 1]
                right_val = arr[end]
                if not np.isnan(left_val) and not np.isnan(right_val):
                    if abs(right_val - left_val) <= max_delta:
                        arr[start:end] = np.interp(
                            np.arange(start, end),
                            [start - 1, end],
                            [left_val, right_val]
                        )
    return arr

def get_outliers_index(x, threshold = 2):
  if threshold <= 0:
      raise ArithmeticError("threshold parameter should be > 0")
  threshold = sum(x)/len(x) * threshold
  last = x[0]
  outliers_index = []
  for i,v in enumerate(x):
      if abs(v-last) <= threshold:
          last = v
      else:
          outliers_index.append(i)
  return outliers_index


def nan_convolve(x, win=11):
    return convolve(x, np.ones(win)/win)


def clean_velocity(v, outlier_threshold = 2, win = int()):
    o = get_outliers_index(v, outlier_threshold)
    v_clean = np.array(v)
    v_clean[o] = np.nan
    if win:
        v_clean = convolve(v_clean, np.ones(win)/win)
    return v_clean

def get_world(world):
    assert world is not None, 'world must be a string or World object'
    if type(world) is str:
        return World.get_from_parameters_names('hexagonal', 'canonical', world)
    else:
        return world

def get_unique_frames(episode):
    return np.unique(episode.trajectories.get('frame'), return_index=True)

def clean_episode_tracking(episode, threshold_distance=0.25):
    agent_trajectory = episode.trajectories.get_agent_trajectory('prey')
    error_count = 0
    last_good_location = agent_trajectory[0].location
    flag = False
    bad_frames = []
    clean_trajectory = Trajectories()
    for i,step in enumerate(episode.trajectories):
        if step.agent_name == 'prey':
            dist = last_good_location.dist(step.location)
            if dist > threshold_distance:
                error_count = error_count + 1
                bad_frames.append(i)
                # print(i, step.frame, dist, error_count, last_good_location)
            else:
                clean_trajectory.append(step)
                error_count = 0
                last_good_location = step.location
        else:
            clean_trajectory.append(step)
    episode.trajectories = clean_trajectory

    return episode

def bad_episode_tracking(episode, threshold_distance = 0.1, agent_name = 'prey'):
    agent_trajectory = episode.trajectories.get_agent_trajectory(agent_name)
    last_location = None
    flag = False
    for i,step in enumerate(agent_trajectory):
        if last_location is not None:
            if last_location.dist(step.location) > threshold_distance:
                print(i, last_location.dist(step.location),)
                flag = True
                break
        last_location = step.location
    return flag

def clean_episode_timestamps(episode):
    frames = episode.trajectories.get('frame')
    dt = episode.trajectories.get('time_stamp')[1] - episode.trajectories.get('time_stamp')[0]
    if dt < 0:
        episode.trajectories[0].time_stamp = 0
    if frames[0] > 0:
        last_frame = frames[0]
        for i,step in enumerate(episode.trajectories):
            if step.frame == last_frame:
                episode.trajectories[i].frame = 0
            else:
                break
    return episode

def episode_to_dataframe(episode, world=None, number=np.nan, interpolate=False, smooth=False):
    # setup
    u_frames, ind = get_unique_frames(episode)
    df = pd.DataFrame(index=u_frames, columns=['time_stamp', 'episode', 'visible',
                            'prey_location', 'prey_velocity',
                            'predator_location', 'predator_velocity'])
    df.index.name = 'frame'
    df['episode'] = [number for i in range(len(df))]
    df['time_stamp'] = np.array(episode.trajectories.get('time_stamp'))[ind]

    # add captures
    captures = [np.argmin(np.abs(u_frames - c)) for c in episode.captures]
    df['captures'] = False
    df['captures'].iloc[captures] = True

    # add rewards
    rewards = [np.argmin(np.abs(df['time_stamp'] - r)) for r in episode.rewards_time_stamps]
    reward_id = np.nan
    if len(episode.rewards_sequence) > 0:
        reward_id = episode.rewards_sequence[0]
    df['reward_id'] = reward_id
    df['reward_location'] = [[np.nan, np.nan] for i in range(len(df))]
    if world and (len(episode.rewards_sequence) > 0):
        df['reward_location'] = [[world.cells[reward_id].location.x, 
                                 world.cells[reward_id].location.y] for i in range(len(df))]
    df['rewards'] = False
    if len(rewards) > 0:
        df['rewards'].iloc[rewards] = True

    # add position data
    df['prey_location'] = [[np.nan, np.nan] for i in range(len(df))]
    df['predator_location'] = [[np.nan, np.nan] for i in range(len(df))]
    agent_frames = {'prey': [], 'predator': []}
    for agent in ('prey', 'predator'):
        traj = episode.trajectories.where('agent_name', agent)
        if len(traj) > 1:
            locs = np.vstack([traj.get('location').get('x'), traj.get('location').get('y')]).T
            frames = traj.get('frame')
            t = np.array(traj.get('time_stamp'))
            if smooth:
                locs = kalman_smoother(locs, t, return_results=False)
            dist = np.sqrt(np.sum(np.diff(locs, axis=0)**2, axis=1))
            dt = np.diff(t)
            v = dist / dt
            v = np.concatenate([v, np.zeros(1)])
            df[f'{agent}_location'].loc[frames] = locs.tolist()
            df[f'{agent}_velocity'].loc[frames] = v

            agent_frames[agent] = {'frames': frames, 
                                    'locs': locs}
            
    if interpolate:
        # interpolate missing frames
        for agent in ('prey', 'predator'):
            locs = np.vstack(df[f'{agent}_location'])
            locs = interpolate_short_nans_2d(locs, axis=0, max_run_length=180, max_delta=0.05)
            df[f'{agent}_location'] = locs.tolist()
            df[f'{agent}_velocity'] = get_velocity(locs, df['time_stamp'])

    if world:
        # calculate visibility
        w = get_world(world)
        vis = Location_visibility.from_world(w)
        visible = np.ones((len(df),1)) * np.nan
        for i in range(len(df)):
            row = df.iloc[i]
            if not np.isnan(row.prey_location[0]) and not np.isnan(row.predator_location[0]):
                is_visible = vis.is_visible(Location(row.prey_location[0], row.prey_location[1]),
                                            Location(row.predator_location[0], row.predator_location[1]))
                visible[i] = is_visible == 1
        df['visible'] = visible

        # OLD 
        # if (len(agent_frames['prey']) > 0) & (len(agent_frames['predator']) > 0):
        #     xy, x_ind, y_ind = np.intersect1d(agent_frames['prey']['frames'], 
        #                                     agent_frames['predator']['frames'], 
        #                                     return_indices=True)
        #     assert len(x_ind) == len(y_ind), 'predator/prey visible frames should not be different lengths'
        #     prey_locs = agent_frames['prey']['locs'][x_ind,:]
        #     pred_locs = agent_frames['predator']['locs'][y_ind,:]
        #     visible = []
        #     for i in range(len(prey_locs)):
        #         visible.append(vis.is_visible(Location(prey_locs[i,0], prey_locs[i,1]),
        #                                     Location(pred_locs[i,0], pred_locs[i,1])))
        #     df.loc[xy, 'visible'] = visible  

    
    return df

def interpolate_short_nans_2d(arr2d, axis=1, max_run_length=2, max_delta=np.inf):
    arr2d = np.array(arr2d).copy()
    
    # Select axis: rows (1) or columns (0)
    def interpolate_line(arr1d):
        is_nan = np.isnan(arr1d)
        padded = np.pad(is_nan.astype(int), (1, 1), mode='constant')
        diff = np.diff(padded)

        starts = np.where(diff == 1)[0]
        ends   = np.where(diff == -1)[0]

        for start, end in zip(starts, ends):
            run_length = end - start
            if run_length <= max_run_length:
                if start > 0 and end < len(arr1d):
                    left_val = arr1d[start - 1]
                    right_val = arr1d[end]
                    if not np.isnan(left_val) and not np.isnan(right_val):
                        if abs(right_val - left_val) <= max_delta:
                            arr1d[start:end] = np.interp(
                                np.arange(start, end),
                                [start - 1, end],
                                [left_val, right_val]
                            )
        return arr1d

    # Apply row-wise or column-wise
    if axis == 1:
        return np.apply_along_axis(interpolate_line, axis=1, arr=arr2d)
    elif axis == 0:
        return np.apply_along_axis(interpolate_line, axis=0, arr=arr2d)
    else:
        raise ValueError("Axis must be 0 (columns) or 1 (rows)")

def episodes_to_dict(episode_list, ideal_bin_width=0.1, fps=90, mask=None, world=None, return_dataframe=False, smooth=False):
    d = {'prey':   {'location': [], 
                    'time_stamp': [], 
                    'frame': [], 
                    'velocity': [], 
                    'outlier_frames': [],
                    'episode': [],
                    'occupancy': [],
                    'coverage': [],
                    'visible': []}, 
        'predator': {'location': [], 
                    'time_stamp': [], 
                    'frame': [], 
                    'velocity': [], 
                    'outlier_frames': [],
                    'episode': [],
                    'occupancy': [],
                    'coverage': [],
                    'visible': []}}

    # build from dataframes
    dfs = []
    for i,e in enumerate(episode_list):
        tmp = episode_to_dataframe(e, world, smooth=smooth)
        tmp['episode'] = i
        dfs.append(tmp)
    df = pd.concat(dfs)

    # append
    for agent in d.keys():
        vals = df[f'{agent}_location'].values
        if len(vals) > 0:
            I = ~np.any(np.isnan(np.vstack(vals)), axis=1)
        else:
            I = []         
        for key in d[agent].keys():
            df_key = [i for i in list(df.columns) if key in i]
            data = np.array([])
            if np.sum(I) > 0:
                if len(df_key) == 1:
                    data = np.vstack(df[df_key[0]].loc[I])
                elif len(df_key) == 2:
                    df_key = [i for i in df_key if agent in i]
                    data = np.vstack(df[df_key[0]].loc[I])
            if key == 'frame':
                data = df.index[I]
            d[agent][key].append(data)

    # reshape
    for agent in d.keys():
        for key in d[agent].keys():
            if len(d[agent][key]) > 0:
                d[agent][key] = np.vstack(d[agent][key])

    # occupancy/coverage
    bins, _, _ = make_map_bins(ideal_bin_width = ideal_bin_width)
    for agent in d.keys():
        d[agent]['time_stamp'] = np.sort(d[agent]['time_stamp']) # rarely, timestamps will come in out of order, which causes issues in other analysis
        if len(d[agent]['location']) > 1:
            d[agent]['occupancy'] = get_occupancy(d[agent]['location'][:,0], d[agent]['location'][:,1], bins, fps=fps)
            d[agent]['coverage'] = get_visit_histogram(d[agent]['location'][:,0], d[agent]['location'][:,1], bins=bins, mask=mask, dt=fps)

    if return_dataframe:
        return d, df
    else:
        return d
    
def recording_stats(R, cutoff=0.2):
    # mouse, datetime, experiment name, world, coverage, time spent in arena, total time, number of good units, number of clusters, number of place cells
    d = {'mouse': R.experiment_info['mouse'],
         'datetime': datetime.strptime(R.experiment_info['date'] + R.experiment_info['time'], '%Y%m%d%M%S'),
         'experiment': R.experiment_name,
         'suffix': R.experiment_info['suffix'],
         'world': R.experiment_info['world'],
         'coverage': np.nansum(R.trajectory_dict['prey']['coverage']>1) / np.sum(~np.isnan(R.trajectory_dict['prey']['coverage'])),
         'arena_time': len(R.trajectory_dict['prey']['visible']) / R.trajectory_dict['prey']['fps'],
         'total_time': R.duration,
         'n_episodes': len(R.episodes),
         'n_good_clusters': (R.clusters_info.KSLabel == 'good').sum(),
         'n_clusters': len(R.clusters_info),
         'n_place_cells': ((R.clusters_info.KSLabel == 'good') & (R.clusters_info.prey_place_cell) & (R.clusters_info.prey_spatial_info > cutoff)).sum()}
    return d




## event detection
def get_amplitude_events(amplitude, amplitude_cutoff=3, min_duration=0.02, min_interval=0.1, fs=30000):
    assert len(amplitude.shape) == 1, f'amplitude must be 1D (for now)'
    candidates = (amplitude > amplitude_cutoff).astype(int)
    starts = np.argwhere(np.diff(candidates) > 0)

    mean_crossings = (amplitude > 0).astype(int)
    crossing_starts = np.argwhere(np.diff(mean_crossings) > 0)
    crossing_stops = np.argwhere(np.diff(mean_crossings) < 0)

    true_starts = []
    true_stops = []
    for i,s in enumerate(starts):
        crossing_before = s - crossing_starts
        crossing_after = crossing_stops - s
        if not np.any(crossing_before > 0) or not np.any(crossing_after > 0):
            continue
        true_starts.append(s - np.min(crossing_before[crossing_before > 0]))
        true_stops.append(s + np.min(crossing_after[crossing_after > 0]))
    true_starts = np.array(true_starts)
    true_stops = np.array(true_stops)

    nearby_events = ((true_stops[1:] - true_starts[:-1]) / fs) < min_interval
    while np.sum(nearby_events) > 0:
        merges = np.argwhere(nearby_events)
        true_stops = np.delete(true_stops, merges)[:,np.newaxis]
        true_starts = np.delete(true_starts, merges+1)[:,np.newaxis]
        nearby_events = ((true_stops[1:] - true_starts[:-1]) / fs) < min_interval
        
    events = np.hstack([true_starts, true_stops])
    events = np.unique(events, axis=0)
    durations = np.diff(events, axis=1) / fs

    return events[durations.squeeze() > min_duration, :]

def clean_events(on_ev, off_ev):
    # if signal started high, discard first off event
    if off_ev[0] < on_ev[0]:
        off_ev = np.delete(off_ev, 0)

    # if signal ended high, discard last on event
    if off_ev[-1] < on_ev[-1]:
        on_ev = np.delete(on_ev, -1)

    return on_ev, off_ev

def get_runs(is_valid, max_gap=1, min_duration=2):
    is_valid = np.atleast_1d(is_valid)
    if is_valid.sum() > 0:
        diff = np.diff(is_valid.astype(int))
        starts = np.where(diff == 1)[0] + 1
        stops = np.where(diff == -1)[0] + 1
        if is_valid[0]:
            starts = np.insert(starts, 0, 0)
        if is_valid[-1]:
            stops = np.append(stops, len(is_valid))

        merged_starts = [starts[0]]
        merged_stops = []

        for i in range(1, len(starts)):
            gap = starts[i] - stops[i-1]
            if gap <= max_gap:
                # extend previous run
                continue
            else:
                # close previous run
                merged_stops.append(stops[i-1])
                merged_starts.append(starts[i])
        merged_stops.append(stops[-1])

        merged_starts = np.array(merged_starts)
        merged_stops = np.array(merged_stops)
        durations = merged_stops - merged_starts

        valid = durations >= min_duration
        filtered_starts = merged_starts[valid]
        filtered_stops = merged_stops[valid]
        filtered_durations = durations[valid]

        return list(zip(filtered_starts, filtered_stops, filtered_durations))
    
    else:
        return [[np.nan],[np.nan],[np.nan]]

def get_run_filter(x, max_gap=1, min_duration=2):
    runs = get_runs(x, max_gap=max_gap, min_duration=min_duration)
    bool_mask = np.zeros_like(x, dtype=bool)
    for run in runs:
        start, stop, duration = run
        bool_mask[start:stop] = True
    return bool_mask

def get_threshold_events(signal, threshold, edge_threshold=0, min_gap=1, min_duration=2):
    above_main = signal > threshold
    core_runs = get_runs(above_main, min_duration=min_duration)
    expanded_events = []

    for start, stop, _ in core_runs:
        # Backtrack to edge_threshold
        left = start
        while left > 0 and signal[left - 1] > edge_threshold:
            left -= 1

        # Forward-track to edge_thresh
        right = stop
        while right < len(signal) and signal[right] > edge_threshold:
            right += 1

        expanded_events.append((left, right, right - left))

    # Merge close events
    if not expanded_events:
        return []

    merged = [expanded_events[0]]
    for start, stop, _ in expanded_events[1:]:
        prev_start, prev_stop, _ = merged[-1]
        if start - prev_stop <= min_gap:
            # merge with previous
            new_start = prev_start
            new_stop = stop
            merged[-1] = (new_start, new_stop, new_stop - new_start)
        else:
            merged.append((start, stop, stop - start))

    return merged

def plot_signal_with_events(signal, events, time=None, ax=None):
    if time is None:
        time = np.arange(len(signal))
    if events is None:
        events = []

    if ax is None:
        _, ax = plt.subplots(1,1)
    ax.plot(time, signal, label='Signal')

    # Overlay events
    for start, stop, _ in events:
        ax.axvspan(time[start], time[stop-1], color='orange', alpha=0.3)

def plot_place_spikes(x, y, t, st):
    spike_index = np.searchsorted(t[:-1], st)
    plt.plot(x, y, 'k')
    plt.scatter(x[spike_index], y[spike_index], c='r', s=2, zorder=10)





## cellworld plotting   
def get_experiment_world(experiment_str):
    if ('FULL' in experiment_str) or ('full' in experiment_str):
        if 'oasis_14_02_00' in experiment_str:
            w = World.get_from_parameters_names('hexagonal', 'canonical', 'oasis_14_02_00')
        elif 'oasis_14_02_01' in experiment_str:
            w = World.get_from_parameters_names('hexagonal', 'canonical', 'oasis_14_02_01')
        else:
            w = World.get_from_parameters_names('hexagonal', 'canonical', 'oasis_14_02')
    else:
        w = World.get_from_parameters_names('hexagonal', 'canonical', '00_00')
    return w


def triangle_points(cell_loc, angle, cell_radius=0.026):
  cell_radius = 0.026
  cell_ori = math.radians(60-angle*60)
  pts = np.array([[cell_loc.x,cell_loc.y],
                  [cell_loc.x+math.cos(cell_ori-math.radians(30))*cell_radius,cell_loc.y+math.sin(cell_ori-math.radians(30))*cell_radius],
                  [cell_loc.x+math.cos(cell_ori+math.radians(30))*cell_radius,cell_loc.y+math.sin(cell_ori+math.radians(30))*cell_radius]])
  return pts


def display_oasis_world(e, w, ax=None, fig=None, plot_scale=False):
    if ax is None:
        _,ax = plt.subplots(1,1, figsize=(6,6))
    if fig is None:
        fig = ax.get_figure()
    if type(w) is str:
        w = World.get_from_parameters_names('hexagonal', 'canonical', w)
    if w is None:
        w = World.get_from_parameters_names('hexagonal', 'canonical', e.occlusions)

    reward_locations = e.rewards_cells
    reward_angles = e.rewards_orientations
    reward_cmap = plt.cm.tab20

    d = Display(w, fig_size=(6,6), ax=ax, fig=fig, 
                show_cell=False, habitat_edge_color='k', habitat_zorder=0, habitat_fill=False)
    ax.set_frame_on(False)
    if plot_scale:
        ax.plot([0,0.25/2.34], [0,0], 'k', linewidth=1.5)
        ax.text(0, 0.01, '25 cm')

    for i, cell in enumerate(reward_locations):
       d.cell(cell_id = cell, color='grey')
       pts = triangle_points(w.cells[cell].location, reward_angles[i], d.cells_size)
       d.ax.add_patch(plt.Polygon(pts, facecolor=reward_cmap(i*2), edgecolor='black'))

    return d, ax

def display_world(w, ax=None, fig=None):
    if ax is None:
        _,ax = plt.subplots(1,1, figsize=(6,6))
    if fig is None:
        fig = ax.get_figure()
    if type(w) is str:
        w = World.get_from_parameters_names('hexagonal', 'canonical', w)
    d = Display(w, fig_size=(6,6), habitat_edge_color='k', habitat_zorder=0, habitat_fill=False, ax=ax, fig=fig)
    return d, ax


def plot_color(x, y, c=None, cmap='viridis', linewidth=2, zorder=None, ax=None, Norm=None, alpha=1.0, lighten=1.0, label=None, rasterize=False):

    if c is None:
        c = np.ones(x.shape)

    if Norm is None:
        norm = plt.Normalize(c.min(), c.max())
    else:
        norm = plt.Normalize(Norm[0], Norm[1])

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap=cmap, norm=norm, capstyle="round")
    lc.set_array(c)
    lc.set_linewidth(linewidth)
    lc.set_zorder(zorder)
    lc.set_alpha(alpha)
    lc.set_rasterized(rasterize)
    if ax:
        line = ax.add_collection(lc)
    else:
        line = plt.gca().add_collection(lc)

    return line

def plot_oasis_trajectories(R, agent='prey', ax=None):
    w, exp, _, _ = R.get_experiment_info()
    d, ax = display_oasis_world(exp, w, ax=ax)
    outliers = R.trajectory_dict[agent]['outlier_frames']
    index = (outliers == False)
    fig = ax.get_figure()
    h = ax.plot(R.trajectory_dict[agent]['location'][index,0], 
                R.trajectory_dict[agent]['location'][index,1],
                'k', linewidth=0.5)
    fig.colorbar(plt.cm.ScalarMappable(cmap='Greys'), ax=ax, fraction=0.046, pad=0.04)
    ax.set_aspect('equal')

    return h


def plot_oasis_occupancy(R, bins, mask, agent='prey', ax=None):
    w, exp, _ = R.get_experiment_info()
    fps = R.get_sync_device('episode').sample_rate
    outliers = R.trajectory_dict[agent]['outlier_frames']
    index = (outliers == False)
    x = R.trajectory_dict[agent]['location'][index,0]
    y = R.trajectory_dict[agent]['location'][index,1]

    d,ax = display_oasis_world(exp, w, ax=ax)
    occupancy = plot_occupancy(x, y, fps, bins=bins, mask=mask, ax=ax)
    return occupancy


def plot_oasis_coverage(R, bins, mask, cutoff=3, normalize=True, agent='prey', ax=None):
    w, exp, _, = R.get_experiment_info()
    fps = R.get_sync_device('episode').sample_rate
    outliers = R.trajectory_dict[agent]['outlier_frames']
    index = (outliers == False)
    x = R.trajectory_dict[agent]['location'][index,0]
    y = R.trajectory_dict[agent]['location'][index,1]
    normalizer = None
    if normalize:
        normalizer = R.duration / 60 / 60
    d,ax = display_oasis_world(exp, w, ax=ax)
    coverage = plot_coverage(x, y, bins, normalizer=normalizer, cutoff=cutoff, mask=mask, ax=ax, dt=int(1*fps))
    return coverage


def plot_oasis_behavior_summary(R, cutoff=2, ideal_bin_width=0.1, figsize=(15,10)):
    # create bins for occupancy
    bins, _, _ = make_map_bins(ideal_bin_width = ideal_bin_width)

    # get experiment info and world mask
    w, _, _ = R.get_experiment_info()
    mask = get_world_mask(w, bins)
    plt.show() # this displays the map

    # return occupancy and coverage
    d = {'prey': {'occupancy': [], 'coverage': []}, 
         'predator': {'occupancy': [], 'coverage': []}}

    fig, ax = plt.subplots(2,3, figsize=figsize)

    agent = 'prey'
    _ = plot_oasis_trajectories(R, agent, ax=ax[0,0])
    _ = ax[0,0].set_title(f'{R.experiment_str}\n{R.n_episodes} episodes in {R.duration / 60:3.1f} minutes\n{agent}')
    d[agent]['occupancy'] = plot_oasis_occupancy(R, bins, mask, agent=agent, ax=ax[0,1])
    _ = ax[0,1].set_title(f'{agent} occupancy')
    d[agent]['coverage'] = plot_oasis_coverage(R, bins, mask, agent=agent, cutoff=cutoff, ax=ax[0,2], normalize=False)
    _ = ax[0,2].set_title(f'{d[agent]["coverage"]*100:3.0f}% coverage')

    agent = 'predator'
    _ = plot_oasis_trajectories(R, agent, ax=ax[1,0])
    _ = ax[1,0].set_title(f'{agent}')
    d[agent]['occupancy'] = plot_oasis_occupancy(R, bins, mask, agent=agent, ax=ax[1,1])
    _ = ax[1,1].set_title(f'{agent} occupancy')
    d[agent]['coverage'] = plot_oasis_coverage(R, bins, mask, agent=agent, cutoff=cutoff, ax=ax[1,2], normalize=False)
    _ = ax[1,2].set_title(f'{d[agent]["coverage"]*100:3.0f}% coverage')

    fig.tight_layout()

    return fig, d

def find_bounding_box(matrix):
    rows, cols = np.where(~np.isnan(matrix))
    if rows.size == 0 or cols.size == 0:
        return None  # All values are NaN
    
    # Bounding box coordinates
    row_min, row_max = rows.min(), rows.max()
    col_min, col_max = cols.min(), cols.max()
    
    return row_min, row_max, col_min, col_max

def clean_boolean_time_jumps(timestamps, flags, threshold=1):
    timestamps = np.asarray(timestamps.copy())
    flags = np.asarray(flags.copy(), dtype=bool)
    
    if len(timestamps) != len(flags):
        raise ValueError("Timestamps and flags must be the same length.")

    # Compute time differences
    diffs = np.diff(timestamps)

    # Find indices where the jump is greater than threshold
    jump_indices = np.where(diffs > threshold)[0]

    # Set the flag at index before jump to False
    for i in jump_indices:
        flags[i] = False

    return flags






# def episodes_to_dict(episode_list, fps, mask=None, ideal_bin_width=0.1, world=None):
#     d = {'prey':   {'location': [], 
#                     'frame_time': [], 
#                     'frame': [], 
#                     'velocity': [], 
#                     'outlier_frames': [],
#                     'episode': [],
#                     'occupancy': [],
#                     'coverage': [],
#                     'visible': []}, 
#         'predator': {'location': [], 
#                     'frame_time': [], 
#                     'frame': [], 
#                     'velocity': [], 
#                     'outlier_frames': [],
#                     'episode': [],
#                     'occupancy': [],
#                     'coverage': [],
#                     'visible': []}}

#     if world:
#         if type(world) is str:
#             w = World.get_from_parameters_names('hexagonal', 'canonical', world)
#         else:
#             w = world
#         vis = Location_visibility.from_world(w)
#     else:
#         vis = None
                    
#     for i,e in enumerate(episode_list):
#         traj = {}
#         samps = []
#         for agent in d.keys():
#             traj[agent] = e.trajectories.where('agent_name', agent)
#             samps.append(len(traj[agent]))
#             if len(traj[agent]) > 0:
#                 locs = np.vstack([traj[agent].get('location').get('x'), 
#                                     traj[agent].get('location').get('y')])
#                 assert locs.shape[0] == 2, 'Locations must have two rows'
#                 frames = traj[agent].get('frame')
#                 t = traj[agent].get('time_stamp')
#                 #v = traj.get_velocities()[agent]
#                 dist = np.sqrt(np.sum(np.diff(locs, axis=1)**2, axis=0))
#                 dt = np.diff(t)
#                 v = dist / dt
#                 o = get_outliers_index(v, 2)

#                 d[agent]['location'].append(locs)
#                 d[agent]['frame_time'].append(t)
#                 d[agent]['frame'].append(np.array(frames))
#                 d[agent]['outlier_frames'].append(np.array([f in o for f in frames]))
#                 d[agent]['velocity'].append(clean_velocity(v, 2, 11))
#                 d[agent]['episode'].append(np.repeat(i, locs.shape[1]))

#         if (vis is not None):
#             if (samps[0] > 0) and (samps[1] > 0):
#                 ind = {}
#                 _, ind['prey'], ind['predator'] = np.intersect1d(traj['prey'].get('frame'),
#                                                                  traj['predator'].get('frame'),
#                                                                  return_indices=True)
#                 assert len(ind['prey']) == len(ind['predator']), 'pred/prey intersection frames must have equal length'

#                 locs = {}
#                 visibility = {}
#                 for agent in d.keys():
#                     visibility[agent] = np.empty((len(traj[agent].get('frame')))) * np.nan
#                     locs[agent] = np.vstack([traj[agent].get('location').get('x'), 
#                                             traj[agent].get('location').get('y')])
#                 prey_locs = locs['prey'][:, ind['prey']]
#                 pred_locs = locs['predator'][:, ind['predator']]

#                 visible = []
#                 for i in range(prey_locs.shape[1]):
#                     try:
#                         visible.append(vis.is_visible(Location(prey_locs[0,i], prey_locs[1,i]),
#                                                     Location(pred_locs[0,i], pred_locs[1,i])))
#                     except:
#                         visible.append(np.nan)
#                 for agent in d.keys():
#                     visibility[agent][ind[agent]] = visible
#                     d[agent]['visible'].append(visibility[agent])
#                     print(len(d[agent]['visible']), len(d[agent]['frame']))
#                     assert len(d[agent]['visible']) == len(d[agent]['frame']), f'{agent} episode count does not match'

#             else:
#                 for agent in d.keys():
#                     if len(traj[agent]) > 0:
#                         d[agent]['visible'].append(len(traj[agent].get('frame')) * np.nan)

#     for agent in d.keys():
#         for key in d[agent].keys():
#             if len(d[agent][key])> 0:
#                 d[agent][key] = np.hstack(d[agent][key]).T

#     # calulate occupancy
#     bins, _, _ = make_map_bins(ideal_bin_width = ideal_bin_width)
#     for agent in d.keys():
#         if len(d[agent]['location']) > 0:
#             d[agent]['occupancy'] = get_occupancy(d[agent]['location'][:,0], d[agent]['location'][:,1], bins, fps=fps)
#             d[agent]['coverage'] = get_visit_histogram(d[agent]['location'][:,0], d[agent]['location'][:,1], bins=bins, mask=mask, dt=fps)
#     return d



# def trajectories_to_dict(R, ideal_bin_width=0.1, compute_visible=False):
#     #frames_aligned, _ = R.match_experiment_syncs(plot=False, verbose=False, all_frames=True)
#     d = {'prey':   {'location': [], 
#                     'frame_time': [], 
#                     'frame': [], 
#                     'velocity': [], 
#                     'outlier_frames': [],
#                     'episode': [],
#                     'visible': []}, 
#         'predator': {'location': [], 
#                     'frame_time': [], 
#                     'frame': [], 
#                     'velocity': [], 
#                     'outlier_frames': [],
#                     'episode': [], 
#                     'visible': []}}
#     for i,e in enumerate(R.episodes):
#         if e.valid_episode:
#             for agent in d.keys():

#                 traj = e.episode.trajectories.where('agent_name', agent)

#                 locs = np.vstack([traj.get('location').get('x'), traj.get('location').get('y')])
#                 #print(agent, i, locs.shape)
#                 d[agent]['location'].append(locs)

#                 agent_index = np.where(np.array(e.episode.trajectories.get('agent_name')) == agent)
#                 aligned_frames = e.frame_times[agent_index]
#                 d[agent]['frame_time'].append(aligned_frames)

#                 frames = traj.get('frame')
#                 d[agent]['frame'].append(np.array(frames))

#                 v = traj.get_velocities()[agent]
#                 o = get_outliers_index(v, 2)
#                 d[agent]['outlier_frames'].append(np.array([f in o for f in frames]))

#                 d[agent]['velocity'].append(clean_velocity(v, 2, 11))

#                 d[agent]['episode'].append(np.repeat(R.episode_num[i], locs.shape[1]))


#     for agent in d.keys():
#         for key in d[agent].keys():
#             d[agent][key] = np.hstack(d[agent][key]).T

#     for agent in d.keys():
#         d[agent]['frame_time'] = np.sort(d[agent]['frame_time']) # sometimes frames come in out of order... super rare

#     # calulate occupancy
#     bins, _, _ = make_map_bins(ideal_bin_width = ideal_bin_width)
#     fps = R.get_sync_device('episode').sample_rate
#     for agent in d.keys():
#         d[agent]['occupancy'] = get_occupancy(d[agent]['location'][:,0], d[agent]['location'][:,1], bins, fps=fps)

#     return d