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
# FILE: image_to_image.py
# CREATION DATE: 15-01-2026
# LAST Modified: 4:12:11 15-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file containing the code for converting bytes to a base of the user's choice.
# // AR
# +==== END CatFeeder =================+
"""

import base64
from typing import Optional, Dict, Callable

from display_tty import Disp, initialise_logger

from . import converters_constants as CONV_CONST

from ..http_constants import DataTypes, CONVERSION_TARGETS

from ...core import FinalClass
from ...utils import CONST


class BytesToBase(metaclass=FinalClass):
    """Class used to convert images from one format to another using Pillow."""

    disp: Disp = initialise_logger(__qualname__, CONST.DEBUG)

    _instance: Optional["BytesToBase"] = None

    def __new__(cls) -> "BytesToBase":
        if cls._instance is None:
            cls._instance = super(BytesToBase, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.disp.log_debug("Initialising...")
        self._cls_reference: Dict[DataTypes, Callable[[bytes], str]] = {
            DataTypes.BASE16: self.bytes_to_base16,
            DataTypes.BASE32: self.bytes_to_base32,
            DataTypes.BASE64: self.bytes_to_base64,
            DataTypes.BASE85: self.bytes_to_base85,
        }
        self.disp.log_debug("Initialised.")

    def __call__(self, data: bytes, source_format: DataTypes) -> CONV_CONST.ConversionResult:
        return self.convert(data, source_format)

    def _convert(self, data: bytes, from_type: DataTypes, to_type: DataTypes) -> CONV_CONST.ConversionResult:
        """_summary_
        Internal method to convert data from one type to another.
        Args:
            data (bytes): The data to convert.
            from_type (str): The original data type.
            to_type (str): The target data type.
        Returns:
            ConversionResult: The converted data in a contained dataclass.
        """
        func = self._cls_reference.get(to_type)
        if from_type == DataTypes.BYTES and func:
            return CONV_CONST.ConversionResult(
                data=data,
                converted=True,
                from_type=from_type,
                to_type=to_type,
                result=func(data)
            )
        return CONV_CONST.ConversionResult(
            data=data,
            converted=False,
            from_type=from_type,
            to_type=to_type,
            result=None
        )

    def convert(self, data: bytes, from_type: DataTypes) -> CONV_CONST.ConversionResult:
        """_summary_
        Convert data from one type to another.
        Args:
            data (bytes): The data to convert.
            from_type (str): The original data type.
            to_type (str): The target data type.
        Returns:
            bytes: The converted data.
        """
        target = CONVERSION_TARGETS.get(from_type)
        resp = CONV_CONST.ConversionResult(
            data=data,
            converted=False,
            from_type=from_type,
            to_type=target or from_type,
            result=None
        )
        if target:
            return self._convert(data, from_type, target)
        return resp

    @staticmethod
    def bytes_to_base85(data: bytes) -> str:
        """_summary_
        Convert bytes data to a base85 encoded string.
        Args:
            data (bytes): The bytes data to convert.
        Returns:
            str: The base85 encoded string.
        """
        return base64.b85encode(data).decode('utf-8')

    @staticmethod
    def bytes_to_base64(data: bytes) -> str:
        """_summary_
        Convert bytes data to a base64 encoded string.
        Args:
            data (bytes): The bytes data to convert.
        Returns:
            str: The base64 encoded string.
        """
        return base64.b64encode(data).decode('utf-8')

    @staticmethod
    def bytes_to_base32(data: bytes) -> str:
        """_summary_
        Convert bytes data to a base32 encoded string.
        Args:
            data (bytes): The bytes data to convert.
        Returns:
            str: The base32 encoded string.
        """
        return base64.b32encode(data).decode('utf-8')

    @staticmethod
    def bytes_to_base16(data: bytes) -> str:
        """_summary_
        Convert bytes data to a base16 encoded string.
        Args:
            data (bytes): The bytes data to convert.
        Returns:
            str: The base16 encoded string.
        """
        return base64.b16encode(data).decode('utf-8')
