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
# LAST Modified: 4:5:3 26-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The swagger wrapper to help inject it into the server.
# // AR
# +==== END CatFeeder =================+
"""

from .swagger_class import SwaggerHandler
from . import swagger_constants as SWAGGER_CONST

__all__ = [
    "SwaggerHandler",
    "SWAGGER_CONST"
]
