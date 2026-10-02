from __future__ import annotations

import functools
import uuid
from collections.abc import Callable
from typing import Any, TypeVar

from .session_endpoint import SessionEndpoint

T = TypeVar("T")


def instrument_tool(endpoint: SessionEndpoint, tool_name: str, fn: Callable[..., T]) -> Callable[..., T]:
    """Emit tool lifecycle evidence without serializing arguments, results, prompts or errors."""
    @functools.wraps(fn)
    def wrapped(*args: Any, **kwargs: Any) -> T:
        call_id = f"GSCC-TOOL-{uuid.uuid4()}"
        endpoint.tool_started(tool_name=tool_name, tool_call_id=call_id)
        try:
            result = fn(*args, **kwargs)
        except Exception as exc:
            endpoint.tool_failed(
                tool_name=tool_name,
                tool_call_id=call_id,
                outcome="FAILED",
                exception_type=type(exc).__name__,
            )
            raise
        endpoint.tool_completed(tool_name=tool_name, tool_call_id=call_id, outcome="COMPLETED")
        return result
    return wrapped
