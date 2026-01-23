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
# CREATION DATE: 23-01-2026
# LAST Modified: 20:50:11 23-01-2026
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the module file that allows the endpoint decorators to be found and used throughout the program.
# Decorator module for API endpoint metadata management.

# Provides decorators for adding authentication, authorization, and documentation
# metadata to API endpoints.
# /STOP
# // AR
# +==== END CatFeeder =================+
"""

from .security import auth_endpoint, admin_endpoint, public_endpoint, test_endpoint
from .metadata import set_tags, set_description, set_summary
from .response import set_response_model

__all__ = [
    # Security decorators
    "auth_endpoint",
    "admin_endpoint",
    "public_endpoint",
    "test_endpoint",
    # Metadata decorators
    "set_tags",
    "set_description",
    "set_summary",
    # Response decorators
    "set_response_model"
]
