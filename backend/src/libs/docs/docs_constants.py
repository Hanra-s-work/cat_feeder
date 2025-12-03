""" 
# +==== BEGIN AsperBackend =================+
# LOGO: 
# ..........####...####..........
# ......###.....#.#########......
# ....##........#.###########....
# ...#..........#.############...
# ...#..........#.#####.######...
# ..#.....##....#.###..#...####..
# .#.....#.##...#.##..##########.
# #.....##########....##...######
# #.....#...##..#.##..####.######
# .#...##....##.#.##..###..#####.
# ..#.##......#.#.####...######..
# ..#...........#.#############..
# ..#...........#.#############..
# ...##.........#.############...
# ......#.......#.#########......
# .......#......#.########.......
# .........#####...#####.........
# /STOP
# PROJECT: AsperBackend
# FILE: docs_constants.py
# CREATION DATE: 26-11-2025
# LAST Modified: 7:49:57 27-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: The file containing the constants for the documentation handler.
# // AR
# +==== END AsperBackend =================+
"""
from enum import Enum
from typing import Dict, Optional, Any

import os
import toml
import dotenv
from display_tty import Disp, initialise_logger
IDISP: Disp = initialise_logger("docs_constants", False)

# Environement initialisation
dotenv.load_dotenv(".env")
_DOTENV = dict(dotenv.dotenv_values())
_OS_ENV = dict(os.environ)
ENV = {}
ENV.update(_OS_ENV)
ENV.update(_DOTENV)

# toml config file
TOML_CONF = toml.load("config.toml")


def _get_environement_variable(environement: Dict[str, Optional[str]], variable_name: str) -> str:
    """_summary_
        Get the content of an environement variable.

    Args:
        variable_name (str): _description_

    Returns:
        str: _description_: the value of that variable, otherwise an exception is raised.
    """
    if environement is None:
        raise ValueError(
            "No environement file loaded."
        )
    data = environement.get(variable_name, None)
    if data is None:
        # required for expanding the variable name
        error_msg = f"Variable '{variable_name}' not found in the environement"
        raise ValueError(error_msg)
    return data


def _get_toml_variable(toml_conf: dict, section: str, key: str, default=None) -> Any:
    """
    Get the value of a configuration variable from the TOML file.

    Args:
        toml_conf (dict): The loaded TOML configuration as a dictionary.
        section (str): The section of the TOML file to search in.
        key (str): The key within the section to fetch.
        default: The default value to return if the key is not found. Defaults to None.

    Returns:
        str: The value of the configuration variable, or the default value if the key is not found.

    Raises:
        KeyError: If the section is not found in the TOML configuration.
    """
    try:
        keys = section.split('.')
        current_section = toml_conf

        for k in keys:
            if k in current_section:
                current_section = current_section[k]
            else:
                raise KeyError(
                    f"Section '{section}' not found in TOML configuration."
                )

        if key in current_section:
            msg = f"current_section[{key}] = {current_section[key]} : "
            msg += f"{type(current_section[key])}"
            IDISP.log_debug(msg, "_get_toml_variable")
            if current_section[key] == "none":
                IDISP.log_debug(
                    "The value none has been converted to None.",
                    "_get_toml_variable"
                )
                return None
            return current_section[key]
        if default is None:
            msg = f"Key '{key}' not found in section '{section}' "
            msg += "of TOML configuration."
            raise KeyError(msg)
        return default

    except KeyError as e:
        IDISP.log_warning(f"{e}", "_get_toml_variable")
        return default


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
OPENAPI_URL: str = _get_toml_variable(
    TOML_CONF, "Documentation", "openapi_url", "/openapi.json"
)
OPENAPI_TITLE: str = _get_toml_variable(
    TOML_CONF, "Documentation", "api_title", "AsperBackend API"
)
OPENAPI_VERSION: str = _get_toml_variable(
    TOML_CONF, "Documentation", "api_version", "1.0.0"
)
OPENAPI_DESCRIPTION: str = _get_toml_variable(
    TOML_CONF, "Documentation", "api_description",
    "API documentation for the AsperBackend server"
)

# Contact information
CONTACT_INFO: dict = _get_toml_variable(
    TOML_CONF, "Documentation.contact", "info", {
        "name": "Asperguide Team",
        "url": "https://github.com/Asperguide",
        "email": "support@asperguide.com",
    }
)

# License information
LICENSE_INFO: dict = _get_toml_variable(
    TOML_CONF, "Documentation.license", "info", {
        "name": "Proprietary",
        "url": "https://github.com/Asperguide/back-end/blob/prod/LICENSE",
    }
)

# Server information
SERVERS: list = _get_toml_variable(
    TOML_CONF, "Documentation", "servers", [
        {"url": "http://localhost:5000", "description": "Development server"},
        {"url": "https://api.asperguide.fr", "description": "Production server"},
    ]
)

# Tags metadata for grouping endpoints
TAGS_METADATA: list = _get_toml_variable(
    TOML_CONF, "Documentation", "tags_metadata", [
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
    ENABLE_REDOC: bool = _get_environement_variable(
        ENV, "ENABLE_REDOC").lower() == "true"
except (ValueError, AttributeError):
    ENABLE_REDOC: bool = False
    IDISP.log_debug(
        "ENABLE_REDOC not set, defaulting to False", "docs_constants")

try:
    ENABLE_EDITOR: bool = _get_environement_variable(
        ENV, "ENABLE_EDITOR").lower() == "true"
except (ValueError, AttributeError):
    ENABLE_EDITOR: bool = False
    IDISP.log_debug(
        "ENABLE_EDITOR not set, defaulting to False", "docs_constants")

try:
    ENABLE_SCALAR: bool = _get_environement_variable(
        ENV, "ENABLE_SCALAR").lower() == "true"
except (ValueError, AttributeError):
    ENABLE_SCALAR: bool = False
    IDISP.log_debug(
        "ENABLE_SCALAR not set, defaulting to False", "docs_constants")

try:
    ENABLE_SWAGGER: bool = _get_environement_variable(
        ENV, "ENABLE_SWAGGER").lower() == "true"
except (ValueError, AttributeError):
    ENABLE_SWAGGER: bool = True
    IDISP.log_debug(
        "ENABLE_SWAGGER not set, defaulting to True", "docs_constants")

try:
    ENABLE_RAPIDOC: bool = _get_environement_variable(
        ENV, "ENABLE_RAPIDOC").lower() == "true"
except (ValueError, AttributeError):
    ENABLE_RAPIDOC: bool = False
    IDISP.log_debug(
        "ENABLE_RAPIDOC not set, defaulting to False", "docs_constants")

try:
    ENABLE_RAPIPDF: bool = _get_environement_variable(
        ENV, "ENABLE_RAPIPDF").lower() == "true"
except (ValueError, AttributeError):
    ENABLE_RAPIPDF: bool = False
    IDISP.log_debug(
        "ENABLE_RAPIPDF not set, defaulting to False", "docs_constants")

try:
    ENABLE_EXPLORER: bool = _get_environement_variable(
        ENV, "ENABLE_EXPLORER").lower() == "true"
except (ValueError, AttributeError):
    ENABLE_EXPLORER: bool = False
    IDISP.log_debug(
        "ENABLE_EXPLORER not set, defaulting to False", "docs_constants")

try:
    ENABLE_ELEMENTS: bool = _get_environement_variable(
        ENV, "ENABLE_ELEMENTS").lower() == "true"
except (ValueError, AttributeError):
    ENABLE_ELEMENTS: bool = False
    IDISP.log_debug(
        "ENABLE_ELEMENTS not set, defaulting to False", "docs_constants")

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
RAPIDOC_CDN_VERSION: str = _get_toml_variable(
    TOML_CONF, "Documentation.cdn_versions", "rapidoc", "9.3.4"
)
SCALAR_CDN_VERSION: str = _get_toml_variable(
    TOML_CONF, "Documentation.cdn_versions", "scalar", "1.24.0"
)
ELEMENTS_CDN_VERSION: str = _get_toml_variable(
    TOML_CONF, "Documentation.cdn_versions", "elements", "8.4.7"
)
EDITOR_CDN_VERSION: str = _get_toml_variable(
    TOML_CONF, "Documentation.cdn_versions", "editor", "5.0.0"
)
EXPLORER_CDN_VERSION: str = _get_toml_variable(
    TOML_CONF, "Documentation.cdn_versions", "explorer", "0.0.58"
)
RAPIPDF_CDN_VERSION: str = _get_toml_variable(
    TOML_CONF, "Documentation.cdn_versions", "rapipdf", "2.2.1"
)

# OAuth2 configuration for documentation
OAUTH2_REDIRECT_URL: str = _get_toml_variable(
    TOML_CONF, "Documentation", "oauth2_redirect_url", "/docs/oauth2-redirect"
)
ENABLE_OAUTH2_DOCS: bool = _get_toml_variable(
    TOML_CONF, "Documentation", "enable_oauth2", False
)

# OAuth2 scopes for API documentation (from TOML or defaults)
_DEFAULT_OAUTH2_SCOPES: dict[str, str] = {
    "read": "Read access to API resources",
    "write": "Write access to API resources",
    "admin": "Administrative access to API resources",
}
OAUTH2_SCOPES: dict[str, str] = _get_toml_variable(
    TOML_CONF, "Documentation", "oauth2_scopes", _DEFAULT_OAUTH2_SCOPES
)

# OAuth2 URLs from environment variables (sensitive data)
try:
    OAUTH2_AUTHORIZATION_URL: str = _get_environement_variable(
        ENV, "DOCS_OAUTH2_AUTHORIZATION_URL")
except ValueError:
    OAUTH2_AUTHORIZATION_URL: str = ""
    IDISP.log_debug(
        "DOCS_OAUTH2_AUTHORIZATION_URL not set in environment", "docs_constants")

try:
    OAUTH2_TOKEN_URL: str = _get_environement_variable(
        ENV, "DOCS_OAUTH2_TOKEN_URL")
except ValueError:
    OAUTH2_TOKEN_URL: str = ""
    IDISP.log_debug(
        "DOCS_OAUTH2_TOKEN_URL not set in environment", "docs_constants")
