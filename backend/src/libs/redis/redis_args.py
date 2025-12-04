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
# FILE: redis_args.py
# CREATION DATE: 15-11-2025
# LAST Modified: 15:41:0 17-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the file that will contain the dataclass with the optional redis initialisation information.
# // AR
# +==== END CatFeeder =================+
"""

import os
from platform import system
from dataclasses import dataclass
from typing import Mapping, List, Optional, Callable, Union, Type, TYPE_CHECKING

from redis import ConnectionPool
from redis.retry import Retry
from redis.cache import CacheConfig, CacheInterface
from redis.event import EventDispatcher
from redis.backoff import ExponentialWithJitterBackoff
from redis.credentials import CredentialProvider
from redis.maint_notifications import MaintNotificationsConfig
from redis.utils import get_lib_version

from .redis_constants import REDIS_PASSWORD_KEY, REDIS_SOCKET_DEFAULT, REDIS_SOCKET_KEY

if TYPE_CHECKING:
    import ssl
    import OpenSSL


@dataclass
class RedisArgs:
    """
    This is the config section to allow the server to easily set up the parameters for the redis instance.
    """
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    socket_timeout: Optional[float] = None
    socket_connect_timeout: Optional[float] = None
    socket_keepalive: Optional[bool] = None
    socket_keepalive_options: Optional[Mapping[int, Union[int, bytes]]] = None
    connection_pool: Optional[ConnectionPool] = None
    unix_socket_path: Optional[str] = None
    encoding: str = "utf-8"
    encoding_errors: str = "strict"
    decode_responses: bool = False
    retry_on_timeout: bool = False
    retry: Retry = Retry(
        backoff=ExponentialWithJitterBackoff(base=1, cap=10), retries=3
    )
    retry_on_error: Optional[List[Type[Exception]]] = None
    ssl: bool = False
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_cert_reqs: Union[str, "ssl.VerifyMode"] = "required"
    ssl_include_verify_flags: Optional[List["ssl.VerifyFlags"]] = None
    ssl_exclude_verify_flags: Optional[List["ssl.VerifyFlags"]] = None
    ssl_ca_certs: Optional[str] = None
    ssl_ca_path: Optional[str] = None
    ssl_ca_data: Optional[str] = None
    ssl_check_hostname: bool = True
    ssl_password: Optional[str] = None
    ssl_validate_ocsp: bool = False
    ssl_validate_ocsp_stapled: bool = False
    ssl_ocsp_context: Optional["OpenSSL.SSL.Context"] = None
    ssl_ocsp_expected_cert: Optional[str] = None
    ssl_min_version: Optional["ssl.TLSVersion"] = None
    ssl_ciphers: Optional[str] = None
    max_connections: Optional[int] = None
    single_connection_client: bool = False
    health_check_interval: int = 0
    client_name: Optional[str] = None
    lib_name: Optional[str] = "redis-py"
    lib_version: Optional[str] = get_lib_version()
    username: Optional[str] = None
    redis_connect_func: Optional[Callable[[], None]] = None
    credential_provider: Optional[CredentialProvider] = None
    protocol: Optional[int] = 2
    cache: Optional[CacheInterface] = None
    cache_config: Optional[CacheConfig] = None
    event_dispatcher: Optional[EventDispatcher] = None
    maint_notifications_config: Optional[MaintNotificationsConfig] = None


def build_redis_args() -> RedisArgs:
    """Create and return a configured Redis client.

    This function does not connect immediately; the client will establish
    a connection upon first command execution.

    Returns:
        redis.Redis: Configured Redis client instance.
    """
    socket_path = os.getenv(REDIS_SOCKET_KEY, REDIS_SOCKET_DEFAULT)
    password = os.getenv(REDIS_PASSWORD_KEY)
    if system().lower() != "Windows":
        unix_socket_path = socket_path
    else:
        unix_socket_path = None
    node: RedisArgs = RedisArgs(
        unix_socket_path=unix_socket_path,
        password=password,
        decode_responses=True
    )
    return node
