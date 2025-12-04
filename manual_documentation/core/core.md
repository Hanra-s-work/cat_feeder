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
-- FILE: core.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 15:24:23 02-12-2025
-- DESCRIPTION: 
-- This is the project in charge of making the connected cat feeder project work.
-- /STOP
-- COPYRIGHT: (c) Cat Feeder
-- PURPOSE: The core dependencies of the server.
-- // AR
-- +==== END CatFeeder =================+
-->
# Core Module

## Overview

The **core** module provides the foundational design patterns for the Cat Feeder backend architecture. It implements a **Service Locator Pattern** combined with a **Protected Singleton Pattern** to enable centralized, thread-safe service management.

**Location**: `backend/src/libs/core/`

**Key Files**:

- `runtime_manager.py` - Service container and lazy initialization
- `final_singleton_class.py` - Protected singleton base class
- `final_class.py` - Metaclass to prevent inheritance
- `runtime_controls.py` - Global shutdown coordination

## Purpose

1. **Centralized Service Management**: Single point of access for all backend services
2. **Lazy Initialization**: Services created only when first requested
3. **Thread Safety**: Synchronized access across multiple request handlers
4. **Lifecycle Control**: Coordinated startup, access, and shutdown
5. **Singleton Enforcement**: Prevent accidental multiple instantiations

## Architecture

@startuml{core_architecture.puml}
@enduml

## RuntimeManager: Service Locator

### Overview

`RuntimeManager` acts as a **service container** providing:

- Named service registration
- Lazy instantiation with caching
- Constructor argument forwarding
- Thread-safe access

### API

```python
from core import RuntimeManager
from sql import SQL

# Register and eagerly construct
RuntimeManager.set(SQL, database_url="postgresql://...")

# Lazy retrieval (creates if not exists)
sql = RuntimeManager.get(SQL)

# Check existence
if RuntimeManager.exists(SQL):
    sql = RuntimeManager.get(SQL)

# Get all service instances
services = RuntimeManager.get_all_instances()

# Clear cache (testing only)
RuntimeManager.clear()
```

### Initialization Sequence

@startuml{core_initialization.puml}
@enduml

### Thread Safety

The `RuntimeManager` uses a **lock-per-service** strategy:

```python
_thread_locks: Dict[str, threading.Lock] = {}
```

- **Read operations** (`exists`, cached `get`): Lock-free, O(1)
- **Write operations** (`set`, first `get`): Synchronized with lock
- **No global lock**: Multiple services can initialize concurrently

### Error Handling

```python
# Failed constructions are NOT cached
try:
    sql = RuntimeManager.get(SQL, url="invalid://")
except ConnectionError:
    pass  # Retry is possible

# Next call attempts fresh construction
sql = RuntimeManager.get(SQL, url="valid://")
```

## FinalSingleton: Protected Construction

### Overview

`FinalSingleton` is a **base class** that prevents direct instantiation:

```python
class MyService(FinalSingleton):
    def __init__(self, config: str):
        self.config = config
    
    async def async_init(self):
        # Async initialization (e.g., database connections)
        await self.connect()

# ❌ Direct instantiation raises RuntimeError
service = MyService("config")  # RuntimeError!

# ✅ Must use RuntimeManager
RuntimeManager.set(MyService, "config")
service = RuntimeManager.get(MyService)
```

### Mechanism

```python
class FinalSingleton:
    _instances: Dict[type, Self] = {}
    _lock: threading.RLock = threading.RLock()
    
    def __new__(cls, *args, **kwargs):
        # Check if called by RuntimeManager
        frame = inspect.currentframe()
        caller = frame.f_back.f_code.co_name
        
        if caller not in {"set", "get", "_create_instance"}:
            raise RuntimeError(
                f"{cls.__name__} must be created through RuntimeManager"
            )
        
        # Thread-safe singleton creation
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__new__(cls)
                cls._instances[cls] = instance
            return cls._instances[cls]
```

### Async Initialization

Services requiring async setup implement `async_init()`:

```python
class SQL(FinalSingleton):
    def __init__(self, database_url: str):
        self.url = database_url
        self.engine = None
    
    async def async_init(self):
        """Called automatically by RuntimeManager after construction."""
        self.engine = create_async_engine(self.url)
        await self.engine.connect()
```

`RuntimeManager.get()` automatically calls `async_init()` if defined:

```python
# RuntimeManager internally:
instance = cls(*args, **kwargs)
if hasattr(instance, "async_init"):
    await instance.async_init()
```

## RuntimeControl: Shutdown Coordination

### Overview

`RuntimeControl` provides a **global shutdown signal** that all services can observe:

```python
from core import RuntimeControl

# Signal shutdown (called by server)
RuntimeControl.signal_shutdown()

# Check shutdown status (in service code)
if RuntimeControl.is_shutting_down():
    return  # Stop processing

# Wait for shutdown (in background threads)
RuntimeControl.wait_for_shutdown(timeout=30)
```

### Shutdown Sequence

@startuml{core_shutdown.puml}
@enduml

### Implementation

```python
class RuntimeControl:
    _shutdown_event: threading.Event = threading.Event()
    _lock: threading.Lock = threading.Lock()
    
    @classmethod
    def signal_shutdown(cls) -> None:
        """Signal all services to shut down."""
        with cls._lock:
            cls._shutdown_event.set()
    
    @classmethod
    def is_shutting_down(cls) -> bool:
        """Check if shutdown has been signaled."""
        return cls._shutdown_event.is_set()
    
    @classmethod
    def wait_for_shutdown(cls, timeout: Optional[float] = None) -> bool:
        """Block until shutdown signaled or timeout."""
        return cls._shutdown_event.wait(timeout)
```

### Usage in Services

```python
class BackgroundWorker(FinalSingleton):
    async def run_loop(self):
        while not RuntimeControl.is_shutting_down():
            await self.process_task()
            await asyncio.sleep(1)
        
        # Cleanup
        await self.cleanup()
```

## FinalClass: Inheritance Prevention

### Overview

`FinalClass` is a **metaclass** that prevents inheritance from classes using it:

```python
from core import FinalClass

class CannotInherit(metaclass=FinalClass):
    pass

# ❌ This raises TypeError
class Derived(CannotInherit):
    pass  # TypeError: Cannot inherit from final class 'CannotInherit'
```

### Use Cases

Applied to classes that should never be subclassed:

- Configuration containers
- Utility classes with static methods
- Classes with security-critical behavior

## Design Patterns

### 1. Service Locator Pattern

**Intent**: Centralize service creation and access

**Implementation**: `RuntimeManager`

**Benefits**:

- Decouples service consumers from construction
- Enables lazy initialization
- Simplifies dependency management
- Facilitates testing (mock services)

**Example**:

```python
# In Server.__init__()
RuntimeManager.set(SQL, database_url)
RuntimeManager.set(Redis, redis_url)
RuntimeManager.set(Bucket, s3_config)

# In endpoint handlers
sql = RuntimeManager.get(SQL)
users = await sql.query("SELECT * FROM users")
```

### 2. Protected Singleton Pattern

**Intent**: Enforce single instance through controlled creation

**Implementation**: `FinalSingleton`

**Benefits**:

- Prevents accidental multiple instances
- Centralizes lifecycle management
- Thread-safe by design
- Clear intent (cannot be instantiated directly)

**Example**:

```python
class DatabaseConnection(FinalSingleton):
    def __init__(self, url: str):
        self.url = url
    
    def query(self, sql: str):
        return self.engine.execute(sql)

# Only one instance ever exists
db = RuntimeManager.get(DatabaseConnection, "postgresql://...")
```

### 3. Observer Pattern (Shutdown)

**Intent**: Notify all services of shutdown

**Implementation**: `RuntimeControl`

**Benefits**:

- Coordinated shutdown
- No tight coupling
- Services can cleanup resources
- Background tasks can terminate gracefully

## Performance Characteristics

| Operation | Time Complexity | Thread Safety |
|-----------|----------------|---------------|
| `RuntimeManager.set()` | O(1) | ✅ Locked |
| `RuntimeManager.get()` (cached) | O(1) | ✅ Lock-free |
| `RuntimeManager.get()` (first) | O(1) + init | ✅ Locked |
| `RuntimeManager.exists()` | O(1) | ✅ Lock-free |
| `RuntimeControl.signal_shutdown()` | O(1) | ✅ Locked |
| `RuntimeControl.is_shutting_down()` | O(1) | ✅ Lock-free |

**Memory**: O(n) where n = number of registered services

## Testing Strategies

### Mocking Services

```python
import unittest
from core import RuntimeManager

class MockSQL(FinalSingleton):
    def __init__(self):
        self.data = {"users": []}
    
    def query(self, sql: str):
        return self.data["users"]

class TestEndpoint(unittest.TestCase):
    def setUp(self):
        # Inject mock
        RuntimeManager.set(SQL, MockSQL())
    
    def tearDown(self):
        # Clear cache
        RuntimeManager.clear()
    
    def test_get_users(self):
        sql = RuntimeManager.get(SQL)
        users = sql.query("SELECT * FROM users")
        self.assertEqual(users, [])
```

### Testing Lazy Initialization

```python
def test_lazy_creation():
    # Service not created yet
    assert not RuntimeManager.exists(MyService)
    
    # First access creates it
    svc1 = RuntimeManager.get(MyService, arg="value")
    assert RuntimeManager.exists(MyService)
    
    # Second access returns same instance
    svc2 = RuntimeManager.get(MyService)
    assert svc1 is svc2
```

### Testing Shutdown

```python
async def test_graceful_shutdown():
    # Setup service
    worker = RuntimeManager.get(BackgroundWorker)
    task = asyncio.create_task(worker.run_loop())
    
    # Signal shutdown
    RuntimeControl.signal_shutdown()
    
    # Wait for task to complete
    await asyncio.wait_for(task, timeout=5)
    
    # Verify cleanup
    assert worker.is_cleaned_up
```

## Common Patterns

### Conditional Initialization

```python
# Initialize only if not already exists
if not RuntimeManager.exists(CacheService):
    RuntimeManager.set(CacheService, cache_url)
```

### Service Dependencies

```python
class EndpointManager(FinalSingleton):
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def async_init(self):
        # Depends on PathManager
        self.path_manager = RuntimeManager.get(PathManager)
        await self.register_routes()
```

### Cleanup on Shutdown

```python
class DatabasePool(FinalSingleton):
    async def async_init(self):
        self.pool = await create_pool()
    
    def shutdown(self):
        """Called during server shutdown."""
        if RuntimeControl.is_shutting_down():
            self.pool.close()
```

## Best Practices

### ✅ DO

- Register all services during server initialization
- Use `RuntimeManager.get()` for lazy retrieval
- Implement `async_init()` for async setup
- Implement `shutdown()` for cleanup
- Use `RuntimeControl.is_shutting_down()` in loops

### ❌ DON'T

- Don't instantiate `FinalSingleton` subclasses directly
- Don't call `RuntimeManager.set()` after server starts
- Don't store service references globally (use RuntimeManager)
- Don't forget to implement `shutdown()` for resource cleanup
- Don't create circular dependencies between services

## Dependencies

**This module depends on**:

- `display_tty` (logging)
- `threading` (standard library)
- `asyncio` (standard library)
- `inspect` (standard library)

**Used by**:

- `server.py` - Initializes all services
- `sql.py`, `redis.py`, `bucket.py` - Data layer services
- `endpoint_manager.py` - Application layer
- All service classes - Base class for singletons

## Related Documentation

- [../server/server.md](../server/server.md) - How Server uses RuntimeManager
- [../sql/sql.md](../sql/sql.md) - SQL as FinalSingleton example
- [../redis/redis.md](../redis/redis.md) - Redis as FinalSingleton example
- [../bucket/bucket.md](../bucket/bucket.md) - Bucket as FinalSingleton example
