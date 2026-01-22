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
# FILE: aliases.py
# CREATION DATE: 15-01-2026
# LAST Modified: 0:33:35 17-01-2026
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The alias file to ensure modules used to convert media has names that correspond to their internal references.
# // AR
# +==== END CatFeeder =================+
"""

from typing import Dict
from ..http_constants import DataTypes

# Maps our internal DataTypes to the format strings Pillow expects in Image.save()
PILLOW_FORMAT_ALIASES: Dict[DataTypes, str] = {
    DataTypes.AVIF: "AVIF",
    DataTypes.BMP: "BMP",
    DataTypes.DIB: "BMP",      # DIB is essentially BMP
    DataTypes.GIF: "GIF",
    DataTypes.HEIC: "HEIC",
    DataTypes.HEIF: "HEIF",
    DataTypes.ICO: "ICO",
    DataTypes.XICON: "ICO",    # alias
    DataTypes.JPEG: "JPEG",
    DataTypes.JPE: "JPEG",
    DataTypes.JPG: "JPEG",
    DataTypes.JFIF: "JPEG",
    DataTypes.PNG: "PNG",
    DataTypes.SVG: "SVG",
    DataTypes.TIFF: "TIFF",
    DataTypes.TIF: "TIFF",     # alias
    DataTypes.WEBP: "WEBP",
    DataTypes.GRIB: "GRIB",
    DataTypes.HDR: "HDR",
    DataTypes.ICNS: "ICNS",
    DataTypes.H5: "HDF5",
    DataTypes.HDF: "HDF5",
    DataTypes.JP2: "JPEG2000",
    DataTypes.J2K: "JPEG2000",
    DataTypes.JPC: "JPEG2000",
    DataTypes.JPF: "JPEG2000",
    DataTypes.JPX: "JPEG2000",
    DataTypes.J2C: "JPEG2000",
    DataTypes.IM: "IM",
    DataTypes.IIM: "IIM",
    DataTypes.MPO: "MPO",
    DataTypes.MSP: "MSP",
    DataTypes.PALM: "PALM",
    DataTypes.PCD: "PCD",
    DataTypes.PXR: "PIXAR",
    DataTypes.PBM: "PPM",      # Pillow uses PPM for PBM/PGM/PPM/PNM
    DataTypes.PGM: "PPM",
    DataTypes.PPM: "PPM",
    DataTypes.PNM: "PPM",
    DataTypes.PFM: "PPM",
    DataTypes.PSD: "PSD",
    DataTypes.QOI: "QOI",
    DataTypes.BW: "SGI",
    DataTypes.RGB: "SGI",
    DataTypes.RGBA: "SGI",
    DataTypes.SGI: "SGI",
    DataTypes.RAS: "RAS",
    DataTypes.ICB: "TGA",
    DataTypes.VDA: "TGA",
    DataTypes.VST: "TGA",
    DataTypes.WMF: "WMF",
    DataTypes.EMF: "EMF",
    DataTypes.CUR: "ICO",       # Cursor files
    DataTypes.PCX: "PCX",
    DataTypes.DDS: "DDS",
    DataTypes.EPS: "EPS",
    DataTypes.FIT: "FITS",
    DataTypes.FITS: "FITS",
    DataTypes.FLI: "FLI",
    DataTypes.FLC: "FLC",
    DataTypes.GBR: "GBR",
    DataTypes.APNG: "PNG",      # Pillow treats APNG as PNG internally
    DataTypes.XBM: "XBM",
    DataTypes.XPM: "XPM",
}

ARCHIVE_FORMAT_ALIASES: Dict[DataTypes, str] = {
    DataTypes.ZIP: "zip",
    DataTypes.TAR: "tar",
    DataTypes.TAR_GZ: "tar.gz",
    DataTypes.TAR_BZ2: "tar.bz2",
    DataTypes.TAR_XZ: "tar.xz",
    DataTypes._7Z: "7z",
    DataTypes.DIGIT_7Z: "7z",
    DataTypes.RAR: "rar",
    DataTypes.GZ: "gz",
    DataTypes.BZ2: "bz2",
    DataTypes.XZ: "xz",
}

# Maps our internal DataTypes to document file extensions for Pandoc
DOCUMENT_FORMAT_ALIASES: Dict[DataTypes, str] = {
    # Plain text formats
    DataTypes.TXT: "txt",
    DataTypes.TEXT: "txt",
    DataTypes.PLAIN: "txt",
    DataTypes.MARKDOWN: "md",
    DataTypes.MD: "md",

    # Structured data formats
    DataTypes.JSON: "json",
    DataTypes.YAML: "yaml",
    DataTypes.YML: "yaml",
    DataTypes.TOML: "toml",
    DataTypes.CSV: "csv",
    DataTypes.XML: "xml",

    # Web formats
    DataTypes.HTML: "html",
    DataTypes.XHTML: "xhtml",
    DataTypes.RSS: "rss",
    DataTypes.ATOM: "atom",

    # Document formats
    DataTypes.PDF: "pdf",
    DataTypes.RTF: "rtf",
    DataTypes.DOC: "doc",
    DataTypes.DOCX: "docx",

    # Spreadsheet formats
    DataTypes.XLS: "xls",
    DataTypes.XLSX: "xlsx",
    DataTypes.ODS: "ods",

    # Presentation formats
    DataTypes.PPT: "ppt",
    DataTypes.PPTX: "pptx",
    DataTypes.ODP: "odp",

    # OpenDocument formats
    DataTypes.ODT: "odt",

    # eBook formats
    DataTypes.EPUB: "epub",

    # Calendar formats
    DataTypes.ICS: "ics",

    # Geographic formats
    DataTypes.GEOJSON: "geojson",
}

# Maps our internal DataTypes to audio file extensions for pydub/ffmpeg
AUDIO_FORMAT_ALIASES: Dict[DataTypes, str] = {
    # Common audio formats
    DataTypes.MP3: "mp3",
    DataTypes.WAV: "wav",
    DataTypes.AAC: "aac",
    DataTypes.FLAC: "flac",
    DataTypes.OGG_AUDIO: "ogg",
    DataTypes.OPUS: "opus",
    DataTypes.M4A: "m4a",
    DataTypes.AIFF: "aiff",
    DataTypes.AMR: "amr",
    DataTypes.MID: "mid",
    DataTypes.MIDI: "midi",
}

# Maps our internal DataTypes to video file extensions for ffmpeg
VIDEO_FORMAT_ALIASES: Dict[DataTypes, str] = {
    # Common video formats
    DataTypes.MP4: "mp4",
    DataTypes.WEBM: "webm",
    DataTypes.AVI: "avi",
    DataTypes.MKV: "matroska",
    DataTypes.MOV: "mov",
    DataTypes.FLV: "flv",
    DataTypes.MPEG: "mpeg",
    DataTypes.WMV: "wmv",
    DataTypes.M4v: "m4v",
    DataTypes.OGG_VIDEO: "ogg",
    DataTypes._3GP: "3gp",
    DataTypes.DIGIT_3GP: "3gp",
    DataTypes._3G2: "3g2",
    DataTypes.DIGIT_3G2: "3g2",
    DataTypes._3GPP: "3gp",
    DataTypes.DIGIT_3GPP: "3gp",
    DataTypes._3GPP2: "3g2",
    DataTypes.DIGIT_3GPP2: "3g2",
}
