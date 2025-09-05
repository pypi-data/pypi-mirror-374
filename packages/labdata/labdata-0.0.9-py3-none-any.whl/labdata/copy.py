from .utils import *
from warnings import warn

def _copyfile_to_upload_server(filepath, local_path=None, server_path = None,overwrite = False):
    '''

    This is an internal function, not meant to be called by the end user, call copy_to_upload_server instead.

    This is a support function that will copy data between computers; it will not overwrite, unless forced.
    
    It will raise an exception if the files are already there unless overwrite is true.
    
    Does not insert to the Upload table.


    Parameters
    ----------
    filepath : str or Path
        Path to the file to copy, relative to local_path
    local_path : str or Path, optional
        Source directory containing the file. If None, uses first path from preferences
    server_path : str or Path, optional
        Destination directory to copy to. If None, uses upload_path from preferences
    overwrite : bool, default False
        Whether to overwrite existing files at the destination

    Returns
    -------
    dict
        Dictionary containing:
        - src_path: Relative path to the file
        - src_md5: MD5 hash of the file
        - src_size: Size of the file in bytes 
        - src_datetime: Creation timestamp of the file

    Raises
    ------
    OSError
        If filepath is a directory
        If destination file exists and overwrite=False
        If copy operation fails


    Joao Couto - labdata 2024
    
    '''
    
    src = Path(local_path)/filepath
    if src.is_dir():
        raise OSError(f'Can only handle files {src}; copy each file in the folder separately.')
    dst = Path(server_path)/filepath
    if not overwrite and dst.exists() and not src == dst:
        raise OSError(f'File {dst} exists; will not overwrite.')
    hash = compute_md5_hash(src)  # computes the hash
    srcstat = src.stat()
    file_size = srcstat.st_size
    from shutil import copy2
    dst.parent.mkdir(parents=True, exist_ok = True)
    if not src == dst: 
        try:
            copy2(src, dst)
        except:
            raise OSError(f'Could not copy {src} to {dst}.')
    else:
        # if the source and destination are the same, don't copy - just return cause its in the same server..
        print('[copy_to_upload_server] Source and destination are the same, not copying.', flush = True)
    filepath = str(filepath).replace(pathlib.os.sep,'/').replace('//','/')
    return dict(src_path = filepath,
                src_md5 = hash,
                src_size = file_size,
                src_datetime = datetime.fromtimestamp(srcstat.st_ctime))

def copy_to_upload_server(filepaths, local_path = None, server_path = None,
                          upload_storage = None,
                          overwrite = False, 
                          n_jobs = 8,
                          job_rule = None,
                          parse_filename = True,
                          **kwargs):
    '''
    Copy data between computers; it will not overwrite, unless forced.

    Returns a list of dictionaries with the file paths and md5 checksums.

    Inserts in the Upload table. 
    Parameters
    ----------
    filepaths : list
        List of file paths to copy to upload server
    local_path : str, optional
        Local path where files are stored. If None, uses first path from preferences
    server_path : str, optional
        Path on upload server. If None, uses upload_path from preferences
    upload_storage : str, optional
        Storage location for uploaded files. If None, uses upload_storage from preferences
    overwrite : bool, default False
        Whether to overwrite existing files on server
    n_jobs : int, default 8
        Number of parallel jobs for copying files
    job_rule : str, optional
        Rule to apply during upload
    parse_filename : bool, default True
        Whether to parse metadata from filenames based on path rules
    **kwargs : dict
        Additional metadata to store with upload (e.g. subject_name, session_name)

    Returns
    -------
    dict
        Dictionary containing upload job information

    Joao Couto - labdata 2024
    '''
    
    from .schema import UploadJob,Setup,Subject,Session,Dataset,dj
    if local_path is None:  # get the local_path from the preferences
        if not 'local_paths' in prefs.keys():
            raise OSError('Local data path [local_paths] not specified in the preference file.')
        local_path = prefs['local_paths'][0]
    if server_path is None: # get the upload_path from the preferences
        if not 'upload_path' in prefs.keys():
            raise OSError('Upload storage [upload_path], not specified in the  preference file.')    
        server_path = prefs['upload_path']
    if upload_storage is None: # get the upload_storage from the preferences, where data will be stored.
        if not 'upload_storage' in prefs.keys():
            raise OSError('Upload storage [upload_storage], not specified in the  preference file.')    
        upload_storage = prefs['upload_storage']
        
    if not type(filepaths) is list: # Check if the filepaths are in a list
        raise ValueError('Input filepaths must be a list of paths.')
    # replace local_path if the user passed it like that by accident.
    filepaths = [str(f).replace(str(local_path),'') for f in filepaths]
    # remove trailing / or \
    filepaths = [f if not f.startswith(pathlib.os.sep) else f[1:] for f in filepaths]
    # make unique
    filepaths = [f for f in np.unique(filepaths)]
    
    if any_path_uploaded(filepaths):
        if not job_rule in ['replace']:
            raise OSError('Path was already uploaded {0}'.format(Path(filepaths[0]).parent))
        else:
            warn('[copy_to_upload_server] Files exist in the server and will be replaced.')
    
    if parse_filename: # parse filename based on the path rules
        tmp = parse_filepath_parts(filepaths[0])
        for k in tmp.keys():
            if not k in kwargs.keys():
                kwargs[k] = tmp[k]

    n_jobs = validate_num_jobs_joblib(n_jobs)   # avoid nested parallelism.
    # copy and compute checksum for all paths in parallel.
    res = Parallel(n_jobs = n_jobs)(
        delayed(_copyfile_to_upload_server)(path,
                                            local_path = local_path,
                                            server_path = server_path,
                                            overwrite = overwrite) for path in filepaths)
    # Add it to the upload table
    # check the job id
    with dj.conn().transaction:
        #print(kwargs)
        if "setup_name" in kwargs.keys():
            Setup.insert1(kwargs, skip_duplicates = True, ignore_extra_fields = True) # try to insert setup
        if "dataset_name" in kwargs.keys() and "session_name" in kwargs.keys() and "subject_name" in kwargs.keys():
            if not len(Subject() & dict(subject_name=kwargs['subject_name'])):
                try:
                    Subject.insert1(kwargs, skip_duplicates = True,ignore_extra_fields = True) # try to insert subject
                except Exception as err:
                    warn(f'Could not insert subject {kwargs}')
                    print(err, flush = True)
                # needs date of birth and sex
            if not len(Session() & dict(subject_name=kwargs['subject_name'],
                                        session_name = kwargs['session_name'])):
                Session.insert1(kwargs, skip_duplicates = True,ignore_extra_fields = True) # try to insert session
            if not len(Dataset() & dict(subject_name = kwargs['subject_name'],
                                        session_name = kwargs['session_name'],
                                        dataset_name = kwargs['dataset_name'])):
                Dataset.insert1(kwargs, skip_duplicates = True, ignore_extra_fields = True) # try to insert dataset
         # this is a brute force way... there should be a better way of doing this but the auto-increment not return in datajoint...
        attempts = 10
        jobid = UploadJob().fetch('job_id')
        if len(jobid):
            jobid = np.max(jobid) + 1 
        else:
            jobid = 1
        job_insert_failed = 1
        for iattempt in range(attempts):
            try: 
                UploadJob.insert1(dict(job_id = jobid, 
                                       job_status = "ON SERVER",
                                       upload_storage = upload_storage,
                                       job_rule = job_rule,
                                       **kwargs),
                                ignore_extra_fields = True) # Need to insert the dataset first if not there
                job_insert_failed = 0
                break # we have the job id
            except Exception as err:
                jobid += 1
                print(err) # we don't have it, do it again
        if job_insert_failed:
            raise ValueError(f'Job insert failed because could not add {jobid} to the UploadJob queue.')
        res = [dict(r, job_id = jobid) for r in res] # add dataset through kwargs
        UploadJob.AssignedFiles.insert(res, ignore_extra_fields=True)
        # the upload server will run the checksum and upload the files.
    return res

def any_path_uploaded(filepaths):
    '''
    any_path_uploaded(filepaths)

    Checks if any of the provided file paths:
    - Exist in the File table (already uploaded)
    - Exist in the UploadJob.AssignedFiles table (queued for upload)
    - Exist in the ProcessedFile table (original file deleted because the dataset was processed with a Rule)

    Parameters
    ----------
    filepaths : list
        List of file paths to check

    Returns
    -------
    bool
        True if any of the files are already uploaded or in the upload queue
        False if none of the files are uploaded or queued
    '''
    from .schema import UploadJob, File, ProcessedFile
    # check if the paths are in "Upload or in Files"
    paths = []
    src_paths = []
    for p in filepaths: # if true for any of the filepaths return True
        pn = p.replace(pathlib.os.sep,'/').replace('//','/')
        paths.append(dict(file_path = pn))
        src_paths.append(dict(src_path = pn))
    if len((File() & paths)) > 0:
        warn(f'Found paths in File table {File() & paths}')
        return True
    if len(UploadJob.AssignedFiles() & src_paths) > 0:
        warn(f'Found paths in UploadJob table {UploadJob.AssignedFiles() & src_paths}')
        return True
    if len(ProcessedFile() & paths) > 0:
        warn(f'Found paths in ProcessedFile table {ProcessedFile() & paths}')
        return True
    return False # Otherwise return False

def all_paths_uploaded(filepaths):
    '''
    all_paths_uploaded(filepaths)

    Checks if all of the provided file paths exist in the File table (already uploaded)
    
    This function only checks the File table, unlike any_path_uploaded() which also checks
    UploadJob.AssignedFiles and ProcessedFile tables.

    Parameters
    ----------
    filepaths : list
        List of file paths to check

    Returns
    -------
    bool
        True if all of the files are already uploaded
        False if any files are missing from the File table
    '''
    from .schema import UploadJob, File, ProcessedFile
    # check if the paths are in "Upload or in Files"
    paths = []
    src_paths = []
    for p in filepaths: # if true for any of the filepaths return True
        pn = p.replace(pathlib.os.sep,'/').replace('//','/')
        paths.append(dict(file_path = pn))
        src_paths.append(dict(src_path = pn))
    if len((File() & paths)) == len(filepaths):
        return True
    
    warn(f'Could not find some files in the table {File() & paths} when trying to find {filepaths}') 
    return False # Otherwise return False
                    
def clean_local_path(local_path = None, filterkeys = [], dry_run = False):
    ''' 
    clean_local_path(local_path = None, filterkeys = [], dry_run = False)

    Remove local files that are already in the database from a local path
    Clean local files that have already been uploaded to the database.
    
    This function checks files in a local directory against the database and removes
    local copies that have already been successfully uploaded (verified by MD5 checksum).
    
    Files are only deleted if they exist in either the File or ProcessedFile tables
      AND their MD5 checksums match exactly
    
    Files with mismatched checksums are kept and reported
    
    Empty directories are not automatically removed (TODO)

    Parameters
    ----------
    local_path : str or Path, optional
        Path to local directory to clean. If None, uses first path from preferences.
    filterkeys : list, optional
        List of strings to filter filenames by. Only files containing all filterkeys will be checked.
    dry_run : bool, optional
        If True, only prints what would be deleted without actually deleting files.
        
    Returns
    -------
    deleted : list
        List of files that were deleted (or would be deleted in dry_run mode)
    keep : list 
        List of files that were kept because their checksums did not match the database
        
    Joao Couto - labdata 2024
    '''
    from .schema import File, ProcessedFile
    if local_path is None:
        local_path = prefs['local_paths'][0]
    filelist = Path(local_path).rglob('*')
    local_filelist = list(filter(lambda x: x.is_file(),filelist))
    remote_filelist = np.array(drop_local_path(local_filelist))
    # check that the files follow a filter
    selection = np.ones_like(remote_filelist, dtype=bool)
    for f in filterkeys:
        selection *= np.array([1 if f in str(k) else 0 for k in remote_filelist],dtype=bool)
    remote_keys_all = [dict(file_path = str(r).replace('\\','/')) for r in remote_filelist[selection]]
    # get the remote keys
    remote_keys = (File() & remote_keys_all).fetch(as_dict = True)
    remote_keys += (ProcessedFile() & remote_keys_all).fetch(as_dict = True)
    keys = [dict(r,
                 local_path = Path(local_path)/r['file_path']) for r in remote_keys]
    res,comparison = compare_md5s([r['local_path'] for r in keys],[r['file_md5'] for r in keys],
                                  full_output = True,
                                  show_progress = True,
                                  suppress_file_not_found = True) # so if the files disappear it doesn't crash.
    if not res:
        print(tcolor['r'](f'{np.sum(~np.array(comparison))} local files have different checksums.'),flush = True)
        for k,r in zip(keys,comparison):
            if not r:
                print(tcolor['r'](f" \t {k['local_path']}"),flush = True)
    keep  = []
    deleted = []
    for k,r in zip(keys,comparison):
        if not r:
            keep.append(k)
        else:
            if not dry_run:
                os.unlink(k['local_path'])
            deleted.append(k['local_path'])
    # check if the "deleted" folders are empty
    for f in deleted:
        print(f.parent)
    return deleted,keep
