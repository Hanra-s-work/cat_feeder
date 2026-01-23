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
# FILE: parameters.py
# CREATION DATE: 23-01-2026
# LAST Modified: 23:16:37 23-01-2026
# DESCRIPTION:
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Parameter decorators for API endpoint metadata management.
# 
# Provides decorators for documenting request parameters, headers, and body content.
# /STOP
# // AR
# +==== END CatFeeder =================+
"""
from typing import Callable, Optional, Dict, Any, Union
from functools import wraps


def _preserve_metadata(func: Callable, wrapper: Callable) -> None:
    """Helper function to preserve existing metadata attributes."""
    metadata_attrs = [
        '_requires_auth', '_requires_admin', '_public', '_testing_only',
        '_security_level', '_environment', '_description', '_summary',
        '_response_model', '_tags', '_requires_body', '_body_model',
        '_requires_headers', '_header_names', '_requires_auth_header',
        '_auth_header_name', '_requires_bearer_auth', '_requires_basic_auth',
        '_requires_api_key', '_auth_scheme', '_requires_query_params',
        '_query_params', '_requires_path_params', '_path_params',
        '_accepts_json_body', '_accepts_form_data', '_accepts_file_upload',
        '_json_body_description', '_json_body_example'
    ]

    for attr in metadata_attrs:
        if hasattr(func, attr):
            setattr(wrapper, attr, getattr(func, attr))


# Existing functions - preserve original API
def inject_query_params(description: str = "Query parameters") -> Callable:
    """Mark endpoint as requiring query parameters (legacy API).

    Args:
        description: Description of the query parameters.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_requires_query_params", True)
        setattr(wrapper, "_query_params_description", description)

        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


def inject_json_body(description: str = "JSON request body", example: Union[str, Dict[str, Any], None] = None) -> Callable:
    """Mark endpoint as accepting JSON body content (legacy API).

    Args:
        description: Description of the JSON body content.
        example: Example JSON content (as dict or JSON string).

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_accepts_json_body", True)
        setattr(wrapper, "_json_body_description", description)
        if example is not None:
            setattr(wrapper, "_json_body_example", example)

        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


def inject_request(description: str = "HTTP request") -> Callable:
    """Mark endpoint as receiving HTTP request (legacy API).

    Args:
        description: Description of the request.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_accepts_request", True)
        setattr(wrapper, "_request_description", description)

        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


def requires_body(model_class: Any = None, description: str = "Request body") -> Callable:
    """Mark endpoint as requiring a request body with optional Pydantic model.

    Args:
        model_class: Optional Pydantic model class for validation.
        description: Description of the request body.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_requires_body", True)
        setattr(wrapper, "_body_model", model_class)
        setattr(wrapper, "_body_description", description)

        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


def requires_headers(*header_names: str, description: str = "Required headers") -> Callable:
    """Mark endpoint as requiring specific headers.

    Args:
        header_names: Names of required headers.
        description: Description of the headers.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_requires_headers", True)
        setattr(wrapper, "_header_names", list(header_names))
        setattr(wrapper, "_headers_description", description)

        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


# New authentication decorators
def requires_auth_header(header_name: str = "Authorization", scheme: Optional[str] = None) -> Callable:
    """Mark endpoint as requiring authentication header.

    Args:
        header_name: Name of the auth header (default: Authorization).
        scheme: Optional auth scheme (e.g., "Bearer", "Basic").

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_requires_auth_header", True)
        setattr(wrapper, "_auth_header_name", header_name)
        if scheme:
            setattr(wrapper, "_auth_scheme", scheme)

        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


def requires_bearer_auth() -> Callable:
    """Mark endpoint as requiring Bearer token authentication.

    Specifically expects: Authorization: Bearer <token>

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_requires_bearer_auth", True)
        setattr(wrapper, "_auth_scheme", "Bearer")
        setattr(wrapper, "_auth_header_name", "Authorization")

        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


def requires_basic_auth() -> Callable:
    """Mark endpoint as requiring Basic authentication.

    Specifically expects: Authorization: Basic <credentials>

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_requires_basic_auth", True)
        setattr(wrapper, "_auth_scheme", "Basic")
        setattr(wrapper, "_auth_header_name", "Authorization")

        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


def requires_api_key(header_name: str = "X-API-Key") -> Callable:
    """Mark endpoint as requiring API key authentication.

    Args:
        header_name: Name of the API key header (default: X-API-Key).

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_requires_api_key", True)
        setattr(wrapper, "_auth_scheme", "API-Key")
        setattr(wrapper, "_auth_header_name", header_name)

        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


def requires_query_params(**params: str) -> Callable:
    """Mark endpoint as requiring specific query parameters.

    Args:
        params: Query parameter names and their descriptions.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_requires_query_params", True)
        setattr(wrapper, "_query_params", dict(params))

        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


def requires_path_params(**params: str) -> Callable:
    """Mark endpoint as requiring specific path parameters.

    Args:
        params: Path parameter names and their descriptions.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_requires_path_params", True)
        setattr(wrapper, "_path_params", dict(params))

        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


# Aliased functions for new naming convention
def json_body(description: str = "JSON request body", example: Union[str, Dict[str, Any], None] = None) -> Callable:
    """Mark endpoint as accepting JSON body content (alias for inject_json_body).

    Args:
        description: Description of the JSON body content.
        example: Example JSON content (as dict or JSON string).

    Returns:
        Decorator function.
    """
    return inject_json_body(description, example)


def form_data(description: str = "Form data") -> Callable:
    """Mark endpoint as accepting form data.

    Args:
        description: Description of the form data.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_accepts_form_data", True)
        setattr(wrapper, "_form_data_description", description)

        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


def file_upload(description: str = "File upload") -> Callable:
    """Mark endpoint as accepting file uploads.

    Args:
        description: Description of the file upload.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_accepts_file_upload", True)
        setattr(wrapper, "_file_upload_description", description)

        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator
