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
# FILE: constants.py
# CREATION DATE: 11-10-2025
# LAST Modified: 16:36:11 30-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: This is the file in charge of containing the constants that run the server.
# // AR
# +==== END AsperBackend =================+
"""

import os
from typing import List, Any, Optional, Dict
from pathlib import Path

import toml
import dotenv
from display_tty import Disp, initialise_logger
IDISP: Disp = initialise_logger("Constants", False)


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


# Base directory
ROOT_DIRECTORY: Path = Path(__file__).parent.parent.parent.parent

# Assets directory
ASSETS_DIRECTORY: Path = ROOT_DIRECTORY / "assets"

# Enable debugging for the functions in the constants file.
IDISP.debug = _get_toml_variable(
    TOML_CONF, "Server_configuration.debug_mode", "debug", False
)


# Server oath variables
REDIRECT_URI = _get_environement_variable(ENV, "REDIRECT_URI")

# Database management
DB_HOST = _get_environement_variable(ENV, "DB_HOST")
DB_PORT_RAW = _get_environement_variable(ENV, "DB_PORT")
if not DB_PORT_RAW.isdigit():
    raise TypeError("Expected a number for the database port")
DB_PORT = int(DB_PORT_RAW)
DB_USER = _get_environement_variable(ENV, "DB_USER")
DB_PASSWORD = _get_environement_variable(ENV, "DB_PASSWORD")
DB_DATABASE = _get_environement_variable(ENV, "DB_DATABASE")

# TOML variables
# |- Server configurations
SERVER_WORKERS = _get_toml_variable(
    TOML_CONF, "Server_configuration", "workers", None
)
SERVER_LIFESPAN = _get_toml_variable(
    TOML_CONF, "Server_configuration", "lifespan", "auto"
)
SERVER_TIMEOUT_KEEP_ALIVE = _get_toml_variable(
    TOML_CONF, "Server_configuration", "timeout_keep_alive", 30
)

# |- Server configuration -> Status codes
SUCCESS = int(_get_toml_variable(
    TOML_CONF, "Server_configuration.status_codes", "success", 0
))
ERROR = int(_get_toml_variable(
    TOML_CONF, "Server_configuration.status_codes", "error", -84
))

# |- Server configuration -> Debug
DEBUG = _get_toml_variable(
    TOML_CONF, "Server_configuration.debug_mode", "debug", False
)

# |- Server configuration -> development
SERVER_DEV_RELOAD = _get_toml_variable(
    TOML_CONF, "Server_configuration.development", "reload", False
)
SERVER_DEV_RELOAD_DIRS = _get_toml_variable(
    TOML_CONF, "Server_configuration.development", "reload_dirs", None
)
SERVER_DEV_LOG_LEVEL = _get_toml_variable(
    TOML_CONF, "Server_configuration.development", "log_level", "info"
)
SERVER_DEV_USE_COLOURS = _get_toml_variable(
    TOML_CONF, "Server_configuration.development", "use_colours", True
)

# |- Server configuration -> production
SERVER_PROD_PROXY_HEADERS = _get_toml_variable(
    TOML_CONF, "Server_configuration.production", "proxy_headers", True
)
SERVER_PROD_FORWARDED_ALLOW_IPS = _get_toml_variable(
    TOML_CONF, "Server_configuration.production", "forwarded_allow_ips", None
)

# |- Server configuration -> database settings
DATABASE_POOL_NAME = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "pool_name", None
)
DATABASE_MAX_POOL_CONNECTIONS = int(_get_toml_variable(
    TOML_CONF, "Server_configuration.database", "max_pool_connections", 10
))
DATABASE_RESET_POOL_NODE_CONNECTION = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "reset_pool_node_connection", True
)
DATABASE_CONNECTION_TIMEOUT = int(_get_toml_variable(
    TOML_CONF, "Server_configuration.database", "connection_timeout", 10
))
DATABASE_LOCAL_INFILE = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "local_infile", False
)
DATABASE_INIT_COMMAND = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "init_command", None
)
DATABASE_DEFAULT_FILE = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "default_file", None
)
DATABASE_SSL_KEY = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "ssl_key", None
)
DATABASE_SSL_CERT = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "ssl_cert", None
)
DATABASE_SSL_CA = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "ssl_ca", None
)
DATABASE_SSL_CIPHER = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "ssl_cipher", None
)
DATABASE_SSL_VERIFY_CERT = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "ssl_verify_cert", False
)
DATABASE_SSL = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "ssl", None
)
DATABASE_AUTOCOMMIT = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "autocommit", False
)
DATABASE_COLLATION = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "collation", "utf8mb4_unicode_ci"
)

# |- Verification
EMAIL_VERIFICATION_DELAY = int(_get_toml_variable(
    TOML_CONF, "Verification", "email_verification_delay", 120
))
CHECK_TOKEN_SIZE = int(_get_toml_variable(
    TOML_CONF,  "Verification", "check_token_size", 4
))
RANDOM_MIN = int(_get_toml_variable(
    TOML_CONF,  "Verification", "random_min", 100000
))
RANDOM_MAX = int(_get_toml_variable(
    TOML_CONF,  "Verification", "random_max", 999999
))

# |- Services
API_REQUEST_DELAY = int(_get_toml_variable(
    TOML_CONF, "Services", "api_request_delay", 5
))

# Json default keys
JSON_TITLE: str = "title"
JSON_MESSAGE: str = "msg"
JSON_ERROR: str = "error"
JSON_RESP: str = "resp"
JSON_LOGGED_IN: str = "logged in"
JSON_UID: str = "user_uid"

# Database table names
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
    ASSETS_DIRECTORY / "icon" / "asperguide" / "favicon.ico"
)

# Path to the png version of the icon
PNG_ICON_PATH: str = str(
    ASSETS_DIRECTORY / "icon" / "asperguide" / "logo_256x256.png"
)
