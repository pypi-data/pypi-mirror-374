import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

import json
import re  # can be removed?
from pathlib import Path
from io import StringIO
from glob import glob
from natsort import natsorted
import hashlib
from datetime import datetime
import pathlib
from joblib import delayed, Parallel
import pickle


LABDATA_PATH = Path.home()/Path('labdata')
if 'LABDATA_PATH' in os.environ.keys():
    LABDATA_PATH = Path(os.environ['LABDATA_PATH'])
LABDATA_FILE = LABDATA_PATH/'user_preferences.json'

DEFAULT_N_JOBS = 8
if 'SLURM_CPUS_ON_NODE' in os.environ.keys():
    DEFAULT_N_JOBS = int(os.environ['SLURM_CPUS_ON_NODE'])
if 'LABDATA_N_JOBS' in os.environ.keys():
    DEFAULT_N_JOBS = int(os.environ['LABDATA_N_JOBS'])

# dataset_type part of Dataset()
dataset_type_names = ['task-training',
                      'task-behavior',
                      'passive-spontaneous',
                      'passive-stimulation',
                      'free-behavior',
                      'imaging-2p',
                      'imaging-widefield',
                      'imaging-miniscope',
                      'ephys',
                      'opto-inactivation',
                      'opto-activation',
                      'analysis']
# The following dictionary describes the equivalency between datatype_name and dataset_type (broadly)
# todo: flip this the other way and split the types with slash or so.
dataset_name_equivalence = dict(ephys ='ephys',
                                task = 'task-training',
                                two_photon = 'imaging-2p',
                                one_photon = 'imaging-widefield',
                                analysis = 'analysis')

default_analysis = dict(populate = 'labdata.compute.PopulateCompute',
                        spks = 'labdata.compute.SpksCompute',
                        deeplabcut = 'labdata.compute.DeeplabcutCompute',
                        caiman = 'labdata.compute.CaimanCompute',
                        suite2p = 'labdata.compute.Suite2pCompute')

default_remote_description = dict(scheduler = 'slurm',
                                  user = 'ec2-user',
                                  permission_key = 'gpu-cluster.pem',
                                  address = 'ec2-xx-xx-xx-xx.us-west-2.compute.amazonaws.com',
                                  analysis_queue = dict(spks = dict(queue='gpu-large',
                                                                    ncpus = 16)), # where to run each analysis
                                  )

default_labdata_preferences = dict(local_paths = [str(Path.home()/'data')],
                                   scratch_path = str(Path.home()/'scratch'),
                                   path_rules='{subject_name}/{session_name}/{dataset_name}', # to read the session/dataset from a path
                                   path_rules_session_date = ['session_name', '%Y%m%d_%H%M%S'], # how to parse the session date from the path
                                   queues= None,
                                   allow_s3_download = False,
                                   compute = dict(
                                       remotes = dict(), # these are to connect
                                       containers = dict(
                                           local = str(Path.home()/Path('labdata')/'containers'),
                                           storage = 'analysis'), # place to store on s3
                                       analysis = default_analysis,
                                       default_target = 'slurm'),
                                   storage = dict(data = dict(protocol = 's3',
                                                              endpoint = 's3.amazonaws.com:9000',
                                                              bucket = 'xxxx-data',
                                                              folder = '',
                                                              access_key = None,
                                                              secret_key = None),
                                                  analysis = dict(protocol = 's3',
                                                                  endpoint = 's3.amazonaws.com:9000',
                                                                  bucket = 'xxxx-analysis',
                                                                  folder = '',
                                                                  access_key = None,
                                                                  secret_key = None)),
                                   database = {
                                       'database.host':'database-path.us-west-2.rds.amazonaws.com',
                                       'database.user': None,
                                       'database.password': None,
                                       'database.name': 'lab_data'},
                                   plugins_folder = str(Path.home()/
                                                        Path('labdata')/'plugins'), # this can be removed?
                                   submit_defaults = None,
                                   run_defaults = {'delete-cache':False},
                                   upload_path = None,           # this is the path to the local computer that writes to s3
                                   upload_storage = None)        # which storage to upload to

tcolor = dict(r = lambda s: f'\033[91m{s}\033[0m',
              g = lambda s: f'\033[92m{s}\033[0m',
              y = lambda s: f'\033[93m{s}\033[0m',
              b = lambda s: f'\033[94m{s}\033[0m',
              m = lambda s: f'\033[95m{s}\033[0m',
              c = lambda s: f'\033[96m{s}\033[0m',
              )

def get_labdata_preferences(prefpath = None):
    '''Reads and returns the labdata preferences from a JSON file.

    Parameters
    ----------
    prefpath : str or Path, optional
        Path to the preferences JSON file. If None, uses default location in user's home directory ($HOME/labdata/user_preferences.json).

    Returns
    -------
    dict
        Dictionary containing the labdata preferences.

    Notes
    -----
    The preferences file contains settings for:
    - Data storage locations (local and remote)
    - Compute configurations (AWS, containers, etc)
    - Database connection details
    - Default analysis parameters
    - Upload paths and storage

    If the preferences file doesn't exist, creates one with default settings.
    Environment variable LABDATA_OVERRIDE_DATAPATH can be used to override paths.
    '''
    
    if prefpath is None:
        prefpath = LABDATA_FILE
    prefpath = Path(prefpath) # needs to be a file
    preffolder = prefpath.parent
    if not preffolder.exists():
        preffolder.mkdir(parents=True,exist_ok = True)
    if not prefpath.exists():
        save_labdata_preferences(default_labdata_preferences, prefpath)
    with open(prefpath, 'r') as infile:
        pref = json.load(infile)
    for k in default_labdata_preferences:
        if not k in pref.keys():
            pref[k] = default_labdata_preferences[k]
    from socket import gethostname
    pref['hostname'] = gethostname()
    if 'LABDATA_OVERRIDE_DATAPATH' in os.environ.keys():
        # then override the paths set in the preference file.
        overpath = os.environ['LABDATA_OVERRIDE_DATAPATH']
        print(f'Overriding local_paths and scratch_path. [{overpath}]')
        pref['scratch_path'] = Path(overpath)
        pref['local_paths'] = [Path(overpath)]
    if 'compute' in pref.keys():
        if 'analysis' in pref['compute'].keys():
            for k in default_analysis.keys(): # add analysis that ship out of the box with labdata
                if not k in pref['compute']['analysis'].keys():
                    pref['compute']['analysis'][k] = default_analysis[k]
        else:
            pref['compute']['analysis'] = dict(default_analysis)
    return pref

def save_labdata_preferences(preferences, prefpath):
    '''Saves labdata preferences to a JSON file.

    Parameters
    ----------
    preferences : dict
        Dictionary containing labdata preferences to save
    prefpath : str or Path
        Path to save the preferences JSON file to

    Notes
    -----
    Saves preferences as formatted JSON with sorted keys and 4-space indentation.
    Prints confirmation message with save location.
    '''
    with open(prefpath, 'w') as outfile:
        json.dump(preferences, 
                  outfile, 
                  sort_keys = True, 
                  indent = 4)    
        print(f'Saving default preferences to: {prefpath}')

prefs = get_labdata_preferences()

def validate_num_jobs_joblib(num_jobs):
    '''Helper function to handle number of parallel jobs in joblib.
    
    When running inside a joblib child process, forces num_jobs=1 to prevent nested parallelism.
    Otherwise returns the input num_jobs value unchanged.

    Parameters
    ----------
    num_jobs : int
        Number of parallel jobs requested

    Returns
    -------
    int
        1 if running in joblib child process, otherwise returns num_jobs unchanged
    '''
    if "JOBLIB_CHILD_PID" in os.environ:
        return 1
    else:
        return num_jobs
##########################################################
##########################################################
def parse_filepath_parts(path,
                         local_path = None,
                         path_rules = None,
                         session_date_rules = None):
    '''Parse filepath into component parts based on path rules.
    
    Parameters
    ----------
    path : str or Path
        Filepath to parse
    local_path : str or Path, optional
        Base path to remove from filepath. If None, uses first path from preferences.
    path_rules : str, optional
        Forward slash separated string defining path components, e.g. "{subject}/{session}/{dataset}".
        If None, uses rules from preferences.
    session_date_rules : list of str, optional
        List of datetime format strings for parsing session names into datetimes.
        Default is ['session_name','%Y%m%d_%H%M%S'].
        The first is a key of path_rules, the second is the parsing command

    Returns
    -------
    dict
        Dictionary containing parsed path components. Keys are the component names from path_rules.
        May include additional keys:
        - session_datetime: datetime object if session_name was parsed successfully
        - dataset_type: standardized dataset type if dataset_name matches known types

    Notes
    -----
    Removes local_path prefix from input path, then splits remaining path on directory separators.
    Components are matched to path_rules in order.
    Special handling for session_name to parse into datetime and dataset_name to standardize type.
    '''
    
    if path_rules is None:
        path_rules = prefs['path_rules']
    if session_date_rules is None:
        session_date_rules = prefs['path_rules_session_date']
    if local_path is None:
        local_path = prefs['local_paths'][0]
    parts = [p for p in str(path).replace(local_path,'').split(pathlib.os.sep) if len(p)]
    names = [f.strip('}').strip('{') for f in  path_rules.split('/')]
    
    t = dict()
    for i,n in enumerate(names):
        print(n,parts[i])
        if not n in t.keys():
            t[n] = parts[i]
        else:
            t[n] += '/' + parts[i] # for when the session name is split across multiple folders..
    print(t)
    if 'session_name' in t.keys() and len(session_date_rules):
        try:
            t['session_datetime'] = datetime.strptime(t[session_date_rules[0]],session_date_rules[1])
        except ValueError as exc:
            ii = str(exc)
            if 'unconverted data remains: ' in ii: # then the session name has trailing characters
                ii = ii.replace('unconverted data remains: ','')
            t['session_datetime'] = datetime.strptime(
                t[session_date_rules[0]].replace(ii,''),
                session_date_rules[1])    
    if 'dataset_name' in t.keys():
        for k in dataset_name_equivalence.keys():
            if k in t['dataset_name'].lower():
                t['dataset_type'] = dataset_name_equivalence[k]
                break # found it..
    return t

def drop_local_path(filepaths,local_path = None):
    if local_path is None:
        local_path = prefs['local_paths'][0]
    if type(filepaths) is Path:
        filepaths = [filepaths]
    clean_filepaths = [str(Path(f)).replace(str(local_path),'') for f in filepaths]
    # remove trailing / or \
    clean_filepaths = [f if not f.startswith(pathlib.os.sep) else f[1:] for f in clean_filepaths]
    # make unique
    clean_filepaths = [f for f in np.unique(clean_filepaths)]
    return clean_filepaths
##########################################################
##########################################################

def compute_md5_hash(fname,suppress_file_not_found = False):
    '''
    Computes the md5 hash that can be used to check file integrity
    '''
    hash_md5 = hashlib.md5()
    if not Path(fname).exists():
        if suppress_file_not_found:
            print(f'File {fname} not found while computing md5 hash.')
            return -1
        else:
            raise(OSError(f'File {fname} not found while computing md5 hash.'))
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def compute_md5s(filepaths,n_jobs = DEFAULT_N_JOBS, show_progress = False,suppress_file_not_found = False):
    '''
    Computes the checksums for multiple files in parallel 
    '''
    if show_progress:
        from tqdm import tqdm
        return Parallel(n_jobs = n_jobs)(delayed(compute_md5_hash)(filepath, suppress_file_not_found = suppress_file_not_found) 
                                         for filepath in tqdm(filepaths,desc = 'Computing md5 checksums:',
                                                              total = len(filepaths)))
    return Parallel(n_jobs = n_jobs)(delayed(compute_md5_hash)(filepath) for filepath in filepaths)


def compare_md5s(paths,checksums, n_jobs = DEFAULT_N_JOBS, full_output = False, show_progress = False, suppress_file_not_found = False):
    '''
    Computes the checksums for multiple files in parallel 
    '''
    localchecksums = compute_md5s(paths, 
                                  n_jobs = n_jobs,
                                  show_progress = show_progress,
                                  suppress_file_not_found = suppress_file_not_found)
    res = [False]*len(paths)
    assert len(paths) == len(checksums), ValueError('Checksums not the same size as paths.')
    for ipath,(local,check) in enumerate(zip(localchecksums,checksums)):
        res[ipath] = local == check
    if full_output:
        return all(res),res
    return all(res)


def get_filepaths(keys,local_paths = None, download = False):
    '''
    Returns the local path to files and downloads the files if needed. 
    '''
    path = keys.file_path
    pass
    
def find_local_filepath(path,allowed_extensions = [],local_paths = None):
    '''
    Search for a file in local paths and return the path.
    This function exists so that files can be distributed in different file systems.
    List the local paths (i.e. the different filesystems) in labdata/user_preferences.json

    allowed_extensions can be used to find similar extensions 
(e.g. when files are compressed and you want to find the original file)

    localpath = find_local_filepath(path, allowed_extensions = ['.ap.bin'])

    Joao Couto - labdata 2024
    '''
    if local_paths is None:
        local_paths = prefs['local_paths']
        
    for p in local_paths:
        p = Path(p)/path
        if p.exists():
            return p # return when you find the file
        for ex in allowed_extensions:
            p = (p.parent/p.stem).with_suffix(ex)
            if p.exists():
                return p # found allowed extensions (use this to find ProcessedFiles)   
    return None  # file not found

def plugin_lazy_import(name):
    '''
    Lazy import function to load the plugins.
    '''
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, str(Path(prefs['plugins'][name])/"__init__.py"))
    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


def extrapolate_time_from_clock(master_clock,master_events, slave_events):
    '''
    Extrapolates the time for synchronizing events on different streams
    '''
    from scipy.interpolate import interp1d
    return interp1d(master_events, master_clock, fill_value='extrapolate')(slave_events)


def save_dict_to_h5(filename,dictionary,compression = 'gzip', compression_opts = 1, compression_size_threshold = 1000):
    '''
    Save a dictionary as a compressed hdf5 dataset.
    filename: path to the file (IMPORTANT: this WILL overwrite without checks.)
    dictionary: the dictionary to save

    If the size of the data are larger than compression_size_threshold it will save with compression.
    default compression is gzip, can also use lzf

    Joao Couto - 2023
    '''
    def _save_dataset(f,key,val,
                      compression = compression,
                      compression_size_threshold = compression_size_threshold):
        # compress if big enough.
                
        if np.size(val)>compression_size_threshold:
            extras = dict(compression = compression,
                          chunks = True, 
                          shuffle = True)
            if compression == 'gzip':
                extras['compression_opts'] = compression_opts
        else:
            extras = dict()
        f.create_dataset(str(key),data = val, **extras)

    import h5py
    keys = []
    values = []
    for k in dictionary.keys():
        if not type(dictionary[k]) in [dict]:
            keys.append(k)
            values.append(dictionary[k])
        else:
            for o in dictionary[k].keys():
                keys.append(k+'/'+str(o))
                values.append(dictionary[k][o])
    filename = Path(filename)
    # create file, this will overwrite without asking.
    from tqdm import tqdm
    with h5py.File(filename,'w') as f:
        for k,v in tqdm(zip(keys,values),total = len(keys),desc = f"Saving to hdf5 {filename.name}"):
            _save_dataset(f = f,key = k,val = v) 

def format_localpath_to_db(filepaths,local_path = None):
    '''
    Remove the local_path from a list of filepaths, the path will be the same as
    '''
    if local_path is None:
        local_path = prefs['local_paths'][0]
    if type(filepaths) is Path:
        filepaths = [filepaths]
    clean_filepaths = [str(Path(f)).replace(str(local_path),'') for f in filepaths]
    # remove trailing / or \
    clean_filepaths = [f if not f.startswith(pathlib.os.sep) else f[1:] for f in clean_filepaths]
    # make unique
    clean_filepaths = [f for f in np.unique(clean_filepaths)]
    # convert \ to / TODO: needs to be tested in windows..
    return clean_filepaths

def load_dict_from_h5(filename):
    ''' 
    Loads a dictionary from hdf5 file.
    
    This is also in github/spkware/spks

    Joao Couto - spks 2023

    '''
    data = {}
    import h5py
    with h5py.File(filename,'r') as f:
        for k in f.keys(): #TODO: read also attributes.
            no = k
            if no[0].isdigit():
                no = int(k)
            if hasattr(f[k],'dims'):
                data[no] = f[k][()]
            else:
                data[no] = dict()
                for o in f[k].keys(): # is group
                    ko = o
                    if o[0].isdigit():
                        ko = int(o)
                    data[no][ko] = f[k][o][()]
    return data

def save_zarr_compressed_stack(stack, filename, 
                          chunksize = [128],
                          compression = None,
                          clevel = 6,
                          shuffle = 1,
                          filters = [],
                          scratch_path = None,
                          check_dataset = False):
    '''Save a numpy array to a compressed zarr file.

    Parameters
    ----------
    stack : numpy.ndarray
        Array to compress and save (up to 4 dimensions)
    filename : str or Path
        Path to save the compressed zarr file
    chunksize : list, optional
        Size of chunks for compression, default [128]
    compression : str, optional
        Compression algorithm to use ('zstd' or 'blosc2'), default None uses 'zstd'
    clevel : int, optional
        Compression level (1-9), default 6
    shuffle : int, optional
        Shuffle filter to use (0=none, 1=byte, 2=bit), default 1
    filters : list, optional
        Additional filters to apply (e.g. ['delta']), default empty list
    scratch_path : str or Path, optional
        Temporary directory for compression, default uses preferences or current dir
    check_dataset : bool, optional
        Whether to verify compressed data matches original, default False

    Returns
    -------
    zarr.core.Array
        The compressed zarr array opened in read mode

    Notes
    -----
    Creates a temporary zarr store, compresses the data in chunks, saves to a zip file,
    then cleans up the temporary files. Optionally verifies the compressed data.
    '''
    
    # stack is up to four dimensional 
    import zarr
    import string
    from zipfile import ZipFile
    from pathlib import Path
    import numcodecs
    from tqdm import tqdm
    filt = []
    if 'delta' in filters:
        filt += [zarr.Delta(dtype=stack.dtype)]
    if compression is None or compression == 'zstd':
        compressor = zarr.Blosc(cname = 'zstd', clevel = clevel, shuffle = shuffle)
    elif compression == 'blosc2':
        from imagecodecs.numcodecs import Blosc2
        numcodecs.register_codec(Blosc2)
        compressor = Blosc2(level=clevel,shuffle = shuffle)
        
    if scratch_path is None:
        if 'scratch_path' in prefs:
            scratch_path = Path(prefs['scratch_path'])
        if scratch_path is None:
            scratch_path = Path('.')
    
    rand = ''.join(np.random.choice([s for s in string.ascii_lowercase + string.digits],9))
    tmppath = Path(scratch_path/f'temporary_zarr_{rand}.zarr')
    # create the output dir
    filename = Path(filename)
    filename.parent.mkdir(exist_ok = True,parents = True)
        
    z1 = zarr.open(tmppath, mode='w', shape = stack.shape,
                   chunks = chunksize*len(stack.shape), dtype = stack.dtype, 
                   compressor = compressor, filters = filt)
    for s in tqdm(chunk_indices(len(stack),chunksize[0]),desc = 'Compressing '):
        z1[s[0]:s[1]] = np.array(stack[s[0]:s[1]])
    
    with ZipFile(filename,'w') as z:
        tmp = list(tmppath.rglob('*'))
        [z.write(t,arcname=t.name) for t in tqdm(tmp, desc='Saving to zip')]
    # delete the temporary
    from shutil import rmtree
    rmtree(tmppath)
    # open the new array
    z1 = open_zarr(filename,mode = 'r')
    if check_dataset:
        # check the new array
        for s in tqdm(chunk_indices(len(stack),chunksize[0]),desc = 'Checking data:'):
            if not np.all(z1[s[0]:s[1]] == np.array(stack[s[0]:s[1]])):
                raise(ValueError(f"Datasets are not equivalent, compression failed {filename}. "))
    return z1

def chunk_indices(nframes, chunksize = 512, min_chunk_size = 16):
    '''
    Gets chunk indices for iterating over an array in evenly sized chunks

    Joao Couto - wfield, 2020
    '''
    chunks = np.arange(0,nframes,chunksize,dtype = int)
    if (nframes - chunks[-1]) < min_chunk_size:
        chunks[-1] = nframes
    if not chunks[-1] == nframes:
        chunks = np.hstack([chunks,nframes])
    return [[chunks[i],chunks[i+1]] for i in range(len(chunks)-1)]

def open_zarr(path, mode = 'r'):
    '''
    Open a zarr.
    
    z1  = open_zarr(path, mode = 'r')

    TODO: Make this work for remote arrays also.
    
    '''
    import zarr
    import numcodecs
    try: # load the imagecodec because it may be there 
        from imagecodecs.numcodecs import Blosc2
        numcodecs.register_codec(Blosc2)
    except:
        pass # move on because it may not be needed depending on the codec
    
    # open the new array (now supporting the new/old api - needs testing on the old API)
    if str(path).endswith('.zip'):
        store = zarr.storage.ZipStore(path, mode = mode)
    else:
        store = Path(path)
    z1 = zarr.open(store, mode = mode)
    return z1
