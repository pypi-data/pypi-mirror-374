from cellworld import *
import numpy as np
import glob
from tqdm.notebook import tqdm
import pandas as pd
import matplotlib.path as mpath
import matplotlib.patches as mpatches
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.path import Path as path
from .kalman import kalman_smoother

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# Pose objects
class PosePart(JsonObject):
  def __init__(self):
    self.part = str()
    self.location = Location()
    self.camera = int()
    self.score = float()


class PartList(JsonList):
    def __init__(self):
        super().__init__(list_type=Pose)


class Pose(JsonList):
    def __init__(self):
        super().__init__(list_type=PosePart)


    def to_array(self, score=0.8):
        '''Covert pose to array'''
        return np.vstack([[i.location.x,i.location.y] for i in self if i.score > score])


    def get_part_feature(self, feature, part):
        '''Returns a pose feature for a specified part'''
        if 'location' in feature:
            x = [i.location for i in self if i.part == part]
        elif 'camera' in feature:
            x = [i.camera for i in self if i.part == part]
        elif 'score' in feature:
            x = [i.score for i in self if i.part == part]
        if len(x) > 0:
            return x[0]
        

    def get_pose_feature(self, feature, value):
        '''Returns a pose object where feature == value'''
        if feature == 'part':
            return [i for i in self if i.part == value][0]
        elif feature == 'camera':
            return [i for i in self if i.camera == value]
        elif feature == 'score':
            return [i for i in self if i.score == value]
        elif feature == 'score<':
            return [i for i in self if i.score < value]
        elif feature == 'score>':
            return [i for i in self if i.score > value]
        elif feature == 'score<=':
            return [i for i in self if i.score <= value]
        elif feature == 'score>=':
            return [i for i in self if i.score >= value]


    def angle(self, parts=['head_base','nose']):
        '''Get angle between two parts of pose object'''
        loca = self.get_part_feature('location', parts[0])
        locb = self.get_part_feature('location', parts[1])
        return to_degrees(loca.atan(locb))


    def transform(self, origin=Location(0,0), offset=Location(0,0), rotation=0):
        '''Transforms a pose object by offsetting and rotating around an origin'''
        for i,p in enumerate(self):
            p.location = p.location + offset
            r = rotate([p.location.x,p.location.y],
                    origin=[origin.x,origin.y],
                    degrees=-rotation)
            p.location = Location(r[0],r[1])


    def normalize(self, reference_part='head_base'):
        '''Rotates pose to face left->right with head at origin'''
        ref_loc = self.get_part_feature('location', reference_part)
        ref_angle = 90 - self.get_pose_angle()
        offset = Location(0,0) - ref_loc
        return self.transform(origin=Location(0,0), offset=offset, rotation=ref_angle)


    def pose_inside_arena(self, d, cutoff = 0):
        '''Returns true if all parts are inside the arena'''
        pose_points = self.to_array(score=cutoff)
        path = d.habitat_polygon.get_path()
        transform = d.habitat_polygon.get_patch_transform()
        newpath = transform.transform_path(path)
        polygon = mpatches.PathPatch(newpath)
        inside = []
        inside.append(newpath.contains_points(pose_points))
        return np.all(np.vstack(inside))


    def pose_inside_occlusions(self, d, cutoff = 0):
        '''Returns true if any part is in an occlusion'''
        pose_points = self.to_array(score=cutoff)
        inside = []
        for poly in d.cell_polygons:
            if poly._facecolor[0]==0:
                path = poly.get_path()
                transform = poly.get_patch_transform()
                newpath = transform.transform_path(path)
                polygon = mpatches.PathPatch(newpath)
                inside.append(newpath.contains_points(pose_points))
        return np.any(np.vstack(inside))


    def pose_is_ordered(self):
        '''Checks if pose parts are in roughly the right order'''
        return all([i.location.x <= 0 for i in self.normalize() if not 'nose' in i.part])


    def plot(self, ax=plt, **plt_kwargs):
        '''Plots pose'''
        ppoints = []
        npoint = []
        hpoint = []
        for p in self:
            if 'nose' in p.part:
                npoint = [p.location.x,p.location.y]
            elif 'head' in p.part:
                hpoint = [p.location.x,p.location.y]
            else:
                ppoints.append([p.location.x,p.location.y])
        ppoints = np.vstack(ppoints)
        hpoint = np.hstack(hpoint)
        npoint = np.hstack(npoint)
        h = []
        h.append(ax.scatter(ppoints[:,0],ppoints[:,1],**plt_kwargs))
        h.append(ax.plot(hpoint[0],hpoint[1],'*',color=h[0].get_facecolors()[0]))
        h.append(ax.plot(npoint[0],npoint[1],'^',color=h[0].get_facecolors()[0]))
        return(h)


    def match_pose(self, pose1, ref_part='head_base'):
        '''Transforms pose1 to match reference pose object based on reference part location and head angle'''
        # get reference location and head angle
        ref_loc = self.get_part_feature('location', ref_part)
        ref_angle = self.get_pose_angle()

        # get the source location and head angle
        src_loc = pose1.get_part_feature('location', ref_part)
        src_angle = pose1.get_pose_angle()

        # calculate location and angle offset
        a = ref_angle - src_angle
        if a > 180:
            a -= 360
        if a < -180:
            a += 360
        offset = (ref_loc - src_loc)

        # offset and rotate
        pose_norm = pose1.transform(origin=ref_loc,offset=offset,angle=a)

        return pose_norm, src_angle, src_loc, ref_angle, ref_loc




# general functions
def rotate(p, origin=(0, 0), degrees=0):
    '''Rotates point p around [origin] by [degrees]'''
    angle = np.deg2rad(degrees)
    R = np.array([[np.cos(angle), -np.sin(angle)],
                  [np.sin(angle),  np.cos(angle)]])
    o = np.atleast_2d(origin)
    p = np.atleast_2d(p)
    return np.squeeze((R @ (p.T-o.T) + o.T).T)

def get_angle(a, b):
    vec = np.array(a) - np.array(b)
    rad = np.arctan2(vec[1], vec[0])
    return (np.degrees(rad)) % 360

def contains(points, poly_points):
    poly_path = path(poly_points)
    return poly_path.contains_points(points)

def get_head_angles(pose, head=3, nose=0, l_ear=1, r_ear=2):
    '''calculates head angles from pose array
        - assumes pose is n parts x m times x 2 positions
        - assumes part order is: [nose, left ear, right ear, head, etc.]
    '''
    if len(pose.shape) == 2:
        pose = pose[:,np.newaxis,:]
    head_angles = get_angle(pose[nose,:,:].squeeze().T, pose[head,:,:].squeeze().T)
    ear_angles = (get_angle(pose[r_ear,:,:].squeeze().T, pose[l_ear,:,:].squeeze().T) + 90) % 360
    lear_head_angles = (get_angle(pose[head,:,:].squeeze().T, pose[l_ear,:,:].squeeze().T) + 90) % 360
    rear_head_angles = (get_angle(pose[r_ear,:,:].squeeze().T, pose[head,:,:].squeeze().T) + 90) % 360
    return [head_angles, ear_angles, lear_head_angles, rear_head_angles]

def get_head_angle(pose):
    '''return head angles if head and nose are valid, otherwise, return mean of ear-head, ear-nose angles'''
    head_angles = np.vstack(get_head_angles(pose))
    if len(head_angles.shape) == 1:
        head_angles = np.atleast_2d(head_angles)
    head_angles = head_angles.T
    angles = np.ones(head_angles.shape[0]) * np.nan
    head_valid = ~np.isnan(head_angles[:,0]).squeeze()
    if np.any(head_valid):
        angles[head_valid] = head_angles[head_valid,0].squeeze()
    if np.any(~head_valid):
        angles[~head_valid] = average_angles(head_angles[~head_valid,:].squeeze())
    return angles.squeeze() % 360

def smooth_head_position(x, t, q=1, dt=1/30, return_velocity=False):
    x = assert_2d(x)
    nan_filter = ~np.any(np.isnan(x),1)
    if return_velocity:
        xy, v = kalman_smoother(x=x[nan_filter,:], t=t[nan_filter], dt=dt, q=q, return_velocity=return_velocity)
        filtered_location = np.ones(x.shape) * np.nan
        filtered_location[np.where(nan_filter),:] = xy
        velocity = np.ones(x.shape[0]) * np.nan
        velocity[np.where(nan_filter)] = v
        return filtered_location, velocity
    else:
        xy = kalman_smoother(x=x[nan_filter,:], t=t[nan_filter], dt=dt, q=q)
        filtered_location = np.ones(x.shape) * np.nan
        filtered_location[np.where(nan_filter),:] = xy
        return filtered_location
    

def average_angles(angles_degrees):
    '''averages angles considering circular wrap'''
    angles_radians = np.deg2rad(angles_degrees)
    x = np.cos(angles_radians)
    y = np.sin(angles_radians)
    x = np.atleast_2d(x); y = np.atleast_2d(y)
    average_radians = np.arctan2(np.nanmean(y, axis=1), np.nanmean(x, axis=1))
    return np.rad2deg(average_radians)

def get_median_nose_distance(pose):
    I = np.argwhere(~np.isnan(pose[0,:,0].squeeze()) & ~np.isnan(pose[3,:,0].squeeze())).squeeze()
    dx = (pose[0,I,0] - pose[3,I,0]) ** 2
    dy = (pose[0,I,1] - pose[3,I,1]) ** 2
    return np.median(np.sqrt(dx + dy))

def get_head_position(pose, head_angle, nose_distance=0.01):
    if len(pose.shape) == 2:
        pose = pose[:,np.newaxis,:]
    head_position = np.ones((pose.shape[1], 2)) * np.nan
    head_tracked = ~np.isnan(pose[3,:,0].squeeze())
    nose_tracked = ~np.isnan(pose[0,:,0].squeeze())
    ears_tracked = ~np.isnan(pose[1,:,0].squeeze()) & ~np.isnan(pose[2,:,0].squeeze())
    # when the head is tracked, use that position
    I = head_tracked
    if np.any(I):
        head_position[I,:] = pose[3,I,:].squeeze()
    # if the head is not tracked, but the ears are, use the point between the ears
    I = ~head_tracked & ears_tracked
    if np.any(I):
        p = pose[[1,2],:,:]
        head_position[I,:] = np.mean(p[:,I,:], axis=0).squeeze()
    # if the head is not tracked, both ears are not tracked, but the nose is tracked, 
    # use the head angle and assumed nose distance to extrapolate
    # TODO: test this more thorougly, alternative is to use direction to body mid or other points
    I = ~head_tracked & ~ears_tracked & nose_tracked
    if np.any(I):
        head_position[I,0] = pose[0,I,0].squeeze() + nose_distance * np.cos(np.deg2rad(head_angle[I]))
        head_position[I,1] = pose[0,I,1].squeeze() + nose_distance * np.sin(np.deg2rad(head_angle[I]))
    return head_position


def get_episode_files(path, exp_name, episode, ext='.h5'):
    '''Looks for files in new experimental directory structure'''
    return glob.glob(f'{path}/episode_{episode:03d}*{exp_name}*{ext}')


def get_pose_from_file(file):
    '''Loads pose dataframe from a DeepLabCut .h5 file'''
    try:
        df = pd.read_hdf(file)
    except:
        return None, None
    base = df.keys()[0][0]
    parts = list(df.columns.levels[1])
    return df[base], parts


def get_parts_from_series(series):
    '''Gets part names from DLC pose series (pose information for a frame)'''
    return series.index.get_level_values('bodyparts').unique().to_list()


def pose_array(pose, likelihood_cutoff=0.8):
    pose_mat = []
    parts = pose.columns.get_level_values(0).unique().to_list()
    for p in parts:    
        pose_mat.append([pose[p]['x'].to_numpy(), pose[p]['y'].to_numpy(), pose[p]['likelihood'].to_numpy()])
    P = np.reshape(np.vstack(pose_mat), (8, 3, -1))

    if likelihood_cutoff is not None:
        nanmask = (P[:,-1,:] < likelihood_cutoff)
        nanmask = np.repeat(nanmask[:,np.newaxis,:], 3, axis=1)
        P[nanmask] = np.nan
    return P


def dlc_to_pose(pose_frame,
                input_space,
                output_space,
                camera=0,
                offset=Location(0,0),
                crop_center=Location(150/2-1, -150/2+1)):
    '''Converts a frame from a DeepLabCut dataframe to a Pose object in a different space'''
    parts = get_parts_from_series(pose_frame)

    # offset the location of each part in a new pose list
    pose = Pose()
    for part in parts:
        pose_part = PosePart()
        pixel_offset = Location(pose_frame[part].x, pose_frame[part].y*-1) - crop_center
        canonical_offset = Space.transform_to(pixel_offset, input_space, output_space)

        pose_part.location = offset + canonical_offset
        pose_part.part = part
        pose_part.camera = camera
        pose_part.score = pose_frame[part].likelihood
        pose.append(pose_part) 
    return pose


def get_experiment_spaces(experiment):
    '''Returns a dictionary containing the experiment world, and the canonical, raw, and CV spaces'''
    # world
    world = World.get_from_parameters_names('hexagonal', 'canonical', experiment.occlusions)
    
    # raw camera space (ie. the pixel space for deeplabcut)
    raw_space = world.implementation.get_from_name('hexagonal', 'cv').space
    raw_space.center = Location(1024, 1024) # Location(1024, 1020)
    raw_space.transformation.size = 2048

    # pixel space (in the main video)
    pixel_space = world.implementation.get_from_name('hexagonal', 'cv').space

    # canonical space
    canon_space = world.implementation.space

    return {'world': world, 'raw_space': raw_space, "pixel_space": pixel_space, 'canonical_space': canon_space}


def location_to_camera(location = Location(), center_coordinates = (0.5, 0.5)):
    '''Converts Location() to camera according to quadrants'''
    if location.x < center_coordinates[0]:
        if location.y < center_coordinates[1]:
            return 0
        else:
            return 2
    else:
        if location.y < center_coordinates[1]:
            return 1
        else:
            return 3


def add_pose_to_experiment(log_file = str(), dlc_folder = str(), output_file = str()):
    ''''Writes an experiment log with Pose() objects addef to data field. Also appends head angle to rotation in prey steps'''
    # by default write new log to folder of old log
    if not output_file:
        output_file = log_file.replace('.json','_pose.json',1)

    # load experiment and spaces
    experiment = Experiment.load_from_file(log_file)
    #print(log_file)
    spaces = get_experiment_spaces(experiment)
    #print(output_file)

    # for each episode
    for episode in tqdm(range(len(experiment.episodes))):
        
        # load the pose data for each camera
        episode_files = get_episode_files(dlc_folder, experiment.name, episode)
        pose = []
        for f in episode_files:
            pose.append(get_pose_from_file(f)[0])
        #print(episode_files)

        if not pose:
            print(f'pose data missing for episode {episode}... skipping')
            continue

        # for each step
        for i, step in enumerate(experiment.episodes[episode].trajectories):

            if step.agent_name == 'prey':

                frame = step.frame

                # determine the best camera and get pose
                best_cam = location_to_camera(step.location, (0.5, 0.5))
                try:
                    p = pose[best_cam].iloc[frame]
                    data = dlc_to_pose(p,
                                   spaces['raw_space'],
                                   spaces['canonical_space'],
                                   camera=best_cam,
                                   offset=step.location)
                    angle = data.angle()
                except:
                    print(f'{frame} not found in pose video!')
                    data = Pose()
                    angle = []
                
                # update the log
                step.data = str(data)
                step.rotation = angle

            experiment.episodes[episode].trajectories[i] = step

    experiment.save(output_file)

def assert_2d(x):
    x = x.squeeze()
    assert len(x.shape) == 2, f'array must be 2d, but shape is {x.shape}'
    assert 2 in x.shape, f'one dimension of x must be 2, but shape is {x.shape}'
    if x.shape[0] == 2:
        x = x.T
    return x

def get_matched_times(t1, t2, thresh=1/30):
    dt = []
    for t in t1:
        dt.append(np.min(np.abs(t - t2)))
    return np.array(dt) < thresh


    







def build_pose_library(logs,filename='./_data/logs/_pose_library.pkl'):
    '''
    Builds a pose library from a list of .json logs
    Inputs:
    - logs: list of .json logs
    - filename: .pkl file name for dataframe
    Returns:
    - df: dataframe where each row represents a frame where the mouse was visible
        'mouse': mouse ID
        'session': date and time of experiment
        'experiment_type': experiment type
        'world': world ID
        'episode': episode number
        'frame': frame number
        'pose': pose object (JsonList)
        'pose_norm': normalized pose object (head facing east, centered at (0,0))
        'head_angle': head angle of the mouse
        'pose_ordered': whether this pose is in reasonable order (body behind nose, roughly)
        'start_dist': distance from start of habitat (Location(0.01,0.5))
        'score_mean': mean of pose scores
        'score_std': std of pose scores
        'score_max': max of pose scores,
        'predator_location': Location of predator
        'predator_angle': orientation of predator
        'log_file': location of the log file for this frame}
    '''

    if glob.glob(filename):
        print(f'{filename} found, loading...')
        df = pd.read_pickle(filename)
        return df

    start_location = Location(0.01,0.5)

    d = {}
    cnt = 0
    for i in tqdm(range(len(logs))):
        # load experiment
        e = Experiment.load_from_file(logs[i])

        # get filename
        fn = e.name.split('_')
        mouse = fn[3]
        session = '_'.join(fn[1:3])
        world = '_'.join(fn[4:6])
        experiment_type = fn[-1]

        # remove bad episodes
        e.remove_episodes(\
        e.get_broken_trajectory_episodes() + \
        e.get_wrong_goal_episodes() + \
        e.get_wrong_origin_episodes() + \
        e.get_incomplete_episodes())

        # print(e.name)
        # print('\t',end='')

        for j,ep in enumerate(e.episodes):

            # get episode and trajectories
            episode = j
            pt = ep.trajectories.where('agent_name','prey').get_unique_steps()
            rt = ep.trajectories.where('agent_name','predator')
            # print(j,end=' ')

            # for each frame
            for step in pt:
                if step.data:
                    # prey info
                    frame = step.frame
                    pose = Pose.parse(step.data)
                    head_angle = step.rotation
                    start_dist = pose[1].location.dist(start_location)
                    score_mean = np.array([p.score for p in pose]).mean()
                    score_std = np.array([p.score for p in pose]).std()
                    score_max = np.array([p.score for p in pose]).max()
                    pose_ordered = pose.pose_is_ordered()

                    # predator info
                    rind = np.where(np.array(rt.get('frame'))==step.frame)[0]
                    if len(rind) > 0:
                        predator_location = rt[rind[0]].location
                        predator_angle = rt[rind[0]].rotation
                    else:
                        predator_location = np.nan
                        predator_angle = np.nan

                    # append to dict
                    d[cnt] = {
                        'mouse': mouse,
                        'session': session,
                        'experiment_type': experiment_type,
                        'world': world,
                        'episode': episode,
                        'frame': frame,
                        'pose': pose,
                        'pose_norm': pose.normalize(),
                        'head_angle': head_angle,
                        'pose_ordered': pose_ordered,
                        'start_dist': start_dist,
                        'score_mean': score_mean,
                        'score_std': score_std,
                        'score_max': score_max,
                        'predator_location': predator_location,
                        'predator_angle': predator_angle,
                        'log_file': logs[i]}
                    cnt = cnt + 1
        # print('\n')

    # save to file
    print(f'saving pose library to {filename}')
    df = pd.DataFrame.from_dict(d,'index')
    df.to_pickle(filename)

    return df