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
# FILE: explorer_constants.py
# CREATION DATE: 26-11-2025
# LAST Modified: 3:30:37 27-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: Constants for OpenAPI Explorer documentation provider.
# // AR
# +==== END AsperBackend =================+
"""

# OpenAPI Explorer configuration
EXPLORER_URL: str = "/explorer"
EXPLORER_CDN_VERSION: str = "5.10.5"
EXPLORER_CDN_BASE: str = f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{EXPLORER_CDN_VERSION}"
EXPLORER_CDN_CSS: str = f"{EXPLORER_CDN_BASE}/swagger-ui.css"
EXPLORER_CDN_JS: str = f"{EXPLORER_CDN_BASE}/swagger-ui-bundle.js"
EXPLORER_CDN_PRESET: str = f"{EXPLORER_CDN_BASE}/swagger-ui-standalone-preset.js"

# Explorer configuration options
EXPLORER_OPTIONS: dict = {
    "deepLinking": True,
    "displayOperationId": True,
    "displayRequestDuration": True,
    "filter": True,
    "showExtensions": True,
    "showCommonExtensions": True,
    "tryItOutEnabled": True,
    "persistAuthorization": True,
    "layout": "BaseLayout",
}
