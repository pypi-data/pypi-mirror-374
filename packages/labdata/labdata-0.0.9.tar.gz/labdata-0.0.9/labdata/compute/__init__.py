'''Compute tasks for lab data processing and analysis.

This module provides compute task classes for running analyses on lab data.
Tasks can be scheduled and run on dedicated containers using job schedulers.

Available compute tasks:
- SpksCompute: Spike sorting using Kilosort/Phy via SPKS
- DeeplabcutCompute: Animal pose estimation using DeepLabCut

Each compute task can be:
- Scheduled to run on compute clusters via SLURM/PBS
- Executed in isolated Singularity/Docker containers
- Tracked and monitored through the database
- Configured via user preferences

The compute tasks handle:
- Input/output file management
- Container and environment setup
- Job scheduling and resource allocation
- Progress tracking and error handling
- Result storage and validation
'''

from .utils import *
from .singularity import build_singularity_container
from .ephys import SpksCompute
from .pose import DeeplabcutCompute
from .caiman import CaimanCompute
from .suite2p import Suite2pCompute