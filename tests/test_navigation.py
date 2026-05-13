"""
Navigation & Session State Tests
Verifies that the navigation routing in app.py provides:
1. Session-state-based page routing (not URL-only)
2. Sidebar navigation always visible on module pages
3. Back-to-home navigation capability
"""
import os
import re
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_PY = os.path.join(PROJECT_ROOT, "app.py")


class TestNavigationRouting:
    """Test that app.py has proper SPA routing via session_state."""

    def test_session_state_page_key_exists(self):
        """Verify app.py uses session_state for page routing."""
        with open(APP_PY, "r", encoding="utf-8") as f:
            content = f.read()
        assert 'st.session_state["page"]' in content or '"page" not in st.session_state' in content, \
            "Must use st.session_state['page'] for routing persistence"

    def test_sidebar_before_module_stop(self):
        """Verify sidebar is rendered BEFORE module page st.stop() call."""
        with open(APP_PY, "r", encoding="utf-8") as f:
            content = f.read()

        sidebar_start = content.find("with st.sidebar:")
        module_stop = content.find("MODULE_PAGES[current_page]()")
        sidebar_after_module_stop = content.find("with st.sidebar:", module_stop)

        assert sidebar_start > 0, "Sidebar must exist in app.py"
        if sidebar_after_module_stop > 0:
            pytest.fail("Sidebar is defined AFTER module page stop - navigation won't appear on module pages")

    def test_home_button_in_sidebar(self):
        """Verify sidebar has a home/back-to-main button."""
        with open(APP_PY, "r", encoding="utf-8") as f:
            content = f.read()

        sidebar_section = content[content.find("with st.sidebar:"):]
        assert "app" in sidebar_section, "Sidebar must include navigation to main 'app' page"

    def test_nav_button_uses_session_state(self):
        """Verify nav_button uses st.session_state to set the current page."""
        with open(APP_PY, "r", encoding="utf-8") as f:
            content = f.read()

        nav_def = content[content.find("def nav_button"):content.find("def nav_button") + 500]
        assert 'st.session_state["page"]' in nav_def or 'session_state' in nav_def, \
            "nav_button must set page in session_state"

    def test_auth_check_is_before_module_routing(self):
        """Verify authentication check happens before module page routing."""
        with open(APP_PY, "r", encoding="utf-8") as f:
            lines = f.readlines()

        auth_line = None
        module_check_line = None
        for i, line in enumerate(lines):
            if "is_authenticated()" in line:
                auth_line = i
            if "MODULE_PAGES[current_page]" in line:
                module_check_line = i

        assert auth_line is not None, "Auth check must exist"
        assert module_check_line is not None, "Module page check must exist"
        assert auth_line < module_check_line, \
            f"Auth check (line {auth_line+1}) must be before module routing (line {module_check_line+1})"


class TestNavigationPersistence:
    """Test that navigation between modules preserves state."""

    def test_session_init_before_page_routing(self):
        """Verify session state 'page' is initialized before it's used for routing."""
        with open(APP_PY, "r", encoding="utf-8") as f:
            lines = f.readlines()

        page_session_init = None
        page_reference = None
        for i, line in enumerate(lines):
            if '"page" not in st.session_state' in line:
                page_session_init = i
            if 'current_page = st.session_state["page"]' in line:
                page_reference = i

        assert page_session_init is not None, "Must initialize page in session_state"
        assert page_reference is not None, "Must read page from session_state"
        assert page_session_init < page_reference, \
            f"Session state init (line {page_session_init+1}) must be before page usage (line {page_reference+1})"
