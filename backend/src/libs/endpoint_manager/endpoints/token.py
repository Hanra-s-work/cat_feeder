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
# FILE: token.py
# CREATION DATE: 10-01-2026
# LAST Modified: 22:18:0 11-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge of providing endpoints to allow the front-end to gather info on the tokens.
# // AR
# +==== END CatFeeder =================+
"""


from typing import Optional, Dict, Union, Any, List, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime, timedelta
from display_tty import Disp, initialise_logger
from fastapi import Request, Response
from ...http_codes import HCI, HttpDataTypes
from ...core import RuntimeManager, RI
from ...utils import CONST
from ..endpoint_helpers import datetime_to_string

if TYPE_CHECKING:
    from ...sql import SQL
    from ...server_header import ServerHeaders
    from ...boilerplates import BoilerplateIncoming, BoilerplateResponses, BoilerplateNonHTTP


DEFAULT_DATE_PLACEHOLDER: datetime = datetime(1984, 1, 1)


@dataclass
class TokenInfo:
    """Container for token metadata retrieved from database.

    Attributes:
        token: The token string value.
        user_id: The ID of the user who owns the token.
        creation_date: When the token was created (server-set).
        edit_date: When the token was last modified in database.
        expiration_date: When the token expires and becomes invalid.
    """
    token: str = ""
    user_id: int = 0
    creation_date: datetime = DEFAULT_DATE_PLACEHOLDER
    edit_date: datetime = DEFAULT_DATE_PLACEHOLDER
    expiration_date: datetime = DEFAULT_DATE_PLACEHOLDER


class TokenEndpoints:
    """Manages token-related HTTP endpoints for authentication and validation.

    Provides endpoints for token validation, token information retrieval,
    token refresh, admin status checking, and token revocation.
    """
    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """Initialize the TokenEndpoints manager.

        Args:
            success (int, optional): Success status code. Defaults to 0.
            error (int, optional): Error status code. Defaults to 84.
            debug (bool, optional): Enable debug logging. Defaults to False.
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
        self.sql_connection: Optional["SQL"] = self.runtime_manager.get_if_exists(
            "SQL",
            None
        )
        self.server_headers_initialised: "ServerHeaders" = self.runtime_manager.get(
            "ServerHeaders", None)
        self.boilerplate_incoming_initialised: Optional["BoilerplateIncoming"] = self.runtime_manager.get_if_exists(
            "BoilerplateIncoming", None)
        self.boilerplate_responses_initialised: Optional["BoilerplateResponses"] = self.runtime_manager.get_if_exists(
            "BoilerplateResponses", None)
        self.boilerplate_non_http_initialised: Optional["BoilerplateNonHTTP"] = self.runtime_manager.get_if_exists(
            "BoilerplateNonHTTP", None)
        self.disp.log_debug("Initialised")

    def _get_ttl_breakdown(self, ttl_delta: timedelta) -> Dict[str, int]:
        """Break down timedelta into hours, minutes, and seconds components.

        Args:
            ttl_delta: The timedelta object to break down.

        Returns:
            Dict[str, int]: Dictionary with 'hours', 'minutes', 'seconds' keys.
        """
        ttl_seconds = int(ttl_delta.total_seconds())
        hours = ttl_seconds // 3600
        remaining = ttl_seconds % 3600
        minutes = remaining // 60
        seconds = remaining % 60
        return {
            "days": ttl_delta.days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds
        }

    def _get_token_if_present(self, request: Request) -> Union[str, None]:
        """Extract token from request headers.

        Checks multiple header formats for token presence: direct token key,
        Bearer token format, and request body parameters.

        Args:
            request (Request): The HTTP request object containing headers.

        Returns:
            Union[str, None]: The extracted token string if found, None otherwise.
        """
        mtoken: Union[str, None] = request.get(CONST.REQUEST_TOKEN_KEY)
        mbearer: Union[str, None] = request.get(CONST.REQUEST_BEARER_KEY)
        token: Union[str, None] = request.headers.get(CONST.REQUEST_TOKEN_KEY)
        bearer: Union[str, None] = request.headers.get(
            CONST.REQUEST_BEARER_KEY
        )
        msg = f"mtoken = {mtoken}, mbearer = {mbearer}"
        msg += f", token = {token}, bearer = {bearer}"
        self.disp.log_debug(msg, "get_token_if_present")
        if token is None and bearer is None and token is None and bearer is None:
            return None
        if mbearer is not None and mbearer.startswith('Bearer '):
            return mbearer.split(" ")[1]
        if bearer is not None and bearer.startswith('Bearer '):
            return bearer.split(" ")[1]
        if token is not None:
            return token
        return mtoken

    def _is_token_correct(self, token: str) -> bool:
        """Validate token correctness by checking expiration in database.

        Args:
            token (str): The token string to validate.

        Returns:
            bool: True if token is valid and not expired, False otherwise.
        """
        title = "is_token_correct"
        self.disp.log_debug("Checking if the token is correct.", title)
        if isinstance(token, str) is False:
            return False
        self.sql_connection = self.runtime_manager.get_if_exists(
            "SQL", self.sql_connection)
        if not self.sql_connection:
            return False
        login_table = self.sql_connection.get_data_from_table(
            CONST.TAB_CONNECTIONS,
            ["expiration_date"],
            where=f"token={token}",
            beautify=False
        )
        if isinstance(login_table, int):
            return False
        if len(login_table) != 1:
            return False
        self.disp.log_debug(f"login_table = {login_table}", title)
        if datetime.now() > login_table[0][0]:
            self.disp.log_warning(
                "The provided token is invalid due to excessive idle time."
            )
            return False
        self.disp.log_debug("The token is still valid.")
        return True

    def _token_correct(self, request: Request) -> bool:
        """Validate token from request using BoilerplateNonHTTP validation.

        Args:
            request (Request): The HTTP request object containing the token.

        Returns:
            bool: True if token is valid, False otherwise.

        Raises:
            RuntimeError: If BoilerplateNonHTTP service is unavailable.
        """
        title = "token_correct"
        self.disp.log_debug(
            f"request = {request}", title
        )
        token = self._get_token_if_present(request)
        self.disp.log_debug(
            f"token = {token}", title
        )
        if token is None:
            return False
        self.boilerplate_non_http_initialised = self.runtime_manager.get_if_exists(
            "BoilerplateNonHTTP",
            self.boilerplate_non_http_initialised
        )
        if not self.boilerplate_non_http_initialised:
            self.disp.log_error("BoilerplateNonHttp is missing")
            raise RuntimeError("Token validation service unavailable")
        return self.boilerplate_non_http_initialised.is_token_correct(token)

    def _get_user_id_from_token(self, title: str, token: str) -> Optional[Union[str, Response]]:
        """Retrieve user ID associated with a given token.

        Args:
            title (str): The name of the calling endpoint for logging purposes.
            token (str): The token to look up.

        Returns:
            Optional[Union[str, Response]]: User ID as string on success, Response object on error, None if services unavailable.
        """
        function_title = "get_user_id_from_token"
        usr_id_node: str = "user_id"
        self.boilerplate_responses_initialised: Optional[BoilerplateResponses] = RI.get_if_exists(
            "BoilerplateResponses", self.boilerplate_responses_initialised)
        if not self.boilerplate_responses_initialised:
            self.disp.log_error(
                "BoilerplateResponses not found, retuning None",
                f"{title}:{function_title}"
            )
            return None
        self.sql_connection = self.runtime_manager.get_if_exists(
            "SQL", self.sql_connection)
        if not self.sql_connection:
            self.disp.log_error(
                "SQL not found, returning None",
                f"{title}:{function_title}"
            )
            return None
        self.disp.log_debug(
            f"Getting user id based on {token}", function_title
        )
        current_user_raw: Union[int, List[Dict[str, Any]]] = self.sql_connection.get_data_from_table(
            table=CONST.TAB_CONNECTIONS,
            column="*",
            where=f"token='{token}'",
            beautify=True
        )
        if isinstance(current_user_raw, int):
            return self.boilerplate_responses_initialised.user_not_found(title, token)
        current_user: List[Dict[str, Any]] = current_user_raw
        self.disp.log_debug(f"current_user = {current_user}", function_title)
        if current_user == self.error:
            return self.boilerplate_responses_initialised.user_not_found(title, token)
        self.disp.log_debug(
            f"user_length = {len(current_user)}", function_title
        )
        if len(current_user) == 0 or len(current_user) > 1:
            return self.boilerplate_responses_initialised.user_not_found(title, token)
        self.disp.log_debug(
            f"current_user[0] = {current_user[0]}", function_title
        )
        if usr_id_node not in current_user[0]:
            return self.boilerplate_responses_initialised.user_not_found(title, token)
        msg = "str(current_user[0]["
        msg += f"{usr_id_node}]) = {str(current_user[0][usr_id_node])}"
        self.disp.log_debug(msg, function_title)
        return str(current_user[0][usr_id_node])

    def _is_token_admin(self, token: str) -> Optional[bool]:
        """Check if a given token correspond to a user that is an administrator or not.

        Args:
            token (str): The token to analyse.

        Returns:
            bool: The administrative status.
        """
        title: str = "is_token_admin"
        self.sql_connection = self.runtime_manager.get_if_exists(
            "SQL", self.sql_connection)
        if not self.sql_connection:
            self.disp.log_error(
                "The SQL class was not initialised in the runtime manager.")
            return None
        usr_id: Union[
            str, Response, None
        ] = self._get_user_id_from_token(title, token)
        if not isinstance(usr_id, str):
            return False
        current_user_raw: Union[int, List[Dict[str, Any]]] = self.sql_connection.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{usr_id}'",
            beautify=True
        )
        self.disp.log_debug(f"Queried data = {current_user_raw}")
        if isinstance(current_user_raw, int) or current_user_raw == []:
            return False
        if "admin" in current_user_raw[0]:
            if str(current_user_raw[0].get("admin", "0")) == "1":
                self.disp.log_warning(
                    f"User account {usr_id} with name {current_user_raw[0].get('username', '<unknown_username>')} is an admin"
                )
                self.disp.log_warning(
                    "They probably called an admin endpoint."
                )
                return True
        return False

    def _get_token_info(self, token: str) -> Optional[TokenInfo]:
        """Retrieve token metadata from database.

        Args:
            token (str): The token string to look up.

        Returns:
            Optional[TokenInfo]: Token information dataclass if found, None otherwise.
        """
        resp: TokenInfo = TokenInfo()
        self.sql_connection = self.runtime_manager.get_if_exists(
            "SQL", self.sql_connection)
        if not self.sql_connection:
            self.disp.log_error(
                "The SQL class was not initialised in the runtime manager."
            )
            return None
        token_data: Union[int, List[Dict[str, Any]]] = self.sql_connection.get_data_from_table(
            table=CONST.TAB_CONNECTIONS,
            column="*",
            where=f"token='{token}'",
            beautify=True
        )
        self.disp.log_debug(f"Queried data = {token_data}")
        if isinstance(token_data, int) or token_data == []:
            return None
        token_data_dict: Dict[str, Any] = token_data[0]
        resp.token = token_data_dict.get("token", "")
        resp.user_id = int(token_data_dict.get("user_id", 0))
        resp.creation_date = token_data_dict.get(
            "creation_date", DEFAULT_DATE_PLACEHOLDER)
        resp.edit_date = token_data_dict.get(
            "edit_date", DEFAULT_DATE_PLACEHOLDER)
        resp.expiration_date = token_data_dict.get(
            "expiration_date", DEFAULT_DATE_PLACEHOLDER)
        return resp

    def _get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve user account information from database.

        Args:
            user_id (int): The user ID to look up.

        Returns:
            Optional[Dict[str, Any]]: User account data dictionary if found, None otherwise.
        """

        self.sql_connection = self.runtime_manager.get_if_exists(
            "SQL", self.sql_connection)
        if not self.sql_connection:
            self.disp.log_error(
                "The SQL class was not initialised in the runtime manager.")
            return None
        current_user_raw: Union[int, List[Dict[str, Any]]] = self.sql_connection.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{user_id}'",
            beautify=True
        )
        self.disp.log_debug(f"Queried data = {current_user_raw}")
        if isinstance(current_user_raw, int) or current_user_raw == []:
            return None
        return current_user_raw[0]

    def get_token_valid(self, request: Request) -> Response:
        """Validate if the provided token is currently valid.

        Returns ok/ko message indicating token validity.

        Args:
            request (Request): The HTTP request containing the token.

        Returns:
            Response: HTTP response with validity status (ok/ko).
        """
        token_correct = self._token_correct(request)
        if token_correct:
            return HCI.success("ok", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        return HCI.invalid_token("ko", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())

    def get_admin(self, request: Request) -> Response:
        """Check if the provided token corresponds to an administrator account.

        Returns ok if admin, ko if not admin, and error responses for invalid/missing tokens.

        Args:
            request (Request): The HTTP request containing the token.

        Returns:
            Response: HTTP response with admin status (ok/ko) or error code.
        """
        token = self._get_token_if_present(request)
        if not token:
            return HCI.invalid_token("No token provided", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        admin = self._is_token_admin(token)
        if admin is None:
            return HCI.internal_server_error("Failed to check admin status", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        if not admin:
            return HCI.unauthorized("ko", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        return HCI.success("ok", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())

    def get_time_to_live(self, request: Request) -> Response:
        """Retrieve the remaining time-to-live (TTL) for the provided token.

        Calculates TTL as the difference between expiration date and current time in seconds.

        Args:
            request (Request): The HTTP request containing the token.

        Returns:
            Response: JSON response containing TTL in seconds, or appropriate error response.
        """
        token = self._get_token_if_present(request)
        if not token:
            return HCI.unauthorized("No token provided", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        if not self.sql_connection:
            return HCI.service_unavailable("The server is missing a critical component for this endpoint to complete.", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        token_info = self._get_token_info(token)
        if not token_info:
            return HCI.invalid_token("The provided token does not exist.", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        ttl_delta = (token_info.expiration_date - datetime.now())
        body_content: Dict[str, Any] = {
            "ttl_seconds": ttl_delta.total_seconds(),
            "ttl_breakdown": self._get_ttl_breakdown(ttl_delta)
        }
        return HCI.success(body_content, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    def get_token_info(self, request: Request) -> Response:
        """Endpoint to get information about the provided token.

        Args:
            request (Request): The incoming request.

        Returns:
            Response: The response to send back to the client.
        """
        self.disp.log_debug("Getting token info...")
        if not self.sql_connection:
            return HCI.service_unavailable("The server is missing a critical component for this endpoint to complete.", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        token = self._get_token_if_present(request)
        if not token:
            return HCI.unauthorized("No token provided", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        connected = self._is_token_correct(token)
        if not connected:
            return HCI.invalid_token("The provided token is invalid", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        token_info = self._get_token_info(token)
        if not token_info:
            return HCI.invalid_token("The provided token does not exist", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        user_info = self._get_user_info(token_info.user_id)
        if not user_info:
            return HCI.internal_server_error("Failed to retrieve user information", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        ttl_delta = (token_info.expiration_date - datetime.now())
        body_content: Dict[str, Any] = {
            "user_id": token_info.user_id,
            "token_creation_date": token_info.creation_date.isoformat(),
            "token_edit_date": token_info.edit_date.isoformat(),
            "token_expiration_date": token_info.expiration_date.isoformat(),
            "ttl_seconds": ttl_delta.total_seconds(),
            "ttl_breakdown": self._get_ttl_breakdown(ttl_delta),
            "username": user_info.get("username", "<unknown_username>"),
            "email": CONST.hide_user_email(user_info.get("email", ""), self.disp),
            "admin": str(user_info.get("admin", "0")) == "1",
            "password": user_info.get("password", "") != "",
            "gender": user_info.get("gender", "<unknown_gender>"),
            "age": user_info.get("age", "<unknown_age>"),
            "last_connection": datetime_to_string(user_info.get("last_connection", "<unknown_last_connection>"), "<unknown_last_connection>"),
            "creation_date": datetime_to_string(user_info.get("creation_date", "<unknown_creation_date>"), "<unknown_creation_date>"),
            "edit_date": datetime_to_string(user_info.get("edit_date", "<unknown_edit_date>"), "<unknown_edit_date>"),
            "deletion_date": datetime_to_string(user_info.get("deletion_date", "<unknown_deletion_date>"), "<unknown_deletion_date>")
        }
        self.disp.log_debug(f"Token info response body: {body_content}")
        return HCI.success(body_content, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    def post_refresh_token(self, request: Request) -> Response:
        """Generate and store a new token for the authenticated user.

        Invalidates the old token and creates a fresh one with updated expiration date.
        This operation is non-idempotent: each call produces a different token.

        Args:
            request (Request): The HTTP request containing the current token.

        Returns:
            Response: JSON response containing the new token and expiration date, or error response.
        """
        self.sql_connection = self.runtime_manager.get_if_exists(
            "SQL", self.sql_connection)
        if not self.sql_connection:
            return HCI.service_unavailable("The server is missing a critical component for this endpoint to complete.", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.boilerplate_non_http_initialised = self.runtime_manager.get_if_exists(
            "BoilerplateNonHTTP", self.boilerplate_non_http_initialised)
        if not self.boilerplate_non_http_initialised:
            return HCI.service_unavailable("The server is missing a critical component for this endpoint to complete.", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.boilerplate_responses_initialised = self.runtime_manager.get_if_exists(
            "BoilerplateResponses", self.boilerplate_responses_initialised)
        if not self.boilerplate_responses_initialised:
            return HCI.service_unavailable("The server is missing a critical component for this endpoint to complete.", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        token = self._get_token_if_present(request)
        if not token:
            return HCI.unauthorized("No token provided", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        connected = self._is_token_correct(token)
        if not connected:
            return HCI.invalid_token("The provided token is invalid", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        token_info = self._get_token_info(token)
        if not token_info:
            return HCI.invalid_token("The provided token does not exist", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        new_token = self.boilerplate_non_http_initialised.generate_token()
        new_lifespan = self.boilerplate_non_http_initialised.set_lifespan(
            CONST.UA_TOKEN_LIFESPAN
        )
        creation_date = datetime.now()
        data = [
            new_token,
            new_lifespan,
            creation_date
        ]
        columns = [
            "token",
            "expiration_date",
            "creation_date"
        ]

        status = self.sql_connection.update_data_in_table(
            table=CONST.TAB_CONNECTIONS,
            data=data,
            column=columns,
            where=f"token='{token}'"
        )
        if status != self.success:
            return HCI.internal_server_error("Failed to refresh token", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        body = self.boilerplate_responses_initialised.build_response_body(
            title="refresh_token",
            message="Token refreshed successfully",
            resp="success",
            token=new_token,
            error=False
        )
        body["token"] = new_token
        body["expiration_date"] = new_lifespan.isoformat()
        return HCI.success(body, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    def delete_revoke_account_token(self, request: Request) -> Response:
        """Revoke all active tokens for the authenticated user's account.

        Removes all tokens associated with the user, effectively logging them out
        from all devices/sessions.

        Args:
            request (Request): The HTTP request containing the user's current token.

        Returns:
            Response: Success message if all tokens revoked, or appropriate error response.
        """
        token = self._get_token_if_present(request)
        self.sql_connection = self.runtime_manager.get_if_exists(
            "SQL", self.sql_connection)
        if not self.sql_connection:
            return HCI.service_unavailable("The server is missing a critical component for this endpoint to complete.", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        if not token:
            return HCI.unauthorized("No token provided", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        connected = self._is_token_correct(token)
        if not connected:
            return HCI.invalid_token("The provided token is invalid", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        token_info = self._get_token_info(token)
        if not token_info:
            return HCI.invalid_token("The provided token does not exist", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        status = self.sql_connection.remove_data_from_table(
            table=CONST.TAB_CONNECTIONS,
            where=f"user_id='{token_info.user_id}'"
        )
        if status != self.success:
            return HCI.internal_server_error("Failed to revoke tokens", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        return HCI.success("All tokens revoked", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
