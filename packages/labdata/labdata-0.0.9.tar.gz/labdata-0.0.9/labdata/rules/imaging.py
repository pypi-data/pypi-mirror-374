from .utils import *

class FixedBrainRule(UploadRule):
    def __init__(self, job_id, prefs = None):
        super(FixedBrainRule,self).__init__(job_id = job_id, prefs = prefs)
        self.rule_name = 'fixed_brain'
        self.metadata = dict(num_channels = None,
                             um_per_pixel = None,
                             hardware = 'unknown',
                             width = None,
                             height = None)
        self.max_concurrent = 2

    def parse_metadata(self,data):
        '''
        Reads metadata from a MultifolderTiffStack
        '''
        from tifffile import TiffFile
        tf = TiffFile(data.filenames[0][0])
        metadata = tf.ome_metadata
        um_per_pixel = []
        if not metadata is None: # to work with non-OME files 
            for t in metadata.split('\n'):
                if 'Pixels' in t:
                    for p in t.strip('>').split(' '):
                        if 'PhysicalSize' in p:
                            um_per_pixel.append(float(p.split('=')[1].split('"')[1]))
            self.metadata['um_per_pixel'] = um_per_pixel[::-1]
        
            if 'UltraII' in metadata:
                self.metadata['hardware'] = 'lightsheet UltraII'
        
        self.metadata['num_channels'] = len(data.filenames)
        self.metadata['height'] = data.shape[-2]
        self.metadata['width'] = data.shape[-1]

    def _apply_rule(self):
        extensions = ['.ome.tif','.tif','.TIFF','.TIF']
        for extension in extensions:
            files_to_compress = list(filter(lambda x: (extension in x),
                                            self.src_paths.src_path.values))
            if len(files_to_compress):
                break # found files
        local_path = self.prefs['local_paths'][0]
        local_path = Path(local_path)
        
        new_files = []
        full_file_paths = [local_path/f for f in files_to_compress]
        channel_folders = np.sort(np.unique([p.parent for p in full_file_paths]))
        print(f'Found folders: {channel_folders}')
        data = MultifolderTiffStack(channel_folders = channel_folders,
                                    extensions = extensions)
        compressed_file = channel_folders[0].parent.with_suffix('.zarr.zip')
        # read the first file and get metadata
        self.parse_metadata(data)
        # compression to zarr.zip
        self.set_job_status(job_status = 'WORKING',
                            job_log = datetime.now().strftime('Compressing data %Y %m %d %H:%M:%S'),
                            job_waiting = 0)
        z1 = compress_imaging_stack(data,
                                    compressed_file,
                                    chunksize = 4,
                                    compression = 'zstd',
                                    clevel = 6,
                                    shuffle = 1,
                                    filters = [])
        new_files.append(str(compressed_file).replace(str(local_path),'').strip(pathlib.os.sep))
        if len(new_files):
            self._handle_processed_and_src_paths(files_to_compress, new_files)
        return self.src_paths
    # need to implement post-upload for lightsheet.
    def _post_upload(self):
        if not self.dataset_key is None:
            from ..schema import FixedBrain
            if len(self.inserted_files) > 0:
                storage = self.inserted_files[0]['storage']
                filenames = [f['file_path'] for f in self.inserted_files if f['file_path'].endswith('.zarr.zip')]
                if not len(filenames):
                    print('Could not find zarr compressed stack.')
                FixedBrain().insert1(dict(self.dataset_key,
                                         file_path = filenames[0],
                                         storage = storage,
                                         **self.metadata),allow_direct_insert=True)
                

class OnePhotonRule(UploadRule):
    def __init__(self, job_id, prefs = None):
        super(OnePhotonRule,self).__init__(job_id = job_id, prefs = prefs)
        self.rule_name = 'one_photon'
        self.imaging_metadata = None
        self.max_concurrent = 2    

    def _apply_rule(self):
        files_to_compress = list(filter(lambda x: ('.dat' in x),
                                        self.src_paths.src_path.values))
        # TODO: make this work for tiff files also
        local_path = self.prefs['local_paths'][0]
        local_path = Path(local_path)
        if len(files_to_compress):
            if len(files_to_compress)>1:
                raise(ValueError(f'Can only handle one file {files_to_compress}'))
            new_files = []
            for f in files_to_compress:
                filename = local_path/f
                data = mmap_wfield_binary(filename)
                compressed_file = filename.with_suffix('.zarr.zip')
                # compression to zarr.zip
                self.set_job_status(job_status = 'WORKING',
                                    job_log = datetime.now().strftime('Compressing data %Y %m %d %H:%M:%S'),
                                    job_waiting = 0)
                z1 = compress_imaging_stack(data,
                                            compressed_file,
                                            chunksize = 16,
                                            compression = 'zstd',
                                            clevel = 6,
                                            shuffle = 1,
                                            filters = [])
                # pass the file path without the "local_path"!
                new_files.append(str(compressed_file).replace(str(local_path),'').strip(pathlib.os.sep))
            if len(new_files):
                self._handle_processed_and_src_paths(files_to_compress, new_files)
        return self.src_paths
    # need to implement post-upload for widefield imaging.
    def _post_upload(self):
        if not self.dataset_key is None:
            insert_widefield_dataset(self.dataset_key,local_paths=[self.local_path])
        

class TwoPhotonRule(UploadRule):
    def __init__(self, job_id,prefs = None):
        super(TwoPhotonRule,self).__init__(job_id = job_id, prefs = prefs)
        self.rule_name = 'two_photon'
        self.recording_metadata = None
        self.planes_metadata = []
        self.max_concurrent = 2    

    def _apply_rule(self):
        # compress ap files or lf files.
        files_to_compress = list(filter(lambda x: ('.sbx' in x),
                                        self.src_paths.src_path.values))
        if not len(files_to_compress):
            print('There are no sbx files.')
            files_to_compress = list(filter(lambda x: ('.tif' in x),
                                        self.src_paths.src_path.values))
            if len(files_to_compress):
                raise(ValueError('Tiff processing not implemented for this rule.'))
        # TODO: make this work for tiff files also
        local_path = self.prefs['local_paths'][0]
        local_path = Path(local_path)

        if len(files_to_compress):
            if len(files_to_compress)>1:
                raise(ValueError(f'Can only handle one file {files_to_compress}'))
            new_files = []
            for f in files_to_compress:
                compressed_file = self.process_sbx(local_path/f)
                # pass the file path without the "local_path"!
                new_files.append(str(compressed_file).replace(str(local_path),'').strip(pathlib.os.sep))
            if len(new_files):
                self._handle_processed_and_src_paths(files_to_compress, new_files)
        return self.src_paths

    def process_sbx(self,sbxfile):
        try:
            from sbxreader import sbx_memmap
        except:
            msg = f'Could not import SBXREADER: "pip install sbxreader" on {pref["hostname"]}'
            print(msg)
            self.set_job_status(job_status = 'FAILED',job_log = msg,job_waiting = 0)
        sbx = sbx_memmap(sbxfile)
        compressed_file = sbxfile.with_suffix('.zarr.zip')
        z1 = compress_imaging_stack(sbx,
                                    compressed_file,
                                    chunksize = 128,
                                    compression = 'zstd',#'blosc2',
                                    clevel = 6,
                                    shuffle = 1)
        nframes,nplanes,nchannels,H,W = z1.shape

        pmt_gain = [sbx.metadata['pmt0_gain']]
        if nchannels>1:
            pmt_gain+= [sbx.metadata['pmt1_gain']],

        self.recording_metadata = dict(n_planes = nplanes,
                                       n_channels = nchannels,
                                       n_frames = nframes,
                                       width = W,
                                       height = H,
                                       magnification = sbx.metadata['magnification'],
                                       objective_angle = sbx.metadata['stage_angle'],
                                       objective = sbx.metadata['objective'],
                                       um_per_pixel = np.array([sbx.metadata['um_per_pixel_x'],
                                                                sbx.metadata['um_per_pixel_y']]),
                                       frame_rate = sbx.metadata['frame_rate']/nchannels,
                                       scanning_mode = sbx.metadata['scanning_mode'],
                                       pmt_gain = np.array(pmt_gain),
                                       imaging_software = f"scanbox_{sbx.metadata['scanbox_version']}")
        for iplane in range(nplanes):
            depth = sbx.metadata['stage_pos'][-1]
            if nplanes > 1:
                depth += sbx.metadata['etl_pos'][iplane] - sbx.metadata['etl_pos'][0]
                
            self.planes_metadata.append(dict(plane_num = iplane,
                                             plane_depth = depth))
        return compressed_file

    def _post_upload(self):
        if not self.dataset_key is None:
            from ..schema import TwoPhoton
            if len(self.inserted_files) > 0:
                storage = self.inserted_files[0]['storage']
                filenames = [f['file_path'] for f in self.inserted_files if f['file_path'].endswith('.zarr.zip')]
                if not len(filenames):
                    print('Could not find zarr compressed stack.')
                TwoPhoton().insert1(dict(self.dataset_key,
                                         file_path = filenames[0],
                                         storage = storage,
                                         **self.recording_metadata),allow_direct_insert=True)
                TwoPhoton.Plane().insert([dict(self.dataset_key,**d) for d in self.planes_metadata],allow_direct_insert=True)
                

class MiniscopeRule(UploadRule):
    def __init__(self, job_id, prefs = None):
        super(MiniscopeRule,self).__init__(job_id = job_id, prefs = prefs)
        self.rule_name = 'miniscope'
        self.imaging_metadata = None
        self.max_concurrent = 4    

    def _apply_rule(self):
        from natsort import natsorted
        files_to_compress = natsorted([str(s) for s in list(filter(lambda x: ('.avi' in x),
                                                         self.src_paths.src_path.values))])
        local_path = self.prefs['local_paths'][0]
        local_path = Path(local_path)

        new_files = []
        files_to_process = [local_path/f for f in files_to_compress]
        # open the video stack
        from ..stacks import VideoStack
        data = VideoStack(files_to_process)  # this does not support multiple channels at the moment.
        compressed_file = (Path(files_to_process[0]).parent/'miniscope_stack').with_suffix('.zarr.zip')
        self.set_job_status(job_status = 'WORKING',
                            job_log = datetime.now().strftime('Compressing data %Y %m %d %H:%M:%S'),
                            job_waiting = 0)
        z1 = compress_imaging_stack(data,
                                    compressed_file,
                                    chunksize = 512,
                                    compression = 'zstd',
                                    clevel = 6,
                                    shuffle = 1,
                                    filters = [])
        new_files.append(str(compressed_file).replace(str(local_path),'').strip(pathlib.os.sep))
        if len(new_files):
            self._handle_processed_and_src_paths(files_to_compress, new_files)
        return self.src_paths

    def _post_upload(self):
        if not self.dataset_key is None:
            insert_miniscope_dataset(self.dataset_key, local_paths = [self.local_path])
            
############################################################################################################
############################################################################################################

def insert_miniscope_dataset(key, local_paths = None, skip_duplicates = False):

    from labdata.schema import Dataset, DatasetEvents, Miniscope, File
    if len(Miniscope & key):
        from warnings import warn
        warn(f'Dataset {key} was already inserted.')
        return
    
    filedict = (File & (Dataset.DataFiles & key) & 'file_path LIKE "%.zarr.zip"').proj().fetch1()
    datafile = (File & (Dataset.DataFiles & key) & 'file_path LIKE "%.zarr.zip"').get(local_paths = local_paths)[0]

    from ..utils import open_zarr
    dat = open_zarr(datafile)


    metafile = (File & (Dataset.DataFiles & key) & 'file_path LIKE "%metaData.json"').get(local_paths = local_paths)[0]
    tsfile = (File & (Dataset.DataFiles & key) & 'file_path LIKE "%timeStamps.csv"').get(local_paths = local_paths)[0]
    orifile = (File & (Dataset.DataFiles & key) & 'file_path LIKE "%headOrientation.csv"').get(local_paths = local_paths)
    # read the metadata
    with open(metafile,'r') as d:
        metadata = json.load(d)

    frame_rate = metadata['frameRate']
    if type(frame_rate) is str: # the frame rate changed in different versions
        frame_rate = float(metadata['frameRate'].strip('FPS'))
    gain = metadata['gain'] # the gain changed in differnet versions..
    if type(gain) is str:
        if gain == 'Low':
            gain = 1
        elif gain == 'High':
            gain = 10
        else:
            gain = None
            print('Could not read gain')
    leds = [k for k in metadata.keys() if 'led' in k]
    miniscope_dict = dict(key,
                          n_channels = len(leds),
                          n_frames = dat.shape[0],
                          width = dat.shape[1],
                          height = dat.shape[2], 
                          device = metadata['deviceType'],
                          frame_rate = float(frame_rate),
                          sensor_gain = gain,
                          power = [metadata[k] for k in leds],
                          lens_tuning = metadata['ewl'],
                          **filedict)
    # read the timestamps
    timestamps = pd.read_csv(tsfile)
    del dat

    dataseteventsdict = [dict((Dataset.proj() & key).fetch1(),
                            stream_name = 'miniscope')]
    dataseteventsstreams = [dict(dataseteventsdict[0],
                                 event_name = 'clock',
                                 event_timestamps = timestamps['Time Stamp (ms)'].values/1000.,
                                 event_values = timestamps['Frame Number'].values)]
    if len(orifile):
        head = pd.read_csv(orifile[0])
        for k in ['qw','qx','qy','qz']:
            dataseteventsstreams.append(dict(dataseteventsdict[0],
                                         event_name = k,
                                         event_timestamps = head['Time Stamp (ms)'].values/1000.,
                                         event_values = head[k].values))
        

    DatasetEvents.insert(dataseteventsdict, allow_direct_insert=True, skip_duplicates=skip_duplicates)
    DatasetEvents.Digital.insert(dataseteventsstreams, allow_direct_insert=True, skip_duplicates=skip_duplicates)
    Miniscope.insert1(miniscope_dict, allow_direct_insert=True, skip_duplicates = skip_duplicates)
    return 

    
def compress_imaging_stack(stack, filename, 
                           chunksize = 256,
                           compression = 'blosc2',
                           clevel = 6,
                           shuffle = 1,
                           filters = [],
                           zarr_format = 2,
                           scratch_path = None,
                           check_dataset = True):
    '''
    stack is in shape [nframes,nchan,H,W]
    
    Typical use case for two photon datasets:
          - blosc2 compression clevel 6, shuffle 1, no filters
         this will take ~10min/25Gb and the result is a file 77% of the original file.
    Typical use case for one photon datasets:
          - blosc2 compression clevel 6, shuffle 1, no filters
    Typical use for lightsheet imaging:
          - blosc2 compression clevel 6, shuffle 1, no filters
    
    TODO: implement a way of changing the chunksize of the inner dimensions..
    TODO: implement a way to skip the zip
    
    '''

    import zarr
    import string
    from tqdm import tqdm
    from zipfile import ZipFile
    from pathlib import Path
    import numcodecs
    filt = []
    if 'delta' in filters:
        from numcodecs import Delta
        #raise NotImplementedError('Filters are not implemented because of incompatibility issues with zarr v3.')
        filt += [Delta(dtype=stack.dtype)]
    if compression in ['zstd','lz4hc','lz4']:
        if zarr_format == 3:
            compressor = zarr.codecs.BloscCodec(cname = compression, clevel = clevel, shuffle = 'shuffle')
        else: # zarr v2 is smaller and faster at least Feb 2025..
            from numcodecs import Blosc
            zarr_format = 2
            compressor = Blosc(cname = compression, clevel = clevel, shuffle = shuffle)
    elif compression == 'blosc2':
        from imagecodecs.numcodecs import Blosc2
        numcodecs.register_codec(Blosc2)
        compressor = Blosc2(level=clevel, shuffle = shuffle)
        zarr_format = 2
    else:
        raise NotImplementedError(f'Compression {compression} not implemented')

    if scratch_path is None:
        if 'scratch_path' in prefs:
            scratch_path = Path(prefs['scratch_path'])
        if scratch_path is None:
            scratch_path = Path('.')
    
    rand = ''.join(np.random.choice([s for s in string.ascii_lowercase + string.digits],9))
    tmppath = Path(scratch_path/f'temporary_zarr_{rand}.zarr')
    if len(stack.shape) == 4:
        chunks = (chunksize, 1,*stack.shape[-2:])
    elif len(stack.shape) == 3:
        chunks = (chunksize, *stack.shape[-2:])
    elif len(stack.shape) == 5:
        chunks = (chunksize,1, 1,*stack.shape[-2:])        
    else:
        raise(ValueError(f'Only 3d, 4d or 5d stacks are supported. Stack: {stack.shape}.'))
    if zarr_format == 2:
        z1 = zarr.open(tmppath, mode='w', shape = stack.shape,
        chunks = chunks, dtype = stack.dtype, 
        compressor = compressor, filters = filt, zarr_format = 2)
    elif zarr_format == 3:
        z1 = zarr.create_array(store=tmppath, 
        shape=stack.shape, dtype=stack.dtype, chunks=chunks, compressors=compressor)
    else:
        raise NotImplementedError(f'The array format {zarr_format} is not implemented.')
    for s in tqdm(chunk_indices(len(stack),chunksize),
                  desc = 'Compressing to zarr:'):
        z1[s[0]:s[1]] = np.array(stack[s[0]:s[1]])
    with ZipFile(filename,'w') as z:
        tmp = list(tmppath.rglob('*'))
        tmp = list(filter(lambda x: x.is_file(),tmp)) # for compat with zarr3
        [z.write(t,arcname=t.relative_to(tmppath)) for t in tqdm(
            tmp,
            desc='Saving to zip:')]
    # delete the temporary
    from shutil import rmtree
    rmtree(tmppath)
    # open the new array
    z1 = open_zarr(filename,mode = 'r')
    if check_dataset:
        # check the new array
        for s in tqdm(chunk_indices(len(stack),chunksize),desc = 'Checking data:'):
            if not np.all(z1[s[0]:s[1]] == np.array(stack[s[0]:s[1]])):
                raise(ValueError(f"Datasets are not equivalent, compression failed {filename}. "))
    return z1

def _parse_wfield_fname(fname,lastidx=None, dtype = 'uint16', shape = None, sep = '_'):
    '''
    Gets the data type and the shape from the filename 
    This is a helper function to use in load_dat.
    
    out = _parse_wfield_fname(fname)
    
    With out default to: 
        out = dict(dtype=dtype, shape = shape, fnum = None)

    this is from wfield - jcouto
    '''
    fn = os.path.splitext(os.path.basename(str(fname)))[0]
    fnsplit = fn.split(sep)
    fnum = None
    if lastidx is None:
        # find the datatype first (that is the first dtype string from last)
        lastidx = -1
        idx = np.where([not f.isnumeric() for f in fnsplit])[0]
        for i in idx[::-1]:
            try:
                dtype = np.dtype(fnsplit[i])
                lastidx = i
            except TypeError:
                pass
    if dtype is None:
        dtype = np.dtype(fnsplit[lastidx])
    # further split in those before and after lastidx
    before = [f for f in fnsplit[:lastidx] if f.isdigit()]
    after = [f for f in fnsplit[lastidx:] if f.isdigit()]
    if shape is None:
        # then the shape are the last 3
        shape = [int(t) for t in before[-3:]]
    if len(after)>0:
        fnum = [int(t) for t in after]
    return dtype,shape,fnum


def mmap_wfield_binary(filename,
                       mode = 'r',
                       nframes = None,
                       shape = None,
                       dtype='uint16'):
    '''
    Loads frames from a binary file as a memory map.
    This is useful when the data does not fit to memory.
    
    Inputs:
        filename (str)       : fileformat convention, file ends in _NCHANNELS_H_W_DTYPE.dat
        mode (str)           : memory map access mode (default 'r')
                'r'   | Open existing file for reading only.
                'r+'  | Open existing file for reading and writing.                 
        nframes (int)        : number of frames to read (default is None: the entire file)
        offset (int)         : offset frame number (default 0)
        shape (list|tuple)   : dimensions (NCHANNELS, HEIGHT, WIDTH) default is None
        dtype (str)          : datatype (default uint16) 
    Returns:
        A memory mapped  array with size (NFRAMES,NCHANNELS, HEIGHT, WIDTH).

    Example:
        dat = mmap_dat(filename)

    This is from wfield - jcouto
    '''
    
    if not os.path.isfile(filename):
        raise OSError('File {0} not found.'.format(filename))
    if shape is None or dtype is None: # try to get it from the filename
        dtype,shape,_ = _parse_wfield_fname(filename,
                                            shape = shape,
                                            dtype = dtype)
    if type(dtype) is str:
        dt = np.dtype(dtype)
    else:
        dt = dtype
    if nframes is None:
        # Get the number of samples from the file size
        nframes = int(os.path.getsize(filename)/(np.prod(shape)*dt.itemsize))
    dt = np.dtype(dtype)
    return np.memmap(filename,
                     mode=mode,
                     dtype=dt,
                     shape = (int(nframes),*shape))


class MultifolderTiffStack(object):
    def __init__(self,channel_folders, extensions = ['.ome.tif','.tif','.TIFF']):
        '''
        Simple class to access tiff files that are organized in a folders
        Each folder is a channel and contains multiple TIFF files.
        
        This is the format of the lightsheet microscope for example. 
        It is a place-holder class that should be modified to work for scanimage files also.
        '''
        self.nchannels = len(channel_folders)
        self.filenames = []
        for folder in channel_folders:
            for extension in extensions:
                tiffs = list(Path(folder).rglob('*' + extension))
                if len(tiffs) > 0:
                    self.filenames.append(natsorted(tiffs))
                    break # found extension
        # read the first file
        im = read_ome_tif(self.filenames[0][0])
        if len(im.shape) == 2:
            # then the number frames is the number of tiff files
            self.nframes = len(self.filenames[0])
            self.frame_dims = im.shape
            self.dtype = im.dtype
        else:
            raise NotImplementedError('This needs to be changed to work with multiple-frame TIFF files.')
        self.shape = (self.nframes,self.nchannels,*self.frame_dims)
    def __len__(self):
        return self.nframes
    
    def __getitem__(self,*args):
        index = args[0]
        if type(index) is slice:
            idx1 = range(*index.indices(self.nframes))
        elif type(index) in [int,np.int32, np.int64]: # just one frame
            idx1 = [index]
        else: # np.array?
            idx1 = index
        img = []
        for i in idx1:
            img.append(self.get(i))
        return np.stack(img).squeeze().reshape(len(img),self.nchannels, *self.frame_dims)
    
    def get(self,idx):
        return np.stack([read_ome_tif(files[idx]) for files in self.filenames])


def read_ome_tif(file):
    from tifffile import TiffFile
    try:
        res = TiffFile(file).pages.get(0).asarray()
    except Exception as err:
        print(f'TIFF error for {file}')
        print(err) # raise the exception again
        raise(OSError(f'TIFF error for {file}'))
    return res

def insert_widefield_dataset(key, local_paths = None, skip_duplicates = False):
    '''
    Insert widefield dataset keys (assumes data were collected with labcams but there can be adapted to support other formats.)
    ask jpcouto@gmail.com
    '''
    from labdata.schema import Dataset, DatasetEvents, Widefield, File
    if len(Widefield & key):
        from warnings import warn
        warn(f'Dataset {key} was already inserted.')
        return
    
    filedict = (File & (Dataset.DataFiles & key) & 'file_path LIKE "%.zarr.zip"').proj().fetch1()
    datafile = (File & (Dataset.DataFiles & key) & 'file_path LIKE "%.zarr.zip"').get(local_paths = local_paths)[0]
    camlogfile = (File & (Dataset.DataFiles & key) & 'file_path LIKE "%.camlog"').get(local_paths = local_paths)[0]
    
    from ..utils import open_zarr
    dat = open_zarr(datafile)
    
    dataseteventsdict = None
    software = 'unknown'
    try:
        from ..schema.utils import read_camlog
        comm,log = read_camlog(camlogfile)
        led = [c.split('LED:')[-1] for c in comm if c.startswith('#LED')] 
        if len(led):
            from io import StringIO
            led = pd.read_csv(StringIO('\n'.join(led)),delimiter = ',',header = None,names= ['channel','frame_id','timestamp'])
            frame_rate = np.nanmean(1000./np.diff(led.timestamp.values[::dat.shape[1]]))
            dataseteventsdict = [dict((Dataset.proj() & key).fetch1(),
                                  stream_name = 'widefield')]
            dataseteventsstreams = [dict(dataseteventsdict[0],event_name = u,
                                     event_timestamps = led[led.channel.values == u].timestamp.values,
                                     event_values = led[led.channel.values == u].frame_id.values) for u in np.unique(led.channel.values)]
        else:
            print('There was no LED in the log, trying to get the frame rate from the camera log.')
            frame_rate = np.nanmean(1./np.diff(log[1].values))

        software = 'labcams'
        lv = [l.split(':')[-1].strip(' ') for l in comm if 'labcams version' in l]
        if len(lv):
            software += ' '+lv[0]
        
    except Exception as err:
        from warnings import warn
        warn('Could not parse the frame rate.')
        print(err)
        frame_rate = -1
    widefielddict = dict((Dataset.proj() & key).fetch1(),
                         n_channels = dat.shape[1],
                         n_frames = dat.shape[0],
                         height = dat.shape[2],
                         width = dat.shape[3],
                         frame_rate = frame_rate,
                         imaging_software = software,
                         **filedict)
    del dat
    if not dataseteventsdict is None:
        DatasetEvents.insert(dataseteventsdict, allow_direct_insert=True, skip_duplicates=skip_duplicates)
        DatasetEvents.Digital.insert(dataseteventsstreams, allow_direct_insert=True, skip_duplicates=skip_duplicates)
    Widefield.insert1(widefielddict, allow_direct_insert=True, skip_duplicates = skip_duplicates)
    return
