from __future__ import annotations

from typing import Any

from .protocol import MessageEnvelope


class GACRCompatibilityError(RuntimeError):
    pass


class GACRClientEmitterAdapter:
    """Map the compatible GSCC event subset onto the historical GACR client emitter API.

    Credentials remain owned by the wrapped emitter/runtime. GSCC receives no token/cookie data.
    """

    def __init__(self, emitter: Any) -> None:
        self.emitter = emitter

    def send(self, message: MessageEnvelope) -> dict[str, Any]:
        message.validated()
        if message.kind != "EVENT":
            raise GACRCompatibilityError("historical GACR emitter adapter accepts GSCC EVENT messages only")
        p = dict(message.payload)
        session_id = message.source.get("session_id") or p.pop("session_id", None)
        common = {
            "observed_head": message.scope.get("observed_head"),
            "branch": message.scope.get("branch"),
            "task_id": message.scope.get("task_id"),
        }
        common = {k: v for k, v in common.items() if v not in (None, "", "UNAVAILABLE")}

        if message.type in {"SESSION_ATTACH", "SESSION_RESUME"}:
            return self.emitter.attach(**{**p, **common})
        if message.type == "HEARTBEAT":
            if not session_id:
                raise GACRCompatibilityError("HEARTBEAT requires source.session_id")
            return self.emitter.heartbeat(session_id, **{**p, **common})
        if message.type in {"ACTIVITY_STARTED", "ACTIVITY_COMPLETED", "ACTIVITY_FAILED", "TOOL_STARTED", "TOOL_COMPLETED", "TOOL_FAILED"}:
            if not session_id:
                raise GACRCompatibilityError(f"{message.type} requires source.session_id")
            phase = "STARTED" if message.type.endswith("STARTED") else "COMPLETED" if message.type.endswith("COMPLETED") else "FAILED"
            return self.emitter.trace(session_id, action_phase=phase, **{**p, **common})
        if message.type == "INTERRUPTION":
            if not session_id:
                raise GACRCompatibilityError("INTERRUPTION requires source.session_id")
            code = p.pop("interruption_code", "UNKNOWN")
            return self.emitter.interrupt(session_id, interruption_code=code, **{**p, **common})
        raise GACRCompatibilityError(f"GSCC event {message.type} has no historical GACR emitter mapping")
