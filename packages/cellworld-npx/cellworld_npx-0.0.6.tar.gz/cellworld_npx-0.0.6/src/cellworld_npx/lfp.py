from matplotlib.colors import TwoSlopeNorm
from kilosort.io import BinaryFiltered, load_ops
from pathlib import Path, WindowsPath
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, decimate
from sympy.ntheory import factorint
from torch.fft import fft, ifft, fftshift
from .probe import channel_to_lfp # keep this to use from this module
from .io import walk_back, find_file
from tqdm import tqdm
import numpy as np
import torch
import torchaudio
from torchaudio.transforms import Resample
import os
import gc

def get_binary_file(binary_file, return_ops=False, hp_filter=False, whiten=False, dshift=False):
    device = torch.device('cuda')
    binary_file, ops_file = find_binary_file(binary_file)
    ops = load_ops(ops_file)
    chan_map = ops['chanMap']
    if hp_filter:
        hp_filter = ops['fwav']
    else:
        hp_filter = None
    if whiten:
        whiten = ops['Wrot']
    else:
        whiten = None
    if dshift:
        dshift = ops['dshift']
    else:
        dshift=None
    bfile = BinaryFiltered(binary_file, n_chan_bin=ops['n_chan_bin'], 
                           chan_map=chan_map, device=device,
                           hp_filter=hp_filter, 
                           whiten_mat=whiten, 
                           dshift=dshift)
    if return_ops:
        return bfile, ops
    else:
        return bfile
    
def find_binary_file(original_file):
    if type(original_file) == WindowsPath:
        original_file = str(original_file)
    if 'continuous.dat' in original_file:
        binary_file = original_file
    elif 'continuous.dat' in os.listdir(original_file):
        binary_file = Path(original_file) / 'continuous.dat'
    else:
        root_path = walk_back(original_file, 'Record Node')
        binary_file = find_file(root_path, 'continuous.dat', joined=True)
        assert binary_file is not None, f'continuous.dat not found in {binary_file}'
        assert len(binary_file) == 1, f'multiple continuous.dat files found in {binary_file}, check your folder structures'
        binary_file = binary_file[0]
    ops_file = find_file(os.path.split(binary_file)[0], 'ops.npy', joined=True)
    if ops_file is None:
        # if ops.npy is not in the binary path, look backwards for it
        root_path = walk_back(binary_file, 'Record Node')
        ops_file = find_file(root_path, 'ops.npy', joined=True)
        assert ops_file is not None, f'no ops.npy file found, run kilosort'
        assert len(ops_file) == 1, f'{len(ops_file)} ops.npy files found, requires a single file'
    ops_file = ops_file[0]
    return str(binary_file), ops_file
    
def get_spike_amplitudes(results_dir, filename=None, dtype='float32', binary_file=None):
    # calculate or load spike amplitudes
    results_dir = Path(results_dir)
    if filename is None:
        fn = results_dir / 'spike_amplitudes.npy'
    else:
        fn = filename
    if not os.path.exists(fn):
        if binary_file is None:
            bfile = get_binary_file(results_dir)
        else:
            bfile = get_binary_file(binary_file)
        spike_times = np.load(results_dir / 'spike_times.npy')
        ops = load_ops(results_dir / 'ops.npy')
        spike_amps = np.zeros((len(spike_times), ops['n_chan_bin']), dtype=dtype)
        for i,t in enumerate(tqdm(spike_times, desc='extracting spike amplitudes')):
            tmin = t - bfile.nt0min
            tmax = t + (bfile.nt - bfile.nt0min) + 1
            spike_amps[i,:] = bfile[tmin:tmax].cpu().numpy()[:,ops['nt0min']]
        np.save(fn, spike_amps.astype(dtype))
        del bfile
        torch.cuda.empty_cache()
        gc.collect()
    else:
        print(f'loading spike amplitudes from {fn}')
        spike_amps = np.load(fn)

    return spike_amps

def get_filter(cutoff, fs=30000, device=torch.device('cuda'), btype='highpass', order=1):
    if type(cutoff) is list:
        btype = 'bandpass'
    
    # a butterworth filter is specified in scipy
    b,a = butter(order, cutoff, fs=fs, btype=btype)

    # a signal with a single entry is used to compute the impulse response
    NT = 30122
    x = np.zeros(NT)
    x[NT//2] = 1

    # symmetric filter from scipy
    filter = filtfilt(b, a, x).copy()
    filter = torch.from_numpy(filter).to(device).float()
    return filter

def filter_to_fft(filter, NT=30122):
    """Convert filter to fourier domain."""
    device = filter.device
    ft = filter.shape[0]

    # the filter is padded or cropped depending on the size of NT
    if ft < NT:
        pad = (NT - ft) // 2
        fhp = fft(torch.cat((torch.zeros(pad, device=device), 
                             filter,
                             torch.zeros(pad + (NT-pad*2-ft), device=device))))
    elif ft > NT:
        crop = (ft - NT) // 2 
        fhp = fft(filter[crop : crop + NT])
    else:
        fhp = fft(filter)
    return fhp

def fft_filter(filter, X):
    fwav = filter_to_fft(filter, NT=X.shape[-1])
    X = torch.real(ifft(fft(X) * torch.conj(fwav)))
    X = fftshift(X, dim = -1)
    return X

def filter_torch(x, cutoff, btype='highpass', fs=30000, device=torch.device('cuda'), order=1):
    filter = get_filter(cutoff=cutoff, fs=fs, btype=btype, device=device, order=order)
    return fft_filter(filter, x)

def numpy_to_torch(data):
    if type(data) is np.ndarray:
        if torch.cuda_is_available():
            data = torch.from_numpy(data).to('cuda')
        else:
            data = torch.from_numpy(data).to('cpu')
    return data

def rms_torch(data):
    data = numpy_to_torch(data)
    return torch.sqrt(torch.sum(torch.square(data), axis=-1) / data.shape[1])

def hilbert_torch(data):
    data = numpy_to_torch(data)
    transforms = -1j * torch.fft.rfft(data, axis=-1)
    transforms[0] = 0
    imaginary = torch.fft.irfft(transforms, axis=-1)
    real = data
    return torch.complex(real, imaginary)

def gaussian(x, mu=0, sd=1):
    return 1.0 / (np.sqrt(2.0 * np.pi) * sd) * np.exp(-np.power((x - mu) / sd, 2.0) / 2)

def gaussian_kernel(sd=1, width=None):
    if width is None:
        width = int(sd*6)
    t = np.linspace(-width, width, width*2+1)
    return gaussian(t, sd=sd)

def gaussian_smoother(x, sd=1, width=None):
    return np.convolve(x, gaussian_kernel(sd=sd, width=width), 'same')

def gaussian_filter_torch(x, sd=1, width=None):
    kernel = gaussian_kernel(sd=sd, width=width)
    kernel = torch.from_numpy(kernel).to('cuda') 
    kernel = kernel.view(1, 1, 1, -1).float()
    x = x.expand(1, 1, x.shape[0], -1)
    return torch.conv2d(x, kernel, padding="same").squeeze()

def get_bad_channels(x, threshold=0.99):
    '''x = n channels x m timepoints (note: only have tested with ripple filtered data)
       threshold = correlation value above which a channel is "bad"
       
       computes pairwise correlations between channels, then looks for impossibly high correlation 
       values on the off diagonal. channels above this are considered "bad"
    '''
    r = torch.corrcoef(x).cpu().numpy()
    r[np.eye(r.shape[0],dtype=bool)] = np.nan
    ind0 = np.argwhere(np.sum(r > threshold, axis=0) > 0)
    ind1 = np.argwhere(np.sum(r > threshold, axis=1) > 0)
    assert np.sum(ind0-ind1) == 0
    return ind0

def get_ripple_amplitude(x, sd=0.004, fs=30000, method='sum'):
    if 'each' in method:
        x_ripple = filter_torch(x, [100, 250], order=1)
        amplitude = hilbert_torch(x_ripple).abs() # abs of hilbert transform to get amplitude
        amplitude = gaussian_filter_torch(amplitude, sd=int(sd*fs)) # smooth
        amplitude = ((amplitude.T - amplitude.mean(1)) / amplitude.std(1)).T # z-score
    elif 'sum' in method:
        x_ripple = filter_torch(x, [150, 250], order=1)
        amplitude = (x_ripple ** 2).sum(0).expand(1,-1) # power is square and sum over supplied channels
        amplitude = gaussian_filter_torch(amplitude, sd=int(sd*fs)) ** 0.5 # smooth and sqrt
        amplitude = (amplitude - amplitude.mean()) / amplitude.std() # z-score
    return amplitude.cpu().numpy()

def get_amplitude(x, sd=0.004, fs=30000, band=[6,12], method='each'):
    x_f = filter_torch(x, band, order=1)
    if (method == 'sum') & (len(x.shape) > 1):
        amplitude = (x_f ** 2).sum(0)
    else:
        amplitude = (x_f ** 2)
    if len(amplitude.shape) == 1:
        amplitude = amplitude.expand(1,-1)
    if sd > 0:
        amplitude = gaussian_filter_torch(amplitude, sd=int(sd*fs)) ** 0.5
    if len(amplitude.shape) > 1:
        amplitude = (amplitude.T - amplitude.mean(1)) / amplitude.std(1).T
    else:
        amplitude = (amplitude - amplitude.mean()) / amplitude.std()

    return amplitude.cpu().numpy()

def get_rms_amplitude(x, band=[6,12]):
    x_f = filter_torch(x, band, order=1)
    return torch.sqrt(torch.mean(x_f**2, axis=1)).cpu().numpy()

def decimate_cpu(signal, samples, factor, ftype='iir', zero_phase=True, axis=-1):
    stage_factors = factorint(factor)
    x = signal
    s = samples #samples
    for q in stage_factors:
        for i in range(stage_factors[q]):
            x = decimate(x, q, ftype=ftype, zero_phase=zero_phase, axis=axis)
            s = s[::q]
            #s = decimate(s, q, ftype='fir', zero_phase=zero_phase)

    return x, s

def decimate_torch(signal, fs=30000, resampler=None, factor=None):
    if resampler is None:
        if factor is not None:
            resampler = get_decimation_factors(factor, fs=fs)

    for r in resampler:
        signal = r(signal)

    return signal

def get_decimation_factors(factor, fs=30000, device='cuda:0'):
    '''creates a multi-stage decimation pipeline to reduce filter artifacts:
    eg. decimation factor of 20 becomes a 3 stage series of factors: 2, 2, 5'''
    stage_factors = factorint(factor)
    resamplers = []
    original_fs = fs
    for q in stage_factors:
        for i in range(stage_factors[q]):
            new_fs = original_fs / q
            resamplers.append(Resample(orig_freq=original_fs, new_freq=new_fs).to(device))
            original_fs = new_fs
    return resamplers


def plot_lfp(arr, times=[], sample_times=None, offset=100, heat_map=False, fs=30e3, ax=plt, bounds=None, yvals=None, scale=1, bad_channels=None,
             color='k', alpha=0.5, linewidth=0.5, **kwargs):
    if type(arr) is torch.Tensor:
        arr = arr.cpu()
    if len(arr.shape) == 1:
        arr = arr[np.newaxis,:]
    if len(times) == 0:
        rng = range(0,arr.shape[1])
    else:
        rng = range(int(np.round(times[0]*fs)),
                int(np.round(times[1]*fs)))
    if sample_times is None:
        t = np.array(rng) / fs
        plt_dat = arr[:,rng] * scale
    else:
        I = (sample_times > times[0]) & (sample_times < times[1])
        t = sample_times[I]
        plt_dat = arr[:,I] * scale

    if not heat_map:
        if yvals is not None:
            yvals = np.array(yvals)
            if len(yvals.shape) == 0:
                yvals = np.array([yvals])
            plt_dat += yvals[:,np.newaxis]
        else:
            plt_offsets = np.arange(0, plt_dat.shape[0]*offset, offset)
            plt_dat += plt_offsets[:,np.newaxis]
        if bad_channels is not None:
            plt_dat[bad_channels,:] = np.nan
        _ = ax.plot(t, plt_dat.T, color=color, alpha=alpha, linewidth=linewidth, **kwargs)
    else:
        if bounds is not None:
            if len(bounds) == 1:
                vmin = bounds[0]
                vmax = bounds[0]
            elif len(bounds) == 2:
                vmin = bounds[0]
                vmax = bounds[1]
        else:
            vmin = None
            vmax = None
        h = ax.pcolor(t, np.arange(plt_dat.shape[0]), plt_dat, cmap='coolwarm', norm=TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax), rasterized=True)
        plt.colorbar(h, label='uV')

def get_spike_amplitudes_fast(
    results_dir,
    spike_times=None,
    binary_file=None,
    chunk_size_samples=500_000,   # time chunk (samples)
    max_spikes_per_batch=10_000,    # micro-batch size
    target_dtype=None,           # torch.float32/float16/bfloat16; None = keep bfile dtype
    return_torch=False,
    *,
    output_backend="cpu",        # "cpu" | "memmap" | "gpu"
    out_path=None,               # used if output_backend == "memmap"
    channels_per_tile=None,      # e.g. 64 or 128 to cap VRAM
    out_dtype="float32",         # dtype of final stored amplitudes ("float32"/"float16"/"bfloat16")
):

    results_dir = Path(results_dir)
    bfile = get_binary_file(binary_file if binary_file is not None else results_dir)

    if spike_times is None:
        spike_times = np.load(results_dir / "spike_times.npy")
    spike_times = np.asarray(spike_times, dtype=np.int64)

    ops = load_ops(results_dir / "ops.npy")
    C = int(ops["n_chan_bin"])
    W = int(getattr(bfile, "nt"))
    pre = int(getattr(bfile, "nt0min"))
    post = W - pre - 1

    # total samples
    if hasattr(bfile, "n_timepoints"):
        total_T = int(bfile.n_timepoints)
    elif hasattr(bfile, "nsamples"):
        total_T = int(bfile.nsamples)
    else:
        total_T = int(spike_times.max() + post + 1)

    # sort spikes & inverse to restore original order on CPU later
    order = np.argsort(spike_times, kind="mergesort")
    st_sorted = spike_times[order]
    inv = np.empty_like(order)
    inv[order] = np.arange(order.size)

    # Prepare CPU/memmap output buffer in SORTED order
    np_dtype = np.dtype(out_dtype)
    if output_backend == "memmap":
        if out_path is None:
            out_path = results_dir / "spike_amps_sorted.memmap"
        amps_sorted_cpu = np.memmap(out_path, mode="w+", dtype=np_dtype, shape=(st_sorted.size, C))
    elif output_backend == "cpu":
        amps_sorted_cpu = np.empty((st_sorted.size, C), dtype=np_dtype)
    elif output_backend == "gpu":
        amps_sorted_cpu = None  # keep legacy behavior (discouraged for big runs)
    else:
        raise ValueError("output_backend must be 'cpu', 'memmap', or 'gpu'.")

    # torch helpers
    def to_torch_dtype(np_or_torch_dt):
        if np_or_torch_dt is None:
            return None
        if isinstance(np_or_torch_dt, torch.dtype):
            return np_or_torch_dt
        if str(np_or_torch_dt) in ("float32", "float"):
            return torch.float32
        if str(np_or_torch_dt) == "float16":
            return torch.float16
        if str(np_or_torch_dt) == "bfloat16":
            return torch.bfloat16
        raise ValueError("Unsupported dtype")

    compute_dtype = None
    target_torch_dtype = to_torch_dtype(target_dtype)

    # move sorted spike times to torch (CPU first; will move to device lazily)
    st_sorted_t = torch.from_numpy(st_sorted)

    device = None
    keep_gpu_output = (output_backend == "gpu")
    spike_amps_sorted_gpu = None  # only if output_backend == "gpu"

    # channel tiling
    if channels_per_tile is None or channels_per_tile <= 0 or channels_per_tile >= C:
        tiles = [(0, C)]
    else:
        tiles = []
        for c0 in range(0, C, channels_per_tile):
            tiles.append((c0, min(C, c0 + channels_per_tile)))

    with torch.no_grad():
        for chunk_start in tqdm(range(0, total_T, chunk_size_samples),
                                desc="extracting spike amplitudes (fixed chunks)"):
            chunk_end = min(chunk_start + chunk_size_samples, total_T)

            # lazily move st_sorted_t to bfile device for fast searchsorted
            if hasattr(bfile, "device"):
                bdev = bfile.device
            else:
                bdev = torch.device("cpu")

            if st_sorted_t.device != bdev:
                st_sorted_t = st_sorted_t.to(bdev)

            left  = int(torch.searchsorted(st_sorted_t, torch.tensor([chunk_start], device=st_sorted_t.device), right=False))
            right = int(torch.searchsorted(st_sorted_t, torch.tensor([chunk_end  ], device=st_sorted_t.device), right=False))
            if left == right:
                continue

            centers = st_sorted_t[left:right]  # device 1-D tensor (N_block,)

            # read buffer including margins
            read_start = max(0, chunk_start - pre)
            read_end   = min(total_T, chunk_end + post + 1)
            buf = bfile[read_start:read_end]  # expected (C, Tbuf) or torch Tensor

            if not isinstance(buf, torch.Tensor):
                buf = torch.as_tensor(buf, device=bdev)

            # infer device / set dtype
            if device is None:
                device = buf.device
                compute_dtype = buf.dtype if target_torch_dtype is None else target_torch_dtype

                if keep_gpu_output:
                    # allocate big output ON GPU (legacy behavior – risky)
                    spike_amps_sorted_gpu = torch.empty(
                        (st_sorted_t.numel(), C), device=device, dtype=compute_dtype
                    )

            if buf.dtype != compute_dtype:
                buf = buf.to(dtype=compute_dtype)

            Cbuf, Tbuf = int(buf.shape[0]), int(buf.shape[1])
            if Cbuf != C or Tbuf < W:
                del buf
                continue

            # Sliding window view: (C, L, W)
            winview = buf.unfold(dimension=1, size=W, step=1)  # strided view
            L = winview.shape[1]

            block_positions_sorted = torch.arange(left, right, device=device, dtype=torch.long)
            centers_local = centers - read_start
            starts_all = centers_local - pre

            # Process spikes in micro-batches
            for s in range(0, starts_all.numel(), max_spikes_per_batch):
                e = min(s + max_spikes_per_batch, starts_all.numel())
                starts = starts_all[s:e]  # (N_mb,)

                valid = (starts >= 0) & (starts < L)
                if not torch.any(valid):
                    continue

                starts_v = starts[valid]
                pos_sorted_v = block_positions_sorted[s:e][valid]

                # Process channels in tiles to bound VRAM
                for (c0, c1) in tiles:
                    # pick waveforms: (Ct, N_valid, W) -> (N_valid, Ct, W)
                    waves = winview[c0:c1].index_select(1, starts_v).permute(1, 0, 2).contiguous()

                    # per-waveform preprocessing
                    waves -= waves.mean(dim=2, keepdim=True)
                    # subtract median across channels per timepoint (within tile)
                    waves -= waves.median(dim=1, keepdim=True).values

                    amps_tile = waves[:, :, pre]  # (N_valid, Ct)

                    if keep_gpu_output:
                        # write to GPU big tensor (legacy)
                        spike_amps_sorted_gpu.index_copy_(0, pos_sorted_v, 
                            torch.zeros_like(spike_amps_sorted_gpu[pos_sorted_v, c0:c1]).scatter_add(
                                1, torch.arange(0, c1-c0, device=device)[None, :].expand_as(amps_tile), amps_tile
                            )
                        )
                    else:
                        # move only this tile to CPU and write into CPU/memmap
                        # non_blocking=True works if CPU tensor is pinned; we’ll just copy synchronously for simplicity
                        tile_cpu = amps_tile.detach().to("cpu").numpy()  # (N_valid, Ct)
                        amps_sorted_cpu[pos_sorted_v.cpu().numpy(), c0:c1] = tile_cpu

                    del waves, amps_tile

                del starts_v, pos_sorted_v

            del winview, buf

    # Build final output in original spike order
    if output_backend == "gpu":
        if spike_amps_sorted_gpu is None:
            # no spikes
            if return_torch:
                return torch.empty((0, 0))
            return np.empty((0, 0), dtype=np_dtype)
        # unsort on GPU if returning torch, else single CPU copy
        inv_t = torch.from_numpy(inv).to(spike_amps_sorted_gpu.device)
        spike_amps = spike_amps_sorted_gpu.index_select(0, inv_t)
        if return_torch:
            return spike_amps
        out = spike_amps.detach().to("cpu").numpy().astype(np_dtype, copy=False)
        del spike_amps, spike_amps_sorted_gpu
    else:
        # CPU/memmap path
        if st_sorted.size == 0:
            return (torch.empty((0, 0)) if return_torch else np.empty((0, 0), dtype=np_dtype))
        out_sorted = amps_sorted_cpu  # np.ndarray or np.memmap
        out = out_sorted[inv, :]      # restore original ordering
        if return_torch:
            return torch.from_numpy(out)

    # tidy up
    if device is not None and device.type == "cuda":
        torch.cuda.synchronize()
        torch.cuda.empty_cache()
    gc.collect()
    return out





# def load_binary_chunk(dp, times, channels=np.arange(384), filt_key='lowpass', scale=True, verbose=False):
#     dp = Path(dp)
#     meta = read_metadata(dp)
#     fname = Path(dp)/meta[filt_key]['binary_relative_path'][2:]
    
#     fs = meta[filt_key]['sampling_rate']
#     Nchans=meta[filt_key]['n_channels_binaryfile']
#     bytes_per_sample=2
    
#     assert len(times)==2
#     assert times[0]>=0
#     assert times[1]<meta['recording_length_seconds']
    
#     # Format inputs
#     ignore_ks_chanfilt = True
#     channels=assert_chan_in_dataset(dp, channels, ignore_ks_chanfilt)
#     t1, t2 = int(np.round(times[0]*fs)), int(np.round(times[1]*fs))
    
#     vmem=dict(psutil.virtual_memory()._asdict())
#     chunkSize = int(fs*Nchans*bytes_per_sample*(times[1]-times[0]))
#     if verbose:
#         print('Used RAM: {0:.1f}% ({1:.2f}GB total).'.format(vmem['used']*100/vmem['total'], vmem['total']/1024/1024/1024))
#         print('Chunk size:{0:.3f}MB. Available RAM: {1:.3f}MB.'.format(chunkSize/1024/1024, vmem['available']/1024/1024))
#     if chunkSize>0.9*vmem['available']:
#         print('WARNING you are trying to load {0:.3f}MB into RAM but have only {1:.3f}MB available.\
#               Pick less channels or a smaller time chunk.'.format(chunkSize/1024/1024, vmem['available']/1024/1024))
#         return
    
#     # Get chunk from binary file
#     with open(fname, 'rb') as f_src:
#         # each sample for each channel is encoded on 16 bits = 2 bytes: samples*Nchannels*2.
#         byte1 = int(t1*Nchans*bytes_per_sample)
#         byte2 = int(t2*Nchans*bytes_per_sample)
#         bytesRange = byte2-byte1

#         f_src.seek(byte1)

#         bData = f_src.read(bytesRange)
        
#     # Decode binary data
#     # channels on axis 0, time on axis 1
#     assert len(bData)%2==0
#     rc = np.frombuffer(bData, dtype=np.int16) # 16bits decoding
#     rc = rc.reshape((int(t2-t1), Nchans)).T
#     rc = rc[channels, :]
    
#     # Scale data
#     if scale:
#         rc = rc * meta['bit_uV_conv_factor'] # convert into uV
    
#     return rc