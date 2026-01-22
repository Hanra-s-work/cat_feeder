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
# CREATION DATE: 26-11-2025
# LAST Modified: 14:44:50 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: RapiDoc documentation provider.
# // AR
# +==== END CatFeeder =================+
"""

from .rapidoc_provider import RapiDocProvider
from . import rapidoc_constants as RAPIDOC_CONST

__all__ = [
    "RapiDocProvider",
    "RAPIDOC_CONST"
]
