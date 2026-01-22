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
# FILE: rapipdf_provider.py
# CREATION DATE: 26-11-2025
# LAST Modified: 14:45:19 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: RapiPDF documentation provider implementation.
# // AR
# +==== END CatFeeder =================+
"""
import os
from typing import TYPE_CHECKING
from display_tty import Disp, initialise_logger
from fastapi import Request, Response
from . import rapipdf_constants as RAPIPDF_CONST
from ...http_codes import HCI, HttpDataTypes
from ...core.runtime_manager import RuntimeManager, RI
from ...server_header import ServerHeaders
from ...boilerplates import BoilerplateResponses, BoilerplateIncoming

if TYPE_CHECKING:
    from ...path_manager.path_manager import PathManager


class RapiPDFProvider:
    """RapiPDF documentation provider.

    Provides PDF generation interface for OpenAPI documentation.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, openapi_url: str, api_title: str, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """Initialize RapiPDF provider.

        Args:
            openapi_url (str): URL to OpenAPI JSON schema.
            api_title (str): Title of the API.
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising RapiPDF provider...")

        self.success = success
        self.error = error
        self.openapi_url = openapi_url
        self.api_title = api_title
        self.runtime_manager: RuntimeManager = RI
        self.server_headers_initialised: ServerHeaders = self.runtime_manager.get(
            ServerHeaders)
        self.boilerplate_responses_initialised: BoilerplateResponses = self.runtime_manager.get(
            BoilerplateResponses)
        self.boilerplate_incoming_initialised: BoilerplateIncoming = self.runtime_manager.get(
            BoilerplateIncoming)

        self.disp.log_debug("RapiPDF provider initialised")

    async def get_documentation(self, request: Request) -> Response:
        """Serve RapiPDF documentation page.

        Args:
            request (Request): The incoming request.

        Returns:
            Response: HTML response with RapiPDF interface.
        """
        func_title = "get_documentation"
        self.disp.log_debug("Serving RapiPDF documentation", func_title)

        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request)
        self.disp.log_debug(f"token = {token}", func_title)

        config_options = {}
        for key, value in RAPIPDF_CONST.RAPIPDF_OPTIONS.items():
            if isinstance(value, bool):
                if value:
                    config_options[key] = "true"
                else:
                    config_options[key] = "false"
            else:
                config_options[key] = value

        pdf_primary = config_options.get("pdf-primary-color", "#4A90E2")
        pdf_alternate = config_options.get("pdf-alternate-color", "#F5F5F5")
        pdf_title = config_options.get("pdf-title", "API Documentation")
        pdf_footer = config_options.get("pdf-footer-text", "")
        include_api_list = config_options.get("include-api-list", "true")
        include_api_details = config_options.get("include-api-details", "true")
        include_security = config_options.get("include-security", "true")

        if RAPIPDF_CONST.RAPIPDF_STYLE == "dark":
            bg_color = "#1a1a1a"
            text_color = "#ffffff"
            status_text_color = "#000000"
        else:
            bg_color = "#ffffff"
            text_color = "#000000"
            status_text_color = "#333333"

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.api_title} - RapiPDF</title>
    <script type="module" src="{RAPIPDF_CONST.RAPIPDF_CDN_JS_ENDPOINT}"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: {bg_color};
            color: {text_color};
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            margin-bottom: 10px;
        }}
        p {{
            margin-bottom: 30px;
            color: {text_color};
        }}
        rapi-pdf {{
            --primary-color: {pdf_primary};
            --input-bg: {bg_color};
            --fg: {text_color};
            --primary-text: white;
            --font-size: 14px;
            width: 100%;
            max-width: 500px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{self.api_title} - PDF Documentation</h1>
        <p>Generate a comprehensive PDF document of the API specification.</p>

        <rapi-pdf
            spec-url="{self.openapi_url}"
            style="{RAPIPDF_CONST.RAPIPDF_STYLE}"
            pdf-title="{pdf_title}"
            pdf-footer-text="{pdf_footer}"
            pdf-primary-color="{pdf_primary}"
            pdf-alternate-color="{pdf_alternate}"
            include-api-list="{str(include_api_list).lower()}"
            include-api-details="{str(include_api_details).lower()}"
            include-security="{str(include_security).lower()}"
            button-label="{RAPIPDF_CONST.RAPIPDF_BUTTON_LABEL}"
            hide-input="false"
        ></rapi-pdf>
    </div>
</body>
</html>
"""
        return HCI.success(content=html_content, content_type=HttpDataTypes.HTML)

    async def get_rapipdf_cdn_js_ressource(self, request: Request) -> Response:
        """Serve the RapiPDF JavaScript library file.

        Args:
            request (Request): The incoming request.

        Returns:
            Response: JavaScript file response or error response if file not found.
        """
        file = RAPIPDF_CONST.RAPIPDF_CDN_JS
        if not os.path.isfile(file):
            error_msg: str = f"Filepath: {file} does not exist or is not a file"
            self.disp.log_error(error_msg)
            return HCI.not_found(error_msg, content_type=HttpDataTypes.TEXT, headers=self.server_headers_initialised.for_text())
        return HCI.success(file, content_type=HttpDataTypes.JAVASCRIPT, headers=self.server_headers_initialised.for_javascript())

    def inject_js_ressource(self, path_handler: "PathManager") -> int:
        """Register the JavaScript resource endpoint with the path manager.

        Args:
            path_handler (PathManager): The path manager instance to register the endpoint with.

        Returns:
            int: Success or error code from the path registration.
        """
        return path_handler.add_path(
            RAPIPDF_CONST.RAPIPDF_CDN_JS_ENDPOINT,
            self.get_rapipdf_cdn_js_ressource,
            "GET"
        )

    def get_url(self) -> str:
        """Get the URL path for this documentation provider.

        Returns:
            str: The URL path.
        """
        return RAPIPDF_CONST.RAPIPDF_URL
