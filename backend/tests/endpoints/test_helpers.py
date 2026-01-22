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
# FILE: test_helpers.py
# CREATION DATE: 11-01-2026
# LAST Modified: 22:46:55 11-01-2026
# DESCRIPTION:
# Unit tests for endpoint helper functions for data processing.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Testing conversion functions for datetimes, bytes, and strings in endpoints.
# // AR
# +==== END CatFeeder =================+
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import pytest

try:
    from libs.endpoint_manager.endpoint_helpers import (
        datetime_to_string,
        string_to_datetime,
        convert_datetime_instances_to_strings,
        convert_bytes_to_str,
        convert_str_to_bytes
    )
    from libs.utils import constants as CONST
except Exception:
    from src.libs.endpoint_manager.endpoint_helpers import (
        datetime_to_string,
        string_to_datetime,
        convert_datetime_instances_to_strings,
        convert_bytes_to_str,
        convert_str_to_bytes
    )
    from src.libs.utils import constants as CONST


class TestDatetimeToString:
    """Test datetime to ISO string conversion."""

    def test_datetime_to_string_conversion(self):
        """Verify datetime is converted to ISO format string."""
        dt = datetime(2026, 1, 11, 15, 30, 45)
        result = datetime_to_string(dt, "fallback")

        assert isinstance(result, str)
        assert "2026-01-11" in result
        assert "15:30:45" in result

    def test_datetime_to_string_with_microseconds(self):
        """Verify datetime with microseconds is converted correctly."""
        dt = datetime(2026, 1, 11, 15, 30, 45, 123456)
        result = datetime_to_string(dt)

        assert isinstance(result, str)
        assert "2026-01-11" in result
        assert "123456" in result

    def test_datetime_to_string_with_string_input(self):
        """Verify string input is returned as-is."""
        input_str = "2026-01-11T15:30:45"
        result = datetime_to_string(input_str, "fallback")

        assert result == input_str
        assert isinstance(result, str)

    def test_datetime_to_string_with_none_input(self):
        """Verify fallback is returned for None input."""
        result = datetime_to_string(None, "<unknown>")
        assert result == "<unknown>"

    def test_datetime_to_string_with_custom_default(self):
        """Verify custom default message is used."""
        result = datetime_to_string(None, "CUSTOM_DEFAULT")
        assert result == "CUSTOM_DEFAULT"

    def test_datetime_to_string_with_invalid_type(self):
        """Verify fallback is returned for invalid type."""
        result = datetime_to_string(12345, "fallback_msg")
        assert result == "fallback_msg"

    def test_datetime_to_string_iso_format(self):
        """Verify output is valid ISO 8601 format."""
        dt = datetime(2026, 1, 11, 15, 30, 45)
        result = datetime_to_string(dt)

        # Should be parseable back to datetime
        parsed = datetime.fromisoformat(result)
        assert parsed.year == 2026
        assert parsed.month == 1
        assert parsed.day == 11


class TestStringToDatetime:
    """Test ISO 8601 string to datetime conversion."""

    def test_string_to_datetime_conversion(self):
        """Verify ISO string is converted to datetime."""
        date_str = "2026-01-11T15:30:45"
        result = string_to_datetime(date_str)

        assert isinstance(result, datetime)
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 11
        assert result.hour == 15
        assert result.minute == 30
        assert result.second == 45

    def test_string_to_datetime_with_microseconds(self):
        """Verify ISO string with microseconds converts correctly."""
        date_str = "2026-01-11T15:30:45.123456"
        result = string_to_datetime(date_str)

        assert isinstance(result, datetime)
        assert result.microsecond == 123456

    def test_string_to_datetime_invalid_format(self):
        """Verify default is returned for invalid format."""
        result = string_to_datetime("invalid_date_string")
        assert result == datetime.min

    def test_string_to_datetime_with_custom_default(self):
        """Verify custom default datetime is used."""
        custom_default = datetime(2020, 1, 1)
        result = string_to_datetime("invalid", custom_default)
        assert result == custom_default

    def test_string_to_datetime_with_none_input(self):
        """Verify default is returned for None input."""
        result = string_to_datetime(None)
        assert result == datetime.min

    def test_string_to_datetime_empty_string(self):
        """Verify default is returned for empty string."""
        result = string_to_datetime("", datetime(2025, 12, 31))
        assert result == datetime(2025, 12, 31)

    def test_string_to_datetime_roundtrip(self):
        """Verify datetime -> string -> datetime roundtrip works."""
        original = datetime(2026, 1, 11, 15, 30, 45, 123456)
        iso_string = datetime_to_string(original)
        recovered = string_to_datetime(iso_string)

        assert recovered.year == original.year
        assert recovered.month == original.month
        assert recovered.day == original.day
        assert recovered.hour == original.hour
        assert recovered.minute == original.minute
        assert recovered.second == original.second


class TestConvertDatetimeInstancesToStrings:
    """Test batch datetime conversion in dictionaries."""

    def test_convert_single_datetime_in_dict(self):
        """Verify single datetime in dict is converted."""
        dt = datetime(2026, 1, 11, 15, 30, 45)
        data = {"created": dt, "name": "test"}
        result = convert_datetime_instances_to_strings(data)

        assert isinstance(result["created"], str)
        assert "2026-01-11" in result["created"]
        assert result["name"] == "test"

    def test_convert_multiple_datetimes_in_dict(self):
        """Verify multiple datetimes in dict are all converted."""
        dt1 = datetime(2026, 1, 11, 15, 30, 45)
        dt2 = datetime(2025, 12, 25, 10, 0, 0)
        data = {
            "creation_date": dt1,
            "last_modified": dt2,
            "user_name": "john"
        }
        result = convert_datetime_instances_to_strings(data)

        assert isinstance(result["creation_date"], str)
        assert isinstance(result["last_modified"], str)
        assert result["user_name"] == "john"
        assert "2026-01-11" in result["creation_date"]
        assert "2025-12-25" in result["last_modified"]

    def test_convert_skips_non_datetime_values(self):
        """Verify non-datetime values are left unchanged."""
        data = {
            "created": datetime(2026, 1, 11),
            "count": 42,
            "name": "test",
            "enabled": True
        }
        result = convert_datetime_instances_to_strings(data)

        assert isinstance(result["created"], str)
        assert result["count"] == 42
        assert result["name"] == "test"
        assert result["enabled"] is True

    def test_convert_with_custom_default_message(self):
        """Verify custom default message is used for invalid conversions."""
        data = {"created": datetime(2026, 1, 11), "name": "test"}
        result = convert_datetime_instances_to_strings(data, "<no_date>")

        assert isinstance(result["created"], str)
        assert result["name"] == "test"

    def test_convert_empty_dict(self):
        """Verify empty dict is handled correctly."""
        result = convert_datetime_instances_to_strings({})
        assert result == {}

    def test_convert_preserves_dict_structure(self):
        """Verify dict structure is preserved after conversion."""
        dt = datetime(2026, 1, 11, 15, 30, 45)
        data = {"created": dt, "modified": dt, "name": "test"}
        result = convert_datetime_instances_to_strings(data)

        assert len(result) == 3
        assert set(result.keys()) == {"created", "modified", "name"}

    def test_convert_modifies_original_dict(self):
        """Verify conversion modifies the original dict in-place."""
        dt = datetime(2026, 1, 11)
        data = {"created": dt}
        result = convert_datetime_instances_to_strings(data)

        assert result is data
        assert isinstance(data["created"], str)


class TestConvertBytesToStr:
    """Test bytes to string conversion."""

    def test_convert_bytes_to_str_utf8(self):
        """Verify bytes are converted to UTF-8 string."""
        data = b"Hello, World!"
        result = convert_bytes_to_str(data)

        assert isinstance(result, str)
        assert result == "Hello, World!"

    def test_convert_bytes_to_str_custom_encoding(self):
        """Verify custom encoding is respected."""
        data = "café".encode('latin-1')
        result = convert_bytes_to_str(data, encoding='latin-1')

        assert isinstance(result, str)
        assert result == "café"

    def test_convert_string_returns_as_is(self):
        """Verify string input is returned unchanged."""
        data = "Already a string"
        result = convert_bytes_to_str(data)

        assert result == "Already a string"
        assert isinstance(result, str)

    def test_convert_empty_bytes(self):
        """Verify empty bytes are converted to empty string."""
        result = convert_bytes_to_str(b"")
        assert result == ""

    def test_convert_bytes_with_unicode(self):
        """Verify bytes with unicode characters are decoded correctly."""
        data = "こんにちは".encode('utf-8')
        result = convert_bytes_to_str(data, encoding='utf-8')

        assert isinstance(result, str)
        assert result == "こんにちは"

    def test_convert_bytes_with_special_characters(self):
        """Verify special characters are preserved."""
        special = "!@#$%^&*()\n\t"
        data = special.encode('utf-8')
        result = convert_bytes_to_str(data)

        assert result == special

    def test_convert_bytes_invalid_encoding_raises(self):
        """Verify invalid encoding handling."""
        data = b"test"
        # Using invalid encoding that would fail
        with pytest.raises(LookupError):
            convert_bytes_to_str(data, encoding='invalid_codec')

    def test_convert_bytes_mixed_content(self):
        """Verify bytes with mixed ascii and extended characters."""
        content = "Test 123 café ñ"
        data = content.encode('utf-8')
        result = convert_bytes_to_str(data)

        assert result == content


class TestConvertStrToBytes:
    """Test string to bytes conversion."""

    def test_convert_str_to_bytes_utf8(self):
        """Verify string is converted to UTF-8 bytes."""
        data = "Hello, World!"
        result = convert_str_to_bytes(data)

        assert isinstance(result, bytes)
        assert result == b"Hello, World!"

    def test_convert_str_to_bytes_custom_encoding(self):
        """Verify custom encoding is respected."""
        data = "café"
        result = convert_str_to_bytes(data, encoding='latin-1')

        assert isinstance(result, bytes)
        assert result == "café".encode('latin-1')

    def test_convert_bytes_returns_as_is(self):
        """Verify bytes input is returned unchanged."""
        data = b"Already bytes"
        result = convert_str_to_bytes(data)

        assert result == b"Already bytes"
        assert isinstance(result, bytes)

    def test_convert_empty_string(self):
        """Verify empty string is converted to empty bytes."""
        result = convert_str_to_bytes("")
        assert result == b""

    def test_convert_string_with_unicode(self):
        """Verify string with unicode characters converts correctly."""
        data = "こんにちは"
        result = convert_str_to_bytes(data, encoding='utf-8')

        assert isinstance(result, bytes)
        assert result == "こんにちは".encode('utf-8')

    def test_convert_string_with_special_characters(self):
        """Verify special characters are encoded correctly."""
        special = "!@#$%^&*()\n\t"
        result = convert_str_to_bytes(special)

        assert result == special.encode('utf-8')

    def test_convert_string_invalid_encoding_raises(self):
        """Verify invalid encoding handling."""
        data = "test"
        with pytest.raises(LookupError):
            convert_str_to_bytes(data, encoding='invalid_codec')

    def test_convert_string_mixed_content(self):
        """Verify string with mixed ascii and extended characters."""
        content = "Test 123 café ñ"
        result = convert_str_to_bytes(content)

        assert result == content.encode('utf-8')

    def test_convert_str_to_bytes_roundtrip(self):
        """Verify string -> bytes -> string roundtrip works."""
        original = "Test content: café ñ"
        as_bytes = convert_str_to_bytes(original)
        recovered = convert_bytes_to_str(as_bytes)

        assert recovered == original

    def test_convert_large_string(self):
        """Verify large strings are handled correctly."""
        large_data = "x" * 10000
        result = convert_str_to_bytes(large_data)

        assert len(result) == 10000
        assert convert_bytes_to_str(result) == large_data
