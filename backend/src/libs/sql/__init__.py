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
# LAST Modified: 14:51:55 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file allowing the code for the sql management files to be imported seamlessly.
# // AR
# +==== END CatFeeder =================+
"""

from .sql_injection import SQLInjection
from .sql_constants import TARGET
from .sql_manager import SQL

__all__ = [
    # SQL API
    "TARGET",
    "SQLInjection",
    "SQL"
]

"""
Module: __init__.py

This module initializes the SQL management package, allowing seamless imports of key components such as:
- `SQLInjection`: Provides SQL injection protection utilities.
- `TARGET`: Constants for SQL operations.
- `SQL`: Core SQL management class.

Exports:
    TARGET, SQLInjection, SQL
"""
