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
# LAST Modified: 23:18:2 23-01-2026
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Decorator module initialization for API endpoint metadata management.
# /STOP
# // AR
# +==== END CatFeeder =================+
"""

try:
    from .security import auth_endpoint, admin_endpoint, public_endpoint, test_endpoint
    from .metadata import (
        set_tags, set_description, set_summary,
        user_endpoint, cat_endpoint, oauth_endpoint, token_endpoint, system_endpoint
    )
    from .parameters import (
        requires_body, requires_headers, requires_auth_header, requires_bearer_auth,
        requires_basic_auth, requires_api_key, requires_query_params,
        requires_path_params, json_body, form_data, file_upload
    )
    from .decorator_constants import AuthScheme, CommonHeaders, ContentType
except ImportError as e:
    # Fallback decorators to prevent startup failures
    def auth_endpoint(func=None):
        if func is None:
            return auth_endpoint
        setattr(func, "_requires_auth", True)
        return func

    def admin_endpoint(func=None):
        if func is None:
            return admin_endpoint
        setattr(func, "_requires_admin", True)
        return func

    def public_endpoint(func=None):
        if func is None:
            return public_endpoint
        setattr(func, "_public", True)
        return func

    def test_endpoint(func=None):
        if func is None:
            return test_endpoint
        setattr(func, "_testing_only", True)
        return func

    def user_endpoint(func):
        setattr(func, "_tags", ["Users"])
        return func

    def cat_endpoint(func):
        setattr(func, "_tags", ["Cat Management"])
        return func

    def oauth_endpoint(func):
        setattr(func, "_tags", ["OAuth"])
        return func

    def token_endpoint(func):
        setattr(func, "_tags", ["Authentication"])
        return func

    def system_endpoint(func):
        setattr(func, "_tags", ["System"])
        return func

    def json_body(description="JSON body", example=None):
        def decorator(func):
            setattr(func, "_accepts_json_body", True)
            setattr(func, "_json_body_description", description)
            if example is not None:
                setattr(func, "_json_body_example", example)
            return func
        return decorator

    def requires_bearer_auth():
        def decorator(func):
            setattr(func, "_requires_bearer_auth", True)
            return func
        return decorator

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
    # Parameter decorators
    "json_body",
    "requires_bearer_auth"
]
