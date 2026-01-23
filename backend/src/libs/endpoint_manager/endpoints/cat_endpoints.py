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
# LAST Modified: 11:49:31 23-01-2026
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the file containing the endpoints used for the application of the cat feeder.
# // AR
# +==== END CatFeeder =================+
"""
from typing import TYPE_CHECKING, Union, Optional
from dataclasses import dataclass
from display_tty import Disp, initialise_logger
from fastapi import Request, Response
from ...core import RuntimeManager, RI
from ...utils import PasswordHandling, CONST
from ...e_mail import MailManagement
from ...http_codes import HCI, HTTP_DEFAULT_TYPE
import requests
from datetime import datetime, timezone, timedelta

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
        if not self.boilerplate_non_http_initialised.is_token_admin(token):
            return self.boilerplate_responses_initialised.insuffisant_rights(title, token)
        usr_data = self.database_link.get_data_from_table(
            CONST.TAB_ACCOUNTS,
            ["id", "username", "email", "is_admin"],
            f"token={token}",
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
        try:
            # try ISO first
            dt = datetime.fromisoformat(val)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except (ValueError, TypeError):
            # fallback common formats
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                try:
                    dt = datetime.strptime(val, fmt)
                    return dt.replace(tzinfo=timezone.utc)
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
            f"user_id={data.user_id} AND mac='{body['mac']}'",
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
            cols,
            sql_data
        )
        if not isinstance(resp, int):
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
        allowed = {"latitude", "longitude",
                   "city_locality", "country", "mac", "name"}

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
            where = f"id={feeder_id} AND user_id={data.user_id}"
        else:
            where = f"user_id={data.user_id} AND mac='{body['mac']}'"

        resp = self.database_link.update_data_in_table(
            self.tab_feeder,
            sql_data,
            update_cols,
            where=where
        )
        if not isinstance(resp, int):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Feeder updated successfully", "updated", data.token, error=False
        )
        return HCI.success(bod)

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

        # require feeder name (unique) to identify the feeder
        if "name" not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "name")

        # get feeder id owned by this user
        feeder_rows = self.database_link.get_data_from_table(
            self.tab_feeder,
            ["id"],
            f"user_id={data.user_id} AND name='{body['name']}'",
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
            ["ip_address", "edit_date"],
            f"feeder_id={feeder_id}",
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

        latest = None
        latest_dt = None
        for r in ip_rows:
            dt = self._parse_dt(r.get("edit_date"))
            if dt is None:
                continue
            if latest_dt is None or dt > latest_dt:
                latest_dt = dt
                latest = r

        if latest is None or latest_dt is None:
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        # if last update older than 1 hour -> consider feeder offline
        if datetime.now(timezone.utc) - latest_dt > timedelta(hours=1):
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

        ip_address = latest.get("ip_address", "")
        if not ip_address:
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        # try to query the feeder device with a short timeout
        try:
            url = f"http://{ip_address}"
            resp = requests.get(url, timeout=3)
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
        elem = "id"
        if elem not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, elem)

        try:
            feeder_id = int(body["id"])
        except (ValueError, TypeError):
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "valid id")

        # Check if feeder exists and belongs to user
        feeder_exists = self.database_link.get_data_from_table(
            self.tab_feeder,
            ["id"],
            f"id={feeder_id} AND owner={data.user_id}",
            beautify=True
        )
        if not isinstance(feeder_exists, list) or len(feeder_exists) == 0:
            return HCI.not_found(
                self.boilerplate_responses_initialised.build_response_body(
                    title,
                    "Feeder not found or not owned by user",
                    "not_found",
                    data.token,
                    error=True
                )
            )

        resp = self.database_link.remove_data_from_table(
            self.tab_feeder,
            f"id={feeder_id} AND owner={data.user_id}"
        )
        if not isinstance(resp, int):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Feeder deleted successfully", "deleted", data.token, error=False
        )
        return HCI.success(bod)

    async def register_beacon(self, request: Request) -> Response:
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

        # Check if beacon already exists with this MAC or name
        present = self.database_link.get_data_from_table(
            self.tab_beacon,
            ["id"],
            f"owner={data.user_id} AND (mac='{body['mac']}' OR name='{body['name']}')",
            beautify=True
        )
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
        if not isinstance(cols, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)
        cols = CONST.clean_list(cols, self.cols_to_remove, self.disp)
        sql_data = [data.user_id, body["mac"], body["name"]]

        resp = self.database_link.insert_data_into_table(
            self.tab_beacon,
            cols,
            sql_data
        )
        if not isinstance(resp, int):
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
        elem = "id"
        if elem not in body:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, elem)

        try:
            beacon_id = int(body["id"])
        except (ValueError, TypeError):
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "valid id")

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

        bod = self.boilerplate_responses_initialised.build_response_body(
            title,
            "Beacon status retrieved successfully",
            resp={"beacon": beacon_data[0]},
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
        update_cols = [c for c in cols if c in allowed and c in body]
        if not update_cols:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "fields to update")

        sql_data = [body[col] for col in update_cols]

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
        if not isinstance(resp, int):
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
        if not isinstance(resp, int):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Beacon deleted successfully", "deleted", data.token, error=False
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
                locations.append({
                    "visit_time": location["creation_date"],
                    "feeder": feeder_data[0]
                })

        bod = self.boilerplate_responses_initialised.build_response_body(
            title,
            "Beacon locations retrieved successfully",
            {"locations": locations},
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
            cols,
            sql_data
        )
        if not isinstance(resp, int):
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
        visits = []
        for visit in visit_data:
            beacon_info = self.database_link.get_data_from_table(
                self.tab_beacon,
                ["mac", "name"],
                f"id={visit['beacon']}",
                beautify=True
            )
            if isinstance(beacon_info, list) and len(beacon_info) > 0:
                visits.append({
                    "visit_time": visit["creation_date"],
                    "beacon": beacon_info[0]
                })

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

        bod = self.boilerplate_responses_initialised.build_response_body(
            title,
            "Food distribution status checked",
            {
                "can_distribute": can_distribute,
                "food_eaten": pet["food_eaten"],
                "food_max": pet["food_max"]
            },
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
        if not isinstance(resp, int):
            return self.boilerplate_responses_initialised.internal_server_error(title, "")

        bod = self.boilerplate_responses_initialised.build_response_body(
            title,
            "Food distributed successfully",
            {
                "amount_distributed": food_amount,
                "new_total": new_food_eaten,
                "remaining": pet["food_max"] - new_food_eaten
            },
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
        # This is essentially the same as post_beacon_location
        return await self.post_beacon_location(request)

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
        elems = ["beacon_id", "name"]
        for elem in elems:
            if elem not in body:
                return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, elem)

        try:
            beacon_id = int(body["beacon_id"])
        except (ValueError, TypeError):
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "valid beacon_id")

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

        sql_data = [
            beacon_id,
            body["name"],
            body.get("food_eaten", 0),
            body.get("food_max", 100),
            body.get("food_reset", None),
            body.get("time_reset_hours", 24),
            body.get("time_reset_minutes", 0)
        ]

        resp = self.database_link.insert_data_into_table(
            self.tab_pet,
            cols,
            sql_data
        )
        if not isinstance(resp, int):
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
        allowed = {"name", "food_eaten", "food_max", "food_reset",
                   "time_reset_hours", "time_reset_minutes"}

        cols = self.database_link.get_table_column_names(self.tab_pet)
        if not isinstance(cols, list):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        # determine which columns from the table we can update based on request body
        update_cols = [c for c in cols if c in allowed and c in body]
        if not update_cols:
            return self.boilerplate_responses_initialised.missing_variable_in_body(title, data.token, "fields to update")

        sql_data = [body[col] for col in update_cols]

        resp = self.database_link.update_data_in_table(
            self.tab_pet,
            sql_data,
            update_cols,
            where=f"id={pet_id}"
        )
        if not isinstance(resp, int):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Pet updated successfully", "updated", data.token, error=False
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
        if not isinstance(resp, int):
            return self.boilerplate_responses_initialised.internal_server_error(title, data.token)

        bod = self.boilerplate_responses_initialised.build_response_body(
            title, "Pet deleted successfully", "deleted", data.token, error=False
        )
        return HCI.success(bod)
