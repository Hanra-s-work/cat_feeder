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
# FILE: test_common_constants.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Unit tests for the common constants module.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Test suite for common documentation constants and utilities.
# // AR
# +==== END CatFeeder =================+
"""
import pytest

try:
    from libs.docs.common.common_constants import (
        CDN_UNPKG_BASE, CDN_JSDELIVR_BASE, CDN_CDNJS_BASE,
        HTML_DOCTYPE, HTML_META_CHARSET, HTML_META_VIEWPORT,
        create_html_page, create_cdn_script_tag, create_cdn_link_tag
    )
except Exception:
    from src.libs.docs.common.common_constants import (
        CDN_UNPKG_BASE, CDN_JSDELIVR_BASE, CDN_CDNJS_BASE,
        HTML_DOCTYPE, HTML_META_CHARSET, HTML_META_VIEWPORT,
        create_html_page, create_cdn_script_tag, create_cdn_link_tag
    )


class TestCDNConstants:
    """Test CDN base URL constants."""

    def test_cdn_unpkg_base_defined(self):
        """Verify CDN_UNPKG_BASE is defined."""
        assert CDN_UNPKG_BASE is not None
        assert isinstance(CDN_UNPKG_BASE, str)

    def test_cdn_unpkg_base_valid_url(self):
        """Verify CDN_UNPKG_BASE is valid URL."""
        assert CDN_UNPKG_BASE.startswith("https://")
        assert "unpkg" in CDN_UNPKG_BASE

    def test_cdn_jsdelivr_base_defined(self):
        """Verify CDN_JSDELIVR_BASE is defined."""
        assert CDN_JSDELIVR_BASE is not None
        assert isinstance(CDN_JSDELIVR_BASE, str)

    def test_cdn_jsdelivr_base_valid_url(self):
        """Verify CDN_JSDELIVR_BASE is valid URL."""
        assert CDN_JSDELIVR_BASE.startswith("https://")
        assert "jsdelivr" in CDN_JSDELIVR_BASE

    def test_cdn_cdnjs_base_defined(self):
        """Verify CDN_CDNJS_BASE is defined."""
        assert CDN_CDNJS_BASE is not None
        assert isinstance(CDN_CDNJS_BASE, str)

    def test_cdn_cdnjs_base_valid_url(self):
        """Verify CDN_CDNJS_BASE is valid URL."""
        assert CDN_CDNJS_BASE.startswith("https://")
        assert "cdnjs" in CDN_CDNJS_BASE


class TestHTMLConstants:
    """Test HTML constant definitions."""

    def test_html_doctype_defined(self):
        """Verify HTML_DOCTYPE is defined."""
        assert HTML_DOCTYPE is not None
        assert isinstance(HTML_DOCTYPE, str)

    def test_html_doctype_correct(self):
        """Verify HTML_DOCTYPE is correct."""
        assert "DOCTYPE" in HTML_DOCTYPE
        assert "html" in HTML_DOCTYPE.lower()

    def test_html_meta_charset_defined(self):
        """Verify HTML_META_CHARSET is defined."""
        assert HTML_META_CHARSET is not None
        assert isinstance(HTML_META_CHARSET, str)

    def test_html_meta_charset_correct(self):
        """Verify HTML_META_CHARSET is correct."""
        assert "charset" in HTML_META_CHARSET
        assert "utf-8" in HTML_META_CHARSET

    def test_html_meta_viewport_defined(self):
        """Verify HTML_META_VIEWPORT is defined."""
        assert HTML_META_VIEWPORT is not None
        assert isinstance(HTML_META_VIEWPORT, str)

    def test_html_meta_viewport_correct(self):
        """Verify HTML_META_VIEWPORT is correct."""
        assert "viewport" in HTML_META_VIEWPORT
        assert "width=device-width" in HTML_META_VIEWPORT


class TestCreateHTMLPage:
    """Test create_html_page function."""

    def test_create_html_page_basic(self):
        """Test basic HTML page creation."""
        result = create_html_page("Test Title", "<p>Content</p>")

        assert "<!DOCTYPE html>" in result
        assert "Test Title" in result
        assert "<p>Content</p>" in result
        assert "<html" in result
        assert "</html>" in result

    def test_create_html_page_with_head_extra(self):
        """Test HTML page with extra head content."""
        extra_head = '<link rel="stylesheet" href="style.css">'
        result = create_html_page(
            "Test", "<p>Content</p>", head_extra=extra_head)

        assert extra_head in result
        assert "Test" in result

    def test_create_html_page_with_body_attributes(self):
        """Test HTML page with body attributes."""
        result = create_html_page(
            "Test", "<p>Content</p>", body_attributes='class="main"')

        assert 'class="main"' in result
        assert "<body" in result

    def test_create_html_page_with_all_options(self):
        """Test HTML page with all options."""
        extra_head = '<meta name="description" content="Test">'
        body_attrs = 'id="app" class="main"'
        result = create_html_page(
            "Full Test",
            "<p>Full Content</p>",
            head_extra=extra_head,
            body_attributes=body_attrs
        )

        assert "Full Test" in result
        assert "<p>Full Content</p>" in result
        assert extra_head in result
        assert body_attrs in result

    def test_create_html_page_charset_included(self):
        """Verify charset is always included."""
        result = create_html_page("Test", "<p>Content</p>")

        assert "charset" in result.lower()

    def test_create_html_page_viewport_included(self):
        """Verify viewport meta tag is included."""
        result = create_html_page("Test", "<p>Content</p>")

        assert "viewport" in result

    def test_create_html_page_valid_structure(self):
        """Verify HTML structure is valid."""
        result = create_html_page("Test", "<p>Content</p>")

        assert result.count("<html") == 1
        assert result.count("</html>") == 1
        assert result.count("<head>") == 1
        assert result.count("</head>") == 1
        assert result.count("<body") == 1
        assert result.count("</body>") == 1


class TestCreateCDNScriptTag:
    """Test create_cdn_script_tag function."""

    def test_create_cdn_script_tag_basic(self):
        """Test basic script tag creation."""
        url = "https://cdn.example.com/script.js"
        result = create_cdn_script_tag(url)

        assert "<script" in result
        assert url in result
        assert "></script>" in result

    def test_create_cdn_script_tag_with_attributes(self):
        """Test script tag with attributes."""
        url = "https://cdn.example.com/script.js"
        attrs = 'async defer'
        result = create_cdn_script_tag(url, attributes=attrs)

        assert "<script" in result
        assert url in result
        assert attrs in result
        assert "></script>" in result

    def test_create_cdn_script_tag_empty_attributes(self):
        """Test script tag with empty attributes."""
        url = "https://cdn.example.com/script.js"
        result = create_cdn_script_tag(url, attributes="")

        assert "<script" in result
        assert url in result

    def test_create_cdn_script_tag_no_attributes(self):
        """Test script tag without attributes parameter."""
        url = "https://cdn.example.com/script.js"
        result = create_cdn_script_tag(url)

        assert "<script" in result
        assert url in result
        assert "src=" in result


class TestCreateCDNLinkTag:
    """Test create_cdn_link_tag function."""

    def test_create_cdn_link_tag_default(self):
        """Test basic link tag creation."""
        url = "https://cdn.example.com/style.css"
        result = create_cdn_link_tag(url)

        assert "<link" in result
        assert url in result
        assert 'rel="stylesheet"' in result

    def test_create_cdn_link_tag_custom_rel(self):
        """Test link tag with custom rel attribute."""
        url = "https://cdn.example.com/icon.png"
        result = create_cdn_link_tag(url, rel="icon")

        assert "<link" in result
        assert url in result
        assert 'rel="icon"' in result

    def test_create_cdn_link_tag_with_attributes(self):
        """Test link tag with additional attributes."""
        url = "https://cdn.example.com/style.css"
        attrs = 'media="print"'
        result = create_cdn_link_tag(url, attributes=attrs)

        assert "<link" in result
        assert url in result
        assert attrs in result

    def test_create_cdn_link_tag_with_all_options(self):
        """Test link tag with all options."""
        url = "https://cdn.example.com/fonts.css"
        rel = "preconnect"
        attrs = 'crossorigin'
        result = create_cdn_link_tag(url, rel=rel, attributes=attrs)

        assert "<link" in result
        assert url in result
        assert f'rel="{rel}"' in result
        assert attrs in result

    def test_create_cdn_link_tag_empty_attributes(self):
        """Test link tag with empty attributes."""
        url = "https://cdn.example.com/style.css"
        result = create_cdn_link_tag(url, attributes="")

        assert "<link" in result
        assert url in result


class TestHTMLFunctionsIntegration:
    """Integration tests for HTML creation functions."""

    def test_create_page_with_cdn_script(self):
        """Test creating page with CDN script."""
        script_url = "https://cdn.example.com/lib.js"
        script_tag = create_cdn_script_tag(script_url)
        page = create_html_page(
            "Test", "<p>Content</p>", head_extra=script_tag)

        assert script_tag in page
        assert "<!DOCTYPE html>" in page

    def test_create_page_with_cdn_link(self):
        """Test creating page with CDN link."""
        link_url = "https://cdn.example.com/style.css"
        link_tag = create_cdn_link_tag(link_url)
        page = create_html_page("Test", "<p>Content</p>", head_extra=link_tag)

        assert link_tag in page
        assert "<!DOCTYPE html>" in page

    def test_create_complete_documentation_page(self):
        """Test creating complete documentation page."""
        script_tag = create_cdn_script_tag(
            "https://cdn.example.com/redoc.standalone.js")
        link_tag = create_cdn_link_tag("https://cdn.example.com/redoc.css")
        head_extra = f"{link_tag}\n{script_tag}"

        page = create_html_page(
            "API Documentation",
            '<div id="redoc-container"></div>',
            head_extra=head_extra,
            body_attributes='id="root"'
        )

        assert "API Documentation" in page
        assert "redoc" in page.lower()
        assert 'id="root"' in page
