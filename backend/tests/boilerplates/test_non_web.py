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
# FILE: test_non_web.py
# CREATION DATE: 19-12-2025
# LAST Modified: 0:10:43 28-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The code in charge of testing the non web boilerplate code to make sure it works properly.
# // AR
# +==== END CatFeeder =================+
"""
import os
import re
import sys
from types import SimpleNamespace
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

# Flexible import pattern similar to http_codes tests: try libs package first,
# then fall back to src.libs when executed from repository root.
try:
    from libs.boilerplates.non_web import BoilerplateNonHTTP
    from libs.utils import constants as CONST
except Exception:
    from src.libs.boilerplates.non_web import BoilerplateNonHTTP
    from src.libs.utils import constants as CONST


@pytest.fixture()
def inst():
    """Create a lightweight BoilerplateNonHTTP instance without running __init__.

    Tests mock `database_link` and other attributes directly to avoid touching
    RuntimeManager/SQL initialization.
    """
    obj = object.__new__(BoilerplateNonHTTP)
    obj.debug = False
    obj.success = 0
    obj.error = 84
    obj.runtime_manager = None
    obj.database_link = SimpleNamespace()
    # Provide a minimal boilerplate_responses object so methods that call
    # `RI.get_if_exists` behave consistently and don't return early.
    obj.boilerplate_responses = SimpleNamespace(
        user_not_found=lambda *a, **k: None,
        internal_server_error=lambda *a, **k: None,
    )
    return obj


def test_set_lifespan(inst):
    """Verify that `set_lifespan` returns a datetime in the future."""
    now = datetime.now()
    future = inst.set_lifespan(5)
    assert isinstance(future, datetime)
    assert future > now


def test_check_date_valid_and_invalid(inst):
    """Check date validation for valid, invalid and malformed inputs."""
    assert inst.check_date("01/01/2020") is True
    assert inst.check_date("31/02/2020") is False
    assert inst.check_date("not-a-date") is False


def test_generate_check_token_default_size(inst):
    """Ensure `generate_check_token` returns a string token containing a dash."""
    token = inst.generate_check_token(2)
    assert isinstance(token, str)
    assert "-" in token


def test_hide_api_key(inst):
    """Validate `hide_api_key` returns human-readable placeholders."""
    assert inst.hide_api_key(None) == "No api key"
    assert inst.hide_api_key("abcd") == "Some api key"


def test_update_single_data_calls_db_and_returns_success(inst):
    """Confirm `update_single_data` forwards parameters to DB layer and returns success."""
    called = {}

    def fake_update(table, data, column, where):
        called['args'] = (table, data, column, where)
        return inst.success

    inst.database_link.update_data_in_table = fake_update
    res = inst.update_single_data("t", "finder", "col", "val", {"col": "v"})
    assert res == inst.success
    assert called['args'][0] == "t"


def test_remove_user_from_tables_with_list_and_str(inst):
    """Test removal helper handles both list and single-table inputs."""
    inst.database_link.remove_data_from_table = Mock(return_value=inst.success)
    res = inst.remove_user_from_tables("id='1'", ["A", "B"])
    assert res == {"A": inst.success, "B": inst.success}

    res2 = inst.remove_user_from_tables("id='1'", "C")
    assert res2 == {"C": inst.success}


def test_generate_token_returns_new_uuid_when_db_empty(inst):
    """When the DB contains no tokens, `generate_token` should return a non-empty string."""
    def fake_get(table, column, where, beautify=False):
        return []

    inst.database_link.get_data_from_table = fake_get
    token = inst.generate_token()
    assert isinstance(token, str)
    assert len(token) > 0


def test_is_token_correct_updates_expiration(inst):
    """Verify `is_token_correct` returns True and triggers a DB update for expiration."""
    future = datetime.now() + timedelta(minutes=10)
    inst.database_link.get_data_from_table = Mock(return_value=[(future,)])

    def fake_datetime_to_string(datetime_instance, date_only=False, sql_mode=False):
        return "2025-01-01 00:00:00"

    inst.database_link.datetime_to_string = fake_datetime_to_string
    inst.database_link.update_data_in_table = Mock(return_value=inst.success)

    assert inst.is_token_correct("sometoken") is True
    inst.database_link.update_data_in_table.assert_called()


def test_is_token_admin_checks_admin_flag(inst):
    """Check that `is_token_admin` correctly interprets the admin flag from DB records."""
    inst.get_user_id_from_token = Mock(return_value="42")
    inst.database_link.get_data_from_table = Mock(
        return_value=[{"admin": "1", "username": "bob"}])
    assert inst.is_token_admin("tok") is True

    inst.database_link.get_data_from_table = Mock(
        return_value=[{"username": "bob"}])
    assert inst.is_token_admin("tok") is False


def test_get_user_id_from_token_returns_user_not_found_on_error_and_list_behavior(inst):
    """Ensure `get_user_id_from_token` handles DB errors and successful lookups appropriately."""
    inst.boilerplate_responses = SimpleNamespace(
        user_not_found=lambda title, token: "notfound")
    inst.database_link.get_data_from_table = Mock(return_value=inst.error)
    assert inst.get_user_id_from_token("t", "tok") == "notfound"

    inst.database_link.get_data_from_table = Mock(
        return_value=[{"user_id": "7"}])
    assert inst.get_user_id_from_token("t", "tok") == "7"


def test_update_user_data_calls_update_and_returns_success(inst):
    """Validate `update_user_data` uses column names and calls the DB update endpoint."""
    inst.database_link.get_table_column_names = Mock(
        return_value=["id", "a", "b"])
    inst.database_link.update_data_in_table = Mock(return_value=inst.success)
    res = inst.update_user_data("t", "uid", [1, 2])
    assert res == inst.success
    inst.database_link.update_data_in_table.assert_called()
