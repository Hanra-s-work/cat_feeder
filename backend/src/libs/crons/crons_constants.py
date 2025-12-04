"""
# +==== BEGIN CatFeeder =================+
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
# PROJECT: CatFeeder
# FILE: crons_constants.py
# CREATION DATE: 19-11-2025
# LAST Modified: 7:26:1 04-12-2025
# DESCRIPTION:
# This is the project in charge of making the connected cat feeder project work.
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

# Enable debugging for the functions in the constants file.
DEBUG_MODE: bool = TOML.get_toml_variable(
    "Server_configuration.debug_mode", "debug", False
)
IDISP.update_disp_debug(DEBUG_MODE)
TOML.disp.update_disp_debug(DEBUG_MODE)

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
