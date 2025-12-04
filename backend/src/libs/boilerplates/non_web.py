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
# FILE: incoming.py
# CREATION DATE: 11-10-2025
# LAST Modified: 3:34:10 25-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the the class in charge of containing the non-http boilerplates.
# // AR
# +==== END CatFeeder =================+
"""


import re
import uuid
from random import randint
from datetime import datetime, timedelta

from display_tty import Disp, initialise_logger

from ..core.runtime_manager import RuntimeManager, RI
from ..utils import constants as CONST
from ..sql.sql_manager import SQL


class BoilerplateNonHTTP:
    """_summary_
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """_summary_
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
        return False

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
            "*",
            where=f"token={token}",
            beautify=False
        )
        if isinstance(login_table, int):
            return False
        if len(login_table) != 1:
            return False
        self.disp.log_debug(f"login_table = {login_table}", title)
        if datetime.now() > login_table[0][-1]:
            return False
        new_date = self.set_lifespan(
            CONST.UA_TOKEN_LIFESPAN
        )
        new_date_str = self.database_link.datetime_to_string(
            datetime_instance=new_date,
            date_only=False,
            sql_mode=True
        )
        self.disp.log_debug(f"string date: {new_date_str}", title)
        status = self.database_link.update_data_in_table(
            table=CONST.TAB_CONNECTIONS,
            data=[new_date_str],
            column=["expiration_date"],
            where=f"token={token}"
        )
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
        self.disp.log_debug(f"user_token = {user_token}", title)
        while not isinstance(user_token, int):
            token = str(uuid.uuid4())
            user_token = self.database_link.get_data_from_table(
                table=CONST.TAB_CONNECTIONS,
                column="token",
                where=f"token='{token}'",
                beautify=False
            )
            self.disp.log_debug(f"user_token = {user_token}", title)
            if isinstance(user_token, int) and user_token == self.error:
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
        pattern = re.compile(
            r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"
        )
        match = pattern.match(date)
        return bool(match)

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
