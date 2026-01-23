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
# FILE: response.py
# CREATION DATE: 23-01-2026
# LAST Modified: 20:35:31 23-01-2026
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the file containing the decorators in charge of providing details for the responses of the endpoints.
# Response decorators for API endpoints.
# 
# Provides decorators to set response models and response-related metadata.
# /STOP
# // AR
# +==== END CatFeeder =================+
"""

from functools import wraps
from typing import Callable, Any, Optional


def set_response_model(model: Optional[Any]) -> Callable:
    """Set response model for the endpoint.

    Args:
        model: Pydantic model class or None to disable response model.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, "_response_model", model)

        # Preserve any existing metadata
        if hasattr(func, '_requires_auth'):
            setattr(wrapper, "_requires_auth", getattr(func, "_requires_auth"))
        if hasattr(func, '_requires_admin'):
            setattr(wrapper, "_requires_admin",
                    getattr(func, "_requires_admin"))
        if hasattr(func, '_public'):
            setattr(wrapper, "_public", getattr(func, "_public"))
        if hasattr(func, '_security_level'):
            setattr(wrapper, "_security_level",
                    getattr(func, "_security_level"))
        if hasattr(func, '_tags'):
            setattr(wrapper, "_tags", getattr(func, "_tags"))
        if hasattr(func, '_description'):
            setattr(wrapper, "_description", getattr(func, "_description"))
        if hasattr(func, '_summary'):
            setattr(wrapper, "_summary", getattr(func, "_summary"))

        return wrapper
    return decorator
