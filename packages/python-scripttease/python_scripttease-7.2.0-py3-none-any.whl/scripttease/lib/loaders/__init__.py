"""
The job of a loader is to collect commands and their arguments from a text file.
"""
from .base import load_variables
from .ini import INILoader
from .yaml import YMLLoader
