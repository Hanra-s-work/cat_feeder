""" 
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
# FILE: test_sql_sanitisation_functions.py
# CREATION DATE: 11-12-2025
# LAST Modified: 7:43:55 13-12-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file that is in charge of testing the sanitisation functions of the sql library.
# // AR
# +==== END CatFeeder =================+
"""

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
    """Test check_sql_cell handles None values and basic string wrapping.

    Verifies that None values are returned as-is when raw=True, and
    that basic strings are properly wrapped in double quotes for SQL safety.
    """
    sf = SQLSanitiseFunctions(debug=False)
    # raw=True and cell is None should return None
    assert sf.check_sql_cell(None, raw=True) is None
    # basic string should be wrapped in double quotes
    assert sf.check_sql_cell("hello") == '"hello"'


def test_check_sql_cell_now_returns_timestamp_string():
    """Test that check_sql_cell converts 'now' keyword to timestamp string.

    The special keyword 'now' should be converted to an actual timestamp
    value wrapped in double quotes, not the literal string 'now'. This
    ensures proper temporal value handling in SQL queries.
    """
    sf = SQLSanitiseFunctions(debug=False)
    res = sf.check_sql_cell("now")
    # Should be a double-quoted string and should not literally be "now"
    assert isinstance(res, str)
    assert res.startswith('"') and res.endswith('"')
    assert res.strip('"') != "now"
