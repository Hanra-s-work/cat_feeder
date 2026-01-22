""" 
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
# FILE: cat_endpoints.py
# CREATION DATE: 08-12-2025
# LAST Modified: 14:24:8 22-01-2026
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the file containing the endpoints used for the application of the cat feeder.
# // AR
# +==== END CatFeeder =================+
"""
from typing import TYPE_CHECKING
from display_tty import Disp, initialise_logger
from fastapi import Request, Response
from ...core import RuntimeManager, RI
from ...utils import PasswordHandling
from ...e_mail import MailManagement
from ...http_codes import HCI, HTTP_DEFAULT_TYPE

if TYPE_CHECKING:
    from typing import List, Dict
    from ...sql import SQL
    from ...server_header import ServerHeaders
    from ...boilerplates import BoilerplateIncoming, BoilerplateResponses, BoilerplateNonHTTP


class CatEndpoints:

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
        # ------------------------ The password checker ------------------------
        if not self.runtime_manager.exists("PasswordHandling"):
            self.runtime_manager.set(
                PasswordHandling,
                error=self.error,
                success=self.success,
                debug=self.debug
            )
        self.password_handling_initialised: PasswordHandling = self.runtime_manager.get(
            "PasswordHandling")
        # ---------------------------- Mail sending ----------------------------
        if not self.runtime_manager.exists("MailManagement"):
            self.runtime_manager.set(
                MailManagement,
                **{
                    "error": self.error,
                    "success": self.success,
                    "debug": self.debug
                }
            )
        self.mail_management_initialised: MailManagement = self.runtime_manager.get(
            "MailManagement")
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
        self.disp.log_debug("Initialised")
