from .general import *
from .procedures import *
from .histology import *

@dataschema
class TwoPhoton(dj.Imported):
    definition = '''
    -> Dataset
    ---
    n_planes               : smallint            # number of planes
    n_channels             : smallint            # number of channels
    n_frames               : int                 # duration of the recording
    width                  : int                 # width of each frame
    height                 : int                 # height of each frame
    frame_rate             : double              # frame rate
    -> File                                      # path to the stack
    magnification = NULL   : double              # magnification
    objective_angle = NULL : double              # angle
    objective = NULL       : varchar(32)         # objective
    um_per_pixel = NULL    : blob                # XY scale conversion factors
    scanning_mode = NULL   : varchar(32)         # bidirectional or unidirectional
    pmt_gain = NULL        : blob                # pmt gains
    imaging_software       : varchar(32)         # software and version
    -> [nullable] Atlas.Region                   # target region (or the center of the imaging plane)
    '''

    class Plane(dj.Part):
        definition = '''
        -> master
        plane_num               : smallint       # probe number
        ---
        plane_depth = NULL      : float          # depth from surface
        '''
    
    def open(self):
        # download and open a stack
        if len(self) != 1:
            raise(ValueError(f'Select only one dataset {self.proj().fetch(as_dict = True)}.'))
        fname = (File() & self).get()[0]
        return open_zarr(fname)

@analysisschema
class CellSegmentationParams(dj.Manual):
    definition = '''
    parameter_set_num      : int            # number of the parameters set
    ---
    algorithm_name               : varchar(64)    # cell segmentation algorithm
    parameter_description = NULL : varchar(256)   # description or specific use case
    parameters_dict              : varchar(2000)  # parameters json formatted dictionary "json.dumps"
    code_link = NULL             : varchar(300)   # link to the code
    '''


@analysisschema
class CellSegmentation(dj.Imported):
    definition = '''
    -> Dataset
    -> CellSegmentationParams
    ---
    algorithm_version             : varchar(56)     # version of the algorithm
    n_rois                        : int             # number of segmented ROIs
    crop_region = NULL            : blob            # Region to crop
    segmentation_datetime = NULL  : datetime        # date that the algorith was ran
    -> [nullable] AnalysisFile                      # results file (optional)
     '''
    class Plane(dj.Part):
        definition = '''
        -> master
        plane_num                 : smallint
        ---
        plane_n_rois              : int
        dims = NULL               : blob            # dimensions of the plane
        '''
    class MotionCorrection(dj.Part):
        definition = '''
        -> master.Plane
        ---
        motion_block_size = 0     : int             # 0 is rigid
        displacement              : longblob        # storage of the motion displacement 
        '''
    class Projection(dj.Part):
        definition = '''
        -> master.Plane
        proj_name                 : varchar(16)
        ---
        proj_im                   : longblob
        '''
    class ROI(dj.Part):
        definition = '''
        -> master.Plane
        roi_num                   : int
        ---
        roi_pixels                : blob
        roi_pixels_values = NULL  : blob
        neuropil_pixels = NULL    : blob
        '''
        def get_roi_sparse_masks(self):
            '''
            This returns a sparse array for the sake of speed.
        
            '''
            try:
                dims = (CellSegmentation.Plane & self).fetch1('dims')
            except dj.DataJointError as err:
                if 'fetch1 should only' in str(err):
                    raise ValueError(
                        f"Can only get ROIs simultanously from a single plane {(CellSegmentation.Plane & self).fetch('session_name','plane_num',as_dict = True)}.")
                else:
                    raise(err)
            sparse_masks = []
            from scipy import sparse
            for roi in self.fetch(as_dict = True):
                sparse_masks.append(sparse.csr_array((roi['roi_pixels_values'], 
                                                      np.unravel_index(roi['roi_pixels'],dims)), shape=dims, dtype = 'float32'))
            return sparse_masks
        
        def get_roi_contours(self,percentile_threshold = 80,footprints = None):
            if footprints is None:
                footprints = self.get_roi_sparse_masks()
            roi_contours = []
            from skimage.measure import find_contours
            for f in footprints:
                level = np.percentile(f.data,percentile_threshold)
                from skimage.measure import find_contours
                cc = find_contours(f.todense(),level = level)
                if len(cc):
                    # take the largest contour
                    roi_contours.append(cc[np.argmax([len(c) for c in cc])])
                else:
                    roi_contours.append(None)
            return roi_contours
                
    class RawTraces(dj.Part):
        definition = '''
        -> master.ROI
        ---
        f_trace                   : longblob
        f_neuropil = NULL         : longblob 
        '''    
    class Traces(dj.Part):
        definition = '''
        -> master.ROI
        ---
        dff                       : longblob
        neuropil_coeff = NULL     : float
        '''
    class Deconvolved(dj.Part):
        definition = '''
        -> master.ROI
        ---
        deconv                    : longblob
        '''
    
    class Selection(dj.Part):
        definition = '''
        -> master.ROI
        selection_method = 'auto' : varchar(12)
        ---
        selection                 : smallint      # 0 not a cell, 1 is a cell
        likelihood = NULL         : float
        '''
    
    class LinkedDatasets(dj.Part):
        definition = '''
        -> master
        linked_session_id         : int
        ---
        -> Dataset.proj(linked_session_name='session_name',linked_dataset_session='dataset_name')
    '''
        
    def delete(
            self,
            transaction = True,
            safemode  = None,
            force_parts = False):
        files = [f['file_path'] for f in self]
        
        super().delete(transaction = transaction,
                       safemode = safemode,
                       force_parts = force_parts)
        if len(self) == 0:
            if len(files):
                (AnalysisFile() & [f'file_path = "{t}"' for t in files]).delete(force_parts=force_parts, 
                                                                                safemode = safemode) 

@analysisschema
class SegmentationROIMetrics(dj.Computed):
    definition = '''
    -> CellSegmentation.ROI
    ---
    roi_center               : blob
    radius = NULL            : float
    snr = NULL               : float
    aspect_ratio = NULL      : float
    skewness = NULL          : float
    std = NULL               : float
    noise_level = NULL       : float 
    '''

    def make(self, key):
        # 90th percentile/np.median(np.abs(np.diff(dff))) / np.sqrt(frame_rate)?
        return
