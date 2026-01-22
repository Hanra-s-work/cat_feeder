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
# LAST Modified: 14:44:0 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Swagger Editor documentation provider.
# // AR
# +==== END CatFeeder =================+
"""

from .editor_provider import SwaggerEditorProvider
from . import editor_constants as EDITOR_CONST

__all__ = [
    "SwaggerEditorProvider",
    "EDITOR_CONST"
]
