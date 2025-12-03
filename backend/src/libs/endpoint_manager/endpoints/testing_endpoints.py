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
# FILE: testing_endpoints.py
# CREATION DATE: 30-11-2025
# LAST Modified: 7:52:38 02-12-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: Files to test the submodules of the server.
# // AR
# +==== END AsperBackend =================+
"""

from typing import Optional, Dict, Union
from display_tty import Disp, initialise_logger
from fastapi import Request, Response
from ...core import RuntimeControl, RuntimeManager, RI
from ...crons import BackgroundTasks
from ...server_header import ServerHeaders
from ...http_codes import HCI, HttpDataTypes
from ...boilerplates import BoilerplateIncoming, BoilerplateResponses, BoilerplateNonHTTP
from ...sql import SQL
from ...bucket import Bucket


class TestingEndpoints:
    """_summary_
    """
    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """_summary_

        Args:
            success (int, optional): _description_. Defaults to 0.
            error (int, optional): _description_. Defaults to 84.
            debug (bool, optional): _description_. Defaults to False.
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
        self.boilerplate_incoming_initialised: BoilerplateIncoming = self.runtime_manager.get(
            BoilerplateIncoming)
        self.boilerplate_responses_initialised: BoilerplateResponses = self.runtime_manager.get(
            BoilerplateResponses)
        self.boilerplate_non_http_initialised: BoilerplateNonHTTP = self.runtime_manager.get(
            BoilerplateNonHTTP)
        self.runtime_controls_initialised: RuntimeControl = self.runtime_manager.get(
            RuntimeControl)
        self.server_headers_initialised: ServerHeaders = self.runtime_manager.get(
            ServerHeaders)
        self.background_tasks_initialised: BackgroundTasks = self.runtime_manager.get(
            BackgroundTasks)
        self.sql_connection: Optional[SQL] = self.runtime_manager.get_if_exists(
            SQL,
            None
        )
        self.bucket_connection: Optional[Bucket] = self.runtime_manager.get_if_exists(
            Bucket,
            None
        )
        self.disp.log_debug("Initialised")

    # SQL testing

    async def get_tables(self, request: Request) -> Response:
        """Get a list of all database table names.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON list of table names or error response.
        """
        self.sql_connection = self.runtime_manager.get_if_exists(
            SQL,
            self.sql_connection
        )
        if not self.sql_connection:
            return HCI.service_unavailable("Database connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug("Gathering tables")
        data = self.sql_connection.get_table_names()
        self.disp.log_debug(f"Gathered tables: {data}")
        if isinstance(data, int):
            return HCI.not_found(str(data), content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        return HCI.success(data, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def get_table_columns(self, request: Request) -> Response:
        """Get column names for a specific table.

        Query Parameters:
            table_name (str): Name of the table to inspect.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON list of column names or error response.
        """
        self.sql_connection = self.runtime_manager.get_if_exists(
            SQL, self.sql_connection)
        if not self.sql_connection:
            return HCI.service_unavailable("Database connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        table_name = request.query_params.get("table_name")
        if not table_name:
            return HCI.bad_request("Missing required parameter: table_name", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug(f"Gathering columns from table: {table_name}")
        data = self.sql_connection.get_table_column_names(table_name)
        self.disp.log_debug(f"Gathered columns: {data}")
        if isinstance(data, int):
            return HCI.not_found(f"Table '{table_name}' not found or has no columns", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        return HCI.success({"table": table_name, "columns": data}, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def describe_table(self, request: Request) -> Response:
        """Get the full schema description of a table.

        Query Parameters:
            table_name (str): Name of the table to describe.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON with table schema information or error response.
        """
        self.sql_connection = self.runtime_manager.get_if_exists(
            SQL, self.sql_connection)
        if not self.sql_connection:
            return HCI.service_unavailable("Database connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        table_name = request.query_params.get("table_name")
        if not table_name:
            return HCI.bad_request("Missing required parameter: table_name", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug(f"Describing table: {table_name}")
        data = self.sql_connection.describe_table(table_name)
        self.disp.log_debug(f"Table description: {data}")
        if isinstance(data, int):
            return HCI.not_found(f"Failed to describe table '{table_name}'", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        return HCI.success({"table": table_name, "schema": data}, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def get_database_version(self, request: Request) -> Response:
        """Get the database version information.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON with database version or error response.
        """
        self.sql_connection = self.runtime_manager.get_if_exists(
            SQL, self.sql_connection)
        if not self.sql_connection:
            return HCI.service_unavailable("Database connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug("Gathering database version")
        data = self.sql_connection.get_database_version()
        self.disp.log_debug(f"Database version: {data}")
        if data is None:
            return HCI.not_found("Failed to retrieve database version", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        return HCI.success({"version": data}, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def test_sql_connection(self, request: Request) -> Response:
        """Test if the SQL database connection is active.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON with connection status.
        """
        self.sql_connection = self.runtime_manager.get_if_exists(
            SQL, self.sql_connection)
        if not self.sql_connection:
            return HCI.service_unavailable("Database connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug("Testing database connection")
        is_connected: bool = self.sql_connection.is_connected()
        result: Dict[str, Union[str, bool]] = {"connected": is_connected}
        node_id: str = "message"
        if is_connected:
            result[node_id] = "Connection is active"
        else:
            result[node_id] = "Connection failed"
        self.disp.log_debug(f"Connection status: {is_connected}")
        return HCI.success(result, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def get_table_size(self, request: Request) -> Response:
        """Get the number of rows in a table.

        Query Parameters:
            table_name (str): Name of the table to count rows.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON with row count or error response.
        """
        self.sql_connection = self.runtime_manager.get_if_exists(
            SQL, self.sql_connection)
        if not self.sql_connection:
            return HCI.service_unavailable("Database connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        table_name = request.query_params.get("table_name")
        if not table_name:
            return HCI.bad_request("Missing required parameter: table_name", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug(f"Getting size of table: {table_name}")
        row_count = self.sql_connection.get_table_size(table_name, "*")
        self.disp.log_debug(f"Table size: {row_count}")
        if row_count < 0:
            return HCI.not_found(f"Failed to get size of table '{table_name}'", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        return HCI.success({"table": table_name, "row_count": row_count}, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def get_triggers(self, request: Request) -> Response:
        """Get all database triggers.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON with triggers dictionary or error response.
        """
        self.sql_connection = self.runtime_manager.get_if_exists(
            SQL, self.sql_connection)
        if not self.sql_connection:
            return HCI.service_unavailable("Database connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug("Gathering triggers")
        data = self.sql_connection.get_triggers()
        self.disp.log_debug(f"Gathered triggers: {data}")
        if isinstance(data, int):
            return HCI.not_found("Failed to retrieve triggers", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        return HCI.success(data, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def get_trigger_names(self, request: Request) -> Response:
        """Get list of all trigger names.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON list of trigger names or error response.
        """
        self.sql_connection = self.runtime_manager.get_if_exists(
            SQL, self.sql_connection)
        if not self.sql_connection:
            return HCI.service_unavailable("Database connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug("Gathering trigger names")
        data = self.sql_connection.get_trigger_names()
        self.disp.log_debug(f"Gathered trigger names: {data}")
        if isinstance(data, int):
            return HCI.not_found("Failed to retrieve trigger names", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        return HCI.success(data, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def get_current_datetime(self, request: Request) -> Response:
        """Get current datetime in the project's format.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON with current datetime string.
        """
        self.sql_connection = self.runtime_manager.get_if_exists(
            SQL, self.sql_connection)
        if not self.sql_connection:
            return HCI.service_unavailable("Database connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug("Getting current datetime")
        datetime_str = self.sql_connection.get_correct_now_value()
        self.disp.log_debug(f"Current datetime: {datetime_str}")
        return HCI.success({"datetime": datetime_str}, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def get_current_date(self, request: Request) -> Response:
        """Get current date in the project's format.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON with current date string.
        """
        self.sql_connection = self.runtime_manager.get_if_exists(
            SQL, self.sql_connection)
        if not self.sql_connection:
            return HCI.service_unavailable("Database connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug("Getting current date")
        date_str = self.sql_connection.get_correct_current_date_value()
        self.disp.log_debug(f"Current date: {date_str}")
        return HCI.success({"date": date_str}, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def convert_datetime_to_string(self, request: Request) -> Response:
        """Convert a datetime object to project's string format.

        Query Parameters:
            datetime (str): ISO format datetime string to convert.
            date_only (bool, optional): If true, return only date portion. Defaults to false.
            sql_mode (bool, optional): If true, include millisecond precision. Defaults to false.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON with formatted datetime string or error response.
        """
        self.sql_connection = self.runtime_manager.get_if_exists(
            SQL, self.sql_connection)
        if not self.sql_connection:
            return HCI.service_unavailable("Database connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        datetime_str = request.query_params.get("datetime")
        if not datetime_str:
            return HCI.bad_request("Missing required parameter: datetime (ISO format)", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        date_only = request.query_params.get(
            "date_only", "false").lower() == "true"
        sql_mode = request.query_params.get(
            "sql_mode", "false").lower() == "true"
        self.disp.log_debug(f"Converting datetime: {datetime_str}")
        try:
            from datetime import datetime
            dt_obj = datetime.fromisoformat(datetime_str)
            formatted = self.sql_connection.datetime_to_string(
                dt_obj, date_only, sql_mode)
            self.disp.log_debug(f"Formatted datetime: {formatted}")
            return HCI.success({"original": datetime_str, "formatted": formatted, "date_only": date_only, "sql_mode": sql_mode}, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())
        except ValueError as e:
            return HCI.bad_request(f"Invalid datetime format: {str(e)}", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())

    async def convert_string_to_datetime(self, request: Request) -> Response:
        """Convert a project-formatted string to datetime object.

        Query Parameters:
            datetime_str (str): Project-formatted datetime string to parse.
            date_only (bool, optional): If true, parse as date only. Defaults to false.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON with ISO format datetime or error response.
        """
        self.sql_connection = self.runtime_manager.get_if_exists(
            SQL, self.sql_connection)
        if not self.sql_connection:
            return HCI.service_unavailable("Database connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        datetime_str = request.query_params.get("datetime_str")
        if not datetime_str:
            return HCI.bad_request("Missing required parameter: datetime_str", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        date_only = request.query_params.get(
            "date_only", "false").lower() == "true"
        self.disp.log_debug(f"Parsing datetime string: {datetime_str}")
        try:
            dt_obj = self.sql_connection.string_to_datetime(
                datetime_str, date_only)
            iso_format = dt_obj.isoformat()
            self.disp.log_debug(f"Parsed to ISO: {iso_format}")
            return HCI.success({"original": datetime_str, "iso_format": iso_format, "date_only": date_only}, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())
        except ValueError as e:
            return HCI.bad_request(f"Invalid datetime string: {str(e)}", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())

    # Bucket (S3) testing

    async def get_buckets(self, request: Request) -> Response:
        """Get a list of all S3 bucket names.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON list of bucket names or error response.
        """
        self.bucket_connection = self.runtime_manager.get_if_exists(
            Bucket,
            self.bucket_connection
        )
        if not self.bucket_connection:
            return HCI.service_unavailable("S3 bucket connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug("Gathering buckets")
        data = self.bucket_connection.get_bucket_names()
        self.disp.log_debug(f"Gathered buckets: {data}")
        if isinstance(data, int):
            return HCI.not_found("Failed to retrieve bucket names", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        return HCI.success(data, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def test_bucket_connection(self, request: Request) -> Response:
        """Test if the S3 bucket connection is active.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON with connection status.
        """
        self.bucket_connection = self.runtime_manager.get_if_exists(
            Bucket,
            self.bucket_connection
        )
        if not self.bucket_connection:
            return HCI.service_unavailable("S3 bucket connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug("Testing bucket connection")
        is_connected: bool = self.bucket_connection.is_connected()
        result: Dict[str, Union[str, bool]] = {"connected": is_connected}
        node_id: str = "message"
        if is_connected:
            result[node_id] = "Connection is active"
        else:
            result[node_id] = "Connection failed"
        self.disp.log_debug(f"Connection status: {is_connected}")
        return HCI.success(result, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def get_bucket_files(self, request: Request) -> Response:
        """Get all files in a specific bucket.

        Query Parameters:
            bucket_name (str): Name of the bucket to list files from.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON list of file names or error response.
        """
        self.bucket_connection = self.runtime_manager.get_if_exists(
            Bucket,
            self.bucket_connection
        )
        if not self.bucket_connection:
            return HCI.service_unavailable("S3 bucket connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        bucket_name = request.query_params.get("bucket_name")
        if not bucket_name:
            return HCI.bad_request("Missing required parameter: bucket_name", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug(f"Gathering files from bucket: {bucket_name}")
        data = self.bucket_connection.get_bucket_files(bucket_name)
        self.disp.log_debug(f"Gathered files: {data}")
        if isinstance(data, int):
            return HCI.not_found(f"Failed to retrieve files from bucket '{bucket_name}'", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        return HCI.success({"bucket": bucket_name, "files": data}, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def get_bucket_file_info(self, request: Request) -> Response:
        """Get information about a specific file in a bucket.

        Query Parameters:
            bucket_name (str): Name of the bucket.
            file_name (str): Name of the file to get info about.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: JSON with file metadata or error response.
        """
        self.bucket_connection = self.runtime_manager.get_if_exists(
            Bucket,
            self.bucket_connection
        )
        if not self.bucket_connection:
            return HCI.service_unavailable("S3 bucket connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        bucket_name = request.query_params.get("bucket_name")
        file_name = request.query_params.get("file_name")
        if not bucket_name or not file_name:
            return HCI.bad_request("Missing required parameters: bucket_name and file_name", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug(
            f"Getting info for file '{file_name}' in bucket '{bucket_name}'"
        )
        data = self.bucket_connection.get_bucket_file(bucket_name, file_name)
        self.disp.log_debug(f"File info: {data}")
        if isinstance(data, int):
            return HCI.not_found(f"File '{file_name}' not found in bucket '{bucket_name}'", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        return HCI.success(data, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def create_test_bucket(self, request: Request) -> Response:
        """Create a new test bucket.

        Query Parameters:
            bucket_name (str): Name of the bucket to create.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: Success or error response.
        """
        self.bucket_connection = self.runtime_manager.get_if_exists(
            Bucket,
            self.bucket_connection
        )
        if not self.bucket_connection:
            return HCI.service_unavailable("S3 bucket connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        bucket_name = request.query_params.get("bucket_name")
        if not bucket_name:
            return HCI.bad_request("Missing required parameter: bucket_name", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug(f"Creating bucket: {bucket_name}")
        result = self.bucket_connection.create_bucket(bucket_name)
        if result != self.success:
            return HCI.internal_server_error(f"Failed to create bucket '{bucket_name}'", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug(f"Bucket '{bucket_name}' created successfully")
        return HCI.created({"message": f"Bucket '{bucket_name}' created successfully"}, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    async def delete_test_bucket(self, request: Request) -> Response:
        """Delete a test bucket.

        Query Parameters:
            bucket_name (str): Name of the bucket to delete.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: Success or error response.
        """
        self.bucket_connection = self.runtime_manager.get_if_exists(
            Bucket,
            self.bucket_connection
        )
        if not self.bucket_connection:
            return HCI.service_unavailable("S3 bucket connection not available", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        bucket_name = request.query_params.get("bucket_name")
        if not bucket_name:
            return HCI.bad_request("Missing required parameter: bucket_name", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug(f"Deleting bucket: {bucket_name}")
        result = self.bucket_connection.delete_bucket(bucket_name)
        if result != self.success:
            return HCI.internal_server_error(f"Failed to delete bucket '{bucket_name}'", content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        self.disp.log_debug(f"Bucket '{bucket_name}' deleted successfully")
        return HCI.success({"message": f"Bucket '{bucket_name}' deleted successfully"}, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())
