# Functions for interacting with S3 storage.
# This file provides utilities for uploading, downloading and managing files on S3 storage.
# Key functionality includes:
#   - Validating S3 storage configurations 
#   - Copying files to/from S3 buckets
#   - Deleting files from S3
#   - Parallel file transfer operations
#
# labdata 2024

from .utils import *

__all__ = ['validate_storage',
           'copyfile_to_s3',
           'copyfile_from_s3',
           'copy_to_s3',
           'copy_from_s3',
           's3_delete_file']

def validate_storage(storage):
    '''
    storage = validate_storage(storage)

    Checks that there is an s3 access_key and secret_key in the storage dictionary.
    Updates the labdata preference file.

    Joao Couto - labdata 2024

    '''
    # lets find the storage in the preferences
    if 'storage' in prefs.keys():
        for key in prefs['storage'].keys():
            if prefs['storage'][key] == storage:
                save_prefs = False
                storage = prefs['storage'][key]
    if not 'protocol' in storage.keys():
        # assume S3
        storage['protocol'] = 's3'
        if 'save_prefs' in dir():
            save_prefs = True
    if storage['protocol'] == 's3':
        # then try to find an access key
        for k in ['access_key','secret_key']:
            if not k in storage.keys():
                storage[k] = None
            if storage[k] is None:
                import getpass
                # get the password and write to file
                storage[k] = getpass.getpass(prompt=f'S3 {k}:')
                if 'save_prefs' in dir():
                    save_prefs = True
    if 'save_prefs' in dir():
        if save_prefs:
            save_labdata_preferences(prefs, LABDATA_FILE)                
    return storage


def copyfile_to_s3(source_file,
                   destination_file,
                   storage,
                   md5_checksum = None):
    '''
    Copy a single file to S3 and do a checksum comparisson.

    Joao Couto - 2024
    '''
    from minio import Minio
    client = Minio(endpoint = storage['endpoint'],
                   access_key = storage['access_key'],
                   secret_key = storage['secret_key'])

    if 'folder' in storage.keys():
        if len(storage['folder']):
            destination_file = storage['folder'] + '/' + destination_file

    if not md5_checksum is None:
        if not md5_checksum == compute_md5_hash(source_file):
            raise OSError(f'Checksum {md5_checksum} does not match {source_file}.')
    res = client.fput_object(
        storage['bucket'], destination_file, source_file)
    return res

def copy_to_s3(source_files, destination_files,
               storage = None,
               storage_name = None,
               md5_checksum = None,
               n_jobs = DEFAULT_N_JOBS):
    '''
    Copy S3 and do a checksum comparisson.
    Copy occurs in parallel for multiple files.

    Joao Couto - 2024
    '''
    if storage is None:
        if storage_name is None:
            raise ValueError("Specify a storage to copy to - either pass the storage dictionary or specify a name from the prefs.")
        storage = prefs['storage'][storage_name] # link to preferences storage from storage_name
    storage = validate_storage(storage) # validate and update keys

    if not type(source_files) is list: # check type of source
        raise ValueError('source_files has to be a list of paths')
    
    if not type(destination_files) is list:  # check type of destination
        raise ValueError('destination_files has to be a list of paths')
    # Check if the source and the destination are the correct sizes
    assert len(source_files) == len(destination_files),ValueError('source and destination are the wrong size')
    
    if md5_checksum is None:
        md5_checksum = [None]*len(source_files)
    from tqdm import tqdm
    n_jobs = validate_num_jobs_joblib(n_jobs) # check if running inside a joblib worker.
    res = Parallel(n_jobs = n_jobs)(delayed(copyfile_to_s3)(src,
                                                            dst,
                                                            storage = storage,
                                                            md5_checksum = md5)
                                    for src,dst,md5 in tqdm(zip(source_files,destination_files,md5_checksum),
                                                            desc = f'Pushing to S3 [{storage["bucket"]}]'))
    return res

def boto3_copy_from_s3(src,dst,store):
    import boto3
    Path(dst).parent.mkdir(exist_ok=True,parents = True)
    s3 = boto3.resource('s3',aws_access_key_id = store['access_key'],
                    aws_secret_access_key = store['secret_key'])
    obj = s3.Object(bucket_name = store['bucket'],
                    key = str(src))
    obj.download_file(str(dst))
    return True

def copyfile_from_s3(source_file,
                     destination_file,
                     storage,
                     md5_checksum = None,
                     engine = 'boto3'):
    '''
    Copy a single file to S3 and do a checksum comparisson.
    
    This function copies a single file from an S3 bucket to local storage. 
    Supports both boto3 and minio engines for S3 operations and handles creating destination directories.
    The function can optionally verify file integrity using an MD5 checksum [NOT IMPLEMENTED]. 
    
    Note: If 'use_awscli' is set to TRUE in the preferences, it will use AWS CLI to copy from S3

    Parameters
    ----------
    source_file : str
        Path to file in S3 bucket to copy
    destination_file : str
        Local path to copy file to
    storage : dict
        Dictionary containing S3 storage configuration with:
        - endpoint: S3 endpoint URL 
        - access_key: AWS access key
        - secret_key: AWS secret key
        - bucket: S3 bucket name
    md5_checksum : str, optional
        MD5 hash to verify file integrity
    engine : str, default 'boto3'
        Engine to use for S3 operations ('boto3' or 'minio')

    Returns
    -------
    bool or MinioResponse
        True if copy successful with boto3
        MinioResponse object if using minio engine

    Joao Couto - 2024
    '''
    if 'use_awscli' in prefs.keys():  # to copy from inside ec2 
        if prefs['use_awscli']:
            cmd = f'AWS_ACCESS_KEY_ID={storage["access_key"]} AWS_SECRET_ACCESS_KEY={storage["secret_key"]} aws s3 cp s3://{storage["bucket"]}/{source_file} {destination_file}'
            os.system(cmd)
            return True
    if engine == 'boto3':
        res = boto3_copy_from_s3(source_file,destination_file,storage)
    else:
        from minio import Minio
        client = Minio(endpoint = storage['endpoint'],
                       access_key = storage['access_key'],
                       secret_key = storage['secret_key'])

        if 'folder' in storage.keys():
            if len(storage['folder']):
                destination_file = storage['folder'] + '/' + destination_file

        res = client.fget_object(
            storage['bucket'], source_file, destination_file)
    return res

def copy_from_s3(source_files, destination_files,
                 storage = None,
                 storage_name = None,
                 n_jobs = DEFAULT_N_JOBS,
                 engine = 'boto3'):
    '''
    copy_from_s3(source_files, destination_files,
                 storage = None,
                 storage_name = None,
                 n_jobs = DEFAULT_N_JOBS,
                 engine = 'boto3')

    This function handles copying multiple files in parallel from an S3 bucket to local storage.
    It supports both boto3 and minio engines for S3 operations. Files can be copied using
    credentials directly provided in a storage dict or from named storage configurations in
    preferences.

    Parameters
    ----------
    source_files : list
        List of file paths to copy from S3
    destination_files : list 
        List of local file paths to copy to
    storage : dict, optional
        Dictionary containing S3 storage configuration. Must include:
        - endpoint: S3 endpoint URL
        - access_key: AWS access key
        - secret_key: AWS secret key
        - bucket: S3 bucket name
    storage_name : str, optional
        Name of storage configuration to use from preferences. Required if storage not provided.
    n_jobs : int, default DEFAULT_N_JOBS
        Number of parallel jobs for copying files
    engine : str, default 'boto3'
        Engine to use for S3 operations ('boto3' or 'minio')

    Returns
    -------
    list
        List of results from copy operations

    Raises
    ------
    ValueError
        If storage or storage_name not provided
        If source_files or destination_files not lists
        If source_files and destination_files different lengths
    Joao Couto - 2024
    '''
    if storage is None:
        if storage_name is None:
            raise ValueError("Specify a storage to copy to - either pass the storage dictionary or specify a name from the prefs.")
        storage = prefs['storage'][storage_name] # link to preferences storage from storage_name
    storage = validate_storage(storage) # validate and update keys, this will store the credentials

    if not type(source_files) is list: # check type of source
        raise ValueError('source_files has to be a list of paths from s3')
    
    if not type(destination_files) is list:  # check type of destination
        raise ValueError(f'destination_files has to be a list of paths {destination_files}')
    # Check if the source and the destination are the correct sizes
    assert len(source_files) == len(destination_files),ValueError(f'source {source_files} and destination {destination_files} are the wrong size')
    if len(source_files) == 1: # don't run in parallel if only copying one file.
        print(f'[Downloading] {source_files[0]}')
        res = [copyfile_from_s3(source_files[0],destination_files[0],storage = storage)]
    else:
        from tqdm import tqdm
        n_jobs = validate_num_jobs_joblib(n_jobs) # avoid nested parallelism.
        res = Parallel(n_jobs = n_jobs)(delayed(copyfile_from_s3)(src,
                                                                  dst,
                                                                  storage = storage,
                                                                  engine = engine)
                                        for src,dst in tqdm(zip(source_files,destination_files),
                                                            desc = f'Pulling from S3 [{storage["bucket"]}]'))
    return res


def s3_delete_file(filepath,storage, remove_versions = False):
    '''
    s3_delete_file(filepath,storage, remove_versions = False)

    Deletes files from s3.
    TODO: make this parallel or a parallel version of the function.
    !!Warning!! this does not wait for confirmation.
    remove_versions = True will delete all versions from the bucket.

    Parameters
    ----------
    filepath : str
        Path to file to delete on S3
    storage : dict
        Dictionary containing S3 storage configuration:
        - endpoint: S3 endpoint URL
        - access_key: S3 access key
        - secret_key: S3 secret key
        - bucket: S3 bucket name
    remove_versions : bool, default False
        Whether to remove all versions of the file
        If True, deletes all versions
        If False, only deletes latest version

    Returns
    -------
    object
        Response from S3 delete operation

    Raises
    ------
    MinioException
        If delete operation fails
        If file does not exist
        If credentials are invalid

    Joao Couto - 2024
    '''
    from minio import Minio
    client = Minio(endpoint = storage['endpoint'],
                   access_key = storage['access_key'],
                   secret_key = storage['secret_key'])

    if remove_versions:
        objects = client.list_objects(storage['bucket'], prefix=filepath,include_version=True)
        for obj in objects:
            res = client.remove_object(storage['bucket'], obj.object_name,version_id = obj.version_id)
        return 
    else:
        res = client.remove_object(storage['bucket'], filepath)
    return res
