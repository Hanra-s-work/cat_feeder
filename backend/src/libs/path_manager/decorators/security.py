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
# LAST Modified: 1:12:17 24-01-2026
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Security decorators for API endpoint authentication and authorization.
# /STOP
# // AR
# +==== END CatFeeder =================+
"""

from functools import wraps
from typing import Callable

from .decorator_constants import SecurityLevel, Environment


def auth_endpoint(
    security_level: SecurityLevel = SecurityLevel.AUTHENTICATED,
    environment: Environment = Environment.ALL
) -> Callable:
    """Mark endpoint as requiring authentication.

    Args:
        security_level: Level of security required (default: AUTHENTICATED).
        environment: Environment where this applies (default: ALL).

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_requires_auth", True)
        setattr(wrapper, "_security_level", security_level.value)
        setattr(wrapper, "_environment", environment.value)

        # Preserve existing metadata
        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


def admin_endpoint(
    security_level: SecurityLevel = SecurityLevel.ADMIN,
    environment: Environment = Environment.ALL
) -> Callable:
    """Mark endpoint as requiring admin privileges.

    Args:
        security_level: Level of admin access required (default: ADMIN).
        environment: Environment where this applies (default: ALL).

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_requires_admin", True)
        setattr(wrapper, "_security_level", security_level.value)
        setattr(wrapper, "_environment", environment.value)

        # Preserve existing metadata
        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


def public_endpoint(environment: Environment = Environment.ALL) -> Callable:
    """Mark endpoint as public (no authentication required).

    Args:
        environment: Environment where this applies (default: ALL).

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_public", True)
        setattr(wrapper, "_security_level", SecurityLevel.PUBLIC.value)
        setattr(wrapper, "_environment", environment.value)

        # Preserve existing metadata
        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


def test_endpoint(environment: Environment = Environment.TESTING) -> Callable:
    """Mark endpoint as testing-only.

    Args:
        environment: Environment where this applies (default: TESTING).

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_testing_only", True)
        setattr(wrapper, "_environment", environment.value)

        # Preserve existing metadata
        _preserve_metadata(func, wrapper)
        return wrapper
    return decorator


def _preserve_metadata(func: Callable, wrapper: Callable) -> None:
    """Helper function to preserve existing metadata attributes."""
    metadata_attrs = [
        '_requires_auth', '_requires_admin', '_public', '_testing_only',
        '_security_level', '_environment', '_description', '_summary',
        '_response_model', '_tags'
    ]

    for attr in metadata_attrs:
        if hasattr(func, attr):
            setattr(wrapper, attr, getattr(func, attr))
