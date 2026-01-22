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
# FILE: favicon_constants.py
# CREATION DATE: 05-01-2026
# LAST Modified: 22:19:58 12-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: These are the constants used by the favicon handler.
# // AR
# +==== END CatFeeder =================+
"""

import re
from typing import Dict, Any, Optional
from dataclasses import dataclass
from ..utils.constants import BUCKET_NAME
from ..http_codes import HttpDataTypes

FAVICON_TABLE_MAIN: str = "ProfileIconsAvailable"
FAVICON_USER_OWNED_TABLE: str = "ProfileIconsUserOwned"
FAVICON_USER_ACTIVE_TABLE: str = "ProfileIconsInUse"
FAVICON_TABLE_GENDER: str = "ProfileIconGender"
FAVICON_TABLE_SEASON: str = "ProfileIconSeason"
FAVICON_TABLE_TYPE: str = "ProfileIconType"

FAVICON_IMAGE_PATH_KEY: str = "img_path"
FAVICON_BUCKET_NAME: str = BUCKET_NAME
FAVICON_BUCKET_FOLDER_USER: str = "user_favicons/"

FAVICON_DEFAULT_PRICE: int = 5

FAVICON_HEX_COLOUR_RE = re.compile(
    r'^#(?:'
    r'[0-9A-Fa-f]{3}'      # RGB
    r'|[0-9A-Fa-f]{4}'     # RGBA
    r'|[0-9A-Fa-f]{6}'     # RRGGBB
    r'|[0-9A-Fa-f]{8}'     # RRGGBBAA
    r')$'
)


@dataclass
class FaviconData:
    """This is the dataclass in charge of handling the image and it's data during processing.
    """
    img: Optional[bytes] = None
    img_type: HttpDataTypes = HttpDataTypes.OCTET_STREAM
    data: Optional[Dict[str, Any]] = None
