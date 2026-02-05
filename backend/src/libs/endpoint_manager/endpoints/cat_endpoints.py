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
# FILE: cat_endpoints.py
# CREATION DATE: 08-12-2025
# LAST Modified: 21:33:16 05-02-2026
# DESCRIPTION:
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the file containing the endpoints used for the application of the cat feeder.
# // AR
# +==== END CatFeeder =================+
"""
from dataclasses import dataclass
from typing import TYPE_CHECKING, Union, Optional
from datetime import datetime, timezone, timedelta

import requests
from display_tty import Disp, initialise_logger

from fastapi import Request, Response
from ...utils import CONST
from ...core import RuntimeManager, RI
from .. import endpoint_helpers as EN_CONST
from ...http_codes import HCI

if TYPE_CHECKING:
    from typing import List, Dict, Tuple
    from ...sql import SQL
    from ...server_header import ServerHeaders
    from ...boilerplates import BoilerplateIncoming, BoilerplateResponses, BoilerplateNonHTTP


@dataclass
class UserInfo:
    """Dataclass to store user information.
    """
    user_id: int
    username: str
    email: str
    is_admin: bool
    token: str


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
        # ---------------------------- Table Names -----------------------------
        self.tab_feeder: str = "Feeder"
        self.tab_feeder_ip: str = "FeederIp"
        self.tab_beacon: str = "Beacon"
        self.tab_pet: str = "Pet"
        self.tab_location_history: str = "Location_history"
        self.cols_to_remove: Tuple[str, ...] = (
            "id", "creation_date", "edit_date"
        )
        # -------------------------- forced timezone  --------------------------
        # self.forced_timezone: timezone = timezone.fromutc(timedelta(hours=0))
        self.forced_timezone: timezone = timezone.utc
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

    def _user_connected(self, request: Request, title: str = "_user_connected") -> Union[UserInfo, Response]:
        """Check if the user is connected and return their information.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            UserInfo: The user information if connected, None otherwise.
        """
        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        if not token:
            return self.boilerplate_responses_initialised.invalid_token(title)
        if not self.boilerplate_non_http_initialised.is_token_correct(token):
            return self.boilerplate_responses_initialised.invalid_token(title)
        user_id = self.boilerplate_non_http_initialised.get_user_id_from_token(
            title, token)
        if isinstance(user_id, Response):
            return user_id
        if not user_id or user_id is None:
            return self.boilerplate_responses_initialised.user_not_found(title, token)
        usr_data = self.database_link.get_data_from_table(
            CONST.TAB_ACCOUNTS,
            "*",
            f"id={user_id}",
            beautify=True
        )
        if not isinstance(usr_data, list) or len(usr_data) == 0:
            return self.boilerplate_responses_initialised.missing_resource(title, token)
        return UserInfo(
            user_id=usr_data[0]["id"],
            username=usr_data[0]["username"],
            email=usr_data[0]["email"],
            is_admin=usr_data[0]["admin"],
            token=token
        )

    # pick the most recent entry by edit_date (robust parsing)
    def _parse_dt(self, val: Optional[str]) -> Optional[datetime]:
        if val is None:
            return None
        if isinstance(val, datetime):
            return val
        try:
            # try ISO first
            dt = datetime.fromisoformat(val)
            return dt
        except (ValueError, TypeError):
            # fallback common formats
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.strptime(val, fmt)
                except (ValueError, TypeError):
                    continue
        return None

    async def put_register_feeder(self, request: Request) -> Response:
        """Register a new cat feeder in the database.

        Args:
            request (Request): The incoming request parameters.

        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "put_register_feeder"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        body = await self.boilerplate_incoming_initialised.get_body(request)
        elems = [
            "latitude", "longitude",
            "city_locality", "country", "mac", "name"
        ]
        for elem in elems:
            if elem not in body:
                return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, elem)
        present = self.database_link.get_data_from_table(
            self.tab_feeder,
            ["id"],
            f"owner={data.user_id} AND mac='{body['mac']}'",
            beautify=True
        )
        if isinstance(present, list) and len(present) > 0:
            return HCI.conflict(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Feeder with this MAC address already registered",
                    "exists",
                    data.token,
                    error=True
                )
            )
        cols = self.database_link.get_table_column_names(self.tab_feeder)
        if not isinstance(cols, list):
            return self.boilerplate_responses_initialised.internal_server_error(
                title, data.token
            )
        cols = CONST.clean_list(cols, self.cols_to_remove, self.disp)
        sql_data = [
            data.user_id,
            body["latitude"],
            body["longitude"],
            body["city_locality"],
            body["country"],
            body["mac"],
            body["name"]
        ]
        resp = self.database_link.insert_data_into_table(
            self.tab_feeder,
            sql_data,
            cols
        )
        if resp == self.database_link.error:
            return self.boilerplate_responses_initialised.internal_server_error(
                title, data.token
            )
        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Feeder registered successfully", "registered", data.token, error=False
        )
        return HCI.created(bod)

    async def patch_feeder(self, request: Request) -> Response:
        """Patch (partial update) of a cat feeder.

        Args:
            request (Request): The incoming request parameters.

        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "patch_feeder"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data

        body = await self.boilerplate_incoming_initialised.get_body(request)

        # identifier: either id or mac must be provided
        if "id" not in body and "mac" not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "id or mac")

        # allowed fields to update
        allowed = {
            "latitude", "longitude",
            "city_locality", "country", "mac", "name"
        }

        cols = self.database_link.get_table_column_names(self.tab_feeder)
        if not isinstance(cols, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        # determine which columns from the table we can update based on request body
        update_cols = [c for c in cols if c in allowed and c in body]
        if not update_cols:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "fields to update")

        sql_data = [body[col] for col in update_cols]

        # build where clause to ensure user updates only their feeder
        if "id" in body:
            try:
                feeder_id = int(body["id"])
            except (ValueError, TypeError):
                return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "id")
            where = f"id={feeder_id} AND owner={data.user_id}"
        else:
            where = f"owner={data.user_id} AND mac='{body['mac']}'"

        resp = self.database_link.update_data_in_table(
            self.tab_feeder,
            sql_data,
            update_cols,
            where=where
        )
        if resp == self.database_link.error:
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Feeder updated successfully", "updated", data.token, error=False
        )
        return HCI.success(bod)

    async def get_feeder(self, request: Request) -> Response:
        """Get the status of a cat feeder.

        Args:
            request (Request): The incoming request parameters.

        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "get_feeder"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data

        body = await self.boilerplate_incoming_initialised.get_body(request)

        # require one of: id, name, or mac to identify the feeder
        if "id" not in body and "name" not in body and "mac" not in body:
            self.disp.log_debug(f"body={body}\n\n\n\n\n")
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "id, name, or mac")

        # build where clause
        where_parts = [f"owner={data.user_id}"]
        if "id" in body:
            try:
                feeder_id = int(body["id"])
                where_parts.append(f"id={feeder_id}")
            except (ValueError, TypeError):
                return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "id")
        elif "mac" in body:
            where_parts.append(f"mac='{body['mac']}'")
        else:  # name
            where_parts.append(f"name='{body['name']}'")

        where = " AND ".join(where_parts)

        # get feeder id
        feeder_rows = self.database_link.get_data_from_table(
            self.tab_feeder,
            ["id"],
            where,
            beautify=True
        )
        if not isinstance(feeder_rows, list) or len(feeder_rows) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Feeder not found",
                    "not_found",
                    data.token,
                    error=True
                )
            )
        data_raw: Dict = feeder_rows[0]
        data_clean = EN_CONST.sanitize_response_data(
            data_raw, disp=self.disp
        )
        return HCI.success(
            self.boilerplate_responses_initialised.build_response_body(
                title,
                "Feeder found",
                data_clean,
                data.token,
                error=False
            )
        )

    async def get_feeder_status(self, request: Request) -> Response:
        """Get the status of a cat feeder.

        Args:
            request (Request): The incoming request parameters.

        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "get_feeder_status"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data

        body = await self.boilerplate_incoming_initialised.get_body(request)

        # require one of: id, name, or mac to identify the feeder
        if "id" not in body and "name" not in body and "mac" not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "id, name, or mac")

        # build where clause
        where_parts = [f"owner={data.user_id}"]
        if "id" in body:
            try:
                feeder_id = int(body["id"])
                where_parts.append(f"id={feeder_id}")
            except (ValueError, TypeError):
                return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "id")
        elif "mac" in body:
            where_parts.append(f"mac='{body['mac']}'")
        else:  # name
            where_parts.append(f"name='{body['name']}'")

        where = " AND ".join(where_parts)

        # get feeder id
        feeder_rows = self.database_link.get_data_from_table(
            self.tab_feeder,
            ["id"],
            where,
            beautify=True
        )
        if not isinstance(feeder_rows, list) or len(feeder_rows) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Feeder not found",
                    "not_found",
                    data.token,
                    error=True
                )
            )
        feeder_id = feeder_rows[0]["id"]

        # get IP history for this feeder
        ip_rows = self.database_link.get_data_from_table(
            self.tab_feeder_ip,
            "*",
            f"parent_id={feeder_id}",
            beautify=True
        )
        if not isinstance(ip_rows, list) or len(ip_rows) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "No IP record for this feeder",
                    "not_found",
                    data.token,
                    error=True
                )
            )

        self.disp.log_debug(f"IP rows: {ip_rows}")
        latest = None
        latest_dt = None
        for r in ip_rows:
            self.disp.log_debug(f"Evaluating row: {r}")
            dt = self._parse_dt(r.get("edit_date"))
            self.disp.log_debug(
                f"Parsed datetime: {dt} from edit_date: {r.get('edit_date')}"
            )
            if dt is None:
                continue
            if latest_dt is None or dt > latest_dt:
                latest_dt = dt
                latest = r

        if latest is None or latest_dt is None:
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        # if last update older than 1 hour -> consider feeder offline
        if datetime.now() - latest_dt > timedelta(hours=1):
            bod = self.boilerplate_responses_initialised.build_response_body(
                title,
                "Feeder last seen more than 1 hour ago",
                "offline",
                data.token,
                error=True
            )
            # use request timeout style response for offline status
            try:
                return HCI.request_timeout(bod)
            except AttributeError:
                return HCI.not_found(bod)

        ip_address = latest.get("ip", "")
        if not ip_address:
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        # try to query the feeder device with a short timeout
        try:
            url = f"http://{ip_address}"
            resp = requests.get(url, timeout=5)
            if 200 <= resp.status_code < 400:
                bod = self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Feeder is reachable",
                    "reachable",
                    data.token,
                    error=False
                )
                return HCI.success(bod)
            bod = self.boilerplate_responses_initialised.build_response_body(
                title,
                f"Feeder responded with status {resp.status_code}",
                "unreachable",
                data.token,
                error=True
            )
            return HCI.bad_gateway(bod) if hasattr(HCI, "bad_gateway") else HCI.internal_server_error(bod)
        except requests.exceptions.Timeout:
            bod = self.boilerplate_responses_initialised.build_response_body(
                title,
                "Timed out while contacting feeder",
                "timeout",
                data.token,
                error=True
            )
            return HCI.request_timeout(bod) if hasattr(HCI, "request_timeout") else HCI.internal_server_error(bod)
        except (requests.exceptions.ConnectionError, requests.exceptions.RequestException):
            bod = self.boilerplate_responses_initialised.build_response_body(
                title,
                "Error while contacting feeder",
                "error",
                data.token,
                error=True
            )
            return HCI.internal_server_error(bod)

    async def put_feeder_ip(self, request: Request) -> Response:
        """Update the IP address of the feeder (called by feeder itself)

        Args:
            request (Request): The incoming request with MAC and new IP

        Returns:
            Response: Success/error response
        """
        title = "put_feeder_ip"

        body = await self.boilerplate_incoming_initialised.get_body(request)

        # Require MAC and new IP address
        required_fields = ["mac", "ip"]
        for field in required_fields:
            if field not in body:
                return self.boilerplate_responses_initialised.missing_variable_in_body(
                    title, "", field
                )

        feeder_rows = self.database_link.get_data_from_table(
            self.tab_feeder,
            ["id"],
            f"mac='{body['mac']}'",
            beautify=True
        )

        if not isinstance(feeder_rows, list) or len(feeder_rows) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Feeder not found with this MAC",
                    "not_found",
                    "",
                    error=True
                )
            )

        feeder_id = feeder_rows[0]["id"]
        new_ip = body["ip"]

        # Insert or update IP record for this feeder
        cols = self.database_link.get_table_column_names(self.tab_feeder_ip)
        if not isinstance(cols, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, "")

        cols = CONST.clean_list(cols, self.cols_to_remove, self.disp)

        # Try to update existing record first
        existing_ip = self.database_link.get_data_from_table(
            self.tab_feeder_ip,
            ["id"],
            f"parent_id={feeder_id}",
            beautify=True
        )

        if isinstance(existing_ip, list) and len(existing_ip) > 0:
            self.disp.log_debug(f"Existing IP record found: {existing_ip}")
            self.disp.log_debug(f"Updating IP to: {new_ip}")
            # Update existing record
            _now = datetime.now()  # tz=self.forced_timezone
            now_str = self.database_link.datetime_to_string(_now, False, True)
            resp = self.database_link.update_data_in_table(
                self.tab_feeder_ip,
                [new_ip, now_str],
                ["ip", "edit_date"],
                where=f"parent_id={feeder_id}"
            )
        else:
            self.disp.log_debug(
                "No existing IP record found, inserting new one.")
            self.disp.log_debug(f"Inserting new IP: {new_ip}")
            # Insert new record
            sql_data = [feeder_id, new_ip]
            resp = self.database_link.insert_data_into_table(
                self.tab_feeder_ip,
                sql_data,
                cols
            )

        if resp == self.database_link.error:
            return self.boilerplate_responses_initialised.internal_server_error(title, "")

        bod = self.boilerplate_responses_initialised.build_response_body(
            title,
            f"Feeder IP updated to {new_ip}",
            "updated",
            "",
            error=False
        )
        return HCI.success(bod)

    async def delete_feeder(self, request: Request) -> Response:
        """Delete a cat feeder from the database.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "delete_feeder"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        body = await self.boilerplate_incoming_initialised.get_body(request)
        if "id" not in body and "mac" not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "id or mac")

        if "id" in body:
            try:
                feeder_id_val = int(body["id"])
            except (ValueError, TypeError):
                return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "valid id")
            where = f"owner={data.user_id} AND id={feeder_id_val}"
        else:
            where = f"owner={data.user_id} AND mac='{body['mac']}'"

        # Check if feeder exists and belongs to user
        feeder_rows = self.database_link.get_data_from_table(
            self.tab_feeder,
            ["id"],
            where,
            beautify=True
        )
        if not isinstance(feeder_rows, list) or len(feeder_rows) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Feeder not found or not owned by user",
                    "not_found",
                    data.token,
                    error=True
                )
            )

        feeder_id = feeder_rows[0]["id"]

        resp = self.database_link.remove_data_from_table(
            self.tab_feeder,
            f"id={feeder_id} AND owner={data.user_id}"
        )
        if resp == self.database_link.error:
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Feeder deleted successfully", "deleted", data.token, error=False
        )
        return HCI.success(bod)

    async def get_feeders(self, request: Request) -> Response:
        """Get all feeders for the authenticated user.

        Args:
            request (Request): The incoming request parameters.

        Returns:
            Response: The HTTP response with the list of feeders.
        """
        title = "get_feeders"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        feeders = self.database_link.get_data_from_table(
            self.tab_feeder,
            [
                "id", "name", "mac", "latitude", "longitude",
                "city_locality", "country", "creation_date", "edit_date"
            ],
            f"owner={data.user_id}",
            beautify=True
        )
        if not isinstance(feeders, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)
        feeders = EN_CONST.sanitize_response_data(
            feeders, disp=self.disp
        )
        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "The feeders have been gathered", feeders, data.token, error=False
        )
        return HCI.success(bod)

    async def put_register_beacon(self, request: Request) -> Response:
        """Register a beacon signal from a cat feeder.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "register_beacon"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        body = await self.boilerplate_incoming_initialised.get_body(request)
        elems = ["mac", "name"]
        for elem in elems:
            if elem not in body:
                return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, elem)
        self.disp.log_debug(f"body: {body}")

        # Check if beacon already exists with this MAC or name
        present = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["id"],
            f"owner={data.user_id} AND (mac='{body['mac']}' OR name='{body['name']}')",
            beautify=True
        )
        self.disp.log_debug(f"present: {present}")
        if isinstance(present, list) and len(present) > 0:
            return HCI.conflict(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Beacon with this MAC address or name already registered",
                    "exists",
                    data.token,
                    error=True
                )
            )

        cols = self.database_link.get_table_column_names(self.tab_beacon)
        self.disp.log_debug(f"Column names: {cols}")
        if not isinstance(cols, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)
        cols = CONST.clean_list(cols, self.cols_to_remove, self.disp)
        sql_data = [str(data.user_id), body["mac"], body["name"]]
        self.disp.log_debug(f"raw sql_data: {sql_data}")
        self.disp.log_debug(f"cols: {cols}")
        resp = self.database_link.insert_data_into_table(
            self.tab_beacon,
            sql_data,
            cols
        )
        if resp == self.database_link.error:
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Beacon registered successfully", "registered", data.token, error=False
        )
        return HCI.created(bod)

    async def get_beacon_status(self, request: Request) -> Response:
        """Get the status of a beacon signal from a cat feeder.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "get_beacon_status"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        body = await self.boilerplate_incoming_initialised.get_body(request)
        # Accept beacon identifier: id or name or mac
        if not body or ("id" not in body and "name" not in body and "mac" not in body):
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "id or name or mac")

        beacon_id = None
        if "id" in body:
            try:
                beacon_id = int(body["id"])
            except (ValueError, TypeError):
                return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "valid id")
        else:
            # resolve by name or mac
            if "name" in body:
                where = f"owner={data.user_id} AND name='{body['name']}'"
            else:
                where = f"owner={data.user_id} AND mac='{body['mac']}'"
            rows = self.database_link.get_data_from_table(
                self.tab_beacon,
                ["id"],
                where,
                beautify=True
            )
            if not isinstance(rows, list) or len(rows) == 0:
                return HCI.not_found(
                    self.boilerplate_responses_initialised.build_response_body(
                        title,
                        "Beacon not found",
                        "not_found",
                        data.token,
                        error=True
                    )
                )
            beacon_id = rows[0]["id"]

        beacon_data = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["id", "mac", "name", "creation_date", "edit_date"],
            f"id={beacon_id} AND owner={data.user_id}",
            beautify=True
        )
        if not isinstance(beacon_data, list) or len(beacon_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Beacon not found",
                    "not_found",
                    data.token,
                    error=True
                )
            )
        beacon_cleared = EN_CONST.sanitize_response_data(
            beacon_data[0], disp=self.disp
        )
        bod = self.boilerplate_responses_initialised.build_response_body(
            title,
            "Beacon status retrieved successfully",
            resp={"beacon": beacon_cleared},
            token=data.token,
            error=False,
        )
        return HCI.success(bod)

    async def patch_beacon(self, request: Request) -> Response:
        """Update the beacon signal from a cat feeder.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "patch_beacon"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        body = await self.boilerplate_incoming_initialised.get_body(request)

        # identifier: either id or mac must be provided
        if "id" not in body and "mac" not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "id or mac")

        # allowed fields to update
        allowed = {"mac", "name"}

        cols = self.database_link.get_table_column_names(self.tab_beacon)
        if not isinstance(cols, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        # determine which columns from the table we can update based on request body
        update_cols = []
        for c in cols:
            if c in allowed and c in body:
                update_cols.append(c)
        if not update_cols:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "fields to update")

        sql_data = []
        for col in update_cols:
            sql_data.append(body[col])

        # build where clause to ensure user updates only their beacon
        if "id" in body:
            try:
                beacon_id = int(body["id"])
            except (ValueError, TypeError):
                return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "valid id")
            where = f"id={beacon_id} AND owner={data.user_id}"
        else:
            where = f"owner={data.user_id} AND mac='{body['mac']}'"

        resp = self.database_link.update_data_in_table(
            self.tab_beacon,
            sql_data,
            update_cols,
            where=where
        )
        if resp == self.database_link.error:
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Beacon updated successfully", "updated", data.token, error=False
        )
        return HCI.success(bod)

    async def delete_beacon(self, request: Request) -> Response:
        """Delete the beacon signal from a cat feeder.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "delete_beacon"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        body = await self.boilerplate_incoming_initialised.get_body(request)
        elem = "id"
        if elem not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, elem)

        try:
            beacon_id = int(body["id"])
        except (ValueError, TypeError):
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "valid id")

        # Check if beacon exists and belongs to user
        beacon_exists = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["id"],
            f"id={beacon_id} AND owner={data.user_id}",
            beautify=True
        )
        if not isinstance(beacon_exists, list) or len(beacon_exists) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Beacon not found or not owned by user",
                    "not_found",
                    data.token,
                    error=True
                )
            )

        resp = self.database_link.remove_data_from_table(
            self.tab_beacon,
            f"id={beacon_id} AND owner={data.user_id}"
        )
        if resp == self.database_link.error:
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Beacon deleted successfully", "deleted", data.token, error=False
        )
        return HCI.success(bod)

    async def get_beacons(self, request: Request) -> Response:
        """Get all beacons for the authenticated user.

        Args:
            request (Request): The incoming request parameters.

        Returns:
            Response: The HTTP response with the list of beacons.
        """
        title = "get_beacons"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        beacons_raw = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["id", "name", "mac", "creation_date", "edit_date"],
            f"owner={data.user_id}",
            beautify=True
        )
        if not isinstance(beacons_raw, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        beacons = EN_CONST.sanitize_response_data(
            beacons_raw, disp=self.disp
        )

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "The beacons have been gathered", beacons, data.token, error=False
        )
        return HCI.success(bod)

    async def get_beacon_locations(self, request: Request) -> Response:
        """Get the list of beacon locations from cat feeders.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "get_beacon_locations"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        body = await self.boilerplate_incoming_initialised.get_body(request)

        # Require beacon identifier (name or mac)
        if "name" not in body and "mac" not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "name or mac")

        # Get beacon ID
        if "name" in body:
            where_clause = f"owner={data.user_id} AND name='{body['name']}'"
        else:
            where_clause = f"owner={data.user_id} AND mac='{body['mac']}'"

        beacon_data = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["id"],
            where_clause,
            beautify=True
        )
        if not isinstance(beacon_data, list) or len(beacon_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Beacon not found",
                    "not_found",
                    data.token,
                    error=True
                )
            )

        beacon_id = beacon_data[0]["id"]

        # Get location history for this beacon
        location_data = self.database_link.get_data_from_table(
            self.tab_location_history,
            ["feeder", "creation_date"],
            f"beacon={beacon_id}",
            beautify=True
        )
        if not isinstance(location_data, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        # Correlate with feeder data
        locations = []
        for location in location_data:
            feeder_data = self.database_link.get_data_from_table(
                self.tab_feeder,
                ["name", "latitude", "longitude", "city_locality", "country"],
                f"id={location['feeder']} AND owner={data.user_id}",
                beautify=True
            )
            if isinstance(feeder_data, list) and len(feeder_data) > 0:
                locations.append(
                    {
                        "visit_time": location["creation_date"],
                        "feeder": feeder_data[0]
                    }
                )

        locations_cleaned = EN_CONST.sanitize_response_data(
            locations, disp=self.disp
        )
        bod = self.boilerplate_responses_initialised.build_response_body(
            title,
            "Beacon locations retrieved successfully",
            {"locations": locations_cleaned},
            data.token,
            error=False
        )
        return HCI.success(bod)

    async def post_beacon_location(self, request: Request) -> Response:
        """Post a new beacon location from a cat feeder.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "post_beacon_location"
        body = await self.boilerplate_incoming_initialised.get_body(request)

        # Require both beacon and feeder MACs
        elems = ["beacon_mac", "feeder_mac"]
        for elem in elems:
            if elem not in body:
                return self.boilerplate_responses_initialised.missing_variable_in_body(title, "", elem)

        # Get beacon ID
        beacon_data = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["id"],
            f"mac='{body['beacon_mac']}'",
            beautify=True
        )
        if not isinstance(beacon_data, list) or len(beacon_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Beacon not found",
                    "not_found",
                    "",
                    error=True
                )
            )

        # Get feeder ID
        feeder_data = self.database_link.get_data_from_table(
            self.tab_feeder,
            ["id"],
            f"mac='{body['feeder_mac']}'",
            beautify=True
        )
        if not isinstance(feeder_data, list) or len(feeder_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Feeder not found",
                    "not_found",
                    "",
                    error=True
                )
            )

        beacon_id = beacon_data[0]["id"]
        feeder_id = feeder_data[0]["id"]

        # Insert location record
        cols = self.database_link.get_table_column_names(
            self.tab_location_history)
        if not isinstance(cols, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, "")
        cols = CONST.clean_list(cols, self.cols_to_remove, self.disp)
        sql_data = [beacon_id, feeder_id]

        resp = self.database_link.insert_data_into_table(
            self.tab_location_history,
            sql_data,
            cols
        )
        if resp == self.database_link.error:
            return self.boilerplate_responses_initialised.internal_server_error(title, "")

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Beacon location recorded successfully", "recorded", "", error=False
        )
        return HCI.created(bod)

    async def get_feeder_visits(self, request: Request) -> Response:
        """Get the list of visits recorded by a cat feeder.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "get_feeder_visits"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        body = await self.boilerplate_incoming_initialised.get_body(request)

        # Require feeder identifier (name or mac)
        if "name" not in body and "mac" not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "name or mac")

        # Get feeder ID
        if "name" in body:
            where_clause = f"owner={data.user_id} AND name='{body['name']}'"
        else:
            where_clause = f"owner={data.user_id} AND mac='{body['mac']}'"

        feeder_data = self.database_link.get_data_from_table(
            self.tab_feeder,
            ["id"],
            where_clause,
            beautify=True
        )
        if not isinstance(feeder_data, list) or len(feeder_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Feeder not found",
                    "not_found",
                    data.token,
                    error=True
                )
            )

        feeder_id = feeder_data[0]["id"]

        # Get visits for this feeder
        visit_data = self.database_link.get_data_from_table(
            self.tab_location_history,
            ["beacon", "creation_date"],
            f"feeder={feeder_id}",
            beautify=True
        )
        if not isinstance(visit_data, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        # Get beacon information for each visit
        visits_raw = []
        for visit in visit_data:
            beacon_info = self.database_link.get_data_from_table(
                self.tab_beacon,
                ["mac", "name"],
                f"id={visit['beacon']}",
                beautify=True
            )
            if isinstance(beacon_info, list) and len(beacon_info) > 0:
                visits_raw.append({
                    "visit_time": visit["creation_date"],
                    "beacon": beacon_info[0]
                })

        visits = EN_CONST.sanitize_response_data(
            visits_raw, disp=self.disp
        )
        bod = self.boilerplate_responses_initialised.build_response_body(
            title,
            "Feeder visits retrieved successfully",
            {"visits": visits},
            data.token,
            error=False
        )
        return HCI.success(bod)

    async def get_distribute_food(self, request: Request) -> Response:
        """Get the food distribution status from a cat feeder.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "get_distribute_food"
        body = await self.boilerplate_incoming_initialised.get_body(request)

        # Require beacon MAC to identify the pet
        if "beacon_mac" not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, "", "beacon_mac")

        # Get beacon ID
        beacon_data = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["id"],
            f"mac='{body['beacon_mac']}'",
            beautify=True
        )
        if not isinstance(beacon_data, list) or len(beacon_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Beacon not found",
                    "not_found",
                    "",
                    error=True
                )
            )

        beacon_id = beacon_data[0]["id"]

        # Get pet data for this beacon
        pet_data = self.database_link.get_data_from_table(
            self.tab_pet,
            ["food_eaten", "food_max", "food_reset",
                "time_reset_hours", "time_reset_minutes"],
            f"beacon={beacon_id}",
            beautify=True
        )
        if not isinstance(pet_data, list) or len(pet_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Pet not found for this beacon",
                    "not_found",
                    "",
                    error=True
                )
            )

        pet = pet_data[0]

        # Check if food counter needs reset
        food_reset_time = self._parse_dt(pet.get("food_reset"))
        if food_reset_time and datetime.now(timezone.utc) >= food_reset_time:
            # Reset food counter and update next reset time
            reset_hours = pet.get("time_reset_hours", 24)
            reset_minutes = pet.get("time_reset_minutes", 0)
            next_reset = datetime.now(
                timezone.utc) + timedelta(hours=reset_hours, minutes=reset_minutes)

            self.database_link.update_data_in_table(
                self.tab_pet,
                [0, next_reset.isoformat()],
                ["food_eaten", "food_reset"],
                where=f"beacon={beacon_id}"
            )
            pet["food_eaten"] = 0

        # Check if pet can receive food
        can_distribute = pet["food_eaten"] < pet["food_max"]

        raw_content = {
            "can_distribute": can_distribute,
            "food_eaten": pet["food_eaten"],
            "food_max": pet["food_max"]
        }

        cleaned_content = EN_CONST.sanitize_response_data(
            raw_content, disp=self.disp
        )

        bod = self.boilerplate_responses_initialised.build_response_body(
            title,
            "Food distribution status checked",
            cleaned_content,
            "",
            error=False
        )
        return HCI.success(bod)

    async def post_distribute_food(self, request: Request) -> Response:
        """Record food distribution to a pet.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "post_distribute_food"
        body = await self.boilerplate_incoming_initialised.get_body(request)

        # Require both beacon and feeder MACs
        elems = ["beacon_mac", "feeder_mac"]
        for elem in elems:
            if elem not in body:
                return self.boilerplate_responses_initialised.missing_variable_in_body(title, "", elem)

        # Get beacon ID
        beacon_data = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["id"],
            f"mac='{body['beacon_mac']}'",
            beautify=True
        )
        if not isinstance(beacon_data, list) or len(beacon_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Beacon not found",
                    "not_found",
                    "",
                    error=True
                )
            )

        # Get feeder ID (verify feeder exists)
        feeder_data = self.database_link.get_data_from_table(
            self.tab_feeder,
            ["id"],
            f"mac='{body['feeder_mac']}'",
            beautify=True
        )
        if not isinstance(feeder_data, list) or len(feeder_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Feeder not found",
                    "not_found",
                    "",
                    error=True
                )
            )

        beacon_id = beacon_data[0]["id"]

        # Get pet data
        pet_data = self.database_link.get_data_from_table(
            self.tab_pet,
            [
                "food_eaten", "food_max", "food_reset",
                "time_reset_hours", "time_reset_minutes"
            ],
            f"beacon={beacon_id}",
            beautify=True
        )
        if not isinstance(pet_data, list) or len(pet_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Pet not found for this beacon",
                    "not_found",
                    "",
                    error=True
                )
            )

        pet = pet_data[0]

        # Check if food counter needs reset
        food_reset_time = self._parse_dt(pet.get("food_reset"))
        if food_reset_time and datetime.now(timezone.utc) >= food_reset_time:
            # Reset food counter
            reset_hours = pet.get("time_reset_hours", 24)
            reset_minutes = pet.get("time_reset_minutes", 0)
            next_reset = datetime.now(
                timezone.utc) + timedelta(hours=reset_hours, minutes=reset_minutes)

            self.database_link.update_data_in_table(
                self.tab_pet,
                [0, next_reset.isoformat()],
                ["food_eaten", "food_reset"],
                where=f"beacon={beacon_id}"
            )
            pet["food_eaten"] = 0

        # Check if pet can receive food
        if pet["food_eaten"] >= pet["food_max"]:
            return HCI.forbidden(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Pet has reached daily food limit",
                    "limit_reached",
                    "",
                    error=True
                )
            )

        # Distribute food (increment counter)
        food_amount = body.get("amount", 1)
        new_food_eaten = pet["food_eaten"] + food_amount

        # Ensure we don't exceed the limit
        if new_food_eaten > pet["food_max"]:
            new_food_eaten = pet["food_max"]

        # Update pet food counter
        resp = self.database_link.update_data_in_table(
            self.tab_pet,
            [new_food_eaten],
            ["food_eaten"],
            where=f"beacon={beacon_id}"
        )
        if resp == self.database_link.error:
            return self.boilerplate_responses_initialised.internal_server_error(title, "")

        raw_data = {
            "amount_distributed": food_amount,
            "new_total": new_food_eaten,
            "remaining": pet["food_max"] - new_food_eaten
        }
        cleaned_data = EN_CONST.sanitize_response_data(
            raw_data, disp=self.disp
        )

        bod = self.boilerplate_responses_initialised.build_response_body(
            title,
            "Food distributed successfully",
            cleaned_data,
            "",
            error=False
        )
        return HCI.success(bod)

    async def post_feeder_visit(self, request: Request) -> Response:
        """Register a visit from a cat to a feeder.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "post_feeder_visit"
        body = await self.boilerplate_incoming_initialised.get_body(request)

        # This endpoint might be called with different parameter combinations
        # It could be called with feeder_mac + beacon_mac, or just beacon_mac if the feeder is making the call
        if "beacon_mac" not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, "", "beacon_mac")

        # If feeder_mac is not provided, we might need to identify the feeder differently
        # For example, by IP address or require it in the request
        if "feeder_mac" not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, "", "feeder_mac")

        # Get beacon ID
        beacon_data = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["id"],
            f"mac='{body['beacon_mac']}'",
            beautify=True
        )
        if not isinstance(beacon_data, list) or len(beacon_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Beacon not found",
                    "not_found",
                    "",
                    error=True
                )
            )

        # Get feeder ID
        feeder_data = self.database_link.get_data_from_table(
            self.tab_feeder,
            ["id"],
            f"mac='{body['feeder_mac']}'",
            beautify=True
        )
        if not isinstance(feeder_data, list) or len(feeder_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Feeder not found",
                    "not_found",
                    "",
                    error=True
                )
            )

        beacon_id = beacon_data[0]["id"]
        feeder_id = feeder_data[0]["id"]

        # Insert visit record in location history
        cols = self.database_link.get_table_column_names(
            self.tab_location_history)
        if not isinstance(cols, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, "")
        cols = CONST.clean_list(cols, self.cols_to_remove, self.disp)
        sql_data = [beacon_id, feeder_id]

        resp = self.database_link.insert_data_into_table(
            self.tab_location_history,
            sql_data,
            cols
        )
        if resp == self.database_link.error:
            return self.boilerplate_responses_initialised.internal_server_error(title, "")

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Feeder visit recorded successfully", "recorded", "", error=False
        )
        return HCI.created(bod)

    async def put_register_pet(self, request: Request) -> Response:
        """Register a new pet linked to a beacon.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "put_register_pet"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        body = await self.boilerplate_incoming_initialised.get_body(request)
        # Accept either `beacon_id` (numeric) or `beacon_mac` (string) to identify the beacon
        if "name" not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "name")

        beacon_id = None
        if "beacon_id" in body:
            try:
                beacon_id = int(body["beacon_id"])
            except (ValueError, TypeError):
                return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "valid beacon_id")
        elif "beacon_mac" in body:
            # resolve mac to id
            beacon_rows = self.database_link.get_data_from_table(
                self.tab_beacon,
                ["id"],
                f"mac='{body['beacon_mac']}' AND owner={data.user_id}",
                beautify=True
            )
            if not isinstance(beacon_rows, list) or len(beacon_rows) == 0:
                return HCI.not_found(
                    self.boilerplate_responses_initialised.build_response_body(
                        title,
                        "Beacon not found or not owned by user",
                        "not_found",
                        data.token,
                        error=True
                    )
                )
            beacon_id = beacon_rows[0]["id"]
        else:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "beacon_id or beacon_mac")

        # Check if beacon exists and belongs to user (redundant for beacon_mac path but kept for beacon_id path)
        beacon_exists = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["id"],
            f"id={beacon_id} AND owner={data.user_id}",
            beautify=True
        )
        if not isinstance(beacon_exists, list) or len(beacon_exists) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Beacon not found or not owned by user",
                    "not_found",
                    data.token,
                    error=True
                )
            )

        # Check if pet already exists for this beacon
        present = self.database_link.get_data_from_table(
            self.tab_pet,
            ["id"],
            f"beacon={beacon_id}",
            beautify=True
        )
        if isinstance(present, list) and len(present) > 0:
            return HCI.conflict(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Pet already registered for this beacon",
                    "exists",
                    data.token,
                    error=True
                )
            )

        cols = self.database_link.get_table_column_names(self.tab_pet)
        if not isinstance(cols, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)
        cols = CONST.clean_list(cols, self.cols_to_remove, self.disp)

        time_reset_hours = body.get("time_reset_hours", 24)
        time_reset_minutes = body.get("time_reset_minutes", 0)
        default_reset: datetime = datetime.now(timezone.utc).astimezone()
        default_reset = default_reset + timedelta(
            hours=time_reset_hours,
            minutes=time_reset_minutes
        )

        sql_data = [
            beacon_id,
            body["name"],
            body.get("breed", None),
            body.get("age", None),
            body.get("weight", None),
            body.get("microchip_id", None),
            body.get("food_eaten", 0),
            body.get("food_max", 100),
            body.get("food_reset", default_reset),
            time_reset_hours,
            time_reset_minutes
        ]

        resp = self.database_link.insert_data_into_table(
            self.tab_pet,
            sql_data,
            cols
        )
        if resp == self.database_link.error:
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Pet registered successfully", "registered", data.token, error=False
        )
        return HCI.created(bod)

    async def patch_pet(self, request: Request) -> Response:
        """Update pet information.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "patch_pet"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        body = await self.boilerplate_incoming_initialised.get_body(request)

        if "id" not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "id")

        try:
            pet_id = int(body["id"])
        except (ValueError, TypeError):
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "valid id")

        # Check if pet exists and beacon belongs to user
        pet_data = self.database_link.get_data_from_table(
            self.tab_pet,
            ["beacon"],
            f"id={pet_id}",
            beautify=True
        )
        if not isinstance(pet_data, list) or len(pet_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Pet not found",
                    "not_found",
                    data.token,
                    error=True
                )
            )

        beacon_id = pet_data[0]["beacon"]
        beacon_owner = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["owner"],
            f"id={beacon_id}",
            beautify=True
        )
        if not isinstance(beacon_owner, list) or len(beacon_owner) == 0 or beacon_owner[0]["owner"] != data.user_id:
            return self.boilerplate_responses_initialised.insuffisant_rights(title, data.token)

        # allowed fields to update
        allowed = {
            "name", "food_eaten", "food_max", "food_reset",
            "time_reset_hours", "time_reset_minutes"
        }

        cols = self.database_link.get_table_column_names(self.tab_pet)
        if not isinstance(cols, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        # determine which columns from the table we can update based on request body
        update_cols = [c for c in cols if c in allowed and c in body]
        if not update_cols:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "fields to update")

        sql_data = []
        for col in update_cols:
            sql_data.append(body[col])

        resp = self.database_link.update_data_in_table(
            self.tab_pet,
            sql_data,
            update_cols,
            where=f"id={pet_id}"
        )
        if resp == self.database_link.error:
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Pet updated successfully", "updated", data.token, error=False
        )
        return HCI.success(bod)

    async def get_pet(self, request: Request) -> Response:
        """Get pet information.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "get_pet"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        body = await self.boilerplate_incoming_initialised.get_body(request)

        if "id" not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "id")

        try:
            pet_id = int(body["id"])
        except (ValueError, TypeError):
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "valid id")

        # Check if pet exists and beacon belongs to user
        # Query pet once with all needed columns (including beacon for auth)
        pet_data = self.database_link.get_data_from_table(
            self.tab_pet,
            [
                "beacon", "name", "food_eaten", "food_max", "food_reset",
                "time_reset_hours", "time_reset_minutes"
            ],
            f"id={pet_id}",
            beautify=True
        )
        if not isinstance(pet_data, list) or len(pet_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Pet not found",
                    "not_found",
                    data.token,
                    error=True
                )
            )

        self.disp.log_debug(
            f"Pet data retrieved for pet_id {pet_id}: {pet_data}"
        )

        # Verify authorization: check if beacon belongs to user
        beacon_id = pet_data[0]["beacon"]
        beacon_owner = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["owner"],
            f"id={beacon_id}",
            beautify=True
        )
        self.disp.log_debug(
            f"Beacon owner for beacon_id {beacon_id}: {beacon_owner}"
        )
        if not isinstance(beacon_owner, list) or len(beacon_owner) == 0 or beacon_owner[0]["owner"] != data.user_id:
            return self.boilerplate_responses_initialised.insuffisant_rights(title, data.token)

        # Use the pet data we already retrieved (remove beacon field from response)
        pet_dict = {}
        for k, v in pet_data[0].items():
            if k != "beacon":
                pet_dict[k] = v
        resp_raw = [pet_dict]

        resp = EN_CONST.sanitize_response_data(
            resp_raw, disp=self.disp
        )

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Pet retrieved successfully", resp, data.token, error=False
        )
        return HCI.success(bod)

    async def delete_pet(self, request: Request) -> Response:
        """Delete a pet from the database.

        Args:
            request (Request): The incoming request parameters.
        Returns:
            Response: The HTTP response to send back to the user.
        """
        title = "delete_pet"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        body = await self.boilerplate_incoming_initialised.get_body(request)
        elem = "id"
        if elem not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, elem)

        try:
            pet_id = int(body["id"])
        except (ValueError, TypeError):
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "valid id")

        # Check if pet exists and beacon belongs to user
        pet_data = self.database_link.get_data_from_table(
            self.tab_pet,
            ["beacon"],
            f"id={pet_id}",
            beautify=True
        )
        if not isinstance(pet_data, list) or len(pet_data) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Pet not found",
                    "not_found",
                    data.token,
                    error=True
                )
            )

        beacon_id = pet_data[0]["beacon"]
        beacon_owner = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["owner"],
            f"id={beacon_id}",
            beautify=True
        )
        if not isinstance(beacon_owner, list) or len(beacon_owner) == 0 or beacon_owner[0]["owner"] != data.user_id:
            return self.boilerplate_responses_initialised.insuffisant_rights(title, data.token)

        resp = self.database_link.remove_data_from_table(
            self.tab_pet,
            f"id={pet_id}"
        )
        if resp == self.database_link.error:
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Pet deleted successfully", "deleted", data.token, error=False
        )
        return HCI.success(bod)

    async def get_pets(self, request: Request) -> Response:
        """Get all pets for the authenticated user.

        Args:
            request (Request): The incoming request parameters.

        Returns:
            Response: The HTTP response with the list of pets.
        """
        title = "get_pets"
        data = self._user_connected(request, title)
        if isinstance(data, Response):
            return data
        beacons_raw = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["id"],
            f"owner={data.user_id}",
            beautify=True
        )
        if not isinstance(beacons_raw, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)
        if len(beacons_raw) == 0:
            bod = self.boilerplate_responses_initialised.build_response_body(
                title, "The pets have been gathered.", [], data.token, error=False
            )
            return HCI.success(bod)
        beacons = []
        for i in enumerate(beacons_raw):
            beacons.append(i[1]["id"])
        columns = self.database_link.get_table_column_names(self.tab_pet)
        if not isinstance(columns, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)
        pets_raw = []
        for beacon in beacons:
            pet = self.database_link.get_data_from_table(
                self.tab_pet,
                columns,
                f"beacon={beacon}",
                beautify=True
            )
            self.disp.log_debug(f"Pet data for beacon {beacon}: {pet}")
            if not isinstance(pet, list):
                return self.boilerplate_responses_initialised.internal_server_error(title, data.token)
            if len(pet) == 0:
                continue
            pets_raw.append(pet[0])
        self.disp.log_debug(f"Raw pets data: {pets_raw}")
        pets = EN_CONST.sanitize_response_data(
            pets_raw, disp=self.disp
        )
        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "The pets have been gathered.", pets,  data.token, error=False
        )
        return HCI.success(bod)
