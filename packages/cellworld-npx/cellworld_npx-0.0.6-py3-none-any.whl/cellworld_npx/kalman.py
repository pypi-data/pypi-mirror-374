from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag
import numpy as np
import matplotlib.pyplot as plt

def kalman_smoother(x, t, dt=1/90, q=0.01, r=1e-3, p=1, return_results=False, return_velocity=False):
    # parameters
    q = q / (dt)**2  # process noise: how much variability there is in the mouses movement (larger will overfit noise)
    r = r            # measurement noise: variability in sensor outputs
    p = p            # initial guess of noise in each dimension

    fk = KalmanFilter(4, 2)
    F = np.array([[1, dt],
                [0,  1]])
    fk.F = block_diag(F,F)
    fk.P = np.eye(4) * p
    fk.R *= r
    fk.x = np.array([[0., 0.1, 0., 0.1]]).T
    fk.H = np.array([[1, 0, 0, 0],
                    [0, 0, 1, 0]])
    Q = Q_discrete_white_noise(dim=2, dt=dt, var=q)
    fk.Q = block_diag(Q,Q)
    #mu, cov, _, _ = fk.batch_filter(locs)
    mu, cov, fk = variable_kalman_update(fk, x, t)
    M, P, C, _ = fk.rts_smoother(mu, cov)
    results = {'filter':fk, 'dt':dt, 'q':q, 'r':r, 'p':p,
                   'x':x, 't':t, 'x_hat':M[:,[0,2],:].squeeze(), 'mu':mu, 'cov':cov, 'mu_smooth':M}
    if return_velocity:
        velocity = get_velocity(M[:,[0,2],:].squeeze(), t)
    if return_results and return_velocity:
        return M[:,[0,2],:].squeeze(), results, velocity
    elif return_results and not return_velocity:
        return M[:,[0,2],:].squeeze(), results
    elif return_velocity and not return_results:
        return M[:,[0,2],:].squeeze(), velocity
    else:
        return M[:,[0,2],:].squeeze()
    
def variable_kalman_update(kf: KalmanFilter, z, dt):
    assert len(dt) == len(z)
    mu = []; cov = []
    for i,d in enumerate(dt):
        kf.F[~((kf.F == 0.) | (kf.F == 1.))] = d - dt[i-1]
        kf.predict()
        kf.update(z[i,:])
        mu.append(kf.x)
        cov.append(kf.P)
    return np.array(mu), np.array(cov), kf
    
def plot_residual_limits(Ps, stds=1., ax=None):
    """ plots standard deviation given in Ps as a yellow shaded region. One std
    by default, use stds for a different choice (e.g. stds=3 for 3 standard
    deviations.
    """
    if ax is None:
        _,ax = plt.subplots(1,1)
    std = np.sqrt(Ps) * stds

    ax.plot(-std, color='k', ls=':', lw=2)
    ax.plot(std, color='k', ls=':', lw=2)
    ax.fill_between(range(len(std)), -std, std,
                 facecolor='#ffff00', alpha=0.3)
    
def plot_kf_results(results):
    M = results['mu_smooth']
    mu = results['mu']
    cov = results['cov']
    locs = results['x']
    time = results['t']

    fig, ax = plt.subplots(4,1, figsize=(5, 15))

    ax[0].plot(M[:,0,0].squeeze(), M[:,2,0].squeeze(), 'tab:orange', label='Kalman Smoothed')
    ax[0].plot(mu[:,0,0].squeeze(), mu[:,2,0].squeeze(), 'r--', label='Kalman')
    ax[0].plot(locs[:,0], locs[:,1], '.', label='data', zorder=0)
    ax[0].legend()
    ax[0].set_title(f"Q:{results['q']:0.2f}, R:{results['r']:0.2f}, P:{results['p']:0.2f}")
    ax[0].set_aspect('equal')


    vs = np.sqrt(np.sum(np.diff(M[:,[0,2],0],axis=0)**2,axis=1)) / np.diff(time,axis=0)
    vk = np.sqrt(np.sum(np.diff(mu[:,[0,2],0],axis=0)**2,axis=1)) / np.diff(time,axis=0)
    v = np.sqrt(np.sum(np.diff(locs,axis=0)**2,axis=1)) / np.diff(time,axis=0)
    ax[1].plot(v, 'tab:blue', label='data')
    ax[1].plot(vk, 'r--', zorder=3, label='kf')
    ax[1].plot(vs, 'tab:orange', zorder=4, label='kf smooth')
    ax[1].plot(M[:,1], 'tab:pink', label='kf smooth dx')
    ax[1].plot(M[:,3], 'tab:purple', label='kf smooth dy')
    ax[1].legend()
    ax[1].set_ylabel('velocity')

    plot_residual_limits(cov[:,0,0], 1, ax[2])
    ax[2].plot(locs[:,0] - mu[:,0,0].squeeze(), 'r--')
    ax[2].plot(locs[:,0] - M[:,0,0].squeeze(), color='tab:orange')
    ax[2].set_ylabel('residual x')


    dx = np.diff(locs[:,0]) / np.diff(time,axis=0)
    plot_residual_limits(cov[:,1,1], 1, ax[3])
    ax[3].plot(np.hstack((0,dx)) - mu[:,1,0].squeeze(), 'r')
    ax[3].plot(np.hstack((0,dx)) - M[:,1,0].squeeze(), '--', color='tab:orange')
    ax[3].set_ylabel('residual dx/dt')

def get_velocity(x, t):
    return np.hstack((0, np.sqrt(np.sum(np.diff(x,axis=0)**2,axis=1)) / np.diff(t,axis=0)))