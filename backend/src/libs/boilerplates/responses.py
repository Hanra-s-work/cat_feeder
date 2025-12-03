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
# FILE: responses.py
# CREATION DATE: 11-10-2025
# LAST Modified: 9:49:51 27-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: File containing boilerplate responses that could be used by the server in it's endpoints_initialised.
# // AR
# +==== END AsperBackend =================+
"""

from typing import Union, Dict, Any, Optional
from fastapi import Response
from display_tty import Disp, initialise_logger
from .non_web import BoilerplateNonHTTP
from ..core import FinalSingleton
from ..utils import constants as CONST
from ..core.runtime_manager import RuntimeManager, RI
from ..server_header import ServerHeaders
from ..http_codes import HCI, HTTP_DEFAULT_TYPE


class BoilerplateResponses(FinalSingleton):
    """_summary_
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self,  debug: bool = False) -> None:
        """_summary_

        Args:
            debug (bool, optional): _description_. Defaults to False.
        """
        super().__init__()
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self.debug: bool = debug
        self.runtime_manager: RuntimeManager = RI
        # -------------------------- Shared instances --------------------------
        self.boilerplate_non_http_initialised: Optional[BoilerplateNonHTTP] = self.runtime_manager.get_if_exists(
            BoilerplateNonHTTP, None)
        self.server_headers_initialised: ServerHeaders = self.runtime_manager.get(
            ServerHeaders)

        self.disp.log_debug("Initialised")

    def build_response_body(self, title: str, message: str, resp: Any, token: Optional[str], error: bool = False) -> Dict[str, Any]:
        """_summary_
            This is a function that will create a response body for the queries of the server.
        Args:
            title (str): _description_: The title of the message in the body
            message (any): _description_: The actual message you wish to send (this is so that it is human friendly [i.e. "You have successfully logged in"])
            resp (any): _description_: The section where you can put more coder side data.
            token Union[str, None]: _description_: The user token or None if not present
            error (bool, optional): _description_: If this is an error message or not. Defaults to False.

        Returns:
            Dict[str, any]: _description_: the final version of the body message
        """
        func_title = "build_response_body"
        json_body = {}
        msg = f"title={title}, message={message}, resp={resp},"
        msg += f"token={token}, error={error}"
        self.disp.log_debug(msg, func_title)

        json_body[CONST.JSON_TITLE] = title
        json_body[CONST.JSON_MESSAGE] = message
        if error is False:
            json_body[CONST.JSON_RESP] = resp
        else:
            json_body[CONST.JSON_ERROR] = resp
        self.disp.log_debug(f"token = {token}", func_title)
        self.boilerplate_non_http_initialised = self.runtime_manager.get_if_exists(
            BoilerplateNonHTTP,
            self.boilerplate_non_http_initialised
        )
        if not self.boilerplate_non_http_initialised:
            self.disp.log_warning(
                "Token validation service unavailable, unable to verify authentication status",
                func_title
            )
            json_body[CONST.JSON_LOGGED_IN] = None
        else:
            if token:
                json_body[CONST.JSON_LOGGED_IN] = self.boilerplate_non_http_initialised.is_token_correct(
                    token
                )
            else:
                json_body[CONST.JSON_LOGGED_IN] = False
        return json_body

    def invalid_token(self, title: str) -> Response:
        """_summary_
            This is a function that will return an invalid token response.

        Args:
            title (str): _description_: The title of the called endpoint

        Returns:
            Response: _description_: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="The token you entered is invalid.",
            resp="Invalid token",
            token="",
            error=True
        )
        return HCI.invalid_token(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    def no_access_token(self, title: str, token: Union[str, None] = None) -> Response:
        """_summary_
            This is a function that will return a no access token response.

        Args:
            title (str): _description_: The name of the endpoint that is concerned
            token (str): _description_: The token corresponding to the user being logged in

        Returns:
            Response: _description_: A pre-made http response ready to go.
        """
        body = self.build_response_body(
            title=title,
            message="Access token not found.",
            resp="No access token",
            token=token,
            error=True
        )
        return HCI.bad_request(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    def provider_not_found(self, title: str, token: Union[str, None] = None) -> Response:
        """_summary_
            This is a function that will return a provider not found response.

        Args:
            title (str): _description_: The title of the called endpoint
            token (Union[str, None], optional): _description_. Defaults to None.: The token provided by the user of the called endpoint

        Returns:
            Response: _description_: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="The provider you are looking for was not found.",
            resp="Provider not found",
            token=token,
            error=True
        )
        return HCI.not_found(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    def provider_not_given(self, title: str, token: Union[str, None] = None) -> Response:
        """_summary_
            This is a function that will return a provider not found response.

        Args:
            title (str): _description_: The title of the called endpoint
            token (Union[str, None], optional): _description_. Defaults to None.: The token provided by the user of the called endpoint

        Returns:
            Response: _description_: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="You have not given a provider.",
            resp="Provider missing",
            token=token,
            error=True
        )
        return HCI.bad_request(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    def not_logged_in(self, title: str) -> Response:
        """_summary_
            This is a function that will return a not logged in response.

        Args:
            title (str): _description_: The title of the called endpoint

        Returns:
            Response: _description_: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="You need to be logged in to be able to run this endpoint.",
            resp="User not logged in",
            token="",
            error=True
        )
        return HCI.unauthorized(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    def login_failed(self, title: str) -> Response:
        """_summary_
            This is a function that will return a failed login response.

        Args:
            title (str): _description_: The title of the called endpoint

        Returns:
            Response: _description_: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="Login failed, invalid credentials or username.",
            resp="Invalid credentials or username.",
            token="",
            error=True
        )
        return HCI.unauthorized(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    def insuffisant_rights(self, title: str, token: Union[str, None] = None) -> Response:
        """_summary_
            This is a function that will return an insuffisant rights response.

        Args:
            title (str): _description_: The title of the called endpoint
            token (Union[str, None], optional): _description_. Defaults to None.:  The token provided by the user of the called endpoint

        Returns:
            Response: _description_: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="You do not have enough permissions to execute this endpoint.",
            resp="Insufficient rights for given account.",
            token=token,
            error=True
        )
        return HCI.forbidden(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    def bad_request(self, title: str, token: Union[str, None] = None) -> Response:
        """_summary_
            This is a function that will return a bad request response.

        Args:
            title (str): _description_: The title of the called endpoint
            token (Union[str, None], optional): _description_. Defaults to None.: The token provided by the user of the called endpoint

        Returns:
            Response: _description_: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="The request was not formatted correctly.",
            resp="Bad request",
            token=token,
            error=True
        )
        return HCI.bad_request(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    def internal_server_error(self, title: str, token: Union[str, None] = None) -> Response:
        """_summary_
            This is a function that will return an internal server error response.

        Args:
            title (str): _description_: The title of the called endpoint
            token (Union[str, None], optional): _description_. Defaults to None.: The token provided by the user of the called endpoint

        Returns:
            Response: _description_: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="The server has encountered an error.",
            resp="Internal server error",
            token=token,
            error=True
        )
        return HCI.internal_server_error(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    def unauthorized(self, title: str, token: Union[str, None] = None) -> Response:
        """_summary_
            This is a function that will return an unauthorized response.

        Args:
            title (str): _description_: The title of the called endpoint
            token (Union[str, None], optional): _description_. Defaults to None.: The token provided by the user of the called endpoint

        Returns:
            Response: _description_: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="You do not have permission to run this endpoint.",
            resp="Access denied",
            token=token,
            error=True
        )
        return HCI.unauthorized(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    def invalid_verification_code(self, title: str, token: Union[str, None] = None) -> Response:
        """_summary_
            This is a function that will return an invalid verification code response.

        Args:
            title (str): _description_: The title of the called endpoint
            token (Union[str, None], optional): _description_. Defaults to None.: The token provided by the user of the called endpoint

        Returns:
            Response: _description_: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="The verification code you have entered is incorrect.",
            resp="Invalid verification code",
            token=token,
            error=True
        )
        return HCI.bad_request(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    def user_not_found(self, title: str, token: Union[str, None] = None) -> Response:
        """_summary_
            Function that will return a user not found error.

        Args:
            title (str): _description_: The title of the endpoint
            token (Union[str, None], optional): _description_. Defaults to None.: The token if present.

        Returns:
            Response: _description_: The pre-compiled response (ready to go)
        """
        body = self.build_response_body(
            title=title,
            message="The current user was not found.",
            resp="Not found",
            token=token,
            error=True
        )
        return HCI.not_found(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    def missing_variable_in_body(self, title: str, token: Union[str, None] = None) -> Response:
        """_summary_
            Function that will return a message saying that there is a missing variable in the provided body.

        Args:
            title (str): _description_: The name of the endpoint
            token (Union[str, None], optional): _description_. Defaults to None.: The token of the account.

        Returns:
            Response: _description_: The pre-compiled response (ready to go)
        """
        body = self.build_response_body(
            title=title,
            message="A variable is missing in the body of the request.",
            resp="Missing variable",
            token=token,
            error=True
        )
        return HCI.bad_request(body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())
