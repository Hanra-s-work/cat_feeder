"""Unit tests for image_reducer module."""

import io
import sys
import pytest
from PIL import Image
from unittest.mock import MagicMock, patch

# Flexible import pattern matching existing tests approach
# conftest.py sets up sys.path, try libs first (works from backend/),
# fall back to src.libs (works from project root)
try:
    from libs.image_reducer.image_reducer import ImageReducer
    from libs.image_reducer import image_reducer_constants as IR_CONST
    from libs.image_reducer import image_reducer_error_class as IR_ERR
except ImportError:
    from src.libs.image_reducer.image_reducer import ImageReducer
    from src.libs.image_reducer import image_reducer_constants as IR_CONST
    from src.libs.image_reducer import image_reducer_error_class as IR_ERR


class TestDetectFileFormat:
    """Tests for detect_file_format method."""

    def test_detect_png_format(self, image_reducer_instance, png_bytes):
        """PNG bytes should be detected as PNG format."""
        detected_format = image_reducer_instance.detect_file_format(png_bytes)
        assert detected_format == IR_CONST.FileFormat.PNG

    def test_detect_jpeg_format(self, image_reducer_instance, jpeg_bytes):
        """JPEG bytes should be detected as JPEG format."""
        detected_format = image_reducer_instance.detect_file_format(
            jpeg_bytes)
        # JPEG could be detected as JPEG or JPG
        assert detected_format in (
            IR_CONST.FileFormat.JPEG, IR_CONST.FileFormat.JPG)

    def test_detect_webp_format(self, image_reducer_instance, webp_bytes):
        """WebP bytes should be detected as WEBP format."""
        detected_format = image_reducer_instance.detect_file_format(
            webp_bytes)
        assert detected_format == IR_CONST.FileFormat.WEBP

    def test_detect_svg_format(self, image_reducer_instance, svg_bytes):
        """SVG bytes with <svg tag should be detected as SVG format."""
        detected_format = image_reducer_instance.detect_file_format(svg_bytes)
        assert detected_format == IR_CONST.FileFormat.SVG

    def test_detect_svg_format_with_xml_declaration(self, image_reducer_instance):
        """SVG with XML declaration should be detected as SVG."""
        svg_bytes = b"""<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <circle cx="50" cy="50" r="40" fill="blue"/>
</svg>"""
        detected_format = image_reducer_instance.detect_file_format(svg_bytes)
        assert detected_format == IR_CONST.FileFormat.SVG

    def test_detect_invalid_format(self, image_reducer_instance, invalid_bytes):
        """Invalid bytes should be detected as UNKNOWN format."""
        detected_format = image_reducer_instance.detect_file_format(
            invalid_bytes)
        assert detected_format == IR_CONST.FileFormat.UNKNOWN


class TestCompressSvg:
    """Tests for _compress_svg method."""

    def test_compress_svg_removes_comments(self, image_reducer_instance, svg_bytes):
        """SVG compression should remove comments."""
        compressed = image_reducer_instance._compress_svg(svg_bytes)
        assert isinstance(compressed, bytes)
        # Comments should be removed
        assert b"<!-- A simple rectangle -->" not in compressed

    def test_compress_svg_preserves_structure(self, image_reducer_instance, svg_bytes):
        """SVG compression should preserve essential SVG structure."""
        compressed = image_reducer_instance._compress_svg(svg_bytes)
        # SVG should still start with <?xml or <svg
        assert b"<?xml" in compressed or b"<svg" in compressed

    def test_compress_svg_returns_bytes(self, image_reducer_instance, svg_bytes):
        """_compress_svg should return bytes."""
        result = image_reducer_instance._compress_svg(svg_bytes)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_compress_svg_reduces_size(self, image_reducer_instance, svg_bytes):
        """SVG compression should reduce file size by removing whitespace."""
        compressed = image_reducer_instance._compress_svg(svg_bytes)
        # Compressed should be smaller (removed comments and excess whitespace)
        assert len(compressed) < len(svg_bytes)


class TestOpenImage:
    """Tests for _open_image method."""

    def test_open_image_valid_png(self, image_reducer_instance, png_bytes):
        """Valid PNG bytes should open successfully."""
        img = image_reducer_instance._open_image(png_bytes)
        assert isinstance(img, Image.Image)
        assert img.size == (100, 100)

    def test_open_image_valid_jpeg(self, image_reducer_instance, jpeg_bytes):
        """Valid JPEG bytes should open successfully."""
        img = image_reducer_instance._open_image(jpeg_bytes)
        assert isinstance(img, Image.Image)
        assert img.size == (100, 100)

    def test_open_image_invalid_bytes(self, image_reducer_instance, invalid_bytes):
        """Invalid bytes should raise ImageReducerInvalidImageFile."""
        with pytest.raises(IR_ERR.ImageReducerInvalidImageFile):
            image_reducer_instance._open_image(invalid_bytes)


class TestValidateFormat:
    """Tests for _validate_format method."""

    def test_validate_format_png(self, image_reducer_instance, png_bytes):
        """PNG format should validate against ALLOWED_FORMATS."""
        img = image_reducer_instance._open_image(png_bytes)
        # Should not raise
        image_reducer_instance._validate_format(img, IR_CONST.ALLOWED_FORMATS)

    def test_validate_format_jpeg(self, image_reducer_instance, jpeg_bytes):
        """JPEG format should validate against ALLOWED_FORMATS."""
        img = image_reducer_instance._open_image(jpeg_bytes)
        # Should not raise
        image_reducer_instance._validate_format(img, IR_CONST.ALLOWED_FORMATS)

    def test_validate_format_unsupported(self, image_reducer_instance):
        """Unsupported format should raise ImageReducerUnsupportedFormat."""
        img = Image.new("RGB", (100, 100))
        img.format = "TIFF"  # Not in ALLOWED_FORMATS by default for validation
        with pytest.raises(IR_ERR.ImageReducerUnsupportedFormat):
            image_reducer_instance._validate_format(
                img, ["PNG", "JPEG", "WEBP"])


class TestEnforceMaxDimension:
    """Tests for _enforce_max_dimension method."""

    def test_enforce_max_dimension_within_limit(self, image_reducer_instance):
        """Image within max dimensions should pass."""
        img = Image.new("RGB", (100, 100))
        # Should not raise
        image_reducer_instance._enforce_max_dimension(img, max_dimension=200)

    def test_enforce_max_dimension_at_limit(self, image_reducer_instance):
        """Image at max dimensions should pass."""
        img = Image.new("RGB", (200, 200))
        # Should not raise
        image_reducer_instance._enforce_max_dimension(img, max_dimension=200)

    def test_enforce_max_dimension_exceeds_limit(self, image_reducer_instance):
        """Image exceeding max dimensions should raise ImageReducerTooLarge."""
        img = Image.new("RGB", (300, 100))
        with pytest.raises(IR_ERR.ImageReducerTooLarge):
            image_reducer_instance._enforce_max_dimension(
                img, max_dimension=200)

    def test_enforce_max_dimension_height_exceeds(self, image_reducer_instance):
        """Image with height exceeding limit should raise ImageReducerTooLarge."""
        img = Image.new("RGB", (100, 300))
        with pytest.raises(IR_ERR.ImageReducerTooLarge):
            image_reducer_instance._enforce_max_dimension(
                img, max_dimension=200)


class TestEnsureMode:
    """Tests for _ensure_mode method."""

    def test_ensure_mode_rgb_unchanged(self, image_reducer_instance):
        """RGB mode should remain unchanged."""
        img = Image.new("RGB", (100, 100))
        result = image_reducer_instance._ensure_mode(img)
        assert result.mode == "RGB"

    def test_ensure_mode_rgba_unchanged(self, image_reducer_instance):
        """RGBA mode should remain unchanged."""
        img = Image.new("RGBA", (100, 100))
        result = image_reducer_instance._ensure_mode(img)
        assert result.mode == "RGBA"

    def test_ensure_mode_la_converts_to_rgba(self, image_reducer_instance):
        """LA mode (with alpha) should convert to RGBA."""
        img = Image.new("LA", (100, 100))
        result = image_reducer_instance._ensure_mode(img)
        assert result.mode == "RGBA"

    def test_ensure_mode_l_converts_to_rgb(self, image_reducer_instance):
        """L mode (grayscale) should convert to RGB."""
        img = Image.new("L", (100, 100))
        result = image_reducer_instance._ensure_mode(img)
        assert result.mode == "RGB"

    def test_ensure_mode_p_converts_to_rgb(self, image_reducer_instance):
        """P mode (palette) should convert to RGB."""
        img = Image.new("P", (100, 100))
        result = image_reducer_instance._ensure_mode(img)
        assert result.mode == "RGB"


class TestBuildSaveParams:
    """Tests for _build_save_params method."""

    def test_build_save_params_png(self, image_reducer_instance):
        """Build save params for PNG format."""
        fmt, params = image_reducer_instance._build_save_params(
            "PNG", img_format="PNG")
        assert fmt == "PNG"
        assert "optimize" in params

    def test_build_save_params_webp_with_quality(self, image_reducer_instance):
        """Build save params for WebP format uses default compression."""
        fmt, params = image_reducer_instance._build_save_params(
            "WEBP", img_format="PNG")
        assert fmt == "WEBP"
        assert "optimize" in params

    def test_build_save_params_jpeg_with_quality(self, image_reducer_instance):
        """Build save params for JPEG format uses default compression."""
        fmt, params = image_reducer_instance._build_save_params(
            "JPEG", img_format="PNG")
        assert fmt == "JPEG"
        # Default JPEG quality from COMPRESSION_QUALITY
        assert params.get("quality") == 90

    def test_build_save_params_default_format(self, image_reducer_instance):
        """Build save params with None format should use DEFAULT_OUTPUT_FORMAT."""
        fmt, params = image_reducer_instance._build_save_params(
            None, img_format="PNG")
        assert fmt in (IR_CONST.DEFAULT_OUTPUT_FORMAT, "PNG")


class TestSaveImage:
    """Tests for _save_image method."""

    def test_save_image_returns_bytes(self, image_reducer_instance):
        """_save_image should return bytes."""
        img = Image.new("RGB", (100, 100), color="red")
        save_params = {"format": "PNG"}
        result = image_reducer_instance._save_image(img, save_params)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_save_image_creates_valid_image(self, image_reducer_instance):
        """Saved image bytes should be readable as a valid image."""
        img = Image.new("RGB", (100, 100), color="blue")
        save_params = {"format": "JPEG", "quality": 85}
        result = image_reducer_instance._save_image(img, save_params)
        # Should be able to reopen the saved image
        reopened = Image.open(io.BytesIO(result))
        assert reopened.size == (100, 100)


class TestReprocessImageStrict:
    """Tests for reprocess_image_strict orchestrator method."""

    def test_reprocess_png_to_webp(self, image_reducer_instance, png_bytes):
        """PNG should be reprocessed to WebP."""
        result = image_reducer_instance.reprocess_image_strict(
            file_bytes=png_bytes,
            output_format="WEBP"
        )
        assert isinstance(result, bytes)
        # Should be valid WebP
        img = Image.open(io.BytesIO(result))
        assert img.format == "WEBP"

    def test_reprocess_jpeg_to_png(self, image_reducer_instance, jpeg_bytes):
        """JPEG should be reprocessed to PNG."""
        result = image_reducer_instance.reprocess_image_strict(
            file_bytes=jpeg_bytes,
            output_format="PNG"
        )
        assert isinstance(result, bytes)
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"

    def test_reprocess_with_max_dimension(self, image_reducer_instance, png_bytes):
        """Image exceeding max dimension should raise ImageReducerTooLarge."""
        with pytest.raises(IR_ERR.ImageReducerTooLarge):
            image_reducer_instance.reprocess_image_strict(
                file_bytes=png_bytes,
                output_format="PNG",
                max_dimension=50  # PNG fixture is 100x100
            )

    def test_reprocess_svg_with_compression(self, image_reducer_instance, svg_bytes):
        """SVG with compress_svg=True should return minified SVG."""
        result = image_reducer_instance.reprocess_image_strict(
            file_bytes=svg_bytes,
            compress_svg=True
        )
        assert isinstance(result, bytes)
        assert b"<svg" in result or b"<?xml" in result
        # Compressed should be smaller
        assert len(result) < len(svg_bytes)

    def test_reprocess_invalid_bytes_raises(self, image_reducer_instance, invalid_bytes):
        """Invalid image bytes should raise ImageReducerInvalidImageFile."""
        with pytest.raises(IR_ERR.ImageReducerInvalidImageFile):
            image_reducer_instance.reprocess_image_strict(
                file_bytes=invalid_bytes,
                output_format="PNG"
            )


class TestReprocessImageStrictSafe:
    """Tests for reprocess_image_strict_safe safe wrapper method."""

    def test_safe_wrapper_valid_input_returns_bytes(self, image_reducer_instance, png_bytes):
        """Valid input should return bytes."""
        result = image_reducer_instance.reprocess_image_strict_safe(
            file_bytes=png_bytes,
            output_format="WEBP"
        )
        assert isinstance(result, bytes)

    def test_safe_wrapper_invalid_image_returns_400(self, image_reducer_instance, invalid_bytes):
        """Invalid image should return 400 Bad Request response."""
        result = image_reducer_instance.reprocess_image_strict_safe(
            file_bytes=invalid_bytes,
            output_format="PNG"
        )
        # Should return an HCI response with 400 status
        # Verify by checking the response object
        assert hasattr(result, "status_code") and result.status_code == 400

    def test_safe_wrapper_unsupported_format_returns_415(self, image_reducer_instance):
        """Unsupported format should return 415 Unsupported Media Type response."""
        # Create an image that will be detected as having unsupported format
        # Use TIFF which is not in typical allowed input formats for processing
        tiff_img = Image.new("RGB", (100, 100))
        buf = io.BytesIO()
        tiff_img.save(buf, format="TIFF")
        tiff_bytes = buf.getvalue()

        result = image_reducer_instance.reprocess_image_strict_safe(
            file_bytes=tiff_bytes,
            # Explicitly restrict to not include TIFF
            allowed_formats=["PNG", "JPEG", "WEBP"],
            output_format="PNG"
        )
        # Should return 415 response
        assert hasattr(result, "status_code") and result.status_code == 415

    def test_safe_wrapper_too_large_image_returns_413(self, image_reducer_instance, png_bytes):
        """Too large image should return 413 Payload Too Large response."""
        result = image_reducer_instance.reprocess_image_strict_safe(
            file_bytes=png_bytes,
            max_dimension=50  # PNG fixture is 100x100
        )
        # Should return 413 response
        assert hasattr(result, "status_code") and result.status_code == 413

    def test_safe_wrapper_with_valid_svg(self, image_reducer_instance, svg_bytes):
        """Valid SVG with compression should return bytes."""
        result = image_reducer_instance.reprocess_image_strict_safe(
            file_bytes=svg_bytes,
            compress_svg=True
        )
        assert isinstance(result, bytes)


class TestCustomExceptionClasses:
    """Tests for custom exception classes."""

    def test_image_reducer_invalid_image_file_exception(self):
        """ImageReducerInvalidImageFile should be an ImageReducer exception."""
        exc = IR_ERR.ImageReducerInvalidImageFile(
            image_file="test.txt", allowed_files="PNG, JPEG, WEBP")
        assert isinstance(exc, IR_ERR.ImageReducer)
        assert "Invalid Image file" in str(exc)

    def test_image_reducer_unsupported_format_exception(self):
        """ImageReducerUnsupportedFormat should be an ImageReducer exception."""
        exc = IR_ERR.ImageReducerUnsupportedFormat(
            image_file="GIF", allowed_files=["PNG", "JPEG", "WEBP"])
        assert isinstance(exc, IR_ERR.ImageReducer)
        assert "Unsupported image format" in str(exc)

    def test_image_reducer_too_large_exception(self):
        """ImageReducerTooLarge should be an ImageReducer exception."""
        exc = IR_ERR.ImageReducerTooLarge(
            width=300, height=300, max_dimension=200)
        assert isinstance(exc, IR_ERR.ImageReducer)
        assert "Image too large" in str(exc)

    def test_exception_hierarchy(self):
        """All custom exceptions should inherit from ImageReducer."""
        assert issubclass(IR_ERR.ImageReducerInvalidImageFile,
                          IR_ERR.ImageReducer)
        assert issubclass(
            IR_ERR.ImageReducerUnsupportedFormat, IR_ERR.ImageReducer)
        assert issubclass(IR_ERR.ImageReducerTooLarge, IR_ERR.ImageReducer)


class TestIntegration:
    """Integration tests for full image processing workflows."""

    def test_full_workflow_png_to_webp(self, image_reducer_instance, png_bytes):
        """Full workflow: PNG input → WEBP output."""
        result = image_reducer_instance(
            file_bytes=png_bytes,
            output_format="WEBP"
        )
        assert isinstance(result, bytes)
        img = Image.open(io.BytesIO(result))
        assert img.format == "WEBP"

    def test_full_workflow_with_dimension_enforcement(self, image_reducer_instance):
        """Full workflow: resize within max dimensions."""
        large_img = Image.new("RGB", (200, 200), color="red")
        buf = io.BytesIO()
        large_img.save(buf, format="PNG")
        large_bytes = buf.getvalue()

        result = image_reducer_instance.reprocess_image_strict(
            file_bytes=large_bytes,
            output_format="JPEG",
            max_dimension=200  # Should pass as it's at limit
        )
        assert isinstance(result, bytes)

    def test_full_workflow_rgba_conversion(self, image_reducer_instance, rgba_png_bytes):
        """Full workflow: RGBA PNG → PNG."""
        result = image_reducer_instance.reprocess_image_strict(
            file_bytes=rgba_png_bytes,
            output_format="PNG"
        )
        assert isinstance(result, bytes)
        img = Image.open(io.BytesIO(result))
        # PNG can support RGBA after ensure_mode conversion
        assert img.mode in ("RGBA", "RGB")
