'''Upload rules for lab data management.

This module provides rules for processing data uploads to the database.
Rules handle validation, preprocessing, and storage of different data types.

Default rules included:

 - UploadRule: Base rule for generic file uploads
 - EphysRule: Rule for electrophysiology data (SpikeGLX)
 - TwoPhotonRule: Rule for two-photon microscopy data (ScanImage/Scanbox)
 - OnePhotonRule: Rule for one-photon imaging data (Widefield - labcams)
 - MiniscopeRule: Rule for (UCLA) Miniscope imaging data
 - FixedBrainRule: Rule for fixed tissue microscopy data
 - ReplaceRule: Rule for replacing existing files

Custom rules can be added to the user_preferences.json configuration.
'''

from .utils import *
from .ephys import *
from .imaging import *

rulesmap = dict(none = UploadRule,
                ephys = EphysRule,
                two_photon = TwoPhotonRule,
                one_photon = OnePhotonRule,
                fixed_brain = FixedBrainRule,
                miniscope = MiniscopeRule,
                replace = ReplaceRule)

if 'upload_rules' in prefs.keys():
    for k in prefs['upload_rules']:
        # TODO: this may need a special field for imports?
        rulesmap[k] = eval(prefs['upload_rules'][k])

def process_upload_jobs(key = None,
                        rule = 'all',
                        n_jobs = 8,
                        job_host = None,
                        force = False,
                        prefs = None):
    '''
    Process UploadJobs using UploadRule(s).
    Custom upload rules can be added as plugins, just include in prefs['upload_rules']

    Joao Couto - labdata 2024
    '''
    from tqdm import tqdm
    from ..schema import UploadJob
    def _job(j,rule = None, prefs = None):
        jb = (UploadJob() & f'job_id = {j}').fetch()
        if len(jb):
            if jb[0]['job_rule'] in rulesmap.keys(): 
                rl = rulesmap[jb[0]['job_rule']](j, prefs = prefs)
            else:
                rl = UploadRule(j,prefs = prefs)
            res = rl.apply()
        return res
    if key is None:
        jobs = (UploadJob() & 'job_waiting = 1').fetch('job_id')
        if not job_host is None:
            if job_host == 'self':
                job_host = prefs['hostname']
            jobs = (UploadJob() &
                    'job_waiting = 1' &
                    f'job_host = "{job_host}"').fetch('job_id')
    else:
        jobs = (UploadJob() & key).fetch('job_id')
    if force:
        for j in jobs:
            UploadJob().update1(dict(job_id  = j, job_waiting = 1)) # reset job
    if len(jobs) == 1:
        res = [_job(jobs[0], rule = rule, prefs = prefs)]
    else:   
        res = Parallel(backend='loky',n_jobs = n_jobs)(delayed(_job)(u,
                                                                     rule = rule,
                                                                     prefs = prefs) 
                       for u in tqdm(jobs,desc = "Running upload jobs: "))
    return res
