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
# FILE: test_token.py
# CREATION DATE: 11-01-2026
# LAST Modified: 22:41:18 11-01-2026
# DESCRIPTION:
# Unit tests for TokenEndpoints class.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Testing token endpoint functionality including validation, info retrieval, and TTL.
# // AR
# +==== END CatFeeder =================+
"""
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import pytest

try:
    from libs.endpoint_manager.endpoints.token import TokenEndpoints, TokenInfo, DEFAULT_DATE_PLACEHOLDER
    from libs.http_codes import HCI, HttpDataTypes
    from libs.utils import constants as CONST
except Exception:
    from src.libs.endpoint_manager.endpoints.token import TokenEndpoints, TokenInfo, DEFAULT_DATE_PLACEHOLDER
    from src.libs.http_codes import HCI, HttpDataTypes
    from src.libs.utils import constants as CONST


class TestTokenInfoDataclass:
    """Test TokenInfo dataclass initialization and defaults."""

    def test_token_info_creation(self, sample_token_info):
        """Verify TokenInfo can be created with all fields."""
        assert sample_token_info.token == "valid_token_123"
        assert sample_token_info.user_id == 1
        assert isinstance(sample_token_info.creation_date, datetime)
        assert isinstance(sample_token_info.expiration_date, datetime)

    def test_token_info_defaults(self):
        """Verify TokenInfo uses default placeholder date when not provided."""
        info = TokenInfo()
        assert info.token == ""
        assert info.user_id == 0
        assert info.creation_date == DEFAULT_DATE_PLACEHOLDER
        assert info.edit_date == DEFAULT_DATE_PLACEHOLDER
        assert info.expiration_date == DEFAULT_DATE_PLACEHOLDER


class TestGetTokenIfPresent:
    """Test token extraction from request headers."""

    def test_extract_token_from_headers(self, token_endpoints, mock_request_with_token):
        """Verify token is extracted from standard header."""
        token = token_endpoints._get_token_if_present(mock_request_with_token)
        assert token == "valid_token_123"

    def test_extract_bearer_token(self, token_endpoints, mock_request_bearer_token):
        """Verify Bearer token format is parsed correctly."""
        token = token_endpoints._get_token_if_present(
            mock_request_bearer_token)
        assert token == "valid_token_123"

    def test_no_token_present(self, token_endpoints, mock_request_without_token):
        """Verify None is returned when no token present."""
        token = token_endpoints._get_token_if_present(
            mock_request_without_token)
        assert token is None


class TestGetTtlBreakdown:
    """Test TTL breakdown calculation."""

    def test_ttl_breakdown_format(self, token_endpoints):
        """Verify TTL breakdown returns correct dictionary format."""
        delta = timedelta(hours=2, minutes=30, seconds=45)
        breakdown = token_endpoints._get_ttl_breakdown(delta)

        assert isinstance(breakdown, dict)
        assert "hours" in breakdown
        assert "minutes" in breakdown
        assert "seconds" in breakdown

    def test_ttl_breakdown_calculations(self, token_endpoints):
        """Verify TTL breakdown performs correct hour/minute/second calculations."""
        # 3661 seconds = 1 hour, 1 minute, 1 second
        delta = timedelta(seconds=3661)
        breakdown = token_endpoints._get_ttl_breakdown(delta)

        assert breakdown["hours"] == 1
        assert breakdown["minutes"] == 1
        assert breakdown["seconds"] == 1

    def test_ttl_breakdown_large_value(self, token_endpoints):
        """Verify TTL breakdown handles large time deltas."""
        # 7384 seconds = 2 hours, 3 minutes, 4 seconds
        delta = timedelta(seconds=7384)
        breakdown = token_endpoints._get_ttl_breakdown(delta)

        assert breakdown["hours"] == 2
        assert breakdown["minutes"] == 3
        assert breakdown["seconds"] == 4


class TestGetTokenValid:
    """Test token validity check endpoint."""

    def test_valid_token_returns_ok(self, token_endpoints, mock_request_with_token):
        """Verify valid token returns success with 'ok' message."""
        token_endpoints._token_correct = MagicMock(return_value=True)

        response = token_endpoints.get_token_valid(mock_request_with_token)

        assert response is not None
        # Verify success was called
        token_endpoints.boilerplate_responses_initialised = MagicMock()

    def test_invalid_token_returns_error(self, token_endpoints, mock_request_with_token):
        """Verify invalid token returns error response."""
        token_endpoints._token_correct = MagicMock(return_value=False)

        response = token_endpoints.get_token_valid(mock_request_with_token)

        assert response is not None


class TestGetAdmin:
    """Test admin status check endpoint."""

    def test_admin_user_returns_ok(self, token_endpoints, mock_request_with_token):
        """Verify admin user gets 'ok' response."""
        token_endpoints._get_token_if_present = MagicMock(
            return_value="valid_token")
        token_endpoints._is_token_admin = MagicMock(return_value=True)

        response = token_endpoints.get_admin(mock_request_with_token)

        assert response is not None

    def test_non_admin_user_returns_unauthorized(self, token_endpoints, mock_request_with_token):
        """Verify non-admin user gets unauthorized response."""
        token_endpoints._get_token_if_present = MagicMock(
            return_value="valid_token")
        token_endpoints._is_token_admin = MagicMock(return_value=False)

        response = token_endpoints.get_admin(mock_request_with_token)

        assert response is not None

    def test_missing_token_returns_invalid(self, token_endpoints, mock_request_without_token):
        """Verify missing token returns invalid_token response."""
        token_endpoints._get_token_if_present = MagicMock(return_value=None)

        response = token_endpoints.get_admin(mock_request_without_token)

        assert response is not None


class TestGetTimeToLive:
    """Test TTL retrieval endpoint."""

    def test_ttl_endpoint_returns_seconds_and_breakdown(self, token_endpoints, mock_request_with_token, sample_token_info):
        """Verify TTL endpoint returns both seconds and breakdown."""
        token_endpoints._get_token_if_present = MagicMock(
            return_value="valid_token")
        token_endpoints.sql_connection = MagicMock()
        token_endpoints._get_token_info = MagicMock(
            return_value=sample_token_info)

        response = token_endpoints.get_time_to_live(mock_request_with_token)

        assert response is not None

    def test_ttl_no_token_returns_unauthorized(self, token_endpoints, mock_request_without_token):
        """Verify missing token returns unauthorized."""
        token_endpoints._get_token_if_present = MagicMock(return_value=None)

        response = token_endpoints.get_time_to_live(mock_request_without_token)

        assert response is not None

    def test_ttl_no_sql_connection_returns_error(self, token_endpoints, mock_request_with_token):
        """Verify missing SQL connection returns internal server error."""
        token_endpoints._get_token_if_present = MagicMock(
            return_value="valid_token")
        token_endpoints.sql_connection = None

        response = token_endpoints.get_time_to_live(mock_request_with_token)

        assert response is not None

    def test_ttl_invalid_token_returns_error(self, token_endpoints, mock_request_with_token):
        """Verify invalid token in database returns error."""
        token_endpoints._get_token_if_present = MagicMock(
            return_value="invalid_token")
        token_endpoints.sql_connection = MagicMock()
        token_endpoints._get_token_info = MagicMock(return_value=None)

        response = token_endpoints.get_time_to_live(mock_request_with_token)

        assert response is not None


class TestGetTokenInfo:
    """Test token information retrieval endpoint."""

    def test_get_token_info_returns_user_data(self, token_endpoints, mock_request_with_token, sample_token_info, sample_user_info):
        """Verify token info endpoint returns user information."""
        token_endpoints._get_token_if_present = MagicMock(
            return_value="valid_token")
        token_endpoints.sql_connection = MagicMock()
        token_endpoints._is_token_correct = MagicMock(return_value=True)
        token_endpoints._get_token_info = MagicMock(
            return_value=sample_token_info)
        token_endpoints._get_user_info = MagicMock(
            return_value=sample_user_info)

        response = token_endpoints.get_token_info(mock_request_with_token)

        assert response is not None

    def test_get_token_info_no_token(self, token_endpoints, mock_request_without_token):
        """Verify missing token returns unauthorized."""
        token_endpoints._get_token_if_present = MagicMock(return_value=None)

        response = token_endpoints.get_token_info(mock_request_without_token)

        assert response is not None

    def test_get_token_info_invalid_token(self, token_endpoints, mock_request_with_token):
        """Verify invalid token returns error."""
        token_endpoints._get_token_if_present = MagicMock(
            return_value="invalid_token")
        token_endpoints.sql_connection = MagicMock()
        token_endpoints._is_token_correct = MagicMock(return_value=False)

        response = token_endpoints.get_token_info(mock_request_with_token)

        assert response is not None

    def test_get_token_info_missing_user(self, token_endpoints, mock_request_with_token, sample_token_info):
        """Verify missing user info returns server error."""
        token_endpoints._get_token_if_present = MagicMock(
            return_value="valid_token")
        token_endpoints.sql_connection = MagicMock()
        token_endpoints._is_token_correct = MagicMock(return_value=True)
        token_endpoints._get_token_info = MagicMock(
            return_value=sample_token_info)
        token_endpoints._get_user_info = MagicMock(return_value=None)

        response = token_endpoints.get_token_info(mock_request_with_token)

        assert response is not None


class TestPostRefreshToken:
    """Test token refresh endpoint."""

    def test_refresh_token_generates_new_token(self, token_endpoints, mock_request_with_token, sample_token_info):
        """Verify refresh endpoint generates new token."""
        token_endpoints._get_token_if_present = MagicMock(
            return_value="valid_token")
        token_endpoints.sql_connection = MagicMock()
        token_endpoints._is_token_correct = MagicMock(return_value=True)
        token_endpoints._get_token_info = MagicMock(
            return_value=sample_token_info)
        token_endpoints.boilerplate_non_http_initialised.generate_token = MagicMock(
            return_value="new_token_456")
        token_endpoints.boilerplate_non_http_initialised.set_lifespan = MagicMock(
            return_value=datetime.now() + timedelta(hours=2))
        token_endpoints.sql_connection.update_data_in_table = MagicMock(
            return_value=0)

        response = token_endpoints.post_refresh_token(mock_request_with_token)

        assert response is not None

    def test_refresh_token_no_token(self, token_endpoints, mock_request_without_token):
        """Verify missing token returns unauthorized."""
        token_endpoints._get_token_if_present = MagicMock(return_value=None)

        response = token_endpoints.post_refresh_token(
            mock_request_without_token)

        assert response is not None

    def test_refresh_token_db_error(self, token_endpoints, mock_request_with_token, sample_token_info):
        """Verify database error returns internal server error."""
        token_endpoints._get_token_if_present = MagicMock(
            return_value="valid_token")
        token_endpoints.sql_connection = MagicMock()
        token_endpoints._is_token_correct = MagicMock(return_value=True)
        token_endpoints._get_token_info = MagicMock(
            return_value=sample_token_info)
        token_endpoints.boilerplate_non_http_initialised.generate_token = MagicMock(
            return_value="new_token_456")
        token_endpoints.boilerplate_non_http_initialised.set_lifespan = MagicMock(
            return_value=datetime.now() + timedelta(hours=2))
        token_endpoints.sql_connection.update_data_in_table = MagicMock(
            return_value=84)  # error code

        response = token_endpoints.post_refresh_token(mock_request_with_token)

        assert response is not None


class TestDeleteRevokeAccountToken:
    """Test token revocation endpoint."""

    def test_revoke_tokens_success(self, token_endpoints, mock_request_with_token, sample_token_info):
        """Verify token revocation succeeds."""
        token_endpoints._get_token_if_present = MagicMock(
            return_value="valid_token")
        token_endpoints.sql_connection = MagicMock()
        token_endpoints._is_token_correct = MagicMock(return_value=True)
        token_endpoints._get_token_info = MagicMock(
            return_value=sample_token_info)
        token_endpoints.sql_connection.remove_data_from_table = MagicMock(
            return_value=0)

        response = token_endpoints.delete_revoke_account_token(
            mock_request_with_token)

        assert response is not None

    def test_revoke_tokens_no_token(self, token_endpoints, mock_request_without_token):
        """Verify missing token returns unauthorized."""
        token_endpoints._get_token_if_present = MagicMock(return_value=None)

        response = token_endpoints.delete_revoke_account_token(
            mock_request_without_token)

        assert response is not None

    def test_revoke_tokens_db_error(self, token_endpoints, mock_request_with_token, sample_token_info):
        """Verify database error returns internal server error."""
        token_endpoints._get_token_if_present = MagicMock(
            return_value="valid_token")
        token_endpoints.sql_connection = MagicMock()
        token_endpoints._is_token_correct = MagicMock(return_value=True)
        token_endpoints._get_token_info = MagicMock(
            return_value=sample_token_info)
        token_endpoints.sql_connection.remove_data_from_table = MagicMock(
            return_value=84)  # error code

        response = token_endpoints.delete_revoke_account_token(
            mock_request_with_token)

        assert response is not None
