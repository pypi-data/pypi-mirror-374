'''Schema for lab data management.

This package provides DataJoint schemas (tables) for accessing and managing laboratory data.
The schemas are organized into modules by data type:

- `general`     - Core tables for files, subjects, sessions, datasets
- `procedures`  - Tables for experimental procedures and protocols
- `ephys`       - Tables for electrophysiology recordings and analysis
- `twophoton`   - Tables for two-photon microscopy data
- `onephoton`   - Tables for one-photon imaging (widefield and miniscope)
- `tasks`       - Tables for behavioral task data
- `video`       - Tables for video recordings
- `histology`   - Tables for histology and anatomy data
'''

from .general import *
from .procedures import *
from .ephys import *
from .twophoton import * 
from .onephoton import *  # includes widefield and miniscope
from .tasks import *
from .video import *
from .histology import *

