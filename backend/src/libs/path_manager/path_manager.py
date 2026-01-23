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
# LAST Modified: 20:47:40 23-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge of referencing all the paths_initialised supported by the server.
# // AR
# +==== END CatFeeder =================+
"""

import inspect
from typing import Union, List, Dict, Any, Optional, TYPE_CHECKING, Callable
from display_tty import Disp, initialise_logger
from starlette.responses import Response
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.exceptions import FastAPIError
from pydantic import ValidationError
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

    def add_path(self, path: str, endpoint: object, method: Union[str, List[str]], *, decorators: Optional[List[Callable]] = None) -> int:
        """Add or update a path in the routes list.

        If the same path with the same endpoint function already exists,
        merges the new method(s) with existing ones. Otherwise, adds a new route.

        Args:
            path: The path to call for the endpoint to be triggered.
            endpoint: The function that represents the endpoint.
            method: The HTTP method(s) used (GET, PUT, POST, etc.).
            decorators: Optional list of decorators to apply to the endpoint.

        Returns:
            success if it succeeded, error if there was an error in the data.
        """
        self.disp.log_debug(f"Adding path <{path}> with methods {method}")

        # Apply decorators if provided
        if decorators:
            self.disp.log_debug(
                f"Applying {len(decorators)} decorator(s) to {path}")
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
                        f"Decorator {decorator_name} did not return callable for {path}"
                    )
                    return self.error

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

    def _extract_endpoint_metadata(self, endpoint: Callable) -> Dict[str, Any]:
        """Extract metadata from endpoint function for FastAPI documentation.

        Args:
            endpoint: The endpoint function to analyze.

        Returns:
            Dictionary containing endpoint metadata like response_model, tags, etc.
        """
        endpoint_name = getattr(endpoint, '__name__', 'unknown_endpoint')
        self.disp.log_debug(
            f"Extracting metadata for endpoint: {endpoint_name}"
        )

        metadata = {}

        # Extract decorator metadata first
        decorator_metadata = self._extract_decorator_metadata(endpoint)
        if decorator_metadata:
            self.disp.log_debug(
                f"Found decorator metadata for {endpoint_name}: {list(decorator_metadata.keys())}"
            )
        metadata.update(decorator_metadata)

        # Get function signature for parameter inspection - check if inspect module is available
        if hasattr(inspect, 'signature') and callable(endpoint):
            signature_result = self._safe_extract_signature(
                endpoint, endpoint_name
            )
            if signature_result:
                metadata['signature'] = signature_result
                param_count = len(signature_result.parameters)
                self.disp.log_debug(
                    f"Extracted signature for {endpoint_name} with {param_count} parameters"
                )
        else:
            self.disp.log_warning(
                "Cannot extract signature - inspect.signature not available or endpoint not callable"
            )

        # Handle description: prefer function docstring, then decorator description
        function_description = ""
        if hasattr(endpoint, '__doc__') and endpoint.__doc__:
            function_description = endpoint.__doc__.strip()
            self.disp.log_debug(
                f"Found function docstring for {endpoint_name}"
            )

        decorator_description = metadata.get('description', "")
        if decorator_description:
            self.disp.log_debug(
                f"Found decorator description for {endpoint_name}"
            )

        if function_description and decorator_description:
            # Concatenate both if they're different
            if function_description != decorator_description:
                metadata['description'] = f"{function_description}\n\n{decorator_description}"
                self.disp.log_debug(
                    f"Combined function and decorator descriptions for {endpoint_name}"
                )
            else:
                metadata['description'] = function_description
                self.disp.log_debug(
                    f"Using identical description for {endpoint_name}"
                )
        elif function_description:
            metadata['description'] = function_description
            self.disp.log_debug(
                f"Using function description for {endpoint_name}"
            )
        elif decorator_description:
            metadata['description'] = decorator_description
            self.disp.log_debug(
                f"Using decorator description for {endpoint_name}"
            )

        # Extract any existing FastAPI metadata
        if hasattr(endpoint, '__annotations__'):
            annotation_count = len(endpoint.__annotations__)
            self.disp.log_debug(
                f"Found {annotation_count} annotations for {endpoint_name}"
            )
            metadata['annotations'] = endpoint.__annotations__

        # Check for response model in return annotation (if not set by decorator)
        if 'response_model' not in metadata and 'return' in metadata.get('annotations', {}):
            return_type = metadata['annotations']['return']
            self.disp.log_debug(
                f"Analyzing return type annotation for {endpoint_name}: {return_type}"
            )

            # Check if return type is a Response object or contains Response
            if self._is_response_type(return_type):
                # Don't set response_model for Response types
                metadata['response_model'] = None
                self.disp.log_debug(
                    f"Detected Response type for {endpoint_name}, setting response_model to None"
                )
            else:
                metadata['response_model'] = return_type
                self.disp.log_debug(
                    f"Using return type as response_model for {endpoint_name}"
                )

        self.disp.log_debug(
            f"Completed metadata extraction for {endpoint_name}"
        )
        return metadata

    def _safe_extract_signature(self, endpoint: Callable, endpoint_name: str) -> Optional[inspect.Signature]:
        """Safely extract function signature without using exceptions.

        Args:
            endpoint: The endpoint function to analyze.
            endpoint_name: Name of the endpoint for logging.

        Returns:
            Signature object if successful, None if failed.
        """
        # Check if the endpoint is callable and has the required attributes
        if not callable(endpoint):
            self.disp.log_warning(f"Endpoint {endpoint_name} is not callable")
            return None

        # Check if we can access the function's code object
        if not hasattr(endpoint, '__code__'):
            self.disp.log_warning(
                f"Endpoint {endpoint_name} has no __code__ attribute"
            )
            return None

        # Use inspect.signature with validation
        try:
            sig = inspect.signature(endpoint)
            return sig
        except (ValueError, TypeError, AttributeError) as e:
            self.disp.log_warning(
                f"Could not extract signature from {endpoint_name}: {e}"
            )
            return None

    def _extract_decorator_metadata(self, endpoint: Callable) -> Dict[str, Any]:
        """Extract metadata from decorator attributes.

        Args:
            endpoint: The endpoint function to analyze.

        Returns:
            Dictionary containing decorator metadata.
        """
        endpoint_name = getattr(endpoint, '__name__', 'unknown_endpoint')
        self.disp.log_debug(
            f"Checking for decorator metadata on {endpoint_name}"
        )

        metadata = {}

        # Security metadata
        if hasattr(endpoint, '_requires_auth') and getattr(endpoint, "_requires_auth", None):
            metadata['requires_auth'] = True
            self.disp.log_debug(
                f"Endpoint {endpoint_name} requires authentication"
            )

        if hasattr(endpoint, '_requires_admin') and getattr(endpoint, "_requires_admin", None):
            metadata['requires_admin'] = True
            self.disp.log_debug(
                f"Endpoint {endpoint_name} requires admin privileges"
            )

        if hasattr(endpoint, '_public') and getattr(endpoint, "_public", None):
            metadata['public'] = True
            self.disp.log_debug(f"Endpoint {endpoint_name} is public")

        if hasattr(endpoint, '_testing_only') and getattr(endpoint, "_testing_only", None):
            metadata['testing_only'] = True
            self.disp.log_debug(f"Endpoint {endpoint_name} is testing-only")

        if hasattr(endpoint, '_security_level'):
            metadata['security_level'] = getattr(
                endpoint, "_security_level", None
            )
            self.disp.log_debug(
                f"Endpoint {endpoint_name} has security level: {getattr(endpoint, '_security_level', 'unknown')}"
            )

        if hasattr(endpoint, '_environment'):
            metadata['environment'] = getattr(
                endpoint, "_environment", None
            )
            self.disp.log_debug(
                f"Endpoint {endpoint_name} has environment: {getattr(endpoint, '_environment', 'unknown')}"
            )

        # Documentation metadata
        if hasattr(endpoint, '_tags'):
            metadata['tags'] = getattr(endpoint, "_tags", None)
            self.disp.log_debug(
                f"Endpoint {endpoint_name} has tags: {getattr(endpoint, '_tags', False)}"
            )

        if hasattr(endpoint, '_description'):
            metadata['description'] = getattr(endpoint, "_description", None)
            self.disp.log_debug(
                f"Endpoint {endpoint_name} has decorator description"
            )

        if hasattr(endpoint, '_summary'):
            metadata['summary'] = getattr(endpoint, "_summary", None)
            self.disp.log_debug(
                f"Endpoint {endpoint_name} has summary: {getattr(endpoint, '_summary', 'None')}"
            )

        # Response metadata
        if hasattr(endpoint, '_response_model'):
            metadata['response_model'] = getattr(
                endpoint, "_response_model", None
            )
            self.disp.log_debug(
                f"Endpoint {endpoint_name} has decorator response_model"
            )

        if metadata:
            self.disp.log_debug(
                f"Found decorator metadata for {endpoint_name}: {list(metadata.keys())}"
            )
        else:
            self.disp.log_debug(
                f"No decorator metadata found for {endpoint_name}"
            )

        return metadata

    def _is_response_type(self, type_hint: Any) -> bool:
        """Check if a type hint represents a Response type that should not be used as Pydantic model.

        Args:
            type_hint: The type annotation to check.

        Returns:
            True if the type is a Response type, False otherwise.
        """
        # Check if it's directly a Response type - avoid exception by checking type first
        response_types = (
            Response, JSONResponse, HTMLResponse,
            PlainTextResponse, RedirectResponse
        )
        if type_hint in response_types:
            return True

        # Check if it's a string representation of a Response type
        if isinstance(type_hint, str):
            response_type_names = [
                'Response', 'JSONResponse',
                'HTMLResponse', 'PlainTextResponse', 'RedirectResponse'
            ]
            return any(resp_type in type_hint for resp_type in response_type_names)

        # Check if it has __name__ attribute and matches Response types
        if hasattr(type_hint, '__name__'):
            response_names = [
                'Response', 'JSONResponse',
                'HTMLResponse', 'PlainTextResponse', 'RedirectResponse'
            ]
            return type_hint.__name__ in response_names

        # Check if it's a Union type containing Response
        if hasattr(type_hint, '__origin__') and hasattr(type_hint, '__args__'):
            if type_hint.__origin__ is Union:
                return any(self._is_response_type(arg) for arg in type_hint.__args__)

        # Fallback check for string representation - avoid exception
        if hasattr(type_hint, '__str__'):
            type_str = str(type_hint)
            if 'Response' in type_str:
                # More specific check to avoid false positives
                response_indicators = [
                    'starlette.responses', 'fastapi.responses', 'Response'
                ]
                return any(indicator in type_str for indicator in response_indicators)

        return False

    def inject_routes(self) -> None:
        """Inject all registered routes into the FastAPI application.

        Iterates through all registered routes and adds them to the FastAPI
        app instance using add_api_route(). Routes must be registered before
        calling this method. Preserves endpoint metadata for proper documentation.

        Raises:
            RuntimeError: If FastAPI app instance is not found or doesn't have add_api_route method.
        """
        self.disp.log_info("Starting route injection process")
        self.disp.log_info(f"Total routes to inject: {len(self.routes)}")

        app = self.runtime_control_initialised.app

        if not app:
            self.disp.log_critical(
                "No FastAPI app instance found in RuntimeControl"
            )
            raise RuntimeError(
                "No instance was found in the app variable of the RuntimeControl instance"
            )

        if not hasattr(app, "add_api_route"):
            self.disp.log_critical("FastAPI app missing add_api_route method")
            raise RuntimeError(
                "No add_api_route function was found in the app variable of the RuntimeControl instance"
            )

        successful_injections = 0
        failed_injections = 0

        for i, route in enumerate(self.routes, 1):
            route_path = route[PATH_KEY]
            route_methods = route[METHOD_KEY]

            self.disp.log_debug(
                f"Processing route {i}/{len(self.routes)}: {route_path} [{', '.join(route_methods)}]"
            )

            # Extract endpoint metadata for better FastAPI documentation
            try:
                endpoint_metadata = self._extract_endpoint_metadata(
                    route[ENDPOINT_KEY]
                )
                self.disp.log_debug(
                    f"Successfully extracted metadata for {route_path}"
                )
            except (AttributeError, TypeError, ValueError) as e:
                self.disp.log_error(
                    f"Failed to extract metadata for {route_path}: {e}"
                )
                endpoint_metadata = {}

            # Build kwargs for add_api_route with preserved metadata
            route_kwargs = {
                'methods': route[METHOD_KEY]
            }

            # Add description if available
            if 'description' in endpoint_metadata:
                route_kwargs['description'] = endpoint_metadata['description']
                self.disp.log_debug(f"Added description to {route_path}")

            # Add summary if available
            if 'summary' in endpoint_metadata:
                route_kwargs['summary'] = endpoint_metadata['summary']
                self.disp.log_debug(f"Added summary to {route_path}")

            # Handle response model - explicitly set to None for Response types
            if 'response_model' in endpoint_metadata:
                route_kwargs['response_model'] = endpoint_metadata['response_model']
                self.disp.log_debug(f"Set response_model for {route_path}")
            else:
                # If no response model detected, set to None to prevent auto-inference issues
                route_kwargs['response_model'] = None
                self.disp.log_debug(
                    f"Set response_model to None for {route_path}"
                )

            # Add tags if available
            if 'tags' in endpoint_metadata:
                route_kwargs['tags'] = endpoint_metadata['tags']
                self.disp.log_debug(
                    f"Added tags to {route_path}: {endpoint_metadata['tags']}"
                )

            # Add security information to description for better documentation
            security_info = self._build_security_description(endpoint_metadata)
            if security_info:
                if 'description' in route_kwargs:
                    route_kwargs['description'] += f"\n\n{security_info}"
                else:
                    route_kwargs['description'] = security_info
                self.disp.log_debug(
                    f"Added security information to {route_path}"
                )

            # Add the route with metadata
            try:
                app.add_api_route(
                    route[PATH_KEY],
                    route[ENDPOINT_KEY],
                    **route_kwargs
                )
                self.disp.log_info(
                    f"Successfully injected route: {route_path} [{', '.join(route_methods)}]"
                )
                successful_injections += 1

            except (ValidationError, ValueError, TypeError) as e:
                self.disp.log_error(
                    f"Validation/Parameter error adding route {route_path}: {e}"
                )
                # Try adding route with minimal configuration as fallback
                try:
                    app.add_api_route(
                        route[PATH_KEY],
                        route[ENDPOINT_KEY],
                        methods=route[METHOD_KEY],
                        response_model=None
                    )
                    self.disp.log_warning(
                        f"Fallback injection successful for {route_path}"
                    )
                    successful_injections += 1
                except (ValidationError, ValueError, TypeError, FastAPIError, AttributeError) as fallback_error:
                    self.disp.log_error(
                        f"Fallback injection also failed for {route_path}: {fallback_error}"
                    )
                    failed_injections += 1

            except FastAPIError as e:
                self.disp.log_error(
                    f"FastAPI error adding route {route_path}: {e}"
                )
                # Try adding route with minimal configuration as fallback
                try:
                    app.add_api_route(
                        route[PATH_KEY],
                        route[ENDPOINT_KEY],
                        methods=route[METHOD_KEY],
                        response_model=None
                    )
                    self.disp.log_warning(
                        f"Fallback injection successful for {route_path}"
                    )
                    successful_injections += 1
                except (ValidationError, ValueError, TypeError, FastAPIError, AttributeError) as fallback_error:
                    self.disp.log_error(
                        f"Fallback injection also failed for {route_path}: {fallback_error}"
                    )
                    failed_injections += 1

            except AttributeError as e:
                self.disp.log_critical(
                    f"Attribute error adding route {route_path}: {e}"
                )
                failed_injections += 1
                raise RuntimeError(
                    f"FastAPI app missing required methods: {e}"
                ) from e
            except (ImportError, ModuleNotFoundError) as e:
                self.disp.log_error(
                    f"Import error adding route {route_path}: {e}"
                )
                failed_injections += 1

        # Log final summary
        self.disp.log_info(
            f"Route injection completed: {successful_injections} successful, {failed_injections} failed"
        )
        if failed_injections > 0:
            self.disp.log_warning(
                f"{failed_injections} routes failed to inject properly"
            )
        else:
            self.disp.log_info("All routes injected successfully")

    def _build_security_description(self, metadata: Dict[str, Any]) -> str:
        """Build security description from metadata.

        Args:
            metadata: Extracted endpoint metadata.

        Returns:
            Security description string or empty string.
        """
        security_notes = []

        if metadata.get('testing_only'):
            security_notes.append("Testing only - Not available in production")

        if metadata.get('public'):
            security_notes.append(
                "Public endpoint - No authentication required"
            )
        elif metadata.get('requires_admin'):
            security_notes.append("Admin only - Requires admin privileges")
        elif metadata.get('requires_auth'):
            security_notes.append(
                "Authentication required - Valid token needed"
            )

        if security_notes:
            security_description = f"Security: {' | '.join(security_notes)}"
            self.disp.log_debug(
                f"Built security description: {security_description}"
            )
            return security_description

        return ""
