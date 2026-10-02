from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable
import itertools
import uuid

EVENTS = (
    "SESSION_ATTACH",
    "SESSION_RESUME",
    "HEARTBEAT",
    "ACTIVITY_STARTED",
    "ACTIVITY_COMPLETED",
    "ACTIVITY_FAILED",
    "TOOL_STARTED",
    "TOOL_COMPLETED",
    "TOOL_FAILED",
    "PROGRESS",
    "BLOCKED",
    "CHECKPOINT",
    "CONTEXT_UPDATE",
    "INTERRUPTION",
    "CHALLENGE_RESPONSE",
    "COMMAND_ACK",
)

COMMANDS = (
    "PING",
    "LIVENESS_CHALLENGE",
    "STATUS_REQUEST",
    "PROGRESS_REQUEST",
    "CONTEXT_REQUEST",
    "CHECKPOINT_REQUEST",
    "REOBSERVE_HEAD",
    "REPORT_BLOCKER",
    "PAUSE",
    "RESUME",
    "SUPERVISOR_INSTRUCTION",
    "HANDOFF_PREPARE",
    "TAKEOVER_OFFER",
)

DELIVERY_STATES = (
    "CREATED",
    "QUEUED",
    "DISPATCHED",
    "DELIVERED",
    "ACKNOWLEDGED",
    "EXECUTING",
    "COMPLETED",
    "FAILED",
    "DECLINED",
    "EXPIRED",
    "CANCELLED",
    "NO_RESPONSE",
    "UNSUPPORTED",
)

TERMINAL_STATES = {
    "COMPLETED",
    "FAILED",
    "DECLINED",
    "EXPIRED",
    "CANCELLED",
    "NO_RESPONSE",
    "UNSUPPORTED",
}

FORBIDDEN_KEY_FRAGMENTS = (
    "token",
    "secret",
    "authorization",
    "cookie",
    "password",
    "private_key",
    "browser_session",
)

FORBIDDEN_EXACT_KEYS = {
    "raw_transcript",
    "transcript",
    "conversation_text",
    "prompt",
    "private_reasoning",
    "chain_of_thought",
    "raw_response",
    "page_content",
}

UNAVAILABLE = "UNAVAILABLE"


class ControlValidationError(ValueError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    if value.tzinfo is None:
        raise ControlValidationError("timestamps must be timezone-aware")
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def parse_iso(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ControlValidationError("invalid ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ControlValidationError("timestamps must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def validate_safe_payload(value: Any, path: str = "payload") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = str(key).lower()
            if lowered in FORBIDDEN_EXACT_KEYS:
                raise ControlValidationError(f"forbidden control payload key: {path}.{key}")
            if any(fragment in lowered for fragment in FORBIDDEN_KEY_FRAGMENTS):
                raise ControlValidationError(f"forbidden control payload key: {path}.{key}")
            validate_safe_payload(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            validate_safe_payload(child, f"{path}[{index}]")
    elif isinstance(value, str):
        if "-----BEGIN PRIVATE KEY-----" in value:
            raise ControlValidationError(f"secret-like control payload value: {path}")
        if value.startswith(("ghp_", "github_pat_", "sk-")):
            raise ControlValidationError(f"secret-like control payload value: {path}")


class DeterministicIdSource:
    """Deterministic IDs for tests and protocol fixtures."""

    def __init__(self, prefix: str = "gscc-gacr") -> None:
        self.prefix = prefix
        self._counter = itertools.count(1)

    def __call__(self, kind: str) -> str:
        return f"{self.prefix}-{kind}-{next(self._counter):04d}"


def random_id_source(kind: str) -> str:
    return f"{kind}-{uuid.uuid4().hex}"


@dataclass(frozen=True)
class EndpointExchange:
    delivered: bool = True
    ack: dict[str, Any] | None = None
    response: dict[str, Any] | None = None
    execution_started: bool = False
    terminal_state: str | None = None
    detail: str | None = None


Clock = Callable[[], datetime]
IdSource = Callable[[str], str]
