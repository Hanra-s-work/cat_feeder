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
# FILE: rapidoc_constants.py
# CREATION DATE: 26-11-2025
# LAST Modified: 14:44:55 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Constants for RapiDoc documentation provider.
# // AR
# +==== END CatFeeder =================+
"""

from .. import docs_constants as DOCS_CONST

# RapiDoc configuration
RAPIDOC_URL: str = "/rapidoc"
RAPIDOC_CDN_VERSION: str = DOCS_CONST.RAPIDOC_CDN_VERSION
RAPIDOC_CDN_URL: str = f"https://unpkg.com/rapidoc@{RAPIDOC_CDN_VERSION}/dist/rapidoc-min.js"

# RapiDoc layout options: "row", "column", "focused"
RAPIDOC_LAYOUT: str = "row"

# RapiDoc theme: "light", "dark"
RAPIDOC_THEME: str = "dark"

# RapiDoc render style: "read", "view", "focused"
RAPIDOC_RENDER_STYLE: str = "view"

# RapiDoc schema style: "tree", "table"
RAPIDOC_SCHEMA_STYLE: str = "tree"

# Additional RapiDoc options
RAPIDOC_OPTIONS: dict = {
    "sort-tags": "true",
    "sort-endpoints-by": "path",
    "show-header": "true",
    "allow-authentication": "true",
    "allow-server-selection": "true",
    "allow-api-list-style-selection": "true",
    "show-info": "true",
    "show-components": "true",
    "response-area-height": "400px",
    "fill-request-fields-with-example": "true",
    "persist-auth": "true",
}
