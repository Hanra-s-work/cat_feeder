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
# FILE: image_reducer_error_class.py
# CREATION DATE: 05-01-2026
# LAST Modified: 0:21:25 08-01-20266
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE:
# This is the file in charge of providing custom classes that can be thrown as error.
# This module defines a small hierarchy of exceptions raised by the image reducer code. Use these specific exceptions to distinguish between different error conditions when opening, validating or saving images.
# /STOP
# // AR
# +==== END CatFeeder =================+
"""

from typing import Union, List, Optional


class ImageReducer(ValueError):
    """Base exception for image reducer errors.

    All custom image-reducer exceptions inherit from this class. Catching this
    base class will handle any error produced by the image reducer module.
    """


class ImageReducerInvalidImageFile(ImageReducer):
    """Raised when image bytes cannot be identified as a valid image.

    This exception is typically raised when PIL.Image.open fails with an
    UnidentifiedImageError and the input does not represent a known image format.

    Attributes:
        image_file: The file type that was provided.
        allowed_files: The expected file format(s).
    """

    def __init__(self, image_file: str, allowed_files: str):
        """Initialize ImageReducerInvalidImageFile exception.

        Arguments:
            image_file: The file type or name that was provided.
            allowed_files: The expected file format(s).
        """
        self.image_file = image_file
        self.allowed_files = allowed_files
        super().__init__(
            f"Invalid Image file/data, you provided {self.image_file} but the program expected {self.allowed_files}"
        )


class ImageReducerUnsupportedFormat(ImageReducer):
    """Raised when image format is not in the allowed formats list.

    This exception signals that the image's format (as reported by Pillow) is not
    accepted by the current configuration.

    Attributes:
        image_file: The image format that was detected.
        allowed_files: The allowed image format(s).
    """

    def __init__(self, image_file: Optional[str], allowed_files: Union[List[str], str]):
        """Initialize ImageReducerUnsupportedFormat exception.

        Arguments:
            image_file: The image format that was detected.
            allowed_files: The allowed image format(s) as list or comma-separated string.
        """
        self.image_file = image_file
        self.allowed_files = allowed_files
        if isinstance(self.allowed_files, List):
            self.allowed_files = ", ".join(self.allowed_files)
        super().__init__(
            f"Unsupported image format, you provided '{self.image_file}' but the program expected '{self.allowed_files}'"
        )


class ImageReducerTooLarge(ImageReducer):
    """Raised when image dimensions exceed the configured maximum.

    This exception indicates that either the width or height of the image is
    larger than an allowed max_dimension. The caller should request a resized
    image before retrying the operation.

    Attributes:
        width: The image width in pixels.
        height: The image height in pixels.
        max_dimension: The maximum allowed dimension in pixels.
    """

    def __init__(self, width: int, height: int, max_dimension: int):
        """Initialize ImageReducerTooLarge exception.

        Arguments:
            width: The image width in pixels.
            height: The image height in pixels.
            max_dimension: The maximum allowed dimension in pixels.
        """
        self.width = width
        self.height = height
        self.max_dimension = max_dimension
        super().__init__(
            f"Image too large ({width}x{height}), max allowed is {max_dimension}px"
        )
