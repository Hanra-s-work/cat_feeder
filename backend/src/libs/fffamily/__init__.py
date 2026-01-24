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
# CREATION DATE: 19-11-2025
# LAST Modified: 14:50:16 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The ff family binary downloader.
# // AR
# +==== END CatFeeder =================+
"""

from .ff_downloader import FFMPEGDownloader

__all__ = [
    "FFMPEGDownloader"
]
