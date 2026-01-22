"""
# +==== BEGIN CatFeeder =================+
# LOGO:
# ..............(..../\\
# ...............)..(.')
# ..............(../..)
# ...............\\(__)|
# Inspired by Joan Stark
# source https://www.asciiart.eu/
# animals/cats
# /STOP
# PROJECT: CatFeeder
# FILE: admin.py
# CREATION DATE: 04-01-2026
# LAST Modified: 8:43:1 22-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The endpoints that are only accessible by the administrators of the server.
# // AR
# +==== END CatFeeder =================+
"""
from typing import TYPE_CHECKING, Union, List, Dict, Any, Optional
from display_tty import Disp, initialise_logger
from fastapi import Request, Response
from ...core import RuntimeManager, RI
from ...utils import constants as CONST
from ...http_codes import HCI, HttpDataTypes, HTTP_DEFAULT_TYPE
from ...favicon import FAV_ERR, favicon_constants as FAV_CONST
from .. import endpoint_helpers as EP_HELPERS, endpoint_constants as EP_CONST

if TYPE_CHECKING:
    from ...sql import SQL
    from ...server_header import ServerHeaders
    from ...favicon.favicon_admin import FaviconAdmin
    from ...boilerplates import BoilerplateIncoming, BoilerplateResponses, BoilerplateNonHTTP


class AdminEndpoints:
    """Handle user-related HTTP endpoints.

    The class implements endpoints for authentication, registration,
    password reset, profile management, email verification and session
    management used by the CatFeeder backend.
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
        self.runtime_manager: RuntimeManager = RI
        # -------------------------- Shared instances --------------------------
        self.boilerplate_incoming_initialised: "BoilerplateIncoming" = self.runtime_manager.get(
            "BoilerplateIncoming")
        self.boilerplate_responses_initialised: "BoilerplateResponses" = self.runtime_manager.get(
            "BoilerplateResponses")
        self.boilerplate_non_http_initialised: "BoilerplateNonHTTP" = self.runtime_manager.get(
            "BoilerplateNonHTTP")
        self.database_link: "SQL" = self.runtime_manager.get("SQL")
        self.server_headers_initialised: "ServerHeaders" = self.runtime_manager.get(
            "ServerHeaders")
        self.favicon_admin: Optional["FaviconAdmin"] = self.runtime_manager.get_if_exists(
            "FaviconAdmin", None)
        self.disp.log_debug("Initialised")

    def _get_admin_token(self, title: str, request: Request) -> Union[Response, str]:
        """Get the token of the user if they are administrator, otherwise, return the correct http response.

        Args:
            title (str): The title of the endpoint calling this function.
            request (Request): The incoming request parameters

        Returns:
            Union[Response, str]: The response if an error occurred, the token otherwise.
        """
        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        if not token:
            return self.boilerplate_responses_initialised.invalid_token(title)
        if not self.boilerplate_non_http_initialised.is_token_correct(token):
            return self.boilerplate_responses_initialised.invalid_token(title)
        if not self.boilerplate_non_http_initialised.is_token_admin(token):
            return self.boilerplate_responses_initialised.insuffisant_rights(title, token)
        return token
