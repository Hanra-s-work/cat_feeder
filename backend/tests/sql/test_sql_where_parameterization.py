from unittest.mock import Mock, MagicMock
import pytest
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
# FILE: test_sql_where_parameterization.py
# CREATION DATE: 15-12-2025
# LAST Modified: 14:55:29 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Test file for WHERE clause parameterization to prevent SQL injection false positives.
# // AR
# +==== END CatFeeder =================+
"""

try:
    # Import path when running from project root
    from libs.sql.sql_query_boilerplates import SQLQueryBoilerplates
    from libs.sql.sql_injection import SQLInjection
    from libs.sql.sql_sanitisation_functions import SQLSanitiseFunctions
except ImportError:
    # Import path when running from backend directory
    from src.libs.sql.sql_query_boilerplates import SQLQueryBoilerplates
    from src.libs.sql.sql_injection import SQLInjection
    from src.libs.sql.sql_sanitisation_functions import SQLSanitiseFunctions


@pytest.fixture
def mock_sql_pool():
    """Create a mock SQL connection pool for testing."""
    pool = Mock()
    pool.is_pool_active.return_value = True
    pool.run_and_fetch_all.return_value = []
    pool.run_editing_command.return_value = 0
    return pool


@pytest.fixture
def boilerplate(mock_sql_pool):
    """Create an SQLQueryBoilerplates instance for testing."""
    return SQLQueryBoilerplates(sql_pool=mock_sql_pool, debug=False)


class TestWhereClauseParameterization:
    """Test suite for WHERE clause parameterization functionality."""

    def test_parse_where_clause_with_uuid(self, boilerplate):
        """Test that UUIDs in WHERE clauses don't trigger false positives."""
        where = "token='742430a7-8222-4509-9dfe-e40c6b3ad3eb'"

        where_string, params = boilerplate._parse_where_clause(where)

        assert where_string == "token=%s"
        assert params == ['742430a7-8222-4509-9dfe-e40c6b3ad3eb']

    def test_parse_where_clause_with_email(self, boilerplate):
        """Test that email addresses in WHERE clauses are handled correctly."""
        where = "email='user@example.com'"

        where_string, params = boilerplate._parse_where_clause(where)

        assert where_string == "email=%s"
        assert params == ['user@example.com']

    def test_parse_where_clause_with_single_quotes(self, boilerplate):
        """Test that values with single quotes are properly extracted."""
        where = "username='john_doe'"

        where_string, params = boilerplate._parse_where_clause(where)

        assert where_string == "username=%s"
        assert params == ['john_doe']

    def test_parse_where_clause_with_double_quotes(self, boilerplate):
        """Test that values with double quotes are properly extracted."""
        where = 'status="active"'

        where_string, params = boilerplate._parse_where_clause(where)

        assert where_string == "status=%s"
        assert params == ['active']

    def test_parse_where_clause_list(self, boilerplate):
        """Test that WHERE clause lists are properly parsed."""
        where = ["username='admin'", "role='superuser'"]

        where_string, params = boilerplate._parse_where_clause(where)

        assert where_string == "username=%s AND role=%s"
        assert params == ['admin', 'superuser']

    def test_parse_where_clause_empty_string(self, boilerplate):
        """Test that empty WHERE clause returns empty results."""
        where = ""

        where_string, params = boilerplate._parse_where_clause(where)

        assert where_string == ""
        assert params == []

    def test_parse_where_clause_empty_list(self, boilerplate):
        """Test that empty WHERE clause list returns empty results."""
        where = []

        where_string, params = boilerplate._parse_where_clause(where)

        assert where_string == ""
        assert params == []

    def test_parse_where_clause_risky_column_name(self, boilerplate):
        """Test that risky column names are escaped with backticks."""
        where = "order='pending'"

        where_string, params = boilerplate._parse_where_clause(where)

        assert where_string == "`order`=%s"
        assert params == ['pending']

    def test_parse_where_clause_numeric_value(self, boilerplate):
        """Test that numeric values are handled correctly."""
        where = "age=25"

        where_string, params = boilerplate._parse_where_clause(where)

        assert where_string == "age=%s"
        assert params == ['25']

    def test_parse_where_clause_injection_in_column_name(self, boilerplate):
        """Test that SQL injection in column names is detected."""
        where = "username'; DROP TABLE users--='test'"

        with pytest.raises(RuntimeError, match="SQL injection detected"):
            boilerplate._parse_where_clause(where)

    def test_parse_where_clause_multiple_clauses(self, boilerplate):
        """Test parsing multiple WHERE clauses."""
        where = [
            "user_id='123e4567-e89b-12d3-a456-426614174000'",
            "status='active'",
            "created_at='2025-12-15'"
        ]

        where_string, params = boilerplate._parse_where_clause(where)

        assert where_string == "user_id=%s AND status=%s AND created_at=%s"
        assert len(params) == 3
        assert params[0] == '123e4567-e89b-12d3-a456-426614174000'
        assert params[1] == 'active'
        assert params[2] == '2025-12-15'

    def test_parse_where_clause_special_characters_in_value(self, boilerplate):
        """Test that special characters in values don't cause false positives."""
        where = "description='This is a test with special chars: @#$%'"

        where_string, params = boilerplate._parse_where_clause(where)

        assert where_string == "description=%s"
        assert params == ['This is a test with special chars: @#$%']

    def test_normalize_cell_now_function(self, boilerplate):
        """Test that 'now' values are normalized to proper SQL function."""
        result = boilerplate._normalize_cell('now')
        assert result is not None
        # Result should be a timestamp string from the time manipulation utility

    def test_normalize_cell_current_date_function(self, boilerplate):
        """Test that 'current_date' values are normalized to proper SQL function."""
        result = boilerplate._normalize_cell('current_date')
        assert result is not None
        # Result should be a date string from the time manipulation utility

    def test_normalize_cell_none_value(self, boilerplate):
        """Test that None values are handled correctly."""
        result = boilerplate._normalize_cell(None)
        assert result is None

    def test_normalize_cell_integer_value(self, boilerplate):
        """Test that integer values are preserved."""
        result = boilerplate._normalize_cell(42)
        assert result == 42
        assert isinstance(result, int)

    def test_normalize_cell_float_value(self, boilerplate):
        """Test that float values are preserved."""
        result = boilerplate._normalize_cell(3.14)
        assert result == 3.14
        assert isinstance(result, float)

    def test_normalize_cell_string_value(self, boilerplate):
        """Test that regular string values are preserved."""
        result = boilerplate._normalize_cell('test_value')
        assert result == 'test_value'


class TestWhereClauseIntegration:
    """Integration tests for WHERE clause functionality across SQL components."""

    def test_update_data_with_where_clause(self, boilerplate, mock_sql_pool):
        """Test that update operations use parameterized WHERE clauses."""
        table = "users"
        data = ["active"]
        column = ["status"]
        where = "token='742430a7-8222-4509-9dfe-e40c6b3ad3eb'"

        # Mock the run_editing_command to capture the call
        mock_sql_pool.run_editing_command.return_value = 0

        result = boilerplate.update_data_in_table(table, data, column, where)

        # Verify the function was called
        assert mock_sql_pool.run_editing_command.called

        # Get the call arguments
        call_args = mock_sql_pool.run_editing_command.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        # Verify parameterization
        assert "%s" in query
        assert "token=%s" in query
        assert len(params) == 2  # One for status, one for token
        assert params[0] == "active"
        assert params[1] == '742430a7-8222-4509-9dfe-e40c6b3ad3eb'
        assert result == 0

    def test_get_data_with_where_clause(self, boilerplate, mock_sql_pool):
        """Test that SELECT operations use parameterized WHERE clauses."""
        table = "sessions"
        column = "*"
        where = "token='test-token-123'"

        # Mock the return value
        mock_sql_pool.run_and_fetch_all.return_value = []

        result = boilerplate.get_data_from_table(
            table, column, where, beautify=False)

        # Verify the function was called
        assert mock_sql_pool.run_and_fetch_all.called

        # Get the call arguments
        call_args = mock_sql_pool.run_and_fetch_all.call_args
        query = call_args[1]['query']
        params = call_args[1]['values']

        # Verify parameterization
        assert "token=%s" in query
        assert len(params) == 1
        assert params[0] == 'test-token-123'

    def test_remove_data_with_where_clause(self, boilerplate, mock_sql_pool):
        """Test that DELETE operations use parameterized WHERE clauses."""
        table = "sessions"
        where = "expired='true'"

        # Mock the return value
        mock_sql_pool.run_editing_command.return_value = 0

        result = boilerplate.remove_data_from_table(table, where)

        # Verify the function was called
        assert mock_sql_pool.run_editing_command.called

        # Get the call arguments
        call_args = mock_sql_pool.run_editing_command.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        # Verify parameterization
        assert "expired=%s" in query
        assert len(params) == 1
        assert params[0] == 'true'
        assert result == 0
