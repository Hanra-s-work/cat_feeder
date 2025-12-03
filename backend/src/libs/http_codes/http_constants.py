"""
# +==== BEGIN AsperBackend =================+
# LOGO:
# ..........####...####..........
# ......###.....#.#########......
# ....##........#.###########....
# ...#..........#.############...
# ...#..........#.#####.######...
# ..#.....##....#.###..#...####..
# .#.....#.##...#.##..##########.
# #.....##########....##...######
# #.....#...##..#.##..####.######
# .#...##....##.#.##..###..#####.
# ..#.##......#.#.####...######..
# ..#...........#.#############..
# ..#...........#.#############..
# ...##.........#.############...
# ......#.......#.#########......
# .......#......#.########.......
# .........#####...#####.........
# /STOP
# PROJECT: AsperBackend
# FILE: http_constants.py
# CREATION DATE: 19-11-2025
# LAST Modified: 16:33:2 30-11-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
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
# +==== END AsperBackend =================+
"""

from __future__ import annotations
from enum import Enum
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
    # Archive / Binary formats
    _7Z = 'application/x-7z-compressed'
    DIGIT_7Z = 'application/x-7z-compressed'
    BZ2 = 'application/x-bzip2'
    DMG = 'application/x-apple-diskimage'
    GZIP = 'application/gzip'
    ISO = 'application/x-iso9660-image'
    OCTET_STREAM = 'application/octet-stream'
    RAR = 'application/vnd.rar'
    TAR = 'application/x-tar'
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
    JPG = 'image/jpeg'
    PNG = 'image/png'
    SVG = 'image/svg+xml'
    TIFF = 'image/tiff'
    WEBP = 'image/webp'
    XICON = 'image/x-icon'

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

    # WASM
    WASM = 'application/wasm'
    OGG = 'application/ogg'

    # Class cleaning + optimisation
    __KEY_TO_VALUE: ClassVar[Dict[str, str]] = {}
    __VALUE_TO_MEMBER: ClassVar[Dict[str, "DataTypes"]] = {}

    @classmethod
    def _init_cache(cls) -> None:
        """Initialize internal caches, called on first use."""
        # Only build if caches are empty (dicts start empty by definition)
        if cls.__KEY_TO_VALUE and cls.__VALUE_TO_MEMBER:
            return
        # build the key->value dict once
        key_to_value: Dict[str, str] = {}
        for name, member in cls.__members__.items():
            key_to_value[cls._normalize_key(name)] = member.value
        cls.__KEY_TO_VALUE = key_to_value
        # build the value->member dict once
        value_to_member: Dict[str, "DataTypes"] = {}
        for member in cls.__members__.values():
            value_to_member[member.value] = member
        cls.__VALUE_TO_MEMBER = value_to_member

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
        if not cls.__KEY_TO_VALUE:
            return None
        value = cls.__KEY_TO_VALUE.get(norm)
        if not value:
            return None
        if not cls.__VALUE_TO_MEMBER:
            return None
        return cls.__VALUE_TO_MEMBER.get(value)

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
        if cls.__KEY_TO_VALUE:
            return cls.__KEY_TO_VALUE
        return {}

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
    # Fonts
    DataTypes.EOT, DataTypes.OTF, DataTypes.TTF, DataTypes.WOFF, DataTypes.WOFF2,
    # Audio
    DataTypes.MP3, DataTypes.WAV, DataTypes.FLAC, DataTypes.AAC, DataTypes.OGG_AUDIO, DataTypes.OPUS,
    # Video
    DataTypes.MP4, DataTypes.MPEG, DataTypes.AVI,
    DataTypes._3GP, DataTypes.DIGIT_3GP,
    DataTypes._3GPP, DataTypes.DIGIT_3GPP,
    DataTypes._3G2, DataTypes.DIGIT_3G2,
    DataTypes._3GPP2, DataTypes.DIGIT_3GPP2,
    # Documents
    DataTypes.PDF, DataTypes.RTF, DataTypes.DOC, DataTypes.DOCX,
    DataTypes.XLS, DataTypes.XLSX, DataTypes.PPT, DataTypes.PPTX,
    # Images
    DataTypes.JPEG, DataTypes.JPG, DataTypes.PNG, DataTypes.GIF, DataTypes.BMP,
    DataTypes.TIFF, DataTypes.WEBP, DataTypes.ICO, DataTypes.SVG, DataTypes.XICON,
    # Streaming / others
    DataTypes.OGG, DataTypes.STREAM,
    # JavaScript files (served as files, not inline)
    DataTypes.JAVASCRIPT, DataTypes.JS
)

# HTML-like responses
HTML_TYPES: Tuple[DataTypes, ...] = (
    DataTypes.CSS,
    DataTypes.HTML,
    DataTypes.XML
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
