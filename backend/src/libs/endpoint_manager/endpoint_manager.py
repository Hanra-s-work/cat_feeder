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
# FILE: endpoints_routes.py
# CREATION DATE: 11-10-2025
# LAST Modified: 7:50:36 02-12-20255
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: This is the file in charge of storing the endpoints_initialised ready to be imported into the server class.
# // AR
# +==== END AsperBackend =================+
"""
from typing import Optional
from display_tty import Disp, initialise_logger
from . import endpoint_constants as ENDPOINT_CONST
from .endpoints import Bonus
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
        self.bonus: Bonus = Bonus(
            success=success,
            error=error,
            debug=debug
        )
        self.testing_endpoints: TestingEndpoints = TestingEndpoints(
            success=self.success,
            error=self.error,
            debug=self.debug
        )
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
            "/api/v1/", self.bonus.get_welcome, "GET"
        )
        self.paths_initialised.add_path(
            "/api/v1/stop", self.bonus.post_stop_server, "PUT"
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
            "/api/v1/oauth/login", self.oauth_authentication_initialised.oauth_login, "POST"
        )
        self.paths_initialised.add_path(
            "/api/v1/oauth/callback", self.oauth_authentication_initialised.oauth_callback, "POST"
        )
        self.paths_initialised.add_path(
            "/api/v1/oauth/{provider}", self.oauth_authentication_initialised.add_oauth_provider, "POST"
        )
        self.paths_initialised.add_path(
            "/api/v1/oauth/{provider}", self.oauth_authentication_initialised.update_oauth_provider_data, "PUT"
        )
        self.paths_initialised.add_path(
            "/api/v1/oauth/{provider}", self.oauth_authentication_initialised.patch_oauth_provider_data, "PATCH"
        )
        self.paths_initialised.add_path(
            "/api/v1/oauth/{provider}", self.oauth_authentication_initialised.delete_oauth_provider, "DELETE"
        )

        # Testing endpoints (only if enabled in configuration)
        if ENDPOINT_CONST.TEST_ENABLE_TESTING_ENDPOINTS:
            test_endpoint: str = "/testing"
            sql_endpoint: str = f"{test_endpoint}/sql"
            bucket_endpoint: str = f"{test_endpoint}/bucket"
            self.disp.log_debug("Testing endpoints enabled")
            self.paths_initialised.add_path(
                f"{sql_endpoint}/tables", self.testing_endpoints.get_tables, "GET"
            )
            self.paths_initialised.add_path(
                f"{sql_endpoint}/table/columns", self.testing_endpoints.get_table_columns, "GET"
            )
            self.paths_initialised.add_path(
                f"{sql_endpoint}/table/describe", self.testing_endpoints.describe_table, "GET"
            )
            self.paths_initialised.add_path(
                f"{sql_endpoint}/table/size", self.testing_endpoints.get_table_size, "GET"
            )
            self.paths_initialised.add_path(
                f"{sql_endpoint}/version", self.testing_endpoints.get_database_version, "GET"
            )
            self.paths_initialised.add_path(
                f"{sql_endpoint}/connected", self.testing_endpoints.test_sql_connection, "GET"
            )
            self.paths_initialised.add_path(
                f"{sql_endpoint}/triggers", self.testing_endpoints.get_triggers, "GET"
            )
            self.paths_initialised.add_path(
                f"{sql_endpoint}/triggers/names", self.testing_endpoints.get_trigger_names, "GET"
            )
            self.paths_initialised.add_path(
                f"{sql_endpoint}/datetime/now", self.testing_endpoints.get_current_datetime, "GET"
            )
            self.paths_initialised.add_path(
                f"{sql_endpoint}/datetime/today", self.testing_endpoints.get_current_date, "GET"
            )
            self.paths_initialised.add_path(
                f"{sql_endpoint}/datetime/to-string", self.testing_endpoints.convert_datetime_to_string, "GET"
            )
            self.paths_initialised.add_path(
                f"{sql_endpoint}/datetime/from-string", self.testing_endpoints.convert_string_to_datetime, "GET"
            )
            self.paths_initialised.add_path(
                f"{bucket_endpoint}/buckets", self.testing_endpoints.get_buckets, "GET"
            )
            self.paths_initialised.add_path(
                f"{bucket_endpoint}/connected", self.testing_endpoints.test_bucket_connection, "GET"
            )
            self.paths_initialised.add_path(
                f"{bucket_endpoint}/files", self.testing_endpoints.get_bucket_files, "GET"
            )
            self.paths_initialised.add_path(
                f"{bucket_endpoint}/files/info", self.testing_endpoints.get_bucket_file_info, "GET"
            )
            self.paths_initialised.add_path(
                f"{bucket_endpoint}/create", self.testing_endpoints.create_test_bucket, "POST"
            )
            self.paths_initialised.add_path(
                f"{bucket_endpoint}/delete", self.testing_endpoints.delete_test_bucket, "DELETE"
            )
        else:
            self.disp.log_debug("Testing endpoints disabled")
