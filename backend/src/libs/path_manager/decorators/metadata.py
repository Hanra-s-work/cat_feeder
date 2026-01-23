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
# FILE: metadata.py
# CREATION DATE: 23-01-2026
# LAST Modified: 20:33:38 23-01-2026
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The decorator allowing the user to set and specify their own tags for the endpoint.
# Metadata decorators for API endpoint documentation.
# 
# Provides decorators to add tags, descriptions, and other documentation metadata.
# /STOP
# // AR
# +==== END CatFeeder =================+
"""

from functools import wraps
from typing import Callable, List, Union


def set_tags(tags: Union[List[str], str]) -> Callable:
    """Set OpenAPI tags for the endpoint.

    Args:
        tags: Tag(s) to assign to the endpoint.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Normalize tags to list
        if isinstance(tags, str):
            setattr(wrapper, "_tags", [tags])
        else:
            setattr(wrapper, "_tags", list(tags))

        # Preserve any existing metadata
        if hasattr(func, '_requires_auth'):
            setattr(wrapper, "_requires_auth", getattr(func, "_requires_auth"))
        if hasattr(func, '_requires_admin'):
            setattr(
                wrapper,
                "_requires_admin",
                getattr(func, "_requires_admin")
            )
        if hasattr(func, '_public'):
            setattr(wrapper, "_public", getattr(func, "_public"))
        if hasattr(func, '_security_level'):
            setattr(
                wrapper,
                "_security_level",
                getattr(func, "_security_level")
            )
        if hasattr(func, '_description'):
            setattr(wrapper, "_description", getattr(func, "_description"))
        if hasattr(func, '_summary'):
            setattr(wrapper, "_summary", getattr(func, "_summary"))
        if hasattr(func, '_response_model'):
            setattr(
                wrapper,
                "_response_model",
                getattr(func, "_response_model")
            )

        return wrapper
    return decorator


def set_description(description: str) -> Callable:
    """Set description for the endpoint.

    Args:
        description: Description text for the endpoint.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_description", description)

        # Preserve any existing metadata
        if hasattr(func, '_requires_auth'):
            setattr(wrapper, "_requires_auth", getattr(func, "_requires_auth"))
        if hasattr(func, '_requires_admin'):
            setattr(
                wrapper,
                "_requires_admin",
                getattr(func, "_requires_admin")
            )
        if hasattr(func, '_public'):
            setattr(wrapper, "_public", getattr(func, "_public"))
        if hasattr(func, '_security_level'):
            setattr(
                wrapper,
                "_security_level",
                getattr(func, "_security_level")
            )
        if hasattr(func, '_tags'):
            setattr(wrapper, "_tags", getattr(func, "_tags"))
        if hasattr(func, '_summary'):
            setattr(wrapper, "_summary", getattr(func, "_summary"))
        if hasattr(func, '_response_model'):
            setattr(
                wrapper,
                "_response_model",
                getattr(func, "_response_model")
            )

        return wrapper
    return decorator


def set_summary(summary: str) -> Callable:
    """Set summary for the endpoint.

    Args:
        summary: Summary text for the endpoint.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_summary", summary)

        # Preserve any existing metadata
        if hasattr(func, '_requires_auth'):
            setattr(wrapper, "_requires_auth", getattr(func, "_requires_auth"))
        if hasattr(func, '_requires_admin'):
            setattr(
                wrapper,
                "_requires_admin",
                getattr(func, "_requires_admin")
            )
        if hasattr(func, '_public'):
            setattr(wrapper, "_public", getattr(func, "_public"))
        if hasattr(func, '_security_level'):
            setattr(
                wrapper,
                "_security_level",
                getattr(func, "_security_level")
            )
        if hasattr(func, '_tags'):
            setattr(wrapper, "_tags", getattr(func, "_tags"))
        if hasattr(func, '_description'):
            setattr(wrapper, "_description", getattr(func, "_description"))
        if hasattr(func, '_response_model'):
            setattr(
                wrapper,
                "_response_model",
                getattr(func, "_response_model")
            )

        return wrapper
    return decorator
