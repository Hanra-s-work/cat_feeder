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
# FILE: image_reducer_constants.py
# CREATION DATE: 05-01-2026
# LAST Modified: 0:48:0 08-01-2026
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file in charge of containing the constants that will be used in the class.
# // AR
# +==== END CatFeeder =================+
"""

from typing import List, Dict
from enum import Enum

DEFAULT_OUTPUT_FORMAT: str = "PNG"
ALLOWED_FORMATS: List[str] = [
    "PNG",
    "JPEG",
    "WEBP",
    "SVG",
    "GIF",
    "BMP",
    "TIFF",
    "ICO",
    "AVIF"
]
ALLOWED_OUTPUT_FORMATS: List[str] = ["WEBP", "JPEG", "JPG", "PNG"]

COMPRESSION_QUALITY: Dict[str, int] = {
    "webp": 85,      # Quality 0-100, perceptually lossless at 1080p
    "png": 9,        # Compression level 0-9 (lossless)
    "jpeg": 90,      # Quality 0-100, invisible quality loss at 1080p
    "jpg": 90,       # Quality 0-100, invisible quality loss at 1080p
    "gif": 1,        # Optimize flag (lossless)
    "bmp": 0,        # No compression (lossless, larger file)
    "tiff": 0,       # No compression (lossless, larger file)
    "ico": 0,        # No compression (lossless, smaller images)
    "avif": 70,      # Quality 0-100, perceptually lossless at 1080p
}


class FileFormat(Enum):
    """Enumeration of supported image file formats.

    Includes both raster and vector image formats that can be processed
    by the ImageReducer. Supports common web-friendly formats as well as
    traditional image formats.
    """
    # Vector formats
    SVG = "svg"

    # Raster formats - Modern/Web-optimized
    WEBP = "webp"
    AVIF = "avif"

    # Raster formats - Traditional/Widely supported
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    GIF = "gif"

    # Raster formats - Legacy/Specialized
    BMP = "bmp"
    TIFF = "tiff"
    ICO = "ico"

    # Unknown/Unsupported format
    UNKNOWN = "unknown"
