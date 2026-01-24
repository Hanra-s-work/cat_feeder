r"""
# +==== BEGIN CatFeeder =================+
# LOGO:
# ..............(..../\
# ...............)..(.')
# ..............(../..)
# ...............\(__)|
# Inspired by Joan Stark
# source https://www.asciiart.eu/
# animals/cats
# /STOP
# PROJECT: CatFeeder
# FILE: __init__.py
# CREATION DATE: 22-11-2025
# LAST Modified: 20:42:12 23-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file in charge of exposing the endpoint for handling the paths that will be passed to the server.
# // AR
# +==== END CatFeeder =================+
"""

from .path_manager import PathManager
from . import decorators

ServerPaths = PathManager

__all__ = [
    "PathManager",
    "ServerPaths",
    "decorators"
]
