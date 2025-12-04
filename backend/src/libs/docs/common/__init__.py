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
# CREATION DATE: 26-11-2025
# LAST Modified: 26-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Common utilities and constants for documentation providers.
# // AR
# +==== END CatFeeder =================+
"""

from .common_constants import (
    CDN_UNPKG_BASE,
    CDN_JSDELIVR_BASE,
    CDN_CDNJS_BASE,
    HTML_DOCTYPE,
    HTML_META_CHARSET,
    HTML_META_VIEWPORT,
    create_html_page,
    create_cdn_script_tag,
    create_cdn_link_tag
)

__all__ = [
    "CDN_UNPKG_BASE",
    "CDN_JSDELIVR_BASE",
    "CDN_CDNJS_BASE",
    "HTML_DOCTYPE",
    "HTML_META_CHARSET",
    "HTML_META_VIEWPORT",
    "create_html_page",
    "create_cdn_script_tag",
    "create_cdn_link_tag"
]
