'''General schema classes for lab data management.

This module defines the core database schema for managing laboratory data using DataJoint.
It includes tables for tracking files, subjects, sessions, datasets and analysis results.

Configuration
------------
Uses the following settings from user_preferences.json:
- database.host : Database server hostname
- database.user : Database username 
- database.password : Database password
- database.name : Name of the database

Schemas
-------
- dataschema : DataJoint schema
      Primary schema for raw experimental data tables
- analysisschema : DataJoint schema
      Schema for computed/analyzed data tables

Classes
-------
- ``File`` : Table for tracking raw data files with paths, checksums and metadata
- ``AnalysisFile`` : Table for tracking analysis output files
- ``ProcessedFile`` : Table for tracking processed data files
- ``LabMember`` : Table of lab personnel
- ``Species`` : Table of experimental animal species
- ``Strain`` : Table of animal strains/lines
- ``Subject`` : Table of experimental subjects
- ``Session`` : Table of experimental sessions
- ``Dataset`` : Table of experimental datasets
- ``SetupLocation`` : Table of experimental setup locations
- ``Setup`` : Table of experimental setups and equipment
- ``Note`` : Table for general notes and comments
- ``DatasetType`` : Table of dataset type definitions
- ``DatasetEvents`` : Table of events within datasets
- ``StreamSync`` : Table for synchronization between data streams
- ``UploadJob`` : Table for tracking data uploads
- ``ComputeTask`` : Table for tracking analysis computations
'''

from ..utils import *
import datajoint as dj

if 'database' in prefs.keys():
    for k in prefs['database'].keys():
        if prefs['database'][k] is None:
            if k in ['database.user', 'database.password']:
                import getpass
                # get the password and write to file
                prefs['database'][k] = getpass.getpass(prompt=k)
                gotpass = True
        if not prefs['database'][k] is None:
            dj.config[k] = prefs['database'][k]
    if 'gotpass' in dir():
        # overwrite the preference file (save the datajoint password.)
        save_labdata_preferences(prefs, LABDATA_FILE) 

# overwride the user 
if 'LABDATA_DATABASE_USER' in os.environ.keys():
    dj.config['database.user'] = prefs['database']['database.user']
    if 'LABDATA_DATABASE_PASS' in os.environ.keys():
        dj.config['database.password'] = prefs['database']['database.password']
    else:
        raise(ValueError('Must specify both LABDATA_DATABASE_USER and LABDATA_DATABASE_PASS.'))

# overwride the database host
if 'LABDATA_DATABASE_HOST' in os.environ.keys():
    dj.config['database.host'] = os.environ['LABDATA_DATABASE']

# overwride the database name
dbase_name = dj.config['database.name']
if 'LABDATA_DATABASE' in os.environ.keys():
    dbase_name = os.environ['LABDATA_DATABASE']
    print(f'Overriding the database {dbase_name}')
dataschema = dj.schema(dbase_name)
analysisschema = dj.schema(dbase_name+'_computed')

DEFAULT_RAW_STORAGE = 'data'
DEFAULT_ANALYSIS_STORAGE = 'analysis'


@dataschema 
class File(dj.Manual):
    '''Table for tracking files stored in (s3 or local) storages.
    
    This table stores metadata about files including their path, storage location,
    creation date, size and MD5 checksum. It provides methods for:
    
    - Deleting files from both the database and S3 storage (does not delete local files)
    - Downloading files from S3 to local storage (does not download local storagefiles)
    - Checking if files are archived in S3 Glacier storage (does not check local storage)
    
    The table is used as a base class for AnalysisFile which handles analysis outputs.
    '''
    definition = '''
    file_path                 : varchar(300)  # Path to the file
    storage = "{0}"           : varchar(12)   # storage name 
    ---
    file_datetime             : datetime      # date created
    file_size                 : double        # using double because int64 does not exist
    file_md5 = NULL           : varchar(32)   # md5 checksum
    '''.format(DEFAULT_RAW_STORAGE)
    storage = DEFAULT_RAW_STORAGE
    # Files get deleted from AWS if the user has permissions
    def delete(
            self,
            transaction = True,
            safemode  = None,
            force_parts = False):
        '''Delete files from both the database and S3 storage.
        
        Parameters
        ----------
        transaction : bool, optional
            Whether to perform deletion as a transaction, by default True
        safemode : bool, optional
            Whether to run in safe mode, by default None
        force_parts : bool, optional
            Whether to force deletion of parts, by default False
            
        Raises
        ------
        ValueError
            If files are deleted from database but not from S3
        '''
        
        from ..s3 import s3_delete_file
        from tqdm import tqdm
        filesdict = [f for f in self]
        super().delete(transaction = transaction,
                       safemode = safemode,
                       force_parts = force_parts)
        if len(self) == 0:
            files_not_deleted = []
            files_kept = []
            for s in tqdm(filesdict,desc = f'Deleting objects from s3 {"storage"}:'):
                fname = s["file_path"]
                storage = prefs['storage'][s['storage']]
                if storage['protocol'] == 's3':
                    try:
                        s3_delete_file(fname,
                                   storage = prefs['storage'][s['storage']],
                                   remove_versions = True)
                    except Exception as err:
                        print(f'Could not delete {fname}.')
                        files_not_deleted.append(fname)
                else:
                    print(f'Skipping {fname} because it is not in S3.')
                    files_kept.append(fname)
            if len(files_not_deleted):
                print('\n'.join(files_not_deleted))
                raise(ValueError('''

[Integrity error] Files were deleted from the database but not from AWS.

            Save this message and show it to your database ADMIN.

{0}
                
'''.format('\n'.join(files_not_deleted))))
            if len(files_kept):
                print('Files where not deleted from the local storage.')

    def check_if_files_local(self, local_paths = None):
        '''
        Checks if files are in a local path, searches accross all local paths
        
        Parameters
        ----------
        local_paths : list of str or Path, optional
            List of local paths to check for files, by default None uses paths in preferences
        
        Returns
        -------
        tuple
            Tuple of local file paths and missing files
        
        Raises
        ------
        ValueError
            If no files in the object
        '''
        if local_paths is None:
            local_paths = prefs['local_paths']
        if not len(self):
            raise(ValueError('No files to get.'))
        # this does not work with multiple storages
        files = [f['file_path'] for f in self]
        localfiles = [find_local_filepath(a, local_paths = local_paths) for a in files]
        # check if they exist and download only missing files.
        missingfiles = []
        for f in files:
            if not np.any([str(l).endswith(f) for l in localfiles]):
                missingfiles.append(f)
        return localfiles, missingfiles
    
    def get(self,local_paths = None, check_if_archived = True, restore=True, download = True):
        '''Download files from S3 to local storage.
        
        Parameters
        ----------
        local_paths : list of str or Path, optional
            List of local paths to download files to, by default None uses paths in preferences
        check_if_archived : bool, optional
            Whether to check if files are in Glacier storage, by default True
        restore : bool, optional
            Whether to restore archived files, by default True
        download : bool, optional
            Whether to actually download the files, by default True
            
        Returns
        -------
        list
            List of local file paths that were downloaded
            
        Raises
        ------
        ValueError
            If no files are found to download
        '''
        if local_paths is None:
            local_paths = prefs['local_paths']
        if not len(self):
            raise(ValueError('No files to get.'))
        
        localfiles, remotefiles = self.check_if_files_local(local_paths = local_paths)
        storage = [f['storage'] for f in self][0]
        remotefiles = self & [dict(file_path = f) for f in remotefiles]
        if len(remotefiles):
            if prefs['storage'][storage]['protocol'] == 's3':
                if check_if_archived:
                    # TODO: add to the preference file to not restore by default.
                    self.check_if_files_archived(files = remotefiles, restore = restore)
                if download:
                    print(f'Downloading {len(remotefiles)} files from S3 [{storage}].')
                    remotefiles = [r['file_path'] for r in remotefiles]
                    dstfiles = [Path(local_paths[0])/f for f in remotefiles]  # place to store file.
                    from ..s3 import copy_from_s3
                    copy_from_s3(remotefiles,dstfiles,storage_name = storage)
                    localfiles, _ = self.check_if_files_local(local_paths = local_paths)
            elif prefs['storage'][storage]['protocol'] == 'local':
                # TODO, copy files from local storage to the first local path.
                print('Downloading from local storage is not implemented, use local_paths.')
        return localfiles
    
    def check_if_files_archived(self, files = None, restore = True, suppress_error = False):
        '''Check if files are archived in S3 Glacier storage.
        
        Parameters
        ----------
        restore : bool, optional
            Whether to initiate restore of archived files, by default True
        suppress_error : bool, optional
            Whether to suppress error if files are being restored, by default False
            
        Returns
        -------
        bool
            True if files are archived, False otherwise
            
        Raises
        ------
        OSError
            If storage is not in preferences or if files are being restored
        '''
        files_restoring = []
        import boto3
        if files is None:
            files = self
        for f in files:
            # check if files are archived
            # TODO: run this in parallel because it takes a while.
            if not f['storage'] in prefs['storage'].keys():
                raise(OSError(f"Store {f['storage']} is not in the preference file."))
            store = prefs['storage'][f['storage']]
    
            s3 = boto3.resource('s3',aws_access_key_id = store['access_key'],
                            aws_secret_access_key = store['secret_key'])

            obj = s3.Object(bucket_name = store['bucket'],
                            key = f['file_path'])
    
            if not obj.archive_status is None and 'ARCHIVE' in obj.archive_status:
                if obj.restore is None:
                    if restore:
                        resp = obj.restore_object(RestoreRequest = {})
                    files_restoring.append(f['file_path'])
                elif 'true' in obj.restore:
                    files_restoring.append(f['file_path'])
        if len(files_restoring):
            import warnings
            warnings.warn(f"Files are being restored [{files_restoring}]")
            if not suppress_error:
                raise(OSError(f"Files are being restored [{files_restoring}]"))
            return True # files are in arquive
        return False # files are not in archive



# This is in "analysisschema" so users can delete analysis files.
@analysisschema 
class AnalysisFile(File):
    definition = '''
    file_path                 : varchar(300)  # Path to the file
    storage = "{0}"           : varchar(12)   # storage name 
    ---
    file_datetime             : datetime      # date created
    file_size                 : double        # using double because int64 does not exist
    file_md5 = NULL           : varchar(32)   # md5 checksum
    '''.format(DEFAULT_ANALYSIS_STORAGE)
    storage = DEFAULT_ANALYSIS_STORAGE
    # All users with permission to run analysis should also have permission to add and remove files from the analysis bucket in AWS
    def upload_files(self,src,dataset, force = True):
        assert 'subject_name' in dataset.keys(), ValueError('dataset must have subject_name')
        assert 'session_name' in dataset.keys(), ValueError('dataset must have session_name')
        assert 'dataset_name' in dataset.keys(), ValueError('dataset must have dataset_name')
        
        destpath = '{subject_name}/{session_name}/{dataset_name}/'.format(**dataset)
        dst = [destpath+k.name for k in src]
        for d in dst:
            if len(AnalysisFile() & dict(file_path = d)) > 0:
                if not force:
                    ValueError(f'File is already in database, delete it to re-upload {d}.')
                else:
                    (AnalysisFile() & dict(file_path = d)).delete(safemode = False)
        assert self.storage in prefs['storage'].keys(),ValueError(
            'Specify an {self.storage} bucket in preferences["storage"].')
        from ..s3 import copy_to_s3

        copy_to_s3(src, dst, md5_checksum=None, storage_name = self.storage)
        dates = [datetime.utcfromtimestamp(Path(f).stat().st_mtime) for f in src]
        sizes = [Path(f).stat().st_size for f in src]
        md5 = compute_md5s(src)
        # insert in AnalysisFile if all went well
        self.insert([dict(file_path = f,
                          storage = self.storage,
                          file_datetime = d,
                          file_md5 = m,
                          file_size = s) for f,d,s,m in zip(dst,dates,sizes,md5)])
        return [dict(file_path = f,storage = self.storage) for f in dst]

        
# This table stores file name and checksums of files that were sent to upload but were processed by upload rules
# There are no actual files associated with these paths
@dataschema
class ProcessedFile(dj.Manual): 
    definition = '''
    file_path                 : varchar(300)  # Path to the file that was processe (these are not in S3)
    ---
    file_datetime             : datetime      # date created
    file_size                 : double        # using double because int64 does not exist
    file_md5 = NULL           : varchar(32)   # md5 checksum
    '''
        
@dataschema
class LabMember(dj.Manual):
    definition = """
    user_name                 : varchar(32)	# username
    ---
    email=null                : varchar(128)	# email address
    first_name = null         : varchar(32)	# first name
    last_name = null          : varchar(32)   	# last name
    date_joined               : date            # when the user joined the lab
    is_active = 1             : boolean	        # active or left the lab
    """

@dataschema
class Species(dj.Lookup):
    definition = """
    species_name              : varchar(32)       # species nickname
    ---
    species_scientific_name   : varchar(56)	  # scientific name 
    species_description=null  : varchar(256)       # description
    """
    
@dataschema
class Strain(dj.Lookup):
    definition = """
    strain_name                : varchar(56)	# strain name
    ---
    -> Species
    strain_description=null    : varchar(256)	# description
    """

@dataschema
class Subject(dj.Manual):
    ''' Experimental subject.'''
    definition = """
    subject_name               : varchar(20)          # unique mouse id
    ---
    subject_dob                : date                 # mouse date of birth
    subject_sex                : enum('M', 'F', 'U')  # sex of mouse - Male, Female, or Unknown
    -> Strain
    -> LabMember
    """

@dataschema
class SetupLocation(dj.Lookup):
    definition = """
    setup_location    : varchar(255)   # room 
    ---
"""
    contents = zip(['CHS-74100'])

@dataschema
class Setup(dj.Lookup):
    definition = """
    setup_name        : varchar(54)     # setup name          
    ---
    -> [nullable] SetupLocation 
    setup_description = NULL : varchar(512) 
"""

@dataschema
class Note(dj.Manual):
    definition = """
    -> LabMember.proj(notetaker='user_name')
    note_datetime       : datetime
    ---
    notes = ''          : varchar(4000)   # free-text notes
    """
    class Image(dj.Part):
        definition = """
        -> Note
        image_id       : int
        ---
        image          : longblob
        caption = NULL : varchar(256)
        """
    class Attachment(dj.Part):
        definition = """
        -> Note
        -> File
        ---
        caption = NULL : varchar(256)
        """

@dataschema
class Session(dj.Manual):
    definition = """
    -> Subject
    session_name             : varchar(54)     # session identifier
    ---
    session_datetime         : datetime        # experiment date
    -> [nullable] LabMember.proj(experimenter = 'user_name') 
    """
    
@dataschema
class DatasetType(dj.Lookup):
    definition = """
    dataset_type: varchar(32)
    """
    contents = zip(dataset_type_names)

@dataschema
class Dataset(dj.Manual):
    definition = """
    -> Subject
    -> Session
    dataset_name             : varchar(128)    
    ---
    -> [nullable] DatasetType
    -> [nullable] Setup
    -> [nullable] Note
    """
    class DataFiles(dj.Part):  # the files that were acquired on that dataset.
        definition = '''
        -> master
        -> File
        '''

# Synchronization variables for the dataset live here; these can come from different streams
@dataschema
class DatasetEvents(dj.Imported):
    definition = '''
    -> Dataset
    stream_name                       : varchar(54)   # which clock is used e.g. btss, nidq, bpod, imecX
    ---
    stream_time = NULL                 : longblob     # for e.g. the analog channels
    '''
    class Digital(dj.Part):
        definition = '''
        -> master
        event_name                    : varchar(54)
        ---
        event_timestamps = NULL       : longblob  # timestamps of the events
        event_values = NULL           : longblob  # event value or count
        '''
        projkeys = ['subject_name','session_name','dataset_name','stream_name','event_name']
        
        def fetch_synced(self, force = False,method = 'cubic-spline'):
            ''' 
            Returned events already synchronized between data streams, following the StreamSync table.
            '''
            keys = [dict(subject_name = s["subject_name"],
                         session_name = s["session_name"],
                         dataset_name = s["dataset_name"],
                         stream_name = s["stream_name"]) for s in self]
            evnts = []
            streams = (StreamSync() & keys)
            if not len(streams):
                from warnings import warn
                warn(f'There are no StreamSync for events {self.proj()}. This will return only the clock stream.')
            else:    
                for s in streams:
                    evs = (self & dict(stream_name = s["stream_name"])).fetch(as_dict = True)
                    func = (StreamSync() & s).apply(None, force = force,method = 'cubic-spline')
                    for evnt in evs:
                        if not evnt['event_timestamps'] is None:
                            evnt['event_timestamps'] = func(evnt['event_timestamps'])
                            evnts.append(evnt)
            # add the events from the clock stream
            if len(streams):
                evs = (self & dict(stream_name = streams.clock_stream())).fetch(as_dict = True)
            else:
                evs = self
            for evnt in evs:
                evnts.append(evnt)
            return evnts
        
        def plot_synced(self, stream_colors = 'krbgyb', overlay_original = False, lw = 1,force = True):
            ''' Plot DatasetEvents.Digital.'''
            evnts = self.fetch_synced(force = force)
            ustreams = [n for n in np.unique([e['stream_name'] for e in evnts])]
            
            import pylab as plt
            caption = []
            ticks = []
            lns = []
            for i,e in enumerate(evnts):
                ln = plt.vlines(e['event_timestamps'],i,i+0.7,
                                color = stream_colors[np.mod(ustreams.index(e['stream_name']),len(stream_colors))],
                                lw = lw)
                if overlay_original:
                    ee = (DatasetEvents.Digital() & {k:e[k] for k in self.projkeys}).fetch('event_timestamps')[0]
                    plt.vlines(ee,i+0.6,i+0.9,color='gray',lw = lw)
                lns.append(ln)
                ticks.append(i+0.35)
                caption.append(f'{e["stream_name"]}_{e["event_name"]}')
            plt.yticks(ticks,caption);
            return lns
        
    class AnalogChannel(dj.Part):
        definition = '''
        -> master
        channel_name                 : varchar(54)
        ---
        channel_values = NULL        : longblob  # analog values for channel
        '''
        
@analysisschema
class StreamSync(dj.Manual):
    definition = '''
    -> Dataset
    -> DatasetEvents.Digital
    -> DatasetEvents.Digital.proj(clock_stream='stream_name',clock_stream_event='event_name',clock_dataset = 'dataset_name')
    '''
    def get_interp_data(self,force = False, warn = True, allowed_offset = 2):
        ''' Force will attempt to remove events from the longest stream so the streams are matched. '''
        
        assert len(self)==1, ValueError(f"This function only takes one element at a time not {len(self)}.")
        s = self.fetch1()
        clock = (DatasetEvents.Digital() & dict(subject_name = s['subject_name'],
                                                session_name = s['session_name'],
                                                dataset_name = s['clock_dataset'],
                                                stream_name = s['clock_stream'],
                                                event_name = s['clock_stream_event'])).fetch1()
        clock_onsets = clock['event_timestamps']#[clock['event_values'] == 1]
        sync = (DatasetEvents.Digital() & dict(subject_name = s['subject_name'],
                                               session_name = s['session_name'],
                                               dataset_name = s['dataset_name'],
                                               stream_name = s['stream_name'],
                                               event_name = s['event_name'])).fetch1()
        sync_onsets = sync['event_timestamps']
        if ((len(sync_onsets)>=(len(clock_onsets)//2)-allowed_offset) and 
            (len(sync_onsets)<=(len(clock_onsets)//2)+allowed_offset)): # in case clock has both onsets and offsets
            if clock['event_values'] is None:
                clock_onsets = clock_onsets[::2]
            else:
                clock_onsets = clock_onsets[clock['event_values'] == 1]
        if ((len(clock_onsets)>=(len(sync_onsets)//2)-allowed_offset) and 
            (len(clock_onsets)<=(len(sync_onsets)//2)+allowed_offset)): # in case sync has both onsets and offsets
            if sync['event_values'] is None:
                sync_onsets = sync_onsets[::2]
            else:
                sync_onsets = sync_onsets[sync['event_values']==1]
        if warn: 
            if not len(sync_onsets) == len(clock_onsets):
                import warnings
                warnings.warn(f"There is a potential issue with the syncronization of sessions: {s['subject_name']} {s['session_name']}", UserWarning)
                print(f"    - stream {s['clock_stream']} channel {s['clock_stream_event']} {len(clock_onsets)}")
                print(f"    - stream {s['stream_name']} channel {s['event_name']} {len(sync_onsets)}")
        if not force: # by default this is set to false.
            assert len(clock_onsets) == len(sync_onsets), ValueError(f'\n\n Length of the clock and sync not the same? \n\n {self}')
        N = np.min([len(sync_onsets),len(clock_onsets)])
        return sync_onsets[:N],clock_onsets[:N]

    def apply(self, values, sync_onsets = None, warn = True, clock_onsets = None, force = False, method = 'cubic-spline'):
        '''
        Returns synchronized signals according a sync pulse shared from a clock.
        "clock" is main, "sync" is the same acquisition system as "values"
        '''
        if sync_onsets is None or clock_onsets is None:
            sync_onsets, clock_onsets = self.get_interp_data(force = force, warn = warn)
        if method == 'cubic-spline':
            # cubic spline interpolation handles the extrapolated points better
            from scipy.interpolate import CubicSpline
            func = CubicSpline(sync_onsets,clock_onsets)
        elif method == 'piecewise-linear':
            # linear interpolation to get the time of events syncronized across streams
            func = lambda x: np.interp(x,sync_onsets,clock_onsets)
        else:
            raise(ValueError(f'Unknown interpolation method {method}'))
        if values is None: # return a function if no values passed
            return func
        return func(values)
    
    def clock_stream(self):
        '''
        Returns the name of the clock stream(s)
        '''
        clkstreams = np.unique(self.fetch('clock_stream'))
        if len(clkstreams) == 1:
            return clkstreams[0]
        return clkstreams
    
####################################################
#######################QUEUES#######################
####################################################
# Upload queue, so that experimental computers are not transfering data 
# @dataschema
@analysisschema
class UploadJob(dj.Manual):
    definition = '''
    job_id                  : int auto_increment
    ---
    job_waiting = 1         : tinyint             # 1 if the job is up for grabs
    job_status = NULL       : varchar(52)         # status of the job (did it fail?)
    job_host = NULL         : varchar(52)         # where the job is running
    job_rule = NULL         : varchar(52)         # what rule is it following
    job_log = NULL          : varchar(500)        # LOG
    -> [nullable] Dataset                         # optionally insert to dataset
    upload_storage = NULL  : varchar(12)          # storage name, where to upload

    '''
    
    class AssignedFiles(dj.Part):
        definition = '''
        -> master
        src_path               : varchar(300)      # local file path 
        ---
        src_datetime           : datetime          # date created
        src_size               : double            # using double because int64 does not exist
        src_md5 = NULL         : varchar(32)       # md5 checksum
        '''

# Jobs to perform computations, like spike sorting or segmentation
# @dataschema
@analysisschema
class ComputeTask(dj.Manual):
    definition = '''
    job_id                      : int auto_increment
    ---
    task_waiting = 1            : tinyint             # 1 if the job is up for grabs
    task_name = NULL            : varchar(52)         # what task to run
    task_status = NULL          : varchar(52)         # status of the job (did it fail?)
    task_target = NULL          : varchar(52)         # where to run the job, so it only runs where selected
    task_host = NULL            : varchar(52)         # where the job is running
    task_cmd = NULL             : varchar(500)        # command to run 
    task_parameters = NULL      : varchar(2000)       # command to run after the job finishes
    task_log = NULL             : varchar(2000)       # LOG
    task_starttime = NULL       : datetime            # time of task start
    task_endtime = NULL         : datetime            # time of task completion
    
    -> [nullable] Dataset                             # dataset
    '''
    
    class AssignedFiles(dj.Part):
        definition = '''
        -> master
        -> File
        '''
    
