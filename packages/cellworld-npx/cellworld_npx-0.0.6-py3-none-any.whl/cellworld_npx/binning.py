import numpy as np
import pandas as pd
from tqdm import tqdm
import copy

class BinnedRecording(object):
    def __init__(self, RecordingObject, dt=0.005, bins=None, window=None, cluster_ids=None):
        self.recording = RecordingObject
        self.behavior_data = pd.DataFrame()
        self.spikes = pd.DataFrame()
        self.spike_array = None
        self.clusters_info = pd.DataFrame()
        self.cluster_ids = cluster_ids
        self.dt = dt
        self.bins = bins
        self.window = window
        
    def __getitem__(self, key):
        '''custom slicing of BinnedRecording object'''
        if self.spike_array is None:
            raise ValueError("Spike array not initialized. Run load_data() first.")
        new_obj = copy.copy(self)  # shallow copy; we'll replace relevant fields below

        if isinstance(key, tuple):
            row_key, col_key = key
            new_obj.spike_array = self.spike_array[row_key,:][:,col_key].copy()
            new_obj.clusters_info = self.clusters_info.iloc[_normalize_index(col_key, len(self.clusters_info))].copy()
            new_obj.behavior_data = self.behavior_data.iloc[_normalize_index(row_key, len(self.behavior_data))].copy()
        else:
            new_obj.spike_array = self.spike_array[key, :].copy()
            new_obj.behavior_data = self.behavior_data.iloc[_normalize_index(key, len(self.behavior_data))].copy()
        return new_obj
    
    def __len__(self):
        if self.spike_array is None:
            raise ValueError("Spike array not initialized.")
        return self.spike_array.shape[0]

    def get_spike_data(self):
        self.clusters_info = self.recording.clusters_info
        spike_times, clusters, _, probe_index = self.recording.get_spikes()
        self.spikes['spike_times'] = spike_times
        self.spikes['clusters'] = clusters
        self.spikes['probe_index'] = probe_index

    def get_behavior_data(self):
        self.behavior_data = self.recording.get_behavior_dataframe()

    def bin_spikes(self):
        n_clusters = len(self.clusters_info)
        spike_array = np.nan * np.ones((len(self.bins), n_clusters))
        for i in tqdm(range(n_clusters), desc='Binning spikes... ', total=n_clusters):
            spike_times = self.spikes['spike_times'][(self.spikes['clusters'] == self.clusters_info.iloc[i].cluster_id) & 
                                                     (self.spikes['probe_index'] == self.clusters_info.iloc[i].probe_index)]
            spike_array[:,i] = bin_spikes(spike_times, self.bins, self.window)
        return spike_array
    
    def load_data(self):
        self.get_spike_data()
        self.get_behavior_data()
    
    def resample(self, dt=None, window=None):
        if dt is not None:
            self.dt = dt
        if window is not None:
            self.window = window
        self.bins = np.arange(self.spikes['spike_times'].min(), 
                              self.spikes['spike_times'].max(), 
                              self.dt)

        self.spike_array = self.bin_spikes()
        self.behavior_data = bin_dataframe(self.behavior_data, bins=self.bins)

def _normalize_index(idx, N):
    """
    Converts a slice, list of bool, list of ints, or np.ndarray index
    to a valid index for .iloc[]
    """
    if isinstance(idx, slice):
        return range(*idx.indices(N))
    elif isinstance(idx, (list, np.ndarray)):
        idx = np.asarray(idx)
        if idx.dtype == bool:
            # Boolean mask
            if idx.size != N:
                raise IndexError("Boolean index does not match array length.")
            return np.flatnonzero(idx)
        else:
            # List/array of indices
            return idx
    elif isinstance(idx, int):
        return [idx]
    else:
        raise TypeError(f"Unsupported index type: {type(idx)}")
    
def bin_dataframe(df, interval=0.05, bins=None):
    if bins is None:
        bins = np.arange(df['time_stamp'].min(), df['time_stamp'].max(), interval)
    df_grid = pd.DataFrame({'time_stamp': bins})
    df_interp = pd.merge_asof(df_grid, df.sort_values('time_stamp'), on='time_stamp')
    for col in df_interp.columns:
        if col != 'time_stamp':
            df_interp[col] = df_interp[col].interpolate(method='linear')
    return df_interp   

def bin_spikes(spike_times, bin_centers, window_width, sort=False):
    spike_times = np.asarray(spike_times)
    bin_centers = np.asarray(bin_centers)
    if window_width is None:
        half_width = np.mean(np.diff(bin_centers)) / 2
    else:
        half_width = window_width / 2

    if sort:
        spike_times = np.sort(spike_times)

    left_edges = bin_centers - half_width
    right_edges = bin_centers + half_width

    left_idxs = np.searchsorted(spike_times, left_edges, side='left')
    right_idxs = np.searchsorted(spike_times, right_edges, side='right')

    counts = right_idxs - left_idxs
    return counts

def filter_dataframe(df, filters:dict):
    filter_expr = ' & '.join([f"(df['{k}'] {v})" for k, v in filters.items()])
    return df[eval(filter_expr)]

def make_map_bins(ideal_bin_width=0.10, bin_range=(-0.05, 1.05), canonical_to_m=2.34, scaler=1, return_canonical=True):
    # range typically is (0,1) but in NPX hab there is extra space at either entrance
    bin_range = np.array(bin_range) * scaler
    n_bins = int(np.ceil((bin_range[1]*canonical_to_m - bin_range[0]*canonical_to_m) / ideal_bin_width))
    # n_bins = int(np.round((2.34*scaler) / ideal_bin_width))
    if return_canonical:
        bins = np.linspace(bin_range[0], bin_range[1], n_bins)
    else:
        bins = np.linspace(bin_range[0]*canonical_to_m, bin_range[1]*canonical_to_m, n_bins)
    bin_width = np.mean(np.diff(bins))
    bin_centers = bins[:-1] + bin_width/2
    return bins, bin_width, bin_centers

