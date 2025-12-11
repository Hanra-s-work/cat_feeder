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
# LAST Modified: 2:0:5 11-12-2025
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
    s = "a'b\\c"
    sf = SQLSanitiseFunctions(debug=False)
    out = sf.protect_sql_cell(s)
    # expected: a\'b\\c  (single quote becomes \' and backslash becomes \\)
    assert out == "a\\'b\\\\c"


def test__protect_value_quotes_and_escaping():
    sf = SQLSanitiseFunctions(debug=False)
    v = sf._protect_value("O'Reilly")
    assert v == "'O''Reilly'"


def test_check_sql_cell_none_and_basic():
    sf = SQLSanitiseFunctions(debug=False)
    # raw=True and cell is None should return None
    assert sf.check_sql_cell(None, raw=True) is None
    # basic string should be wrapped in double quotes
    assert sf.check_sql_cell("hello") == '"hello"'


def test_check_sql_cell_now_returns_timestamp_string():
    sf = SQLSanitiseFunctions(debug=False)
    res = sf.check_sql_cell("now")
    # Should be a double-quoted string and should not literally be "now"
    assert isinstance(res, str)
    assert res.startswith('"') and res.endswith('"')
    assert res.strip('"') != "now"
