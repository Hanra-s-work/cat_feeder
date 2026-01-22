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
# FILE: core_const.py
# CREATION DATE: 13-01-2026
# LAST Modified: 22:16:13 14-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge of containing the settings for the core functionalities of the server.
# // AR
# +==== END CatFeeder =================+
"""

from typing import List
from display_tty import Disp, initialise_logger

from ..config import TOMLLoader, refresh_debug

from ..utils import constants as CONST

# toml config file
TOML: TOMLLoader = TOMLLoader()

# Refresh debug mode based on the latest configuration
IDISP: Disp = initialise_logger("CORE Constants", refresh_debug(CONST.DEBUG))

# The section where the middleware configuration is stored in the toml file
TOML_MIDDLEWARE_SECTION = "Server_configuration.middleware."


# Gzip optimisation parameters
# Minimum size in bytes to apply Gzip compression
GZIP_MINIMUM_SIZE: int = TOML.get_toml_variable(
    f"{TOML_MIDDLEWARE_SECTION}gzip", "minimum_size", 500
)

# Compression level for Gzip (1-9)
GZIP_COMPRESSION_LEVEL: int = TOML.get_toml_variable(
    f"{TOML_MIDDLEWARE_SECTION}gzip", "compression_level", 9
)

# Cors parameters
# List of allowed origins for CORS
CORS_ALLOW_ORIGINS: List[str] = TOML.get_toml_variable(
    f"{TOML_MIDDLEWARE_SECTION}cors", "allow_origins", ["*"]
)

# Whether to allow credentials in CORS
CORS_ALLOW_CREDENTIALS: bool = TOML.get_toml_variable(
    f"{TOML_MIDDLEWARE_SECTION}cors", "allow_credentials", True
)

# List of allowed HTTP methods for CORS
CORS_ALLOW_METHODS: List[str] = TOML.get_toml_variable(
    f"{TOML_MIDDLEWARE_SECTION}cors", "allow_methods", ["*"]
)

# List of allowed headers for CORS
CORS_ALLOW_HEADERS: List[str] = TOML.get_toml_variable(
    f"{TOML_MIDDLEWARE_SECTION}cors", "allow_headers", ["*"]
)

# Https redirection
# Whether to force HTTPS redirection in production
SERVER_PROD_FORCE_HTTPS: bool = TOML.get_toml_variable(
    f"{TOML_MIDDLEWARE_SECTION}https", "force_https", True
)

# Trusted hosts
TRUSTED_HOSTS_LIST: List[str] = TOML.get_toml_variable(
    f"{TOML_MIDDLEWARE_SECTION}trusted_hosts", "host", []
)

if not SERVER_PROD_FORCE_HTTPS:
    LOCAL_HOSTS: List[str] = TOML.get_toml_variable(
        f"{TOML_MIDDLEWARE_SECTION}trusted_hosts", "dev_hosts",
        ["localhost", "127.0.0.1", "::1"]
    )
    TRUSTED_HOSTS_LIST.extend(LOCAL_HOSTS)

IDISP.log_info("Core constants loaded configurations.")
IDISP.log_debug(f"GZIP_MINIMUM_SIZE: {GZIP_MINIMUM_SIZE}")
IDISP.log_debug(f"GZIP_COMPRESSION_LEVEL: {GZIP_COMPRESSION_LEVEL}")
IDISP.log_debug(f"CORS_ALLOW_ORIGINS: {CORS_ALLOW_ORIGINS}")
IDISP.log_debug(f"CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")
IDISP.log_debug(f"CORS_ALLOW_METHODS: {CORS_ALLOW_METHODS}")
IDISP.log_debug(f"CORS_ALLOW_HEADERS: {CORS_ALLOW_HEADERS}")
IDISP.log_debug(f"SERVER_PROD_FORCE_HTTPS: {SERVER_PROD_FORCE_HTTPS}")
IDISP.log_debug(f"TRUSTED_HOSTS_LIST: {TRUSTED_HOSTS_LIST}")
