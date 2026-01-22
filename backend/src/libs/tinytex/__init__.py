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
# CREATION DATE: 16-01-2026
# LAST Modified: 23:15:26 16-01-2026
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file in charge of exposing the dependencies located in the module
# // AR
# +==== END CatFeeder =================+
"""
from .downloader import TinyTeXInstaller

__all__ = ["TinyTeXInstaller"]
