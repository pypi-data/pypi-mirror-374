from .binning import BinnedRecording, make_map_bins
from .celltile import get_world_mask
from replay_trajectory_classification import SortedSpikesClassifier, ClusterlessClassifier, Environment, RandomWalk, Uniform, Identity
from scipy.ndimage import gaussian_filter
from scipy.spatial.distance import squareform, pdist, cdist
from scipy.special import factorial
from scipy.stats import norm
from tqdm import tqdm
import statsmodels.api as sm
import torch.nn.functional as F
import torch
import gc
import numpy as np
import copy
import pickle

from matplotlib.colors import ListedColormap
from matplotlib import animation
from moviepy.video.io.bindings import mplfig_to_npimage
from .utils import display_oasis_world
import matplotlib.pyplot as plt

class RateMaps(object):
    def __init__(self, 
                recording:BinnedRecording,
                bins = None,
                bin_size=0.1, 
                smooth_sigma=1.0, 
                mask_nans=True,
                occupancy_cutoff=0.0,
                use_torch=True):
        self.recording = recording
        self.bin_size = bin_size
        if bins is None:
            self.bins, _, _ = make_map_bins(self.bin_size)
        else:
            self.bins = bins
        self.smooth_sigma = smooth_sigma
        self.mask_nans = mask_nans
        self.use_torch = use_torch
        self.occupancy_cutoff = occupancy_cutoff
        self.occupancy = self.get_occupancy()
        self.rate_maps = self.get_rate_maps()

    def get_occupancy(self):
        occupancy = get_occupancy(self.recording.behavior_data.prey_location_x, 
                                  self.recording.behavior_data.prey_location_y, 
                                  bins=self.bins,
                                  cutoff=self.occupancy_cutoff,
                                  dt=self.recording.dt)
        return occupancy
    
    def get_rate_maps(self):
        if self.use_torch:
            rate_maps = self.get_rate_maps_torch()
        else:
            rate_maps = self.get_rate_maps_cpu()
        return rate_maps
    
    def get_rate_maps_torch(self):
        x = torch.from_numpy(self.recording.behavior_data.prey_location_x.to_numpy()).cuda()
        y = torch.from_numpy(self.recording.behavior_data.prey_location_y.to_numpy()).cuda()
        spike_counts_all = torch.from_numpy(self.recording.spike_array.T).cuda()
        occupancy = torch.from_numpy(self.occupancy).cuda()
        bins = torch.from_numpy(self.bins).cuda()
        rate_maps_cuda = get_rate_maps_torch(spike_counts_all, x, y, bins, bins, occupancy, 
                                        self.smooth_sigma, self.mask_nans)
        rate_maps = [r.cpu().numpy() for r in rate_maps_cuda]
        del rate_maps_cuda, x, y, spike_counts_all, occupancy, bins
        gc.collect()
        torch.cuda.empty_cache()
        return rate_maps

    def get_rate_maps_cpu(self):
        rate_maps = []
        for i in range(self.recording.spike_array.shape[0]):
            rate_maps.append(get_rate_map_cpu(self.recording.spike_array[i,:], 
                                          self.recording.behavior_data.prey_location_x,
                                          self.recording.behavior_data.prey_location_y,
                                          self.bins,
                                          self.bins,
                                          self.occupancy,
                                          self.smooth_sigma,
                                          self.mask_nans))
        return rate_maps
    
class BayesDecoderTorch(object):
    def __init__(self,
                 bins=None,
                 encoding_model='quadratic',
                 device='cuda',
                 mask='world',
                 smooth_sigma=3.0,
                 occupancy_cutoff=0,
                 smooth_constraint=False
                 ):
        self.name = 'Bayesian'
        self.encoding_model = encoding_model
        self.bins = bins
        self.device = device
        self.mask = mask
        self.smooth_sigma = smooth_sigma
        self.occupancy_cutoff = occupancy_cutoff
        self.smooth_constraint = smooth_constraint
        self.location_bins = self.get_location_bins()
        self.tuning_all = None
        self.std = None

    def get_mask(self, recording:BinnedRecording):
        mask = np.ones((len(self.bins) * len(self.bins),1))
        if self.mask == 'occupancy':
            occ = get_occupancy(recording.behavior_data.prey_location_x,
                                recording.behavior_data.prey_location_y,
                                self.bins,
                                cutoff=0.1,
                                dt=recording.dt)
            mask = (np.rot90(occ) > 0).flatten()
        elif self.mask == 'world':
            mask = get_world_mask(recording.recording.world, self.bins)
            mask = np.rot90(mask.reshape(len(self.bins)-1, len(self.bins)-1) < 1).flatten()
        return mask
    
    def get_variables(self, recording:BinnedRecording, remove_nans=True):
        X = recording.spike_array
        y = np.vstack([recording.behavior_data.prey_location_x, 
                       recording.behavior_data.prey_location_y]).T
        if remove_nans:
            invalid = np.any(np.isnan(X), axis=1) | np.any(np.isnan(y), axis=1)
            X = X[~invalid, :]
            y = y[~invalid, :]
        return X, y

    def get_location_bins(self):
        bin_centers = self.bins[:-1] + np.mean(np.diff(self.bins)) / 2
        input_mat = np.meshgrid(bin_centers, bin_centers)
        xs = np.reshape(input_mat[0],[bin_centers.shape[0]*bin_centers.shape[0],1])
        ys = np.reshape(input_mat[1],[bin_centers.shape[0]*bin_centers.shape[0],1])
        return np.concatenate((xs,ys),axis=1)

    def fit_glm(self, recording:BinnedRecording, max_iter=2000, lr=1e-2, verbose=False):
        X, y = self.get_variables(recording)
        # Feature engineering
        if self.encoding_model == 'linear':
            Y_design = y
            bins_design = self.location_bins
        elif self.encoding_model == 'quadratic':
            Y_design = self.quadratic_features(y)
            bins_design = self.quadratic_features(self.location_bins)

        # Convert to torch tensors and push to device
        X = torch.tensor(X, dtype=torch.float32, device=self.device)
        Y_design = torch.tensor(Y_design, dtype=torch.float32, device=self.device)
        bins_design = torch.tensor(bins_design, dtype=torch.float32, device=self.device)

        n_obs, n_cells = X.shape
        n_bins = bins_design.shape[0]

        # Add intercept
        Y_design_ = torch.cat([torch.ones((Y_design.shape[0], 1), device=self.device), Y_design], dim=1)
        bins_design_ = torch.cat([torch.ones((bins_design.shape[0], 1), device=self.device), bins_design], dim=1)
        n_feat = Y_design_.shape[1]

        # Parallel weights for all cells: shape (n_cells, n_feat)
        weights = torch.zeros((n_cells, n_feat), device=self.device, requires_grad=True)
        optimizer = torch.optim.Adam([weights], lr=lr)

        targets = X # (n_obs, n_cells)

        for it in tqdm(range(max_iter), desc='Fitting Poisson GLMs (batch)', disable=not verbose):
            optimizer.zero_grad()
            eta = Y_design_ @ weights.T        # (n_obs, n_cells)
            mu = torch.exp(eta)
            loss = torch.sum(mu - targets * eta)
            loss.backward()
            optimizer.step()
            if verbose and it % 500 == 0:
                print(f"Iter {it}: Loss={loss.item():.4f}")

        # Predict tuning for all location bins, all cells at once
        with torch.no_grad():
            eta_pred = bins_design_ @ weights.T  # (n_bins, n_cells)
            mu_pred = torch.exp(eta_pred)        # (n_bins, n_cells)
        
        return mu_pred.cpu().numpy().T  # (n_cells, n_bins)

    def quadratic_features(self, arr):
        out = np.empty([arr.shape[0], 5])
        out[:,0] = arr[:,0] ** 2
        out[:,1] = arr[:,0]
        out[:,2] = arr[:,1] ** 2
        out[:,3] = arr[:,1]
        out[:,4] = arr[:,0] * arr[:,1]
        return out
    
    def fit_rate_map(self, recording:BinnedRecording, smooth_sigma=3, occupancy_cutoff=0):
        spike_maps = RateMaps(recording, 
                              bins=self.bins, 
                              smooth_sigma=smooth_sigma, 
                              occupancy_cutoff=occupancy_cutoff).rate_maps
        spike_maps = [s.T.flatten() for s in spike_maps]
        spike_maps = np.vstack(spike_maps)
        spike_maps[np.isnan(spike_maps)] = 0
        return spike_maps * recording.dt
    
    def fit(self, recording:BinnedRecording):
        if 'quadratic' in self.encoding_model or 'linear' in self.encoding_model:
            self.tuning_all = self.fit_glm(recording)
        else:
            self.tuning_all = self.fit_rate_map(recording, 
                                                smooth_sigma=self.smooth_sigma, 
                                                occupancy_cutoff=self.occupancy_cutoff)

        if self.mask is not None:
            mask = self.get_mask(recording)
            for i in range(self.tuning_all.shape[0]):
                self.tuning_all[i,:] = self.tuning_all[i,:] * mask

        _, y = self.get_variables(recording)
        dx = np.sqrt(np.sum(np.diff(y, axis=0)**2, axis=1))
        std = np.sqrt(np.mean(dx**2))
        self.std = std

        gc.collect()
        torch.cuda.empty_cache()


    def predict(self, recording:BinnedRecording, return_posterior=False, batch_size=1000):
        smooth_constraint = self.smooth_constraint
        X_test = recording.spike_array
        y_test = np.vstack([recording.behavior_data.prey_location_x, 
                            recording.behavior_data.prey_location_y]).T
        nt, n_cells = X_test.shape

        tuning_all = torch.tensor(self.tuning_all, dtype=torch.float32, device=self.device)  # (n_cells, n_bins)
        tuning_all = torch.nan_to_num(tuning_all, nan=0.0)
        location_bins = torch.tensor(self.location_bins, dtype=torch.float32, device=self.device)  # (n_bins, 2)
        n_bins = tuning_all.shape[1]

        X_test = torch.tensor(X_test, dtype=torch.float32, device=self.device)  # CPU batching for memory
        y_test_predicted = torch.empty((nt, 2), dtype=torch.float32, device=self.device)

        if return_posterior:
            posterior_array = torch.empty((nt, n_bins), dtype=torch.float32, device=self.device)

        # --- Smoothing: precompute transition matrix ---
        prob_dists = None
        if smooth_constraint:
            dists = squareform(pdist(self.location_bins), 'euclidean')
            prob_dists = norm.pdf(dists, 0, self.std)
            log_trans = torch.log(torch.tensor(prob_dists + 1e-12, dtype=torch.float32, device=self.device))

        # --- Precompute Poisson terms ---
        log_tuning = torch.log(tuning_all + 1e-8)  # (n_cells, n_bins)
        lam = tuning_all.unsqueeze(0)             # (1, n_cells, n_bins)
        log_lam = log_tuning.unsqueeze(0)         # (1, n_cells, n_bins)

        # --- Loop over batches ---
        log_belief = None  # used only if smooth_constraint is on
        for batch_start in tqdm(range(0, nt, batch_size), desc='Batch prediction'):
            batch_end = min(batch_start + batch_size, nt)
            batch_idx = slice(batch_start, batch_end)
            Xc = torch.clamp(X_test[batch_idx], max=170).round()  # (batch, n_cells)

            # Poisson log likelihood
            log_fact = torch.lgamma(Xc + 1).unsqueeze(-1)  # (batch, n_cells, 1)
            Xc_exp = Xc.unsqueeze(-1)                     # (batch, n_cells, 1)
            log_probs_batch = torch.sum(
                -lam + Xc_exp * log_lam - log_fact,
                dim=1  # sum over cells
            )  # (batch, n_bins)

            if smooth_constraint:
                for k in range(log_probs_batch.shape[0]):
                    t = batch_start + k
                    log_likelihood = log_probs_batch[k]
                    if t == 0:
                        log_belief = log_likelihood
                    else:
                        log_belief = torch.logsumexp(log_belief.unsqueeze(0) + log_trans, dim=1)
                        log_belief = log_belief + log_likelihood

                    loc_idx = torch.argmax(log_belief).item()
                    y_test_predicted[t] = self.location_bins[loc_idx].cpu()

                    if return_posterior:
                        lb = log_belief - torch.max(log_belief)
                        posterior_probs = torch.exp(lb)
                        posterior_probs /= posterior_probs.sum()
                        posterior_array[t] = posterior_probs.cpu()
            else:
                # --- Vectorized no-smoothing prediction ---
                max_idx = torch.argmax(log_probs_batch, dim=1)  # (batch,)
                y_test_predicted[batch_start:batch_end] = location_bins[max_idx]

                if return_posterior:
                    posterior_batch = logsumexp_normalize(log_probs_batch)
                    posterior_array[batch_start:batch_end] = posterior_batch

        posterior = posterior_array.cpu().numpy()
        y_predicted = y_test_predicted.cpu().numpy()

        del posterior_array, y_test_predicted, X_test, Xc, log_fact, Xc_exp, log_probs_batch, tuning_all, location_bins, log_tuning, lam, log_lam, prob_dists, log_belief, max_idx, posterior_batch
        gc.collect()
        torch.cuda.empty_cache()

        # print("\n[After cleanup] Tensors still on GPU:")
        for obj in gc.get_objects():
            try:
                if torch.is_tensor(obj) and obj.is_cuda:
                    print(f"Type: {type(obj)}, shape: {obj.shape}, device: {obj.device}")
            except:
                pass

        if return_posterior:
            return y_predicted, posterior
        else:
            return y_predicted
        
class ClusterlessClassifier(object):
    def __init__(self,
                bin_size=5,
                states=['continuous', 'fragmented'],
                movement_var=6,
                mark_variance=24,
                position_variance=6,
                drop_causal_posterior=True,
                device='cuda',
                canonical_to_cm=234
                ):
        self.name = 'ClusterlessClassifier'
        self.bin_size = bin_size
        self.states = states
        self.movement_var = movement_var
        self.mark_variance = mark_variance
        self.position_variance = position_variance
        self.drop_causal_posterior = drop_causal_posterior
        self.device = device
        self.canonical_to_cm = canonical_to_cm
        self.transitions = get_continuous_transitions(self.movement_var, self.states)
        self.environment = Environment(place_bin_size=bin_size, 
                                       position_range=(-0.05*234, 1.05*234), 
                                       alternate_binning=True)


class SortedClassifier(object):
    def __init__(self,
                 bin_size=5,
                 states=['continuous', 'fragmented'],
                 movement_var=6,
                 position_var=6,
                 drop_causal_posterior=True,
                 algorithm='spiking_likelihhod_kde_gpu',
                 canonical_to_cm=234
                 ):
        self.name = 'SortedClassifier'
        self.bin_size = bin_size
        self.states = states
        self.movement_var = movement_var
        self.position_var = position_var
        self.drop_causal_posterior = drop_causal_posterior
        self.algorithm = algorithm
        self.canonical_to_cm = canonical_to_cm
        self.transitions = get_continuous_transitions(self.movement_var, self.states)
        self.environment = Environment(place_bin_size=bin_size, 
                                       position_range=(-0.05*234, 1.05*234), 
                                       alternate_binning=True)
        self.classifier = SortedSpikesClassifier(
            environments=[self.environment],
            continuous_transition_types=self.transitions,
            sorted_spikes_algorithm ='spiking_likelihood_kde_gpu',
            sorted_spikes_algorithm_params={'position_std': self.position_var})
        self.bins = None
        self.encoding_model = None
        
        
    def fit(self, recording:BinnedRecording):
        position = np.vstack([recording.behavior_data.prey_location_x, 
                              recording.behavior_data.prey_location_y]).T
        self.encoding_model = self.classifier.fit(position*self.canonical_to_cm, recording.spike_array)
        self.bins = self.encoding_model.environments[0].edges_[0]

    def predict(self, recording:BinnedRecording, return_posterior=False, batch_size=None):
        result = self.encoding_model.predict(spikes=recording.spike_array, time=recording.behavior_data.time_stamp, use_gpu=True)
        posterior = result.acausal_posterior.sum('state').stack(position=['x_position', 'y_position'])
        y_predicted = posterior.position[posterior.argmax('position')]
        y_predicted = np.asarray(y_predicted.values.tolist())
        if return_posterior:
            return y_predicted, np.asarray(posterior)
        else:
            return y_predicted
        
            
class Decoder(object):
    def __init__(self, 
                 recording:BinnedRecording, 
                 model,
                 dt=None, 
                 window=None,
                 cv_folds=5,
                 batch_size=100):
        self.recording = recording
        self.model = model
        self.dt = dt
        if dt is None:
            self.dt = recording.dt
        self.window = window
        if window is None:
            self.window = recording.window
        self.window = window
        self.batch_size = batch_size
        self.cv_folds = cv_folds
        self.train_index = (self.recording.behavior_data.prey_velocity > 0.017).to_list()
        self.test_index = np.arange(0,len(self.recording.behavior_data))
        self.cell_index = self.recording.clusters_info.good_unit.to_list()

    def train(self):
        # train
        self.model.fit(self.recording[self.test_index,self.cell_index])

    def test(self):
        # test
        prediction, posterior = self.model.predict(self.recording[self.test_index,self.cell_index], 
                                                   batch_size=self.batch_size, 
                                                   return_posterior=True)
        self.prediction = prediction
        self.posterior = posterior

    def copy(self, deep=False):
        if deep:
            return copy.deepcopy(self)
        else:
            return copy.copy(self)
        
    def save(self, fn):
        with open(fn, 'wb') as f:
            pickle.dump(self, f)


        

class DecoderVideo(object):
    def __init__(self, decoder:Decoder):
        self.decoder = decoder
        bins = self.decoder.model.bins
        self.n_bins = len(bins) - 1
        scale = 1
        if hasattr(self.decoder.model, 'canonical_to_cm'):
            scale = 234
        self.extent = [bins.min() / scale, bins.max() / scale, 
                       bins.min() / scale, bins.max() / scale]

    def plot_frame(self, f=0, dpi=300, res=[720, 720], scale=1, vmin=0, vmax=None): 
        fig, ax = plt.subplots(1, 1, figsize=(res[0]/dpi, res[1]/dpi))
        display_oasis_world(self.decoder.recording.recording.experiments[0], 
                            self.decoder.recording.recording.world, 
                            fig=fig, 
                            ax=ax)
        ax.set_title(self.decoder.recording.recording.experiment_name)
        cmap = get_cmap("Blues")
        post = self.decoder.posterior[f].reshape(self.n_bins, self.n_bins)
        if 'Classifier' in self.decoder.model.name:
            post = np.flipud(post.T) #np.fliplr(np.rot90(post))
        else:
            post = np.flipud(post)
        handles = []
        if vmax is None:
            vmax = np.nanmax(post)
        h = ax.imshow(post, cmap=cmap, extent=self.extent, zorder=-7, 
                    vmin=vmin, vmax=vmax)
        handles.append(h)
        h, = ax.plot(self.decoder.recording.behavior_data.prey_location_x[f]/scale, 
                     self.decoder.recording.behavior_data.prey_location_y[f]/scale, 'co', 
                    markeredgecolor='k', zorder=10, markersize=3, label='mouse')
        handles.append(h)
        h, = ax.plot(self.decoder.recording.behavior_data.predator_location_x[f]/scale, 
                     self.decoder.recording.behavior_data.predator_location_y[f]/scale, 'mo', 
                    markeredgecolor='k', zorder=10, markersize=3, label='robot')
        handles.append(h)
        h = ax.text(0.5, 0.01, f'{self.decoder.recording.behavior_data.time_stamp[f]:0.3f} s', 
                    color='k', horizontalalignment='center')
        handles.append(h)
        ax.legend(bbox_to_anchor=(0.75, 1.05))
        return handles, fig, ax

    def update_frame(self, f, h, scale=1, return_image=False, vmin=0, vmax=None):
        post = self.decoder.posterior[f].reshape(self.n_bins, self.n_bins)
        if 'Classifier' in self.decoder.model.name:
            post = np.flipud(post.T) #np.fliplr(np.rot90(post))
        else:
            post = np.flipud(post)
        if vmax is None:
            vmax = np.nanmax(post)
        h[0].set_data(post)
        h[0].set_clim(vmin=vmin, vmax=vmax)
        h[1].set_xdata([self.decoder.recording.behavior_data.prey_location_x[f]/scale])
        h[1].set_ydata([self.decoder.recording.behavior_data.prey_location_y[f]/scale])
        h[2].set_xdata([self.decoder.recording.behavior_data.predator_location_x[f]/scale])
        h[2].set_ydata([self.decoder.recording.behavior_data.predator_location_y[f]/scale])
        h[3].set_text(f'{self.decoder.recording.behavior_data.time_stamp[f]:0.3f} s')
        if return_image:
            return mplfig_to_npimage(h[0].figure)
        else:
            return h
        
    def animate(self, window, frames=None, downsample=10):
        interval = int(self.decoder.dt * 1000)
        if frames is None:
            time = self.decoder.recording.behavior_data.time_stamp
            time_index = np.argwhere((time > window[0]) & (time < window[1])).squeeze()
            frames = range(time_index[0], time_index[-1])[0::downsample]
        h, fig, _ = self.plot_frame(0)
        anim = animation.FuncAnimation(fig, self.update_frame, fargs=(h,), repeat=False,
                                    frames=frames, interval=interval*downsample, blit=False)
        return anim
    
    def write(self, window, fn=None, downsample=10, slowdown=10, dpi=100):
        fps = 1 / (self.decoder.dt * downsample)
        a = self.animate(window, downsample=downsample)
        writer = animation.writers['ffmpeg'](fps=fps/slowdown)
        if fn is None:
            fn = f'./decoding_frames_{downsample}subsamp_{slowdown}xslowdown_{window[0]}-{window[-1]}s.mp4'
        a.save(fn, writer=writer, dpi=dpi)


## state space classifier helper functions
def get_continuous_transitions(movement_var=6, states=['continuous', 'fragmented']):
    state_transitions = {'continuous': RandomWalk(movement_var=movement_var),
                        'fragmented': Uniform(),
                        'stationary': Identity()}
    if 'continuous' in states and 'fragmented' in states and 'stationary' in states:
        return [
            [RandomWalk(movement_var=movement_var), Uniform(), Identity()],
            [Uniform(), Uniform(), Uniform()],
            [RandomWalk(movement_var=movement_var), Uniform(), Identity()],
            ]
    elif 'continuous' in states and 'fragmented' in states and 'stationary' not in states:
        return [
            [RandomWalk(movement_var=movement_var), Uniform()],
            [Uniform(), Uniform()]
            ]
    elif len(states) == 1:
        return state_transitions[states[0]]
    else:
        raise AssertionError("self.states must be ['continuous', 'fragmented', 'stationary'], ['continuous', 'fragmented'] or ['continuous'], ['fragmented'], or ['stationary']")

## bayesian helper functions
def logsumexp_normalize(log_probs):
    """ Numerically stable exp-normalize of log-probs (2D tensor) """
    log_probs = log_probs - torch.max(log_probs, dim=1, keepdim=True).values
    probs = torch.exp(log_probs)
    return probs / torch.sum(probs, dim=1, keepdim=True)

def log_p_norm(log_p):
    log_p = log_p - torch.max(log_p)  # for numerical stability
    posterior_probs = torch.exp(log_p)
    posterior_probs = posterior_probs / torch.sum(posterior_probs)  # normalize to 1
    return posterior_probs

def get_cmap(name="Blues"):
    cmap_og = plt.get_cmap(name)
    rgba_lin = cmap_og(np.arange(cmap_og.N))
    rgba_lin[:,-1] = np.linspace(0, 1, cmap_og.N)
    return ListedColormap(rgba_lin)

def get_occupancy(x, y, bins, cutoff, dt):
        occupancy, _, _ = np.histogram2d(x, y, bins)
        occupancy = occupancy / (1 / dt)
        occupancy[occupancy < cutoff] = 0
        return occupancy

#GLM helper function for the NaiveBayesDecoder
def glm_run(Xr, Yr, X_range):

    X2 = sm.add_constant(Xr)

    poiss_model = sm.GLM(Yr, X2, family=sm.families.Poisson())
    try:
        glm_results = poiss_model.fit()
        #glm_results = poiss_model.fit_regularized(alpha=0.1, L1_wt=0) # regularization does not work well here
        Y_range=glm_results.predict(sm.add_constant(X_range))
    except np.linalg.LinAlgError:
        print("\nWARNING: LinAlgError")
        Y_range=np.mean(Yr)*np.ones([X_range.shape[0],1])
    except ValueError:
        print("\nWARNING: ValueError")
        Y_range=np.mean(Yr)*np.ones([X_range.shape[0],1])

    return Y_range

def get_rate_map_cpu(spike_counts, x_positions, y_positions, x_edges, y_edges, 
                     occupancy, smooth_sigma=1.0, mask_nans=True):
    if mask_nans:
        valid_mask = (~np.isnan(x_positions) &
                    ~np.isnan(y_positions) &
                    ~np.isnan(spike_counts))

        x_positions = x_positions[valid_mask]
        y_positions = y_positions[valid_mask]
        spike_counts = spike_counts[valid_mask]

    spike_map, _, _ = np.histogram2d(
        x_positions, y_positions,
        bins=[x_edges, y_edges],
        weights=spike_counts
    )

    with np.errstate(divide='ignore', invalid='ignore'):
        rate_map = spike_map / occupancy
        rate_map[occupancy == 0] = np.nan  # mask empty bins

    if smooth_sigma > 0:
        mask = np.isnan(rate_map)
        rate_map[mask] = 0
        rate_map = gaussian_filter(rate_map, sigma=smooth_sigma)
        rate_map[mask] = np.nan

    return rate_map

def gaussian_kernel2d(kernel_size: int, sigma: float, device='cpu'):
    """Returns a 2D Gaussian kernel as a 4D tensor for conv2d."""
    ax = torch.arange(kernel_size, device=device) - kernel_size // 2
    xx, yy = torch.meshgrid(ax, ax, indexing='ij')
    kernel = torch.exp(-(xx**2 + yy**2) / (2. * sigma**2))
    kernel /= kernel.sum()

    # Shape (out_channels, in_channels/groups, H, W) for conv2d
    kernel = kernel.view(1, 1, kernel_size, kernel_size)
    return kernel

def smooth_rate_maps(rate_maps: torch.Tensor, sigma: float, kernel_size: int = None):
    """
    Applies 2D Gaussian smoothing to a batch of rate maps on GPU.
    rate_maps: (N, H, W)
    Returns: smoothed rate_maps (N, H, W)
    """
    device = rate_maps.device
    N, H, W = rate_maps.shape

    # NaN-safe mask
    nan_mask = torch.isnan(rate_maps)
    rate_maps = rate_maps.clone()
    rate_maps[nan_mask] = 0

    # Create Gaussian kernel
    if kernel_size is None:
        kernel_size = int(6 * sigma + 1) | 1  # ensure odd

    kernel = gaussian_kernel2d(kernel_size, sigma, device=device)

    # Prepare for conv2d: shape (N, 1, H, W)
    x = rate_maps.unsqueeze(1)

    # Weight mask to preserve valid regions
    weight_mask = (~nan_mask).float().unsqueeze(1)

    # Convolve
    smoothed = F.conv2d(x, kernel, padding=kernel_size // 2, groups=1)
    weights = F.conv2d(weight_mask, kernel, padding=kernel_size // 2, groups=1)

    # Normalize and restore NaNs
    smoothed = smoothed / weights
    smoothed[weights == 0] = float('nan')

    return smoothed.squeeze(1)  # shape: (N, H, W)


def get_rate_maps_torch(spike_counts_all, x_positions, y_positions, x_edges, y_edges, 
                        occupancy, smooth_sigma=1.0, mask_nans=True):
    device = spike_counts_all.device

    # remove nan data
    if mask_nans:
        # Find timepoints that are valid across all inputs
        valid_mask = (~torch.isnan(x_positions) &
                      ~torch.isnan(y_positions) &
                      ~torch.any(torch.isnan(spike_counts_all), dim=0))

        x_positions = x_positions[valid_mask]
        y_positions = y_positions[valid_mask]
        spike_counts_all = spike_counts_all[:, valid_mask]

    # handle position data
    n_bins_x, n_bins_y = len(x_edges)-1, len(y_edges)-1
    x_bin_idx = torch.bucketize(x_positions, x_edges) - 1
    y_bin_idx = torch.bucketize(y_positions, y_edges) - 1
    x_bin_idx = x_bin_idx.clamp(0, n_bins_x - 1)
    y_bin_idx = y_bin_idx.clamp(0, n_bins_y - 1)
    linear_idx = x_bin_idx * n_bins_y + y_bin_idx
    n_bins_total = n_bins_x * n_bins_y

    # count spikes
    n_units = spike_counts_all.shape[0]
    spike_maps = torch.zeros((n_units, n_bins_total), device=device)
    for i in range(n_units):
        spike_maps[i] = torch.bincount(linear_idx, weights=spike_counts_all[i], minlength=n_bins_total)
    spike_maps = spike_maps.reshape(n_units, n_bins_x, n_bins_y)

    # convert to rate
    occupancy_safe = occupancy.clone()
    occupancy_safe[occupancy_safe == 0] = float('inf')
    rate_maps = spike_maps / occupancy_safe  # broadcast

    # smooth
    if smooth_sigma > 0:
        spike_maps_cpu = spike_maps.cpu().numpy()
        smoothed_occupancy = gaussian_filter(occupancy.cpu().numpy(), sigma=smooth_sigma)
        for i in range(n_units):
            spike_maps_cpu[i] = gaussian_filter(spike_maps_cpu[i], sigma=smooth_sigma)
        spike_maps = torch.tensor(spike_maps_cpu, device=device)
        rate_maps = spike_maps / torch.tensor(smoothed_occupancy, device=device)
        # rate_maps_cpu = rate_maps.cpu().numpy()
        # for i in range(n_units):
        #     rate_maps_cpu[i] = gaussian_filter(rate_maps_cpu[i], sigma=smooth_sigma)
        # rate_maps = torch.tensor(rate_maps_cpu, device=device)

    # mask
    rate_maps[:, occupancy == 0] = float('nan')

    return rate_maps





# class BayesDecoderCPU(object):
#     def __init__(self, 
#                  recording:BinnedRecording,
#                  bins=None,
#                  encoding_model='quadratic',
#                  ):
#         self.recording = recording
#         self.encoding_model = encoding_model
#         self.bins = bins
#         self.X = self.recording.spike_array
#         self.y = np.vstack([self.recording.behavior_data.prey_location_x, 
#                             self.recording.behavior_data.prey_location_y]).T
#         self.remove_nans()
#         self.location_bins = self.get_location_bins()
#         self.tuning_all = None

#     def remove_nans(self):
#         invalid = np.any(np.isnan(self.X), axis=1) | np.any(np.isnan(self.y), axis=1)
#         self.X = self.X[~invalid, :]
#         self.y = self.y[~invalid, :]

#     def get_location_bins(self):
#         bin_centers = self.bins[:-1] + np.mean(np.diff(self.bins)) / 2
#         input_mat = np.meshgrid(bin_centers, bin_centers)
#         xs = np.reshape(input_mat[0],[bin_centers.shape[0]*bin_centers.shape[0],1])
#         ys = np.reshape(input_mat[1],[bin_centers.shape[0]*bin_centers.shape[0],1])
#         return np.concatenate((xs,ys),axis=1)
    
#     def fit(self):
#         if self.encoding_model == 'linear':
#             location_bins = self.location_bins.copy()
#             y = self.y
#         elif self.encoding_model == 'quadratic':
#             location_bins_orig = self.location_bins.copy()
#             location_bins = np.empty([location_bins_orig.shape[0],5])
#             location_bins[:,0] = location_bins_orig[:,0] ** 2
#             location_bins[:,1] = location_bins_orig[:,0]
#             location_bins[:,2] = location_bins_orig[:,1] ** 2
#             location_bins[:,3] = location_bins_orig[:,1]
#             location_bins[:,4] = location_bins_orig[:,0] * location_bins_orig[:,1]
#             y_orig = self.y.copy()
#             y = np.empty([y_orig.shape[0],5])
#             y[:,0] = y_orig[:,0] ** 2
#             y[:,1] = y_orig[:,0]
#             y[:,2] = y_orig[:,1] ** 2
#             y[:,3] = y_orig[:,1]
#             y[:,4] = y_orig[:,0] * y_orig[:,1]

#         if (self.encoding_model == 'linear') | (self.encoding_model == 'quadratic'):
#             n = self.X.shape[1]
#             spike_maps = np.zeros([n, self.location_bins.shape[0]])
#             for j in tqdm(range(n)):
#                 tuning = glm_run(y, self.X[:,j:j+1], location_bins)
#                 spike_maps[j,:] = np.squeeze(tuning)
#         else:
#             spike_maps = RateMaps(self.recording)
#         self.tuning_all = spike_maps

#         dx = np.sqrt(np.sum(np.diff(self.y, axis=0)**2, axis=1))
#         std = np.sqrt(np.mean(dx**2))
#         self.std = std

#     def predict(self, recording:BinnedRecording, return_posterior=False, smooth_constraint=False):
#         X_test = recording.spike_array
#         y_test = np.vstack([recording.behavior_data.prey_location_x, 
#                             recording.behavior_data.prey_location_y]).T
        
#         if smooth_constraint:
#             # probability distribution based on distance from each bin in the space, scaled by average speed
#             dists = squareform(pdist(self.location_bins), 'euclidean')
#             prob_dists = norm.pdf(dists, 0, self.std)

#         # initialize
#         loc_idx = np.argmin(cdist(y_test[0:1,:], self.location_bins))
#         y_test_predicted = np.empty([X_test.shape[0], 2])
#         nt = X_test.shape[0]
#         posterior = []

#         # loop through each time point
#         for t in tqdm(range(nt), desc='Reconstructing location...'):
#             rs = X_test[t,:].astype(int)
#             rs[rs > 170] = 170

#             # bayes rule
#             probs = np.exp(-self.tuning_all) * self.tuning_all ** rs[:,np.newaxis] / factorial(rs[:,np.newaxis])
#             probs_final = np.prod(probs, axis=0)
#             if smooth_constraint:
#                 probs_final = probs_final * prob_dists[loc_idx,:]
#             loc_idx = np.argmax(probs_final)
#             y_test_predicted[t,:] = self.location_bins[loc_idx,:]
#             if return_posterior:
#                 posterior.append(probs_final)
            
#         if return_posterior:
#             return y_test_predicted, posterior
#         else:
#             return y_test_predicted  