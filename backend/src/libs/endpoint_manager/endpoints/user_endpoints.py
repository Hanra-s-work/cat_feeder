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
# LAST Modified: 12:8:15 30-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The endpoints used for tracking the user requirements.
# // AR
# +==== END CatFeeder =================+
"""
from typing import TYPE_CHECKING
from display_tty import Disp, initialise_logger
from fastapi import Request, Response
from ...core import RuntimeManager, RI
from ...utils import constants as CONST, PasswordHandling
from ...e_mail import MailManagement
from ...http_codes import HCI, HTTP_DEFAULT_TYPE

if TYPE_CHECKING:
    from typing import List, Dict
    from ...sql import SQL
    from ...server_header import ServerHeaders
    from ...boilerplates import BoilerplateIncoming, BoilerplateResponses, BoilerplateNonHTTP


class UserEndpoints:
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

    async def post_login(self, request: Request) -> Response:
        """_summary_
            The endpoint allowing a user to log into the server.

        Returns:
            Response: _description_: The data to send back to the user as a response.
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
        if isinstance(user_info, int):
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

    async def post_register(self, request: Request) -> Response:
        """_summary_

        Args:
            request (Request): _description_

        Returns:
            Response: _description_
        """
        title = "Register"
        request_body = await self.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)
        if not request_body or not all(key in request_body for key in ("email", "password")):
            return self.boilerplate_responses_initialised.bad_request(title)
        email: str = request_body["email"]
        password = request_body["password"]
        if not email or email == "" or not password or password == "":
            return self.boilerplate_responses_initialised.bad_request(title)
        user_info = self.database_link.get_data_from_table(
            CONST.TAB_ACCOUNTS, "*", f"email='{email}'")
        if isinstance(user_info, int) is False:
            node = self.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="Email already exist.",
                resp="email exists",
                token=None,
                error=True
            )
            return HCI.conflict(node)
        hashed_password = self.password_handling_initialised.hash_password(
            password)
        username = email.split('@')[0]
        self.disp.log_debug(f"Username = {username}", title)
        admin = str(int(False))
        favicon = "NULL"
        data = [username, email, hashed_password, "local", favicon, admin]
        self.disp.log_debug(f"Data list = {data}", title)
        column = self.database_link.get_table_column_names(
            CONST.TAB_ACCOUNTS
        )
        self.disp.log_debug(f"Column = {column}", title)
        if isinstance(column, int):
            return self.boilerplate_responses_initialised.internal_server_error(title)
        column.pop(0)
        self.disp.log_debug(f"Column after id pop = {column}", title)
        if self.database_link.insert_data_into_table(CONST.TAB_ACCOUNTS, data, column) == self.error:
            return self.boilerplate_responses_initialised.internal_server_error(title)
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
        body = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=f"Welcome {username}",
            resp="success",
            token=data["token"],
            error=False
        )
        body["token"] = data["token"]
        return HCI.success(
            content=body,
            content_type=HTTP_DEFAULT_TYPE,
            headers=self.server_headers_initialised.for_json()
        )

    async def post_send_email_verification(self, request: Request) -> Response:
        """_summary_
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
        self.disp.log_debug(f"user query = {data}", title)
        if data == self.error or len(data) == 0:
            return self.boilerplate_responses_initialised.bad_request(title)
        email_subject = "[AREA] Verification code"
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
        if tab_column == self.error or len(tab_column) == 0:
            return self.boilerplate_responses_initialised.internal_server_error(title)
        tab_column.pop(0)
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
        """_summary_
            The function in charge of resetting the user's password.
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
        if current_codes == self.error or len(current_codes) == 0:
            return self.boilerplate_responses_initialised.internal_server_error(title)
        for user in current_codes:
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
        """_summary_
            Endpoint allowing the user to update it's account data.

        Args:
            request (Request): _description_

        Returns:
            Response: _description_
        """
        title = "Put user"
        token: str = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
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
        if isinstance(usr_id, Response) is True:
            return usr_id
        user_profile: List[Dict[str]] = self.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{usr_id}'",
        )
        self.disp.log_debug(f"User profile = {user_profile}", title)
        if user_profile == self.error or len(user_profile) == 0:
            return self.boilerplate_responses_initialised.user_not_found(title, token)
        data: List[str] = [
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
        if isinstance(status, Response) is True:
            return status
        data = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The account information has been updated.",
            resp="success",
            token=token,
            error=False
        )
        return HCI.success(content=data, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    async def patch_user(self, request: Request) -> Response:
        """_summary_
            Endpoint allowing the user to update it's account data.

        Args:
            request (Request): _description_

        Returns:
            Response: _description_
        """
        title = "Patch user"
        token: str = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        token_valid: bool = self.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.boilerplate_responses_initialised.unauthorized(title, token)
        request_body = await self.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)
        body_username: str = request_body.get("username")
        body_email: str = request_body.get("email")
        body_password: str = request_body.get("password")
        usr_id = self.boilerplate_non_http_initialised.get_user_id_from_token(
            title, token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id
        user_profile: List[Dict[str]] = self.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{usr_id}'",
        )
        self.disp.log_debug(f"User profile = {user_profile}", title)
        if user_profile == self.error or len(user_profile) == 0:
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
        data: List[str] = [
            username, email, password,
            user_profile[0]["method"], user_profile[0]["favicon"],
            str(user_profile[0]["admin"])
        ]
        status = self.boilerplate_non_http_initialised.update_user_data(
            title, usr_id, data
        )
        if isinstance(status, Response) is True:
            return status
        data = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The account information has been updated.",
            resp="success",
            token=token,
            error=False
        )
        return HCI.success(content=data, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    async def get_user(self, request: Request) -> Response:
        """_summary_
            Endpoint allowing the user to get it's account data.

        Args:
            request (Request): _description_

        Returns:
            Response: _description_
        """
        title = "Get user"
        token: str = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
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
        if isinstance(usr_id, Response) is True:
            return usr_id
        user_profile: List[Dict[str]] = self.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{usr_id}'",
        )
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
            message=new_profile,
            resp="success",
            token=token,
            error=False
        )
        return HCI.success(content=data, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    async def delete_user(self, request: Request) -> Response:
        """_summary_
            Endpoint allowing the user to delete it's account.

        Args:
            request (Request): _description_

        Returns:
            Response: _description_
        """
        title = "Delete user"
        token: str = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
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
        if isinstance(usr_id, Response) is True:
            return usr_id
        user_profile: List[Dict[str]] = self.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{usr_id}'",
        )
        self.disp.log_debug(f"User profile = {user_profile}", title)
        if user_profile == self.error or len(user_profile) == 0:
            return self.boilerplate_responses_initialised.user_not_found(title, token)
        tables_of_interest = [
            CONST.TAB_USER_SERVICES, CONST.TAB_ACTIONS,
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

    async def put_user_favicon(self, request: Request) -> Response:
        """_summary_
            Endpoint allowing the user to update it's favicon.

        Args:
            request (Request): _description_

        Returns:
            Response: _description_
        """

    async def delete_user_favicon(self, request: Request) -> Response:
        """_summary_
            Endpoint allowing the user to delete it's favicon.

        Args:
            request (Request): _description_

        Returns:
            Response: _description_
        """

    async def post_logout(self, request: Request) -> Response:
        """_summary_
            The endpoint allowing a user to log out of the server.

        Returns:
            Response: _description_: The data to send back to the user as a response.
        """
        title = "Logout"
        token: str = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        token_valid: bool = self.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.boilerplate_responses_initialised.unauthorized(title, token)
        response = self.database_link.remove_data_from_table(
            CONST.TAB_CONNECTIONS,
            f"token='{token}'"
        )
        if response == self.error:
            return self.boilerplate_responses_initialised.internal_server_error(title)
        data = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="You have successfully logged out...",
            resp="success",
            token=token,
            error=False
        )
        return HCI.success(content=data, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())

    async def get_user_id(self, request: Request) -> Response:
        """_summary_
            This is an endpoint that will allow the user to query it's id.

        Args:
            request (Request): _description_

        Returns:
            Response: _description_
        """
        title = "Get user id"
        token: str = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
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
        if isinstance(usr_id, Response) is True:
            return usr_id
        data = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=f"Your id is {usr_id}",
            resp=usr_id,
            token=token,
            error=False
        )
        return HCI.success(content=data, content_type=HTTP_DEFAULT_TYPE, headers=self.server_headers_initialised.for_json())
