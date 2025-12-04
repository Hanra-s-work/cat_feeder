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
# CREATION DATE: 27-11-2025
# LAST Modified: 9:33:12 27-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
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
