from cellworld import Episode
from json_cpp import JsonObject, JsonList
import numpy as np

class RecordingEpisodes(JsonList):
    def __init__(self):
        super().__init__(list_type=RecordingEpisode)
    

class RecordingEpisode(JsonObject):
    def __init__(self):
        self.number = int()
        self.frame_times = list()
        self.start_time = float()
        self.end_time = float()
        self.drift_coeffs = list()
        self.valid_episode = bool()
        self.capture_times = list()
        self.reward_sequence = list()
        self.reward_times = list()
        self.episode = Episode


    def align_episode_times(self, z, episode=Episode):
        self.episode = episode
        self.drift_coeffs = z
        ts = episode.trajectories.get('time_stamp')
        self.frame_times = np.polyval(z, ts)
        self.start_time = np.polyval(z, np.min(ts))
        self.end_time = np.polyval(z, np.max(ts))
        # TODO: align capture timestamps
        self.capture_times = episode.captures
        self.reward_sequence = episode.rewards_sequence
        self.reward_times = np.polyval(z, episode.rewards_time_stamps)