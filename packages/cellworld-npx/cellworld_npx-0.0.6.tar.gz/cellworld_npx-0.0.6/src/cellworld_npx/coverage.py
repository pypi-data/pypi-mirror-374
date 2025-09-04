import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from .celltile import get_world_mask

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

def get_histogram2(x, y, bins=np.linspace(0,1,100), mask=None):
  H,_,_ = np.histogram2d(x, y, bins=bins)
  if mask is not None:
    H = apply_mask(H, mask)
  return H


def get_visit_histogram(x, y, bins=np.linspace(0,1,100), dt=90*1, mask=None):
  '''computes an occupancy histogram every dt samples, thresholds, then sums'''
  dt = int(dt)
  duration = len(x)
  chunks = int(np.ceil(duration/dt))
  H1 = []
  for i in range(chunks):
    I = range((i*dt), np.min([len(x),(i*dt)+dt]))
    H = get_histogram2(x[I], y[I], bins)
    H1.append(H>0)
  H = np.dstack(H1).sum(2).astype(float)

  if mask is not None:
    H = apply_mask(H, mask)
  
  return H

def get_mask(w, bins, wall_mask=True, occlusion_mask=True, reshape=False):
   mask = get_world_mask(w, bins, wall_mask, occlusion_mask)
   if reshape:
      mask = np.reshape(mask, (len(bins)-1, len(bins)-1))
   return mask

def apply_mask(H, mask):
  if any(mask.shape) == 1:
    H[np.reshape(mask, (H.shape[0], H.shape[1]))] = np.nan
  else:
    assert mask.shape == H.shape, f'mask must be same shape as H'
    H[mask] = np.nan
  return H   


def get_occupancy(x, y, bins, fps, mask=None):
    '''
    get_occupancy(x, y, bins, fps, mask=None)

    returns occupancy (in seconds) spent in each bin based on x, y locations
    '''
    occupancy = get_histogram2(x, y, bins) / fps
    if mask is not None:
      occupancy[mask.reshape(occupancy.shape)] = np.nan
    return occupancy


def plot_occupancy(x, y, fps, bins=np.linspace(0,1,100), mask=None, cmap='viridis', ax=None):
  if ax is None:
    fig,ax = plt.subplots(1,1,figsize=figsize)
  else:
    fig = ax.get_figure()
  extent = [bins.min(), bins.max(), bins.min(), bins.max()]
  occupancy = get_occupancy(x, y, bins, fps, mask=mask)
  h = ax.imshow(np.rot90(occupancy), cmap=cmap, extent=extent, interpolation=None, norm=LogNorm(), alpha = 0.9)
  ax.set_aspect('equal')
  fig.colorbar(h, fraction=0.046, pad=0.04)

  return occupancy


def get_coverage(H, cutoff=0):
  H = np.array(H)
  return np.sum(H > cutoff) / np.sum(~np.isnan(H))
  

def plot_coverage(x, y, bins=np.linspace(0,1,100), cutoff=3, mask=None, normalizer=None, ax=None, dt=None, cmap='viridis'):
  label = 'Visits / hour'
  if normalizer is None:
    label = 'Visits'
    normalizer = 1
  if ax is None:
      fig,ax = plt.subplots(1,1)
  else:
      fig = ax.get_figure()
  if dt is not None:
      H = get_visit_histogram(x, y, bins=bins, mask=mask, dt=dt)
  else:
      H = get_histogram2(x, y, bins=bins, mask=mask)
  H = H / normalizer

  H = get_visit_histogram(x, y, bins=bins, mask=mask, dt=88)
  extent = [bins.min(), bins.max(), bins.min(), bins.max()]
  #plt.imshow(np.rot90(H > cutoff))
  h = ax.imshow(np.rot90(H), cmap=cmap, vmin=cutoff, vmax=cutoff+1, extent=extent, interpolation=None, alpha=0.8)
  ax.set_aspect('equal')
  cbar = fig.colorbar(h, fraction=0.046, pad=0.04, label=label)
  cbar.set_ticks([cutoff, cutoff+1])
  cbar.set_ticklabels([f'<={cutoff}', f'>{cutoff}'])

  return get_coverage(H, cutoff)


def calculate_coverage(x, y, bins, cutoff=3, mask=None, normalizer=None, dt=88):
  if normalizer is None:
    normalizer = 1
  if dt is not None:
    H = get_visit_histogram(x, y, bins=bins, mask=mask, dt=dt)
  else:
    H = get_histogram2(x, y, bins=bins, mask=mask)
  H = H / normalizer
  return get_coverage(H, cutoff)
