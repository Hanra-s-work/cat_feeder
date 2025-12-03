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
# FILE: paths_constants.py
# CREATION DATE: 22-11-2025
# LAST Modified: 18:50:29 22-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: The constants used for the path handling.
# // AR
# +==== END AsperBackend =================+
"""

from typing import List

# For Path creation variables
PATH_KEY: str = "path"
ENDPOINT_KEY: str = "endpoint"
METHOD_KEY: str = "method"
ALLOWED_METHODS: List[str] = [
    "GET", "POST",
    "PUT", "PATCH",
    "DELETE", "HEAD",
    "OPTIONS"
]
