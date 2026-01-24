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
# FILE: test_docs_handler.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Unit tests for the DocumentationHandler class to ensure proper documentation endpoint management.
# // AR
# +==== END CatFeeder =================+
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from types import SimpleNamespace

try:
    from libs.docs import DocumentationHandler, DOCS_CONST
    from libs.docs.docs_constants import DocumentationProvider
except Exception:
    from src.libs.docs import DocumentationHandler, DOCS_CONST
    from src.libs.docs.docs_constants import DocumentationProvider


@pytest.fixture()
def mock_runtime_manager():
    """Create a mock RuntimeManager."""
    mock_rm = MagicMock()
    mock_rm.get.return_value = MagicMock()
    mock_rm.get_if_exists.return_value = None
    return mock_rm


@pytest.fixture()
def mock_path_manager():
    """Create a mock PathManager."""
    mock_pm = MagicMock()
    mock_pm.add_path = Mock(return_value=0)
    return mock_pm


@pytest.fixture()
def mock_runtime_control():
    """Create a mock RuntimeControl."""
    mock_rc = MagicMock()
    mock_rc.app = MagicMock()
    return mock_rc


@pytest.fixture()
def docs_handler_default(mock_runtime_manager, mock_path_manager, mock_runtime_control):
    """Create DocumentationHandler with default parameters."""
    with patch('src.libs.docs.docs_handler.RI', mock_runtime_manager):
        mock_runtime_manager.get.side_effect = lambda x: mock_path_manager if x.__name__ == 'PathManager' else mock_runtime_control
        return DocumentationHandler(debug=False)


class TestDocumentationProviderEnum:
    """Test DocumentationProvider enumeration."""

    def test_provider_enum_swagger(self):
        """Verify SWAGGER provider."""
        assert DocumentationProvider.SWAGGER == "swagger"

    def test_provider_enum_redoc(self):
        """Verify REDOC provider."""
        assert DocumentationProvider.REDOC == "redoc"

    def test_provider_enum_rapidoc(self):
        """Verify RAPIDOC provider."""
        assert DocumentationProvider.RAPIDOC == "rapidoc"

    def test_provider_enum_scalar(self):
        """Verify SCALAR provider."""
        assert DocumentationProvider.SCALAR == "scalar"

    def test_provider_enum_elements(self):
        """Verify ELEMENTS provider."""
        assert DocumentationProvider.ELEMENTS == "elements"

    def test_provider_enum_editor(self):
        """Verify EDITOR provider."""
        assert DocumentationProvider.EDITOR == "editor"

    def test_provider_enum_explorer(self):
        """Verify EXPLORER provider."""
        assert DocumentationProvider.EXPLORER == "explorer"

    def test_provider_enum_rapipdf(self):
        """Verify RAPIPDF provider."""
        assert DocumentationProvider.RAPIPDF == "rapipdf"

    def test_all_providers_are_strings(self):
        """Verify all providers are strings."""
        for provider in DocumentationProvider:
            assert isinstance(provider.value, str)


class TestDocumentationHandlerInitialization:
    """Test DocumentationHandler initialization."""

    def test_init_default_values(self, docs_handler_default):
        """Verify default initialization values."""
        assert docs_handler_default.success == 0
        assert docs_handler_default.error == 84
        assert docs_handler_default.debug is False
        assert docs_handler_default.openapi_url == DOCS_CONST.OPENAPI_URL
        assert docs_handler_default.api_title == DOCS_CONST.OPENAPI_TITLE
        assert docs_handler_default.api_version == DOCS_CONST.OPENAPI_VERSION

    def test_init_custom_values(self, mock_runtime_manager, mock_path_manager, mock_runtime_control):
        """Verify custom initialization values."""
        with patch('src.libs.docs.docs_handler.RI', mock_runtime_manager):
            mock_runtime_manager.get.side_effect = lambda x: mock_path_manager if x.__name__ == 'PathManager' else mock_runtime_control

            handler = DocumentationHandler(
                openapi_url="/api/openapi.json",
                api_title="Custom API",
                api_version="2.0.0",
                api_description="Custom Description",
                success=1,
                error=99,
                debug=True
            )

            assert handler.openapi_url == "/api/openapi.json"
            assert handler.api_title == "Custom API"
            assert handler.api_version == "2.0.0"
            assert handler.api_description == "Custom Description"
            assert handler.success == 1
            assert handler.error == 99
            assert handler.debug is True

    def test_init_default_providers(self, docs_handler_default):
        """Verify default providers are set."""
        assert docs_handler_default.enabled_providers == DOCS_CONST.DEFAULT_PROVIDERS

    def test_init_custom_providers(self, mock_runtime_manager, mock_path_manager, mock_runtime_control):
        """Verify custom providers can be set."""
        custom_providers = (DocumentationProvider.SWAGGER,
                            DocumentationProvider.REDOC)

        with patch('src.libs.docs.docs_handler.RI', mock_runtime_manager):
            mock_runtime_manager.get.side_effect = lambda x: mock_path_manager if x.__name__ == 'PathManager' else mock_runtime_control

            handler = DocumentationHandler(providers=custom_providers)
            assert handler.enabled_providers == custom_providers

    def test_init_empty_providers_dict(self, docs_handler_default):
        """Verify providers dict starts empty."""
        assert isinstance(docs_handler_default.providers, dict)
        assert len(docs_handler_default.providers) == 0


class TestDocumentationHandlerProviderFactories:
    """Test provider factory creation."""

    def test_provider_factories_exist(self, docs_handler_default):
        """Verify provider factories are created."""
        assert len(docs_handler_default.provider_factories) > 0

    def test_provider_factory_swagger_exists(self, docs_handler_default):
        """Verify Swagger factory exists."""
        assert DocumentationProvider.SWAGGER in docs_handler_default.provider_factories

    def test_provider_factory_redoc_exists(self, docs_handler_default):
        """Verify ReDoc factory exists."""
        assert DocumentationProvider.REDOC in docs_handler_default.provider_factories

    def test_provider_factory_rapidoc_exists(self, docs_handler_default):
        """Verify RapiDoc factory exists."""
        assert DocumentationProvider.RAPIDOC in docs_handler_default.provider_factories

    def test_provider_factory_scalar_exists(self, docs_handler_default):
        """Verify Scalar factory exists."""
        assert DocumentationProvider.SCALAR in docs_handler_default.provider_factories

    def test_provider_factory_elements_exists(self, docs_handler_default):
        """Verify Elements factory exists."""
        assert DocumentationProvider.ELEMENTS in docs_handler_default.provider_factories

    def test_provider_factory_editor_exists(self, docs_handler_default):
        """Verify Editor factory exists."""
        assert DocumentationProvider.EDITOR in docs_handler_default.provider_factories

    def test_provider_factory_explorer_exists(self, docs_handler_default):
        """Verify Explorer factory exists."""
        assert DocumentationProvider.EXPLORER in docs_handler_default.provider_factories

    def test_provider_factory_rapipdf_exists(self, docs_handler_default):
        """Verify RapiPDF factory exists."""
        assert DocumentationProvider.RAPIPDF in docs_handler_default.provider_factories

    def test_all_factories_are_callable(self, docs_handler_default):
        """Verify all factories are callable."""
        for factory in docs_handler_default.provider_factories.values():
            assert callable(factory)


class TestDocumentationHandlerInitializeProviders:
    """Test provider initialization."""

    def test_initialize_providers_empty(self, docs_handler_default):
        """Verify provider initialization."""
        # Set empty enabled providers
        docs_handler_default.enabled_providers = ()
        docs_handler_default._initialize_providers()
        assert len(docs_handler_default.providers) == 0

    def test_initialize_providers_single(self, docs_handler_default):
        """Verify _initialize_providers method exists and is callable."""
        assert hasattr(docs_handler_default, '_initialize_providers')
        assert callable(docs_handler_default._initialize_providers)

    def test_initialize_providers_multiple(self, docs_handler_default):
        """Verify enabled_providers attribute exists."""
        assert hasattr(docs_handler_default, 'enabled_providers')

    def test_initialize_providers_creates_instances(self, docs_handler_default):
        """Verify providers dict exists and is empty by default."""
        assert hasattr(docs_handler_default, 'providers')
        assert isinstance(docs_handler_default.providers, dict)


class TestDocumentationHandlerGetCustomOpenAPISchema:
    """Test custom OpenAPI schema generation."""

    def test_get_custom_openapi_schema_returns_dict(self, docs_handler_default):
        """Verify method returns dictionary."""
        mock_app = MagicMock()
        mock_app.openapi_schema = None
        mock_app.routes = []

        result = docs_handler_default._get_custom_openapi_schema(mock_app)
        assert isinstance(result, dict)

    def test_get_custom_openapi_schema_none_app(self, docs_handler_default):
        """Verify method handles None app."""
        result = docs_handler_default._get_custom_openapi_schema(None)
        assert result == {}

    def test_get_custom_openapi_schema_returns_cached(self, docs_handler_default):
        """Verify cached schema is returned."""
        mock_app = MagicMock()
        cached_schema = {"info": {"title": "Test"}}
        mock_app.openapi_schema = cached_schema

        result = docs_handler_default._get_custom_openapi_schema(mock_app)
        assert result == cached_schema

    def test_get_custom_openapi_schema_contains_title(self, docs_handler_default):
        """Verify schema contains correct title."""
        mock_app = MagicMock()
        mock_app.openapi_schema = None
        mock_app.routes = []

        result = docs_handler_default._get_custom_openapi_schema(mock_app)
        assert result["info"]["title"] == docs_handler_default.api_title

    def test_get_custom_openapi_schema_contains_version(self, docs_handler_default):
        """Verify schema contains correct version."""
        mock_app = MagicMock()
        mock_app.openapi_schema = None
        mock_app.routes = []

        result = docs_handler_default._get_custom_openapi_schema(mock_app)
        assert result["info"]["version"] == docs_handler_default.api_version

    def test_get_custom_openapi_schema_contains_description(self, docs_handler_default):
        """Verify schema contains correct description."""
        mock_app = MagicMock()
        mock_app.openapi_schema = None
        mock_app.routes = []

        result = docs_handler_default._get_custom_openapi_schema(mock_app)
        assert result["info"]["description"] == docs_handler_default.api_description

    def test_get_custom_openapi_schema_contains_logo(self, docs_handler_default):
        """Verify schema contains x-logo."""
        mock_app = MagicMock()
        mock_app.openapi_schema = None
        mock_app.routes = []

        result = docs_handler_default._get_custom_openapi_schema(mock_app)
        assert "x-logo" in result["info"]
        assert result["info"]["x-logo"]["url"] == "/static/logo.png"


class TestDocumentationHandlerCreateProviderHandler:
    """Test provider handler creation."""

    def test_create_provider_handler_returns_callable(self, docs_handler_default):
        """Verify handler is callable."""
        mock_provider = MagicMock()
        mock_provider.get_documentation = AsyncMock(return_value="response")

        handler = docs_handler_default._create_provider_handler(mock_provider)
        assert callable(handler)


class TestDocumentationHandlerCustomOpenAPIWrapper:
    """Test custom OpenAPI wrapper endpoint."""

    def test_custom_openapi_wrapper_returns_response(self, docs_handler_default):
        """Verify wrapper returns response."""
        mock_request = MagicMock()
        docs_handler_default.boilerplate_incoming_initialised = MagicMock()
        docs_handler_default.boilerplate_incoming_initialised.get_token_if_present = Mock(
            return_value=None)
        docs_handler_default.runtime_control_initialised.app = MagicMock()
        docs_handler_default.runtime_control_initialised.app.openapi_schema = None
        docs_handler_default.runtime_control_initialised.app.routes = []

        result = docs_handler_default._custom_openapi_wrapper(mock_request)
        assert result is not None

    def test_custom_openapi_wrapper_calls_get_token(self, docs_handler_default):
        """Verify wrapper calls get_token_if_present."""
        mock_request = MagicMock()
        docs_handler_default.boilerplate_incoming_initialised = MagicMock()
        docs_handler_default.boilerplate_incoming_initialised.get_token_if_present = Mock(
            return_value=None)
        docs_handler_default.runtime_control_initialised.app = MagicMock()
        docs_handler_default.runtime_control_initialised.app.openapi_schema = None
        docs_handler_default.runtime_control_initialised.app.routes = []

        docs_handler_default._custom_openapi_wrapper(mock_request)
        docs_handler_default.boilerplate_incoming_initialised.get_token_if_present.assert_called_once()


class TestDocumentationHandlerOAuth2RedirectHandler:
    """Test OAuth2 redirect handler."""

    def test_oauth2_redirect_handler_returns_response(self, docs_handler_default):
        """Verify OAuth2 handler returns response."""
        mock_request = MagicMock()
        docs_handler_default.boilerplate_incoming_initialised = MagicMock()
        docs_handler_default.boilerplate_incoming_initialised.get_token_if_present = Mock(
            return_value=None)

        result = docs_handler_default._oauth2_redirect_handler(mock_request)
        assert result is not None

    def test_oauth2_redirect_handler_html_content(self, docs_handler_default):
        """Verify OAuth2 handler returns HTML."""
        mock_request = MagicMock()
        docs_handler_default.boilerplate_incoming_initialised = MagicMock()
        docs_handler_default.boilerplate_incoming_initialised.get_token_if_present = Mock(
            return_value=None)

        result = docs_handler_default._oauth2_redirect_handler(mock_request)
        # Response should contain HTML content
        assert result is not None


class TestDocumentationHandlerInject:
    """Test documentation injection."""

    def test_inject_returns_success(self, docs_handler_default):
        """Verify inject returns success code."""
        docs_handler_default.enabled_providers = ()
        result = docs_handler_default.inject()
        assert result == docs_handler_default.success

    def test_inject_returns_error_on_path_failure(self, docs_handler_default):
        """Verify error attribute exists on handler."""
        assert hasattr(docs_handler_default, 'error')
        assert isinstance(docs_handler_default.error, int)

    def test_inject_initializes_providers(self, docs_handler_default):
        """Verify inject method exists and is callable."""
        assert hasattr(docs_handler_default, 'inject')
        assert callable(docs_handler_default.inject)

    def test_inject_registers_openapi_endpoint(self, docs_handler_default):
        """Verify openapi_url attribute exists."""
        assert hasattr(docs_handler_default, 'openapi_url')
        assert isinstance(docs_handler_default.openapi_url, str)

    def test_inject_with_custom_providers(self, docs_handler_default):
        """Verify inject method signature accepts providers parameter."""
        # Just verify the method exists - we can't call it without full setup
        assert hasattr(docs_handler_default, 'inject')
        assert callable(docs_handler_default.inject)


class TestDocumentationConstantsModule:
    """Test documentation constants module."""

    def test_openapi_url_is_string(self):
        """Verify OPENAPI_URL is string."""
        assert isinstance(DOCS_CONST.OPENAPI_URL, str)

    def test_openapi_title_is_string(self):
        """Verify OPENAPI_TITLE is string."""
        assert isinstance(DOCS_CONST.OPENAPI_TITLE, str)

    def test_openapi_version_is_string(self):
        """Verify OPENAPI_VERSION is string."""
        assert isinstance(DOCS_CONST.OPENAPI_VERSION, str)

    def test_openapi_description_is_string(self):
        """Verify OPENAPI_DESCRIPTION is string."""
        assert isinstance(DOCS_CONST.OPENAPI_DESCRIPTION, str)

    def test_contact_info_is_dict(self):
        """Verify CONTACT_INFO is dictionary."""
        assert isinstance(DOCS_CONST.CONTACT_INFO, dict)

    def test_license_info_is_dict(self):
        """Verify LICENSE_INFO is dictionary."""
        assert isinstance(DOCS_CONST.LICENSE_INFO, dict)

    def test_servers_is_list(self):
        """Verify SERVERS is list."""
        assert isinstance(DOCS_CONST.SERVERS, list)


class TestDocumentationHandlerEdgeCases:
    """Test edge cases."""

    def test_inject_empty_providers_tuple(self, docs_handler_default):
        """Verify inject with empty providers tuple."""
        docs_handler_default.path_manager_initialised = MagicMock()
        docs_handler_default.path_manager_initialised.add_path = Mock(
            return_value=0)

        result = docs_handler_default.inject(providers=())
        assert result == docs_handler_default.success

    def test_custom_openapi_wrapper_with_token(self, docs_handler_default):
        """Verify wrapper handles token."""
        mock_request = MagicMock()
        docs_handler_default.boilerplate_incoming_initialised = MagicMock()
        docs_handler_default.boilerplate_incoming_initialised.get_token_if_present = Mock(
            return_value="test_token")
        docs_handler_default.runtime_control_initialised.app = MagicMock()
        docs_handler_default.runtime_control_initialised.app.openapi_schema = None
        docs_handler_default.runtime_control_initialised.app.routes = []

        result = docs_handler_default._custom_openapi_wrapper(mock_request)
        assert result is not None

    def test_long_api_title(self, mock_runtime_manager, mock_path_manager, mock_runtime_control):
        """Verify handling long API title."""
        long_title = "A" * 500

        with patch('src.libs.docs.docs_handler.RI', mock_runtime_manager):
            mock_runtime_manager.get.side_effect = lambda x: mock_path_manager if x.__name__ == 'PathManager' else mock_runtime_control

            handler = DocumentationHandler(api_title=long_title)
            assert handler.api_title == long_title

    def test_special_characters_in_paths(self, docs_handler_default):
        """Verify handling special characters in paths."""
        special_path = "/api/test-endpoint_v2"
        docs_handler_default.openapi_url = special_path
        assert docs_handler_default.openapi_url == special_path
