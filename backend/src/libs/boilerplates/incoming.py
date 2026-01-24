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
# FILE: incoming.py
# CREATION DATE: 11-10-2025
# LAST Modified: 22:47:49 14-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File containing boilerplate functions that could be used by the server in it's endpoints_initialised for checking incoming data.
# // AR
# +==== END CatFeeder =================+
"""

from typing import Union, Dict, Any, Optional
from fastapi import Request, UploadFile
from display_tty import Disp, initialise_logger

from .non_web import BoilerplateNonHTTP
from ..utils import constants as CONST
from ..core import FinalSingleton
from ..core.runtime_manager import RuntimeManager, RI
from ..sql import SQL


class BoilerplateIncoming(FinalSingleton):
    """_summary_
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, error: int = 84, success: int = 0, debug: bool = False) -> None:
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self.debug: bool = debug
        self.success: int = success
        self.error: int = error
        self.runtime_manager: RuntimeManager = RI
        # -------------------------- Shared instances --------------------------
        self.boilerplate_non_http_initialised: Optional[BoilerplateNonHTTP] = self.runtime_manager.get_if_exists(
            BoilerplateNonHTTP,
            None
        )
        self.database_link: SQL = self.runtime_manager.get(SQL)
        self.disp.log_debug("Initialised")

    def token_correct(self, request: Request) -> bool:
        """_summary_
            This is a function that will check if the token is correct or not.
        Args:
            request (Request): _description_: The request object

        Returns:
            bool: _description_: True if the token is correct, False otherwise
        """
        title = "token_correct"
        self.disp.log_debug(
            f"request = {request}", title
        )
        token = self.get_token_if_present(request)
        self.disp.log_debug(
            f"token = {token}", title
        )
        if token is None:
            return False
        self.boilerplate_non_http_initialised = self.runtime_manager.get_if_exists(
            BoilerplateNonHTTP,
            self.boilerplate_non_http_initialised
        )
        if not self.boilerplate_non_http_initialised:
            self.disp.log_error("BoilerplateNonHttp is missing")
            raise RuntimeError("Token validation service unavailable")
        return self.boilerplate_non_http_initialised.is_token_correct(token)

    def logged_in(self, request: Request) -> bool:
        """_summary_
            This is a function that will check if the user is logged in or not.
        Args:
            request (Request): _description_: The request object

        Returns:
            bool: _description_: True if the user is logged in, False otherwise
        """
        title = "logged_in"
        self.disp.log_debug(
            f"request = {request}", title
        )
        self.disp.log_warning(
            "This function is the same as token_correct, please call token correct instead",
            title
        )
        return self.token_correct(request)

    def _insert_login_into_database(self, user_data: dict[str, Any]) -> int:
        """_summary_
            Insert the user data into the database.
        Args:
            user_data (dict[str, any]): _description_: The user data to insert into the database

        Returns:
            int: _description_: The status of the operation
        """
        title = "_insert_login_into_database"
        if len(user_data) != 3:
            self.disp.log_error(
                "The user data is not in the correct format !", title
            )
            return self.error
        self.disp.log_debug(
            f"user_data = {user_data}", title
        )
        user_data[-1] = self.database_link.datetime_to_string(
            user_data[-1]
        )
        self.disp.log_debug(
            f"stringed_datetime = {user_data}", title
        )
        table_columns = self.database_link.get_table_column_names(
            CONST.TAB_CONNECTIONS
        )
        if isinstance(table_columns, int):
            return self.error
        table_columns = CONST.clean_list(
            table_columns,
            CONST.TABLE_COLUMNS_TO_IGNORE,
            self.disp
        )
        self.disp.log_debug(
            f"table_columns = {table_columns}", title
        )
        status = self.database_link.insert_or_update_data_into_table(
            table="Connections",
            data=user_data,
            columns=table_columns
        )
        if status != self.success:
            self.disp.log_error(
                "Data not inserted successfully !", title
            )
            return self.error
        self.disp.log_debug(
            "Data inserted successfully.", title
        )
        return self.success

    def log_user_in(self, email: str = '') -> Dict[str, Any]:
        """_summary_
            Attempt to log the user in based on the provided credentials and the database.

        Args:
            email (str): _description_: The email of the account

        Returns:
            Dict[str, Any]: _description_: The response status
            {'status':Union[success, error], 'token':Union['some_token', '']}
        """
        title = "log_user_in"
        data = {'status': self.success, 'token': ''}
        self.boilerplate_non_http_initialised = self.runtime_manager.get_if_exists(
            BoilerplateNonHTTP,
            self.boilerplate_non_http_initialised
        )
        if not self.boilerplate_non_http_initialised:
            self.disp.log_error("BoilerplateNonHttp is missing")
            raise RuntimeError("Token validation service unavailable")
        self.disp.log_debug(f"e-mail = {email}", title)
        token = self.boilerplate_non_http_initialised.generate_token()
        usr_id = self.database_link.get_data_from_table(
            CONST.TAB_ACCOUNTS,
            "id",
            f"email='{email}'",
            beautify=False
        )
        if isinstance(usr_id, int):
            data['status'] = self.error
            return data
        self.disp.log_debug(f"usr_id = {usr_id}", title)
        lifespan = self.boilerplate_non_http_initialised.set_lifespan(
            CONST.UA_TOKEN_LIFESPAN
        )
        try:
            uid = str(int(usr_id[0][0]))
            self.disp.log_debug(f"uid = {uid}", title)
        except (ValueError, IndexError):
            data['status'] = self.error
            return data
        usr_data = [token, uid, lifespan]
        self.disp.log_debug(f"usr_data = {usr_data}", title)
        data['status'] = self._insert_login_into_database(usr_data)
        data['token'] = token
        self.disp.log_debug(f"Response data: {data}", title)
        return data

    def get_token_if_present(self, request: Request) -> Union[str, None]:
        """_summary_
            Return the token if it is present.

        Args:
            request (Request): _description_: the request header created by the endpoint caller.

        Returns:
            Union[str, None]: _description_: If the token is present, a string is returned, otherwise, it is None.
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

    async def get_body(self, request: Request) -> Dict[str, Any]:
        """
            Get the body of a request, whether it's JSON or form data.
        Args:
            request (Request): The incoming request object.

        Returns:
            Dict[str, Any]: Parsed request body in dictionary format.
        """
        body: Dict[str, Any] = {}

        try:
            body = await request.json()
        except Exception:
            try:
                form = await request.form()
                body = dict(form)

                files = await request.form()
                body["_files"] = {}

                for file_key, file_value in files.items():
                    if isinstance(file_value, UploadFile):
                        body["_files"][file_key] = {
                            "filename": file_value.filename,
                            "content_type": file_value.content_type,
                            "content": await file_value.read()
                        }
            except Exception as form_error:
                msg = f"Failed to parse request body: {str(form_error)}"
                body = {"error": msg}
        return body

    def get_body_type(self, request: Request) -> Optional[str]:
        """Retrieve the type of the request body if present.
            Get the content type of the request body.
        Args:
            request (Request): The incoming request object.
        Returns:
            Optional[str]: The content type of the request body, or None if not present.
        """
        body_type = request.headers.get("content-type", None)
        self.disp.log_debug(f"Body type: {body_type}")
        return body_type

    def log_user_out(self, token: str = "") -> Union[Dict[str, Any], bool]:
        """_summary_
            Attempt to log the user out based on the provided token.

        Args:
            token (str): _description_: The token of the account

        Returns:
            Dict[str, Any]: _description_: The response status
            {'status':Union[success, error], 'msg':'message'}
        """
        title = "log_user_out"
        data = {'status': self.error, 'msg': "You are not logged in !"}
        if token == "":
            data["msg"] = "No token provided !"
            return data

        login_table = self.database_link.get_data_from_table(
            CONST.TAB_CONNECTIONS,
            "*",
            where=f"token={token}",
            beautify=False
        )
        if isinstance(login_table, int):
            return False
        if len(login_table) != 1:
            return False
        self.disp.log_debug(f"login_table = {login_table}", title)
        status = self.database_link.remove_data_from_table(
            CONST.TAB_CONNECTIONS,
            f"token={token}"
        )
        if status != self.success:
            data["msg"] = "Data not removed successfully !"
            self.disp.log_error(data["msg"], title)
            return data
        data["status"] = self.success
        data["msg"] = "You have successfully logged out."
        return data
