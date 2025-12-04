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
# FILE: sql_cache_orchestrator.py
# CREATION DATE: 18-11-2025
# LAST Modified: 3:51:0 25-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File that contains the class in charge of calling the redis cache if present and fallback to sql querying if absent.
# // AR
# +==== END CatFeeder =================+
"""

# typing helper
from typing import List, Dict, Union, Any, Tuple, Optional, Literal, overload, Callable


# logger class
from display_tty import Disp, initialise_logger

# sql wrapper components
from .sql_injection import SQLInjection
from .sql_constants import GET_TABLE_SIZE_ERROR
from .sql_query_boilerplates import SQLQueryBoilerplates
from .sql_redis_cache_rebinds import SQLRedisCacheRebinds
from .sql_sanitisation_functions import SQLSanitiseFunctions


class SQLCacheOrchestrator:

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, sql_query_boilerplates: SQLQueryBoilerplates, redis_cacher: Optional[SQLRedisCacheRebinds] = None, success: int = 0, error: int = 84, debug: bool = False) -> None:
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self.success: int = success
        self.error = error
        self.debug = debug
        # ---------------------- SQL boilerplate handler  ----------------------
        self._sql_query_boilerplate: SQLQueryBoilerplates = sql_query_boilerplates
        # ---------------------- Reddis caching instance  ----------------------
        self._redis_cacher: Optional[SQLRedisCacheRebinds] = redis_cacher

        # ---------------------- The anty injection class ----------------------
        self.sql_injection: SQLInjection = SQLInjection(
            self.error,
            self.success,
            self.debug
        )
        # -------------------- Keyword sanitizing functions --------------------
        self.sanitize_functions: SQLSanitiseFunctions = SQLSanitiseFunctions(
            success=self.success, error=self.error, debug=self.debug
        )
        self.disp.log_debug("Initialised")

    def _normalize_cell(self, cell: object) -> Union[str, None, int, float]:
        """Normalize a cell value for parameter binding.

        Converts special tokens (e.g., 'now', 'current_date') and preserves numeric
        types. Returns None for null-like inputs.

        Args:
            cell (object): The cell value to normalize.

        Returns:
            Union[str, None, int, float]: Normalized cell value.
        """
        if cell is None:
            return None
        if isinstance(cell, (int, float)):
            return cell
        s = str(cell)
        sl = s.lower()
        if sl in ("now", "now()"):
            return self.sanitize_functions.sql_time_manipulation.get_correct_now_value()
        if sl in ("current_date", "current_date()"):
            return self.sanitize_functions.sql_time_manipulation.get_correct_current_date_value()
        return s

    def update_redis_cacher(self, redis_cacher: Optional[SQLRedisCacheRebinds] = None) -> None:
        """Update the redis caching instance only with an initialised SQLRedisCacheRebinds class.
        This function has no effect if a non-initialised SQLRedisCacheRebinds class or other arguments are passed.

        Args:
            redis_cacher (Optional[SQLRedisCacheRebinds], optional): The initialised SQLRedisCacheRebinds class instance. Defaults to None.
        """
        if isinstance(redis_cacher, SQLRedisCacheRebinds) and not callable(redis_cacher):
            self._redis_cacher = redis_cacher

    def get_database_version(self) -> Optional[Tuple[int, int, int]]:
        """Fetch and parse the database version.

        Returns:
            Optional[Tuple[int, int, int]]: A tuple representing the database version,
            or None if the query fails.
        """
        sql_function: Callable = self._sql_query_boilerplate.get_database_version
        resp: Optional[Tuple[int, int, int]] = None
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.get_database_version(
                fetcher=sql_function
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function()
        return resp

    def get_table_column_names(self, table_name: str) -> Union[List[str], int]:
        """Return the list of column names for a given table.

        Args:
            table_name (str): Name of the table to retrieve column names from.

        Returns:
            Union[List[str], int]: List of column names on success, or `self.error` on failure.
        """
        sql_function: Callable = self._sql_query_boilerplate.get_table_column_names
        resp: Union[List[str], int] = self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.get_table_column_names(
                table_name=table_name,
                fetcher=sql_function,
                error_token=self.error
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(table_name)
        return resp

    def get_table_names(self) -> Union[int, List[str]]:
        """Retrieve the names of all tables in the database.

        Returns:
            Union[int, List[str]]: List of table names on success, or `self.error` on failure.
        """
        sql_function: Callable = self._sql_query_boilerplate.get_table_names
        resp: Union[int, List[str]] = self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.get_table_names(
                fetcher=sql_function,
                error_token=self.error
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function()
        return resp

    def get_triggers(self) -> Union[int, Dict[str, str]]:
        """Retrieve all triggers and their SQL definitions.

        Returns:
            Union[int, Dict[str, str]]: Dictionary of {trigger_name: sql_definition},
            or `self.error` on failure.
        """
        sql_function: Callable = self._sql_query_boilerplate.get_triggers
        resp: Union[int, Dict[str, str]] = self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.get_triggers(
                fetcher=sql_function,
                error_token=self.error
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function()
        return resp

    def get_trigger(self, trigger_name: str, db_name: Optional[str] = None) -> Union[int, str]:
        """Retrieve the SQL definition of a specific trigger.

        Args:
            trigger_name (str): The trigger name to fetch.
            db_name (Optional[str], optional): Database name. Defaults to None.

        Returns:
            Union[int, str]: The SQL definition, or `self.error` on failure.
        """
        sql_function: Callable = self._sql_query_boilerplate.get_trigger
        resp: Union[int, str] = self.error
        if not trigger_name:
            self.disp.log_error("Trigger name cannot be empty.")
            return self.error

        to_check: List[str] = [trigger_name]
        if db_name:
            to_check.append(db_name)

        if self.sql_injection.check_if_injections_in_strings(to_check):
            self.disp.log_error("SQL Injection detected in trigger name.")
            return self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.get_trigger(
                trigger_name=trigger_name,
                fetcher=sql_function,
                error_token=self.error
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(trigger_name)
        return resp

    def get_trigger_names(self, db_name: Optional[str] = None) -> Union[int, List[str]]:
        """Return a list of trigger names in the current or specified MySQL database.

        Args:
            db_name (Optional[str], optional):
                Name of the database/schema to query.
                Defaults to None, which uses the currently selected database.

        Returns:
            Union[int, List[str]]: List of trigger names, or ``self.error`` on failure.
        """
        sql_function: Callable = self._sql_query_boilerplate.get_trigger_names
        resp: Union[int, List[str]] = self.error
        if db_name:
            if self.sql_injection.check_if_injections_in_strings([db_name]):
                self.disp.log_error(
                    "SQL Injection detected in database name."
                )
                return self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.get_trigger_names(
                fetcher=sql_function,
                error_token=self.error
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(db_name)
        return resp

    def describe_table(self, table: str) -> Union[int, List[Any]]:
        """Fetch the headers (description) of a table from the database.

        Args:
            table (str): The name of the table to describe.

        Returns:
            Union[int, List[Any]]: A list containing the description of the table, or self.error if an error occurs.
        """
        sql_function: Callable = self._sql_query_boilerplate.describe_table
        resp: Union[List[str], int] = self.error
        if self.sql_injection.check_if_sql_injection(table) is True:
            self.disp.log_error("Injection detected.", "sql")
            return self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.describe_table(
                table=table,
                fetcher=sql_function,
                error_token=self.error
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(table)
        return resp

    def create_table(self, table: str, columns: List[Tuple[str, str]]) -> int:
        """Create a new table in the MySQL database, compatible with MySQL 5.0+.

        Args:
            table (str): Name of the new table.
            columns (List[Tuple[str, str]]): List of (column_name, column_type) pairs.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.

        Example:
            .. code-block:: python

                table_name = "users"
                columns = [
                    ("id", "INT AUTO_INCREMENT PRIMARY KEY"),
                    ("username", "VARCHAR(255) NOT NULL UNIQUE"),
                    ("email", "VARCHAR(255) NOT NULL"),
                    ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
                ]

                result = self.create_table(table_name, columns)
                if result == self.success:
                    print(f"Table '{table_name}' created successfully.")
                else:
                    print(f"Failed to create table '{table_name}'.")

        Notes:
            - Protects against SQL injection using :class:`SQLInjection`.
            - Escapes table and column names with backticks for MySQL.
            - Includes version-aware fallback for MySQL 5.0 compatibility.
        """
        sql_function: Callable[
            [str, List[Tuple[str, str]]],
            int
        ] = self._sql_query_boilerplate.create_table
        resp: int = self.error
        if self.sql_injection.check_if_injections_in_strings([table]):
            self.disp.log_error("Injection detected in table name.")
            return self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.create_table(
                table=table,
                columns=columns,
                writer=sql_function
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(table, columns)
        return resp

    def insert_data_into_table(self, table: str, data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], column: Union[List[str], None] = None) -> int:
        """Insert data into a table.

        Args:
            table (str): Name of the table.
            data (Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]]): Data to insert.
            column (Union[List[str], None], optional): List of column names. Defaults to None.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        sql_function: Callable = self._sql_query_boilerplate.insert_data_into_table
        resp: int = self.error
        if column is None:
            column = []
        check_data: Union[
            List[List[Union[str, None, int, float]]],
            List[Union[str, None, int, float]]
        ] = [table]
        if column is not None:
            check_data.extend(column)
        if isinstance(data, List):
            for i in data:
                if isinstance(i, List):
                    check_data.extend(i)
                else:
                    check_data.append(i)
        if self.sql_injection.check_if_injections_in_strings(check_data) is True:
            self.disp.log_error("Injection detected.", "sql")
            return self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.insert_data_into_table(
                table=table,
                data=data,
                column=column,
                writer=sql_function
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(table, data, column)
        return resp

    def insert_trigger(self, trigger_name: str, table_name: str, timing_event: str, body: str) -> int:
        """Insert (create) a new SQL trigger into a MySQL or MariaDB database.

        Args:
            trigger_name (str): The name of the trigger to create.
            table_name (str): The name of the table the trigger is being applied to.
            timing_event (str): The rule when the event is to be triggered. e.g., 'BEFORE INSERT'.
            body (str): The full SQL CREATE TRIGGER statement.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        sql_function: Callable = self._sql_query_boilerplate.insert_trigger
        resp: int = self.error
        if not all([trigger_name, table_name, timing_event, body]):
            self.disp.log_error("All parameters must be provided.")
            return self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.insert_trigger(
                trigger_name=trigger_name,
                table_name=table_name,
                timing_event=timing_event,
                body=body,
                writer=sql_function
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(trigger_name, table_name, timing_event, body)
        return resp

    @overload
    def get_data_from_table(
        self,
        table: str,
        column: Union[str, List[str]],
        where: Union[str, List[str]] = "",
        beautify: Literal[True] = True,
    ) -> Union[int, List[Dict[str, Any]]]: ...

    @overload
    def get_data_from_table(
        self,
        table: str,
        column: Union[str, List[str]],
        where: Union[str, List[str]] = "",
        beautify: Literal[False] = False,
    ) -> Union[int, List[Tuple[Any, Any]]]: ...

    def get_data_from_table(self, table: str, column: Union[str, List[str]], where: Union[str, List[str]] = "", beautify: bool = True) -> Union[int, Union[List[Dict[str, Any]], List[Tuple[Any, Any]]]]:
        """Fetch rows from a table.

        Args:
            table (str): Name of the table to query.
            column (Union[str, List[str]]): Column selector; a single column name or a list of column names.
            where (Union[str, List[str]]): Optional WHERE clause content; string or list joined by ``AND``.
            beautify (bool): When True, return a list of dict rows; when False, return a list of tuples.

        Returns:
            Union[int, List[Dict[str, Any]], List[Tuple[Any, Any]]]: Query result on success, or ``self.error`` on failure.
        """
        sql_function: Callable = self._sql_query_boilerplate.get_data_from_table
        resp: Union[
            int,
            Union[
                List[Dict[str, Any]],
                List[Tuple[Any, Any]]
            ]
        ] = self.error
        if self.sql_injection.check_if_injections_in_strings([table, column]) is True or self.sql_injection.check_if_symbol_and_command_injection(where) is True:
            self.disp.log_error("Injection detected.", "sql")
            return self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.get_data_from_table(
                table=table,
                column=column,
                where=where,
                beautify=beautify,
                fetcher=sql_function,
                error_token=self.error
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(table, column, where, beautify)
        return resp

    def get_table_size(self, table: str, column: Union[str, List[str]], where: Union[str, List[str]] = "") -> int:
        """Return the row count for a table.

        Args:
            table (str): Name of the table to count rows in.
            column (Union[str, List[str]]): Column expression passed to ``COUNT(...)``.
            where (Union[str, List[str]]): Optional WHERE clause content; string or list joined by ``AND``.

        Returns:
            int: Number of rows on success, or ``GET_TABLE_SIZE_ERROR`` on failure.
        """
        sql_function: Callable = self._sql_query_boilerplate.get_table_size
        resp: int = self.error
        if self.sql_injection.check_if_injections_in_strings([table, column]) is True or self.sql_injection.check_if_symbol_and_command_injection(where) is True:
            self.disp.log_error("Injection detected.", "sql")
            return GET_TABLE_SIZE_ERROR
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.get_table_size(
                table=table,
                column=column,
                where=where,
                fetcher=sql_function
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(table, column, where)
        return resp

    def update_data_in_table(self, table: str, data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], column: List[str], where: Union[str, List[str]] = "") -> int:
        """Update rows in a table.

        Args:
            table (str): Name of the table to update.
            data (Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]]): Values aligned to ``column`` order; single row or list of rows.
            column (List[str]): Column names to update.
            where (Union[str, List[str]]): Optional WHERE clause content; string or list joined by ``AND``.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        sql_function: Callable = self._sql_query_boilerplate.update_data_in_table
        resp: int = self.error
        if column is None:
            column = ""

        # Only check table/column names for injection — data is parameterized
        check_items = [table]
        if isinstance(column, list):
            check_items.extend([str(c) for c in column])
        else:
            check_items.append(str(column))
        if self.sql_injection.check_if_injections_in_strings(check_items) or self.sql_injection.check_if_symbol_and_command_injection(where):
            self.disp.log_error("Injection detected.", "sql")
            return self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.update_data_in_table(
                table=table,
                data=data,
                column=column,
                where=where,
                writer=sql_function
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(table, data, column, where)
        return resp

    def insert_or_update_data_into_table(self, table: str, data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], columns: Union[List[str], None] = None) -> int:
        """Insert or update rows using the first column as key.

        Args:
            table (str): Table name.
            data (Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]]): Single row or list of rows to upsert.
            columns (Union[List[str], None], optional): Column names for ``data``; when None, infer columns from the table.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        sql_function: Callable = self._sql_query_boilerplate.insert_or_update_data_into_table
        resp: int = self.error
        check_list = [table]
        if columns:
            check_list.extend(columns)
        if self.sql_injection.check_if_injections_in_strings(check_list):
            self.disp.log_error("SQL Injection detected.", "sql")
            return self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.insert_or_update_data_into_table(
                table=table,
                data=data,
                columns=columns,
                writer=sql_function
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(table, data, columns)
        return resp

    def insert_or_update_trigger(self, trigger_name: str, table_name: str, timing_event: str, body: str) -> int:
        """Insert (create) or update an SQL trigger into a MySQL or MariaDB database.

        Args:
            trigger_name (str): The name of the trigger to create.
            table_name (str): The name of the table the trigger is being applied to.
            timing_event (str): The rule when the event is to be triggered. e.g., 'BEFORE INSERT'.
            body (str): The full SQL CREATE TRIGGER statement.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        sql_function: Callable = self._sql_query_boilerplate.insert_or_update_trigger
        resp: int = self.error
        if self.sql_injection.check_if_injections_in_strings([trigger_name, table_name]):
            self.disp.log_error("SQL injection detected.")
            return self.error

        if self.sql_injection.check_if_symbol_and_logic_gate_injection(timing_event):
            self.disp.log_error("SQL injection detected")
            return self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.insert_or_update_trigger(
                trigger_name=trigger_name,
                table_name=table_name,
                timing_event=timing_event,
                body=body,
                writer=sql_function
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(trigger_name, table_name, timing_event, body)
        return resp

    def remove_data_from_table(self, table: str, where: Union[str, List[str]] = "") -> int:
        """Delete rows from a table.

        Args:
            table (str): Table name.
            where (Union[str, List[str]]): Optional WHERE clause to limit deletions.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        sql_function: Callable = self._sql_query_boilerplate.remove_data_from_table
        resp: int = self.error
        if self.sql_injection.check_if_sql_injection(table) is True or self.sql_injection.check_if_symbol_and_command_injection(where) is True:
            self.disp.log_error("Injection detected.", "sql")
            return self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.remove_data_from_table(
                table=table,
                where=where,
                writer=sql_function
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(table, where)
        return resp

    def remove_table(self, table: str) -> int:
        """Drop a table from the MySQL database.

        Args:
            table (str): Name of the table to drop.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.

        Notes:
            - Performs SQL injection detection on the table name.
            - Uses ``DROP TABLE IF EXISTS`` to avoid errors when the table is missing.
        """
        sql_function: Callable = self._sql_query_boilerplate.remove_table
        resp: int = self.error
        if self.sql_injection.check_if_injections_in_strings([table]):
            self.disp.log_error("Injection detected in table name.")
            return self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.remove_table(
                table=table,
                writer=sql_function
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(table)
        return resp

    def remove_trigger(self, trigger_name: str) -> int:
        """Drop/Remove an existing SQL trigger if it exists.

        Args:
            trigger_name (str): Name of the trigger to drop.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on error.
        """
        sql_function: Callable = self._sql_query_boilerplate.remove_trigger
        resp: int = self.error
        if not trigger_name:
            self.disp.log_error("Trigger name cannot be empty.")
            return self.error
        if self.sql_injection.check_if_injections_in_strings([trigger_name]):
            self.disp.log_error("SQL Injection detected in trigger name.")
            return self.error
        if self._redis_cacher:
            self.disp.log_debug("Cacher instance is defined, calling.")
            resp = self._redis_cacher.remove_trigger(
                trigger_name=trigger_name,
                writer=sql_function
            )
        else:
            self.disp.log_debug(
                "No cacher instance defined, calling sql boilerplate directly."
            )
            resp = sql_function(trigger_name)
        return resp
