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
# FILE: test_sql_sanitisation_functions.py
# CREATION DATE: 11-12-2025
# LAST Modified: 14:55:21 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file that is in charge of testing the sanitisation functions of the sql library.
# // AR
# +==== END CatFeeder =================+
"""

try:
    # Import path when running from project root
    from libs.sql.sql_sanitisation_functions import SQLSanitiseFunctions
except ImportError:
    # Import path when running from backend directory
    from src.libs.sql.sql_sanitisation_functions import SQLSanitiseFunctions


def test_protect_sql_cell_escapes_chars():
    """Test that protect_sql_cell properly escapes special characters.

    Verifies that single quotes are escaped with backslash and backslashes
    themselves are doubled to prevent SQL injection through string escaping.
    """
    s = "a'b\\c"
    sf = SQLSanitiseFunctions(debug=False)
    out = sf.protect_sql_cell(s)
    # expected: a\'b\\c  (single quote becomes \' and backslash becomes \\)
    assert out == "a\\'b\\\\c"


def test__protect_value_quotes_and_escaping():
    """Test that _protect_value wraps strings in quotes and escapes internal quotes.

    Verifies SQL-standard quote doubling: single quotes inside strings are
    doubled ('') to escape them, and the entire value is wrapped in quotes.
    """
    sf = SQLSanitiseFunctions(debug=False)
    v = sf._protect_value("O'Reilly")
    assert v == "'O''Reilly'"


def test_check_sql_cell_none_and_basic():
    """Test check_sql_cell handles None values and returns raw strings.

    Verifies that None values are returned as-is when raw=True, and
    that basic strings are returned as raw values for parameterized queries.
    The MySQL driver handles escaping automatically when using %s placeholders.
    """
    sf = SQLSanitiseFunctions(debug=False)
    # raw=True and cell is None should return None
    assert sf.check_sql_cell(None, raw=True) is None
    # basic string should be returned raw (no extra quotes)
    assert sf.check_sql_cell("hello") == "hello"


def test_check_sql_cell_now_returns_timestamp_string():
    """Test that check_sql_cell converts 'now' keyword to timestamp value.

    The special keyword 'now' should be converted to an actual timestamp
    value as a raw string, not the literal string 'now'. This ensures
    proper temporal value handling in parameterized SQL queries.
    """
    sf = SQLSanitiseFunctions(debug=False)
    res = sf.check_sql_cell("now")
    # Should be a timestamp string (not literally "now")
    assert isinstance(res, str)
    assert res != "now"
    # Should look like a timestamp (contains date/time separators)
    assert any(char in res for char in ['-', ':', ' '])


def test_check_sql_cell_returns_raw_values():
    """Test that check_sql_cell returns raw values for parameterized queries.

    When using parameterized queries with %s placeholders, check_sql_cell
    should return raw values without adding extra quotes. The MySQL driver
    handles escaping automatically when the query is executed.
    """
    sf = SQLSanitiseFunctions(debug=False)

    # Test string value
    assert sf.check_sql_cell("test_value") == "test_value"

    # Test with special characters that would be escaped by protect_sql_cell
    result = sf.check_sql_cell("O'Reilly")
    assert isinstance(result, str)
    assert "O" in result  # Should contain the original content

    # Test numeric values with raw=True
    assert sf.check_sql_cell(123, raw=True) == 123
    assert sf.check_sql_cell(45.67, raw=True) == 45.67

    # Test None with raw=True
    assert sf.check_sql_cell(None, raw=True) is None


def test_check_sql_cell_uuid_tokens():
    """Test that check_sql_cell handles UUID tokens correctly.

    UUIDs are commonly used for session tokens and unique identifiers.
    They should be returned as raw strings for use in parameterized queries.
    """
    sf = SQLSanitiseFunctions(debug=False)
    uuid = "00000000-0000-0000-0000-000000000002"
    result = sf.check_sql_cell(uuid)
    assert result == uuid
