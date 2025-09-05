from .general import *
from .procedures import *
from .histology import *

@dataschema
class Widefield(dj.Imported):
    '''Table for widefield one-photon imaging data.
    
    This table stores metadata about widefield imaging recordings including:
    - Frame dimensions and counts
    - Frame rate
    - Optical parameters (magnification, objective, pixel scale)
    - Reference to raw data file
    - Imaging software details
    
    The table includes a Part table for storing different projections of the data
    (mean, std, var, max).
    '''
    definition = '''
    -> Dataset
    ---
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
    imaging_software       : varchar(32)         # software and version
    '''
    
    def open(self):
        '''Opens the widefield imaging data file.
        
        Returns
        -------
        zarr.Array
            The opened zarr array containing the widefield imaging data.
            Data is stored in a compressed zarr format with dimensions:
            [frames, channels, height, width]
        '''
        if len(self) != 1:
            raise(ValueError(f'Select only one dataset {self.proj().fetch(as_dict = True)}.'))
        fname = (File() & (Widefield & self.proj()) & 'file_path LIKE "%.zarr.zip"').get()[0]
        return open_zarr(fname)

    class Projection(dj.Part):
        '''Part table for storing projections of widefield imaging data.
        
        This table stores projections (mean, std, var, max) of the 
        widefield imaging data.
        
        Attributes
        ----------
        proj_name : enum
            Type of projection ('mean', 'std', 'var', 'max')
        proj : longblob
            The projection data array
        '''
        definition = '''
        -> master
        proj_name           : enum('mean','std','var','max')                  
        ---
        proj      : longblob
    '''
        
@dataschema
class Miniscope(dj.Imported):
    definition = '''
    -> Dataset
    ---
    n_channels             : smallint            # number of channels
    n_frames               : int                 # duration of the recording
    width                  : int                 # width of each frame
    height                 : int                 # height of each frame
    frame_rate             : double              # frame rate
    -> File                                      # path to the stack
    device = NULL          : varchar(32)         # miniscope device
    power = NULL           : blob                # power used per channel
    lens_tuning            : int                 # EWL tuning (focus)
    sensor_gain = NULL     : int                 # gain of the imaging sensor
    um_per_pixel = NULL    : blob                # XY scale conversion factors
    -> [nullable] Atlas.Region                   # target region (or the center of the imaging plane)
    '''
    def open(self):
        if len(self) != 1:
            raise(ValueError(f'Select only one dataset {self.proj().fetch(as_dict = True)}.'))
        fname = (File() & self).get()[0]
        return open_zarr(fname)
    