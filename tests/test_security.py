"""
Security Compliance Tests
Verifies that no hardcoded passwords, API keys, or secrets exist in production code.
"""
import os
import re
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PRODUCTION_FILES = [
    "admin.py",
    "auth.py",
    "config.py",
    "db.py",
    "app.py",
]

EXCLUDED_DIRS = ["tests", "__pycache__", ".git", "venv"]


class TestNoHardcodedSecrets:
    """Verify no hardcoded passwords or secrets in production code."""

    def test_admin_password_not_hardcoded(self):
        """Verify ADMIN_PASSWORD is not a hardcoded literal."""
        admin_path = os.path.join(PROJECT_ROOT, "admin.py")
        with open(admin_path, "r", encoding="utf-8") as f:
            content = f.read()

        has_hardcoded_password = bool(re.search(
            r'ADMIN_PASSWORD\s*=\s*["\'][^"\']+["\']',
            content
        ))
        assert not has_hardcoded_password, (
            "ADMIN_PASSWORD should NOT be a hardcoded string literal. "
            "Use os.environ.get('ADMIN_PASSWORD') or st.secrets instead."
        )

        env_pattern = r'os\.environ\.get\(["\']ADMIN_PASSWORD["\']'
        secrets_pattern = r'st\.secrets\[?["\']admin_password["\']\]?'
        assert re.search(env_pattern, content) or re.search(secrets_pattern, content), (
            "ADMIN_PASSWORD must be read from environment variable or Streamlit secrets"
        )

    def test_db_seed_password_not_hardcoded(self):
        """Verify seed password in db.py is not a hardcoded literal."""
        db_path = os.path.join(PROJECT_ROOT, "db.py")
        with open(db_path, "r", encoding="utf-8") as f:
            content = f.read()

        hardcoded_seed = re.search(r'admin123["\']', content)
        assert hardcoded_seed is None, (
            "Seed password 'admin123' must not be hardcoded. "
            "Read from environment variable instead."
        )

    def test_encryption_key_not_hardcoded_in_production(self):
        """Verify no hardcoded encryption key in production code."""
        prod_files = [os.path.join(PROJECT_ROOT, f) for f in PRODUCTION_FILES]
        for file_path in prod_files:
            if not os.path.exists(file_path):
                continue
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            if "ENCRYPTION_KEY" in content:
                assert "os.environ.get" in content or "st.secrets" in content, \
                    f"ENCRYPTION_KEY in {file_path} must use env variable"
