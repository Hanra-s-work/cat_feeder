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
# FILE: test_runtime_manager.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Unit tests for the RuntimeManager service container.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Comprehensive test suite for RuntimeManager class.
# // AR
# +==== END CatFeeder =================+
"""
import pytest
from unittest.mock import MagicMock, patch

try:
    from libs.core import RuntimeManager, FinalSingleton
except Exception:
    from src.libs.core import RuntimeManager, FinalSingleton


class SimpleService:
    """Simple test service."""

    def __init__(self, value=42):
        self.value = value


class SimpleSingletonService(FinalSingleton):
    """Simple singleton service for testing."""

    def __init__(self, value=42):
        self.value = value


class TestRuntimeManagerSet:
    """Test RuntimeManager.set() method."""

    def test_set_plain_class(self):
        """Verify set() can register plain classes."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        RuntimeManager.set(SimpleService, 99)

        assert "SimpleService" in RuntimeManager._instances
        assert RuntimeManager._instances["SimpleService"].value == 99

    def test_set_singleton_class(self):
        """Verify set() can register FinalSingleton classes."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        RuntimeManager.set(SimpleSingletonService, 77)

        assert "SimpleSingletonService" in RuntimeManager._instances
        assert RuntimeManager._instances["SimpleSingletonService"].value == 77

    def test_set_idempotent(self):
        """Verify set() is idempotent."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        RuntimeManager.set(SimpleService, 1)
        first_instance = RuntimeManager._instances["SimpleService"]

        RuntimeManager.set(SimpleService, 2)
        second_instance = RuntimeManager._instances["SimpleService"]

        assert first_instance is second_instance


class TestRuntimeManagerGet:
    """Test RuntimeManager.get() method."""

    def test_get_registered_class(self):
        """Verify get() retrieves registered services."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        RuntimeManager.set(SimpleService, 42)
        instance = RuntimeManager.get(SimpleService)

        assert instance.value == 42

    def test_get_with_auto_register(self):
        """Verify get() with auto_register=True registers unregistered classes."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        instance = RuntimeManager.get(SimpleService, 88, auto_register=True)

        assert "SimpleService" in RuntimeManager._classes
        assert instance.value == 88

    def test_get_without_auto_register_fails(self):
        """Verify get() without auto_register=True raises for unregistered classes."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        with pytest.raises(RuntimeError) as exc_info:
            RuntimeManager.get(SimpleService, auto_register=False)

        assert "not registered" in str(exc_info.value)

    def test_get_by_string_name(self):
        """Verify get() can retrieve services by string name."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        RuntimeManager.set(SimpleService, 55)
        instance = RuntimeManager.get("SimpleService")

        assert instance.value == 55

    def test_get_by_string_unregistered_fails(self):
        """Verify get() by string fails for unregistered services."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        with pytest.raises(RuntimeError) as exc_info:
            RuntimeManager.get("NonexistentService")

        assert "not registered" in str(exc_info.value)

    def test_get_returns_same_instance(self):
        """Verify get() returns the same instance on multiple calls."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        RuntimeManager.set(SimpleService, 42)
        instance1 = RuntimeManager.get(SimpleService)
        instance2 = RuntimeManager.get(SimpleService)

        assert instance1 is instance2


class TestRuntimeManagerGetIfExists:
    """Test RuntimeManager.get_if_exists() method."""

    def test_get_if_exists_with_registered_service(self):
        """Verify get_if_exists() returns instance for registered services."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        RuntimeManager.set(SimpleService, 42)
        instance = RuntimeManager.get_if_exists(SimpleService)

        assert instance is not None
        assert instance.value == 42

    def test_get_if_exists_with_unregistered_service(self):
        """Verify get_if_exists() returns None for unregistered services."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        instance = RuntimeManager.get_if_exists(SimpleService)

        assert instance is None

    def test_get_if_exists_with_target(self):
        """Verify get_if_exists() returns target if provided."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        target = SimpleService(99)
        instance = RuntimeManager.get_if_exists(SimpleService, target=target)

        assert instance is target

    def test_get_if_exists_by_string(self):
        """Verify get_if_exists() works with string names."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        RuntimeManager.set(SimpleService, 42)
        instance = RuntimeManager.get_if_exists("SimpleService")

        assert instance is not None
        assert instance.value == 42


class TestRuntimeManagerExists:
    """Test RuntimeManager.exists() method."""

    def test_exists_returns_true_for_registered_class(self):
        """Verify exists() returns True for registered classes."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        RuntimeManager.set(SimpleService, 42)

        assert RuntimeManager.exists(SimpleService) is True

    def test_exists_returns_false_for_unregistered_class(self):
        """Verify exists() returns False for unregistered classes."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        assert RuntimeManager.exists(SimpleService) is False

    def test_exists_with_string_name(self):
        """Verify exists() works with string names."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        RuntimeManager.set(SimpleService, 42)

        assert RuntimeManager.exists("SimpleService") is True
        assert RuntimeManager.exists("NonexistentService") is False


class TestRuntimeManagerThreadSafety:
    """Test RuntimeManager thread safety."""

    def test_thread_lock_created_per_service(self):
        """Verify thread locks are created per service."""
        RuntimeManager._instances.clear()
        RuntimeManager._classes.clear()
        RuntimeManager._thread_locks.clear()

        RuntimeManager.set(SimpleService, 42)

        assert "SimpleService" in RuntimeManager._thread_locks


class TestRuntimeManagerDebug:
    """Test RuntimeManager debug functionality."""

    def test_update_debug_method_exists(self):
        """Verify update_debug() method exists."""
        assert hasattr(RuntimeManager, 'update_debug')
        assert callable(RuntimeManager.update_debug)

    def test_update_debug_callable(self):
        """Verify update_debug() can be called."""
        # Should not raise
        RuntimeManager.update_debug(True)
        RuntimeManager.update_debug(False)


class TestRuntimeManagerAttributes:
    """Test RuntimeManager class attributes."""

    def test_has_instances_dict(self):
        """Verify _instances dict exists."""
        assert hasattr(RuntimeManager, '_instances')
        assert isinstance(RuntimeManager._instances, dict)

    def test_has_classes_dict(self):
        """Verify _classes dict exists."""
        assert hasattr(RuntimeManager, '_classes')
        assert isinstance(RuntimeManager._classes, dict)

    def test_has_thread_locks_dict(self):
        """Verify _thread_locks dict exists."""
        assert hasattr(RuntimeManager, '_thread_locks')
        assert isinstance(RuntimeManager._thread_locks, dict)

    def test_has_disp_logger(self):
        """Verify _disp logger exists."""
        assert hasattr(RuntimeManager, '_disp')


class TestRuntimeManagerDocstring:
    """Test RuntimeManager documentation."""

    def test_class_has_docstring(self):
        """Verify RuntimeManager has a docstring."""
        assert RuntimeManager.__doc__ is not None

    def test_set_has_docstring(self):
        """Verify set() has a docstring."""
        assert RuntimeManager.set.__doc__ is not None

    def test_get_has_docstring(self):
        """Verify get() has a docstring."""
        assert RuntimeManager.get.__doc__ is not None

    def test_exists_has_docstring(self):
        """Verify exists() has a docstring."""
        assert RuntimeManager.exists.__doc__ is not None
