from cellworld import World, Location, Location_visibility
from .utils import distance, get_runs
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd

def get_worlds_dict(worlds):
    world_dict = {}
    for w in worlds:
        world = World.get_from_parameters_names('hexagonal', 'canonical', w)
        world_dict[w] = {'world': world, 'visibility': Location_visibility.from_world(world)}
    return world_dict

def get_captures(dist, vis=None, capture_radius=32, cooldown=1.0, fs=90, visible=True):
    if visible:
        assert vis is not None, 'visibility must be provided when visible is True'
        new_captures = ((dist < capture_radius) & vis).squeeze()
    else:
        new_captures = (dist < capture_radius).squeeze()
    new_captures = get_runs(new_captures, max_gap=cooldown*fs, min_duration=1)
    new_captures = np.vstack(new_captures)[:,0]
    new_captures = new_captures[new_captures > 0]
    return new_captures

def get_visible_captures(captures, prey_location, predator_location, visible):
    visible_captures = []
    for c in captures:
        if visible.is_visible(
            Location(prey_location[c,0], prey_location[c,1]),
            Location(predator_location[c,0], predator_location[c,1])) == 1:
            visible_captures.append(c)
    return visible_captures

def get_valid_captures(captures, capture_distance, capture_radius=32):
    valid_captures = []
    for i,c in enumerate(captures):
        if capture_distance[i] < capture_radius:
            valid_captures.append(c)
    return valid_captures

def extract_window(data, center_idx, window):
    pre_len = np.abs(np.min(window))
    post_len = np.max(window)

    start = center_idx - pre_len
    end = center_idx + post_len + 1  # +1 because slicing is exclusive

    pad_left = max(0, -start)
    pad_right = max(0, end - len(data))
    data_slice = data[max(0, start):min(len(data), end)]

    return np.pad(data_slice, (pad_left, pad_right), mode='constant', constant_values=np.nan)


def extract_time_window(data, time, center_time, window, step=None, atol=1e-2):
    t_before, t_after = (window.min(), window.max())
    win_start = center_time + t_before
    win_end = center_time + t_after

    # If step is not specified, estimate from minimum positive diff in time
    if step is None:
        diffs = np.diff(np.sort(np.unique(time)))
        step = np.min(diffs[diffs > 0])

    # Create array of desired time points in window
    num_points = int(np.round((win_end - win_start) / step)) + 1
    window_times = win_start + np.arange(num_points) * step

    # Output array
    out = np.full(len(window_times), np.nan)
    for i, t in enumerate(window_times):
        matches = np.isclose(time, t, atol=atol)
        if np.any(matches):
            out[i] = data[np.where(matches)[0][0]]  # take the first match

    return out


def shuffle_behavioral_data(values, visibility, window, fs=90, min_shuff=2):
    prey_location = np.vstack(values.prey_location) * 234
    predator_location = np.vstack(values.predator_location) * 234
    shift = np.random.randint(min_shuff*fs, len(prey_location)-min_shuff*fs)
    prey_location_shuff = np.roll(prey_location, shift=shift, axis=0)
    dist_shuff = distance(prey_location_shuff, predator_location)
    capture_candidates = get_captures(dist_shuff, visible=False)
    valid_captures = get_visible_captures(capture_candidates, prey_location_shuff / 234, predator_location / 234, visibility)
    d1 = len(valid_captures)
    if d1 == 0:
        d1 = 1
    dist = np.ones((d1, window.shape[0])) * np.nan
    for i, c in enumerate(valid_captures):
        dist[i,:] = extract_window(dist_shuff, c, window)
    return valid_captures, dist

def get_trial_captures(trial: pd.Series, window=np.arange(-90, 180)):
    captures = np.vstack(trial.captures)
    captures = np.atleast_1d(np.argwhere(trial.captures).squeeze())
    if len(captures) > 0:
        valid_captures = get_valid_captures(captures, trial.distance[trial.captures==True].values)
        dist = np.ones((len(valid_captures), window.shape[0])) * np.nan
        for i, c in enumerate(valid_captures):
            dist[i,:] = extract_window(trial.distance, c, window)
    else:
        valid_captures = []
        dist = np.ones((len(valid_captures), window.shape[0])) * np.nan
    return valid_captures, dist

def get_session_captures(values, window=np.arange(-90, 180)):
    capture_count = 0
    capture_distance = []
    for e in values.episode.unique():
        trial = values[values['episode'] == e]
        valid_captures, capture_distances = get_trial_captures(trial, window=window)
        capture_count = capture_count + len(valid_captures)
        capture_distance.append(np.nanmean(capture_distances, axis=0))
    capture_distance = np.nanmean(np.vstack(capture_distance), axis=0)
    return capture_count, capture_distance

def get_shuffled_captures(values, visibility, window=np.arange(-90, 180), fs=90, min_shuff=2):
    capture_count = 0
    capture_distance = []
    for e in values.episode.unique():
        trial = values[values['episode'] == e]
        if len(trial.prey_location) < (2*min_shuff+1)*fs:
            print(f'trial < {2*min_shuff+1}s, skipping...')
            continue
        valid_captures, capture_distances = shuffle_behavioral_data(trial, visibility, window=window, min_shuff=min_shuff)
        capture_count = capture_count + len(valid_captures)
        capture_distance.append(np.nanmean(capture_distances, axis=0))
    capture_distance = np.nanmean(np.vstack(capture_distance), axis=0)
    return capture_count, capture_distance
