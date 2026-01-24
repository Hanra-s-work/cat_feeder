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
# FILE: image_reducer.py
# CREATION DATE: 05-01-2026
# LAST Modified: 23:3:11 10-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the class in charge of doing the reducing work.
# // AR
# +==== END CatFeeder =================+
"""

import io
from typing import TYPE_CHECKING, Optional, List, Union

from fastapi import Response
from scour import scour as _scour
from PIL import Image, UnidentifiedImageError
from display_tty import Disp, initialise_logger

from . import image_reducer_constants as IR_CONST
from . import image_reducer_error_class as IR_ERR

from ..core import FinalClass
from ..core.runtime_manager import RI, RuntimeManager
from ..http_codes import HCI, HttpDataTypes

if TYPE_CHECKING:
    from ..server_header import ServerHeaders
    from ..boilerplates.responses import BoilerplateResponses


class ImageReducer(metaclass=FinalClass):
    """Utility for validating, converting and compressing images.

    Provides methods for opening, validating, converting, and saving images
    in different formats. Supports raster formats (PNG, JPEG, WebP) and SVG
    with optional compression.
    """

    # --------------------------------------------------------------------------
    # STATIC CLASS VALUES
    # --------------------------------------------------------------------------

    # -------------- Initialise the logger globally in the class. --------------
    disp: Disp = initialise_logger(__qualname__, False)

    # --------------------------------------------------------------------------
    # CONSTRUCTOR & DESTRUCTOR
    # --------------------------------------------------------------------------

    def __init__(self, error: int = 84, success: int = 0, debug: bool = False) -> None:
        """Initialize the ImageReducer instance with dependencies.

        Keyword Arguments:
            debug: Enable debug logging when True. Defaults to False.
        """
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        self.error = error
        self.success = success
        self.runtime_manager: RuntimeManager = RI
        self.boilerplate_response: "BoilerplateResponses" = self.runtime_manager.get(
            "BoilerplateResponses")
        self.server_header: "ServerHeaders" = self.runtime_manager.get(
            "ServerHeaders")
        self.disp.log_debug("Initialised")

    def __call__(
        self,
        file_bytes: bytes,
        allowed_formats: Optional[List[str]] = None,
        output_format: Optional[str] = "WEBP",
        max_dimension: Optional[int] = None,
        *,
        compress_svg: bool = False
    ) -> bytes:
        """Process an image with validation and conversion.

        Convenience wrapper that calls reprocess_image_strict with the given
        arguments. Validates image format, enforces maximum dimensions, and
        converts to the specified output format using predefined compression settings.

        Arguments:
            file_bytes: Image data as raw bytes.
            allowed_formats: Allowed input formats. Defaults to None.
            output_format: Desired output format. Defaults to "WEBP".
            max_dimension: Maximum allowed width/height in pixels. Defaults to None.
            compress_svg: Whether to minify SVG files. Defaults to False.

        Returns:
            Processed image as bytes.
        """

        self.disp.log_debug(
            f"output_format={output_format}, max_dimension={max_dimension}")
        result = self.reprocess_image_strict(
            file_bytes=file_bytes,
            allowed_formats=allowed_formats,
            output_format=output_format,
            max_dimension=max_dimension,
            compress_svg=compress_svg
        )
        self.disp.log_debug("completed")
        return result

    def reprocess_image_strict_safe(
        self,
        file_bytes: bytes,
        allowed_formats: Optional[List[str]] = None,
        output_format: Optional[str] = "WEBP",
        max_dimension: Optional[int] = None,
        *,
        compress_svg: bool = False,
        title: str = "reprocess_image",
        token: Optional[str] = None
    ) -> Union[bytes, Response]:
        """Process an image and return bytes or an error response.

        Safely processes an image with comprehensive error handling. Returns
        processed image bytes on success or an HTTP error response (400/413/415/500)
        if validation fails. Uses predefined compression settings from constants.

        Arguments:
            file_bytes: The image data to process as raw bytes.
            allowed_formats: Allowed input formats. Defaults to None.
            output_format: Desired output format. Defaults to "WEBP".
            max_dimension: Maximum allowed width/height in pixels. Defaults to None.
            compress_svg: Whether to minify SVG files. Defaults to False.
            title: Title for the HTTP response in case of error. Defaults to "reprocess_image".
            token: Token to include in the HTTP response. Defaults to None.

        Returns:
            Processed image bytes on success, or an HTTP error Response.

        Raises:
            No exceptions raised. All errors result in HTTP responses.
        """
        try:
            self.disp.log_debug("Reducing image (safe)")
            data = self.reprocess_image_strict(
                file_bytes=file_bytes,
                allowed_formats=allowed_formats,
                output_format=output_format,
                max_dimension=max_dimension,
                compress_svg=compress_svg
            )
            self.disp.log_info("Image_reduced")
            self.disp.log_debug(
                f"Image reduced (safe) result_bytes={len(data) if hasattr(data, '__len__') else 'unknown'}")
            return data
        except IR_ERR.ImageReducerInvalidImageFile as e:
            self.disp.log_error(f"ImageReducerInvalidImageFile : '{str(e)}'")
            body = self.boilerplate_response.build_response_body(
                title=title,
                message=str(e),
                resp="invalid_image_file",
                token=token,
                error=True
            )
            return HCI.bad_request(content=body, content_type=HttpDataTypes.JSON, headers=self.server_header.for_json())
        except IR_ERR.ImageReducerUnsupportedFormat as e:
            self.disp.log_error(f"ImageReducerUnsupportedFormat : '{str(e)}'")
            body = self.boilerplate_response.build_response_body(
                title=title,
                message=str(e),
                resp="unsupported_format",
                token=token,
                error=True
            )
            return HCI.unsupported_media_type(content=body, content_type=HttpDataTypes.JSON, headers=self.server_header.for_json())
        except IR_ERR.ImageReducerTooLarge as e:
            self.disp.log_error(f"ImageReducerTooLarge : '{str(e)}'")
            body = self.boilerplate_response.build_response_body(
                title=title,
                message=str(e),
                resp="too_large",
                token=token,
                error=True
            )
            return HCI.payload_too_large(content=body, content_type=HttpDataTypes.JSON, headers=self.server_header.for_json())
        except IR_ERR.ImageReducer as e:
            self.disp.log_error(f"ImageReducer : '{str(e)}'")
            body = self.boilerplate_response.build_response_body(
                title=title,
                message=str(e),
                resp="image_reducer_error",
                token=token,
                error=True
            )
            return HCI.internal_server_error(content=body, content_type=HttpDataTypes.JSON, headers=self.server_header.for_json())
        except ValueError as e:
            self.disp.log_error(f"ValueError : '{str(e)}'")
            body = self.boilerplate_response.build_response_body(
                title=title,
                message=str(e),
                resp="value_error",
                token=token,
                error=True
            )
            return HCI.internal_server_error(content=body, content_type=HttpDataTypes.JSON, headers=self.server_header.for_json())

    def reprocess_image_strict(
        self,
        file_bytes: bytes,
        allowed_formats: Optional[List[str]] = None,
        output_format: Optional[str] = "WEBP",
        max_dimension: Optional[int] = None,
        *,
        compress_svg: bool = False
    ) -> bytes:
        """Process an image with validation and format conversion.

        Detects file format, validates against allowed formats, enforces
        dimension limits, converts to the desired output format using predefined
        compression settings. For SVG files, optionally minifies them.
        Does not rescale raster images.

        Arguments:
            file_bytes: Uploaded image as raw bytes.
            allowed_formats: Allowed input formats. Defaults to None (uses ALLOWED_FORMATS).
            output_format: Output format to use. Defaults to "WEBP".
            max_dimension: Maximum allowed width/height in pixels. Defaults to None.
            compress_svg: Whether to minify SVG files. Defaults to False.

        Returns:
            Processed image bytes.

        Raises:
            ImageReducerInvalidImageFile: If image bytes cannot be decoded.
            ImageReducerUnsupportedFormat: If image format is not in allowed_formats.
            ImageReducerTooLarge: If image dimensions exceed max_dimension.
        """

        self.disp.log_debug(
            f"reprocess_image_strict start: output_format={output_format}, max_dimension={max_dimension}")

        _file_format: IR_CONST.FileFormat = self.detect_file_format(
            file_bytes)

        if _file_format == IR_CONST.FileFormat.SVG:
            if compress_svg:
                return self._compress_svg(file_bytes)
            return file_bytes

        if allowed_formats is None:
            allowed_formats = IR_CONST.ALLOWED_FORMATS
            self.disp.log_debug(
                f"Using default allowed_formats={allowed_formats}")

        # Open and validate image
        img: Image.Image = self._open_image(file_bytes)
        self._validate_format(img, allowed_formats)
        self._enforce_max_dimension(img, max_dimension)

        # Ensure correct mode
        img = self._ensure_mode(img)

        # Build save parameters and save
        fmt, save_params = self._build_save_params(output_format, img.format)
        save_params["format"] = fmt
        result = self._save_image(img, save_params)
        self.disp.log_debug(
            f"completed: result_bytes={len(result)}")
        return result

    def detect_file_format(self, file_bytes: bytes) -> IR_CONST.FileFormat:
        """Detect file format from bytes content.

        Uses heuristics to identify the image format:
        1. Checks for SVG XML tags (lossless, checks first).
        2. Uses Pillow to identify raster formats (PNG, JPEG, WebP).
        3. Returns FileFormat.UNKNOWN if detection fails.

        Arguments:
            file_bytes: Raw file bytes to analyze.

        Returns:
            FileFormat enum indicating the detected format.
        """
        # Quick check for SVG textual content
        if isinstance(file_bytes, (bytes, bytearray)):
            head = file_bytes[:512].lstrip()
            if b"<svg" in head.lower() or (head.startswith(b"<?xml") and b"<svg" in head.lower()):
                self.disp.log_debug(
                    "detected SVG by content")
                return IR_CONST.FileFormat.SVG
        else:
            self.disp.log_warning(
                "file_bytes is not bytes-like")

        # Try to use Pillow to identify raster formats
        try:
            img = Image.open(io.BytesIO(file_bytes))
            fmt = (img.format or "").upper()
            self.disp.log_debug(
                f"Pillow detected format={fmt}")
            if fmt == "PNG":
                return IR_CONST.FileFormat.PNG
            if fmt in ("JPEG", "JPG"):
                return IR_CONST.FileFormat.JPEG
            if fmt == "WEBP":
                return IR_CONST.FileFormat.WEBP
        except (UnidentifiedImageError, OSError) as e:
            self.disp.log_debug(
                f"Pillow failed to identify format: {e}")

        return IR_CONST.FileFormat.UNKNOWN

    def _compress_svg(self, file_bytes: bytes) -> bytes:
        """Minify SVG content by removing comments and metadata.

        Uses the scour library for safe, lossless SVG optimization. Removes
        XML comments, metadata, and enables viewboxing. Gracefully degrades
        if decoding fails and returns original bytes.

        Arguments:
            file_bytes: SVG file content as bytes (must be valid UTF-8).

        Returns:
            Minified SVG content as bytes.
        """
        self.disp.log_debug("_compress_svg: attempting svg minify")
        if not isinstance(file_bytes, (bytes, bytearray)):
            self.disp.log_warning(
                "_compress_svg: input is not bytes-like, returning original")
            return file_bytes

        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = file_bytes.decode("utf-8", errors="ignore")

        # Use scour for safer, stronger optimisation (assumed available)
        opts = _scour.sanitizeOptions()
        opts.remove_metadata = True
        opts.strip_comments = True
        opts.enable_viewboxing = True
        out_text = _scour.scourString(text, opts)
        out_bytes = out_text.encode("utf-8")
        self.disp.log_debug(
            f"_compress_svg (scour): reduced from {len(file_bytes)} to {len(out_bytes)} bytes")
        return out_bytes

    def _open_image(self, file_bytes: bytes) -> Image.Image:
        """Open image bytes and return a Pillow Image instance.

        Arguments:
            file_bytes: Raw image bytes to open.

        Returns:
            Pillow Image instance.

        Raises:
            ImageReducerInvalidImageFile: If bytes cannot be identified as a valid image.
        """
        self.disp.log_debug("attempting to open image bytes")
        try:
            img = Image.open(io.BytesIO(file_bytes))
            self.disp.log_debug(
                f"opened image format={img.format}, mode={img.mode}, size={getattr(img, 'size', None)}")
            return img
        except UnidentifiedImageError as e:
            file = "incorrect byte format"
            if not isinstance(file_bytes, bytes):
                file = f"{type(file_bytes)}"
            self.disp.log_error(f"{file}")
            raise IR_ERR.ImageReducerInvalidImageFile(file, "bytes") from e

    def _validate_format(self, img: Image.Image, allowed_formats: List[str]) -> None:
        """Validate that image format is in the allowed formats list.

        Arguments:
            img: Pillow image to validate.
            allowed_formats: List of allowed image format strings.

        Raises:
            ImageReducerUnsupportedFormat: If image format is not in allowed_formats.
        """
        self.disp.log_debug(
            f"img.format={img.format}, allowed={allowed_formats}")
        if img.format not in allowed_formats:
            self.disp.log_warning(
                f"unsupported format {img.format}")
            raise IR_ERR.ImageReducerUnsupportedFormat(
                img.format, allowed_formats
            )

    def _enforce_max_dimension(self, img: Image.Image, max_dimension: Optional[int]) -> None:
        """Validate that image dimensions do not exceed the maximum allowed size.

        Arguments:
            img: Pillow image to check.
            max_dimension: Maximum allowed width/height in pixels. If None, no check is performed.

        Raises:
            ImageReducerTooLarge: If image width or height exceeds max_dimension.
        """
        self.disp.log_debug(
            f"img.size={img.width}x{img.height}, max_dimension={max_dimension}")
        if max_dimension is not None:
            if img.width > max_dimension or img.height > max_dimension:
                self.disp.log_warning(
                    f"image too large {img.width}x{img.height} > {max_dimension}")
                raise IR_ERR.ImageReducerTooLarge(
                    img.width, img.height, max_dimension
                )

    def _ensure_mode(self, img: Image.Image) -> Image.Image:
        """Ensure image is in RGB or RGBA mode, converting if necessary.

        Converts indexed (P), grayscale (L, LA), or other color modes to either
        RGB (for opaque images) or RGBA (for images with alpha channel).

        Arguments:
            img: Pillow image to convert if necessary.

        Returns:
            Image in RGB or RGBA mode.
        """
        self.disp.log_debug(f"current mode={img.mode}")
        if img.mode not in ("RGB", "RGBA"):
            if "A" in img.mode:
                target = "RGBA"
            else:
                target = "RGB"
            self.disp.log_debug(
                f"converting mode from {img.mode} to {target}")
            return img.convert(target)
        self.disp.log_debug("no conversion needed")
        return img

    def _build_save_params(self, output_format: Optional[str], img_format: Optional[str]) -> tuple:
        """Build parameters for saving an image in the desired format.

        Resolves the output format (from parameter, original format, or default),
        and constructs a dictionary of save parameters using predefined compression
        settings from COMPRESSION_QUALITY for the target format.

        Arguments:
            output_format: Desired output format (e.g., "WEBP", "PNG"). If None, uses original format or default.
            img_format: Original image format from Pillow.

        Returns:
            Tuple of (format_string: str, save_params: dict).
        """
        self.disp.log_debug(
            f"requested output_format={output_format}, img_format={img_format}")
        # Determine output format
        if not output_format:
            if not img_format:
                output_format = IR_CONST.DEFAULT_OUTPUT_FORMAT
            else:
                output_format = img_format

        output_format = output_format.upper()
        save_params: dict = {"optimize": True}

        # Apply format-specific compression settings
        of = output_format.lower()

        if output_format in IR_CONST.ALLOWED_OUTPUT_FORMATS:
            # For formats with quality settings, use the provided quality or default from COMPRESSION_QUALITY
            if of in IR_CONST.COMPRESSION_QUALITY:
                compression_value = IR_CONST.COMPRESSION_QUALITY[of]
                # For lossy formats (JPEG, WebP, AVIF), use quality parameter
                if of in ("jpeg", "jpg", "webp", "avif"):
                    save_params["quality"] = compression_value
                # For PNG, use compression level (0-9)
                elif of == "png":
                    save_params["compress_level"] = compression_value
                # For GIF, use optimize flag
                elif of == "gif":
                    save_params["optimize"] = bool(compression_value)

        self.disp.log_debug(
            f"resolved format={output_format}, save_params={save_params}")
        return output_format, save_params

    def _save_image(self, img: Image.Image, save_params: dict) -> bytes:
        """Save a Pillow image to bytes using the specified parameters.

        Arguments:
            img: Pillow image to save.
            save_params: Dictionary of parameters to pass to Image.save() (e.g., format, quality, optimize).

        Returns:
            Saved image content as raw bytes.
        """
        self.disp.log_debug(f"saving with params={save_params}")
        data = io.BytesIO()
        img.save(data, **save_params)
        out = data.getvalue()
        self.disp.log_debug(f"saved {len(out)} bytes")
        return out

    def test_images(self) -> None:
        """Test image reduction by processing a sample file.

        Loads "admin_upload.png", processes it to WebP format with quality 90
        and a maximum dimension of 1024px, then saves the result to "processed.webp".
        Useful for validating the reduction pipeline end-to-end.
        """
        with open("admin_upload.png", "rb") as f:
            original_bytes: bytes = f.read()

        processed_bytes: bytes = self.reprocess_image_strict(
            file_bytes=original_bytes,
            output_format="WEBP",
            max_dimension=1024
        )

        with open("processed.webp", "wb") as f:
            f.write(processed_bytes)
