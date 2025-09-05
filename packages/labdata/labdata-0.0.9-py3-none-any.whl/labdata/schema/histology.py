from .general import *

@dataschema
class Atlas(dj.Manual):
    definition = '''
    atlas_id : varchar(12)
    ---
    atlas_description = NULL: varchar(156)
    atlas_url = NULL: varchar(156)
    atlas_citation = NULL: varchar(156)
    '''
    class Region(dj.Part):
        definition = '''
        -> master
        region_acronym : varchar(12)
        ---
        region_name: varchar(256)
        region_id: int
        region_atlas_id: int
        region_level: int
        region_graph_depth = NULL: int
        region_graph_order = NULL: int
        structure_id_path: varchar(80)
        color_hex = NULL: char(8)
        '''

@dataschema
class FixedBrain(dj.Imported):
    '''Whole brain histology or fixed tissue. 
    The class provides methods for:
    - Loading brain image data via get() method
    - Viewing brain data in napari via napari_open() method
    
    Definition
    ----------
    file_path : str
        Path to the brain imaging data file
    num_channels : int
        Number of imaging channels
    width : int 
        Image width in pixels
    height : int
        Image height in pixels
    um_per_pixel : array
        Microns per pixel resolution in each dimension
    hardware : str
        Imaging hardware/microscope used
    '''
    definition = '''
    -> Dataset
    ---
    -> [nullable] File
    num_channels = NULL          : smallint
    width = NULL                 : int
    height = NULL                : int
    um_per_pixel = NULL          : blob
    hardware  = NULL             : varchar(56)
    '''
    
    class Channel(dj.Part):
        definition = '''
        -> master
        channel_index : smallint
        ---
        channel_wavelength = NULL : float
        channel_description = NULL : varchar(64)
        '''

    def get(self):
        '''Get the brain imaging data.
        
        Returns
        -------
        array or list
            If single brain, returns array containing brain data.
            If multiple brains, returns list of arrays.
        '''
        brains = []
        for s in self:
            brains.append(open_zarr((File() & s).get()[0]))
        if len(brains)==1:
            return brains[0] # like fetch1
        return brains
    
    def napari_open(self, **kwargs):
        '''Open brain data in napari viewer.
        
        Opens the brain imaging data in a napari viewer window for visualization.
        Only one brain can be opened at a time.
        
        Pass channel_axis = 1 to open with color
        Returns
        -------
        napari.Viewer
            The napari viewer instance displaying the brain data
            
        Raises
        ------
        AssertionError
            If more than one brain is selected
        '''
        assert len(self) == 1, 'Open only one brain at a time.'
        from labdata.stacks import napari_open
        napari_open(self.get(),**kwargs)


@analysisschema
class FixedBrainTransformParameters(dj.Manual):
    '''Table for storing manual transformation parameters for fixed brain images.
    
    The parameters are used by FixedBrainTransform to generate transformed versions
    of the original brain images for analysis and visualization.

    Definition
    ----------
    transform_id : int
        ID for this set of transform parameters (default 0)
    downsample : array-like
        Downsampling factors for [T,C,X,Y] dimensions
    rotate : array-like  
        [Z,Y,X] rotation angles and [flipx,flipy] boolean flags
    crop : array-like
        Crop ranges [[start,end,step], ...] for each dimension
    transpose : array-like
        Order to transpose dimensions, e.g. [2,1,3,0]
    cast : str
        Data type to cast output to (e.g. 'uint16')
    '''
    definition = '''
    -> FixedBrain
    transform_id = 0 : smallint
    ---
    downsample = NULL : blob       # [T, C, X, Y]
    rotate = NULL     : blob       # [Z, Y, X, flipx, flipy]
    crop = NULL       : blob       # [[START,END,STEP],None,None,None] what to crop 
    transpose = NULL  : blob       # [2,1,3,0]  order to transpose so it is a coronal section
    cast = NULL       : varchar(8) # datatype of the downsampled data
    '''

@analysisschema
class FixedBrainTransform(dj.Computed):
    '''Table for storing transformed fixed brain images.
    
    This class computes and stores transformed versions of fixed brain images based on 
    parameters from FixedBrainTransformParameters. 
 
    The transformed images are stored as TIFF files in the analysis storage location.
    
    Definition
    ----------
    file_path : str
        Path to the transformed TIFF file in analysis storage
    storage : str
        Storage location name (default: 'analysis')
    um_per_pixel : array-like
        Resolution in microns per pixel for each dimension
    shape : array-like 
        Shape of the transformed stack [T,C,X,Y]
    hemisphere : str
        Which hemisphere is included ('left', 'right', or 'both')
        
    Methods
    -------
    transform(key)
        Apply transformations specified in parameters to generate transformed stack
            
        Returns
        -------
        ndarray
            The transformed image stack
        
    get()
        Load and return the transformed image stack(s)
        
        Returns
        -------
        list
            List of transformed image stacks as numpy arrays
    '''
    definition = '''
    -> FixedBrain
    -> FixedBrainTransformParameters
    ---
    -> AnalysisFile
    um_per_pixel = NULL : blob
    shape = NULL        : blob
    hemisphere = NULL   : varchar(5)  # left, right, both
    '''

    def transform(self,key):
        '''Transform fixed brain image according to parameters.
        
        Applies transformations specified in FixedBrainTransformParameters to generate
        a transformed stack. If the transform has already been computed, loads and 
        returns the existing transformed stack from storage.

        Transformation order:
        1. Downsample if specified
        2. Rotate if specified 
        3. Crop if specified
        4. Transpose dimensions if specified

        Parameters
        ----------
        key : dict
            Primary key specifying which FixedBrainTransformParameters to use
            
        Returns
        -------
        ndarray
            The transformed image stack. Shape depends on transformation parameters.
            
        '''
        if len(self & key):
            key = (self & key).fetch1()
            print(f'Transform has been computed. Fetching from {key["file_path"]}.')
            apath = (AnalysisFile() & key).get()[0]

            from tifffile import imread 
            stack = imread(apath)
            return stack
        stack = (FixedBrain() & key).get()
        params = (FixedBrainTransformParameters() & key).fetch1()
        from labdata.stacks import rotate_stack,downsample_stack
        if not params['downsample'] is None:
            stack = downsample_stack(stack,params['downsample'])
        if not params['rotate'] is None:
            stack = rotate_stack(stack,*params['rotate'])
        if not params['crop'] is None:
            A,B,C,D = params['crop']
            if A is None:
                A = [0,stack.shape[0],1]
            if B is None:
                B = [0,stack.shape[1],1]
            if C is None:
                C = [0,stack.shape[2],1]
            if D is None:
                D = [0,stack.shape[3],1]
            stack = stack[A[0]:A[1]:A[2],
                          B[0]:B[1]:B[2],
                          C[0]:C[1]:C[2],
                          D[0]:D[1]:D[2],]
        if not params['transpose'] is None:
            stack = stack.transpose(params['transpose'])
        return stack
    
    def get(self):
        '''Load the transformed brain stacks.
        
        Returns
        -------
        ndarray or list
            If only one stack exists, returns a single ndarray.
            If multiple stacks exist, returns a list of ndarrays.
        '''
        brains = []
        from tifffile import imread
        for s in self:
            brains.append(imread((AnalysisFile() & s).get()[0]))
        if len(brains)==1:
            return brains[0] # like fetch1
        return brains

    def make(self,k):
        par = (FixedBrainTransformParameters() & k).fetch1()
        origpar = (FixedBrain() & k).fetch1()

        downsample_par = np.array(par['downsample'])[np.array([0,2,3])]
        stack = self.transform(k)
        um_per_pixel = list(origpar['um_per_pixel']/downsample_par)

        folder_path = (((Path(prefs['local_paths'][0])
                            /k['subject_name']))
                            /k['session_name'])/f'brain_transform_{k["transform_id"]}'
        filepath = folder_path/f'stack_{um_per_pixel[0]}um.ome.tif'
        folder_path.mkdir(exist_ok=True)
        from tifffile import imwrite  # saving in tiff so it is easier to read
        imwrite(filepath,stack, 
                imagej = True,
                metadata={'axes': 'ZCYX'}, 
                compression ='zlib',
                compressionargs = {'level': 6})
        added = AnalysisFile().upload_files([filepath],dict(subject_name = k['subject_name'],
                                                session_name = k['session_name'],
                                                dataset_name = f'brain_transform_{k["transform_id"]}'))[0]

        to_add = dict(k,
                      um_per_pixel = um_per_pixel,
                      shape = stack.shape,
                      **added)
        self.insert1(to_add)
        # save to tiff and upload to the analysis bucket

@analysisschema
class FixedBrainTransformAnnotation(dj.Manual):
    '''Table for storing manual annotations of brain locations.
    
    This table stores manually annotated points in transformed brain volumes, such as:
    - Probe tracks
    - Injection sites 
    - Anatomical landmarks
    - Region boundaries
    
    Each annotation consists of:
    - annotation_name: Description of what is being annotated
    - annotation_type: Category of annotation (e.g. 'probe_track', 'injection')
    - xyz: Array of x,y,z coordinates marking the annotation location
    
    The coordinates are in pixels relative to the transformed brain volume.
    '''
    definition = '''
    -> FixedBrainTransform
    annotation_id : int
    ---
    annotation_name : varchar(36)
    annotation_type : varchar(36)
    xyz : blob
    '''
    