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
# LAST Modified: 4:51:56 26-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The swagger wrapper to help inject it into the server.
# // AR
# +==== END CatFeeder =================+
"""

from .redoc_class import RedocHandler
from . import redoc_constants as REDOC_CONST

__all__ = [
    "RedocHandler",
    "REDOC_CONST"
]
