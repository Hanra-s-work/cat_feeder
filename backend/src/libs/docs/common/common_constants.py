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
# FILE: common_constants.py
# CREATION DATE: 26-11-2025
# LAST Modified: 7:1:37 26-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Common constants and utilities for all documentation providers.
# // AR
# +==== END CatFeeder =================+
"""

from typing import Optional

# CDN base URLs (common across multiple providers)
CDN_UNPKG_BASE: str = "https://unpkg.com"
CDN_JSDELIVR_BASE: str = "https://cdn.jsdelivr.net"
CDN_CDNJS_BASE: str = "https://cdnjs.cloudflare.com"

# Common HTML document elements
HTML_DOCTYPE: str = "<!DOCTYPE html>"
HTML_META_CHARSET: str = '<meta charset="utf-8">'
HTML_META_VIEWPORT: str = '<meta name="viewport" content="width=device-width, initial-scale=1">'


def create_html_page(
    title: str,
    body_content: str,
    head_extra: str = "",
    body_attributes: str = ""
) -> str:
    """Create a complete HTML page with common structure.

    Args:
        title (str): The page title.
        body_content (str): The HTML content for the body.
        head_extra (str, optional): Additional head elements. Defaults to "".
        body_attributes (str, optional): Additional body tag attributes. Defaults to "".

    Returns:
        str: Complete HTML page as a string.
    """
    return f"""{HTML_DOCTYPE}
<html lang="en">
<head>
    {HTML_META_CHARSET}
    {HTML_META_VIEWPORT}
    <title>{title}</title>
    {head_extra}
</head>
<body{' ' + body_attributes if body_attributes else ''}>
    {body_content}
</body>
</html>"""


def create_cdn_script_tag(url: str, attributes: Optional[str] = None) -> str:
    """Create a script tag for CDN resources.

    Args:
        url (str): The CDN URL for the script.
        attributes (Optional[str], optional): Additional script attributes. Defaults to None.

    Returns:
        str: HTML script tag as a string.
    """
    attr_str = f" {attributes}" if attributes else ""
    return f'<script src="{url}"{attr_str}></script>'


def create_cdn_link_tag(url: str, rel: str = "stylesheet", attributes: Optional[str] = None) -> str:
    """Create a link tag for CDN resources.

    Args:
        url (str): The CDN URL for the resource.
        rel (str, optional): The rel attribute value. Defaults to "stylesheet".
        attributes (Optional[str], optional): Additional link attributes. Defaults to None.

    Returns:
        str: HTML link tag as a string.
    """
    attr_str = f" {attributes}" if attributes else ""
    return f'<link rel="{rel}" href="{url}"{attr_str}>'
