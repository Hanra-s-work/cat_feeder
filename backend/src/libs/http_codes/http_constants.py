r"""
# +==== BEGIN CatFeeder =================+
# LOGO:
# ..............(..../\
# ...............)..(.')
# ..............(../..)
# ...............\(__)|
# Inspired by Joan Stark
# source https://www.asciiart.eu/
# animals/cats
# /STOP
# PROJECT: CatFeeder
# FILE: http_constants.py
# CREATION DATE: 19-11-2025
# LAST Modified: 22:21:27 23-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE:
# File containing the constants that are used by the http codes class.
# Central definitions for HTTP-related constants:
# - Known status codes
# - Known MIME types (DATA_TYPES)
# - DataTypes Enum (auto-mapped from DATA_TYPES and sorted)
# - Grouped categories: FILE_TYPES, HTML_TYPES, JSON_TYPES, PLAIN_TEXT_TYPES, etc.
# - Redirect type added ("redirect")
#
# This file is designed to be:
# - Alphabetically sorted
# - Fully deduplicated
# - Easy to maintain
# /STOP
# // AR
# +==== END CatFeeder =================+
"""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, ClassVar, Optional, Set


# ============================================================
# HTTP STATUS CODES (Authorised)
# ============================================================

AUTHORISED_STATUSES: List[int] = [
    # 1xx - Informational
    100, 101, 102, 103, 110,
    # 2xx - Successful
    200, 201, 202, 203, 204, 205, 206, 207, 208, 226,
    # 3xx - Redirection
    300, 301, 302, 303, 304, 305, 306, 307, 308,
    # 4xx - Client error
    400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411,
    412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423,
    424, 425, 426, 428, 429, 430, 431, 451, 498,
    # 5xx - Server error
    500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511
]

# ============================================================
# ENUM (alphabetically sorted)
# ============================================================


class DataTypes(str, Enum):
    """Enumeration of common HTTP content (MIME) types.

    Member names are uppercased, hyphen replaced by underscore, and
    prefixed with an underscore if starting with a digit (e.g. _3GP).
    The value of each member is the canonical MIME type string.

    Example:
        >>> DataTypes.JSON.value
        'application/json'
        >>> DataTypes.from_key('json') is DataTypes.JSON
        True

    Use `from_key()` to resolve a member from the original lower-case
    dictionary key (case-insensitive, supports hyphenated keys).
    """
    # Python 3.10 compatibility: ignore cache variables so they're not treated as enum members
    _ignore_ = ['_key_to_value_cache', '_value_to_member_cache']

    # Archive / Binary formats
    _7Z = 'application/x-7z-compressed'
    DIGIT_7Z = 'application/x-7z-compressed'
    BZ2 = 'application/x-bzip2'
    DMG = 'application/x-apple-diskimage'
    GZIP = 'application/gzip'
    GZ = 'application/gzip'
    ISO = 'application/x-iso9660-image'
    OCTET_STREAM = 'application/octet-stream'
    RAR = 'application/vnd.rar'
    TAR = 'application/x-tar'
    TAR_GZ = 'application/gzip'
    TAR_BZ2 = 'application/x-bzip2'
    TAR_XZ = 'application/x-xz'
    XZ = 'application/x-xz'
    ZIP = 'application/zip'

    # Audio formats
    AAC = 'audio/aac'
    AIFF = 'audio/aiff'
    AMR = 'audio/amr'
    FLAC = 'audio/flac'
    M4A = 'audio/mp4'
    MID = 'audio/midi'
    MIDI = 'audio/midi'
    MP3 = 'audio/mpeg'
    OGG_AUDIO = 'audio/ogg'
    OPUS = 'audio/opus'
    WAV = 'audio/wav'

    # Document formats
    CSV = 'text/csv'
    DOC = 'application/msword'
    DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    EPUB = 'application/epub+zip'
    GEOJSON = 'application/geo+json'
    ICS = 'text/calendar'
    JSON = 'application/json'
    JSONLD = 'application/ld+json'
    JSONPATCH = 'application/json-patch+json'
    JSONSCHEMA = 'application/schema+json'
    MARKDOWN = 'text/markdown'
    MD = 'text/markdown'
    ODS = 'application/vnd.oasis.opendocument.spreadsheet'
    ODT = 'application/vnd.oasis.opendocument.text'
    ODP = 'application/vnd.oasis.opendocument.presentation'
    PDF = 'application/pdf'
    PLAIN = 'text/plain'
    PPT = 'application/vnd.ms-powerpoint'
    PPTX = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    RTF = 'application/rtf'
    TEXT = 'text/plain'
    TOML = 'application/toml'
    TXT = 'text/plain'
    XLS = 'application/vnd.ms-excel'
    XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    YAML = 'application/yaml'
    YML = 'application/yaml'
    XHTML = "application/xhtml+xml"
    RSS = "application/rss+xml"
    ATOM = "application/atom+xml"

    # Font formats
    EOT = 'application/vnd.ms-fontobject'
    OTF = 'font/otf'
    TTF = 'font/ttf'
    WOFF = 'font/woff'
    WOFF2 = 'font/woff2'

    # HTML / CSS / JS / XML
    CSS = 'text/css'
    FORM = 'application/x-www-form-urlencoded'
    FORM_DATA = 'multipart/form-data'
    MULTIPART = 'multipart/form-data'  # Alias for FORM_DATA
    HTML = 'text/html'
    JAVASCRIPT = 'application/javascript'
    JS = 'application/javascript'
    XML = 'application/xml'

    # Image formats
    AVIF = 'image/avif'
    BMP = 'image/bmp'
    GIF = 'image/gif'
    HEIC = 'image/heic'
    HEIF = 'image/heif'
    ICO = 'image/vnd.microsoft.icon'
    JPEG = 'image/jpeg'
    JPE = 'image/jpe'
    JPG = 'image/jpeg'
    PNG = 'image/png'
    SVG = 'image/svg+xml'
    TIFF = 'image/tiff'
    WEBP = 'image/webp'
    XICON = 'image/x-icon'
    # Less common image types
    GRIB = 'application/grib'
    HDR = 'image/vnd.radiance'
    ICNS = 'image/icns'
    H5 = 'application/x-hdf5'
    HDF = 'application/x-hdf'
    JP2 = 'image/jp2'
    J2K = 'image/jp2'
    JPC = 'image/jp2'
    JPF = 'image/jp2'
    JPX = 'image/jp2'
    J2C = 'image/jp2'
    IM = 'image/im'
    IIM = 'application/x-iim'
    JFIF = 'image/jpeg'
    MPO = 'image/mpo'
    MSP = 'image/x-mspaint'
    PALM = 'image/x-palm'
    PCD = 'image/x-photo-cd'
    PXR = 'image/pxr'
    PBM = 'image/portable-bitmap'
    PGM = 'image/portable-graymap'
    PPM = 'image/portable-pixmap'
    PNM = 'image/portable-anymap'
    PFM = 'image/portable-floatmap'
    PSD = 'image/vnd.adobe.photoshop'
    QOI = 'image/qoi'
    BW = 'image/bw'
    RGB = 'image/rgb'
    RGBA = 'image/rgba'
    SGI = 'image/sgi'
    RAS = 'image/cmu-raster'
    ICB = 'image/tga'
    VDA = 'image/tga'
    VST = 'image/tga'
    WMF = 'image/wmf'
    EMF = 'image/emf'
    DIB = "image/bmp"                      # DIB is essentially BMP
    CUR = "image/x-icon"                    # Cursor files
    PCX = "image/pcx"                       # PCX
    DDS = "image/vnd.ms-dds"                # DirectDraw Surface
    EPS = "application/postscript"          # Encapsulated PostScript
    FIT = "image/fits"                       # FITS (astronomical)
    FITS = "image/fits"
    FLI = "video/fli"                       # FLI animation
    FLC = "video/flc"                       # FLC animation
    GBR = "image/gbr"                        # GIMP brush / old graphics
    APNG = "image/apng"                      # Animated PNG
    TIF = "image/tiff"                       # TIFF alternate extension
    XBM = "image/x-xbitmap"                  # X bitmap
    XPM = "image/x-xpixmap"                  # X pixmap

    # Redirect pseudo-type
    REDIRECT = 'application/redirect'

    # Streaming
    STREAM = 'application/octet-stream'

    # Video formats
    _3G2 = 'video/3gpp2'
    DIGIT_3G2 = 'video/3gpp2'
    _3GP = 'video/3gpp'
    DIGIT_3GP = 'video/3gpp'
    _3GPP = 'video/3gpp'
    DIGIT_3GPP = 'video/3gpp'
    _3GPP2 = 'video/3gpp2'
    DIGIT_3GPP2 = 'video/3gpp2'
    AVI = 'video/x-msvideo'
    FLV = 'video/x-flv'
    MKV = 'video/x-matroska'
    MOV = 'video/quicktime'
    MP4 = 'video/mp4'
    MPEG = 'video/mpeg'
    WEBM = 'video/webm'
    OGG_VIDEO = "video/ogg"
    WMV = "video/x-ms-wmv"
    M4v = "video/x-m4v"

    # WASM
    WASM = 'application/wasm'
    OGG = 'application/ogg'

    # Not a mime
    BASE16 = 'application/base16'
    BASE32 = 'application/base32'
    BASE64 = 'application/base64'
    BASE85 = 'application/base85'
    BYTES = 'application/bytes'

    # Class cleaning + optimisation
    _key_to_value_cache: ClassVar[Dict[str, str]] = {}
    _value_to_member_cache: ClassVar[Dict[str, "DataTypes"]] = {}

    @classmethod
    def _init_cache(cls) -> None:
        """Initialize internal caches, called on first use."""
        # Access via __dict__ to bypass enum's __getattr__ in Python 3.10
        key_cache = cls.__dict__.get('_key_to_value_cache', {})
        val_cache = cls.__dict__.get('_value_to_member_cache', {})

        # Only build if caches are empty (dicts start empty by definition)
        if key_cache and val_cache:
            return

        # build the key->value dict once
        key_to_value: Dict[str, str] = {}
        for name, member in cls.__members__.items():
            key_to_value[cls._normalize_key(name)] = member.value
        cls._key_to_value_cache = key_to_value

        # build the value->member dict once
        value_to_member: Dict[str, "DataTypes"] = {}
        for member in cls.__members__.values():
            value_to_member[member.value] = member
        cls._value_to_member_cache = value_to_member

    @staticmethod
    def _normalize_key(name: str) -> str:
        """Convert enum member name to dictionary key."""
        if name.startswith("_"):
            return name[1:].lower()
        if name.startswith("DIGIT_"):
            return name[6:].lower()
        return name.lower()

    @classmethod
    def from_key(cls, key: str) -> Optional['DataTypes']:
        """Return enum member matching original DATA_TYPES key (case-insensitive)."""
        norm = key.strip().lower()
        cls._init_cache()

        # Access via __dict__ to bypass enum's __getattr__ in Python 3.10
        key_cache = cls.__dict__.get('_key_to_value_cache', {})
        if not key_cache:
            return None

        value = key_cache.get(norm)
        if not value:
            return None

        val_cache = cls.__dict__.get('_value_to_member_cache', {})
        if not val_cache:
            return None

        return val_cache.get(value)

    @classmethod
    def get_dict(cls) -> Dict[str, str]:
        """
        Return a dictionary mapping normalized lowercase keys to MIME type strings.

        The keys correspond to the naming convention used in DATA_TYPES:
            - enum names are lowercased
            - a leading underscore becomes a leading digit key (e.g. _3GP -> "3gp")
            - underscores become hyphens only if originally used to escape illegal names

        Example:
            >>> DataTypes.get_dict()["json"]
            'application/json'

        Returns:
            Dict[str, str]: A mapping of normalized string keys to MIME type strings.
        """
        cls._init_cache()
        # Access via __dict__ to bypass enum's __getattr__ in Python 3.10
        return cls.__dict__.get('_key_to_value_cache', {})

# ============================================================
# BASE MIME-TYPE DEFINITIONS
# Alphabetically sorted
# ============================================================


DATA_TYPES: Dict[str, str] = DataTypes.get_dict()

# File-like responses
FILE_TYPES: Tuple[DataTypes, ...] = (
    # Archives / binaries
    DataTypes.ZIP, DataTypes.GZIP, DataTypes.TAR,
    DataTypes._7Z, DataTypes.DIGIT_7Z,
    DataTypes.BZ2, DataTypes.DMG, DataTypes.ISO, DataTypes.OCTET_STREAM, DataTypes.RAR,
    DataTypes.TAR_GZ, DataTypes.TAR_BZ2, DataTypes.TAR_XZ, DataTypes.XZ,
    # Fonts
    DataTypes.EOT, DataTypes.OTF, DataTypes.TTF, DataTypes.WOFF, DataTypes.WOFF2,
    # Audio
    DataTypes.MP3, DataTypes.WAV, DataTypes.FLAC, DataTypes.AAC, DataTypes.OGG_AUDIO, DataTypes.OPUS,
    DataTypes.M4A, DataTypes.AIFF, DataTypes.AMR, DataTypes.MID, DataTypes.MIDI,
    # Video
    DataTypes.MP4, DataTypes.MPEG, DataTypes.AVI,
    DataTypes._3GP, DataTypes.DIGIT_3GP,
    DataTypes._3GPP, DataTypes.DIGIT_3GPP,
    DataTypes._3G2, DataTypes.DIGIT_3G2,
    DataTypes._3GPP2, DataTypes.DIGIT_3GPP2,
    DataTypes.MOV, DataTypes.FLV, DataTypes.MKV, DataTypes.WEBM, DataTypes.OGG_VIDEO,
    DataTypes.WMV, DataTypes.M4v,
    # Documents
    DataTypes.PDF, DataTypes.RTF, DataTypes.DOC, DataTypes.DOCX,
    DataTypes.XLS, DataTypes.XLSX, DataTypes.PPT, DataTypes.PPTX,
    DataTypes.ODT, DataTypes.ODS, DataTypes.ODP, DataTypes.EPUB,
    DataTypes.ICS, DataTypes.CSV, DataTypes.GEOJSON,
    # Images
    DataTypes.JPEG, DataTypes.JPG, DataTypes.JPE, DataTypes.PNG, DataTypes.GIF, DataTypes.BMP,
    DataTypes.TIFF, DataTypes.WEBP, DataTypes.ICO, DataTypes.SVG, DataTypes.XICON, DataTypes.GRIB,
    DataTypes.HDR, DataTypes.ICNS, DataTypes.H5, DataTypes.HDF, DataTypes.JP2, DataTypes.J2K,
    DataTypes.JPC, DataTypes.JPF, DataTypes.JPX, DataTypes.J2C, DataTypes.IM, DataTypes.IIM,
    DataTypes.JFIF, DataTypes.MPO, DataTypes.MSP, DataTypes.PALM, DataTypes.PCD, DataTypes.PXR,
    DataTypes.PBM, DataTypes.PGM, DataTypes.PPM, DataTypes.PNM, DataTypes.PFM, DataTypes.PSD,
    DataTypes.QOI, DataTypes.BW, DataTypes.RGB, DataTypes.RGBA, DataTypes.SGI, DataTypes.RAS,
    DataTypes.ICB, DataTypes.VDA, DataTypes.VST, DataTypes.WMF, DataTypes.EMF, DataTypes.DIB,
    DataTypes.CUR, DataTypes.PCX, DataTypes.DDS, DataTypes.EPS, DataTypes.FIT, DataTypes.FITS,
    DataTypes.FLI, DataTypes.FLC, DataTypes.GBR, DataTypes.APNG, DataTypes.TIF, DataTypes.XBM,
    DataTypes.XPM,
    # Streaming / others
    DataTypes.OGG, DataTypes.STREAM,
    # JavaScript files (served as files, not inline)
    DataTypes.JAVASCRIPT, DataTypes.JS,
    # Form data (for file uploads and mixed content)
    DataTypes.FORM_DATA, DataTypes.MULTIPART
)

# HTML-like responses
HTML_TYPES: Tuple[DataTypes, ...] = (
    DataTypes.CSS,
    DataTypes.HTML,
    DataTypes.XML,
    # Form data for simple form submissions (not file uploads)
    DataTypes.FORM
)

# JSON responses
JSON_TYPES: Tuple[DataTypes, ...] = (
    DataTypes.JSON,
    DataTypes.JSONLD,
    DataTypes.GEOJSON,
    DataTypes.JSONPATCH,
    DataTypes.JSONSCHEMA
)

# Plain text responses
PLAIN_TEXT_TYPES: Tuple[DataTypes, ...] = (
    DataTypes.CSV,
    DataTypes.MARKDOWN,
    DataTypes.MD,
    DataTypes.PLAIN,
    DataTypes.TEXT,
    DataTypes.TOML,
    DataTypes.TXT,
    DataTypes.YAML,
    DataTypes.YML
)

# Redirect responses
REDIRECT_TYPES: Tuple[DataTypes, ...] = (
    DataTypes.REDIRECT,
)

# Streaming responses
STREAMING_TYPES: Tuple[DataTypes, ...] = (
    DataTypes.STREAM,
    DataTypes.OCTET_STREAM
)

# JSON-optimized responses
UJSON_TYPES: Tuple[DataTypes, ...] = JSON_TYPES
ORJSON_TYPES: Tuple[DataTypes, ...] = JSON_TYPES

# ============================================================
# DERIVED MIME TYPE VALUE SETS (for quick membership checks)
# ============================================================


def _build_mime_set(group: Tuple[DataTypes, ...]) -> Set[str]:
    """Return a set of MIME type strings for the provided DataTypes group.

    Using an explicit loop for clarity and easier debugging instead of a
    comprehension per user preference.
    """
    result: Set[str] = set()
    for member in group:
        result.add(member.value)
    return result


# Build MIME sets with explicit loops (no inline comprehensions)
FILE_MIME_TYPES: Set[str] = _build_mime_set(FILE_TYPES)
HTML_MIME_TYPES: Set[str] = _build_mime_set(HTML_TYPES)
JSON_MIME_TYPES: Set[str] = _build_mime_set(JSON_TYPES)
PLAIN_TEXT_MIME_TYPES: Set[str] = _build_mime_set(PLAIN_TEXT_TYPES)
REDIRECT_MIME_TYPES: Set[str] = _build_mime_set(REDIRECT_TYPES)
STREAMING_MIME_TYPES: Set[str] = _build_mime_set(STREAMING_TYPES)
UJSON_MIME_TYPES: Set[str] = _build_mime_set(UJSON_TYPES)
ORJSON_MIME_TYPES: Set[str] = _build_mime_set(ORJSON_TYPES)

# ============================================================
# Default values for the response
# ============================================================

DEFAULT_MESSAGE_CONTENT: Dict[str, str] = {'msg': 'message'}

DEFAULT_MESSAGE_TYPE: str = DataTypes.JSON

# ============================================================
# Media type groupings

# Image types
IMAGE_TYPES_UNIVERSAL: Tuple[DataTypes, ...] = (
    DataTypes.PNG, DataTypes.JPEG, DataTypes.JPE,
    DataTypes.JPG, DataTypes.GIF, DataTypes.SVG,
    DataTypes.ICO, DataTypes.WEBP, DataTypes.APNG
)
IMAGE_TYPES_NEED_CONVERTING: Tuple[DataTypes, ...] = (
    DataTypes.BMP, DataTypes.HEIC, DataTypes.HEIF, DataTypes.XICON, DataTypes.AVIF,
    DataTypes.GRIB, DataTypes.HDR, DataTypes.ICNS, DataTypes.H5, DataTypes.HDF,
    DataTypes.JP2, DataTypes.J2K, DataTypes.JPC, DataTypes.JPF, DataTypes.JPX, DataTypes.J2C,
    DataTypes.IM, DataTypes.IIM, DataTypes.JFIF, DataTypes.MPO, DataTypes.MSP,
    DataTypes.PALM, DataTypes.PCD, DataTypes.PBM, DataTypes.PGM, DataTypes.PPM,
    DataTypes.PNM, DataTypes.PFM, DataTypes.PSD, DataTypes.QOI, DataTypes.BW,
    DataTypes.RGB, DataTypes.RGBA, DataTypes.SGI, DataTypes.RAS, DataTypes.ICB,
    DataTypes.VDA, DataTypes.VST, DataTypes.WMF, DataTypes.EMF, DataTypes.DIB,
    DataTypes.CUR, DataTypes.PCX, DataTypes.DDS, DataTypes.EPS, DataTypes.FIT,
    DataTypes.FITS, DataTypes.FLI, DataTypes.FLC, DataTypes.GBR, DataTypes.TIF,
    DataTypes.XBM, DataTypes.XPM
)
IMAGE_TYPES_HEAVY: Tuple[DataTypes, ...] = (
    DataTypes.BMP,
    DataTypes.TIFF,
    DataTypes.PNG,   # large for photos
    DataTypes.HEIC,
    DataTypes.HEIF,
    DataTypes.HDR,
    DataTypes.JP2,
    DataTypes.J2K,
    DataTypes.JPC,
    DataTypes.JPF,
    DataTypes.JPX,
    DataTypes.J2C,
    DataTypes.PSD,
    DataTypes.TIF
)

IMAGE_CONVERSION_TARGET: Dict[DataTypes, DataTypes] = {
    DataTypes.BMP: DataTypes.WEBP,
    DataTypes.HEIC: DataTypes.WEBP,
    DataTypes.HEIF: DataTypes.WEBP,
    DataTypes.XICON: DataTypes.PNG,
    DataTypes.AVIF: DataTypes.WEBP,
    DataTypes.TIFF: DataTypes.WEBP,
    DataTypes.JPE: DataTypes.JPEG,
    DataTypes.JPG: DataTypes.JPEG,
    DataTypes.GRIB: DataTypes.PNG,
    DataTypes.HDR: DataTypes.PNG,
    DataTypes.ICNS: DataTypes.PNG,
    DataTypes.H5: DataTypes.PNG,
    DataTypes.HDF: DataTypes.PNG,
    DataTypes.JP2: DataTypes.JPEG,
    DataTypes.J2K: DataTypes.JPEG,
    DataTypes.JPC: DataTypes.JPEG,
    DataTypes.JPF: DataTypes.JPEG,
    DataTypes.JPX: DataTypes.JPEG,
    DataTypes.J2C: DataTypes.JPEG,
    DataTypes.IM: DataTypes.PNG,
    DataTypes.IIM: DataTypes.PNG,
    DataTypes.JFIF: DataTypes.JPEG,
    DataTypes.MPO: DataTypes.JPEG,
    DataTypes.MSP: DataTypes.PNG,
    DataTypes.PALM: DataTypes.PNG,
    DataTypes.PCD: DataTypes.JPEG,
    DataTypes.PBM: DataTypes.PNG,
    DataTypes.PGM: DataTypes.PNG,
    DataTypes.PPM: DataTypes.PNG,
    DataTypes.PNM: DataTypes.PNG,
    DataTypes.PFM: DataTypes.PNG,
    DataTypes.PSD: DataTypes.PNG,
    DataTypes.QOI: DataTypes.PNG,
    DataTypes.BW: DataTypes.PNG,
    DataTypes.RGB: DataTypes.PNG,
    DataTypes.RGBA: DataTypes.PNG,
    DataTypes.SGI: DataTypes.PNG,
    DataTypes.RAS: DataTypes.PNG,
    DataTypes.ICB: DataTypes.PNG,
    DataTypes.VDA: DataTypes.PNG,
    DataTypes.VST: DataTypes.PNG,
    DataTypes.WMF: DataTypes.PNG,
    DataTypes.EMF: DataTypes.PNG,
    DataTypes.DIB: DataTypes.PNG,
    DataTypes.CUR: DataTypes.PNG,
    DataTypes.PCX: DataTypes.PNG,
    DataTypes.DDS: DataTypes.PNG,
    DataTypes.EPS: DataTypes.PNG,
    DataTypes.FIT: DataTypes.PNG,
    DataTypes.FITS: DataTypes.PNG,
    DataTypes.FLI: DataTypes.GIF,
    DataTypes.FLC: DataTypes.GIF,
    DataTypes.GBR: DataTypes.PNG,
    DataTypes.TIF: DataTypes.WEBP,
    DataTypes.XBM: DataTypes.PNG,
    DataTypes.XPM: DataTypes.PNG
}

# Video types
VIDEO_TYPES_UNIVERSAL: Tuple[DataTypes, ...] = (
    DataTypes.MP4,    # H.264 + AAC assumed
    DataTypes.WEBM,   # VP8/VP9 (modern-safe)
)

VIDEO_TYPES_NEED_CONVERTING: Tuple[DataTypes, ...] = (
    DataTypes.MKV,
    DataTypes.AVI,
    DataTypes.FLV,
    DataTypes.MOV,
    DataTypes.MPEG,
    DataTypes._3GP,
    DataTypes._3G2,
    DataTypes._3GPP,
    DataTypes._3GPP2,
)

VIDEO_TYPES_HEAVY: Tuple[DataTypes, ...] = (
    DataTypes.MKV,
    DataTypes.AVI,
    DataTypes.MOV,
    DataTypes.MPEG,
)

VIDEO_CONVERSION_TARGET: Dict[DataTypes, DataTypes] = {
    DataTypes.MKV: DataTypes.MP4,
    DataTypes.AVI: DataTypes.MP4,
    DataTypes.FLV: DataTypes.MP4,
    DataTypes.MOV: DataTypes.MP4,
    DataTypes.MPEG: DataTypes.MP4,
    DataTypes._3GP: DataTypes.MP4,
    DataTypes._3G2: DataTypes.MP4,
    DataTypes._3GPP: DataTypes.MP4,
    DataTypes._3GPP2: DataTypes.MP4,
}

# Audio types
AUDIO_TYPES_UNIVERSAL: Tuple[DataTypes, ...] = (
    DataTypes.MP3,
    DataTypes.WAV,
    DataTypes.AAC,
)

AUDIO_TYPES_NEED_CONVERTING: Tuple[DataTypes, ...] = (
    DataTypes.FLAC,
    DataTypes.AIFF,
    DataTypes.OPUS,
    DataTypes.OGG_AUDIO,
    DataTypes.M4A,
    DataTypes.AMR,
    DataTypes.MID,
    DataTypes.MIDI,
)

AUDIO_TYPES_HEAVY: Tuple[DataTypes, ...] = (
    DataTypes.WAV,
    DataTypes.AIFF,
    DataTypes.FLAC,
    DataTypes.MID,
    DataTypes.MIDI,
)

AUDIO_CONVERSION_TARGET: Dict[DataTypes, DataTypes] = {
    DataTypes.FLAC: DataTypes.MP3,
    DataTypes.AIFF: DataTypes.MP3,
    DataTypes.OPUS: DataTypes.MP3,
    DataTypes.OGG_AUDIO: DataTypes.MP3,
    DataTypes.M4A: DataTypes.MP3,
    DataTypes.AMR: DataTypes.MP3,
    DataTypes.MID: DataTypes.MP3,
    DataTypes.MIDI: DataTypes.MP3,
}

# Document types
DOCUMENT_TYPES_UNIVERSAL: Tuple[DataTypes, ...] = (
    DataTypes.PDF,
    DataTypes.JSON,
    DataTypes.PLAIN,
    DataTypes.TEXT,
    DataTypes.TXT,
    DataTypes.CSV,
    DataTypes.HTML,
    DataTypes.XML,
)

DOCUMENT_TYPES_NEED_CONVERTING: Tuple[DataTypes, ...] = (
    DataTypes.DOC,
    DataTypes.DOCX,
    DataTypes.PPT,
    DataTypes.PPTX,
    DataTypes.XLS,
    DataTypes.XLSX,
    DataTypes.ODS,
    DataTypes.ODT,
    DataTypes.ODP,
    DataTypes.EPUB,
    DataTypes.MARKDOWN,
    DataTypes.MD,
    DataTypes.RTF,
    DataTypes.TOML,
    DataTypes.YAML,
    DataTypes.YML,
)

DOCUMENT_TYPES_HEAVY: Tuple[DataTypes, ...] = (
    DataTypes.PDF,
    DataTypes.PPTX,
    DataTypes.DOCX,
    DataTypes.XLSX,
)

DOCUMENT_CONVERSION_TARGET: Dict[DataTypes, DataTypes] = {
    DataTypes.DOC: DataTypes.PDF,
    DataTypes.DOCX: DataTypes.PDF,
    DataTypes.PPT: DataTypes.PDF,
    DataTypes.PPTX: DataTypes.PDF,
    DataTypes.XLS: DataTypes.PDF,
    DataTypes.XLSX: DataTypes.PDF,
    DataTypes.ODS: DataTypes.PDF,
    DataTypes.ODT: DataTypes.PDF,
    DataTypes.ODP: DataTypes.PDF,
    DataTypes.EPUB: DataTypes.PDF,
    DataTypes.MARKDOWN: DataTypes.HTML,
    DataTypes.MD: DataTypes.HTML,
    DataTypes.RTF: DataTypes.PDF,
    DataTypes.TOML: DataTypes.JSON,
    DataTypes.YAML: DataTypes.JSON,
    DataTypes.YML: DataTypes.JSON,
}

# Archive types
ARCHIVE_TYPES_UNIVERSAL: Tuple[DataTypes, ...] = (
    DataTypes.ZIP,
)

ARCHIVE_TYPES_NEED_CONVERTING: Tuple[DataTypes, ...] = (
    DataTypes.RAR,
    DataTypes._7Z,
    DataTypes.BZ2,
    DataTypes.TAR,
    DataTypes.TAR_GZ,
    DataTypes.TAR_BZ2,
    DataTypes.TAR_XZ,
    DataTypes.XZ,
    DataTypes.GZIP,
    DataTypes.ISO,
    DataTypes.DMG,
)

ARCHIVE_TYPES_HEAVY: Tuple[DataTypes, ...] = (
    DataTypes.ISO,
    DataTypes.DMG,
    DataTypes.TAR,
    DataTypes.TAR_GZ,
    DataTypes.TAR_BZ2,
    DataTypes.TAR_XZ,
    DataTypes.XZ,
)

ARCHIVE_CONVERSION_TARGET: Dict[DataTypes, DataTypes] = {
    DataTypes.RAR: DataTypes.ZIP,
    DataTypes._7Z: DataTypes.ZIP,
    DataTypes.BZ2: DataTypes.ZIP,
    DataTypes.TAR: DataTypes.ZIP,
    DataTypes.GZIP: DataTypes.ZIP,
    DataTypes.ISO: DataTypes.ZIP,
    DataTypes.DMG: DataTypes.ZIP,
    DataTypes.TAR_GZ: DataTypes.ZIP,
    DataTypes.TAR_BZ2: DataTypes.ZIP,
    DataTypes.TAR_XZ: DataTypes.ZIP,
}

# Font types
FONT_TYPES_UNIVERSAL: Tuple[DataTypes, ...] = (
    DataTypes.WOFF,
    DataTypes.WOFF2,
)

FONT_TYPES_NEED_CONVERTING: Tuple[DataTypes, ...] = (
    DataTypes.TTF,
    DataTypes.OTF,
    DataTypes.EOT,
)

FONT_TYPES_HEAVY: Tuple[DataTypes, ...] = (
    DataTypes.TTF,
    DataTypes.OTF,
)

FONT_CONVERSION_TARGET: Dict[DataTypes, DataTypes] = {
    DataTypes.TTF: DataTypes.WOFF2,
    DataTypes.OTF: DataTypes.WOFF2,
    DataTypes.EOT: DataTypes.WOFF2,
}

# Stream binary types
BINARY_TYPES_UNIVERSAL: Tuple[DataTypes, ...] = (
    DataTypes.OCTET_STREAM,
    DataTypes.STREAM,
)

BINARY_TYPES_NEED_CONVERTING: Tuple[DataTypes, ...] = ()
BINARY_TYPES_HEAVY: Tuple[DataTypes, ...] = ()
BINARY_CONVERSION_TARGET: Dict[DataTypes, DataTypes] = {}

# Base types
BASE_TYPES_UNIVERSAL: Tuple[DataTypes, ...] = (
    DataTypes.BASE16,
    DataTypes.BASE32,
    DataTypes.BASE64,
    DataTypes.BASE85,
)
BASE_TYPES_NEED_CONVERTING: Tuple[DataTypes, ...] = ()
BASE_TYPES_HEAVY: Tuple[DataTypes, ...] = ()
BASE_TYPES_CONVERSION_TARGET: Dict[DataTypes, DataTypes] = {}

# ============================================================

# lookup conversion table
CONVERSION_TARGETS: Dict[DataTypes, DataTypes] = {}
for d in (
    IMAGE_CONVERSION_TARGET, VIDEO_CONVERSION_TARGET,
    AUDIO_CONVERSION_TARGET, DOCUMENT_CONVERSION_TARGET,
    ARCHIVE_CONVERSION_TARGET, FONT_CONVERSION_TARGET,
    BINARY_CONVERSION_TARGET, BASE_TYPES_CONVERSION_TARGET
):
    CONVERSION_TARGETS.update(d)

# ============================================================

# Media type lookup tables


@dataclass(frozen=True)
class MediaTypeRegistry:
    """Registry of media type groupings and conversion targets."""
    # Images
    image_universal: Tuple[DataTypes, ...]
    image_needs_converting: Tuple[DataTypes, ...]
    image_heavy: Tuple[DataTypes, ...]
    image_conversion_targets: Dict[DataTypes, DataTypes]

    # Video
    video_universal: Tuple[DataTypes, ...]
    video_needs_converting: Tuple[DataTypes, ...]
    video_heavy: Tuple[DataTypes, ...]
    video_conversion_targets: Dict[DataTypes, DataTypes]

    # Audio
    audio_universal: Tuple[DataTypes, ...]
    audio_needs_converting: Tuple[DataTypes, ...]
    audio_heavy: Tuple[DataTypes, ...]
    audio_conversion_targets: Dict[DataTypes, DataTypes]

    # Documents
    document_universal: Tuple[DataTypes, ...]
    document_needs_converting: Tuple[DataTypes, ...]
    document_heavy: Tuple[DataTypes, ...]
    document_conversion_targets: Dict[DataTypes, DataTypes]

    # Archives
    archive_universal: Tuple[DataTypes, ...]
    archive_needs_converting: Tuple[DataTypes, ...]
    archive_heavy: Tuple[DataTypes, ...]
    archive_conversion_targets: Dict[DataTypes, DataTypes]

    # Fonts
    font_universal: Tuple[DataTypes, ...]
    font_needs_converting: Tuple[DataTypes, ...]
    font_heavy: Tuple[DataTypes, ...]
    font_conversion_targets: Dict[DataTypes, DataTypes]

    # Binary
    binary_universal: Tuple[DataTypes, ...]
    binary_needs_converting: Tuple[DataTypes, ...]
    binary_heavy: Tuple[DataTypes, ...]
    binary_conversion_targets: Dict[DataTypes, DataTypes]

    # Base type
    base_types_universal: Tuple[DataTypes, ...]
    base_types_need_converting: Tuple[DataTypes, ...]
    base_types_heavy: Tuple[DataTypes, ...]
    base_types_conversion_targets: Dict[DataTypes, DataTypes]

    # Conversion lookup
    conversion_targets: Dict[DataTypes, DataTypes]

    def is_image(self, mime: DataTypes) -> bool:
        """Check if the given MIME type is an image.
        Args:
            mime (DataTypes): The MIME type to check.
        Returns:
            bool: True if it's an image, False otherwise.
        """
        return mime in self.image_universal or mime in self.image_needs_converting

    def is_video(self, mime: DataTypes) -> bool:
        """Check if the given MIME type is a video.
        Args:
            mime (DataTypes): The MIME type to check.
        Returns:
            bool: True if it's a video, False otherwise.
        """
        return mime in self.video_universal or mime in self.video_needs_converting

    def is_audio(self, mime: DataTypes) -> bool:
        """Check if the given MIME type is an audio.
        Args:
            mime (DataTypes): The MIME type to check.
        Returns:
            bool: True if it's an audio, False otherwise.
        """
        return mime in self.audio_universal or mime in self.audio_needs_converting

    def is_document(self, mime: DataTypes) -> bool:
        """Check if the given MIME type is a document.
        Args:
            mime (DataTypes): The MIME type to check.
        Returns:
            bool: True if it's a document, False otherwise.
        """
        return mime in self.document_universal or mime in self.document_needs_converting

    def is_archive(self, mime: DataTypes) -> bool:
        """Check if the given MIME type is an archive.
        Args:
            mime (DataTypes): The MIME type to check.
        Returns:
            bool: True if it's an archive, False otherwise.
        """
        return mime in self.archive_universal or mime in self.archive_needs_converting

    def is_font(self, mime: DataTypes) -> bool:
        """Check if the given MIME type is a font.
        Args:
            mime (DataTypes): The MIME type to check.
        Returns:
            bool: True if it's a font, False otherwise.
        """
        return mime in self.font_universal or mime in self.font_needs_converting

    def is_binary(self, mime: DataTypes) -> bool:
        """Check if the given MIME type is a binary stream.
        Args:
            mime (DataTypes): The MIME type to check.
        Returns:
            bool: True if it's a binary stream, False otherwise.
        """
        return mime in self.binary_universal or mime in self.binary_needs_converting

    def is_base_type(self, mime: DataTypes) -> bool:
        """Check if the given MIME type is a base (universal) type.
        Args:
            mime (DataTypes): The MIME type to check.
        Returns:
            bool: True if it's a base type, False otherwise.
        """
        return mime in self.base_types_universal or mime in self.base_types_need_converting

    def is_heavy(self, mime: DataTypes) -> bool:
        """Check if the given MIME type is considered heavy.
        Args:
            mime (DataTypes): The MIME type to check.
        Returns:
            bool: True if it's heavy, False otherwise.
        """
        return (
            mime in self.image_heavy or
            mime in self.video_heavy or
            mime in self.audio_heavy or
            mime in self.document_heavy or
            mime in self.archive_heavy or
            mime in self.font_heavy or
            mime in self.binary_heavy
        )

    def is_supported(self, mime: DataTypes) -> bool:
        """Check if the given MIME type is supported in any category.
        Args:
            mime (DataTypes): The MIME type to check.
        Returns:
            bool: True if supported, False otherwise.
        """
        return (
            self.is_image(mime) or
            self.is_video(mime) or
            self.is_audio(mime) or
            self.is_document(mime) or
            self.is_archive(mime) or
            self.is_font(mime) or
            self.is_binary(mime)
        )

    def needs_conversion(self, mime: DataTypes) -> bool:
        """Check if the given MIME type requires conversion.
        Args:
            mime (DataTypes): The MIME type to check.
        Returns:
            bool: True if conversion is needed, False otherwise.
        """
        return mime in MEDIA_TYPES.conversion_targets

    def get_conversion_target(self, mime: DataTypes) -> Optional[DataTypes]:
        """Get the conversion target MIME type for the given MIME type.
        Args:
            mime (DataTypes): The MIME type to check.
        Returns:
            Optional[DataTypes]: The target MIME type if conversion is needed, None otherwise.
        """
        return MEDIA_TYPES.conversion_targets.get(mime)


MEDIA_TYPES = MediaTypeRegistry(
    image_universal=IMAGE_TYPES_UNIVERSAL,
    image_needs_converting=IMAGE_TYPES_NEED_CONVERTING,
    image_heavy=IMAGE_TYPES_HEAVY,
    image_conversion_targets=IMAGE_CONVERSION_TARGET,

    video_universal=VIDEO_TYPES_UNIVERSAL,
    video_needs_converting=VIDEO_TYPES_NEED_CONVERTING,
    video_heavy=VIDEO_TYPES_HEAVY,
    video_conversion_targets=VIDEO_CONVERSION_TARGET,

    audio_universal=AUDIO_TYPES_UNIVERSAL,
    audio_needs_converting=AUDIO_TYPES_NEED_CONVERTING,
    audio_heavy=AUDIO_TYPES_HEAVY,
    audio_conversion_targets=AUDIO_CONVERSION_TARGET,

    document_universal=DOCUMENT_TYPES_UNIVERSAL,
    document_needs_converting=DOCUMENT_TYPES_NEED_CONVERTING,
    document_heavy=DOCUMENT_TYPES_HEAVY,
    document_conversion_targets=DOCUMENT_CONVERSION_TARGET,

    archive_universal=ARCHIVE_TYPES_UNIVERSAL,
    archive_needs_converting=ARCHIVE_TYPES_NEED_CONVERTING,
    archive_heavy=ARCHIVE_TYPES_HEAVY,
    archive_conversion_targets=ARCHIVE_CONVERSION_TARGET,

    font_universal=FONT_TYPES_UNIVERSAL,
    font_needs_converting=FONT_TYPES_NEED_CONVERTING,
    font_heavy=FONT_TYPES_HEAVY,
    font_conversion_targets=FONT_CONVERSION_TARGET,

    binary_universal=BINARY_TYPES_UNIVERSAL,
    binary_needs_converting=BINARY_TYPES_NEED_CONVERTING,
    binary_heavy=BINARY_TYPES_HEAVY,
    binary_conversion_targets=BINARY_CONVERSION_TARGET,

    base_types_universal=BASE_TYPES_UNIVERSAL,
    base_types_need_converting=BASE_TYPES_NEED_CONVERTING,
    base_types_heavy=BASE_TYPES_HEAVY,
    base_types_conversion_targets=BASE_TYPES_CONVERSION_TARGET,

    conversion_targets=CONVERSION_TARGETS,
)
