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
# FILE: sql_redis_cache_rebinds.py
# CREATION DATE: 18-11-2025
# LAST Modified: 3:52:21 25-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: This is the redis cache handler for the sql library using the underlying redis wrapper.
# // AR
# +==== END AsperBackend =================+
"""
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, Literal, overload

from display_tty import Disp, initialise_logger

from redis import Redis

from ..redis import RedisCaching, RedisArgs


class SQLRedisCacheRebinds(RedisCaching):
    """Redis cache rebind layer for the SQL library.

    Thin subclass of ``RedisCaching`` that adds structured debug logging and a
    convenience initializer for binding Redis caching to SQL fetcher/writer
    callables. It does not alter caching semantics; all logic for key
    construction, serialization, TTL handling, and invalidation lives in the
    base class. This class simply centralizes instrumentation (``log_debug``)
    and provides a clearer integration point for the SQL manager without
    changing its source. No artificial line wrapping is used; paragraphs are
    kept intact for readability.
    """

    disp_inner: Disp = initialise_logger(__qualname__, False)

    def __new__(cls, *args, existing_instance: Optional["RedisCaching"] = None, **kwargs):
        # If a base RedisCaching instance is passed, create a subclass instance
        # and transparently adopt its state so the child behaves as if
        # super().__init__ had populated inherited fields.
        if isinstance(existing_instance, RedisCaching) and not isinstance(existing_instance, SQLRedisCacheRebinds):
            obj = super().__new__(cls)
            # Shallow copy instance dictionary to preserve inherited state
            # type: ignore[attr-defined]
            obj.__dict__ = existing_instance.__dict__.copy()
            # Marker to let __init__ know we've already adopted base state
            obj._adopted_from_base = True  # type: ignore[attr-defined]
            return obj
        return super().__new__(cls)

    def __init__(self, client: Optional[Union[Redis, RedisArgs]] = None, debug: bool = False, *, namespace: str = "sql", db_label: Optional[str] = None, default_ttls: Optional[Dict[str, int]] = None, existing_instance: Optional["RedisCaching"] = None,) -> None:
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        if getattr(self, "_adopted_from_base", False):
            # Already adopted base state in __new__; do not re-run parent init.
            # Clean up marker to avoid leaking it.
            if hasattr(self, "_adopted_from_base"):
                delattr(self, "_adopted_from_base")
        else:
            super().__init__(
                client,
                debug,
                namespace=namespace,
                db_label=db_label,
                default_ttls=default_ttls,
                existing_instance=existing_instance if isinstance(
                    existing_instance, SQLRedisCacheRebinds) else None,
            )
        self.disp_inner.log_debug(
            f"Initialized SQLRedisCacheRebinds namespace='{self.namespace}', db_label='{self.db_label}'"
        )
        self.disp.log_debug("Initialised")

    # ------------------------------------------------------------------
    # Read-through cache wrappers (to be linked with SQL manager calls)
    # ------------------------------------------------------------------

    def get_database_version(
        self,
        *,
        fetcher: Callable[[], Optional[Tuple[int, int, int]]],
        ttl_seconds: Optional[int] = None,
    ) -> Optional[Tuple[int, int, int]]:
        """Get and cache the database semantic version.

        Args:
            fetcher (Callable[[], Optional[Tuple[int,int,int]]]): Function that returns the database version as a 3-tuple or ``None``.
            ttl_seconds (int | None): Optional TTL override in seconds.

        Returns:
            tuple[int,int,int] | None: Version tuple or ``None``.
        """
        key = self._key("meta", "db_version")
        self.disp_inner.log_debug(f"Get database version using key='{key}'")
        cached = self._get_cached(key)
        if cached is not None:
            self.disp_inner.log_debug("Cache hit for database version")
            if isinstance(cached, (list, tuple)) and len(cached) == 3:
                try:
                    major, minor, patch = (
                        int(cached[0]), int(cached[1]), int(cached[2]))
                    return (major, minor, patch)
                except (ValueError, TypeError):
                    return tuple(cached)  # type: ignore[return-value]
            return None
        self.disp_inner.log_debug(
            "Cache miss for database version; invoking fetcher")
        value = fetcher()
        if ttl_seconds is None:
            ttl_to_use = self.default_ttls["version"]
        else:
            ttl_to_use = int(ttl_seconds)
        self.disp_inner.log_debug(
            f"Caching database version with ttl={ttl_to_use}s")
        self._set_cached(key, value, ttl_to_use)
        return value

    def get_table_names(
        self,
        *,
        fetcher: Callable[[], Union[int, List[str]]],
        ttl_seconds: Optional[int] = None,
        error_token: Optional[int] = None,
    ) -> Union[int, List[str]]:
        """Get and cache the list of non-internal table names.

        Args:
            fetcher (Callable[[], int | list[str]]): Function fetching table names or an error token.
            ttl_seconds (int | None): Optional TTL override.
            error_token (int | None): Error sentinel; result equal to this is not cached.

        Returns:
            int | list[str]: Error token or list of table names.
        """
        key = self._key("schema", "table_names")
        self.disp_inner.log_debug(f"Get table names using key='{key}'")
        cached = self._get_cached(key)
        if cached is not None:
            self.disp_inner.log_debug("Cache hit for table names")
            return cached
        self.disp_inner.log_debug(
            "Cache miss for table names; invoking fetcher")
        value = fetcher()
        if self._should_cache_union_result(value, error_token):
            if ttl_seconds is None:
                ttl_to_use = self.default_ttls["schema"]
            else:
                ttl_to_use = int(ttl_seconds)
            self.disp_inner.log_debug(
                f"Caching table names with ttl={ttl_to_use}s")
            self._set_cached(key, value, ttl_to_use)
        return value

    def get_table_column_names(
        self,
        table_name: str,
        *,
        fetcher: Callable[[str], Union[List[str], int]],
        ttl_seconds: Optional[int] = None,
        error_token: Optional[int] = None,
    ) -> Union[List[str], int]:
        """Get and cache the list of column names for a table.

        Args:
            table_name (str): Target table name.
            fetcher (Callable[[str], list[str] | int]): Function returning columns or error token.
            ttl_seconds (int | None): Optional TTL override.
            error_token (int | None): Error sentinel; result equal to this is not cached.

        Returns:
            list[str] | int: Column names or error token.
        """
        key = self._key("schema", f"columns:{table_name}")
        self.disp_inner.log_debug(
            f"Get column names for table='{table_name}' using key='{key}'")
        cached = self._get_cached(key)
        if cached is not None:
            self.disp_inner.log_debug("Cache hit for table columns")
            return cached
        self.disp_inner.log_debug(
            "Cache miss for table columns; invoking fetcher")
        value = fetcher(table_name)
        if self._should_cache_union_result(value, error_token):
            if ttl_seconds is None:
                ttl_to_use = self.default_ttls["schema"]
            else:
                ttl_to_use = int(ttl_seconds)
            self.disp_inner.log_debug(
                f"Caching columns for '{table_name}' with ttl={ttl_to_use}s")
            self._set_cached(key, value, ttl_to_use)
        return value

    def describe_table(
        self,
        table: str,
        *,
        fetcher: Callable[[str], Union[int, List[Any]]],
        ttl_seconds: Optional[int] = None,
        error_token: Optional[int] = None,
    ) -> Union[int, List[Any]]:
        """Get and cache a table schema description.

        Args:
            table (str): Table name.
            fetcher (Callable[[str], int | list[Any]]): Function returning description rows or error token.
            ttl_seconds (int | None): Optional TTL override.
            error_token (int | None): Error sentinel; result equal to this is not cached.

        Returns:
            int | list[Any]: Error token or description rows.
        """
        key = self._key("schema", f"describe:{table}")
        self.disp_inner.log_debug(
            f"Describe table='{table}' using key='{key}'")
        cached = self._get_cached(key)
        if cached is not None:
            self.disp_inner.log_debug("Cache hit for table description")
            return cached
        self.disp_inner.log_debug(
            "Cache miss for table description; invoking fetcher")
        value = fetcher(table)
        if self._should_cache_union_result(value, error_token):
            if ttl_seconds is None:
                ttl_to_use = self.default_ttls["schema"]
            else:
                ttl_to_use = int(ttl_seconds)
            self.disp_inner.log_debug(
                f"Caching description for '{table}' with ttl={ttl_to_use}s")
            self._set_cached(key, value, ttl_to_use)
        return value

    def get_triggers(
        self,
        *,
        fetcher: Callable[[], Union[int, Dict[str, str]]],
        ttl_seconds: Optional[int] = None,
        error_token: Optional[int] = None,
    ) -> Union[int, Dict[str, str]]:
        """Get and cache all triggers with their SQL definitions.

        Args:
            fetcher (Callable[[], int | dict[str,str]]): Function returning mapping or error token.
            ttl_seconds (int | None): Optional TTL override.
            error_token (int | None): Error sentinel; result equal to this is not cached.

        Returns:
            int | dict[str, str]: Error token or triggers mapping.
        """
        key = self._key("schema", "triggers")
        self.disp_inner.log_debug(f"Get triggers using key='{key}'")
        cached = self._get_cached(key)
        if cached is not None:
            self.disp_inner.log_debug("Cache hit for triggers")
            return cached
        self.disp_inner.log_debug("Cache miss for triggers; invoking fetcher")
        value = fetcher()
        if self._should_cache_union_result(value, error_token):
            if ttl_seconds is None:
                ttl_to_use = self.default_ttls["schema"]
            else:
                ttl_to_use = int(ttl_seconds)
            self.disp_inner.log_debug(
                f"Caching triggers with ttl={ttl_to_use}s")
            self._set_cached(key, value, ttl_to_use)
        return value

    def get_trigger(
        self,
        trigger_name: str,
        *,
        fetcher: Callable[[str], Union[int, str]],
        ttl_seconds: Optional[int] = None,
        error_token: Optional[int] = None,
    ) -> Union[int, str]:
        """Get and cache a single trigger definition.

        Args:
            trigger_name (str): Trigger identifier.
            fetcher (Callable[[str], int | str]): Function returning SQL text or error token.
            ttl_seconds (int | None): Optional TTL override.
            error_token (int | None): Error sentinel; result equal to this is not cached.

        Returns:
            int | str: Error token or trigger SQL.
        """
        key = self._key("schema", f"trigger:{trigger_name}")
        self.disp_inner.log_debug(
            f"Get trigger='{trigger_name}' using key='{key}'")
        cached = self._get_cached(key)
        if cached is not None:
            self.disp_inner.log_debug("Cache hit for trigger definition")
            return cached
        self.disp_inner.log_debug(
            "Cache miss for trigger definition; invoking fetcher")
        value = fetcher(trigger_name)
        if self._should_cache_union_result(value, error_token):
            ttl_to_use = self.default_ttls["schema"] if ttl_seconds is None else int(
                ttl_seconds)
            self.disp_inner.log_debug(
                f"Caching trigger '{trigger_name}' with ttl={ttl_to_use}s")
            self._set_cached(key, value, ttl_to_use)
        return value

    def get_trigger_names(
        self,
        *,
        fetcher: Callable[[], Union[int, List[str]]],
        ttl_seconds: Optional[int] = None,
        error_token: Optional[int] = None,
    ) -> Union[int, List[str]]:
        """Get and cache the list of trigger names.

        Args:
            fetcher (Callable[[], int | list[str]]): Function returning trigger names or error token.
            ttl_seconds (int | None): Optional TTL override.
            error_token (int | None): Error sentinel; result equal to this is not cached.

        Returns:
            int | list[str]: Error token or trigger names.
        """
        key = self._key("schema", "trigger_names")
        self.disp_inner.log_debug(f"Get trigger names using key='{key}'")
        cached = self._get_cached(key)
        if cached is not None:
            self.disp_inner.log_debug("Cache hit for trigger names")
            return cached
        self.disp_inner.log_debug(
            "Cache miss for trigger names; invoking fetcher")
        value = fetcher()
        if self._should_cache_union_result(value, error_token):
            if ttl_seconds is None:
                ttl_to_use = self.default_ttls["schema"]
            else:
                ttl_to_use = int(ttl_seconds)
            self.disp_inner.log_debug(
                f"Caching trigger names with ttl={ttl_to_use}s")
            self._set_cached(key, value, ttl_to_use)
        return value

    def get_table_size(
        self,
        table: str,
        column: Union[str, List[str]],
        where: Union[str, List[str]] = "",
        *,
        fetcher: Callable[[str, Union[str, List[str]], Union[str, List[str]]], int],
        ttl_seconds: Optional[int] = None,
    ) -> int:
        """Get and cache the number of rows matching an optional filter.

        Args:
            table (str): Table name.
            column (str | list[str]): Column to count over (usually ``"*"``).
            where (str | list[str]): Optional WHERE clause or conditions.
            fetcher (Callable[[str, str | list[str], str | list[str]], int]): Function returning the count.
            ttl_seconds (int | None): Optional TTL override.

        Returns:
            int: Row count.
        """
        params = {
            "table": table,
            "column": self._normalize_selector(column),
            "where": self._normalize_selector(where),
        }
        key = self._key("count", table, params)
        self.disp_inner.log_debug(
            f"Get table size for table='{table}' using key='{key}'"
        )
        cached = self._get_cached(key)
        if cached is not None:
            # Count is an int; cached JSON restores it directly
            self.disp_inner.log_debug("Cache hit for table size")
            return int(cached)
        self.disp_inner.log_debug(
            "Cache miss for table size; invoking fetcher")
        value = int(fetcher(table, column, where))
        if ttl_seconds is None:
            ttl_to_use = self.default_ttls["count"]
        else:
            ttl_to_use = int(ttl_seconds)
        self.disp_inner.log_debug(f"Caching table size with ttl={ttl_to_use}s")
        self._set_cached(key, value, ttl_to_use)
        return value

    @overload
    def get_data_from_table(
        self,
        table: str,
        column: Union[str, List[str]],
        where: Union[str, List[str]] = "",
        *,
        beautify: Literal[True] = True,
        fetcher: Callable[[], Union[int, List[Dict[str, Any]]]],
        ttl_seconds: Optional[int] = None,
        error_token: Optional[int] = None,
    ) -> Union[int, List[Dict[str, Any]]]:
        ...

    @overload
    def get_data_from_table(
        self,
        table: str,
        column: Union[str, List[str]],
        where: Union[str, List[str]] = "",
        *,
        beautify: Literal[False],
        fetcher: Callable[[], Union[int, List[Tuple[Any, ...]]]],
        ttl_seconds: Optional[int] = None,
        error_token: Optional[int] = None,
    ) -> Union[int, List[Tuple[Any, ...]]]:
        ...

    def get_data_from_table(
        self,
        table: str,
        column: Union[str, List[str]],
        where: Union[str, List[str]] = "",
        *,
        beautify: bool = True,
        fetcher: Callable[[], Union[int, List[Dict[str, Any]], List[Tuple[Any, ...]]]],
        ttl_seconds: Optional[int] = None,
        error_token: Optional[int] = None,
    ) -> Union[int, Union[List[Dict[str, Any]], List[Tuple[Any, ...]]]]:
        """Get and cache rows from a table.

        When ``beautify`` is True the fetcher must return a list of dictionaries. When False it must return a list of tuples (or a list of lists convertible to tuples). On error the fetcher may return an integer error token.

        Args:
            table (str): Table name.
            column (str | list[str]): Column name(s) or ``"*"``.
            where (str | list[str]): Optional WHERE clause or conditions.
            beautify (bool): Whether rows are dictionary-shaped.
            fetcher (Callable[[], int | list[dict[str, Any]] | list[tuple[Any,...]]]): Function that executes the actual SQL call.
            ttl_seconds (int | None): Optional TTL override.
            error_token (int | None): Error sentinel; result equal to this is not cached.

        Returns:
            int | list[dict[str, Any]] | list[tuple[Any, ...]]: Error token or rows.
        """
        params = {
            "table": table,
            "column": self._normalize_selector(column),
            "where": self._normalize_selector(where),
            "beautify": bool(beautify),
        }
        key = self._key("data", table, params)
        self.disp_inner.log_debug(
            f"Get data from table='{table}', beautify={bool(beautify)} using key='{key}'"
        )
        cached = self._get_cached(key)
        if cached is not None:
            self.disp_inner.log_debug("Cache hit for table data")
            if beautify:
                return cached
            # Convert inner lists to tuples for non-beautified rows
            if isinstance(cached, list) and (not cached or isinstance(cached[0], list)):
                rows: List[Tuple[Any, ...]] = []
                for row in cached:
                    rows.append(tuple(row))
                self.disp_inner.log_debug(
                    "Converted cached rows to tuples for non-beautified result")
                return rows  # type: ignore[return-value]
            return cached
        self.disp_inner.log_debug(
            "Cache miss for table data; invoking fetcher")
        value = fetcher()
        if self._should_cache_union_result(value, error_token):
            if ttl_seconds is None:
                ttl_to_use = self.default_ttls["data"]
            else:
                ttl_to_use = int(ttl_seconds)
            self.disp_inner.log_debug(
                f"Caching table data with ttl={ttl_to_use}s")
            self._set_cached(key, value, ttl_to_use)
        return value

    # ------------------------------------------------------------------
    # Write wrappers (invalidate appropriate caches on success)
    # ------------------------------------------------------------------
    def create_table(
        self,
        table: str,
        columns: List[Tuple[str, str]],
        *,
        writer: Callable[[str, List[Tuple[str, str]]], int],
    ) -> int:
        """Create a table and invalidate related cache entries on success.

        Args:
            table (str): New table name.
            columns (list[tuple[str,str]]): Column definitions.
            writer (Callable[[str, list[tuple[str,str]]], int]): Function performing the SQL execution.

        Returns:
            int: Writer return code.
        """
        result = writer(table, columns)
        self.disp_inner.log_debug(
            f"Writer executed for create_table, result={result}")
        if isinstance(result, int) and result == 0:
            self.disp_inner.log_debug(
                "Invalidating caches after create_table success")
            # Invalidate table list and specific table schema
            self._invalidate_patterns([
                f"{self.namespace}:{self.db_label}:schema:table_names",
                f"{self.namespace}:{self.db_label}:schema:columns:{table}:*",
                f"{self.namespace}:{self.db_label}:schema:describe:{table}:*",
            ])
        return result

    def insert_trigger(
        self,
        trigger_name: str,
        table_name: str,
        timing_event: str,
        body: str,
        *,
        writer: Callable[[str, str, str, str], int],
    ) -> int:
        """Insert a trigger and invalidate trigger caches on success.

        Args:
            trigger_name (str): Trigger name.
            table_name (str): Related table name.
            timing_event (str): Trigger timing/event (e.g., ``BEFORE INSERT``).
            body (str): SQL body.
            writer (Callable[[str,str,str,str], int]): Function performing the SQL execution.

        Returns:
            int: Writer return code.
        """
        result = writer(trigger_name, table_name, timing_event, body)
        self.disp_inner.log_debug(
            f"Writer executed for insert_trigger '{trigger_name}', result={result}")
        if isinstance(result, int) and result == 0:
            self.disp_inner.log_debug(
                "Invalidating caches after insert_trigger success")
            self.invalidate_trigger(trigger_name)
            self._invalidate_patterns([
                f"{self.namespace}:{self.db_label}:schema:triggers",
                f"{self.namespace}:{self.db_label}:schema:trigger_names",
            ])
        return result

    # create_trigger is an alias to insert_trigger to preserve API consistency
    def create_trigger(
        self,
        trigger_name: str,
        table_name: str,
        timing_event: str,
        body: str,
        *,
        writer: Callable[[str, str, str, str], int],
    ) -> int:
        """Alias to :py:meth:`insert_trigger`.

        Args:
            trigger_name (str): Trigger name.
            table_name (str): Related table name.
            timing_event (str): Trigger timing/event.
            body (str): SQL body.
            writer (Callable[[str,str,str,str], int]): SQL executor.

        Returns:
            int: Writer return code.
        """
        return self.insert_trigger(trigger_name, table_name, timing_event, body, writer=writer)

    def insert_data_into_table(
        self,
        table: str,
        data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]],
        column: Optional[List[str]] = None,
        *,
        writer: Callable[[str, Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], Optional[List[str]]], int],
    ) -> int:
        """Insert row(s) into a table and invalidate related caches.

        Args:
            table (str): Target table.
            data (list[list[str|None|int|float]] | list[str|None|int|float]): Row or rows.
            column (list[str] | None): Optional column list.
            writer (Callable[..., int]): Function performing the SQL execution.

        Returns:
            int: Writer return code.
        """
        result = writer(table, data, column)
        self.disp_inner.log_debug(
            f"Writer executed for insert_data_into_table on '{table}', result={result}")
        if isinstance(result, int) and result == 0:
            self.disp_inner.log_debug(
                "Invalidating table caches after insert_data_into_table success")
            self.invalidate_table(table)
        return result

    def update_data_in_table(
        self,
        table: str,
        data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]],
        column: List[str],
        where: Union[str, List[str]] = "",
        *,
        writer: Callable[[str, Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], List[str], Union[str, List[str]]], int],
    ) -> int:
        """Update row(s) in a table and invalidate related caches.

        Args:
            table (str): Target table.
            data (list[list[str|None|int|float]] | list[str|None|int|float]): New values.
            column (list[str]): Column names corresponding to ``data``.
            where (str | list[str]): WHERE clause/conditions.
            writer (Callable[..., int]): Function performing the SQL execution.

        Returns:
            int: Writer return code.
        """
        result = writer(table, data, column, where)
        self.disp_inner.log_debug(
            f"Writer executed for update_data_in_table on '{table}', result={result}")
        if isinstance(result, int) and result == 0:
            self.disp_inner.log_debug(
                "Invalidating table caches after update_data_in_table success")
            self.invalidate_table(table)
        return result

    def insert_or_update_data_into_table(
        self,
        table: str,
        data: Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]],
        columns: Optional[List[str]] = None,
        *,
        writer: Callable[[str, Union[List[List[Union[str, None, int, float]]], List[Union[str, None, int, float]]], Optional[List[str]]], int],
    ) -> int:
        """Insert or update row(s) and invalidate related caches.

        Args:
            table (str): Target table.
            data (list[list[str|None|int|float]] | list[str|None|int|float]): Rows.
            columns (list[str] | None): Optional columns.
            writer (Callable[..., int]): Function performing the SQL execution.

        Returns:
            int: Writer return code.
        """
        result = writer(table, data, columns)
        self.disp_inner.log_debug(
            f"Writer executed for insert_or_update_data_into_table on '{table}', result={result}")
        if isinstance(result, int) and result == 0:
            self.disp_inner.log_debug(
                "Invalidating table caches after insert_or_update_data_into_table success")
            self.invalidate_table(table)
        return result

    def insert_or_update_trigger(
        self,
        trigger_name: str,
        table_name: str,
        timing_event: str,
        body: str,
        *,
        writer: Callable[[str, str, str, str], int],
    ) -> int:
        """Insert or update a trigger and invalidate related caches.

        Args:
            trigger_name (str): Trigger name.
            table_name (str): Related table name.
            timing_event (str): Trigger timing/event.
            body (str): SQL body.
            writer (Callable[[str,str,str,str], int]): SQL executor.

        Returns:
            int: Writer return code.
        """
        result = writer(trigger_name, table_name, timing_event, body)
        self.disp_inner.log_debug(
            f"Writer executed for insert_or_update_trigger '{trigger_name}', result={result}")
        if isinstance(result, int) and result == 0:
            self.disp_inner.log_debug(
                "Invalidating caches after insert_or_update_trigger success")
            self.invalidate_trigger(trigger_name)
            self._invalidate_patterns([
                f"{self.namespace}:{self.db_label}:schema:triggers",
                f"{self.namespace}:{self.db_label}:schema:trigger_names",
            ])
        return result

    def remove_data_from_table(
        self,
        table: str,
        where: Union[str, List[str]] = "",
        *,
        writer: Callable[[str, Union[str, List[str]]], int],
    ) -> int:
        """Delete row(s) from a table and invalidate related caches.

        Args:
            table (str): Target table.
            where (str | list[str]): WHERE clause/conditions.
            writer (Callable[[str, str | list[str]], int]): SQL executor.

        Returns:
            int: Writer return code.
        """
        result = writer(table, where)
        self.disp_inner.log_debug(
            f"Writer executed for remove_data_from_table on '{table}', result={result}")
        if isinstance(result, int) and result == 0:
            self.disp_inner.log_debug(
                "Invalidating table caches after remove_data_from_table success")
            self.invalidate_table(table)
        return result

    # drop_data_from_table preserved as alias to remove_data_from_table
    def drop_data_from_table(
        self,
        table: str,
        *,
        writer: Callable[[str], int],
    ) -> int:
        """Alias to :py:meth:`remove_data_from_table` without a WHERE clause."""
        result = writer(table)
        self.disp_inner.log_debug(
            f"Writer executed for drop_data_from_table on '{table}', result={result}")
        if isinstance(result, int) and result == 0:
            self.disp_inner.log_debug(
                "Invalidating table caches after drop_data_from_table success")
            self.invalidate_table(table)
        return result

    def remove_table(
        self,
        table: str,
        *,
        writer: Callable[[str], int],
    ) -> int:
        """Drop a table and invalidate related caches.

        Args:
            table (str): Table name.
            writer (Callable[[str], int]): SQL executor.

        Returns:
            int: Writer return code.
        """
        result = writer(table)
        self.disp_inner.log_debug(
            f"Writer executed for remove_table '{table}', result={result}")
        if isinstance(result, int) and result == 0:
            self.disp_inner.log_debug(
                "Invalidating caches after remove_table success")
            self.invalidate_table(table)
            # Also refresh table_names
            self._invalidate_patterns(
                [f"{self.namespace}:{self.db_label}:schema:table_names"])
        return result

    # drop_table preserved as alias to remove_table
    def drop_table(
        self,
        table: str,
        *,
        writer: Callable[[str], int],
    ) -> int:
        """Alias to :py:meth:`remove_table`."""
        return self.remove_table(table, writer=writer)

    def remove_trigger(
        self,
        trigger_name: str,
        *,
        writer: Callable[[str], int],
    ) -> int:
        """Drop a trigger and invalidate related caches.

        Args:
            trigger_name (str): Trigger identifier.
            writer (Callable[[str], int]): SQL executor.

        Returns:
            int: Writer return code.
        """
        result = writer(trigger_name)
        self.disp_inner.log_debug(
            f"Writer executed for remove_trigger '{trigger_name}', result={result}")
        if isinstance(result, int) and result == 0:
            self.disp_inner.log_debug(
                "Invalidating caches after remove_trigger success")
            self.invalidate_trigger(trigger_name)
            self._invalidate_patterns([
                f"{self.namespace}:{self.db_label}:schema:triggers",
                f"{self.namespace}:{self.db_label}:schema:trigger_names",
            ])
        return result

    # drop_trigger preserved as alias to remove_trigger
    def drop_trigger(
        self,
        trigger_name: str,
        *,
        writer: Callable[[str], int],
    ) -> int:
        """Alias to :py:meth:`remove_trigger`."""
        return self.remove_trigger(trigger_name, writer=writer)
