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
# LAST Modified: 14:45:41 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Scalar documentation provider.
# // AR
# +==== END CatFeeder =================+
"""

from .scalar_provider import ScalarProvider
from . import scalar_constants as SCALAR_CONST

__all__ = [
    "ScalarProvider",
    "SCALAR_CONST"
]
