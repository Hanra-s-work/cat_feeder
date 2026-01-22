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
# FILE: docs_constants.py
# CREATION DATE: 26-11-2025
# LAST Modified: 14:46:12 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file containing the constants for the documentation handler.
# // AR
# +==== END CatFeeder =================+
"""
from enum import Enum

from display_tty import Disp, initialise_logger

from ..config import EnvLoader, TOMLLoader

IDISP: Disp = initialise_logger("docs_constants", False)

# Environement initialisation
ENV: EnvLoader = EnvLoader()

# toml config file
TOML: TOMLLoader = TOMLLoader()


class DocumentationProvider(str, Enum):
    """Enumeration of available documentation providers.

    Each provider offers a different interface for viewing API documentation.
    Multiple providers can be enabled simultaneously.
    """
    SWAGGER = "swagger"
    REDOC = "redoc"
    RAPIDOC = "rapidoc"
    SCALAR = "scalar"
    ELEMENTS = "elements"
    EDITOR = "editor"
    EXPLORER = "explorer"
    RAPIPDF = "rapipdf"


# OpenAPI configuration
OPENAPI_URL: str = TOML.get_toml_variable(
    "Documentation", "openapi_url", "/openapi.json"
)
OPENAPI_TITLE: str = TOML.get_toml_variable(
    "Documentation", "api_title", "CatFeeder API"
)
OPENAPI_VERSION: str = TOML.get_toml_variable(
    "Documentation", "api_version", "1.0.0"
)
OPENAPI_DESCRIPTION: str = TOML.get_toml_variable(
    "Documentation", "api_description",
    "API documentation for the CatFeeder server"
)

# Contact information
CONTACT_INFO: dict = TOML.get_toml_variable(
    "Documentation.contact", "info", {
        "name": "Asperguide Team",
        "url": "https://github.com/Asperguide",
        "email": "support@asperguide.com",
    }
)

# License information
LICENSE_INFO: dict = TOML.get_toml_variable(
    "Documentation.license", "info", {
        "name": "Proprietary",
        "url": "https://github.com/Asperguide/back-end/blob/prod/LICENSE",
    }
)

# Server information
SERVERS: list = TOML.get_toml_variable(
    "Documentation", "servers", [
        {"url": "http://localhost:5000", "description": "Development server"},
        {"url": "https://api.asperguide.fr", "description": "Production server"},
    ]
)

# Tags metadata for grouping endpoints
TAGS_METADATA: list = TOML.get_toml_variable(
    "Documentation", "tags_metadata", [
        {"name": "Welcome", "description": "Welcome and health check endpoints"},
        {"name": "Authentication",
            "description": "Authentication and authorization operations"},
        {"name": "Users", "description": "User management operations"},
        {"name": "Server", "description": "Server management and control operations"},
        {"name": "Documentation", "description": "API documentation endpoints"},
    ]
)

# Environment variables for enabling/disabling providers
try:
    ENABLE_REDOC: bool = ENV.get_environment_variable(
        "ENABLE_REDOC"
    ).lower() == "true"
except (ValueError, AttributeError):
    ENABLE_REDOC: bool = False
    IDISP.log_debug(
        "ENABLE_REDOC not set, defaulting to False"
    )

try:
    ENABLE_EDITOR: bool = ENV.get_environment_variable(
        "ENABLE_EDITOR"
    ).lower() == "true"
except (ValueError, AttributeError):
    ENABLE_EDITOR: bool = False
    IDISP.log_debug(
        "ENABLE_EDITOR not set, defaulting to False"
    )

try:
    ENABLE_SCALAR: bool = ENV.get_environment_variable(
        "ENABLE_SCALAR"
    ).lower() == "true"
except (ValueError, AttributeError):
    ENABLE_SCALAR: bool = False
    IDISP.log_debug(
        "ENABLE_SCALAR not set, defaulting to False"
    )

try:
    ENABLE_SWAGGER: bool = ENV.get_environment_variable(
        "ENABLE_SWAGGER"
    ).lower() == "true"
except (ValueError, AttributeError):
    ENABLE_SWAGGER: bool = True
    IDISP.log_debug(
        "ENABLE_SWAGGER not set, defaulting to True"
    )

try:
    ENABLE_RAPIDOC: bool = ENV.get_environment_variable(
        "ENABLE_RAPIDOC"
    ).lower() == "true"
except (ValueError, AttributeError):
    ENABLE_RAPIDOC: bool = False
    IDISP.log_debug(
        "ENABLE_RAPIDOC not set, defaulting to False"
    )

try:
    ENABLE_RAPIPDF: bool = ENV.get_environment_variable(
        "ENABLE_RAPIPDF"
    ).lower() == "true"
except (ValueError, AttributeError):
    ENABLE_RAPIPDF: bool = False
    IDISP.log_debug(
        "ENABLE_RAPIPDF not set, defaulting to False"
    )

try:
    ENABLE_EXPLORER: bool = ENV.get_environment_variable(
        "ENABLE_EXPLORER"
    ).lower() == "true"
except (ValueError, AttributeError):
    ENABLE_EXPLORER: bool = False
    IDISP.log_debug(
        "ENABLE_EXPLORER not set, defaulting to False"
    )

try:
    ENABLE_ELEMENTS: bool = ENV.get_environment_variable(
        "ENABLE_ELEMENTS"
    ).lower() == "true"
except (ValueError, AttributeError):
    ENABLE_ELEMENTS: bool = False
    IDISP.log_debug(
        "ENABLE_ELEMENTS not set, defaulting to False"
    )

# Build default providers list based on environment variables
_enabled_providers = []
if ENABLE_SWAGGER:
    _enabled_providers.append(DocumentationProvider.SWAGGER)
if ENABLE_REDOC:
    _enabled_providers.append(DocumentationProvider.REDOC)
if ENABLE_RAPIDOC:
    _enabled_providers.append(DocumentationProvider.RAPIDOC)
if ENABLE_SCALAR:
    _enabled_providers.append(DocumentationProvider.SCALAR)
if ENABLE_EDITOR:
    _enabled_providers.append(DocumentationProvider.EDITOR)
if ENABLE_EXPLORER:
    _enabled_providers.append(DocumentationProvider.EXPLORER)
if ENABLE_RAPIPDF:
    _enabled_providers.append(DocumentationProvider.RAPIPDF)
if ENABLE_ELEMENTS:
    _enabled_providers.append(DocumentationProvider.ELEMENTS)

DEFAULT_PROVIDERS: tuple[DocumentationProvider, ...] = tuple(
    _enabled_providers)

# CDN versions from TOML configuration
RAPIDOC_CDN_VERSION: str = TOML.get_toml_variable(
    "Documentation.cdn_versions", "rapidoc", "9.3.4"
)
SCALAR_CDN_VERSION: str = TOML.get_toml_variable(
    "Documentation.cdn_versions", "scalar", "1.24.0"
)
ELEMENTS_CDN_VERSION: str = TOML.get_toml_variable(
    "Documentation.cdn_versions", "elements", "8.4.7"
)
EDITOR_CDN_VERSION: str = TOML.get_toml_variable(
    "Documentation.cdn_versions", "editor", "5.0.0"
)
EXPLORER_CDN_VERSION: str = TOML.get_toml_variable(
    "Documentation.cdn_versions", "explorer", "0.0.58"
)
RAPIPDF_CDN_VERSION: str = TOML.get_toml_variable(
    "Documentation.cdn_versions", "rapipdf", "2.2.1"
)

# OAuth2 configuration for documentation
OAUTH2_REDIRECT_URL: str = TOML.get_toml_variable(
    "Documentation", "oauth2_redirect_url", "/docs/oauth2-redirect"
)
ENABLE_OAUTH2_DOCS: bool = TOML.get_toml_variable(
    "Documentation", "enable_oauth2", False
)

# OAuth2 scopes for API documentation (from TOML or defaults)
_DEFAULT_OAUTH2_SCOPES: dict[str, str] = {
    "read": "Read access to API resources",
    "write": "Write access to API resources",
    "admin": "Administrative access to API resources",
}
OAUTH2_SCOPES: dict[str, str] = TOML.get_toml_variable(
    "Documentation", "oauth2_scopes", _DEFAULT_OAUTH2_SCOPES
)

# OAuth2 URLs from environment variables (sensitive data)
try:
    OAUTH2_AUTHORIZATION_URL: str = ENV.get_environment_variable(
        "DOCS_OAUTH2_AUTHORIZATION_URL"
    )
except ValueError:
    OAUTH2_AUTHORIZATION_URL: str = ""
    IDISP.log_debug(
        "DOCS_OAUTH2_AUTHORIZATION_URL not set in environment"
    )

try:
    OAUTH2_TOKEN_URL: str = ENV.get_environment_variable(
        "DOCS_OAUTH2_TOKEN_URL"
    )
except ValueError:
    OAUTH2_TOKEN_URL: str = ""
    IDISP.log_debug(
        "DOCS_OAUTH2_TOKEN_URL not set in environment"
    )
