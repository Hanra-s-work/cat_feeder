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
# FILE: test_redis_args.py
# CREATION DATE: 11-01-2026
# LAST Modified: 5:5:37 11-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Unit tests for the RedisArgs dataclass to ensure proper configuration initialization.
# // AR
# +==== END CatFeeder =================+
"""
import os
import pytest
from unittest.mock import patch

try:
    from libs.redis import RedisArgs, build_redis_args
    from libs.redis import redis_constants as CONST
except Exception:
    from src.libs.redis import RedisArgs, build_redis_args
    from src.libs.redis import redis_constants as CONST


class TestRedisArgsInitialization:
    """Test RedisArgs dataclass initialization."""

    def test_init_default_values(self):
        """Verify default initialization values."""
        args = RedisArgs()
        assert args.host == "localhost"
        assert args.port == 6379
        assert args.db == 0
        assert args.password is None
        assert args.socket_timeout is None
        assert args.socket_connect_timeout is None
        assert args.socket_keepalive is None
        assert args.unix_socket_path is None
        assert args.encoding == "utf-8"
        assert args.encoding_errors == "strict"
        assert args.decode_responses is False
        assert args.retry_on_timeout is False
        assert args.ssl is False
        assert args.ssl_check_hostname is True
        assert args.single_connection_client is False
        assert args.health_check_interval == 0

    def test_init_custom_values(self):
        """Verify custom initialization values."""
        args = RedisArgs(
            host="redis.example.com",
            port=6380,
            db=1,
            password="secret",
            decode_responses=True,
            ssl=True
        )
        assert args.host == "redis.example.com"
        assert args.port == 6380
        assert args.db == 1
        assert args.password == "secret"
        assert args.decode_responses is True
        assert args.ssl is True

    def test_init_unix_socket_path(self):
        """Verify Unix socket path configuration."""
        args = RedisArgs(unix_socket_path="/tmp/redis.sock")
        assert args.unix_socket_path == "/tmp/redis.sock"

    def test_init_ssl_settings(self):
        """Verify SSL configuration."""
        args = RedisArgs(
            ssl=True,
            ssl_keyfile="/path/to/key.pem",
            ssl_certfile="/path/to/cert.pem",
            ssl_ca_certs="/path/to/ca.pem"
        )
        assert args.ssl is True
        assert args.ssl_keyfile == "/path/to/key.pem"
        assert args.ssl_certfile == "/path/to/cert.pem"
        assert args.ssl_ca_certs == "/path/to/ca.pem"

    def test_init_timeout_settings(self):
        """Verify timeout configuration."""
        args = RedisArgs(
            socket_timeout=5.0,
            socket_connect_timeout=3.0
        )
        assert args.socket_timeout == 5.0
        assert args.socket_connect_timeout == 3.0


class TestBuildRedisArgsEnvironment:
    """Test build_redis_args environment variable handling."""

    def test_build_redis_args_default_tcp(self):
        """Verify TCP connection with default settings."""
        with patch.dict(os.environ, {"REDIS_SOCKET": "/nonexistent/path"}, clear=True):
            args = build_redis_args()
            assert args.host == CONST.REDIS_HOST_DEFAULT
            assert args.port == CONST.REDIS_PORT_DEFAULT
            assert args.decode_responses is True

    def test_build_redis_args_custom_host(self):
        """Verify custom host from environment."""
        with patch.dict(os.environ, {"REDIS_HOST": "redis.local", "REDIS_SOCKET": "/nonexistent/path"}, clear=True):
            args = build_redis_args()
            assert args.host == "redis.local"

    def test_build_redis_args_custom_port(self):
        """Verify custom port from environment."""
        with patch.dict(os.environ, {"REDIS_PORT": "6380", "REDIS_SOCKET": "/nonexistent/path"}, clear=True):
            args = build_redis_args()
            assert args.port == 6380

    def test_build_redis_args_with_password(self):
        """Verify password from environment."""
        with patch.dict(os.environ, {"REDIS_PASSWORD": "mypassword"}, clear=True):
            args = build_redis_args()
            assert args.password == "mypassword"

    def test_build_redis_args_invalid_port_raises(self):
        """Verify invalid port raises ValueError."""
        with patch.dict(os.environ, {"REDIS_PORT": "invalid"}, clear=True):
            with pytest.raises(ValueError):
                build_redis_args()

    def test_build_redis_args_port_out_of_range(self):
        """Verify port out of range raises ValueError."""
        with patch.dict(os.environ, {"REDIS_PORT": "70000"}, clear=True):
            with pytest.raises(ValueError):
                build_redis_args()

    def test_build_redis_args_decode_responses_true(self):
        """Verify decode_responses is always True."""
        with patch.dict(os.environ, {}, clear=True):
            args = build_redis_args()
            assert args.decode_responses is True

    def test_build_redis_args_tcp_settings(self):
        """Verify TCP connection settings."""
        with patch.dict(os.environ, {
            "REDIS_HOST": "myhost",
            "REDIS_PORT": "6380",
            "REDIS_SOCKET": "/nonexistent/path"
        }, clear=True):
            args = build_redis_args()
            assert args.host == "myhost"
            assert args.port == 6380

    def test_build_redis_args_multiple_env_vars(self):
        """Verify multiple environment variables work together."""
        with patch.dict(os.environ, {
            "REDIS_HOST": "redis.example.com",
            "REDIS_PORT": "6380",
            "REDIS_PASSWORD": "secret123",
            "REDIS_SOCKET": "/nonexistent/path"
        }, clear=True):
            args = build_redis_args()
            assert args.host == "redis.example.com"
            assert args.port == 6380
            assert args.password == "secret123"


class TestRedisConstants:
    """Test redis_constants values."""

    def test_environment_variable_keys(self):
        """Verify environment variable key constants."""
        assert CONST.REDIS_SOCKET_KEY == "REDIS_SOCKET"
        assert CONST.REDIS_PASSWORD_KEY == "REDIS_PASSWORD"
        assert CONST.REDIS_HOST_KEY == "REDIS_HOST"
        assert CONST.REDIS_PORT_KEY == "REDIS_PORT"

    def test_default_values(self):
        """Verify default value constants."""
        assert CONST.REDIS_SOCKET_DEFAULT == "/run/redis/redis.sock"
        assert CONST.REDIS_HOST_DEFAULT == "127.0.0.1"
        assert CONST.REDIS_PORT_DEFAULT == 6379

    def test_time_constants_seconds(self):
        """Verify second constants."""
        assert CONST.SEC_1 == 1
        assert CONST.SEC_10 == 10
        assert CONST.SEC_30 == 30
        assert CONST.SEC_60 == 60

    def test_time_constants_minutes(self):
        """Verify minute constants."""
        assert CONST.MIN_1 == 60
        assert CONST.MIN_5 == 300
        assert CONST.MIN_10 == 600
        assert CONST.MIN_60 == 3600

    def test_time_constants_hours(self):
        """Verify hour constants."""
        assert CONST.HOUR_1 == 3600
        assert CONST.HOUR_2 == 7200
        assert CONST.HOUR_12 == 43200
        assert CONST.HOUR_24 == 86400

    def test_time_constants_days(self):
        """Verify day constants."""
        assert CONST.DAY_1 == 86400
        assert CONST.DAY_2 == 172800
        assert CONST.DAY_5 == 432000
        assert CONST.DAY_6 == 518400

    def test_time_constant_relationships(self):
        """Verify relationships between time constants."""
        assert CONST.MIN_1 == 60
        assert CONST.HOUR_1 == CONST.MIN_1 * 60
        assert CONST.DAY_1 == CONST.HOUR_24
        assert CONST.MIN_5 == CONST.MIN_1 * 5
        assert CONST.HOUR_2 == CONST.HOUR_1 * 2


class TestRedisArgsDataclassFeatures:
    """Test RedisArgs as a dataclass."""

    def test_is_dataclass(self):
        """Verify RedisArgs is properly configured as a dataclass."""
        args = RedisArgs()
        assert hasattr(args, "host")
        assert hasattr(args, "port")
        assert hasattr(args, "password")

    def test_can_be_instantiated_with_kwargs(self):
        """Verify instantiation with keyword arguments."""
        args = RedisArgs(host="test", port=1234, password="test123")
        assert args.host == "test"
        assert args.port == 1234
        assert args.password == "test123"

    def test_partial_initialization(self):
        """Verify partial initialization uses defaults."""
        args = RedisArgs(host="custom.host")
        assert args.host == "custom.host"
        assert args.port == 6379
        assert args.password is None

    def test_retry_object_default(self):
        """Verify retry object is properly initialized."""
        args = RedisArgs()
        assert args.retry is not None

    def test_client_name_parameter(self):
        """Verify client_name parameter."""
        args = RedisArgs(client_name="my-app")
        assert args.client_name == "my-app"

    def test_lib_name_default(self):
        """Verify lib_name default value."""
        args = RedisArgs()
        assert args.lib_name == "redis-py"


class TestRedisArgsPortValidation:
    """Test port validation in build_redis_args."""

    def test_valid_port_minimum(self):
        """Verify minimum valid port."""
        with patch.dict(os.environ, {"REDIS_PORT": "1", "REDIS_SOCKET": "/nonexistent/path"}, clear=True):
            args = build_redis_args()
            assert args.port == 1

    def test_valid_port_maximum(self):
        """Verify maximum valid port."""
        with patch.dict(os.environ, {"REDIS_PORT": "65535", "REDIS_SOCKET": "/nonexistent/path"}, clear=True):
            args = build_redis_args()
            assert args.port == 65535

    def test_invalid_port_zero(self):
        """Verify port 0 is invalid."""
        with patch.dict(os.environ, {"REDIS_PORT": "0"}, clear=True):
            with pytest.raises(ValueError):
                build_redis_args()

    def test_invalid_port_negative(self):
        """Verify negative port is invalid."""
        with patch.dict(os.environ, {"REDIS_PORT": "-1"}, clear=True):
            with pytest.raises(ValueError):
                build_redis_args()

    def test_invalid_port_non_numeric(self):
        """Verify non-numeric port raises ValueError."""
        with patch.dict(os.environ, {"REDIS_PORT": "notaport"}, clear=True):
            with pytest.raises(ValueError):
                build_redis_args()


class TestRedisArgsConnectionModes:
    """Test different connection modes in RedisArgs."""

    def test_tcp_mode_default(self):
        """Verify default TCP mode settings."""
        args = RedisArgs()
        assert args.host == "localhost"
        assert args.port == 6379
        assert args.unix_socket_path is None

    def test_unix_socket_mode(self):
        """Verify Unix socket mode."""
        args = RedisArgs(unix_socket_path="/tmp/redis.sock")
        assert args.unix_socket_path == "/tmp/redis.sock"
        assert args.host == "localhost"
        assert args.port == 6379

    def test_ssl_enabled_mode(self):
        """Verify SSL mode configuration."""
        args = RedisArgs(ssl=True)
        assert args.ssl is True

    def test_all_ssl_options(self):
        """Verify all SSL-related options."""
        args = RedisArgs(
            ssl=True,
            ssl_keyfile="/path/key",
            ssl_certfile="/path/cert",
            ssl_cert_reqs="required",
            ssl_ca_certs="/path/ca",
            ssl_ca_path="/path/cadir",
            ssl_check_hostname=True
        )
        assert args.ssl is True
        assert args.ssl_keyfile == "/path/key"
        assert args.ssl_certfile == "/path/cert"
        assert args.ssl_ca_certs == "/path/ca"


class TestRedisArgsEdgeCases:
    """Test edge cases in RedisArgs configuration."""

    def test_empty_password(self):
        """Verify empty string password."""
        args = RedisArgs(password="")
        assert args.password == ""

    def test_zero_db(self):
        """Verify db=0."""
        args = RedisArgs(db=0)
        assert args.db == 0

    def test_high_db_number(self):
        """Verify high db number."""
        args = RedisArgs(db=15)
        assert args.db == 15

    def test_zero_health_check_interval(self):
        """Verify zero health check interval."""
        args = RedisArgs(health_check_interval=0)
        assert args.health_check_interval == 0

    def test_large_health_check_interval(self):
        """Verify large health check interval."""
        args = RedisArgs(health_check_interval=300)
        assert args.health_check_interval == 300

    def test_special_characters_in_password(self):
        """Verify password with special characters."""
        password = "p@ss!w0rd#123"
        args = RedisArgs(password=password)
        assert args.password == password

    def test_special_characters_in_host(self):
        """Verify host with special characters."""
        host = "redis-cache-01.internal"
        args = RedisArgs(host=host)
        assert args.host == host
