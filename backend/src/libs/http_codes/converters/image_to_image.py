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
# FILE: image_to_image.py
# CREATION DATE: 15-01-2026
# LAST Modified: 6:13:53 15-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file containing the code for converting unusual image formats to more common ones.
# // AR
# +==== END CatFeeder =================+
"""

from io import BytesIO
from typing import Optional

from PIL import Image
from pillow_heif import register_heif_opener

from display_tty import Disp, initialise_logger

from .aliases import PILLOW_FORMAT_ALIASES
from . import converters_constants as CONV_CONST

from ..http_constants import DataTypes, MEDIA_TYPES

from ...core import FinalClass
from ...utils import CONST


class ImageToImage(metaclass=FinalClass):
    """Class used to convert images from one format to another using Pillow."""

    disp: Disp = initialise_logger(__qualname__, CONST.DEBUG)

    _instance: Optional["ImageToImage"] = None

    def __new__(cls) -> "ImageToImage":
        if cls._instance is None:
            cls._instance = super(ImageToImage, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.disp.log_debug("Initialising...")
        self.disp.log_debug("Acquireing Pillow pointer...")
        self.pillow = Image
        self.disp.log_debug("Registering HEIF pillow support...")
        register_heif_opener()
        self.disp.log_debug("Initialised.")

    def __call__(self, data: bytes, source_format: DataTypes) -> CONV_CONST.ConversionResult:
        return self.image_to_image(data, source_format)

    def image_to_image(self, data: bytes, source_format: DataTypes) -> CONV_CONST.ConversionResult:
        """_summary_
        Convert image data from one format to another using Pillow.
        Args:
            data (bytes): The image data to convert.
            source_format (DataTypes): The original image format.
        Returns:
            ConversionResult: The converted image data in a contained dataclass.
        """
        converted_data: Optional[bytes] = None
        destination_format = MEDIA_TYPES.get_conversion_target(source_format)
        if destination_format is None:
            return CONV_CONST.ConversionResult(
                data=data,
                converted=False,
                from_type=source_format,
                to_type=source_format,
                result=None
            )
        if source_format == destination_format:
            return CONV_CONST.ConversionResult(
                data=data,
                converted=False,
                from_type=source_format,
                to_type=source_format,
                result=data
            )
        pillow_format: Optional[str] = PILLOW_FORMAT_ALIASES.get(
            destination_format
        )
        if pillow_format is None:
            self.disp.log_warning(
                f"No Pillow alias for {destination_format}, skipping conversion"
            )
            return CONV_CONST.ConversionResult(
                data=data,
                converted=False,
                from_type=source_format,
                to_type=destination_format,
                result=data
            )
        try:
            with Image.open(BytesIO(data)) as img:
                output_buffer = BytesIO()
                img.save(
                    output_buffer,
                    format=pillow_format or destination_format.name
                )
                converted_data = output_buffer.getvalue()
            return CONV_CONST.ConversionResult(
                data=data,
                converted=True,
                from_type=source_format,
                to_type=destination_format,
                result=converted_data
            )
        except Exception as e:
            self.disp.log_error(f"Image conversion error: {e}")
            return CONV_CONST.ConversionResult(
                data=data,
                converted=False,
                from_type=source_format,
                to_type=destination_format,
                result=None
            )
