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
# FILE: redoc_constants.py
# CREATION DATE: 26-11-2025
# LAST Modified: 5:2:35 26-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: The constants used in the redoc class.
# // AR
# +==== END AsperBackend =================+
"""

from .. import docs_constants as DOCS_CONST

# ReDoc configuration
REDOC_URL: str = "/redoc"

# Re-export from docs_constants for backward compatibility
OPENAPI_URL: str = DOCS_CONST.OPENAPI_URL
API_TITLE: str = DOCS_CONST.OPENAPI_TITLE
API_VERSION: str = DOCS_CONST.OPENAPI_VERSION
API_DESCRIPTION: str = DOCS_CONST.OPENAPI_DESCRIPTION

# ReDoc options
REDOC_OPTIONS: dict = {
    "disableSearch": False,
    "expandResponses": "200,201",
    "hideDownloadButton": False,
    "hideHostname": False,
    "hideSingleRequestSampleTab": False,
    "jsonSampleExpandLevel": 2,
    "menuToggle": True,
    "nativeScrollbars": False,
    "noAutoAuth": False,
    "pathInMiddlePanel": False,
    "requiredPropsFirst": True,
    "scrollYOffset": 0,
    "sortPropsAlphabetically": True,
    "theme": {
        "colors": {
            "primary": {
                "main": "#32329f"
            }
        },
        "typography": {
            "fontSize": "14px",
            "fontFamily": "Arial, sans-serif",
            "headings": {
                "fontFamily": "Arial, sans-serif"
            }
        }
    }
}

# Re-export from docs_constants for backward compatibility
TAGS_METADATA: list = DOCS_CONST.TAGS_METADATA
CONTACT_INFO: dict = DOCS_CONST.CONTACT_INFO
LICENSE_INFO: dict = DOCS_CONST.LICENSE_INFO
SERVERS: list = DOCS_CONST.SERVERS
