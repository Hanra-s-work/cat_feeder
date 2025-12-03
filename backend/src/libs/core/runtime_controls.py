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
# FILE: runtime_controls.py
# CREATION DATE: 24-11-2025
# LAST Modified: 4:42:9 27-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: Class in charge of tracking variables and some functions that aim to control the state of the server (this includes being able to stop it)
# // AR
# +==== END AsperBackend =================+
"""

import signal
from types import FrameType
from typing import Optional, TYPE_CHECKING
from display_tty import Disp, initialise_logger
from .final_singleton_class import FinalSingleton

if TYPE_CHECKING:
    from fastapi import FastAPI
    from uvicorn import Config as UConfig, Server as UServer


class RuntimeControl(FinalSingleton):
    """Runtime control manager for server state and lifecycle.

    This singleton class manages the server's runtime state, including the FastAPI application,
    uvicorn server instance, and server lifecycle flags. It provides methods for graceful
    shutdown and signal handling.

    Attributes:
        disp (Disp): Logger instance for this class.
        app (Optional[FastAPI]): The FastAPI application instance.
        config (Optional[uvicorn.Config]): The uvicorn server configuration.
        server (Optional[uvicorn.Server]): The uvicorn server instance.
        server_running (bool): Flag indicating if the server is currently running.
        continue_running (bool): Flag indicating if the server should continue running.
    """
    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, debug: bool = False) -> None:
        """Initialize the RuntimeControl singleton.

        Args:
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        super().__init__()
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self._debug = debug
        # --------------------- The rest api boiling class ---------------------
        self.app: Optional["FastAPI"] = None
        # ------------------------- The uvicorn server classes -------------------------
        self.config: Optional["UConfig"] = None
        self.server: Optional["UServer"] = None
        # ------------------------- The server Status  -------------------------
        self.server_running: bool = True
        self.continue_running: bool = True
        # --------------------- The rest api boiling class ---------------------
        self.disp.log_debug("Initialised")

    def handle_exit(self, sig: int = signal.SIGTERM, frame: Optional[FrameType] = None) -> None:
        """Handle system exit signals by delegating to uvicorn's signal handler.

        This method captures signals (SIGTERM, SIGINT, etc.) and passes them to uvicorn's
        built-in signal handler. Note that uvicorn will re-raise captured signals after
        shutdown, which may prevent cleanup code from executing. For graceful shutdown
        without signal handling, use graceful_shutdown() instead.

        Args:
            sig (int, optional): The signal number to handle. Defaults to signal.SIGTERM.
            frame (Optional[FrameType], optional): The current stack frame. Defaults to None.
        """
        if self.server:
            self.server.handle_exit(sig, frame)

    def graceful_shutdown(self) -> None:
        """Trigger a graceful server shutdown without signal handling.

        This method triggers uvicorn's graceful shutdown by setting the should_exit flag
        directly, avoiding signal capture and re-raising that would kill the process.
        This allows cleanup code in finally blocks to execute properly. Preferred over
        handle_exit() when shutdown is initiated programmatically (e.g., from an API endpoint).

        The method:
            1. Sets server_running and continue_running flags to False
            2. Sets uvicorn's should_exit flag to trigger graceful shutdown
            3. Logs debug messages for tracking shutdown progress

        Note:
            If no server instance exists, logs a warning and only updates the flags.
        """
        self.disp.log_debug("Triggering graceful shutdown...")
        self.server_running = False
        self.continue_running = False
        if self.server:
            self.server.should_exit = True
            self.disp.log_debug("Uvicorn shutdown flag set")
        else:
            self.disp.log_warning("No server instance to shutdown")
