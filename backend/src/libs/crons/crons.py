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
# FILE: crons.py
# CREATION DATE: 11-10-2025
# LAST Modified: 14:43:37 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge of containing the functions that will be run in the background.
# // AR
# +==== END CatFeeder =================+
"""

from typing import Any, Union, List, Dict, Optional
from datetime import datetime
from display_tty import Disp, initialise_logger
from .background_tasks import BackgroundTasks
from . import crons_constants as CRON_CONST

from ..core import FinalClass
from ..core.runtime_manager import RuntimeManager, RI
from ..utils import constants as CONST
from ..utils.oauth_authentication import OAuthAuthentication
from ..sql import SQL
from ..boilerplates import BoilerplateNonHTTP


class Crons(metaclass=FinalClass):
    """_summary_
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, error: int = 84, success: int = 0, debug: bool = False) -> None:

        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self.error: int = error
        self.success: int = success
        self.debug: bool = debug
        self.runtime_manager: RuntimeManager = RI
        # ------ The class in charge of handling tasks in the background  ------
        if not self.runtime_manager.exists(BackgroundTasks):
            self.runtime_manager.set(
                BackgroundTasks,
                **{"success": self.success, "error": self.error, "debug": self.debug}
            )
        self.background_tasks: BackgroundTasks = self.runtime_manager.get(
            BackgroundTasks)
        # ---------------------- The Database connection  ----------------------
        self.database_link: SQL = self.runtime_manager.get(SQL)
        # --------------------------- OAuth handler  ---------------------------
        self.oauth_authentication_initialised: Optional[OAuthAuthentication] = self.runtime_manager.get_if_exists(
            OAuthAuthentication,
            None
        )
        # ----------------- Regular server checking processes  -----------------
        self.boilerplate_non_http_initialised: Optional[BoilerplateNonHTTP] = self.runtime_manager.get_if_exists(
            BoilerplateNonHTTP,
            None
        )
        self.disp.log_debug("Initialised")

    def __del__(self) -> None:
        """_summary_
            The destructor of the class
        """
        if self.disp:
            self.disp.log_info("Cron sub processes are shutting down.")

    def inject_crons(self) -> int:
        """_summary_
            Add the cron functions to the cron loop.

        Returns:
            int: _description_: The overall status of the injection.
        """
        if self.background_tasks is None:
            return self.error
        self.background_tasks.safe_add_task(
            func=self.check_actions,
            args=None,
            trigger='interval',
            seconds=CRON_CONST.CHECK_ACTIONS_INTERVAL
        )
        if CRON_CONST.ENABLE_TEST_CRONS is True:
            self.background_tasks.safe_add_task(
                func=self._test_current_date,
                args=(datetime.now,),
                trigger='interval',
                seconds=CRON_CONST.TEST_CRONS_INTERVAL
            )
            self.background_tasks.safe_add_task(
                func=self._test_hello_world,
                args=None,
                trigger='interval',
                seconds=CRON_CONST.TEST_CRONS_INTERVAL
            )
        if CRON_CONST.CLEAN_TOKENS is True:
            self.background_tasks.safe_add_task(
                func=self.clean_expired_tokens,
                args=None,
                trigger='interval',
                seconds=CRON_CONST.CLEAN_TOKENS_INTERVAL
            )
        if CRON_CONST.CLEAN_VERIFICATION is True:
            self.background_tasks.safe_add_task(
                func=self.clean_expired_verification_nodes,
                args=None,
                trigger='interval',
                seconds=CRON_CONST.CLEAN_VERIFICATION_INTERVAL
            )
        if CRON_CONST.RENEW_OATH_TOKENS is True:
            self.background_tasks.safe_add_task(
                func=self.renew_oaths,
                args=None,
                trigger='interval',
                seconds=CRON_CONST.RENEW_OATH_TOKENS_INTERVAL
            )
        return self.success

    def _test_hello_world(self) -> None:
        """_summary_
            This is a test function that will print "Hello World".
        """
        self.disp.log_info("Hello World", "_test_hello_world")

    def _test_current_date(self, *args: Any) -> None:
        """_summary_
            This is a test function that will print the current date.
        Args:
            date (datetime): _description_
        """
        if len(args) >= 1:
            date = args[0]
        else:
            date = datetime.now()
        if callable(date):
            self.disp.log_info(f"(Called) Current date: {date()}")
        else:
            self.disp.log_info(f"(Not called) Current date: {date}")

    def clean_expired_tokens(self) -> None:
        """_summary_
            Remove the tokens that have passed their lifespan.
        """
        title = "clean_expired_tokens"
        date_node = "expiration_date"
        current_time = datetime.now()
        self.disp.log_info("Cleaning expired tokens", title)
        current_tokens = self.database_link.get_data_from_table(
            table=CONST.TAB_CONNECTIONS,
            column="*",
            where="",
            beautify=True
        )
        if isinstance(current_tokens, int):
            msg = "There is no data to be cleared in "
            msg += f"{CONST.TAB_CONNECTIONS} table."
            self.disp.log_warning(msg, title)
            return
        self.disp.log_debug(f"current tokens = {current_tokens}", title)
        for i in current_tokens:
            if i[date_node] is not None and i[date_node] != "" and isinstance(i[date_node], str) is True:
                datetime_node = self.database_link.string_to_datetime(
                    i[date_node]
                )
                msg = f"Converted {i[date_node]} to a datetime instance"
                msg += f" ({datetime_node})."
                self.disp.log_debug(msg, title)
            else:
                datetime_node = i[date_node]
                self.disp.log_debug(f"Did not convert {i[date_node]}.", title)
            if datetime_node < current_time:
                self.database_link.remove_data_from_table(
                    table=CONST.TAB_CONNECTIONS,
                    where=f"id='{i['id']}'"
                )
                self.disp.log_debug(f"Removed {i}.", title)
            else:
                self.disp.log_debug(
                    f"Did not remove {i} because it is not yet time.", title
                )
        self.disp.log_debug("Cleaned expired tokens", title)

    def clean_expired_verification_nodes(self) -> None:
        """_summary_
            Remove the nodes in the verification table that have passed their lifespan.
        """
        title = "clean_expired_verification_nodes"
        date_node = "expiration"
        current_time = datetime.now()
        self.disp.log_info(
            f"Cleaning expired lines in the {CONST.TAB_VERIFICATION} table.",
            title
        )
        current_lines = self.database_link.get_data_from_table(
            table=CONST.TAB_VERIFICATION,
            column="*",
            where="",
            beautify=True
        )
        if isinstance(current_lines, int):
            msg = "There is no data to be cleared in "
            msg += f"{CONST.TAB_VERIFICATION} table."
            self.disp.log_warning(
                msg,
                title
            )
            return
        self.disp.log_debug(f"current lines = {current_lines}", title)
        for i in current_lines:
            if i[date_node] is not None and i[date_node] != "" and isinstance(i[date_node], str) is True:
                datetime_node = self.database_link.string_to_datetime(
                    i[date_node]
                )
                msg = f"Converted {i[date_node]} to a datetime instance"
                msg += f" ({datetime_node})."
                self.disp.log_debug(msg, title)
            else:
                datetime_node = i[date_node]
                self.disp.log_debug(f"Did not convert {i[date_node]}.", title)
            if datetime_node < current_time:
                self.database_link.remove_data_from_table(
                    table=CONST.TAB_VERIFICATION,
                    where=f"id='{i['id']}'"
                )
                self.disp.log_debug(f"Removed {i}.", title)
        self.disp.log_debug("Cleaned expired lines", title)

    def renew_oaths(self) -> None:
        """_summary_
            Function in charge of renewing the oath tokens that are about to expire.
        """
        title = "renew_oaths"
        self.disp.log_debug(
            "Checking for oaths that need to be renewed", title
        )
        self.boilerplate_non_http_initialised = self.runtime_manager.get_if_exists(
            BoilerplateNonHTTP,
            self.boilerplate_non_http_initialised
        )
        if not self.boilerplate_non_http_initialised:
            self.disp.log_error(
                "Boilerplate Non Http class not present, aborting check."
            )
            return None
        self.oauth_authentication_initialised = self.runtime_manager.get_if_exists(
            OAuthAuthentication,
            self.oauth_authentication_initialised
        )
        if not self.oauth_authentication_initialised:
            self.disp.log_error(
                "Oauth Authentication class not present, aborting check."
            )
            return None
        oath_connections: Union[List[Dict[str, Any]], int] = self.database_link.get_data_from_table(
            table=CONST.TAB_ACTIVE_OAUTHS,
            column="*",
            where="",
            beautify=True
        )
        if isinstance(oath_connections, int) or len(oath_connections) == 0:
            return
        current_time: datetime = datetime.now()
        for oath in oath_connections:
            if oath["token_lifespan"] == 0:
                self.disp.log_debug(
                    f"Token for {oath['id']} does not need to be renewed.", title
                )
                continue
            node_id: str = oath['id']
            expiration_raw = oath["token_expiration"]
            if isinstance(expiration_raw, datetime):
                token_expiration: datetime = expiration_raw
            else:
                token_expiration = self.database_link.string_to_datetime(
                    expiration_raw, False
                )
            if current_time > token_expiration:
                renew_link: str = oath["refresh_link"]
                lifespan: int = int(oath["token_lifespan"])
                provider_name: Union[int, List[Dict[str, Any]]] = self.database_link.get_data_from_table(
                    table=CONST.TAB_SERVICES,
                    column="*",
                    where=f"id='{oath['service_id']}'",
                    beautify=True
                )
                if isinstance(provider_name, int):
                    self.disp.log_error(
                        f"Could not find provider name for {node_id}", title
                    )
                    continue
                # narrowed type: List[Dict[str, Any]]
                provider_list = provider_name
                if not provider_list:
                    self.disp.log_error(
                        f"Empty provider list for {node_id}", title
                    )
                    continue
                provider_node = provider_list[0]
                new_token: Union[str, None] = self.oauth_authentication_initialised.refresh_token(
                    provider_node.get('name', ''),
                    renew_link
                )
                if new_token is None:
                    self.disp.log_error(
                        "Refresh token failed to generate a new token.", title)
                    continue
                # Produce new expiration string for database separately; do not overwrite datetime variable.
                new_expiration_dt = self.boilerplate_non_http_initialised.set_lifespan(
                    seconds=lifespan
                )
                token_expiration_str: str = self.database_link.datetime_to_string(
                    datetime_instance=new_expiration_dt,
                    date_only=False,
                    sql_mode=True
                )
                self.disp.log_debug(
                    f"token expiration = {token_expiration_str}", title
                )
                if new_token != "":
                    self.database_link.update_data_in_table(
                        table=CONST.TAB_ACTIVE_OAUTHS,
                        data=[
                            new_token,
                            token_expiration_str
                        ],
                        column=[
                            "token",
                            "token_expiration"
                        ],
                        where=f"id='{node_id}'"
                    )
                    self.disp.log_debug(
                        f"token {new_token} updated for {node_id}"
                    )
                else:
                    self.disp.log_error(f"Could not renew token for {node_id}")
            else:
                self.disp.log_debug(
                    f"Token for {node_id} does not need to be renewed.", title
                )
        self.disp.log_debug("Checked for oath that need to be renewed", title)

    def check_actions(self) -> None:
        """_summary_
            Function in charge of checking if any actions need to be run.
        """
        title = "check_actions"
        if self.background_tasks is None:
            return None
        self.disp.log_debug("Checking for actions that need to be run.", title)
        self.disp.log_debug("Checked for actions that needed to be run", title)
        return None
