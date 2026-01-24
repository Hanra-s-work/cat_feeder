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
# FILE: test_bucket_init.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Unit tests for bucket module __init__.py exports.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Verify correct exports from bucket module.
# // AR
# +==== END CatFeeder =================+
"""
import pytest

try:
    from libs import bucket as bucket_module
    from libs.bucket import Bucket
except Exception:
    from src.libs import bucket as bucket_module
    from src.libs.bucket import Bucket


class TestBucketModuleExports:
    """Test bucket module exports."""

    def test_bucket_class_exported(self):
        """Verify Bucket class is exported from bucket module."""
        assert hasattr(bucket_module, 'Bucket')

    def test_bucket_in_all(self):
        """Verify Bucket is in __all__."""
        assert hasattr(bucket_module, '__all__')
        assert 'Bucket' in bucket_module.__all__

    def test_bucket_direct_import(self):
        """Verify Bucket can be imported directly."""
        assert Bucket is not None
        assert hasattr(Bucket, '__init__')

    def test_bucket_class_is_callable(self):
        """Verify Bucket class is callable."""
        assert callable(Bucket)

    def test_bucket_docstring(self):
        """Verify Bucket has proper docstring."""
        assert Bucket.__doc__ is not None
