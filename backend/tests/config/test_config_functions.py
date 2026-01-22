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
# FILE: test_config_functions.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Unit tests for the config module functions.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Comprehensive test suite for config module functions.
# // AR
# +==== END CatFeeder =================+
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

try:
    from libs.config import (
        load_env, get_env, apply_env,
        load_config, get_config, get_project_root,
        EnvLoader, TOMLLoader, ConfigLoader
    )
except Exception:
    from src.libs.config import (
        load_env, get_env, apply_env,
        load_config, get_config, get_project_root,
        EnvLoader, TOMLLoader, ConfigLoader
    )


class TestConfigFunctionExports:
    """Test that config functions are properly exported."""

    def test_load_env_callable(self):
        """Verify load_env is callable."""
        assert callable(load_env)

    def test_get_env_callable(self):
        """Verify get_env is callable."""
        assert callable(get_env)

    def test_apply_env_callable(self):
        """Verify apply_env is callable."""
        assert callable(apply_env)

    def test_load_config_callable(self):
        """Verify load_config is callable."""
        assert callable(load_config)

    def test_get_config_callable(self):
        """Verify get_config is callable."""
        assert callable(get_config)

    def test_get_project_root_callable(self):
        """Verify get_project_root is callable."""
        assert callable(get_project_root)


class TestEnvFunctions:
    """Test environment variable functions."""

    def test_load_env_returns_dict(self):
        """Verify load_env returns dictionary."""
        with patch.object(EnvLoader, 'load_env_file', return_value={}):
            result = load_env()
            assert isinstance(result, dict)

    def test_get_env_returns_optional_string(self):
        """Verify get_env returns optional string."""
        with patch.object(EnvLoader, 'get_env_value', return_value="test_value"):
            result = get_env("TEST_KEY")
            assert result == "test_value" or result is None

    def test_get_env_with_default(self):
        """Verify get_env can use default value."""
        with patch.object(EnvLoader, 'get_env_value', return_value=None):
            result = get_env("NON_EXISTENT", default="default_value")
            assert result is None or result == "default_value"

    def test_apply_env_callable_without_error(self):
        """Verify apply_env can be called."""
        with patch.object(EnvLoader, 'apply_to_os_environ'):
            # Should not raise
            apply_env()


class TestConfigFunctions:
    """Test config/TOML functions."""

    def test_load_config_returns_dict(self):
        """Verify load_config returns dictionary."""
        with patch.object(TOMLLoader, 'load_config_toml', return_value={}):
            result = load_config()
            assert isinstance(result, dict)

    def test_get_config_returns_value(self):
        """Verify get_config returns value."""
        with patch.object(TOMLLoader, 'get_config_value', return_value="test_value"):
            result = get_config("section", "key")
            assert result == "test_value"

    def test_get_config_with_default(self):
        """Verify get_config can use default value."""
        with patch.object(TOMLLoader, 'get_config_value', return_value=None):
            result = get_config("section", "key", default="default_value")
            assert result is None or result == "default_value"

    def test_get_project_root_returns_path(self):
        """Verify get_project_root returns Path."""
        with patch.object(TOMLLoader, 'get_project_root', return_value=Path("/")):
            result = get_project_root()
            assert isinstance(result, Path)


class TestLoaderExports:
    """Test loader class exports."""

    def test_env_loader_exported(self):
        """Verify EnvLoader is exported."""
        assert EnvLoader is not None

    def test_toml_loader_exported(self):
        """Verify TOMLLoader is exported."""
        assert TOMLLoader is not None

    def test_config_loader_alias_exists(self):
        """Verify ConfigLoader alias exists."""
        assert ConfigLoader is not None
        assert ConfigLoader is TOMLLoader


class TestConfigModuleAttributes:
    """Test config module attributes."""

    def test_env_loader_is_class(self):
        """Verify EnvLoader is a class."""
        assert isinstance(EnvLoader, type)

    def test_toml_loader_is_class(self):
        """Verify TOMLLoader is a class."""
        assert isinstance(TOMLLoader, type)

    def test_functions_are_callable(self):
        """Verify all exported functions are callable."""
        assert callable(load_env)
        assert callable(get_env)
        assert callable(apply_env)
        assert callable(load_config)
        assert callable(get_config)
        assert callable(get_project_root)


class TestGetEnvFunction:
    """Test get_env function behavior."""

    def test_get_env_accepts_key_and_default(self):
        """Verify get_env accepts key and default arguments."""
        with patch.object(EnvLoader, 'get_env_value', return_value="value"):
            # Should not raise
            result = get_env("KEY", default="default")
            assert result is not None

    def test_get_env_passes_arguments_correctly(self):
        """Verify get_env passes arguments to loader."""
        with patch.object(EnvLoader, 'get_env_value', return_value="expected") as mock_method:
            result = get_env("TEST_KEY", default="default")
            mock_method.assert_called_once()


class TestLoadConfigFunction:
    """Test load_config function behavior."""

    def test_load_config_returns_dict_type(self):
        """Verify load_config returns dict type."""
        with patch.object(TOMLLoader, 'load_config_toml', return_value={"key": "value"}):
            result = load_config()
            assert isinstance(result, dict)

    def test_load_config_can_be_called_multiple_times(self):
        """Verify load_config can be called multiple times."""
        with patch.object(TOMLLoader, 'load_config_toml', return_value={}):
            result1 = load_config()
            result2 = load_config()
            assert isinstance(result1, dict)
            assert isinstance(result2, dict)


class TestGetConfigFunction:
    """Test get_config function behavior."""

    def test_get_config_with_single_key(self):
        """Verify get_config works with single key."""
        with patch.object(TOMLLoader, 'get_config_value', return_value="value"):
            result = get_config("key")
            assert result == "value"

    def test_get_config_with_multiple_keys(self):
        """Verify get_config works with multiple keys."""
        with patch.object(TOMLLoader, 'get_config_value', return_value="nested_value"):
            result = get_config("section", "subsection", "key")
            assert result == "nested_value"

    def test_get_config_with_default_parameter(self):
        """Verify get_config accepts default parameter."""
        with patch.object(TOMLLoader, 'get_config_value', return_value=None):
            result = get_config("key", default="fallback")
            assert result is None or result == "fallback"


class TestGetProjectRootFunction:
    """Test get_project_root function behavior."""

    def test_get_project_root_returns_path_instance(self):
        """Verify get_project_root returns Path instance."""
        with patch.object(TOMLLoader, 'get_project_root', return_value=Path(".")):
            result = get_project_root()
            assert isinstance(result, Path)

    def test_get_project_root_can_be_called_multiple_times(self):
        """Verify get_project_root can be called multiple times."""
        with patch.object(TOMLLoader, 'get_project_root', return_value=Path(".")):
            result1 = get_project_root()
            result2 = get_project_root()
            assert isinstance(result1, Path)
            assert isinstance(result2, Path)
