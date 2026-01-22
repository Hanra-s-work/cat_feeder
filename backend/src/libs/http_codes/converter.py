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
# FILE: converter.py
# CREATION DATE: 14-01-2026
# LAST Modified: 23:43:25 16-01-2026
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is a python class that aims to convert received data types into other when the type is either not universally supported by browsers or to big to store. These are on demand functions, this means that they don't execute unless the endpoint calls them.
# // AR
# +==== END CatFeeder =================+
"""
from typing import Optional
from display_tty import Disp, initialise_logger


from .http_constants import DataTypes, MEDIA_TYPES
from .converters import (
    CONV_CONST,
    BytesToBase, ImageToImage,
    VideoToVideo, AudioToAudio,
    DocumentToDocument, ArchiveToArchive,
    FontToFont,
)

from ..utils import CONST
from ..core import FinalClass


class Converter(metaclass=FinalClass):
    """_summary_
    This class contains methods to convert data types into other formats.
    """

    disp: Disp = initialise_logger(__qualname__, CONST.DEBUG)

    _instance: Optional["Converter"] = None

    def __new__(cls) -> "Converter":
        if cls._instance is None:
            cls._instance = super(Converter, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.disp.log_debug("Initialising...")
        self.disp.log_debug("Initialising ImageToImage...")
        self.iti: ImageToImage = ImageToImage()
        self.disp.log_debug("Initialising BytesToBase...")
        self.btb: BytesToBase = BytesToBase()
        self.disp.log_debug("Initialising VideoToVideo...")
        self.vtv: VideoToVideo = VideoToVideo()
        self.disp.log_debug("Initialising AudioToAudio...")
        self.ata: AudioToAudio = AudioToAudio()
        self.disp.log_debug("Initialising DocumentToDocument...")
        self.dtd: DocumentToDocument = DocumentToDocument()
        self.disp.log_debug("Initialising ArchiveToArchive...")
        self.artoar: ArchiveToArchive = ArchiveToArchive()
        self.disp.log_debug("Initialising FontToFont...")
        self.ftf: FontToFont = FontToFont()
        self.disp.log_debug("Setting up conversion references...")
        self.disp.log_debug("Initialised.")

    def __call__(self, data: bytes, from_type: DataTypes) -> CONV_CONST.ConversionResult:
        return self.convert(data, from_type)

    def _no_conversion_needed(self, data: bytes, from_type: DataTypes) -> CONV_CONST.ConversionResult:
        """_summary_
        Handle cases where no conversion is needed.
        Args:
            data (bytes): The original data.
            from_type (DataTypes): The original data type.
        Returns:
            CONV_CONST.ConversionResult: The result indicating no conversion was performed.
        """
        return CONV_CONST.ConversionResult(
            data=data,
            converted=False,
            from_type=from_type,
            to_type=from_type,
            result=data
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
        if not MEDIA_TYPES.needs_conversion(from_type):
            return self._no_conversion_needed(data, from_type)
        if not MEDIA_TYPES.get_conversion_target(from_type):
            return self._no_conversion_needed(data, from_type)
        if MEDIA_TYPES.is_base_type(from_type):
            return self.btb(data, from_type)
        if MEDIA_TYPES.is_image(from_type):
            return self.iti(data, from_type)
        if MEDIA_TYPES.is_video(from_type):
            return self.vtv(data, from_type)
        if MEDIA_TYPES.is_audio(from_type):
            return self.ata(data, from_type)
        if MEDIA_TYPES.is_document(from_type):
            return self.dtd(data, from_type)
        if MEDIA_TYPES.is_archive(from_type):
            return self.artoar(data, from_type)
        if MEDIA_TYPES.is_font(from_type):
            return self.ftf(data, from_type)
        if MEDIA_TYPES.is_binary(from_type):
            return self._no_conversion_needed(data, from_type)
        return self._no_conversion_needed(data, from_type)
