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
# CREATION DATE: 11-10-2025
# LAST Modified: 15:26:15 11-10-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge or referencing the boilerplate classes for the server.
# // AR
# +==== END CatFeeder =================+
"""

from .responses import BoilerplateResponses
from .incoming import BoilerplateIncoming
from .non_web import BoilerplateNonHTTP

__all__ = [
    "BoilerplateResponses",
    "BoilerplateIncoming",
    "BoilerplateNonHTTP"
]
