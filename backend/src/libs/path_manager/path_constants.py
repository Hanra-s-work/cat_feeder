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
# FILE: paths_constants.py
# CREATION DATE: 22-11-2025
# LAST Modified: 18:50:29 22-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The constants used for the path handling.
# // AR
# +==== END CatFeeder =================+
"""

from typing import List

# For Path creation variables
PATH_KEY: str = "path"
ENDPOINT_KEY: str = "endpoint"
METHOD_KEY: str = "method"
ALLOWED_METHODS: List[str] = [
    "GET", "POST",
    "PUT", "PATCH",
    "DELETE", "HEAD",
    "OPTIONS"
]
