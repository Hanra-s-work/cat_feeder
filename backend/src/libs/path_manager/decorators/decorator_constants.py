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
# FILE: decorator_constants.py
# CREATION DATE: 24-01-2026
# LAST Modified: 23:49:49 24-01-2026
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the file containing the constants for the decorators.
# Constants for API endpoint decorators.
# 
# Provides enums and constants to ensure consistency and reduce spelling mistakes in decorator usage.
# // AR
# +==== END CatFeeder =================+
"""

from enum import Enum
# Fix the import - use the actual DataTypes from http_constants
from ...http_codes.http_constants import DataTypes as ContentType


class AuthScheme(Enum):
    """Enumeration of supported authentication schemes."""
    BEARER = "Bearer"
    BASIC = "Basic"
    DIGEST = "Digest"
    API_KEY = "API-Key"
    OAUTH = "OAuth"
    JWT = "JWT"


class CommonHeaders(Enum):
    """Enumeration of commonly used HTTP headers."""
    AUTHORIZATION = "Authorization"
    API_KEY = "X-API-Key"
    API_TOKEN = "X-API-Token"
    CLIENT_ID = "X-Client-ID"
    CONTENT_TYPE = "Content-Type"
    USER_AGENT = "User-Agent"
    ACCEPT = "Accept"
    ACCEPT_LANGUAGE = "Accept-Language"


class SecurityLevel(Enum):
    """Enumeration of security levels for endpoints."""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    INTERNAL = "internal"


class Environment(Enum):
    """Enumeration of deployment environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    ALL = "all"


class HttpMethod(Enum):
    """Enumeration of HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class TagCategory(Enum):
    """Enumeration of common API endpoint categories for tagging."""
    ADMIN = "Admin"
    USERS = "Users"
    OAUTH = "OAuth"
    PUBLIC = "Public"
    SYSTEM = "System"
    TESTING = "Testing"
    FRONT_END = "Front-End"
    AUTHENTICATED = "Authenticated"
    CAT_MANAGEMENT = "Cat Management"
    AUTHENTICATION = "Authentication"
    FRONT_END_ASSETS = "Front-End Assets"


class StatusCode(Enum):
    """Common HTTP status codes for response documentation."""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503


class QueryParamType(Enum):
    """Common query parameter types."""
    STRING = str
    INTEGER = int
    FLOAT = float
    BOOLEAN = bool
    LIST = list


# Convenience constants for the most common combinations
BEARER_AUTH = AuthScheme.BEARER.value
BASIC_AUTH = AuthScheme.BASIC.value
AUTH_HEADER = CommonHeaders.AUTHORIZATION.value
API_KEY_HEADER = CommonHeaders.API_KEY.value

# Security constants
PUBLIC_SECURITY = SecurityLevel.PUBLIC.value
AUTHENTICATED_SECURITY = SecurityLevel.AUTHENTICATED.value
ADMIN_SECURITY = SecurityLevel.ADMIN.value

# Environment constants
DEV_ENV = Environment.DEVELOPMENT.value
PROD_ENV = Environment.PRODUCTION.value
TEST_ENV = Environment.TESTING.value

# Common tag categories
PUBLIC_TAG = TagCategory.PUBLIC.value
USER_TAG = TagCategory.USERS.value
ADMIN_TAG = TagCategory.ADMIN.value

# Common content types from ContentType
JSON_CONTENT = ContentType.JSON
FORM_CONTENT = ContentType.FORM
MULTIPART_CONTENT = ContentType.MULTIPART
TEXT_CONTENT = ContentType.TEXT
HTML_CONTENT = ContentType.HTML
BINARY_CONTENT = ContentType.OCTET_STREAM
