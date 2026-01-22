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
# FILE: conftest.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Test configuration for endpoint tests (path and lightweight mocks).
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Configuration for endpoint tests to work from multiple locations.
# // AR
# +==== END CatFeeder =================+
"""
import os
import sys
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock, MagicMock
import pytest

# Determine project root relative to this test file
test_file_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(test_file_dir, "..", ".."))
src_dir = os.path.join(project_root, "src")

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


try:
    from libs.endpoint_manager.endpoints.token import TokenEndpoints, TokenInfo, DEFAULT_DATE_PLACEHOLDER
    from libs.utils import constants as CONST
except Exception:
    from src.libs.endpoint_manager.endpoints.token import TokenEndpoints, TokenInfo, DEFAULT_DATE_PLACEHOLDER
    from src.libs.utils import constants as CONST


@pytest.fixture()
def mock_request_with_token():
    """Create a mock request with a valid token in headers."""
    request = MagicMock()
    request.headers = {CONST.REQUEST_TOKEN_KEY: "valid_token_123"}
    request.get = MagicMock(return_value=None)
    return request


@pytest.fixture()
def mock_request_without_token():
    """Create a mock request without a token."""
    request = MagicMock()
    request.headers = {}
    request.get = MagicMock(return_value=None)
    return request


@pytest.fixture()
def mock_request_bearer_token():
    """Create a mock request with Bearer token format."""
    request = MagicMock()
    request.headers = {CONST.REQUEST_BEARER_KEY: "Bearer valid_token_123"}
    request.get = MagicMock(return_value=None)
    return request


@pytest.fixture()
def token_endpoints():
    """Create a TokenEndpoints instance with mocked runtime manager and services."""
    endpoints = object.__new__(TokenEndpoints)
    endpoints.debug = False
    endpoints.success = 0
    endpoints.error = 84

    # Mock runtime manager
    endpoints.runtime_manager = MagicMock()

    # Mock SQL connection
    endpoints.sql_connection = MagicMock()

    # Mock server headers
    endpoints.server_headers_initialised = MagicMock()
    endpoints.server_headers_initialised.for_text = MagicMock(return_value={})
    endpoints.server_headers_initialised.for_json = MagicMock(
        return_value={"Content-Type": "application/json"})

    # Mock boilerplate services
    endpoints.boilerplate_non_http_initialised = MagicMock()
    endpoints.boilerplate_responses_initialised = MagicMock()
    endpoints.boilerplate_incoming_initialised = MagicMock()

    # Mock display logger
    endpoints.disp = MagicMock()

    return endpoints


@pytest.fixture()
def sample_token_info():
    """Create a sample TokenInfo object."""
    now = datetime.now()
    future = now + timedelta(hours=2)
    return TokenInfo(
        token="valid_token_123",
        user_id=1,
        creation_date=now,
        edit_date=now,
        expiration_date=future
    )


@pytest.fixture()
def sample_user_info():
    """Create sample user information."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "admin": "1",
        "password": "hashed_password_xyz",
        "gender": "unknown",
        "age": "25",
        "last_connection": datetime.now().isoformat(),
        "creation_date": datetime.now().isoformat(),
        "edit_date": datetime.now().isoformat(),
        "deletion_date": None
    }
