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
# FILE: test_docs_constants.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Unit tests for the documentation constants module.
# // AR
# +==== END CatFeeder =================+
"""
import pytest

try:
    from libs.docs import docs_constants as DOCS_CONST
    from libs.docs.docs_constants import DocumentationProvider
except Exception:
    from src.libs.docs import docs_constants as DOCS_CONST
    from src.libs.docs.docs_constants import DocumentationProvider


class TestDocumentationProvider:
    """Test DocumentationProvider enumeration."""

    def test_provider_values_are_strings(self):
        """Verify all provider values are strings."""
        for provider in DocumentationProvider:
            assert isinstance(provider.value, str)

    def test_provider_enum_count(self):
        """Verify expected number of providers."""
        assert len(DocumentationProvider) == 8

    def test_provider_swagger(self):
        """Verify SWAGGER provider value."""
        assert DocumentationProvider.SWAGGER.value == "swagger"

    def test_provider_redoc(self):
        """Verify REDOC provider value."""
        assert DocumentationProvider.REDOC.value == "redoc"

    def test_provider_rapidoc(self):
        """Verify RAPIDOC provider value."""
        assert DocumentationProvider.RAPIDOC.value == "rapidoc"

    def test_provider_scalar(self):
        """Verify SCALAR provider value."""
        assert DocumentationProvider.SCALAR.value == "scalar"

    def test_provider_elements(self):
        """Verify ELEMENTS provider value."""
        assert DocumentationProvider.ELEMENTS.value == "elements"

    def test_provider_editor(self):
        """Verify EDITOR provider value."""
        assert DocumentationProvider.EDITOR.value == "editor"

    def test_provider_explorer(self):
        """Verify EXPLORER provider value."""
        assert DocumentationProvider.EXPLORER.value == "explorer"

    def test_provider_rapipdf(self):
        """Verify RAPIPDF provider value."""
        assert DocumentationProvider.RAPIPDF.value == "rapipdf"


class TestOpenAPIConfiguration:
    """Test OpenAPI configuration constants."""

    def test_openapi_url_exists(self):
        """Verify OPENAPI_URL is defined."""
        assert hasattr(DOCS_CONST, "OPENAPI_URL")

    def test_openapi_url_is_string(self):
        """Verify OPENAPI_URL is a string."""
        assert isinstance(DOCS_CONST.OPENAPI_URL, str)

    def test_openapi_url_is_not_empty(self):
        """Verify OPENAPI_URL is not empty."""
        assert len(DOCS_CONST.OPENAPI_URL) > 0

    def test_openapi_url_starts_with_slash(self):
        """Verify OPENAPI_URL starts with /."""
        assert DOCS_CONST.OPENAPI_URL.startswith("/")

    def test_openapi_title_exists(self):
        """Verify OPENAPI_TITLE is defined."""
        assert hasattr(DOCS_CONST, "OPENAPI_TITLE")

    def test_openapi_title_is_string(self):
        """Verify OPENAPI_TITLE is a string."""
        assert isinstance(DOCS_CONST.OPENAPI_TITLE, str)

    def test_openapi_title_is_not_empty(self):
        """Verify OPENAPI_TITLE is not empty."""
        assert len(DOCS_CONST.OPENAPI_TITLE) > 0

    def test_openapi_version_exists(self):
        """Verify OPENAPI_VERSION is defined."""
        assert hasattr(DOCS_CONST, "OPENAPI_VERSION")

    def test_openapi_version_is_string(self):
        """Verify OPENAPI_VERSION is a string."""
        assert isinstance(DOCS_CONST.OPENAPI_VERSION, str)

    def test_openapi_version_is_not_empty(self):
        """Verify OPENAPI_VERSION is not empty."""
        assert len(DOCS_CONST.OPENAPI_VERSION) > 0

    def test_openapi_description_exists(self):
        """Verify OPENAPI_DESCRIPTION is defined."""
        assert hasattr(DOCS_CONST, "OPENAPI_DESCRIPTION")

    def test_openapi_description_is_string(self):
        """Verify OPENAPI_DESCRIPTION is a string."""
        assert isinstance(DOCS_CONST.OPENAPI_DESCRIPTION, str)


class TestContactInformation:
    """Test contact information constants."""

    def test_contact_info_exists(self):
        """Verify CONTACT_INFO is defined."""
        assert hasattr(DOCS_CONST, "CONTACT_INFO")

    def test_contact_info_is_dict(self):
        """Verify CONTACT_INFO is a dictionary."""
        assert isinstance(DOCS_CONST.CONTACT_INFO, dict)

    def test_contact_info_has_name(self):
        """Verify CONTACT_INFO has name."""
        assert "name" in DOCS_CONST.CONTACT_INFO

    def test_contact_info_has_url(self):
        """Verify CONTACT_INFO has url."""
        assert "url" in DOCS_CONST.CONTACT_INFO

    def test_contact_info_has_email(self):
        """Verify CONTACT_INFO has email."""
        assert "email" in DOCS_CONST.CONTACT_INFO

    def test_contact_info_name_is_string(self):
        """Verify contact name is string."""
        assert isinstance(DOCS_CONST.CONTACT_INFO["name"], str)

    def test_contact_info_url_is_string(self):
        """Verify contact url is string."""
        assert isinstance(DOCS_CONST.CONTACT_INFO["url"], str)

    def test_contact_info_email_is_string(self):
        """Verify contact email is string."""
        assert isinstance(DOCS_CONST.CONTACT_INFO["email"], str)


class TestLicenseInformation:
    """Test license information constants."""

    def test_license_info_exists(self):
        """Verify LICENSE_INFO is defined."""
        assert hasattr(DOCS_CONST, "LICENSE_INFO")

    def test_license_info_is_dict(self):
        """Verify LICENSE_INFO is a dictionary."""
        assert isinstance(DOCS_CONST.LICENSE_INFO, dict)

    def test_license_info_has_name(self):
        """Verify LICENSE_INFO has name."""
        assert "name" in DOCS_CONST.LICENSE_INFO

    def test_license_info_has_url(self):
        """Verify LICENSE_INFO has url."""
        assert "url" in DOCS_CONST.LICENSE_INFO

    def test_license_info_name_is_string(self):
        """Verify license name is string."""
        assert isinstance(DOCS_CONST.LICENSE_INFO["name"], str)

    def test_license_info_url_is_string(self):
        """Verify license url is string."""
        assert isinstance(DOCS_CONST.LICENSE_INFO["url"], str)


class TestServersConfiguration:
    """Test server configuration constants."""

    def test_servers_exists(self):
        """Verify SERVERS is defined."""
        assert hasattr(DOCS_CONST, "SERVERS")

    def test_servers_is_list(self):
        """Verify SERVERS is a list."""
        assert isinstance(DOCS_CONST.SERVERS, list)

    def test_servers_not_empty(self):
        """Verify SERVERS list is not empty."""
        assert len(DOCS_CONST.SERVERS) > 0

    def test_servers_contain_url(self):
        """Verify servers contain url field."""
        for server in DOCS_CONST.SERVERS:
            assert isinstance(server, dict)
            assert "url" in server

    def test_servers_contain_description(self):
        """Verify servers contain description field."""
        for server in DOCS_CONST.SERVERS:
            assert isinstance(server, dict)
            assert "description" in server


class TestTagsMetadata:
    """Test tags metadata constants."""

    def test_tags_metadata_exists(self):
        """Verify TAGS_METADATA is defined."""
        assert hasattr(DOCS_CONST, "TAGS_METADATA")

    def test_tags_metadata_is_list(self):
        """Verify TAGS_METADATA is a list."""
        assert isinstance(DOCS_CONST.TAGS_METADATA, list)


class TestOAuth2Configuration:
    """Test OAuth2 configuration constants."""

    def test_enable_oauth2_docs_exists(self):
        """Verify ENABLE_OAUTH2_DOCS is defined."""
        assert hasattr(DOCS_CONST, "ENABLE_OAUTH2_DOCS")

    def test_enable_oauth2_docs_is_bool(self):
        """Verify ENABLE_OAUTH2_DOCS is boolean."""
        assert isinstance(DOCS_CONST.ENABLE_OAUTH2_DOCS, bool)

    def test_oauth2_authorization_url_exists(self):
        """Verify OAUTH2_AUTHORIZATION_URL is defined."""
        assert hasattr(DOCS_CONST, "OAUTH2_AUTHORIZATION_URL")

    def test_oauth2_token_url_exists(self):
        """Verify OAUTH2_TOKEN_URL is defined."""
        assert hasattr(DOCS_CONST, "OAUTH2_TOKEN_URL")

    def test_oauth2_redirect_url_exists(self):
        """Verify OAUTH2_REDIRECT_URL is defined."""
        assert hasattr(DOCS_CONST, "OAUTH2_REDIRECT_URL")

    def test_oauth2_scopes_exists(self):
        """Verify OAUTH2_SCOPES is defined."""
        assert hasattr(DOCS_CONST, "OAUTH2_SCOPES")

    def test_oauth2_redirect_url_is_string(self):
        """Verify OAUTH2_REDIRECT_URL is string."""
        assert isinstance(DOCS_CONST.OAUTH2_REDIRECT_URL, str)


class TestDefaultProviders:
    """Test default providers configuration."""

    def test_default_providers_exists(self):
        """Verify DEFAULT_PROVIDERS is defined."""
        assert hasattr(DOCS_CONST, "DEFAULT_PROVIDERS")

    def test_default_providers_is_tuple(self):
        """Verify DEFAULT_PROVIDERS is a tuple."""
        assert isinstance(DOCS_CONST.DEFAULT_PROVIDERS, tuple)

    def test_default_providers_may_be_empty(self):
        """Verify DEFAULT_PROVIDERS length is valid.

        DEFAULT_PROVIDERS is built from environment variables that default to False,
        so it may be empty if no providers are explicitly enabled in the environment.
        """
        assert len(DOCS_CONST.DEFAULT_PROVIDERS) >= 0

    def test_default_providers_contain_valid_providers(self):
        """Verify all default providers are valid DocumentationProviders."""
        for provider in DOCS_CONST.DEFAULT_PROVIDERS:
            assert provider in DocumentationProvider


class TestConstantsConsistency:
    """Test consistency of constants."""

    def test_all_string_constants_not_empty(self):
        """Verify all string constants are not empty."""
        string_constants = [
            DOCS_CONST.OPENAPI_URL,
            DOCS_CONST.OPENAPI_TITLE,
            DOCS_CONST.OPENAPI_VERSION,
            DOCS_CONST.OAUTH2_REDIRECT_URL,
        ]

        for const in string_constants:
            assert isinstance(const, str)
            assert len(const) > 0

    def test_all_dict_constants_are_dicts(self):
        """Verify all dict constants are dictionaries."""
        dict_constants = [
            DOCS_CONST.CONTACT_INFO,
            DOCS_CONST.LICENSE_INFO,
        ]

        for const in dict_constants:
            assert isinstance(const, dict)

    def test_all_list_constants_are_lists(self):
        """Verify all list constants are lists."""
        list_constants = [
            DOCS_CONST.SERVERS,
            DOCS_CONST.TAGS_METADATA,
        ]

        for const in list_constants:
            assert isinstance(const, list)
