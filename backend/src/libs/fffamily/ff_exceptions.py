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
# FILE: ff_exceptions.py
# CREATION DATE: 19-11-2025
# LAST Modified: 14:50:47 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The exceptions that could be raised by the downloader.
# // AR
# +==== END CatFeeder =================+
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
