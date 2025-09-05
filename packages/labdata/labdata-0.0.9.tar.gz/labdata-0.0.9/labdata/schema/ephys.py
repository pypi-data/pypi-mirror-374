from .general import *
from .procedures import *

@dataschema
class Probe(dj.Manual):
    definition = '''
    probe_id                  : varchar(32)    # probe id to keep track or re-uses
    ---
    probe_type                : varchar(12)    # probe type
    probe_n_shanks            : tinyint        # number of shanks
    probe_recording_channels  : int            # number of recording channels
    '''

@dataschema
class ProbeInsertion(dj.Manual):
    definition = '''
    -> Procedure
    -> Probe
    ---
    insertion_ap         : float   # anterior posterior distance from bregma
    insertion_ml         : float   # median lateral distance from bregma
    insertion_depth      : float   # insertion depth (how much shank is inserted from dura)
    insertion_el         : float   # elevation of the probe (angle)
    insertion_az         : float   # azimuth of the probe  (angle)
    insertion_spin = 0   : float   # spin on the probe shanks
    '''

@dataschema
class ProbeExtraction(dj.Manual):
    definition = '''
    -> Procedure
    -> Probe
    ---
    extraction_successful  : tinyint   # boolean for successfull or not
    '''
    
@dataschema
class ProbeConfiguration(dj.Manual):
    definition = '''
    -> Probe
    configuration_id  : smallint
    ---
    probe_n_channels  : int            # number of connected channels
    probe_gain        : float          # gain of the probe (multiplication factor) 
    channel_idx       : blob           # index of the channels
    channel_shank     : blob           # shank of each channel
    channel_coords    : blob           # channel x,y position
    '''
    def add_from_spikeglx_metadata(self,metadata):
        '''
        Metadata can be a dictionary (with the metadata) or the path to an ap.meta file.
        '''
        from ..rules.ephys import get_probe_configuration
        if not hasattr(metadata,'keys'):
            conf = get_probe_configuration(metadata)
        else:
            conf = metadata
        
        probeid = conf['probe_id']
        if not len(Probe() & f'probe_id = "{probeid}"'):
            Probe.insert1(dict(probe_id = conf['probe_id'],
                               probe_type = conf['probe_type'],
                               probe_n_shanks = conf['probe_n_shanks'],
                               probe_recording_channels = conf['probe_recording_channels']))
        configs = (ProbeConfiguration() & f'probe_id = "{probeid}"').fetch(as_dict = True)
        for c in configs:
            if ((c['channel_coords'] == conf['channel_coords']).all() and
                (c['channel_idx'] == conf['channel_idx']).all()):
                print("The coords are the same, probe is already there. ")
                
                return dict(probe_id = probeid,
                            configuration_id = c['configuration_id'],
                            sampling_rate = conf['sampling_rate'],
                            recording_software = conf['recording_software'],
                            recording_duration = conf['recording_duration'])
        # add to configuration
        confid = len(configs)+1
        ProbeConfiguration.insert1(dict(probe_id = probeid,
                                        configuration_id = confid,
                                        probe_n_channels = conf['probe_n_channels'],
                                        probe_gain = conf['probe_gain'],
                                        channel_idx = conf['channel_idx'],
                                        channel_shank = conf['channel_shank'],
                                        channel_coords = conf['channel_coords']))
        return dict(probe_id = probeid,
                    configuration_id = confid,
                    sampling_rate = conf['sampling_rate'],
                    recording_software = conf['recording_software'],
                    recording_duration = conf['recording_duration'])

@dataschema
class EphysRecording(dj.Imported):
    definition = '''
    -> Dataset
    ---
    n_probes               : smallint            # number of probes
    recording_duration     : float               # duration of the recording
    recording_software     : varchar(56)         # software_version 
    '''
    
    class ProbeSetting(dj.Part):
        definition = '''
        -> master
        probe_num               : smallint          # probe number
        ---
        -> ProbeConfiguration
        sampling_rate           : decimal(22,14)    # sampling rate 
        '''
    class ProbeFile(dj.Part):
        definition = '''
        -> EphysRecording.ProbeSetting
        -> File                                     # binary file that contains the data
        '''
        
    def add_spikeglx_recording(self,key):
        '''
        Adds a recording from Dataset ap.meta files.
        '''
        allpaths = pd.DataFrame((Dataset.DataFiles() & key).fetch()).file_path.values
        paths = natsorted(list(filter( lambda x: x.endswith('.ap.meta'),
                                       allpaths)))
        keys = []
        local_path = Path(prefs['local_paths'][0])
        for iprobe, p in enumerate(paths):
            # add each configuration
            tmp = ProbeConfiguration().add_from_spikeglx_metadata(local_path/p)
            tt = dict(key,n_probes = len(paths),probe_num = iprobe,**tmp)
            EphysRecording.insert1(tt,
                                   ignore_extra_fields = True,
                                   skip_duplicates = True,
                                   allow_direct_insert = True)
            EphysRecording.ProbeSetting.insert1(tt,
                                                ignore_extra_fields = True,
                                                skip_duplicates = True,
                                                allow_direct_insert = True)
            # only working for spikeglx files for the moment.
            pfiles = list(filter(lambda x: f'imec{iprobe}.ap.' in x,allpaths))
            EphysRecording.ProbeFile().insert([
                dict(tt,
                     **(File() & f'file_path = "{fi}"').proj().fetch(as_dict = True)[0])
                for fi in pfiles],
                                              skip_duplicates = True,
                                              ignore_extra_fields = True,
                                              allow_direct_insert = True)
            EphysRecordingNoiseStats().populate(tt) # try to populate the NoiseStats table (this will take a couple of minutes)
    
    def add_nidq_events(self,key = None):
        if key is None:
            key = [k for k in self] # create a list
        if type(key) is dict:
            key = [key]
        for k in key:
            dkey = (Dataset() & key).proj().fetch1()
            dkey = dict(dkey,
                        stream_name = 'nidq')
            
            if len(DatasetEvents() & dkey):
                print(f' DatasetEvents for nidq are already there for {dkey}')
                continue
            
            allpaths = pd.DataFrame((Dataset.DataFiles() & k).fetch()).file_path.values
            paths = list(filter( lambda x: '.nidq.' in x, allpaths))
            file_paths = (File() & [dict(file_path = p) for p in paths])
            try:
                file_paths = file_paths.get() # download or get the path
            except ValueError:
                raise(ValueError(f'Error getting files for dataset {k}.'))
            from ..rules.ephys import extract_events_from_nidq
            events,daq = extract_events_from_nidq(file_paths)
            
            if not len(events):
                print(f'No events for key: {k}')
                continue
            
            DatasetEvents().insert1(dkey, allow_direct_insert =  True)
            DatasetEvents.Digital().insert([dict(dkey,**ev) for ev in events], allow_direct_insert = True)
        return 
        
@dataschema
class EphysRecordingNoiseStats(dj.Computed):
    # Statistics to access recording noise on multisite 
    definition = '''
    -> EphysRecording.ProbeSetting
    ---
    channel_median = NULL             : longblob  # nchannels*2 array, the 1st column is the start, 2nd at the end of the file
    channel_max = NULL                : longblob 
    channel_min = NULL                : longblob
    channel_peak_to_peak = NULL       : longblob
    channel_mad = NULL                : longblob  # median absolute deviation
    '''
    duration = 30                     # duration of the stretch to sample (takes it from the start and the end of the file)

    def make(self,key):
        files = pd.DataFrame((EphysRecording.ProbeFile() & key).fetch())
        assert len(files), ValueError(f'No files for dataset {key}')
        # search for the recording files (this is set for compressed files now)
        recording_file = list(filter(lambda x : 'ap.cbin' in x,files.file_path.values))
        assert len(recording_file),ValueError(f'Could not find ap.cbin for {key}. Check Dataset.DataFiles?')
        recording_file = recording_file[0]
        filepath = find_local_filepath(recording_file, allowed_extensions = ['.ap.bin'])
        assert not filepath is None, ValueError(f'File [{recording_file}] not found in local paths.')
        # to get the gain, the channel_indices, and the sampling rate
        config = pd.DataFrame((ProbeConfiguration()*EphysRecording.ProbeSetting() & key).fetch()).iloc[0]
        # compute
        from ..rules.ephys import ephys_noise_statistics_from_file
        noisestats = ephys_noise_statistics_from_file(filepath,
                                                      duration = self.duration,
                                                      channel_indices = config.channel_idx,
                                                      sampling_rate = float(config.sampling_rate),
                                                      gain = config.probe_gain)        
        self.insert1(dict(key,**noisestats),ignore_extra_fields = True)

    
@dataschema
class SpikeSortingParams(dj.Manual):
    definition = '''
    parameter_set_num      : int            # number of the parameters set
    ---
    algorithm_name         : varchar(64)    # preprocessing  and spike sorting algorithm 
    parameters_dict        : varchar(2000)  # parameters json formatted dictionary
    code_link = NULL       : varchar(300)   # the software that preprocesses and sorts
    '''

@dataschema
class SpikeSorting(dj.Manual):
    definition = '''
    -> EphysRecording.ProbeSetting
    -> SpikeSortingParams
    ---
    n_pre_samples                   : smallint   # to compute the waveform time 
    n_sorted_units    = NULL        : int        # number of sorted units
    n_detected_spikes = NULL        : int        # number of detected spikes
    sorting_datetime  = NULL        : datetime   # date of the spike sorting analysis
    channel_indices   = NULL        : longblob   # channel_map
    channel_coords    = NULL        : longblob   # channel_positions
    -> [nullable] AnalysisFile.proj(features_file='file_path',features_storage='storage')
    -> [nullable] AnalysisFile.proj(waveforms_file='file_path',waveforms_storage='storage')
   '''
    # For each sorting, create a "features.hdf5" file that has the: (this file can be > 4Gb)
    #    - template features
    #    - cluster indices
    #    - whitening_matrix
    #    - templates 
    # For each sorting create a "waveforms.hdf5" file that has the: (this file can be > 10Gb)
    #   - filtered waveform samples for each unit (1000 per unit)
    #   - indices of the extracted waveforms
    
    class Segment(dj.Part):
        definition = '''
        -> master
        segment_num               : int  # number of the segment
        ---
        offset_samples            : int         # offset where the traces comes from
        segment                   : longblob    # 2 second segment of data in the AP band
        '''
        
    class Unit(dj.Part):
        definition = '''
        -> master
        unit_id                  : int       # cluster id
        ---
        spike_times              : longblob  # in samples (uint64)
        spike_positions  = NULL  : longblob  # spike position in the electrode (float32)
        spike_amplitudes = NULL  : longblob  # spike template amplitudes (float32)
        '''
        def get_sampling_rates(self):
            sampling_rates = (self*EphysRecording.ProbeSetting()).fetch('sampling_rate')
            return [float(s) for s in sampling_rates] # cast to float if decimal

        def get_units_with_waveforms(self, return_seconds = True, interp_method = 'cubic-spline'):
            units = []
            sampling_rates = self.get_sampling_rates()
            # get the interpolation functions for all experiments if return_seconds = True
            if return_seconds:
                exps = (EphysRecording.ProbeSetting() & self.proj()).proj().fetch(as_dict = True)
                interpolations = dict()
                for e in exps:
                    k = '{subject_name}_{session_name}_{dataset_name}_{probe_num}'.format(**e)
                    try:
                        interpolations[k] = (StreamSync() & e).apply(None, method = interp_method)
                    except:
                        interpolations[k] = None
            for p,u,r in zip(self.proj(),self,sampling_rates):
                w = (SpikeSorting.Waveforms() & p)
                if len(w):
                    w = w.fetch('waveform_median')[0]
                else:
                    w = None
                units.append(dict(u, waveform_median = w))
                if return_seconds:
                    k = '{subject_name}_{session_name}_{dataset_name}_{probe_num}'.format(**p)
                    if interpolations[k] is None:
                        units[-1]['spike_times'] = units[-1]['spike_times'].astype(np.float32)/np.float32(r)
                    else:
                        units[-1]['spike_times'] = interpolations[k](units[-1]['spike_times'].astype(np.float32))
            return units
        
        def get_spike_times(self, as_dict = True, return_seconds = True, extra_keys = [], warn = False, include_metrics = False,
                            interp_method = 'cubic-spline'):
            '''
spike_times = get_spike_times()

Gets spike times corrected if the sync is applied.

    as_dict = True
    return_seconds = True
    extra_keys = []
    warn = False
    include_metrics = False
            '''
            if return_seconds:
                exps = (EphysRecording.ProbeSetting() & self.proj()).proj().fetch(as_dict = True)
                interpolations = dict()
                for e in exps:
                    k = '{subject_name}_{session_name}_{dataset_name}_{probe_num}'.format(**e)
                    try:
                        probe_num = e['probe_num']
                        interpolations[k] = (StreamSync() & e & f'stream_name = "imec{probe_num}"').apply(None, warn = False,
                                                                                                          method = interp_method)
                    except AssertionError as err:
                        import warnings
                        warnings.warn(f"Using the sampling rate for spike times", RuntimeWarning)
                        interpolations[k] = lambda x: x/float((EphysRecording.ProbeSetting() & e).fetch1('sampling_rate'))
            keys = ['subject_name','session_name','dataset_name','probe_num','parameter_set_num','unit_id','spike_times'] + extra_keys
            
            if include_metrics:
                units = (self*UnitMetrics).fetch(*keys,as_dict=True)
            else:
                units = self.fetch(*keys,as_dict=True)
            if return_seconds:
                for u in units:
                    k = '{subject_name}_{session_name}_{dataset_name}_{probe_num}'.format(**u)
                    u['spike_times'] = interpolations[k](u['spike_times'])
            if as_dict:
                return units
            return [u['spike_times'] for u in units]

            
    class Waveforms(dj.Part):
        definition = '''
        -> SpikeSorting.Unit
        ---
        waveform_median   :  longblob         # average waveform (gain corrected in microvolt - float32)
        '''

    def delete(
            self,
            transaction = True,
            safemode  = None,
            force_parts = False):
        
        files = [f['waveforms_file'] for f in self]
        files += [f['features_file'] for f in self]
        super().delete(transaction = transaction,
                       safemode = safemode,
                       force_parts = force_parts)
        if len(self) == 0:
            if len(files):
                (AnalysisFile() & [f'file_path = "{t}"' for t in files]).delete(force_parts=force_parts,
                                                                                safemode = safemode) 

        
@analysisschema 
class UnitMetrics(dj.Computed):
   default_container = 'labdata-spks'
   # Compute the metrics from the each unit,
   # so we can recompute and add new ones if needed and not depend on the clustering
   definition = '''
   -> SpikeSorting.Unit
   ---
   num_spikes                        : int
   depth                   = NULL    : double
   position                = NULL    : blob
   shank                   = NULL    : int
   channel_index           = NULL    : int
   n_electrodes_spanned    = NULL    : int
   firing_rate             = NULL    : float
   isi_contamination       = NULL    : float
   isi_contamination_hill  = NULL    : float
   amplitude_cutoff        = NULL    : float
   presence_ratio          = NULL    : float
   depth_drift_range       = NULL    : float
   depth_drift_fluctuation = NULL    : float
   spike_amplitude         = NULL    : float
   spike_duration          = NULL    : float
   trough_time             = NULL    : float
   trough_amplitude        = NULL    : float
   fw3m                    = NULL    : float
   trough_gradient         = NULL    : float
   peak_gradient           = NULL    : float
   peak_time               = NULL    : float
   peak_amplitude          = NULL    : float
   polarity                = NULL    : tinyint
   active_electrodes       = NULL    : blob
   '''
   def make(self, key):
       dat = (SpikeSorting.Unit & key).get_units_with_waveforms()
       assert len(dat) == 1, ValueError('Need to select only one unit')
       dat = dat[0]
       
       from spks.metrics import (isi_contamination,
                                 isi_contamination_hill,
                                 amplitude_cutoff,
                                 presence_ratio,
                                 firing_rate,
                                 depth_stability)
       from spks.waveforms import waveforms_position, compute_waveform_metrics
       
       kk = {k:dat[k] for k in ['subject_name','session_name','dataset_name','probe_num']}
       channel_coords,srate,wpre = (EphysRecording.ProbeSetting()*SpikeSorting() & kk 
                                    & f'parameter_set_num = {key["parameter_set_num"]}').fetch1(
                                    'channel_coords','sampling_rate','n_pre_samples')
       channel_shanks,duration = (EphysRecording()*EphysRecording.ProbeSetting()*
                                 ProbeConfiguration() & kk).fetch1('channel_shank','recording_duration')
       
       metrics = dict(key)
       
       metrics['num_spikes'] = len(dat['spike_times'])
       if metrics['num_spikes'] > 5: # skip if less than 5 spikes
           metrics['firing_rate'] = firing_rate(dat['spike_times'],0, t_max = duration)
       if metrics['num_spikes'] > 50: # skip if less than 50 spikes
           metrics['isi_contamination'] = isi_contamination(dat['spike_times'], T = duration)
           metrics['isi_contamination_hill'] = isi_contamination_hill(dat['spike_times'],
                                                                      T = duration)
           metrics['amplitude_cutoff'] = amplitude_cutoff(dat['spike_amplitudes'])
           metrics['presence_ratio'] = presence_ratio(dat['spike_times'],
                                                      t_min = 0, t_max = duration)
           metrics['depth_drift_range'],metrics['depth_drift_fluctuation'] = depth_stability(
               dat['spike_times'],
               dat['spike_positions'][:,1],tmax = duration)
           if not dat['waveform_median'] is None:
               waves = dat['waveform_median']
               
               pos,channel,active_idx = waveforms_position(np.expand_dims(dat['waveform_median'],
                                                                          axis = 0),
                                                           channel_positions = channel_coords,
                                                           active_electrode_threshold = 3)
               if not np.all(np.isfinite(pos)): 
                   # this can happen when there is noise in the waveform estimate, choose the position of the peak channel then
                   pos = channel_coords[channel]
                   active_idx = [channel]
               metrics['n_electrodes_spanned'] = len(active_idx[0])
               if len(active_idx):
                   metrics['active_electrodes'] = np.array(active_idx).astype(int)
                   metrics['depth'] = pos[0][1] # TODO: estimate position from 6 channels around the peak channel
                   metrics['position'] = pos[0]
                   metrics['shank'] = channel_shanks[channel[0]]
                   metrics['channel_index'] = channel[0]
                   # the com only works if it is done only for the values that have spikes
                   wavemetrics = compute_waveform_metrics(waves[:,channel[0]],
                                                          wpre, float(srate))
                   metrics = dict(metrics,**wavemetrics)
                   metrics['spike_amplitude'] = np.abs(metrics['trough_amplitude']-metrics['peak_amplitude']) 
       self.insert1(metrics,skip_duplicates = True)

@analysisschema
class UnitCountCriteria(dj.Manual):
    definition = '''
    unit_criteria_id : int
   ---
    sua_criteria             : varchar(2000)       
    mua_criteria = NULL      : varchar(2000)      # if NULL, subtracts the SUA labels.
   '''
    
@analysisschema 
class UnitCount(dj.Computed):
    definition = '''
   -> SpikeSorting
   -> UnitCountCriteria
   ---
    all : int
    sua : int
    mua : int
   '''
    class Unit(dj.Part):
        definition = '''
        -> master
        -> UnitMetrics
        ---
        passes  : tinyint
        '''

    def make(self,key):
        allu = pd.DataFrame((UnitMetrics() & key).fetch())
        criteria = (UnitCountCriteria() &
                    f"unit_criteria_id = {key['unit_criteria_id']}").fetch('sua_criteria')[0]
        suaidx = _apply_unit_criteria(allu, criteria)
        sua = np.sum(suaidx)
        muacriteria = (UnitCountCriteria() &
                       f"unit_criteria_id = {key['unit_criteria_id']}").fetch('mua_criteria')[0]
        if muacriteria is None:
            mua = len(allu) - np.sum(suaidx)
        else:
            mua = np.sum(_apply_unit_criteria(allu, muacriteria))
        # Code for parsing the unit count criteria missing here.
        unitcounts = dict(key,
                          all = len(allu),
                          sua = sua,
                          mua = mua)        
        self.insert1(unitcounts)
        # select only a projection later, for now we ignore the extra fields
        allu['passes'] = suaidx.astype(int)
        keys = [dict(a,unit_criteria_id = key['unit_criteria_id']) for i,a in allu.iterrows()]
        self.Unit.insert(keys, ignore_extra_fields = True) # add to the Unit part table

def _apply_unit_criteria(unitmetrics,criteria):
    parameters = [p.strip(' ') for p in criteria.split('&')]
    operators = {'<': np.less, '>': np.greater, '<=':np.less_equal, '>=':np.greater_equal, '==': np.equal, '!=':np.not_equal}
    idx = []
    for p in parameters:
        for o in operators.keys():
            if o in p:
                n = [t.strip(' ') for t in p.split(o)]
                try:
                    n[1] = float(n[1])
                except:
                    pass
                idx.append(operators[o](unitmetrics[n[0]].values,n[1]))
    for i in idx:
        idx[0] = np.logical_and(idx[0],i)
    return idx[0]

from .histology import Atlas

@analysisschema
class ProbeBrainRegion(dj.Manual):
    definition = '''
    -> ProbeInsertion
    -> ProbeConfiguration
    -> Atlas.Region
    ---
    min_depth = NULL  : double
    max_depth = NULL  : double
    shanks = NULL     : blob
    electrodes = NULL : blob
    '''
