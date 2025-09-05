# files to process or visualize imaging stacks

from .utils import *

def downsample_stack(stack, ratio = [0.3,1,0.40625,0.40625],n_jobs = DEFAULT_N_JOBS,order = 1):
    '''
    Downsamples a 4D stack using interpolation.

    smaller_stack = downsample_stack(stack, ratio = [0.3,1,0.40625,0.40625],n_jobs = DEFAULT_N_JOBS)
    
    '''
    assert len(stack.shape) == 4, ValueError('Only downsampling 4D stacks is supported.')
    from scipy.ndimage import zoom
    from joblib import Parallel, delayed
    from tqdm import tqdm
    import numpy as np
    assert len(stack.shape) == len(ratio), ValueError(f'Stack ({stack.shape}) and ratio {len(ratio)} need to match')
    a = Parallel(n_jobs = n_jobs)(delayed(zoom)(
        frame,np.array(ratio)[1:],order = order) 
        for frame in tqdm(stack, 
        total = stack.shape[0],desc = 'Downsampling inner dimensions:'))
    na = np.stack(a)
    if na.shape[1] == 1:
        return na
    del a
    na = Parallel(n_jobs = n_jobs)(delayed(zoom)(
        na[:,i],[ratio[0],1,1],order = order) 
        for i in tqdm(range(na.shape[1]), 
        total = stack.shape[1],desc = 'Downsampling outer dimensions:'))
    return np.stack(na).transpose([1,0,2,3])

def rotate_stack(stack, 
                 anglez = 0, 
                 angley = 0, 
                 anglex = 0, 
                 flip_x = False, 
                 flip_y = False, 
                 n_jobs = DEFAULT_N_JOBS,
                 order = 1):
    '''
    Rotate a stack a 4d stack.

    This can be used for instance to rotate a whole brain image. Channels are rotated in paralell, careful with the 
    To get the angles: 
    
    Joao Couto - adapted from deeptrace (2023)
    '''
    from tqdm import tqdm
    na = stack.transpose(1,0,2,3)
    from scipy.ndimage import rotate
    if anglex != 0.0:
        na = Parallel(n_jobs = n_jobs)(delayed(rotate)(
            s, angle = anglex,order = order,axes = [1,2],reshape = False) 
            for s in tqdm(na, total = na.shape[0],desc = 'Rotating the x axis:'))
        na = np.stack(na)
    if angley != 0.0:
        na = Parallel(n_jobs = n_jobs)(delayed(rotate)(
            s, angle = angley,order = order,axes = [0,2],reshape = False) 
            for s in tqdm(na, 
            total = na.shape[0],desc = 'Rotating the y axis:'))
        na = np.stack(na)
    if anglez != 0.0:
        na = Parallel(n_jobs = n_jobs)(delayed(rotate)(
            s, angle = anglez,order = order,axes = [0,1],reshape = False) 
            for s in tqdm(na, 
            total = na.shape[0],desc = 'Rotating the z axis:'))
        na = np.stack(na)
    if flip_x:
        na = na[:,:,:,::-1]
    if flip_y:
        na = na[:,:,::-1,:]
    return na.transpose(1,0,2,3)

def napari_open(stack,**kwargs):
    '''
    Example:

    napari_open(stack.transpose(1,0,2,3),contrast_limits=[0,65000],channel_axis = 1,multiscale=False)

    '''
    import napari
    napari.view_image(stack,**kwargs)

class VideoStack():
    '''
    Class to read video file sequences.
    '''
    def __init__(self,files, use_fast_seek = False):
        self.N = 0
        self.W = None
        self.H = None
        self.files = files
        self.file_offsets = []
        self.current_file = None
        self.current_offset = -1
        self.use_fast_seek = use_fast_seek
        self.cap = None
        self._read_properties()
        self.dtype = np.uint8



    def _read_properties(self):
        self.file_offsets = [0]
        self.N = 0
        self.W = None
        self.H = None
        import cv2
        for f in self.files:
            cap = cv2.VideoCapture(f)
            N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.N += N
            self.file_offsets.append(N)
            if self.W is None:
                self.W  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if self.W != int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)):
                raise(ValueError(f'Video {f} has a different width.'))
            if self.H != int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)):
                raise(ValueError(f'Video {f} has a different height.'))
            cap.release()
        self.shape = (self.N,self.H,self.W)
        self.file_offsets = np.cumsum(self.file_offsets)
    def __len__(self):
        return self.shape[0]
    
    def __getitem__(self, *args):
        index  = args[0]
        idx1 = None
        idx2 = None
        if type(index) is tuple: # then look for 2 channels
            if type(index[1]) is slice:
                idx2 = range(index[1].start, index[1].stop, index[1].step)
            else:
                idx2 = index[1]
            index = index[0]
        if type(index) is slice:
            idx1 = range(*index.indices(self.N))#start, index.stop, index.step)
        elif type(index) in [int,np.int32, np.int64]: # just a frame
            idx1 = [index]
        else: # np.array?
            idx1 = index
        img = np.empty((len(idx1),*self.shape[1:]), dtype = self.dtype)
        # print(img.shape,idx1)
        for i,ind in enumerate(idx1):
            img[i] = self._get_frame(ind)
        if not idx2 is None:
            return img[:,idx2].squeeze()
        else:
            return img[:].squeeze()

    def _open_file(self,ifile):
        if not self.cap is None:
            self.cap.release()
            self.cap = None
        import cv2
        self.cap = cv2.VideoCapture(self.files[ifile])
        self.current_offset = 0
        self.current_file = ifile
        # print(f'Opened file {self.files[ifile]}.')
        
    def _get_frame(self,ind):
        import cv2
        ifile = np.where(self.file_offsets <= ind)[0][-1]
        if not self.current_file == ifile:
            self._open_file(ifile)
        ind = ind - self.file_offsets[self.current_file]
        if ind == 0:
            self._open_file(ifile) # open twice if zero because we may need to reset for sequential access
        if self.use_fast_seek and not self.current_offset == ind:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES,ind)
            ret, frame = self.cap.read()
            self._open_file(ifile)
            return frame[...,0]
        
        while True:
            ret, frame = self.cap.read()
            self.current_offset += 1
            if self.current_offset-1 == ind:
                return frame[...,0]
            elif (self.current_offset-1) > ind: # re-open the file
                self._open_file(ifile)


def export_to_tiff(dat, folder, crop_region = None, plane=None, chunksize = 1024):
    '''
    Export data stack to tiff sequence.
    '''
    from tqdm import tqdm
    from tifffile import imwrite
    chunks = chunk_indices(nframes=dat.shape[0],chunksize=chunksize)
    Path(folder).mkdir(exist_ok=True)
    paths = []
    if not crop_region is None:
        x0,y0,x1,y1 = crop_region
    for i,(o,f) in tqdm(enumerate(chunks),desc='Exporting to tiff',total=len(chunks)):
        x = dat[o:f]
        if not plane is None:
            x = x[:,plane].squeeze()
            paths.append(folder/f'plane_{plane}_chunk_{i:010d}.tiff')
        else:
            paths.append(folder/f'chunk_{i:010d}.tiff')
        if not crop_region is None:
            x = x[:,x0:x1,y0:y1]
        imwrite(paths[-1],x)  
    return paths

def get_roi_contour(roi_mask,percentile_threshold = 80):
    from skimage.measure import find_contours
    # find_contours?
    level = np.percentile(roi_mask[roi_mask>0], percentile_threshold)
    C = find_contours(roi_mask,level = level) # there should be only one contour, this takes the first one
    return C[0]

def get_roi_pixels(roi_mask):
    ii = np.ravel_multi_index(np.where(roi_mask!=0), roi_mask.shape)
    return ii, np.take(roi_mask,ii)

# take a set of binned images, compute the mean, std and local correlation projections
def compute_projections(stack, n_subsample = 2000,kernel_size = 3):
    ''' 
    mean_proj,std_proj,max_proj, corr_proj = compute_projections(stack, n_subsample = 2000,kernel_size = 3)
    
    Computes different projections from a stack of images (a 3d stack)
    
    '''
    A = np.array(stack[:np.min([n_subsample,len(stack)])]).astype('float32')
    mean_proj = np.nanmean(A,axis = 0)
    std_proj = np.nanstd(A,axis = 0)
    max_proj = np.nanmax(A,axis = 0)
    # local correlation
    A -= mean_proj
    A /= std_proj
    
    kern = np.ones((kernel_size,kernel_size),dtype='float32')
    kern[kernel_size//2,kernel_size//2] = 0
    
    from scipy.ndimage import convolve
    A_conv = convolve(A,kern[np.newaxis,:],mode='constant')
    weights = convolve(np.ones(A.shape[1:],dtype='float32'),kern,mode='constant')
    corr_proj =  (np.nanmean(A_conv*A,axis=0)/weights).reshape(A.shape[1:])

    return mean_proj.astype(stack.dtype),std_proj,max_proj.astype(stack.dtype),corr_proj
