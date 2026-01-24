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
# LAST Modified: 1:26:25 24-01-2026
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Decorator module initialization for API endpoint metadata management.
# /STOP
# // AR
# +==== END CatFeeder =================+
"""
from display_tty import Disp, initialise_logger
try:
    IDISP: Disp = initialise_logger("decorators_init", False)
except Exception:
    pass  # Logger initialization failed; proceed without logging
try:
    IDISP.log_info("Importing decorators...")
except NameError:
    # Logger not initialized yet; skip logging
    pass
from .security import auth_endpoint, admin_endpoint, public_endpoint, test_endpoint
from .metadata import (
    set_tags, set_description, set_summary, set_operation_id,
    user_endpoint, cat_endpoint, oauth_endpoint, token_endpoint, system_endpoint
)
from .parameters import (
    requires_body, requires_headers, requires_auth_header, requires_bearer_auth,
    requires_basic_auth, requires_api_key, requires_query_params,
    requires_path_params, json_body, form_data, file_upload
)
from .decorator_constants import AuthScheme, CommonHeaders, ContentType
try:
    IDISP.log_info("Decorators imported successfully.")
except NameError:
    # Logger not initialized yet; skip logging
    pass

__all__ = [
    # Security decorators
    "auth_endpoint",
    "admin_endpoint",
    "public_endpoint",
    "test_endpoint",
    # Functional decorators
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
