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
-- FILE: server_main.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 14:33:20 02-12-2025
-- DESCRIPTION: 
-- This is the project in charge of making the connected cat feeder project work.
-- /STOP
-- COPYRIGHT: (c) Cat Feeder
-- PURPOSE: The structure of the very first class initialised and called by the program (it is in charge of processing input arguments)
-- // AR
-- +==== END CatFeeder =================+
-->
# Server Main Entry Point

## Overview

**server_main.py** is the primary entry point for running the Cat Feeder backend server in standalone mode. It provides command-line argument parsing and bootstraps the Server class.

**Location**: `backend/src/server_main.py`

## Purpose

1. **Command-Line Interface**: Parse startup arguments (host, port, debug mode)
2. **Server Bootstrap**: Create and launch the Server instance
3. **Argument Validation**: Validate and process CLI options
4. **Help System**: Provide usage information

## Main Class

```python
class Main(metaclass=FinalClass):
    """Bootstrapper for launching the server in standalone mode."""
    
    def __init__(self, success: int = 0, error: int = 84):
        self.argc = len(argv)
        self.host: str = "0.0.0.0"
        self.port: int = 5000
        self.success: int = success
        self.error: int = error
        self.app_name: str = "Cat Feeder"
        self.debug: bool = False
    
    def process_args(self) -> None:
        """Parse command-line arguments."""
        # Processes --host, --port, --debug, --help, etc.
    
    def main(self) -> int:
        """Launch the server."""
        self.process_args()
        server = Server(
            host=self.host,
            port=self.port,
            app_name=self.app_name,
            debug=self.debug
        )
        return server.main()
```

## Command-Line Arguments

### Supported Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--host=<host>` | - | Server bind address | `0.0.0.0` |
| `--port=<port>` | `-p <port>` | Server port | `5000` |
| `--success=<n>` | `-s <n>` | Success exit code | `0` |
| `--error=<n>` | `-e <n>` | Error exit code | `84` |
| `--debug` | - | Enable debug mode | `false` |
| `--help` | `-h` | Show help message | - |

### Usage Examples

```bash
# Default settings (0.0.0.0:5000)
python -m backend.src

# Custom host and port
python -m backend.src --host=localhost --port=8000

# Short form for port
python -m backend.src -p 8080

# Debug mode
python -m backend.src --debug

# Custom exit codes
python -m backend.src --success=0 --error=1

# Show help
python -m backend.src --help
```

## Execution Flow

1. **Parse Arguments**: `process_args()` processes CLI options
2. **Create Server**: Instantiate `Server` with parsed config
3. **Launch Server**: Call `server.main()` to start Uvicorn
4. **Return Exit Code**: Exit with success/error code

## Import Handling

The module handles both direct and package imports:

```python
try:
    from .libs import Server, CONST, FinalClass
except ImportError:
    from libs import Server, CONST, FinalClass
```

This allows running as:

- `python -m backend.src` (package import)
- `python backend/src/server_main.py` (direct import)

## Integration with Server

```python
def main(self) -> int:
    """Main entry point."""
    self.process_args()
    
    server = Server(
        host=self.host,
        port=self.port,
        success=self.success,
        error=self.error,
        app_name=self.app_name,
        debug=self.debug
    )
    
    try:
        return server.main()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return self.success
    except Exception as e:
        print(f"Server error: {e}")
        return self.error
```

## Design Patterns

### Final Class Pattern

Uses `FinalClass` metaclass to prevent inheritance:

```python
class Main(metaclass=FinalClass):
    pass

# This would raise TypeError:
# class DerivedMain(Main):
#     pass
```

**Rationale**: Main is a bootstrapper that should not be extended.

## Related Documentation

- [server/server.md](../server/server.md) - Server orchestration
- [core/core.md](../core/core.md) - FinalClass metaclass
- [00_ARCHITECTURE.md](../00_ARCHITECTURE.md) - System architecture
