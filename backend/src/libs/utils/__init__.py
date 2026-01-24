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
# CREATION DATE: 11-10-2025
# LAST Modified: 17:36:54 07-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge of relaying the server components to the server class so that they can be imported.
# // AR
# +==== END CatFeeder =================+
"""


from . import constants as CONST
from .password_handling import PasswordHandling
from .oauth_authentication import OAuthAuthentication

__all__ = [
    "CONST",
    "PasswordHandling",
    "OAuthAuthentication"
]
