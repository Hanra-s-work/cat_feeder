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
# FILE: mail_constants.py
# CREATION DATE: 18-11-2025
# LAST Modified: 0:38:53 26-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: The file in charge of containing the constants for the mail management class.
# // AR
# +==== END AsperBackend =================+
"""

import os
from typing import Optional, Dict
import dotenv
from display_tty import Disp, initialise_logger
IDISP: Disp = initialise_logger("mail_constants", False)

# Environement initialisation
dotenv.load_dotenv(".env")
_DOTENV = dict(dotenv.dotenv_values())
_OS_ENV = dict(os.environ)
ENV = {}
ENV.update(_OS_ENV)
ENV.update(_DOTENV)


def _get_environement_variable(environement: Dict[str, Optional[str]], variable_name: str) -> str:
    """_summary_
        Get the content of an environement variable.

    Args:
        variable_name (str): _description_

    Returns:
        str: _description_: the value of that variable, otherwise an exception is raised.
    """
    if environement is None:
        raise ValueError(
            "No environement file loaded."
        )
    data = environement.get(variable_name, None)
    if data is None:
        # required for expanding the variable name
        error_msg = f"Variable {variable_name} not found in the environement"
        raise ValueError(error_msg)
    return data


SENDER_ADDRESS: str = _get_environement_variable(ENV, "SENDER_ADDRESS")
SENDER_HOST: str = _get_environement_variable(ENV, "SENDER_HOST")
SENDER_KEY: str = _get_environement_variable(ENV, "SENDER_KEY")
tmp: str = _get_environement_variable(ENV, "SENDER_PORT")
try:
    SENDER_PORT: int = int(tmp)
except ValueError as e:
    ERR_MSG: str = "Failed to retrieve the sender port as a number from the environement"
    IDISP.log_error(f"{ERR_MSG}: {e}")
    raise RuntimeError(ERR_MSG) from e
