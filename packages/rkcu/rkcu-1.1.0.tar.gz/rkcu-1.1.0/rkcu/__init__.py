"""
RKCU - Royal Kludge Config Utility

A Python utility for managing profiles and per-key RGB lighting 
on Royal Kludge keyboards.

Author: Hardik Srivastava [oddlyspaced]
"""

__version__ = "1.1.0"
__author__ = "Hardik Srivastava"
__maintainer__ = "gagan16k"

# Import main classes and functions that users might want to use directly
from .utils import RKCU
from .config import Config, get_base_config
from .per_key_rgb import PerKeyRGB
from .enums import Animation, Speed, Brightness, RainbowMode, Sleep

# Define what gets imported with "from rkcu import *"
__all__ = [
    'RKCU',
    'Config', 
    'get_base_config',
    'PerKeyRGB',
    'Animation',
    'Speed', 
    'Brightness',
    'RainbowMode',
    'Sleep',
]