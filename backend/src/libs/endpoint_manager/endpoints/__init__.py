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
# CREATION DATE: 21-11-2025
# LAST Modified: 12:20:21 30-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The folder in charge of grouping the endpoints by functionality.
# The file to export every endpoints class
# /STOP
# // AR
# +==== END CatFeeder =================+
"""

from .bonus import Bonus
from .user_endpoints import UserEndpoints
from .testing_endpoints import TestingEndpoints
__all__ = [
    "Bonus",
    "UserEndpoints",
    "TestingEndpoints"
]
