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
# LAST Modified: 21:32:4 01-02-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the the class in charge of containing the non-http boilerplates.
# // AR
# +==== END CatFeeder =================+
"""

from typing import TYPE_CHECKING, Union, List, Optional, Dict, Any
import re
import uuid
from random import randint
from datetime import datetime, timedelta
from fastapi import Response

from display_tty import Disp, initialise_logger

from ..core import FinalSingleton
from ..core.runtime_manager import RuntimeManager, RI
from ..utils import constants as CONST
from ..sql.sql_manager import SQL

if TYPE_CHECKING:
    from .responses import BoilerplateResponses


class BoilerplateNonHTTP(FinalSingleton):
    """_summary_
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """Initialize the BoilerplateNonHTTP instance.
        The initializer configures the logger, stores commonly used status codes and
        runtime manager references, and obtains shared instances such as the
        database link and optional response helper.

        Args:
            success (int): Numeric code representing a successful operation. Defaults to 0.
            error (int): Numeric code representing an error. Defaults to 84.
            debug (bool): Enable debug logging when True. Defaults to False.
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
        self.database_link: SQL = RI.get(SQL)
        self.boilerplate_responses: Optional[BoilerplateResponses] = RI.get_if_exists(
            "BoilerplateResponses", None)
        self.disp.log_debug("Initialised")

    def pause(self) -> str:
        """_summary_
            This is a pause function that works in the same wat as the batch pause command.
            It pauses the program execution until the user presses the enter key.

        Returns:
            str: _description_: The input from the user
        """
        return input("Press enter to continue...")

    def set_lifespan(self, seconds: int) -> datetime:
        """
                The function to set the lifespan of the user token
            Args:
                seconds (int): Seconds

            Returns:
                datetime: The datetime of the lifespan of the token
            """
        current_time = datetime.now()
        offset_time = current_time + timedelta(seconds=seconds)
        return offset_time

    def is_token_admin(self, token: str) -> bool:
        """Check if a given token correspond to a user that is an administrator or not.

        Args:
            token (str): The token to analyse.

        Returns:
            bool: The administrative status.
        """
        title: str = "is_token_admin"
        usr_id: Union[
            str, Response, None
        ] = self.get_user_id_from_token(title, token)
        if not isinstance(usr_id, str):
            return False
        current_user_raw: Union[int, List[Dict[str, Any]]] = self.database_link.get_data_from_table(
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

    def update_lifespan(self, token: str) -> int:
        """Refresh the expiration date for a connection token.
        The function computes a new expiration datetime using :meth:`set_lifespan`
        and persists it to the database using the configured SQL manager. The
        stored value is formatted for SQL using :meth:`SQL.datetime_to_string`.

        Args:
            token (str): The connection token whose expiration should be updated.

        Returns:
            int: The status code returned by the database update operation. This will be `self.success` on success or an error code on failure.
        """
        self.disp.log_debug("The token is still valid, updating lifespan.")
        new_date = self.set_lifespan(
            CONST.UA_TOKEN_LIFESPAN
        )
        self.disp.log_debug(f"New token lifespan: {new_date}")
        new_date_str = self.database_link.datetime_to_string(
            datetime_instance=new_date,
            date_only=False,
            sql_mode=True
        )
        self.disp.log_debug(f"string date: {new_date_str}")
        status = self.database_link.update_data_in_table(
            table=CONST.TAB_CONNECTIONS,
            data=[new_date_str],
            column=["expiration_date"],
            where=f"token='{token}'"
        )
        if status == self.success:
            self.disp.log_debug("Token expiration date updated.")
            return status
        self.disp.log_error("Failed to update token lifespan.")
        return status

    def is_token_correct(self, token: str) -> bool:
        """_summary_
            Check if the token is correct.
        Args:
            token (str): _description_: The token to check

        Returns:
            bool: _description_: True if the token is correct, False otherwise
        """
        title = "is_token_correct"
        self.disp.log_debug("Checking if the token is correct.", title)
        if isinstance(token, str) is False:
            return False
        login_table = self.database_link.get_data_from_table(
            CONST.TAB_CONNECTIONS,
            ["expiration_date"],
            where=f"token='{token}'",
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
        self.disp.log_debug("The token is still valid, updating lifespan.")
        status = self.update_lifespan(token)
        if status != self.success:
            self.disp.log_warning(
                f"Failed to update expiration_date for {token}.",
                title
            )
        return True

    def generate_token(self) -> str:
        """_summary_
            This is a function that will generate a token for the user.
        Returns:
            str: _description_: The token generated
        """
        title = "generate_token"
        token = str(uuid.uuid4())
        user_token = self.database_link.get_data_from_table(
            table=CONST.TAB_CONNECTIONS,
            column="token",
            where=f"token='{token}'",
            beautify=False
        )
        if isinstance(user_token, int):
            return token
        if isinstance(user_token, list) and token not in user_token:
            return token
        self.disp.log_debug(f"user_token = {user_token}", title)
        while not isinstance(user_token, int):
            token = str(uuid.uuid4())
            user_token = self.database_link.get_data_from_table(
                table=CONST.TAB_CONNECTIONS,
                column="token",
                where=f"token='{token}'",
                beautify=False
            )
            if user_token == []:
                user_token = self.success
            self.disp.log_debug(f"user_token = {user_token}", title)
            if isinstance(user_token, int) and user_token == self.error:
                return token
            if isinstance(user_token, list) and token not in user_token:
                return token
        return token

    def server_show_item_content(self, function_name: str = "show_item_content", item_name: str = "", item: object = None, show: bool = True) -> None:
        """_summary_
            This is a function that will display the content of an item.
            The purpose of this function is more for debugging purposes.
        Args:
            function_name (str, optional): _description_. Defaults to "show_item_content".
            item (object, optional): _description_. Defaults to None.
        """
        if show is False:
            return
        self.disp.log_debug(
            f"({function_name}) dir({item_name}) = {dir(item)}",
            "pet_server_show_item_content"
        )
        for i in dir(item):
            if i in ("auth", "session", "user"):
                self.disp.log_debug(
                    f"({function_name}) skipping {item_name}.{i}"
                )
                continue
            self.disp.log_debug(
                f"({function_name}) {item_name}.{i} = {getattr(item, i)}"
            )

    def check_date(self, date: str = "DD/MM/YYYY") -> bool:
        """_summary_
            This is a function that will check if the date is correct or not.
        Args:
            date (str, optional): _description_: The date to check. Defaults to "DD/MM/YYYY".

        Returns:
            bool: _description_: True if the date is correct, False otherwise
        """
        # First a quick format check, then validate actual calendar date
        pattern = re.compile(
            r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"
        )
        if not pattern.match(date):
            return False
        try:
            # Validate real calendar date (catches things like 31/02/2020)
            datetime.strptime(date, "%d/%m/%Y")
            return True
        except Exception:
            return False

    def generate_check_token(self, token_size: int = 4) -> str:
        """_summary_
            Create a token that can be used for e-mail verification.

        Returns:
            str: _description_
        """
        if isinstance(token_size, (int, float)) is False:
            token_size = 4
        token_size = int(token_size)
        token_size = max(token_size, 0)
        code = f"{randint(CONST.RANDOM_MIN, CONST.RANDOM_MAX)}"
        for i in range(token_size):
            code += f"-{randint(CONST.RANDOM_MIN, CONST.RANDOM_MAX)}"
        return code

    def update_single_data(self, table: str, column_finder: str, column_to_update: str, data_finder: str, request_body: dict) -> int:
        """
        The function in charge of updating the data in the database
        """
        if self.database_link.update_data_in_table(
            table,
            [request_body[column_to_update]],
            [column_to_update],
            f"{column_finder}='{data_finder}'"
        ) == self.error:
            return self.error
        return self.success

    def get_user_id_from_token(self, title: str, token: str) -> Optional[Union[str, Response]]:
        """_summary_
            The function in charge of getting the user id based of the provided content.

        Args:
            title (str): _description_: The title of the endpoint calling it
            token (str): _description_: The token of the user account

        Returns:
            Optional[Union[str, Response]]: _description_: Returns as string id if success, otherwise, a pre-made response for the endpoint.
        """
        function_title = "get_user_id_from_token"
        usr_id_node: str = "user_id"
        self.boilerplate_responses: Optional[BoilerplateResponses] = RI.get_if_exists(
            "BoilerplateResponses", self.boilerplate_responses)
        if not self.boilerplate_responses:
            self.disp.log_error(
                "BoilerplateResponses not found, retuning None",
                f"{title}:{function_title}"
            )
            return None
        self.disp.log_debug(
            f"Getting user id based on {token}", function_title
        )
        current_user_raw: Union[int, List[Dict[str, Any]]] = self.database_link.get_data_from_table(
            table=CONST.TAB_CONNECTIONS,
            column="*",
            where=f"token='{token}'",
            beautify=True
        )
        if isinstance(current_user_raw, int):
            return self.boilerplate_responses.user_not_found(title, token)
        current_user: List[Dict[str, Any]] = current_user_raw
        self.disp.log_debug(f"current_user = {current_user}", function_title)
        if current_user == self.error:
            return self.boilerplate_responses.user_not_found(title, token)
        self.disp.log_debug(
            f"user_length = {len(current_user)}", function_title
        )
        if len(current_user) == 0 or len(current_user) > 1:
            return self.boilerplate_responses.user_not_found(title, token)
        self.disp.log_debug(
            f"current_user[0] = {current_user[0]}", function_title
        )
        if usr_id_node not in current_user[0]:
            return self.boilerplate_responses.user_not_found(title, token)
        msg = "str(current_user[0]["
        msg += f"{usr_id_node}]) = {str(current_user[0][usr_id_node])}"
        self.disp.log_debug(msg, function_title)
        return str(current_user[0][usr_id_node])

    def update_user_data(self, title: str, usr_id: str, line_content: List[Optional[Union[str, int, float]]]) -> Optional[Union[int, Response]]:
        """_summary_
            Update the account information based on the provided line.

        Args:
            title (str): _description_: This is the title of the endpoint
            usr_id (str): _description_: This is the id of the user that needs to be updated
            line_content (List[str]): _description_: The content of the line to be edited.

        Returns:
            Union[int, Response]: _description_
        """
        self.boilerplate_responses: Optional[BoilerplateResponses] = RI.get_if_exists(
            "BoilerplateResponses", self.boilerplate_responses)
        if not self.boilerplate_responses:
            return None
        self.disp.log_debug(f"Compile line_content: {line_content}.", title)
        columns_raw: Union[int, List[str]] = self.database_link.get_table_column_names(
            CONST.TAB_ACCOUNTS
        )
        if isinstance(columns_raw, int):
            return columns_raw
        columns: List[str] = columns_raw
        self.disp.log_debug(f"Removing id from columns: {columns}.", title)
        columns.pop(0)
        status = self.database_link.update_data_in_table(
            table=CONST.TAB_ACCOUNTS,
            data=line_content,
            column=columns,
            where=f"id='{usr_id}'"
        )
        if status == self.error:
            return self.boilerplate_responses.internal_server_error(title, usr_id)
        return self.success

    def remove_user_from_tables(self, where: str, tables: List[str]) -> Union[int, Dict[str, int]]:
        """_summary_
            Remove the user from the provided tables.

        Args:
            where (str): _description_: The id of the user to remove
            tables (List[str]): _description_: The tables to remove the user from

        Returns:
            int: _description_: The status of the operation
        """
        title = "remove_user_from_tables"
        if not isinstance(tables, (List, tuple, str)):
            self.disp.log_error(
                f"Expected tables to be of type list but got {type(tables)}",
                title
            )
            return self.error
        if isinstance(tables, str):
            self.disp.log_warning(
                "Tables is of type str, converting to list[str].", title
            )
            tables = [tables]
        deletion_status = {}
        for table in tables:
            status = self.database_link.remove_data_from_table(
                table=table,
                where=where
            )
            deletion_status[str(table)] = status
            if status == self.error:
                self.disp.log_warning(
                    f"Failed to remove data from table: {table}",
                    title
                )
        return deletion_status

    def hide_api_key(self, api_key: str) -> str:
        """_summary_
            Hide the api key from the user.

        Args:
            api_key (str): _description_: The api key to hide

        Returns:
            str: _description_: The hidden api key
        """
        title = "hide_api_key"
        self.disp.log_debug(f"api_key = {api_key}", title)
        if api_key is None:
            api_key = "No api key"
        else:
            api_key = "Some api key"
        self.disp.log_debug(f"api_key after: {api_key}", title)
        return api_key
