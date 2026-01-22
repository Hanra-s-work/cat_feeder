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
# FILE: converters_constants.py
# CREATION DATE: 15-01-2026
# LAST Modified: 1:21:18 17-01-2026
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The constants used in the converter instances.
# // AR
# +==== END CatFeeder =================+
"""

from typing import Optional, Union

from dataclasses import dataclass

from pathlib import Path

from ..http_constants import DataTypes

from ...utils import constants as CONST


@dataclass(frozen=True)
class FontResult:
    """Structure used to store the response of the font conversion procedure."""
    ttf: bytes
    otf: bytes
    woff: bytes
    woff2: bytes
    css: Union[bytes, str]


@dataclass(frozen=True)
class ConversionResult:
    """Structure used to store the response of the conversion procedure."""
    data: bytes
    converted: bool
    from_type: DataTypes
    to_type: DataTypes
    result: Optional[Union[bytes, str, FontResult]] = None


FF_FAMILY_PATH: Path = CONST.ASSETS_DIRECTORY / "fffamily"
SUCCESS: int = CONST.SUCCESS
ERROR: int = CONST.ERROR
DEBUG: bool = CONST.DEBUG
