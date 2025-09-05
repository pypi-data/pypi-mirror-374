from ..utils import *
from ..s3 import copy_to_s3

# has utilities needed by other rules
def _checksum_files(filepath, local_path):
    '''
    Checksum files that don't need to be copied
    '''
    # construct the path:
    src = Path(local_path)/filepath
    hash = compute_md5_hash(src)  # computes the hash
    srcstat = src.stat()
    file_size = srcstat.st_size
    return dict(src_path = filepath,
                src_md5 = hash,
                src_size = file_size,
                src_datetime = datetime.fromtimestamp(srcstat.st_ctime))

class UploadRule():
    def __init__(self,job_id,prefs = None):
        '''

Rule to apply on upload. 

        1) Checksum on the files; compare with provided (reserve job if use_db)
        2) Apply function
        3) Checksum on the output - the files that changed
        4) Submit upload
        5) Update tables 

Can submit job on slurm, some of these can be long or take resources.

        '''
        self.rule_name = 'default'
        
        self.job_id = job_id
        self.src_paths = None
        self.processed_paths = None
        self.dst_paths = None
        self.inserted_files = []
        if prefs is None:
            from ..utils import prefs
        self.prefs = prefs
        self.local_path = self.prefs['local_paths'][0]
        self.dataset_key = None # will get written on upload, use in _post_upload
        self.max_concurrent = -1  # maximum number of concurrent UploadJobs that can run [-1 is infinite].

    def apply(self):
        # parse inputs
        from ..schema import UploadJob, File, dj

        if not self.job_id is None:
            with dj.conn().transaction:
                self.jobquery = (UploadJob() & dict(job_id = self.job_id))
                job_status = self.jobquery.fetch(as_dict = True)
                if len(job_status):
                    if job_status[0]['job_waiting']:
                        # check here if there are other jobs running for the same rule on this host
                        if self.max_concurrent > 0:
                            kk = dict(job_host = self.prefs['hostname'],
                                      job_waiting = 0,
                                      job_status = 'WORKING',
                                      job_rule = None)
                            if not self.rule_name == 'default':
                                kk['job_rule'] = self.rule_name
                            number_of_running_jobs = len(UploadJob() & kk)
                            if number_of_running_jobs >= self.max_concurrent:
                                print(f"Job {self.job_id} can not run because there are {number_of_running_jobs} for the same rule.")
                                self.set_job_status(job_status = 'WAITING', job_waiting = 1, job_log = f'Waiting for {number_of_running_jobs}.')
                                return
                        self.set_job_status(job_status = 'WORKING', job_waiting = 0) # take the job
                    else:
                        print(f"Job {self.job_id} is already taken.")
                        #print(job_status, flush = True)
                        return # exit.
                else:
                    raise ValueError(f'job_id {self.job_id} does not exist.')
        # get the paths
        self.src_paths = pd.DataFrame((UploadJob.AssignedFiles() & dict(job_id = self.job_id)).fetch())
        if not len(self.src_paths):
            self.set_job_status(job_status = 'FAILED',
                                job_log = f'Could not find files for {self.job_id} in Upload.AssignedFiles.')
            raise ValueError(f'Could not find files for {self.job_id} in Upload.AssignedFiles.')
        self.upload_storage = self.jobquery.fetch('upload_storage')[0]
        if self.upload_storage is None:
            if 'upload_storage' in self.prefs.keys():
                self.upload_storage = self.prefs['upload_storage']
        
        # this should not fail because we have to keep track of errors, should update the table
        src = [Path(self.local_path) / p for p in self.src_paths.src_path.values]
        try:
            comparison = compare_md5s(src,self.src_paths.src_md5.values)
        except FileNotFoundError:
            print('File not found for {0}'.format(Path(self.src_paths.src_path.iloc[0]).parent))
            self.set_job_status(job_status = 'FAILED', job_log = 'FILE NOT FOUND; check file transfer.')
            return
        
        if not comparison:
            print('CHECKSUM FAILED for {0}'.format(Path(self.src_paths.src_path.iloc[0]).parent))
            self.set_job_status(job_status = 'FAILED',job_log = 'MD5 CHECKSUM failed; check file transfer.')
            return # exit.
        import traceback
        try:
            paths = self._apply_rule() # can use the src_paths
            self._upload()             # compare the hashes after
        except Exception as err:
            # log the error
            print('There was an error processing or uploading this dataset.')
            print(err)
            self.set_job_status(job_status = 'FAILED',job_log = f'{traceback.print_exc()}')
            return
        try:
            self._post_upload()        # so the rules can insert tables and all.
        except Exception as err:
            # log the error
            print('There was an error with the post-upload this dataset.')
            print(err)
            self.set_job_status(job_status = 'FAILED',job_log = f'POST-UPLOAD: {traceback.print_exc()}')
            return 
        return paths # so apply can output paths.
    
    def set_job_status(self, job_status = 'FAILED',job_log = '',job_waiting = 0):
        from ..schema import UploadJob
        if not self.job_id is None:
            kk = dict(job_id = self.job_id,
                      job_waiting = job_waiting,
                      job_status = job_status,
                      job_log = job_log)
            if job_status == 'FAILED':
                print(f'Check job_id {self.job_id} : {job_status}')
                kk['job_host'] = self.prefs['hostname'], # write the hostname so we know where it failed.
            UploadJob.update1(kk)
            

    def _handle_processed_and_src_paths(self, processed_files,new_files):
        '''
        Put the files in the proper place and compute checksums for new files.
        Call this from the apply method.
        '''
        n_jobs = DEFAULT_N_JOBS
        self.processed_paths = []
        for f in processed_files:
            i = np.where(self.src_paths.src_path == f)[0][0]
            self.processed_paths.append(self.src_paths.iloc[i])
            self.src_paths.drop(self.src_paths.iloc[i].name,axis = 0,inplace = True)
            self.src_paths.reset_index(drop=True,inplace = True)
        self.processed_paths = pd.DataFrame(self.processed_paths).reset_index(drop=True)        

        res = Parallel(n_jobs = n_jobs)(delayed(_checksum_files)(
            path,
            local_path = self.local_path) for path in new_files)
        for r in res:
            r['job_id'] = self.job_id
        self.src_paths = pd.concat([self.src_paths,pd.DataFrame(res)], ignore_index=True)
        # drop duplicate paths in case there are any
        self.src_paths = self.src_paths.drop_duplicates(subset=['src_path'], keep='last')
        
    def _post_upload(self):
        return
    
    def _upload(self):
        # this reads the attributes and uploads
        # It also puts the files in the Tables
        
        # destination in the bucket is actually the path
        dst = [k for k in self.src_paths.src_path.values]
        # source is the place where data are
        src = [Path(self.local_path) / p for p in self.src_paths.src_path.values] # same as md5
        # s3 copy in parallel hashes were compared before so no need to do it now.
        self.set_job_status(job_status = 'WORKING',
                            job_log = datetime.now().strftime(f'Uploading {len(src)} files %Y %m %d %H:%M:%S'),
                            job_waiting = 0)
        copy_to_s3(src, dst, md5_checksum=None,storage_name=self.upload_storage)
        from ..schema import UploadJob, File, dj, ProcessedFile, Dataset
        self.set_job_status(job_status = 'WORKING',
                            job_log = datetime.now().strftime('%Y %m %d %H:%M:%S'),
                            job_waiting = 0)
        with dj.conn().transaction:  # make it all update at the same time
            # insert to Files so we know where to get the data
            insfiles = []
            for i,f in self.src_paths.iterrows():
                insfiles.append(dict(file_path = f.src_path,
                                     storage = self.upload_storage,
                                     file_datetime = f.src_datetime,
                                     file_size = f.src_size,
                                     file_md5 = f.src_md5))
            if len(insfiles):
                File.insert(insfiles)
            # Add to dataset?
            job = self.jobquery.fetch(as_dict=True)[0]
            # check if it has a dataset
            if all([not job[a] is None for a in ['subject_name','session_name','dataset_name']]):
                for i,p in enumerate(insfiles):
                    insfiles[i] = dict(subject_name = job['subject_name'],
                                       session_name = job['session_name'],
                                       dataset_name = job['dataset_name'],
                                       file_path = p['file_path'],
                                       storage = self.upload_storage)
                if len(insfiles):
                    Dataset.DataFiles.insert(insfiles)
                self.dataset_key = dict(subject_name = job['subject_name'],
                                        session_name = job['session_name'],
                                        dataset_name = job['dataset_name'])
            self.inserted_files += insfiles
            # Insert the processed files so the deletions are safe
            if not self.processed_paths is None:
                ins = []
                for i,f in self.processed_paths.iterrows():
                    ins.append(dict(file_path = f.src_path,
                                    file_datetime = f.src_datetime,
                                    file_size = f.src_size,
                                    file_md5 = f.src_md5))
                if len(ins):
                    ProcessedFile.insert(ins)
            if len(self.inserted_files): # keep the job in the queue 
                # completed
                self.set_job_status(job_status = 'COMPLETED',
                                    job_log = datetime.now().strftime('UPLOADED %Y %m %d %H:%M:%S'),
                                    job_waiting = 0)
            else:
                self.set_job_status(job_status = 'FAILED',
                                    job_log = datetime.now().strftime('No files inserted %Y %m %d %H:%M:%S'),
                                    job_waiting = 0)
            #(UploadJob & dict(job_id = self.job_id)).delete(safemode = False) # only delete if on completed
        
    def _apply_rule(self):
        # this rule does nothing, so the src_paths are going to be empty,
        # and the "paths" are going to be the src_paths
        self.processed_paths = None # processed paths are just the same, no file changed, so no need to do anything.
        # needs to compute the checksum on all the new files
        return self.src_paths.src_path.values
    
class ReplaceRule(UploadRule):
    '''
    Check if files exist in storage
    Upload new versions of the files
    Update MD5 checksums in database
    '''

    def __init__(self, job_id, prefs = None):
        super(ReplaceRule,self).__init__(job_id = job_id, prefs = prefs)
        self.rule_name = 'replace'

    def _apply_rule(self):
        # can only replace files that were uploaded, the files that are not there will be added to the dataset.
        from ..s3 import s3_delete_file, copyfile_to_s3
        from ..schema import File
        self.processed_paths = None # processed paths are just the same, no file changed, so no need to do anything.

        same_files = []
        replace_files = []
        new_files = []
        for i,f in self.src_paths.iterrows():
            existing = (File() & dict(file_path = f.src_path,
                          storage = self.upload_storage)).fetch(as_dict = True)
            if len(existing):
                existing = existing[0] # there is only one file
                if existing['file_md5'] == f.src_md5:
                    same_files.append(dict(f))
                else:
                    replace_files.append(dict(f))
            else:
                new_files.append(dict(f))
        txt = f'There are {len(new_files)} new files, {len(replace_files)} files to be replaced and {len(same_files)} unmodified files.'
        print(txt,flush = True)
        self.set_job_status(job_status = 'WORKING',
                            job_log = txt,
                            job_waiting = 0)
        ##################### replace files happens here #########################
         # destination in the bucket is actually the path
        dst = [k['src_path'] for k in replace_files]
        # source is the place where data are (this only works for a UNIX server at the moment)
        src = [Path(self.local_path) / p['src_path'] for p in replace_files] # same as md5
        # s3 copy in parallel hashes were compared before so no need to do it now.
        copy_to_s3(src, dst, md5_checksum=None, storage_name=self.upload_storage)
        for f in replace_files:
            File.update1(dict(file_path = f['src_path'],
                              storage = self.upload_storage,
                              file_datetime = f['src_datetime'],
                              file_size = f['src_size'],
                              file_md5 = f['src_md5']))
            print(f'Updated {f["src_path"]}')
        
        # replace the src_paths with the new files otherwise delete all rows
        if len(new_files):
            self.src_paths = pd.DataFrame(new_files)
        else:
            self.src_paths.drop(self.src_paths.index, inplace = True)
        
        return new_files+replace_files
