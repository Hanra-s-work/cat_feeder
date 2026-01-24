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
# LAST Modified: 14:39:16 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
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
