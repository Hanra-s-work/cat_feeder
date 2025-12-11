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
# FILE: test_sql_injection.py
# CREATION DATE: 11-12-2025
# LAST Modified: 1:59:12 11-12-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file in charge of checking the injection prevention measures for sql that are implemented in the sql library binder.
# // AR
# +==== END CatFeeder =================+
"""
import pytest

from src.libs.sql.sql_injection import SQLInjection


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
    # valid base64 with marker should be accepted as base64
    s = "YWJjZA==;base64"
    assert injector.check_if_symbol_sql_injection(s) is False
