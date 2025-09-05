from ..utils import *
from .utils import BaseCompute
from .suite2p import Suite2pCompute
class CaimanCompute(Suite2pCompute):
    container = 'labdata-caiman'
    cuda = False
    name = 'caiman'
    url = 'http://github.com/flatironinstitute/CaImAn'
    def __init__(self,job_id, allow_s3 = None, delete_results = True, **kwargs):
        '''
        This class runs Caiman on a dataset, which can be used for both 1p and 2p data. The ComputeTask will:
        
        1. **File Identification and Dataset Type Check**: Identify the files and determine the type of dataset (Miniscope or TwoPhoton).
        2. **File Copy to Scratch**: Copy only the necessary file(s) to a scratch folder for processing.
        3. **Caiman Execution**: Execute Caiman on the copied file or folder. Using the parameters specified.
        4. **Cleanup and Result Integration**: Delete the memory-mapped files generated during processing and integrate the results into the CellSegmentation table.

        This class includes a handler for the CLI.
        '''
        super(Suite2pCompute,self).__init__(job_id, allow_s3 = allow_s3) # takes BaseCompute init
        self.file_filters = ['.zarr.zip'] # this only runs on zarr.zip for the moment.
        # default parameters
        self.parameters = dict(algorithm_name = 'caiman')
        # will only store these in CellSegmentationParams
        self.parameter_keys = ['pw_rigid','p','gSig','gSiz','merge_thr','rf','stride','tsub',
                               'ssub','nb','min_corr','min_pnr','ssub_B','ring_size_factor',
                               'min_SNR', 'rval_thr', 'use_cnn', 'detrendWin','quantileMin','denoise_dff']
        
        self.parameter_set_num = None # identifier in CellSegmentationParams

        self._init_job()
        if not self.job_id is None:
            self.add_parameter_key()
        self.delete_results = delete_results
      
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
                description = 'Segmentation of imaging datasets using CaImAn.',
                usage = 'caiman -a <SUBJECT> -s <SESSION> -- <PARAMETERS>')
            parser.add_argument('-i','--parameter_set',default = None, type=int, help = 'Parameter set number')
            parser.add_argument('-m','--pwrigid',
                                action='store_true', default=False,
                                help = "Piecewise-rigid registration")
            parser.add_argument('-p',
                                action='store', default=1, type = int,
                                help = "Order of the autoregressive system")
            parser.add_argument('-g','--gsig',
                                action='store', default=[6,6], type = int, nargs = 2,
                                help = "Expected halfwidth of the neurons in pixels")
            parser.add_argument('--nb',
                                action='store', default=0, type = int,
                                help = "number of background components (rank) if positive, set to 0 for CNMFE")
            parser.add_argument('-r','--rf',
                                action='store', default=40, type = int,
                                help = "half-size of the patches in pixels. e.g., if rf=40, patches are 80x80")
            parser.add_argument('--stride',
                                action='store', default=20, type = int,
                                help = "size of the overlap in pixels")
            parser.add_argument('-s','--ring-size',
                                action='store', default=1.4, type = float,
                                help = "radius of ring is gSiz*ring_size_factor")
            parser.add_argument('--merge-thr',
                                action='store', default=.7, type = float,
                                help = "merging threshold, max correlation allowed")
            parser.add_argument('--tsub',
                                action='store', default=4, type = int,
                                help = "downsampling factor in time for initialization, increase if you have memory problems")
            parser.add_argument('--ssub',
                                action='store', default=2, type = int,
                                help = "downsampling factor in space for initialization, increase if you have memory problems")
            parser.add_argument('--ssub_b',
                                action='store', default=2, type = int,
                                help = "additional downsampling factor for the background")
            parser.add_argument('--min-corr',
                                action='store', default=.8, type = float,
                                help = "min peak value from correlation image")
            parser.add_argument('--min-pnr',
                                action='store', default=10, type = float,
                                help = "min peak to noise ratio")

            parser.add_argument('--snr_thr',
                                action='store', default=7, type = float,
                                help = "[cell selection] signal to noise ratio threshold")
            parser.add_argument('--rval-thr',
                                action='store', default=0.85, type = float,
                                help = "[cell selection] spatial correlation threshold")
            parser.add_argument('--use-cnn',
                                action='store_true', default = False,
                                help = "[cell selection] use a CNN to help deciding good from bad units")
            parser.add_argument('--denoise-dff',
                                action='store_true', default = False,
                                help = "[df/f] compute dff on the denoised data")

            parser.add_argument('--quantile_min',
                                action='store', default=8, type = float,
                                help = "[df/f] Minimum quantile for df/f detrending")
            parser.add_argument('--detrend_win',
                                action='store', default=250, type = int,
                                help = "[df/f] Number of frames for detrending")
            parser.add_argument('--roi',
                                action='store', default=None, type = int, nargs = 4,
                                help = "ROI")

            args = parser.parse_args(arguments[1:])
            
            params = dict(pw_rigid = args.pwrigid,
                          p = int(args.p),
                          gSig = [int(a) for a in args.gsig], 
                          gSiz = [int(a) for a in 2*np.array(args.gsig) + 1],
                          merge_thr = float(args.merge_thr),      
                          rf = int(args.rf),                    
                          stride = int(args.stride),              
                          tsub = int(args.tsub),                  
                          ssub = int(args.ssub),                  
                          nb = int(args.nb),                      
                          min_corr = float(args.min_corr),             
                          min_pnr = float(args.min_pnr),               
                          ssub_B = int(args.ssub_b),                 
                          ring_size_factor = float(args.ring_size),
                          min_SNR = float(args.snr_thr),
                          rval_thr = float(args.rval_thr),
                          use_cnn = bool(args.use_cnn),
                          detrendWin = int(args.detrend_win),
                          denoise_dff = bool(args.denoise_dff),
                          quantileMin = float(args.quantile_min),
                          roi = args.roi)   
            self.parameters = params
        
    def _compute(self):

        from ..schema import Miniscope, CellSegmentationParams, CellSegmentation, TwoPhoton
        from ..stacks import export_to_tiff
        import string
        rand = ''.join(np.random.choice([s for s in string.ascii_lowercase + string.digits],9))
        temporary_folder = Path(prefs['scratch_path'])/f'caiman_temporary_{rand}'
        dset = (Miniscope() & self.dataset_key)
        cnmfparams = {
                'motion_correct' : True,
                'method_init': 'corr_pnr',  # use this for 1 photon
                'K': None, # for 1p                                
                'nb': 0,             # number of background components (rank) if positive, set to 0 for CNMFE
                'nb_patch': 0,
                'low_rank_background': None,           # for 1p
                'update_background_components': True,  # sometimes setting to False improve the results
                'del_duplicates': True,                # whether to remove duplicates from initialization
                'normalize_init': False,               # just leave as is
                'center_psf': True,                    # True for 1p
                'only_init': True,    # set it to True to run CNMF-E
                'method_deconvolution': 'oasis'}       # could use 'cvxpy' alternatively

        if not len(dset):
            dset = (TwoPhoton() & self.dataset_key)
            # add the 2p parameters here and do the processing per plane.
            is_two_photon = True
        else:
            frame_rate = (Miniscope() & self.dataset_key).fetch1('frame_rate')
            is_two_photon = False
        dat = dset.open()
        parameters = (CellSegmentationParams & f'parameter_set_num = {self.parameter_set_num}').fetch1()

        params = json.loads(parameters['parameters_dict'])
        for k in params.keys():
            cnmfparams[k] = params[k]

        import logging
        logger = logging.getLogger('caiman')
        # Set to logging.INFO if you want much output, potentially much more output
        logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        
        import time
        from caiman.source_extraction.cnmf.params import CNMFParams
        parameters = CNMFParams(params_dict = dict({k:cnmfparams[k] for k in ['motion_correct','pw_rigid']},
                                                   fr = frame_rate))
        
        os.environ['CAIMAN_DATA'] = f'{temporary_folder}'

        paths = export_to_tiff(dat,temporary_folder,
                               crop_region = self.parameters['roi'])
        pmotion = parameters.get_group('motion')

        n_cpus = DEFAULT_N_JOBS
        cluster = setup_cluster(n_cpus)

        tstart = time.time()
        from caiman.motion_correction import MotionCorrect
        mot_correct = MotionCorrect(paths, dview=cluster, **pmotion)
        mot_correct.motion_correct(save_movie=True)
        print(f'Done with motion correction in {(time.time() - tstart)/60.} min.')
        
        [os.unlink(f) for f in paths]
        fname_mc = mot_correct.fname_tot_els if cnmfparams['pw_rigid'] else mot_correct.fname_tot_rig
        if pmotion['pw_rigid']:
            bord_px = np.ceil(np.maximum(np.max(np.abs(mot_correct.x_shifts_els)),
                                         np.max(np.abs(mot_correct.y_shifts_els)))).astype(int)
        else:
            bord_px = np.ceil(np.max(np.abs(mot_correct.shifts_rig))).astype(int)

        bord_px = 0 if pmotion['border_nan'] == 'copy' else bord_px
        from caiman import save_memmap
        fname_new = save_memmap(fname_mc, base_name='memmap_', order='C',
                                border_to_0 = bord_px)
        [os.unlink(f) for f in fname_mc]
        
        from caiman import load_memmap
        Yr, dims, T = load_memmap(fname_new)
        images = Yr.T.reshape((T,) + dims, order='F')

        tstart = time.time()
        from caiman.source_extraction import cnmf
        parameters.change_params(cnmfparams)
        cnmfe_model = cnmf.CNMF(n_processes = n_cpus, 
                                dview = cluster, 
                                params = parameters)

        cnmfe_model.fit(images);

        print(f'Done with CNMF in {(time.time() - tstart)/60.} min.')
        
        quality_params = {'min_SNR': params['min_SNR'],
                          'rval_thr': params['rval_thr'],
                          'use_cnn': params['use_cnn']}
        cnmfe_model.params.change_params(params_dict=quality_params)
        print(f"Evaluating components.")
        cnmfe_model.estimates.evaluate_components(images, cnmfe_model.params, dview=cluster)
        print(f"Computing df/f.")
        cnmfe_model.estimates.detrend_df_f(quantileMin = params['quantileMin'], 
                                           frames_window = int(params['detrendWin']),
                                           flag_auto = False,
                                           use_residuals = not params['denoise_dff'])
        print('*****')
        print(f"Total number of components: {len(cnmfe_model.estimates.C)}")
        print(f"Number accepted: {len(cnmfe_model.estimates.idx_components)}")
        print(f"Number rejected: {len(cnmfe_model.estimates.idx_components_bad)}")
        cluster.terminate()
        from ..stacks import compute_projections
        mean_proj,std_proj,max_proj,corr_proj = compute_projections(images)
        print('Projections computed.')
        import caiman
        if not is_two_photon:
            iplane = 0
            dkey = (Miniscope & self.dataset_key).proj().fetch1()
        cell_seg = dict(dkey,
                        parameter_set_num = self.parameter_set_num,
                        algorithm_version = f'caiman {caiman.__version__}',
                        n_rois = cnmfe_model.estimates.A.shape[-1],
                        crop_region = self.parameters['roi'],
                        segmentation_datetime = datetime.now()) # if we need a file to store results, it goes here
        roi_masks = np.array(cnmfe_model.estimates.A.todense()).reshape((*cnmfe_model.dims,-1))
        roi_masks = roi_masks.transpose(2,0,1)
        
        planekey = dict(dkey,
                        parameter_set_num  = self.parameter_set_num,
                        plane_num = iplane)
        planedict = dict(planekey,
                         plane_n_rois = len(roi_masks),
                         dims = [a for a in mean_proj.shape])
        roidict = []
        tracesdict = []
        rawtracesdict = []
        selectiondict = []
        for icell,roi in enumerate(roi_masks):
            roi_pixels, roi_pixels_values = get_roi_pixels(roi)
            roidict.append(dict(planekey,
                                roi_num = icell,
                                roi_pixels = roi_pixels,
                                roi_pixels_values = roi_pixels_values))
            tracesdict.append(dict(planekey,
                                   roi_num = icell,
                                   dff = cnmfe_model.estimates.F_dff[icell].astype(np.float32)))
            rawtracesdict.append(dict(planekey,
                                      roi_num = icell,
                                      f_trace = cnmfe_model.estimates.C[icell].astype(np.float32)))
            selection = 0
            if icell in cnmfe_model.estimates.idx_components:
                selection = 1
            selectiondict.append(dict(planekey,
                                  roi_num = icell,
                                  selection_method = 'auto',
                                  selection = selection))
        projdict = [dict(planekey,
                         proj_name = n,
                         proj_im = pi) for n,pi in zip(
                             ['mean','std','max','lcorr'],
                             [mean_proj,std_proj,max_proj,corr_proj])]

        CellSegmentation.insert1(cell_seg, allow_direct_insert = True)
        CellSegmentation.Plane.insert1(planedict,allow_direct_insert = True)
        if not params['pw_rigid']:
            motion = np.array(mot_correct.shifts_rig).astype(np.float32)
            CellSegmentation.MotionCorrection.insert1(dict(planekey,
                                                           motion_block_size = 0,
                                                           displacement = motion))
        CellSegmentation.Projection.insert(projdict,allow_direct_insert = True)
        CellSegmentation.ROI.insert(roidict ,allow_direct_insert = True)
        # Insert traces in parallel to prevent timeout errors from mysql
        from tqdm import tqdm
        Parallel(n_jobs = DEFAULT_N_JOBS)(delayed(CellSegmentation.Traces.insert1)(
            u,
            skip_duplicates=True,
            ignore_extra_fields = True,
            allow_direct_insert = True) for u in tqdm(tracesdict,desc = 'Inserting traces'))
        # CellSegmentation.Traces.insert(tracesdict,allow_direct_insert = True)
        # CellSegmentation.RawTraces.insert(rawtracesdict,allow_direct_insert = True)
        Parallel(n_jobs = DEFAULT_N_JOBS)(delayed(CellSegmentation.RawTraces.insert1)(
            u,
            skip_duplicates = True,
            ignore_extra_fields = True,
            allow_direct_insert = True) for u in tqdm(rawtracesdict,desc = 'Inserting raw traces'))
        CellSegmentation.Selection.insert(selectiondict,allow_direct_insert = True)
        if self.delete_results:
            print(f'[{self.name} job] Removing the temporary folder.')
            import shutil
            shutil.rmtree(temporary_folder)

        
def get_roi_contour(roi_mask,percentile_threshold = 80):
    from skimage.measure import find_contours
    # find_contours?
    level = np.percentile(roi_mask[roi_mask>0], percentile_threshold)
    C = find_contours(roi_mask,level = level) # there should be only one contour, this takes the first one
    return C[0]
    
def get_roi_pixels(roi_mask):
    ii = np.ravel_multi_index(np.where(roi_mask!=0), roi_mask.shape)
    return ii, np.take(roi_mask,ii)


def setup_cluster(n_cpus,cluster = None):
    from caiman import stop_server, cluster
    #%% start a cluster for parallel processing (if a cluster already exists it will be closed and a new session will be opened)
    if not cluster is None:  # 'locals' contains list of current local variables
        stop_server(dview=cluster)
    _, cluster, n_processes = cluster.setup_cluster(backend='multiprocessing',
                                                    n_processes = n_cpus,
                                                    ignore_preexisting = False)
    print(f"Set up parallelization with {n_processes} processes.")
    return cluster
