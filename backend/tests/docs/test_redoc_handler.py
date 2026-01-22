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
# FILE: test_redoc_handler.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Unit tests for the ReDoc documentation handler module.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Comprehensive test suite for RedocHandler class.
# // AR
# +==== END CatFeeder =================+
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import FastAPI

try:
    from libs.docs.redoc.redoc_class import RedocHandler
    from libs.docs.redoc import redoc_constants as REDOC_CONST
except Exception:
    from src.libs.docs.redoc.redoc_class import RedocHandler
    from src.libs.docs.redoc import redoc_constants as REDOC_CONST


class TestRedocHandlerInitialization:
    """Test RedocHandler initialization."""

    def test_initialization_default_values(self):
        """Test initialization with default values."""
        with patch.dict('sys.modules', {'display_tty': MagicMock()}):
            mock_runtime = MagicMock()
            mock_runtime.get.return_value = MagicMock()

            with patch('src.libs.docs.redoc.redoc_class.RI', mock_runtime):
                handler = RedocHandler()
                assert handler.success == 0
                assert handler.error == 84
                assert handler.debug is False

    def test_initialization_custom_values(self):
        """Test initialization with custom values."""
        with patch.dict('sys.modules', {'display_tty': MagicMock()}):
            mock_runtime = MagicMock()
            mock_runtime.get.return_value = MagicMock()

            with patch('src.libs.docs.redoc.redoc_class.RI', mock_runtime):
                handler = RedocHandler(success=100, error=200, debug=True)
                assert handler.success == 100
                assert handler.error == 200
                assert handler.debug is True


class TestRedocHandlerConstants:
    """Test ReDoc constants."""

    def test_redoc_url_constant(self):
        """Verify REDOC_URL constant is defined."""
        assert hasattr(REDOC_CONST, 'REDOC_URL')
        assert isinstance(REDOC_CONST.REDOC_URL, str)
        assert len(REDOC_CONST.REDOC_URL) > 0

    def test_openapi_url_constant(self):
        """Verify OPENAPI_URL constant is defined."""
        assert hasattr(REDOC_CONST, 'OPENAPI_URL')
        assert isinstance(REDOC_CONST.OPENAPI_URL, str)

    def test_api_title_constant(self):
        """Verify API_TITLE constant is defined."""
        assert hasattr(REDOC_CONST, 'API_TITLE')
        assert isinstance(REDOC_CONST.API_TITLE, str)

    def test_api_version_constant(self):
        """Verify API_VERSION constant is defined."""
        assert hasattr(REDOC_CONST, 'API_VERSION')
        assert isinstance(REDOC_CONST.API_VERSION, str)

    def test_contact_info_constant(self):
        """Verify CONTACT_INFO constant is defined."""
        assert hasattr(REDOC_CONST, 'CONTACT_INFO')
        assert isinstance(REDOC_CONST.CONTACT_INFO, dict)


class TestRedocHandlerInjection:
    """Test ReDoc injection into FastAPI app."""

    def test_inject_success(self):
        """Test successful ReDoc injection."""
        with patch.dict('sys.modules', {'display_tty': MagicMock()}):
            mock_runtime = MagicMock()
            mock_app = Mock(spec=FastAPI)

            mock_path_manager = MagicMock()
            mock_path_manager.add_path.return_value = 0
            mock_runtime.get.side_effect = lambda x, *args, **kwargs: mock_path_manager

            with patch('src.libs.docs.redoc.redoc_class.RI', mock_runtime):
                handler = RedocHandler()
                result = handler.inject(mock_app)

                assert result == handler.success

    def test_inject_invalid_app_type(self):
        """Test injection with invalid app type."""
        with patch.dict('sys.modules', {'display_tty': MagicMock()}):
            mock_runtime = MagicMock()
            mock_runtime.get.return_value = MagicMock()

            with patch('src.libs.docs.redoc.redoc_class.RI', mock_runtime):
                handler = RedocHandler()
                result = handler.inject("not_a_fastapi_app")

                assert result == handler.error
