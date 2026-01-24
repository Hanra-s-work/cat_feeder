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
# FILE: docs_handler.py
# CREATION DATE: 26-11-2025
# LAST Modified: 2:9:10 24-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file containing the class in charge of injecting the documentation handler desired by the user.
# // AR
# +==== END CatFeeder =================+
"""
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, Response
from fastapi.openapi.utils import get_openapi
from display_tty import Disp, initialise_logger
from . import docs_constants as DOCS_CONST
from .swagger import SwaggerHandler
from .redoc import RedocHandler
from .rapidoc import RapiDocProvider
from .scalar import ScalarProvider
from .elements import StoplightElementsProvider
from .editor import SwaggerEditorProvider
from .explorer import OpenAPIExplorerProvider
from .rapipdf import RapiPDFProvider
from ..core import FinalClass, RuntimeControl
from ..http_codes import HCI, HttpDataTypes
from ..core.runtime_manager import RuntimeManager, RI
from ..server_header import ServerHeaders
from ..path_manager import PathManager
from ..boilerplates import BoilerplateResponses, BoilerplateIncoming


class DocumentationHandler(metaclass=FinalClass):
    """Unified documentation handler for managing multiple API documentation providers.

    This class provides a centralized interface for enabling and managing different
    API documentation providers (Swagger UI, ReDoc, RapiDoc, Scalar, etc.). It handles
    the registration of documentation endpoints and the serving of OpenAPI schemas.

    Attributes:
        disp (Disp): Logger instance for this class.
        debug (bool): Debug mode flag.
        success (int): Success return code.
        error (int): Error return code.
        runtime_manager (RuntimeManager): Shared runtime manager instance.
        enabled_providers (tuple): Tuple of enabled documentation providers.
        providers (Dict): Dictionary mapping provider names to their instances.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(
        self,
        providers: Optional[tuple[DOCS_CONST.DocumentationProvider, ...]] = None,
        openapi_url: str = DOCS_CONST.OPENAPI_URL,
        api_title: str = DOCS_CONST.OPENAPI_TITLE,
        api_version: str = DOCS_CONST.OPENAPI_VERSION,
        api_description: str = DOCS_CONST.OPENAPI_DESCRIPTION,
        success: int = 0,
        error: int = 84,
        debug: bool = False
    ) -> None:
        """Initialize the DocumentationHandler.

        Args:
            providers (Optional[tuple], optional): Tuple of documentation providers to enable.
                Defaults to DOCS_CONST.DEFAULT_PROVIDERS.
            openapi_url (str, optional): URL path for OpenAPI JSON schema.
                Defaults to DOCS_CONST.OPENAPI_URL.
            api_title (str, optional): API title for documentation.
                Defaults to DOCS_CONST.OPENAPI_TITLE.
            api_version (str, optional): API version string.
                Defaults to DOCS_CONST.OPENAPI_VERSION.
            api_description (str, optional): API description for documentation.
                Defaults to DOCS_CONST.OPENAPI_DESCRIPTION.
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
        # ----------------------- Shared instance handler ----------------------
        self.runtime_manager: RuntimeManager = RI
        # -------------------------- Shared instances --------------------------
        self.path_manager_initialised: PathManager = self.runtime_manager.get(
            PathManager)
        self.runtime_control_initialised: RuntimeControl = self.runtime_manager.get(
            RuntimeControl)
        self.server_headers_initialised: ServerHeaders = self.runtime_manager.get(
            ServerHeaders)
        self.boilerplate_responses_initialised: BoilerplateResponses = self.runtime_manager.get(
            BoilerplateResponses)
        self.boilerplate_incoming_initialised: BoilerplateIncoming = self.runtime_manager.get(
            BoilerplateIncoming)
        # ------------------ Inherited documentation settings ------------------
        self.openapi_url: str = openapi_url
        self.api_title: str = api_title
        self.api_version: str = api_version
        self.api_description: str = api_description
        # ------------------------- Provider handling  -------------------------
        if providers is None:
            self.enabled_providers = DOCS_CONST.DEFAULT_PROVIDERS
        else:
            self.enabled_providers = providers

        self.providers: Dict[str, Any] = {}
        # Note: Providers are initialized in inject() to avoid accessing FastAPI before it exists
        # ----- The actual classes in charge of handling the documentation -----
        self.provider_factories = {
            DOCS_CONST.DocumentationProvider.SWAGGER: lambda: SwaggerHandler(
                success=self.success,
                error=self.error,
                debug=self.debug
            ),
            DOCS_CONST.DocumentationProvider.REDOC: lambda: RedocHandler(
                success=self.success,
                error=self.error,
                debug=self.debug
            ),
            DOCS_CONST.DocumentationProvider.RAPIDOC: lambda: RapiDocProvider(
                openapi_url=self.openapi_url,
                api_title=self.api_title,
                debug=self.debug
            ),
            DOCS_CONST.DocumentationProvider.SCALAR: lambda: ScalarProvider(
                openapi_url=self.openapi_url,
                api_title=self.api_title,
                debug=self.debug
            ),
            DOCS_CONST.DocumentationProvider.ELEMENTS: lambda: StoplightElementsProvider(
                openapi_url=self.openapi_url,
                api_title=self.api_title,
                debug=self.debug
            ),
            DOCS_CONST.DocumentationProvider.EDITOR: lambda: SwaggerEditorProvider(
                openapi_url=self.openapi_url,
                api_title=self.api_title,
                debug=self.debug
            ),
            DOCS_CONST.DocumentationProvider.EXPLORER: lambda: OpenAPIExplorerProvider(
                openapi_url=self.openapi_url,
                api_title=self.api_title,
                debug=self.debug
            ),
            DOCS_CONST.DocumentationProvider.RAPIPDF: lambda: RapiPDFProvider(
                openapi_url=self.openapi_url,
                api_title=self.api_title,
                success=self.success,
                error=self.error,
                debug=self.debug
            ),
        }
        self.disp.log_debug("Initialised")

    def _initialize_providers(self) -> None:
        """Initialize the enabled documentation providers.

        Creates instances of the selected providers and stores them in the providers dictionary.
        """
        func_title = "_initialize_providers"
        self.disp.log_debug(
            "Initializing documentation providers...", func_title)

        for provider in self.enabled_providers:
            factory = self.provider_factories.get(provider)
            if factory:
                self.providers[provider.value] = factory()
                self.disp.log_debug(
                    f"Initialized {provider.value} provider", func_title
                )

        self.disp.log_debug(
            f"Initialized {len(self.providers)} documentation provider(s)", func_title
        )

    def _get_custom_openapi_schema(self, app: Optional["FastAPI"]) -> Dict[str, Any]:
        """Generate custom OpenAPI schema with metadata.

        Args:
            app (Optional[FastAPI]): The FastAPI application instance.

        Returns:
            Dict[str, Any]: The custom OpenAPI schema.
        """
        func_title = "_get_custom_openapi_schema"

        if app is None:
            self.disp.log_error("FastAPI app is None", func_title)
            return {}

        if app.openapi_schema:
            self.disp.log_debug("Returning cached OpenAPI schema", func_title)
            return app.openapi_schema

        self.disp.log_debug("Generating custom OpenAPI schema", func_title)

        openapi_schema = get_openapi(
            title=self.api_title,
            version=self.api_version,
            description=self.api_description,
            routes=app.routes,
        )

        openapi_schema["info"]["x-logo"] = {
            "url": "/static/logo.png"
        }

        if DOCS_CONST.ENABLE_OAUTH2_DOCS and DOCS_CONST.OAUTH2_AUTHORIZATION_URL and DOCS_CONST.OAUTH2_TOKEN_URL:
            openapi_schema["components"] = openapi_schema.get("components", {})
            openapi_schema["components"]["securitySchemes"] = {
                "OAuth2": {
                    "type": "oauth2",
                    "flows": {
                        "authorizationCode": {
                            "authorizationUrl": DOCS_CONST.OAUTH2_AUTHORIZATION_URL,
                            "tokenUrl": DOCS_CONST.OAUTH2_TOKEN_URL,
                            "scopes": DOCS_CONST.OAUTH2_SCOPES
                        }
                    }
                },
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
            self.disp.log_debug(
                "Added OAuth2 security scheme to OpenAPI schema", func_title)

        app.openapi_schema = openapi_schema
        self.disp.log_debug("OpenAPI schema generated and cached", func_title)
        return app.openapi_schema

    def _custom_openapi_wrapper(self, request: Request) -> Response:
        """Wrapper for custom OpenAPI endpoint.

        Args:
            request (Request): The incoming request.

        Returns:
            Response: JSON response containing the OpenAPI schema.
        """
        func_title = "_custom_openapi_wrapper"
        self.disp.log_debug("Serving OpenAPI schema", func_title)

        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request)
        self.disp.log_debug(f"token = {token}", func_title)

        app = self.runtime_control_initialised.app
        openapi_schema = self._get_custom_openapi_schema(app)

        return HCI.success(content=openapi_schema, content_type=HttpDataTypes.JSON)

    def _oauth2_redirect_handler(self, request: Request) -> Response:
        """Handle OAuth2 redirect for Swagger UI authentication.

        This endpoint is called by OAuth2 providers after user authentication.
        It extracts the authorization code/token and passes it back to Swagger UI.

        Args:
            request (Request): The incoming request with OAuth2 callback parameters.

        Returns:
            Response: HTML response that passes credentials back to Swagger UI.
        """
        func_title = "_oauth2_redirect_handler"
        self.disp.log_debug("Handling OAuth2 redirect", func_title)

        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request)
        self.disp.log_debug(f"token = {token}", func_title)

        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OAuth2 Redirect</title>
</head>
<body>
    <script>
        // This script passes the OAuth2 response back to Swagger UI
        'use strict';
        function run() {
            var oauth2 = window.opener.swaggerUIRedirectOauth2;
            var sentState = oauth2.state;
            var redirectUrl = oauth2.redirectUrl;
            var isValid, qp, arr;

            if (/code|token|error/.test(window.location.hash)) {
                qp = window.location.hash.substring(1);
            } else {
                qp = location.search.substring(1);
            }

            arr = qp.split("&");
            arr.forEach(function (v, i, _arr) {
                var _arr2 = v.split("=");
                if (_arr2[0] === "state") {
                    isValid = _arr2[1] === sentState;
                }
            });

            if (oauth2.auth.schema.get("flow") === "accessCode" && !oauth2.auth.code) {
                if (!isValid) {
                    oauth2.errCb({
                        authId: oauth2.auth.name,
                        source: "auth",
                        level: "warning",
                        message: "Authorization may be unsafe, passed state was changed in server Passed state wasn't returned from auth server"
                    });
                }

                if (qp) {
                    arr = qp.split("&");
                    arr.forEach(function (v, i, _arr) {
                        var _arr3 = v.split("=");
                        if (_arr3[0] === "code") {
                            oauth2.auth.code = _arr3[1];
                        } else if (_arr3[0] === "error") {
                            oauth2.auth.error = _arr3[1];
                        }
                    });
                }
            }

            if (oauth2.auth.code || oauth2.auth.error) {
                window.close();
            }
        }

        window.addEventListener('DOMContentLoaded', function () {
            run();
        });
    </script>
</body>
</html>
"""
        return HCI.success(content=html_content, content_type=HttpDataTypes.HTML)

    def _create_provider_handler(self, provider_instance: Any, provider_name: str) -> Any:
        """Create an async handler function for a documentation provider.

        Args:
            provider_instance (Any): The provider instance to create a handler for.
            provider_name (str): Name of the provider for unique operation ID.

        Returns:
            Any: An async handler function with unique name.
        """
        async def handler(request: Request) -> Response:
            return await provider_instance.get_documentation(request)

        # Give each handler a unique name to avoid duplicate Operation IDs
        handler.__name__ = f"{provider_name}_documentation_handler"

        return handler

    def inject(self, providers: Optional[tuple[DOCS_CONST.DocumentationProvider, ...]] = None) -> int:
        """Inject documentation endpoints into the FastAPI application.

        Registers all enabled documentation providers and the OpenAPI schema endpoint.

        Args:
            providers (Optional[tuple], optional): Tuple of documentation providers to enable.
                If None, uses the providers set in the constructor. Defaults to None.

        Returns:
            int: Success or error code.
        """
        func_title = "inject"
        self.disp.log_debug("Injecting documentation endpoints...", func_title)

        if providers is not None:
            self.enabled_providers = providers
            self.providers = {}

        # Initialize providers here (not in __init__) to ensure FastAPI app exists
        if not self.providers:
            self._initialize_providers()
            self.disp.log_debug(
                "Initialized providers during inject()", func_title
            )

        result = self.path_manager_initialised.add_path_if_not_exists(
            path=self.openapi_url,
            endpoint=self._custom_openapi_wrapper,
            method="GET"
        )
        if result != self.success:
            self.disp.log_error(
                f"Failed to register OpenAPI schema endpoint at {self.openapi_url}",
                func_title
            )
            return self.error

        self.disp.log_debug(
            f"Registered OpenAPI schema endpoint: {self.openapi_url}", func_title
        )

        if DOCS_CONST.ENABLE_OAUTH2_DOCS:
            result = self.path_manager_initialised.add_path_if_not_exists(
                path=DOCS_CONST.OAUTH2_REDIRECT_URL,
                endpoint=self._oauth2_redirect_handler,
                method="GET"
            )
            if result != self.success:
                self.disp.log_error(
                    f"Failed to register OAuth2 redirect endpoint at {DOCS_CONST.OAUTH2_REDIRECT_URL}",
                    func_title
                )
                return self.error
            self.disp.log_debug(
                f"Registered OAuth2 redirect endpoint: {DOCS_CONST.OAUTH2_REDIRECT_URL}", func_title)

        for provider_name, provider_instance in self.providers.items():
            if provider_name in [DOCS_CONST.DocumentationProvider.SWAGGER.value, DOCS_CONST.DocumentationProvider.REDOC.value]:
                inject_result = provider_instance.inject()
                if inject_result != self.success:
                    self.disp.log_error(
                        f"Failed to inject {provider_name} endpoints",
                        func_title
                    )
                    return self.error
                self.disp.log_debug(
                    f"Injected {provider_name} endpoints via inject() method", func_title
                )
            elif provider_name in [DOCS_CONST.DocumentationProvider.RAPIPDF.value]:
                doc_url = provider_instance.get_url()

                handler_func = self._create_provider_handler(
                    provider_instance, provider_name)

                result = self.path_manager_initialised.add_path_if_not_exists(
                    path=doc_url,
                    endpoint=handler_func,
                    method="GET"
                )
                if result != self.success:
                    self.disp.log_error(
                        f"Failed to register {provider_name} endpoint at {doc_url}",
                        func_title
                    )
                    return self.error
                result = provider_instance.inject_js_ressource(
                    self.path_manager_initialised
                )
                if result != self.success:
                    self.disp.log_error(
                        f"Failed to register {provider_name} child javascript ressources"
                    )
                    return self.error
                self.disp.log_debug(
                    f"Registered {provider_name} endpoint: {doc_url}", func_title
                )
            else:
                doc_url = provider_instance.get_url()

                handler_func = self._create_provider_handler(
                    provider_instance, provider_name)

                result = self.path_manager_initialised.add_path_if_not_exists(
                    path=doc_url,
                    endpoint=handler_func,
                    method="GET"
                )
                if result != self.success:
                    self.disp.log_error(
                        f"Failed to register {provider_name} endpoint at {doc_url}",
                        func_title
                    )
                    return self.error

                self.disp.log_debug(
                    f"Registered {provider_name} endpoint: {doc_url}", func_title
                )

        self.disp.log_debug(
            f"Successfully injected {len(self.providers)} documentation provider(s)", func_title
        )
        return self.success
