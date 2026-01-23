"""
# +==== BEGIN CatFeeder =================+
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
# ...##.........#.############...
# ......#.......#.#########......
# .......#......#.########.......
# .........#####...#####.........
# /STOP
# PROJECT: CatFeeder
# FILE: endpoints_routes.py
# CREATION DATE: 11-10-2025
# LAST Modified: 11:56:14 23-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the file in charge of storing the endpoints_initialised ready to be imported into the server class.
# // AR
# +==== END CatFeeder =================+
"""
from typing import Optional
from display_tty import Disp, initialise_logger
from . import endpoint_constants as ENDPOINT_CONST
from .endpoints import Bonus
from .endpoints import CatEndpoints
from .endpoints import UserEndpoints
from .endpoints import AdminEndpoints
from .endpoints import TokenEndpoints
from .endpoints import TestingEndpoints
from ..path_manager import PathManager
from ..core import FinalClass
from ..utils.password_handling import PasswordHandling
from ..core.runtime_manager import RuntimeManager, RI
from ..utils.oauth_authentication import OAuthAuthentication


class EndpointManager(metaclass=FinalClass):
    """_summary_
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """_summary_

        Args:
            runtime_data (RuntimeData): _description_
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
        self.password_handling_initialised: PasswordHandling = PasswordHandling(
            self.error,
            self.success,
            self.debug
        )
        self.paths_initialised: Optional[PathManager] = None
        self._retrieve_path_manager()
        self.oauth_authentication_initialised: Optional[OAuthAuthentication] = self.runtime_manager.get_if_exists(
            OAuthAuthentication,
            None
        )
        self.disp.update_disp_debug(self.debug)
        # ------------------- Initialize endpoints sub-classes ------------------
        self.user: UserEndpoints = UserEndpoints(
            success=self.success,
            error=self.error,
            debug=self.debug
        )
        self.bonus: Bonus = Bonus(
            success=success,
            error=error,
            debug=debug
        )
        self.cat_endpoints: CatEndpoints = CatEndpoints(
            success=success,
            error=error,
            debug=debug
        )
        self.admin: AdminEndpoints = AdminEndpoints(
            success=success,
            error=error,
            debug=debug
        )
        self.testing_endpoints: TestingEndpoints = TestingEndpoints(
            success=self.success,
            error=self.error,
            debug=self.debug
        )
        self.token_endpoints: TokenEndpoints = TokenEndpoints(
            success=self.success,
            error=self.error,
            debug=self.debug
        )
        # ------------------------- Endpoint Prefixing -------------------------
        self.api_str: str = "/api"
        self.v1_str: str = f"{self.api_str}/v1"
        self.oauth_str: str = f"{self.v1_str}/oauth"
        self.test_endpoint: str = "/testing"
        self.sql_endpoint: str = f"{self.test_endpoint}/sql"
        self.bucket_endpoint: str = f"{self.test_endpoint}/bucket"
        self.favicon_endpoint: str = f"{self.v1_str}/favicons"
        self.user_favicon_endpoint: str = f"{self.v1_str}/user_favicon"
        self.token_endpoint: str = f"{self.v1_str}/token"
        self.disp.log_debug("Initialised")

    def _retrieve_path_manager(self) -> Optional[PathManager]:
        if self.paths_initialised is not None:
            return self.paths_initialised
        if self.runtime_manager.exists(PathManager):
            self.paths_initialised = self.runtime_manager.get(PathManager)
            return self.paths_initialised
        return None

    def inject_routes(self) -> None:
        """_summary_
        """
        self._retrieve_path_manager()
        if not self.paths_initialised:
            err_msg: str = "PathManager could not be found"
            self.disp.log_critical(err_msg)
            raise RuntimeError(err_msg)

        # User Endpoints
        # |- connection
        self.paths_initialised.add_path(
            f"{self.v1_str}/register", self.user.post_register, ["POST"]
        )

        self.paths_initialised.add_path(
            f"{self.v1_str}/login", self.user.post_login, ["POST"]
        )

        self.paths_initialised.add_path(
            f"{self.v1_str}/logout", self.user.post_logout, ["POST"]
        )

        # |- e-mail verification
        self.paths_initialised.add_path(
            f"{self.v1_str}/send_email_verification", self.user.post_send_email_verification,
            ["POST"]
        )

        # |- password reset
        self.paths_initialised.add_path(
            f"{self.v1_str}/reset_password", self.user.put_reset_password,
            ["PUT"]
        )

        # |- user update
        self.paths_initialised.add_path(
            f"{self.v1_str}/user", self.user.put_user, ["PUT"]
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/user", self.user.patch_user, ["PATCH"]
        )

        # |- info querying
        self.paths_initialised.add_path(
            f"{self.v1_str}/user", self.user.get_user, ["GET"]
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/user_id", self.user.get_user_id, ["GET"]
        )

        # |- user removal
        self.paths_initialised.add_path(
            f"{self.v1_str}/user", self.user.delete_user, ["DELETE"]
        )

        # Cat Endpoints
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder/register", self.cat_endpoints.put_register_feeder, "PUT"
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder", self.cat_endpoints.patch_feeder, "PATCH"
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder/status", self.cat_endpoints.get_feeder_status, "GET"
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder", self.cat_endpoints.delete_feeder, "DELETE"
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder/feed", self.cat_endpoints.get_distribute_food, "GET"
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder/fed", self.cat_endpoints.post_distribute_food, "POST"
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder/ip", self.cat_endpoints.put_register_feeder, "PUT"
        )
        # Beacon routes
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder/beacon/register", self.cat_endpoints.register_beacon, "PUT"
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder/beacon/status", self.cat_endpoints.get_beacon_status, "GET"
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder/beacon", self.cat_endpoints.patch_beacon, "PATCH"
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder/beacon", self.cat_endpoints.delete_beacon, "DELETE"
        )
        # location endpoints
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder/beacon/locations", self.cat_endpoints.get_beacon_locations, "GET"
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder/beacon/location", self.cat_endpoints.post_beacon_location, "POST"
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder/visits", self.cat_endpoints.get_feeder_visits, "GET"
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/feeder/visit", self.cat_endpoints.post_feeder_visit, "POST"
        )

        # Pet endpoints
        self.paths_initialised.add_path(
            f"{self.v1_str}/pet/register", self.cat_endpoints.put_register_pet, "PUT"
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/pet", self.cat_endpoints.patch_pet, "PATCH"
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/pet", self.cat_endpoints.delete_pet, "DELETE"
        )

        # Bonus routes
        self.paths_initialised.add_path(
            "", self.bonus.get_welcome, [
                "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"
            ]
        )
        self.paths_initialised.add_path(
            "/", self.bonus.get_welcome, [
                "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"
            ]
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/", self.bonus.get_welcome, [
                "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"
            ]
        )
        self.paths_initialised.add_path(
            f"{self.v1_str}/stop", self.bonus.post_stop_server, "PUT"
        )

        # Health check endpoint
        self.paths_initialised.add_path(
            "/health", self.bonus.get_health, "GET"
        )

        # favicon.ico support
        self.paths_initialised.add_path(
            "/favicon.ico", self.bonus.get_favicon, "GET"
        )

        # /static/logo.png support
        self.paths_initialised.add_path(
            "/static/logo.png", self.bonus.get_static_logo, "GET"
        )

        # Oauth routes
        self.oauth_authentication_initialised = self.runtime_manager.get_if_exists(
            OAuthAuthentication,
            self.oauth_authentication_initialised
        )
        if not self.oauth_authentication_initialised:
            self.disp.log_error("OAuth Authentication is missing")
            raise RuntimeError("Token validation service unavailable")
        self.paths_initialised.add_path(
            f"{self.oauth_str}/login", self.oauth_authentication_initialised.oauth_login, "POST"
        )
        self.paths_initialised.add_path(
            f"{self.oauth_str}/callback", self.oauth_authentication_initialised.oauth_callback, "POST"
        )
        self.paths_initialised.add_path(
            f"{self.oauth_str}/{'{provider}'}",
            self.oauth_authentication_initialised.add_oauth_provider, "POST"
        )
        self.paths_initialised.add_path(
            f"{self.oauth_str}/{'{provider}'}",
            self.oauth_authentication_initialised.update_oauth_provider_data, "PUT"
        )
        self.paths_initialised.add_path(
            f"{self.oauth_str}/{'{provider}'}",
            self.oauth_authentication_initialised.patch_oauth_provider_data, "PATCH"
        )
        self.paths_initialised.add_path(
            f"{self.oauth_str}/{'{provider}'}",
            self.oauth_authentication_initialised.delete_oauth_provider, "DELETE"
        )

        # Token route
        self.paths_initialised.add_path(
            f"{self.token_endpoint}/valid", self.token_endpoints.get_token_valid, "GET"
        )
        self.paths_initialised.add_path(
            f"{self.token_endpoint}/admin", self.token_endpoints.get_admin, "GET"
        )
        self.paths_initialised.add_path(
            f"{self.token_endpoint}/ttl", self.token_endpoints.get_time_to_live, "GET"
        )
        self.paths_initialised.add_path(
            f"{self.token_endpoint}/info", self.token_endpoints.get_token_info, "GET"
        )
        self.paths_initialised.add_path(
            f"{self.token_endpoint}/refresh", self.token_endpoints.post_refresh_token, "POST"
        )
        self.paths_initialised.add_path(
            f"{self.token_endpoint}/revoke_account_tokens", self.token_endpoints.delete_revoke_account_token, "DELETE"
        )

        # Testing endpoints (only if enabled in configuration)
        if ENDPOINT_CONST.TEST_ENABLE_TESTING_ENDPOINTS:
            self.disp.log_debug("Testing endpoints enabled")
            # SQL testing endpoints
            self.paths_initialised.add_path(
                f"{self.sql_endpoint}/tables", self.testing_endpoints.get_tables, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.sql_endpoint}/table/columns", self.testing_endpoints.get_table_columns, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.sql_endpoint}/table/describe", self.testing_endpoints.describe_table, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.sql_endpoint}/table/size", self.testing_endpoints.get_table_size, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.sql_endpoint}/version", self.testing_endpoints.get_database_version, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.sql_endpoint}/connected", self.testing_endpoints.test_sql_connection, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.sql_endpoint}/triggers", self.testing_endpoints.get_triggers, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.sql_endpoint}/triggers/names", self.testing_endpoints.get_trigger_names, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.sql_endpoint}/datetime/now", self.testing_endpoints.get_current_datetime, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.sql_endpoint}/datetime/today", self.testing_endpoints.get_current_date, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.sql_endpoint}/datetime/to-string", self.testing_endpoints.convert_datetime_to_string, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.sql_endpoint}/datetime/from-string", self.testing_endpoints.convert_string_to_datetime, "GET"
            )
            # Bucket testing endpoints
            self.paths_initialised.add_path(
                f"{self.bucket_endpoint}/buckets", self.testing_endpoints.get_buckets, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.bucket_endpoint}/connected", self.testing_endpoints.test_bucket_connection, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.bucket_endpoint}/create", self.testing_endpoints.create_test_bucket, "POST"
            )
            self.paths_initialised.add_path(
                f"{self.bucket_endpoint}/upload", self.testing_endpoints.upload_test_file_stream, "POST"
            )
            self.paths_initialised.add_path(
                f"{self.bucket_endpoint}/files", self.testing_endpoints.get_bucket_files, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.bucket_endpoint}/files/info", self.testing_endpoints.get_bucket_file_info, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.bucket_endpoint}/download", self.testing_endpoints.download_test_file_stream, "GET"
            )
            self.paths_initialised.add_path(
                f"{self.bucket_endpoint}/delete", self.testing_endpoints.delete_test_bucket, "DELETE"
            )
            self.paths_initialised.add_path(
                f"{self.bucket_endpoint}/delete-file", self.testing_endpoints.delete_test_file, "DELETE"
            )
        else:
            self.disp.log_debug("Testing endpoints disabled")
