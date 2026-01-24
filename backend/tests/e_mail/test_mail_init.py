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
# FILE: test_mail_init.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Unit tests for email module __init__.py exports.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Verify correct exports from email module.
# // AR
# +==== END CatFeeder =================+
"""
import pytest

try:
    from libs import e_mail as mail_module
    from libs.e_mail import MailManagement
except Exception:
    from src.libs import e_mail as mail_module
    from src.libs.e_mail import MailManagement


class TestMailModuleExports:
    """Test email module exports."""

    def test_mail_management_class_exported(self):
        """Verify MailManagement class is exported from email module."""
        assert hasattr(mail_module, 'MailManagement')

    def test_mail_management_in_all(self):
        """Verify MailManagement is in __all__."""
        assert hasattr(mail_module, '__all__')
        assert 'MailManagement' in mail_module.__all__

    def test_mail_management_direct_import(self):
        """Verify MailManagement can be imported directly."""
        assert MailManagement is not None
        assert hasattr(MailManagement, '__init__')

    def test_mail_management_class_is_callable(self):
        """Verify MailManagement class is callable."""
        assert callable(MailManagement)

    def test_mail_management_docstring(self):
        """Verify MailManagement has proper docstring."""
        assert MailManagement.__doc__ is not None

    def test_mail_module_has_all_attribute(self):
        """Verify email module has __all__ attribute."""
        assert hasattr(mail_module, '__all__')
        assert isinstance(mail_module.__all__, list)

    def test_mail_module_all_contains_only_exports(self):
        """Verify __all__ contains only exported names."""
        assert len(mail_module.__all__) > 0
        for name in mail_module.__all__:
            assert hasattr(mail_module, name)
