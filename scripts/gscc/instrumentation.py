from __future__ import annotations

import functools
import uuid
from collections.abc import Callable
from typing import Any, TypeVar

from .session_endpoint import SessionEndpoint

T = TypeVar("T")


def instrument_tool(
    endpoint: SessionEndpoint,
    tool_name: str,
    fn: Callable[..., T],
    *,
    before_tool_call: Callable[[str], dict[str, Any] | None] | None = None,
    exposure_guard: Callable[[str], dict[str, Any]] | None = None,
) -> Callable[..., T]:
    """Emit GSCC lifecycle evidence without serializing arguments/results.

    Controlled hosts may supply a before_tool_call hook. It executes before any
    exposure evaluation or TOOL_STARTED event and is the canonical extension point
    for provider First Touch emission. The hook receives only the tool name and
    must not inspect or serialize tool arguments/results.

    Controlled hosts may also supply an exposure_guard. When present, the guard is
    evaluated after before_tool_call and before TOOL_STARTED, and must return a
    VALIDATED exposure receipt. The guard decision itself is transported through
    GSCC as activity evidence.
    """
    @functools.wraps(fn)
    def wrapped(*args: Any, **kwargs: Any) -> T:
        if before_tool_call is not None:
            before_tool_call(tool_name)

        if exposure_guard is not None:
            gate_id = f"GSCC-EXPOSURE-GATE-{uuid.uuid4()}"
            endpoint.activity_started(
                action_id=gate_id,
                action_label="FUNCTION_EXPOSURE_GATE",
                tool_name=tool_name,
            )
            receipt = exposure_guard(tool_name)
            if not isinstance(receipt, dict) or receipt.get("status") != "VALIDATED" or receipt.get("exposable") is not True:
                reason = "EXPOSURE_NOT_VALIDATED"
                if isinstance(receipt, dict) and receipt.get("reason_code"):
                    reason = str(receipt["reason_code"])
                endpoint.activity_failed(
                    action_id=gate_id,
                    action_label="FUNCTION_EXPOSURE_GATE",
                    tool_name=tool_name,
                    outcome="DENIED",
                    reason_code=reason,
                )
                raise PermissionError(f"GSCC function exposure denied: {reason}")
            endpoint.activity_completed(
                action_id=gate_id,
                action_label="FUNCTION_EXPOSURE_GATE",
                tool_name=tool_name,
                outcome="VALIDATED",
                exposure_receipt=receipt.get("exposure_receipt"),
            )

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
