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
# FILE: test_runtime_controls.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Unit tests for the RuntimeControl singleton class.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Comprehensive test suite for RuntimeControl class.
# // AR
# +==== END CatFeeder =================+
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import signal

try:
    from libs.core import RuntimeControl, FinalSingleton
except Exception:
    from src.libs.core import RuntimeControl, FinalSingleton


@pytest.fixture()
def runtime_control_instance():
    """Create RuntimeControl instance with construction guard."""
    RuntimeControl._allow_create = True
    instance = RuntimeControl(debug=False)
    RuntimeControl._allow_create = False
    return instance


class TestRuntimeControlInitialization:
    """Test RuntimeControl initialization."""

    def test_runtime_control_is_final_singleton(self):
        """Verify RuntimeControl is a FinalSingleton."""
        assert issubclass(RuntimeControl, FinalSingleton)

    def test_initialization_with_default_values(self):
        """Test initialization with default values."""
        RuntimeControl._allow_create = True
        rc = RuntimeControl()
        RuntimeControl._allow_create = False

        assert rc.server_running is True
        assert rc.continue_running is True

    def test_initialization_with_debug_enabled(self):
        """Test initialization with debug enabled."""
        RuntimeControl._allow_create = True
        rc = RuntimeControl(debug=True)
        RuntimeControl._allow_create = False

        assert rc._debug is True

    def test_app_initialized_to_none(self, runtime_control_instance):
        """Verify app is initialized to None."""
        assert runtime_control_instance.app is None

    def test_config_initialized_to_none(self, runtime_control_instance):
        """Verify config is initialized to None."""
        assert runtime_control_instance.config is None

    def test_server_initialized_to_none(self, runtime_control_instance):
        """Verify server is initialized to None."""
        assert runtime_control_instance.server is None


class TestRuntimeControlAttributes:
    """Test RuntimeControl attributes."""

    def test_has_disp_logger(self, runtime_control_instance):
        """Verify disp logger attribute exists."""
        assert hasattr(runtime_control_instance, 'disp')

    def test_server_running_flag_accessible(self, runtime_control_instance):
        """Verify server_running flag is accessible."""
        assert isinstance(runtime_control_instance.server_running, bool)

    def test_continue_running_flag_accessible(self, runtime_control_instance):
        """Verify continue_running flag is accessible."""
        assert isinstance(runtime_control_instance.continue_running, bool)


class TestRuntimeControlHandleExit:
    """Test RuntimeControl exit handling."""

    def test_handle_exit_method_exists(self, runtime_control_instance):
        """Verify handle_exit method exists."""
        assert hasattr(runtime_control_instance, 'handle_exit')
        assert callable(runtime_control_instance.handle_exit)

    def test_handle_exit_with_no_server(self, runtime_control_instance):
        """Verify handle_exit doesn't crash when server is None."""
        runtime_control_instance.server = None
        # Should not raise
        runtime_control_instance.handle_exit(signal.SIGTERM, None)

    def test_handle_exit_with_server(self, runtime_control_instance):
        """Verify handle_exit delegates to server."""
        mock_server = MagicMock()
        runtime_control_instance.server = mock_server

        runtime_control_instance.handle_exit(signal.SIGTERM, None)

        mock_server.handle_exit.assert_called_once_with(signal.SIGTERM, None)


class TestRuntimeControlGracefulShutdown:
    """Test RuntimeControl graceful shutdown."""

    def test_graceful_shutdown_method_exists(self, runtime_control_instance):
        """Verify graceful_shutdown method exists."""
        assert hasattr(runtime_control_instance, 'graceful_shutdown')
        assert callable(runtime_control_instance.graceful_shutdown)

    def test_graceful_shutdown_sets_flags(self, runtime_control_instance):
        """Verify graceful_shutdown sets flags."""
        runtime_control_instance.server_running = True
        runtime_control_instance.continue_running = True

        runtime_control_instance.graceful_shutdown()

        assert runtime_control_instance.server_running is False
        assert runtime_control_instance.continue_running is False

    def test_graceful_shutdown_with_server(self, runtime_control_instance):
        """Verify graceful_shutdown sets server flag."""
        mock_server = MagicMock()
        runtime_control_instance.server = mock_server

        runtime_control_instance.graceful_shutdown()

        assert mock_server.should_exit is True

    def test_graceful_shutdown_without_server(self, runtime_control_instance):
        """Verify graceful_shutdown works without server."""
        runtime_control_instance.server = None

        # Should not raise
        runtime_control_instance.graceful_shutdown()

        assert runtime_control_instance.server_running is False
        assert runtime_control_instance.continue_running is False


class TestRuntimeControlStateManagement:
    """Test RuntimeControl state management."""

    def test_can_set_app(self, runtime_control_instance):
        """Verify app can be set."""
        mock_app = MagicMock()
        runtime_control_instance.app = mock_app
        assert runtime_control_instance.app is mock_app

    def test_can_set_config(self, runtime_control_instance):
        """Verify config can be set."""
        mock_config = MagicMock()
        runtime_control_instance.config = mock_config
        assert runtime_control_instance.config is mock_config

    def test_can_set_server(self, runtime_control_instance):
        """Verify server can be set."""
        mock_server = MagicMock()
        runtime_control_instance.server = mock_server
        assert runtime_control_instance.server is mock_server

    def test_can_toggle_server_running(self, runtime_control_instance):
        """Verify server_running flag can be toggled."""
        runtime_control_instance.server_running = False
        assert runtime_control_instance.server_running is False

        runtime_control_instance.server_running = True
        assert runtime_control_instance.server_running is True

    def test_can_toggle_continue_running(self, runtime_control_instance):
        """Verify continue_running flag can be toggled."""
        runtime_control_instance.continue_running = False
        assert runtime_control_instance.continue_running is False

        runtime_control_instance.continue_running = True
        assert runtime_control_instance.continue_running is True


class TestRuntimeControlDocstring:
    """Test RuntimeControl documentation."""

    def test_class_has_docstring(self):
        """Verify RuntimeControl has a docstring."""
        assert RuntimeControl.__doc__ is not None

    def test_handle_exit_has_docstring(self, runtime_control_instance):
        """Verify handle_exit has a docstring."""
        assert RuntimeControl.handle_exit.__doc__ is not None

    def test_graceful_shutdown_has_docstring(self, runtime_control_instance):
        """Verify graceful_shutdown has a docstring."""
        assert RuntimeControl.graceful_shutdown.__doc__ is not None
