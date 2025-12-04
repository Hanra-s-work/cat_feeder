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
-- FILE: redis.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 14:29:44 02-12-2025
-- DESCRIPTION: 
-- This is the project in charge of making the connected cat feeder project work.
-- /STOP
-- COPYRIGHT: (c) Cat Feeder
-- PURPOSE: The structure of the redis module.
-- // AR
-- +==== END CatFeeder =================+
-->
# Redis Module

## Overview

The **redis** module provides a high-level caching facade for SQL query results and general key-value storage, using **Redis** as the backend. It features JSON serialization, deterministic key generation, TTL-based expiration, and pattern-based invalidation.

**Location**: `backend/src/libs/redis/`

**Key Files**:

- `redis_instance.py` - Main RedisCaching class
- `redis_args.py` - Configuration from environment
- `redis_constants.py` - Redis-related constants

## Purpose

1. **Query Result Caching**: Cache SQL query results to reduce database load
2. **Key-Value Storage**: General-purpose caching for any serializable data
3. **Automatic Invalidation**: Pattern-based cache clearing on writes
4. **TTL Management**: Time-based cache expiration
5. **Connection Management**: Unix socket or TCP connection to Redis server

## Architecture

@startuml{redis_architecture.puml}
@enduml

## RedisCaching Class

### Overview

`RedisCaching` provides a high-level interface for caching with Redis. It handles:

- JSON serialization/deserialization
- Deterministic key generation
- TTL management
- Pattern-based invalidation

### Initialization

```python
from redis import RedisCaching

# Default initialization (uses environment variables)
cache = RedisCaching()

# Access Redis client directly if needed
cache.client.ping()  # Test connection
```

### Configuration

Environment variables:

```bash
# Unix socket (Linux/Mac)
REDIS_SOCKET_PATH=/var/run/redis/redis.sock

# Password (optional)
REDIS_PASSWORD=your_redis_password

# Decode responses to str (default: true)
REDIS_DECODE_RESPONSES=true
```

Python configuration:

```python
from redis.redis_args import RedisArgs

# Load from environment
args = RedisArgs.from_env()
print(args.socket_path)  # /var/run/redis/redis.sock
print(args.password)      # your_redis_password

# Convert to redis-py kwargs
kwargs = args.to_redis_kwargs()
# {"unix_socket_path": "/var/run/redis/redis.sock", "password": "...", "decode_responses": True}
```

## Caching Patterns

### Read-Through Caching

@startuml{redis_caching_flow.puml}
@enduml

#### Basic Usage

```python
from redis import RedisCaching

cache = RedisCaching()

# Cache a SQL query result
def fetch_users():
    """Expensive database query."""
    sql = RuntimeManager.get(SQL)
    return sql.get_data_from_table(
        table="users",
        column=["id", "username", "email"]
    )

# First call - database hit
users = cache.get_data_from_table(
    table="users",
    column=["id", "username", "email"],
    where=[],
    beautify=True,
    fetcher=fetch_users,
    ttl_seconds=300  # 5 minutes
)

# Subsequent calls within TTL - cache hit
users = cache.get_data_from_table(
    table="users",
    column=["id", "username", "email"],
    where=[],
    beautify=True,
    fetcher=fetch_users,
    ttl_seconds=300
)
```

### Write-Through Caching

```python
# Update data and invalidate cache
result = cache.update_data_in_table(
    table="users",
    data=["newemail@example.com"],
    column=["email"],
    where=["id=1"],
    writer=lambda: sql.update_data_in_table(
        table="users",
        data=["newemail@example.com"],
        column=["email"],
        where=["id=1"]
    )
)
# Automatically invalidates all "sql:users:*" keys
```

## Key Management

### Key Generation

Keys follow a deterministic pattern:

```text
{namespace}:{category}:{identifier}:{param_hash}
```

Examples:

```text
sql:users:data:a3f7c21e  # Query: SELECT * FROM users WHERE active=1
sql:schema:version:       # Database version
sql:users:count:          # Row count for users table
```

### Key Generation Algorithm

```python
import hashlib
import json

def build_cache_key(table, columns, where):
    # Normalize parameters
    params = {
        "table": table,
        "columns": sorted(columns),  # Sort for determinism
        "where": sorted(where)        # Sort for determinism
    }
    
    # JSON serialize (sorted keys)
    params_json = json.dumps(params, sort_keys=True)
    
    # SHA-256 hash (first 8 hex characters)
    param_hash = hashlib.sha256(params_json.encode()).hexdigest()[:8]
    
    # Build key
    return f"sql:{table}:data:{param_hash}"
```

### Manual Key Operations

```python
# Set a value
cache.set("my_key", {"data": "value"}, ttl=600)

# Get a value
value = cache.get("my_key")

# Delete a value
cache.delete("my_key")

# Check if exists
exists = cache.client.exists("my_key")
```

## Cache Invalidation

@startuml{redis_invalidation.puml}
@enduml

### Pattern-Based Invalidation

```python
# Invalidate all user-related cache
deleted_count = cache.invalidate("sql:users:*")
print(f"Deleted {deleted_count} keys")

# Invalidate specific query pattern
cache.invalidate("sql:users:data:*")

# Invalidate all SQL cache
cache.invalidate("sql:*")
```

### Automatic Invalidation

Cache is automatically invalidated on writes:

```python
# This automatically clears "sql:users:*"
cache.update_data_in_table(
    table="users",
    data=["new_value"],
    column=["column_name"],
    where=["id=1"],
    writer=update_function
)
```

### Manual Table Invalidation

```python
# Clear all cache for a specific table
from sql.sql_cache_orchestrator import SQLCacheOrchestrator

orchestrator = SQLCacheOrchestrator(sql_instance, cache_instance)
orchestrator.invalidate_table_cache("users")
```

## TTL Management

### Default TTLs

```python
default_ttls = {
    "data": 300,        # 5 minutes - table data
    "schema": 3600,     # 1 hour - schema information
    "metadata": 7200,   # 2 hours - database metadata
    "count": 60         # 1 minute - row counts
}
```

### Custom TTL

```python
# Short TTL for frequently changing data
recent_orders = cache.get_data_from_table(
    table="orders",
    column=["*"],
    where=["created_at > NOW() - INTERVAL 1 HOUR"],
    fetcher=fetch_recent_orders,
    ttl_seconds=30  # 30 seconds
)

# Long TTL for static data
countries = cache.get_data_from_table(
    table="countries",
    column=["*"],
    where=[],
    fetcher=fetch_countries,
    ttl_seconds=86400  # 24 hours
)

# No expiration (use carefully!)
config = cache.set("app_config", config_data, ttl=None)
```

### TTL Inspection

```python
# Check remaining TTL
ttl_seconds = cache.client.ttl("sql:users:data:a3f7c21e")
if ttl_seconds == -1:
    print("Key exists but has no expiration")
elif ttl_seconds == -2:
    print("Key does not exist")
else:
    print(f"Key expires in {ttl_seconds} seconds")
```

## Error Handling

### Connection Errors

```python
from redis.exceptions import ConnectionError, TimeoutError

try:
    cache = RedisCaching()
    cache.set("key", "value")
except ConnectionError:
    print("Cannot connect to Redis server")
    # Fallback to direct database access
except TimeoutError:
    print("Redis operation timed out")
```

### Graceful Degradation

```python
def get_users_with_fallback():
    """Get users with Redis fallback."""
    cache = RedisCaching()
    
    try:
        # Try cache first
        return cache.get_data_from_table(
            table="users",
            column=["*"],
            fetcher=fetch_users,
            ttl_seconds=300
        )
    except Exception as e:
        print(f"Cache error: {e}, falling back to database")
        # Direct database access
        return fetch_users()
```

### Health Check

```python
def check_redis_health():
    """Check if Redis is accessible."""
    try:
        cache = RedisCaching()
        return cache.check_cache_health()
    except Exception:
        return False

if not check_redis_health():
    print("WARNING: Redis is not available")
```

## Performance Optimization

### Batch Operations

```python
# Batch get (using pipeline)
pipe = cache.client.pipeline()
keys = ["key1", "key2", "key3"]
for key in keys:
    pipe.get(key)
results = pipe.execute()

# Batch set (using pipeline)
pipe = cache.client.pipeline()
for key, value in data_dict.items():
    pipe.set(key, json.dumps(value), ex=300)
pipe.execute()
```

### Compression for Large Values

```python
import gzip
import json

def set_compressed(cache, key, value, ttl):
    """Store compressed JSON."""
    json_str = json.dumps(value)
    compressed = gzip.compress(json_str.encode())
    cache.client.set(key, compressed, ex=ttl)

def get_compressed(cache, key):
    """Retrieve compressed JSON."""
    compressed = cache.client.get(key)
    if compressed:
        decompressed = gzip.decompress(compressed)
        return json.loads(decompressed)
    return None
```

### Connection Pooling

Redis-py automatically uses connection pooling:

```python
# Connection pool is created automatically
cache = RedisCaching()

# Pool parameters (if needed custom configuration)
import redis
pool = redis.ConnectionPool(
    unix_socket_path="/var/run/redis/redis.sock",
    max_connections=50,
    decode_responses=True
)
client = redis.Redis(connection_pool=pool)
```

## Testing Strategies

### Mocking Redis

```python
import unittest
from unittest.mock import Mock, patch
from redis import RedisCaching

class TestCaching(unittest.TestCase):
    def setUp(self):
        # Mock Redis client
        self.mock_redis = Mock()
        self.mock_redis.get.return_value = '{"data": "cached"}'
        self.mock_redis.set.return_value = True
        
        # Patch RedisCaching
        with patch('redis.redis_instance._build_redis_client') as mock_build:
            mock_build.return_value = self.mock_redis
            self.cache = RedisCaching()
    
    def test_cache_hit(self):
        result = self.cache.get("test_key")
        self.assertEqual(result, {"data": "cached"})
        self.mock_redis.get.assert_called_once_with("test_key")
```

### Integration Testing

```python
def test_redis_integration():
    cache = RedisCaching()
    
    # Set value
    cache.set("test_key", {"test": "data"}, ttl=10)
    
    # Get value
    value = cache.get("test_key")
    assert value == {"test": "data"}
    
    # Delete value
    cache.delete("test_key")
    value = cache.get("test_key")
    assert value is None
```

### Cache Behavior Testing

```python
def test_ttl_expiration():
    import time
    cache = RedisCaching()
    
    # Set with short TTL
    cache.set("expiring_key", "value", ttl=1)
    
    # Immediate get - should exist
    assert cache.get("expiring_key") == "value"
    
    # Wait for expiration
    time.sleep(2)
    
    # Should be gone
    assert cache.get("expiring_key") is None
```

## Monitoring and Debugging

### Cache Statistics

```python
# Get Redis info
info = cache.client.info()
print(f"Used memory: {info['used_memory_human']}")
print(f"Connected clients: {info['connected_clients']}")
print(f"Total keys: {info['db0']['keys']}")

# Get specific database stats
db_info = cache.client.info('stats')
print(f"Total connections received: {db_info['total_connections_received']}")
print(f"Total commands processed: {db_info['total_commands_processed']}")
```

### Cache Hit Rate

```python
def calculate_hit_rate():
    info = cache.client.info('stats')
    hits = info.get('keyspace_hits', 0)
    misses = info.get('keyspace_misses', 0)
    total = hits + misses
    
    if total == 0:
        return 0.0
    
    return (hits / total) * 100

print(f"Cache hit rate: {calculate_hit_rate():.2f}%")
```

### Key Inspection

```python
# List all keys (use carefully in production!)
all_keys = cache.client.keys("*")
print(f"Total keys: {len(all_keys)}")

# Scan keys (better for production)
for key in cache.client.scan_iter(match="sql:*", count=100):
    print(f"Key: {key}, TTL: {cache.client.ttl(key)}")

# Get key type
key_type = cache.client.type("my_key")
print(f"Key type: {key_type}")  # string, list, set, zset, hash
```

## Configuration

### Environment Variables

```bash
# Redis connection
REDIS_SOCKET_PATH=/var/run/redis/redis.sock  # Unix socket
REDIS_HOST=localhost                          # TCP host (if not using socket)
REDIS_PORT=6379                               # TCP port (if not using socket)
REDIS_PASSWORD=secure_password                # Authentication
REDIS_DB=0                                    # Database number

# Connection pool
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=30
REDIS_SOCKET_CONNECT_TIMEOUT=10
```

### Redis Server Configuration

`redis.conf` settings for optimal performance:

```conf
# Memory
maxmemory 2gb
maxmemory-policy allkeys-lru  # Evict least recently used keys

# Persistence (adjust based on needs)
save 900 1
save 300 10
save 60 10000

# Unix socket
unixsocket /var/run/redis/redis.sock
unixsocketperm 770

# Performance
tcp-backlog 511
timeout 0
tcp-keepalive 300
```

## Best Practices

### ✅ DO

- Use TTLs appropriate for data volatility
- Invalidate cache on writes
- Monitor cache hit rates
- Use pattern-based invalidation
- Compress large values
- Use pipelines for batch operations
- Handle connection errors gracefully

### ❌ DON'T

- Don't cache rapidly changing data with long TTLs
- Don't use `KEYS *` in production (use `SCAN`)
- Don't store sensitive data without encryption
- Don't set infinite TTLs unless necessary
- Don't forget to invalidate on updates
- Don't cache error results

## Dependencies

**This module depends on**:

- `redis-py` - Redis Python client
- `json` - JSON serialization
- `hashlib` - Key hashing
- `display_tty` - Logging

**Used by**:

- `sql` - Query result caching (via SQLCacheOrchestrator)
- `server.py` - Initialized during startup
- Any module needing caching

## Related Documentation

- [sql.md](../sql/sql.md) - SQL module using Redis caching
- [core.md](../core/core.md) - RuntimeManager pattern
- [server.md](../server/server.md) - Service initialization
