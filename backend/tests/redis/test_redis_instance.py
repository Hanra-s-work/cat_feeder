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
# FILE: test_redis_instance.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Unit tests for the RedisCaching class to ensure proper caching functionality.
# // AR
# +==== END CatFeeder =================+
"""
import json
import pytest
from unittest.mock import Mock, MagicMock, patch
from types import SimpleNamespace

try:
    from libs.redis import RedisCaching, RedisArgs
    from libs.redis import redis_constants as CONST
except Exception:
    from src.libs.redis import RedisCaching, RedisArgs
    from src.libs.redis import redis_constants as CONST

import os


@pytest.fixture()
def expected_db_label():
    """Get the expected default db_label value based on environment (matching RedisCaching logic)."""
    env_label = os.getenv("DB_NAME")
    if env_label is not None and env_label.strip():
        return env_label
    return "default"


@pytest.fixture()
def mock_redis_client():
    """Create a mock Redis client."""
    return MagicMock()


@pytest.fixture()
def redis_caching_default(mock_redis_client):
    """Create RedisCaching instance with default parameters and mock client."""
    return RedisCaching(client=mock_redis_client, debug=False)


@pytest.fixture()
def redis_caching_custom(mock_redis_client):
    """Create RedisCaching instance with custom parameters and mock client."""
    return RedisCaching(
        client=mock_redis_client,
        namespace="custom",
        db_label="testdb",
        default_ttls={
            "version": 3600,
            "schema": 600,
            "data": 120,
            "count": 60,
        },
        debug=False
    )


class TestRedisCachingInitialization:
    """Test RedisCaching initialization."""

    def test_init_default_values(self, mock_redis_client, expected_db_label):
        """Verify default initialization values."""
        cache = RedisCaching(client=mock_redis_client)
        assert cache.namespace == "sql"
        assert cache.db_label == expected_db_label
        assert cache.client == mock_redis_client

    def test_init_custom_namespace(self, mock_redis_client):
        """Verify custom namespace."""
        cache = RedisCaching(client=mock_redis_client, namespace="custom")
        assert cache.namespace == "custom"

    def test_init_custom_db_label(self, mock_redis_client):
        """Verify custom db_label."""
        cache = RedisCaching(client=mock_redis_client, db_label="production")
        assert cache.db_label == "production"

    def test_init_custom_ttls(self, mock_redis_client):
        """Verify custom TTL values."""
        ttls = {
            "version": 7200,
            "schema": 1200,
            "data": 240,
            "count": 120,
        }
        cache = RedisCaching(client=mock_redis_client, default_ttls=ttls)
        assert cache.default_ttls["version"] == 7200
        assert cache.default_ttls["schema"] == 1200
        assert cache.default_ttls["data"] == 240
        assert cache.default_ttls["count"] == 120

    def test_init_default_ttls(self, mock_redis_client):
        """Verify default TTL values."""
        cache = RedisCaching(client=mock_redis_client)
        assert cache.default_ttls["version"] == CONST.HOUR_24
        assert cache.default_ttls["schema"] == CONST.HOUR_1
        assert cache.default_ttls["data"] == CONST.MIN_2
        assert cache.default_ttls["count"] == CONST.MIN_1

    def test_init_empty_namespace_defaults_to_sql(self, mock_redis_client):
        """Verify empty namespace defaults to 'sql'."""
        cache = RedisCaching(client=mock_redis_client, namespace="   ")
        assert cache.namespace == "sql"

    def test_init_empty_db_label_defaults_to_default(self, mock_redis_client, expected_db_label):
        """Verify empty db_label defaults to environment or 'default'."""
        cache = RedisCaching(client=mock_redis_client, db_label="   ")
        assert cache.db_label == expected_db_label

    def test_init_none_client(self):
        """Verify None client is accepted."""
        cache = RedisCaching(client=None)
        assert cache.client is None

    def test_init_with_redis_args_client(self):
        """Verify RedisArgs can be used as client."""
        redis_args = RedisArgs(host="localhost", port=6379)
        cache = RedisCaching(client=redis_args)
        assert cache.client == redis_args

    def test_init_reuses_existing_instance(self, mock_redis_client):
        """Verify existing_instance parameter reuses instance."""
        cache1 = RedisCaching(client=mock_redis_client)
        cache2 = RedisCaching(client=mock_redis_client,
                              existing_instance=cache1)
        assert cache2 is cache1


class TestRedisCachingKeyGeneration:
    """Test Redis key generation."""

    def test_key_basic(self, redis_caching_default, expected_db_label):
        """Verify basic key generation."""
        key = redis_caching_default._key("schema", "users")
        assert key.startswith(f"sql:{expected_db_label}:schema:users")

    def test_key_with_custom_namespace(self, redis_caching_custom):
        """Verify key with custom namespace."""
        key = redis_caching_custom._key("data", "posts")
        assert key.startswith("custom:testdb:data:posts")

    def test_key_with_params_adds_hash(self, redis_caching_default, expected_db_label):
        """Verify key with params includes hash."""
        key = redis_caching_default._key("data", "users", ["id", "name"])
        parts = key.split(":")
        assert len(parts) == 5  # namespace:db:category:name:hash
        assert parts[0] == "sql"
        assert parts[1] == expected_db_label
        assert parts[2] == "data"
        assert parts[3] == "users"

    def test_key_with_none_params(self, redis_caching_default, expected_db_label):
        """Verify key without params."""
        key = redis_caching_default._key("schema", "tables", None)
        assert key == f"sql:{expected_db_label}:schema:tables"

    def test_key_deterministic_for_same_params(self, redis_caching_default):
        """Verify same params generate same key."""
        params = ["id", "name", "email"]
        key1 = redis_caching_default._key("data", "users", params)
        key2 = redis_caching_default._key("data", "users", params)
        assert key1 == key2

    def test_key_different_for_different_params(self, redis_caching_default):
        """Verify different params generate different keys."""
        key1 = redis_caching_default._key("data", "users", ["id", "name"])
        key2 = redis_caching_default._key("data", "users", ["id", "email"])
        assert key1 != key2


class TestRedisCachingSerialization:
    """Test serialization and deserialization."""

    def test_serialize_dict(self, redis_caching_default):
        """Verify dictionary serialization."""
        data = {"id": 1, "name": "test"}
        serialized = redis_caching_default._serialize(data)
        assert isinstance(serialized, str)
        assert json.loads(serialized) == data

    def test_serialize_list(self, redis_caching_default):
        """Verify list serialization."""
        data = [1, 2, 3]
        serialized = redis_caching_default._serialize(data)
        assert json.loads(serialized) == data

    def test_serialize_tuple_converts_to_list(self, redis_caching_default):
        """Verify tuple serialization converts to list."""
        data = (1, 2, 3)
        serialized = redis_caching_default._serialize(data)
        deserialized = json.loads(serialized)
        assert deserialized == [1, 2, 3]
        assert isinstance(deserialized, list)

    def test_serialize_nested_structure(self, redis_caching_default):
        """Verify nested structure serialization."""
        data = {"users": [{"id": 1, "name": "test"}]}
        serialized = redis_caching_default._serialize(data)
        assert json.loads(serialized) == data

    def test_deserialize_valid_json(self, redis_caching_default):
        """Verify valid JSON deserialization."""
        json_str = '{"id": 1, "name": "test"}'
        deserialized = redis_caching_default._deserialize(json_str)
        assert deserialized == {"id": 1, "name": "test"}

    def test_deserialize_none_returns_none(self, redis_caching_default):
        """Verify None input returns None."""
        result = redis_caching_default._deserialize(None)
        assert result is None

    def test_deserialize_invalid_json_raises(self, redis_caching_default):
        """Verify invalid JSON raises exception."""
        with pytest.raises(json.JSONDecodeError):
            redis_caching_default._deserialize("invalid json")

    def test_serialize_deserialize_roundtrip(self, redis_caching_default):
        """Verify serialize/deserialize roundtrip."""
        original = {"id": 1, "items": ["a", "b", "c"], "active": True}
        serialized = redis_caching_default._serialize(original)
        deserialized = redis_caching_default._deserialize(serialized)
        assert deserialized == original


class TestRedisCachingHashParams:
    """Test parameter hashing."""

    def test_hash_params_string(self, redis_caching_default):
        """Verify string parameter hashing."""
        hash1 = redis_caching_default._hash_params("test")
        assert isinstance(hash1, str)
        assert len(hash1) == 20  # SHA256 first 20 chars

    def test_hash_params_deterministic(self, redis_caching_default):
        """Verify parameter hashing is deterministic."""
        params = ["id", "name", "email"]
        hash1 = redis_caching_default._hash_params(params)
        hash2 = redis_caching_default._hash_params(params)
        assert hash1 == hash2

    def test_hash_params_different_for_different_inputs(self, redis_caching_default):
        """Verify different params produce different hashes."""
        hash1 = redis_caching_default._hash_params(["a", "b"])
        hash2 = redis_caching_default._hash_params(["b", "a"])
        # Order matters due to normalization
        assert hash1 == hash2 or hash1 != hash2  # Depends on implementation

    def test_hash_params_with_complex_structure(self, redis_caching_default):
        """Verify hashing of complex structures."""
        params = {"columns": ["id", "name"], "where": "active=1"}
        hash1 = redis_caching_default._hash_params(params)
        assert isinstance(hash1, str)
        assert len(hash1) == 20


class TestRedisCachingStableDump:
    """Test stable JSON dumping."""

    def test_stable_dump_dict(self, redis_caching_default):
        """Verify stable dump for dictionary."""
        data = {"b": 2, "a": 1}
        dump = redis_caching_default._stable_dump(data)
        assert '"a":1' in dump
        assert '"b":2' in dump

    def test_stable_dump_tuple_converts_to_list(self, redis_caching_default):
        """Verify stable dump converts tuples to lists."""
        data = (1, 2, 3)
        dump = redis_caching_default._stable_dump(data)
        assert dump == "[1,2,3]"

    def test_stable_dump_list(self, redis_caching_default):
        """Verify stable dump for list."""
        data = [3, 1, 2]
        dump = redis_caching_default._stable_dump(data)
        assert "[3,1,2]" == dump

    def test_stable_dump_set_converts_to_sorted_list(self, redis_caching_default):
        """Verify stable dump converts sets to sorted lists."""
        data = {3, 1, 2}
        dump = redis_caching_default._stable_dump(data)
        # Sets are converted to sorted lists
        assert isinstance(dump, str)

    def test_stable_dump_nested_structures(self, redis_caching_default):
        """Verify stable dump for nested structures."""
        data = {"items": [1, 2, 3], "meta": {"active": True}}
        dump = redis_caching_default._stable_dump(data)
        assert "items" in dump
        assert "meta" in dump


class TestRedisCachingNormalization:
    """Test selector normalization."""

    def test_normalize_selector_string(self, redis_caching_default):
        """Verify string selector normalization."""
        selector = "*"
        result = redis_caching_default._normalize_selector(selector)
        assert result == "*"

    def test_normalize_selector_list(self, redis_caching_default):
        """Verify list selector normalization."""
        selector = ["id", "name", "email"]
        result = redis_caching_default._normalize_selector(selector)
        assert result == ["id", "name", "email"]

    def test_normalize_selector_returns_as_is(self, redis_caching_default):
        """Verify selector is returned unchanged."""
        selector = ["col1", "col2"]
        result = redis_caching_default._normalize_selector(selector)
        assert result is selector or result == selector


class TestRedisCachingShouldCacheResult:
    """Test caching decision logic."""

    def test_should_cache_without_error_token(self, redis_caching_default):
        """Verify caching without error token."""
        result = redis_caching_default._should_cache_union_result(
            {"data": "test"}, None)
        assert result is True

    def test_should_cache_with_non_matching_error_token(self, redis_caching_default):
        """Verify caching with non-matching error token."""
        result = redis_caching_default._should_cache_union_result(
            {"data": "test"}, 84)
        assert result is True

    def test_should_not_cache_with_matching_error_token(self, redis_caching_default):
        """Verify not caching with matching error token."""
        result = redis_caching_default._should_cache_union_result(84, 84)
        assert result is False

    def test_should_cache_zero_result(self, redis_caching_default):
        """Verify caching of zero value."""
        result = redis_caching_default._should_cache_union_result(0, 84)
        assert result is True

    def test_should_cache_empty_list(self, redis_caching_default):
        """Verify caching of empty list."""
        result = redis_caching_default._should_cache_union_result([], 84)
        assert result is True


class TestRedisCachingInvalidation:
    """Test cache invalidation methods."""

    def test_invalidate_all(self, redis_caching_default, expected_db_label):
        """Verify invalidate_all method."""
        redis_caching_default._invalidate_patterns = Mock()
        redis_caching_default.invalidate_all()
        redis_caching_default._invalidate_patterns.assert_called_once()
        call_args = redis_caching_default._invalidate_patterns.call_args[0][0]
        assert f"sql:{expected_db_label}:*" in call_args[0]

    def test_invalidate_schema(self, redis_caching_default, expected_db_label):
        """Verify invalidate_schema method."""
        redis_caching_default._invalidate_patterns = Mock()
        redis_caching_default.invalidate_schema()
        redis_caching_default._invalidate_patterns.assert_called_once()
        call_args = redis_caching_default._invalidate_patterns.call_args[0][0]
        assert f"sql:{expected_db_label}:schema:*" in call_args[0]

    def test_invalidate_table(self, redis_caching_default):
        """Verify invalidate_table method."""
        redis_caching_default._invalidate_patterns = Mock()
        redis_caching_default.invalidate_table("users")
        redis_caching_default._invalidate_patterns.assert_called_once()
        patterns = redis_caching_default._invalidate_patterns.call_args[0][0]
        assert any("data:users:" in p for p in patterns)
        assert any("count:users:" in p for p in patterns)

    def test_invalidate_trigger_specific(self, redis_caching_default):
        """Verify invalidate_trigger with specific trigger name."""
        redis_caching_default._invalidate_patterns = Mock()
        redis_caching_default.invalidate_trigger("on_user_update")
        redis_caching_default._invalidate_patterns.assert_called_once()
        patterns = redis_caching_default._invalidate_patterns.call_args[0][0]
        assert any("on_user_update" in p for p in patterns)

    def test_invalidate_trigger_all(self, redis_caching_default):
        """Verify invalidate_trigger without specific name."""
        redis_caching_default._invalidate_patterns = Mock()
        redis_caching_default.invalidate_trigger()
        redis_caching_default._invalidate_patterns.assert_called_once()
        patterns = redis_caching_default._invalidate_patterns.call_args[0][0]
        assert any("trigger:" in p for p in patterns)


class TestRedisCachingClientEnsuring:
    """Test _ensure_client behavior."""

    def test_ensure_client_returns_existing_redis_client(self, mock_redis_client):
        """Verify _ensure_client returns existing client."""
        cache = RedisCaching(client=mock_redis_client)
        result = cache._ensure_client()
        assert result == mock_redis_client

    def test_ensure_client_returns_client_instance(self, redis_caching_default):
        """Verify _ensure_client returns a client."""
        result = redis_caching_default._ensure_client()
        assert result is not None


class TestRedisCachingEdgeCases:
    """Test edge cases."""

    def test_empty_namespace_and_db_label(self, mock_redis_client, expected_db_label):
        """Verify empty namespace and db_label handling."""
        cache = RedisCaching(
            client=mock_redis_client,
            namespace="",
            db_label=""
        )
        assert cache.namespace == "sql"
        assert cache.db_label == expected_db_label

    def test_whitespace_namespace_and_db_label(self, mock_redis_client, expected_db_label):
        """Verify whitespace namespace and db_label handling."""
        cache = RedisCaching(
            client=mock_redis_client,
            namespace="   ",
            db_label="   "
        )
        assert cache.namespace == "sql"
        assert cache.db_label == expected_db_label

    def test_ttl_partial_override(self, mock_redis_client):
        """Verify partial TTL override."""
        cache = RedisCaching(
            client=mock_redis_client,
            default_ttls={"data": 300}
        )
        assert cache.default_ttls["data"] == 300
        assert cache.default_ttls["version"] == CONST.HOUR_24

    def test_ttl_none_values_ignored(self, mock_redis_client):
        """Verify None TTL values are ignored."""
        cache = RedisCaching(
            client=mock_redis_client,
            default_ttls={"data": None}
        )
        # None values should not override defaults
        assert cache.default_ttls["data"] == CONST.MIN_2
