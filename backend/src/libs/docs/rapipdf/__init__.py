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
# LAST Modified: 5:20:26 26-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: RapiPDF documentation provider.
# // AR
# +==== END CatFeeder =================+
"""

from .rapipdf_provider import RapiPDFProvider
from . import rapipdf_constants as RAPIPDF_CONST

__all__ = [
    "RapiPDFProvider",
    "RAPIPDF_CONST"
]
