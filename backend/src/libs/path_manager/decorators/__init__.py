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
# LAST Modified: 23:50:20 24-01-2026
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Decorator module initialization for API endpoint metadata management.
# /STOP
# // AR
# +==== END CatFeeder =================+
"""
from .security import auth_endpoint, admin_endpoint, public_endpoint, test_endpoint
from .metadata import (
    set_tags, set_description, set_summary, set_operation_id,
    front_end_endpoint, front_end_assets_endpoint, user_endpoint, cat_endpoint,
    oauth_endpoint, token_endpoint, system_endpoint
)
from .parameters import (
    requires_body, requires_headers, requires_auth_header, requires_bearer_auth,
    requires_basic_auth, requires_api_key, requires_query_params,
    requires_path_params, json_body, form_data, file_upload
)
from .decorator_constants import AuthScheme, CommonHeaders, ContentType


__all__ = [
    # Security decorators
    "auth_endpoint",
    "admin_endpoint",
    "public_endpoint",
    "test_endpoint",
    # Functional decorators
    "front_end_endpoint",
    "front_end_assets_endpoint",
    "user_endpoint",
    "cat_endpoint",
    "oauth_endpoint",
    "token_endpoint",
    "system_endpoint",
    # Metadata decorators
    "set_tags",
    "set_description",
    "set_summary",
    "set_operation_id",
    # Parameter decorators
    "json_body",
    "requires_bearer_auth",
    # Additional decorators
    "requires_body",
    "requires_headers",
    "requires_auth_header",
    "requires_basic_auth",
    "requires_api_key",
    "requires_query_params",
    "requires_path_params",
    "form_data",
    "file_upload",
    # Constants
    "AuthScheme",
    "CommonHeaders",
    "ContentType"
]
