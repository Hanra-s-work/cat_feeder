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
# FILE: test_final_singleton_class.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Unit tests for the FinalSingleton base class.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Comprehensive test suite for FinalSingleton class.
# // AR
# +==== END CatFeeder =================+
"""
import pytest
import threading

try:
    from libs.core import FinalSingleton
except Exception:
    from src.libs.core import FinalSingleton


class TestFinalSingletonConstruction:
    """Test FinalSingleton construction guard."""

    def test_direct_instantiation_fails(self):
        """Verify direct instantiation of FinalSingleton subclass fails."""
        class Config(FinalSingleton):
            pass

        with pytest.raises(RuntimeError) as exc_info:
            Config()

        assert "must be instantiated through RuntimeManager" in str(
            exc_info.value)

    def test_error_message_includes_class_name(self):
        """Verify error message includes the class name."""
        class MyService(FinalSingleton):
            pass

        with pytest.raises(RuntimeError) as exc_info:
            MyService()

        assert "MyService" in str(exc_info.value)

    def test_allowed_create_flag_enables_construction(self):
        """Verify _allow_create flag enables construction."""
        class Config(FinalSingleton):
            def __init__(self):
                self.value = 42

        # Without flag, should fail
        with pytest.raises(RuntimeError):
            Config()

        # With flag set, should succeed
        setattr(Config, "_allow_create", True)
        instance = Config()
        setattr(Config, "_allow_create", False)

        assert instance.value == 42

    def test_flag_is_reset_after_construction(self):
        """Verify flag can be toggled for construction control."""
        class Service(FinalSingleton):
            pass

        # Flag starts as False
        assert Service._allow_create is False

        # Can be temporarily set to True
        Service._allow_create = True
        Service()
        Service._allow_create = False

        assert Service._allow_create is False


class TestFinalSingletonInitialization:
    """Test FinalSingleton initialization."""

    def test_subclass_can_have_init(self):
        """Verify FinalSingleton subclass can have __init__."""
        class Service(FinalSingleton):
            def __init__(self, value):
                self.value = value

        Service._allow_create = True
        instance = Service(42)
        Service._allow_create = False

        assert instance.value == 42

    def test_subclass_can_have_custom_init_parameters(self):
        """Verify FinalSingleton subclass can accept various init parameters."""
        class Service(FinalSingleton):
            def __init__(self, a, b, c=None):
                self.a = a
                self.b = b
                self.c = c

        Service._allow_create = True
        instance = Service(1, 2, c=3)
        Service._allow_create = False

        assert instance.a == 1
        assert instance.b == 2
        assert instance.c == 3

    def test_subclass_can_have_methods(self):
        """Verify FinalSingleton subclass can have methods."""
        class Service(FinalSingleton):
            def get_value(self):
                return 42

        Service._allow_create = True
        instance = Service()
        Service._allow_create = False

        assert instance.get_value() == 42


class TestFinalSingletonLocking:
    """Test FinalSingleton thread locking."""

    def test_creation_lock_exists(self):
        """Verify _creation_lock attribute exists."""
        class Service(FinalSingleton):
            pass

        assert hasattr(Service, "_creation_lock")
        # threading.Lock() returns a lock object, verify it exists and is not None
        assert Service._creation_lock is not None
        # Verify it has the expected lock methods
        assert hasattr(Service._creation_lock, 'acquire')
        assert hasattr(Service._creation_lock, 'release')

    def test_lock_is_per_class(self):
        """Verify each FinalSingleton subclass has a lock."""
        class ServiceA(FinalSingleton):
            pass

        class ServiceB(FinalSingleton):
            pass

        # Both should have locks
        assert hasattr(ServiceA, "_creation_lock")
        assert hasattr(ServiceB, "_creation_lock")


class TestFinalSingletonAsyncInit:
    """Test FinalSingleton async initialization support."""

    def test_async_init_method_can_exist(self):
        """Verify async_init method can be defined."""
        class Service(FinalSingleton):
            async def async_init(self):
                self.initialized = True

        Service._allow_create = True
        instance = Service()
        Service._allow_create = False

        assert hasattr(instance, "async_init")
        assert callable(instance.async_init)

    def test_instance_without_async_init(self):
        """Verify instance works fine without async_init."""
        class Service(FinalSingleton):
            def __init__(self):
                self.value = 42

        Service._allow_create = True
        instance = Service()
        Service._allow_create = False

        assert instance.value == 42


class TestFinalSingletonAttributes:
    """Test FinalSingleton attributes."""

    def test_allow_create_default_is_false(self):
        """Verify _allow_create defaults to False."""
        class Service(FinalSingleton):
            pass

        assert Service._allow_create is False

    def test_subclass_inherits_allow_create(self):
        """Verify _allow_create is inherited by subclasses."""
        class BaseService(FinalSingleton):
            pass

        class DerivedService(BaseService):
            pass

        # Both should have the flag
        assert hasattr(BaseService, "_allow_create")
        assert hasattr(DerivedService, "_allow_create")


class TestFinalSingletonDocstring:
    """Test FinalSingleton documentation."""

    def test_class_has_docstring(self):
        """Verify FinalSingleton has a docstring."""
        assert FinalSingleton.__doc__ is not None
        assert len(FinalSingleton.__doc__) > 0

    def test_docstring_mentions_singleton(self):
        """Verify docstring mentions singleton concept."""
        assert "singleton" in FinalSingleton.__doc__.lower()

    def test_docstring_mentions_guard(self):
        """Verify docstring mentions construction guard."""
        assert "guard" in FinalSingleton.__doc__.lower()
