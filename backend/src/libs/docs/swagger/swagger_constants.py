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
# FILE: swagger_constants.py
# CREATION DATE: 26-11-2025
# LAST Modified: 4:10:7 26-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: The constants used in the swagger class.
# // AR
# +==== END AsperBackend =================+
"""

from .. import docs_constants as DOCS_CONST
from ..redoc import redoc_constants as REDOC_CONST

# Swagger UI configuration
SWAGGER_URL: str = "/docs"
SWAGGER_REDIRECT_URL: str = DOCS_CONST.OAUTH2_REDIRECT_URL

# ReDoc URL (imported from redoc constants for SwaggerHandler which includes both)
REDOC_URL: str = REDOC_CONST.REDOC_URL

# Re-export from docs_constants for backward compatibility
OPENAPI_URL: str = DOCS_CONST.OPENAPI_URL
API_TITLE: str = DOCS_CONST.OPENAPI_TITLE
API_VERSION: str = DOCS_CONST.OPENAPI_VERSION
API_DESCRIPTION: str = DOCS_CONST.OPENAPI_DESCRIPTION

# Swagger UI parameters
SWAGGER_UI_PARAMETERS: dict = {
    "deepLinking": True,
    "displayRequestDuration": True,
    "docExpansion": "none",
    "filter": True,
    "showExtensions": True,
    "showCommonExtensions": True,
    "syntaxHighlight.theme": "monokai",
    "tryItOutEnabled": True,
}

# Re-export from docs_constants for backward compatibility
TAGS_METADATA: list = DOCS_CONST.TAGS_METADATA
CONTACT_INFO: dict = DOCS_CONST.CONTACT_INFO
LICENSE_INFO: dict = DOCS_CONST.LICENSE_INFO
SERVERS: list = DOCS_CONST.SERVERS
