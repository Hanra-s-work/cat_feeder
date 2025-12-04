""" 
# +==== BEGIN CatFeeder =================+
# LOGO: 
# ..............(..../\\
# ...............)..(.')
# ..............(../..)
# ...............\\(__)|
# Inspired by Joan Stark
# source https://www.asciiart.eu/
# animals/cats
# /STOP
# PROJECT: CatFeeder
# FILE: __init__.py
# CREATION DATE: 11-10-2025
# LAST Modified: 18:45:27 22-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE:
# File in charge of containing a human readable functions that will return the code corresponding to the HTTP status code.
# This is used to avoid having to remember the codes and their meanings.
# This binder also contains a function to ease the wrapping of the fastapi responses when one whishes to return a response with a status code.
# /STOP
# // AR
# +==== END CatFeeder =================+
"""


from .http_codes import HttpCodes, HCI
from .http_constants import DataTypes as HttpDataTypes, DEFAULT_MESSAGE_TYPE as HTTP_DEFAULT_TYPE

__all__ = [
    "HttpCodes",
    "HCI",
    "HttpDataTypes",
    "HTTP_DEFAULT_TYPE"
]
