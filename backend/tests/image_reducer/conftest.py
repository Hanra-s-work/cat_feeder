"""Pytest fixtures for image_reducer tests."""

import io
import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from PIL import Image

# Dynamically determine paths relative to this test file
# Structure: <root>/tests/image_reducer/conftest.py -> go up 2 levels to get <root>
# Works regardless of whether <root> is named "backend", "app", etc.
test_file_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(test_file_dir, "..", ".."))
src_dir = os.path.join(project_root, "src")

# Ensure the src directory is available on sys.path for imports
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Also add project_root to allow "src." imports from project root
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture
def png_bytes():
    """Create a simple PNG image as bytes."""
    img = Image.new("RGB", (100, 100), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def jpeg_bytes():
    """Create a simple JPEG image as bytes."""
    img = Image.new("RGB", (100, 100), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def webp_bytes():
    """Create a simple WebP image as bytes."""
    img = Image.new("RGB", (100, 100), color="green")
    buf = io.BytesIO()
    img.save(buf, format="WEBP")
    return buf.getvalue()


@pytest.fixture
def rgba_png_bytes():
    """Create a PNG image with alpha channel as bytes."""
    img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def svg_bytes():
    """Create a simple SVG as bytes."""
    svg_content = b"""<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <!-- A simple rectangle -->
  <rect x="10" y="10" width="80" height="80" fill="red"/>
</svg>"""
    return svg_content


@pytest.fixture
def invalid_bytes():
    """Return invalid image bytes."""
    return b"this is not an image"


@pytest.fixture
def image_reducer_instance():
    """Provide an ImageReducer instance without initializing runtime dependencies."""
    # Flexible import pattern matching existing tests approach
    try:
        from libs.image_reducer.image_reducer import ImageReducer
    except ImportError:
        from src.libs.image_reducer.image_reducer import ImageReducer

    # Mock RuntimeManager.get to return mocked services for any service name
    with patch("src.libs.core.runtime_manager.RuntimeManager.get") as mock_get:
        # Make RuntimeManager.get return a MagicMock for any service requested
        mock_get.return_value = MagicMock()

        # Create the reducer instance with mocked dependencies
        reducer = ImageReducer(debug=True)

        # Ensure the mocks are in place after creation
        reducer.runtime_manager = MagicMock()

        # Mock boilerplate_response with build_response_body returning JSON-serializable dict
        reducer.boilerplate_response = MagicMock()
        reducer.boilerplate_response.build_response_body.return_value = {
            "title": "Error",
            "message": "An error occurred",
            "resp": "error",
            "token": None,
            "error": True,
            "data": None
        }

        # server_header.for_json() must return a dict-like object, not MagicMock
        reducer.server_header = MagicMock()
        reducer.server_header.for_json.return_value = {}

        return reducer
