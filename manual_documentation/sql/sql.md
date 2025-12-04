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
-- FILE: sql.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 14:1:22 02-12-2025
-- DESCRIPTION: 
-- This is the project in charge of making the connected cat feeder project work.
-- /STOP
-- COPYRIGHT: (c) Cat Feeder
-- PURPOSE: The overview of the SQL module.
-- // AR
-- +==== END CatFeeder =================+
-->
# SQL Module

## Overview

The **sql** module provides a high-level interface for database operations with **MySQL**, featuring connection pooling, Redis-backed caching, query sanitization, and time manipulation utilities.

**Location**: `backend/src/libs/sql/`

**Key Files**:

- `sql_manager.py` - Main SQL facade class
- `sql_connections.py` - Connection pool management
- `sql_cache_orchestrator.py` - Caching layer orchestration
- `sql_query_boilerplates.py` - Query building helpers
- `sql_time_manipulation.py` - SQL datetime conversions
- `sql_sanitisation_functions.py` - SQL injection prevention
- `sql_injection.py` - Injection detection
- `sql_redis_cache_rebinds.py` - Redis cache integration
- `sql_constants.py` - SQL-related constants

## Purpose

1. **Database Abstraction**: High-level API for common database operations
2. **Connection Pooling**: Efficient connection reuse and management
3. **Caching Layer**: Redis-backed query result caching with TTL
4. **Query Safety**: SQL injection detection and sanitization
5. **Time Handling**: Conversion between Python datetime and SQL timestamps
6. **Performance**: Reduced database load through intelligent caching

## Architecture

@startuml{sql_architecture.puml}
@enduml

## SQL Class: Main Interface

### Overview

`SQL` is the primary entry point for database operations. It uses `FinalClass` metaclass (not `FinalSingleton`), meaning multiple instances can exist but it cannot be inherited.

### Initialization

```python
from sql import SQL
from core import RuntimeManager

# Factory method (recommended)
sql = SQL.create(
    url="localhost",
    port=3306,
    username="Cat Feeder",
    password="secure_password",
    db_name="Cat Feeder_db"
)

# Or via RuntimeManager
RuntimeManager.set(SQL, 
    url="localhost",
    port=3306,
    username="Cat Feeder",
    password="secure_password",
    db_name="Cat Feeder_db"
)
sql = RuntimeManager.get(SQL)
```

### Core Operations

#### SELECT Queries

```python
# Get all users
users = sql.get_data_from_table(
    table="users",
    column=["id", "username", "email"],
    where=["active=1"],
    beautify=True  # Returns list of dicts
)
# Result: [{"id": 1, "username": "alice", "email": "alice@example.com"}, ...]

# Get single user
user = sql.get_data_from_table(
    table="users",
    column=["*"],
    where=["id=1"],
    beautify=True
)
```

#### INSERT Operations

```python
# Insert new user
result = sql.insert_data_into_table(
    table="users",
    data=["alice", "alice@example.com", "hashed_password"],
    column=["username", "email", "password_hash"]
)
# Returns: 0 (success) or 84 (error)
```

#### UPDATE Operations

```python
# Update user email
result = sql.update_data_in_table(
    table="users",
    data=["newemail@example.com"],
    column=["email"],
    where=["id=1"]
)
```

#### DELETE Operations

```python
# Delete user
result = sql.delete_data_from_table(
    table="users",
    where=["id=1"]
)
```

#### Existence Checks

```python
# Check if user exists
exists = sql.check_if_data_exists(
    table="users",
    where=["username='alice'"]
)
# Returns: True or False
```

## Connection Management

### Connection Pool

@startuml{sql_connection_pool.puml}
@enduml

### SQLManageConnections

Manages a pool of database connections for efficiency:

```python
class SQLManageConnections:
    def __init__(self, url, port, username, password, db_name):
        self.pool = self._create_pool()
    
    def get_connection(self):
        """Get connection from pool (thread-safe)."""
        return self.pool.get_connection()
    
    def execute_query(self, query, params=None):
        """Execute query using pooled connection."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            conn.close()  # Returns to pool
```

### Pool Configuration

Environment variables for connection pool:

- `SQL_POOL_SIZE`: Maximum pool size (default: 10)
- `SQL_POOL_TIMEOUT`: Connection timeout (default: 30s)
- `SQL_MAX_OVERFLOW`: Extra connections beyond pool_size (default: 5)

## Caching Strategy

### Query Flow with Cache

@startuml{sql_query_flow.puml}
@enduml

### SQLCacheOrchestrator

Coordinates between SQL queries and Redis cache:

```python
class SQLCacheOrchestrator:
    def get_cached_or_fetch(self, table, columns, where, fetcher, ttl):
        # Generate cache key
        cache_key = self._generate_key(table, columns, where)
        
        # Try cache first
        cached = self.redis_cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Cache miss - execute query
        result = fetcher()
        
        # Store in cache
        self.redis_cache.set(cache_key, result, ttl)
        return result
    
    def invalidate_table_cache(self, table):
        """Clear all cache entries for a table."""
        pattern = f"sql:{table}:*"
        self.redis_cache.invalidate(pattern)
```

### Cache TTLs

Default time-to-live values:

```python
default_ttls = {
    "data": 300,        # 5 minutes for table data
    "schema": 3600,     # 1 hour for schema info
    "metadata": 7200,   # 2 hours for metadata
    "count": 60         # 1 minute for row counts
}
```

### Cache Invalidation

```python
# Automatic invalidation on writes
sql.update_data_in_table(...)
# Internally calls: cache_orchestrator.invalidate_table_cache(table)

# Manual invalidation
sql.sql_cache_orchestrator.invalidate_table_cache("users")

# Targeted invalidation
sql.sql_cache_orchestrator.redis_cache.invalidate("sql:users:id=*")
```

## Query Safety

### SQL Injection Prevention

#### Sanitization Functions

```python
from sql.sql_sanitisation_functions import (
    sanitize_column_name,
    sanitize_table_name,
    sanitize_value
)

# Sanitize identifiers
table = sanitize_table_name(user_input_table)
column = sanitize_column_name(user_input_column)

# Sanitize values (use parameterized queries instead when possible)
value = sanitize_value(user_input)
```

#### Injection Detection

```python
from sql.sql_injection import detect_sql_injection

user_input = "'; DROP TABLE users; --"
if detect_sql_injection(user_input):
    raise ValueError("Potential SQL injection detected")
```

#### Parameterized Queries

The SQL module uses parameterized queries internally:

```python
# GOOD - Parameterized (automatic)
sql.get_data_from_table(
    table="users",
    where=[f"username='{username}'"]  # BAD - manual escaping
)

# BETTER - Use sanitization
from sql.sql_sanitisation_functions import sanitize_value
sql.get_data_from_table(
    table="users",
    where=[f"username={sanitize_value(username)}"]
)

# BEST - Let the module handle it
sql.get_data_from_table(
    table="users",
    column=["*"],
    where=["username=?"],  # Placeholder
    params=[username]       # Separate params
)
```

## Time Manipulation

### SQLTimeManipulation

Handles conversion between Python `datetime` and SQL timestamps:

```python
from sql.sql_time_manipulation import SQLTimeManipulation

time_utils = SQLTimeManipulation()

# Python datetime → SQL timestamp
from datetime import datetime
now = datetime.now()
sql_timestamp = time_utils.convert_to_sql_datetime(now)
# Result: "2025-12-02 15:30:45"

# SQL timestamp → Python datetime
sql_time = "2025-12-02 15:30:45"
py_datetime = time_utils.convert_from_sql_datetime(sql_time)

# Get current SQL timestamp
current = time_utils.get_current_sql_timestamp()
```

### Usage in Queries

```python
# Insert with current timestamp
time_utils = sql.sql_time_manipulation
timestamp = time_utils.get_current_sql_timestamp()

sql.insert_data_into_table(
    table="events",
    data=["user_login", timestamp],
    column=["event_type", "created_at"]
)
```

## Query Boilerplates

### SQLQueryBoilerplates

Provides helper methods for building common SQL queries:

```python
from sql.sql_query_boilerplates import SQLQueryBoilerplates

qb = SQLQueryBoilerplates()

# SELECT query
query = qb.build_select_query(
    table="users",
    columns=["id", "username"],
    where_clauses=["active=1"],
    order_by="created_at DESC",
    limit=10
)
# Result: "SELECT id, username FROM users WHERE active=1 ORDER BY created_at DESC LIMIT 10"

# INSERT query
query = qb.build_insert_query(
    table="users",
    columns=["username", "email"],
    values=["alice", "alice@example.com"]
)

# UPDATE query
query = qb.build_update_query(
    table="users",
    columns=["email"],
    values=["newemail@example.com"],
    where_clauses=["id=1"]
)

# DELETE query
query = qb.build_delete_query(
    table="users",
    where_clauses=["id=1"]
)
```

## Error Handling

### Exception Types

```python
try:
    sql.get_data_from_table(...)
except mysql_connector.Error as e:
    # Database connection/query errors
    print(f"Database error: {e}")
except AttributeError:
    # Connection pool not initialized
    print("SQL not properly initialized")
except RuntimeError as e:
    # Cache orchestrator issues
    print(f"Cache error: {e}")
```

### Return Codes

```python
result = sql.insert_data_into_table(...)
if result == sql.success:  # 0
    print("Insert successful")
else:  # sql.error = 84
    print("Insert failed")
```

## Performance Optimization

### Best Practices

#### 1. Use Caching for Repeated Queries

```python
# First call - hits database
users = sql.get_data_from_table(table="users", column=["*"], where=[])

# Subsequent calls within TTL - from cache
users = sql.get_data_from_table(table="users", column=["*"], where=[])
```

#### 2. Limit Result Sets

```python
# BAD - fetches all rows
all_users = sql.get_data_from_table(table="users", column=["*"])

# GOOD - limit results
recent_users = sql.get_data_from_table(
    table="users",
    column=["*"],
    where=["created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)"]
)
```

#### 3. Use Specific Columns

```python
# BAD - fetches all columns
users = sql.get_data_from_table(table="users", column=["*"])

# GOOD - only needed columns
users = sql.get_data_from_table(
    table="users",
    column=["id", "username"]
)
```

#### 4. Batch Operations

```python
# BAD - multiple inserts
for user in users:
    sql.insert_data_into_table(table="users", data=[user], column=["username"])

# GOOD - batch insert (if supported)
sql.insert_many_data_into_table(
    table="users",
    data=[[u] for u in users],
    column=["username"]
)
```

## Testing Strategies

### Mocking SQL

```python
import unittest
from unittest.mock import Mock, patch
from sql import SQL

class TestEndpoint(unittest.TestCase):
    def setUp(self):
        # Mock SQL instance
        self.mock_sql = Mock(spec=SQL)
        self.mock_sql.get_data_from_table.return_value = [
            {"id": 1, "username": "alice"}
        ]
        
        # Inject into RuntimeManager
        RuntimeManager.set(SQL, self.mock_sql)
    
    def test_get_users(self):
        sql = RuntimeManager.get(SQL)
        users = sql.get_data_from_table(table="users", column=["*"])
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["username"], "alice")
```

### Integration Testing

```python
def test_sql_integration():
    # Use test database
    sql = SQL.create(
        url="localhost",
        port=3306,
        username="test_user",
        password="test_pass",
        db_name="test_db"
    )
    
    # Insert test data
    result = sql.insert_data_into_table(
        table="test_users",
        data=["testuser"],
        column=["username"]
    )
    assert result == sql.success
    
    # Verify insertion
    users = sql.get_data_from_table(
        table="test_users",
        column=["username"],
        where=["username='testuser'"]
    )
    assert len(users) == 1
    
    # Cleanup
    sql.delete_data_from_table(
        table="test_users",
        where=["username='testuser'"]
    )
```

## Configuration

### Environment Variables

```bash
# Database connection
SQL_HOST=localhost
SQL_PORT=3306
SQL_USERNAME=Cat Feeder
SQL_PASSWORD=secure_password
SQL_DATABASE=Cat Feeder_db

# Connection pool
SQL_POOL_SIZE=10
SQL_POOL_TIMEOUT=30
SQL_MAX_OVERFLOW=5

# Caching
SQL_CACHE_ENABLED=true
SQL_CACHE_DEFAULT_TTL=300
```

### Runtime Configuration

```python
# Enable debug logging
sql.disp.update_disp_debug(True)

# Adjust cache TTLs
sql.sql_cache_orchestrator.redis_cache.default_ttls["data"] = 600
```

## Shutdown

### Graceful Shutdown

```python
class SQL:
    def shutdown(self):
        """Cleanup connections and cache."""
        try:
            # Close all database connections
            if self.sql_manage_connections:
                self.sql_manage_connections.close_all()
            
            # Flush pending cache writes
            if self.sql_cache_orchestrator:
                self.sql_cache_orchestrator.redis_cache.client.save()
            
            self.disp.log_info("SQL shutdown complete")
        except Exception as e:
            self.disp.log_error(f"Error during SQL shutdown: {e}")
```

Usage:

```python
# During server shutdown
sql = RuntimeManager.get(SQL)
sql.shutdown()
```

## Dependencies

**This module depends on**:

- `mysql-connector-python` - MySQL driver
- `redis` - Redis client (via redis module)
- `display_tty` - Logging
- `core` - FinalClass metaclass

**Used by**:

- `server.py` - Initialized during server startup
- All endpoint handlers - Database access
- `boilerplates` - Data validation
- `crons` - Background tasks accessing database

## Related Documentation

- [redis.md](../redis/redis.md) - Caching layer details
- [core.md](../core/core.md) - FinalClass and RuntimeManager
- [server.md](../server/server.md) - Service initialization
- [boilerplates.md](../boilerplates/boilerplates.md) - Request/response handling
