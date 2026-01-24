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
# LAST Modified: 14:43:21 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge of containing the cron overlay that will allow you to set crons up to run in the background.
# // AR
# +==== END CatFeeder =================+
"""


from .crons import Crons
from .background_tasks import BackgroundTasks


__all__ = [
    "Crons",
    "BackgroundTasks"
]
