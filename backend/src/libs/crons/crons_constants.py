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
# FILE: crons_constants.py
# CREATION DATE: 19-11-2025
# LAST Modified: 12:12:38 19-11-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: The constants used for the cron library.
# // AR
# +==== END AsperBackend =================+
"""

from typing import Any

import toml
from display_tty import Disp, initialise_logger
IDISP: Disp = initialise_logger("Crons Constants", False)

# toml config file
TOML_CONF = toml.load("config.toml")


def _get_toml_variable(toml_conf: dict, section: str, key: str, default=None) -> Any:
    """
    Get the value of a configuration variable from the TOML file.

    Args:
        toml_conf (dict): The loaded TOML configuration as a dictionary.
        section (str): The section of the TOML file to search in.
        key (str): The key within the section to fetch.
        default: The default value to return if the key is not found. Defaults to None.

    Returns:
        str: The value of the configuration variable, or the default value if the key is not found.

    Raises:
        KeyError: If the section is not found in the TOML configuration.
    """
    try:
        keys = section.split('.')
        current_section = toml_conf

        for k in keys:
            if k in current_section:
                current_section = current_section[k]
            else:
                raise KeyError(
                    f"Section '{section}' not found in TOML configuration."
                )

        if key in current_section:
            msg = f"current_section[{key}] = {current_section[key]} : "
            msg += f"{type(current_section[key])}"
            IDISP.log_debug(msg, "_get_toml_variable")
            if current_section[key] == "none":
                IDISP.log_debug(
                    "The value none has been converted to None.",
                    "_get_toml_variable"
                )
                return None
            return current_section[key]
        if default is None:
            msg = f"Key '{key}' not found in section '{section}' "
            msg += "of TOML configuration."
            raise KeyError(msg)
        return default

    except KeyError as e:
        IDISP.log_warning(f"{e}", "_get_toml_variable")
        return default


# Enable debugging for the functions in the constants file.
IDISP.update_disp_debug(_get_toml_variable(
    TOML_CONF, "Server_configuration.debug_mode", "debug", False
))

# TOML variables
# |- Cron settings
CLEAN_TOKENS = _get_toml_variable(TOML_CONF, "Crons", "clean_tokens", True)
CLEAN_TOKENS_INTERVAL = int(_get_toml_variable(
    TOML_CONF, "Crons", "clean_tokens_interval", 1800
))
ENABLE_TEST_CRONS = _get_toml_variable(
    TOML_CONF, "Crons", "enable_test_crons", False
)
TEST_CRONS_INTERVAL = int(_get_toml_variable(
    TOML_CONF, "Crons", "test_cron_interval", 200
))
CHECK_ACTIONS_INTERVAL = int(_get_toml_variable(
    TOML_CONF, "Crons", "check_actions_interval", 300
))
CLEAN_VERIFICATION = _get_toml_variable(
    TOML_CONF, "Crons", "clean_verification", True
)
CLEAN_VERIFICATION_INTERVAL = _get_toml_variable(
    TOML_CONF, "Crons", "clean_verification_interval", 900
)
RENEW_OATH_TOKENS = _get_toml_variable(
    TOML_CONF, "Crons", "renew_oath_tokens", True
)
RENEW_OATH_TOKENS_INTERVAL = _get_toml_variable(
    TOML_CONF, "Crons", "renew_oath_tokens_interval", 1800
)
