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
# CREATION DATE: 15-01-2026
# LAST Modified: 6:14:27 15-01-2026
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The folder used to contain the code for the different format scenarios to be used for conversion.
# // AR
# +==== END CatFeeder =================+
"""

from .aliases import PILLOW_FORMAT_ALIASES
from .font_to_font import FontToFont
from .bytes_to_base import BytesToBase
from .video_to_video import VideoToVideo
from .audio_to_audio import AudioToAudio
from .archive_to_archive import ArchiveToArchive
from .image_to_image import ImageToImage
from .document_to_document import DocumentToDocument
from . import converters_constants as CONV_CONST

__all__ = [
    "PILLOW_FORMAT_ALIASES",
    "CONV_CONST",
    "FontToFont",
    "BytesToBase",
    "VideoToVideo",
    "AudioToAudio",
    "ImageToImage",
    "ArchiveToArchive",
    "DocumentToDocument",
]
