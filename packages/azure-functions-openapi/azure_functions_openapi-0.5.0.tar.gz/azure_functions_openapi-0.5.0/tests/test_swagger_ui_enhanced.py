# tests/test_swagger_ui_enhanced.py

import pytest
from typing import Any
from unittest.mock import patch, MagicMock
from azure.functions import HttpResponse

from azure_functions_openapi.swagger_ui import (
    render_swagger_ui,
    _sanitize_html_content,
    _sanitize_url,
)


class TestRenderSwaggerUI:
    """Test render_swagger_ui function."""

    def test_render_swagger_ui_default(self) -> None:
        """Test rendering Swagger UI with default parameters."""
        response = render_swagger_ui()

        assert isinstance(response, HttpResponse)
        assert response.mimetype == "text/html"

        # Check HTML content
        html_content = response.get_body().decode()
        assert "<!DOCTYPE html>" in html_content
        assert "API Documentation" in html_content
        assert "/api/openapi.json" in html_content

        # Check security headers
        assert "Content-Security-Policy" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Strict-Transport-Security" in response.headers
        assert "Cache-Control" in response.headers

    def test_render_swagger_ui_custom_title(self) -> None:
        """Test rendering Swagger UI with custom title."""
        response = render_swagger_ui(title="Custom API Docs")

        html_content = response.get_body().decode()
        assert "Custom API Docs" in html_content
        assert "<title>Custom API Docs</title>" in html_content

    def test_render_swagger_ui_custom_url(self) -> None:
        """Test rendering Swagger UI with custom OpenAPI URL."""
        response = render_swagger_ui(openapi_url="/custom/openapi.json")

        html_content = response.get_body().decode()
        assert "/custom/openapi.json" in html_content

    def test_render_swagger_ui_custom_csp(self) -> None:
        """Test rendering Swagger UI with custom CSP."""
        custom_csp = "default-src 'self'; script-src 'self'"
        response = render_swagger_ui(custom_csp=custom_csp)

        html_content = response.get_body().decode()
        assert custom_csp in html_content
        assert response.headers["Content-Security-Policy"] == custom_csp

    def test_render_swagger_ui_security_headers(self) -> None:
        """Test that all security headers are present."""
        response = render_swagger_ui()

        expected_headers = {
            "Content-Security-Policy",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Referrer-Policy",
            "Strict-Transport-Security",
            "Cache-Control",
            "Pragma",
            "Expires",
        }

        for header in expected_headers:
            assert header in response.headers

    def test_render_swagger_ui_security_values(self) -> None:
        """Test that security headers have correct values."""
        response = render_swagger_ui()

        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
        assert response.headers["Cache-Control"] == "no-cache, no-store, must-revalidate"
        assert response.headers["Pragma"] == "no-cache"
        assert response.headers["Expires"] == "0"

    def test_render_swagger_ui_swagger_config(self) -> None:
        """Test that Swagger UI configuration is correct."""
        response = render_swagger_ui()

        html_content = response.get_body().decode()

        # Check Swagger UI configuration
        assert "validatorUrl: null" in html_content  # Disabled for security
        assert "tryItOutEnabled: true" in html_content
        assert "supportedSubmitMethods" in html_content
        assert "requestInterceptor" in html_content
        assert "responseInterceptor" in html_content

    @patch("azure_functions_openapi.swagger_ui.logger")
    def test_render_swagger_ui_logging(self, mock_logger: Any) -> None:
        """Test that render_swagger_ui logs correctly."""
        response = render_swagger_ui(openapi_url="/test/openapi.json")

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "Swagger UI rendered with enhanced security headers" in call_args
        assert "/test/openapi.json" in call_args


class TestSanitizeHtmlContent:
    """Test _sanitize_html_content function."""

    def test_sanitize_html_content_normal(self) -> None:
        """Test sanitizing normal HTML content."""
        result = _sanitize_html_content("Normal Title")
        assert result == "Normal Title"

    def test_sanitize_html_content_with_dangerous_chars(self) -> None:
        """Test sanitizing HTML content with dangerous characters."""
        dangerous_content = "<script>alert('xss')</script>"
        result = _sanitize_html_content(dangerous_content)
        assert "<" not in result
        assert ">" not in result
        assert "'" not in result
        assert '"' not in result

    def test_sanitize_html_content_empty(self) -> None:
        """Test sanitizing empty content."""
        result = _sanitize_html_content("")
        assert result == "API Documentation"

    def test_sanitize_html_content_none(self) -> None:
        """Test sanitizing None content."""
        result = _sanitize_html_content(None)  # type: ignore
        assert result == "API Documentation"

    def test_sanitize_html_content_not_string(self) -> None:
        """Test sanitizing non-string content."""
        result = _sanitize_html_content(123)  # type: ignore
        assert result == "API Documentation"

    def test_sanitize_html_content_long(self) -> None:
        """Test sanitizing long content."""
        long_content = "A" * 150
        result = _sanitize_html_content(long_content)
        assert len(result) == 100
        assert result == "A" * 100

    def test_sanitize_html_content_with_newlines(self) -> None:
        """Test sanitizing content with newlines and tabs."""
        content = "Title\nwith\ttabs"
        result = _sanitize_html_content(content)
        assert "\n" not in result
        assert "\t" not in result
        assert "\r" not in result


class TestSanitizeUrl:
    """Test _sanitize_url function."""

    def test_sanitize_url_normal(self) -> None:
        """Test sanitizing normal URL."""
        result = _sanitize_url("/api/openapi.json")
        assert result == "/api/openapi.json"

    def test_sanitize_url_without_slash(self) -> None:
        """Test sanitizing URL without leading slash."""
        result = _sanitize_url("api/openapi.json")
        assert result == "/api/openapi.json"

    def test_sanitize_url_empty(self) -> None:
        """Test sanitizing empty URL."""
        result = _sanitize_url("")
        assert result == "/api/openapi.json"

    def test_sanitize_url_none(self) -> None:
        """Test sanitizing None URL."""
        result = _sanitize_url(None)  # type: ignore
        assert result == "/api/openapi.json"

    def test_sanitize_url_not_string(self) -> None:
        """Test sanitizing non-string URL."""
        result = _sanitize_url(123)  # type: ignore
        assert result == "/api/openapi.json"

    def test_sanitize_url_javascript(self) -> None:
        """Test sanitizing URL with javascript: scheme."""
        result = _sanitize_url("javascript:alert('xss')")
        assert result == "/api/openapi.json"

    def test_sanitize_url_data(self) -> None:
        """Test sanitizing URL with data: scheme."""
        result = _sanitize_url("data:text/html,<script>alert('xss')</script>")
        assert result == "/api/openapi.json"

    def test_sanitize_url_vbscript(self) -> None:
        """Test sanitizing URL with vbscript: scheme."""
        result = _sanitize_url("vbscript:msgbox('xss')")
        assert result == "/api/openapi.json"

    def test_sanitize_url_script_tag(self) -> None:
        """Test sanitizing URL with script tag."""
        result = _sanitize_url("/api/<script>alert('xss')</script>")
        assert result == "/api/openapi.json"

    def test_sanitize_url_onload(self) -> None:
        """Test sanitizing URL with onload attribute."""
        result = _sanitize_url("/api/openapi.json?onload=alert('xss')")
        assert result == "/api/openapi.json"

    @patch("azure_functions_openapi.swagger_ui.logger")
    def test_sanitize_url_logging(self, mock_logger: Any) -> None:
        """Test that _sanitize_url logs dangerous patterns."""
        _sanitize_url("javascript:alert('xss')")

        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]
        assert "Potentially dangerous URL pattern detected" in call_args
        assert "javascript:" in call_args

    def test_sanitize_url_case_insensitive(self) -> None:
        """Test that dangerous pattern detection is case insensitive."""
        result1 = _sanitize_url("JAVASCRIPT:alert('xss')")
        result2 = _sanitize_url("JavaScript:alert('xss')")
        result3 = _sanitize_url("DATA:text/html,<script>")

        assert result1 == "/api/openapi.json"
        assert result2 == "/api/openapi.json"
        assert result3 == "/api/openapi.json"
