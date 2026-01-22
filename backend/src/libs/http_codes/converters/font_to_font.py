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
# LAST Modified: 6:14:23 15-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file containing the code for converting fonts to other font formats.
# // AR
# +==== END CatFeeder =================+
"""
from __future__ import annotations
from io import BytesIO
from typing import Optional, Dict, Union
from fontTools.ttLib import TTFont, TTLibError

from display_tty import Disp, initialise_logger
from ..http_constants import DataTypes, MEDIA_TYPES
from . import converters_constants as CONV_CONST
from ...core import FinalClass
from ...utils import CONST


class FontToFont(metaclass=FinalClass):
    """Convert fonts between web-compatible formats (TTF, OTF, WOFF, WOFF2)."""

    disp: Disp = initialise_logger(__qualname__, CONST.DEBUG)
    _instance: Optional["FontToFont"] = None

    def __new__(cls) -> "FontToFont":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.disp.log_debug("Initialising...")
        self.disp.log_debug("Initialised.")

    def __call__(
        self, data: bytes, source_format: DataTypes, generate_css: bool = True
    ) -> CONV_CONST.ConversionResult:
        return self.font_to_font(data, source_format, generate_css)

    # ------------------------- Main Conversion ------------------------- #
    def font_to_font(
        self, data: bytes, source_format: DataTypes, generate_css: bool = True
    ) -> CONV_CONST.ConversionResult:
        """_summary_

        Args:
            data (bytes): _description_
            source_format (DataTypes): _description_
            generate_css (bool, optional): _description_. Defaults to True.

        Returns:
            CONV_CONST.ConversionResult: _description_
        """

        # Unsupported formats
        if not MEDIA_TYPES.is_font(source_format):
            self.disp.log_warning(f"Unsupported font format: {source_format}")
            return self._build_result(data, False, source_format, source_format, None)

        # EOT is read-only
        if source_format == DataTypes.EOT:
            self.disp.log_warning("EOT is read-only; returning original data")
            return self._build_result(data, False, source_format, source_format, data)

        # Load font
        font = self._load_font(data)
        if font is None:
            return self._build_result(data, False, source_format, source_format, None)

        # Determine target formats
        targets = self._determine_targets(source_format)

        # Convert each target
        converted_files = self._convert_all_targets(font, data, targets)

        # Generate CSS if requested
        css_text = self._generate_css(converted_files) if generate_css else ""

        font.close()

        # Wrap all converted files in FontResult
        font_result = CONV_CONST.FontResult(
            ttf=converted_files.get(DataTypes.TTF, b""),
            otf=converted_files.get(DataTypes.OTF, b""),
            woff=converted_files.get(DataTypes.WOFF, b""),
            woff2=converted_files.get(DataTypes.WOFF2, b""),
            css=css_text
        )

        return self._build_result(
            data=data,
            converted=True,
            from_type=source_format,
            to_type=None,
            result=font_result
        )

    # ------------------------- Helper Functions ------------------------- #
    def _load_font(self, data: bytes) -> Optional[TTFont]:
        try:
            return TTFont(BytesIO(data))
        except TTLibError as e:
            self.disp.log_error(f"Cannot load font: {e}")
            return None

    def _determine_targets(self, source_format: DataTypes) -> list[DataTypes]:
        targets = [DataTypes.WOFF, DataTypes.WOFF2]
        if source_format in (DataTypes.TTF, DataTypes.OTF):
            targets.append(source_format)
        return targets

    def _convert_all_targets(
        self, font: TTFont, data: bytes, targets: list[DataTypes]
    ) -> Dict[DataTypes, bytes]:
        converted_files: Dict[DataTypes, bytes] = {}
        for target in targets:
            converted = self._convert_target(data, target)
            if converted:
                converted_files[target] = converted
        return converted_files

    def _convert_target(self, data: bytes, target: DataTypes) -> Optional[bytes]:
        try:
            font_copy = TTFont(BytesIO(data))
            out_buffer = BytesIO()

            if target == DataTypes.WOFF:
                font_copy.flavor = "woff"
                font_copy.save(out_buffer)
            elif target == DataTypes.WOFF2:
                font_copy.flavor = "woff2"
                font_copy.save(out_buffer)
            else:  # TTF/OTF passthrough
                font_copy.save(out_buffer)

            return out_buffer.getvalue()
        except Exception as e:
            self.disp.log_error(f"Failed to convert to {target}: {e}")
            return None

    def _generate_css(self, converted_files: Dict[DataTypes, bytes]) -> str:
        family = self._get_family_name(
            next(iter(converted_files.values()))) or "Unknown"

        css_srcs = []
        for fmt, _ in converted_files.items():
            ext = fmt.name.lower()
            css_fmt = "opentype" if fmt == DataTypes.OTF else fmt.name.lower()
            css_srcs.append(f"url('{family}.{ext}') format('{css_fmt}')")

        return (
            f"@font-face {{\n"
            f"  font-family: '{family}';\n"
            f"  font-style: normal;\n"
            f"  font-weight: 400;\n"
            f"  src: {', '.join(css_srcs)};\n"
            f"  font-display: swap;\n"
            f"}}\n"
        )

    def _get_family_name(self, font_bytes: bytes) -> Optional[str]:
        try:
            tt = TTFont(BytesIO(font_bytes))
            name_table = tt["name"]
            for rec in name_table.names:
                if rec.nameID == 1:  # Font Family Name
                    try:
                        return str(rec.toUnicode())
                    except Exception:
                        return str(rec)
            return None
        except TTLibError:
            return None

    def _build_result(
        self,
        data: bytes,
        converted: bool,
        from_type: DataTypes,
        to_type: Optional[DataTypes],
        result: Optional[Union[bytes, str, CONV_CONST.FontResult]] = None
    ) -> CONV_CONST.ConversionResult:
        if not to_type:
            return CONV_CONST.ConversionResult(
                data=data,
                converted=False,
                from_type=from_type,
                to_type=from_type,
                result=data
            )
        return CONV_CONST.ConversionResult(
            data=data,
            converted=converted,
            from_type=from_type,
            to_type=to_type,
            result=result
        )
