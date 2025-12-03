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
# FILE: ff_exceptions.py
# CREATION DATE: 19-11-2025
# LAST Modified: 0:40:29 19-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: The exceptions that could be raised by the downloader.
# // AR
# +==== END AsperBackend =================+
"""


class ArchitectureNotSupported(Exception):
    """
    This class informs the user that the system architecture they are using is not supported by this script

    Args:
        Exception (_type_): _description_
    """


class PackageNotInstalled(Exception):
    """
    This class informs the user that the ff dependency(ies) they required does not exist.

    Args:
        Exception (_type_): _description_
    """


class PackageNotSupported(Exception):
    """
    This class informs the user that the package they requested is not unsupported by this script.

    Args:
        Exception (_type_): _description_
    """
