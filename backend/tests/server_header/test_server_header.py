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
# FILE: test_server_header.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Unit tests for the ServerHeaders class to ensure proper header generation for different content types.
# // AR
# +==== END CatFeeder =================+
"""
import pytest

try:
    from libs.server_header import ServerHeaders
    from libs.server_header import server_header_constants as HEADER_CONST
except Exception:
    from src.libs.server_header import ServerHeaders
    from src.libs.server_header import server_header_constants as HEADER_CONST


@pytest.fixture()
def headers_default():
    """Create ServerHeaders instance with default parameters."""
    return ServerHeaders()


@pytest.fixture()
def headers_custom():
    """Create ServerHeaders instance with custom parameters."""
    return ServerHeaders(
        host="127.0.0.1",
        port=8000,
        app_name="TestApp",
        error=1,
        success=2,
        debug=True
    )


class TestServerHeadersInitialization:
    """Test ServerHeaders initialization."""

    def test_init_default_values(self):
        """Verify default initialization values."""
        headers = ServerHeaders()
        assert headers.host == "0.0.0.0"
        assert headers.port == 5000
        assert headers.app_name == "Asperguide"
        assert headers.error == 84
        assert headers.success == 0
        assert headers.debug is False

    def test_init_custom_values(self, headers_custom):
        """Verify custom initialization values."""
        assert headers_custom.host == "127.0.0.1"
        assert headers_custom.port == 8000
        assert headers_custom.app_name == "TestApp"
        assert headers_custom.error == 1
        assert headers_custom.success == 2
        assert headers_custom.debug is True

    def test_init_partial_custom_values(self):
        """Verify partial custom initialization."""
        headers = ServerHeaders(app_name="CustomApp", port=9000)
        assert headers.app_name == "CustomApp"
        assert headers.port == 9000
        assert headers.host == "0.0.0.0"
        assert headers.error == 84


class TestBaseSecurityHeaders:
    """Test base security headers common to all responses."""

    def test_base_security_headers_contains_required_fields(self, headers_default):
        """Verify base security headers contain all required security fields."""
        headers = headers_default._base_security_headers()

        assert HEADER_CONST.HEADER_APP_NAME in headers
        assert HEADER_CONST.CONTENT_TYPE in headers
        assert HEADER_CONST.FRAME_OPTIONS in headers
        assert HEADER_CONST.XSS_PROTECTION in headers
        assert HEADER_CONST.REFERRER_POLICY in headers

    def test_base_security_headers_correct_values(self, headers_default):
        """Verify base security headers have correct values."""
        headers = headers_default._base_security_headers()

        assert headers[HEADER_CONST.HEADER_APP_NAME] == "Asperguide"
        assert headers[HEADER_CONST.CONTENT_TYPE] == "nosniff"
        assert headers[HEADER_CONST.FRAME_OPTIONS] == "DENY"
        assert headers[HEADER_CONST.XSS_PROTECTION] == "1; mode=block"
        assert headers[HEADER_CONST.REFERRER_POLICY] == "strict-origin-when-cross-origin"

    def test_base_security_headers_custom_app_name(self, headers_custom):
        """Verify custom app name is included in base security headers."""
        headers = headers_custom._base_security_headers()
        assert headers[HEADER_CONST.HEADER_APP_NAME] == "TestApp"

    def test_get_app_name_str_with_string(self):
        """Test _get_app_name_str with string app_name."""
        headers = ServerHeaders(app_name="MyApp")
        assert headers._get_app_name_str() == "MyApp"

    def test_get_app_name_str_with_non_string(self):
        """Test _get_app_name_str converts non-string to string."""
        headers = ServerHeaders()
        headers.app_name = 123
        assert headers._get_app_name_str() == "123"


class TestJSONHeaders:
    """Test JSON response headers."""

    def test_for_json_contains_base_headers(self, headers_default):
        """Verify JSON headers contain base security headers."""
        headers = headers_default.for_json()

        assert HEADER_CONST.HEADER_APP_NAME in headers
        assert HEADER_CONST.CONTENT_TYPE in headers
        assert HEADER_CONST.FRAME_OPTIONS in headers

    def test_for_json_no_cache_policy(self, headers_default):
        """Verify JSON headers have aggressive no-cache policy."""
        headers = headers_default.for_json()

        assert HEADER_CONST.CACHE_CONTROL in headers
        assert "no-cache" in headers[HEADER_CONST.CACHE_CONTROL]
        assert "no-store" in headers[HEADER_CONST.CACHE_CONTROL]
        assert "must-revalidate" in headers[HEADER_CONST.CACHE_CONTROL]
        assert headers[HEADER_CONST.PRAGMA] == "no-cache"
        assert headers[HEADER_CONST.EXPIRES] == "0"

    def test_for_json_returns_dict(self, headers_default):
        """Verify for_json returns a dictionary."""
        headers = headers_default.for_json()
        assert isinstance(headers, dict)


class TestTextHeaders:
    """Test plain text response headers."""

    def test_for_text_contains_base_headers(self, headers_default):
        """Verify text headers contain base security headers."""
        headers = headers_default.for_text()

        assert HEADER_CONST.HEADER_APP_NAME in headers
        assert HEADER_CONST.CONTENT_TYPE in headers

    def test_for_text_no_cache_policy(self, headers_default):
        """Verify text headers have no-cache policy."""
        headers = headers_default.for_text()

        assert HEADER_CONST.CACHE_CONTROL in headers
        assert "no-cache" in headers[HEADER_CONST.CACHE_CONTROL]
        assert "no-store" in headers[HEADER_CONST.CACHE_CONTROL]

    def test_for_text_returns_dict(self, headers_default):
        """Verify for_text returns a dictionary."""
        headers = headers_default.for_text()
        assert isinstance(headers, dict)


class TestHTMLHeaders:
    """Test HTML response headers."""

    def test_for_html_contains_base_headers(self, headers_default):
        """Verify HTML headers contain base security headers."""
        headers = headers_default.for_html()

        assert HEADER_CONST.HEADER_APP_NAME in headers
        assert HEADER_CONST.CONTENT_TYPE in headers

    def test_for_html_has_content_security_policy(self, headers_default):
        """Verify HTML headers include Content-Security-Policy."""
        headers = headers_default.for_html()

        assert HEADER_CONST.CONTENT_SECURITY_POLICY in headers
        csp = headers[HEADER_CONST.CONTENT_SECURITY_POLICY]
        assert "default-src 'self'" in csp
        assert "script-src" in csp
        assert "style-src" in csp

    def test_for_html_no_cache_policy(self, headers_default):
        """Verify HTML headers have no-cache policy."""
        headers = headers_default.for_html()

        assert "no-cache" in headers[HEADER_CONST.CACHE_CONTROL]


class TestXMLHeaders:
    """Test XML response headers."""

    def test_for_xml_contains_base_headers(self, headers_default):
        """Verify XML headers contain base security headers."""
        headers = headers_default.for_xml()

        assert HEADER_CONST.HEADER_APP_NAME in headers
        assert HEADER_CONST.CONTENT_TYPE in headers

    def test_for_xml_no_cache_policy(self, headers_default):
        """Verify XML headers have no-cache policy."""
        headers = headers_default.for_xml()

        assert "no-cache" in headers[HEADER_CONST.CACHE_CONTROL]
        assert "no-store" in headers[HEADER_CONST.CACHE_CONTROL]


class TestStaticAssetHeaders:
    """Test headers for static assets (CSS, JavaScript)."""

    def test_for_css_long_cache(self, headers_default):
        """Verify CSS headers have long-term caching (1 year)."""
        headers = headers_default.for_css()

        assert HEADER_CONST.CACHE_CONTROL in headers
        assert "public" in headers[HEADER_CONST.CACHE_CONTROL]
        assert "max-age=31536000" in headers[HEADER_CONST.CACHE_CONTROL]
        assert "immutable" in headers[HEADER_CONST.CACHE_CONTROL]

    def test_for_javascript_long_cache(self, headers_default):
        """Verify JavaScript headers have long-term caching (1 year)."""
        headers = headers_default.for_javascript()

        assert HEADER_CONST.CACHE_CONTROL in headers
        assert "public" in headers[HEADER_CONST.CACHE_CONTROL]
        assert "max-age=31536000" in headers[HEADER_CONST.CACHE_CONTROL]
        assert "immutable" in headers[HEADER_CONST.CACHE_CONTROL]

    def test_css_and_js_have_base_security_headers(self, headers_default):
        """Verify CSS and JS headers contain base security headers."""
        css_headers = headers_default.for_css()
        js_headers = headers_default.for_javascript()

        assert HEADER_CONST.HEADER_APP_NAME in css_headers
        assert HEADER_CONST.HEADER_APP_NAME in js_headers


class TestMediaHeaders:
    """Test headers for media files (images, video, audio)."""

    def test_for_image_24h_cache(self, headers_default):
        """Verify image headers have 24-hour caching."""
        headers = headers_default.for_image()

        assert "public" in headers[HEADER_CONST.CACHE_CONTROL]
        assert "max-age=86400" in headers[HEADER_CONST.CACHE_CONTROL]

    def test_for_image_sameorigin_frame_options(self, headers_default):
        """Verify image headers allow SAMEORIGIN frame embedding."""
        headers = headers_default.for_image()

        assert headers[HEADER_CONST.FRAME_OPTIONS] == "SAMEORIGIN"

    def test_for_video_range_support(self, headers_default):
        """Verify video headers support byte-range requests."""
        headers = headers_default.for_video()

        assert HEADER_CONST.ACCEPT_RANGES in headers
        assert headers[HEADER_CONST.ACCEPT_RANGES] == "bytes"

    def test_for_video_24h_cache(self, headers_default):
        """Verify video headers have 24-hour caching."""
        headers = headers_default.for_video()

        assert "max-age=86400" in headers[HEADER_CONST.CACHE_CONTROL]

    def test_for_video_sameorigin_frame_options(self, headers_default):
        """Verify video headers allow SAMEORIGIN frame embedding."""
        headers = headers_default.for_video()

        assert headers[HEADER_CONST.FRAME_OPTIONS] == "SAMEORIGIN"

    def test_for_audio_range_support(self, headers_default):
        """Verify audio headers support byte-range requests."""
        headers = headers_default.for_audio()

        assert headers[HEADER_CONST.ACCEPT_RANGES] == "bytes"

    def test_for_audio_24h_cache(self, headers_default):
        """Verify audio headers have 24-hour caching."""
        headers = headers_default.for_audio()

        assert "max-age=86400" in headers[HEADER_CONST.CACHE_CONTROL]


class TestFileDownloadHeaders:
    """Test headers for file downloads."""

    def test_for_file_default(self, headers_default):
        """Verify file download headers with default parameters."""
        headers = headers_default.for_file()

        assert HEADER_CONST.CACHE_CONTROL in headers
        assert "max-age=3600" in headers[HEADER_CONST.CACHE_CONTROL]

    def test_for_file_with_filename(self, headers_default):
        """Verify file download headers with custom filename."""
        headers = headers_default.for_file(filename="report.pdf")

        assert HEADER_CONST.CONTENT_DISPOSITION in headers
        assert 'attachment; filename="report.pdf"' in headers[HEADER_CONST.CONTENT_DISPOSITION]

    def test_for_file_without_filename(self, headers_default):
        """Verify file download headers without filename."""
        headers = headers_default.for_file()

        assert HEADER_CONST.CONTENT_DISPOSITION not in headers

    def test_for_file_empty_filename(self, headers_default):
        """Verify file download headers with empty filename string."""
        headers = headers_default.for_file(filename="")

        assert HEADER_CONST.CONTENT_DISPOSITION not in headers


class TestPDFHeaders:
    """Test headers for PDF responses."""

    def test_for_pdf_default_download(self, headers_default):
        """Verify PDF headers default to download mode."""
        headers = headers_default.for_pdf()

        assert HEADER_CONST.CONTENT_DISPOSITION in headers
        assert 'attachment; filename="document.pdf"' in headers[HEADER_CONST.CONTENT_DISPOSITION]

    def test_for_pdf_custom_filename_download(self, headers_default):
        """Verify PDF headers with custom filename in download mode."""
        headers = headers_default.for_pdf(filename="myfile.pdf", inline=False)

        assert 'attachment; filename="myfile.pdf"' in headers[HEADER_CONST.CONTENT_DISPOSITION]

    def test_for_pdf_inline_mode(self, headers_default):
        """Verify PDF headers in inline mode."""
        headers = headers_default.for_pdf(inline=True)

        assert HEADER_CONST.CONTENT_DISPOSITION in headers
        assert 'inline; filename="document.pdf"' in headers[HEADER_CONST.CONTENT_DISPOSITION]

    def test_for_pdf_inline_custom_filename(self, headers_default):
        """Verify PDF headers in inline mode with custom filename."""
        headers = headers_default.for_pdf(filename="custom.pdf", inline=True)

        assert 'inline; filename="custom.pdf"' in headers[HEADER_CONST.CONTENT_DISPOSITION]

    def test_for_pdf_1hour_cache(self, headers_default):
        """Verify PDF headers have 1-hour caching."""
        headers = headers_default.for_pdf()

        assert "max-age=3600" in headers[HEADER_CONST.CACHE_CONTROL]


class TestStreamingHeaders:
    """Test headers for streaming responses."""

    def test_for_stream_range_support(self, headers_default):
        """Verify stream headers support byte-range requests."""
        headers = headers_default.for_stream()

        assert HEADER_CONST.ACCEPT_RANGES in headers
        assert headers[HEADER_CONST.ACCEPT_RANGES] == "bytes"

    def test_for_stream_no_cache(self, headers_default):
        """Verify stream headers have no-cache policy."""
        headers = headers_default.for_stream()

        assert "no-cache" in headers[HEADER_CONST.CACHE_CONTROL]

    def test_for_stream_contains_base_headers(self, headers_default):
        """Verify stream headers contain base security headers."""
        headers = headers_default.for_stream()

        assert HEADER_CONST.HEADER_APP_NAME in headers


class TestCSVHeaders:
    """Test headers for CSV export responses."""

    def test_for_csv_default_filename(self, headers_default):
        """Verify CSV headers with default filename."""
        headers = headers_default.for_csv()

        assert HEADER_CONST.CONTENT_DISPOSITION in headers
        assert 'attachment; filename="export.csv"' in headers[HEADER_CONST.CONTENT_DISPOSITION]

    def test_for_csv_custom_filename(self, headers_default):
        """Verify CSV headers with custom filename."""
        headers = headers_default.for_csv(filename="data.csv")

        assert 'attachment; filename="data.csv"' in headers[HEADER_CONST.CONTENT_DISPOSITION]

    def test_for_csv_no_cache(self, headers_default):
        """Verify CSV headers have no-cache policy."""
        headers = headers_default.for_csv()

        assert "no-cache" in headers[HEADER_CONST.CACHE_CONTROL]
        assert "no-store" in headers[HEADER_CONST.CACHE_CONTROL]
        assert "must-revalidate" in headers[HEADER_CONST.CACHE_CONTROL]

    def test_for_csv_contains_base_headers(self, headers_default):
        """Verify CSV headers contain base security headers."""
        headers = headers_default.for_csv()

        assert HEADER_CONST.HEADER_APP_NAME in headers


class TestRedirectHeaders:
    """Test headers for redirect responses."""

    def test_for_redirect_minimal_headers(self, headers_default):
        """Verify redirect headers contain minimal required headers."""
        headers = headers_default.for_redirect()

        assert HEADER_CONST.HEADER_APP_NAME in headers
        assert HEADER_CONST.CACHE_CONTROL in headers

    def test_for_redirect_no_full_security_headers(self, headers_default):
        """Verify redirect headers don't include full security headers."""
        headers = headers_default.for_redirect()

        # Redirects should have minimal headers
        assert HEADER_CONST.CONTENT_TYPE not in headers
        assert HEADER_CONST.FRAME_OPTIONS not in headers

    def test_for_redirect_no_cache(self, headers_default):
        """Verify redirect headers have no-cache policy."""
        headers = headers_default.for_redirect()

        assert "no-cache" in headers[HEADER_CONST.CACHE_CONTROL]
        assert "no-store" in headers[HEADER_CONST.CACHE_CONTROL]

    def test_for_redirect_app_name(self, headers_default):
        """Verify redirect headers include app name."""
        headers = headers_default.for_redirect()

        assert headers[HEADER_CONST.HEADER_APP_NAME] == "Asperguide"


class TestFormHeaders:
    """Test headers for form data responses."""

    def test_for_form_contains_base_headers(self, headers_default):
        """Verify form headers contain base security headers."""
        headers = headers_default.for_form()

        assert HEADER_CONST.HEADER_APP_NAME in headers
        assert HEADER_CONST.CONTENT_TYPE in headers

    def test_for_form_no_cache(self, headers_default):
        """Verify form headers have no-cache policy."""
        headers = headers_default.for_form()

        assert "no-cache" in headers[HEADER_CONST.CACHE_CONTROL]
        assert "no-store" in headers[HEADER_CONST.CACHE_CONTROL]
        assert "must-revalidate" in headers[HEADER_CONST.CACHE_CONTROL]

    def test_for_form_returns_dict(self, headers_default):
        """Verify for_form returns a dictionary."""
        headers = headers_default.for_form()
        assert isinstance(headers, dict)


class TestHeadersConsistency:
    """Test consistency across different header generation methods."""

    def test_all_methods_return_dict(self, headers_default):
        """Verify all header methods return dictionaries."""
        methods = [
            headers_default.for_json,
            headers_default.for_text,
            headers_default.for_html,
            headers_default.for_xml,
            headers_default.for_css,
            headers_default.for_javascript,
            headers_default.for_image,
            headers_default.for_file,
            headers_default.for_pdf,
            headers_default.for_stream,
            headers_default.for_video,
            headers_default.for_audio,
            headers_default.for_csv,
            headers_default.for_redirect,
            headers_default.for_form,
        ]

        for method in methods:
            result = method()
            assert isinstance(
                result, dict), f"{method.__name__} did not return a dict"

    def test_all_methods_include_app_name(self, headers_custom):
        """Verify all header methods include the app name."""
        methods = [
            headers_custom.for_json,
            headers_custom.for_text,
            headers_custom.for_html,
            headers_custom.for_xml,
            headers_custom.for_css,
            headers_custom.for_javascript,
            headers_custom.for_image,
            headers_custom.for_pdf,
            headers_custom.for_stream,
            headers_custom.for_video,
            headers_custom.for_audio,
            headers_custom.for_csv,
            headers_custom.for_redirect,
            headers_custom.for_form,
        ]

        for method in methods:
            headers = method()
            assert HEADER_CONST.HEADER_APP_NAME in headers
            assert headers[HEADER_CONST.HEADER_APP_NAME] == "TestApp"

    def test_headers_are_independent_instances(self, headers_default):
        """Verify each call returns independent header dictionaries."""
        headers1 = headers_default.for_json()
        headers2 = headers_default.for_json()

        # Modify one and verify the other is unchanged
        headers1["X-Custom"] = "value"
        assert "X-Custom" not in headers2

    def test_different_methods_dont_share_references(self, headers_default):
        """Verify different methods don't share header dictionary references."""
        json_headers = headers_default.for_json()
        text_headers = headers_default.for_text()

        json_headers["X-Custom-JSON"] = "json-value"
        assert "X-Custom-JSON" not in text_headers


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_special_characters_in_filename(self, headers_default):
        """Verify handling of special characters in filenames."""
        headers = headers_default.for_file(filename='report_2025-01-11.pdf')
        assert 'report_2025-01-11.pdf' in headers[HEADER_CONST.CONTENT_DISPOSITION]

    def test_special_characters_in_app_name(self):
        """Verify handling of special characters in app name."""
        headers = ServerHeaders(app_name="App-With-Special_Chars@123")
        base_headers = headers._base_security_headers()
        assert base_headers[HEADER_CONST.HEADER_APP_NAME] == "App-With-Special_Chars@123"

    def test_pdf_filename_with_spaces(self, headers_default):
        """Verify PDF filename handling with spaces."""
        headers = headers_default.for_pdf(filename="My Document.pdf")
        assert 'attachment; filename="My Document.pdf"' in headers[HEADER_CONST.CONTENT_DISPOSITION]

    def test_csv_filename_with_special_chars(self, headers_default):
        """Verify CSV filename handling with special characters."""
        headers = headers_default.for_csv(filename="report_2025-01-11.csv")
        assert 'report_2025-01-11.csv' in headers[HEADER_CONST.CONTENT_DISPOSITION]

    def test_large_max_age_values(self, headers_default):
        """Verify max-age values are correct for long cache periods."""
        headers = headers_default.for_css()
        # 1 year = 31536000 seconds
        assert "31536000" in headers[HEADER_CONST.CACHE_CONTROL]

    def test_zero_port(self):
        """Verify initialization with zero port."""
        headers = ServerHeaders(port=0)
        assert headers.port == 0

    def test_empty_app_name(self):
        """Verify initialization with empty app name."""
        headers = ServerHeaders(app_name="")
        base_headers = headers._base_security_headers()
        assert base_headers[HEADER_CONST.HEADER_APP_NAME] == ""
