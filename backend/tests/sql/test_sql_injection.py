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
# FILE: test_sql_injection.py
# CREATION DATE: 11-12-2025
# LAST Modified: 7:26:21 13-12-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file in charge of checking the injection prevention measures for sql that are implemented in the sql library binder.
# // AR
# +==== END CatFeeder =================+
"""
import pytest

from libs.sql.sql_injection import SQLInjection


@pytest.fixture
def injector():
    return SQLInjection(debug=False)


def test_email_not_flagged(injector):
    assert injector.check_if_symbol_sql_injection("my.real@email.com") is False


def test_single_at_variable_flagged(injector):
    # @var is commonly used in some SQL dialects for variables and should be flagged
    assert injector.check_if_symbol_sql_injection("@var") is True


def test_double_at_system_var_flagged(injector):
    assert injector.check_if_symbol_sql_injection("@@version") is True


def test_sql_keyword_flagged(injector):
    assert injector.check_if_command_sql_injection(
        "SELECT * FROM users;") is True


def test_semicolon_symbol_flagged(injector):
    assert injector.check_if_symbol_sql_injection("some;thing") is True


def test_base64_detection(injector):
    # Note: base64 check happens after email normalization but before symbol scanning
    # The semicolon in ";base64" is flagged as a symbol before reaching base64 validation
    # This is expected behavior - base64 data should be URL-safe encoded in production
    s = "YWJjZA==;base64"
    # The semicolon triggers symbol detection first
    assert injector.check_if_symbol_sql_injection(s) is True

    # Test that valid base64 content without semicolon is not flagged
    valid_b64 = "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo"
    assert injector.check_if_symbol_sql_injection(valid_b64) is False


# ==================== EMAIL VALIDATION TESTS ====================


def test_plain_email_not_flagged(injector):
    """Plain emails should not be flagged as injection."""
    assert injector.check_if_symbol_sql_injection("user@example.com") is False
    assert injector.check_if_command_sql_injection("user@example.com") is False


def test_quoted_email_not_flagged(injector):
    """Single and double quoted emails should not be flagged."""
    assert injector.check_if_symbol_sql_injection(
        "'user@example.com'") is False
    assert injector.check_if_symbol_sql_injection(
        '"user@example.com"') is False


def test_key_value_email_not_flagged(injector):
    """Email in key=value format should not be flagged."""
    assert injector.check_if_symbol_sql_injection(
        "email='user@example.com'") is False
    assert injector.check_if_command_sql_injection(
        "email='user@example.com'") is False


def test_email_with_special_chars_not_flagged(injector):
    """Emails with RFC-compliant special characters should not be flagged."""
    assert injector.check_if_symbol_sql_injection(
        "user+tag@example.com") is False
    assert injector.check_if_symbol_sql_injection(
        "user.name@example.com") is False


def test_unicode_email_not_flagged(injector):
    """Unicode emails should not be flagged."""
    assert injector.check_if_symbol_sql_injection(
        "user+tag@exämple.com") is False


def test_email_with_trailing_sql_flagged(injector):
    """Email-like strings with trailing SQL should be flagged as injection."""
    assert injector.check_if_symbol_sql_injection(
        "user@example.com; DROP TABLES;") is True
    assert injector.check_if_command_sql_injection(
        "hello@world.com; DROP TABLES;") is True


def test_sql_injection_with_at_symbol_flagged(injector):
    """SQL injection attempts containing @ should still be flagged."""
    assert injector.check_if_symbol_sql_injection(
        "DROP mydatabase; --@gmail.com") is True
    assert injector.check_if_command_sql_injection(
        "DROP mydatabase; --@gmail.com") is True


def test_invalid_email_domain_flagged(injector):
    """Emails with invalid TLDs should be flagged."""
    assert injector.check_if_symbol_sql_injection(
        "not_an_email@notvalid") is True


# ==================== HELPER FUNCTION TESTS ====================


def test_extract_email_candidate_plain(injector):
    """Test _extract_email_candidate with plain email."""
    result = injector._extract_email_candidate("user@example.com")
    assert result == "user@example.com"


def test_extract_email_candidate_quoted(injector):
    """Test _extract_email_candidate strips quotes."""
    result = injector._extract_email_candidate("'user@example.com'")
    assert result == "user@example.com"
    result = injector._extract_email_candidate('"user@example.com"')
    assert result == "user@example.com"


def test_extract_email_candidate_key_value(injector):
    """Test _extract_email_candidate handles key=value."""
    result = injector._extract_email_candidate("email='user@example.com'")
    assert result == "user@example.com"


def test_extract_email_candidate_no_at(injector):
    """Test _extract_email_candidate returns None for non-email."""
    result = injector._extract_email_candidate("no_at_symbol")
    assert result is None


def test_extract_email_candidate_with_whitespace(injector):
    """Test _extract_email_candidate returns None for strings with whitespace."""
    result = injector._extract_email_candidate("user @example.com")
    assert result is None


def test_validate_and_normalize_email_valid(injector):
    """Test _is_email with valid emails."""
    result = injector._is_email("user@example.com")
    assert result is not None
    assert "@" in result


def test_validate_and_normalize_email_with_trailing_sql(injector):
    """Test _is_email rejects emails with trailing SQL."""
    result = injector._is_email(
        "user@example.com; DROP TABLES;")
    assert result is None


def test_validate_and_normalize_email_key_value(injector):
    """Test _is_email with key=value format."""
    result = injector._is_email("email='user@example.com'")
    assert result is not None


def test_validate_and_normalize_email_invalid_domain(injector):
    """Test _is_email rejects invalid domains."""
    result = injector._is_email("user@notvalid")
    assert result is None


# ==================== NUMERIC AND BASE64 TESTS ====================


def test_numeric_values_not_flagged(injector):
    """Numeric values should not be flagged."""
    assert injector.check_if_symbol_sql_injection("12345") is False
    assert injector.check_if_command_sql_injection("12345") is False
    assert injector.check_if_symbol_sql_injection("123.45") is False


def test_none_values_not_flagged(injector):
    """None values should not be flagged."""
    assert injector.check_if_symbol_sql_injection(None) is False
    assert injector.check_if_command_sql_injection(None) is False


def test_list_with_injection_flagged(injector):
    """Lists containing injection attempts should be flagged."""
    assert injector.check_if_injections_in_strings(
        ["valid", "DROP TABLE"]) is True
    assert injector.check_if_injections_in_strings(
        ["user@example.com", "safe"]) is False


def test_nested_list_with_injection_flagged(injector):
    """Nested lists containing injection attempts should be flagged."""
    assert injector.check_if_injections_in_strings(
        [["safe"], ["DROP TABLE"]]) is True


# ==================== LOGIC GATE TESTS ====================


def test_logic_gates_flagged(injector):
    """SQL logic gates should be flagged."""
    assert injector.check_if_logic_gate_sql_injection("OR 1=1") is True
    assert injector.check_if_logic_gate_sql_injection("AND 1=1") is True
    assert injector.check_if_logic_gate_sql_injection("NOT EXISTS") is True


def test_email_not_flagged_by_logic_gate_check(injector):
    """Emails should not be flagged by logic gate checks."""
    assert injector.check_if_logic_gate_sql_injection(
        "user@example.com") is False


# ==================== COMBINED TESTS ====================


def test_combined_symbol_and_command(injector):
    """Test combined symbol and command injection check."""
    assert injector.check_if_symbol_and_command_injection(
        "'; DROP TABLE users--") is True
    assert injector.check_if_symbol_and_command_injection(
        "user@example.com") is False


def test_all_injection_check(injector):
    """Test the comprehensive check_if_sql_injection method."""
    assert injector.check_if_sql_injection("SELECT * FROM users") is True
    assert injector.check_if_sql_injection("user@example.com") is False
    assert injector.check_if_sql_injection("'; DROP TABLE users--") is True
