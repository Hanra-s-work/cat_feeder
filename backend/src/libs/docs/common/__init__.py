""" 
# +==== BEGIN AsperBackend =================+
# LOGO: 
# ..........####...####..........
# ......###.....#.#########......
# ....##........#.###########....
# ...#..........#.############...
# ...#..........#.#####.######...
# ..#.....##....#.###..#...####..
# .#.....#.##...#.##..##########.
# #.....##########....##...######
# #.....#...##..#.##..####.######
# .#...##....##.#.##..###..#####.
# ..#.##......#.#.####...######..
# ..#...........#.#############..
# ..#...........#.#############..
# ...##.........#.############...
# ......#.......#.#########......
# .......#......#.########.......
# .........#####...#####.........
# /STOP
# PROJECT: AsperBackend
# FILE: __init__.py
# CREATION DATE: 26-11-2025
# LAST Modified: 26-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: Common utilities and constants for documentation providers.
# // AR
# +==== END AsperBackend =================+
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
