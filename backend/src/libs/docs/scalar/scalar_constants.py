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
# FILE: scalar_constants.py
# CREATION DATE: 26-11-2025
# LAST Modified: 5:20:43 26-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Constants for Scalar documentation provider.
# // AR
# +==== END CatFeeder =================+
"""

from .. import docs_constants as DOCS_CONST

# Scalar configuration
SCALAR_URL: str = "/scalar"
SCALAR_CDN_VERSION: str = DOCS_CONST.SCALAR_CDN_VERSION
SCALAR_CDN_URL: str = f"https://cdn.jsdelivr.net/npm/@scalar/api-reference@{SCALAR_CDN_VERSION}"

# Scalar theme: "default", "alternate", "moon", "purple", "solarized", "bluePlanet", "saturn", "kepler", "mars", "deepSpace"
SCALAR_THEME: str = "purple"

# Scalar layout: "modern" or "classic"
SCALAR_LAYOUT: str = "modern"

# Scalar configuration options
SCALAR_OPTIONS: dict = {
    "showSidebar": True,
    "darkMode": True,
    "hideDownloadButton": False,
    "searchHotKey": "k",
}
