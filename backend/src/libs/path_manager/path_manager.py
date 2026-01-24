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
# FILE: paths.py
# CREATION DATE: 11-10-2025
# LAST Modified: 1:44:14 24-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge of referencing all the paths_initialised supported by the server.
# // AR
# +==== END CatFeeder =================+
"""

from typing import Union, List, Dict, Any, Optional, TYPE_CHECKING, Callable
import inspect
from functools import wraps

from display_tty import Disp, initialise_logger
from .path_constants import PATH_KEY, ENDPOINT_KEY,  METHOD_KEY, ALLOWED_METHODS
from ..core.runtime_manager import RuntimeManager, RI
from ..core import FinalClass, RuntimeControl
from .openapi_builder import OpenAPIBuilder

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
        self.openapi_builder = OpenAPIBuilder(debug=debug)
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

    def add_path(self, path: str, endpoint: object, method: Union[str, List[str]], *, decorators: Optional[List[Callable]] = None) -> int:
        """Add or update a path in the routes list."""
        self.disp.log_debug(f"Adding path <{path}> with methods {method}")

        # Apply decorators if provided
        if decorators:
            self.disp.log_debug(
                f"Applying {len(decorators)} decorator(s) to {path}")

            # Log the original endpoint signature
            try:
                orig_sig = inspect.signature(endpoint)
                self.disp.log_debug(f"Original endpoint signature: {orig_sig}")
            except Exception as e:
                self.disp.log_warning(f"Could not get original signature: {e}")

            for i, decorator in enumerate(decorators):
                decorator_name = getattr(
                    decorator, '__name__', f'decorator_{i}')
                self.disp.log_debug(
                    f"Applying decorator {decorator_name} to {path}")

                # Check if decorator is callable before applying
                if not callable(decorator):
                    self.disp.log_error(
                        f"Decorator {decorator_name} is not callable for {path}")
                    return self.error

                # Apply decorator and check if it returns a valid result
                decorated_endpoint = decorator(endpoint)
                if not callable(decorated_endpoint):
                    self.disp.log_error(
                        f"Decorator {decorator_name} did not return callable for {path}")
                    return self.error

                # Log the signature after each decorator
                try:
                    new_sig = inspect.signature(decorated_endpoint)
                    self.disp.log_debug(f"After {decorator_name}: {new_sig}")
                except Exception as e:
                    self.disp.log_warning(
                        f"Could not get signature after {decorator_name}: {e}")

                endpoint = decorated_endpoint
        else:
            self.disp.log_debug(f"No decorators provided for {path}")

        # Validate the endpoint first
        if not self.endpoint_valid(path, endpoint, method):
            self.disp.log_error(
                f"Endpoint validation failed for {path} with method {method}"
            )
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
                self.disp.log_error(f"Failed to build endpoint for {path}")
                return self.error
            self.routes.append(new_endpoint)
            self.disp.log_info(
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

    def is_path_registered(self, path: str, method: Optional[Union[str, List[str]]] = None) -> bool:
        """Check if a path is already registered, optionally with specific method(s).

        Args:
            path: The endpoint path to check.
            method: Optional HTTP method(s) to check. If None, checks if path exists with any method.

        Returns:
            True if path is registered (with optional method match), False otherwise.
        """
        for route in self.routes:
            if route[PATH_KEY] == path:
                if method is None:
                    # Just checking if path exists, regardless of methods
                    return True

                # Check if specific method(s) are registered
                if isinstance(method, str):
                    methods_to_check = [method.upper()]
                else:
                    methods_to_check = [m.upper() for m in method]

                route_methods = [m.upper() for m in route[METHOD_KEY]]

                # Check if any of the requested methods are already registered
                for check_method in methods_to_check:
                    if check_method in route_methods:
                        return True

        return False

    def add_path_if_not_exists(self, path: str, endpoint: object, method: Union[str, List[str]], *, decorators: Optional[List[Callable]] = None) -> int:
        """Add path only if it doesn't already exist.

        Args:
            path: The path to call for the endpoint to be triggered.
            endpoint: The function that represents the endpoint.
            method: The HTTP method(s) used (GET, PUT, POST, etc.).
            decorators: Optional list of decorators to apply.

        Returns:
            success if it succeeded or already exists, error if there was an error.
        """
        if self.is_path_registered(path, method):
            self.disp.log_debug(
                f"Path {path} with method(s) {method} already registered, skipping")
            return self.success

        return self.add_path(path, endpoint, method, decorators=decorators)

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

    def _wrap_endpoint_to_hide_parameters(self, endpoint: Callable, endpoint_name: str) -> Callable:
        """Wrap endpoint to hide parameters that FastAPI shouldn't see as query parameters."""

        # Check if the endpoint has parameters that might cause issues
        try:
            sig = inspect.signature(endpoint)
            params = list(sig.parameters.keys())

            # Filter out 'self' for instance methods
            if params and params[0] == 'self':
                params = params[1:]

            # If there are remaining parameters, they'll be treated as query parameters
            if params:
                self.disp.log_warning(
                    f"Endpoint {endpoint_name} has parameters {params} that will become query parameters")

                # Create a wrapper that accepts the request but doesn't expose it to FastAPI
                @wraps(endpoint)
                def wrapper(request):
                    # Call original endpoint with the request parameter
                    if hasattr(endpoint, '__self__'):
                        # Instance method - call with self and request
                        return endpoint(request)
                    else:
                        # Static/class method - call with request
                        return endpoint(request)

                # Override the signature to show no parameters to FastAPI
                setattr(wrapper, "__signature__", inspect.Signature())
                wrapper.__name__ = f"wrapped_{endpoint_name}"
                self.disp.log_info(
                    f"Wrapped endpoint {endpoint_name} to hide parameters")
                return wrapper
            else:
                # No problematic parameters
                return endpoint

        except Exception as e:
            self.disp.log_warning(
                f"Could not inspect endpoint {endpoint_name}: {e}")
            return endpoint

    def inject_routes(self) -> None:
        """Inject all registered routes into the FastAPI application."""
        self.disp.log_info("Starting route injection process")
        self.disp.log_info(f"Total routes to inject: {len(self.routes)}")

        app = self.runtime_control_initialised.app

        if not app:
            self.disp.log_critical(
                "No FastAPI app instance found in RuntimeControl")
            raise RuntimeError(
                "No instance was found in the app variable of the RuntimeControl instance")

        if not hasattr(app, "add_api_route"):
            self.disp.log_critical("FastAPI app missing add_api_route method")
            raise RuntimeError(
                "No add_api_route function was found in the app variable of the RuntimeControl instance")

        successful_injections = 0
        failed_injections = 0

        for i, route in enumerate(self.routes, 1):
            route_path = route[PATH_KEY]
            route_methods = route[METHOD_KEY]

            self.disp.log_debug(
                f"Processing route {i}/{len(self.routes)}: {route_path} [{', '.join(route_methods)}]")

            original_endpoint = route[ENDPOINT_KEY]
            endpoint_name = getattr(
                original_endpoint, '__name__', 'unknown_endpoint')

            try:
                sig = inspect.signature(original_endpoint)
                self.disp.log_debug(
                    f"Endpoint {endpoint_name} signature: {sig}")
            except Exception as e:
                self.disp.log_warning(
                    f"Could not get signature for {endpoint_name}: {e}")

            # Use OpenAPIBuilder to extract metadata - this is its responsibility
            route_kwargs = self.openapi_builder.extract_route_metadata(
                original_endpoint)
            route_kwargs['methods'] = route_methods

            self.disp.log_debug(
                f"Route metadata for {route_path}: {route_kwargs}")

            try:
                app.add_api_route(
                    route_path, original_endpoint, **route_kwargs)
                self.disp.log_info(
                    f"Successfully injected route: {route_path} [{', '.join(route_methods)}]")
                successful_injections += 1

            except Exception as e:
                self.disp.log_error(f"Error adding route {route_path}: {e}")
                # Fallback with minimal config
                try:
                    app.add_api_route(
                        route_path, original_endpoint, methods=route_methods)
                    self.disp.log_warning(
                        f"Fallback injection successful for {route_path}")
                    successful_injections += 1
                except Exception as fallback_error:
                    self.disp.log_error(
                        f"Fallback injection failed for {route_path}: {fallback_error}")
                    failed_injections += 1

        self.disp.log_info(
            f"Route injection completed: {successful_injections} successful, {failed_injections} failed")
