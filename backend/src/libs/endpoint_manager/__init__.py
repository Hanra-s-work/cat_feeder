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
# CREATION DATE: 11-10-2025
# LAST Modified: 14:48:35 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge of containing the code that will ease the adding of routes in the server.
# // AR
# +==== END CatFeeder =================+
"""

from .endpoint_manager import EndpointManager

Endpoints = EndpointManager

__all__ = [
    "Endpoints",
    "EndpointManager"
]
