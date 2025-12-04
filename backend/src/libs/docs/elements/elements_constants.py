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
# FILE: elements_constants.py
# CREATION DATE: 26-11-2025
# LAST Modified: 5:20:46 26-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Constants for Stoplight Elements documentation provider.
# // AR
# +==== END CatFeeder =================+
"""

from .. import docs_constants as DOCS_CONST

# Stoplight Elements configuration
ELEMENTS_URL: str = "/elements"
ELEMENTS_CDN_VERSION: str = DOCS_CONST.ELEMENTS_CDN_VERSION
ELEMENTS_CDN_JS: str = f"https://unpkg.com/@stoplight/elements@{ELEMENTS_CDN_VERSION}/web-components.min.js"
ELEMENTS_CDN_CSS: str = f"https://unpkg.com/@stoplight/elements@{ELEMENTS_CDN_VERSION}/styles.min.css"

# Elements layout: "sidebar", "stacked"
ELEMENTS_LAYOUT: str = "sidebar"

# Elements router: "hash", "memory", "history"
ELEMENTS_ROUTER: str = "hash"

# Elements configuration options
ELEMENTS_OPTIONS: dict = {
    "hideTryIt": False,
    "hideSchemas": False,
    "hideInternal": False,
    "hideExport": False,
    "tryItCredentialsPolicy": "include",
}
