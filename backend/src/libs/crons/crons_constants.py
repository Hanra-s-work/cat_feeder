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
# FILE: crons_constants.py
# CREATION DATE: 19-11-2025
# LAST Modified: 21:44:44 14-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The constants used for the cron library.
# // AR
# +==== END CatFeeder =================+
"""

from display_tty import Disp, initialise_logger

from ..config import TOMLLoader

IDISP: Disp = initialise_logger("Crons Constants", False)

# The TOML instance in charge of loading the toml config file
TOML = TOMLLoader()

# TOML variables
# |- Cron settings
CLEAN_TOKENS = TOML.get_toml_variable("Crons", "clean_tokens", True)
CLEAN_TOKENS_INTERVAL = int(TOML.get_toml_variable(
    "Crons", "clean_tokens_interval", 1800
))
ENABLE_TEST_CRONS = TOML.get_toml_variable(
    "Crons", "enable_test_crons", False
)
TEST_CRONS_INTERVAL = int(TOML.get_toml_variable(
    "Crons", "test_cron_interval", 200
))
CHECK_ACTIONS_INTERVAL = int(TOML.get_toml_variable(
    "Crons", "check_actions_interval", 300
))
CLEAN_VERIFICATION = TOML.get_toml_variable(
    "Crons", "clean_verification", True
)
CLEAN_VERIFICATION_INTERVAL = TOML.get_toml_variable(
    "Crons", "clean_verification_interval", 900
)
RENEW_OATH_TOKENS = TOML.get_toml_variable(
    "Crons", "renew_oath_tokens", True
)
RENEW_OATH_TOKENS_INTERVAL = TOML.get_toml_variable(
    "Crons", "renew_oath_tokens_interval", 1800
)
