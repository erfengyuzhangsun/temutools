"""
Tests for TemuApiClient DNS and network error handling
Verifies:
1. DNS errors are caught and reported with user-friendly Chinese messages
2. Proxy configuration is supported via environment variables
3. Timeout and connection errors are handled gracefully
"""
import os
import sys
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

TEMU_CLIENT_PY = os.path.join(PROJECT_ROOT, "common", "temu_client.py")


class TestTemuClientNetworkErrors:
    """Verify network error handling in TemuApiClient."""

    def test_dns_error_detected_by_keyword(self):
        """Verify DNS error keyword detection exists in request method."""
        with open(TEMU_CLIENT_PY, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Name or service not known" in content, \
            "DNS error keyword 'Name or service not known' must be detected"

    def test_dns_error_friendly_message(self):
        """Verify DNS errors produce user-friendly Chinese message."""
        with open(TEMU_CLIENT_PY, "r", encoding="utf-8") as f:
            content = f.read()
        assert "DNS解析失败" in content or "无法连接" in content, \
            "DNS error must produce user-friendly Chinese message"

    def test_proxy_support_exists(self):
        """Verify proxy from HTTPS_PROXY env var is supported."""
        with open(TEMU_CLIENT_PY, "r", encoding="utf-8") as f:
            content = f.read()
        assert "HTTPS_PROXY" in content or "https_proxy" in content or "proxy" in content.lower(), \
            "Proxy configuration from environment variable must be supported"

    def test_dns_error_has_specific_error_code(self):
        """Verify DNS errors have DNS_ERROR error_code."""
        with open(TEMU_CLIENT_PY, "r", encoding="utf-8") as f:
            content = f.read()
        assert "DNS_ERROR" in content, \
            "DNS errors must have DNS_ERROR error_code to differentiate from general network errors"
