"""
Safe async runner utility for Streamlit environments.
Resolves "asyncio.run() cannot be called from a running event loop" errors
by detecting existing event loops and adapting accordingly.
"""
import asyncio
from typing import TypeVar, Awaitable

T = TypeVar("T")


def run(coro: Awaitable[T]) -> T:
    """Safely execute an async coroutine, compatible with Streamlit's event loop.

    - If no event loop is running: uses asyncio.run() (standard approach)
    - If an event loop IS running (e.g., inside Streamlit's asyncio context):
      uses loop.run_until_complete() to avoid nested loop errors

    Args:
        coro: An awaitable coroutine to execute

    Returns:
        The result of the coroutine
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    if loop.is_running():
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result()
    else:
        return loop.run_until_complete(coro)
