import numpy as np
from datetime import datetime
import re
from datetime import datetime, timedelta
from collections import defaultdict
from glob import glob
import os
from kilosort import run_kilosort
from time import sleep
from .probe import create_kilosort_probe


def find_file(folder, fstr, joined=False):
    for root,dirs,files in os.walk(folder):
        files = [f for f in files if fstr in f]
        if len(files) > 0:
            if joined:
                return [os.sep.join([root, f]) for f in files]
            else:
                return root, files
        
def find_files(folder, filestr, foldstr=''):
    """
    Lists files containing "fstr" in directory "folder". Optionally filter folders containing "foldstr".
    """
    d = []
    for root,dirs,files in os.walk(folder):
        file = [f for f in files if filestr in f]
        if (len(file) > 0) & (foldstr in root):
            d.append({'root': root, 'files': file})
    return d

def split_path(path):
    path = os.path.normpath(path)
    parts = path.split(os.sep)
    return parts

def walk_back(path, x:str):
    parts = split_path(path)
    i = [i for i in range(len(parts)) if x in parts[i]]
    assert len(i) == 1, f'multiple parent directories containing {x} found'
    return os.sep.join(parts[0:i[0]+1])

def match_date(dates, date, threshold=5*60):
    dt = np.abs(np.array([(date - t).total_seconds() for t in dates]))
    if any(dt < threshold):
        return np.argmin(dt)

def get_session_folders(sess_path=str):
    spk_path,_ = find_file(sess_path, 'cluster_group')
    beh_path,_ = find_file(sess_path, 'experiment.json')

    assert len(beh_path) > 0, f'No behavioral data found in {sess_path}'
    assert len(spk_path) > 0, f'No curated spike data found in {sess_path}'

    return spk_path, beh_path

def get_session_paths(sess_path=str):
    spk_path = find_files(sess_path, 'cluster_group')
    beh_path = find_files(sess_path, 'experiment.json')

    assert len(beh_path) > 0, f'No behavioral data found in {sess_path}'
    assert len(spk_path) > 0, f'No curated spike data found in {sess_path}'

    spk_paths = [f['root'] for f in spk_path]
    beh_paths = [f['root'] for f in beh_path]

    return spk_paths, beh_paths

def match_experiment_date(target_experiment, path_list=list, delta_t=3600):
    if type(target_experiment) != datetime:
        target_date = get_experiment_datetime(target_experiment)
    else:
        target_date = target_experiment
    dates = [get_experiment_datetime(p) for p in path_list]
    time_delta = [(d - target_date).total_seconds() for d in dates]
    candidate_experiments = [p for i,p in enumerate(path_list) if (np.abs(time_delta[i]) < delta_t)]
    return candidate_experiments

def get_experiment_datetime(experiment=str):
    if '\\\\' in experiment:
        experiment = experiment.split('\\\\')[-1]
    if '\\' in experiment:
        experiment = experiment.split('\\')[-1]
    return datetime.strptime('_'.join(experiment.split('_')[1:3]), '%Y%m%d_%H%M')

def match_session_paths(spike_folder=str, behavior_database='D:\\behavior', sort=False, pre=-5, post=60):
    spk_path = find_files(spike_folder, 'cluster_group')
    if (len(spk_path) == 0) & sort:
        binary_files = find_files(spike_folder, 'continuous.dat', 'Neuropix-PXI')
        print(f"{len(binary_files)} binary files found in {spike_folder}")
        for file in binary_files:
            print(f"\nRUNNING KILOSORT FOR {os.path.split(file['root'])[-1]}... this may take some time!")
            sleep(1)
            run_ks(file['root'], file['root'])
        spk_path = find_files(spike_folder, 'cluster_group')
    if len(spk_path) == 0:
        print(f'Warning: No curated spike data found in {spike_folder}, run kilosort.')
        spk_path = find_files(spike_folder, 'structure')

    # get behavioral sessions close to current spike session
    mouse = spike_folder.split(os.sep)[-2]
    spike_date = datetime.strptime(spike_folder.split(os.sep)[-1], '%Y-%m-%d_%H-%M-%S')
    path_list = os.listdir(behavior_database)
    path_list = [p for p in path_list if mouse in p and not os.path.isfile(os.path.join(behavior_database,p))]
    behavior_dates = [datetime.strptime('_'.join(p.split('_')[1:3]), '%Y%m%d_%H%M') for p in path_list]
    time_delta = [(b - spike_date).total_seconds() for b in behavior_dates]
    candidate_sessions = [p for i,p in enumerate(path_list) if (time_delta[i] > pre*60) & (time_delta[i] < post*60)]

    # check if any other spike sessions are a better match to the candidates
    spike_files = os.listdir(os.sep.join(spike_folder.split(os.sep)[:-1]))
    spike_files = [s for s in spike_files if 'BAD' not in s and 'bad' not in s and 'Bad' not in s]
    spike_dates = [datetime.strptime(f.split(os.sep)[-1], '%Y-%m-%d_%H-%M-%S') for f in spike_files]
    candidates = [datetime.strptime('_'.join(c.split('_')[1:3]), '%Y%m%d_%H%M') for c in candidate_sessions]
    mn = []
    for c in candidates:
        mn.append(np.min(np.abs([(c - sd).total_seconds() for sd in spike_dates])))
    better_candidates = np.array(mn) < np.min(np.abs(time_delta))
    if any(better_candidates):
        candidate_sessions = [c for i,c in enumerate(candidate_sessions) if not better_candidates[i]]

    spk_paths = [f['root'] for f in spk_path]
    beh_paths = [os.path.join(behavior_database, s) for s in candidate_sessions]
    
    return spk_paths, beh_paths

def get_episode_folders(behavior_path, return_valid=True):
    p = behavior_path

    if type(p) == list:
        folders = []
        episodes = []
        counter = 0
        for path in p:
            tmp = glob(os.path.join(path, 'episode_*'))
            folders.extend(tmp)
            episodes.extend([int(f.split(os.sep)[-1].split('_')[-1]) + counter for f in tmp])
            counter = counter + len(tmp)
    else:
        folders = glob(os.path.join(p, 'episode_*'))
        episodes = [int(f.split(os.sep)[-1].split('_')[-1]) for f in folders]

    if not return_valid:
        episode_is_valid = [1] * len(folders)
        return folders, episodes, episode_is_valid
    
    return get_valid_episodes(folders, episodes)

def get_valid_episodes(folders=list(), episodes=list()):
    valid_folders = []
    valid_episodes = []
    episode_is_valid = []
    sync_data_present = []
    for i,f in enumerate(folders):
        episode_file = glob(os.path.join(f, '*episode*.json'))
        sync_file = glob(os.path.join(f, '*sync*.json'))
        if (len(episode_file) > 0) & (len(sync_file) > 0):
            valid_folders.append(f)
            valid_episodes.append(episodes[i])
            episode_is_valid.append(1)
        else:
            episode_is_valid.append(0)
        if (len(sync_file) > 0):
            sync_data_present.append(1)
    return valid_folders, valid_episodes, episode_is_valid, sync_data_present

def run_ks(data_dir, results_dir=None, probe=None):
    if results_dir is None:
        results_dir = os.path.join(data_dir, '..', '..')
    if probe is None:
        root = os.path.join(data_dir, '..', '..', '..', '..')
        xml = [os.path.join(root, f) for f in os.listdir(root) if 'settings.xml' in f]
        assert len(xml) > 0, f'No settings.xml file found in {root}, must provide probe object to use for sorting!'
        probe = create_kilosort_probe(xml[0])

    settings = {'data_dir': data_dir, 'results_dir': results_dir, 'n_chan_bin':probe['n_chan']}
    ops, st, clu, tF, Wall, similar_templates, is_ref, est_contam_rate, kept_spikes = \
        run_kilosort(settings=settings, probe=probe)
    

def parse_datetime_from_string(s, pattern=r'\d{8}_\d{4}', dt_format='%Y%m%d_%H%M'):
    match = re.search(pattern, s)
    if match:
        return datetime.strptime(match.group(), dt_format)
    return None

# def group_by_time(strings, threshold_minutes=5, pattern=r'\d{8}_\d{4}', dt_format='%Y%m%d_%H%M'):
#     """
#     Groups strings based on timestamps within a certain time threshold.
    
#     Parameters:
#         strings (list): List of strings with datetime info.
#         threshold_minutes (int): Threshold in minutes to group by.
#         pattern (str): Regex pattern to extract datetime.
#         dt_format (str): Datetime format for parsing.
    
#     Returns:
#         list of lists: Groups of strings.
#     """
#     # Parse datetimes and filter out unparseable strings
#     parsed = [(s, parse_datetime_from_string(s, pattern, dt_format)) for s in strings]
#     parsed = [(s, dt) for s, dt in parsed if dt is not None]
#     parsed.sort(key=lambda x: x[1])  # Sort by time

#     groups = []
#     current_group = []

#     for s, dt in parsed:
#         if not current_group:
#             current_group.append((s, dt))
#         else:
#             last_dt = current_group[-1][1]
#             if (dt - last_dt) <= timedelta(minutes=threshold_minutes):
#                 current_group.append((s, dt))
#             else:
#                 groups.append([item[0] for item in current_group])
#                 current_group = [(s, dt)]
    
#     if current_group:
#         groups.append([item[0] for item in current_group])

#     return groups

def parse_datetime_and_suffix(s, pattern=r'\d{8}_\d{4}', dt_format='%Y%m%d_%H%M'):
    match = re.search(pattern, s)
    if match:
        dt_str = match.group()
        dt = datetime.strptime(dt_str, dt_format)
        suffix = s[match.end():]  # everything after the date
        return dt, suffix
    return None, None

def group_experiments(strings, threshold_minutes=15,
                      pattern=r'\d{8}_\d{4}', dt_format='%Y%m%d_%H%M'):
    """
    Groups strings if they are within a time threshold and have the same suffix.
    
    Parameters:
        strings (list): List of strings with datetime info.
        threshold_minutes (int): Threshold in minutes to group by.
        pattern (str): Regex pattern to extract datetime.
        dt_format (str): Datetime format for parsing.
    
    Returns:
        list of lists: Groups of strings.
    """
    parsed = []
    for s in strings:
        dt, suffix = parse_datetime_and_suffix(s, pattern, dt_format)
        if dt is not None:
            parsed.append((s, dt, suffix))

    # Group by suffix
    suffix_groups = defaultdict(list)
    for item in parsed:
        suffix_groups[item[2]].append((item[0], item[1]))  # key: suffix

    # Now group each suffix group by time
    final_groups = []
    for suffix, items in suffix_groups.items():
        items.sort(key=lambda x: x[1])  # sort by datetime
        current_group = []

        for s, dt in items:
            if not current_group:
                current_group.append((s, dt))
            else:
                last_dt = current_group[-1][1]
                if (dt - last_dt) <= timedelta(minutes=threshold_minutes):
                    current_group.append((s, dt))
                else:
                    final_groups.append([x[0] for x in current_group])
                    current_group = [(s, dt)]
        
        if current_group:
            final_groups.append([x[0] for x in current_group])
    
    return final_groups