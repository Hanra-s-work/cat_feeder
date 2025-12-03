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
# FILE: constants.py
# CREATION DATE: 11-10-2025
# LAST Modified: 16:37:32 30-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: The constants file in charge of storing the constants for the endpoints.
# // AR
# +==== END AsperBackend =================+
"""
from typing import Any
import toml
from display_tty import Disp, initialise_logger
IDISP: Disp = initialise_logger("Endpoint Constants", False)

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


# Test configuration
TEST_ENABLE_TESTING_ENDPOINTS = _get_toml_variable(
    TOML_CONF, "Test", "enable_testing_endpoints", False
)
