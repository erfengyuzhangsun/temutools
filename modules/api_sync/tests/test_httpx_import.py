"""
测试：httpx 依赖是否正常可用
覆盖场景：
  1. httpx 包本身可导入
  2. common/temu_client.py 中的 httpx 异常类型可正常引用
"""
import importlib
import sys


def test_httpx_package_installed():
    """验证 httpx 包已正确安装"""
    try:
        import httpx
        assert httpx is not None
        assert hasattr(httpx, "TimeoutException")
        assert hasattr(httpx, "HTTPStatusError")
        assert hasattr(httpx, "RequestError")
        assert hasattr(httpx, "AsyncClient")
        assert hasattr(httpx, "Client")
    except ImportError as e:
        pytest.fail(f"httpx 包未安装: {e}")


def test_temu_client_httpx_imports():
    """验证 common/temu_client.py 中的 httpx 异常类型可正确解析"""
    import ast
    with open("common/temu_client.py", "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    # 检查文件顶层是否有 import httpx
    top_level_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top_level_imports.append(alias.name)

    has_httpx = any("httpx" in name for name in top_level_imports)
    has_import_from = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "httpx":
            has_import_from = True

    # 检查 request 方法中是否引用了 httpx.xxx 异常
    # 如果 httpx 不是模块级别导入，则引用 httpx.TimeoutException 等会 NameError
    uses_httpx_exceptions = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id == "httpx" and node.attr in ("TimeoutException", "HTTPStatusError", "RequestError"):
                uses_httpx_exceptions = True

    # 验证：如果引用了 httpx 异常，必须有顶层 import httpx
    if uses_httpx_exceptions and not (has_httpx or has_import_from):
        pytest.fail(
            "common/temu_client.py 中引用了 httpx.xxx 异常类型，"
            "但 httpx 仅在 _ensure_client() 方法内部导入（局部作用域），"
            "导致 request() 方法中的异常处理抛出 NameError: name 'httpx' is not defined"
        )


def test_temu_client_request_httpx_available():
    """验证 TemuApiClient.request 方法能正确捕获 httpx 异常"""
    from common.temu_client import TemuApiClient

    # 验证异常类型引用正常（不会 NameError）
    client = TemuApiClient(shop_id=1, api_key="test", api_secret="test")

    # 检查 request 方法源码是否包含 httpx. 引用
    import inspect
    source = inspect.getsource(client.request)

    # 如果源码中使用 httpx.xxx 但 httpx 不是全局导入，则必定出错
    if "httpx." in source:
        # 验证 httpx 在模块级别可用
        import common.temu_client as tc_module
        assert hasattr(tc_module, "httpx") or any(
            "httpx" in name for name in dir(tc_module)
        ), (
            "request() 方法引用了 httpx.xxx 异常，"
            "但 httpx 未在模块级别导入，运行时会 NameError"
        )


# 确保 pytest 可用
import pytest
