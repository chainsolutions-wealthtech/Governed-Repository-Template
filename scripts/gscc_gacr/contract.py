from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable
import itertools
import uuid

try:
    from scripts.gscc.protocol import (
        COMMAND_TYPES,
        DELIVERY_STATES as GSCC_DELIVERY_STATES,
        EVENT_TYPES,
        TERMINAL_DELIVERY_STATES,
        UnsafePayloadError,
        assert_secretless,
    )
except ModuleNotFoundError:
    from gscc.protocol import (
        COMMAND_TYPES,
        DELIVERY_STATES as GSCC_DELIVERY_STATES,
        EVENT_TYPES,
        TERMINAL_DELIVERY_STATES,
        UnsafePayloadError,
        assert_secretless,
    )

# Shared protocol authority lives exclusively in scripts.gscc.protocol.
# These aliases intentionally preserve the historical gscc_gacr contract API.
EVENTS = EVENT_TYPES
COMMANDS = COMMAND_TYPES
DELIVERY_STATES = GSCC_DELIVERY_STATES
TERMINAL_STATES = TERMINAL_DELIVERY_STATES

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
    """Preserve the control-layer API while delegating safety authority to GSCC."""
    try:
        assert_secretless(value, path)
    except UnsafePayloadError as exc:
        raise ControlValidationError(str(exc)) from exc


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
