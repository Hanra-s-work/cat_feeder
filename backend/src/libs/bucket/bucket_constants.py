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
# FILE: bucket_constants.py
# CREATION DATE: 18-11-2025
# LAST Modified: 7:41:32 02-12-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: File in charge of containing the constants required for the bucket wrapper.
# // AR
# +==== END AsperBackend =================+
"""

import os
from typing import Optional, Dict

import dotenv
from display_tty import Disp, initialise_logger
IDISP: Disp = initialise_logger("Bucket Constants", False)

# Environement initialisation
dotenv.load_dotenv(".env")
_DOTENV = dict(dotenv.dotenv_values())
_OS_ENV = dict(os.environ)
ENV = {}
ENV.update(_OS_ENV)
ENV.update(_DOTENV)


def _get_environement_variable(environement: Dict[str, Optional[str]], variable_name: str, required: bool = True) -> str:
    """_summary_
        Get the content of an environement variable.

    Args:
        variable_name (str): _description_
        required (bool): If False, return empty string if variable not found. Defaults to True.

    Returns:
        str: _description_: the value of that variable, otherwise an exception is raised.
    """
    if environement is None:
        raise ValueError(
            "No environement file loaded."
        )
    data = environement.get(variable_name, None)
    if data is None:
        if not required:
            return ""
        raise ValueError(
            f"Variable {variable_name} not found in the environement"
        )
    return data


# S3 resource type - this never changes for S3-compatible services
BUCKET_RESSOURCE_TYPE: str = "s3"

# S3 signature version - configurable for edge cases, defaults to modern s3v4
BUCKET_SIGNATURE_VERSION: str = _get_environement_variable(
    ENV, "BUCKET_SIGNATURE_VERSION", required=False) or "s3v4"

BUCKET_HOST: str = _get_environement_variable(ENV, "BUCKET_HOST")
BUCKET_PORT: str = _get_environement_variable(
    ENV, "BUCKET_PORT", required=False)
BUCKET_USER: str = _get_environement_variable(ENV, "BUCKET_USER")
BUCKET_PASSWORD: str = _get_environement_variable(
    ENV,
    "BUCKET_PASSWORD"
)
