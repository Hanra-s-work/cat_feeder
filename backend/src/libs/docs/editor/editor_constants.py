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
# FILE: editor_constants.py
# CREATION DATE: 26-11-2025
# LAST Modified: 14:44:4 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Constants for Swagger Editor documentation provider.
# // AR
# +==== END CatFeeder =================+
"""

# API Editor configuration
EDITOR_URL: str = "/editor"
EDITOR_CDN_VERSION: str = "5.10.5"  # Using Swagger UI for reliability
EDITOR_CDN_BASE: str = f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{EDITOR_CDN_VERSION}"
EDITOR_CDN_CSS: str = f"{EDITOR_CDN_BASE}/swagger-ui.css"
EDITOR_CDN_JS: str = f"{EDITOR_CDN_BASE}/swagger-ui-bundle.js"
EDITOR_CDN_PRESET: str = f"{EDITOR_CDN_BASE}/swagger-ui-standalone-preset.js"

# Editor configuration options
EDITOR_OPTIONS: dict = {
    "deepLinking": True,
    "displayOperationId": True,
    "displayRequestDuration": True,
    "filter": True,
    "showExtensions": True,
    "showCommonExtensions": True,
    "tryItOutEnabled": True,
    "layout": "BaseLayout",
}
