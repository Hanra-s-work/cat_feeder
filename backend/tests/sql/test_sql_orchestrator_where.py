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
# FILE: test_sql_orchestrator_where.py
# CREATION DATE: 15-12-2025
# LAST Modified: 14:55:17 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Test file for orchestrator WHERE clause validation.
# // AR
# +==== END CatFeeder =================+
"""
import pytest
from unittest.mock import Mock, MagicMock

try:
    # Import path when running from project root
    from libs.sql.sql_cache_orchestrator import SQLCacheOrchestrator
    from libs.sql.sql_query_boilerplates import SQLQueryBoilerplates
except ImportError:
    # Import path when running from backend directory
    from src.libs.sql.sql_cache_orchestrator import SQLCacheOrchestrator
    from src.libs.sql.sql_query_boilerplates import SQLQueryBoilerplates


@pytest.fixture
def mock_sql_pool():
    """Create a mock SQL connection pool for testing."""
    pool = Mock()
    pool.is_pool_active.return_value = True
    pool.run_and_fetch_all.return_value = []
    pool.run_editing_command.return_value = 0
    return pool


@pytest.fixture
def mock_boilerplate(mock_sql_pool):
    """Create a mock SQLQueryBoilerplates instance."""
    return SQLQueryBoilerplates(sql_pool=mock_sql_pool, debug=False)


@pytest.fixture
def orchestrator(mock_boilerplate):
    """Create an SQLCacheOrchestrator instance for testing."""
    return SQLCacheOrchestrator(
        sql_query_boilerplates=mock_boilerplate,
        redis_cacher=None,
        debug=False
    )


class TestOrchestratorWhereValidation:
    """Test suite for orchestrator WHERE clause validation."""

    def test_parse_and_validate_where_with_uuid(self, orchestrator):
        """Test that UUIDs in WHERE clauses pass validation."""
        where = "token='742430a7-8222-4509-9dfe-e40c6b3ad3eb'"

        validated_where, params = orchestrator._parse_and_validate_where(where)

        assert validated_where == where
        assert params == []

    def test_parse_and_validate_where_with_email(self, orchestrator):
        """Test that email addresses in WHERE clauses pass validation."""
        where = "email='user@example.com'"

        validated_where, params = orchestrator._parse_and_validate_where(where)

        assert validated_where == where
        assert params == []

    def test_parse_and_validate_where_list(self, orchestrator):
        """Test that WHERE clause lists pass validation."""
        where = ["username='admin'", "role='superuser'"]

        validated_where, params = orchestrator._parse_and_validate_where(where)

        assert validated_where == where
        assert params == []

    def test_parse_and_validate_where_empty_string(self, orchestrator):
        """Test that empty WHERE clause returns empty results."""
        where = ""

        validated_where, params = orchestrator._parse_and_validate_where(where)

        assert validated_where == ""
        assert params == []

    def test_parse_and_validate_where_empty_list(self, orchestrator):
        """Test that empty WHERE clause list returns empty results."""
        where = []

        validated_where, params = orchestrator._parse_and_validate_where(where)

        assert validated_where == []
        assert params == []

    def test_parse_and_validate_where_injection_in_column(self, orchestrator):
        """Test that SQL injection in column names is detected."""
        where = "username'; DROP TABLE users--='test'"

        with pytest.raises(RuntimeError, match="SQL injection detected"):
            orchestrator._parse_and_validate_where(where)

    def test_parse_and_validate_where_multiple_clauses(self, orchestrator):
        """Test validation of multiple WHERE clauses."""
        where = [
            "user_id='123e4567-e89b-12d3-a456-426614174000'",
            "status='active'",
            "created_at='2025-12-15'"
        ]

        validated_where, params = orchestrator._parse_and_validate_where(where)

        assert validated_where == where
        assert params == []

    def test_parse_and_validate_where_special_chars_in_value(self, orchestrator):
        """Test that special characters in values don't trigger false positives."""
        where = "description='Test with @#$% chars'"

        validated_where, params = orchestrator._parse_and_validate_where(where)

        assert validated_where == where
        assert params == []

    def test_get_data_from_table_validates_where(self, orchestrator, mock_boilerplate):
        """Test that get_data_from_table validates WHERE clause before execution."""
        table = "users"
        column = "*"
        where = "token='valid-token-123'"

        # Mock the boilerplate method
        mock_boilerplate.get_data_from_table = Mock(return_value=[])

        result = orchestrator.get_data_from_table(
            table, column, where, beautify=False)

        # Verify the boilerplate method was called with validated WHERE
        assert mock_boilerplate.get_data_from_table.called
        call_args = mock_boilerplate.get_data_from_table.call_args
        assert call_args[0][2] == where  # Third positional arg is WHERE

    def test_get_data_from_table_blocks_injection(self, orchestrator, mock_boilerplate):
        """Test that get_data_from_table blocks injection in WHERE clause."""
        table = "users"
        column = "*"
        where = "id'; DROP TABLE users--='1"

        # Mock the boilerplate method
        mock_boilerplate.get_data_from_table = Mock(return_value=[])

        result = orchestrator.get_data_from_table(
            table, column, where, beautify=False)

        # Should return error without calling boilerplate
        assert result == orchestrator.error
        assert not mock_boilerplate.get_data_from_table.called

    def test_update_data_in_table_validates_where(self, orchestrator, mock_boilerplate):
        """Test that update_data_in_table validates WHERE clause."""
        table = "users"
        data = ["active"]
        column = ["status"]
        where = "id='123'"

        # Mock the boilerplate method
        mock_boilerplate.update_data_in_table = Mock(return_value=0)

        result = orchestrator.update_data_in_table(table, data, column, where)

        # Verify the boilerplate method was called
        assert mock_boilerplate.update_data_in_table.called
        call_args = mock_boilerplate.update_data_in_table.call_args
        assert call_args[0][3] == where  # Fourth positional arg is WHERE

    def test_update_data_in_table_blocks_injection(self, orchestrator, mock_boilerplate):
        """Test that update_data_in_table blocks injection in WHERE clause."""
        table = "users"
        data = ["active"]
        column = ["status"]
        where = "id'; DELETE FROM users--='1"

        # Mock the boilerplate method
        mock_boilerplate.update_data_in_table = Mock(return_value=0)

        result = orchestrator.update_data_in_table(table, data, column, where)

        # Should return error without calling boilerplate
        assert result == orchestrator.error
        assert not mock_boilerplate.update_data_in_table.called

    def test_remove_data_from_table_validates_where(self, orchestrator, mock_boilerplate):
        """Test that remove_data_from_table validates WHERE clause."""
        table = "sessions"
        where = "expired='true'"

        # Mock the boilerplate method
        mock_boilerplate.remove_data_from_table = Mock(return_value=0)

        result = orchestrator.remove_data_from_table(table, where)

        # Verify the boilerplate method was called
        assert mock_boilerplate.remove_data_from_table.called
        call_args = mock_boilerplate.remove_data_from_table.call_args
        assert call_args[0][1] == where  # Second positional arg is WHERE

    def test_remove_data_from_table_blocks_injection(self, orchestrator, mock_boilerplate):
        """Test that remove_data_from_table blocks injection in WHERE clause."""
        table = "sessions"
        where = "id'; DROP DATABASE test--='1"

        # Mock the boilerplate method
        mock_boilerplate.remove_data_from_table = Mock(return_value=0)

        result = orchestrator.remove_data_from_table(table, where)

        # Should return error without calling boilerplate
        assert result == orchestrator.error
        assert not mock_boilerplate.remove_data_from_table.called

    def test_get_table_size_validates_where(self, orchestrator, mock_boilerplate):
        """Test that get_table_size validates WHERE clause."""
        table = "users"
        column = "*"
        where = "status='active'"

        # Mock the boilerplate method
        mock_boilerplate.get_table_size = Mock(return_value=10)

        result = orchestrator.get_table_size(table, column, where)

        # Verify the boilerplate method was called
        assert mock_boilerplate.get_table_size.called
        call_args = mock_boilerplate.get_table_size.call_args
        assert call_args[0][2] == where  # Third positional arg is WHERE

    def test_get_table_size_blocks_injection(self, orchestrator, mock_boilerplate):
        """Test that get_table_size blocks injection in WHERE clause."""
        table = "users"
        column = "*"
        where = "status'; TRUNCATE TABLE users--='active"

        # Mock the boilerplate method
        mock_boilerplate.get_table_size = Mock(return_value=10)

        result = orchestrator.get_table_size(table, column, where)

        # Should return error code without calling boilerplate
        try:
            from libs.sql.sql_constants import GET_TABLE_SIZE_ERROR
        except ImportError:
            from src.libs.sql.sql_constants import GET_TABLE_SIZE_ERROR
        assert result == GET_TABLE_SIZE_ERROR
        assert not mock_boilerplate.get_table_size.called
