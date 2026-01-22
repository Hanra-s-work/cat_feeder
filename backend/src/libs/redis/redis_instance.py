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
# FILE: redis_instance.py
# CREATION DATE: 11-10-2025
# LAST Modified: 14:51:35 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file in charge of handling the redis connection as well as cache.
# // AR
# +==== END CatFeeder =================+
"""

import os
import json
import hashlib
from typing import Any, Callable, Dict, List, Optional, Union, cast
from platform import system

import redis

from display_tty import Disp, initialise_logger

from .redis_args import RedisArgs
from . import redis_constants as CONST


def _build_redis_client() -> redis.Redis:
    """Create and return a configured Redis client.

    This function does not connect immediately; the client will establish
    a connection upon first command execution.

    Returns:
        redis.Redis: Configured Redis client instance.
    """
    socket_path = os.getenv(CONST.REDIS_SOCKET_KEY, CONST.REDIS_SOCKET_DEFAULT)
    password = os.getenv(CONST.REDIS_PASSWORD_KEY)
    if system().lower() != "Windows":
        unix_socket_path = socket_path
    else:
        unix_socket_path = None
    node: redis.Redis = redis.Redis(
        unix_socket_path=unix_socket_path,
        password=password,
        decode_responses=True
    )
    return node


class RedisCaching:
    """High-level Redis cache facade for SQL-related data.

    Provides read-through caching, key namespacing, and targeted invalidation for database metadata (version, schema objects), table data, and row counts. The layer is intentionally thin: actual SQL execution is delegated to caller‑supplied callables (``fetcher``/``writer``) so this class remains decoupled from any specific database driver.

    Design Highlights:
    - JSON Serialization: All cached values are stored as JSON for portability and human inspection. Tuples are normalized to lists.
    - Deterministic Keys: Keys follow the pattern ``{namespace}:{db_label}:{category}:{name}[:{param_hash}]``. The optional hash is a stable SHA‑256 prefix over normalized parameters ensuring low collision probability while keeping keys concise.
    - Lazy Client: A Redis client is created only on first access allowing import/use without forcing an immediate socket connection.
    - Safe Invalidation: Category/table/trigger specific invalidation methods use ``SCAN`` + ``DELETE`` rather than broad ``FLUSHDB`` calls.
    - Error Sentinel Respect: Methods can be given an ``error_token`` so failed results are not cached (preventing sticky error states).

    Typical Read Usage:
        cache = RedisCaching()
        rows = cache.get_data_from_table(
            table="users",
            column=["id", "name"],
            where=["active=1"],
            beautify=True,
            fetcher=lambda: sql.get_data_from_table("users", ["id", "name"], ["active=1"], True),
            ttl_seconds=cache.default_ttls["data"],
            error_token=84,
        )

    Typical Write Usage:
        result = cache.update_data_in_table(
            table="users",
            data=["42", "new_name"],
            column=["id", "name"],
            where="id = 42",
            writer=lambda t, d, c, w: sql.update_data_in_table(t, d, c, w)
        )  # On success, relevant keys are invalidated automatically.

    Attributes:
        namespace (str): Top‑level logical partition for all keys (default ``"sql"``).
        db_label (str): Database label inserted into every key for multi‑DB isolation.
        default_ttls (dict[str,int]): Per category TTL defaults (``version``, ``schema``, ``data``, ``count``).
        client (redis.Redis | RedisArgs | None): Underlying Redis client or lazy args container.
        disp (Disp): Logger used for debug and diagnostic messages.
    """
    existing_instance: Optional["RedisCaching"] = None
    disp: Disp = initialise_logger(__qualname__, False)

    def __new__(cls, *args, existing_instance: Optional["RedisCaching"] = None, **kwargs):
        """Return a new or previously existing instance.

        If ``existing_instance`` is provided and is an instance of ``cls`` (the
        exact class being constructed, potentially a subclass), it is returned
        as-is and ``__init__`` will not run again. Otherwise, a fresh instance
        of ``cls`` is allocated normally.

        Args:
            existing_instance (RedisCaching | None): An existing instance to reuse.

        Returns:
            RedisCaching: Either the supplied ``existing_instance`` or a freshly allocated object.
        """
        if existing_instance is not None and isinstance(existing_instance, cls):
            return existing_instance
        return super().__new__(cls)

    def __init__(
        self,
        client: Optional[Union[redis.Redis, RedisArgs]] = None,
        debug: bool = False,
        *,
        namespace: str = "sql",
        db_label: Optional[str] = None,
        default_ttls: Optional[Dict[str, int]] = None,
        existing_instance: Optional["RedisCaching"] = None,
    ) -> None:
        """Initialize the Redis caching layer.

        Args:
            client (redis.Redis | None): Optional Redis client. When omitted, a client is built from environment variables.
            namespace (str): Top-level namespace used to prefix keys.
            db_label (str | None): Optional database label to isolate keys per DB. Defaults to the ``DB_NAME`` environment variable or ``"default"``.
            default_ttls (dict[str, int] | None): Optional TTLs in seconds per category (``version``, ``schema``, ``data``, ``count``).
            existing_instance (RedisCaching | None): When provided, indicates this __init__ call is for a reused instance and initialization should be skipped.
        """
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        # Only initialize if this is NOT a reused instance
        if existing_instance is not None:
            return
        # Redis client (constructed lazily if not provided)
        self._client_factory: Callable[[], redis.Redis] = _build_redis_client
        if client is not None:
            self.client: Optional[Union[redis.Redis, RedisArgs]] = client
        else:
            self.client = None

        # Namespace and DB label (used to isolate keys per application/database)
        ns_candidate = namespace.strip()
        if ns_candidate:
            self.namespace: str = ns_candidate
        else:
            self.namespace = "sql"

        label_candidate: Optional[str]
        if db_label is not None and db_label.strip():
            label_candidate = db_label
        else:
            env_label = os.getenv("DB_NAME")
            if env_label is not None and env_label.strip():
                label_candidate = env_label
            else:
                label_candidate = "default"
        self.db_label = label_candidate.strip()

        # Default per-category TTLs (seconds)
        self.default_ttls: Dict[str, int] = {
            "version": CONST.HOUR_24,  # 24h
            "schema": CONST.HOUR_1,    # 1h
            "data": CONST.MIN_2,       # 2min
            "count": CONST.MIN_1,      # 1min
        }
        if default_ttls:
            for k, v in default_ttls.items():
                if v is not None:
                    self.default_ttls[k] = int(v)

        # Summarize initialization
        client_kind: str = "None"
        if self.client is None:
            client_kind = "None"
        if isinstance(self.client, RedisArgs):
            client_kind = "RedisArgs"
        else:
            client_kind = "Redis"
        self.disp.log_debug(
            f"Initialized RedisCaching namespace='{self.namespace}', db_label='{self.db_label}', client={client_kind}"
        )
        self.disp.log_debug("Initialised")

    # ------------------------------------------------------------------
    # Generic helpers
    # ------------------------------------------------------------------
    def _stable_dump(self, obj: Any) -> str:
        """Return a stable JSON string for ``obj`` used in key hashing.

        Tuples are converted to lists for JSON compatibility; sets are
        converted to sorted lists. Dicts are sorted by key.

        Args:
            obj (Any): Any JSON-serializable Python object.

        Returns:
            str: A deterministically ordered JSON string.
        """
        def normalize(x: Any) -> Any:
            if isinstance(x, tuple):
                out_list: List[Any] = []
                for v in x:
                    out_list.append(normalize(v))
                return out_list
            if isinstance(x, set):
                tmp: List[Any] = []
                for v in x:
                    tmp.append(normalize(v))
                tmp.sort(key=lambda i: json.dumps(
                    i, sort_keys=True, ensure_ascii=False))
                return tmp
            if isinstance(x, list):
                out_list2: List[Any] = []
                for v in x:
                    out_list2.append(normalize(v))
                return out_list2
            if isinstance(x, dict):
                out_dict: Dict[str, Any] = {}
                for k in sorted(x.keys()):
                    out_dict[k] = normalize(x[k])
                return out_dict
            return x

        return json.dumps(normalize(obj), separators=(",", ":"), ensure_ascii=False)

    def _hash_params(self, params: Any) -> str:
        """Hash arbitrary parameters deterministically for compact keys.

        Args:
            params (Any): Parameters to be represented in the cache key.

        Returns:
            str: A short SHA-256 hex digest prefix.
        """
        dumped = self._stable_dump(params)
        digest = hashlib.sha256(dumped.encode("utf-8")).hexdigest()[:20]
        self.disp.log_debug(f"Computed params hash='{digest}'")
        return digest

    def _key(self, category: str, name: str, params: Optional[Any] = None) -> str:
        """Build a namespaced Redis key.

        Key format: ``{namespace}:{db_label}:{category}:{name}[:{hash}]``

        Args:
            category (str): Logical grouping (e.g., ``schema``, ``data``).
            name (str): Base key name within the category.
            params (Any | None): Optional parameters to hash for uniqueness.

        Returns:
            str: Fully-qualified Redis key.
        """
        base = f"{self.namespace}:{self.db_label}:{category}:{name}"
        if params is None:
            self.disp.log_debug(f"Key generated='{base}' (no params)")
            return base
        key = f"{base}:{self._hash_params(params)}"
        self.disp.log_debug(f"Key generated='{key}' (with params)")
        return key

    def _serialize(self, value: Any) -> str:
        """Serialize a Python value to a JSON string.

        Tuples are converted to lists; on read we may convert back where needed.

        Args:
            value (Any): Value to serialize.

        Returns:
            str: JSON string representation.
        """
        def normalize(x: Any) -> Any:
            if isinstance(x, tuple):
                out_list: List[Any] = []
                for v in x:
                    out_list.append(normalize(v))
                return out_list
            if isinstance(x, list):
                out_list2: List[Any] = []
                for v in x:
                    out_list2.append(normalize(v))
                return out_list2
            if isinstance(x, dict):
                out_dict: Dict[str, Any] = {}
                for k, v in x.items():
                    out_dict[k] = normalize(v)
                return out_dict
            return x

        payload = json.dumps(normalize(value), ensure_ascii=False)
        self.disp.log_debug(f"Serialized payload length={len(payload)}")
        return payload

    def _deserialize(self, raw: Optional[str]) -> Any:
        """Deserialize a JSON string back to Python.

        Args:
            raw (str | None): Raw JSON string from Redis or ``None``.

        Returns:
            Any: Deserialized Python value, or ``None`` if input is ``None``.
        """
        if raw is None:
            self.disp.log_debug(
                "Deserialize called with raw=None (cache miss)")
            return None
        try:
            value = json.loads(raw)
            self.disp.log_debug("Deserialized payload successfully")
            return value
        except json.JSONDecodeError as e:
            self.disp.log_warning(
                f"Failed to deserialize payload: {e}"
            )
            raise

    def _get_cached(self, key: str) -> Any:
        """Get and deserialize a cached value for ``key``.

        Args:
            key (str): Redis key to fetch.

        Returns:
            Any: Deserialized cached value, or ``None`` if not present.
        """
        self.disp.log_debug(f"GET key='{key}'")
        raw = cast(Optional[str], self._ensure_client().get(key))
        val = self._deserialize(raw)
        if val is None:
            self.disp.log_debug("Cache miss")
        else:
            self.disp.log_debug("Cache hit")
        return val

    def _set_cached(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Serialize and set a value under ``key`` with TTL.

        Uses ``SETEX`` when ``ttl_seconds > 0``; otherwise uses ``SET``.

        Args:
            key (str): Redis key.
            value (Any): Python value to serialize and store.
            ttl_seconds (int): Time to live in seconds; 0 or negative disables TTL.
        """
        payload = self._serialize(value)
        if ttl_seconds > 0:
            self.disp.log_debug(f"SETEX key='{key}', ttl={ttl_seconds}s")
            self._ensure_client().setex(key, ttl_seconds, payload)
        else:
            self.disp.log_debug(f"SET key='{key}' (no ttl)")
            self._ensure_client().set(key, payload)

    def _should_cache_union_result(self, result: Any, error_token: Optional[int]) -> bool:
        """Decide whether to cache a union-typed result.

        When ``error_token`` is provided, skip caching if result equals it.
        Otherwise, cache the value (including ints such as row counts).

        Args:
            result (Any): Value returned by the fetcher.
            error_token (int | None): Error sentinel value to avoid caching.

        Returns:
            bool: ``True`` if the value should be cached, else ``False``.
        """
        if error_token is None:
            self.disp.log_debug("No error_token provided; will cache result")
            return True
        decision = result != error_token
        self.disp.log_debug(
            f"Error token present; will_cache={decision} (result == error_token? {not decision})"
        )
        return decision

    def _invalidate_patterns(self, patterns: List[str]) -> None:
        """Delete all keys matching the provided patterns.

        Args:
            patterns (list[str]): List of glob-style patterns for ``SCAN``.
        """
        for p in patterns:
            deleted = 0
            self.disp.log_debug(f"Invalidating keys with pattern='{p}'")
            for key in self._ensure_client().scan_iter(p):
                self._ensure_client().delete(key)
                deleted += 1
            self.disp.log_debug(
                f"Invalidation pattern='{p}' deleted={deleted} keys")

    def _ensure_client(self) -> redis.Redis:
        """Return a Redis client, constructing it on first use.

        Returns:
            redis.Redis: Active Redis client instance.
        """
        if self.client is None:
            self.disp.log_debug("Constructing Redis client via factory")
            self.client = self._client_factory()
        elif isinstance(self.client, RedisArgs):
            self.disp.log_debug(
                "Building Redis client from RedisArgs configuration")
            tmp = redis.Redis(
                host=self.client.host,
                port=self.client.port,
                db=self.client.db,
                password=self.client.password,
                socket_timeout=self.client.socket_timeout,
                socket_connect_timeout=self.client.socket_connect_timeout,
                socket_keepalive=self.client.socket_keepalive,
                socket_keepalive_options=self.client.socket_keepalive_options,
                connection_pool=self.client.connection_pool,
                unix_socket_path=self.client.unix_socket_path,
                encoding=self.client.encoding,
                encoding_errors=self.client.encoding_errors,
                decode_responses=self.client.decode_responses,
                retry_on_timeout=self.client.retry_on_timeout,
                retry=self.client.retry,
                retry_on_error=self.client.retry_on_error,
                ssl=self.client.ssl,
                ssl_keyfile=self.client.ssl_keyfile,
                ssl_certfile=self.client.ssl_certfile,
                ssl_cert_reqs=self.client.ssl_cert_reqs,
                ssl_include_verify_flags=self.client.ssl_include_verify_flags,
                ssl_exclude_verify_flags=self.client.ssl_exclude_verify_flags,
                ssl_ca_certs=self.client.ssl_ca_certs,
                ssl_ca_path=self.client.ssl_ca_path,
                ssl_ca_data=self.client.ssl_ca_data,
                ssl_check_hostname=self.client.ssl_check_hostname,
                ssl_password=self.client.ssl_password,
                ssl_validate_ocsp=self.client.ssl_validate_ocsp,
                ssl_validate_ocsp_stapled=self.client.ssl_validate_ocsp_stapled,
                ssl_ocsp_context=self.client.ssl_ocsp_context,
                ssl_ocsp_expected_cert=self.client.ssl_ocsp_expected_cert,
                ssl_min_version=self.client.ssl_min_version,
                ssl_ciphers=self.client.ssl_ciphers,
                max_connections=self.client.max_connections,
                single_connection_client=self.client.single_connection_client,
                health_check_interval=self.client.health_check_interval,
                client_name=self.client.client_name,
                lib_name=self.client.lib_name,
                lib_version=self.client.lib_version,
                username=self.client.username,
                redis_connect_func=self.client.redis_connect_func,
                credential_provider=self.client.credential_provider,
                protocol=self.client.protocol,
                cache=self.client.cache,
                cache_config=self.client.cache_config,
                event_dispatcher=self.client.event_dispatcher,
                maint_notifications_config=self.client.maint_notifications_config
            )
            self.client = tmp
        else:
            self.disp.log_debug("Using provided Redis client instance")
        return self.client

    def _normalize_selector(self, selector: Union[str, List[str]]) -> Any:
        """Return selector as-is, normalizing list vs string types.

        Args:
            selector (str | list[str]): Column list or ``"*"``.

        Returns:
            Any: The selector unchanged, used for hashing and display.
        """
        if isinstance(selector, list):
            self.disp.log_debug("Normalizing selector: list")
            return selector
        self.disp.log_debug("Normalizing selector: str")
        return selector

    # ------------------------------------------------------------------
    # Public invalidation helpers
    # ------------------------------------------------------------------
    def invalidate_all(self) -> None:
        """Remove all keys for the current namespace and DB label."""
        prefix = f"{self.namespace}:{self.db_label}:*"
        self.disp.log_debug("Invalidating all keys for namespace/db_label")
        self._invalidate_patterns([prefix])

    def invalidate_schema(self) -> None:
        """Remove all schema-related keys (tables, columns, triggers, descriptions)."""
        base = f"{self.namespace}:{self.db_label}:schema:*"
        self.disp.log_debug("Invalidating all schema keys")
        self._invalidate_patterns([base])

    def invalidate_table(self, table: str) -> None:
        """Remove all cache entries related to a specific table.

        Args:
            table (str): Table name.
        """
        ns = f"{self.namespace}:{self.db_label}"
        self.disp.log_debug(f"Invalidating caches for table='{table}'")
        patterns = [
            f"{ns}:data:{table}:*",
            f"{ns}:count:{table}:*",
            f"{ns}:schema:columns:{table}:*",
            f"{ns}:schema:describe:{table}:*",
        ]
        self._invalidate_patterns(patterns)

    def invalidate_trigger(self, trigger_name: Optional[str] = None) -> None:
        """Remove cache entries related to triggers.

        Args:
            trigger_name (str | None): Specific trigger to clean. When omitted,
                all trigger-related entries are removed.
        """
        ns = f"{self.namespace}:{self.db_label}"
        if trigger_name:
            self.disp.log_debug(
                f"Invalidating caches for trigger='{trigger_name}'")
            self._invalidate_patterns(
                [f"{ns}:schema:trigger:{trigger_name}:*"])
        else:
            self.disp.log_debug("Invalidating all trigger-related caches")
            self._invalidate_patterns([
                f"{ns}:schema:trigger:*",
                f"{ns}:schema:triggers",
                f"{ns}:schema:trigger_names",
            ])
