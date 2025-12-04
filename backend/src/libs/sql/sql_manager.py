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
# FILE: sql_manager.py
# CREATION DATE: 11-10-2025
# LAST Modified: 7:30:29 02-12-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE:
# File in charge of containing the interfacing between an sql library and the program.
# This contains functions that simplify the process of interracting with databases as well as check for injection attempts.
# /STOP
# // AR
# +==== END CatFeeder =================+

"""

from typing import Optional, Union, List, Dict, Tuple, Literal, Any, overload

from datetime import datetime

from display_tty import Disp, initialise_logger
from redis import Redis
try:
    import mysql.connector as mysql_connector  # type: ignore
    _MYSQL_ERROR_TUPLE: tuple = (mysql_connector.Error,)
except ImportError:  # mysql-connector may be optional in some deployments
    mysql_connector = None  # type: ignore
    _MYSQL_ERROR_TUPLE = tuple()

from .sql_time_manipulation import SQLTimeManipulation
from .sql_connections import SQLManageConnections
from .sql_query_boilerplates import SQLQueryBoilerplates
from .sql_cache_orchestrator import SQLCacheOrchestrator
from .sql_redis_cache_rebinds import RedisCaching, RedisArgs, SQLRedisCacheRebinds
from ..core import FinalClass

# Specific exception tuple used when closing/destroying pool resources without
# resorting to a broad Exception catch. Includes AttributeError/RuntimeError and
# mysql connector Error when available.
_EXC_POOL_CLOSE = (AttributeError, RuntimeError) + _MYSQL_ERROR_TUPLE


class SQL(metaclass=FinalClass):
    """Manage database access and provide high-level query helpers.

    This class wraps a low-level connection manager and exposes convenience
    methods for common operations. Can auto-initialize via RuntimeManager or
    use :py:meth:`create` for explicit factory initialization.

    Attributes:
        disp (Disp): Logger instance for debugging and error reporting.
        sql_manage_connections (SQLManageConnections): Manages database connections.
        sql_time_manipulation (SQLTimeManipulation): Handles time-related SQL operations.
        sql_cache_orchestrator (SQLQueryBoilerplates): Provides query boilerplates.
        debug (bool): Debug mode flag.
        success (int): Numeric success code.
        error (int): Numeric error code.
        url (str): Database URL.
        port (int): Database port.
        username (str): Database username.
        password (str): Database password.
        db_name (str): Database name.
    """

    # --------------------------------------------------------------------------
    # STATIC CLASS VALUES
    # --------------------------------------------------------------------------

    # -------------- Initialise the logger globally in the class. --------------
    disp: Disp = initialise_logger(__qualname__, False)

    # ------------------ Runtime error for undefined elements ------------------
    _runtime_error_string: str = "SQLCacheOrchestrator method not initialized"

    # Docstring wrapper notice
    _wrapper_notice_begin: str = "(Wrapper) Delegates to SQLQueryBoilerplates."
    _wrapper_notice_end: str = "\n\nOriginal docstring:\n"

    # --- Instance tracker to avoid creating unnecessary duplicate instances ---
    _instace: Optional['SQL'] = None
    _initialization_attempted: bool = False
    _initialization_failed: bool = False

    # --------------------------------------------------------------------------
    # CONSTRUCTOR & DESTRUCTOR
    # --------------------------------------------------------------------------

    def __init__(self, url: str, port: int, username: str, password: str, db_name: str, *, success: int = 0, error: int = 84, redis: Optional[Union[Redis, RedisArgs, RedisCaching]] = None, redis_namespace: str = "sql", redis_db_label: Optional[str] = None, redis_default_ttls: Optional[Dict[str, int]] = None, auto_initialize: bool = True, debug: bool = False):
        """Initialize the SQL facade instance.

        Args:
            url (str): Database URL.
            port (int): Database port.
            username (str): Database username.
            password (str): Database password.
            db_name (str): Database name.
            success (int, optional): Numeric success code. Defaults to 0.
            error (int, optional): Numeric error code. Defaults to 84.
            redis (union[Redis, RedisArgs, RedisCaching], optional): The arguments to initialise the redis caching instance. Defaults to None.
            redis_namespace (str, optional): The name of the namespace to use in the redis environement. Defaults to sql.
            redis_db_label (str, optional): Optional database label to isolate keys per DB. Defaults to the `DB_NAME` environment variable or "default". Defaults to None.
            redis_default_ttls (Dict[str, str], optional): Optional TTLs in seconds per category (`version`, `schema`, `data`, `count`). Defaults to None.
            auto_initialize (bool, optional): If True, automatically initialize connection pool. Defaults to True.
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self.debug: bool = debug
        self.success: int = success
        self.error: int = error
        self.url: str = url
        self.port: int = port
        self.username: str = username
        self.password: str = password
        self.db_name: str = db_name

        self.sql_time_manipulation = SQLTimeManipulation(
            self.debug
        )
        self._get_correct_now_value = self.sql_time_manipulation.get_correct_now_value
        self._get_correct_current_date_value = self.sql_time_manipulation.get_correct_current_date_value
        # --------------------------- debug section  ---------------------------
        # Note: pool initialisation is  Use the factory `create` to
        # obtain a fully-initialized SQL instance.
        self.sql_manage_connections = SQLManageConnections(
            url=self.url,
            port=self.port,
            username=self.username,
            password=self.password,
            db_name=self.db_name,
            success=self.success,
            error=self.error,
            debug=self.debug
        )

        # ---------------------------- Time logger  ----------------------------
        self.sql_time_manipulation = SQLTimeManipulation(
            self.debug
        )
        self._get_correct_now_value = self.sql_time_manipulation.get_correct_now_value
        self._get_correct_current_date_value = self.sql_time_manipulation.get_correct_current_date_value
        # ----------------------- Redis caching instance -----------------------
        self.redis_cacher: Optional[SQLRedisCacheRebinds] = None
        self.redis_namespace: str = redis_namespace
        self.redis_db_label: Optional[str] = redis_db_label
        self.redis_default_ttls: Optional[Dict[str, int]] = redis_default_ttls
        if isinstance(redis, SQLRedisCacheRebinds):
            self.redis_cacher = redis
        elif isinstance(redis, RedisCaching):
            self.redis_cacher = SQLRedisCacheRebinds(
                existing_instance=redis,
                debug=self.debug
            )
        elif isinstance(redis, (Redis, RedisArgs)):
            self.redis_cacher = SQLRedisCacheRebinds(
                client=redis,
                namespace=redis_namespace,
                db_label=redis_db_label,
                default_ttls=redis_default_ttls
            )

        # --------------------------- debug section  ---------------------------
        # Note: pool initialisation is  Use the factory `create` to
        # obtain a fully-initialized SQL instance.
        self.sql_manage_connections.show_connection_info()
        # sql_cache_orchestrator will be created by the factory once the
        # connection pool is initialised.
        self._sql_query_boilerplate: Optional[SQLQueryBoilerplates] = None
        self.sql_cache_orchestrator: Optional[SQLCacheOrchestrator] = None
        self._is_initialized: bool = False

        # Auto-initialize if requested (for RuntimeManager compatibility)
        if auto_initialize:
            self._auto_initialize()

        self.disp.log_debug("Initialised")

    def _auto_initialize(self) -> None:
        """Automatically initialize connection pool and query helpers.

        Called during __init__ when auto_initialize=True.
        Tracks initialization attempts to provide better error messages.
        """
        SQL._initialization_attempted = True
        try:
            assert self.sql_manage_connections is not None, "sql_manage_connections not initialized"
            if self.sql_manage_connections.initialise_pool() != self.success:
                SQL._initialization_failed = True
                msg = "Failed to initialise the connection pool."
                self.disp.log_critical(msg)
                raise RuntimeError(f"Error: {msg}")

            # Create the query helper now that the pool is ready
            self._sql_query_boilerplate = SQLQueryBoilerplates(
                sql_pool=self.sql_manage_connections,
                success=self.success,
                error=self.error,
                debug=self.debug
            )
            self.sql_cache_orchestrator = SQLCacheOrchestrator(
                sql_query_boilerplates=self._sql_query_boilerplate,
                redis_cacher=self.redis_cacher,
                success=self.success,
                error=self.error,
                debug=self.debug
            )
            self._is_initialized = True
        except Exception as e:
            SQL._initialization_failed = True
            self.disp.log_critical(f"Initialization failed: {e}")
            raise

    def __del__(self) -> None:
        """Best-effort cleanup invoked when the instance is garbage-collected.

        This releases references to internal helpers so external resources
        can be freed by the event loop later. Avoiding inside destructors.
        """
        if self.sql_manage_connections is not None:
            del self.sql_manage_connections
            self.sql_manage_connections = None
        if self.sql_time_manipulation is not None:
            del self.sql_time_manipulation
            self.sql_time_manipulation = None
        if self._sql_query_boilerplate is not None:
            del self._sql_query_boilerplate
            self._sql_query_boilerplate = None
        if self.sql_cache_orchestrator is not None:
            del self.sql_cache_orchestrator
            self.sql_cache_orchestrator = None

    def _ensure_initialized(self) -> None:
        """Ensure the SQL instance is initialized.

        If initialization was never attempted, try to auto-initialize.
        If initialization was attempted but failed, raise an error.

        Raises:
            RuntimeError: If initialization has failed or cannot be performed.
        """
        if self._is_initialized:
            return

        if SQL._initialization_failed:
            raise RuntimeError(
                "SQL initialization has previously failed. Cannot perform operations on a failed instance."
            )

        if not SQL._initialization_attempted:
            self.disp.log_debug(
                "Attempting lazy initialization", "_ensure_initialized"
            )
            self._auto_initialize()
        elif not self._is_initialized:
            raise RuntimeError(
                "SQL instance is not properly initialized. Use auto_initialize=True or call create() factory method."
            )

    # --------------------------------------------------------------------------
    # WRAPPER DEFINITIONS
    # --------------------------------------------------------------------------

    def datetime_to_string(self, datetime_instance: datetime, date_only: bool = False, sql_mode: bool = False) -> str:
        """(Wrapper) Delegates to SQLTimeManipulation.datetime_to_string

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Format a :class:`datetime` to the project's string representation.

        Args:
            datetime_instance (datetime): Datetime to format.
            date_only (bool): When True, return only the date portion.
            sql_mode (bool): When True, include millisecond precision suitable
                for insertion into SQL text fields.

        Raises:
            ValueError: If ``datetime_instance`` is not a :class:`datetime`.

        Returns:
            str: Formatted date/time string.
        """
        if self.sql_time_manipulation is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_time_manipulation.datetime_to_string(datetime_instance, date_only, sql_mode)

    def string_to_datetime(self, datetime_string_instance: str, date_only: bool = False) -> datetime:
        """(Wrapper) Delegates to SQLTimeManipulation.string_to_datetime

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Parse a formatted date/time string into a :class:`datetime`.

        Args:
            datetime_string_instance (str): The string to parse.
            date_only (bool): When True, parse using the date-only format.

        Raises:
            ValueError: If the input is not a string or cannot be parsed.

        Returns:
            datetime: Parsed :class:`datetime` instance.
        """
        if self.sql_time_manipulation is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_time_manipulation.string_to_datetime(datetime_string_instance, date_only)

    def is_connected(self) -> bool:
        """(Wrapper) Delegates to SQLManageConnection.is_connected

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:
        Check if there is an active connection to the database.

        Returns:
            bool: The state of the connection.
        """
        if self.sql_manage_connections is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_manage_connections.is_connected()

    def get_correct_now_value(self) -> str:
        """(Wrapper) Delegates to SQLTimeManipulation.get_correct_now_value

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return the current date/time formatted using the project's pattern.

        Returns:
            str: Formatted current date/time string.
        """
        if self.sql_time_manipulation is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_time_manipulation.get_correct_now_value()

    def get_correct_current_date_value(self) -> str:
        """(Wrapper) Delegates to SQLTimeManipulation.get_correct_current_date_value

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return the current date formatted using the project's date-only pattern.

        Returns:
            str: Formatted current date string.
        """
        if self.sql_time_manipulation is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_time_manipulation.get_correct_current_date_value()

    def get_database_version(self) -> Optional[Tuple[int, int, int]]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.create_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Fetch and parse the database version.

        Returns:
            Optional[Tuple[Union[int, str], ...]]:
                A tuple representing the database version, or None if the query fails.
        """
        self._ensure_initialized()
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.get_database_version()

    def update_redis_cacher(self, redis_cacher: Optional[RedisCaching] = None) -> None:
        """(Wrapper) Delegates to SQLQueryBoilerplates.create_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Update the redis caching instance only with an initialised RedisCaching class.
        This function has no effect if a non-initialised RedisCaching class or other arguments are passed.

        Args:
            redis_cacher (Optional[RedisCaching], optional): The initialised RedisCaching class instance. Defaults to None.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        if isinstance(redis_cacher, RedisCaching) and not callable(redis_cacher):
            self.redis_cacher = SQLRedisCacheRebinds(
                existing_instance=redis_cacher
            )
        self.sql_cache_orchestrator.update_redis_cacher(self.redis_cacher)

    def get_table_column_names(self, table_name: str) -> Union[List[str], int]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.get_table_column_names

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return the list of column names for ``table_name``.

        Args:
            table_name (str): Name of the table to inspect.

        Returns:
            Union[List[str], int]: List of column names on success, or
            ``self.error`` on failure.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.get_table_column_names(table_name)

    def get_table_names(self) -> Union[int, List[str]]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.get_table_names

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return a list of non-internal table names in the database.

        Returns:
            Union[int, List[str]]: List of table names or ``self.error`` on failure.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.get_table_names()

    def get_triggers(self) -> Union[int, Dict[str, str]]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.get_triggers

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return a dictionary of all triggers and their SQL definitions.

        Returns:
            Union[int, Dict[str, str]]: Dict of {trigger_name: sql_definition}, or ``self.error``.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.get_triggers()

    def get_trigger(self, trigger_name: str) -> Union[int, str]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.get_trigger

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return a dictionary of all triggers and their SQL definitions.

        Returns:
            Union[int, Dict[str, str]]: Dict of {trigger_name: sql_definition}, or ``self.error``.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.get_trigger(trigger_name)

    def get_trigger_names(self) -> Union[int, List[str]]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.get_trigger_names

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return a list of non-internal trigger names in the database.

        Returns:
            Union[int, List[str]]: List of trigger names, or ``self.error`` on failure.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.get_trigger_names()

    def describe_table(self, table: str) -> Union[int, List[Any]]:
        """(Wrapper) Delegates to SQLQueryBoilerplates.describe_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Fetch the schema description for a table.

        This returns rows similar to SQLite's PRAGMA table_info but is
        transformed so the first element is the column name (to remain
        compatible with previous MySQL-style DESCRIBE results).

        Args:
            table (str): Name of the table to describe.

        Raises:
            RuntimeError: On critical SQLite errors (re-raised as RuntimeError).

        Returns:
            Union[int, List[Any]]: Transformed description rows on success,
            or ``self.error`` on failure.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.describe_table(table)

    def create_table(self, table: str, columns: List[Tuple[str, str]]) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.create_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Create a new table in the SQLite database.

        Args:
            table (str): Name of the new table.
            columns (List[Tuple[str, str]]): List of (column_name, column_type) pairs.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.

        Example:
            Example usage to create a basic ``users`` table:

            .. code-block:: python

                # Define the table name and column definitions
                table_name = "users"
                columns = [
                    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                    ("username", "TEXT NOT NULL UNIQUE"),
                    ("email", "TEXT NOT NULL"),
                    ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
                ]

                # Create the table ronously
                result = self.create_table(table_name, columns)

                # Check if the operation succeeded
                if result == self.success:
                    print(f"Table '{table_name}' created successfully.")
                else:
                    print(f"Failed to create table '{table_name}'.")

        Notes:
            - This method automatically checks for SQL injection attempts using :class:`SQLInjection` before executing the query.
            - Single quotes in table or column names are escaped defensively.
            - The query uses ``CREATE TABLE IF NOT EXISTS`` to avoid errors if the table already exists.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.create_table(table, columns)

    def create_trigger(self, trigger_name: str, table_name: str, timing_event: str, body: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.insert_trigger

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Insert (create) a new SQL trigger into a MySQL or MariaDB database.

        Args:
            trigger_name (str): The name of the trigger to create.
            table_name (str): The name of the table the trigger is being applied to.
            timing_event (str): The rule when the event is to be triggered. e.g., 'BEFORE INSERT'.
            body (str): The full SQL CREATE TRIGGER statement.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.insert_trigger(trigger_name, table_name, timing_event, body)

    def insert_trigger(self, trigger_name: str, table_name: str, timing_event: str, body: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.insert_trigger

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Insert (create) a new SQL trigger into a MySQL or MariaDB database.

        Args:
            trigger_name (str): The name of the trigger to create.
            table_name (str): The name of the table the trigger is being applied to.
            timing_event (str): The rule when the event is to be triggered. e.g., 'BEFORE INSERT'.
            body (str): The full SQL CREATE TRIGGER statement.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.insert_trigger(trigger_name, table_name, timing_event, body)

    def insert_data_into_table(self, table: str, data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], column: Union[List[str], None] = None) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.insert_data_into_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Insert one or multiple rows into ``table``.

        Args:
            table (str): Table name.
            data (Union[List[List[str]], List[str]]): Row data. Either a
                single row (List[str]) or a list of rows (List[List[str]]).
            column (List[str] | None): Optional list of columns to insert into.

        Returns:
            int: ``self.success`` on success or ``self.error`` on failure.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.insert_data_into_table(table, data, column)

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
        """(Wrapper) Delegates to SQLQueryBoilerplates.get_data_from_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Query rows from ``table`` and optionally return them in a beautified form.

        Args:
            table (str): Table name.
            column (Union[str, List[str]]): Column name(s) or '*' to select.
            where (Union[str, List[str]], optional): WHERE clause or list of
                conditions. Defaults to empty string.
            beautify (bool, optional): If True, convert rows to list of dicts
                keyed by column names. Defaults to True.

        Returns:
            Union[int, List[Dict[str, Any]], List[Tuple[str, Any]]]: Beautified list of Dictionaries on success and if beautify is True, otherwise, a list of tuples is beautify is set to False, or ``self.error`` on failure.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.get_data_from_table(table, column, where, beautify)

    def get_table_size(self, table: str, column: Union[str, List[str]], where: Union[str, List[str]] = "") -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.get_table_size

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Return the number of rows matching the optional WHERE clause.

        Args:
            table (str): Table name.
            column (Union[str, List[str]]): Column to COUNT over (often '*').
            where (Union[str, List[str]], optional): WHERE clause or list of
                conditions. Defaults to empty string.

        Returns:
            int: Number of matching rows, or ``SCONST.GET_TABLE_SIZE_ERROR`` on error.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.get_table_size(table, column, where)

    def update_data_in_table(self, table: str, data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], column: List[str], where: Union[str, List[str]] = "") -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.update_data_in_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Update rows in ``table`` matching ``where`` with values from ``data``.

        Args:
            table (str): Table name.
            data (List[str]): New values to set.
            column (List): Column names corresponding to data.
            where (Union[str, List[str]], optional): WHERE clause or list of
                conditions. Defaults to empty string.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.update_data_in_table(table, data, column, where)

    def insert_or_update_data_into_table(self, table: str, data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], columns: Union[List[str], None] = None) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.insert_or_update_data_into_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Insert new rows or update existing rows for ``table``.

        This method determines column names if not provided and delegates
        to the appropriate INSERT/UPDATE boilerplate.

        Args:
            table (str): Table name.
            data (Union[List[List[str]], List[str]]): Data to insert or update.
            columns (List[str] | None, optional): Column names. Defaults to None.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on error.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.insert_or_update_data_into_table(table, data, columns)

    def insert_or_update_trigger(self,  trigger_name: str, table_name: str, timing_event: str, body: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.insert_or_update_trigger

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Insert (create) or update an SQL trigger into a MySQL or MariaDB database.

        Args:
            trigger_name (str): The name of the trigger to create.
            table_name (str): The name of the table the trigger is being applied to.
            timing_event (str): The rule when the event is to be triggered. e.g., 'BEFORE INSERT'.
            body (str): The full SQL CREATE TRIGGER statement.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.insert_or_update_trigger(trigger_name, table_name, timing_event, body)

    def remove_data_from_table(self, table: str, where: Union[str, List[str]] = "") -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.remove_data_from_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Delete rows from ``table`` matching ``where``.

        Args:
            table (str): Table name to delete rows from.
            where (Union[str, List[str]], optional): WHERE clause or list of
                conditions to filter rows. If empty, all rows are deleted.

        Returns:
            int: ``self.success`` on success or ``self.error`` on failure.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.remove_data_from_table(table, where)

    def drop_data_from_table(self, table: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.remove_data_from_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Delete rows from ``table`` matching ``where``.

        Args:
            table (str): Table name to delete rows from.
            where (Union[str, List[str]], optional): WHERE clause or list of
                conditions to filter rows. If empty, all rows are deleted.

        Returns:
            int: ``self.success`` on success or ``self.error`` on failure.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        # alias for remove_data_from_table to preserve API consistency
        return self.sql_cache_orchestrator.remove_data_from_table(table)

    def remove_table(self, table: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.remove_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Drop/Remove (delete) a table from the SQLite database.

        Args:
            table (str): Name of the table to drop.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.

        Example:
            Example usage to drop the ``users`` table:

            .. code-block:: python

                table_name = "users"
                result = self.drop_table(table_name)

                if result == self.success:
                    print(f"Table '{table_name}' dropped successfully.")
                else:
                    print(f"Failed to drop table '{table_name}'.")

        Notes:
            - The method performs SQL injection detection on the table name.
            - If the table does not exist, no error is raised (uses ``DROP TABLE IF EXISTS`` internally).
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.remove_table(table)

    def drop_table(self, table: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.remove_table

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Drop/Remove (delete) a table from the SQLite database.

        Args:
            table (str): Name of the table to drop.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on failure.

        Example:
            Example usage to drop the ``users`` table:

            .. code-block:: python

                table_name = "users"
                result = self.drop_table(table_name)

                if result == self.success:
                    print(f"Table '{table_name}' dropped successfully.")
                else:
                    print(f"Failed to drop table '{table_name}'.")

        Notes:
            - The method performs SQL injection detection on the table name.
            - If the table does not exist, no error is raised (uses ``DROP TABLE IF EXISTS`` internally).
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.remove_table(table)

    def remove_trigger(self, trigger_name: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.remove_trigger

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Drop/Remove an existing SQL trigger if it exists.

        Args:
            trigger_name (str): Name of the trigger to drop.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on error.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.remove_trigger(trigger_name)

    def drop_trigger(self, trigger_name: str) -> int:
        """(Wrapper) Delegates to SQLQueryBoilerplates.remove_trigger

        Raises:
            Runtime error if the class is not yet declared.

        Original docstring:

        Drop/Remove an existing SQL trigger if it exists.

        Args:
            trigger_name (str): Name of the trigger to drop.

        Returns:
            int: ``self.success`` on success, or ``self.error`` on error.
        """
        if self.sql_cache_orchestrator is None:
            raise RuntimeError(self._runtime_error_string)
        return self.sql_cache_orchestrator.remove_trigger(trigger_name)

    # --------------------------------------------------------------------------
    # FACTORY + CLEANUP
    # --------------------------------------------------------------------------
    @classmethod
    def create(cls, url: str, port: int, username: str, password: str, db_name: str, success: int = 0, error: int = 84, debug: bool = False) -> 'SQL':
        """factory to create and initialise an SQL instance.

        This factory completes ronous initialisation steps that the
        synchronous constructor cannot perform (notably the connection
        pool initialisation). After this call returns the instance is ready
        for usage and convenience callables are bound on the
        instance.

        Args:
            url (str): DB host or file path (for sqlite this is a filename).
            port (int): DB port (unused for sqlite but retained for API
                compatibility).
            username (str): DB username (unused for sqlite).
            password (str): DB password (unused for sqlite).
            db_name (str): Database name or sqlite filename.
            success (int, optional): numeric success code used across the
                sql helpers. Defaults to 0.
            error (int, optional): numeric error code used across the sql
                helpers. Defaults to 84.
            debug (bool, optional): enable debug logging. Defaults to False.

        Returns:
            SQL: Initialized SQL instance ready for operations.

        Raises:
            RuntimeError: If the connection pool cannot be initialised.

        Example:
            sql = SQL.create('db.sqlite', 0, '', '', 'db.sqlite')
            sql.get_data_from_table('my_table')
        """

        self = cls(
            url,
            port,
            username,
            password,
            db_name,
            success=success,
            error=error,
            auto_initialize=False,  # Don't auto-init, we'll do it manually
            debug=debug
        )
        # Manually initialize the connection pool
        # static checkers see `sql_manage_connections` as Optional; assert
        # it's available to narrow the type for the following calls.
        assert self.sql_manage_connections is not None
        assert self.disp is not None
        if self.sql_manage_connections.initialise_pool() != self.success:
            msg = "Failed to initialise the connection pool."
            self.disp.log_critical(msg)
            raise RuntimeError(f"Error: {msg}")
        # Create the query helper now that the pool is ready
        self._sql_query_boilerplate = SQLQueryBoilerplates(
            sql_pool=self.sql_manage_connections,
            success=self.success,
            error=self.error,
            debug=self.debug
        )
        self.sql_cache_orchestrator = SQLCacheOrchestrator(
            sql_query_boilerplates=self._sql_query_boilerplate,
            redis_cacher=self.redis_cacher,
            success=self.success,
            error=self.error,
            debug=self.debug
        )
        self._is_initialized = True
        return self

    def close(self) -> None:
        """Cleanly close resources like the connection pool."""
        if self.sql_manage_connections is not None:
            try:
                status = self.sql_manage_connections.destroy_pool()
            except _EXC_POOL_CLOSE as e:  # type: ignore[misc]
                if self.disp:
                    self.disp.log_error(
                        f"Error while closing connection pool: {e}"
                    )
            else:
                if hasattr(self, "disp") and self.disp and status != self.success:
                    self.disp.log_error(
                        "Destroying the connection pool returned an error status."
                    )
        # Clean up all references
        self.sql_manage_connections = None
        self._sql_query_boilerplate = None
        self.sql_cache_orchestrator = None
        self.sql_time_manipulation = None
