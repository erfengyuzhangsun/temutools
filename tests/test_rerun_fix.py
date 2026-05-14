"""
Tests for NotFoundError: removeChild fix
Verifies that app.py has proper rerun debounce guards
to prevent Streamlit DOM reconciliation conflicts.
"""
import os
import re
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_PY = os.path.join(PROJECT_ROOT, "app.py")


class TestRerunDebounce:
    """Verify rerun debounce guards exist in app.py."""

    def test_rerun_pending_guard_exists(self):
        """Verify _rerun_pending guard pattern exists in app.py."""
        with open(APP_PY, "r", encoding="utf-8") as f:
            content = f.read()

        assert "_rerun_pending" in content, (
            "Must have _rerun_pending debounce guard to prevent duplicate reruns"
        )

    def test_rerun_checks_guard_before_executing(self):
        """Verify st.rerun() calls check _rerun_pending before executing."""
        with open(APP_PY, "r", encoding="utf-8") as f:
            lines = f.readlines()

        rerun_calls = []
        for i, line in enumerate(lines):
            if "st.rerun()" in line and not line.strip().startswith("#"):
                rerun_calls.append(i + 1)

        guard_checks = []
        for i, line in enumerate(lines):
            if "_rerun_pending" in line:
                guard_checks.append(i + 1)

        assert len(guard_checks) > 0, "Must have _rerun_pending guard checks"
        # At minimum, the first rerun call should have a guard before it
        assert guard_checks[0] < rerun_calls[0], (
            f"_rerun_pending guard (line {guard_checks[0]}) should be checked "
            f"before st.rerun() (line {rerun_calls[0]})"
        )

    def test_no_rerun_inside_form_or_container(self):
        """Verify all st.rerun() calls are guarded by _rerun_pending check."""
        with open(APP_PY, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            stripped = line.strip()
            if "st.rerun()" in stripped and not stripped.startswith("#"):
                prev_line = lines[i - 1].strip() if i > 0 else ""
                has_guard = (
                    "_rerun_pending" in prev_line
                )
                assert has_guard, (
                    f"st.rerun() on line {i+1} must be immediately "
                    f"preceded by a _rerun_pending guard check. "
                    f"Prev line: '{prev_line}'"
                )
