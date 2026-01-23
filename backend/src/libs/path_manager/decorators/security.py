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
# FILE: security.py
# CREATION DATE: 23-01-2026
# LAST Modified: 20:49:31 23-01-2026
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the file in charge of containing the decorators used for security descriptions.
# Security decorators for API endpoints.
# 
# Provides decorators to mark endpoints with authentication and authorization requirements.
# LAST Modified: 20:49:38 23-01-2026
# // AR
# +==== END CatFeeder =================+
"""

from functools import wraps
from typing import Callable


def auth_endpoint(func: Callable) -> Callable:
    """Mark endpoint as requiring authentication.

    Args:
        func: The endpoint function to decorate.

    Returns:
        The decorated function with authentication metadata.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    # Add metadata attributes
    setattr(wrapper, "_requires_auth", True)
    setattr(wrapper, "_security_level", "auth")

    # Preserve any existing metadata
    if hasattr(func, '_requires_admin'):
        setattr(wrapper, "_requires_admin", getattr(func, "_requires_admin"))
    if hasattr(func, '_public'):
        setattr(wrapper, "_public", getattr(func, "_public"))
    if hasattr(func, '_tags'):
        setattr(wrapper, "_tags", getattr(func, "_tags"))
    if hasattr(func, '_description'):
        setattr(wrapper, "_description", getattr(func, "_description"))
    if hasattr(func, '_summary'):
        setattr(wrapper, "_summary", getattr(func, "_summary"))
    if hasattr(func, '_response_model'):
        setattr(wrapper, "_response_model", getattr(func, "_response_model"))

    return wrapper


def admin_endpoint(func: Callable) -> Callable:
    """Mark endpoint as requiring admin privileges.

    Automatically implies requires_auth as well.

    Args:
        func: The endpoint function to decorate.

    Returns:
        The decorated function with admin metadata.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    # Add metadata attributes
    setattr(wrapper, "_requires_admin", True)
    setattr(wrapper, "_requires_auth", True)  # Admin implies auth
    setattr(wrapper, "_security_level", "admin")

    # Preserve any existing metadata
    if hasattr(func, '_public'):
        setattr(wrapper, "_public", getattr(func, "_public"))
    if hasattr(func, '_tags'):
        setattr(wrapper, "_tags", getattr(func, "_tags"))
    if hasattr(func, '_description'):
        setattr(wrapper, "_description", getattr(func, "_description"))
    if hasattr(func, '_summary'):
        setattr(wrapper, "_summary", getattr(func, "_summary"))
    if hasattr(func, '_response_model'):
        setattr(wrapper, "_response_model", getattr(func, "_response_model"))

    return wrapper


def public_endpoint(func: Callable) -> Callable:
    """Mark endpoint as publicly accessible (no authentication required).

    Args:
        func: The endpoint function to decorate.

    Returns:
        The decorated function with public metadata.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    # Add metadata attributes
    setattr(wrapper, "_public", True)
    setattr(wrapper, "_security_level", "public")

    # Override any auth requirements
    setattr(wrapper, "_requires_auth", False)
    setattr(wrapper, "_requires_admin", False)

    # Preserve any existing metadata
    if hasattr(func, '_tags'):
        setattr(wrapper, "_tags", getattr(func, "_tags"))
    if hasattr(func, '_description'):
        setattr(wrapper, "_description", getattr(func, "_description"))
    if hasattr(func, '_summary'):
        setattr(wrapper, "_summary", getattr(func, "_summary"))
    if hasattr(func, '_response_model'):
        setattr(wrapper, "_response_model", getattr(func, "_response_model"))

    return wrapper


def test_endpoint(func: Callable) -> Callable:
    """Mark endpoint as testing-only (should not be available in production).

    Args:
        func: The endpoint function to decorate.

    Returns:
        The decorated function with testing metadata.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    # Add metadata attributes
    setattr(wrapper, "_testing_only", True)
    setattr(wrapper, "_environment", "testing")

    # Preserve any existing metadata
    if hasattr(func, '_requires_auth'):
        setattr(wrapper, "_requires_auth", getattr(func, "_requires_auth"))
    if hasattr(func, '_requires_admin'):
        setattr(wrapper, "_requires_admin", getattr(func, "_requires_admin"))
    if hasattr(func, '_public'):
        setattr(wrapper, "_public", getattr(func, "_public"))
    if hasattr(func, '_security_level'):
        setattr(wrapper, "_security_level", getattr(func, "_security_level"))
    if hasattr(func, '_tags'):
        setattr(wrapper, "_tags", getattr(func, "_tags"))
    if hasattr(func, '_description'):
        setattr(wrapper, "_description", getattr(func, "_description"))
    if hasattr(func, '_summary'):
        setattr(wrapper, "_summary", getattr(func, "_summary"))
    if hasattr(func, '_response_model'):
        setattr(wrapper, "_response_model", getattr(func, "_response_model"))

    return wrapper
