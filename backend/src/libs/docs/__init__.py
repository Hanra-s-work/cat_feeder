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
# CREATION DATE: 26-11-2025
# LAST Modified: 14:46:8 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The module in charge of handling the different types of documentation available.
# // AR
# +==== END CatFeeder =================+
"""

from .docs_handler import DocumentationHandler
from . import docs_constants as DOCS_CONST
from .docs_constants import DocumentationProvider

DocsHandler = DocumentationHandler
DOCUMENTATION_CONST = DOCS_CONST

__all__ = [
    "DocumentationHandler",
    "DocsHandler",
    "DOCUMENTATION_CONST",
    "DOCS_CONST",
    "DocumentationProvider"
]
