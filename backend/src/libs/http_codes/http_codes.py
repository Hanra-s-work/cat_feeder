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
# FILE: http_codes.py
# CREATION DATE: 11-10-2025
# LAST Modified: 22:25:14 10-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File containing the list of http codes that can be sent and received by the server.
# // AR
# +==== END CatFeeder =================+
"""

import os
from typing import Mapping, Dict, Any, Optional, Union, TypeAlias

from fastapi.responses import (
    Response, FileResponse, HTMLResponse, JSONResponse,
    PlainTextResponse, RedirectResponse, StreamingResponse,
    UJSONResponse, ORJSONResponse
)

from . import http_constants as CONST
from ..core import FinalClass

# Accept either a `DataTypes` enum member or a string key/MIME type
ContentTypeLike: TypeAlias = Union[CONST.DataTypes, str]


class HttpCodes(metaclass=FinalClass):
    """HTTP status code response handler using FastAPI response types.

    Provides methods for returning standardized HTTP responses with appropriate
    status codes, content types, and headers. Supports JSON, plain text, HTML,
    binary, file, and redirect responses.

    HTTP Response Categories:
    - 1xx: Informational
    - 2xx: Successful
    - 3xx: Redirection
    - 4xx: Client error
    - 5xx: Server error
    """

    def __init__(self) -> None:
        self.authorised_statuses = CONST.AUTHORISED_STATUSES
        self.data_types = CONST.DATA_TYPES

    # """ General basic success message that speaks on channel 200 by default """

    def _check_data_type(self, data_type: Optional[ContentTypeLike] = None) -> str:
        """Validate and normalize provided content type to canonical MIME string.

        Resolves content type from DataTypes enum member, known key string, or raw MIME type string to standardized MIME format.

        Args:
            data_type (ContentTypeLike, optional): Desired content type or alias.

        Returns:
            str: Canonical MIME type string (e.g., "application/json").

        Raises:
            TypeError: If the provided type cannot be resolved to a known or valid MIME type.
        """
        if data_type is None:
            return "text/plain"

        if isinstance(data_type, CONST.DataTypes):
            return data_type.value

        if isinstance(data_type, str):
            resolved = CONST.DataTypes.from_key(data_type)
            if resolved is not None:
                return resolved.value

            lowered = data_type.lower()
            if lowered in self.data_types:
                return self.data_types[lowered]
            if data_type in self.data_types.values():
                return data_type

        raise TypeError(f"Invalid data type: {data_type}")

    def _check_header(self, header: Optional[Mapping[str, str]] = None) -> Any:
        """Validate and normalize HTTP headers.

        Args:
            header (Mapping[str, str], optional): _description_. Defaults to None.
        Returns:
            Any: Returns the correct known version of the sent headers.
        Raises:
            TypeError: If header is not a Mapping or Dict.
        """
        if header is None:
            return {}
        if not isinstance(header, (Dict, Mapping)):
            raise TypeError(
                f"Invalid header format, the format you provided is: {type(header)}"
            )
        return dict(header)

    def _process_data_content(self, data: Any, data_type: str) -> Any:
        """Process data content for HTTP response based on MIME type.

        Handles binary passthrough, file-like objects, JSON, and streaming data.

        Args:
            data (Any): _description_: The data to be sent.
            data_type (str): _description_: The type of the data to be sent.

        Returns:
            Any: Processed data in appropriate format for response type.
        """
        if data is None:
            return ""
        # Binary passthrough
        if isinstance(data, (bytes, bytearray)):
            return data
        # File-like object
        if hasattr(data, "read"):
            return data
        # JSON: let JSONResponse handle encoding
        if data_type in CONST.JSON_MIME_TYPES:
            return data
        # Streaming: allow raw data
        if data_type in CONST.STREAMING_MIME_TYPES:
            return data
        return str(data)

    def _package_correctly(self, status: int = 200, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Union[Response, FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, StreamingResponse, UJSONResponse, ORJSONResponse]:
        """Route response content to appropriate FastAPI response class.

        Determines correct response type based on content type and returns properly formatted response with status code, content, type, and headers.

        Args:
            status (int, optional): HTTP status code. Defaults to 200.
            content (Any, optional): Response content. Defaults to DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): MIME type or DataTypes member. Defaults to DEFAULT_MESSAGE_TYPE.
            headers (Optional[Mapping[str, str]], optional): HTTP headers mapping. Defaults to None.

        Raises:
            TypeError: If content type is incompatible with content.

        Returns:
            Union[Response, FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, StreamingResponse, UJSONResponse, ORJSONResponse]: _description_
        """
        # Returning the content as a response if the payload data is bytes.
        if isinstance(content, bytes):
            return Response(
                content=content,
                status_code=status,
                headers=headers,
                media_type=content_type
            )

        # Streaming / Binary (check BEFORE FILE because OCTET_STREAM is in both categories)
        if content_type in CONST.STREAMING_MIME_TYPES:
            # For actual iterables/generators, use StreamingResponse
            return StreamingResponse(
                content=content,
                status_code=status,
                headers=headers,
                media_type=content_type
            )

        # FILE BASED
        if content_type in CONST.FILE_MIME_TYPES:
            if not isinstance(content, str):
                raise TypeError(
                    "FileResponse requires the content to be a file path string."
                )
            return FileResponse(
                path=content,
                status_code=status,
                headers=headers,
                media_type=content_type,
                filename=os.path.basename(content)
            )

        # HTML / XML / JS
        if content_type in CONST.HTML_MIME_TYPES:
            return HTMLResponse(
                content=content,
                status_code=status,
                headers=headers,
                media_type=content_type
            )

        # JSON
        if content_type in CONST.JSON_MIME_TYPES:
            return JSONResponse(
                content=content,
                status_code=status,
                headers=headers,
                media_type=content_type
            )

        # Plain text
        if content_type in CONST.PLAIN_TEXT_MIME_TYPES:
            return PlainTextResponse(
                content=content,
                status_code=status,
                headers=headers,
                media_type=content_type
            )

        # Redirect
        if content_type in CONST.REDIRECT_MIME_TYPES:
            return RedirectResponse(
                url=str(content),
                status_code=status,
                headers=headers
            )

        # UJSON
        if content_type in CONST.UJSON_MIME_TYPES:
            return UJSONResponse(
                content=content,
                status_code=status,
                headers=headers,
                media_type=content_type
            )

        # ORJSON
        if content_type in CONST.ORJSON_MIME_TYPES:
            return ORJSONResponse(
                content=content,
                status_code=status,
                headers=headers,
                media_type=content_type
            )

        # Default Response catch-all
        return Response(
            content=content,
            status_code=status,
            headers=headers,
            media_type=content_type
        )

    def send_message_on_status(self, status: int = 200, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """Send HTTP response with specified status code and content.

        Args:
            status (int, optional): HTTP status code. Defaults to 200.
            content (Any, optional): Response content. Defaults to DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): MIME type as DataTypes, known key, or string. Defaults to DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): HTTP headers mapping. Defaults to None.

        Raises:
            ValueError: If status code is not authorized.

        Returns:
            Response: FastAPI response object.
        """
        # Validate status code
        if isinstance(status, str) and status.isdigit():
            status = int(status)

        if status not in self.authorised_statuses:
            raise ValueError(f"Invalid HTTP status code: {status}")

        # Validate content-type + headers
        data_type = self._check_data_type(content_type)
        data_header = self._check_header(headers)
        data = self._process_data_content(content, data_type)

        if isinstance(status, str) and status.isnumeric():
            status = int(status)

        if status not in self.authorised_statuses:
            raise ValueError(
                f"Invalid status code, the code you entered is: {status}"
            )

        # Route to correct Response class
        return self._package_correctly(
            status=status,
            content=data,
            content_type=data_type,
            headers=data_header
        )

    # """ 1xx informational response"""

    def send_continue(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """Send 100 Continue HTTP response.

        Indicates initial part of request received; client should continue or ignore if already finished.

        Args:
            content (Any, optional): Response content. Defaults to DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): MIME type or DataTypes member. Defaults to DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str,str], optional): HTTP headers mapping. Defaults to None.

        Returns:
            Response: A FastAPI Response object with status 100.
        """
        return self.send_message_on_status(status=100, content=content, content_type=content_type, headers=headers)

    def switching_protocols(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """Send 101 Switching Protocols HTTP response.

        Server switches protocols as requested by client, typically for WebSocket.

        Args:
            content (Any, optional): Response content. Defaults to DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): MIME type or DataTypes member. Defaults to DEFAULT_MESSAGE_TYPE.
            headers (Optional[Mapping[str, str]], optional): HTTP headers mapping. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 101.
        """
        return self.send_message_on_status(status=101, content=content, content_type=content_type, headers=headers)

    def processing(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """Send 102 Processing HTTP response.

        Server has received and is processing request; no response available yet. Commonly used in WebDAV.

        Args:
            content (Any, optional): Response content. Defaults to DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): MIME type or DataTypes member. Defaults to DEFAULT_MESSAGE_TYPE.
            headers (Optional[Mapping[str, str]], optional): HTTP headers mapping. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 102.
        """
        return self.send_message_on_status(status=102, content=content, content_type=content_type, headers=headers)

    def early_hints(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """Send 103 Early Hints HTTP response.

        Preload resources while server prepares final response. Improves page load.

        Args:
            content (Any, optional): Response content. Defaults to DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): MIME type or DataTypes member. Defaults to DEFAULT_MESSAGE_TYPE.
            headers (Optional[Mapping[str, str]], optional): HTTP headers mapping. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 103.
        """
        return self.send_message_on_status(status=103, content=content, content_type=content_type, headers=headers)

    def response_is_stale(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """Send 110 Response Is Stale HTTP response.

        Cached response is stale but still usable. Used in caching scenarios.

        Args:
            content (Any, optional): Response content. Defaults to DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): MIME type or DataTypes member. Defaults to DEFAULT_MESSAGE_TYPE.
            headers (Optional[Mapping[str, str]], optional): HTTP headers mapping. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 110.
        """
        return self.send_message_on_status(status=110, content=content, content_type=content_type, headers=headers)

    # """success: 200"""

    def success(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """Send 200 OK HTTP response.

        Request succeeded. Meaning depends on HTTP method (GET, POST, etc.).

        Args:
            content (Any, optional): Response content. Defaults to DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): MIME type or DataTypes member. Defaults to DEFAULT_MESSAGE_TYPE.
            headers (Optional[Mapping[str, str]], optional): HTTP headers mapping. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 200.
        """
        return self.send_message_on_status(status=200, content=content, content_type=content_type, headers=headers)

    def created(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """Send 201 Created HTTP response.

        Request fulfilled; new resource created.

        Args:
            content (Any, optional): Response content. Defaults to DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): MIME type or DataTypes member. Defaults to DEFAULT_MESSAGE_TYPE.
            headers (Optional[Mapping[str, str]], optional): HTTP headers mapping. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 201.
        """
        return self.send_message_on_status(status=201, content=content, content_type=content_type, headers=headers)

    def accepted(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """Send 202 Accepted HTTP response.

        Request accepted for processing but not yet completed. Used for async ops.

        Args:
            content (Any, optional): Response content. Defaults to DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): MIME type or DataTypes member. Defaults to DEFAULT_MESSAGE_TYPE.
            headers (Optional[Mapping[str, str]], optional): HTTP headers mapping. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 202.
        """
        return self.send_message_on_status(status=202, content=content, content_type=content_type, headers=headers)

    def non_authoritative_information(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """Send 203 Non-Authoritative Information HTTP response.

        Request succeeded
        returned info from third-party source.

        Args:
            content_type: MIME type or DataTypes member.
            Defaults to DEFAULT_MESSAGE_TYPE.
            content(Any, optional): The content to send. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type(ContentTypeLike, optional): Content type as `DataTypes` member, known key(e.g., "json"), or raw MIME string. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers(Mapping[str, str], optional): Additional headers to include. Defaults to None.

        Returns:
            Response: A FastAPI Response object with status 203.
        """
        return self.send_message_on_status(status=203, content=content, content_type=content_type, headers=headers)

    def no_content(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 204 No Content HTTP response.

        This response indicates that the server successfully processed the request,
        but is not returning any content. Typically used for DELETE operations.

        Args:
            content (Any, optional): The content to send. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): Content type as `DataTypes` member, known key (e.g., "json"), or raw MIME string. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Additional headers to include. Defaults to None.

        Returns:
            Response: A FastAPI Response object with status 204.
        """
        return self.send_message_on_status(status=204, content=content, content_type=content_type, headers=headers)

    def reset_content(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 205 Reset Content HTTP response.

        This response indicates that the server successfully processed the request,
        and the user agent should reset the document view.

        Args:
            content (Any, optional): The content to send. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): Content type as `DataTypes` member, known key (e.g., "json"), or raw MIME string. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Additional headers to include. Defaults to None.

        Returns:
            Response: A FastAPI Response object with status 205.
        """
        return self.send_message_on_status(status=205, content=content, content_type=content_type, headers=headers)

    def partial_content(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 206 Partial Content HTTP response.

        This response indicates that the server is delivering only part of the
        resource due to a range header sent by the client.

        Args:
            content (Any, optional): The content to send. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): Content type as `DataTypes` member, known key (e.g., "json"), or raw MIME string. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Additional headers to include. Defaults to None.

        Returns:
            Response: A FastAPI Response object with status 206.
        """
        return self.send_message_on_status(status=206, content=content, content_type=content_type, headers=headers)

    def multi_status(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 207 Multi-Status HTTP response.

        Used by WebDAV to convey status for multiple independent sub-requests
        (e.g., batch file operations). The response body typically enumerates
        individual resource states with their own status codes. Prefer this
        when returning heterogeneous results for a single compound action.

        Args:
            content (Any, optional): Structured status description (often JSON/XML). Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type for the body. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Extra response headers. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 207.
        """
        return self.send_message_on_status(status=207, content=content, content_type=content_type, headers=headers)

    def already_reported(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 208 Already Reported HTTP response.

        WebDAV specific: indicates members of a DAV binding have already been
        listed in a previous multi-status response and need not be repeated.
        Helps reduce payload duplication in complex collection listings.

        Args:
            content (Any, optional): Optional explanatory payload. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type for the body. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Extra response headers. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 208.
        """
        return self.send_message_on_status(status=208, content=content, content_type=content_type, headers=headers)

    def im_used(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 226 IM Used HTTP response.

        Indicates the server fulfilled a GET using instance manipulations (e.g.,
        delta encoding) applied to the current instance. Rarely used; applicable
        when returning transformed representations rather than originals to
        save bandwidth.

        Args:
            content (Any, optional): The manipulated representation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type for the body. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Extra response headers detailing transformations. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 226.
        """
        return self.send_message_on_status(status=226, content=content, content_type=content_type, headers=headers)

    """ 3xx redirection """

    def multiple_choices(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 300 Multiple Choices HTTP response.

        Indicates multiple possible representations / endpoints for the resource
        (e.g., different file formats or language variants). Provide a body or
        headers (like `Link`) to guide client selection. Avoid if automated
        negotiation can resolve the choice.

        Args:
            content (Any, optional): Description of available choices. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type for the body. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Optional navigation metadata. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 300.
        """
        return self.send_message_on_status(status=300, content=content, content_type=content_type, headers=headers)

    def moved_permanently(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 301 Moved Permanently HTTP response.

        Indicates the resource has a new canonical URI. Clients should update
        bookmarks and future requests. Use for stable, long-term relocations.
        Supply `Location` header pointing to the new URI.

        Args:
            content (Any, optional): Optional explanatory note. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type for the body. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Should include a `Location` header. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 301.
        """
        return self.send_message_on_status(status=301, content=content, content_type=content_type, headers=headers)

    def found(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 302 Found (Temporary Redirect) HTTP response.

        Historically ambiguous; modern semantics suggest temporary relocation.
        Client should continue using original URI for future requests. Provide
        `Location` header. Prefer 307 if preserving method matters.

        Args:
            content (Any, optional): Optional details about redirect. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type for the body. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Include `Location`. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 302.
        """
        return self.send_message_on_status(status=302, content=content, content_type=content_type, headers=headers)

    def see_other(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 303 See Other HTTP response.

        Directs client to retrieve a representation from a different URI using
        GET. Common after POST to show resulting resource or status page.
        Include `Location` header.

        Args:
            content (Any, optional): Optional redirect explanation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type for body. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Should include `Location`. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 303.
        """
        return self.send_message_on_status(status=303, content=content, content_type=content_type, headers=headers)

    def not_modified(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 304 Not Modified HTTP response.

        Indicates conditional GET found resource unchanged; client should use
        cached version. Do not include a body. Must accompany relevant caching
        headers (ETag / Last-Modified previously supplied).

        Args:
            content (Any, optional): Ignored; body omitted. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Ignored. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include cache validators. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 304.
        """
        return self.send_message_on_status(status=304, content=content, content_type=content_type, headers=headers)

    def use_proxy(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 305 Use Proxy HTTP response.

        Deprecated in modern HTTP; originally indicated resource must be
        accessed through a specified proxy. Avoid using; retain only for legacy
        compatibility contexts.

        Args:
            content (Any, optional): Advisory note. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type for body. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Legacy metadata. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 305.
        """
        return self.send_message_on_status(status=305, content=content, content_type=content_type, headers=headers)

    def switch_proxy(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 306 Switch Proxy HTTP response.

        Reserved / unused status code kept for historical reasons. Should not
        appear in new applications. Provided here for completeness.

        Args:
            content (Any, optional): Typically empty. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 306.
        """
        return self.send_message_on_status(status=306, content=content, content_type=content_type, headers=headers)

    def temporary_redirect(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 307 Temporary Redirect HTTP response.

        Indicates resource temporarily at another URI; original method and body
        must be reused. Safer than 302 for non-GET requests. Include `Location`.

        Args:
            content (Any, optional): Optional description. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Must include `Location`. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 307.
        """
        return self.send_message_on_status(status=307, content=content, content_type=content_type, headers=headers)

    def permanent_redirect(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 308 Permanent Redirect HTTP response.

        Resource permanently moved; future requests should use new URI. Unlike
        301, preserves method and body. Include `Location` header and migrate
        clients accordingly.

        Args:
            content (Any, optional): Optional explanation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Should include `Location`. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 308.
        """
        return self.send_message_on_status(status=308, content=content, content_type=content_type, headers=headers)

    """ 4xx client error """

    def bad_request(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 400 Bad Request HTTP response.

        This response indicates that the server cannot process the request due to
        client error (e.g., malformed request syntax, invalid request message framing,
        or deceptive request routing).

        Args:
            content (Any, optional): The content to send. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): Content type as `DataTypes` member, known key (e.g., "json"), or raw MIME string. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Additional headers to include. Defaults to None.

        Returns:
            Response: A FastAPI Response object with status 400.
        """
        return self.send_message_on_status(status=400, content=content, content_type=content_type, headers=headers)

    def unauthorized(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 401 Unauthorized HTTP response.

        This response indicates that the request requires user authentication.
        The client should authenticate itself to get the requested response.

        Args:
            content (Any, optional): The content to send. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): Content type as `DataTypes` member, known key (e.g., "json"), or raw MIME string. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Additional headers to include. Defaults to None.

        Returns:
            Response: A FastAPI Response object with status 401.
        """
        return self.send_message_on_status(status=401, content=content, content_type=content_type, headers=headers)

    def payment_required(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 402 Payment Required HTTP response.

        Reserved for future digital payment flows; occasionally repurposed for
        quota or subscription enforcement. Provide actionable guidance for
        completing payment or upgrading.

        Args:
            content (Any, optional): Payment or upgrade instructions. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include billing references. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 402.
        """
        return self.send_message_on_status(status=402, content=content, content_type=content_type, headers=headers)

    def forbidden(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 403 Forbidden HTTP response.

        Indicates authenticated client lacks permission for the target resource.
        Use for authorization failures (role / ACL issues). Do not reveal
        sensitive existence details beyond necessity.

        Args:
            content (Any, optional): Permission denial explanation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Additional security headers. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 403.
        """
        return self.send_message_on_status(status=403, content=content, content_type=content_type, headers=headers)

    def not_found(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 404 Not Found HTTP response.

        Indicates the server cannot locate the target resource. Use for missing
        identifiers, deleted objects, or invalid routes. Avoid leaking internal
        structure; keep messages generic for security-sensitive contexts.

        Args:
            content (Any, optional): User-facing explanation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 404.
        """
        return self.send_message_on_status(status=404, content=content, content_type=content_type, headers=headers)

    def method_not_allowed(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 405 Method Not Allowed HTTP response.

        Method exists but is not permitted for this resource (e.g., POST on a
        read-only endpoint). Include an `Allow` header enumerating supported
        methods.

        Args:
            content (Any, optional): Optional guidance. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Should include `Allow`. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 405.
        """
        return self.send_message_on_status(status=405, content=content, content_type=content_type, headers=headers)

    def not_acceptable(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 406 Not Acceptable HTTP response.

        Indicates server cannot produce a representation matching client's
        proactive content negotiation headers. Suggest alternative formats when
        possible.

        Args:
            content (Any, optional): Negotiation failure details. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include `Vary`. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 406.
        """
        return self.send_message_on_status(status=406, content=content, content_type=content_type, headers=headers)

    def proxy_authentication_required(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 407 Proxy Authentication Required HTTP response.

        Client must authenticate with a proxy before request can proceed.
        Include `Proxy-Authenticate` challenge. Similar flow to 401 but for
        intermediary.

        Args:
            content (Any, optional): Challenge/description. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Should include `Proxy-Authenticate`. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 407.
        """
        return self.send_message_on_status(status=407, content=content, content_type=content_type, headers=headers)

    def request_timeout(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 408 Request Timeout HTTP response.

        Server terminated an idle connection because the client did not produce
        a complete request in time. Client may retry. Consider adjusting timeouts
        for large uploads.

        Args:
            content (Any, optional): Timeout explanation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 408.
        """
        return self.send_message_on_status(status=408, content=content, content_type=content_type, headers=headers)

    def conflict(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 409 Conflict HTTP response.

        Indicates request conflicts with current resource state (e.g., version
        mismatch, duplicate unique field). Provide resolution instructions or a
        representation of the current state.

        Args:
            content (Any, optional): Conflict description. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include `ETag`. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 409.
        """
        return self.send_message_on_status(status=409, content=content, content_type=content_type, headers=headers)

    def gone(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 410 Gone HTTP response.

        Resource intentionally removed and no forwarding address known. Different
        from 404 by permanence. Useful for deprecated APIs or purged content.

        Args:
            content (Any, optional): Removal explanation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 410.
        """
        return self.send_message_on_status(status=410, content=content, content_type=content_type, headers=headers)

    def length_required(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 411 Length Required HTTP response.

        Server refuses request without a valid `Content-Length` header when one
        is mandated. Client should resend with explicit length.

        Args:
            content (Any, optional): Instruction to include length. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 411.
        """
        return self.send_message_on_status(status=411, content=content, content_type=content_type, headers=headers)

    def precondition_failed(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 412 Precondition Failed HTTP response.

        One or more conditional request headers (If-Match, If-Unmodified-Since)
        did not match resource state, aborting the operation. Client should
        refetch representation and retry.

        Args:
            content (Any, optional): Failed condition explanation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include updated validators. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 412.
        """
        return self.send_message_on_status(status=412, content=content, content_type=content_type, headers=headers)

    def payload_too_large(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 413 Payload Too Large HTTP response.

        Request entity exceeds server limits (size caps, upload restrictions).
        Provide maximum allowed size to assist client correction.

        Args:
            content (Any, optional): Size limit details. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include limit hints. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 413.
        """
        return self.send_message_on_status(status=413, content=content, content_type=content_type, headers=headers)

    def uri_too_long(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 414 URI Too Long HTTP response.

        Target URI exceeds server parsing or policy limits (often due to huge
        query strings). Recommend switching to POST with body parameters.

        Args:
            content (Any, optional): Advisory message. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 414.
        """
        return self.send_message_on_status(status=414, content=content, content_type=content_type, headers=headers)

    def unsupported_media_type(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 415 Unsupported Media Type HTTP response.

        Request's `Content-Type` not supported for target resource (e.g., image
        upload in unsupported format). List accepted types where feasible.

        Args:
            content (Any, optional): Supported formats guidance. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include `Accept-Post`. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 415.
        """
        return self.send_message_on_status(status=415, content=content, content_type=content_type, headers=headers)

    def range_not_satisfiable(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 416 Range Not Satisfiable HTTP response.

        Client requested a byte range outside resource bounds. Include a
        `Content-Range` header indicating valid size to guide retries.

        Args:
            content (Any, optional): Range error details. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Should include `Content-Range`. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 416.
        """
        return self.send_message_on_status(status=416, content=content, content_type=content_type, headers=headers)

    def expectation_failed(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 417 Expectation Failed HTTP response.

        Server cannot meet requirements of the `Expect` request-header (commonly
        `100-continue`). Client should adjust headers or remove Expect.

        Args:
            content (Any, optional): Explanation of unmet expectation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 417.
        """
        return self.send_message_on_status(status=417, content=content, content_type=content_type, headers=headers)

    def im_a_teapot(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 418 I'm a Teapot HTTP response.

        April Fools RFC (RFC 2324) humorous code. Occasionally used for rate
        limiting or easter eggs. Avoid in production protocols unless intentional.

        Args:
            content (Any, optional): Playful message. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 418.
        """
        return self.send_message_on_status(status=418, content=content, content_type=content_type, headers=headers)

    def page_expired(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 419 Page Expired HTTP response.

        Non-standard code sometimes used to indicate expired session or CSRF
        token invalidation. Provide re-authentication or refresh guidance.

        Args:
            content (Any, optional): Expiration details. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include session hints. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 419.
        """
        return self.send_message_on_status(status=419, content=content, content_type=content_type, headers=headers)

    def enhance_your_calm(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 420 Enhance Your Calm HTTP response.

        Non-standard (Twitter usage) for rate limiting or abuse detection.
        Provide throttling window and retry-after guidance where possible.

        Args:
            content (Any, optional): Rate limit explanation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include `Retry-After`. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 420.
        """
        return self.send_message_on_status(status=420, content=content, content_type=content_type, headers=headers)

    def misdirected_request(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 421 Misdirected Request HTTP response.

        Request was directed to a server incapable of producing a response (e.g.,
        SNI routing mismatch). Client should retry against correct origin.

        Args:
            content (Any, optional): Routing error details. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 421.
        """
        return self.send_message_on_status(status=421, content=content, content_type=content_type, headers=headers)

    def unprocessable_entity(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 422 Unprocessable Entity HTTP response.

        Syntax is correct but semantic validation failed (e.g., domain rules,
        constraint violations). Return structured field error details to aid
        client correction.

        Args:
            content (Any, optional): Validation errors payload. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 422.
        """
        return self.send_message_on_status(status=422, content=content, content_type=content_type, headers=headers)

    def locked(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 423 Locked HTTP response.

        WebDAV: resource is locked and cannot be modified. Provide lock token or
        instructions for obtaining access if appropriate.

        Args:
            content (Any, optional): Lock state description. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include lock token reference. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 423.
        """
        return self.send_message_on_status(status=423, content=content, content_type=content_type, headers=headers)

    def failed_dependency(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 424 Failed Dependency HTTP response.

        WebDAV: a method failed because a prior request on which it depended
        failed. Use in batch or chained operations to clarify cascading errors.

        Args:
            content (Any, optional): Upstream failure details. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 424.
        """
        return self.send_message_on_status(status=424, content=content, content_type=content_type, headers=headers)

    def too_early(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 425 Too Early HTTP response.

        Indicates server is unwilling to risk replay of a request that might be
        unsafe if repeated (e.g., early data in TLS 1.3). Client should resend
        without early data.

        Args:
            content (Any, optional): Replay risk explanation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 425.
        """
        return self.send_message_on_status(status=425, content=content, content_type=content_type, headers=headers)

    def upgrade_required(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 426 Upgrade Required HTTP response.

        Client must switch to a different protocol (e.g., TLS, HTTP/2) to proceed.
        Include `Upgrade` header advertising acceptable protocols.

        Args:
            content (Any, optional): Upgrade instructions. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Should include `Upgrade`. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 426.
        """
        return self.send_message_on_status(status=426, content=content, content_type=content_type, headers=headers)

    def precondition_required(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 428 Precondition Required HTTP response.

        Server requires the request be conditional (e.g., to prevent lost updates
        in concurrent modifications). Client should include appropriate
        conditional headers (If-Match / If-Unmodified-Since).

        Args:
            content (Any, optional): Instruction to add conditions. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 428.
        """
        return self.send_message_on_status(status=428, content=content, content_type=content_type, headers=headers)

    def too_many_requests(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 429 Too Many Requests HTTP response.

        Rate limiting triggered. Provide retry guidance via `Retry-After` or
        quota headers. Distinguish per-user vs global limits where relevant.

        Args:
            content (Any, optional): Throttling explanation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Include rate limit metadata. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 429.
        """
        return self.send_message_on_status(status=429, content=content, content_type=content_type, headers=headers)

    def request_header_fields_too_large(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 431 Request Header Fields Too Large HTTP response.

        One or more header fields exceed size limits (security or performance
        constraints). Client should reduce header volume (cookies, custom
        metadata) and retry.

        Args:
            content (Any, optional): Reduction guidance. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 431.
        """
        return self.send_message_on_status(status=431, content=content, content_type=content_type, headers=headers)

    def unavailable_for_legal_reasons(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 451 Unavailable For Legal Reasons HTTP response.

        Resource unavailable due to legal demands (e.g., censorship, DMCA). Keep
        explanation minimal yet transparent. Avoid exposing sensitive legal
        references publicly.

        Args:
            content (Any, optional): Legal restriction notice. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include policy links. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 451.
        """
        return self.send_message_on_status(status=451, content=content, content_type=content_type, headers=headers)

    def invalid_token(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 498 Invalid Token HTTP response.

        Non-standard code occasionally used when token (API key / session) is
        malformed or expired but distinct from 401 semantics. Provide refresh
        / re-authentication instructions.

        Args:
            content (Any, optional): Token validity explanation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include security hints. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 498.
        """
        return self.send_message_on_status(status=498, content=content, content_type=content_type, headers=headers)

    """ 5xx server error"""

    def internal_server_error(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 500 Internal Server Error HTTP response.

        This response indicates that the server encountered an unexpected condition
        that prevented it from fulfilling the request.

        Args:
            content (Any, optional): The content to send. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): Content type as `DataTypes` member, known key (e.g., "json"), or raw MIME string. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Additional headers to include. Defaults to None.

        Returns:
            Response: A FastAPI Response object with status 500.
        """
        return self.send_message_on_status(status=500, content=content, content_type=content_type, headers=headers)

    def not_implemented(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 501 Not Implemented HTTP response.

        This response indicates that the server does not support the functionality
        required to fulfill the request.

        Args:
            content (Any, optional): The content to send. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (ContentTypeLike, optional): Content type as `DataTypes` member, known key (e.g., "json"), or raw MIME string. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Additional headers to include. Defaults to None.

        Returns:
            Response: A FastAPI Response object with status 501.
        """
        return self.send_message_on_status(status=501, content=content, content_type=content_type, headers=headers)

    def bad_gateway(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 502 Bad Gateway HTTP response.

        Upstream server returned an invalid / error response to a gateway or
        proxy. Client may retry; investigate upstream health. Include minimal
        diagnostic context if safe.

        Args:
            content (Any, optional): Upstream failure summary. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 502.
        """
        return self.send_message_on_status(status=502, content=content, content_type=content_type, headers=headers)

    def service_unavailable(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 503 Service Unavailable HTTP response.

        Server temporarily unable to handle the request (maintenance / overload).
        Provide `Retry-After` if known. Differentiate transient from permanent
        failure states.

        Args:
            content (Any, optional): Downtime notice. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include `Retry-After`. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 503.
        """
        return self.send_message_on_status(status=503, content=content, content_type=content_type, headers=headers)

    def gateway_timeout(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 504 Gateway Timeout HTTP response.

        Upstream server failed to respond in time to a gateway / proxy. Client
        may retry with backoff. Monitor latency and circuit breaker thresholds.

        Args:
            content (Any, optional): Timeout context. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 504.
        """
        return self.send_message_on_status(status=504, content=content, content_type=content_type, headers=headers)

    def http_version_not_supported(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 505 HTTP Version Not Supported HTTP response.

        Server rejects requested HTTP protocol version. Advise supported versions
        (e.g., HTTP/1.1, HTTP/2). Could imply need for TLS upgrade pathway.

        Args:
            content (Any, optional): Supported version info. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 505.
        """
        return self.send_message_on_status(status=505, content=content, content_type=content_type, headers=headers)

    def variant_also_negotiates(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 506 Variant Also Negotiates HTTP response.

        Internal configuration error: content negotiation process is itself
        negotiated recursively. Rare; indicates misconfigured server variant
        selection logic.

        Args:
            content (Any, optional): Diagnostic hint. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 506.
        """
        return self.send_message_on_status(status=506, content=content, content_type=content_type, headers=headers)

    def insufficient_storage(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 507 Insufficient Storage HTTP response.

        WebDAV / extension: server cannot store the representation needed to
        complete the request. Suggest freeing space or upgrading quotas.

        Args:
            content (Any, optional): Storage limitation explanation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include quota metadata. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 507.
        """
        return self.send_message_on_status(status=507, content=content, content_type=content_type, headers=headers)

    def loop_detected(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 508 Loop Detected HTTP response.

        WebDAV: infinite loop encountered while processing a request (e.g.,
        cyclic bindings). Client should adjust request path or structure.

        Args:
            content (Any, optional): Loop diagnostic. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 508.
        """
        return self.send_message_on_status(status=508, content=content, content_type=content_type, headers=headers)

    def bandwidth_limit_exceeded(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 509 Bandwidth Limit Exceeded HTTP response.

        Non-standard: hosting provider quota surpassed. Provide reset window or
        upgrade path. Distinguish from transient network congestion.

        Args:
            content (Any, optional): Bandwidth quota details. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include usage metrics. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 509.
        """
        return self.send_message_on_status(status=509, content=content, content_type=content_type, headers=headers)

    def not_extended(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 510 Not Extended HTTP response.

        Further extensions to the request are required for it to be fulfilled
        (e.g., additional protocol capabilities). Rare; provide explicit next
        steps.

        Args:
            content (Any, optional): Extension requirement explanation. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): Headers map. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 510.
        """
        return self.send_message_on_status(status=510, content=content, content_type=content_type, headers=headers)

    def network_authentication_required(self, content: Any = CONST.DEFAULT_MESSAGE_CONTENT, *, content_type: ContentTypeLike = CONST.DEFAULT_MESSAGE_TYPE, headers: Optional[Mapping[str, str]] = None) -> Response:
        """
        Send a 511 Network Authentication Required HTTP response.

        Client must authenticate to gain network access (e.g., captive portal).
        Provide login or acceptance instructions. After completion, original
        request can be retried.

        Args:
            content (Any, optional): Network access instructions. Defaults to CONST.DEFAULT_MESSAGE_CONTENT.
            content_type (str, optional): Media type. Defaults to CONST.DEFAULT_MESSAGE_TYPE.
            headers (Mapping[str, str], optional): May include portal references. Defaults to None.

        Returns:
            Response: FastAPI Response object with status 511.
        """
        return self.send_message_on_status(status=511, content=content, content_type=content_type, headers=headers)


HCI = HttpCodes()
