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
-- FILE: crons.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 15:22:45 02-12-2025
-- DESCRIPTION: 
-- This is the project in charge of making the connected cat feeder project work.
-- /STOP
-- COPYRIGHT: (c) Cat Feeder
-- PURPOSE: The overview of the cron module.
-- // AR
-- +==== END CatFeeder =================+
-->
# Crons Module

## Overview

The crons module provides background task scheduling and management capabilities using APScheduler. It consists of two main classes that work together to schedule and execute recurring tasks in the backend server.

**Location:** `backend/src/libs/crons/`

**Key Components:**

- `BackgroundTasks` - Core scheduler wrapper for APScheduler
- `Crons` - High-level task manager with predefined maintenance jobs
- `crons_constants.py` - Configuration constants loaded from TOML

## Architecture

See [crons_architecture.puml](crons_architecture.puml) for visual representation.

## Core Classes

### BackgroundTasks

A final class that wraps APScheduler's `BackgroundScheduler` to provide safe, non-crashing task scheduling.

**Purpose:** Provides a robust interface for scheduling background tasks with error handling and graceful degradation.

**Key Features:**

- Non-breaking task operations with `safe_*` methods
- Automatic scheduler lifecycle management
- Support for interval and cron-based triggers
- Comprehensive logging and error handling

**Constructor:**

```python
BackgroundTasks(success: int = 0, error: int = 84, debug: bool = False)
```

**Key Methods:**

| Method | Description |
|--------|-------------|
| `safe_add_task()` | Add a task without crashing on errors |
| `safe_start()` | Start the scheduler safely |
| `safe_pause()` | Pause the scheduler |
| `safe_resume()` | Resume a paused scheduler |
| `safe_stop()` | Stop the scheduler and optionally wait for tasks |
| `add_task()` | Direct task addition (can raise exceptions) |

**Task Configuration:**

```python
def safe_add_task(
    func: Callable,
    args: Union[Tuple, None] = None,
    kwargs: Union[Dict, None] = None,
    trigger: Union[str, Any] = "interval",
    seconds: int = 5
) -> Union[int, Job]
```

### Crons

A final class that manages predefined background tasks for server maintenance.

**Purpose:** Orchestrates scheduled maintenance tasks like token cleanup, verification cleanup, and OAuth token renewal.

**Key Features:**

- Database cleanup tasks
- OAuth token renewal
- Configurable task intervals via TOML
- Optional test/debug cron jobs
- Runtime integration with SQL, OAuth, and boilerplate classes

**Constructor:**

```python
Crons(error: int = 84, success: int = 0, debug: bool = False)
```

**Predefined Tasks:**

| Task | Description | Enabled By | Interval Constant |
|------|-------------|-----------|-------------------|
| `check_actions()` | General action checking | Always | `CHECK_ACTIONS_INTERVAL` |
| `clean_expired_tokens()` | Remove expired auth tokens | `CLEAN_TOKENS` | `CLEAN_TOKENS_INTERVAL` |
| `clean_expired_verification_nodes()` | Remove expired verification entries | `CLEAN_VERIFICATION` | `CLEAN_VERIFICATION_INTERVAL` |
| `renew_oaths()` | Renew OAuth tokens | `RENEW_OATH_TOKENS` | `RENEW_OATH_TOKENS_INTERVAL` |
| `_test_hello_world()` | Test cron (debug) | `ENABLE_TEST_CRONS` | `TEST_CRONS_INTERVAL` |
| `_test_current_date()` | Test cron with date (debug) | `ENABLE_TEST_CRONS` | `TEST_CRONS_INTERVAL` |

## Configuration (crons_constants.py)

Configuration is loaded from `config.toml` using the `_get_toml_variable()` function.

**Key Constants:**

```python
# Enable/disable specific cron jobs
ENABLE_TEST_CRONS: bool
CLEAN_TOKENS: bool
CLEAN_VERIFICATION: bool
RENEW_OATH_TOKENS: bool

# Task intervals (in seconds)
CHECK_ACTIONS_INTERVAL: int
TEST_CRONS_INTERVAL: int
CLEAN_TOKENS_INTERVAL: int
CLEAN_VERIFICATION_INTERVAL: int
RENEW_OATH_TOKENS_INTERVAL: int
```

## APScheduler Integration

The module leverages APScheduler's `BackgroundScheduler`:

**Trigger Types:**

- `interval` - Execute at fixed time intervals (most common)
- `cron` - Execute using cron-like scheduling expressions
- `date` - Execute once at a specific datetime

**Job Management:**

- Jobs are added via `scheduler.add_job()`
- Returns `Job` instance for monitoring/manipulation
- Scheduler runs in a background thread
- Graceful shutdown via destructor

## Usage Examples

### Example 1: Basic Task Scheduling

```python
from backend.src.libs.crons import BackgroundTasks

# Initialize scheduler
background = BackgroundTasks(debug=True)

# Define a task function
def cleanup_task():
    print("Running cleanup...")
    # Cleanup logic here

# Add task to run every 60 seconds
background.safe_add_task(
    func=cleanup_task,
    trigger='interval',
    seconds=60
)

# Start the scheduler
background.safe_start()
```

### Example 2: Task with Arguments

```python
def send_notification(user_id: int, message: str):
    print(f"Notifying user {user_id}: {message}")

# Add task with arguments
background.safe_add_task(
    func=send_notification,
    args=(123,),  # positional args as tuple
    kwargs={'message': 'Hello!'},  # keyword args as dict
    trigger='interval',
    seconds=300  # every 5 minutes
)
```

### Example 3: Using the Crons Manager

```python
from backend.src.libs.crons import Crons

# Initialize with dependencies already in RuntimeManager
crons_manager = Crons(debug=True)

# Inject all predefined tasks
crons_manager.inject_crons()

# Scheduler starts automatically when BackgroundTasks is initialized
# Tasks will run according to their configured intervals
```

### Example 4: Manual Token Cleanup

```python
# Access the crons manager (typically from RuntimeManager)
crons_manager = RI.get(Crons)

# Manually trigger cleanup (normally runs automatically)
crons_manager.clean_expired_tokens()
crons_manager.clean_expired_verification_nodes()
```

## Error Handling

**Safe Methods Pattern:**
All critical operations have `safe_*` variants that catch exceptions and return status codes:

```python
# Returns self.error (84) on failure, Job instance on success
result = background.safe_add_task(func=my_task)

if isinstance(result, int) and result == background.error:
    print("Failed to add task")
else:
    print(f"Task added successfully: {result}")
```

**Exception Handling:**

- `ValueError` - Invalid function, trigger, or parameters
- `RuntimeError` - Scheduler state issues
- `SchedulerAlreadyRunningError` - Attempting to start running scheduler
- `SchedulerNotRunningError` - Attempting to stop/pause inactive scheduler

## Lifecycle Management

**Initialization:**

1. `BackgroundTasks` creates `BackgroundScheduler` instance
2. `Crons` retrieves/creates `BackgroundTasks` from `RuntimeManager`
3. Database and OAuth connections are established
4. `inject_crons()` adds all enabled tasks

**Execution:**

1. Tasks run in background threads
2. Database operations performed via `SQL` instance
3. Logging via `display_tty.Disp`
4. Errors are logged, execution continues

**Shutdown:**

1. `Crons.__del__()` called on shutdown
2. `BackgroundTasks.__del__()` calls `safe_stop()`
3. Scheduler waits for running tasks (if `wait=True`)
4. All resources released

## Best Practices

1. **Always use `safe_*` methods** in production code
2. **Keep task functions lightweight** - long-running tasks block the scheduler
3. **Use appropriate intervals** - balance between responsiveness and resource usage
4. **Log task execution** - helps debugging scheduled operations
5. **Handle database failures gracefully** - tasks should not crash on DB errors
6. **Test with `ENABLE_TEST_CRONS`** before deploying new tasks
7. **Monitor task execution times** - adjust intervals if tasks overlap
8. **Use TOML configuration** for easy interval adjustments without code changes

## Dependencies

- `apscheduler` - Background scheduling engine
- `display_tty` - Logging functionality
- `backend.src.libs.core` - `FinalClass`, `RuntimeManager`
- `backend.src.libs.sql` - Database operations
- `backend.src.libs.utils` - OAuth and server utilities
- `backend.src.libs.boilerplates` - Non-HTTP boilerplate operations

## Related Modules

- [SQL](../sql/sql.md) - Database operations used by cleanup tasks
- [Utils](../utils/utils.md) - OAuth authentication and server management
- [Core](../core/core.md) - Runtime management and final class pattern
