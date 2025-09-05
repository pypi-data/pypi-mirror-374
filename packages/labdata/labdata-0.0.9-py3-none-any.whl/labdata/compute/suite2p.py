from ..utils import *
from .utils import BaseCompute

class Suite2pCompute(BaseCompute):
    container = 'labdata-suite2p'
    cuda = False
    name = 'suite2p'
    url = 'http://github.com/mouseland/suite2p'
    def __init__(self,job_id, allow_s3 = None, delete_results = True, **kwargs):
        '''
        This class runs Suite2p and FISSA neuropil decontamination on a dataset, which can be used for 2p data. 
        '''
        super(Suite2pCompute,self).__init__(job_id, allow_s3 = allow_s3)
        self.file_filters = ['.zarr.zip','.sbx','.tiff'] #works with zarr, sbx and tiff
        # default parameters
        self.parameters = dict(algorithm_name = 'suite2p+fissa')
        # will only store these in CellSegmentationParams
        self.parameter_keys = ["use_builtin_classifier","use_fissa","tau","nonrigid",
                               "sparse_mode","connected","spatial_scale","diameter",
                               "threshold_scaling"]
        
        self.parameter_set_num = None # identifier in CellSegmentationParams

        self._init_job()
        if not self.job_id is None:
            self.add_parameter_key()
        self.delete_results = delete_results

    def _get_parameter_number(self):
        parameter_set_num = None
        from labdata.schema import CellSegmentationParams
        # check if in spike sorting
        parameters = pd.DataFrame(CellSegmentationParams().fetch())
        filtered_par = {k:self.parameters[k] for k in self.parameter_keys}

        for i,r in parameters.iterrows():
            # go through every algo
            if filtered_par == json.loads(r.parameters_dict):
                parameter_set_num = r.parameter_set_num
        if parameter_set_num is None:
            if len(parameters) == 0:
                parameter_set_num = 1
            else:
                parameter_set_num = np.max(parameters.parameter_set_num.values) + 1
                
        return parameter_set_num,parameters
    
    def add_parameter_key(self):
        parameter_set_num, parameters = self._get_parameter_number()
        #print(f'Running add_parameter_key {parameters}')
        from ..schema import CellSegmentation, CellSegmentationParams
        if not parameter_set_num in parameters.parameter_set_num.values:
            filtered_par = {k:self.parameters[k] for k in self.parameter_keys}  
            CellSegmentationParams().insert1(dict(parameter_set_num = parameter_set_num,
                                                  algorithm_name = self.name,
                                                  parameters_dict = json.dumps(filtered_par),
                                                  code_link = self.url),
                                             skip_duplicates=True)
        self.parameter_set_num = parameter_set_num
        # this can be applied to the TwoPhoton or the Miniscope datasets
        from ..schema import TwoPhoton, Miniscope
        if self.dataset_key is None:
            print('dataset_key was not set.')
            return
        if len(TwoPhoton.Plane() & self.dataset_key):
            recordings = TwoPhoton.Plane() & self.dataset_key
            segmentations = CellSegmentation.Plane() & self.dataset_key & dict(parameter_set_num = self.parameter_set_num)
        elif len(Miniscope() & self.dataset_key):
            recordings = Miniscope() & self.dataset_key
            segmentations = CellSegmentation.Plane() & self.dataset_key & dict(parameter_set_num = self.parameter_set_num)
        if len(recordings) == len(segmentations):
            self.set_job_status(
                job_status = 'FAILED',
                job_waiting = 0,
                job_log = f'{self.dataset_key} was already segmented with parameters {self.parameter_set_num}.')    
            raise(ValueError(f'{self.dataset_key} was already segmented with parameters {self.parameter_set_num}.'))
           
    def _secondary_parse(self,arguments,parameter_number = None):
        '''
        Handles parsing the command line interface
        '''
        if not parameter_number is None:
            self.parameters = ((CellSegmentationParams() & f'parameter_set_num = {parameter_number}')).fetch(as_dict = True)
            if not len(self.parameters):
                raise(f'Could not find parameter {parameter_number} in CellSegmentationParams.')
            self.parameters = self.parameters[0]
        else:
            import argparse
            parser = argparse.ArgumentParser(
                description = 'Segmentation of imaging datasets using Suite2p and FISSA neuropil correction.',
                usage = 'suite2p -a <SUBJECT> -s <SESSION> -- <PARAMETERS>')
            parser.add_argument('-i','--parameter_set',default = None, type=int, help = 'Parameter set number')

            parser.add_argument('--tau',default = 1.5, type=float, help = 'Decay time constant of the calcium indicator, use 0.7 for GCaMP6f, 1.0 for GCaMP6m, 1.25-1.5 for GCaMP6s.')
            parser.add_argument('--no-use-classifier',
                                action='store_true', default = False,
                                help = "[cell selection] do not use a classifier to help deciding good from bad cells")
            parser.add_argument('--no-nonrigid',
                                action='store_true', default = False,
                                help = "[motion correction] perform rigid motion correction")
            parser.add_argument('--no-fissa-denoise',
                                action='store_true', default = False,
                                help = "Use FISSA to get df/f and correct for neuropil contamination")
            parser.add_argument('--spatial-scale',default = 0, type=int,
                                help = 'Spatial scale for the recordings 0: auto, 1: 6 pixels, 2: 12 pixels), 3: 24 pixels, 4: 48 pixels')
            parser.add_argument('--diameter',default = 6, type=int,
                                help = 'Diameter for cell detection (when not running in sparse mode; default is 6)')
            parser.add_argument('--threshold-scaling',default = 1.2, type=float,
                                help = 'Threshold for ROI detection (higher=less cells detected; default is 1.2).')
            parser.add_argument('--no-sparse',default = True,action = "store_false",
                                help = 'Flag to control "sparse_mode" cell detection.')       
            parser.add_argument('--detect-processes',default = False,action = "store_true",
                                help = 'Allow connected components.')       
            parser.add_argument('--roi',
                                action='store', default=None, type = int, nargs = 4,
                                help = "ROI")

            args = parser.parse_args(arguments[1:])
            
            params = dict(use_builtin_classifier = not args.no_use_classifier,
                          use_fissa = not args.no_fissa_denoise,
                          tau = args.tau,
                          sparse_mode = not args.no_sparse,
                          connected = args.detect_processes,
                          threshold_scaling = args.threshold_scaling,
                          spatial_scale = args.spatial_scale,
                          diameter = args.diameter,
                          nonrigid = not args.no_nonrigid,
                          roi = args.roi)
            self.parameters = params

    def find_datasets(self, subject_name = None, session_name = None):
        '''
        Searches for subjects and sessions in TwoPhoton
        '''
        if subject_name is None and session_name is None:
            print("\n\nPlease specify a 'subject_name' and a 'session_name' to perform segmentation with Suite2p.\n\n")
        from labdata.schema import Miniscope, CellSegmentation, TwoPhoton
        keys = []
        if not subject_name is None:
            if len(subject_name) > 1:
                raise ValueError(f'Please submit one subject at a time {subject_name}.')
            if not subject_name[0] == '':
                subject_name = subject_name[0]
        if not session_name is None:
            for s in session_name:
                if not s == '':
                    keys.append(dict(subject_name = subject_name,
                                     session_name = s))
        else:
            # find all sessions that can be segmented
            parameter_set_num, parameters = self._get_parameter_number()
            sessions = np.unique(((
                (Miniscope() & f'subject_name = "{subject_name}"') -
                (CellSegmentation() & f'parameter_set_num = {parameter_set_num}'))).fetch('session_name'))
            for ses in sessions:
                keys.append(dict(subject_name = subject_name,
                                 session_name = ses))
        datasets = []
        for k in keys:
            datasets += (Miniscope()& k).proj('subject_name','session_name','dataset_name').fetch(
                as_dict = True)

        if not len(datasets):
            for k in keys:
                datasets += (TwoPhoton()& k).proj('subject_name','session_name','dataset_name').fetch(
                    as_dict = True)
        return datasets
        
    def _compute(self):
        from numba import set_num_threads # control the number of threads used by suite2p 
        set_num_threads(DEFAULT_N_JOBS)
        import suite2p
        version = f'suite2p{suite2p.version}'
        if self.parameters['use_fissa']:
            import fissa
            version+= f';fissa{fissa.__version__}'
        from ..schema import TwoPhoton, CellSegmentation, File
        
        seskeys = (TwoPhoton() & self.dataset_key).proj().fetch(as_dict = True)
        if len(seskeys):
            rec_files = (File & (TwoPhoton & seskeys)).get()
            ses_par = (TwoPhoton() & seskeys).fetch(as_dict = True)
        else:
            raise(NotImplemented("Only two-photon segmentation is implemented using this compute."))
        
        nchannels = ses_par[0]['n_channels']
        nplanes = ses_par[0]['n_planes']
        fs = ses_par[0]['frame_rate']
        
        import string
        rand = ''.join(np.random.choice([s for s in string.ascii_lowercase + string.digits],9))
        savedir = Path(prefs['scratch_path'])/f'suite2p_temporary_{rand}'
        savedir.mkdir(exist_ok=True,parents=True)

        ops = suite2p.default_ops()
        for p in self.parameters.keys():
            if p in ops.keys():
                ops[p] = self.parameters[p]

        # handle different file types
        sbx_files = [f for f in rec_files if str(f).endswith('.sbx')]
        zarr_files = [f for f in rec_files if str(f).endswith('.zarr.zip')]
        if len(zarr_files):
            print('Converting zarr file to tiff.')
            rec_files = [savedir/'rawdata.tif']
            from tifffile import TiffWriter
            with TiffWriter(str(rec_files[0]), bigtiff=True, append=True) as tif:
                from tqdm import tqdm 
                for ifile,zarrfile in enumerate(zarr_files):
                    fd = open_zarr(zarrfile)
                    for o,f in tqdm(chunk_indices(len(fd),512),
                                    desc = f"Concatenating raw data [{ifile}]"):
                        tif.save(np.array(fd[o:f]).reshape((-1,*fd.shape[-2:])))
            ops['input_format'] = 'tif'
        elif len(sbx_files):
            print('File format is SBX.')
            ops['input_format'] = 'sbx'
            rec_files = sbx_files
        else:
            raise(ValueError(f'No valid file format found in {rec_files}.'))
        
        ops['fs'] = fs
        ops['nplanes'] = nplanes
        ops['nchannels'] = nchannels
        ops['fast_disk'] = str(savedir)
        ops['save_folder'] = str(savedir/'suite2p')
        ops['combined'] = False # do not combine planes
        db = {
            'data_path': [s.parent for s in rec_files],
        }
        for o in ops.keys():
            print(f'    {o} : {ops[o]}')
        
        suite2p.run_s2p(ops=ops, db = db)
        
        from labdata.stacks import compute_projections
        planefolders = natsorted([a.parent for a in savedir.rglob('*F.npy') 
                                  if not 'combined' in str(a)])
        
        offsets = np.cumsum([0,*[int(a) for a in (TwoPhoton() & seskeys).fetch('n_frames')]])
        cellsegdicts = []
        planedicts = []
        projdicts = [] 
        roidicts = []
        tracesdicts = []
        rawtracesdicts = []
        deconvdicts = []
        selectiondicts = []
        nframes_projection = 4000
        cellcount = [0 for s in seskeys]
        for iplane,planefolder in enumerate(planefolders):
            F = np.load(planefolder/'F.npy')
            Fneu = np.load(planefolder/'Fneu.npy')
            spks = np.load(planefolder/'spks.npy')
            stats = np.load(planefolder/'stat.npy',allow_pickle=True)
            ops = np.load(planefolder/'ops.npy',allow_pickle=True).item()
            iscell = np.load(planefolder/'iscell.npy', allow_pickle=True)
            # load the binary file
            binaryfile = planefolder/'data.bin'
            nrows = ops['Ly']
            ncols = ops['Lx']
            nframes = int(binaryfile.stat().st_size/nrows/ncols/2)
            binary = np.memmap(binaryfile,shape = (nframes, nrows, ncols),
                               dtype = 'int16',order = 'C')
            dims = binary.shape[1:]
            rois = []
            for icell,s in enumerate(stats):
                ii = np.ravel_multi_index([s['ypix'],s['xpix']],dims)
                rois.append(dict(roi_num = icell,
                                 roi_pixels = ii,
                                 roi_pixels_values = s['lam']))
            # extract and denoise with FISSA!
            if self.parameters['use_fissa']:
                
                dff,spks = extract_dff_fissa(stats,binary,dims,
                                             batch_size=ops['batch_size'],
                                             tau=ops['tau'],
                                             fs=ops['fs'])
            else:
                print('Skipping df/f, there will be no "Traces".')
                dff = None
            iplane = int(iplane)
            for isession, (key,on,off) in enumerate(zip(seskeys,offsets[:-1],offsets[1:])):
                mean_proj,std_proj,max_proj, corr_proj =  compute_projections(binary[on:on+nframes_projection])
                planekey = dict(key,
                            parameter_set_num = self.parameter_set_num,
                            plane_num = iplane)
                planedicts.append(dict(planekey,
                             plane_n_rois = len(rois),
                             dims = [a for a in dims]))
                cellcount[isession] += len(rois) # count cells in all planes
                projdicts.extend([dict(planekey, proj_name = n,
                                       proj_im = pi) for n,pi in zip(['mean','std','max','lcorr'],
                                                                     [mean_proj,std_proj,max_proj,corr_proj])])
                for icell,roi in enumerate(rois):
                    roidicts.append(dict(planekey,**roi))
                    if not dff is None:
                        tracesdicts.append(dict(planekey,
                                                roi_num = icell,
                                                dff = dff[icell].astype(np.float32)[on:off]))
                    rawtracesdicts.append(dict(planekey,
                                              roi_num = icell,
                                              f_trace = F[icell].astype(np.float32)[on:off],
                                              f_neuropil = Fneu[icell].astype(np.float32)[on:off]))
                    deconvdicts.append(dict(planekey,
                                            roi_num = icell,
                                            deconv = spks[icell].astype(np.float32)[on:off]))
                    selectiondicts.append(dict(planekey,
                                               roi_num = icell,
                                               selection_method = 'auto',
                                               selection = bool(iscell[icell,0]),
                                               likelihood = iscell[icell,1]))                  
        datenow = datetime.now()
        for key,ncells in zip(seskeys,cellcount):
            cellsegdicts.append(dict(key,parameter_set_num = self.parameter_set_num,
                                     n_rois = ncells,
                                     crop_region = None,
                                     algorithm_version = version,
                                     segmentation_datetime = datenow))
        CellSegmentation.insert(cellsegdicts, allow_direct_insert = True)
        CellSegmentation.Plane.insert(planedicts,allow_direct_insert = True)
        # if not params['pw_rigid']: # Not implemented
        #     motion = np.array(shifts).astype(np.float32)
        #     CellSegmentation.MotionCorrection.insert1(dict(planekey,
        #                                                    motion_block_size = 0,
        #                                                    displacement = motion))
        CellSegmentation.Projection.insert(projdicts,allow_direct_insert = True)
        CellSegmentation.ROI.insert(roidicts ,allow_direct_insert = True)
        # Insert traces in parallel to prevent timeout errors from mysql
        from tqdm import tqdm
        Parallel(n_jobs = DEFAULT_N_JOBS)(delayed(CellSegmentation.Traces.insert1)(
            u,
            skip_duplicates=True,
            ignore_extra_fields = True,
            allow_direct_insert = True) for u in tqdm(tracesdicts,desc = 'Inserting df/f'))
        Parallel(n_jobs = DEFAULT_N_JOBS)(delayed(CellSegmentation.RawTraces.insert1)(
            u,
            skip_duplicates = True,
            ignore_extra_fields = True,
            allow_direct_insert = True) for u in tqdm(rawtracesdicts,desc = 'Inserting raw'))
        
        Parallel(n_jobs = DEFAULT_N_JOBS)(delayed(CellSegmentation.Deconvolved.insert1)(
            u,
            skip_duplicates = True,
            ignore_extra_fields = True,
            allow_direct_insert = True) for u in tqdm(deconvdicts,desc = 'Deconvolved'))
        
        CellSegmentation.Selection.insert(selectiondicts,allow_direct_insert = True)
        if self.delete_results:
            print(f'[{self.name} job] Removing the temporary folder.')
            import shutil
            shutil.rmtree(savedir)

def extract_dff_fissa(stats,binary,dims,fs, batch_size,tau):
    '''
    stats is from suite 2p 
    binary is the raw data stack
    dims are (ops["Ly"],ops["Lx"])
    '''
    cell_ids = np.arange(len(stats)) 
    # cell_ids = cell_ids[iscell == 1]  # only take the ROIs that are actually cells.
    num_rois = len(cell_ids)
    # Generate ROI masks in a format usable by FISSA
    rois = [np.zeros(dims, dtype=bool) for n in range(num_rois)]

    for i, n in enumerate(cell_ids):
        # i is the position in cell_ids, and n is the actual cell number
        ypix = stats[n]["ypix"][~stats[n]["overlap"]]
        xpix = stats[n]["xpix"][~stats[n]["overlap"]]
        rois[i][ypix, xpix] = 1
    import fissa
    roiidx = np.where([r.sum()>4 for r in rois ])[0]
    fissa_res = fissa.Experiment(images=[binary],rois=[[rois[i] for i in roiidx]],
                                 ncores_separation = DEFAULT_N_JOBS,
                                 ncores_preparation = DEFAULT_N_JOBS)

    res = fissa_res.separate()
    fissa_res.calc_deltaf(freq=fs)

    dff = np.zeros((num_rois,
                    len(fissa_res.deltaf_result[0][0][0])),dtype = 'float32')
    for iroi,r in zip(roiidx,fissa_res.deltaf_result):
        dff[iroi] = r[0][0]
    # the deconvolution should be ran on the demixed traces
    from suite2p.extraction import dcnv
    spks = dcnv.oasis(F=dff, batch_size=batch_size, tau=tau, fs=fs)
    return dff,spks  
