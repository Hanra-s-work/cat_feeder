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
# FILE: test_path_manager.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Unit tests for the PathManager class to ensure proper endpoint registration and validation.
# // AR
# +==== END CatFeeder =================+
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from types import SimpleNamespace

try:
    from libs.path_manager import PathManager
    from libs.path_manager import path_constants as CONST
except Exception:
    from src.libs.path_manager import PathManager
    from src.libs.path_manager import path_constants as CONST


@pytest.fixture()
def mock_runtime_manager():
    """Create a mock RuntimeManager."""
    mock_rm = MagicMock()
    mock_rm.get_if_exists.return_value = None
    mock_rm.get.return_value = MagicMock()
    return mock_rm


@pytest.fixture()
def path_manager_default(mock_runtime_manager):
    """Create PathManager instance with default parameters."""
    with patch('src.libs.path_manager.path_manager.RI', mock_runtime_manager):
        return PathManager(debug=False)


@pytest.fixture()
def path_manager_custom(mock_runtime_manager):
    """Create PathManager instance with custom parameters."""
    with patch('src.libs.path_manager.path_manager.RI', mock_runtime_manager):
        return PathManager(success=1, error=2, debug=False)


@pytest.fixture()
def sample_endpoint():
    """Create a sample endpoint function."""
    def endpoint_func():
        return {"message": "success"}
    return endpoint_func


class TestPathManagerInitialization:
    """Test PathManager initialization."""

    def test_init_default_values(self, path_manager_default):
        """Verify default initialization values."""
        assert path_manager_default.success == 0
        assert path_manager_default.error == 84
        assert path_manager_default.debug is False
        assert path_manager_default.routes == []

    def test_init_custom_values(self, path_manager_custom):
        """Verify custom initialization values."""
        assert path_manager_custom.success == 1
        assert path_manager_custom.error == 2
        assert path_manager_custom.debug is False

    def test_init_routes_empty_list(self, path_manager_default):
        """Verify routes initialized as empty list."""
        assert isinstance(path_manager_default.routes, list)
        assert len(path_manager_default.routes) == 0


class TestPathConstants:
    """Test path_constants values."""

    def test_path_key_constant(self):
        """Verify PATH_KEY constant."""
        assert CONST.PATH_KEY == "path"

    def test_endpoint_key_constant(self):
        """Verify ENDPOINT_KEY constant."""
        assert CONST.ENDPOINT_KEY == "endpoint"

    def test_method_key_constant(self):
        """Verify METHOD_KEY constant."""
        assert CONST.METHOD_KEY == "method"

    def test_allowed_methods_constant(self):
        """Verify ALLOWED_METHODS constant."""
        assert "GET" in CONST.ALLOWED_METHODS
        assert "POST" in CONST.ALLOWED_METHODS
        assert "PUT" in CONST.ALLOWED_METHODS
        assert "PATCH" in CONST.ALLOWED_METHODS
        assert "DELETE" in CONST.ALLOWED_METHODS
        assert "HEAD" in CONST.ALLOWED_METHODS
        assert "OPTIONS" in CONST.ALLOWED_METHODS

    def test_allowed_methods_count(self):
        """Verify all HTTP methods are present."""
        assert len(CONST.ALLOWED_METHODS) == 7


class TestEndpointValidation:
    """Test endpoint validation."""

    def test_endpoint_valid_with_string_method(self, path_manager_default, sample_endpoint):
        """Verify valid endpoint with string method."""
        result = path_manager_default.endpoint_valid(
            "/api/test", sample_endpoint, "GET")
        assert result is True

    def test_endpoint_valid_with_list_methods(self, path_manager_default, sample_endpoint):
        """Verify valid endpoint with list of methods."""
        result = path_manager_default.endpoint_valid(
            "/api/test", sample_endpoint, ["GET", "POST"])
        assert result is True

    def test_endpoint_invalid_path_not_string(self, path_manager_default, sample_endpoint):
        """Verify invalid when path is not string."""
        result = path_manager_default.endpoint_valid(
            123, sample_endpoint, "GET")
        assert result is False

    def test_endpoint_invalid_endpoint_not_callable(self, path_manager_default):
        """Verify invalid when endpoint is not callable."""
        result = path_manager_default.endpoint_valid(
            "/api/test", "not_callable", "GET")
        assert result is False

    def test_endpoint_invalid_method_string_not_allowed(self, path_manager_default, sample_endpoint):
        """Verify invalid when method string not in ALLOWED_METHODS."""
        result = path_manager_default.endpoint_valid(
            "/api/test", sample_endpoint, "INVALID")
        assert result is False

    def test_endpoint_invalid_method_in_list_not_allowed(self, path_manager_default, sample_endpoint):
        """Verify invalid when any method in list not in ALLOWED_METHODS."""
        result = path_manager_default.endpoint_valid(
            "/api/test", sample_endpoint, ["GET", "INVALID"])
        assert result is False

    def test_endpoint_valid_case_insensitive_method(self, path_manager_default, sample_endpoint):
        """Verify method validation is case-insensitive."""
        result = path_manager_default.endpoint_valid(
            "/api/test", sample_endpoint, "get")
        assert result is True

    def test_endpoint_invalid_method_not_string_or_list(self, path_manager_default, sample_endpoint):
        """Verify invalid when method is not string or list."""
        result = path_manager_default.endpoint_valid(
            "/api/test", sample_endpoint, 123)
        assert result is False


class TestBuildEndpoint:
    """Test endpoint building."""

    def test_build_endpoint_valid_string_method(self, path_manager_default, sample_endpoint):
        """Verify building endpoint with string method."""
        result = path_manager_default._build_endpoint(
            "/api/test", sample_endpoint, "GET")
        assert result is not None
        assert result[CONST.PATH_KEY] == "/api/test"
        assert result[CONST.ENDPOINT_KEY] == sample_endpoint
        assert result[CONST.METHOD_KEY] == ["GET"]

    def test_build_endpoint_valid_list_methods(self, path_manager_default, sample_endpoint):
        """Verify building endpoint with list of methods."""
        methods = ["GET", "POST"]
        result = path_manager_default._build_endpoint(
            "/api/test", sample_endpoint, methods)
        assert result is not None
        assert result[CONST.METHOD_KEY] == ["GET", "POST"]

    def test_build_endpoint_invalid_returns_none(self, path_manager_default):
        """Verify building invalid endpoint returns None."""
        result = path_manager_default._build_endpoint(
            123, "not_callable", "INVALID")
        assert result is None

    def test_build_endpoint_structure(self, path_manager_default, sample_endpoint):
        """Verify endpoint has correct structure."""
        result = path_manager_default._build_endpoint(
            "/api/test", sample_endpoint, "GET")
        assert CONST.PATH_KEY in result
        assert CONST.ENDPOINT_KEY in result
        assert CONST.METHOD_KEY in result


class TestAddPath:
    """Test path addition and management."""

    def test_add_path_success(self, path_manager_default, sample_endpoint):
        """Verify successful path addition."""
        result = path_manager_default.add_path(
            "/api/test", sample_endpoint, "GET")
        assert result == path_manager_default.success
        assert len(path_manager_default.routes) == 1

    def test_add_path_multiple_routes(self, path_manager_default, sample_endpoint):
        """Verify adding multiple paths."""
        def endpoint2():
            return {"message": "endpoint2"}

        path_manager_default.add_path("/api/test1", sample_endpoint, "GET")
        path_manager_default.add_path("/api/test2", endpoint2, "POST")
        assert len(path_manager_default.routes) == 2

    def test_add_path_invalid_path(self, path_manager_default, sample_endpoint):
        """Verify adding invalid path returns error."""
        result = path_manager_default.add_path(123, sample_endpoint, "GET")
        assert result == path_manager_default.error
        assert len(path_manager_default.routes) == 0

    def test_add_path_invalid_endpoint(self, path_manager_default):
        """Verify adding invalid endpoint returns error."""
        result = path_manager_default.add_path(
            "/api/test", "not_callable", "GET")
        assert result == path_manager_default.error
        assert len(path_manager_default.routes) == 0

    def test_add_path_invalid_method(self, path_manager_default, sample_endpoint):
        """Verify adding invalid method returns error."""
        result = path_manager_default.add_path(
            "/api/test", sample_endpoint, "INVALID")
        assert result == path_manager_default.error
        assert len(path_manager_default.routes) == 0

    def test_add_path_duplicate_merges_methods(self, path_manager_default, sample_endpoint):
        """Verify adding duplicate path/endpoint merges methods."""
        path_manager_default.add_path("/api/test", sample_endpoint, "GET")
        result = path_manager_default.add_path(
            "/api/test", sample_endpoint, "POST")

        assert result == path_manager_default.success
        assert len(path_manager_default.routes) == 1
        assert "GET" in path_manager_default.routes[0][CONST.METHOD_KEY]
        assert "POST" in path_manager_default.routes[0][CONST.METHOD_KEY]

    def test_add_path_duplicate_with_list_methods(self, path_manager_default, sample_endpoint):
        """Verify adding duplicate path/endpoint with list of methods."""
        path_manager_default.add_path(
            "/api/test", sample_endpoint, ["GET", "POST"])
        result = path_manager_default.add_path(
            "/api/test", sample_endpoint, "PUT")

        assert result == path_manager_default.success
        assert len(path_manager_default.routes) == 1
        assert len(path_manager_default.routes[0][CONST.METHOD_KEY]) == 3


class TestHasEndpoint:
    """Test endpoint existence checking."""

    def test_has_endpoint_exists(self, path_manager_default, sample_endpoint):
        """Verify checking for existing endpoint."""
        path_manager_default.add_path("/api/test", sample_endpoint, "GET")
        result = path_manager_default.has_endpoint(
            "/api/test", sample_endpoint, "GET")
        assert result is True

    def test_has_endpoint_not_exists(self, path_manager_default, sample_endpoint):
        """Verify checking for non-existing endpoint."""
        result = path_manager_default.has_endpoint(
            "/api/test", sample_endpoint, "GET")
        assert result is False

    def test_has_endpoint_different_path(self, path_manager_default, sample_endpoint):
        """Verify checking for different path."""
        path_manager_default.add_path("/api/test1", sample_endpoint, "GET")
        result = path_manager_default.has_endpoint(
            "/api/test2", sample_endpoint, "GET")
        assert result is False

    def test_has_endpoint_different_endpoint(self, path_manager_default, sample_endpoint):
        """Verify checking for different endpoint function."""
        def other_endpoint():
            pass

        path_manager_default.add_path("/api/test", sample_endpoint, "GET")
        result = path_manager_default.has_endpoint(
            "/api/test", other_endpoint, "GET")
        assert result is False

    def test_has_endpoint_different_method(self, path_manager_default, sample_endpoint):
        """Verify checking for different method."""
        path_manager_default.add_path("/api/test", sample_endpoint, "GET")
        result = path_manager_default.has_endpoint(
            "/api/test", sample_endpoint, "POST")
        assert result is False


class TestFindRouteIndex:
    """Test route index finding."""

    def test_find_route_index_found(self, path_manager_default, sample_endpoint):
        """Verify finding route index when exists."""
        path_manager_default.add_path("/api/test", sample_endpoint, "GET")
        index = path_manager_default._find_route_index(
            "/api/test", sample_endpoint)
        assert index == 0

    def test_find_route_index_not_found(self, path_manager_default, sample_endpoint):
        """Verify finding route index when not exists."""
        index = path_manager_default._find_route_index(
            "/api/test", sample_endpoint)
        assert index == -1

    def test_find_route_index_multiple_routes(self, path_manager_default, sample_endpoint):
        """Verify finding correct index in multiple routes."""
        def endpoint2():
            pass

        path_manager_default.add_path("/api/test1", sample_endpoint, "GET")
        path_manager_default.add_path("/api/test2", endpoint2, "GET")
        path_manager_default.add_path("/api/test3", sample_endpoint, "GET")

        index = path_manager_default._find_route_index(
            "/api/test3", sample_endpoint)
        assert index == 2

    def test_find_route_index_different_endpoint_same_path(self, path_manager_default, sample_endpoint):
        """Verify finding index distinguishes by endpoint function."""
        def endpoint2():
            pass

        path_manager_default.add_path("/api/test", sample_endpoint, "GET")
        path_manager_default.add_path("/api/test", endpoint2, "POST")

        index = path_manager_default._find_route_index("/api/test", endpoint2)
        assert index == 1


class TestMergeMethods:
    """Test method merging."""

    def test_merge_methods_string_to_list(self, path_manager_default):
        """Verify merging string method to list."""
        existing = ["GET", "POST"]
        result = path_manager_default._merge_methods(existing, "PUT")
        assert "GET" in result
        assert "POST" in result
        assert "PUT" in result
        assert len(result) == 3

    def test_merge_methods_list_to_list(self, path_manager_default):
        """Verify merging list methods to list."""
        existing = ["GET", "POST"]
        result = path_manager_default._merge_methods(
            existing, ["PUT", "DELETE"])
        assert len(result) == 4
        assert "DELETE" in result

    def test_merge_methods_no_duplicates(self, path_manager_default):
        """Verify merging removes duplicates."""
        existing = ["GET", "POST"]
        result = path_manager_default._merge_methods(existing, "GET")
        assert result.count("GET") == 1
        assert len(result) == 2

    def test_merge_methods_case_normalization(self, path_manager_default):
        """Verify merging normalizes case to uppercase."""
        existing = ["get", "post"]
        result = path_manager_default._merge_methods(existing, "put")
        assert "GET" in result
        assert "POST" in result
        assert "PUT" in result

    def test_merge_methods_sorted(self, path_manager_default):
        """Verify merged methods are sorted."""
        existing = ["POST", "GET"]
        result = path_manager_default._merge_methods(existing, "DELETE")
        assert result == sorted(result)

    def test_merge_methods_empty_existing(self, path_manager_default):
        """Verify merging with empty existing methods."""
        existing = []
        result = path_manager_default._merge_methods(existing, "GET")
        assert "GET" in result
        assert len(result) == 1

    def test_merge_methods_empty_new(self, path_manager_default):
        """Verify merging with empty new methods."""
        existing = ["GET", "POST"]
        result = path_manager_default._merge_methods(existing, [])
        assert "GET" in result
        assert "POST" in result
        assert len(result) == 2


class TestInjectRoutes:
    """Test route injection into FastAPI."""

    def test_inject_routes_no_app(self, path_manager_default, sample_endpoint):
        """Verify inject_routes raises when app not available."""
        path_manager_default.add_path("/api/test", sample_endpoint, "GET")
        path_manager_default.runtime_control_initialised.app = None

        with pytest.raises(RuntimeError):
            path_manager_default.inject_routes()

    def test_inject_routes_no_add_api_route(self, path_manager_default, sample_endpoint):
        """Verify inject_routes raises when add_api_route not available."""
        mock_app = Mock()
        del mock_app.add_api_route
        path_manager_default.runtime_control_initialised.app = mock_app

        with pytest.raises(RuntimeError):
            path_manager_default.inject_routes()

    def test_inject_routes_success(self, path_manager_default, sample_endpoint):
        """Verify successful route injection."""
        mock_app = MagicMock()
        path_manager_default.runtime_control_initialised.app = mock_app

        path_manager_default.add_path("/api/test", sample_endpoint, "GET")
        path_manager_default.inject_routes()

        mock_app.add_api_route.assert_called_once()
        call_args = mock_app.add_api_route.call_args
        assert call_args[0][0] == "/api/test"
        assert call_args[0][1] == sample_endpoint
        assert call_args[1]["methods"] == ["GET"]

    def test_inject_routes_multiple(self, path_manager_default):
        """Verify injecting multiple routes."""
        def endpoint1():
            pass

        def endpoint2():
            pass

        mock_app = MagicMock()
        path_manager_default.runtime_control_initialised.app = mock_app

        path_manager_default.add_path("/api/test1", endpoint1, "GET")
        path_manager_default.add_path("/api/test2", endpoint2, "POST")
        path_manager_default.inject_routes()

        assert mock_app.add_api_route.call_count == 2


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_path_with_parameters(self, path_manager_default, sample_endpoint):
        """Verify handling paths with parameters."""
        path = "/api/users/{user_id}"
        result = path_manager_default.add_path(path, sample_endpoint, "GET")
        assert result == path_manager_default.success
        assert path_manager_default.routes[0][CONST.PATH_KEY] == path

    def test_root_path(self, path_manager_default, sample_endpoint):
        """Verify handling root path."""
        result = path_manager_default.add_path("/", sample_endpoint, "GET")
        assert result == path_manager_default.success

    def test_path_with_query_params_in_definition(self, path_manager_default, sample_endpoint):
        """Verify handling path with query params."""
        path = "/api/search?q=test"
        result = path_manager_default.add_path(path, sample_endpoint, "GET")
        assert result == path_manager_default.success

    def test_all_allowed_methods(self, path_manager_default, sample_endpoint):
        """Verify adding endpoint with all allowed methods."""
        result = path_manager_default.add_path(
            "/api/test",
            sample_endpoint,
            CONST.ALLOWED_METHODS
        )
        assert result == path_manager_default.success
        assert len(path_manager_default.routes[0][CONST.METHOD_KEY]) == len(
            CONST.ALLOWED_METHODS)

    def test_empty_path_string(self, path_manager_default, sample_endpoint):
        """Verify handling empty path string."""
        result = path_manager_default.add_path("", sample_endpoint, "GET")
        # Empty string is still a string, so it should be valid
        assert result == path_manager_default.success

    def test_lambda_as_endpoint(self, path_manager_default):
        """Verify handling lambda as endpoint."""
        def endpoint(): return {"message": "lambda"}
        result = path_manager_default.add_path("/api/test", endpoint, "GET")
        assert result == path_manager_default.success

    def test_class_method_as_endpoint(self, path_manager_default):
        """Verify handling class method as endpoint."""
        class TestClass:
            def method(self):
                return {"message": "method"}

        obj = TestClass()
        result = path_manager_default.add_path("/api/test", obj.method, "GET")
        assert result == path_manager_default.success

    def test_mixed_case_methods(self, path_manager_default, sample_endpoint):
        """Verify handling mixed case HTTP methods."""
        result = path_manager_default.add_path(
            "/api/test", sample_endpoint, "GeT")
        assert result == path_manager_default.success
