<!-- 
-- +==== BEGIN AsperBackend =================+
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
-- PROJECT: AsperBackend
-- FILE: 00_ARCHITECTURE.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 13:57:39 02-12-2025
-- DESCRIPTION: 
-- This is the backend server in charge of making the actual website work.
-- /STOP
-- COPYRIGHT: (c) Asperguide
-- PURPOSE: A brief overview of the projects architecture.
-- // AR
-- +==== END AsperBackend =================+
-->
# Asperguide Backend Architecture

**Version:** 1.0  
**Last Updated:** December 2, 2025

## Overview

The Asperguide Backend is a FastAPI-based RESTful API server designed for the Asperguide platform. It follows a **layered architecture** with clear separation of concerns, featuring centralized service management, Redis-backed caching, and MySQL for persistent storage.

**Key Characteristics:**

- **Framework**: FastAPI (Python 3.12+)
- **Database**: MySQL with SQLAlchemy
- **Caching**: Redis
- **Storage**: MinIO/S3-compatible object storage
- **Background Tasks**: APScheduler
- **Authentication**: OAuth2 with JWT tokens
- **API Documentation**: Multiple formats (Swagger, ReDoc, RapiDoc, Scalar)

## System Architecture

@startuml{system_architecture.puml}
@enduml

## Architecture Layers

The backend is organized into **6 distinct layers**, each with specific responsibilities:

### 1. Entry Point Layer

**Location**: `backend/src/server_main.py`

The application entry point that:

- Loads environment configuration
- Creates the Server instance
- Initializes Uvicorn ASGI server
- Handles process signals (SIGINT, SIGTERM)

```python
# Simplified entry point
from libs import Server

def main():
    server = Server(
        host="0.0.0.0",
        port=5000,
        app_name="Asperguide"
    )
    server.main()
```

**Documentation**:

- [project_structure/server_main.md](project_structure/server_main.md) - Entry point details
- [project_structure/project_structure.md](project_structure/project_structure.md) - Full project structure

---

### 2. Orchestration Layer

**Location**: `backend/src/libs/server.py`, `backend/src/libs/core/`

**Components**:

- **Server**: Main orchestrator, initializes all services
- **RuntimeManager**: Service locator container
- **FinalSingleton/FinalClass**: Lifecycle enforcement

The Server class acts as the **central coordinator**, registering 15+ services with RuntimeManager during initialization.

**Documentation**:

- [server/server.md](server/server.md) - Server orchestration
- [core/core.md](core/core.md) - RuntimeManager and patterns

---

### 3. Data Layer

**Location**: `backend/src/libs/sql/`, `backend/src/libs/redis/`, `backend/src/libs/bucket/`

**Components**:

- **SQL**: MySQL interface with connection pooling
- **Redis**: Caching layer with TTL management
- **Bucket**: S3-compatible object storage

**Key Features**:

- Write-through caching (SQL ↔ Redis)
- Connection pooling for database efficiency
- Automatic cache invalidation on writes
- Type-safe S3 operations

**Documentation**:

- [sql/sql.md](sql/sql.md) - Database operations
- [redis/redis.md](redis/redis.md) - Caching strategies
- [bucket/bucket.md](bucket/bucket.md) - Object storage

---

### 4. Application Layer

**Location**: `backend/src/libs/path_manager/`, `backend/src/libs/endpoint_manager/`, `backend/src/libs/docs/`

**Components**:

- **PathManager**: Deferred route registration
- **EndpointManager**: Route aggregation and FastAPI injection
- **DocumentationHandler**: Multi-format API documentation

**Key Innovation**: **Deferred Route Registration Pattern**

1. Routes defined BEFORE FastAPI app creation
2. PathManager stores routes in memory
3. EndpointManager aggregates from sub-modules
4. All routes injected into FastAPI in one operation

**Documentation**:

- [path_manager/path_manager.md](path_manager/path_manager.md) - Route registration
- [endpoint_manager/endpoint_manager.md](endpoint_manager/endpoint_manager.md) - Route aggregation
- [docs/docs.md](docs/docs.md) - API documentation

---

### 5. Service Layer

**Location**: `backend/src/libs/boilerplates/`, `backend/src/libs/crons/`, `backend/src/libs/e_mail/`, `backend/src/libs/utils/`

**Components**:

- **Boilerplates**: Standardized request/response handling
- **BackgroundTasks/Crons**: Scheduled jobs (APScheduler)
- **MailManagement**: Email sending (SMTP)
- **OAuthAuthentication**: OAuth2 flows
- **ServerManagement**: Server lifecycle management

**Key Patterns**:

- Standardized error responses
- Token-based authentication
- Scheduled database cleanup
- OAuth token renewal

**Documentation**:

- [boilerplates/boilerplates.md](boilerplates/boilerplates.md) - Request/response standards
- [crons/crons.md](crons/crons.md) - Background tasks
- [e_mail/e_mail.md](e_mail/e_mail.md) - Email management
- [utils/utils.md](utils/utils.md) - OAuth and utilities

---

### 6. Utility Layer

**Location**: `backend/src/libs/http_codes/`, `backend/src/libs/server_header/`, `backend/src/libs/fffamily/`

**Components**:

- **HttpCodes**: HTTP status code interface
- **ServerHeaders**: CORS and security headers
- **FFFamily**: FFmpeg binary management
- **Passwords**: bcrypt hashing utilities

**Key Features**:

- 80+ HTTP status methods
- Cross-platform FFmpeg setup
- Security headers (XSS, CORS, CSP)
- Password hashing with bcrypt

**Documentation**:

- [http_codes/http_codes.md](http_codes/http_codes.md) - Status codes
- [server_header/server_header.md](server_header/server_header.md) - Security headers
- [fffamily/fffamily.md](fffamily/fffamily.md) - FFmpeg utilities

---

## Request Flow

@startuml{request_flow.puml}
@enduml

### Typical Request Lifecycle

1. **Client sends HTTP request** → FastAPI receives it
2. **FastAPI route lookup** → EndpointManager finds handler
3. **Boilerplates parse request** → Extract token, body, params
4. **OAuth validates token** → Check user authentication
   - SQL queries user session
   - Redis caches authentication result
5. **Handler executes business logic**
   - Queries SQL for data
   - SQL checks Redis cache first
   - Returns result
6. **Boilerplates standardize response** → JSON format
7. **FastAPI returns HTTP response** → Client receives data

**Caching Benefits**:

- Database queries cached in Redis (5-60 min TTL)
- Authentication results cached (reducing database load)
- Schema/metadata cached (1-2 hour TTL)

---

## Module Dependencies

@startuml{module_dependencies.puml}
@enduml

### Dependency Hierarchy

**No Dependencies:**

- `core` (RuntimeManager, FinalSingleton, FinalClass)
- `http_codes`
- `fffamily`

**Depends on Core:**

- `sql`, `redis`, `bucket` (use RuntimeManager)
- `boilerplates` (uses FinalClass)

**Depends on Data:**

- `boilerplates` → SQL, OAuth
- `crons` → SQL, OAuth
- `path_manager` → HttpCodes

**Depends on Application:**

- `endpoint_manager` → PathManager, OAuth, Boilerplates

**Top-Level Orchestrator:**

- `server` → depends on ALL modules

---

## Design Patterns

### 1. Service Locator Pattern

**Implementation**: `RuntimeManager`

```python
from core import RuntimeManager
from sql import SQL

# Register service
RuntimeManager.set(SQL, url="localhost", port=3306, ...)

# Retrieve service (lazy initialization)
sql = RuntimeManager.get(SQL)
```

**Benefits**:

- Centralized service access
- Lazy initialization
- Simplified dependency management
- Easy testing (mock injection)

**Documentation**: [core/core.md](core/core.md)

---

### 2. Protected Singleton Pattern

**Implementation**: `FinalSingleton`

```python
from core import FinalSingleton

class MyService(FinalSingleton):
    def __init__(self):
        pass

# ❌ Direct instantiation forbidden
service = MyService()  # RuntimeError!

# ✅ Must use RuntimeManager
RuntimeManager.set(MyService)
service = RuntimeManager.get(MyService)
```

**Benefits**:

- Enforced single instance
- Prevents accidental multiple instantiations
- Thread-safe by design
- Clear lifecycle management

**Documentation**: [core/core.md](core/core.md)

---

### 3. Deferred Registration Pattern

**Implementation**: `PathManager`

```python
from path_manager import PathManager

# Register route BEFORE FastAPI exists
PathManager.add_path(
    "/users",
    "GET",
    get_users_handler
)

# Later: Inject all routes into FastAPI
PathManager.inject_routes(app)
```

**Benefits**:

- Decouples route definition from FastAPI
- Enables modular route organization
- Allows route introspection before registration
- Simplifies testing

**Documentation**: [path_manager/path_manager.md](path_manager/path_manager.md)

---

### 4. Write-Through Cache Pattern

**Implementation**: `SQL` + `Redis`

```python
# Read operation - automatic caching
users = sql.get_data_from_table("users", ["*"])
# 1. Check Redis cache
# 2. If miss, query MySQL
# 3. Store result in Redis
# 4. Return data

# Write operation - automatic invalidation
sql.update_data_in_table("users", ...)
# 1. Execute database write
# 2. Invalidate "sql:users:*" cache
# 3. Next read will refresh cache
```

**Benefits**:

- Reduced database load (5-10x fewer queries)
- Consistent cache state
- Automatic invalidation
- Configurable TTLs

**Documentation**:

- [sql/sql.md](sql/sql.md)
- [redis/redis.md](redis/redis.md)

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Web Framework** | FastAPI | Latest | ASGI web framework |
| **ASGI Server** | Uvicorn | Latest | Production server |
| **Database** | MySQL | 8.0+ | Persistent storage |
| **Cache** | Redis | 6.0+ | Query caching |
| **Object Storage** | MinIO | Latest | S3-compatible storage |
| **Scheduler** | APScheduler | 3.x | Background tasks |
| **ORM** | SQLAlchemy | 2.x | Database abstraction |
| **Validation** | Pydantic | 2.x | Data validation |

### Python Libraries

```python
# Web & API
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0

# Database
mysql-connector-python
sqlalchemy>=2.0.0
redis>=4.5.0

# Object Storage
boto3
botocore

# Authentication
python-jose[cryptography]
passlib[bcrypt]
python-multipart

# Background Tasks
apscheduler>=3.10.0

# Utilities
python-dotenv
display-tty>=1.3.5
```

### External Services

- **MySQL**: Primary database
- **Redis**: Caching layer
- **MinIO**: Object storage (S3-compatible)
- **SMTP Server**: Email delivery

---

## Configuration

### Environment Variables

```bash
# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
DEBUG=false

# Database
SQL_HOST=localhost
SQL_PORT=3306
SQL_USERNAME=asperguide
SQL_PASSWORD=secure_password
SQL_DATABASE=asperguide_db

# Redis
REDIS_SOCKET_PATH=/var/run/redis/redis.sock
REDIS_PASSWORD=redis_password

# MinIO/S3
BUCKET_ENDPOINT=localhost:9000
BUCKET_ACCESS_KEY=minioadmin
BUCKET_SECRET_KEY=minioadmin
BUCKET_SECURE=false

# OAuth
OAUTH_SECRET_KEY=your_secret_key_here
OAUTH_ALGORITHM=HS256
OAUTH_TOKEN_EXPIRE_MINUTES=30

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=app_password

# Background Tasks
ENABLE_CRONS=true
DB_CLEANUP_INTERVAL=3600  # 1 hour
TOKEN_RENEWAL_INTERVAL=86400  # 24 hours
```

### Configuration Files

- `config.toml`: Main configuration file
- `.env`: Environment variables (development)
- `docker-compose.yaml`: Docker orchestration

---

## Startup Sequence

@startuml{startup_sequence.puml}
@enduml

### Initialization Steps

1. **server_main.py** loads environment
2. **Server.**init**()** registers all services with RuntimeManager:
   - SQL (database connection)
   - Redis (cache client)
   - Bucket (S3 client)
   - PathManager (route storage)
   - Boilerplates (request/response handlers)
   - ServerHeaders (CORS configuration)
   - OAuth (authentication)
   - MailManagement (email sender)
   - FFFamily (FFmpeg binaries)
   - BackgroundTasks/Crons (scheduler)
3. **Server.main()** executes:
   - Create FastAPI app
   - Configure CORS via ServerHeaders
   - Initialize EndpointManager (aggregates routes)
   - PathManager.inject_routes() (add all routes to FastAPI)
   - DocumentationHandler (setup API docs)
   - BackgroundTasks.start() (begin scheduled jobs)
   - Uvicorn.run() (start ASGI server)

**Total Startup Time**: ~2-3 seconds (depending on database/cache connections)

---

## Shutdown Sequence

### Graceful Shutdown

1. **Signal received** (SIGINT/SIGTERM)
2. **RuntimeControl.signal_shutdown()** sets global flag
3. **Server.shutdown()** executes:
   - Stop accepting new requests
   - ServerManagement.cleanup()
   - BackgroundTasks.stop()
   - Crons.shutdown()
   - SQL.shutdown() (close connections)
   - Redis client disconnection
   - Bucket.disconnect()
4. **Process exits** cleanly

**Shutdown Time**: ~1-2 seconds

---

## Security Features

### Authentication & Authorization

- **OAuth2 with JWT tokens**
- **bcrypt password hashing**
- **Token expiration and renewal**
- **Session management in database**

### HTTP Security Headers

```python
# Configured via ServerHeaders
{
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000",
    "Content-Security-Policy": "default-src 'self'"
}
```

### CORS Configuration

```python
# Allowed origins, methods, headers
CORSMiddleware(
    app,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### SQL Injection Prevention

- Parameterized queries
- Input sanitization
- SQL injection detection

**Documentation**: [sql/sql.md](sql/sql.md), [server_header/server_header.md](server_header/server_header.md)

---

## Performance Optimizations

### Caching Strategy

- **Query caching**: 5-60 minute TTLs
- **Schema caching**: 1-2 hour TTLs
- **Authentication caching**: 15-30 minute TTLs
- **Write-through invalidation**: Automatic

### Database Optimization

- **Connection pooling**: Reuse connections
- **Query optimization**: Indexed columns
- **Batch operations**: Bulk inserts/updates
- **Lazy loading**: On-demand initialization

### Resource Management

- **Service locator**: Single instances
- **Thread safety**: Lock-based synchronization
- **Graceful shutdown**: Resource cleanup
- **Background tasks**: Off-peak scheduling

---

## Testing Strategy

### Unit Testing

```python
import unittest
from core import RuntimeManager
from unittest.mock import Mock

class TestEndpoint(unittest.TestCase):
    def setUp(self):
        # Mock dependencies
        self.mock_sql = Mock()
        RuntimeManager.set(SQL, self.mock_sql)
    
    def test_get_users(self):
        # Test logic
        pass
```

### Integration Testing

```python
# Test with actual services
sql = SQL.create(url="test_db", ...)
result = sql.get_data_from_table("users", ["*"])
assert result is not None
```

### API Testing

```bash
# Using pytest + httpx
pytest tests/api/test_users.py
```

---

## Module Documentation

### Core Modules

- [core/core.md](core/core.md) - RuntimeManager, FinalSingleton, patterns
- [server/server.md](server/server.md) - Main orchestrator

### Data Layer

- [sql/sql.md](sql/sql.md) - Database operations, caching
- [redis/redis.md](redis/redis.md) - Caching strategies
- [bucket/bucket.md](bucket/bucket.md) - Object storage

### Application Layer

- [path_manager/path_manager.md](path_manager/path_manager.md) - Route registration
- [endpoint_manager/endpoint_manager.md](endpoint_manager/endpoint_manager.md) - Route aggregation
- [docs/docs.md](docs/docs.md) - API documentation

### Service Layer

- [boilerplates/boilerplates.md](boilerplates/boilerplates.md) - Request/response handling
- [crons/crons.md](crons/crons.md) - Background tasks
- [e_mail/e_mail.md](e_mail/e_mail.md) - Email management
- [utils/utils.md](utils/utils.md) - OAuth, passwords, utilities

### Utility Layer

- [http_codes/http_codes.md](http_codes/http_codes.md) - HTTP status codes
- [server_header/server_header.md](server_header/server_header.md) - Security headers
- [fffamily/fffamily.md](fffamily/fffamily.md) - FFmpeg utilities

---

## Quick Start

### Development Setup

```bash
# Clone repository
git clone https://github.com/Asperguide/back-end.git
cd back-end

# Create virtual environment
python3.12 -m venv server_env
source server_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp sample.env .env
# Edit .env with your configuration

# Start services (MySQL, Redis, MinIO)
docker-compose up -d

# Run server
python -m backend.src
```

### Production Deployment

```bash
# Build Docker image
docker build -f docker/dockerfile.backend -t asperguide-backend .

# Run with docker-compose
docker-compose -f docker-compose.yaml up -d
```

### Access API Documentation

Once running, visit:

- Swagger UI: <http://localhost:5000/docs>
- ReDoc: <http://localhost:5000/redoc>
- RapiDoc: <http://localhost:5000/rapipdf>

---

## Contributing

When contributing to the backend:

1. **Read relevant module documentation** before making changes
2. **Follow existing patterns** (Service Locator, FinalSingleton, etc.)
3. **Add tests** for new functionality
4. **Update documentation** if adding/modifying modules
5. **Run linters** before committing (black, pylint, mypy)

### Code Style

```bash
# Format code
black backend/

# Lint
pylint backend/src

# Type check
mypy backend/src
```

---

## Troubleshooting

### Common Issues

**Issue**: Cannot connect to database  
**Solution**: Check `SQL_HOST`, `SQL_PORT`, `SQL_USERNAME`, `SQL_PASSWORD` in `.env`

**Issue**: Redis connection timeout  
**Solution**: Verify Redis server is running: `redis-cli ping`

**Issue**: MinIO bucket access denied  
**Solution**: Check `BUCKET_ACCESS_KEY` and `BUCKET_SECRET_KEY`

**Issue**: Endpoints not registering  
**Solution**: Check PathManager logs, ensure routes defined before `inject_routes()`

---

## Additional Resources

- **Source Code**: `backend/src/`
- **Configuration**: `config.toml`, `.env`
- **Docker**: `docker-compose.yaml`
- **API Docs** (live): <http://localhost:5000/docs>

---

**For detailed module information, see the respective documentation files linked above.**
