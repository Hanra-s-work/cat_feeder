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
# CREATION DATE: 04-12-2025
# LAST Modified: 22:15:22 14-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE:
# The file in charge of exposing the classes and functions in the folder that the user is supposed to be able to use.
# Configuration Package
# Centralized configuration management for the Asperguide Backend.
# Provides singleton loaders for config.toml and .env files with smart path resolution.
# Usage:
#     from config import get_config, get_env
#     db_host = get_config('Database', 'host')
#     api_key = get_env('API_KEY')
# /STOP
# // AR
# +==== END CatFeeder =================+
"""

from .toml_loader import load_config, get_config, get_project_root, refresh_debug, TOMLLoader
from .env_loader import load_env, get_env, apply_env, EnvLoader

ConfigLoader = TOMLLoader

__all__ = [
    # TOML config
    'load_config',
    'get_config',
    'get_project_root',
    'refresh_debug',
    'TOMLLoader',
    'ConfigLoader',

    # Environment variables
    'load_env',
    'get_env',
    'apply_env',
    'EnvLoader',
]
