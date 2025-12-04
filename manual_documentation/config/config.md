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
-- FILE: config.md
-- CREATION DATE: 04-12-2025
-- LAST Modified: 8:6:52 04-12-2025
-- DESCRIPTION: 
-- This is the project in charge of making the connected cat feeder project work.
-- /STOP
-- COPYRIGHT: (c) Cat Feeder
-- PURPOSE: The explanation of the config module used in the server to gather the config.toml and .env files in the server in a memory and cpu optimised way.
-- // AR
-- +==== END CatFeeder =================+
-->
# Configuration Management Module

**Location**: `backend/src/libs/config/`  
**Purpose**: Centralized configuration and environment variable loading with smart path resolution and caching  
**Last Modified**: 04-12-2025

---

## Architecture Diagrams

- **[Architecture Overview](config_architecture.puml)**: Component dependencies and relationships
- **[Class Diagram](config_class_diagram.puml)**: Detailed class structure with methods and attributes
- **[Sequence Diagram](config_sequence.puml)**: Configuration loading flow with caching
- **[Path Resolution](path_resolution.puml)**: Smart path discovery algorithm
- **[Singleton Pattern](singleton_pattern.puml)**: Thread-safe singleton implementation

---

## Overview

The **config** module provides singleton loaders for `config.toml` and `.env` files with intelligent path discovery. It solves the problem of hardcoded paths and redundant file loading by caching configuration data on first access.

### Key Features

- **Smart Path Resolution**: Automatically finds config files by checking up to 5 levels up, prioritizing working directory
- **Singleton Pattern**: Loads configuration once, caches forever (per application lifecycle)
- **Thread-Safe**: Proper initialization prevents race conditions
- **No Deep Recursion**: Maximum ~20 file checks - no CPU hogging
- **Active Loading**: Environment file loaded during initialization
- **Import-Time Safe**: Works with Python's module caching system

---

## Architecture

```text
backend/src/libs/config/
├── __init__.py          # Public API exports
├── toml_loader.py       # config.toml singleton loader
└── env_loader.py        # .env singleton loader
```

![Architecture Diagram](config_architecture.puml)

### Module Components

#### `toml_loader.py`

- `TOMLLoader` class: Singleton for loading `config.toml`
- **TOML Library Priority**: `tomllib` (Python 3.11+) → `tomli` (Python < 3.11)
- Supports nested key access with variadic keys
- Caches parsed TOML data
- All methods have comprehensive PEP 257 docstrings

#### `env_loader.py`

- `EnvLoader` class: Singleton for loading `.env` files
- **Active loading**: Loads `.env` during `__init__` by calling `load_env_file()`
- Optional merge with `os.environ` (default: True)
- Parses key=value pairs with quote handling
- Applies environment variables to `os.environ` on demand
- All methods have comprehensive PEP 257 docstrings

### Design Patterns

#### Singleton Pattern

![Singleton Pattern](singleton_pattern.puml)

Both `ConfigLoader` and `EnvLoader` implement thread-safe singleton pattern:

- `__new__()` ensures only one instance exists
- `_initialized` flag prevents re-initialization
- Same instance shared across all imports
- Cached data shared globally

#### Two-Level Caching

1. **Python Module Cache** (`sys.modules`): Module code executes only once
2. **Singleton Cache**: Configuration data loaded once on first access

This ensures zero redundancy even with multiple imports.

---

## Usage

### Basic Usage

```python
from config import get_config, get_env

# Load config.toml values
db_host = get_config('Database', 'host')
db_port = get_config('Database', 'port', default=3306)

# Load .env variables
api_key = get_env('API_KEY')
smtp_password = get_env('SMTP_PASSWORD', default='')
```

### Loading Full Configuration

```python
from config import load_config, load_env

# Get entire config.toml as dictionary
config = load_config()
print(config['Server']['port'])

# Get all .env variables as dictionary
env_vars = load_env()
print(env_vars['DATABASE_URL'])
```

### Advanced Usage

```python
from config import ConfigLoader, EnvLoader, get_project_root

# Get project root directory
root = get_project_root()
assets_dir = root / 'backend' / 'assets'

# Force reload configuration (useful for testing)
loader = ConfigLoader()
loader.clear_cache()
fresh_config = loader.load_config_toml(force_reload=True)

# Load .env without merging os.environ
env_loader = EnvLoader()
env_vars = env_loader.load_env_file(merge_os_environ=False)

# Apply .env to os.environ globally
from config import apply_env
apply_env()  # Now os.environ contains all .env variables

# Use custom config file paths (environment variables)
import os
os.environ['CONFIG_FILE'] = '/custom/path/config.toml'
os.environ['ENV_FILE'] = '/custom/path/.env'
# Next import will use custom paths

# Or pass directly to loader
config = loader.load_config_toml(custom_path='/custom/config.toml')
env = env_loader.load_env_file(custom_path='/custom/.env')
```

**Note**: The loaders automatically check `sys.argv` for `--config` and `--env` flags, so no additional setup is needed for command-line usage.

---

## Path Resolution Strategy

![Path Resolution Flow](path_resolution.puml)

### Project Root Detection

The loaders find the project root by searching for marker files:

- `docker-compose.yaml`
- `requirements.txt`
- `backend/` directory
- `.git` directory
- `config.toml`
- `.env`

**Search strategy**:

1. Start from current working directory (`cwd`) and module's directory (`__file__`)
2. Prioritize `cwd` first (checked before module location)
3. Check current directory + up to 5 levels up (6 locations total per path)
4. Check all markers at each level
5. First marker found determines project root
6. If no marker found, use `cwd` as fallback

**Performance**: Maximum ~20 file existence checks (no recursive scanning)

**Why cwd-first**: Prevents incorrect root detection when marker names match intermediate directories (e.g., `backend/` directory matching "backend" marker)

**Container Support**: Expanded marker list ensures detection even in container environments where some markers may be absent

### Configuration File Locations

**Priority order for config.toml**:

1. Custom path (via `custom_path` parameter)
2. Command-line argument (`--config /path/to/config.toml`)
3. Environment variable (`CONFIG_FILE=/path/to/config.toml`)
4. Auto-discovered in project tree:
   - `<project_root>/config.toml`
   - `<project_root>/backend/config.toml`
   - `<project_root>/backend/src/config.toml`

**Priority order for .env**:

1. Custom path (via `custom_path` parameter)
2. Command-line argument (`--env /path/to/.env`)
3. Environment variable (`ENV_FILE=/path/to/.env`)
4. Auto-discovered in project tree:
   - `<project_root>/.env`
   - `<project_root>/tmp.env` (fallback)
   - `<project_root>/backend/.env`
   - `<project_root>/backend/tmp.env` (fallback)

---

## Integration with Existing Code

### Replacing Hardcoded Paths

**Before**:

```python
# utils/constants.py - OLD
import dotenv
import toml

dotenv.load_dotenv(".env")
TOML_CONF = toml.load("config.toml")

DB_HOST = TOML_CONF['Database']['host']
```

**After**:

```python
# utils/constants.py - NEW
from config import get_config, load_env

# Auto-cached, smart path resolution
ENV = load_env()  # Merged with os.environ
DB_HOST = get_config('Database', 'host')
```

### Active Loading Architecture

The `EnvLoader` uses active loading - `.env` is loaded during `__init__` by calling the public `load_env_file()` API:

```python
class EnvLoader:
    def __new__(cls, *args, **kwargs):
        # Singleton pattern ensures single instance
        
    def __init__(self, debug=False):
        # Active loading: call the public API
        try:
            self.load_env_file()  # Handles priority: argv → ENV_FILE → auto-search
        except FileNotFoundError:
            self._env_vars = dict(os.environ)  # Fallback to os.environ
```

**Benefits**:

- No logic duplication - uses the proper public API
- Respects priority chain (custom_path → argv → ENV_FILE → auto-search)
- Graceful fallback to `os.environ` if no `.env` found
- Thread-safe singleton pattern ensures single initialization

### Import-Time Compatibility

The config loaders work seamlessly with import-time loading thanks to multi-level caching:

1. **Python's module cache** (`sys.modules`): Module code only runs once
2. **Singleton cache**: Configuration data loaded once during first instantiation
3. **Instance cache**: `_env_vars` and `_config_data` prevent redundant file I/O

```python
# constants.py
from config import load_config

CONFIG = load_config()  # Runs at import time

# First import: Loads config.toml, caches it
# Subsequent imports: Returns cached module (doesn't re-execute)
# Direct calls to load_config(): Return cached data
```

---

## Configuration File Formats

### config.toml Format

```toml
[Server]
host = "0.0.0.0"
port = 8000
debug = false

[Database]
host = "localhost"
port = 3306
name = "Cat Feeder"

[Test]
enable_testing_endpoints = false
```

### .env Format

```bash
# Database credentials
DB_USER=admin
DB_PASSWORD="secure_password"
DB_HOST=localhost

# API Keys
API_KEY=your-api-key-here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Quotes are optional but recommended for values with spaces
EMAIL_SENDER="noreply@Cat Feeder.com"
```

---

## API Reference

![Class Diagram](config_class_diagram.puml)
![Sequence Diagram](config_sequence.puml)

### TOML Configuration

#### `load_config() -> Dict[str, Any]`

```python
"""
Load config.toml (cached).

Returns:
    Dictionary containing parsed TOML configuration
    
Raises:
    FileNotFoundError: If config.toml not found
"""
```

#### `get_config(*keys: str, default: Any = None) -> Any`

```python
"""
Get config.toml value using nested keys.

Args:
    *keys: Nested keys to traverse (e.g., 'database', 'host')
    default: Default value if key not found (default: None)
    
Returns:
    Value at specified key path or default if not found
"""
```

**Example**:

```python
host = get_config('Database', 'host', default='localhost')
port = get_config('Database', 'port', default=3306)
```

#### `get_project_root() -> Path`

```python
"""
Get the project root directory.
"""
```

#### `ConfigLoader.clear_cache() -> None`

```python
"""
Clear cached configuration.
"""
```

Clear cached configuration data (useful for testing).

#### `ConfigLoader.load_config_toml(force_reload: bool = False, custom_path: Optional[str] = None) -> Dict[str, Any]`

```python
"""
Load config.toml file and return as dictionary.

Args:
    force_reload: Force reload even if cached (default: False)
    custom_path: Custom path to config file (default: None)
    
Returns:
    Dictionary containing parsed TOML configuration
    
Raises:
    FileNotFoundError: If config.toml not found
    OSError: If file cannot be read
    IOError: If file read operation fails
"""
```

### Environment Variables

#### `load_env(merge_os_environ: bool = True) -> Dict[str, str]`

```python
"""
Load .env file (cached).

Args:
    merge_os_environ: Merge with os.environ variables (default: True)
    
Returns:
    Dictionary containing environment variables
    
Raises:
    FileNotFoundError: If .env file not found
"""
```

**Args**:

- `merge_os_environ`: If True, merges with `os.environ` (os.environ values take precedence)

#### `get_env(key: str, default: Optional[str] = None) -> Optional[str]`

```python
"""
Get .env value.

Args:
    key: Environment variable key
    default: Default value if key not found (default: None)
    
Returns:
    Environment variable value or default if not found
"""
```

#### `apply_env() -> None`

```python
"""
Apply loaded .env variables to os.environ.
"""
```

Apply loaded `.env` variables to `os.environ` globally.

#### `EnvLoader.clear_cache() -> None`

```python
"""
Clear cached environment variables.
"""
```

Clear cached environment variables (useful for testing).

#### `EnvLoader.load_env_file(force_reload: bool = False, merge_os_environ: bool = True, custom_path: Optional[str] = None) -> Dict[str, str]`

```python
"""
Load .env file and return as dictionary.

Args:
    force_reload: Force reload even if cached (default: False)
    merge_os_environ: Merge with os.environ variables (default: True)
    custom_path: Custom path to .env file (default: None)
    
Returns:
    Dictionary containing environment variables
    
Raises:
    FileNotFoundError: If .env file not found
    OSError: If file cannot be read
    IOError: If file read operation fails
"""
```

---

## Error Handling

### FileNotFoundError

Both loaders raise `FileNotFoundError` if configuration files cannot be found:

```python
from config import load_config

try:
    config = load_config()
except FileNotFoundError as e:
    print(f"Configuration not found: {e}")
    # Fallback logic or exit
```

### OSError / IOError

Specific file operation errors are caught and re-raised:

```python
from config import load_config

try:
    config = load_config()
except (OSError, IOError) as e:
    print(f"File operation failed: {e}")
```

### tomli.TOMLDecodeError

TOML parsing errors are propagated:

```python
from config import load_config
import sys

if sys.version_info >= (3, 11):
    import tomllib as tomli
else:
    import tomli

try:
    config = load_config()
except tomli.TOMLDecodeError as e:
    print(f"Invalid TOML syntax: {e}")
```

**Note**: Never catch generic `Exception` - all errors are specific and anticipated.

---

## Performance Characteristics

### Memory Usage

- **Cached TOML data**: ~1-2KB
- **Cached ENV data**: ~0.5-1KB
- **Total overhead**: <5KB

### CPU Usage

- **First access**: 10-15ms (file I/O + parsing)
- **Subsequent accesses**: <0.001ms (cached)
- **Path resolution**: <1ms (max ~20 file checks)

### Comparison with Direct Loading

```python
# OLD: Multiple direct loads
# Module A: 10ms
# Module B: 10ms  
# Module C: 10ms
# Total: 30ms + 3× file I/O

# NEW: Singleton pattern
# Module A: 10ms (loads + caches)
# Module B: <0.001ms (cached)
# Module C: <0.001ms (cached)
# Total: 10ms + 1× file I/O
```

---

## Testing

### Clearing Cache Between Tests

```python
from config import ConfigLoader, EnvLoader

def test_configuration():
    # Clear cache before test
    ConfigLoader().clear_cache()
    EnvLoader().clear_cache()
    
    # Your test code
    config = load_config()
    assert config['Server']['port'] == 8000
    
    # Clear cache after test (optional)
    ConfigLoader().clear_cache()
```

### Mocking Configuration

```python
import pytest
from unittest.mock import patch
from config import get_config

def test_with_mock_config():
    mock_config = {'Database': {'host': 'test-db'}}
    
    with patch('config.toml_loader._config_loader._config_toml', mock_config):
        assert get_config('Database', 'host') == 'test-db'
```

---

## Dependencies

### Python Standard Library

- **tomllib**: Built-in TOML parser (Python 3.11+)
- **pathlib**: Path manipulation
- **sys**: Version checking and argv parsing
- **os**: Environment variable access

### External Dependencies

- **tomli**: TOML parser for Python < 3.11
  - `tomli==2.0.1` for Python < 3.8
  - `tomli==2.0.2` for Python 3.8-3.10
- **display_tty**: Logging with structured output (Disp, initialise_logger)

### Library Priority

```python
if sys.version_info >= (3, 11):
    import tomllib as tomli  # stdlib
else:
    import tomli  # PyPI package
```

---

## Migration Guide

### Step 1: Update Imports

Replace hardcoded loading with config imports:

```python
# OLD
import dotenv
import toml
dotenv.load_dotenv(".env")
config = toml.load("config.toml")

# NEW
from config import get_config, get_env
```

### Step 2: Update Variable Access

```python
# OLD
DB_HOST = config['Database']['host']
API_KEY = os.environ.get('API_KEY')

# NEW
DB_HOST = get_config('Database', 'host')
API_KEY = get_env('API_KEY')
```

### Step 3: Remove Hardcoded Paths

Search for and remove:

- `dotenv.load_dotenv(".env")`
- `toml.load("config.toml")`
- Relative paths like `"../../config.toml"`

---

## Related Modules

- **core/**: Provides `RuntimeManager` for service management
- **utils/constants.py**: Uses config loaders for application constants
- All service modules: Load configuration via this module

---

## Code Quality Standards

### PEP 257 Compliance

All functions and classes have comprehensive docstrings following PEP 257:

- **Class docstrings**: Multi-line format with summary and detailed description
- **Method docstrings**: Include Args, Returns, and Raises sections
- **Private methods**: Documented even though they're internal
- **Imperative mood**: "Load config" not "Loads config"

### Exception Handling

- **No generic Exception**: Always catch specific exceptions (`OSError`, `IOError`)
- **Anticipated errors**: All error paths are explicitly handled
- **Proper propagation**: Errors raised with context for debugging

### Design Principles

- **No nested functions**: All functionality as class methods for clarity
- **Singleton pattern**: Thread-safe with `_initialized` flag
- **Logging levels**: `log_info` for initialization, `log_debug` for flow, `log_critical` for failures
- **Return type annotations**: All methods have explicit return types

## Future Enhancements

Potential improvements:

- Support for multiple environment files (`.env.local`, `.env.production`)
- JSON configuration support
- Configuration validation schemas (optionally using Pydantic)
- Hot-reloading for development
- Encrypted configuration values
- Configuration versioning and migrations
