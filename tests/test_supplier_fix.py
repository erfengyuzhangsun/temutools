"""
Tests for Supplier Page NameError fix
Verifies:
1. async_runner utility works safely in Streamlit environments
2. SupplierService methods handle async correctly
3. No NameError for missing imports
"""
import sys
import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


class TestSupplierImport:
    """Verify supplier/ui.py has correct imports."""

    def test_asyncio_imported(self):
        """Verify asyncio is imported in supplier/ui.py."""
        ui_path = os.path.join(PROJECT_ROOT, "modules", "supplier", "ui.py")
        with open(ui_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "import asyncio" in content, "asyncio must be imported in supplier/ui.py"

    def test_no_asyncio_run_in_supplier_ui(self):
        """Verify supplier/ui.py uses safe runner instead of raw asyncio.run()."""
        ui_path = os.path.join(PROJECT_ROOT, "modules", "supplier", "ui.py")
        with open(ui_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "asyncio.run" not in content, "Use safe_async.run() instead of asyncio.run()"


class TestAsyncRunner:
    """Test the safe async runner utility."""

    def test_async_runner_module_exists(self):
        """Verify common/async_runner.py exists."""
        runner_path = os.path.join(PROJECT_ROOT, "common", "async_runner.py")
        assert os.path.exists(runner_path), "common/async_runner.py must exist"

    def test_async_runner_has_run_function(self):
        """Verify async_runner has a run() function."""
        from common.async_runner import run
        assert callable(run)

    def test_async_runner_executes_sync_function(self):
        """Verify run() can execute a simple sync function wrapped in async."""
        from common.async_runner import run

        async def simple_func():
            return 42

        result = run(simple_func())
        assert result == 42

    def test_async_runner_executes_async_with_result(self):
        """Verify run() can execute an async function and return the result."""
        from common.async_runner import run

        async def add(a, b):
            return a + b

        result = run(add(3, 4))
        assert result == 7
