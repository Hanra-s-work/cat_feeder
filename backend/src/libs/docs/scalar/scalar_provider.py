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
# FILE: scalar_provider.py
# CREATION DATE: 26-11-2025
# LAST Modified: 9:52:25 27-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Scalar documentation provider implementation.
# // AR
# +==== END CatFeeder =================+
"""
import json
from display_tty import Disp, initialise_logger
from fastapi import Request, Response
from . import scalar_constants as SCALAR_CONST
from ...http_codes import HCI, HttpDataTypes
from ...core.runtime_manager import RuntimeManager, RI
from ...server_header import ServerHeaders
from ...boilerplates import BoilerplateResponses, BoilerplateIncoming


class ScalarProvider:
    """Scalar documentation provider.

    Provides modern Scalar API documentation interface with beautiful design.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, openapi_url: str, api_title: str, debug: bool = False) -> None:
        """Initialize Scalar provider.

        Args:
            openapi_url (str): URL to OpenAPI JSON schema.
            api_title (str): Title of the API.
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising Scalar provider...")

        self.openapi_url = openapi_url
        self.api_title = api_title
        self.runtime_manager: RuntimeManager = RI
        self.server_headers_initialised: ServerHeaders = self.runtime_manager.get(
            ServerHeaders)
        self.boilerplate_responses_initialised: BoilerplateResponses = self.runtime_manager.get(
            BoilerplateResponses)
        self.boilerplate_incoming_initialised: BoilerplateIncoming = self.runtime_manager.get(
            BoilerplateIncoming)

        self.disp.log_debug("Scalar provider initialised")

    async def get_documentation(self, request: Request) -> Response:
        """Serve Scalar documentation page.

        Args:
            request (Request): The incoming request.

        Returns:
            Response: HTML response with Scalar interface.
        """
        func_title = "get_documentation"
        self.disp.log_debug("Serving Scalar documentation", func_title)

        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request)
        self.disp.log_debug(f"token = {token}", func_title)

        config = {
            "spec": {"url": self.openapi_url},
            "theme": SCALAR_CONST.SCALAR_THEME,
            "layout": SCALAR_CONST.SCALAR_LAYOUT,
            **SCALAR_CONST.SCALAR_OPTIONS
        }

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{self.api_title} - Scalar</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <script id="api-reference" data-url="{self.openapi_url}"></script>
    <script>
        var configuration = {json.dumps(config)};
        document.getElementById('api-reference').dataset.configuration = JSON.stringify(configuration);
    </script>
    <script src="{SCALAR_CONST.SCALAR_CDN_URL}"></script>
</body>
</html>
"""
        return HCI.success(content=html_content, content_type=HttpDataTypes.HTML)

    def get_url(self) -> str:
        """Get the URL path for this documentation provider.

        Returns:
            str: The URL path.
        """
        return SCALAR_CONST.SCALAR_URL
