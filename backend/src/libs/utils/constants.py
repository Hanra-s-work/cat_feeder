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
# FILE: constants.py
# CREATION DATE: 11-10-2025
# LAST Modified: 18:41:7 31-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# Backend server constants and configuration management.
# 
# This module contains all the configuration constants and utility functions
# required to run the CatFeeder server. It manages environment variables,
# TOML configurations, database settings, server configurations, and provides
# helper functions for data manipulation.
# 
# Module-level constants include:
# - Database connection parameters (host, port, user, password, database)
# - Server configurations (workers, timeout, development/production settings)
# - Verification settings (email delays, token sizes)
# - Table names and database schema constants
# - JSON response key constants
# - User data field mappings and indices
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the file in charge of containing the constants that run the server.
# // AR
# +==== END CatFeeder =================+
"""

import re
from typing import List, Tuple, Any, Dict
from pathlib import Path

from display_tty import Disp, initialise_logger

from ..config import TOMLLoader, EnvLoader, refresh_debug

IDISP: Disp = initialise_logger("Constants", False)


# Environement initialisation
ENV: EnvLoader = EnvLoader()

# toml config file
TOML: TOMLLoader = TOMLLoader()

# Base directory
ROOT_DIRECTORY: Path = Path(__file__).parent.parent.parent.parent

# Assets directory
ASSETS_DIRECTORY: Path = ROOT_DIRECTORY / "assets"

# Enable debugging for the functions in the constants file.
DEBUG: bool = refresh_debug(False)

# Server oauth variables
REDIRECT_URI = ENV.get_environment_variable("REDIRECT_URI")

# Database management
DB_HOST = ENV.get_environment_variable("DB_HOST")
DB_PORT_RAW = ENV.get_environment_variable("DB_PORT")
if not DB_PORT_RAW.isdigit():
    raise TypeError("Expected a number for the database port")
DB_PORT = int(DB_PORT_RAW)
DB_USER = ENV.get_environment_variable("DB_USER")
DB_PASSWORD = ENV.get_environment_variable("DB_PASSWORD")
DB_DATABASE = ENV.get_environment_variable("DB_DATABASE")

# TOML variables
# |- Server configurations
SERVER_WORKERS = TOML.get_toml_variable(
    "Server_configuration", "workers", None
)
SERVER_LIFESPAN = TOML.get_toml_variable(
    "Server_configuration", "lifespan", "auto"
)
SERVER_TIMEOUT_KEEP_ALIVE = TOML.get_toml_variable(
    "Server_configuration", "timeout_keep_alive", 30
)

# |- Server configuration -> Status codes
SUCCESS = int(TOML.get_toml_variable(
    "Server_configuration.status_codes", "success", 0
))
ERROR = int(TOML.get_toml_variable(
    "Server_configuration.status_codes", "error", -84
))


# |- Server configuration -> development
SERVER_DEV_RELOAD = TOML.get_toml_variable(
    "Server_configuration.development", "reload", False
)
SERVER_DEV_RELOAD_DIRS = TOML.get_toml_variable(
    "Server_configuration.development", "reload_dirs", None
)
SERVER_DEV_LOG_LEVEL = TOML.get_toml_variable(
    "Server_configuration.development", "log_level", "info"
)
SERVER_DEV_USE_COLOURS = TOML.get_toml_variable(
    "Server_configuration.development", "use_colours", True
)

# |- Server configuration -> production
SERVER_PROD_PROXY_HEADERS = TOML.get_toml_variable(
    "Server_configuration.production", "proxy_headers", True
)
SERVER_PROD_FORWARDED_ALLOW_IPS = TOML.get_toml_variable(
    "Server_configuration.production", "forwarded_allow_ips", None
)

# |- Server configuration -> database settings
DATABASE_POOL_NAME = TOML.get_toml_variable(
    "Server_configuration.database", "pool_name", None
)
DATABASE_MAX_POOL_CONNECTIONS = int(TOML.get_toml_variable(
    "Server_configuration.database", "max_pool_connections", 10
))
DATABASE_RESET_POOL_NODE_CONNECTION = TOML.get_toml_variable(
    "Server_configuration.database", "reset_pool_node_connection", True
)
DATABASE_CONNECTION_TIMEOUT = int(TOML.get_toml_variable(
    "Server_configuration.database", "connection_timeout", 10
))
DATABASE_LOCAL_INFILE = TOML.get_toml_variable(
    "Server_configuration.database", "local_infile", False
)
DATABASE_INIT_COMMAND = TOML.get_toml_variable(
    "Server_configuration.database", "init_command", None
)
DATABASE_DEFAULT_FILE = TOML.get_toml_variable(
    "Server_configuration.database", "default_file", None
)
DATABASE_SSL_KEY = TOML.get_toml_variable(
    "Server_configuration.database", "ssl_key", None
)
DATABASE_SSL_CERT = TOML.get_toml_variable(
    "Server_configuration.database", "ssl_cert", None
)
DATABASE_SSL_CA = TOML.get_toml_variable(
    "Server_configuration.database", "ssl_ca", None
)
DATABASE_SSL_CIPHER = TOML.get_toml_variable(
    "Server_configuration.database", "ssl_cipher", None
)
DATABASE_SSL_VERIFY_CERT = TOML.get_toml_variable(
    "Server_configuration.database", "ssl_verify_cert", False
)
DATABASE_SSL = TOML.get_toml_variable(
    "Server_configuration.database", "ssl", None
)
DATABASE_AUTOCOMMIT = TOML.get_toml_variable(
    "Server_configuration.database", "autocommit", False
)
DATABASE_COLLATION = TOML.get_toml_variable(
    "Server_configuration.database", "collation", "utf8mb4_unicode_ci"
)

# |- Verification
EMAIL_VERIFICATION_DELAY = int(TOML.get_toml_variable(
    "Verification", "email_verification_delay", 120
))
CHECK_TOKEN_SIZE = int(TOML.get_toml_variable(
    "Verification", "check_token_size", 4
))
RANDOM_MIN = int(TOML.get_toml_variable(
    "Verification", "random_min", 100000
))
RANDOM_MAX = int(TOML.get_toml_variable(
    "Verification", "random_max", 999999
))

# |- Services
API_REQUEST_DELAY = int(TOML.get_toml_variable(
    "Services", "api_request_delay", 5
))

# |- Front-end assets
FRONT_END_ASSETS_REFRESH: int = int(TOML.get_toml_variable(
    "Frontend", "asset_cache_refresh_interval", 300
))

# Json default keys
JSON_TITLE: str = "title"
JSON_MESSAGE: str = "msg"
JSON_ERROR: str = "error"
JSON_RESP: str = "resp"
JSON_LOGGED_IN: str = "logged in"
JSON_UID: str = "user_uid"

# Database table names
TAB_PET = "Pet"
TAB_ACCOUNTS = "Users"
TAB_ACTIONS = "Actions"
TAB_SERVICES = "Services"
TAB_CONNECTIONS = "Connections"
TAB_VERIFICATION = "Verification"
TAB_ACTIVE_OAUTHS = "ActiveOauths"
TAB_ACTION_LOGGING = "ActionLoging"
TAB_ACTION_TEMPLATE = "ActionTemplate"
TAB_USER_OAUTH_CONNECTION = "UserOauthConnection"

# Character info config
CHAR_NODE_KEY: str = "node"
CHAR_ACTIVE_KEY: str = "active"
CHAR_NAME_KEY: str = "name"
CHAR_UID_KEY: str = "uid"
CHAR_ID_DEFAULT_INDEX: int = 0


# User info database table
USERNAME_INDEX_DB: int = 1
PASSWORD_INDEX_DB: int = 2
FIRSTNAME_INDEX_DB: int = 3
LASTNAME_INDEX_DB: int = 4
BIRTHDAY_INDEX_DB: int = 5
GENDER_INDEX_DB: int = 7
ROLE_INDEX_DB: int = 10
UD_USERNAME_KEY: str = "username"
UD_FIRSTNAME_KEY: str = "firstname"
UD_LASTNAME_KEY: str = "lastname"
UD_BIRTHDAY_KEY: str = "birthday"
UD_GENDER_KEY: str = "gender"
UD_ROLE_KEY: str = "role"
UD_ADMIN_KEY: str = "admin"
UD_LOGIN_TIME_KEY: str = "login_time"
UD_LOGGED_IN_KEY: str = "logged_in"

# Incoming header variables
REQUEST_TOKEN_KEY = "token"
REQUEST_BEARER_KEY = "authorization"

# Cache loop
THREAD_CACHE_REFRESH_DELAY = 10

# User sql data
UA_TOKEN_LIFESPAN: int = 7200
UA_EMAIL_KEY: str = "email"
UA_LIFESPAN_KEY: str = "lifespan"

# Get user info banned columns (filtered out columns)
USER_INFO_BANNED: List[str] = ["password", "method", "favicon"]
USER_INFO_ADMIN_NODE: str = "admin"

# The path to the server icon
ICON_PATH: str = str(
    ASSETS_DIRECTORY / "icon" / "cat_feeder" / "favicon.ico"
)

# Path to the png version of the icon
PNG_ICON_PATH: str = str(
    ASSETS_DIRECTORY / "icon" / "cat_feeder" / "logo_256x256.png"
)

# Columns to ignore
TABLE_COLUMNS_TO_IGNORE: Tuple[str, ...] = ("id", "creation_date", "edit_date")

TABLE_COLUMNS_TO_IGNORE_USER: Tuple[str, ...] = (
    "id", "creation_date", "edit_date", "last_connection", "deletion_date"
)

# Bucket info
BUCKET_NAME: str = ENV.get_environment_variable("BUCKET_NAME")

# The front-end assets directories
STYLE_DIRECTORY: Path = ASSETS_DIRECTORY / "css"
HTML_DIRECTORY: Path = ASSETS_DIRECTORY / "html"
JS_DIRECTORY: Path = ASSETS_DIRECTORY / "js" / "web"
IMG_DIRECTORY: Path = ASSETS_DIRECTORY / "icon" / "img"

try:
    GOOGLE_SITE_VERIFICATION_CODE: str = ENV.get_environment_variable(
        "GOOGLE_SITE_VERIFICATION_CODE"
    )
except ValueError:
    GOOGLE_SITE_VERIFICATION_CODE = ""


def clean_list(raw_input: List[Any], items: Tuple[Any, ...], disp: Disp) -> List[Any]:
    """Remove specified items from a list if they are present.

    Iterates through the input list and removes all occurrences of items
    specified in the items tuple. Logs debug information for each removal.

    Args:
        raw_input (List[Any]): The list to check and modify.
        items (Tuple[Any, Any]): The items to remove from the list.
        disp (Disp): The logging object for debug output.

    Returns:
        List[Any]: The modified list with specified items removed.
    """
    to_pop = []
    for index, item in enumerate(raw_input):
        if item in items:
            to_pop.append(index)
            disp.log_debug(f"index to pop: {index}, item: {item}")
    max_length = len(to_pop)
    while max_length > 0:
        node = to_pop[max_length-1]
        node_value = raw_input.pop(node)
        disp.log_debug(f"Popped item[{max_length-1}] = {node} -> {node_value}")
        max_length -= 1
    disp.log_debug(f"final list: {raw_input}")
    return raw_input


def clean_dict(raw_input: Dict[str, Any], items: Tuple[Any, ...], disp: Disp) -> Dict[str, Any]:
    """Remove specified keys from a dictionary if they are present.

    Iterates through the input dictionary and removes all keys specified
    in the items tuple. Logs debug information for each removal.

    Args:
        input (Dict[str, Any]): The dictionary to check and modify.
        items (Tuple[Any, Any]): The keys to remove from the dictionary.
        disp (Disp): The logging object for debug output.

    Returns:
        Dict[str, Any]: The modified dictionary with specified keys removed.
    """
    for item in items:
        if item in raw_input:
            disp.log_debug(f"key to pop: {item}, value: {raw_input[item]}")
            raw_input.pop(item)
            disp.log_debug(f"Popped key: {item}")
    disp.log_debug(f"final dictionary: {raw_input}")
    return raw_input


def mask_email_segment(segment: str) -> str:
    """Mask a single email segment, showing first and last character."""
    if len(segment) <= 2:
        if segment:
            return "[...]"
        return ""
    return f"{segment[0]}[...]{segment[-1]}"


def hide_user_email(user_email: str, disp: Disp) -> str:
    """Mask user email for privacy while preserving structure and shape.

    Masks each word/segment separately, showing only first and last character.
    Segments are separated by special characters: . + - @ 

    Args:
        user_email (str): Email address to mask.

    Returns:
        str: Masked email (e.g., t[...]t.m[...]e+r[...]m@g[...]l.c[...]m).
    """

    if "" == user_email:
        disp.log_warning("Got empty email string to mask")
        return "<unknown_email>"

    if "@" not in user_email:
        disp.log_warning(f"Got invalid email format: '{user_email}'")
        return "<invalid_email>"

    disp.log_debug(f"Masking email: {user_email}")

    # Split on special characters but keep them
    segments = re.split(r"([.+\-@])", user_email)
    disp.log_debug(f"Split segments: {segments}")

    # Process each segment
    masked_parts = []
    for segment in segments:
        if not segment:
            # Skip empty segments
            continue

        # Check if segment is a special character
        is_special_char = re.match(r"[.+\-@]", segment)

        if is_special_char:
            # Keep special characters as-is
            disp.log_debug(f"Keeping special character: '{segment}'")
            masked_parts.append(segment)
        else:
            # Mask alphanumeric segments
            masked_segment = mask_email_segment(segment)
            disp.log_debug(f"Masked segment '{segment}' -> '{masked_segment}'")
            masked_parts.append(masked_segment)

    # Join all parts back together
    result = "".join(masked_parts)
    disp.log_debug(f"Final masked email: {result}")
    return result
