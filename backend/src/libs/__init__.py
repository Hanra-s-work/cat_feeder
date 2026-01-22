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
# LAST Modified: 14:53:23 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file in charge of referencing the python files required for the server in a way that can be imported as a library as well as called directly.
# // AR
# +==== END CatFeeder =================+
"""


from .utils import CONST
from .http_codes import HCI, HttpCodes
from .server import Server
from .core import FinalClass

__all__ = [
    "HCI",
    "HttpCodes",
    "CONST",
    "Server",
    "FinalClass"
]
