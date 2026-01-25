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
# FILE: front_end.py
# CREATION DATE: 24-01-2026
# LAST Modified: 5:34:27 25-01-2026
# DESCRIPTION:
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the python file in charge of loading and providing the ressources required for loading a barebones front-end.
# // AR
# +==== END CatFeeder =================+
"""

import os
from typing import TYPE_CHECKING, Dict, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from pathlib import Path
from fastapi import Response
from display_tty import Disp, initialise_logger

from ...utils import CONST
from ...core import RuntimeManager, RI
from ...http_codes import HCI, HttpDataTypes
from ...path_manager import PathManager, decorators

if TYPE_CHECKING:
    from ...sql import SQL
    from ...server_header import ServerHeaders
    from ...boilerplates import BoilerplateIncoming, BoilerplateResponses, BoilerplateNonHTTP

CACHE_LIFETIME: timedelta = timedelta(seconds=CONST.FRONT_END_ASSETS_REFRESH)


@dataclass
class CacheEntry:
    """The cache node class
    """
    data: str = ""
    timestamp: datetime = datetime.now() + CACHE_LIFETIME
    source: str = ""


class Pages(Enum):
    DEFAULT = "default"
    LOGIN = "login"
    DASHBOARD = "dashboard"
    LOGOUT = "logout"


class FrontEndManager:
    """
    Front-end manager for serving static assets and HTML pages.
    """

    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, error: int = 84, success: int = 0, debug: bool = False) -> None:
        """_summary_
        """
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self.error: int = error
        self.success: int = success
        self.debug: bool = debug
        self.runtime_manager: RuntimeManager = RI
        # ------------------------ General information -------------------------
        self.author: str = "Henry Letellier"
        self.year: str = str(datetime.now().year)
        # ------------------------- Endpoint prefixes --------------------------
        self.front_end: str = "/front-end"
        self.front_end_login: str = f"{self.front_end}/"
        self.front_end_dashboard: str = f"{self.front_end}/dashboard"
        self.front_end_logout: str = f"{self.front_end}/logout"
        self.front_end_assets: str = f"{self.front_end}/assets"
        # ====================== JS asset files
        self.front_end_assets_js: str = f"{self.front_end_assets}/js"
        self.front_end_assets_js_modules: str = f"{self.front_end_assets_js}/modules"
        self.front_end_assets_js_theme: str = f"{self.front_end_assets_js}/theme"
        self.front_end_assets_js_module_cookies: str = f"{self.front_end_assets_js_modules}/cookies.mjs"
        self.front_end_assets_js_module_indexdb: str = f"{self.front_end_assets_js_modules}/indexeddb_manager.mjs"
        self.front_end_assets_js_module_querier: str = f"{self.front_end_assets_js_modules}/querier.mjs"
        self.front_end_assets_js_module_general: str = f"{self.front_end_assets_js_modules}/general.mjs"
        self.front_end_assets_js_theme_pico: str = f"{self.front_end_assets_js_theme}/minimal-theme-switcher.min.js"
        self.front_end_assets_js_dashboard: str = f"{self.front_end_assets_js}/dashboard.js"
        self.front_end_assets_js_login: str = f"{self.front_end_assets_js}/login.js"
        self.front_end_assets_js_logout: str = f"{self.front_end_assets_js}/logout.js"
        # ====================== CSS asset files
        self.front_end_assets_css: str = f"{self.front_end_assets}/css"
        self.front_end_assets_css_pico: str = f"{self.front_end_assets_css}/pico.min.css"
        self.front_end_assets_css_custom: str = f"{self.front_end_assets_css}/custom.css"
        self.front_end_assets_css_emoji_font: str = f"{self.front_end_assets_css}/noto-emoji.css"
        # ====================== CSS asset files
        self.front_end_assets_css_emoji_font_static: str = f"{self.front_end_assets_css}/static"
        self.front_end_assets_css_emoji_font_static_regular: str = f"{self.front_end_assets_css_emoji_font_static}/NotoEmoji-Regular.ttf"
        self.front_end_assets_css_emoji_font_static_light: str = f"{self.front_end_assets_css_emoji_font_static}/NotoEmoji-Light.ttf"
        self.front_end_assets_css_emoji_font_static_medium: str = f"{self.front_end_assets_css_emoji_font_static}/NotoEmoji-Medium.ttf"
        self.front_end_assets_css_emoji_font_static_semi_bold: str = f"{self.front_end_assets_css_emoji_font_static}/NotoEmoji-SemiBold.ttf"
        self.front_end_assets_css_emoji_font_static_bold: str = f"{self.front_end_assets_css_emoji_font_static}/NotoEmoji-Bold.ttf"
        # ====================== Image asset files
        self.front_end_assets_images: str = f"{self.front_end_assets}/images"
        self.front_end_assets_images_favicon: str = f"{self.front_end_assets_images}/favicon.ico"
        self.front_end_assets_image_favicon_png: str = f"{self.front_end_assets_images}/favicon.png"
        self.front_end_assets_images_logos: str = f"{self.front_end_assets_images}/logos"
        # ====================== HTML asset files
        self.front_end_assets_html_login: str = f"{self.front_end_assets}/login.html"
        self.front_end_assets_html_logout: str = f"{self.front_end_assets}/logout.html"
        self.front_end_assets_html_dashboard: str = f"{self.front_end_assets}/dashboard.html"
        # ---------------------------- Source files ----------------------------
        # ======================= CSS Files
        self.source_css_pico: str = str(
            CONST.STYLE_DIRECTORY / "pico.classless.min.css"
        )
        self.source_css_custom: str = str(
            CONST.STYLE_DIRECTORY / "style.css"
        )
        self.source_css_emoji_font: str = str(
            CONST.STYLE_DIRECTORY / "Noto_Emoji" / "noto-emoji.css"
        )
        # ======================= Font Files
        self.source_css_emoji_font_regular: str = str(
            CONST.STYLE_DIRECTORY / "Noto_Emoji" / "static" / "NotoEmoji-Regular.ttf"
        )
        self.source_css_emoji_font_light: str = str(
            CONST.STYLE_DIRECTORY / "Noto_Emoji" / "static" / "NotoEmoji-Light.ttf"
        )
        self.source_css_emoji_font_medium: str = str(
            CONST.STYLE_DIRECTORY / "Noto_Emoji" / "static" / "NotoEmoji-Medium.ttf"
        )
        self.source_css_emoji_font_semi_bold: str = str(
            CONST.STYLE_DIRECTORY / "Noto_Emoji" / "static" / "NotoEmoji-SemiBold.ttf"
        )
        self.source_css_emoji_font_bold: str = str(
            CONST.STYLE_DIRECTORY / "Noto_Emoji" / "static" / "NotoEmoji-Bold.ttf"
        )
        # ======================= Javascript Modules
        self.source_js_module: Path = CONST.JS_DIRECTORY / "modules"
        self.source_js_theme: Path = CONST.JS_DIRECTORY / "theme"
        self.source_js_module_cookies: str = str(
            self.source_js_module / "cookies.mjs"
        )
        self.source_js_module_indexdb: str = str(
            self.source_js_module / "indexeddb_manager.mjs"
        )
        self.source_js_module_querier: str = str(
            self.source_js_module / "querier.mjs"
        )
        self.source_js_module_general: str = str(
            self.source_js_module / "general.mjs"
        )
        # ======================= Javascript Theme
        self.source_js_theme_pico: str = str(
            self.source_js_theme / "minimal-theme-switcher.min.js"
        )
        # ======================= Javascript Files
        self.source_js_dashboard: str = str(
            CONST.JS_DIRECTORY / "dashboard.js"
        )
        self.source_js_login: str = str(
            CONST.JS_DIRECTORY / "login.js"
        )
        self.source_js_logout: str = str(
            CONST.JS_DIRECTORY / "logout.js"
        )
        # ======================= Html Files
        self.source_html_login: str = str(
            CONST.HTML_DIRECTORY / "login.html"
        )
        self.source_html_dashboard: str = str(
            CONST.HTML_DIRECTORY / "dashboard.html"
        )
        self.source_html_logout: str = str(
            CONST.HTML_DIRECTORY / "logout.html"
        )
        # ======================= File List
        self.source_files: Dict[str, str] = {
            self.front_end_assets_css_pico: self.source_css_pico,
            self.front_end_assets_css_custom: self.source_css_custom,
            self.front_end_assets_css_emoji_font: self.source_css_emoji_font,
            self.front_end_assets_js_module_cookies: self.source_js_module_cookies,
            self.front_end_assets_js_module_indexdb: self.source_js_module_indexdb,
            self.front_end_assets_js_module_querier: self.source_js_module_querier,
            self.front_end_assets_js_module_general: self.source_js_module_general,
            self.front_end_assets_js_theme_pico: self.source_js_theme_pico,
            self.front_end_assets_js_dashboard: self.source_js_dashboard,
            self.front_end_assets_js_login: self.source_js_login,
            self.front_end_assets_js_logout: self.source_js_logout,
            self.front_end_assets_html_login: self.source_html_login,
            self.front_end_assets_html_dashboard: self.source_html_dashboard,
            self.front_end_assets_html_logout: self.source_html_logout
        }
        # -------------------------- Shared instances --------------------------
        self.boilerplate_incoming_initialised: "BoilerplateIncoming" = self.runtime_manager.get(
            "BoilerplateIncoming")
        self.boilerplate_responses_initialised: "BoilerplateResponses" = self.runtime_manager.get(
            "BoilerplateResponses")
        self.boilerplate_non_http_initialised: "BoilerplateNonHTTP" = self.runtime_manager.get(
            "BoilerplateNonHTTP")
        self.database_link: "SQL" = self.runtime_manager.get("SQL")
        self.server_headers_initialised: "ServerHeaders" = self.runtime_manager.get(
            "ServerHeaders")
        # ----------------------------- file caches ----------------------------
        self.file_cache: Dict[str, CacheEntry] = {}
        self.key_data: str = "data"
        self.key_timestamp: str = "timestamp"
        self.key_source: str = "source"
        self.cache_expiration: timedelta = CACHE_LIFETIME
        # ---------------------------- Finalisation ----------------------------
        self.disp.log_debug("Initialised")

    # ---------------------------- Cache management ----------------------------
    def _get_file_content(self, file_path: str) -> str:
        """Read the content of a file.

        Args:
            file_path: Path to the file.
        Returns:
            str: Content of the file as a string.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content

    def _load_cache(self, expiration: timedelta = CACHE_LIFETIME) -> None:
        """Load the file cache for static assets.
        """
        self.disp.log_debug("Loading front-end file cache...")
        total_files = 0
        self.cache_expiration = expiration
        for endpoint, path in self.source_files.items():
            self.disp.log_debug(
                f"Caching front-end file: {path} for endpoint: {endpoint}"
            )
            expiration_date = datetime.now() + expiration
            try:
                file_content = self._get_file_content(path)
            except (OSError, UnicodeDecodeError) as e:
                self.disp.log_error(f"Failed to load file {path}: {e}")
                continue
            self.file_cache[endpoint] = CacheEntry(
                data=file_content,
                timestamp=expiration_date,
                source=path
            )
            total_files += 1
            self.disp.log_debug(
                f"Cached front-end file: {path} for endpoint: {endpoint} until {expiration_date}"
            )
        self.disp.log_debug(f"{total_files} Front-end file cache loaded.")

    def _refresh_cache(self) -> None:
        """Refresh the file cache for static assets.
        """
        self.disp.log_debug("Refreshing front-end file cache...")
        cache_refreshed = 0
        skipped = 0
        for endpoint, cache_entry in self.file_cache.items():
            if datetime.now() >= cache_entry.timestamp:
                self.disp.log_debug(
                    f"Refreshing cache for front-end file: {cache_entry.source} at endpoint: {endpoint}"
                )
                expiration_date = datetime.now() + self.cache_expiration
                try:
                    file_content = self._get_file_content(cache_entry.source)
                except (OSError, UnicodeDecodeError) as e:
                    self.disp.log_error(
                        f"Failed to load file {cache_entry.source}: {e}"
                    )
                    continue
                self.file_cache[endpoint] = CacheEntry(
                    data=file_content,
                    timestamp=expiration_date,
                    source=cache_entry.source
                )
                cache_refreshed += 1
                self.disp.log_debug(
                    f"Refreshed cache for front-end file: {cache_entry.source} at endpoint: {endpoint} until {expiration_date}"
                )
            else:
                skipped += 1
        self.disp.log_debug(
            f"Refreshed {cache_refreshed} front-end file caches."
        )
        self.disp.log_debug(f"Skipped {skipped} front-end file caches.")

    def _ressource_not_found_response(self, path: str, title: str) -> Response:
        """Generate a 404 response for missing resources.

        Args:
            path: Path to the missing resource.
        Returns:
            Response: FastAPI Response with 404 error.
        """
        body = self.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=f"The requested resource at path {path} was not found.",
            resp="not_found",
            token=None,
            error=True
        )
        return HCI.not_found(body, content_type=HttpDataTypes.JSON, headers=self.server_headers_initialised.for_json())

    def _get_cache(self, path: str) -> Union[str, Response]:
        """Refresh the file cache for static assets.
        """
        self.disp.log_debug(f"Retrieving front-end file from cache: {path}")
        self._refresh_cache()
        if path not in self.file_cache:
            self.disp.log_debug(f"Front-end file not found in cache: {path}")
            return self._ressource_not_found_response(path, "Resource Not Found")
        data = self.file_cache[path]
        if not data.data:
            self.disp.log_debug(f"Front-end file cache empty for: {path}")
            return self._ressource_not_found_response(
                path, "Resource Not Found"
            )
        self.disp.log_debug(f"Retrieved front-end file from cache: {path}")
        return data.data
    # -------------------------- End Cache management --------------------------
    # ------------------------------ HTML Snippets -----------------------------

    def _get_headers(self, page_title: str) -> str:
        """Generate HTML headers for front-end pages.

        Args:
            page_title: Title of the HTML page.
        Returns:
            str: HTML headers as a string.
        """
        app_name: str = self.server_headers_initialised.app_name
        verification: str = CONST.GOOGLE_SITE_VERIFICATION_CODE
        headers = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta lang="eng">
    <meta charset="UTF-8">
    <meta name="Language" CONTENT="en,fr" />
    <meta name="publisher" content="{self.author}" />
    <meta http-equiv="pragma" content="cache" />
    <meta http-equiv="Cache-control" content="public" />
    <meta name="googlebot" content="index,follow,snippet" />
    <meta name="google" content="translate,sitelinkssearchbox" />
    <link rel="stylesheet" href="{self.front_end_assets_css_pico}">
    <link rel="stylesheet" href="{self.front_end_assets_css_custom}">
    <link rel="stylesheet" href="{self.front_end_assets_css_emoji_font}">
    <meta name="google-site-verification" content="{verification}" />
    <meta name="copyright" content=\"&copy; {self.author} {self.year}"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="index,follow,max-image-preview:standard" />
    <link rel="icon" type="image/png" href="{self.front_end_assets_image_favicon_png}" />
    <meta name="Index" content="This is the page named: {page_title} of the server {app_name}." />
    <link rel="shortcut icon" type="image/x-icon" href="{self.front_end_assets_images_favicon}" />
</head>
"""
        return headers

    def _get_theme_toggler(self) -> str:
        """Generate HTML theme toggler for front-end pages.

        Returns:
            str: HTML theme toggler as a string.
        """
        toggler = """<div class="theme-toggler">
    <label for="theme-select">Theme:</label>
    <select id="theme-select" aria-label="Theme selector">
        <option value="system">System</option>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
    </select>
</div>
"""
        return toggler

    def _get_heading(self, page_title: str, show_logout: bool = False) -> str:
        """Generate HTML heading for front-end pages.

        Args:
            page_title: Title of the page.
            show_logout: Whether to show the logout button.
        Returns:
            str: HTML heading as a string.
        """
        theme_toggle = self._get_theme_toggler()
        logout_button = ""
        if show_logout:
            logout_button = '<div class="logout-container"><button onclick="logout()">Logout</button></div>'
        heading = f"""<header class="page-header">
    <h1 class="page-title">{self.server_headers_initialised.app_name} - {page_title}</h1>
    <div class="theme-container">{theme_toggle}</div>
    {logout_button}
</header>
"""
        return heading

    def _get_footers(self, page_type: Pages = Pages.DEFAULT) -> str:
        """Generate HTML footers for front-end pages.

        Args:
            page_type: Type of the page (Pages enum).
        Returns:
            str: HTML footers as a string.
        """
        host: str = self.server_headers_initialised.host
        if host == "0.0.0.0":
            host = "http://127.0.0.1"
        if not host.startswith("http"):
            host = f"http://{host}"
        port: int = self.server_headers_initialised.port
        if port == 0:
            port = -1
        name: str = self.server_headers_initialised.app_name.lower().replace(" ", "_")
        page_scripts = ""
        if page_type == Pages.LOGIN:
            page_scripts += f'<script type="text/JavaScript" src="{self.front_end_assets_js_login}" data-dashboard-url="{self.front_end_dashboard}"></script>'
        if page_type == Pages.DASHBOARD:
            page_scripts += f'<script type="text/JavaScript" src="{self.front_end_assets_js_dashboard}" data-login-url="{self.front_end_login}" data-logout-url="{self.front_end_logout}"></script>'
        if page_type == Pages.LOGOUT:
            page_scripts += f'<script type="text/JavaScript" src="{self.front_end_assets_js_logout}" data-login-url="{self.front_end_login}"></script>'
        footers = f"""<div class="footer">
    <hr/>
    <p>&copy; {self.author} {self.year}</p>
    <script type="module" src="{self.front_end_assets_js_module_cookies}"></script>
    <script type="module" src="{self.front_end_assets_js_module_indexdb}" data-db-name="{name}" data-store-name="keyValueStore"></script>
    <script type="module" src="{self.front_end_assets_js_module_querier}" data-api-url="{host}" data-api-port="{port}"></script>
    <script id="general-module" type="module" src="{self.front_end_assets_js_module_general}" data-theme-cookie-name="theme" data-cookie-expires-days="365"></script>
    <script type="text/JavaScript" src="{self.front_end_assets_js_theme_pico}"></script>
    {page_scripts}
    <script type="module">
        const moduleScript = document.getElementById('general-module');
        const opts = moduleScript ? moduleScript.dataset : {"{}"};
        window.general_scripts.initThemeToggler(opts);
    </script>
</div>"""
        return footers
    # --------------------------- End HTML Snippets ----------------------------
    # ------------------------------- HTML Pages -------------------------------

    def serve_login(self) -> Response:
        """Serve the login page.

        Returns:
            Response: FastAPI Response with login HTML content.
        """
        page_title = "Login"
        page_header = self._get_headers(page_title)
        page_heading = self._get_heading(page_title)
        page_body = self._get_cache(self.front_end_assets_html_login)
        page_footer = self._get_footers(Pages.LOGIN)
        page_content = f"""{page_header}
<body>
    {page_heading}
    {page_body}
    {page_footer}
</body>
</html>
"""
        return HCI.success(page_content, content_type=HttpDataTypes.HTML, headers=self.server_headers_initialised.for_html())

    def serve_dashboard(self) -> Response:
        """Serve the dashboard page.

        Returns:
            Response: FastAPI Response with dashboard HTML content.
        """
        page_title = "Dashboard"
        page_header = self._get_headers(page_title)
        page_heading = self._get_heading(page_title, show_logout=True)
        page_body = self._get_cache(self.front_end_assets_html_dashboard)
        page_footer = self._get_footers(Pages.DASHBOARD)
        page_content = f"""{page_header}
<body>
    {page_heading}
    {page_body}
    {page_footer}
</body>
</html>
"""
        return HCI.success(page_content, content_type=HttpDataTypes.HTML, headers=self.server_headers_initialised.for_html())

    def serve_logout(self) -> Response:
        """Serve the logout page.

        Returns:
            Response: FastAPI Response with logout HTML content.
        """
        page_title = "Logout"
        page_header = self._get_headers(page_title)
        page_heading = self._get_heading(page_title)
        page_body = self._get_cache(self.front_end_assets_html_logout)
        page_footer = self._get_footers(Pages.LOGOUT)
        page_content = f"""{page_header}
<body>\n
    {page_heading}
    {page_body}
    {page_footer}
</body>
</html>
"""
        return HCI.success(page_content, content_type=HttpDataTypes.HTML, headers=self.server_headers_initialised.for_html())
    # ----------------------------- End HTML Pages -----------------------------
    # ---------------------------- Assets endpoints ----------------------------

    def get_pico(self) -> Response:
        """Get the Pico CSS content.

        Returns:
            Response: FastAPI Response with Pico CSS content.
        """
        css_content = self._get_cache(self.front_end_assets_css_pico)
        if isinstance(css_content, Response):
            return css_content
        return HCI.success(css_content, content_type=HttpDataTypes.CSS, headers=self.server_headers_initialised.for_css())

    def get_custom_css(self) -> Response:
        """Get the Pico CSS content.

        Returns:
            Response: FastAPI Response with Pico CSS content.
        """
        css_content = self._get_cache(self.front_end_assets_css_custom)
        if isinstance(css_content, Response):
            return css_content
        return HCI.success(css_content, content_type=HttpDataTypes.CSS, headers=self.server_headers_initialised.for_css())

    def get_css_emoji_font(self) -> Response:
        """Get the Emoji font CSS content.

        Returns:
            Response: FastAPI Response with Emoji font CSS content.
        """
        css_content = self._get_cache(self.front_end_assets_css_emoji_font)
        if isinstance(css_content, Response):
            return css_content
        return HCI.success(css_content, content_type=HttpDataTypes.CSS, headers=self.server_headers_initialised.for_css())

    def get_css_emoji_regular(self) -> Response:
        """Get the Emoji regular font file

        Returns:
            Response: FastAPI Response with the Emoji font file
        """
        file_content = self._get_cache(
            self.front_end_assets_css_emoji_font_static_regular)
        if isinstance(file_content, Response):
            if os.path.isfile(self.source_css_emoji_font_regular):
                return HCI.success(self.source_css_emoji_font_regular, content_type=HttpDataTypes.TTF, headers=self.server_headers_initialised.for_file())
            return file_content
        return HCI.success(file_content, content_type=HttpDataTypes.TTF, headers=self.server_headers_initialised.for_file())

    def get_css_emoji_light(self) -> Response:
        """Get the Emoji light font file

        Returns:
            Response: FastAPI Response with the Emoji font file
        """
        file_content = self._get_cache(
            self.front_end_assets_css_emoji_font_static_light
        )
        if isinstance(file_content, Response):
            if os.path.isfile(self.source_css_emoji_font_light):
                return HCI.success(self.source_css_emoji_font_light, content_type=HttpDataTypes.TTF, headers=self.server_headers_initialised.for_file())
            return file_content
        return HCI.success(file_content, content_type=HttpDataTypes.TTF, headers=self.server_headers_initialised.for_file())

    def get_css_emoji_medium(self) -> Response:
        """Get the Emoji medium font file

        Returns:
            Response: FastAPI Response with the Emoji font file
        """
        file_content = self._get_cache(
            self.front_end_assets_css_emoji_font_static_medium)
        if isinstance(file_content, Response):
            if os.path.isfile(self.source_css_emoji_font_medium):
                return HCI.success(self.source_css_emoji_font_medium, content_type=HttpDataTypes.TTF, headers=self.server_headers_initialised.for_file())
            return file_content
        return HCI.success(file_content, content_type=HttpDataTypes.TTF, headers=self.server_headers_initialised.for_file())

    def get_css_emoji_semi_bold(self) -> Response:
        """Get the Emoji regular font file

        Returns:
            Response: FastAPI Response with the Emoji font file
        """
        file_content = self._get_cache(
            self.front_end_assets_css_emoji_font_static_semi_bold
        )
        if isinstance(file_content, Response):
            if os.path.isfile(self.source_css_emoji_font_semi_bold):
                return HCI.success(self.source_css_emoji_font_semi_bold, content_type=HttpDataTypes.TTF, headers=self.server_headers_initialised.for_file())
            return file_content
        return HCI.success(file_content, content_type=HttpDataTypes.TTF, headers=self.server_headers_initialised.for_file())

    def get_css_emoji_bold(self) -> Response:
        """Get the Emoji regular font file

        Returns:
            Response: FastAPI Response with the Emoji font file
        """
        file_content = self._get_cache(
            self.front_end_assets_css_emoji_font_static_bold)
        if isinstance(file_content, Response):
            if os.path.isfile(self.source_css_emoji_font_bold):
                return HCI.success(self.source_css_emoji_font_bold, content_type=HttpDataTypes.TTF, headers=self.server_headers_initialised.for_file())
            return file_content
        return HCI.success(file_content, content_type=HttpDataTypes.TTF, headers=self.server_headers_initialised.for_file())

    def get_cookies_module(self) -> Response:
        """Get the cookies JavaScript module content.

        Returns:
            Response: FastAPI Response with cookies JS module content.
        """
        js_content = self._get_cache(self.front_end_assets_js_module_cookies)
        if isinstance(js_content, Response):
            return js_content
        return HCI.success(js_content, content_type=HttpDataTypes.JAVASCRIPT, headers=self.server_headers_initialised.for_javascript())

    def get_indexeddb_module(self) -> Response:
        """Get the IndexedDB JavaScript module content.

        Returns:
            Response: FastAPI Response with IndexedDB JS module content.
        """
        js_content = self._get_cache(self.front_end_assets_js_module_indexdb)
        if isinstance(js_content, Response):
            return js_content
        return HCI.success(js_content, content_type=HttpDataTypes.JAVASCRIPT, headers=self.server_headers_initialised.for_javascript())

    def get_querier_module(self) -> Response:
        """Get the Querier JavaScript module content.

        Returns:
            Response: FastAPI Response with Querier JS module content.
        """
        js_content = self._get_cache(self.front_end_assets_js_module_querier)
        if isinstance(js_content, Response):
            return js_content
        return HCI.success(js_content, content_type=HttpDataTypes.JAVASCRIPT, headers=self.server_headers_initialised.for_javascript())

    def get_general_module(self) -> Response:
        """Get the General JavaScript module content.
        Returns:
            Response: FastAPI Response with General JS module content.
        """
        js_content = self._get_cache(self.front_end_assets_js_module_general)
        if isinstance(js_content, Response):
            return js_content
        return HCI.success(js_content, content_type=HttpDataTypes.JAVASCRIPT, headers=self.server_headers_initialised.for_javascript())

    def get_pico_theme(self) -> Response:
        """Get the Pico theme JavaScript content.

        Returns:
            Response: FastAPI Response with Pico theme JS content.
        """
        js_content = self._get_cache(self.front_end_assets_js_theme_pico)
        if isinstance(js_content, Response):
            return js_content
        return HCI.success(js_content, content_type=HttpDataTypes.JAVASCRIPT, headers=self.server_headers_initialised.for_javascript())

    def get_dashboard_js(self) -> Response:
        """Get the dashboard JavaScript content.

        Returns:
            Response: FastAPI Response with dashboard JS content.
        """
        js_content = self._get_cache(self.front_end_assets_js_dashboard)
        if isinstance(js_content, Response):
            return js_content
        return HCI.success(js_content, content_type=HttpDataTypes.JAVASCRIPT, headers=self.server_headers_initialised.for_javascript())

    def get_login_js(self) -> Response:
        """Get the login JavaScript content.

        Returns:
            Response: FastAPI Response with login JS content.
        """
        js_content = self._get_cache(self.front_end_assets_js_login)
        if isinstance(js_content, Response):
            return js_content
        return HCI.success(js_content, content_type=HttpDataTypes.JAVASCRIPT, headers=self.server_headers_initialised.for_javascript())

    def get_logout_js(self) -> Response:
        """Get the logout JavaScript content.

        Returns:
            Response: FastAPI Response with logout JS content.
        """
        js_content = self._get_cache(self.front_end_assets_js_logout)
        if isinstance(js_content, Response):
            return js_content
        return HCI.success(js_content, content_type=HttpDataTypes.JAVASCRIPT, headers=self.server_headers_initialised.for_javascript())

    def get_favicon_ico(self) -> Response:
        """Get the favicon ICO content.

        Returns:
            Response: FastAPI Response with favicon ICO content.
        """
        icon = CONST.ICON_PATH
        self.disp.log_debug(f"Favicon path: {icon}")
        if os.path.isfile(icon):
            return HCI.success(icon, content_type=HttpDataTypes.XICON)
        return HCI.not_found("Icon not found in the expected directory", content_type=HttpDataTypes.TEXT)

    def get_favicon_png(self) -> Response:
        """Get the favicon PNG content.

        Returns:
            Response: FastAPI Response with favicon PNG content.
        """
        icon = CONST.PNG_ICON_PATH
        self.disp.log_debug(f"Static logo path: {icon}")
        if os.path.isfile(icon):
            return HCI.success(icon, content_type=HttpDataTypes.PNG, headers=self.server_headers_initialised.for_image())
        return HCI.not_found("Icon not found in the expected directory", content_type=HttpDataTypes.TEXT)
    # ---------------------------- Assets endpoints ----------------------------
    # ----------------------------- Path Injection -----------------------------

    def _inject_assets(self, path_manager: "PathManager") -> None:
        """Inject front-end asset paths into the PathManager.

        Args:
            path_manager: Instance of PathManager to inject paths into.
        """
        self._load_cache(self.cache_expiration)
        assets = {
            self.front_end_assets_css_pico: self.get_pico,
            self.front_end_assets_css_custom: self.get_custom_css,
            self.front_end_assets_css_emoji_font: self.get_css_emoji_font,
            self.front_end_assets_css_emoji_font_static_regular: self.get_css_emoji_regular,
            self.front_end_assets_css_emoji_font_static_light: self.get_css_emoji_light,
            self.front_end_assets_css_emoji_font_static_medium: self.get_css_emoji_medium,
            self.front_end_assets_css_emoji_font_static_semi_bold: self.get_css_emoji_semi_bold,
            self.front_end_assets_css_emoji_font_static_bold: self.get_css_emoji_bold,
            self.front_end_assets_js_module_cookies: self.get_cookies_module,
            self.front_end_assets_js_module_indexdb: self.get_indexeddb_module,
            self.front_end_assets_js_module_querier: self.get_querier_module,
            self.front_end_assets_js_module_general: self.get_general_module,
            self.front_end_assets_js_theme_pico: self.get_pico_theme,
            self.front_end_assets_js_dashboard: self.get_dashboard_js,
            self.front_end_assets_js_login: self.get_login_js,
            self.front_end_assets_js_logout: self.get_logout_js,
            self.front_end_assets_images_favicon: self.get_favicon_ico,
            self.front_end_assets_image_favicon_png: self.get_favicon_png
        }
        for endpooint, handler in assets.items():
            path_manager.add_path_if_not_exists(
                endpooint, handler, "GET",
                decorators=[decorators.public_endpoint(),
                            decorators.front_end_assets_endpoint]
            )

    def inject_paths(self, path_manager: "PathManager") -> None:
        """Inject front-end paths into the PathManager.

        Args:
            path_manager: Instance of PathManager to inject paths into.
        """
        path_manager.add_path_if_not_exists(
            f"{self.front_end_login}", self.serve_login, "GET",
            decorators=[decorators.public_endpoint(),
                        decorators.front_end_endpoint]
        )
        path_manager.add_path_if_not_exists(
            f"{self.front_end_dashboard}", self.serve_dashboard, "GET",
            decorators=[decorators.auth_endpoint(),
                        decorators.front_end_endpoint]
        )
        path_manager.add_path_if_not_exists(
            f"{self.front_end_logout}", self.serve_logout, "GET",
            decorators=[decorators.public_endpoint(),
                        decorators.front_end_endpoint]
        )
        self._inject_assets(path_manager)
    # --------------------------- End Path Injection ---------------------------
