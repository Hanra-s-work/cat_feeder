"""
Constants for API endpoint decorators.

Provides enums and constants to ensure consistency and reduce spelling mistakes
in decorator usage.
"""

from enum import Enum
from ...http_codes import HttpDataTypes


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


# Use the existing HttpDataTypes instead of creating a new ContentType enum
ContentType = HttpDataTypes


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
    PUBLIC = "Public"
    AUTHENTICATED = "Authenticated"
    ADMIN = "Admin"
    USERS = "Users"
    CAT_MANAGEMENT = "Cat Management"
    OAUTH = "OAuth"
    AUTHENTICATION = "Authentication"
    SYSTEM = "System"
    TESTING = "Testing"


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

# Common content types from HttpDataTypes
JSON_CONTENT = HttpDataTypes.JSON
FORM_CONTENT = HttpDataTypes.FORM
MULTIPART_CONTENT = HttpDataTypes.MULTIPART
TEXT_CONTENT = HttpDataTypes.TEXT
HTML_CONTENT = HttpDataTypes.HTML
BINARY_CONTENT = HttpDataTypes.OCTET_STREAM
