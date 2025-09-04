import os
import subprocess
import getpass
from kilosort import run_kilosort
from time import sleep, time
from .probe import create_kilosort_probe
from .io import find_files
from .cluster_metrics import get_population


def run_powershell(command):
    process = subprocess.Popen(
        ["powershell.exe", "-Command", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(command)
    
    if stderr:
      print(f"Error: {stderr}")
    return stdout

def mount_drive(drive_letter='Z:', network_path='\\\\129.105.180.130\\DOMBECK_LAB', username='ads\\cfa3244', verbose=False):
    print(f'Mounting drive under user {username}, enter password above.')
    password = getpass.getpass("Enter password: ")
    command = f'net use {drive_letter} "{network_path}" {password} /user:{username} /Y'
    output = run_powershell(command)
    if verbose: print(output)
    if 'success' in output:
        if verbose: print(f'Drive mounted to {drive_letter}')
    elif 'error' in output:
        raise IOError('drive could not be mounted')

def backup_folder(folder, local='D:\\', remote='Z:\\Dombeck_Lab_Data_Backup\\Chris Angeloni\\spikes\\', username='ads\\cfa3244'):
    command = f"rclone copy '{local}{folder}\' '{remote}{folder}\' -P --exclude '/System Volume Information/**'"
    print('BACKING UP DATA USING THE FOLLOWING COMMAND:')
    print(f'\t{command}')
    t0 = time()
    output = run_powershell(command)
    if 'The system cannot find the path specified.' in output:
        print("No remote drive found during backup_folder")
        mount_drive(username=username)
        output = run_powershell(command)
    print(f'successfully finished (time elapsed = {time()-t0:0.2f}s)')

def pull_continuous_data(folder, local='D:\\', remote='Z:\\Dombeck_Lab_Data_Backup\\Chris Angeloni\\spikes\\', username='ads\\cfa3244'):
    command = f"rclone copy '{remote}{folder}\' '{local}{folder}\' -P --include 'continuous.dat'"
    print('PULLING CONTINUOUS DATA USING THE FOLLOWING COMMAND:')
    print(command)
    t0 = time()
    output = run_powershell(command)
    if ('The system cannot find the path specified.' in output) | ('directory not found' in output):
        print("No remote drive found during pull_continuous_data")
        mount_drive(username=username)
        output = run_powershell(command)
    print(f'successfully finished (time elapsed = {time()-t0:0.2f}s)')

def pull_file(remote_file, local_file, username='ads\\cfa3244'):
    command = f"rclone copyto '{remote_file}' '{local_file}' -P"
    print('PULLING CONTINUOUS DATA USING THE FOLLOWING COMMAND:')
    print(command)
    t0 = time()
    output = run_powershell(command)
    if ('The system cannot find the path specified.' in output) | ('directory not found' in output):
        print("No remote drive found during pull_continuous_data")
        mount_drive(username=username)
        output = run_powershell(command)
    print(f'successfully finished (time elapsed = {time()-t0:0.2f}s)')
    return local_file

def delete_file(fn, timeout=10):
    if os.path.exists(fn):
        print(f'WARNING: DELETING {fn} IN {timeout} SECONDS, PRESS CTRL-C TO CANCEL!')
        sleep(timeout)
        os.remove(fn)

def check_remote_file(f, file, source='D:\\', remote='Z:\\Dombeck_Lab_Data_Backup\\Chris Angeloni\\spikes\\', username='ads\\cfa3244'):
    remote_path = f['root'].replace(source, remote)
    if not os.path.exists(remote):
        print("No remote drive found during check_remote_file")
        mount_drive(username=username)
    spike_files = find_files(remote_path, file)
    if len(spike_files) > 0:
        return True
    else:
        return False
        
def start_kilosort(f, source='D:\\'):
    spike_files = find_files(f['root'], 'cluster_group')
    if len(spike_files) == 0:
        print(f"\nRUNNING KILOSORT FOR {os.path.split(f['root'])[-1]}... this may take some time!")
        sleep(1)
        run_ks(f['root'], f['root'])
    else:
        print(f"\nKILSORT RESULTS FOUND IN {os.path.split(f['root'])[-1]}... skipping!")

def extract_cluster_info(f, source='D:\\'):
    spike_files = find_files(f['root'], 'population')
    if len(spike_files) == 0:
        sleep(1)
        get_population(f['root'], save=True)
    else:
        print(f"\nPOPULATION FILE FOUND IN {os.path.split(f['root'])[-1]}... skipping!")

def run_kilosort_and_upload(mouse_name, source='D:\\', remote='Z:\\Dombeck_Lab_Data_Backup\\Chris Angeloni\\spikes\\', username='ads\\cfa3244'):
    if type(mouse_name) is not list:
        mouse_name = [mouse_name]

    for m in mouse_name:
        binary_files = find_files(os.path.join(source, m), 'continuous.dat', 'Neuropix-PXI')
        for b in binary_files:
            if 'LFP' not in b['root']:
                print(f'{m}: {b["root"]}')
                if not check_remote_file(b, 'cluster_group', remote=remote, username=username):
                    start_kilosort(b, source=source)
                if not check_remote_file(b, 'population', remote=remote, username=username):
                    try:
                        _ = extract_cluster_info(b, source=source)
                    except:
                        'Failed to extract cluster_info'
        backup_folder(m, source=source, remote=remote)

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