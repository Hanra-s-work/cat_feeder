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
# FILE: test_final_class.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Unit tests for the FinalClass metaclass.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Comprehensive test suite for FinalClass metaclass.
# // AR
# +==== END CatFeeder =================+
"""
import pytest

try:
    from libs.core import FinalClass
except Exception:
    from src.libs.core import FinalClass


class TestFinalClassMetaclass:
    """Test FinalClass metaclass functionality."""

    def test_can_create_final_class(self):
        """Verify FinalClass can be used as a metaclass."""
        class FinalService(metaclass=FinalClass):
            pass

        assert FinalService is not None
        assert isinstance(FinalService, FinalClass)

    def test_final_class_cannot_be_subclassed(self):
        """Verify that a final class cannot be subclassed."""
        class FinalService(metaclass=FinalClass):
            pass

        with pytest.raises(TypeError) as exc_info:
            class DerivedService(FinalService):
                pass

        assert "final" in str(exc_info.value).lower()
        assert "cannot be subclassed" in str(exc_info.value)

    def test_error_message_includes_class_name(self):
        """Verify error message includes the final class name."""
        class MyFinalClass(metaclass=FinalClass):
            pass

        with pytest.raises(TypeError) as exc_info:
            class Derived(MyFinalClass):
                pass

        assert "MyFinalClass" in str(exc_info.value)

    def test_multiple_final_classes_independent(self):
        """Verify multiple final classes are independent."""
        class FinalA(metaclass=FinalClass):
            pass

        class FinalB(metaclass=FinalClass):
            pass

        # Both should be final
        with pytest.raises(TypeError):
            class DerivedA(FinalA):
                pass

        with pytest.raises(TypeError):
            class DerivedB(FinalB):
                pass

    def test_final_class_can_have_methods(self):
        """Verify final class can contain methods."""
        class FinalService(metaclass=FinalClass):
            def method(self):
                return "test"

        instance = FinalService()
        assert instance.method() == "test"

    def test_final_class_can_have_attributes(self):
        """Verify final class can contain attributes."""
        class FinalService(metaclass=FinalClass):
            value = 42

        assert FinalService.value == 42

    def test_final_class_can_have_init(self):
        """Verify final class can have __init__ method."""
        class FinalService(metaclass=FinalClass):
            def __init__(self, value):
                self.value = value

        instance = FinalService(42)
        assert instance.value == 42

    def test_final_class_with_multiple_bases_fails(self):
        """Verify subclassing final class fails even with multiple inheritance."""
        class FinalService(metaclass=FinalClass):
            pass

        class OtherClass:
            pass

        with pytest.raises(TypeError):
            class Derived(FinalService, OtherClass):
                pass

    def test_final_class_instance_is_valid(self):
        """Verify instances of final classes work correctly."""
        class FinalService(metaclass=FinalClass):
            def __init__(self):
                self.initialized = True

        instance = FinalService()
        assert instance.initialized is True

    def test_final_class_with_class_methods(self):
        """Verify final class can have class methods."""
        class FinalService(metaclass=FinalClass):
            @classmethod
            def create(cls):
                return cls()

        instance = FinalService.create()
        assert isinstance(instance, FinalService)

    def test_final_class_with_static_methods(self):
        """Verify final class can have static methods."""
        class FinalService(metaclass=FinalClass):
            @staticmethod
            def static_method():
                return 42

        assert FinalService.static_method() == 42

    def test_final_class_with_properties(self):
        """Verify final class can have properties."""
        class FinalService(metaclass=FinalClass):
            def __init__(self):
                self._value = 42

            @property
            def value(self):
                return self._value

        instance = FinalService()
        assert instance.value == 42


class TestFinalClassDocstring:
    """Test FinalClass metaclass documentation."""

    def test_metaclass_has_docstring(self):
        """Verify FinalClass has a docstring."""
        assert FinalClass.__doc__ is not None
        assert len(FinalClass.__doc__) > 0

    def test_metaclass_mentions_final(self):
        """Verify docstring mentions 'final' concept."""
        assert "final" in FinalClass.__doc__.lower()
