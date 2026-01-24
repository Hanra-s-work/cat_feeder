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
# FILE: explorer_provider.py
# CREATION DATE: 26-11-2025
# LAST Modified: 14:44:44 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: OpenAPI Explorer documentation provider implementation.
# // AR
# +==== END CatFeeder =================+
"""
from fastapi import Request, Response
from display_tty import Disp, initialise_logger
from . import explorer_constants as EXPLORER_CONST
from ...http_codes import HCI, HttpDataTypes
from ...core.runtime_manager import RuntimeManager, RI
from ...server_header import ServerHeaders
from ...boilerplates import BoilerplateResponses, BoilerplateIncoming


class OpenAPIExplorerProvider:
    """OpenAPI Explorer documentation provider.

    Provides interactive API explorer with request/response console.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, openapi_url: str, api_title: str, debug: bool = False) -> None:
        """Initialize OpenAPI Explorer provider.

        Args:
            openapi_url (str): URL to OpenAPI JSON schema.
            api_title (str): Title of the API.
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising OpenAPI Explorer provider...")

        self.openapi_url = openapi_url
        self.api_title = api_title
        self.runtime_manager: RuntimeManager = RI
        self.server_headers_initialised: ServerHeaders = self.runtime_manager.get(
            ServerHeaders)
        self.boilerplate_responses_initialised: BoilerplateResponses = self.runtime_manager.get(
            BoilerplateResponses)
        self.boilerplate_incoming_initialised: BoilerplateIncoming = self.runtime_manager.get(
            BoilerplateIncoming)

        self.disp.log_debug("OpenAPI Explorer provider initialised")

    async def get_documentation(self, request: Request) -> Response:
        """Serve OpenAPI Explorer documentation page.

        Args:
            request (Request): The incoming request.

        Returns:
            Response: HTML response with OpenAPI Explorer interface.
        """
        func_title = "get_documentation"
        self.disp.log_debug(
            "Serving OpenAPI Explorer documentation", func_title)

        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request)
        self.disp.log_debug(f"token = {token}", func_title)

        options_js = ""
        for key, value in EXPLORER_CONST.EXPLORER_OPTIONS.items():
            if isinstance(value, bool):
                if value:
                    js_value = "true"
                else:
                    js_value = "false"
            elif isinstance(value, str):
                js_value = f'"{value}"'
            else:
                js_value = str(value)
            options_js = options_js + f"                {key}: {js_value},\n"

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.api_title} - OpenAPI Explorer</title>
    <link rel="stylesheet" href="{EXPLORER_CONST.EXPLORER_CDN_CSS}">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
        #explorer {{
            width: 100%;
            height: 100vh;
        }}
    </style>
</head>
<body>
    <div id="explorer"></div>
    <script src="{EXPLORER_CONST.EXPLORER_CDN_JS}"></script>
    <script src="{EXPLORER_CONST.EXPLORER_CDN_PRESET}"></script>
    <script>
        window.onload = function() {{
            window.ui = SwaggerUIBundle({{
                url: '{self.openapi_url}',
                dom_id: '#explorer',
{options_js}                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ]
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
        return EXPLORER_CONST.EXPLORER_URL
