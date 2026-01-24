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
# CREATION DATE: 26-11-2025
# LAST Modified: 14:44:17 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Stoplight Elements documentation provider.
# // AR
# +==== END CatFeeder =================+
"""

from .elements_provider import StoplightElementsProvider
from . import elements_constants as ELEMENTS_CONST

__all__ = [
    "StoplightElementsProvider",
    "ELEMENTS_CONST"
]
