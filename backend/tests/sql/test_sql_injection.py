r"""
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
# FILE: test_sql_injection.py
# CREATION DATE: 11-12-2025
# LAST Modified: 14:55:12 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file in charge of checking the injection prevention measures for sql that are implemented in the sql library binder.
# // AR
# +==== END CatFeeder =================+
"""
import pytest

try:
    # Import path when running from project root
    from libs.sql.sql_injection import SQLInjection
except ImportError:
    # Import path when running from backend directory
    from src.libs.sql.sql_injection import SQLInjection


@pytest.fixture
def injector():
    """Create and return an SQLInjection instance for testing.

    Returns:
        SQLInjection: A configured SQL injection detector with debug mode disabled.
    """
    return SQLInjection(debug=False)


def test_email_not_flagged(injector):
    """Test that legitimate email addresses are not flagged as SQL injection."""
    assert injector.check_if_symbol_sql_injection("my.real@email.com") is False


def test_single_at_variable_flagged(injector):
    """Test that SQL variable syntax (@var) is correctly flagged as injection.

    The @ symbol is commonly used in some SQL dialects for variables
    and should be flagged when not part of a valid email address.
    """
    assert injector.check_if_symbol_sql_injection("@var") is True


def test_double_at_system_var_flagged(injector):
    """Test that SQL system variable syntax (@@version) is flagged as injection."""
    assert injector.check_if_symbol_sql_injection("@@version") is True


def test_sql_keyword_flagged(injector):
    """Test that SQL keywords (SELECT, FROM, etc.) are detected as injection attempts."""
    assert injector.check_if_command_sql_injection(
        "SELECT * FROM users;") is True


def test_semicolon_symbol_flagged(injector):
    """Test that semicolons are detected as potential SQL injection symbols."""
    assert injector.check_if_symbol_sql_injection("some;thing") is True


def test_base64_detection(injector):
    """Test base64 detection logic with injection symbols.

    Base64 check happens after email normalization but before symbol scanning.
    The semicolon in ";base64" is flagged as a symbol before reaching base64
    validation. This is expected behavior - base64 data should be URL-safe
    encoded in production.
    """
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
    """Test that plain email addresses are not flagged as SQL injection.

    Verifies both symbol and command injection checkers correctly identify
    valid email addresses and do not raise false positives.
    """
    assert injector.check_if_symbol_sql_injection("user@example.com") is False
    assert injector.check_if_command_sql_injection("user@example.com") is False


def test_quoted_email_not_flagged(injector):
    """Test that quoted email addresses are not flagged as SQL injection.

    Emails wrapped in single or double quotes are common in form data
    and database queries. These should be recognized as legitimate emails.
    """
    assert injector.check_if_symbol_sql_injection(
        "'user@example.com'") is False
    assert injector.check_if_symbol_sql_injection(
        '"user@example.com"') is False


def test_key_value_email_not_flagged(injector):
    """Test that emails in key=value format are not flagged as SQL injection.

    Form data and query parameters often use key=value format. The injection
    checker should extract and validate the email portion correctly.
    """
    assert injector.check_if_symbol_sql_injection(
        "email='user@example.com'") is False
    assert injector.check_if_command_sql_injection(
        "email='user@example.com'") is False


def test_email_with_special_chars_not_flagged(injector):
    """Test that emails with RFC-compliant special characters are not flagged.

    RFC 5322 allows various special characters in email addresses including
    plus signs (+) and dots (.). These should be recognized as valid.
    """
    assert injector.check_if_symbol_sql_injection(
        "user+tag@example.com") is False
    assert injector.check_if_symbol_sql_injection(
        "user.name@example.com") is False


def test_unicode_email_not_flagged(injector):
    """Test that internationalized email addresses are not flagged.

    RFC 6530 defines internationalized email addresses that can contain
    Unicode characters. These should be validated correctly.
    """
    assert injector.check_if_symbol_sql_injection(
        "user+tag@exämple.com") is False


def test_email_with_trailing_sql_flagged(injector):
    """Test that email-like strings with trailing SQL are flagged as injection.

    This is a critical security test. Attackers may try to bypass email
    validation by appending SQL commands after a valid email address.
    The fullmatch requirement prevents this bypass technique.
    """
    assert injector.check_if_symbol_sql_injection(
        "user@example.com; DROP TABLES;") is True
    assert injector.check_if_command_sql_injection(
        "hello@world.com; DROP TABLES;") is True


def test_sql_injection_with_at_symbol_flagged(injector):
    """Test that SQL injection attempts containing @ are still flagged.

    Attackers may try to disguise SQL injection by including @ symbols
    to make the payload look like an email. The checker must detect
    SQL keywords and symbols regardless of @ presence.
    """
    assert injector.check_if_symbol_sql_injection(
        "DROP mydatabase; --@gmail.com") is True
    assert injector.check_if_command_sql_injection(
        "DROP mydatabase; --@gmail.com") is True


def test_invalid_email_domain_flagged(injector):
    """Test that emails with invalid top-level domains are flagged.

    Email addresses must have a valid TLD (at least 2 characters).
    Strings that look like emails but have invalid domains should
    be flagged as potential injection attempts.
    """
    assert injector.check_if_symbol_sql_injection(
        "not_an_email@notvalid") is True


# ==================== HELPER FUNCTION TESTS ====================


def test_extract_email_candidate_plain(injector):
    """Test _extract_email_candidate with plain email address.

    Verifies that the helper correctly extracts an unmodified email
    when no quotes or key=value wrappers are present.
    """
    result = injector._extract_email_candidate("user@example.com")
    assert result == "user@example.com"


def test_extract_email_candidate_quoted(injector):
    """Test _extract_email_candidate strips surrounding quotes.

    Verifies that both single and double quotes are properly removed
    from email addresses during extraction.
    """
    result = injector._extract_email_candidate("'user@example.com'")
    assert result == "user@example.com"
    result = injector._extract_email_candidate('"user@example.com"')
    assert result == "user@example.com"


def test_extract_email_candidate_key_value(injector):
    """Test _extract_email_candidate handles key=value format.

    Verifies that the helper correctly extracts the email value from
    key=value pairs commonly found in form data and query parameters.
    """
    result = injector._extract_email_candidate("email='user@example.com'")
    assert result == "user@example.com"


def test_extract_email_candidate_no_at(injector):
    """Test _extract_email_candidate returns None for strings without @.

    Strings without the @ symbol cannot be valid email addresses and
    should be rejected early in the extraction process.
    """
    result = injector._extract_email_candidate("no_at_symbol")
    assert result is None


def test_extract_email_candidate_with_whitespace(injector):
    """Test _extract_email_candidate rejects strings with internal whitespace.

    Email addresses cannot contain spaces. Strings with whitespace should
    be rejected to prevent injection attempts that use spaces to separate
    email-like tokens from SQL commands.
    """
    result = injector._extract_email_candidate("user @example.com")
    assert result is None


def test_validate_and_normalize_email_valid(injector):
    """Test _is_email with valid email addresses.

    Verifies that valid email addresses are accepted and a normalized
    version is returned. The normalized form may differ from the input
    but should still be a valid email containing @.
    """
    result = injector._is_email("user@example.com")
    assert result is not None
    assert "@" in result


def test_validate_and_normalize_email_with_trailing_sql(injector):
    """Test _is_email rejects emails with trailing SQL commands.

    This verifies the fullmatch requirement: the entire input must be
    exactly an email address with no trailing content. This prevents
    attackers from bypassing validation with payloads like
    'user@example.com; DROP TABLES;'.
    """
    result = injector._is_email(
        "user@example.com; DROP TABLES;")
    assert result is None


def test_validate_and_normalize_email_key_value(injector):
    """Test _is_email with key=value format.

    Verifies that the validator correctly handles email addresses wrapped
    in key=value syntax and returns a normalized email value.
    """
    result = injector._is_email("email='user@example.com'")
    assert result is not None


def test_validate_and_normalize_email_invalid_domain(injector):
    """Test _is_email rejects emails with invalid domain names.

    Email addresses must have valid domain names with proper TLDs.
    The validator should return None for addresses with invalid domains
    like single-word domains without extensions.
    """
    result = injector._is_email("user@notvalid")
    assert result is None


# ==================== NUMERIC AND BASE64 TESTS ====================


def test_numeric_values_not_flagged(injector):
    """Test that numeric values are not flagged as SQL injection.

    Pure numeric values (integers and floats) cannot be SQL injection
    attempts and should be allowed without triggering false positives.
    """
    assert injector.check_if_symbol_sql_injection("12345") is False
    assert injector.check_if_command_sql_injection("12345") is False
    assert injector.check_if_symbol_sql_injection("123.45") is False


def test_none_values_not_flagged(injector):
    """Test that None values are not flagged as SQL injection.

    None/null values are legitimate in many contexts and should be
    handled gracefully without raising injection alerts.
    """
    assert injector.check_if_symbol_sql_injection(None) is False
    assert injector.check_if_command_sql_injection(None) is False


def test_list_with_injection_flagged(injector):
    """Test that lists containing injection attempts are properly flagged.

    When scanning arrays of strings, even a single malicious element
    should cause the entire list to be flagged. However, lists with
    only safe values (including valid emails) should pass validation.
    """
    assert injector.check_if_injections_in_strings(
        ["valid", "DROP TABLE"]) is True
    assert injector.check_if_injections_in_strings(
        ["user@example.com", "safe"]) is False


def test_nested_list_with_injection_flagged(injector):
    """Test that nested lists containing injection attempts are flagged.

    The checker must recursively scan nested data structures to detect
    injection attempts at any level of nesting.
    """
    assert injector.check_if_injections_in_strings(
        [["safe"], ["DROP TABLE"]]) is True


# ==================== LOGIC GATE TESTS ====================


def test_logic_gates_flagged(injector):
    """Test that SQL logical operators are detected as injection attempts.

    Logic gates (OR, AND, NOT) are commonly used in SQL injection attacks
    to manipulate query conditions. These should be flagged when found
    in user input.
    """
    assert injector.check_if_logic_gate_sql_injection("OR 1=1") is True
    assert injector.check_if_logic_gate_sql_injection("AND 1=1") is True
    assert injector.check_if_logic_gate_sql_injection("NOT EXISTS") is True


def test_email_not_flagged_by_logic_gate_check(injector):
    """Test that emails are not flagged by logic gate detection.

    Valid email addresses should pass all injection checks including
    the logic gate scanner, even though they contain the @ symbol.
    """
    assert injector.check_if_logic_gate_sql_injection(
        "user@example.com") is False


# ==================== COMBINED TESTS ====================


def test_combined_symbol_and_command(injector):
    """Test combined symbol and command injection detection.

    Verifies that the combined checker correctly flags inputs containing
    both SQL symbols and keywords, while still allowing valid emails.
    """
    assert injector.check_if_symbol_and_command_injection(
        "'; DROP TABLE users--") is True
    assert injector.check_if_symbol_and_command_injection(
        "user@example.com") is False


def test_all_injection_check(injector):
    """Test comprehensive SQL injection detection across all check types.

    The check_if_sql_injection method combines symbol, keyword, and logic
    gate detection. It should catch various injection patterns while
    correctly allowing legitimate values like emails and safe strings.
    """
    assert injector.check_if_sql_injection("SELECT * FROM users") is True
    assert injector.check_if_sql_injection("user@example.com") is False
    assert injector.check_if_sql_injection("'; DROP TABLE users--") is True


# ==================== UUID TOKEN TESTS ====================


def test_uuid_token_not_flagged(injector):
    """Test that UUID tokens are not flagged as SQL injection.

    UUIDs (with hyphens) are commonly used for session tokens, API keys,
    and unique identifiers. These should not be flagged despite containing
    hyphens which might resemble SQL comment markers in other contexts.
    """
    uuid = "00000000-0000-0000-0000-000000000001"
    assert injector.check_if_symbol_sql_injection(uuid) is False
    assert injector.check_if_command_sql_injection(uuid) is False
    assert injector.check_if_logic_gate_sql_injection(uuid) is False
    assert injector.check_if_sql_injection(uuid) is False


def test_raw_where_clause_with_quotes_flagged(injector):
    """Test that raw WHERE clauses containing quotes are flagged.

    When WHERE clause strings are pre-formatted with quotes (e.g.,
    "column='value'"), the quotes trigger symbol injection detection.
    This is correct behavior - WHERE clauses should be built using
    parameterized queries or by checking column/value separately.
    """
    # Pre-formatted WHERE clause with quotes should be flagged
    where_clause = "token='00000000-0000-0000-0000-000000000001'"
    assert injector.check_if_symbol_sql_injection(where_clause) is True


def test_where_clause_components_separately_not_flagged(injector):
    """Test that WHERE clause components checked separately are not flagged.

    Column names and values should be validated individually before being
    combined into a WHERE clause. When checked separately, legitimate
    values (like UUIDs) should pass validation.
    """
    column = "token"
    value = "00000000-0000-0000-0000-000000000001"

    assert injector.check_if_sql_injection(column) is False
    assert injector.check_if_sql_injection(value) is False
