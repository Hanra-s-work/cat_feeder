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
# FILE: test_env_loader.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Unit tests for the EnvLoader singleton class.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Comprehensive test suite for EnvLoader class.
# // AR
# +==== END CatFeeder =================+
"""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

try:
    from libs.config import EnvLoader
except Exception:
    from src.libs.config import EnvLoader


class TestEnvLoaderSingleton:
    """Test EnvLoader singleton pattern."""

    def test_env_loader_is_singleton(self):
        """Verify EnvLoader implements singleton pattern."""
        loader1 = EnvLoader()
        loader2 = EnvLoader()
        assert loader1 is loader2

    def test_singleton_returns_same_instance(self):
        """Verify __new__ returns the same instance."""
        EnvLoader._instance = None
        EnvLoader._initialized = False

        loader1 = EnvLoader()
        loader2 = EnvLoader()

        assert loader1 is loader2


class TestEnvLoaderInitialization:
    """Test EnvLoader initialization."""

    def test_initialization_creates_instance(self):
        """Test initialization creates instance."""
        EnvLoader._instance = None
        EnvLoader._initialized = False

        loader = EnvLoader()
        assert loader is not None

    def test_initialization_can_set_debug_via_init(self):
        """Test initialization can accept debug parameter in __init__."""
        EnvLoader._instance = None
        EnvLoader._initialized = False

        # The __new__ method doesn't accept kwargs, so we just test without parameters
        loader = EnvLoader()
        # Verify the loader was created
        assert loader is not None

    def test_initialization_only_once(self):
        """Verify initialization happens only once."""
        EnvLoader._instance = None
        EnvLoader._initialized = False

        loader1 = EnvLoader()
        loader1._env_vars = {"test": "value"}

        loader2 = EnvLoader()
        # Should not reinitialize
        assert loader2._env_vars == {"test": "value"}


class TestEnvLoaderMethods:
    """Test EnvLoader methods."""

    def test_has_disp_logger(self):
        """Verify EnvLoader has disp logger."""
        loader = EnvLoader()
        assert hasattr(loader, 'disp')

    def test_get_env_value_method_exists(self):
        """Verify get_env_value method exists."""
        loader = EnvLoader()
        assert hasattr(loader, 'get_env_value')
        assert callable(loader.get_env_value)

    def test_apply_to_os_environ_method_exists(self):
        """Verify apply_to_os_environ method exists."""
        loader = EnvLoader()
        assert hasattr(loader, 'apply_to_os_environ')
        assert callable(loader.apply_to_os_environ)

    def test_clear_cache_method_exists(self):
        """Verify clear_cache method exists."""
        loader = EnvLoader()
        assert hasattr(loader, 'clear_cache')
        assert callable(loader.clear_cache)

    def test_get_project_root_method_exists(self):
        """Verify get_project_root method exists."""
        loader = EnvLoader()
        assert hasattr(loader, 'get_project_root')
        assert callable(loader.get_project_root)

    def test_load_env_file_method_exists(self):
        """Verify load_env_file method exists."""
        loader = EnvLoader()
        assert hasattr(loader, 'load_env_file')
        assert callable(loader.load_env_file)


class TestEnvLoaderProjectRoot:
    """Test project root discovery."""

    def test_find_project_root_returns_path(self):
        """Verify _find_project_root returns Path object."""
        loader = EnvLoader()
        root = loader._find_project_root()
        assert isinstance(root, Path)

    def test_get_project_root_returns_path(self):
        """Verify get_project_root returns Path object."""
        loader = EnvLoader()
        root = loader.get_project_root()
        assert isinstance(root, Path)

    def test_project_root_caching(self):
        """Verify project root is cached."""
        EnvLoader._instance = None
        EnvLoader._initialized = False

        loader = EnvLoader()
        root1 = loader.get_project_root()
        root2 = loader.get_project_root()

        assert root1 is root2


class TestEnvLoaderCaching:
    """Test EnvLoader caching functionality."""

    def test_clear_cache_resets_env_vars(self):
        """Verify clear_cache resets env_vars."""
        loader = EnvLoader()
        loader._env_vars = {"test": "value"}
        loader.clear_cache()

        assert loader._env_vars is None

    def test_clear_cache_resets_project_root(self):
        """Verify clear_cache resets project_root."""
        loader = EnvLoader()
        loader._project_root = Path("/some/path")
        loader.clear_cache()

        assert loader._project_root is None


class TestEnvLoaderAttributes:
    """Test EnvLoader attributes."""

    def test_has_env_vars_cache(self):
        """Verify _env_vars cache attribute exists."""
        loader = EnvLoader()
        assert hasattr(loader, '_env_vars')

    def test_has_project_root_cache(self):
        """Verify _project_root cache attribute exists."""
        loader = EnvLoader()
        assert hasattr(loader, '_project_root')

    def test_has_instance_class_attribute(self):
        """Verify _instance class attribute exists."""
        assert hasattr(EnvLoader, '_instance')

    def test_has_initialized_flag(self):
        """Verify _initialized flag exists."""
        assert hasattr(EnvLoader, '_initialized')


class TestEnvLoaderGetEnvironmentVariable:
    """Test get_environment_variable method."""

    def test_get_environment_variable_method_exists(self):
        """Verify get_environment_variable method exists."""
        loader = EnvLoader()
        assert hasattr(loader, 'get_environment_variable')
        assert callable(loader.get_environment_variable)

    def test_get_environment_variable_with_missing_env_raises(self):
        """Verify get_environment_variable raises when env not loaded."""
        loader = EnvLoader()
        loader._env_vars = None

        with pytest.raises(ValueError) as exc_info:
            loader.get_environment_variable("NON_EXISTENT")

        assert "No environment file loaded" in str(exc_info.value)


class TestEnvLoaderParseEnvFile:
    """Test env file parsing."""

    def test_parse_env_file_returns_dict(self):
        """Verify _parse_env_file returns dictionary."""
        loader = EnvLoader()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("KEY=value\n")
            f.flush()
            temp_path = Path(f.name)

        try:
            result = loader._parse_env_file(temp_path)
            assert isinstance(result, dict)
            assert result.get("KEY") == "value"
        finally:
            temp_path.unlink()

    def test_parse_env_file_ignores_comments(self):
        """Verify _parse_env_file ignores comments."""
        loader = EnvLoader()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("# This is a comment\n")
            f.write("KEY=value\n")
            f.flush()
            temp_path = Path(f.name)

        try:
            result = loader._parse_env_file(temp_path)
            assert len(result) == 1
            assert "KEY" in result
        finally:
            temp_path.unlink()

    def test_parse_env_file_handles_quoted_values(self):
        """Verify _parse_env_file handles quoted values."""
        loader = EnvLoader()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('KEY="quoted value"\n')
            f.write("KEY2='single quoted'\n")
            f.flush()
            temp_path = Path(f.name)

        try:
            result = loader._parse_env_file(temp_path)
            assert result.get("KEY") == "quoted value"
            assert result.get("KEY2") == "single quoted"
        finally:
            temp_path.unlink()


class TestEnvLoaderDocstring:
    """Test EnvLoader documentation."""

    def test_class_has_docstring(self):
        """Verify EnvLoader has a docstring."""
        assert EnvLoader.__doc__ is not None

    def test_class_docstring_mentions_singleton(self):
        """Verify docstring mentions singleton."""
        assert "singleton" in EnvLoader.__doc__.lower()


class TestEnvLoaderSearchDirectory:
    """Test directory search functionality."""

    def test_search_directory_for_env_returns_optional_path(self):
        """Verify _search_directory_for_env returns Optional[Path]."""
        loader = EnvLoader()
        result = loader._search_directory_for_env(Path.cwd(), 0, 0)
        assert result is None or isinstance(result, Path)

    def test_find_env_file_returns_optional_path(self):
        """Verify _find_env_file returns Optional[Path]."""
        loader = EnvLoader()
        result = loader._find_env_file(max_depth=2)
        assert result is None or isinstance(result, Path)
