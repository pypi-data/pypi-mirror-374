# from npyx import templates, trn, read_metadata, wvf, curve_fit
from json_cpp import JsonObject, JsonList
from scipy.signal import find_peaks, butter, filtfilt
from scipy.stats import pearsonr
from scipy.optimize import curve_fit
from .probe import get_channel_map, get_shank
from .lfp import get_binary_file
from .io import find_file, walk_back
from tqdm import tqdm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import pickle
import torch


class Population(JsonList):
    def __init__(self):
        super().__init__(list_type=Cluster)

    def save(self, fn):
        with open(fn, 'wb') as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)
    

class SpikeQualities(JsonObject):
    def __init__(self):
        self.nspikes = int()
        self.fr = float()
        self.amp = float()
        self.peak_chan = int()
        self.peaks = list()
        self.troughs = list()
        self.troughs_distance = list()
        self.spatial_decay = float()
        self.spatial_decay_params = list()
        self.spike_width = float()
        self.spike_duration = float()
        self.template_snr = float()
        self.waveform_snr = float()
        self.presence_ratio = float()
        self.refractory_violations = float()
        self.median_corr = float()

        
class Cluster(JsonObject):

    def __init__(self, dp=str, u=int, type='binary_waveform', binary_file=None, hp_filter=True, whiten=True, dshift=True):

        self.root = dp
        self.u = u
        self.type = type
        if self.type == 'binary_waveform':
            binary_open = False
            if binary_file is None:
                binary_open = True
                self.binary_file, self.ks_ops = get_binary_file(dp, return_ops=True, hp_filter=hp_filter, whiten=whiten, dshift=dshift)
            else:
                self.binary_file, self.ks_ops = binary_file
            self.fs = self.ks_ops['fs']
            self.duration = int(self.binary_file.shape[0] / self.fs)
            self.order = 'lfp'
        else:
            pass
            # self.duration = read_metadata(dp)['recording_length_seconds']
            # self.fs = read_metadata(dp)['highpass']['sampling_rate']
            # self.order = 'spike'
        self.probe_name = self.get_probe_name()
        self.spikes = self.get_spikes()
        self.isi_histogram = self.get_isi_histogram()
        self.waveforms = self.get_waveforms()
        self.peak_chan = self.get_peak_chan()
        self.depth = self.get_depth()
        self.position = self.get_position()
        self.shank = self.get_shank()
        self.waveform = np.nanmean(self.waveforms[:,:,:],axis=0).squeeze()
        self.waveform_std = np.nanstd(self.waveforms[:,:,:],axis=0).squeeze()
        self.isi_violations = np.sum((np.diff(self.spikes) / self.fs) < 0.001) / len(self.spikes)
        self.qualities = SpikeQualities()
        if binary_open:
            del self.binary_file
            del self.ks_ops
        torch.cuda.empty_cache() 
        #self.get_quality_metrics()

    def get_spikes(self):
        spikes = np.load(os.path.join(self.root, 'spike_times.npy'))
        clust = np.load(os.path.join(self.root, 'spike_clusters.npy'))
        #return trn(self.root, self.u)
        return spikes[clust == self.u]

    def get_waveforms(self, n=100, remove_outliers=True):
        if self.type == 'waveform':
            pass
            # waveforms = wvf(self.root, self.u, n_waveforms=n, 
            #                 selection=selection, periods=periods, hpfilt=hpfilt)
            # if filter:
            #     waveforms = filter_waveforms(waveforms)
        elif self.type == 'binary_waveform':
            waveforms = self.get_binary_waveforms(n)
        else:
            pass
            # waveforms = templates(self.root, self.u)
        if remove_outliers:
            wave_amps = np.max(np.abs(waveforms[:,:,:]),axis=1).sum(1)
            wave_ampz = (wave_amps - np.nanmean(wave_amps)) / np.nanstd(wave_amps)
            outliers = wave_ampz > 3
            waveforms[outliers,:,:] = np.nan
        return waveforms
    
    def get_binary_waveforms(self, n=100):
        spikes = self.spikes[self.spikes > self.binary_file.nt0min]
        spikes = spikes[spikes < (self.duration*self.fs - self.binary_file.nt)]
        waveforms = np.zeros((n, self.ks_ops['nt']+1, self.ks_ops['n_chan_bin']))
        if len(spikes) > 0:
            spike_times = np.random.choice(spikes, n)
            for i, t in enumerate(spike_times):
                tmin = t - self.binary_file.nt0min
                tmax = t + (self.binary_file.nt - self.binary_file.nt0min) + 1
                wvf = self.binary_file[tmin:tmax].cpu().numpy().T
                waveforms[i,:,:] = wvf
        return waveforms
    
    def get_probe_name(self):
        if 'continuous.dat' in os.listdir(self.root):
            return os.path.split(self.root)[-1]
        else:
            return os.path.split(find_file(self.root, 'continuous.dat')[0])[-1]

    def get_peak_chan(self):
        return np.argsort(np.nanmean(self.waveforms, axis=0).min(0))[0]
    
    def get_depth(self, chanI=None):
        if chanI is None and hasattr(self, 'peak_chan'):
            chanI = self.peak_chan
        #subcm = predefined_chanmap(probe_version='1.0')
        subcm = get_channel_map(get_settings_file(self.root), order=self.order)
        return subcm[chanI,-1]
    
    def get_position(self, chanI=None):
        if chanI is None and hasattr(self, 'peak_chan'):
            chanI = self.peak_chan
        subcm = get_channel_map(get_settings_file(self.root), order=self.order)
        return subcm[chanI,-2:]
    
    def get_shank(self, chanI=None):
        if chanI is None and hasattr(self, 'peak_chan'):
            chanI = self.peak_chan
        pos = self.get_position(chanI)
        if len(pos.shape) == 1:
            return get_shank(pos[0])
        else:
            return get_shank(pos[:,0])

    def get_n_channels(self):
        #return predefined_chanmap(probe_version='1.0').shape[0]
        return get_channel_map(get_settings_file(self.root), order=self.order).shape[0]
    
    def get_channel_index(self, N=16, distance=True):
        if not distance:
            if not hasattr(self, 'peak_chan'):
                I = self.get_peak_chan()
            else:
                I = self.peak_chan
            n_channels = self.get_n_channels()
            chStartI = int(max(I - N/2 + 1, 0))
            chStartI = int(min(chStartI, n_channels-N-1))
            chEndI = int(chStartI + N)
            assert chEndI <= n_channels-1
            return np.arange(chStartI, chEndI)
        else:
            return self.get_closest_channels(N)
        
    def get_isi_histogram(self, bin=None, range=None):
        if bin is None:
            bin = 1.0
        if range is None:
            range = 50.0
        bins = np.arange(0, range+bin, bin)
        if len(self.spikes) == 0:
            spikes = self.get_spikes()
        else:
            spikes = self.spikes
        return np.histogram(np.diff(spikes/self.fs*1000), bins)
    
    def get_closest_channels(self, N=16):
        if not hasattr(self, 'peak_chan'):
            I = self.get_peak_chan()
        else:
            I = self.peak_chan
        peak_loc = self.get_channel_locations(I)
        subcm = get_channel_map(get_settings_file(self.root), order=self.order)
        dist = np.sqrt(np.sum((subcm[:,1:] - peak_loc)**2, axis=1))
        return np.argsort(dist)[0:N]

    def get_channel_locations(self, chanI):
        #subcm = predefined_chanmap(probe_version='1.0')
        subcm = get_channel_map(get_settings_file(self.root), order=self.order)
        return subcm[chanI,1:]
    
    def get_peak_waveforms(self, N=16):
        chanI = self.get_channel_index(N)
        return self.waveforms[:,:,chanI]

    def get_peak_waveform(self, N=16):
        chanI = self.get_channel_index(N)
        if not hasattr(self, 'waveforms') or (len(self.waveforms) == 0):
            return self.waveform[:,chanI].squeeze()
        else:
            return np.nanmean(self.waveforms[:,:,chanI],axis=0).squeeze()
    
    def get_peak_waveform_std(self, N=16):
        chanI = self.get_channel_index(N)
        if not hasattr(self, 'waveforms') or (len(self.waveforms) == 0):
            return self.waveform_std[:,chanI].squeeze()
        else:
            return np.nanstd(self.waveforms[:,:,chanI],axis=0).squeeze()
    
    def normalize_waveform(self, N=1):
        pkwvf = self.get_peak_waveform(N)
        off = np.nanmean(pkwvf[0:20])
        div = np.nanmax(np.abs(pkwvf))
        return (pkwvf - off) / div
    
    def plot_waveforms(self, N=16, n_waveforms=100, color='tab:blue', channels=False, title=None,
                       scalerx=5, scalery=10, hpfilt=300, subtract_offset=True, ax=None):

        if ax is None:
            _,ax = plt.subplots(1,1,figsize=(2,5))
        
        chanI = self.get_channel_index(N)
        data = self.get_peak_waveforms(N)[0:n_waveforms,:,:]
        _, n_samples, n_channels = self.waveforms.shape
        data=data[~np.isnan(data[:,0,0]),:,:]
        subcm = get_channel_map(get_settings_file(self.root), order=self.order)
        subcm = subcm[:n_channels,:]

        # filter data
        if hpfilt > 0:
            for i in range(data.shape[0]):
                for j in range(data.shape[-1]):
                    data[i,:,j] = butter_highpass_filter(data[i,:,j].squeeze(), hpfilt, 30000, order=3)
                    if subtract_offset:
                        data[i,:,j] = data[i,:,j] - np.median(data[i,0:20,j].squeeze())

        
        t = np.arange(n_samples) / scalerx
        if self.type == 'waveform':
            yoff = -200/scalery
            ax.plot(np.array([0, int(0.001*30000)]) / scalerx + subcm[chanI,1].min(), 
                np.array([0,0]) + subcm[chanI,2].min() + yoff, 'k')
            ax.text(int(-0.0001*30000) / scalerx + subcm[chanI,1].min(), 
                    50 / scalery + subcm[chanI,2].min() + yoff,
                    '100uV', size=10, ha='right', va='center', rotation=90)
            ax.plot(np.array([0,0]) / scalerx + subcm[chanI,1].min(), 
                    np.array([0, 100 / scalery]) + subcm[chanI,2].min() + yoff, 'k')
            if channels:
                ax.text(int(0.0005*30000) / scalerx + subcm[chanI,1].min(), 
                        -10 / scalery + subcm[chanI,2].min() + yoff,
                        '1ms', size=10, ha='center', va='top')
            
        for i in np.arange(len(chanI)):
            x = t + subcm[chanI[i],1]
            y = data[:,:,i] / scalery + subcm[chanI[i],2]
            ax.plot(x, y.T, linewidth=1, color=color, alpha=0.05)
            ax.plot(x, np.nanmean(y.T,axis=1), color=color, linewidth=2)
            if channels:
                ax.text(subcm[chanI[i],1]-1, subcm[chanI[i],2], int(subcm[chanI[i],0])+1, size=10, ha='right', va='center')
        if title is not None:
            if type(title) is str:
                ax.set_title(title)
            else:
                ax.set_title(self.u)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.axis('off')

        return ax

    def plot_acg(self, ax=None, title=False, bin=None, range=None, **kwargs):
        if ax is None:
            _,ax = plt.subplots(1,1,figsize=(2,2))
        if not hasattr(self, 'isi_histogram') or ((bin is not None) or (range is not None)):
            hist = self.get_isi_histogram(bin=bin, range=range)
        else:
            hist = self.isi_histogram
        width = np.nanmean(np.diff(hist[1]))
        plt.bar(hist[1][:-1] + width/2, hist[0], width=width, **kwargs)
        if title:
            ax.set_title(title)
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Spike Count')
        return ax
    
    def plot_cluster(self, N=16, color='tab:blue', scalerx=5, scalery=1, ax=None, 
                     channels=False, title=False, std=True):

        if ax is None:
            _,ax = plt.subplots(1,1,figsize=(1,7))
        if self.type == 'template':
            scalery = scalery / 40
            scalerx = scalerx / 2

        chanI = self.get_channel_index(N)
        n_samples, n_channels = self.waveform.shape
        datam = self.waveform[:,chanI]
        datastd = self.waveform_std[:,chanI]
        # data=data[~np.isnan(data[:,0,0]),:,:]
        # datam = np.mean(data,0)
        # datastd = np.std(data,0)
        #subcm = predefined_chanmap(probe_version='1.0')
        subcm = get_channel_map(get_settings_file(self.root), order=self.order)
        subcm = subcm[:n_channels,:]

        # plot
        t = np.arange(n_samples) / scalerx

        if self.type == 'waveform':
            ax.plot(np.array([0, int(0.001*30000)]) / scalerx + subcm[chanI,1].min(), 
                np.array([0,0]) + subcm[chanI,2].min(), 'k')
            ax.text(int(-0.0001*30000) / scalerx + subcm[chanI,1].min(), 
                    50 / scalery + subcm[chanI,2].min(),
                    '100uV', size=10, ha='right', va='center', rotation=90)
            ax.plot(np.array([0,0]) / scalerx + subcm[chanI,1].min(), 
                    np.array([0, 100 / scalery]) + subcm[chanI,2].min(), 'k')
            if channels:
                ax.text(int(0.0005*30000) / scalerx + subcm[chanI,1].min(), 
                        -10 / scalery + subcm[chanI,2].min(),
                        '1ms', size=10, ha='center', va='top')
        for i in np.arange(len(chanI)):
            x = t + subcm[chanI[i],1]
            y = datam[:,i] / scalery + subcm[chanI[i],2]
            ax.plot(x, y, linewidth=1, color=color)
            if std:
                yu = (datam[:,i]+datastd[:,i]) / scalery + subcm[chanI[i],2]
                yl = (datam[:,i]-datastd[:,i]) / scalery + subcm[chanI[i],2]
                ax.plot(x, yu, alpha=0.5, linewidth=0.5, color=color)
                ax.plot(x, yl, alpha=0.5, linewidth=0.5, color=color)  
                ax.fill_between(x, yl, yu, interpolate=True, alpha=0.2, color=color)
            if channels:
                ax.text(subcm[chanI[i],1]-1, subcm[chanI[i],2], int(subcm[chanI[i],0])+1, size=10, ha='right', va='center')
        if title:
            ax.set_title(f'{self.u} - {self.good_unit}')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.axis('off')

        return ax

    def get_waveform_snr(self):
        signal = np.abs(self.get_peak_waveform(1).squeeze()).max()
        noise = np.abs(self.get_peak_waveform_std(1).squeeze()[40:60]).mean()
        return signal / noise

    def get_peaks(self, scale=7, plot=False, height=1) -> list:
        wv = self.get_peak_waveform(1)
        peaks, _ = find_peaks(wv, height=height, prominence=np.ptp(wv)/scale)
        if plot:
            plt.plot(wv)
            plt.plot(peaks, wv[peaks], '.')
        return peaks.tolist(), wv[peaks].tolist()
    
    def get_troughs(self, scale=7, plot=False, height=1) -> list:
        wv = self.get_peak_waveform(1)
        troughs, _ = find_peaks(-wv, height=height, prominence=np.ptp(wv)/scale)
        if plot:
            plt.plot(wv)
            plt.plot(troughs, wv[troughs], '.')
        return troughs.tolist(), wv[troughs].tolist()
    
    def get_troughs_distance(self, scale=7, center=20, height=1) -> list:
        wv = self.get_peak_waveform(1)
        troughs, _ = find_peaks(-wv, height=height, prominence=np.ptp(wv)/scale)
        if center is None:
            center = int(len(wv)/2)
        sorti = np.argsort(-wv[troughs])
        if len(troughs) < 1:
            return [np.inf]
        else:
            return np.abs(troughs[sorti] - center) / self.fs

    
    def get_spike_width(self, interp=500, plot=False):
        # full width at half max
        wv = self.get_peak_waveform(1)
        t = np.arange(0, len(wv))
        ti = np.linspace(0, len(wv), interp)
        wvi = np.interp(ti, t, wv)
        amx = np.nanargmax(-wvi)
        mx = wvi[amx]
        diff = np.abs(wvi - mx/2)
        pre_diff = diff.copy()
        pre_diff[amx:] = np.nan
        post_diff = diff.copy()
        post_diff[:amx] = np.nan
        if plot:
            plt.plot(ti,wvi)
            I = np.nanargmin(post_diff)
            plt.plot(ti[I], wvi[I], '.')
            I = np.nanargmin(pre_diff)
            plt.plot(ti[I], wvi[I], '.')
            plt.axvline(ti[amx])
        try:
            return (ti[np.nanargmin(post_diff)] - ti[np.nanargmin(pre_diff)]) / self.fs
        except:
            return 0
        
    def get_spike_duration(self):
        # largest negative peak to next positive peak
        wv = self.get_peak_waveform(1)
        amx = np.nanargmax(-wv)
        mx = wv[amx]
        pks, _ = self.get_peaks()
        pks = np.array(pks)
        if any(pks > amx):
            return (pks[pks > amx][0] - amx) / self.fs
        else:
            return np.nan

    def get_refractory_violations(self, isi_thresh=1.5, isi_min=0):
        # isi violation rate according to Hill et al., 2011
        isi = (np.diff(self.spikes) / self.fs) * 1000
        nv = np.sum(isi < isi_thresh)
        n = len(isi)
        if (n == 0): n = 1e-5
        return (nv * self.duration) / (2 * n**2 * (isi_thresh - isi_min))
    
    def get_spatial_decay(self, N=64, method='gauss', plot=False):
        def gaussian(x, offset, amplitude, mean, stddev):
            return offset + amplitude * np.exp(-((x - mean) / 4 / stddev)**2)
        def SSE(x, y, B):
            resid = gaussian(x, *B) - y
            return np.sum(resid**2)
        def try_fit(func, x, y, p0, bounds, maxfev=5000):
            try: 
                p, _ = curve_fit(func, x, y, p0=p0, maxfev=maxfev, bounds=bounds)
                sse = SSE(x, y, p)
            except:
                p = [np.nan, np.nan, np.nan, np.nan]
                sse = np.inf
            return p, sse

        
        wv = self.get_peak_waveform(N=N).squeeze()
        if 'exp' in method:
            # fits exponential slope of amplitude decay of sorted surrounding channels
            y = np.sort(wv.max(0))
            x = np.arange(len(y))
            yl = np.log(y)
            B0 = np.polyfit(x[~np.isnan(yl)], yl[~np.isnan(yl)], 1, w=np.sqrt(y[~np.isnan(yl)]))

            return B0[0], B0
        
        elif 'gauss' in method:
            # fits gaussian of amplitude decay of ordered surrounding channels
            cx = self.get_channel_locations(self.get_channel_index(N=N))[:,1]
            p = np.diff(np.sort(cx))
            pitch = np.nanmin(p[p>0])
            y = np.max(np.abs(wv),axis=0) #wv.max(0)
            y = np.convolve(y, np.ones(3)/3, mode='same')
            x = np.arange(len(y)) + 1
            bounds = (0, [np.max(y), np.inf, N, 20])
            #mean = sum(x * y) / sum(y)
            #sigma = np.sqrt(sum(y * (x - mean)**2) / sum(y))
            
            B = []
            sse = []
            # first guess is center
            b, s = try_fit(gaussian, x, y, p0=(np.nanmax([np.nanmin(y), 0.01]), np.ptp(y), N/2, 1), 
                           maxfev=5000, bounds=bounds)
            B.append(b); sse.append(s)
            
            # second guess is argmax
            b, s = try_fit(gaussian, x, y, p0=(np.nanmax([np.nanmin(y), 0.01]), np.ptp(y), np.nanmin([np.nanargmax(y) + 1, len(y)]), 1), 
                           maxfev=5000, bounds=bounds)
            B.append(b); sse.append(s)

            # use best guess
            B0 = B[np.nanargmin(sse)]
            if plot:
                plt.plot(x,y)
                plt.plot(gaussian(x, B0[0], B0[1], B0[2], B0[3]))

            return B0[-1]*pitch, B0
        
        else:
            print('WARNING: method must be "exp" or "gauss"')

    def get_spatial_snr(self, N=64):
        wv = self.get_peak_waveform(N=N).squeeze()
        y = np.nanmax(np.abs(wv),axis=0)
        yz = (y - np.nanmean(y)) / np.nanstd(y)

    def get_presence_ratio(self, win=60.0):
        bins = np.arange(0, self.duration*self.fs, win*self.fs)
        counts = np.histogram(self.spikes, bins)[0]
        return np.sum(counts > 0) / len(counts)
    
    def get_quality_metrics(self):
        q = SpikeQualities()
        q.nspikes = len(self.spikes)
        q.fr = len(self.spikes) / self.duration
        peaks = self.get_peaks()
        q.amp = np.nanmax(np.abs(self.get_peak_waveform(N=1)))
        q.peak_chan = self.peak_chan
        q.peaks = self.get_peaks()[0]
        q.troughs = self.get_troughs()[0]
        q.troughs_distance = self.get_troughs_distance()
        B, B0 = self.get_spatial_decay(method='gauss')
        q.spatial_decay = B
        q.spatial_decay_params = B0
        q.spike_width = self.get_spike_width()
        q.spike_duration = self.get_spike_duration()
        q.waveform_snr = self.get_waveform_snr()
        q.presence_ratio = self.get_presence_ratio()
        q.refractory_violations = self.get_refractory_violations()
        q.median_corr = 1.0 # need to compute waveforms for the rest of the population
        self.qualities = q

        return q
    
    
    def is_good_unit(self, 
                     min_spikes = 100, 
                     spatial_decay_range = (5, 70),      # for gaussian
                     min_offset = 2,                     # for gaussian
                     spike_width_range = (0.05, 1.0),    # ms
                     max_peaks = 2, 
                     max_troughs = 1, 
                     max_troughs_distance = 0.0003,      # s
                     amplitude_range = (1, 40),          # used to be uV but is now whitened
                     min_snr = 1.0, 
                     min_refractory_violations = 0.1, 
                     min_presence_ratio = 0.2,
                     min_correlation = 0.2,
                     again=False):
        if (self.qualities.nspikes == 0) | again:
            self.qualities = self.get_quality_metrics()
        q = self.qualities
        good_unit = [
            (q.nspikes > min_spikes),
            ((q.spatial_decay > spatial_decay_range[0]) & (q.spatial_decay < spatial_decay_range[1])),
            (q.spatial_decay_params[0] < min_offset),
            ((q.spike_width > spike_width_range[0]/1000) & (q.spike_width < spike_width_range[1]/1000)),
            (len(q.peaks) <= max_peaks),
            (len(q.troughs) <= max_troughs),
            (q.troughs_distance[-1] < max_troughs_distance),
            ((q.amp > amplitude_range[0]) & (q.amp < amplitude_range[1])),
            (q.waveform_snr > min_snr),
            (q.refractory_violations < min_refractory_violations),
            (q.presence_ratio > min_presence_ratio),
            (q.median_corr > min_correlation)
        ]
        self.good_unit = all(good_unit)
        self.good_unit_criteria = good_unit
        
        return self
    
    def to_series(self, clust_info=pd.DataFrame):
        c = self
        if clust_info.empty:
            KSLabel = []
            group = []
            probe_name = []
            probe_index = []
        else:
            I = (clust_info.cluster_id == c.u) & (clust_info.probe_name == self.probe_name)
            KSLabel = clust_info[I].KSLabel.values[0]
            group = clust_info[I].group.values[0]
            probe_name = clust_info[I].probe_name.values[0]
            probe_index = clust_info[I].probe_index.values[0]
        
        row = pd.Series()
        row['cluster_id'] = c.u
        row['Amplitude'] = []
        row['ContamPct'] = []
        row['KSLabel'] = KSLabel
        row['amp'] = c.qualities.amp
        row['ch'] = c.qualities.peak_chan
        row['depth'] = c.depth
        row['probe_name'] = probe_name
        row['probe_index'] = probe_index
        row['position'] = c.position
        row['shank'] = c.shank
        row['fr'] = c.qualities.fr
        row['group'] = group
        row['n_spikes'] = c.qualities.nspikes

        # info from SpikeQualities
        row['peaks'] = c.qualities.peaks
        row['troughs'] = c.qualities.troughs
        row['spatial_decay'] = c.qualities.spatial_decay
        row['spatial_decay_params'] = c.qualities.spatial_decay_params
        row['spike_width'] = c.qualities.spike_width
        row['spike_duration'] = c.qualities.spike_duration
        row['template_snr'] = c.qualities.template_snr
        row['waveform_snr'] = c.qualities.waveform_snr
        row['presence_ratio'] = c.qualities.presence_ratio
        row['refractory_violations'] = c.qualities.refractory_violations
        row['median_corr'] = c.qualities.median_corr
        row['good_unit'] = c.good_unit

        # other info that might be handy
        row['peak_waveform'] = c.waveform
        row['peak_waveform_std'] = c.waveform_std
        if hasattr(c, 'isi_violations'):
            row['isi_violations'] = c.isi_violations

        return row


def get_cluster_info(dp):
    info_file = os.path.join(dp, 'cluster_info.tsv')
    group_file = os.path.join(dp, 'cluster_group.tsv')
    ks_file = os.path.join(dp, 'cluster_KSLabel.tsv')
    if os.path.exists(info_file):
        return pd.read_csv(info_file, sep='\t', header=0)
    elif os.path.exists(group_file):
        return check_cluster_groups_file(dp)
    # elif os.path.exists(ks_file):
    #     return pd.read_csv(ks_file, sep='\t', header=0)
    else:
        raise FileNotFoundError(f'cluster info files not found in {dp}... did you run kilosort?')
    
def check_cluster_groups_file(dp):
    clust_ids = get_cluster_ids(dp)
    group_file = os.path.join(dp, 'cluster_group.tsv')
    if os.path.exists(group_file):
        group_info = pd.read_csv(group_file, sep='\t', header=0)
        if 'group' not in group_info.columns:
            # data wasnt curated, rewrite group file
            print(f'data not curated... rewriting {group_file}')
            clust_info = pd.DataFrame()
            clust_info['cluster_id'] = clust_ids
            fixed_ks_labels = [group_info.KSLabel[c] for c in clust_info['cluster_id'] if c in group_info.KSLabel]
            clust_info['group'] = ["unsorted"] * len(clust_ids)
            clust_info['KSLabel'] = fixed_ks_labels
            clust_info.to_csv(os.path.join(dp, "cluster_group.tsv"), sep="\t", index=False)
            return clust_info
        else:
            return group_info
    

def get_cluster_ids(dp):
    clust = np.load(os.path.join(dp, 'spike_clusters.npy'))
    return np.unique(clust)


def load_good_units(dp, remove_spikes=True, type='waveform'):
    P = Population()
    clust_ids = get_cluster_info(dp).cluster_id
    for i in tqdm(clust_ids, desc='Building population (good units)'):
        c = Cluster(dp, i, type=type)
        c = c.is_good_unit()
        if remove_spikes:
            c.spikes = []
            del c.waveforms
            if hasattr(c, 'binary_file'):
                del c.binary_file
            torch.cuda.empty_cache()
        if c.good_unit == True:
            P.append(c)

    return P

def load_all_units(dp, check_good_unit=True, remove_spikes=True, type='waveform', binary_file=None):
    P = Population()
    clust_ids = get_cluster_info(dp).cluster_id
    for i in tqdm(clust_ids, desc=f'Building population (all units from {os.path.split(dp)[-1]})'):
        c = Cluster(dp, i, type=type, binary_file=binary_file)
        if check_good_unit:
            c = c.is_good_unit()
        if remove_spikes:
            # do this if you want to save memory
            c.spikes = []
            del c.waveforms
            if hasattr(c, 'binary_file'):
                del c.binary_file
            torch.cuda.empty_cache()
        P.append(c)
    return P

def calc_good_units(dp, corr_cutoff=0.25, remove_spikes=True, type='waveform', binary_file=None):

    P = load_all_units(dp, check_good_unit=True, remove_spikes=remove_spikes, type=type, binary_file=binary_file)

    wvfs = []
    for c in P:
        wvfs.append(c.normalize_waveform(1))
    median_waveform = np.nanmedian(np.vstack(wvfs), 0)

    for i,c in enumerate(P):
        if np.sum(np.isnan(wvfs[i])) == 0:
            r, _ = pearsonr(wvfs[i], median_waveform)
        else:
            r = np.nan
        c.qualities.median_corr = r
        c.good_unit_criteria = np.append(c.good_unit_criteria, (r > corr_cutoff))
        c.good_unit = all(c.good_unit_criteria)
        P[i] = c
    
    return P

def filter_population(P:Population, cell_criteria:dict):
    P_new = Population()
    for c in P:
        P_new.append(c.is_good_unit(**cell_criteria))
    return P_new

def get_population(spike_path, waveform_type='binary_waveform', save=False, overwrite=False,
                   hp_filter=True, whiten=True, dshift=True):
    if type(spike_path) is not list:
        spike_path = [spike_path]
    population = Population()
    for p in spike_path:
        fn = os.path.join(p, 'population.pkl')
        if not os.path.exists(fn) or overwrite:
            if waveform_type == 'binary_waveform':
                binary_file = get_binary_file(p, return_ops=True, hp_filter=hp_filter, whiten=whiten, dshift=dshift)
            else:
                binary_file = None
            P = calc_good_units(p, type=waveform_type, binary_file=binary_file)
            if save:
                with open(fn, 'wb') as f:
                    pickle.dump(P, f, protocol=pickle.HIGHEST_PROTOCOL)
            del binary_file; torch.cuda.empty_cache()
        elif os.path.exists(fn):
            with open(fn, 'rb') as f:
                P = pickle.load(f)
        population.extend(P)

    return population
        

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def filter_waveforms(data, hpfilt=300, subtract_offset=True):
    for i in tqdm(range(data.shape[0])):
        for j in range(data.shape[-1]):
            data[i,:,j] = butter_highpass_filter(data[i,:,j].squeeze(), hpfilt, 30000, order=3)
            if subtract_offset:
                data[i,:,j] = data[i,:,j] - np.median(data[i,0:20,j].squeeze())
    return data

def get_settings_file(dp):
    settings_file = None
    root = walk_back(dp, 'Record Node')
    settings_file = find_file(root, 'settings.xml', joined=True)
    if len(settings_file) > 0:
        return settings_file[0]
    else:
        raise IOError(f'No settings.xml file in {dp}')

def plot_cluster_labels(population, labels=None, cols=15):
    cols = 15
    rows = int(np.ceil(len(population) / cols))
    fig = plt.figure(figsize=(15, 5*rows))
    probe_index = {'Neuropix-PXI-108.ProbeA': 0,
                'Neuropix-PXI-108.ProbeB': 1}

    for i,c in tqdm(enumerate(population), total=len(population)):
        # c.root = R.spike_path[0]
        ax = fig.add_subplot(rows, cols, i+1)
        color = 'k'
        label = ''
        if labels is not None:
            if labels.loc[i].quality == 'bad':
                color = 'grey'
            label = labels.loc[i].quality
        c.plot_cluster(N=24, scalery=1/2, std=False, color=color, ax=ax)
        ax.set_title(f'{probe_index[c.probe_name]}-{c.u}\n{c.good_unit}\n{label}')