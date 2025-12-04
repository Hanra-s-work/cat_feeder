<!-- 
-- +==== BEGIN CatFeeder =================+
-- LOGO: 
-- ..........####...####..........
-- ......###.....#.#########......
-- ....##........#.###########....
-- ...#..........#.############...
-- ...#..........#.#####.######...
-- ..#.....##....#.###..#...####..
-- .#.....#.##...#.##..##########.
-- #.....##########....##...######
-- #.....#...##..#.##..####.######
-- .#...##....##.#.##..###..#####.
-- ..#.##......#.#.####...######..
-- ..#...........#.#############..
-- ..#...........#.#############..
-- ...##.........#.############...
-- ......#.......#.#########......
-- .......#......#.########.......
-- .........#####...#####.........
-- /STOP
-- PROJECT: CatFeeder
-- FILE: utils.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 13:57:52 02-12-2025
-- DESCRIPTION: 
-- This is the project in charge of making the connected cat feeder project work.
-- /STOP
-- COPYRIGHT: (c) Cat Feeder
-- PURPOSE: The architecture of the utils folder.
-- // AR
-- +==== END CatFeeder =================+
-->
# Utils Module

## Overview

The utils module provides essential utility classes for server operations including OAuth authentication, password security, and server lifecycle management. These utilities form the foundation for user authentication, security, and server control.

**Location:** `backend/src/libs/utils/`

**Key Components:**

- `OAuthAuthentication` - OAuth provider integration (Google, Facebook, GitHub, etc.)
- `PasswordHandling` - Bcrypt-based password hashing and verification
- `ServerManagement` - Server lifecycle and CORS configuration
- `constants.py` - Environment and TOML configuration loading

## Architecture

See [utils_architecture.puml](utils_architecture.puml) for visual representation.

## Core Classes

### OAuthAuthentication

Manages OAuth 2.0 authentication flows for multiple providers.

**Purpose:** Provides secure third-party authentication integration with automatic token management and renewal.

**Supported Providers:**

- Google
- Facebook
- GitHub
- Microsoft
- LinkedIn
- Twitter/X
- (Configurable via database)

**Key Features:**

- Authorization URL generation with state validation
- Token exchange (authorization code → access token)
- Token refresh and renewal
- User information retrieval from providers
- State-based CSRF protection
- Automatic token expiration tracking

**Constructor:**

```python
OAuthAuthentication(
    success: int = 0,
    error: int = 84,
    debug: bool = False
)
```

**Key Methods:**

| Method | Description | Return Type |
|--------|-------------|-------------|
| `_generate_oauth_authorization_url()` | Generate OAuth provider URL | Union[int, str] |
| `_exchange_code_for_token()` | Exchange code for access token | Union[int, dict] |
| `_refresh_oauth_token()` | Refresh expired OAuth token | Union[int, dict] |
| `_get_user_info_from_provider()` | Get user profile from provider | Union[int, dict] |
| `renew_oaths()` | Renew all expiring tokens | None |

**Database Tables Used:**

- `TAB_USER_OAUTH_CONNECTION` - OAuth provider configurations
- `TAB_VERIFICATION` - State tokens for CSRF protection
- `TAB_CONNECTIONS` - User OAuth tokens and refresh tokens

### PasswordHandling

Provides secure password hashing and verification using bcrypt.

**Purpose:** Ensures passwords are never stored in plain text and can be securely verified.

**Key Features:**

- Bcrypt hashing with configurable salt rounds
- Automatic salt generation
- Constant-time password comparison
- Support for string and bytes input
- Secure password verification

**Constructor:**

```python
PasswordHandling(
    error: int = 84,
    success: int = 0,
    debug: bool = False
)
```

**Attributes:**

- `salt_rounds: int = 10` - Bcrypt work factor (higher = more secure but slower)

**Key Methods:**

| Method | Description | Parameters | Return Type |
|--------|-------------|------------|-------------|
| `hash_password()` | Hash a password | `password: Union[str, bytes]` | `str` |
| `check_password()` | Verify password | `password: Union[str, bytes]`, `password_hash: bytes` | `bool` |

**Security Features:**

- Salted hashing (prevents rainbow table attacks)
- Adaptive cost factor (future-proof against hardware improvements)
- Constant-time comparison (prevents timing attacks)

### ServerManagement

Manages server lifecycle, shutdown, and FastAPI application configuration.

**Purpose:** Provides centralized control over server startup, shutdown, and runtime status with graceful handling.

**Key Features:**

- Graceful shutdown with cleanup
- Server status monitoring
- Database connection management
- Background task coordination
- Documentation handler integration
- Response background task scheduling

**Constructor:**

```python
ServerManagement(
    error: int = 84,
    success: int = 0,
    debug: bool = False
)
```

**Key Methods:**

| Method | Description | Return Type |
|--------|-------------|-------------|
| `is_server_alive()` | Check if server is running | bool |
| `is_server_running()` | Alias for `is_server_alive()` | bool |
| `shutdown()` | Gracefully shutdown server | Response |
| `_perform_shutdown()` | Internal shutdown handler | None |

**Shutdown Process:**

1. Schedule shutdown in background task
2. Send response to client
3. Close database connections
4. Stop background schedulers
5. Graceful FastAPI shutdown

## Configuration (constants.py)

Loads environment variables and TOML configuration:

### Environment Variables

Loaded from `.env` file and system environment:

```python
ENV: Dict[str, Optional[str]]  # Combined .env + os.environ
```

**Access Function:**

```python
def _get_environement_variable(
    environement: Dict[str, Optional[str]],
    variable_name: str
) -> str
```

**Common Environment Variables:**

- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - Application secret key
- `REDIRECT_URI` - OAuth redirect URI
- OAuth provider credentials (per provider)

### TOML Configuration

Loaded from `config.toml`:

```python
TOML_CONF: dict  # Loaded TOML configuration
```

**Access Function:**

```python
def _get_toml_variable(
    toml_conf: dict,
    section: str,
    key: str,
    default=None
) -> Any
```

**Configuration Sections:**

- `Server_configuration` - Host, port, debug mode
- `Server_configuration.debug_mode` - Debug flags
- `Database` - Connection settings
- `Crons` - Background task intervals
- `OAuth` - Provider-specific settings

## OAuth Flow

### Authorization Flow

```
1. User clicks "Login with Google"
   ↓
2. _generate_oauth_authorization_url("google")
   - Generates state token
   - Stores in verification table
   - Returns provider authorization URL
   ↓
3. User redirected to Google
   ↓
4. User authorizes application
   ↓
5. Google redirects back with code + state
   ↓
6. _exchange_code_for_token("google", code)
   - Validates state token
   - Exchanges code for access token
   - Stores tokens in database
   ↓
7. _get_user_info_from_provider("google", access_token)
   - Retrieves user profile
   - Returns user data
```

### Token Renewal Flow

```
1. Cron job: renew_oaths() runs periodically
   ↓
2. Query TAB_CONNECTIONS for expiring tokens
   ↓
3. For each expiring token:
   - _refresh_oauth_token(provider, refresh_token)
   - Update access token in database
   - Update expiration timestamp
```

## Usage Examples

### Example 1: Hash Password (Registration)

```python
from backend.src.libs.utils import PasswordHandling

password_handler = PasswordHandling(debug=True)

# User registration
plain_password = "SecureP@ssw0rd123"
hashed_password = password_handler.hash_password(plain_password)

# Store hashed_password in database
database.insert_user(
    username="john_doe",
    password_hash=hashed_password
)
```

### Example 2: Verify Password (Login)

```python
# User login
entered_password = "SecureP@ssw0rd123"
stored_hash = database.get_user_password_hash("john_doe")

if password_handler.check_password(entered_password, stored_hash):
    print("Login successful!")
    # Generate session token
else:
    print("Invalid password")
```

### Example 3: OAuth Authorization URL

```python
from backend.src.libs.utils import OAuthAuthentication

oauth = OAuthAuthentication(debug=True)

@app.get("/auth/google")
def google_login():
    auth_url = oauth._generate_oauth_authorization_url("google")
    
    if isinstance(auth_url, int):
        return HCI.internal_server_error("Failed to generate OAuth URL")
    
    return HCI.see_other(
        content=auth_url,
        content_type="redirect"
    )
```

### Example 4: OAuth Callback Handler

```python
@app.get("/auth/callback")
def oauth_callback(code: str, state: str):
    # Extract provider from state
    provider = state.split(":")[-1]
    
    # Exchange code for token
    token_data = oauth._exchange_code_for_token(provider, code)
    
    if isinstance(token_data, int):
        return HCI.unauthorized("Authentication failed")
    
    # Get user info
    access_token = token_data["access_token"]
    user_info = oauth._get_user_info_from_provider(provider, access_token)
    
    # Create session or login user
    return HCI.ok({"user": user_info})
```

### Example 5: Server Shutdown Endpoint

```python
from backend.src.libs.utils import ServerManagement
from fastapi import BackgroundTasks

server_mgmt = ServerManagement(debug=True)

@app.post("/admin/shutdown")
async def shutdown_server(background_tasks: BackgroundTasks):
    # Verify admin authentication first
    if not is_admin():
        return HCI.forbidden("Admin access required")
    
    return await server_mgmt.shutdown(background_tasks)
```

### Example 6: Check Server Status

```python
@app.get("/health")
def health_check():
    if server_mgmt.is_server_alive():
        return HCI.ok({
            "status": "healthy",
            "uptime": get_uptime(),
            "database": database.is_connected()
        })
    else:
        return HCI.service_unavailable("Server shutting down")
```

### Example 7: Load Configuration

```python
from backend.src.libs.utils.constants import (
    ENV,
    TOML_CONF,
    _get_environement_variable,
    _get_toml_variable
)

# Get environment variable
database_url = _get_environement_variable(ENV, "DATABASE_URL")

# Get TOML variable with default
host = _get_toml_variable(
    TOML_CONF,
    "Server_configuration",
    "host",
    default="0.0.0.0"
)

port = _get_toml_variable(
    TOML_CONF,
    "Server_configuration",
    "port",
    default=5000
)
```

### Example 8: Password with Bytes

```python
# Handle bytes input (from form data)
password_bytes = b"MyPassword123"

# Hash works with both str and bytes
hashed = password_handler.hash_password(password_bytes)

# Verification also works with bytes
is_valid = password_handler.check_password(
    password_bytes,
    hashed.encode("utf-8")
)
```

### Example 9: OAuth Token Renewal (Cron)

```python
from backend.src.libs.crons import Crons

# In Crons.inject_crons()
crons = Crons(debug=True)
crons.inject_crons()

# Automatically calls oauth.renew_oaths() periodically
# Renews tokens expiring soon
```

## Security Considerations

### Password Hashing

**Best Practices:**

1. **Never store plain passwords** - Always hash before storage
2. **Use sufficient salt rounds** - Default 10 is good, increase for higher security
3. **Constant-time comparison** - Bcrypt's `checkpw` prevents timing attacks
4. **Regular updates** - Increase salt rounds as hardware improves

**Work Factor:**

```python
# Current: 10 rounds = ~100ms verification time
salt_rounds = 10

# High security: 12 rounds = ~400ms
salt_rounds = 12

# Balance security vs. user experience
```

### OAuth Security

**Best Practices:**

1. **State validation** - Prevents CSRF attacks
2. **Short-lived state tokens** - Expire verification states quickly
3. **Secure token storage** - Database encryption for sensitive tokens
4. **HTTPS only** - OAuth requires secure connections
5. **Token refresh** - Automatic renewal before expiration
6. **Scope limitation** - Request minimum necessary permissions

**State Token Flow:**

```python
# Generate unique state
state = str(uuid.uuid4())

# Store with expiration
expiration = datetime.now() + timedelta(minutes=10)
database.insert_verification_state(state, expiration)

# Validate on callback
if not database.verify_state(state):
    raise ValueError("Invalid or expired state")
```

### Server Management

**Best Practices:**

1. **Graceful shutdown** - Complete in-flight requests
2. **Background cleanup** - Schedule shutdown after response
3. **Connection cleanup** - Close all database/external connections
4. **Health checks** - Monitor server status
5. **Admin authentication** - Protect shutdown endpoints

## Error Handling

### Password Handling Errors

```python
try:
    hashed = password_handler.hash_password(password)
except TypeError as e:
    # Invalid password type (not str or bytes)
    print(f"Type error: {e}")

try:
    is_valid = password_handler.check_password(password, hash)
except TypeError as e:
    # Invalid hash type
    print(f"Type error: {e}")
```

### OAuth Errors

```python
# Authorization URL generation
auth_url = oauth._generate_oauth_authorization_url("google")
if isinstance(auth_url, int):
    # Returns error code on failure
    return HCI.internal_server_error("OAuth initialization failed")

# Token exchange
token_data = oauth._exchange_code_for_token("google", code)
if isinstance(token_data, int):
    # Invalid code or expired state
    return HCI.unauthorized("Authentication failed")

# User info retrieval
user_info = oauth._get_user_info_from_provider("google", token)
if isinstance(user_info, int):
    # Invalid token or API error
    return HCI.internal_server_error("Failed to fetch user info")
```

### Configuration Errors

```python
try:
    db_url = _get_environement_variable(ENV, "DATABASE_URL")
except ValueError as e:
    # Variable not found
    print(f"Missing environment variable: {e}")

# TOML with default (no exception)
debug = _get_toml_variable(
    TOML_CONF,
    "Server_configuration.debug_mode",
    "debug",
    default=False
)
```

## Best Practices

### Password Handling

1. **Always hash on write** - Before storing in database
2. **Never log passwords** - Even hashed ones
3. **Use check_password()** - Don't compare hashes manually
4. **Handle both types** - Support str and bytes input
5. **Consider password policies** - Minimum length, complexity

### OAuth Authentication

1. **Validate state tokens** - Always check CSRF protection
2. **Clean expired states** - Use cron cleanup tasks
3. **Store refresh tokens** - Enable seamless renewal
4. **Handle provider differences** - Each provider has quirks
5. **Log OAuth events** - Track authentication flow
6. **Implement fallback** - Handle provider downtime

### Server Management

1. **Use background tasks** - For shutdown scheduling
2. **Monitor health** - Regular status checks
3. **Log lifecycle events** - Startup, shutdown, errors
4. **Protect admin endpoints** - Authentication required
5. **Test graceful shutdown** - Ensure cleanup works

### Configuration

1. **Use .env for secrets** - Never commit to version control
2. **Use TOML for structure** - Application configuration
3. **Provide defaults** - Graceful fallback values
4. **Validate on load** - Catch configuration errors early
5. **Document requirements** - Required vs. optional variables

## Dependencies

### OAuthAuthentication

- `requests` - HTTP requests to OAuth providers
- `fastapi` - Request/Response handling
- `display_tty` - Logging
- `backend.src.libs.sql` - Database operations
- `backend.src.libs.server_header` - Response headers
- `backend.src.libs.http_codes` - Response generation
- `backend.src.libs.boilerplates` - Response patterns

### PasswordHandling

- `bcrypt` - Password hashing library
- `display_tty` - Logging

### ServerManagement

- `uvicorn` - ASGI server
- `fastapi` - Web framework, middleware
- `display_tty` - Logging
- `backend.src.libs.sql` - Database management
- `backend.src.libs.crons` - Background tasks
- `backend.src.libs.core` - Runtime control

### Constants

- `toml` - TOML parsing
- `dotenv` - Environment variable loading
- `pathlib` - Path operations

## Related Modules

- [Crons](../crons/crons.md) - Uses OAuth token renewal
- [SQL](../sql/sql.md) - Database operations for OAuth/passwords
- [Server](../server/server.md) - Server lifecycle management
- [Boilerplates](../boilerplates/boilerplates.md) - Response generation
- [Core](../core/core.md) - Runtime management
