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
# CREATION DATE: 22-11-2025
# LAST Modified: 18:58:1 22-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file in charge of exposing the endpoint for handling the paths that will be passed to the server.
# // AR
# +==== END CatFeeder =================+
"""

from .path_manager import PathManager

ServerPaths = PathManager

__all__ = [
    "PathManager",
    "ServerPaths"
]
