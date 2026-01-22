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
# CREATION DATE: 05-01-2026
# LAST Modified: 11:56:5 12-01-2026
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the module in charge of handling favicon images wether is regards the users or the admins.
# // AR
# +==== END CatFeeder =================+
"""

from .favicon_admin import FaviconAdmin
from .favicon_user import FaviconUser
from . import favicon_error_class as FAV_ERR

__all__ = [
    "FaviconAdmin",
    "FaviconUser",
    "FAV_ERR"
]
