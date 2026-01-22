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
# FILE: favicon_error_class.py
# CREATION DATE: 12-01-2026
# LAST Modified: 21:6:1 12-01-2026
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge of containing the custom errors that can be raised by the favicon classes
# // AR
# +==== END CatFeeder =================+
"""


class FaviconRuntimeError(RuntimeError):
    """Base class for favicon-related errors.
    """


class FaviconDatabaseError(FaviconRuntimeError):
    """Raised when there is an error interacting with the database for favicon operations.
    """


class FaviconNoImageReducerError(FaviconRuntimeError):
    """Raised when there is no ImageReducer instance available in the runtime manager.
    """


class FaviconImageUploadError(FaviconRuntimeError):
    """Raised when there is an error uploading an image to the storage bucket.
    """


class FaviconImagePathUpdateError(FaviconRuntimeError):
    """Raised when there is an error updating the image path in the database.
    """


class FaviconValueError(ValueError):
    """Base class for favicon-related value errors.
    """
