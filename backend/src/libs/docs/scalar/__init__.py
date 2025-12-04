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
# LAST Modified: 5:20:41 26-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
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
