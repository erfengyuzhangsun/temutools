"""
Brand Consistency Tests
Verifies that all UI text uses the new "Temu全托管自动化运营平台" brand identity.
"""
import re
import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OLD_BRAND_PATTERNS = [
    r"Temu\s*商家风控与利润管家",
    r"Temu\s*利润管家",
]

FILES_TO_CHECK = [
    "app.py",
    "auth.py",
    "api/index.py",
]

EXCLUDED_FILES = [
    "HANDOVER.md",
    "tests/test_brand_consistency.py",
]


def get_all_python_files():
    py_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        if "venv" in root or ".git" in root or "__pycache__" in root:
            continue
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                rel = os.path.relpath(path, PROJECT_ROOT)
                if rel not in EXCLUDED_FILES:
                    py_files.append(path)
    return py_files


@pytest.mark.parametrize("pattern", OLD_BRAND_PATTERNS)
def test_no_old_brand_in_critical_files(pattern, file_path):
    """Verify old brand names are not present in critical UI files."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    matches = re.findall(pattern, content)
    assert len(matches) == 0, (
        f"Found {len(matches)} occurrence(s) of old brand pattern '{pattern}' in {file_path}:\n"
        + "\n".join(f"  - Line {i+1}: {line.strip()}"
                    for i, line in enumerate(content.splitlines())
                    if re.search(pattern, line))
    )


def pytest_generate_tests(metafunc):
    if "file_path" in metafunc.fixturenames:
        files = [os.path.join(PROJECT_ROOT, f) for f in FILES_TO_CHECK]
        metafunc.parametrize("file_path", files)
