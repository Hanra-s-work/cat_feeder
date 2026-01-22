""" 
# +==== BEGIN CatFeeder =================+
# LOGO: 
# ..............(..../\\
# ...............)..(.')
# ..............(../..)
# ...............\\(__)|
# Inspired by Joan Stark
# source https://www.asciiart.eu/
# animals/cats
# /STOP
# PROJECT: CatFeeder
# FILE: __init__.py
# CREATION DATE: 05-01-2026
# LAST Modified: 23:52:8 08-01-2026
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the module that is in charge of reducing the size of an image before it is stored in order to save bandwidth.
# // AR
# +==== END CatFeeder =================+
"""

from .image_reducer import ImageReducer
from .image_reducer_constants import COMPRESSION_QUALITY, FileFormat
from . import image_reducer_error_class as IR_ERROR

__all__ = [
    "FileFormat",
    "ImageReducer",
    "COMPRESSION_QUALITY",
    "IR_ERROR"
]
