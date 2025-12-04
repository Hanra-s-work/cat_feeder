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
# FILE: __init__.py
# CREATION DATE: 11-10-2025
# LAST Modified: 7:16:6 04-12-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file in charge of referencing the python files for the server.
# // AR
# +==== END CatFeeder =================+
"""


if __name__ != "__main__":
    from .libs import HCI, HttpCodes, Server, CONST

    __all__ = [
        "HCI",
        "HttpCodes",
        "Server",
        "CONST"
    ]
else:
    print("Please run python3 ./src")
