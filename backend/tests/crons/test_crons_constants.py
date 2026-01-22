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
# FILE: test_crons_constants.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Unit tests for the crons constants module.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Comprehensive test suite for cron configuration constants.
# // AR
# +==== END CatFeeder =================+
"""
import pytest

try:
    from libs.crons import crons_constants as CRON_CONST
except Exception:
    from src.libs.crons import crons_constants as CRON_CONST


class TestCronsConstants:
    """Test crons constants module."""

    def test_clean_tokens_is_boolean(self):
        """Verify CLEAN_TOKENS is a boolean."""
        assert isinstance(CRON_CONST.CLEAN_TOKENS, bool)

    def test_clean_tokens_interval_is_int(self):
        """Verify CLEAN_TOKENS_INTERVAL is an integer."""
        assert isinstance(CRON_CONST.CLEAN_TOKENS_INTERVAL, int)

    def test_clean_tokens_interval_is_positive(self):
        """Verify CLEAN_TOKENS_INTERVAL is positive."""
        assert CRON_CONST.CLEAN_TOKENS_INTERVAL > 0

    def test_enable_test_crons_is_boolean(self):
        """Verify ENABLE_TEST_CRONS is a boolean."""
        assert isinstance(CRON_CONST.ENABLE_TEST_CRONS, bool)

    def test_test_crons_interval_is_int(self):
        """Verify TEST_CRONS_INTERVAL is an integer."""
        assert isinstance(CRON_CONST.TEST_CRONS_INTERVAL, int)

    def test_test_crons_interval_is_positive(self):
        """Verify TEST_CRONS_INTERVAL is positive."""
        assert CRON_CONST.TEST_CRONS_INTERVAL > 0

    def test_check_actions_interval_is_int(self):
        """Verify CHECK_ACTIONS_INTERVAL is an integer."""
        assert isinstance(CRON_CONST.CHECK_ACTIONS_INTERVAL, int)

    def test_check_actions_interval_is_positive(self):
        """Verify CHECK_ACTIONS_INTERVAL is positive."""
        assert CRON_CONST.CHECK_ACTIONS_INTERVAL > 0

    def test_clean_verification_is_boolean(self):
        """Verify CLEAN_VERIFICATION is a boolean."""
        assert isinstance(CRON_CONST.CLEAN_VERIFICATION, bool)

    def test_clean_verification_interval_is_int(self):
        """Verify CLEAN_VERIFICATION_INTERVAL is an integer."""
        assert isinstance(CRON_CONST.CLEAN_VERIFICATION_INTERVAL, int)

    def test_clean_verification_interval_is_positive(self):
        """Verify CLEAN_VERIFICATION_INTERVAL is positive."""
        assert CRON_CONST.CLEAN_VERIFICATION_INTERVAL > 0

    def test_renew_oath_tokens_is_boolean(self):
        """Verify RENEW_OATH_TOKENS is a boolean."""
        assert isinstance(CRON_CONST.RENEW_OATH_TOKENS, bool)

    def test_renew_oath_tokens_interval_is_int(self):
        """Verify RENEW_OATH_TOKENS_INTERVAL is an integer."""
        assert isinstance(CRON_CONST.RENEW_OATH_TOKENS_INTERVAL, int)

    def test_renew_oath_tokens_interval_is_positive(self):
        """Verify RENEW_OATH_TOKENS_INTERVAL is positive."""
        assert CRON_CONST.RENEW_OATH_TOKENS_INTERVAL > 0

    def test_toml_instance_exists(self):
        """Verify TOML instance is available."""
        assert CRON_CONST.TOML is not None

    def test_idisp_instance_exists(self):
        """Verify IDISP instance is available."""
        assert CRON_CONST.IDISP is not None
