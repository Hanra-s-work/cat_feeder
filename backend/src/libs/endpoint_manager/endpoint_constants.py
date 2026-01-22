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
# LAST Modified: 20:55:1 12-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The constants file in charge of storing the constants for the endpoints.
# // AR
# +==== END CatFeeder =================+
"""
from typing import Tuple
from display_tty import Disp, initialise_logger
from ..config import TOMLLoader


IDISP: Disp = initialise_logger("Endpoint Constants", False)

# toml config file
TOML: TOMLLoader = TOMLLoader()

# Test configuration
TEST_ENABLE_TESTING_ENDPOINTS = TOML.get_toml_variable(
    "Test", "enable_testing_endpoints", False
)

WORDS: Tuple[str, ...] = ()
WORDS_LENGTH: int = 0

DEFAULT_NAME_WORD_COUNT: int = 4
DEFAULT_NAME_LENGTH: int = 12
DEFAULT_NAME_LINK_CHARACTER: str = "-"
