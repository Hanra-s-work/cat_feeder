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
# FILE: swagger_class.py
# CREATION DATE: 26-11-2025
# LAST Modified: 9:52:41 27-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The class in charge of handling the swagger instance.
# // AR
# +==== END CatFeeder =================+
"""
from typing import Optional, Dict, Any, TYPE_CHECKING
from fastapi import FastAPI, Request, Response
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from display_tty import Disp, initialise_logger
from . import swagger_constants as SWAGGER_CONST
from ...core import FinalClass, RuntimeControl, RuntimeManager, RI
from ...http_codes import HCI, HTTP_DEFAULT_TYPE
from ...server_header import ServerHeaders
from ...boilerplates import BoilerplateResponses, BoilerplateIncoming

if TYPE_CHECKING:
    from ...path_manager import PathManager


class SwaggerHandler(metaclass=FinalClass):
    """Handler for Swagger/OpenAPI documentation integration.

    This class manages the configuration and injection of Swagger UI
    documentation interface into the FastAPI application. It provides endpoints
    for accessing interactive API documentation and the OpenAPI schema.

    Attributes:
        disp (Disp): Logger instance for this class.
        debug (bool): Debug mode flag.
        success (int): Success return code.
        error (int): Error return code.
        runtime_manager (RuntimeManager): Shared runtime manager instance.
        path_manager_initialised (PathManager): Path manager for registering endpoints.
        runtime_control_initialised (RuntimeControl): Runtime control for accessing app instance.
        server_headers_initialised (ServerHeaders): Server header configuration.
        boilerplate_responses_initialised (BoilerplateResponses): Response templates.
        boilerplate_incoming_initialised (BoilerplateIncoming): Request handling utilities.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """Initialize the SwaggerHandler.

        Args:
            success (int, optional): Success return code. Defaults to 0.
            error (int, optional): Error return code. Defaults to 84.
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self.debug: bool = debug
        self.success: int = success
        self.error: int = error
        self.runtime_manager: RuntimeManager = RI
        # -------------------------- Shared instances --------------------------
        self.path_manager_initialised: "PathManager" = self.runtime_manager.get(
            "PathManager")
        self.runtime_control_initialised: RuntimeControl = self.runtime_manager.get(
            RuntimeControl)
        self.server_headers_initialised: ServerHeaders = self.runtime_manager.get(
            ServerHeaders)
        self.boilerplate_responses_initialised: BoilerplateResponses = self.runtime_manager.get(
            BoilerplateResponses)
        self.boilerplate_incoming_initialised: BoilerplateIncoming = self.runtime_manager.get(
            BoilerplateIncoming)
        self.disp.log_debug("Initialised")

    def _get_custom_openapi_schema(self, app: "FastAPI") -> Dict[str, Any]:
        """Generate custom OpenAPI schema with metadata.

        Args:
            app (FastAPI): The FastAPI application instance.

        Returns:
            Dict[str, Any]: The OpenAPI schema dictionary.
        """
        func_title = "_get_custom_openapi_schema"
        self.disp.log_debug("Generating custom OpenAPI schema", func_title)

        if app.openapi_schema:
            self.disp.log_debug("Returning cached OpenAPI schema", func_title)
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=SWAGGER_CONST.API_TITLE,
            version=SWAGGER_CONST.API_VERSION,
            description=SWAGGER_CONST.API_DESCRIPTION,
            routes=app.routes,
            tags=SWAGGER_CONST.TAGS_METADATA,
            servers=SWAGGER_CONST.SERVERS,
        )

        openapi_schema["info"]["contact"] = SWAGGER_CONST.CONTACT_INFO
        openapi_schema["info"]["license"] = SWAGGER_CONST.LICENSE_INFO

        app.openapi_schema = openapi_schema
        self.disp.log_debug("OpenAPI schema generated and cached", func_title)
        return app.openapi_schema

    def _custom_openapi_wrapper(self, app: "FastAPI") -> Dict[str, Any]:
        """Wrapper method for app.openapi() that uses the custom schema generator.

        This method serves as the openapi() callable for the FastAPI app instance.

        Args:
            app (FastAPI): The FastAPI application instance.

        Returns:
            Dict[str, Any]: The OpenAPI schema dictionary.
        """
        return self._get_custom_openapi_schema(app)

    async def get_swagger_documentation(self, request: Request) -> Response:
        """Endpoint to serve Swagger UI documentation.

        Args:
            request (Request): The incoming request object.

        Returns:
            Response: HTML response with Swagger UI interface.
        """
        func_title = "get_swagger_documentation"
        self.disp.log_debug("Serving Swagger UI", func_title)

        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request)
        self.disp.log_debug(f"token = {token}", func_title)

        if not self.runtime_control_initialised.app:
            error_body = self.boilerplate_responses_initialised.build_response_body(
                title="Swagger UI",
                message="Application not initialized",
                resp="App instance not found",
                token=token,
                error=True
            )
            return HCI.internal_server_error(
                content=error_body,
                content_type=HTTP_DEFAULT_TYPE,
                headers=self.server_headers_initialised.for_json()
            )

        return get_swagger_ui_html(
            openapi_url=SWAGGER_CONST.OPENAPI_URL,
            title=f"{SWAGGER_CONST.API_TITLE} - Swagger UI",
            oauth2_redirect_url=SWAGGER_CONST.SWAGGER_REDIRECT_URL,
            swagger_ui_parameters=SWAGGER_CONST.SWAGGER_UI_PARAMETERS,
        )

    async def get_redoc_documentation(self, request: Request) -> Response:
        """Endpoint to serve ReDoc documentation.

        Args:
            request (Request): The incoming request object.

        Returns:
            Response: HTML response with ReDoc interface.
        """
        func_title = "get_redoc_documentation"
        self.disp.log_debug("Serving ReDoc", func_title)

        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request)
        self.disp.log_debug(f"token = {token}", func_title)

        if not self.runtime_control_initialised.app:
            error_body = self.boilerplate_responses_initialised.build_response_body(
                title="ReDoc",
                message="Application not initialized",
                resp="App instance not found",
                token=token,
                error=True
            )
            return HCI.internal_server_error(
                content=error_body,
                content_type=HTTP_DEFAULT_TYPE,
                headers=self.server_headers_initialised.for_json()
            )

        return get_redoc_html(
            openapi_url=SWAGGER_CONST.OPENAPI_URL,
            title=f"{SWAGGER_CONST.API_TITLE} - ReDoc",
        )

    async def get_openapi_schema(self, request: Request) -> Response:
        """Endpoint to serve the OpenAPI JSON schema.

        Args:
            request (Request): The incoming request object.

        Returns:
            Response: JSON response with OpenAPI schema.
        """
        func_title = "get_openapi_schema"
        self.disp.log_debug("Serving OpenAPI schema", func_title)

        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request)
        self.disp.log_debug(f"token = {token}", func_title)

        if not self.runtime_control_initialised.app:
            error_body = self.boilerplate_responses_initialised.build_response_body(
                title="OpenAPI Schema",
                message="Application not initialized",
                resp="App instance not found",
                token=token,
                error=True
            )
            return HCI.internal_server_error(
                content=error_body,
                content_type=HTTP_DEFAULT_TYPE,
                headers=self.server_headers_initialised.for_json()
            )

        openapi_schema = self._get_custom_openapi_schema(
            self.runtime_control_initialised.app
        )

        return HCI.success(
            content=openapi_schema,
            content_type=HTTP_DEFAULT_TYPE,
            headers=self.server_headers_initialised.for_json()
        )

    def inject(self, app: Optional["FastAPI"] = None) -> int:
        """Inject Swagger/OpenAPI configuration into the FastAPI application.

        This method configures the FastAPI application with custom OpenAPI documentation
        settings and registers the documentation endpoints (Swagger UI, OpenAPI schema).

        Args:
            app (Optional[FastAPI], optional): The FastAPI application instance.
                If None, uses the instance from RuntimeControl. Defaults to None.

        Returns:
            int: success if injection succeeded, error if there was an error.

        Raises:
            RuntimeError: If no FastAPI application instance is available.
        """
        func_title = "inject"
        self.disp.log_debug("Starting Swagger injection", func_title)

        if app is None:
            app = self.runtime_control_initialised.app

        if not app:
            self.disp.log_error(
                "No FastAPI app instance available", func_title)
            raise RuntimeError("FastAPI application instance not found")

        if not isinstance(app, FastAPI):
            self.disp.log_error(
                f"Invalid app type: {type(app)}, expected FastAPI",
                func_title
            )
            return self.error

        self.disp.log_debug("Configuring FastAPI OpenAPI settings", func_title)

        app.docs_url = None
        app.redoc_url = None
        app.openapi_url = None

        app.title = SWAGGER_CONST.API_TITLE
        app.version = SWAGGER_CONST.API_VERSION
        app.description = SWAGGER_CONST.API_DESCRIPTION
        app.openapi_tags = SWAGGER_CONST.TAGS_METADATA
        app.contact = SWAGGER_CONST.CONTACT_INFO
        app.license_info = SWAGGER_CONST.LICENSE_INFO
        app.servers = SWAGGER_CONST.SERVERS

        self.disp.log_debug("Registering documentation endpoints", func_title)

        result = self.path_manager_initialised.add_path(
            path=SWAGGER_CONST.SWAGGER_URL,
            endpoint=self.get_swagger_documentation,
            method="GET"
        )
        if result != self.success:
            self.disp.log_error(
                f"Failed to register Swagger UI endpoint at {SWAGGER_CONST.SWAGGER_URL}",
                func_title
            )
            return self.error

        def custom_openapi() -> Dict[str, Any]:
            return self._custom_openapi_wrapper(app)

        app.openapi = custom_openapi

        self.disp.log_info(
            "Swagger/OpenAPI injection completed successfully", func_title)
        self.disp.log_info(
            f"Swagger UI available at: {SWAGGER_CONST.SWAGGER_URL}", func_title)
        self.disp.log_info(
            f"OpenAPI schema available at: {SWAGGER_CONST.OPENAPI_URL}", func_title)

        return self.success
