r"""
# +==== BEGIN CatFeeder =================+
# LOGO:
# ..............(..../\
# ...............)..(.')
# ..............(../..)
# ...............\(__)|
# Inspired by Joan Stark
# source https://www.asciiart.eu/
# animals/cats
# /STOP
# PROJECT: CatFeeder
# FILE: server_management.py
# CREATION DATE: 11-10-2025
# LAST Modified: 3:34:56 13-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the file in charge of containing the functions that will manage the server run status.
# // AR
# +==== END CatFeeder =================+
"""


from typing import Optional, TYPE_CHECKING
import uvicorn
from fastapi import FastAPI, Response, BackgroundTasks as FastAPIBackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.asyncexitstack import AsyncExitStackMiddleware
from display_tty import Disp, initialise_logger

from .runtime_manager import RuntimeManager, RI
from .final_class import FinalClass
from . import core_const as CORE_CONST

from ..utils import constants as CONST
from ..http_codes import HCI, HTTP_DEFAULT_TYPE, HttpDataTypes

if TYPE_CHECKING:
    from ..sql import SQL
    from ..crons import BackgroundTasks
    from ..docs import DocumentationHandler
    from ..server_header import ServerHeaders
    from .runtime_controls import RuntimeControl
    from ..boilerplates import BoilerplateResponses


class ServerManagement(metaclass=FinalClass):
    """_summary_
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, error: int = 84, success: int = 0, debug: bool = False) -> None:
        """_summary_
        """
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self.error: int = error
        self.success: int = success
        self.debug: bool = debug
        # ----------------------- Shared instance handler ----------------------
        self.runtime_manager: RuntimeManager = RI
        # -------------------------- Shared instances --------------------------
        self.runtime_control: "RuntimeControl" = self.runtime_manager.get(
            "RuntimeControl")
        self.database_link: "SQL" = self.runtime_manager.get("SQL")
        self.background_tasks_initialised: Optional["BackgroundTasks"] = self.runtime_manager.get(
            "BackgroundTasks")
        self.boilerplate_responses_initialised: Optional["BoilerplateResponses"] = self.runtime_manager.get_if_exists(
            "BoilerplateResponses",
            None
        )
        self.server_headers: "ServerHeaders" = self.runtime_manager.get(
            "ServerHeaders")
        self.documentation_handler_initialised: Optional["DocumentationHandler"] = self.runtime_manager.get_if_exists(
            "DocumentationHandler",
            None
        )
        self.disp.log_debug("Initialised")

    def __del__(self) -> None:
        """_summary_
            The destructor of the class
        """
        self.disp.log_info(
            "Server sub processes are shutting down.",
            "__del__"
        )
        if self.is_server_alive() is True:
            del self.database_link
            self.runtime_control.continue_running = False
            if self.runtime_control.server is not None:
                self.runtime_control.graceful_shutdown()
                self.runtime_control.server = None
        if self.background_tasks_initialised is not None:
            del self.background_tasks_initialised
            self.background_tasks_initialised = None

    def is_server_alive(self) -> bool:
        """
            Check if the server is still running.
        Returns:
            bool: Returns True if it is running.
        """
        return self.runtime_control.continue_running

    def is_server_running(self) -> bool:
        """
            Check if the server is still running.
        Returns:
            bool: Returns True if it is running.
        """
        return self.is_server_alive()

    def _perform_shutdown(self) -> None:
        """Internal method to perform actual shutdown after response is sent"""
        if self.database_link.is_connected() is True:
            self.database_link.close()
        self.runtime_control.graceful_shutdown()

    async def shutdown(self, background_tasks: FastAPIBackgroundTasks) -> Response:
        """
            The function to shutdown the server
        Args:
            background_tasks: FastAPI's background tasks handler
        Returns:
            Response: Return the shutdown server message
        """
        self.boilerplate_responses_initialised = self.runtime_manager.get_if_exists(
            "BoilerplateResponses",
            self.boilerplate_responses_initialised
        )
        # Schedule shutdown to happen after response is sent
        background_tasks.add_task(self._perform_shutdown)

        if not self.boilerplate_responses_initialised:
            self.disp.log_error(
                "Boilerplate Responses class not present during shutdown request."
            )
            return HCI.service_unavailable(
                "Service component unavailable. Server is shutting down.",
                content_type=HttpDataTypes.TEXT,
                headers=self.server_headers.for_json()
            )
        body = self.boilerplate_responses_initialised.build_response_body(
            title="Shutdown",
            message="The server is shutting down.",
            resp="Shutdown",
            token="",
            error=False
        )
        return HCI.success(body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers.for_json())

    def _handle_documentation(self) -> None:
        self.documentation_handler_initialised: Optional["DocumentationHandler"] = self.runtime_manager.get_if_exists(
            "DocumentationHandler",
            self.documentation_handler_initialised
        )
        if not self.documentation_handler_initialised:
            self.disp.log_error(
                "No documentation handler during injection time, skipping injection"
            )
            return None
        self.documentation_handler_initialised.inject()
        return None

    # -------------------Initialisation-----------------------

    def initialise_classes(self) -> None:
        """
            The function to initialise the server classes
        """

        # ========= FastAPI app registration ==========
        self.runtime_control.app = FastAPI(
            # This allows Fastapi to send trace logs to the endpoint when it breaks.
            debug=self.debug,
            docs_url=None,
            redoc_url=None,
            openapi_url=None,
            # Disabled for security - OAuth2 handled separately
            swagger_ui_oauth2_redirect_url=None,
        )
        # ========= Documentation handling ==========
        self._handle_documentation()
        # ========== Middleware registration ==========
        # ......... GZip Middelware .........
        self.runtime_control.app.add_middleware(
            GZipMiddleware,
            minimum_size=CORE_CONST.GZIP_MINIMUM_SIZE,
            compresslevel=CORE_CONST.GZIP_COMPRESSION_LEVEL
        )
        # ......... Force HTTPS Middelware .........
        if CORE_CONST.SERVER_PROD_FORCE_HTTPS is True:
            self.runtime_control.app.add_middleware(HTTPSRedirectMiddleware)
        # ......... Middelware in charge of origin checking .........
        self.runtime_control.app.add_middleware(
            CORSMiddleware,
            allow_origins=CORE_CONST.CORS_ALLOW_ORIGINS,
            allow_credentials=CORE_CONST.CORS_ALLOW_CREDENTIALS,
            allow_methods=CORE_CONST.CORS_ALLOW_METHODS,
            allow_headers=CORE_CONST.CORS_ALLOW_HEADERS,
        )
        # ......... Trusted Host Middelware ..........
        self.runtime_control.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=CORE_CONST.TRUSTED_HOSTS_LIST
        )
        # ......... Async Exit Stack Middelware .........
        self.runtime_control.app.add_middleware(AsyncExitStackMiddleware)
        # ========= Uvicorn server configuration ==========
        msg = "uvicorn.Config(\n"
        msg += f"app='{self.runtime_control.app}',\n"
        msg += f"host='{self.server_headers.host}',\n"
        msg += f"port='{self.server_headers.port}',\n"
        msg += f"lifespan='{CONST.SERVER_LIFESPAN}',\n"
        msg += f"timeout_keep_alive='{CONST.SERVER_TIMEOUT_KEEP_ALIVE}',\n"
        msg += f"workers='{CONST.SERVER_WORKERS}',\n"
        msg += f"reload='{CONST.SERVER_DEV_RELOAD}',\n"
        msg += f"reload_dirs='{CONST.SERVER_DEV_RELOAD_DIRS}',\n"
        msg += f"log_level='{CONST.SERVER_DEV_LOG_LEVEL}',\n"
        msg += f"use_colors='{CONST.SERVER_DEV_USE_COLOURS}',\n"
        msg += f"proxy_headers='{CONST.SERVER_PROD_PROXY_HEADERS}',\n"
        msg += f"forwarded_allow_ips='{CONST.SERVER_PROD_FORWARDED_ALLOW_IPS}'"
        msg += "\n\n)"
        self.disp.log_debug(msg, "initialise_classes")
        self.runtime_control.config = uvicorn.Config(
            app=self.runtime_control.app,
            host=self.server_headers.host,
            port=self.server_headers.port,
            lifespan=CONST.SERVER_LIFESPAN,
            timeout_keep_alive=CONST.SERVER_TIMEOUT_KEEP_ALIVE,
            workers=CONST.SERVER_WORKERS,
            reload=CONST.SERVER_DEV_RELOAD,
            reload_dirs=CONST.SERVER_DEV_RELOAD_DIRS,
            log_level=CONST.SERVER_DEV_LOG_LEVEL,
            use_colors=CONST.SERVER_DEV_USE_COLOURS,
            proxy_headers=CONST.SERVER_PROD_PROXY_HEADERS,
            forwarded_allow_ips=CONST.SERVER_PROD_FORWARDED_ALLOW_IPS
        )
        # ========= Uvicorn server instance ==========
        self.runtime_control.server = uvicorn.Server(
            self.runtime_control.config)
        # ======== Set running flag ==========
        self.runtime_control.continue_running = True
