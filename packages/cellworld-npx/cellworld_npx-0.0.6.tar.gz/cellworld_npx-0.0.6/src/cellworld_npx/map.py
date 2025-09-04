import numpy as np
import matplotlib.pyplot as plt

class Map:
    def __init__(self, coordinates, bins=None, values=None, times=None, fps=None):
        assert coordinates.shape[1] == 2, 'coordinates must be Nx2 matrix'
        self.coordinates = coordinates
        if bins is None:
            self.bins = np.linspace(np.nanmin(coordinates), np.nanmax(coordinates), 20)
        elif type(bins) == int:
            self.bins = np.linspace(np.nanmin(coordinates), np.nanmax(coordinates), bins)
        else:
            self.bins = np.array(bins)
        self.n_bins = len(self.bins)
        self.bin_width = np.mean(np.diff(bins))
        self.bin_centers = bins[:-1] + self.bin_width/2
        self.times = times
        self.fps = fps
        self.values = values

    def histogram(self, normalize=None):
        self.map = histogram2(self.coordinates[:,0], self.coordinates[:,1], bins=self.bins)
        if normalize is not None:
           assert self.fps is not None, f'to normalize self.fps must be specified, but is {self.fps}'
           self.map = self.map / self.fps
        return self

    def temporal_count(self, dt=90*1):
        self.map = visit_histogram(self.coordinates[:,0], self.coordinates[:,1], bins=self.bins, dt=dt)
        return self

    def spike_histogram(self, occupancy=None, normalize=True):
        assert self.times is not None, 'frame times required for rate map'
        assert self.values is not None, 'spike time values required for rate map'
        pos_i = np.searchsorted(self.times[:-1], self.values)
        counts = histogram2(self.coordinates[pos_i,0].squeeze(),
                           self.coordinates[pos_i,1].squeeze(),
                           self.bins)
        if (occupancy is None) & (normalize == True):
           self.map = counts / self.histogram(normalize=True).map
        elif occupancy is not None:
           assert occupancy.shape == counts.shape, f'occupancy shape [{occupancy.shape}] must equal histogram shape [{counts.shape}]'
           self.map = counts / occupancy
        else:
           self.map = counts
        return self
    
    def threshold(self, thresh=0):
        self.map = self.map > thresh
        return self
    
    def coverage(self, thresh=0):
        return np.sum(self.map > thresh) / np.sum(~np.isnan(self.map))
    
    def mask(self, mask=None, thresh=None):
        assert (mask is None) | (thresh is None), 'mask or threshold must be none'
        assert hasattr(self, 'map'), 'must compute a map to mask'
        if mask is not None:
            assert mask.shape == self.map.shape, f'mask shape [{mask.shape}] must equal map shape [{self.map.shape}]'
        elif thresh is not None:
            mask = self.map < thresh
        self.original_map = self.map.copy()
        self.map[~mask] = np.nan
        self.masker = mask
        return self

    def plot(self, ax=None, **kwargs):
       assert hasattr(self, 'map'), 'must compute a map to plot'
       if ax is None:
          _,ax = plt.subplots(1,1)
       extent = [self.bins.min(), self.bins.max(), self.bins.min(), self.bins.max()] 
       h = ax.imshow(np.rot90(self.map), extent=extent, interpolation=None, **kwargs)
       ax.set_aspect('equal')
       plt.colorbar(h, fraction=0.046, pad=0.04)

        




def make_map_bins(ideal_bin_width=0.10, scaler=1, pad=0.05):
    n_bins = int(np.round((2.34*scaler) / ideal_bin_width))
    bins = np.linspace(0-pad, (1+pad)*scaler, n_bins)
    bin_width = np.mean(np.diff(bins))
    bin_centers = bins[:-1] + bin_width/2
    return bins, bin_width, bin_centers

def histogram2(x, y, bins=np.linspace(0,1,100), mask=None):
  H,_,_ = np.histogram2d(x, y, bins=bins)
  if mask is not None:
    H[np.reshape(mask, (len(bins)-1, len(bins)-1))] = np.nan
  return H


def visit_histogram(x, y, bins=np.linspace(0,1,100), dt=90*1, mask=None):
  '''computes an occupancy histogram every dt samples, thresholds, then sums'''
  dt = int(dt)
  duration = len(x)
  chunks = int(np.ceil(duration/dt))
  H1 = []
  for i in range(chunks):
    I = range((i*dt), np.min([len(x),(i*dt)+dt]))
    H = histogram2(x[I], y[I], bins)
    H1.append(H>0)
  H = np.dstack(H1).sum(2).astype(float)

  if mask is not None:
    H[np.reshape(mask, (len(bins)-1, len(bins)-1))] = np.nan
  
  return H