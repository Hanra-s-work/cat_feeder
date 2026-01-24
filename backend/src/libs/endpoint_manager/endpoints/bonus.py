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
# FILE: bonus.py
# CREATION DATE: 19-11-2025
# LAST Modified: 0:15:46 25-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The endpoints that can be considered as bonus in the server.
# // AR
# +==== END CatFeeder =================+
"""

import os
from display_tty import Disp, initialise_logger
from fastapi import Request, Response
from ...core import RuntimeControl, RuntimeManager, RI
from ...crons import BackgroundTasks
from ...server_header import ServerHeaders
from ...utils import constants as CONST
from ...http_codes import HCI, HttpDataTypes, HTTP_DEFAULT_TYPE
from ...boilerplates import BoilerplateIncoming, BoilerplateResponses, BoilerplateNonHTTP


class Bonus:
    """_summary_
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """_summary_

        Args:
            runtime_data (RuntimeData): _description_
            success (int, optional): _description_. Defaults to 0.
            error (int, optional): _description_. Defaults to 84.
            debug (bool, optional): _description_. Defaults to False.
        """
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self.debug: bool = debug
        self.success: int = success
        self.error: int = error
        self.runtime_manager: RuntimeManager = RI
        # -------------------------- Shared instances --------------------------
        self.boilerplate_incoming_initialised: BoilerplateIncoming = self.runtime_manager.get(
            BoilerplateIncoming)
        self.boilerplate_responses_initialised: BoilerplateResponses = self.runtime_manager.get(
            BoilerplateResponses)
        self.boilerplate_non_http_initialised: BoilerplateNonHTTP = self.runtime_manager.get(
            BoilerplateNonHTTP)
        self.runtime_controls_initialised: RuntimeControl = self.runtime_manager.get(
            RuntimeControl)
        self.server_headers_initialised: ServerHeaders = self.runtime_manager.get(
            ServerHeaders)
        self.background_tasks_initialised: BackgroundTasks = self.runtime_manager.get(
            BackgroundTasks)
        self.disp.log_debug("Initialised")

    async def get_welcome(self, request: Request) -> Response:
        """_summary_
            The endpoint corresponding to ''.

        Returns:
            Response: _description_: The data to send back to the user as a response.
        """
        title = "get_welcome"
        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request)
        body = self.boilerplate_responses_initialised.build_response_body(
            title="Home",
            message="Welcome to the cat_feeder server.",
            resp="",
            token=token,
            error=False
        )
        self.disp.log_debug(f"sent body : {body}", title)
        self.disp.log_debug(
            f"header = {self.server_headers_initialised.for_json()}", title
        )
        outgoing = HCI.success(
            content=body,
            content_type=HTTP_DEFAULT_TYPE,
            headers=self.server_headers_initialised.for_json()
        )
        self.disp.log_debug(f"ready_to_go: {outgoing}", title)
        return outgoing

    async def get_root(self, request: Request) -> Response:
        """_summary_
            The endpoint corresponding to '/'.

        Returns:
            Response: _description_: The data to send back to the user as a response.
        """
        title = "get_root"
        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request)
        body = self.boilerplate_responses_initialised.build_response_body(
            title="root",
            message="Welcome to the cat_feeder server.",
            resp="/",
            token=token,
            error=False
        )
        self.disp.log_debug(f"sent body : {body}", title)
        self.disp.log_debug(
            f"header = {self.server_headers_initialised.for_json()}", title
        )
        outgoing = HCI.success(
            content=body,
            content_type=HTTP_DEFAULT_TYPE,
            headers=self.server_headers_initialised.for_json()
        )
        self.disp.log_debug(f"ready_to_go: {outgoing}", title)
        return outgoing

    async def get_api_v1(self, request: Request) -> Response:
        """_summary_
            The endpoint corresponding to '/'.

        Returns:
            Response: _description_: The data to send back to the user as a response.
        """
        title = "get_api_v1"
        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request)
        body = self.boilerplate_responses_initialised.build_response_body(
            title="api_v1",
            message="Welcome to the cat_feeder server.",
            resp="/api/v1",
            token=token,
            error=False
        )
        self.disp.log_debug(f"sent body : {body}", title)
        self.disp.log_debug(
            f"header = {self.server_headers_initialised.for_json()}", title
        )
        outgoing = HCI.success(
            content=body,
            content_type=HTTP_DEFAULT_TYPE,
            headers=self.server_headers_initialised.for_json()
        )
        self.disp.log_debug(f"ready_to_go: {outgoing}", title)
        return outgoing

    async def get_favicon(self, request: Request) -> Response:
        """The endpoint to respond to the typical GET /favicon.ico path.

        Args:
            request (Request): The potential arguments passed in the emitted request.

        Returns:
            Response: The response to the emmiter.
        """
        icon = CONST.ICON_PATH
        self.disp.log_debug(f"Favicon path: {icon}")
        if os.path.isfile(icon):
            return HCI.success(icon, content_type=HttpDataTypes.XICON)
        return HCI.not_found("Icon not found in the expected directory", content_type=HttpDataTypes.TEXT)

    async def get_static_logo(self, request: Request) -> Response:
        """The endpoint to respond to the typical GET /static/logo.png path.

        Args:
            request (Request): The potential arguments passed in the emitted request.

        Returns:
            Response: The response to the emmiter.
        """
        icon = CONST.PNG_ICON_PATH
        self.disp.log_debug(f"Static logo path: {icon}")
        if os.path.isfile(icon):
            return HCI.success(icon, content_type=HttpDataTypes.PNG)
        return HCI.not_found("Icon not found in the expected directory", content_type=HttpDataTypes.TEXT)

    async def post_stop_server(self, request: Request) -> Response:
        """_summary_
            The endpoint allowing a user to stop the server.

        Returns:
            Response: _description_: The data to send back to the user as a response.
        """
        title = "Stop server"
        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        if not token:
            self.disp.log_error(
                "Unauthenticated user tried to stop the server."
            )
            return self.boilerplate_responses_initialised.no_access_token(title=title, token=token)
        if self.boilerplate_non_http_initialised.is_token_admin(token) is False:
            self.disp.log_error(
                "Non-admin user tried to stop the server.", title
            )
            body = self.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="You do not have enough privileges to run this endpoint.",
                resp="privilege to low",
                token=token,
                error=True
            )
            return HCI.unauthorized(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())
        body = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The server is stopping",
            resp="success",
            token=token,
            error=False
        )
        self.disp.log_debug("Server shutting down...", f"{title}")
        # Trigger graceful shutdown without signal capture
        self.runtime_controls_initialised.graceful_shutdown()
        status = self.background_tasks_initialised.safe_stop()
        if status != self.success:
            msg = "The server is stopping with errors, cron exited "
            msg += f"with {status}."
            self.disp.log_error(
                msg,
                "post_stop_server"
            )
            body = self.boilerplate_responses_initialised.build_response_body(
                title=title,
                message=msg,
                resp="error",
                token=token,
                error=True
            )
            del self.background_tasks_initialised
            return HCI.internal_server_error(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())
        return HCI.success(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    async def get_health(self, request: Request) -> Response:
        """Health check endpoint for container orchestration and monitoring.

        Returns a simple 200 OK response to indicate the service is alive and responding.
        Used by Docker healthchecks, Kubernetes probes, load balancers, etc.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: HTTP 200 with status message.
        """
        body = self.boilerplate_responses_initialised.build_response_body(
            title="Health Check",
            message="Service is healthy",
            resp="ok",
            token=None,
            error=False
        )
        return HCI.success(
            content=body,
            content_type=HTTP_DEFAULT_TYPE,
            headers=self.server_headers_initialised.for_json()
        )

    # Dedicated beacon endpoint functions to avoid OpenAPI Operation ID conflicts
    async def root_beacon_get(self, request: Request) -> Response:
        """Root GET beacon endpoint."""
        return await self.get_welcome(request)

    async def root_beacon_post(self, request: Request) -> Response:
        """Root POST beacon endpoint."""
        return await self.get_welcome(request)

    async def root_beacon_put(self, request: Request) -> Response:
        """Root PUT beacon endpoint."""
        return await self.get_welcome(request)

    async def root_beacon_patch(self, request: Request) -> Response:
        """Root PATCH beacon endpoint."""
        return await self.get_welcome(request)

    async def root_beacon_delete(self, request: Request) -> Response:
        """Root DELETE beacon endpoint."""
        return await self.get_welcome(request)

    async def root_beacon_head(self, request: Request) -> Response:
        """Root HEAD beacon endpoint."""
        return await self.get_welcome(request)

    async def root_beacon_options(self, request: Request) -> Response:
        """Root OPTIONS beacon endpoint."""
        return await self.get_welcome(request)

    # Home beacon functions
    async def home_beacon_get(self, request: Request) -> Response:
        """Home GET beacon endpoint."""
        return await self.get_root(request)

    async def home_beacon_post(self, request: Request) -> Response:
        """Home POST beacon endpoint."""
        return await self.get_root(request)

    async def home_beacon_put(self, request: Request) -> Response:
        """Home PUT beacon endpoint."""
        return await self.get_root(request)

    async def home_beacon_patch(self, request: Request) -> Response:
        """Home PATCH beacon endpoint."""
        return await self.get_root(request)

    async def home_beacon_delete(self, request: Request) -> Response:
        """Home DELETE beacon endpoint."""
        return await self.get_root(request)

    async def home_beacon_head(self, request: Request) -> Response:
        """Home HEAD beacon endpoint."""
        return await self.get_root(request)

    async def home_beacon_options(self, request: Request) -> Response:
        """Home OPTIONS beacon endpoint."""
        return await self.get_root(request)

    # API v1 beacon functions
    async def api_v1_beacon_get(self, request: Request) -> Response:
        """API v1 GET beacon endpoint."""
        return await self.get_api_v1(request)

    async def api_v1_beacon_post(self, request: Request) -> Response:
        """API v1 POST beacon endpoint."""
        return await self.get_api_v1(request)

    async def api_v1_beacon_put(self, request: Request) -> Response:
        """API v1 PUT beacon endpoint."""
        return await self.get_api_v1(request)

    async def api_v1_beacon_patch(self, request: Request) -> Response:
        """API v1 PATCH beacon endpoint."""
        return await self.get_api_v1(request)

    async def api_v1_beacon_delete(self, request: Request) -> Response:
        """API v1 DELETE beacon endpoint."""
        return await self.get_api_v1(request)

    async def api_v1_beacon_head(self, request: Request) -> Response:
        """API v1 HEAD beacon endpoint."""
        return await self.get_api_v1(request)

    async def api_v1_beacon_options(self, request: Request) -> Response:
        """API v1 OPTIONS beacon endpoint."""
        return await self.get_api_v1(request)
