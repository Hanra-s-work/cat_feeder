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
# LAST Modified: 1:32:3 17-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file containing the code for converting bytes to a base of the user's choice.
# // AR
# +==== END CatFeeder =================+
"""

from io import BytesIO
from typing import Optional

from display_tty import Disp, initialise_logger

# Audio processing library
from pydub import AudioSegment

from .aliases import AUDIO_FORMAT_ALIASES
from . import converters_constants as CONV_CONST

from ..http_constants import DataTypes, MEDIA_TYPES

from ...core import FinalClass
from ...utils import CONST
from ...fffamily import FFMPEGDownloader


class AudioToAudio(metaclass=FinalClass):
    """Class used to convert audio from one format to another using pydub/ffmpeg.

    Optimized to minimize I/O costs:
    - All conversions done in-memory using BytesIO (zero disk I/O)
    - pydub handles format detection and conversion via ffmpeg
    """

    disp: Disp = initialise_logger(__qualname__, CONST.DEBUG)

    _instance: Optional["AudioToAudio"] = None

    _ffmpeg_ensured: bool = False

    def __new__(cls) -> "AudioToAudio":
        if cls._instance is None:
            cls._instance = super(AudioToAudio, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.disp.log_debug("Initialising...")
        self.disp.log_debug("Ensuring FFMPEG is available...")
        self._ensure_ffmpeg()
        self.disp.log_debug("FFMPEG is available.")
        self.disp.log_debug("Initialised.")

    def __call__(self, data: bytes, source_format: DataTypes) -> CONV_CONST.ConversionResult:
        return self.audio_to_audio(data, source_format)

    def _ensure_ffmpeg(self) -> None:
        """Ensure that FFMPEG is downloaded and available."""
        if self._ffmpeg_ensured:
            return

        self.disp.log_debug("Ensuring FFMPEG is available...")
        FDI = FFMPEGDownloader(
            cwd=str(CONV_CONST.FF_FAMILY_PATH),
            success=CONV_CONST.SUCCESS,
            error=CONV_CONST.ERROR,
            debug=CONV_CONST.DEBUG
        )
        try:
            FDI.main()
            self._ffmpeg_ensured = True
        except Exception as e:
            self.disp.log_error(f"FFMPEG is not available: {e}")
            raise RuntimeError(
                "FFMPEG is required for audio conversion but could not be ensured."
            ) from e
        self.disp.log_debug("FFMPEG is available.")

    def get_audio_extension(self, data_type: DataTypes) -> Optional[str]:
        """
        Get the file extension for a given audio DataType.

        Args:
            data_type: The DataType to get extension for

        Returns:
            Extension string or None
        """
        return AUDIO_FORMAT_ALIASES.get(data_type)

    def _validate_conversion_params(
        self,
        data: bytes,
        source_format: DataTypes
    ) -> tuple[Optional[DataTypes], Optional[str], Optional[str]]:
        """
        Validate conversion parameters and get destination format and extensions.

        Args:
            data: The audio data to validate
            source_format: The source audio format

        Returns:
            Tuple of (destination_format, source_ext, dest_ext)
            Returns (None, None, None) if validation fails
        """
        try:
            destination_format = MEDIA_TYPES.get_conversion_target(
                source_format)
        except (AttributeError, NameError):
            destination_format = None

        if destination_format is None:
            self.disp.log_debug(f"No conversion target for {source_format}")
            return None, None, None

        if source_format == destination_format:
            self.disp.log_debug(
                f"Source and destination formats are the same: {source_format}"
            )
            return destination_format, None, None

        source_ext = self.get_audio_extension(source_format)
        dest_ext = self.get_audio_extension(destination_format)

        if not source_ext or not dest_ext:
            self.disp.log_warning(
                f"Unknown audio extension for {source_format} -> {destination_format}"
            )
            return destination_format, None, None

        return destination_format, source_ext, dest_ext

    def _convert_in_memory(
        self,
        data: bytes,
        source_format: DataTypes,
        destination_format: DataTypes,
        source_ext: str,
        dest_ext: str
    ) -> Optional[bytes]:
        """
        Perform in-memory audio conversion using pydub.
        ZERO I/O COST - everything happens in RAM via BytesIO.

        Args:
            data: Source audio data
            source_format: Source audio format
            destination_format: Destination audio format
            source_ext: Source file extension
            dest_ext: Destination file extension

        Returns:
            Converted audio data as bytes, or None if conversion failed
        """
        self.disp.log_debug(
            f"Converting in-memory (ZERO I/O): {source_format} -> {destination_format}"
        )

        try:
            # Load audio from bytes into pydub AudioSegment
            input_buffer = BytesIO(data)
            audio = AudioSegment.from_file(input_buffer, format=source_ext)

            # Export to destination format in memory
            output_buffer = BytesIO()
            audio.export(
                output_buffer,
                format=dest_ext
            )

            # Get the converted bytes
            converted_data = output_buffer.getvalue()

            self.disp.log_debug(
                f"In-memory audio conversion successful (ZERO I/O cost)"
            )
            return converted_data

        except Exception as e:
            self.disp.log_error(f"In-memory audio conversion failed: {e}")
            return None

    def _create_failed_result(
        self,
        data: bytes,
        source_format: DataTypes,
        destination_format: DataTypes,
        result: Optional[bytes] = None
    ) -> CONV_CONST.ConversionResult:
        """Create a failed conversion result."""
        return CONV_CONST.ConversionResult(
            data=data,
            converted=False,
            from_type=source_format,
            to_type=destination_format,
            result=result
        )

    def _create_success_result(
        self,
        data: bytes,
        source_format: DataTypes,
        destination_format: DataTypes,
        converted_data: bytes
    ) -> CONV_CONST.ConversionResult:
        """Create a successful conversion result."""
        return CONV_CONST.ConversionResult(
            data=data,
            converted=True,
            from_type=source_format,
            to_type=destination_format,
            result=converted_data
        )

    def _handle_validation_failure(
        self,
        data: bytes,
        source_format: DataTypes,
        destination_format: Optional[DataTypes],
        source_ext: Optional[str],
        dest_ext: Optional[str]
    ) -> Optional[CONV_CONST.ConversionResult]:
        """Handle validation failures and return appropriate result."""
        if destination_format is None:
            return self._create_failed_result(
                data, source_format, source_format, None
            )

        if source_ext is None or dest_ext is None:
            result_data = data if source_format == destination_format else data
            return self._create_failed_result(
                data, source_format, destination_format, result_data
            )

        return None

    def audio_to_audio(self, data: bytes, source_format: DataTypes) -> CONV_CONST.ConversionResult:
        """
        Convert audio data from one format to another using pydub/ffmpeg.
        All operations done in-memory (ZERO I/O cost).

        Args:
            data (bytes): The audio data to convert.
            source_format (DataTypes): The original audio format.

        Returns:
            ConversionResult: The converted audio data in a contained dataclass.
        """
        # Validate conversion parameters
        destination_format, source_ext, dest_ext = self._validate_conversion_params(
            data, source_format
        )

        # Handle validation failures
        validation_result = self._handle_validation_failure(
            data, source_format, destination_format, source_ext, dest_ext
        )
        if validation_result is not None:
            return validation_result

        # Type guard: at this point we know these are not None due to validation
        if destination_format is None or source_ext is None or dest_ext is None:
            # This should never happen after validation, but satisfies type checker
            return self._create_failed_result(
                data, source_format, source_format, None
            )

        # Perform in-memory conversion (ZERO I/O cost)
        converted_data = self._convert_in_memory(
            data, source_format, destination_format, source_ext, dest_ext
        )

        if converted_data is None:
            return self._create_failed_result(
                data, source_format, destination_format, None
            )

        return self._create_success_result(
            data, source_format, destination_format, converted_data
        )
