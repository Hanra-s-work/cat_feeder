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
# FILE: openapi_builder.py
# CREATION DATE: 23-01-2026
# LAST Modified: 23:51:26 23-01-2026
# DESCRIPTION:
# OpenAPI schema builder for FastAPI route documentation
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Handles all OpenAPI/documentation related functionality for PathManager
# /STOP
# // AR
# +==== END CatFeeder =================+
"""

import inspect
import json
from typing import Dict, Any, List, Callable, Optional
from display_tty import Disp, initialise_logger


class OpenAPIBuilder:
    """Handles OpenAPI schema generation and metadata extraction for endpoints."""

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, debug: bool = False):
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("OpenAPIBuilder initialized")

    def extract_endpoint_metadata(self, endpoint: Callable) -> Dict[str, Any]:
        """Extract metadata from endpoint function for FastAPI documentation."""
        endpoint_name = getattr(endpoint, '__name__', 'unknown_endpoint')
        self.disp.log_debug(
            f"Extracting metadata for endpoint: {endpoint_name}")

        metadata = {}

        try:
            decorator_metadata = self._extract_decorator_metadata(endpoint)
            if decorator_metadata:
                self.disp.log_debug(
                    f"Found decorator metadata for {endpoint_name}: {list(decorator_metadata.keys())}")
            metadata.update(decorator_metadata)
        except Exception as e:
            self.disp.log_warning(
                f"Failed to extract decorator metadata for {endpoint_name}: {e}")

        # Handle description: prefer function docstring, then decorator description
        self._extract_description_metadata(endpoint, endpoint_name, metadata)

        # DON'T extract annotations - this causes FastAPI to misinterpret function signatures
        # self._extract_annotation_metadata(endpoint, endpoint_name, metadata)

        self.disp.log_debug(
            f"Completed metadata extraction for {endpoint_name}")
        return metadata

    def build_openapi_parameters(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build OpenAPI parameter information from metadata."""
        openapi_info = {}

        # Add request body information
        self._build_request_body_info(metadata, openapi_info)

        # Add parameter information to description
        param_descriptions = []
        self._build_header_descriptions(metadata, param_descriptions)
        self._build_query_param_descriptions(metadata, param_descriptions)
        self._build_path_param_descriptions(metadata, param_descriptions)

        if param_descriptions:
            openapi_info['parameter_description'] = "\n\n".join(
                param_descriptions)

        return openapi_info

    def build_security_description(self, metadata: Dict[str, Any]) -> str:
        """Build security description from metadata."""
        security_parts = []

        if metadata.get('requires_auth'):
            security_parts.append("Authentication required")
        if metadata.get('requires_admin'):
            security_parts.append("Admin privileges required")
        if metadata.get('public'):
            security_parts.append("Public access")
        if metadata.get('testing_only'):
            security_parts.append("Testing only")

        security_level = metadata.get('security_level')
        if security_level:
            security_parts.append(f"Security level: {security_level}")

        environment = metadata.get('environment')
        if environment:
            security_parts.append(f"Environment: {environment}")

        return "\n".join(security_parts)

    # Private methods for metadata extraction
    def _extract_decorator_metadata(self, endpoint: Callable) -> Dict[str, Any]:
        """Extract metadata from decorator attributes."""
        endpoint_name = getattr(endpoint, '__name__', 'unknown_endpoint')
        metadata = {}

        # Extract security metadata
        self._extract_security_metadata(endpoint, endpoint_name, metadata)
        # Extract documentation metadata
        self._extract_documentation_metadata(endpoint, endpoint_name, metadata)
        # Extract parameter metadata
        self._extract_parameter_metadata(endpoint, endpoint_name, metadata)

        return metadata

    def _extract_description_metadata(self, endpoint: Callable, endpoint_name: str, metadata: Dict[str, Any]) -> None:
        """Extract and combine description metadata."""
        function_description = ""
        if hasattr(endpoint, '__doc__') and endpoint.__doc__:
            function_description = endpoint.__doc__.strip()
            self.disp.log_debug(
                f"Found function docstring for {endpoint_name}")

        decorator_description = metadata.get('description', "")
        if decorator_description:
            self.disp.log_debug(
                f"Found decorator description for {endpoint_name}")

        if function_description and decorator_description:
            if function_description != decorator_description:
                metadata['description'] = f"{function_description}\n\n{decorator_description}"
                self.disp.log_debug(
                    f"Combined function and decorator descriptions for {endpoint_name}")
            else:
                metadata['description'] = function_description
                self.disp.log_debug(
                    f"Using identical description for {endpoint_name}")
        elif function_description:
            metadata['description'] = function_description
            self.disp.log_debug(
                f"Using function description for {endpoint_name}")
        elif decorator_description:
            metadata['description'] = decorator_description
            self.disp.log_debug(
                f"Using decorator description for {endpoint_name}")

    def _extract_annotation_metadata(self, endpoint: Callable, endpoint_name: str, metadata: Dict[str, Any]) -> None:
        """Extract type annotation metadata safely."""
        if hasattr(endpoint, '__annotations__'):
            try:
                annotations = endpoint.__annotations__
                safe_annotations = {}
                for key, value in annotations.items():
                    if not callable(value) and not inspect.isclass(value):
                        safe_annotations[key] = str(value)

                if safe_annotations:
                    metadata['annotations'] = safe_annotations
                    self.disp.log_debug(
                        f"Found {len(safe_annotations)} safe annotations for {endpoint_name}")
            except Exception as e:
                self.disp.log_warning(
                    f"Failed to process annotations for {endpoint_name}: {e}")

    def _extract_security_metadata(self, endpoint: Callable, endpoint_name: str, metadata: Dict[str, Any]) -> None:
        """Extract security-related metadata from endpoint."""
        if hasattr(endpoint, '_requires_auth') and getattr(endpoint, "_requires_auth", None):
            metadata['requires_auth'] = True
            self.disp.log_debug(
                f"Endpoint {endpoint_name} requires authentication")

        if hasattr(endpoint, '_requires_admin') and getattr(endpoint, "_requires_admin", None):
            metadata['requires_admin'] = True
            self.disp.log_debug(
                f"Endpoint {endpoint_name} requires admin privileges")

        if hasattr(endpoint, '_public') and getattr(endpoint, "_public", None):
            metadata['public'] = True
            self.disp.log_debug(f"Endpoint {endpoint_name} is public")

        if hasattr(endpoint, '_testing_only') and getattr(endpoint, "_testing_only", None):
            metadata['testing_only'] = True
            self.disp.log_debug(f"Endpoint {endpoint_name} is testing-only")

        if hasattr(endpoint, '_security_level'):
            metadata['security_level'] = getattr(
                endpoint, "_security_level", None)
            self.disp.log_debug(
                f"Endpoint {endpoint_name} has security level: {getattr(endpoint, '_security_level', 'unknown')}")

        if hasattr(endpoint, '_environment'):
            metadata['environment'] = getattr(endpoint, "_environment", None)
            self.disp.log_debug(
                f"Endpoint {endpoint_name} has environment: {getattr(endpoint, '_environment', 'unknown')}")

    def _extract_documentation_metadata(self, endpoint: Callable, endpoint_name: str, metadata: Dict[str, Any]) -> None:
        """Extract documentation-related metadata from endpoint."""
        if hasattr(endpoint, '_tags'):
            metadata['tags'] = getattr(endpoint, "_tags", None)
            self.disp.log_debug(
                f"Endpoint {endpoint_name} has tags: {getattr(endpoint, '_tags', False)}")

        if hasattr(endpoint, '_description'):
            metadata['description'] = getattr(endpoint, "_description", None)
            self.disp.log_debug(
                f"Endpoint {endpoint_name} has decorator description")

        if hasattr(endpoint, '_summary'):
            metadata['summary'] = getattr(endpoint, "_summary", None)
            self.disp.log_debug(
                f"Endpoint {endpoint_name} has summary: {getattr(endpoint, '_summary', 'None')}")

        if hasattr(endpoint, '_response_model'):
            metadata['response_model'] = getattr(
                endpoint, "_response_model", None)
            self.disp.log_debug(
                f"Endpoint {endpoint_name} has decorator response_model")

    def _extract_parameter_metadata(self, endpoint: Callable, endpoint_name: str, metadata: Dict[str, Any]) -> None:
        """Extract parameter-related metadata from endpoint."""
        # Body metadata
        if hasattr(endpoint, '_requires_body') and getattr(endpoint, "_requires_body", None):
            metadata['requires_body'] = True
            metadata['body_model'] = getattr(endpoint, "_body_model", None)
            metadata['body_description'] = getattr(
                endpoint, "_body_description", "Request body")
            self.disp.log_debug(
                f"Endpoint {endpoint_name} requires request body")

        # Header metadata
        if hasattr(endpoint, '_requires_headers') and getattr(endpoint, "_requires_headers", None):
            metadata['requires_headers'] = True
            metadata['header_names'] = getattr(endpoint, "_header_names", [])
            metadata['headers_description'] = getattr(
                endpoint, "_headers_description", "Required headers")
            self.disp.log_debug(
                f"Endpoint {endpoint_name} requires headers: {metadata['header_names']}")

        if hasattr(endpoint, '_requires_auth_header') and getattr(endpoint, "_requires_auth_header", None):
            metadata['requires_auth_header'] = True
            metadata['auth_header_name'] = getattr(
                endpoint, "_auth_header_name", "Authorization")
            metadata['auth_scheme'] = getattr(endpoint, "_auth_scheme", None)
            self.disp.log_debug(
                f"Endpoint {endpoint_name} requires auth header")

        if hasattr(endpoint, '_requires_bearer_auth') and getattr(endpoint, "_requires_bearer_auth", None):
            metadata['requires_bearer_auth'] = True
            metadata['auth_scheme'] = "Bearer"
            metadata['auth_header_name'] = "Authorization"
            self.disp.log_debug(
                f"Endpoint {endpoint_name} requires Bearer token")

        if hasattr(endpoint, '_requires_basic_auth') and getattr(endpoint, "_requires_basic_auth", None):
            metadata['requires_basic_auth'] = True
            metadata['auth_scheme'] = "Basic"
            metadata['auth_header_name'] = "Authorization"
            self.disp.log_debug(
                f"Endpoint {endpoint_name} requires Basic auth")

        if hasattr(endpoint, '_requires_api_key') and getattr(endpoint, "_requires_api_key", None):
            metadata['requires_api_key'] = True
            metadata['auth_scheme'] = "API-Key"
            metadata['auth_header_name'] = getattr(
                endpoint, "_auth_header_name", "X-API-Key")
            self.disp.log_debug(f"Endpoint {endpoint_name} requires API key")

        # Query parameter metadata
        if hasattr(endpoint, '_requires_query_params') and getattr(endpoint, "_requires_query_params", None):
            metadata['requires_query_params'] = True
            metadata['query_params'] = getattr(endpoint, "_query_params", {})
            self.disp.log_debug(
                f"Endpoint {endpoint_name} requires query params: {list(metadata['query_params'].keys())}")

        # Path parameter metadata
        if hasattr(endpoint, '_requires_path_params') and getattr(endpoint, "_requires_path_params", None):
            metadata['requires_path_params'] = True
            metadata['path_params'] = getattr(endpoint, "_path_params", {})
            self.disp.log_debug(
                f"Endpoint {endpoint_name} requires path params: {list(metadata['path_params'].keys())}")

        # Content type metadata
        self._extract_content_type_metadata(endpoint, endpoint_name, metadata)

    def _extract_content_type_metadata(self, endpoint: Callable, endpoint_name: str, metadata: Dict[str, Any]) -> None:
        """Extract content type related metadata from endpoint."""
        if hasattr(endpoint, '_accepts_json_body') and getattr(endpoint, "_accepts_json_body", None):
            metadata['accepts_json_body'] = True
            metadata['json_body_description'] = getattr(
                endpoint, "_json_body_description", "JSON request body")
            # Extract JSON body example if available - but ensure it's serializable
            if hasattr(endpoint, '_json_body_example'):
                json_example = getattr(endpoint, "_json_body_example")
                # Only store the example if it's already a dict or can be safely converted
                if isinstance(json_example, (dict, list, str, int, float, bool, type(None))):
                    metadata['json_body_example'] = json_example
                else:
                    # Convert to string if it's not a simple type
                    metadata['json_body_example'] = str(json_example)
            self.disp.log_debug(f"Endpoint {endpoint_name} accepts JSON body")

        if hasattr(endpoint, '_accepts_form_data') and getattr(endpoint, "_accepts_form_data", None):
            metadata['accepts_form_data'] = True
            metadata['form_data_description'] = getattr(
                endpoint, "_form_data_description", "Form data")
            self.disp.log_debug(f"Endpoint {endpoint_name} accepts form data")

        if hasattr(endpoint, '_accepts_file_upload') and getattr(endpoint, "_accepts_file_upload", None):
            metadata['accepts_file_upload'] = True
            metadata['file_upload_description'] = getattr(
                endpoint, "_file_upload_description", "File upload")
            self.disp.log_debug(
                f"Endpoint {endpoint_name} accepts file upload")

    def _build_request_body_info(self, metadata: Dict[str, Any], openapi_info: Dict[str, Any]) -> None:
        """Build request body information for OpenAPI."""
        if metadata.get('requires_body') and metadata.get('body_model'):
            openapi_info['request_body'] = {
                "content": {
                    "application/json": {
                        "schema": {"type": "object"}  # Simple fallback
                    }
                },
                "description": metadata.get('body_description', 'Request body'),
                "required": True
            }
        elif metadata.get('accepts_json_body'):
            json_schema = {"type": "object"}

            json_example = metadata.get('json_body_example')
            if json_example is not None:
                try:
                    if isinstance(json_example, str):
                        parsed_example = json.loads(json_example)
                        json_schema["example"] = parsed_example
                    else:
                        json_schema["example"] = json_example
                except (json.JSONDecodeError, TypeError) as e:
                    self.disp.log_warning(
                        f"Invalid JSON example provided: {json_example}, error: {e}")
                    json_schema["description"] = f"Example: {json_example}"

            openapi_info['request_body'] = {
                "content": {
                    "application/json": {
                        "schema": json_schema
                    }
                },
                "description": metadata.get('json_body_description', 'JSON request body'),
                "required": True
            }
        elif metadata.get('accepts_form_data'):
            openapi_info['request_body'] = {
                "content": {
                    "application/x-www-form-urlencoded": {
                        "schema": {"type": "object"}
                    }
                },
                "description": metadata.get('form_data_description', 'Form data'),
                "required": True
            }
        elif metadata.get('accepts_file_upload'):
            openapi_info['request_body'] = {
                "content": {
                    "multipart/form-data": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "file": {
                                    "type": "string",
                                    "format": "binary"
                                }
                            }
                        }
                    }
                },
                "description": metadata.get('file_upload_description', 'File upload'),
                "required": True
            }

    def _build_header_descriptions(self, metadata: Dict[str, Any], param_descriptions: List[str]) -> None:
        """Build header parameter descriptions."""
        if metadata.get('requires_bearer_auth'):
            param_descriptions.append(
                "**Header:** `Authorization: Bearer <token>` - Bearer token required")
        elif metadata.get('requires_basic_auth'):
            param_descriptions.append(
                "**Header:** `Authorization: Basic <credentials>` - Basic authentication required")
        elif metadata.get('requires_api_key'):
            header_name = metadata.get('auth_header_name', 'X-API-Key')
            param_descriptions.append(
                f"**Header:** `{header_name}: <api-key>` - API key required")
        elif metadata.get('requires_auth_header'):
            header_name = metadata.get('auth_header_name', 'Authorization')
            scheme = metadata.get('auth_scheme')
            if scheme:
                param_descriptions.append(
                    f"**Header:** `{header_name}: {scheme} <credentials>` - Authentication required")
            else:
                param_descriptions.append(
                    f"**Header:** `{header_name}` - Authentication token required")

        if metadata.get('requires_headers'):
            headers = metadata.get('header_names', [])
            if headers:
                header_list = ", ".join(f"`{h}`" for h in headers)
                param_descriptions.append(
                    f"**Headers:** {header_list} - {metadata.get('headers_description', 'Required headers')}")

    def _build_query_param_descriptions(self, metadata: Dict[str, Any], param_descriptions: List[str]) -> None:
        """Build query parameter descriptions."""
        if metadata.get('requires_query_params'):
            query_params = metadata.get('query_params', {})
            if query_params:
                param_list = []
                for param, desc in query_params.items():
                    param_list.append(f"`{param}` - {desc}")
                param_descriptions.append(
                    f"**Query Parameters:** {'; '.join(param_list)}")

    def _build_path_param_descriptions(self, metadata: Dict[str, Any], param_descriptions: List[str]) -> None:
        """Build path parameter descriptions."""
        if metadata.get('requires_path_params'):
            path_params = metadata.get('path_params', {})
            if path_params:
                param_list = []
                for param, desc in path_params.items():
                    param_list.append(f"`{param}` - {desc}")
                param_descriptions.append(
                    f"**Path Parameters:** {'; '.join(param_list)}")

    def extract_route_metadata(self, endpoint: Callable) -> Dict[str, Any]:
        """Extract route metadata from decorated endpoint for FastAPI route configuration.

        Args:
            endpoint: The decorated endpoint function to extract metadata from.

        Returns:
            Dictionary containing FastAPI route configuration parameters.
        """
        metadata = {}

        # Extract all possible metadata attributes
        metadata_attrs = {
            'operation_id': '__name__',  # FastAPI uses __name__ for operation_id
            'tags': '_tags',
            'summary': '_summary',
            'description': '_description',
            'response_model': '_response_model',
            'responses': '_responses',
            'dependencies': '_dependencies',
            'status_code': '_status_code',
            'deprecated': '_deprecated',
            'include_in_schema': '_include_in_schema'
        }

        for fastapi_param, attr_name in metadata_attrs.items():
            if hasattr(endpoint, attr_name):
                value = getattr(endpoint, attr_name)
                if value is not None:
                    metadata[fastapi_param] = value
                    self.disp.log_debug(f"Found {fastapi_param}: {value}")

        # Special handling for authentication metadata
        if hasattr(endpoint, '_requires_auth') and getattr(endpoint, '_requires_auth'):
            metadata['dependencies'] = metadata.get('dependencies', [])
            # Add auth dependency if needed

        if hasattr(endpoint, '_requires_admin') and getattr(endpoint, '_requires_admin'):
            metadata['dependencies'] = metadata.get('dependencies', [])
            # Add admin dependency if needed

        # Handle JSON body metadata for better request body detection
        if hasattr(endpoint, '_accepts_json_body') and getattr(endpoint, '_accepts_json_body'):
            # This helps FastAPI detect request body requirements
            metadata['include_in_schema'] = True

        # Handle bearer auth metadata
        if hasattr(endpoint, '_requires_bearer_auth') and getattr(endpoint, '_requires_bearer_auth'):
            # Add security dependency for Bearer auth
            metadata['dependencies'] = metadata.get('dependencies', [])

        # Ensure include_in_schema defaults to True
        if 'include_in_schema' not in metadata:
            metadata['include_in_schema'] = True

        return metadata
