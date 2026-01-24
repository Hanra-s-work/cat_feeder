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
# FILE: editor_provider.py
# CREATION DATE: 26-11-2025
# LAST Modified: 14:44:9 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Swagger Editor documentation provider implementation.
# // AR
# +==== END CatFeeder =================+
"""
from fastapi import Request, Response
from display_tty import Disp, initialise_logger
from . import editor_constants as EDITOR_CONST
from ...http_codes import HCI, HttpDataTypes
from ...core.runtime_manager import RuntimeManager, RI
from ...server_header import ServerHeaders
from ...boilerplates import BoilerplateResponses, BoilerplateIncoming


class SwaggerEditorProvider:
    """Swagger Editor documentation provider.

    Provides interactive Swagger Editor for viewing and editing OpenAPI specs.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, openapi_url: str, api_title: str, debug: bool = False) -> None:
        """Initialize Swagger Editor provider.

        Args:
            openapi_url (str): URL to OpenAPI JSON schema.
            api_title (str): Title of the API.
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising Swagger Editor provider...")

        self.openapi_url = openapi_url
        self.api_title = api_title
        self.runtime_manager: RuntimeManager = RI
        self.server_headers_initialised: ServerHeaders = self.runtime_manager.get(
            ServerHeaders)
        self.boilerplate_responses_initialised: BoilerplateResponses = self.runtime_manager.get(
            BoilerplateResponses)
        self.boilerplate_incoming_initialised: BoilerplateIncoming = self.runtime_manager.get(
            BoilerplateIncoming)

        self.disp.log_debug("Swagger Editor provider initialised")

    async def get_documentation(self, request: Request) -> Response:
        """Serve Swagger Editor documentation page.

        Args:
            request (Request): The incoming request.

        Returns:
            Response: HTML response with Swagger Editor interface.
        """
        func_title = "get_documentation"
        self.disp.log_debug("Serving Swagger Editor documentation", func_title)

        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request)
        self.disp.log_debug(f"token = {token}", func_title)

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.api_title} - API Editor</title>
    <link rel="stylesheet" href="{EDITOR_CONST.EDITOR_CDN_CSS}">
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
        }}
        #swagger-ui {{
            height: 100%;
            overflow-y: auto;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="{EDITOR_CONST.EDITOR_CDN_JS}"></script>
    <script src="{EDITOR_CONST.EDITOR_CDN_PRESET}"></script>
    <script>
        window.onload = function() {{
            if (typeof SwaggerUIBundle === 'undefined') {{
                document.getElementById('swagger-ui').innerHTML =
                    '<div style="padding: 20px; color: red;">Editor scripts failed to load. Please check your internet connection.</div>';
                return;
            }}

            window.ui = SwaggerUIBundle({{
                url: '{self.openapi_url}',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                deepLinking: {str(EDITOR_CONST.EDITOR_OPTIONS.get('deepLinking', True)).lower()},
                displayOperationId: {str(EDITOR_CONST.EDITOR_OPTIONS.get('displayOperationId', True)).lower()},
                displayRequestDuration: {str(EDITOR_CONST.EDITOR_OPTIONS.get('displayRequestDuration', True)).lower()},
                filter: {str(EDITOR_CONST.EDITOR_OPTIONS.get('filter', True)).lower()},
                showExtensions: {str(EDITOR_CONST.EDITOR_OPTIONS.get('showExtensions', True)).lower()},
                showCommonExtensions: {str(EDITOR_CONST.EDITOR_OPTIONS.get('showCommonExtensions', True)).lower()},
                tryItOutEnabled: {str(EDITOR_CONST.EDITOR_OPTIONS.get('tryItOutEnabled', True)).lower()},
                layout: "{EDITOR_CONST.EDITOR_OPTIONS.get('layout', 'BaseLayout')}"
            }});
        }};
    </script>
</body>
</html>
"""
        return HCI.success(content=html_content, content_type=HttpDataTypes.HTML)

    def get_url(self) -> str:
        """Get the URL path for this documentation provider.

        Returns:
            str: The URL path.
        """
        return EDITOR_CONST.EDITOR_URL
