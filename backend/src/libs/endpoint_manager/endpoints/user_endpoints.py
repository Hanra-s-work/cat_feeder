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
# FILE: user_endpoints.py
# CREATION DATE: 19-11-2025
# LAST Modified: 15:34:9 22-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The endpoints used for tracking the user requirements.
# // AR
# +==== END CatFeeder =================+
"""
from typing import TYPE_CHECKING, Union
from display_tty import Disp, initialise_logger
from fastapi import Request, Response
from ...core import RuntimeManager, RI
from ...utils import constants as CONST, PasswordHandling
from ...e_mail import MailManagement
from ...http_codes import HCI, HttpDataTypes, HTTP_DEFAULT_TYPE

if TYPE_CHECKING:
    from typing import List, Dict, Any, Optional
    from ...sql import SQL
    from ...server_header import ServerHeaders
    from ...boilerplates import BoilerplateIncoming, BoilerplateResponses, BoilerplateNonHTTP
    from ...favicon import FaviconUser


class UserEndpoints:
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
        self.favicon_user: Optional["FaviconUser"] = self.runtime_manager.get_if_exists(
            "FaviconUser", None)
        self.disp.log_debug("Initialised")

    async def post_login(self, request: Request) -> Response:
        """Log in a user.

        Validate provided credentials and return an authentication token on
        success. Produces a suitable HTTP response for success, unauthorized
        or error cases.

        Args:
            request: The incoming FastAPI request containing JSON with
                ``email`` and ``password``.

        Returns:
            Response: A FastAPI response with the result body and status.
        """
        title = "Login"
        request_body = await self.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)
        if not request_body or not all(key in request_body for key in ("email", "password")):
            return self.boilerplate_responses_initialised.bad_request(title)
        email = request_body["email"]
        password = request_body["password"]
        user_info = self.database_link.get_data_from_table(
            CONST.TAB_ACCOUNTS, "*", f"email='{email}'"
        )
        self.disp.log_debug(f"Retrived data: {user_info}", title)
        if isinstance(user_info, int) or len(user_info) == 0:
            return self.boilerplate_responses_initialised.unauthorized(title)
        if self.password_handling_initialised.check_password(password, user_info[0]["password"]) is False:
            return self.boilerplate_responses_initialised.unauthorized(title)
        data = self.boilerplate_incoming_initialised.log_user_in(
            email
        )
        if data["status"] == self.error:
            body = self.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="Login failed.",
                resp="error",
                token=data["token"],
                error=True
            )
            return HCI.forbidden(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())
        name = user_info[0]["username"]
        body = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=f"Welcome {name}",
            resp="success",
            token=data["token"],
            error=False
        )
        body["token"] = data["token"]
        return HCI.success(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    def _check_gender(self, gender: str) -> str:
        default = "RNS"
        self.disp.log_debug(f"Default gender: '{default}'")
        if not isinstance(gender, str):
            self.disp.log_debug(
                "The provided gender is not a string, returning default"
            )
            return default
        gender_lower = gender.lower()
        if gender_lower in ("m", "male", "man"):
            self.disp.log_debug("Gender is male")
            return "M"
        if gender_lower in ("f", "female", "femme"):
            self.disp.log_debug("Gender is female")
            return "F"
        self.disp.log_debug(
            "Gender is either not in the list or Rather Not Say"
        )
        return default

    def _check_age_range(self, age: Union[str, int, float, None]) -> str:
        default: str = "15-20"
        self.disp.log_debug(f"Default age: '{default}'")

        # Define valid age ranges
        age_ranges = [
            (0, 5, "0-5"),
            (6, 10, "6-10"),
            (11, 15, "11-15"),
            (16, 20, "16-20"),
            (21, 25, "21-25"),
            (26, 30, "26-30"),
            (31, 40, "31-40"),
            (41, 50, "41-50"),
            (51, 60, "51-60"),
            (61, 100, "61+")
        ]

        # If age is a number, find its range
        if isinstance(age, (int, float)):
            age_num = int(age)
            self.disp.log_debug(f"Age provided as number: {age_num}")
            for min_age, max_age, range_str in age_ranges:
                if min_age <= age_num <= max_age:
                    self.disp.log_debug(
                        f"Age {age_num} falls in range {range_str}")
                    return range_str
            self.disp.log_debug(
                f"Age {age_num} doesn't fall in any defined range")
            return default

        # If age is a string
        if isinstance(age, str):
            age_str = age.strip()
            self.disp.log_debug(f"Age provided as string: '{age_str}'")

            # Check if it's already a valid range
            valid_range_strs = [r[2] for r in age_ranges]
            if age_str in valid_range_strs:
                self.disp.log_debug(
                    f"Age string '{age_str}' is already a valid range")
                return age_str

            # Try to parse as a number string
            try:
                age_num = int(float(age_str))
                self.disp.log_debug(f"Age string parsed as number: {age_num}")
                for min_age, max_age, range_str in age_ranges:
                    if min_age <= age_num <= max_age:
                        self.disp.log_debug(
                            f"Age {age_num} falls in range {range_str}")
                        return range_str
                self.disp.log_debug(
                    f"Age {age_num} doesn't fall in any defined range")
            except (ValueError, TypeError):
                self.disp.log_debug(
                    f"Could not parse age string '{age_str}' as number")

            return default

        # If age is None or any other type
        self.disp.log_debug(
            "Age is either not in the list or not provided"
        )
        return default

    async def post_register(self, request: Request) -> Response:
        """Register a new user account.

        Create a new account from provided ``email`` and ``password`` and
        automatically log the user in on success.

        Args:
            request: The incoming FastAPI request with required fields.

        Returns:
            Response: A FastAPI response indicating success or a suitable
            error code (e.g. conflict if the email already exists).
        """
        title = "Register"
        request_body = await self.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)
        if not request_body or ("email" not in request_body and "password" not in request_body):
            return self.boilerplate_responses_initialised.bad_request(title)
        email: str = request_body["email"]
        password: str = request_body["password"]
        if "gender" not in request_body:
            self.disp.log_warning(
                "The gender field was not provided during registration."
            )
        if "age" not in request_body:
            self.disp.log_warning(
                "The age field was not provided during registration."
            )
        gender: str = self._check_gender(request_body.get("gender", ""))
        age: str = self._check_age_range(request_body.get("age", None))
        if not (email and password):
            return self.boilerplate_responses_initialised.bad_request(title)
        user_info = self.database_link.get_data_from_table(
            CONST.TAB_ACCOUNTS, "*", f"email='{email}'"
        )
        account_creation_error = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="Unable to create account. Please try again later.",
            resp="registration_failed",
            token=None,
            error=True
        )
        if not isinstance(user_info, int):
            for user in user_info:
                if email in user["email"]:
                    return HCI.bad_request(account_creation_error)
        else:
            return HCI.bad_request(account_creation_error)
        hashed_password = self.password_handling_initialised.hash_password(
            password)
        username = email.split('@')[0]
        self.disp.log_debug(f"Username = {username}", title)
        admin = int(False)
        favicon = None
        deletion_date = None
        data: List[Union[str, int, float, None]] = [
            username, email, hashed_password, "local", gender, age, favicon, admin, deletion_date
        ]
        self.disp.log_debug(f"Data list = {data}", title)
        column = self.database_link.get_table_column_names(
            CONST.TAB_ACCOUNTS
        )
        self.disp.log_debug(f"Column = {column}", title)
        if isinstance(column, int):
            return self.boilerplate_responses_initialised.internal_server_error(title)
        column = CONST.clean_list(
            column,
            CONST.TABLE_COLUMNS_TO_IGNORE_USER,
            self.disp
        )
        if self.database_link.insert_data_into_table(CONST.TAB_ACCOUNTS, data, column) == self.error:
            return self.boilerplate_responses_initialised.internal_server_error(title)
        login_data = self.boilerplate_incoming_initialised.log_user_in(
            email
        )
        if login_data["status"] == self.error:
            body = self.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="Login failed.",
                resp="error",
                token=login_data["token"],
                error=True
            )
            return HCI.forbidden(content=body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())
        body = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=f"Welcome {username}",
            resp="success",
            token=login_data["token"],
            error=False
        )
        body["token"] = login_data["token"]
        return HCI.success(
            content=body,
            content_type=HTTP_DEFAULT_TYPE,
            headers=self.server_headers_initialised.for_json()
        )

    async def post_send_email_verification(self, request: Request) -> Response:
        """Send an email verification code to a user.

        Generate and store a verification code for the provided email and
        send it via the configured mail management subsystem.

        Args:
            request: The incoming FastAPI request containing the ``email``
                field.

        Returns:
            Response: A FastAPI response indicating whether the email was
            sent successfully or an error occurred.
        """
        title = "Send e-mail verification"
        request_body = await self.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)
        if not request_body or ("email") not in request_body:
            return self.boilerplate_responses_initialised.bad_request(title)
        email: str = request_body["email"]
        data = self.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"email='{email}'",
            beautify=True
        )
        if isinstance(data, int):
            return self.boilerplate_responses_initialised.bad_request(title)
        self.disp.log_debug(f"user query = {data}", title)
        if data == self.error or len(data) == 0:
            return self.boilerplate_responses_initialised.bad_request(title)
        email_subject = "[Asperguide] Verification code"
        code = self.boilerplate_non_http_initialised.generate_check_token(
            CONST.CHECK_TOKEN_SIZE
        )
        expiration_time = self.boilerplate_non_http_initialised.set_lifespan(
            CONST.EMAIL_VERIFICATION_DELAY
        )
        expiration_time_str = self.database_link.datetime_to_string(
            expiration_time, False
        )
        new_node = {}
        new_node['email'] = email
        new_node['code'] = code
        tab_column = self.database_link.get_table_column_names(
            CONST.TAB_VERIFICATION)
        if isinstance(tab_column, int):
            return self.boilerplate_responses_initialised.bad_request(title)
        if tab_column == self.error or len(tab_column) == 0:
            return self.boilerplate_responses_initialised.internal_server_error(title)
        tab_column = CONST.clean_list(
            tab_column,
            CONST.TABLE_COLUMNS_TO_IGNORE,
            self.disp
        )
        self.database_link.remove_data_from_table(
            CONST.TAB_VERIFICATION,
            f"term='{email}'"
        )
        status = self.database_link.insert_data_into_table(
            table=CONST.TAB_VERIFICATION,
            data=[
                email,
                code,
                self.database_link.datetime_to_string(
                    expiration_time, False, True
                )
            ],
            column=tab_column
        )
        if status == self.error:
            return self.boilerplate_responses_initialised.internal_server_error(title)
        code_style = "background-color: lightgray;border: 2px lightgray solid;border-radius: 6px;color: black;font-weight: bold;padding: 5px;padding-top: 5px;padding-bottom: 5px;padding-top: 0px;padding-bottom: 0px;"
        body = ""
        body += "<p>The code is: "
        body += f"<span style=\"{code_style}\">{code}</span></p>"
        body += "<p>The code will be valid until "
        body += f"<span style=\"{code_style}\">"
        body += f"{expiration_time_str}</span>.</p>"
        self.disp.log_debug(f"e-mail body: {body}", title)
        status = self.mail_management_initialised.send_email(
            email, email_subject, body
        )
        if status == self.error:
            return self.boilerplate_responses_initialised.internal_server_error(title)
        body = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="Email send successfully.",
            resp="success",
            token=None,
            error=False
        )
        return HCI.success(body)

    async def put_reset_password(self, request: Request) -> Response:
        """Reset a user's password using a verification code.

        Validates the provided code for the email and updates the account password to the supplied new password on success.

        Args:
            request: The incoming FastAPI request containing ``email``, ``code`` and ``password``.

        Returns:
            Response: A FastAPI response indicating success or an error such as invalid verification code.
        """
        title = "Reset password"
        request_body = await self.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)
        if not request_body or not all(key in request_body for key in ("email", "code", "password")):
            return self.boilerplate_responses_initialised.bad_request(title)
        body_email: str = request_body["email"]
        body_code: str = request_body["code"]
        body_password: str = request_body["password"]
        verified_user: dict = {}
        current_codes = self.database_link.get_data_from_table(
            CONST.TAB_VERIFICATION,
            column="*",
            where=f"term='{body_email}'",
            beautify=True
        )
        self.disp.log_debug(f"Current codes: {current_codes}", title)
        nodes_of_interest = []
        if isinstance(current_codes, int) and current_codes == self.error:
            return self.boilerplate_responses_initialised.internal_server_error(title)
        current_codes_list = []
        if isinstance(current_codes, list):
            current_codes_list: List[Dict[str, Any]] = current_codes
        if len(current_codes_list) == 0:
            return self.boilerplate_responses_initialised.internal_server_error(title)
        for user in current_codes_list:
            if user.get("term") == body_email and user.get("definition") == body_code:
                verified_user = user
                nodes_of_interest.append(user)
        if not verified_user:
            return self.boilerplate_responses_initialised.invalid_verification_code(title)
        data: list = []
        column: list = []
        hashed_password = self.password_handling_initialised.hash_password(
            body_password
        )
        data.append(hashed_password)
        column.append("password")
        status = self.database_link.update_data_in_table(
            CONST.TAB_ACCOUNTS, data, column, f"email='{body_email}'"
        )
        if status == self.error:
            return self.boilerplate_responses_initialised.internal_server_error(title)
        self.disp.log_debug(f"Nodes found: {nodes_of_interest}", title)
        for line in nodes_of_interest:
            self.disp.log_debug(f"line removed: {line}", title)
            self.database_link.remove_data_from_table(
                CONST.TAB_VERIFICATION,
                f"id='{line['id']}'"
            )
        response_body = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="Password changed successfully.",
            resp="success",
            token=None,
            error=False
        )
        return HCI.success(response_body, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    async def put_user(self, request: Request) -> Response:
        """Replace a user's account information.

        Requires a valid authentication token. Replaces username, email and
        password with the submitted values.

        Args:
            request (Request): The incoming FastAPI request with ``username``,
                ``email`` and ``password`` fields and authentication token.

        Returns:
            Response: A FastAPI response indicating update success or an
            appropriate error response.
        """
        title = "Put user"
        token_raw: Optional[str] = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        if not token_raw:
            return self.boilerplate_responses_initialised.no_access_token(title, token_raw)
        token: str = token_raw
        token_valid: bool = self.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.boilerplate_responses_initialised.unauthorized(title, token)
        request_body = await self.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)
        if not request_body or not all(key in request_body for key in ("username", "email", "password")):
            return self.boilerplate_responses_initialised.bad_request(title)
        body_username: str = request_body["username"]
        body_email: str = request_body["email"]
        body_password: str = request_body["password"]
        usr_id = self.boilerplate_non_http_initialised.get_user_id_from_token(
            title, token
        )
        if not usr_id:
            return self.boilerplate_responses_initialised.internal_server_error(title, token)
        if isinstance(usr_id, Response):
            return usr_id
        user_profile_raw: Union[int, List[Dict[str, Any]]] = self.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{usr_id}'",
        )
        if isinstance(user_profile_raw, int):
            return self.boilerplate_responses_initialised.internal_server_error(title, token)
        user_profile: List[Dict[str, Any]] = user_profile_raw
        self.disp.log_debug(f"User profile = {user_profile}", title)
        if user_profile == self.error or len(user_profile) == 0:
            return self.boilerplate_responses_initialised.user_not_found(title, token)
        data: List[Optional[Union[str, int, float]]] = [
            body_username,
            body_email,
            self.password_handling_initialised.hash_password(body_password),
            user_profile[0]["method"],
            user_profile[0]["favicon"],
            str(user_profile[0]["admin"])
        ]
        status = self.boilerplate_non_http_initialised.update_user_data(
            title, usr_id, data
        )
        if isinstance(status, Response):
            return status
        if not status:
            return self.boilerplate_responses_initialised.internal_server_error(title, token)
        data_response = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The account information has been updated.",
            resp="success",
            token=token,
            error=False
        )
        return HCI.success(content=data_response, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    async def patch_user(self, request: Request) -> Response:
        """Partially update a user's account information.

        Only fields present in the request body are updated. Requires a
        valid authentication token.

        Args:
            request (Request): The incoming FastAPI request which may include any of
                ``username``, ``email`` or ``password``.

        Returns:
            Response: A FastAPI response indicating the update result.
        """
        title = "Patch user"
        token_raw: Optional[str] = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        if not token_raw:
            return self.boilerplate_responses_initialised.no_access_token(title, token_raw)
        token: str = token_raw
        token_valid: bool = self.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.boilerplate_responses_initialised.unauthorized(title, token)
        request_body = await self.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)
        body_username: str = request_body.get("username", "")
        body_email: str = request_body.get("email", "")
        body_password: str = request_body.get("password", "")
        usr_id = self.boilerplate_non_http_initialised.get_user_id_from_token(
            title, token
        )
        if isinstance(usr_id, Response):
            return usr_id
        if not usr_id:
            return self.boilerplate_responses_initialised.user_not_found(title, token)
        user_profile_raw: Union[int, List[Dict[str, Any]]] = self.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{usr_id}'",
        )
        if isinstance(user_profile_raw, int) or user_profile_raw == self.error:
            return self.boilerplate_responses_initialised.user_not_found(title, token)
        user_profile: List[Dict[str, Any]] = user_profile_raw
        self.disp.log_debug(f"User profile = {user_profile}", title)
        if len(user_profile) == 0:
            return self.boilerplate_responses_initialised.user_not_found(title, token)
        email: str = user_profile[0]["email"]
        username: str = user_profile[0]["username"]
        password: str = user_profile[0]["password"]
        msg = f"body_username = {body_username}, body_email = {body_email}, "
        msg += f"body_password = {body_password}, email = {email}, "
        msg += f"username = {username}, password = {password}"
        self.disp.log_debug(msg, title)
        if body_username is not None:
            username = body_username
            self.disp.log_debug(f"username is now: {username}", title)
        if body_email is not None:
            email = body_email
            self.disp.log_debug(f"email is now: {email}", title)
        if body_password is not None:
            password = self.password_handling_initialised.hash_password(
                body_password
            )
            self.disp.log_debug(f"password is now: {password}", title)
        data: List[Union[str, int, float, None]] = [
            username, email, password,
            user_profile[0]["method"], user_profile[0]["favicon"],
            str(user_profile[0]["admin"])
        ]
        status = self.boilerplate_non_http_initialised.update_user_data(
            title, usr_id, data
        )
        if isinstance(status, int) or not status:
            return self.boilerplate_responses_initialised.update_failed(title, token)
        if isinstance(status, Response):
            return status
        data_response = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The account information has been updated.",
            resp="success",
            token=token,
            error=False
        )
        return HCI.success(content=data_response, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    async def get_user(self, request: Request) -> Response:
        """Return the authenticated user's profile data.

        Sensitive or banned fields are removed from the returned profile.

        Args:
            request (Request): The incoming FastAPI request carrying an auth token.

        Returns:
            Response: A FastAPI response with the user profile on success.
        """
        title = "Get user"
        token_raw: Optional[str] = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        if not token_raw:
            return self.boilerplate_responses_initialised.no_access_token(title, token_raw)
        token: str = token_raw
        token_valid: bool = self.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.boilerplate_responses_initialised.unauthorized(title, token)
        usr_id = self.boilerplate_non_http_initialised.get_user_id_from_token(
            title, token
        )
        self.disp.log_debug(f"user_id = {usr_id}", title)
        if isinstance(usr_id, Response):
            return usr_id
        user_profile_raw: Union[int, List[Dict[str, Any]]] = self.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{usr_id}'",
        )
        if isinstance(user_profile_raw, int):
            return self.boilerplate_responses_initialised.internal_server_error(title, token)
        user_profile: List[Dict[str, Any]] = user_profile_raw
        self.disp.log_debug(f"User profile = {user_profile}", title)
        if user_profile == self.error or len(user_profile) == 0:
            return self.boilerplate_responses_initialised.user_not_found(title, token)
        new_profile = user_profile[0]
        for i in CONST.USER_INFO_BANNED:
            if i in new_profile:
                new_profile.pop(i)
        if CONST.USER_INFO_ADMIN_NODE in new_profile:
            new_profile[CONST.USER_INFO_ADMIN_NODE] = bool(
                new_profile[CONST.USER_INFO_ADMIN_NODE]
            )
        data = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="success",
            resp=new_profile,
            token=token,
            error=False
        )
        return HCI.success(content=data, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    async def delete_user(self, request: Request) -> Response:
        """Delete the authenticated user's account and related data.

        Removes the user record and cleans up related tables (services,
        actions, connections, OAuth sessions). Requires a valid auth token.

        Args:
            request (Request): The incoming FastAPI request containing the auth token.

        Returns:
            Response: A FastAPI response indicating deletion success or an
            internal server error if cleanup fails.
        """
        title = "Delete user"
        token_raw: Optional[str] = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        if not token_raw:
            return self.boilerplate_responses_initialised.no_access_token(title, token_raw)
        token: str = token_raw
        token_valid: bool = self.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.boilerplate_responses_initialised.unauthorized(title, token)
        usr_id = self.boilerplate_non_http_initialised.get_user_id_from_token(
            title, token
        )
        self.disp.log_debug(f"user_id = {usr_id}", title)
        if isinstance(usr_id, Response):
            return usr_id
        user_profile_raw: Union[int, List[Dict[str, Any]]] = self.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{usr_id}'",
        )
        if isinstance(user_profile_raw, int):
            return self.boilerplate_responses_initialised.internal_server_error(title, token)
        user_profile: List[Dict[str, Any]] = user_profile_raw
        self.disp.log_debug(f"User profile = {user_profile}", title)
        if user_profile == self.error or len(user_profile) == 0:
            return self.boilerplate_responses_initialised.user_not_found(title, token)
        self.disp.log_warning("-------------------------------------")
        self.disp.log_warning("-------------------------------------")
        self.disp.log_warning("-------------------------------------")
        self.disp.log_warning("-------------------------------------")
        self.disp.log_warning(
            "Check table section and make sure that it is up to date."
        )
        self.disp.log_warning("-------------------------------------")
        self.disp.log_warning("-------------------------------------")
        self.disp.log_warning("-------------------------------------")
        self.disp.log_warning("-------------------------------------")
        tables_of_interest = [
            CONST.TAB_ACTIONS,
            CONST.TAB_CONNECTIONS, CONST.TAB_ACTIVE_OAUTHS
        ]
        removal_status = self.boilerplate_non_http_initialised.remove_user_from_tables(
            f"user_id={usr_id}", tables_of_interest
        )
        if isinstance(removal_status, int) or self.error in list(removal_status.values()):
            return self.boilerplate_responses_initialised.internal_server_error(title, token)
        status = self.database_link.remove_data_from_table(
            CONST.TAB_ACCOUNTS, f"id={usr_id}"
        )
        if status == self.error:
            return self.boilerplate_responses_initialised.internal_server_error(title, token)
        data = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The account has successfully been deleted.",
            resp="success",
            token=token,
            error=False
        )
        return HCI.success(content=data, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    async def post_logout(self, request: Request) -> Response:
        """Log out the current user by removing the session token.

        Requires a valid token; removes the connection record associated with the token and returns an appropriate response.

        Args:
            request: The incoming FastAPI request carrying the auth token.

        Returns:
            Response: A FastAPI response indicating logout success or an
            internal server error.
        """
        title = "Logout"
        self.disp.log_debug("Checking is a token is present", title)
        token_raw: Optional[str] = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        if not token_raw:
            return self.boilerplate_responses_initialised.no_access_token(title, token_raw)
        token: str = token_raw
        self.disp.log_debug("Checking if the token is still valid", title)
        token_valid: bool = self.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if not token_valid:
            return self.boilerplate_responses_initialised.unauthorized(title, token)
        self.disp.log_debug("Attempting to remove data from the table", title)
        self.disp.log_debug(
            f"token: {token}, table: {CONST.TAB_CONNECTIONS}", title
        )
        response = self.database_link.remove_data_from_table(
            CONST.TAB_CONNECTIONS,
            f"token='{token}'"
        )
        if response == self.error:
            return self.boilerplate_responses_initialised.internal_server_error(title)
        self.disp.log_debug(
            "Informing the user that the removal was a success", title
        )
        data = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="You have successfully logged out...",
            resp="success",
            token=token,
            error=False
        )
        return HCI.success(content=data, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    async def get_user_id(self, request: Request) -> Response:
        """Return the numerical id of the authenticated user.

        Validates the provided token and returns the user id in the response body.

        Args:
            request (Request): The incoming FastAPI request containing the auth token.

        Returns:
            Response: A FastAPI response with the user's id on success.
        """
        title = "Get user id"
        token_raw: Optional[str] = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        if not token_raw:
            return self.boilerplate_responses_initialised.no_access_token(title, token_raw)
        token: str = token_raw
        token_valid: bool = self.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.boilerplate_responses_initialised.unauthorized(title, token)
        usr_id = self.boilerplate_non_http_initialised.get_user_id_from_token(
            title, token
        )
        self.disp.log_debug(f"user_id = {usr_id}", title)
        if usr_id == self.error or isinstance(usr_id, list) and len(usr_id) == 0:
            return self.boilerplate_responses_initialised.user_not_found(title, token)
        if isinstance(usr_id, Response):
            return usr_id
        data = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=f"Your id is {usr_id}",
            resp=usr_id,
            token=token,
            error=False
        )
        return HCI.success(content=data, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())
