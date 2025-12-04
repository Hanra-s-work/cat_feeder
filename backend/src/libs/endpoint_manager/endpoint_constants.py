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
# FILE: constants.py
# CREATION DATE: 11-10-2025
# LAST Modified: 7:25:42 04-12-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The constants file in charge of storing the constants for the endpoints.
# // AR
# +==== END CatFeeder =================+
"""
from display_tty import Disp, initialise_logger
from ..config import TOMLLoader


IDISP: Disp = initialise_logger("Endpoint Constants", False)

# toml config file
TOML: TOMLLoader = TOMLLoader()

# Test configuration
TEST_ENABLE_TESTING_ENDPOINTS = TOML.get_toml_variable(
    "Test", "enable_testing_endpoints", False
)
