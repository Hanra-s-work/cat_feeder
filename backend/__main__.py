""" 
# +==== BEGIN AsperBackend =================+
# LOGO: 
# ..........####...####..........
# ......###.....#.#########......
# ....##........#.###########....
# ...#..........#.############...
# ...#..........#.#####.######...
# ..#.....##....#.###..#...####..
# .#.....#.##...#.##..##########.
# #.....##########....##...######
# #.....#...##..#.##..####.######
# .#...##....##.#.##..###..#####.
# ..#.##......#.#.####...######..
# ..#...........#.#############..
# ..#...........#.#############..
# ...##.........#.############...
# ......#.......#.#########......
# .......#......#.########.......
# .........#####...#####.........
# /STOP
# PROJECT: AsperBackend
# FILE: __main__.py
# CREATION DATE: 11-10-2025
# LAST Modified: 5:29:6 02-12-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: The file in charge of allowing the files in this folder to be run as is, without any issues.
# // AR
# +==== END AsperBackend =================+
"""

import os
import sys
import time
from pathlib import Path
# Terminal Logging
from display_tty import Disp, initialise_logger

# File Logging functionalities
from rotary_logger import RotaryLogger, RL_CONST
LOG_PATH: Path = Path(__file__).parent
MERGE_STREAMS: bool = os.environ.get(
    "MERGE_STREAMS",
    "false"
).lower() in ("1", "true", "yes")
INSTANCE = RotaryLogger(
    merge_streams=MERGE_STREAMS,
    log_to_file=RL_CONST.LOG_TO_FILE_ENV,
    raw_log_folder=str(LOG_PATH),
    default_log_folder=LOG_PATH
)
INSTANCE.start_logging()


# Server name (local setting)
SERVER_NAME = "Asperbackend"

# Initialising the logger
IDISP: Disp = initialise_logger(f"'{SERVER_NAME}'", False)

# Startup message
IDISP.append_run_date()
IDISP.log_info(f"LOG_PATH: {LOG_PATH}")
IDISP.disp_message_box(f"Starting '{SERVER_NAME}'")
IDISP.log_info(f"Caller: '{sys.executable}")
IDISP.log_info(f"Caller prefix: '{sys.exec_prefix}'")
IDISP.log_info(f"Provided arguments: '{sys.argv}'")
IDISP.log_info(f"Argument count: '{len(sys.argv)}'")
IDISP.log_info(f"Python version: '{sys.version}")
IDISP.log_info(f"Byteorder: '{sys.byteorder}")
IDISP.log_info(f"Base exec prefix: '{sys.base_exec_prefix}'")
IDISP.log_info(
    f"Don't write bytecode: {'True' if sys.dont_write_bytecode else 'False'}"
)


IDISP.log_info("Attempting to import required dependencies...")
try:
    from .src.server_main import Main, CONST
except ImportError:
    from src.server_main import Main, CONST
IDISP.log_info("Required dependencies imported")

IDISP.log_info("Initialising the Main class...")
MI = Main(
    success=CONST.SUCCESS,
    error=CONST.ERROR
)
IDISP.log_info("Main class initialised")
IDISP.log_info("Calling main function...")

STATUS = CONST.ERROR
try:
    STATUS = MI.main()
    IDISP.log_info("Main function called")
except SystemExit as e:
    IDISP.log_info(f"SystemExit caught with code: {e.code}")
    STATUS = e.code if isinstance(e.code, int) else CONST.ERROR
except KeyboardInterrupt:
    IDISP.log_info("KeyboardInterrupt caught (Ctrl+C)")
    STATUS = CONST.SUCCESS
except Exception as e:
    IDISP.log_error(f"Unhandled exception: {type(e).__name__}: {e}")
    STATUS = CONST.ERROR
    raise
finally:
    # Shutdown message
    IDISP.log_info("Shutting down...")
    IDISP.append_run_date()
    IDISP.disp_message_box("The server has shut down")

    IDISP.log_info("Stopping rotary file logging...")
    try:
        INSTANCE.stop_logging()
        IDISP.log_info("Stopped rotary file logging")
    except Exception as cleanup_error:
        IDISP.log_error(f"Error during logging cleanup: {cleanup_error}")

    # Ensure all logs are flushed before exit
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(0.1)  # Small delay to ensure filesystem writes complete

# Only exit if we're not re-raising an exception
sys.exit(STATUS)
