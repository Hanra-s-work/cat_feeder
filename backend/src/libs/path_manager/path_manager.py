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
# FILE: paths.py
# CREATION DATE: 11-10-2025
# LAST Modified: 3:5:6 27-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: File in charge of referencing all the paths_initialised supported by the server.
# // AR
# +==== END AsperBackend =================+
"""

from typing import Union, List, Dict, Any, Optional, TYPE_CHECKING
from display_tty import Disp, initialise_logger
from .path_constants import PATH_KEY, ENDPOINT_KEY,  METHOD_KEY, ALLOWED_METHODS
from ..core.runtime_manager import RuntimeManager, RI
from ..core import FinalClass, RuntimeControl
if TYPE_CHECKING:
    from ..endpoint_manager import EndpointManager


class PathManager(metaclass=FinalClass):
    """Manager for API route registration and validation.

    Handles registration of API endpoints with their paths and HTTP methods,
    validates route configurations, and manages route injection into FastAPI.
    Automatically merges methods when the same path/endpoint combination is
    registered multiple times.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """Initialize the path manager.

        Args:
            success: Success return code.
            error: Error return code.
            debug: Enable debug logging.
        """
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self.success = success
        self.error = error
        self.routes: List[Dict[str, Any]] = []
        self.debug: bool = debug
        self.runtime_manager_initialised: RuntimeManager = RI
        # -------------------------- Shared instances --------------------------
        self.endpoints_initialised: Optional['EndpointManager'] = self.runtime_manager_initialised.get_if_exists(
            "EndpointManager",
            None
        )
        self.runtime_control_initialised: RuntimeControl = self.runtime_manager_initialised.get(
            RuntimeControl)
        self.disp.log_debug("Initialised")

    def endpoint_valid(self, path: str, endpoint: object, method: Union[str, List[str]]) -> bool:
        """Validate endpoint configuration.

        Checks that path is a string, endpoint is callable, and method(s)
        are valid HTTP methods from the ALLOWED_METHODS list.

        Args:
            path: The endpoint path to validate.
            endpoint: The endpoint function to validate.
            method: HTTP method(s) to validate.

        Returns:
            True if all validations pass, False otherwise.
        """
        if not isinstance(path, str) or not isinstance(method, (str, list)) or not callable(endpoint):
            self.disp.log_error(
                f"Failed to insert {path} with method {method}"
            )
            return False

        if isinstance(method, str):
            methods_to_check = [method]
        else:
            methods_to_check = method

        for http_method in methods_to_check:
            if not isinstance(http_method, str) or http_method.upper() not in ALLOWED_METHODS:
                self.disp.log_error(
                    f"Failed to insert {path}, method {http_method} not allowed"
                )
                return False

        return True

    def _build_endpoint(self, path: str, endpoint: object, method: Union[str, List[str]]) -> Optional[Dict[str, Union[str, object, List[str]]]]:
        """Build endpoint dictionary from components.

        Validates the endpoint and constructs a standardized dictionary
        with path, endpoint function, and method(s).

        Args:
            path: The endpoint path.
            endpoint: The endpoint function.
            method: HTTP method(s) - converted to list if string.

        Returns:
            Dictionary with PATH_KEY, ENDPOINT_KEY, and METHOD_KEY if valid,
            None if validation fails.
        """
        if not self.endpoint_valid(path, endpoint, method):
            return None

        if isinstance(method, str):
            methods = [method]
        else:
            methods = method

        return {PATH_KEY: path, ENDPOINT_KEY: endpoint, METHOD_KEY: methods}

    def add_path(self, path: str, endpoint: object, method: Union[str, List[str]]) -> int:
        """Add or update a path in the routes list.

        If the same path with the same endpoint function already exists,
        merges the new method(s) with existing ones. Otherwise, adds a new route.

        Args:
            path: The path to call for the endpoint to be triggered.
            endpoint: The function that represents the endpoint.
            method: The HTTP method(s) used (GET, PUT, POST, etc.).

        Returns:
            success if it succeeded, error if there was an error in the data.
        """
        self.disp.log_debug(f"Adding path <{path}>")

        # Validate the endpoint first
        if not self.endpoint_valid(path, endpoint, method):
            return self.error

        # Check if this path + endpoint combination already exists
        existing_idx = self._find_route_index(path, endpoint)

        if existing_idx != -1:
            # Route exists - merge methods
            existing_route = self.routes[existing_idx]
            merged_methods = self._merge_methods(
                existing_route[METHOD_KEY],
                method
            )
            self.routes[existing_idx][METHOD_KEY] = merged_methods
            self.disp.log_warning(
                f"Updated existing route <{path}> with methods: {merged_methods}"
            )
        else:
            # New route - build and append
            new_endpoint = self._build_endpoint(path, endpoint, method)
            if not new_endpoint:
                return self.error
            self.routes.append(new_endpoint)
            self.disp.log_debug(
                f"Added new route <{path}> with methods: {new_endpoint[METHOD_KEY]}"
            )

        return self.success

    def has_endpoint(self, path: str, endpoint: object, method: Union[str, List[str]]) -> bool:
        """Check if an endpoint with exact path, endpoint function, and method exists.

        Args:
            path: The endpoint path.
            endpoint: The endpoint function.
            method: HTTP method(s) to check.

        Returns:
            True if exact match exists, False otherwise.
        """
        endpoint_config = self._build_endpoint(path, endpoint, method)
        if not endpoint_config:
            return False

        return endpoint_config in self.routes

    def _find_route_index(self, path: str, endpoint: object) -> int:
        """Find the index of a route by path and endpoint function.

        Args:
            path: The endpoint path.
            endpoint: The endpoint function.

        Returns:
            Index of the route if found, -1 otherwise.
        """
        for idx, route in enumerate(self.routes):
            if route[PATH_KEY] == path and route[ENDPOINT_KEY] == endpoint:
                return idx
        return -1

    def _merge_methods(self, existing_methods: List[str], new_methods: Union[str, List[str]]) -> List[str]:
        """Merge new methods with existing methods, avoiding duplicates.

        Args:
            existing_methods: List of existing HTTP methods.
            new_methods: New method(s) to add.

        Returns:
            Merged list of unique methods in uppercase.
        """
        if isinstance(new_methods, str):
            methods_to_add = [new_methods]
        else:
            methods_to_add = new_methods

        all_methods = set()
        for method in existing_methods:
            all_methods.add(method.upper())

        for method in methods_to_add:
            all_methods.add(method.upper())

        return sorted(all_methods)

    def load_default_paths_initialised(self) -> None:
        """Load default application paths from EndpointManager.

        Retrieves the EndpointManager instance and calls its inject_routes()
        method to register all default application endpoints.

        Raises:
            RuntimeError: If EndpointManager instance cannot be found.
        """
        func_title = "load_default_paths_initialised"
        self.disp.log_debug("Loading default paths_initialised", func_title)

        self.endpoints_initialised = self.runtime_manager_initialised.get_if_exists(
            "EndpointManager",
            self.endpoints_initialised
        )

        if not self.endpoints_initialised:
            error_message = "EndpointManager could not be found"
            self.disp.log_critical(error_message)
            raise RuntimeError(error_message)

        self.endpoints_initialised.inject_routes()

    def inject_routes(self) -> None:
        """Inject all registered routes into the FastAPI application.

        Iterates through all registered routes and adds them to the FastAPI
        app instance using add_api_route(). Routes must be registered before
        calling this method.

        Raises:
            RuntimeError: If FastAPI app instance is not found or doesn't have add_api_route method.
        """
        self.disp.log_info("Injecting routes")

        app = self.runtime_control_initialised.app

        if not app:
            raise RuntimeError(
                "No instance was found in the app variable of the RuntimeControl instance"
            )

        if not hasattr(app, "add_api_route"):
            raise RuntimeError(
                "No add_api_route function was found in the app variable of the RuntimeControl instance"
            )

        for route in self.routes:
            self.disp.log_debug(f"route = {route}")
            app.add_api_route(
                route[PATH_KEY],
                route[ENDPOINT_KEY],
                methods=route[METHOD_KEY]
            )
        self.disp.log_info("Routes injected")
