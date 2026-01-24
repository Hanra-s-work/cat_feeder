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
# CREATION DATE: 27-11-2025
# LAST Modified: 14:51:41 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE:
# The file in charge of containing the class that will allow the server header class to have access to it's required constants.
# This also helps with response header structures.
# /STOP
# // AR
# +==== END CatFeeder =================+
"""
from .server_header import ServerHeaders

__all__ = [
    "ServerHeaders"
]
