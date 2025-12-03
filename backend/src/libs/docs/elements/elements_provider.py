""" 
# +==== BEGIN AsperBackend =================+
# LOGO: 
# ..........####...####..........
# ......###.....#.#########......
# ....##........#.###########....
# ...#..........#.############...
# ...#..........#.#####.######...
# ..#.....##....#.###..#...####..
# .#.....#.##...#.##..##########.
# #.....##########....##...######
# #.....#...##..#.##..####.######
# .#...##....##.#.##..###..#####.
# ..#.##......#.#.####...######..
# ..#...........#.#############..
# ..#...........#.#############..
# ...##.........#.############...
# ......#.......#.#########......
# .......#......#.########.......
# .........#####...#####.........
# /STOP
# PROJECT: AsperBackend
# FILE: elements_provider.py
# CREATION DATE: 26-11-2025
# LAST Modified: 9:50:38 27-11-2025
# DESCRIPTION: 
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Asperguide
# PURPOSE: Stoplight Elements documentation provider implementation.
# // AR
# +==== END AsperBackend =================+
"""
from fastapi import Request, Response
from display_tty import Disp, initialise_logger
from . import elements_constants as ELEMENTS_CONST
from ...http_codes import HCI, HttpDataTypes
from ...core.runtime_manager import RuntimeManager, RI
from ...server_header import ServerHeaders
from ...boilerplates import BoilerplateResponses, BoilerplateIncoming


class StoplightElementsProvider:
    """Stoplight Elements documentation provider.

    Provides beautiful API documentation using Stoplight Elements web components.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, openapi_url: str, api_title: str, debug: bool = False) -> None:
        """Initialize Stoplight Elements provider.

        Args:
            openapi_url (str): URL to OpenAPI JSON schema.
            api_title (str): Title of the API.
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising Stoplight Elements provider...")

        self.openapi_url = openapi_url
        self.api_title = api_title
        self.runtime_manager: RuntimeManager = RI
        self.server_headers_initialised: ServerHeaders = self.runtime_manager.get(
            ServerHeaders)
        self.boilerplate_responses_initialised: BoilerplateResponses = self.runtime_manager.get(
            BoilerplateResponses)
        self.boilerplate_incoming_initialised: BoilerplateIncoming = self.runtime_manager.get(
            BoilerplateIncoming)

        self.disp.log_debug("Stoplight Elements provider initialised")

    async def get_documentation(self, request: Request) -> Response:
        """Serve Stoplight Elements documentation page.

        Args:
            request (Request): The incoming request.

        Returns:
            Response: HTML response with Stoplight Elements interface.
        """
        func_title = "get_documentation"
        self.disp.log_debug(
            "Serving Stoplight Elements documentation", func_title)

        token = self.boilerplate_incoming_initialised.get_token_if_present(
            request)
        self.disp.log_debug(f"token = {token}", func_title)

        attributes_str = ""
        for key, value in ELEMENTS_CONST.ELEMENTS_OPTIONS.items():
            attr_name = key
            if isinstance(value, bool):
                if value:
                    attr_value = "true"
                else:
                    attr_value = "false"
            else:
                attr_value = str(value)
            attributes_str = attributes_str + \
                f'        {attr_name}="{attr_value}"\n'

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>{self.api_title} - Stoplight Elements</title>
    <link rel="stylesheet" href="{ELEMENTS_CONST.ELEMENTS_CDN_CSS}">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <elements-api
        apiDescriptionUrl="{self.openapi_url}"
        router="{ELEMENTS_CONST.ELEMENTS_ROUTER}"
        layout="{ELEMENTS_CONST.ELEMENTS_LAYOUT}"
{attributes_str}    />
    <script src="{ELEMENTS_CONST.ELEMENTS_CDN_JS}"></script>
</body>
</html>
"""
        return HCI.success(content=html_content, content_type=HttpDataTypes.HTML)

    def get_url(self) -> str:
        """Get the URL path for this documentation provider.

        Returns:
            str: The URL path.
        """
        return ELEMENTS_CONST.ELEMENTS_URL
