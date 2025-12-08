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
# FILE: constants.py
# CREATION DATE: 11-10-2025
# LAST Modified: 3:56:22 08-12-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the file in charge of containing the constants that run the server.
# // AR
# +==== END CatFeeder =================+
"""

from typing import List
from pathlib import Path

from display_tty import Disp, initialise_logger

from ..config import TOMLLoader, EnvLoader

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
DEBUG_MODE: bool = TOML.get_toml_variable(
    "Server_configuration.debug_mode", "debug", False
)
ENV.disp.update_disp_debug(DEBUG_MODE)
TOML.disp.update_disp_debug(DEBUG_MODE)
IDISP.update_disp_debug(DEBUG_MODE)


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

# |- Server configuration -> Debug
DEBUG = TOML.get_toml_variable(
    "Server_configuration.debug_mode", "debug", False
)

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
    ASSETS_DIRECTORY / "icon" / "cat_feeder" / "favicon.ico"
)

# Path to the png version of the icon
PNG_ICON_PATH: str = str(
    ASSETS_DIRECTORY / "icon" / "cat_feeder" / "logo_256x256.png"
)
