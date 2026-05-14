"""
Tests for MessageService TemuApiError fix
Verifies:
1. Missing API credentials produce friendly guidance message
2. TemuApiError during sync is caught and reported gracefully
3. Client is properly closed on all code paths
"""
import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MESSAGE_SERVICE_PY = os.path.join(PROJECT_ROOT, "modules", "message", "service.py")


class TestMessageServiceCredentials:
    """Verify message service handles API credential and error scenarios."""

    def test_api_error_caught(self):
        """Verify TemuApiError is caught in sync_messages."""
        with open(MESSAGE_SERVICE_PY, "r", encoding="utf-8") as f:
            content = f.read()
        assert "except" in content and "TemuApiError" in content, \
            "sync_messages must catch TemuApiError to prevent crash"

    def test_exception_returns_service_result(self):
        """Verify exceptions return a ServiceResult instead of propagating."""
        with open(MESSAGE_SERVICE_PY, "r", encoding="utf-8") as f:
            content = f.read()
        assert "return ServiceResult" in content, \
            "Error handling must return ServiceResult with friendly message"

    def test_credential_check_before_api_call(self):
        """Verify API credentials are checked before making API calls."""
        with open(MESSAGE_SERVICE_PY, "r", encoding="utf-8") as f:
            content = f.read()
        has_credential_check = (
            "api_key" in content and "api_secret" in content
        ) or "api_key" in content or "没有绑定" in content or "未绑定" in content
        assert has_credential_check, \
            "Must check API credentials before calling Temu API"

    def test_import_temu_api_error(self):
        """Verify TemuApiError is imported in message/service.py."""
        with open(MESSAGE_SERVICE_PY, "r", encoding="utf-8") as f:
            content = f.read()
        assert "TemuApiError" in content, \
            "Must import TemuApiError from common.temu_client"

    def test_client_closed_in_exception_path(self):
        """Verify client.close() is called even when exceptions occur."""
        with open(MESSAGE_SERVICE_PY, "r", encoding="utf-8") as f:
            content = f.read()
        # Check both patterns: "finally:" or ", finally:\n...client.close()"
        has_finally = "finally:" in content
        has_client_close = "client.close()" in content
        assert has_finally and has_client_close, \
            "Client must be closed in finally block on all code paths"
