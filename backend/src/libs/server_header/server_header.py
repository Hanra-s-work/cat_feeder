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
# FILE: server_header.py
# CREATION DATE: 24-11-2025
# LAST Modified: 14:51:49 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The class in charge of building the header for the server (This allows a certain flexibility with regards to the response structure)
# // AR
# +==== END CatFeeder =================+
"""

from typing import Dict

from display_tty import Disp, initialise_logger

from . import server_header_constants as HEADER_CONST

from ..core import FinalClass


class ServerHeaders(metaclass=FinalClass):
    """HTTP response header builder for FastAPI responses.

    Provides standardized header generation methods for different content types
    with appropriate security policies, caching strategies, and content disposition.

    Security Features:
        - X-Content-Type-Options: nosniff (prevents MIME sniffing)
        - X-Frame-Options: DENY/SAMEORIGIN (clickjacking protection)
        - X-XSS-Protection: 1; mode=block (XSS protection)
        - Referrer-Policy: strict-origin-when-cross-origin (privacy control)
        - Content-Security-Policy: Applied to HTML responses

    Caching Strategies:
        - Dynamic content (JSON/text/HTML/forms): no-cache
        - Versioned static assets (JS/CSS): 1 year immutable
        - Media files (images/video/audio): 24 hours
        - Downloadable files (PDF/CSV): 1 hour
        - Streaming content: no-cache

    Usage:
        >>> headers = ServerHeaders(app_name="MyAPI")
        >>> json_headers = headers.for_json()
        >>> file_headers = headers.for_file(filename="report.pdf")
        >>> return Response(content=data, headers=json_headers)

    Attributes:
        host (str): Server host address.
        port (int): Server port number.
        app_name (str): Application name included in X-App-Name header.
        error (int): Error return code.
        success (int): Success return code.
        debug (bool): Debug mode flag.
    """
    disp: Disp = initialise_logger(__qualname__, False)

    def __init__(self, host: str = "0.0.0.0", port: int = 5000, app_name: str = "Asperguide", error: int = 84, success: int = 0, debug: bool = False) -> None:
        """Initialize ServerHeaders instance.

        Args:
            host: Server host address. Defaults to "0.0.0.0".
            port: Server port number. Defaults to 5000.
            app_name: Application name for headers. Defaults to "Asperguide".
            error: Error return code. Defaults to 84.
            success: Success return code. Defaults to 0.
            debug: Enable debug logging. Defaults to False.
        """
        # ------------------------ The logging function ------------------------
        self.disp.update_disp_debug(debug)
        self.disp.log_debug("Initialising...")
        # -------------------------- Inherited values --------------------------
        self.host: str = host
        self.port: int = port
        self.app_name: str = app_name
        self.error: int = error
        self.success: int = success
        self.debug: bool = debug
        self.disp.log_debug("Initialised")

    def _get_app_name_str(self) -> str:
        """Convert app_name to string format.

        Returns:
            str: Application name as string.
        """
        if not isinstance(self.app_name, str):
            return f"{self.app_name}"
        return self.app_name

    def _base_security_headers(self) -> Dict[str, str]:
        """Common security headers for all responses.

        Includes standard security headers to protect against common web vulnerabilities:
        - MIME sniffing attacks
        - Clickjacking
        - Cross-site scripting (XSS)
        - Referrer leakage

        Returns:
            Dict[str, str]: Base security headers dictionary.
        """
        return {
            HEADER_CONST.HEADER_APP_NAME: self._get_app_name_str(),
            HEADER_CONST.CONTENT_TYPE: "nosniff",
            HEADER_CONST.FRAME_OPTIONS: "DENY",
            HEADER_CONST.XSS_PROTECTION: "1; mode=block",
            HEADER_CONST.REFERRER_POLICY: "strict-origin-when-cross-origin",
        }

    def for_json(self) -> Dict[str, str]:
        """Headers for JSON responses.

        Includes aggressive no-cache policy for dynamic API data.

        Returns:
            Dict[str, str]: Headers optimized for JSON responses.
        """
        headers = self._base_security_headers()
        headers[HEADER_CONST.CACHE_CONTROL] = "no-cache, no-store, must-revalidate"
        headers[HEADER_CONST.PRAGMA] = "no-cache"
        headers[HEADER_CONST.EXPIRES] = "0"
        return headers

    def for_text(self) -> Dict[str, str]:
        """Headers for plain text responses.

        Returns:
            Dict[str, str]: Headers optimized for plain text responses.
        """
        headers = self._base_security_headers()
        headers[HEADER_CONST.CACHE_CONTROL] = "no-cache, no-store, must-revalidate"
        return headers

    def for_html(self) -> Dict[str, str]:
        """Headers for HTML responses.

        Includes Content-Security-Policy to control script/style sources and prevent XSS.

        Returns:
            Dict[str, str]: Headers optimized for HTML responses with CSP.
        """
        headers = self._base_security_headers()
        headers[HEADER_CONST.CACHE_CONTROL] = "no-cache, no-store, must-revalidate"
        headers[HEADER_CONST.CONTENT_SECURITY_POLICY] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;"
        return headers

    def for_xml(self) -> Dict[str, str]:
        """Headers for XML responses.

        Returns:
            Dict[str, str]: Headers optimized for XML responses.
        """
        headers = self._base_security_headers()
        headers[HEADER_CONST.CACHE_CONTROL] = "no-cache, no-store, must-revalidate"
        return headers

    def for_css(self) -> Dict[str, str]:
        """Headers for CSS responses.

        Uses aggressive caching (1 year) for versioned static CSS files.

        Returns:
            Dict[str, str]: Headers optimized for CSS with long-term caching.
        """
        headers = self._base_security_headers()
        headers[HEADER_CONST.CACHE_CONTROL] = "public, max-age=31536000, immutable"
        return headers

    def for_javascript(self) -> Dict[str, str]:
        """Headers for JavaScript responses.

        Uses aggressive caching (1 year) for versioned static JavaScript files.

        Returns:
            Dict[str, str]: Headers optimized for JavaScript with long-term caching.
        """
        headers = self._base_security_headers()
        headers[HEADER_CONST.CACHE_CONTROL] = "public, max-age=31536000, immutable"
        return headers

    def for_image(self) -> Dict[str, str]:
        """Headers for image responses.

        Uses 24-hour caching and allows iframe embedding from same origin.

        Returns:
            Dict[str, str]: Headers optimized for image responses.
        """
        headers = self._base_security_headers()
        headers[HEADER_CONST.CACHE_CONTROL] = "public, max-age=86400"
        headers[HEADER_CONST.FRAME_OPTIONS] = "SAMEORIGIN"
        return headers

    def for_file(self, filename: str = "") -> Dict[str, str]:
        """Headers for file download responses.

        Args:
            filename: Optional filename for Content-Disposition header.

        Returns:
            Dict[str, str]: Headers optimized for file downloads with optional filename.
        """
        headers = self._base_security_headers()
        headers[HEADER_CONST.CACHE_CONTROL] = "public, max-age=3600"
        if filename:
            headers[HEADER_CONST.CONTENT_DISPOSITION] = f'attachment; filename="{filename}"'
        return headers

    def for_pdf(self, filename: str = "document.pdf", inline: bool = False) -> Dict[str, str]:
        """Headers for PDF responses.

        Args:
            filename: PDF filename for Content-Disposition. Defaults to "document.pdf".
            inline: If True, display inline in browser; if False, force download. Defaults to False.

        Returns:
            Dict[str, str]: Headers optimized for PDF with configurable display mode.
        """
        headers = self._base_security_headers()
        headers[HEADER_CONST.CACHE_CONTROL] = "public, max-age=3600"
        if inline:
            disposition = "inline"
        else:
            disposition = "attachment"
        headers[HEADER_CONST.CONTENT_DISPOSITION] = f'{disposition}; filename="{filename}"'
        return headers

    def for_stream(self) -> Dict[str, str]:
        """Headers for streaming responses.

        Supports byte-range requests for efficient streaming.

        Returns:
            Dict[str, str]: Headers optimized for streaming with range support.
        """
        headers = self._base_security_headers()
        headers[HEADER_CONST.CACHE_CONTROL] = "no-cache"
        headers[HEADER_CONST.ACCEPT_RANGES] = "bytes"
        return headers

    def for_video(self) -> Dict[str, str]:
        """Headers for video streaming responses.

        Supports byte-range requests for seeking and allows iframe embedding from same origin.

        Returns:
            Dict[str, str]: Headers optimized for video streaming.
        """
        headers = self._base_security_headers()
        headers[HEADER_CONST.CACHE_CONTROL] = "public, max-age=86400"
        headers[HEADER_CONST.ACCEPT_RANGES] = "bytes"
        headers[HEADER_CONST.FRAME_OPTIONS] = "SAMEORIGIN"
        return headers

    def for_audio(self) -> Dict[str, str]:
        """Headers for audio streaming responses.

        Supports byte-range requests for seeking.

        Returns:
            Dict[str, str]: Headers optimized for audio streaming.
        """
        headers = self._base_security_headers()
        headers[HEADER_CONST.CACHE_CONTROL] = "public, max-age=86400"
        headers[HEADER_CONST.ACCEPT_RANGES] = "bytes"
        return headers

    def for_csv(self, filename: str = "export.csv") -> Dict[str, str]:
        """Headers for CSV export responses.

        Forces download with specified filename and no caching for fresh exports.

        Args:
            filename: CSV filename for Content-Disposition. Defaults to "export.csv".

        Returns:
            Dict[str, str]: Headers optimized for CSV exports with download enforcement.
        """
        headers = self._base_security_headers()
        headers[HEADER_CONST.CACHE_CONTROL] = "no-cache, no-store, must-revalidate"
        headers[HEADER_CONST.CONTENT_DISPOSITION] = f'attachment; filename="{filename}"'
        return headers

    def for_redirect(self) -> Dict[str, str]:
        """Headers for redirect responses.

        Minimal headers for HTTP redirects.

        Returns:
            Dict[str, str]: Headers optimized for redirect responses.
        """
        return {
            HEADER_CONST.HEADER_APP_NAME: self._get_app_name_str(),
            HEADER_CONST.CACHE_CONTROL: "no-cache, no-store, must-revalidate",
        }

    def for_form(self) -> Dict[str, str]:
        """Headers for form data responses.

        Returns:
            Dict[str, str]: Headers optimized for form data responses.
        """
        headers = self._base_security_headers()
        headers[HEADER_CONST.CACHE_CONTROL] = "no-cache, no-store, must-revalidate"
        return headers
