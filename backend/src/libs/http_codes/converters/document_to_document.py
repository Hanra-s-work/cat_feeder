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
# FILE: document_to_document.py
# CREATION DATE: 15-01-2026
# LAST Modified: 1:32:47 17-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file containing the code for converting documents from one format to another.
# // AR
# +==== END CatFeeder =================+
"""

from io import BytesIO
from typing import Optional, Set
from pathlib import Path
import tempfile

from display_tty import Disp, initialise_logger

# Document processing libraries
import pypandoc

from .aliases import DOCUMENT_FORMAT_ALIASES
from . import converters_constants as CONV_CONST

from ..http_constants import DataTypes, MEDIA_TYPES

from ...core import FinalClass
from ...utils import CONST
from ...tinytex import TinyTeXInstaller


class DocumentToDocument(metaclass=FinalClass):
    """Class used to convert documents from one format to another using Pandoc.

    Optimized to minimize I/O costs:
    - Text-based formats (MD, HTML, JSON, etc.) converted entirely in-memory (zero I/O)
    - Binary formats (PDF, DOCX, etc.) require file I/O (billable operations)
    """

    disp: Disp = initialise_logger(__qualname__, CONST.DEBUG)

    _instance: Optional["DocumentToDocument"] = None

    _downloaded_tinytex: bool = False

    # Text-based formats that can be processed entirely in-memory (zero I/O cost)
    _TEXT_BASED_FORMATS: Set[DataTypes] = {
        DataTypes.TXT, DataTypes.TEXT, DataTypes.PLAIN,
        DataTypes.MARKDOWN, DataTypes.MD,
        DataTypes.HTML, DataTypes.XML, DataTypes.XHTML,
        DataTypes.JSON, DataTypes.YAML, DataTypes.YML,
        DataTypes.TOML, DataTypes.CSV,
        DataTypes.RSS, DataTypes.ATOM,
    }

    def __new__(cls) -> "DocumentToDocument":
        if cls._instance is None:
            cls._instance = super(DocumentToDocument, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.disp.log_debug("Initialising...")
        self.disp.log_debug("Checking for TinyTeX dependencies...")
        self._ensure_tinytex()
        self.disp.log_debug("TinyTeX dependencies satisfied.")
        self.disp.log_debug("Initialised.")

    def __call__(self, data: bytes, source_format: DataTypes) -> CONV_CONST.ConversionResult:
        return self.document_to_document(data, source_format)

    def _ensure_tinytex(self) -> None:
        """Ensure TinyTeX is installed for LaTeX/PDF operations."""
        if not self._downloaded_tinytex:
            self.disp.log_debug("Installing TinyTeX...")
            try:
                path = TinyTeXInstaller("TinyTeX-1").install()
                self._downloaded_tinytex = True
                self.disp.log_debug(f"TinyTeX installed at: {path}")
            except Exception as e:
                self.disp.log_warning(f"TinyTeX installation failed: {e}")
                self._downloaded_tinytex = False

    def get_document_extension(self, data_type: DataTypes) -> Optional[str]:
        """
        Get the file extension for a given document DataType.

        Args:
            data_type: The DataType to get extension for

        Returns:
            Extension string or None
        """
        return DOCUMENT_FORMAT_ALIASES.get(data_type)

    def _is_text_based(self, data_type: DataTypes) -> bool:
        """Check if a format is text-based and can use in-memory conversion (zero I/O)."""
        return data_type in self._TEXT_BASED_FORMATS

    def _can_use_memory_conversion(self, source: DataTypes, dest: DataTypes) -> bool:
        """Check if conversion can be done entirely in memory (zero I/O cost)."""
        return self._is_text_based(source) and self._is_text_based(dest)

    def _validate_conversion_params(
        self,
        data: bytes,
        source_format: DataTypes
    ) -> tuple[Optional[DataTypes], Optional[str], Optional[str]]:
        """
        Validate conversion parameters and get destination format and extensions.

        Args:
            data: The document data to validate
            source_format: The source document format

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

        source_ext = self.get_document_extension(source_format)
        dest_ext = self.get_document_extension(destination_format)

        if not source_ext or not dest_ext:
            self.disp.log_warning(
                f"Unknown document extension for {source_format} -> {destination_format}"
            )
            return destination_format, None, None

        return destination_format, source_ext, dest_ext

    def _create_temp_files(
        self,
        data: bytes,
        source_ext: str,
        dest_ext: str
    ) -> tuple[Path, Path]:
        """
        Create temporary files for document conversion.
        WARNING: This incurs billable I/O operations. Only used when in-memory conversion is not possible.

        Args:
            data: The source document data
            source_ext: The source file extension
            dest_ext: The destination file extension

        Returns:
            Tuple of (source_path, destination_path)
        """
        self.disp.log_warning(
            "Using file-based conversion - this incurs I/O costs")

        with tempfile.NamedTemporaryFile(
            suffix=f".{source_ext}",
            delete=False
        ) as src_file:
            src_file.write(data)
            src_path = Path(src_file.name)

        with tempfile.NamedTemporaryFile(
            suffix=f".{dest_ext}",
            delete=False
        ) as dst_file:
            dst_path = Path(dst_file.name)

        return src_path, dst_path

    def _convert_in_memory(
        self,
        data: bytes,
        source_format: DataTypes,
        destination_format: DataTypes
    ) -> Optional[bytes]:
        """
        Perform in-memory document conversion for text-based formats.
        ZERO I/O COST - everything happens in RAM, no disk writes.

        Args:
            data: Source document data
            source_format: Source document format
            destination_format: Destination document format

        Returns:
            Converted document data as bytes, or None if conversion failed
        """
        self.disp.log_debug(
            f"Converting in-memory (ZERO I/O): {source_format} -> {destination_format}"
        )

        try:
            # Decode bytes to string for text-based conversion
            text_data = data.decode('utf-8', errors='replace')

            # Use pypandoc.convert_text for pure in-memory conversion
            converted_text = pypandoc.convert_text(
                text_data,
                to=destination_format.name.lower(),
                format=source_format.name.lower(),
                extra_args=['--standalone']
            )

            # Convert back to bytes
            if isinstance(converted_text, str):
                result = converted_text.encode('utf-8')
            else:
                result = converted_text

            self.disp.log_debug(
                "In-memory conversion successful (ZERO I/O cost)")
            return result

        except Exception as e:
            self.disp.log_error(f"In-memory conversion failed: {e}")
            return None

    def _perform_conversion(
        self,
        src_path: Path,
        dst_path: Path,
        source_format: DataTypes,
        destination_format: DataTypes
    ) -> Optional[bytes]:
        """
        Perform the actual document conversion using Pandoc with file I/O.
        WARNING: This incurs billable I/O operations.

        Args:
            src_path: Path to source document file
            dst_path: Path to destination document file
            source_format: Source document format
            destination_format: Destination document format

        Returns:
            Converted document data as bytes, or None if conversion failed
        """
        self.disp.log_debug(
            f"Converting document (file-based, incurs I/O): {source_format} -> {destination_format}"
        )

        try:
            # Use pypandoc to convert
            pypandoc.convert_file(
                str(src_path),
                to=destination_format.name.lower(),
                outputfile=str(dst_path),
                extra_args=['--standalone']
            )

            with open(dst_path, 'rb') as f:
                converted_data = f.read()

            self.disp.log_debug("Document conversion successful")
            return converted_data

        except Exception as e:
            self.disp.log_error(f"Pandoc conversion failed: {e}")
            return None

    @staticmethod
    def _cleanup_temp_files(src_path: Path, dst_path: Path) -> None:
        """
        Clean up temporary files.

        Args:
            src_path: Source file path to delete
            dst_path: Destination file path to delete
        """
        if src_path.exists():
            src_path.unlink()
        if dst_path.exists():
            dst_path.unlink()

    def _create_failed_result(
        self,
        data: bytes,
        source_format: DataTypes,
        destination_format: DataTypes,
        result: Optional[bytes] = None
    ) -> CONV_CONST.ConversionResult:
        """
        Create a failed conversion result.

        Args:
            data: Original document data
            source_format: Source document format
            destination_format: Destination document format
            result: Optional result data

        Returns:
            ConversionResult indicating failure
        """
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
        """
        Create a successful conversion result.

        Args:
            data: Original document data
            source_format: Source document format
            destination_format: Destination document format
            converted_data: Converted document data

        Returns:
            ConversionResult indicating success
        """
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
        """
        Handle validation failures and return appropriate result.

        Args:
            data: Original document data
            source_format: Source document format
            destination_format: Destination format (may be None)
            source_ext: Source extension (may be None)
            dest_ext: Destination extension (may be None)

        Returns:
            ConversionResult if validation failed, None if validation passed
        """
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

    def _convert_with_temp_files(
        self,
        data: bytes,
        source_format: DataTypes,
        destination_format: DataTypes,
        source_ext: str,
        dest_ext: str
    ) -> CONV_CONST.ConversionResult:
        """
        Perform conversion, preferring in-memory (ZERO I/O cost) when possible.
        Falls back to file-based conversion (billable I/O) only for binary formats.

        Args:
            data: Original document data
            source_format: Source document format
            destination_format: Destination document format
            source_ext: Source file extension
            dest_ext: Destination file extension

        Returns:
            ConversionResult with conversion outcome
        """
        # Try in-memory conversion for text-based formats (ZERO I/O cost)
        if self._can_use_memory_conversion(source_format, destination_format):
            try:
                converted_data = self._convert_in_memory(
                    data, source_format, destination_format
                )

                if converted_data is not None:
                    return self._create_success_result(
                        data, source_format, destination_format, converted_data
                    )
                else:
                    self.disp.log_warning(
                        "In-memory conversion failed, falling back to file-based (will incur I/O cost)"
                    )
            except Exception as e:
                self.disp.log_warning(
                    f"In-memory conversion error: {e}, falling back to file-based (will incur I/O cost)"
                )
        else:
            self.disp.log_info(
                f"Binary format conversion {source_format} -> {destination_format} requires file I/O (billable)"
            )

        # Fall back to file-based conversion (incurs billable I/O)
        src_path: Optional[Path] = None
        dst_path: Optional[Path] = None

        try:
            src_path, dst_path = self._create_temp_files(
                data, source_ext, dest_ext
            )

            converted_data = self._perform_conversion(
                src_path, dst_path, source_format, destination_format
            )

            if converted_data is None:
                return self._create_failed_result(
                    data, source_format, destination_format, None
                )

            return self._create_success_result(
                data, source_format, destination_format, converted_data
            )

        except Exception as e:
            self.disp.log_error(f"Document conversion error: {e}")
            return self._create_failed_result(
                data, source_format, destination_format, None
            )

        finally:
            if src_path is not None and dst_path is not None:
                self._cleanup_temp_files(src_path, dst_path)

    def document_to_document(self, data: bytes, source_format: DataTypes) -> CONV_CONST.ConversionResult:
        """
        Convert document data from one format to another using Pandoc.

        Args:
            data (bytes): The document data to convert.
            source_format (DataTypes): The original document format.

        Returns:
            ConversionResult: The converted document data in a contained dataclass.
        """
        destination_format, source_ext, dest_ext = self._validate_conversion_params(
            data, source_format
        )

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
        return self._convert_with_temp_files(
            data, source_format, destination_format, source_ext, dest_ext
        )
