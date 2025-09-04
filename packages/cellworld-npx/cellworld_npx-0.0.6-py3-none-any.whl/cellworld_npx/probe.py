from json_cpp import JsonObject, JsonList
import xml.etree.ElementTree as ET
import numpy as np
from sklearn.cluster import DBSCAN

class Probes(JsonList):
    def __init__(self, fn=''):
        super().__init__(list_type=Probe)
        if fn:
            for probe, processor in zip(*load_probes_from_xml(fn)):
                self.append(Probe(probe, processor))

class Probe(JsonObject):
    def __init__(self, probe=dict(), processor=dict()):
        self.name = str()
        self.reference = str()
        self.nchan = int()
        self.plugin_name = str()
        self.node_id = str()
        self.folder = str()
        self.channel_map = dict()
        self.info = dict()
        self.processor = dict()
        self.probe_id = str()

        if probe:
            self.type = probe['probe_name']
            self.probe_id = probe['probe_id']
            self.channel_map = probe['channel_map']
            self.reference = probe['referenceChannel']
            self.nchan = len(probe['channel_map']['x'])
            self.info = probe

        if processor:
            self.plugin_name = processor['name']
            self.node_id = processor['nodeId']
            self.name = '.'.join(['-'.join([self.plugin_name, self.node_id]), self.probe_id])
            self.processor = processor


class Processors(JsonList):
    def __init__(self, fn=''):
        super().__init__(list_type=Processor)

        if fn:
            for processor in load_processors_from_xml(fn):
                self.append(Processor(processor))

class Processor(JsonObject):
    def __init__(self, processor=dict()):
        self.name = str()
        self.description = str()
        self.sample_rate = float()
        self.channel_count = int()
        self.node_id = str()

        if processor:
            self.name = processor['name']
            self.description = processor['description']
            self.sample_rate = float(processor['sample_rate'])
            self.channel_count = int(processor['channel_count'])
            self.node_id = processor['source_node_id']


# class ChannelMap(JsonList):
#     def __init__(self, fn=''):
#         super().__init__(list_type=Channel)

# class Channel(JsonObject):
#     def __init__(self):
#         self.channel = int()
#         self.x = float()
#         self.y = float()
#         self.shank = int()


def load_recording_metadata(dir):
    # assumes metadata is two directories down
    fn = dir + '/../../settings.xml'
    processors = Processors(fn)
    probes = Probes(fn)
    return processors, probes


def load_processors_from_xml(fn):
    tree = ET.parse(fn)
    root = tree.getroot()
    sc = root.findall('SIGNALCHAIN')
    processors = []
    for s in sc:
        PROCESSORS = s.findall('PROCESSOR')
        for p in PROCESSORS:
            if 'Record Node' in p.attrib['name']:
                CUSTOM_PARAMS = p.findall('CUSTOM_PARAMETERS')
                cpSTREAMS = CUSTOM_PARAMS[0].findall('STREAM')
                pSTREAMS = p.findall('STREAM')
                for i,s in enumerate(pSTREAMS):
                    processors.append(s.attrib | cpSTREAMS[i].attrib)
    return processors


def load_probes_from_xml(fn):
    tree = ET.parse(fn)
    root = tree.getroot()
    sc = root.findall('SIGNALCHAIN')
    probes = []
    processors = []
    for s in sc:
        PROCESSORS = s.findall('PROCESSOR')
        for p in PROCESSORS:
            if 'Neuropix-PXI' in p.attrib['name']:
                STREAMS = p.findall('STREAM')
                EDITOR = p.findall('EDITOR')
                NP_PROBE = EDITOR[0].findall('NP_PROBE')
                for i,probe in enumerate(NP_PROBE):
                    processors.append(p.attrib)
                    tmp = probe.attrib
                    tmp['probe_id'] = STREAMS[i].attrib['name']
                    CHANNELS = probe.findall('CHANNELS')[0].attrib
                    XPOS = probe.findall('ELECTRODE_XPOS')[0].attrib
                    YPOS = probe.findall('ELECTRODE_YPOS')[0].attrib
                    c = []
                    i = []
                    x = []
                    y = []
                    for key in CHANNELS:
                        c.append(key)
                        i.append(CHANNELS[key])
                        x.append(int(XPOS[key]))
                        y.append(int(YPOS[key]))
                    channel_map = {}
                    channel_map['channels'] = c
                    channel_map['probe:shank'] = i
                    channel_map['x'] = x
                    channel_map['y'] = y
                    tmp['channel_map'] = channel_map
                    probes.append(tmp)
    return probes, processors


def create_kilosort_probe(s, probe_index=0):
    probes = load_probes_from_xml(s)[0]
    cm = probes[probe_index]['channel_map']
    nchan = len(cm['x'])
    channelID = [int(c.strip('CH')) for c in cm['channels']]
    probe = {}
    probe['chanMap'] = np.array(channelID) #np.arange(0, nchan)
    probe['xc'] = np.array(cm['x']).astype('float32')
    probe['yc'] = np.array(cm['y']).astype('float32')
    probe['kcoords'] = np.zeros(nchan)
    probe['n_chan'] = nchan
    return probe


def get_channel_map(probe_info, probe_index=0, order='lfp'):
    if type(probe_info) == str:
        probe_info = load_probes_from_xml(probe_info)[0][probe_index]
    if type(probe_info) == dict:
        cmap = probe_info['channel_map']
    else:
        cmap = probe_info.channel_map
    ch = np.array([int(c.strip('CH')) for c in cmap['channels']])
    x = np.array(cmap['x'])
    y = np.array(cmap['y'])
    si = np.argsort(ch)
    if order == 'spike':
        return np.vstack((ch[si], x[si], y[si])).T # this sorting works for kilosort output
    else:
        return np.vstack((ch, x, y)).T # this sorting works for lfp output

def channel_to_lfp(channels, lfp_channel_map):
    return np.argwhere(np.in1d(lfp_channel_map[:,0], channels)).squeeze()
    
def get_shank(x, bins=None):
    if bins is None:
        bins = np.linspace(-1, 791, 5)
    return np.digitize(x, bins, right=True)


def xy_to_site(xy=list(), type='np2'):
    sx, sy, ss = get_probe_sites(type)
    i = np.argmin(np.sqrt((xy[1] - sy)**2 + (xy[0] - sx)**2))
    shank = ss[i]
    sx = sx[ss == shank]; sy = sy[ss == shank]
    site = np.argmin(np.sqrt((xy[1] - sy)**2 + (xy[0] - sx)**2))
    return site, shank


def get_probe_sites(type='np2', x_offset=0, y_offset=0, return_metadata=False):
    if '2' in type:
        y_pitch = 15 # um
        x_pitch = 32 # um
        shank_pitch = 250 # um
        n_contacts = 1280
        x = []
        y = []
        shank = []
        for i in range(4):
            x.append(np.vstack((np.repeat(i * shank_pitch, n_contacts / 2), 
                    np.repeat(i * shank_pitch + x_pitch, n_contacts/2))).T.flatten())
            y.append(np.repeat(np.arange(0, n_contacts/2 * y_pitch, y_pitch), 2))
            shank.append(np.repeat(i, n_contacts))
            
    elif '1' in type:
        y_pitch = 20
        x_pitch = 32
        shank_pitch = 16
        n_contacts = 960

        x = np.repeat(shank_pitch + np.array([[0, x_pitch], [0, x_pitch]]), n_contacts/8, axis=0).flatten()
        y = np.repeat(np.arange(0, y_pitch*n_contacts/2, y_pitch*2), 2).astype(int)
        x = np.hstack((x, x - shank_pitch))
        y = np.hstack((y, y + y_pitch))
        si = np.argsort(y)
        x = x[si]; y = y[si]
        shank = np.zeros(x.shape)

    else:
        raise ValueError('type must be np1/np2')
    
    if return_metadata:
        meta = {'x_pitch': x_pitch, 'y_pitch': y_pitch, 'shank_pitch': shank_pitch, 'n_contacts': n_contacts}
        return np.hstack(x) + x_offset, np.hstack(y) + y_offset, np.hstack(shank), meta
    else:
        return np.hstack(x) + x_offset, np.hstack(y) + y_offset, np.hstack(shank)

def cluster_probe_channels(channel_map, eps=100, min_samples=10):
    dbs = DBSCAN(eps=eps, min_samples=min_samples).fit(channel_map[:,1:])
    return dbs.labels_




























# def load_processors_from_xml(fn):
#     '''
#     loads processing streams from settings.xml file generated by OpenEphys GUI

#     USAGE:
#     processors, probes = load_processors_from_xml(fn)

#     ARGUMENTS:
#     fn: filename of settings.xml file for Neuropixels recordings

#     RETURNS:
#     processors: a list of processors and their attributes (name, source node ID, sample rate, channels, etc)
#     probes: a list of probes and their attributes (name, headstage, serial number, recording slot, channel maps, etc)
#     '''
#     tree = ET.parse(fn)
#     root = tree.getroot()
#     sc = root.findall('SIGNALCHAIN')
#     processors = []
#     probes = []
#     for s in sc:
#         PROCESSORS = s.findall('PROCESSOR')
#         for p in PROCESSORS:
#             if 'Record Node' in p.attrib['name']:
#                 CUSTOM_PARAMS = p.findall('CUSTOM_PARAMETERS')
#                 cpSTREAMS = CUSTOM_PARAMS[0].findall('STREAM')
#                 pSTREAMS = p.findall('STREAM')
#                 for i,s in enumerate(pSTREAMS):
#                     processors.append(s.attrib | cpSTREAMS[i].attrib)

#             if 'Neuropix-PXI' in p.attrib['name']:
#                 processors.append(p.attrib)
#                 EDITOR = p.findall('EDITOR')
#                 NP_PROBE = EDITOR[0].findall('NP_PROBE')
#                 for probe in NP_PROBE:
#                     tmp = probe.attrib
#                     CHANNELS = probe.findall('CHANNELS')[0].attrib
#                     XPOS = probe.findall('ELECTRODE_XPOS')[0].attrib
#                     YPOS = probe.findall('ELECTRODE_YPOS')[0].attrib
#                     c = []
#                     i = []
#                     x = []
#                     y = []
#                     for key in CHANNELS:
#                         c.append(key)
#                         i.append(CHANNELS[key])
#                         x.append(int(XPOS[key]))
#                         y.append(int(YPOS[key]))
#                     channel_map = {}
#                     channel_map['channels'] = c
#                     channel_map['probe:shank'] = i
#                     channel_map['x'] = x
#                     channel_map['y'] = y
#                     tmp['channel_map'] = channel_map
#                     probes.append(tmp)
#     return processors, probes