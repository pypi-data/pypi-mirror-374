import numpy as np
from json_cpp import JsonObject
from cellworld import Experiment, World, Episode
from .episode import RecordingEpisode, RecordingEpisodes
from .sync import *
from .cluster_metrics import get_population, check_cluster_groups_file
from .utils import *
from .coverage import get_visit_histogram, make_map_bins, get_occupancy
from .celltile import get_world_mask
from .map import *
from .probe import *
from .lfp import *
from .io import *
from .pose import *
from .camera import *
from .backup import pull_continuous_data
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
import os
import pickle
import gc
from pathlib import Path


    


class Recording(JsonObject):
    def __init__(self, spike_path=list(), behavior_path=list(), episode=list(), vr_log=str()):
        episode = [episode] if isinstance(episode, int) else episode
        assert all([type(i) is int for i in episode]), 'All episodes must be int' 
        self.spike_path = spike_path
        self.behavior_path = behavior_path
        self.vr_log = vr_log
        self.experiment_name = self.get_experiment_name()
        self.experiment_info = parse_experiment_name(self.experiment_name)
        self.world = self.get_world()
        if len(self.spike_path) > 0:
            # load sync devices and probe/recording metadata
            self.get_spike_paths()
            self.probes, self.processors = self.get_processor_info()
            self.probe_names = self.probes.get('name')
            self.probe_index = {name: i for i,name in enumerate(self.probe_names)}


    def process(self, ops=None, skip_entrance_video=False):
        if ops is None and not hasattr(self, 'ops'):
            self.set_ops()
        self.episode_folders = []
        if len(self.behavior_path) > 0:
            # load experiment logs
            self.episode_folders, self.episode_num, self.episode_is_valid, self.sync_data_present = get_episode_folders(self.behavior_path)
            if not skip_entrance_video:
                self.get_entrance_video()
            self.load_sync_devices()
            self.load_experiments()
            self.episode_fs = self.get_average_fps()

        if len(self.spike_path) > 0:
            # load and align sync devices
            self.load_sync_devices()
            self.align_sync_devices('NI', plot_err=False)

            # load spike data
            self.spike_times, self.clusters, self.clusters_info, self.probe_spike_index = self.get_spikes()
            self.spike_fs = self.get_sync_device(self.probe_names[0]).sample_rate
    

    def process_and_save(self, fn=None, ops=None):
        # standard processing pipeline
        if ops is None and not hasattr(self, 'ops'):
            ops = self.set_ops()
        elif ops is None and hasattr(self, 'ops'):
            ops = self.ops
        else:
            self.ops = ops
        self.process()
        self.info()
        self.drift_correct_episodes()
        self.recording_episodes_to_dict()
        _ = self.get_population(recalculate=ops['recalculate_population'], download=True)
        #_ = self.get_population(type='binary_waveform', save=True, download=True, again=True, delete=True)
        _ = self.update_clust_info()
        _, _, _ = self.restrict_spikes_to_episodes()
        if self.vr_log:
            self.get_vr_data()
        self.run_place_tests(ops['place_tests'])
        if fn is None:
            fn = f'./{self.experiment_name}_recording.pkl'
        self.save(fn)


    def set_ops(self, 
            ideal_bin_width=0.10, # m
            place_tests=['prey', 'predator_visible', 'predator_not_visible'], 
            threshold_distance=0.25, # m
            remove_bad_frames=True, 
            velocity_cutoff=0.04, # m/s
            occupancy_cutoff=0.1, # s
            smooth=1.0,
            shuffles=500, 
            significant_p=0.95,
            kalman_filter=True,
            interpolate_missing=True,
            recalculate_population=False):
        bins,_,_ = make_map_bins(ideal_bin_width)
        self.ops = {'ideal_bin_width': ideal_bin_width,
                    'place_tests': place_tests,
                    'threshold_distance': threshold_distance,
                    'remove_bad_frames': remove_bad_frames,
                    'velocity_cutoff': velocity_cutoff / 2.34,
                    'occupancy_cutoff': occupancy_cutoff,
                    'smooth': smooth,
                    'shuffles': shuffles,
                    'significant_p': significant_p,
                    'kalman_filter': kalman_filter,
                    'interpolate_missing': interpolate_missing,
                    'recalculate_population': recalculate_population,
                    'bins': bins}
        return self.ops
    
    def run_place_tests(self, tests):
        if 'prey' in tests:
            _ = self.calculate_spatial_info(agents=['prey'], 
                                            use_cuda=True, 
                                            velocity_cutoff=self.ops['velocity_cutoff'], 
                                            occupancy_cutoff=self.ops['occupancy_cutoff'], 
                                            smooth=self.ops['smooth'],                                            
                                            its=self.ops['shuffles'],
                                            sig=self.ops['significant_p'])
        if 'predator_visible' in tests:
            _ = self.calculate_spatial_info(agents=['predator'], 
                                            visible=True, 
                                            use_cuda=True, 
                                            velocity_cutoff=self.ops['velocity_cutoff'], 
                                            occupancy_cutoff=self.ops['occupancy_cutoff'], 
                                            smooth=self.ops['smooth'],                                            
                                            its=self.ops['shuffles'],
                                            sig=self.ops['significant_p'])
        if 'predator_not_visible' in tests:
            _ = self.calculate_spatial_info(agents=['predator'], 
                                            visible=False, 
                                            use_cuda=True, 
                                            velocity_cutoff=self.ops['velocity_cutoff'], 
                                            occupancy_cutoff=self.ops['occupancy_cutoff'], 
                                            smooth=self.ops['smooth'],
                                            its=self.ops['shuffles'],
                                            sig=self.ops['significant_p'])
        if 'legacy' in tests:
            _ = self.calculate_spatial_info(velocity_cutoff=self.ops['velocity_cutoff'])
    

    def info(self):
        if len(self.behavior_path) > 0:
            print(f'\nRECORDING {self.experiment_name}')
            print(f'\tBehavioral experiments ({len(self.experiments)}): {len(self.episodes)} episodes, {self.behavior_duration/60:3.2f} minutes, {self.episode_fs:3.2f} samples/s')
            for i,p in enumerate(self.behavior_path):
                print(f'\t\tExperiment {i}: {p}')
        else:
            print('No behavioral data found!')
        if len(self.spike_path) > 0:
            for p in range(len(self.spike_path)):
                print(f'\tNeuronal recording: {self.probes[p]["name"]}, {self.probes[p]["type"]}, {self.spike_fs} samples/s')
                print(f'\t\t{self.spike_path[p]}')
        else:
            print('No spike data found!')


    def save(self, fn=None, method='pickle'):
        self.close_binary_file()
        if fn is None:
            fn = f'{self.experiment_name}_recording.pkl'
        with open(fn, 'wb') as fid:
            pickle.dump(self, fid, protocol=pickle.HIGHEST_PROTOCOL)


    def load(self, fn=str):
        with open(fn, 'rb') as fid:
            recording = pickle.load(fid)

        return recording
    
    
    def get_spike_paths(self):
        self.binary_files = self.get_file('continuous.dat')
        if self.binary_files is None:
            files = self.get_file('timestamps.npy')
        else:
            files = self.binary_files
        self.binary_paths = [os.path.split(f)[0] for f in files]
        self.kilosort_paths = os.path.split(self.get_file('params.py')[0])
        self.settings_file = self.get_file('settings.xml')[0]
        self.sync_messages_file = self.get_file('sync_messages.txt')[0]
        self.spike_root = os.path.split(self.sync_messages_file)[0]


    def get_entrance_video(self, root=None, threshold=30*60):
        if root is None:
            root = os.path.split(self.behavior_path[0])[0]
        files = find_file(root, f"{self.experiment_info['mouse']}.mp4")
        match = None
        if files is not None:
            files = files[-1]
            experiment_time = datetime.strptime(f"{self.experiment_info['date']}_{self.experiment_info['time']}",'%Y%m%d_%H%M')
            movie_times = [datetime.strptime(f.split('_')[0], '%Y%m%d-%H%M%S') for f in files]
            match = match_date(movie_times, experiment_time, threshold=threshold)
        if match is not None:
            self.entrance_video = os.path.join(root, files[match])
            labelled_files = glob.glob(self.entrance_video.replace('.mp4', '') + '*.h5')
            if len(labelled_files) > 0:
                self.entrance_labels = labelled_files[0]
        else:
            print(f'No entrance video found')


    def open_binary_file(self, fn=None):
        if fn is None:
            if self.binary_files is None:
                self.get_spike_paths()
            fn = self.binary_files[0]
        self.binary_file, binary_ops = get_binary_file(fn, return_ops=True)
        if not hasattr(self, 'binary_ops'):
            self.binary_ops = binary_ops
        return self.binary_file, self.binary_ops
    

    def close_binary_file(self):
        if hasattr(self, 'binary_file'):
            delattr(self, 'binary_file')
        gc.collect()
        torch.cuda.empty_cache()


    def get_sync_device(self, name):
        for names in self.sync_devices.get('name'):
            if name in names:
                return self.sync_devices.where('name', names)[0]
            
            
    def get_file(self, filename:str):
        root_path = walk_back(self.spike_path[0], 'Record Node')
        return find_file(root_path, filename, joined=True)
    
    
    def get_probe_sites(self):
        names = self.probes.get('type')
        return [get_probe_sites(n) for n in names]
    
    
    def get_channel_map(self, order='lfp'):
        return [get_channel_map(p, order=order) for p in self.probes]
    
    
    def get_processor_info(self):
        return Probes(self.settings_file), Processors(self.settings_file)
    
    
    def get_episode_times(self):
        return np.vstack([self.episodes.get('start_time'), self.episodes.get('end_time')]).T
    
    
    def get_behavior_duration(self):
        return (self.episodes[-1].end_time - self.episodes[0].start_time).total_seconds()
    
    def get_neural_duration(self):
        if hasattr(self, 'binary_file'):
            pass
    

    def get_average_fps(self):
        fps = [self.sync_devices.where('name',f'episode_{n:03d}')[0].sample_rate for n in self.episode_num]
        return sum(fps) / len(fps)
    
    
    def get_experiment_name(self):
        if len(self.behavior_path) > 0:
            return self.behavior_path[0].split('\\')[-1]
        
        
    def get_world(self):
        world_string = self.experiment_info['world']
        if ('OASIS' in self.experiment_name) and (not 'FULL' in self.experiment_name) and (not 'full' in self.experiment_name):
            world = '00_00'
        else:
            world = world_string
        return World.get_from_parameters_names('hexagonal', 'canonical', world)
    
    
    def load_experiments(self):
        self.experiments = []
        for p in self.behavior_path:
            self.experiments.append(Experiment.load_from_file(glob.glob(os.path.join(p, '*_experiment.json'))[0]))
        self.episodes = Episode_list()
        episode_num = self.episode_num.copy()
        episode_folders = self.episode_folders.copy()
        for i,f in enumerate(self.episode_folders):
            episode_file = glob.glob(os.path.join(f, '*episode*.json'))
            assert len(episode_file) > 0, f'Episode log not found in {f}'
            flag = False
            episode = Episode.load_from_file(episode_file[0])
            # episode.trajectories = episode.trajectories.get_unique_steps() # remove duplicate frames (this introduces many missed frames, removing)
            # print(f'episode {i}: {len(episode.trajectories)}')
            if len(episode.trajectories) == 0:
                print(f'{f} was empty, removing...')
                flag = True
            else:
                if self.ops['remove_bad_frames']:
                    episode = clean_episode_tracking(episode, threshold_distance=self.ops['threshold_distance'])
                else:
                    if bad_episode_tracking(episode, threshold_distance=self.ops['threshold_distance']):
                        print(f'{f} had a tracking error, removing...')
                        flag = True
            if not flag:
                episode = clean_episode_timestamps(episode)
                self.episodes.append(episode)
            else:
                episode_num.remove(self.episode_num[i])
                episode_folders.remove(self.episode_folders[i])
        self.episode_num = episode_num
        self.n_episodes = len(self.episodes)
        self.behavior_duration = self.get_behavior_duration()
        self.episode_folders = episode_folders
        assert len(self.episodes) == len(self.episode_num), f'{len(self.episodes)} episodes but {len(self.episode_num)} indexes'

    
    def load_sync_info(self):
        with open(self.sync_messages_file) as f:
            lines = f.readlines()
            data = {}
            for line in lines:
                l = line.split(':')
                data[l[0]] = int(l[1].strip())
        return data


    def load_sync_devices(self):
        # behavioral sync data
        if not hasattr(self, 'sync_devices'):
            self.sync_devices = SyncDevices()
        for i,f in enumerate(self.episode_folders):
            d = SyncDevice(f'episode_{self.episode_num[i]:03d}', f)
            if len([name for name in self.sync_devices.get('name') if d.name == name]) == 0:
                self.sync_devices.append(d)

        # neural sync data
        if hasattr(self, 'sync_messages_file'):
            sync_info = self.load_sync_info()
            for dev in sync_info:
                d = SyncDevice(dev, self.spike_root)
                self.sync_devices.append(d)

        # entrance video
        if hasattr(self, 'entrance_video') and not 'entrance_camera' in self.sync_devices.get('name'):
            d = SyncDevice(root=self.entrance_video, full_name='entrance_camera')
            self.sync_devices.append(d)


    def align_sync_devices(self, reference_device='NI', plot_err=False):
        ref_device = self.get_sync_device(reference_device)
        for name in self.sync_devices.get('name'):
            if 'episode' in name or 'Probe' in name or 'camera' in name:
                if '000' in name:
                    min_overlap = 1
                else:
                    min_overlap = 5
                self.get_sync_device(name).align(device=ref_device, min_overlap=min_overlap, plot_err=plot_err)


    def drift_correct_episodes(self, plot=False):
        if 'RecordingEpisodes' not in str(type(self.episodes)):
            episodes = RecordingEpisodes()

            for i,e in enumerate(self.episode_num):
                ep = RecordingEpisode()
                if len(self.episodes[i].trajectories) > 0:
                    episode_match = True
                    drift_coeffs = self.get_sync_device(f'episode_{e:03d}').drift_coeffs
                    if len(drift_coeffs[0].coeffs) > 0:
                        z = drift_coeffs[0].coeffs
                    else:
                        print(f'Failed to align episode {e}... discarding episode')
                        episode_match = False

                if episode_match:
                        ep.valid_episode = True
                        ep.number = e
                        ep.align_episode_times(z, self.episodes[i])
                        episodes.append(ep)

            self.episodes = episodes

        if plot:
            for ep in self.episodes:
                h = plot_diff(ep.frame_times, markersize=1)
                plt.eventplot([ep.start_time, ep.end_time], lineoffsets=0.01, linewidths=0.5, color=h[-1].get_color())
            plt.gca().set_yscale('log') 

    def format_recording_episodes(self):
        if 'RecordingEpisodes' not in str(type(self.episodes)):
            episodes = RecordingEpisodes()
            for i,e in enumerate(self.episode_num):
                ep = RecordingEpisode()
                ep.valid_episode = True
                ep.number = e
                ep.align_episode_times([1.0, 0.0], self.episodes[i])
                episodes.append(ep)
            self.episodes = episodes



    def get_spikes(self, probe=None):
        """
        Load and return spike time data, cluster assignments, and cluster metadata from one or more probes.

        Parameters
        ----------
        probe : str or None, optional
            If specified, only load spike data from the given probe name.
            If None (default), load data from all probes listed in `self.probe_names`.

        Returns
        -------
        spike_times : np.ndarray
            Array of drift-corrected spike times (in seconds) across all selected probes.
        clusters : np.ndarray
            Array of cluster IDs corresponding to each spike time.
        clusters_info : pd.DataFrame
            DataFrame with metadata for each cluster, including probe name and index.
        probe_index : np.ndarray
            Array indicating the probe index for each spike.

        Notes
        -----
        - Applies drift correction to spike times using polynomial coefficients from the associated probe sync device.
        - Loads spike cluster assignments and merges cluster metadata from `cluster_info.tsv` (or a fallback method).
        - Each spike is tagged with its probe index, allowing multi-probe analysis.
        """
        if probe is None:
            probe_names = self.probe_names
        else:
            probe_names = [probe]

        spike_times = []
        clusters = []
        probe_index = []
        clusters_info = []
        for p in probe_names:
            probe_sync = self.get_sync_device(p)
            pn = probe_sync.name
            spike_path = self.spike_path[self.probe_index[pn]]

            # load and drift correct spike times, index probe
            fn = os.path.join(spike_path, 'spike_times.npy')
            spk_t = np.load(fn) / probe_sync.sample_rate
            spike_times.append(np.polyval(probe_sync.drift_coeffs[0].coeffs, spk_t))
            probe_index.append([self.probe_index[pn]] * len(spk_t))

            # load clusters
            clusters.append(np.load(os.path.join(spike_path, 'spike_clusters.npy')))

            # load clusters info
            info_file = os.path.join(spike_path, 'cluster_info.tsv')
            if os.path.exists(info_file):
                clust_info = pd.read_csv(info_file, sep='\t', header=0)
            else:
                # update the cluster_group.tsv file to have a column group with correct IDs
                clust_info = check_cluster_groups_file(spike_path)
            clust_info['probe_name'] = pn
            clust_info['probe_index'] = self.probe_index[pn]
            clusters_info.append(clust_info)
        clusters_info = pd.concat(clusters_info)
        clusters_info.index = np.arange(len(clusters_info))

        return np.hstack(spike_times), np.hstack(clusters), clusters_info, np.hstack(probe_index)
        

    def restrict_spikes_to_episodes(self):
        video_times = np.vstack([self.episodes.get('start_time'), self.episodes.get('end_time')]).T
        spikes = []
        clusters = []
        probes = []
        for e in tqdm(range(video_times.shape[0]), desc='Restricting spikes to episodes...'):
            I = (self.spike_times > video_times[e,0]) & (self.spike_times < video_times[e,1])
            spikes.append(self.spike_times[I.squeeze()].squeeze())
            clusters.append(self.clusters[I.squeeze()].squeeze())
            probes.append(self.probe_spike_index[I.squeeze()].squeeze())
        self.spike_times = np.hstack(spikes)
        self.clusters = np.hstack(clusters)
        self.probe_spike_index = np.hstack(probes)
        return self.spike_times, self.clusters, self.probe_spike_index
    
    def download_continuous_data(self, again=False):
        for spike_path in self.spike_path:
            population_present = os.path.exists(os.path.join(spike_path, 'population.pkl'))
            if not os.path.exists(os.path.join(spike_path, 'continuous.dat')):
                if not population_present or again:
                    drive, tail = os.path.splitdrive(spike_path)
                    parts = tail.strip(os.sep).split(os.sep)
                    local = os.path.join(drive + os.sep, parts[0])
                    folder = spike_path.replace(local, '')
                    pull_continuous_data(folder, local)

    def delete_continuous_data(self, timeout=10):
        for spike_path in self.spike_path:
            fn = os.path.join(spike_path, 'continuous.dat')
            if os.path.exists(fn):
                print(f'WARNING: DELETING {fn} IN {timeout} SECONDS, PRESS CTRL-C TO CANCEL!')
                sleep(timeout)
                os.remove(fn)
    
    def delete_partial_files(self):
        for spike_path in self.spike_path:
            partial_files = [f for f in os.listdir(spike_path) if '.partial' in f]
            for f in partial_files:
                os.remove(os.path.join(spike_path,f))

    def get_population(self, again=False, type='binary_waveform', save=True, download=False, delete=False, recalculate=True):
        if recalculate:
            download = True
            again = True
            save = True
            delete = True
        if not hasattr(self, 'population') or again:
            if download:
                self.download_continuous_data(again=again)
                delete = True
            self.population = get_population(self.spike_path, waveform_type=type, save=save, overwrite=again)
        if (not hasattr(self, 'population') or (len(self.population) == 0)) and not again:
            self.population = self.load_population()
        if delete:
            self.delete_continuous_data()
        return self.population
    
    
    def load_population(self):
        return get_population(self.spike_path, save=False, overwrite=False)
    
    
    def update_clust_info(self, delete_population=True):
        assert(hasattr(self, 'clusters_info')), 'ERROR: Recording must have clust_info loaded!'
        assert(hasattr(self, 'population')), 'ERROR: Recording must have a Population loaded!'
        rows = []
        for c in tqdm(self.population, desc='Updating cluster info...'):
            assert(hasattr(c, 'qualities')), f'ERROR: Cluster {c.u} must have qualities computed'
            series = c.to_series(self.clusters_info)
            series['experiment'] = self.experiment_name
            series['prefix'] = self.experiment_info['prefix']
            series['date'] = self.experiment_info['date']
            series['time'] = self.experiment_info['time']
            series['mouse'] = self.experiment_info['mouse']
            series['world'] = self.experiment_info['world']
            series['suffix'] = self.experiment_info['suffix']
            rows.append(series)
        self.clusters_info = pd.concat(rows, axis=1).T
        if delete_population:
            self.population = []
        return self.clusters_info
    

    def refresh_clust_info(self):
        new_df = []
        for i,row in tqdm(self.clusters_info.iterrows(), desc='Refreshing cell info...'):
            #print(R.population[i].qualities.nspikes, row['n_spikes'])
            for key in row.keys():
                if hasattr(self.population[i], key):
                    row[key] = getattr(self.population[i], key)
                if hasattr(self.population[i].qualities, key):
                    row[key] = getattr(self.population[i].qualities, key)
            new_df.append(row)
        self.clusters_info = pd.concat(new_df, axis=1).T
        return self.clusters_info
    
    
    def recording_episodes_to_dict(self, return_data=False, fps=90):
        d = {'prey':    {'location': [], 
                         'time_stamp': [], 
                         'frame': [], 
                         'velocity': [], 
                         'outlier_frames': [],
                         'episode': [],
                         'occupancy': [],
                         'coverage': [],
                         'bins': [],
                         'fps': [],
                         'visible': [],
                         'tracked': []}, 
            'predator': {'location': [],
                         'time_stamp': [], 
                         'frame': [], 
                         'velocity': [], 
                         'outlier_frames': [],
                         'episode': [],
                         'occupancy': [],
                         'coverage': [],
                         'bins': [],
                         'fps': [],
                         'visible': [],
                         'tracked': []}}
        
        if not hasattr(self, 'ops'):
            smooth = True
            interpolate = True
            bins, _, _ = make_map_bins(0.1)
        else:
            smooth = self.ops['kalman_filter']
            interpolate = self.ops['interpolate_missing']
            bins = self.ops['bins']
        
        # build from dataframes
        dfs = []
        frame_count = 0
        for i,e in tqdm(enumerate(self.episodes), 
                        desc='Building episode dictionary...', 
                        total=len(self.episodes)):
            if e.valid_episode:
                tmp = episode_to_dataframe(e.episode, 
                                           self.world, 
                                           smooth=smooth, 
                                           interpolate=interpolate)
                _, ind = get_unique_frames(e.episode)
                aligned_frames = e.frame_times[ind]
                assert len(aligned_frames) == len(tmp['time_stamp']), f'aligned frame times {len(aligned_frames)} must be same length as original time_stamps {len(tmp["time_stamp"])}'
                tmp['time_stamp'] = aligned_frames
                tmp['episode'] = self.episode_num[i]
                tmp = tmp.reset_index()
                frames = tmp['frame'].copy()
                tmp['frame'] = frames + frame_count
                frame_count += frames.max()
                dfs.append(tmp)
        df = pd.concat(dfs)
        df = df.reset_index()

        # convert visibility to boolean (much nicer later on)
        df['visible'][df['visible'] == 1] = True
        df['visible'][df['visible'] == 0] = False

        # append
        for agent in d.keys():
            I = ~np.any(np.isnan(np.vstack(df[f'{agent}_location'].values)), axis=1)
            for key in d[agent].keys():
                df_key = [i for i in list(df.columns) if key in i]
                if np.sum(I) == 0:
                    data = np.array([])
                elif len(df_key) == 1:
                    data = np.vstack(df[df_key[0]].loc[I])
                elif len(df_key) > 1:
                    df_key = [i for i in df_key if agent in i]
                    data = np.vstack(df[df_key[0]].loc[I])
                else:
                    data = np.array([])
                d[agent][key].append(data)
        # print(d['prey']['frame'], d['prey']['location'])
        # reshape
        for agent in d.keys():
            for key in d[agent].keys():
                if len(d[agent][key])> 0:
                    d[agent][key] = np.vstack(d[agent][key]).squeeze()

        # occupancy/coverage
        bins = bins
        mask = get_world_mask(self.world, bins)
        for agent in d.keys():
            d[agent]['time_stamp'] = np.sort(d[agent]['time_stamp']) # rarely, timestamps will come in out of order, which causes issues in other analysis
            if len(d[agent]['location']) > 0:
                d[agent]['occupancy'] = get_occupancy(d[agent]['location'][:,0], d[agent]['location'][:,1], bins, fps=fps)
                d[agent]['coverage'] = get_visit_histogram(d[agent]['location'][:,0], d[agent]['location'][:,1], bins=bins, mask=mask, dt=fps)
                d[agent]['bins'] = bins
                d[agent]['fps'] = fps

        self.trajectory_dict = d
        if return_data:
            return d, df
        
        
    def calculate_spatial_info(self, its=500, sig=95, normalize=True, agents = ['vr', 'prey', 'predator'], visible=None, use_cuda=True, velocity_cutoff=0.0, occupancy_cutoff=0.0, mask=None, bins=None, smooth=None):
        df = self.clusters_info.copy()
        agents = [a for a in agents if a in self.trajectory_dict.keys()]

        for agent in agents:
            vis_labels = {True:'_visible', False:'_not_visible', None:''}
            if f'{agent}{vis_labels[visible]}_place_cell' in self.clusters_info.columns:
                print('WARNING: spatial info found in clusters_info, did you already run it?')
            d = {}
            agent_time = len(self.trajectory_dict[agent]['location']) / self.episode_fs
            if (agent_time / self.behavior_duration) > 0.01: # skip if agent wasn't visible 99% of time
                clusters = self.clusters.copy()
                spike_times = self.spike_times.copy()
                probes = self.probe_spike_index.copy()
                if agent == 'vr':
                    spike_times, clusters, _ = self.get_spikes()
                    start = np.nanmin(self.trajectory_dict[agent]['time_stamp'])
                    end = np.nanmax(self.trajectory_dict[agent]['time_stamp'])
                    I = (spike_times > start) & (spike_times < end)
                    spike_times = spike_times[I]
                    clusters = clusters[I]
                    probes = probes[I]
                else:
                    _, tracked = get_tracked_frames(self.trajectory_dict['prey']['time_stamp'])

                # align agents
                I, ia, ib = np.intersect1d(self.trajectory_dict[agent]['time_stamp'], 
                                           self.trajectory_dict['prey']['time_stamp'], 
                                           return_indices=True)
                
                # use only tracked frames
                mouse_tracked = np.zeros(self.trajectory_dict[agent]['velocity'].shape)
                mouse_tracked[ia] = tracked[ib]
                include = mouse_tracked > 0

                if visible is not None:
                    assert 'visible' in self.trajectory_dict[agent].keys(), 'no "visible" data in trajectory_dict'
                    include = (self.trajectory_dict[agent]['visible'] == visible) & (include > 0)

                if velocity_cutoff > 0:
                    v = np.zeros(self.trajectory_dict[agent]['velocity'].shape)
                    v[ia] = self.trajectory_dict['prey']['velocity'][ib]
                    include = (include > 0) & (v > velocity_cutoff)

                # clean inclusion edges that end "high" (set to low to prevent gaps that spikes can get shuffled into)
                include = clean_boolean_time_jumps(self.trajectory_dict[agent]['time_stamp'], include)

                t = self.trajectory_dict[agent]['time_stamp'][include]
                x = self.trajectory_dict[agent]['location'][include,0].T
                y = self.trajectory_dict[agent]['location'][include,1].T
                if bins is None:
                    bins = self.trajectory_dict[agent]['bins']
                occupancy = get_occupancy(x, y, bins, fps=self.trajectory_dict[agent]['fps'])

                desc = f"Running {agent} {vis_labels[visible]} place tests...\nshuffles: {its}\np-value: {sig}\nvelocity cutoff: {velocity_cutoff:0.2f}\noccupancy cutoff: {occupancy_cutoff:0.2f}"
                print(desc)

                for i in tqdm(range(len(self.clusters_info)), desc=f"smoothing kernel: {smooth}"):
                    u = self.clusters_info['cluster_id'][i]
                    p = self.clusters_info['probe_index'][i]
                    u_spikes = spike_times[(clusters==u) & (probes==p)]
                    if use_cuda:
                        place_cell, SI, shuff_SI, rate_map, mean_fr, percentile_map = spatial_info_fast(
                            u_spikes, self.trajectory_dict[agent]['time_stamp'], include, np.vstack((x,y)).T, occupancy, bins, 
                            its=its, sig=sig, normalize=normalize, mask=mask, occupancy_cutoff=occupancy_cutoff, smooth=smooth)
                    else:
                        epochs = get_epochs(include, self.trajectory_dict[agent]['time_stamp'])
                        u_spikes = filter_spikes(u_spikes, epochs)
                        if len(u_spikes) == 1:
                            u_spikes = np.repeat(u_spikes, 2)
                        place_cell, SI, shuff_SI, rate_map, mean_fr, percentile_map = spatial_info_perm(
                            u_spikes, t, np.vstack([x,y]).T, occupancy, bins, 
                            epochs, its=its, sig=sig, normalize=normalize, mask=mask, occupancy_cutoff=occupancy_cutoff)
                    if place_cell & False:
                        plt.imshow(np.rot90(rate_map)); plt.title(f'cell {i}: place cell ({SI:0.2f}bits/AP)'); plt.show()
                    d[i] = {f'{agent}{vis_labels[visible]}_place_cell': place_cell, 
                            f'{agent}{vis_labels[visible]}_rate_map': rate_map,
                            f'{agent}{vis_labels[visible]}_spatial_info': SI,
                            f'{agent}{vis_labels[visible]}_spatial_info_shuff': shuff_SI,
                            f'{agent}{vis_labels[visible]}_percentile_map': percentile_map,
                            f'{agent}{vis_labels[visible]}_mean_firing_rate': mean_fr}
            else:
                print(f'{agent} not found') 
            tmp_df = pd.DataFrame.from_dict(d, 'index')
            df = pd.concat([df, tmp_df], axis=1)
        self.clusters_info = df
        return df
    
    def get_pose(self):
        if not hasattr(self, 'entrance_video'):
                self.get_entrance_video()
                self.load_sync_devices()
                self.align_sync_devices()

        # load pose data
        assert hasattr(self, 'entrance_labels'), f'No entrance pose labels found'
        pose, parts = get_pose_from_file(self.entrance_labels)
        P = pose_array(pose.copy(), likelihood_cutoff=0.8)

        # align frame times
        assert hasattr(self, 'entrance_video'), f'No entrance video found'
        camera_sync = self.get_sync_device('camera')
        sync_coeffs = camera_sync.drift_coeffs[0].coeffs
        frame_times = np.arange(0,P.shape[-1]) / camera_sync.sample_rate
        frame_times = np.polyval(sync_coeffs, frame_times)

        # apply camera transform
        C = Camera('entrance', self.entrance_video)
        warped_pose = []
        for i in range(P.shape[0]):
            points = P[i,:-1,:].squeeze().T
            warped_pose.append(C.apply_transform(points))
        warped_pose = np.stack(warped_pose, axis=0)
        return frame_times, warped_pose, camera_sync.sample_rate

    def get_entrance_pose(self):
        frame_times, warped_pose, fs = self.get_pose()

        # get head data
        head_angle = get_head_angle(warped_pose)
        head_position = get_head_position(warped_pose, head_angle)
        head_position, head_velocity = smooth_head_position(head_position, frame_times, dt=1/fs, return_velocity=True)
        
        # return as dataframe
        entrance_coordinates = np.array(get_entry_box_coordinates())
        entrance_coordinates[0,0] = 0.01
        entrance_coordinates[3,0] = 0.01
        pose_df = pd.DataFrame()
        pose_df['prey_location'] = head_position.tolist()
        pose_df['prey_velocity'] = head_velocity.tolist()
        pose_df['prey_rotation'] = head_angle.tolist()
        pose_df['time_stamp'] = frame_times.tolist()
        pose_df['prey_in_box'] =  contains(head_position, get_entry_box_coordinates()).tolist()
        pose_df['prey_in_entrance'] = contains(head_position, entrance_coordinates).tolist()
        pose_df['prey_tracked_in_entrance'] = (~np.all(np.isnan(np.vstack(pose_df['prey_location'].values)),axis=1)).tolist()
        pose_df['entrance_cam_frame'] = np.ones(head_angle.shape).tolist()
        return pose_df
        

    def get_behavior_dataframe(self, remove_bad_frames=True):
        # get arena data and reformat
        _, arena_df = self.recording_episodes_to_dict(return_data=True)
        arena_df = clean_df_locations(arena_df)
        arena_df['prey_tracked_in_arena'] = ~np.isnan(arena_df['prey_location_x'])
        arena_df['predator_tracked_in_arena'] = ~np.isnan(arena_df['predator_location_x'])

        try:
            # get arena data and reformat
            entry_df = self.get_entrance_pose()
            entry_df = clean_df_locations(entry_df)

            # remove pose entries where the head wasnt tracked or if it was tracked outside of the entrance area
            entry_df = entry_df[entry_df['prey_in_entrance'] == True]
            entry_df = entry_df[entry_df['prey_tracked_in_entrance'] == True]

            # remove pose entries where the mouse was also tracked in the arena
            entry_df = entry_df[~get_matched_times(np.vstack(entry_df['time_stamp']), 
                                                   np.vstack(arena_df['time_stamp'][arena_df['prey_tracked_in_arena']]))]

            # merge
            df = pd.concat([arena_df, entry_df], ignore_index=True)
            df = df.sort_values(by='time_stamp').reset_index()
        except Exception as e:
            print(f'{e}: could not add entrance pose')
            df = arena_df

        if remove_bad_frames:
            # remove bad frames from merged data
            v = get_velocity(np.vstack([df['prey_location_x'],df['prey_location_y']]).T, df['time_stamp'])
            df['prey_location_x'][v>3] = np.nan; df['prey_location_y'][v>3] = np.nan

        return df
    
    
    
    def remove_outlier_frames(self):
        agents = self.trajectory_dict.keys()
        for agent in agents:
            outliers = self.trajectory_dict[agent]['outlier_frames']
            for key in self.trajectory_dict[agent].keys():
                if ('occupancy' not in key) & ('coverage' not in key):
                    self.trajectory_dict[agent][key] = self.trajectory_dict[agent][key][outliers == False]


    def get_good_cells(self, fr_cutoff=0.1, use_ks_label=True):
        if 'prey_mean_firing_rate' in self.clusters_info.columns:
            fr_include = self.clusters_info.prey_mean_firing_rate > fr_cutoff
        else:
            fr_include = self.clusters_info.fr > fr_cutoff
        if use_ks_label:
            index = (self.clusters_info.KSLabel == 'good') & fr_include
        else:
            index = self.clusters_info.good_unit & fr_include
        return self.clusters_info[index].copy()
    
    
    def get_place_cells(self, agent='prey', value='spatial_info', info_cutoff=0.5, fr_cutoff=0.1, use_ks_label=True):
        good_cells = self.get_good_cells(fr_cutoff=fr_cutoff, use_ks_label=use_ks_label)
        return good_cells[(good_cells[f'{agent}_place_cell'] == True) & (good_cells[f'{agent}_{value}'] > info_cutoff)]
    

    def get_place_cell_channel_groups(self, cutoff=0.5):
        lfp_channel_map = self.get_channel_map(order='lfp')[0]
        channel_groups = cluster_probe_channels(lfp_channel_map)
        place_cell_channels = self.get_place_cells(cutoff=cutoff).ch.values.astype(int)
        return np.sort(np.argsort([np.sum(np.in1d(place_cell_channels, lfp_channel_map[channel_groups == g,0])) for g in np.unique(channel_groups)])[3:])


    def get_ca1_channels(self, ripple_distance=200, close_file=True, cutoff=0.5, time_index=None, plot=False, return_bad_channels=False):
        if not hasattr(self, 'binary_file'):
            self.open_binary_file()
        
        lfp_channel_map = self.get_channel_map(order='lfp')[0]
        channel_groups = cluster_probe_channels(lfp_channel_map)
        groups_index = np.unique(channel_groups)
        if len(groups_index) > 4:
            groups_index = self.get_place_cell_channel_groups(cutoff=cutoff)

        fs = self.binary_ops['fs']
        if time_index is None:
            time_index = range(fs*10)
        lfp_data = self.binary_file[time_index]
        if close_file:
            self.close_binary_file()

        x_ripple = filter_torch(lfp_data, [150, 250], order=1)
        bad_channels = get_bad_channels(x_ripple)
        ripple_power = rms_torch(x_ripple)
        ripple_power[bad_channels] = np.nan

        # find peak ripple power
        peak_channels = []
        for i,g in enumerate(groups_index):
            x0 = ripple_power[channel_groups == g].cpu()
            x = x0 - np.nanmin(x0)
            # x = gaussian_smoother(x, sd=1)
            pks, _ = find_peaks(x, prominence=1, distance=30)
            if plot:
                plt.plot(x); plt.plot(pks, x[pks], 'r.')
            smooth_max = lfp_channel_map[channel_groups == g,-2:][np.max(pks)]
            dists = distance(smooth_max, lfp_channel_map[channel_groups == g,-2:], axis=1)
            si = np.argsort(dists)
            true_max = si[np.argmax(x0[si[0:10]])]
            peak_channels.append(lfp_channel_map[channel_groups == g,:][true_max])
        peak_channels = np.vstack(peak_channels)

        # use only channels nearby those with high ripple power to target CA1
        ripple_channels = []
        for shank in range(4):
            channel_distance = distance(peak_channels[shank,1:], lfp_channel_map[:,1:])
            ripple_channels.extend(lfp_channel_map[channel_distance < ripple_distance,0])

        # remove bad channels
        _, a, b = np.intersect1d(ripple_channels, bad_channels, return_indices=True)
        ripple_channels = np.delete(ripple_channels, a)
        self.channels = {'peak_ripple_channels': peak_channels,
                         'all_ripple_channels': ripple_channels,
                         'bad_channels': bad_channels}

        if close_file:
            self.close_binary_file()

        if return_bad_channels:
            return peak_channels, ripple_channels, bad_channels
        else:
            return peak_channels, ripple_channels
    
    
    def calculate_amplitude(self, sd=0.004, chunk_time=20, band='ripple', method='sum', channels=[0], duration=None, probe=None):
        if probe is None:
            fn = self.binary_files[0]
        else:
            fn = [b for b in self.binary_files if probe in b][0]
        self.close_binary_file()
        self.open_binary_file(fn)
        lfp_channel_map = self.get_channel_map('lfp')[0]
        I = channel_to_lfp(channels, lfp_channel_map)
        fs = self.binary_ops['fs']
        if duration is None:
            duration = int(self.binary_file.shape[0] / fs) #np.ceil(self.binary_ops['runtime'])
        n_chunks = int(np.ceil(duration / chunk_time))
        chunk_size = fs * chunk_time
        amps = []
        for i in tqdm(range(n_chunks)):
            chunk = (i*chunk_size, np.min([i*chunk_size + chunk_size, self.binary_file.shape[0]]))
            lfp = self.binary_file[chunk[0]:chunk[1]]
            if band == 'ripple':
                amps.append(get_ripple_amplitude(lfp[I,:], method=method, sd=sd, fs=fs))
            else:
                amps.append(get_amplitude(lfp[I,:], sd=sd, fs=fs, band=band, method=method))
        self.close_binary_file()
        if len(amps[0].shape) == 1:
            return np.hstack(amps)
        else:
            return np.vstack(amps).T
        
    def calculate_rms_amplitude(self, chunk_time=20, band=[6,12], channels=range(0, 384), duration=None, probe=None, verbose=False):
        if probe is None:
            fn = self.binary_files[0]
        else:
            fn = [b for b in self.binary_files if probe in b][0]
        self.close_binary_file()
        self.open_binary_file(fn)
        fs = self.binary_ops['fs']
        if duration is None:
            duration = int(self.binary_file.shape[0] / fs) #np.ceil(self.binary_ops['runtime'])
        n_chunks = int(duration / chunk_time)
        chunk_size = fs * chunk_time
        amps = []
        for i in tqdm(range(n_chunks), disable=not verbose):
            chunk = (i*chunk_size, np.min([i*chunk_size + chunk_size, self.binary_file.shape[0]]))
            lfp = self.binary_file[chunk[0]:chunk[1]]
            amps.append(get_rms_amplitude(lfp[channels,:], band=band))
        self.close_binary_file()
        if len(amps[0].shape) == 1:
            return np.hstack(amps)
        else:
            return np.vstack(amps).T
    
    
    def load_classifier_results(self, fn):
        with open(fn, 'rb') as fid:
            [data, binned_data, results, ops] = pickle.load(fid)
        p_location = []
        p_state = []
        for r in tqdm(results['cv_results']['results']):
            p_state.append(r.acausal_posterior.sum('x_position').sum('y_position'))
            p_location.append(r.acausal_posterior.sum('state').values)
        self.classifier_data = data
        self.classifier_location_posterior = np.vstack(p_location)
        self.classifier_state_posterior = np.vstack(p_state)
        self.classifier_ops = ops
        self.classifier_environment = results['cv_results']['classifiers'][0].environments[0]
        self.classifier_error = results['dist_error']
        self.classifer_map_estimate = results['map_estimate']


def load_world(occlusions):
    return 

def parse_experiment_name(experiment_name=str):
    splitter = experiment_name.split('_')
    experiment_info = {'prefix': splitter[0], 
                        'date': splitter[1], 
                        'time': splitter[2],
                        'mouse': splitter[3],
                        'world': '_'.join(splitter[4:-1]),
                        'suffix': splitter[-1]}
    return experiment_info

def plot_syncs(x,y):

    fig,ax = plt.subplots(2,2)

    if len(x) == len(y):
        ax[0,0].plot(x, y)
        ax[1,0].plot(x - y)
        ax[1,1].hist((x - y))
    else:
        ax[0,0].set_title('Mismatch in sync event counts')

    ax[0,1].plot(x[:-1], np.diff(x),'ro')
    ax[0,1].plot(y[:-1], np.diff(y),'k.')
    ax[0,1].set_ylim((0,1.2))
    ax[0,1].set_xlim([x.max()-4.5, x.max()+0.5])

    return fig, ax

def plot_diff(x, **kwargs):
    h = plt.plot(x[:-1], np.diff(x), '.', **kwargs)
    return h

def plot_place_map(R:Recording, u=0):
    pass

def plot_place_maps(R:Recording, u=0):
    pass
    
def load_recording(spike_folder, 
                   results_path='D:/chris-lab/projects/cellworld_npx/data', 
                   suffix='_visibility_recording_smooth'):
    spike_paths, behavior_paths = match_session_paths(spike_folder, sort=True)
    R = Recording(spike_paths, behavior_paths)
    fn = f'{results_path}/{R.experiment_name}{suffix}.pkl'
    R = load_recording_from_file(fn)
    return R

def load_recording_from_file(fn):
    if os.path.exists(fn):
        with open(fn, 'rb') as fid:
            R = pickle.load(fid)
    else:
        print(f'Recording file {fn} not found!')
        return None
    return R

def is_continous_path(path):
    return 'continuous.dat' in os.listdir(path)









