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
# CREATION DATE: 15-11-2025
# LAST Modified: 14:51:22 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the redis interface meant to be used by the sql library so that it can ligthen the weight on the running database of the project.
# // AR
# +==== END CatFeeder =================+
"""

from .redis_instance import RedisCaching
from .redis_args import RedisArgs, build_redis_args
from . import redis_constants as REDIS_CONST

__all__ = [
    "RedisCaching",
    "RedisArgs",
    "build_redis_args",
    "REDIS_CONST"
]
