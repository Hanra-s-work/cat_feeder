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
# FILE: rapidoc_provider.py
# CREATION DATE: 26-11-2025
# LAST Modified: 14:44:59 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: RapiDoc documentation provider implementation.
# // AR
# +==== END CatFeeder =================+
"""
from fastapi import Request, Response
from display_tty import Disp, initialise_logger
from . import rapidoc_constants as RAPIDOC_CONST
from ...http_codes import HCI, HttpDataTypes
from ...core.runtime_manager import RuntimeManager, RI
from ...server_header import ServerHeaders
from ...boilerplates import BoilerplateResponses, BoilerplateIncoming


class RapiDocProvider:
    """RapiDoc documentation provider.

    Provides RapiDoc API documentation interface with customizable layouts.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, openapi_url: str, api_title: str, debug: bool = False) -> None:
        """Initialize RapiDoc provider.

        Args:
            openapi_url (str): URL to OpenAPI JSON schema.
            api_title (str): Title of the API.
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising RapiDoc provider...")

        self.openapi_url = openapi_url
        self.api_title = api_title
        self.runtime_manager: RuntimeManager = RI
        self.server_headers_initialised: ServerHeaders = self.runtime_manager.get(
            ServerHeaders)
        self.boilerplate_responses_initialised: BoilerplateResponses = self.runtime_manager.get(
            BoilerplateResponses)
        self.boilerplate_incoming_initialised: BoilerplateIncoming = self.runtime_manager.get(
            BoilerplateIncoming)

        self.disp.log_debug("RapiDoc provider initialised")

    async def get_documentation(self, request: Request) -> Response:
        """Serve RapiDoc documentation page.

        Args:
            request (Request): The incoming request.

        Returns:
            Response: HTML response with RapiDoc interface.
        """
        func_title = "get_documentation"
        self.disp.log_debug("Serving RapiDoc documentation", func_title)

        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request)
        self.disp.log_debug(f"token = {token}", func_title)

        options_str = " ".join(
            [f'{key}="{value}"' for key, value in RAPIDOC_CONST.RAPIDOC_OPTIONS.items()])

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{self.api_title} - RapiDoc</title>
    <script type="module" src="{RAPIDOC_CONST.RAPIDOC_CDN_URL}"></script>
</head>
<body>
    <rapi-doc
        spec-url="{self.openapi_url}"
        render-style="{RAPIDOC_CONST.RAPIDOC_RENDER_STYLE}"
        layout="{RAPIDOC_CONST.RAPIDOC_LAYOUT}"
        theme="{RAPIDOC_CONST.RAPIDOC_THEME}"
        schema-style="{RAPIDOC_CONST.RAPIDOC_SCHEMA_STYLE}"
        {options_str}
    ></rapi-doc>
</body>
</html>
"""
        return HCI.success(content=html_content, content_type=HttpDataTypes.HTML)

    def get_url(self) -> str:
        """Get the URL path for this documentation provider.

        Returns:
            str: The URL path.
        """
        return RAPIDOC_CONST.RAPIDOC_URL
