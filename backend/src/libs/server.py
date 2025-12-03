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
# FILE: server.py
# CREATION DATE: 19-11-2025
# LAST Modified: 6:53:41 02-12-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: The main class required to set up the environement for the server to run properly.
# // AR
# +==== END AsperBackend =================+
"""

from display_tty import Disp, initialise_logger
from .sql import SQL
from .bucket import Bucket
from .e_mail import MailManagement
from .path_manager import PathManager
from .docs import DocumentationHandler
from .server_header import ServerHeaders
from .crons import BackgroundTasks, Crons
from .endpoint_manager import EndpointManager
from .utils import ServerManagement, CONST, OAuthAuthentication
from .core import FinalClass, RuntimeControl, RuntimeManager, RI
from .boilerplates import BoilerplateIncoming, BoilerplateNonHTTP, BoilerplateResponses


class Server(metaclass=FinalClass):
    """_summary_
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, host: str = "0.0.0.0", port: int = 5000, success: int = 0, error: int = 84, app_name: str = "Asperguide", debug: bool = False) -> None:
        """_summary_
            This is the class Server, a class that contains the structures used to allow the uvicorn and fastapi combo to run successfully.
            host (str, optional): _description_. Defaults to "0.0.0.0".
            port (int, optional): _description_. Defaults to 5000.
            character_folder (str, optional): _description_. Defaults to "".
            usr_db_path (str, optional): _description_. Defaults to "".
            success (int, optional): _description_. Defaults to 0.
            error (int, optional): _description_. Defaults to 84.
            app_name (str, optional): _description_. Defaults to "Desktop Pets".
            debug (bool, optional): _description_. Defaults to False.
        """
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # ---------------------   The inherited arguments  ---------------------
        self.host: str = host
        self.port: int = port
        self.success: int = success
        self.error: int = error
        self.debug: bool = debug
        self.app_name: str = app_name
        # ------------------------ Shared Runtime data  ------------------------
        self.runtime_manager: RuntimeManager = RI
        RuntimeManager.update_debug(self.debug)
        RI.update_debug(self.debug)
        # ----- The classes that need to be tracked for the server to run  -----
        self.runtime_manager.set(RuntimeControl)
        self.runtime_manager.set(
            ServerHeaders,
            **{
                "host": self.host,
                "port": self.port,
                "app_name": self.app_name,
                "error": self.error,
                "success": self.success,
                "debug": self.debug
            }
        )
        self.disp.log_debug("Initialising database link.", "__init__")
        self.runtime_manager.set(
            SQL,
            url=CONST.DB_HOST,
            port=CONST.DB_PORT,
            username=CONST.DB_USER,
            password=CONST.DB_PASSWORD,
            db_name=CONST.DB_DATABASE,
            success=self.success,
            error=self.error,
            debug=self.debug
        )
        self.runtime_manager.set(
            Bucket,
            **{"success": self.success, "error": self.error, "debug": self.debug}
        )
        self.runtime_manager.set(
            BackgroundTasks,
            **{"success": self.success, "error": self.error, "debug": self.debug}
        )
        self.runtime_manager.set(
            Crons,
            **{"success": self.success, "error": self.error, "debug": self.debug}
        )
        self.runtime_manager.set(
            ServerManagement,
            **{"success": self.success, "error": self.error, "debug": self.debug}
        )
        self.runtime_manager.set(
            BoilerplateResponses,
            **{"debug": self.debug}
        )
        self.runtime_manager.set(
            BoilerplateIncoming,
            **{"success": self.success, "error": self.error, "debug": self.debug}
        )
        self.runtime_manager.set(
            BoilerplateNonHTTP,
            **{"success": self.success, "error": self.error, "debug": self.debug}
        )
        self.runtime_manager.set(
            PathManager,
            **{"success": self.success, "error": self.error, "debug": self.debug}
        )
        self.runtime_manager.set(
            EndpointManager,
            **{"success": self.success, "error": self.error, "debug": self.debug}
        )
        self.runtime_manager.set(
            OAuthAuthentication,
            **{"success": self.success, "error": self.error, "debug": self.debug}
        )
        self.runtime_manager.set(
            MailManagement,
            **{"success": self.success, "error": self.error, "debug": self.debug}
        )
        self.runtime_manager.set(
            DocumentationHandler,
            **{"success": self.success, "error": self.error, "debug": self.debug}
        )
        #
        # -------------------------- Shared instances --------------------------
        self.server_management_initialised: ServerManagement = self.runtime_manager.get(
            ServerManagement)
        self.paths_initialised: PathManager = self.runtime_manager.get(
            PathManager)
        self.crons_initialised: Crons = self.runtime_manager.get(Crons)
        self.background_tasks_initialised: BackgroundTasks = self.runtime_manager.get(
            BackgroundTasks)
        self.runtime_control: RuntimeControl = self.runtime_manager.get(
            RuntimeControl)
        self.sql_connection: SQL = self.runtime_manager.get(SQL)
        self.disp.log_debug("Initialised")

    def __del__(self) -> None:
        """_summary_
            The destructor of the class.
        """
        self.disp.log_info("The server is shutting down.", "__del__")
        self.stop_server()

    def main(self) -> int:
        """_summary_
            The main function of the server.
            This is the one in charge of starting the server.

        Returns:
            int: _description_
        """
        self.server_management_initialised.initialise_classes()
        self.paths_initialised.load_default_paths_initialised()
        self.paths_initialised.inject_routes()
        self.crons_initialised.inject_crons()
        status = self.background_tasks_initialised.safe_start()
        if status != self.success:
            self.disp.log_error(
                "Error: background tasks failed to start.",
                "main"
            )
            return status
        try:
            if not self.runtime_control.server:
                raise RuntimeError("No server to start")
            self.runtime_control.server.run()
        except Exception as e:
            self.disp.log_error(f"Error: {e}", "main")
            return self.error
        return self.success

    def is_running(self) -> bool:
        """_summary_
            The function in charge of checking if the server is running.

        Returns:
            bool: _description_: Returns True if the server is running.
        """
        return self.server_management_initialised.is_server_running()

    def stop_server(self) -> None:
        """_summary_
            The function in charge of stopping the server.
        """
        title = "stop_server"
        self.disp.log_info("Stopping server", title)
        if hasattr(self, "server_management_initialised") and self.server_management_initialised is not None:
            del self.server_management_initialised
        if hasattr(self, "crons_initialised") and self.crons_initialised is not None:
            del self.crons_initialised
        self.disp.log_info("Server stopped", title)
