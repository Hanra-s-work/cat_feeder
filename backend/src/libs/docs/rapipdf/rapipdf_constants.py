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
# FILE: rapipdf_constants.py
# CREATION DATE: 26-11-2025
# LAST Modified: 8:22:14 27-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Constants for RapiPDF documentation provider.
# // AR
# +==== END CatFeeder =================+
"""

from ...utils.constants import ASSETS_DIRECTORY
from .. import docs_constants as DOCS_CONST

# RapiPDF configuration
RAPIPDF_URL: str = "/rapipdf"
RAPIPDF_CDN_JS_ENDPOINT: str = "/rapipdf.min.js"
RAPIPDF_CDN_VERSION: str = DOCS_CONST.RAPIPDF_CDN_VERSION
# Use local hosted version - download from: https://cdn.jsdelivr.net/npm/rapipdf
RAPIPDF_CDN_JS: str = str(ASSETS_DIRECTORY / "js" / "rapipdf.min.js")

# RapiPDF style: "light", "dark"
RAPIPDF_STYLE: str = "dark"

# RapiPDF button label
RAPIPDF_BUTTON_LABEL: str = "Generate PDF Documentation"

# RapiPDF configuration options
RAPIPDF_OPTIONS: dict = {
    "include-api-list": True,
    "include-api-details": True,
    "include-security": True,
    "pdf-title": "API Documentation",
    "pdf-footer-text": "Generated with RapiPDF",
    "pdf-primary-color": "#4A90E2",
    "pdf-alternate-color": "#F5F5F5",
}
