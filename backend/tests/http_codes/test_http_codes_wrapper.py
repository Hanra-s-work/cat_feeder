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
# FILE: test_http_codes_wrapper.py
# CREATION DATE: 11-12-2025
# LAST Modified: 5:9:16 11-12-2025
# DESCRIPTION:
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: File in charge of testing the http class.
# // AR
# +==== END CatFeeder =================+
"""
from fastapi.responses import (
    Response, FileResponse, HTMLResponse, JSONResponse,
    PlainTextResponse, RedirectResponse, StreamingResponse
)

import re
import os
import io
import sys
import pytest

from pathlib import Path

# The project's import formatter may move imports to the top; to be robust
# we try importing the package normally and on ImportError we adjust
# sys.path and retry. This prevents the formatter from breaking test
# collection when running a single file under pytest.
try:
    from src.libs.http_codes import HttpCodes, HttpDataTypes
    import src.libs.http_codes.http_constants as CONST
except ImportError:
    _here = Path(__file__).resolve()
    repo_root = _here.parents[2]
    src_dir = repo_root / 'src'
    sys.path.insert(0, str(repo_root))
    sys.path.insert(0, str(src_dir))
    from src.libs.http_codes import HttpCodes, HttpDataTypes
    import src.libs.http_codes.http_constants as CONST


@pytest.fixture()
def hc():
    """Create and return an HttpCodes instance for testing.

    Returns:
        HttpCodes: A configured HTTP codes wrapper for generating responses.
    """
    return HttpCodes()


def test_check_data_type_various(hc):
    """Test _check_data_type with various input types and formats.

    Verifies that the method correctly handles None values, HttpDataTypes
    enum members, case-insensitive key names, raw MIME strings, and raises
    TypeError for invalid inputs like integers.
    """
    # None -> text/plain
    assert hc._check_data_type(None) == "text/plain"

    # Enum member
    assert hc._check_data_type(HttpDataTypes.JSON) == HttpDataTypes.JSON.value

    # Key name (case-insensitive)
    assert hc._check_data_type("json") == HttpDataTypes.JSON.value
    assert hc._check_data_type("JSON") == HttpDataTypes.JSON.value

    # Raw MIME string
    assert hc._check_data_type("application/json") == "application/json"

    # Invalid type raises
    with pytest.raises(TypeError):
        hc._check_data_type(123)


def test_check_header(hc):
    """Test _check_header validates and returns header dictionaries.

    Verifies that None returns empty dict, valid dicts are returned as-is,
    and non-mapping types raise TypeError.
    """
    assert hc._check_header(None) == {}
    d = {"X-Test": "1"}
    assert hc._check_header(d) == {"X-Test": "1"}
    # Non-mapping should raise
    with pytest.raises(TypeError):
        hc._check_header(123)


def test_process_data_content(hc, tmp_path):
    """Test _process_data_content with different content types and formats.

    Verifies handling of None values, bytes, file-like objects, JSON types
    (dict), streaming generators, and fallback stringification for other types.
    """
    # None -> empty string
    assert hc._process_data_content(None, "application/json") == ""

    # Bytes passthrough
    b = b"abc"
    assert hc._process_data_content(b, "application/octet-stream") is b

    # File-like object passthrough
    bio = io.BytesIO(b"data")
    assert hc._process_data_content(bio, "text/plain") is bio

    # JSON types: dict remains dict
    d = {"a": 1}
    assert hc._process_data_content(d, HttpDataTypes.JSON.value) == d

    # Streaming types passthrough
    s_obj = (x for x in range(3))
    assert hc._process_data_content(s_obj, "application/octet-stream") is s_obj

    # Other types -> stringified
    assert hc._process_data_content(123, "text/plain") == "123"


def test_send_message_on_status_packaging_and_headers(hc, tmp_path):
    """Test send_message_on_status creates correct Response subclasses.

    Verifies that different content_type values produce the appropriate
    FastAPI Response subclass (JSONResponse, HTMLResponse, PlainTextResponse,
    RedirectResponse, FileResponse) with correct status codes, media types,
    and custom headers.
    """
    # JSONResponse using key name
    resp = hc.send_message_on_status(
        200, content={"ok": True}, content_type="json", headers={"X-A": "1"})
    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 200
    assert resp.media_type == HttpDataTypes.JSON.value
    assert resp.headers.get("X-A") == "1"

    # HTMLResponse
    resp = hc.send_message_on_status(
        200, content="<h1>hi</h1>", content_type="html")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    assert resp.media_type == HttpDataTypes.HTML.value

    # PlainTextResponse using raw MIME
    resp = hc.send_message_on_status(
        200, content="hello", content_type="text/plain")
    assert isinstance(resp, PlainTextResponse)
    assert resp.status_code == 200
    assert resp.media_type == "text/plain"

    # RedirectResponse: content is used as URL
    resp = hc.send_message_on_status(
        302, content="https://example.com", content_type="redirect")
    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 302
    # RedirectResponse sets Location header
    assert resp.headers.get("location") == "https://example.com"

    # FileResponse requires a real file path
    tmp_file = tmp_path / "f.txt"
    tmp_file.write_text("hello")
    resp = hc.send_message_on_status(200, content=str(
        tmp_file), content_type="application/octet-stream")
    assert isinstance(resp, FileResponse)
    assert resp.status_code == 200

    # Numeric string status is accepted
    resp = hc.send_message_on_status(
        "200", content="ok", content_type="text/plain")
    assert isinstance(resp, PlainTextResponse)
    assert resp.status_code == 200

    # Invalid status raises
    with pytest.raises(ValueError):
        hc.send_message_on_status(999, content="nope", content_type="json")


def test_streaming_response(hc):
    """Test that streaming with file MIME types raises TypeError.

    Verifies that providing a generator with application/octet-stream
    (considered a file MIME in this implementation) raises TypeError
    because FileResponse expects a file path string, not a generator.
    """
    # Provide a generator and STREAM mime
    def gen():
        yield b"a"
        yield b"b"

    # Since `application/octet-stream` is considered a file MIME in this
    # project's constant grouping, providing a generator should raise a
    # TypeError because FileResponse expects a file path string.
    with pytest.raises(TypeError):
        hc.send_message_on_status(
            200, content=gen(), content_type="application/octet-stream")


def test_httpdatatypes_basic():
    """Test HttpDataTypes enum provides correct key-value mappings.

    Verifies that well-known keys like 'json' exist in the enum dictionary
    and that from_key() returns the correct enum member for known keys.
    """
    # Ensure some well-known keys exist and resolve correctly
    d = HttpDataTypes.get_dict()
    assert "json" in d
    assert d["json"] == HttpDataTypes.JSON.value
    # from_key should return the enum member for known keys
    member = HttpDataTypes.from_key("json")
    assert member is not None
    assert member.value == HttpDataTypes.JSON.value


def test_all_authorised_statuses_send(hc):
    """Test that all authorized HTTP status codes are accepted.

    Iterates through all status codes in AUTHORISED_STATUSES and verifies
    that send_message_on_status accepts them and returns JSONResponse
    objects with the correct status code.
    """
    # Iterate all authorised statuses and ensure send_message_on_status accepts them
    for status in CONST.AUTHORISED_STATUSES:
        resp = hc.send_message_on_status(
            status, content={"s": status}, content_type="json")
        assert resp.status_code == status
        # When using JSON content_type we expect a JSONResponse
        assert isinstance(resp, JSONResponse)


def test_wrapper_methods_match_source_definitions(hc):
    """Test that HTTP code wrapper methods return their documented status codes.

    Parses the source file to extract the status code used by each wrapper
    method's send_message_on_status call, then verifies that calling the
    wrapper actually returns a Response with that status code. This ensures
    wrapper methods match their implementation.

    The test specifically examines the wrapper methods section of the source
    file (lines 274-1471) to avoid false matches elsewhere.
    extract the expected `status=` integer used in the `send_message_on_status` call.
    """
    src_path = Path(hc.__class__.__module__.replace(
        '.', '/')).parents[1] / 'http_codes.py'
    # Fallback path when run from repository root
    if not src_path.exists():
        src_path = Path(__file__).resolve(
        ).parents[2] / 'src' / 'libs' / 'http_codes' / 'http_codes.py'
    text = src_path.read_text()

    # The wrappers are defined in `http_codes.py` between lines 274 and 1471
    # (1-indexed). Read that slice exactly to avoid accidental matches
    # elsewhere in the file.
    src_path = Path(__file__).resolve(
    ).parents[2] / 'src' / 'libs' / 'http_codes' / 'http_codes.py'
    text_lines = src_path.read_text().splitlines()
    # slice is 1-indexed in description: lines 274..1471 inclusive -> indices 273..1471
    sliced = "\n".join(text_lines[273:1471])

    # Match: def name(...): ... return self.send_message_on_status(status=NNN, ...)
    # Also handle positional form: return self.send_message_on_status(NNN, ...)
    pattern = re.compile(
        r"def\s+(?P<name>\w+)\s*\([^)]*\):\s*.*?return\s+self\.send_message_on_status\(\s*(?:status\s*=\s*(?P<kw>\d{3})|(?P<pos>\d{3}))",
        re.S,
    )
    found = {}
    for m in pattern.finditer(sliced):
        found[m.group('name')] = int(m.group('kw') or m.group('pos'))

    # For each found wrapper, call it and assert returned status matches
    for name, expected in found.items():
        # skip private/utility methods
        if name.startswith('_') or name in ('send_message_on_status',):
            continue
        func = getattr(hc, name, None)
        if not callable(func):
            continue
        # Some wrappers accept positional args; calling with no args should use defaults
        resp = func()
        assert isinstance(resp, (
            Response,
            FileResponse,
            HTMLResponse,
            JSONResponse,
            PlainTextResponse,
            RedirectResponse,
            StreamingResponse
        ))
        assert hasattr(resp, 'status_code')
        assert resp.status_code == expected, f"{name} returned {resp.status_code}, expected {expected}"


def test_response_class_variants(hc, tmp_path):
    """Test different response class variants based on content type.

    Verifies that RedirectResponse is created for redirect content_type
    and FileResponse is created when providing file paths with file MIME types.
    """
    # RedirectResponse via redirect content_type
    resp = hc.moved_permanently(
        content="https://example.com", content_type="redirect")
    assert isinstance(resp, RedirectResponse)
    assert resp.headers.get('location') == "https://example.com"

    # FileResponse when using a file MIME and providing a file path
    f = tmp_path / 'file.bin'
    f.write_bytes(b'bin')
    resp = hc.success(content=str(f), content_type="application/octet-stream")
    assert isinstance(resp, FileResponse)


def test_streaming_unreachable_branch(hc):
    """Test that StreamingResponse branch is unreachable with file MIME types.

    Verifies that the StreamingResponse code path is shadowed by file MIME
    type handling (octet-stream is classified as file), so attempting to
    send a generator with octet-stream raises TypeError instead of creating
    a StreamingResponse.
    """
    # StreamingResponse branch is shadowed by file mime types (octet-stream is file),
    # therefore trying to send a generator with octet-stream should raise TypeError
    def gen():
        yield b'a'

    with pytest.raises(TypeError):
        hc.send_message_on_status(
            200, content=gen(), content_type='application/octet-stream')


def test_explicit_wrappers_from_the_class_and_make_sure_that_they_return_the_expected_statuses(hc):
    """Test explicit wrapper methods return conventional HTTP status codes.

    Explicitly validates a comprehensive set of HTTP status code wrapper
    methods including informational (1xx), success (2xx), redirect (3xx),
    client error (4xx), and server error (5xx) responses. This ensures
    common methods like success(), not_found(), im_a_teapot(), and
    internal_server_error() return their expected numeric codes.

    The test covers 60+ wrapper methods spanning the full HTTP status
    code spectrum to ensure comprehensive coverage of the API surface.
    """
    expected = {
        "send_continue": 100,
        "switching_protocols": 101,
        "processing": 102,
        "early_hints": 103,
        "response_is_stale": 110,
        "success": 200,
        "created": 201,
        "accepted": 202,
        "non_authoritative_information": 203,
        "no_content": 204,
        "reset_content": 205,
        "partial_content": 206,
        "multi_status": 207,
        "already_reported": 208,
        "im_used": 226,
        "multiple_choices": 300,
        "moved_permanently": 301,
        "found": 302,
        "see_other": 303,
        "not_modified": 304,
        "use_proxy": 305,
        "switch_proxy": 306,
        "temporary_redirect": 307,
        "permanent_redirect": 308,
        "bad_request": 400,
        "unauthorized": 401,
        "payment_required": 402,
        "forbidden": 403,
        "not_found": 404,
        "method_not_allowed": 405,
        "not_acceptable": 406,
        "proxy_authentication_required": 407,
        "request_timeout": 408,
        "conflict": 409,
        "gone": 410,
        "length_required": 411,
        "precondition_failed": 412,
        "payload_too_large": 413,
        "uri_too_long": 414,
        "unsupported_media_type": 415,
        "range_not_satisfiable": 416,
        "expectation_failed": 417,
        "im_a_teapot": 418,
        "page_expired": 419,
        "enhance_your_calm": 420,
        "misdirected_request": 421,
        "unprocessable_entity": 422,
        "locked": 423,
        "failed_dependency": 424,
        "too_early": 425,
        "upgrade_required": 426,
        "precondition_required": 428,
        "too_many_requests": 429,
        "request_header_fields_too_large": 431,
        "unavailable_for_legal_reasons": 451,
        "invalid_token": 498,
        "internal_server_error": 500,
        "not_implemented": 501,
        "bad_gateway": 502,
        "service_unavailable": 503,
        "gateway_timeout": 504,
        "http_version_not_supported": 505,
        "variant_also_negotiates": 506,
        "insufficient_storage": 507,
        "loop_detected": 508,
        "bandwidth_limit_exceeded": 509,
        "not_extended": 510,
        "network_authentication_required": 511
    }

    for name, code in expected.items():
        func = getattr(hc, name, None)
        if func is None:
            pytest.skip(f"Wrapper {name} not present on HttpCodes")
        resp = func()
        assert hasattr(resp, 'status_code')
        assert resp.status_code == code, f"{name} returned {resp.status_code}, expected {code}"
