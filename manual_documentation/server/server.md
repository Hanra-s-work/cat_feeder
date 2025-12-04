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
-- FILE: server.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 14:28:7 02-12-2025
-- DESCRIPTION: 
-- This is the project in charge of making the connected cat feeder project work.
-- /STOP
-- COPYRIGHT: (c) Cat Feeder
-- PURPOSE: The Server class of the program, it is in charge of the core steps in the startup process.
-- // AR
-- +==== END CatFeeder =================+
-->
# Server Module

## Overview

The **Server** class is the **main orchestrator** of the Cat Feeder backend system. It acts as the entry point that initializes, coordinates, and manages all backend services through the `RuntimeManager`. The Server class is responsible for the complete lifecycle of the application—from service registration and initialization to graceful shutdown.

**Location**: `backend/src/libs/server.py`

**Design Pattern**: **Orchestrator Pattern** + **Service Locator Pattern**

**Key Responsibilities**:

1. **Service Registration**: Registers all required services with RuntimeManager
2. **Dependency Injection**: Provides configuration parameters to each service
3. **Initialization Orchestration**: Coordinates the startup sequence of all services
4. **Runtime Management**: Maintains references to critical services
5. **Lifecycle Control**: Manages server startup, running state, and graceful shutdown

## Architecture

@startuml{server_architecture.puml}
@enduml

## Service Registration Flow

The Server class follows a **registration-first** approach where all services are registered with the `RuntimeManager` during initialization before any service is actively used.

### Registered Services

The Server registers the following services in order:

1. **RuntimeControl** - Global shutdown coordination
2. **ServerHeaders** - HTTP header management and server metadata
3. **SQL** - Database connection and query management
4. **Bucket** - Object storage interface (S3-compatible)
5. **BackgroundTasks** - Async task queue management
6. **Crons** - Scheduled task execution
7. **ServerManagement** - FastAPI/Uvicorn server lifecycle
8. **BoilerplateResponses** - Standardized HTTP responses
9. **BoilerplateIncoming** - Request validation and parsing
10. **BoilerplateNonHTTP** - Non-HTTP protocol handlers
11. **PathManager** - Route registration and management
12. **EndpointManager** - API endpoint coordination
13. **OAuthAuthentication** - OAuth2 authentication flow
14. **MailManagement** - Email sending and templating
15. **DocumentationHandler** - API documentation generation

### Service Dependencies

```
RuntimeControl (base)
    ├── ServerHeaders
    ├── SQL
    │   └── (used by many services)
    ├── Bucket
    ├── BackgroundTasks
    │   └── Crons
    ├── ServerManagement
    │   ├── PathManager
    │   └── EndpointManager
    ├── BoilerplateResponses
    ├── BoilerplateIncoming
    ├── BoilerplateNonHTTP
    ├── OAuthAuthentication
    ├── MailManagement
    └── DocumentationHandler
```

## Initialization Sequence

@startuml{server_initialization.puml}
@enduml

### Step-by-Step Initialization

#### 1. Constructor (`__init__`)

```python
server = Server(
    host="0.0.0.0",
    port=5000,
    app_name="Cat Feeder",
    debug=False
)
```

**Actions**:

- Initializes logger with debug mode
- Stores configuration parameters (host, port, error/success codes)
- Creates RuntimeManager instance (RI singleton)
- Registers all services with RuntimeManager using `.set()`
- Retrieves shared service instances for quick access
- Each service is instantiated with its required configuration

**Critical Services Retrieved**:

```python
self.server_management_initialised: ServerManagement
self.paths_initialised: PathManager
self.crons_initialised: Crons
self.background_tasks_initialised: BackgroundTasks
self.runtime_control: RuntimeControl
self.sql_connection: SQL
```

#### 2. Main Execution (`main()`)

```python
status = server.main()
```

**Actions**:

1. **Initialize FastAPI Application**:

   ```python
   self.server_management_initialised.initialise_classes()
   ```

   - Creates FastAPI app instance
   - Configures CORS middleware
   - Sets up Uvicorn server configuration
   - Prepares documentation endpoints

2. **Load Default Routes**:

   ```python
   self.paths_initialised.load_default_paths_initialised()
   ```

   - Registers default API endpoints
   - Sets up error handlers
   - Configures static file serving

3. **Inject Routes into FastAPI**:

   ```python
   self.paths_initialised.inject_routes()
   ```

   - Binds all registered routes to FastAPI app
   - Applies middleware to endpoints
   - Validates route configurations

4. **Inject Scheduled Tasks**:

   ```python
   self.crons_initialised.inject_crons()
   ```

   - Registers cron jobs with scheduler
   - Validates cron expressions
   - Prepares background task queue

5. **Start Background Tasks**:

   ```python
   status = self.background_tasks_initialised.safe_start()
   ```

   - Initializes task worker pools
   - Starts cron scheduler
   - Validates all tasks started successfully

6. **Run Server**:

   ```python
   self.runtime_control.server.run()
   ```

   - Starts Uvicorn server
   - Begins accepting HTTP requests
   - Blocks until shutdown signal received

**Error Handling**:

```python
try:
    if not self.runtime_control.server:
        raise RuntimeError("No server to start")
    self.runtime_control.server.run()
except Exception as e:
    self.disp.log_error(f"Error: {e}", "main")
    return self.error
```

## Runtime State Management

### Checking Server Status

```python
if server.is_running():
    print("Server is active")
```

**Implementation**:

```python
def is_running(self) -> bool:
    return self.server_management_initialised.is_server_running()
```

Delegates to `ServerManagement` which checks:

```python
return self.runtime_control.continue_running
```

### Runtime Control Flags

The `RuntimeControl` service maintains global state:

- `continue_running: bool` - Main server loop flag
- `server: Optional[uvicorn.Server]` - Active server instance
- `app: Optional[FastAPI]` - FastAPI application instance
- `config: Optional[uvicorn.Config]` - Server configuration

## Shutdown Sequence

@startuml{server_shutdown.puml}
@enduml

### Graceful Shutdown Process

#### 1. Destructor Triggered (`__del__`)

```python
def __del__(self) -> None:
    self.disp.log_info("The server is shutting down.", "__del__")
    self.stop_server()
```

Called automatically when:

- Server instance goes out of scope
- Process receives termination signal (SIGTERM, SIGINT)
- Application exits normally

#### 2. Stop Server Execution

```python
def stop_server(self) -> None:
    title = "stop_server"
    self.disp.log_info("Stopping server", title)
    
    # Cleanup ServerManagement
    if hasattr(self, "server_management_initialised") and \
       self.server_management_initialised is not None:
        del self.server_management_initialised
    
    # Cleanup Crons
    if hasattr(self, "crons_initialised") and \
       self.crons_initialised is not None:
        del self.crons_initialised
    
    self.disp.log_info("Server stopped", title)
```

#### 3. Cascade Cleanup

**ServerManagement Destructor**:

```python
def __del__(self) -> None:
    if self.is_server_alive():
        del self.database_link  # Close DB connections
        self.runtime_control.continue_running = False
        if self.runtime_control.server is not None:
            self.runtime_control.graceful_shutdown()
            self.runtime_control.server = None
    if self.background_tasks_initialised is not None:
        del self.background_tasks_initialised
```

**Actions**:

1. Closes database connections
2. Sets `continue_running = False`
3. Calls `graceful_shutdown()` on RuntimeControl
4. Stops background tasks and cron jobs
5. Releases all service instances

**Graceful Shutdown Guarantees**:

- Active HTTP requests complete before shutdown
- Background tasks finish current work
- Database transactions are committed or rolled back
- File handles and network connections are closed
- Resources are properly released

## Usage Examples

### Basic Server Startup

```python
from server import Server

# Create server instance
server = Server(
    host="0.0.0.0",
    port=8080,
    app_name="Cat Feeder",
    debug=True
)

# Start server (blocks until shutdown)
exit_code = server.main()

# Exit with appropriate code
sys.exit(exit_code)
```

### Production Configuration

```python
from server import Server

server = Server(
    host="0.0.0.0",
    port=443,  # HTTPS
    app_name="Cat Feeder Production",
    debug=False,
    success=0,
    error=1
)

try:
    status = server.main()
    sys.exit(status)
except KeyboardInterrupt:
    print("Shutdown requested by user")
    sys.exit(0)
except Exception as e:
    print(f"Fatal error: {e}")
    sys.exit(1)
```

### Development with Auto-Reload

```python
from server import Server
import os

# Enable debug mode for detailed logging
server = Server(
    host="127.0.0.1",
    port=5000,
    app_name="Cat Feeder Dev",
    debug=True
)

# Uvicorn will auto-reload on file changes if configured
# (set CONST.SERVER_DEV_RELOAD = True in config)
server.main()
```

### Custom Service Access

```python
from server import Server
from core import RuntimeManager

# Initialize server
server = Server()

# Access any registered service directly
sql = RuntimeManager.get(SQL)
bucket = RuntimeManager.get(Bucket)
path_manager = RuntimeManager.get(PathManager)

# Or use server's cached references
sql_conn = server.sql_connection
paths = server.paths_initialised

# Start server
server.main()
```

### Health Check Integration

```python
from server import Server
import signal
import sys

server = None

def shutdown_handler(signum, frame):
    global server
    print("Shutdown signal received")
    if server:
        server.stop_server()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)

# Create and run server
server = Server(
    host="0.0.0.0",
    port=8000,
    app_name="Cat Feeder"
)

# Check if server is healthy before starting
if server.runtime_control.server is None:
    print("Server initialization failed")
    sys.exit(1)

print("Starting server...")
exit_code = server.main()
sys.exit(exit_code)
```

## Configuration Parameters

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | `str` | `"0.0.0.0"` | Server bind address (0.0.0.0 = all interfaces) |
| `port` | `int` | `5000` | Server listen port |
| `success` | `int` | `0` | Success return code |
| `error` | `int` | `84` | Error return code |
| `app_name` | `str` | `"Cat Feeder"` | Application name for headers/docs |
| `debug` | `bool` | `False` | Enable debug logging and detailed errors |

### Environment-Based Configuration

The Server class reads additional configuration from `CONST` (loaded from environment):

```python
# Database connection
CONST.DB_HOST
CONST.DB_PORT
CONST.DB_USER
CONST.DB_PASSWORD
CONST.DB_DATABASE

# Server settings
CONST.SERVER_LIFESPAN
CONST.SERVER_TIMEOUT_KEEP_ALIVE
CONST.SERVER_WORKERS
CONST.SERVER_DEV_RELOAD
CONST.SERVER_DEV_RELOAD_DIRS
CONST.SERVER_DEV_LOG_LEVEL
CONST.SERVER_DEV_USE_COLOURS
CONST.SERVER_PROD_PROXY_HEADERS
CONST.SERVER_PROD_FORWARDED_ALLOW_IPS
```

## Design Patterns

### 1. Orchestrator Pattern

The Server class acts as a **central orchestrator** that:

- Coordinates initialization of multiple independent services
- Manages inter-service dependencies
- Controls the overall application lifecycle
- Provides a single entry point for the entire system

### 2. Service Locator Pattern

Uses `RuntimeManager` for:

- Centralized service registration
- Lazy service instantiation
- Dependency injection
- Singleton management

### 3. Dependency Injection

Each service receives its dependencies through constructor parameters:

```python
self.runtime_manager.set(
    SQL,
    url=CONST.DB_HOST,
    port=CONST.DB_PORT,
    username=CONST.DB_USER,
    password=CONST.DB_PASSWORD,
    db_name=CONST.DB_DATABASE,
    success=self.success,
    error=self.error,
    debug=self.debug
)
```

### 4. Final Class Pattern

```python
class Server(metaclass=FinalClass):
```

The Server class **cannot be inherited**, ensuring:

- No accidental subclassing
- Consistent behavior across the application
- Clear architectural boundaries

## Error Handling

### Constructor Errors

```python
try:
    server = Server()
except Exception as e:
    print(f"Server initialization failed: {e}")
    sys.exit(1)
```

**Common Errors**:

- Database connection failure (SQL initialization)
- Missing environment variables (CONST values)
- Port already in use
- Invalid configuration parameters

### Runtime Errors

```python
status = server.main()
if status != 0:
    print("Server exited with error")
    sys.exit(status)
```

**Handled Scenarios**:

- Background task startup failure
- Route registration errors
- Server binding issues
- Unexpected exceptions during runtime

### Graceful Degradation

If a non-critical service fails to initialize:

- Server logs the error
- Continues with remaining services
- May operate with reduced functionality

Example:

```python
self.documentation_handler_initialised: Optional[DocumentationHandler] = \
    self.runtime_manager.get_if_exists(DocumentationHandler, None)
```

## Thread Safety

The Server class is **thread-safe** through:

1. **RuntimeManager synchronization**: All service access is protected by per-service locks
2. **Immutable configuration**: Constructor parameters are read-only after initialization
3. **Atomic state changes**: Server state transitions are coordinated through RuntimeControl

**Concurrent Access Pattern**:

```python
# Safe from multiple threads
sql = server.sql_connection  # Always returns same instance
bucket = RuntimeManager.get(Bucket)  # Thread-safe retrieval
```

## Performance Considerations

### Lazy Initialization Benefits

Services are created **only when needed**:

- Faster startup time
- Reduced memory footprint
- Conditional service loading based on configuration

### Caching Strategy

The Server class caches frequently accessed services:

```python
self.sql_connection: SQL = self.runtime_manager.get(SQL)
```

**Benefits**:

- O(1) access time for cached services
- No lock contention on repeated access
- Reduced RuntimeManager lookups

### Background Task Optimization

```python
status = self.background_tasks_initialised.safe_start()
```

Uses thread pools to handle concurrent background operations without blocking the main server loop.

## Testing

### Unit Test Example

```python
import pytest
from server import Server

def test_server_initialization():
    server = Server(
        host="127.0.0.1",
        port=9999,
        debug=True
    )
    assert server.host == "127.0.0.1"
    assert server.port == 9999
    assert server.debug is True

def test_server_service_registration():
    from core import RuntimeManager
    server = Server()
    
    # Verify critical services are registered
    assert RuntimeManager.exists(SQL)
    assert RuntimeManager.exists(Bucket)
    assert RuntimeManager.exists(PathManager)

@pytest.mark.asyncio
async def test_server_startup_shutdown():
    server = Server(port=9998)
    
    # Start in background thread
    import threading
    thread = threading.Thread(target=server.main)
    thread.start()
    
    # Wait for startup
    await asyncio.sleep(2)
    assert server.is_running()
    
    # Trigger shutdown
    server.stop_server()
    thread.join(timeout=5)
    assert not server.is_running()
```

### Integration Test Example

```python
import pytest
from server import Server
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_server_lifecycle():
    server = Server(
        host="127.0.0.1",
        port=8888,
        debug=True
    )
    
    # Start server in background
    import threading
    server_thread = threading.Thread(target=server.main)
    server_thread.start()
    
    # Wait for server to be ready
    await asyncio.sleep(3)
    
    # Make HTTP request
    async with AsyncClient(base_url="http://127.0.0.1:8888") as client:
        response = await client.get("/health")
        assert response.status_code == 200
    
    # Graceful shutdown
    server.stop_server()
    server_thread.join(timeout=10)
```

## Troubleshooting

### Server Won't Start

**Symptoms**: `main()` returns error code immediately

**Checks**:

1. Verify database is accessible
2. Check if port is already in use: `lsof -i :5000`
3. Review logs for service initialization errors
4. Verify all required environment variables are set

### Port Already in Use

```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
server = Server(port=5001)
```

### Background Tasks Not Starting

**Symptoms**: `safe_start()` returns error code

**Checks**:

1. Verify cron expressions are valid
2. Check for circular dependencies in tasks
3. Review task implementation for blocking operations
4. Ensure Redis/queue service is running (if used)

### Graceful Shutdown Hangs

**Symptoms**: Server doesn't stop within expected time

**Causes**:

- Background tasks with infinite loops
- Blocked database connections
- Long-running HTTP requests

**Solution**:

```python
import signal
import sys

def force_shutdown(signum, frame):
    print("Forcing immediate shutdown")
    sys.exit(1)

signal.signal(signal.SIGALRM, force_shutdown)
signal.alarm(30)  # Force quit after 30 seconds

server.stop_server()
```

## Related Documentation

- [Core Module](../core/core.md) - RuntimeManager and service container
- [SQL Module](../sql/sql.md) - Database connection management
- [PathManager Module](../path_manager/path_manager.md) - Route registration
- [EndpointManager Module](../endpoint_manager/endpoint_manager.md) - API coordination
- [Bucket Module](../bucket/bucket.md) - Object storage interface
- [Boilerplates Module](../boilerplates/boilerplates.md) - Request/response standardization

## Summary

The **Server class** is the backbone of the Cat Feeder backend:

✅ **Single Entry Point**: All services initialized through one class  
✅ **Dependency Coordination**: Manages inter-service dependencies automatically  
✅ **Lifecycle Management**: Handles startup, runtime, and graceful shutdown  
✅ **Service Locator**: Leverages RuntimeManager for flexible service access  
✅ **Thread-Safe**: All operations protected by synchronization primitives  
✅ **Error Resilient**: Comprehensive error handling and recovery  
✅ **Production-Ready**: Configurable for development and production environments
