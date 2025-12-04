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
-- FILE: project_structure.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 14:34:17 02-12-2025
-- DESCRIPTION: 
-- This is the project in charge of making the connected cat feeder project work.
-- /STOP
-- COPYRIGHT: (c) Cat Feeder
-- PURPOSE: An overview of the whole project architectureas well as some flags and the __main__.py files.
-- // AR
-- +==== END CatFeeder =================+
-->
# Project Structure Documentation

## Overview

This document explains the Cat Feeder backend project structure, including entry points, initialization files, asset organization, and dependency management.

**Root Directory**: `backend/`

## Directory Structure

```text
backend/
├── __init__.py              # Package marker
├── __main__.py              # Entry point: python -m backend
├── config.toml              # Configuration file
├── requirements.txt         # Python dependencies
├── requirements.dev.txt     # Development dependencies
├── assets/                  # Static assets
│   ├── icon/                # Application icons
│   │   └── Cat Feeder/      # Cat Feeder branding
│   └── js/                  # JavaScript files
│       └── rapipdf.min.js   # RapiDoc PDF plugin
├── deps/                    # Dependency specifications
│   ├── requirements.backend.txt
│   ├── requirements.dev.txt
│   ├── requirements.testing.txt
│   ├── backend/             # Backend-specific deps
│   │   ├── requirements.audio.txt
│   │   ├── requirements.config.txt
│   │   ├── requirements.cron.txt
│   │   ├── requirements.database.txt
│   │   ├── requirements.http.txt
│   │   ├── requirements.image.txt
│   │   └── ...
│   ├── dev/                 # Development tools
│   └── test/                # Testing dependencies
├── logs/                    # Runtime logs (rotary_logger)
│   └── 2025/                # Organized by year
└── src/                     # Source code
    ├── __init__.py          # Package marker
    ├── __main__.py          # Entry point: python -m backend.src
    ├── server_main.py       # Main server bootstrap
    └── libs/                # Application modules
        ├── __init__.py      # Exports all modules
        ├── server.py        # Main orchestrator
        ├── core/            # Core patterns
        ├── sql/             # Database layer
        ├── redis/           # Caching layer
        └── ...              # Other modules
```

## Entry Points

### 1. `backend/__main__.py`

**Purpose**: Entry point for `python -m backend`

**Functionality**:

- Sets up file logging with `rotary_logger`
- Configures log rotation and retention
- Launches `backend.src` module

```python
# Usage
python -m backend
python -m backend --debug
```

**Log Configuration**:

- **Location**: `backend/logs/YYYY/`
- **Rotation**: Daily, keeps last 7 days
- **Format**: `backend-YYYY-MM-DD.log`
- **Stream Merging**: Controlled by `MERGE_STREAMS` environment variable

---

### 2. `backend/src/__main__.py`

**Purpose**: Entry point for `python -m backend.src`

**Functionality**:

- Sets up file logging (one level deeper)
- Imports and runs `server_main.Main`

```python
# Usage
python -m backend.src
python -m backend.src --port=8000 --debug
```

**Log Configuration**:

- **Location**: `backend/logs/YYYY/`
- **Rotation**: Same as backend-level
- **Integration**: Works with `display_tty` for terminal output

---

### 3. `backend/src/server_main.py`

**Purpose**: Main server bootstrap with CLI argument parsing

**Documentation**: [server_main.md](server_main.md)

**Functionality**:

- Parses command-line arguments
- Creates and launches `Server` instance
- Provides help system

```python
# Direct usage
python backend/src/server_main.py --host=0.0.0.0 --port=5000
```

---

## Package Initialization Files

### `backend/__init__.py`

**Purpose**: Mark `backend/` as a Python package

**Typical Content**:

```python
"""Cat Feeder Backend Package"""
__version__ = "1.0.0"
```

---

### `backend/src/__init__.py`

**Purpose**: Mark `src/` as a package, may re-export modules

**Typical Content**:

```python
"""Backend source code package"""
from . import libs
```

---

### `backend/src/libs/__init__.py`

**Purpose**: Export all library modules for convenient imports

**Typical Content**:

```python
"""Backend library modules"""

# Core
from .core import (
    RuntimeManager,
    FinalSingleton,
    FinalClass,
    RuntimeControl,
    RI
)

# Data Layer
from .sql import SQL
from .redis import RedisCaching
from .bucket import Bucket

# Application Layer
from .server import Server
from .path_manager import PathManager
from .endpoint_manager import EndpointManager

# Service Layer
from .boilerplates import (
    BoilerplateResponses,
    BoilerplateIncoming,
    BoilerplateNonHTTP
)
from .crons import BackgroundTasks, Crons
from .e_mail import MailManagement
from .utils import (
    OAuthAuthentication,
    Passwords,
    ServerManagement,
    CONST
)

# Utility Layer
from .http_codes import HCI
from .server_header import ServerHeaders
from .fffamily import FFFamily
from .docs import DocumentationHandler

__all__ = [
    # Core
    "RuntimeManager", "FinalSingleton", "FinalClass", 
    "RuntimeControl", "RI",
    # Data
    "SQL", "RedisCaching", "Bucket",
    # Application
    "Server", "PathManager", "EndpointManager",
    # Service
    "BoilerplateResponses", "BoilerplateIncoming", "BoilerplateNonHTTP",
    "BackgroundTasks", "Crons", "MailManagement",
    "OAuthAuthentication", "Passwords", "ServerManagement", "CONST",
    # Utility
    "HCI", "ServerHeaders", "FFFamily", "DocumentationHandler"
]
```

**Benefit**: Allows clean imports:

```python
from backend.src.libs import Server, SQL, RuntimeManager
# vs
from backend.src.libs.server import Server
from backend.src.libs.sql import SQL
from backend.src.libs.core import RuntimeManager
```

---

## Assets Directory

### `backend/assets/`

**Purpose**: Store static files served by the application or used in documentation

#### `assets/icon/Cat Feeder/`

**Purpose**: Application branding and icons

**Contents**:

- Logos in various formats (PNG, SVG, ICO)
- Favicon files
- App icons for different platforms

**Usage**:

```python
# Serve in FastAPI
from fastapi.staticfiles import StaticFiles

app.mount("/static/icons", StaticFiles(directory="assets/icon"), name="icons")
```

**Access**: `http://localhost:5000/static/icons/Cat Feeder/logo.png`

---

#### `assets/js/`

**Purpose**: JavaScript libraries for API documentation

**Contents**:

- `rapipdf.min.js` - RapiDoc PDF generation plugin

**Usage**:

```python
# Referenced in DocumentationHandler
app.mount("/static/js", StaticFiles(directory="assets/js"), name="js")
```

**Access**: Loaded automatically by RapiDoc documentation pages

---

## Dependencies Directory

### `backend/deps/`

**Purpose**: Organized dependency specifications for different components and environments

#### Top-Level Files

| File | Purpose |
|------|---------|
| `requirements.backend.txt` | All backend runtime dependencies |
| `requirements.dev.txt` | Development tools (linters, formatters) |
| `requirements.testing.txt` | Testing frameworks (pytest, coverage) |

#### `deps/backend/`

**Modular Backend Dependencies**

Each file contains dependencies for a specific module:

| File | Module | Key Dependencies |
|------|--------|------------------|
| `requirements.audio.txt` | Audio processing | pydub, ffmpeg-python |
| `requirements.config.txt` | Configuration | python-dotenv, toml |
| `requirements.cron.txt` | Background tasks | apscheduler |
| `requirements.database.txt` | SQL operations | mysql-connector-python, project-specific DB overlay |
| `requirements.http.txt` | Web framework | fastapi, uvicorn, pydantic |
| `requirements.image.txt` | Image processing | Pillow |
| `requirements.internet.txt` | HTTP clients | httpx, requests |
| `requirements.linting.txt` | Code quality | pylint, mypy, black |

**Usage**:

```bash
# Install all backend dependencies
pip install -r backend/deps/requirements.backend.txt

# Install specific module dependencies
pip install -r backend/deps/backend/requirements.database.txt
```

**Benefit**: Modular installation allows minimal dependency footprint for specific use cases

---

#### `deps/dev/`

**Development Tools**

Dependencies for development environment:

- Code formatters (black, isort)
- Linters (pylint, flake8)
- Type checkers (mypy)
- Git hooks (pre-commit)

---

#### `deps/test/`

**Testing Tools**

Dependencies for testing:

- pytest
- pytest-cov (coverage)
- pytest-asyncio (async tests)
- pytest-mock (mocking)
- httpx (API testing)

---

## Logs Directory

### `backend/logs/`

**Purpose**: Runtime log storage managed by `rotary_logger`

**Structure**:

```text
logs/
└── 2025/
    ├── backend-2025-12-01.log
    ├── backend-2025-12-02.log
    └── backend-2025-12-03.log
```

**Configuration**:

- **Rotation**: Daily at midnight
- **Retention**: Last 7 days (configurable)
- **Format**: `backend-YYYY-MM-DD.log`
- **Compression**: Old logs may be gzipped

**Log Levels**:

```python
# Controlled by DEBUG environment variable
DEBUG=true   # Verbose logging
DEBUG=false  # Info and above only
```

**Integration**:

```python
from rotary_logger import RotaryLogger

logger = RotaryLogger(
    log_path=Path("backend/logs"),
    retention_days=7,
    merge_streams=True  # Combine stdout/stderr
)
```

**Exclusion**: `logs/` should be in `.gitignore` (runtime artifacts)

---

## Configuration Files

### `backend/config.toml`

**Purpose**: Application configuration in TOML format

**Example Structure**:

```toml
[server]
host = "0.0.0.0"
port = 5000
debug = false

[database]
host = "localhost"
port = 3306
name = "Cat Feeder_db"

[redis]
socket_path = "/var/run/redis/redis.sock"

[oauth]
token_expire_minutes = 30
algorithm = "HS256"

[email]
smtp_host = "smtp.gmail.com"
smtp_port = 465

[crons]
enabled = true
db_cleanup_interval = 3600
```

**Loading**:

```python
import toml

with open("backend/config.toml") as f:
    config = toml.load(f)

host = config["server"]["host"]
port = config["server"]["port"]
```

---

## Import Patterns

### Absolute Imports (Recommended)

```python
# From any file in the project
from backend.src.libs import Server, SQL, RuntimeManager
from backend.src.libs.core import FinalSingleton
from backend.src.libs.sql import SQL
```

### Relative Imports (Within Package)

```python
# From backend/src/libs/server.py
from .core import RuntimeManager, FinalSingleton
from .sql import SQL
from .redis import RedisCaching

# From backend/src/libs/sql/sql_manager.py
from ..core import FinalClass
from .sql_connections import SQLManageConnections
```

### Entry Point Imports

```python
# backend/src/server_main.py handles both:
try:
    from .libs import Server  # Package import
except ImportError:
    from libs import Server   # Direct import
```

---

## Best Practices

### ✅ DO

- Use `__init__.py` to expose public API
- Keep assets organized by type
- Modularize dependencies in `deps/backend/`
- Exclude `logs/` from version control
- Use absolute imports in application code
- Use relative imports within packages

### ❌ DON'T

- Don't commit log files
- Don't put secrets in `config.toml` (use `.env` instead)
- Don't import from `__main__.py` files
- Don't hard-code paths to assets

---

## Related Documentation

- [server_main.md](server_main.md) - Entry point details
- [server/server.md](../server/server.md) - Server orchestration
- [00_ARCHITECTURE.md](../00_ARCHITECTURE.md) - System architecture
