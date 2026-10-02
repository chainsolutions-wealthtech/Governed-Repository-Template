from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable, Mapping

SCHEMA = "gscc-message/v1"

KINDS = frozenset({"EVENT", "COMMAND", "ACK", "CAPABILITIES"})
EVENT_TYPES = frozenset({
    "SESSION_ATTACH", "SESSION_RESUME", "HEARTBEAT",
    "ACTIVITY_STARTED", "ACTIVITY_COMPLETED", "ACTIVITY_FAILED",
    "TOOL_STARTED", "TOOL_COMPLETED", "TOOL_FAILED",
    "PROGRESS", "BLOCKED", "CHECKPOINT", "CONTEXT_UPDATE",
    "INTERRUPTION", "CHALLENGE_RESPONSE", "COMMAND_ACK",
})
COMMAND_TYPES = frozenset({
    "PING", "LIVENESS_CHALLENGE", "STATUS_REQUEST", "PROGRESS_REQUEST",
    "CONTEXT_REQUEST", "CHECKPOINT_REQUEST", "REOBSERVE_HEAD", "REPORT_BLOCKER",
    "PAUSE", "RESUME", "SUPERVISOR_INSTRUCTION", "HANDOFF_PREPARE", "TAKEOVER_OFFER",
})
ACK_TYPES = frozenset({"COMMAND_ACK"})
CAPABILITY_TYPES = frozenset({"HELLO"})
CAPABILITIES = frozenset({
    "HEARTBEAT", "STATUS_RESPONSE", "PROGRESS_REPORT", "CONTEXT_REPORT",
    "CHECKPOINT_REPORT", "CHALLENGE_RESPONSE", "COMMAND_RECEIVE", "COMMAND_ACK",
    "BACKGROUND_EXECUTION", "TAKEOVER_RECEIVE",
})
DELIVERY_STATES = frozenset({
    "CREATED", "QUEUED", "DISPATCHED", "DELIVERED", "ACKNOWLEDGED", "EXECUTING", "COMPLETED",
    "FAILED", "DECLINED", "EXPIRED", "CANCELLED", "NO_RESPONSE", "UNSUPPORTED",
})
TERMINAL_DELIVERY_STATES = frozenset({
    "COMPLETED", "FAILED", "DECLINED", "EXPIRED", "CANCELLED", "NO_RESPONSE", "UNSUPPORTED",
})

FORBIDDEN_KEY_FRAGMENTS = (
    "password", "secret", "private_key", "authorization", "access_token", "refresh_token",
    "cookie", "session_cookie", "browser_cookie", "browser_session", "transcript", "raw_prompt", "prompt_text",
    "private_reasoning", "chain_of_thought", "raw_assistant_response", "assistant_response_body",
)
FORBIDDEN_EXACT_KEYS = {
    "token", "cookies", "messages", "transcript", "prompt", "private_reasoning",
    "chain-of-thought", "chain_of_thought", "raw_response", "response_body",
    "conversation_text", "page_content",
}
SECRET_VALUE_PATTERNS = (
    re.compile(r"^gh[pousr]_[A-Za-z0-9_\-]{12,}$"),
    re.compile(r"^github_pat_[A-Za-z0-9_\-]{12,}$"),
    re.compile(r"^sk-[A-Za-z0-9_\-]{12,}$"),
    re.compile(r"^Bearer\s+\S+", re.IGNORECASE),
)


class GSCCError(ValueError):
    pass


class UnsafePayloadError(GSCCError):
    pass


class UnsupportedMessageError(GSCCError):
    pass


class DeliveryTransitionError(GSCCError):
    pass


class DeliveryState(str, Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    DISPATCHED = "DISPATCHED"
    DELIVERED = "DELIVERED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    NO_RESPONSE = "NO_RESPONSE"
    UNSUPPORTED = "UNSUPPORTED"


ALLOWED_DELIVERY_TRANSITIONS: dict[str, frozenset[str]] = {
    "CREATED": frozenset({"QUEUED", "FAILED", "CANCELLED", "EXPIRED"}),
    "QUEUED": frozenset({"DISPATCHED", "FAILED", "CANCELLED", "EXPIRED"}),
    "DISPATCHED": frozenset({"DELIVERED", "FAILED", "CANCELLED", "EXPIRED", "NO_RESPONSE"}),
    "DELIVERED": frozenset({"ACKNOWLEDGED", "FAILED", "DECLINED", "EXPIRED", "CANCELLED", "NO_RESPONSE", "UNSUPPORTED"}),
    "ACKNOWLEDGED": frozenset({"EXECUTING", "COMPLETED", "FAILED", "DECLINED", "CANCELLED", "UNSUPPORTED"}),
    "EXECUTING": frozenset({"COMPLETED", "FAILED", "CANCELLED"}),
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise GSCCError("timestamp must be a non-empty ISO-8601 string")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise GSCCError(f"invalid ISO-8601 timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise GSCCError("timestamp must include timezone information")
    return parsed.astimezone(timezone.utc)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def deterministic_key(value: Mapping[str, Any], prefix: str = "GSCC-IDEM-") -> str:
    return prefix + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _unsafe_key(key: str) -> bool:
    lowered = key.lower().replace("-", "_")
    if lowered in FORBIDDEN_EXACT_KEYS:
        return True
    return any(fragment in lowered for fragment in FORBIDDEN_KEY_FRAGMENTS)


def _unsafe_string(value: str) -> bool:
    stripped = value.strip()
    if "-----BEGIN PRIVATE KEY-----" in value:
        return True
    return any(pattern.search(stripped) is not None for pattern in SECRET_VALUE_PATTERNS)


def assert_secretless(value: Any, path: str = "payload") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if _unsafe_key(key_text):
                raise UnsafePayloadError(f"forbidden GSCC field: {path}.{key_text}")
            assert_secretless(child, f"{path}.{key_text}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            assert_secretless(child, f"{path}[{index}]")
    elif isinstance(value, str) and _unsafe_string(value):
        raise UnsafePayloadError(f"secret-like GSCC value: {path}")


def _require_object(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise GSCCError(f"{name} must be an object")
    return dict(value)


def _validate_identity_object(name: str, value: Mapping[str, Any]) -> None:
    assert_secretless(value, name)
    if name == "source" and not any(value.get(k) not in (None, "", "UNAVAILABLE") for k in ("session_id", "client_instance_id", "provider", "system")):
        raise GSCCError("source must expose at least one non-secret identity fact")
    if name == "target" and not any(value.get(k) not in (None, "", "UNAVAILABLE") for k in ("session_id", "system", "provider", "client_instance_id")):
        raise GSCCError("target must expose at least one routing fact")


def _validate_type(kind: str, message_type: str) -> None:
    if kind not in KINDS:
        raise UnsupportedMessageError(f"unknown GSCC kind: {kind}")
    allowed = {
        "EVENT": EVENT_TYPES,
        "COMMAND": COMMAND_TYPES,
        "ACK": ACK_TYPES,
        "CAPABILITIES": CAPABILITY_TYPES,
    }[kind]
    if message_type not in allowed:
        raise UnsupportedMessageError(f"unknown GSCC {kind.lower()} type: {message_type}")


def validate_capabilities(values: Iterable[str]) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw).strip()
        if not value:
            continue
        if value not in CAPABILITIES:
            raise UnsupportedMessageError(f"unknown GSCC capability: {value}")
        if value not in seen:
            seen.add(value)
            result.append(value)
    return tuple(result)


@dataclass(frozen=True)
class MessageEnvelope:
    schema: str
    message_id: str
    correlation_id: str
    kind: str
    type: str
    issued_at: str
    source: dict[str, Any]
    target: dict[str, Any]
    scope: dict[str, Any]
    payload: dict[str, Any]
    delivery: dict[str, Any]
    idempotency_key: str

    @classmethod
    def create(
        cls,
        *,
        kind: str,
        type: str,
        source: Mapping[str, Any],
        target: Mapping[str, Any],
        scope: Mapping[str, Any] | None = None,
        payload: Mapping[str, Any] | None = None,
        requires_ack: bool = False,
        expires_at: str | None = None,
        correlation_id: str | None = None,
        message_id: str | None = None,
        idempotency_key: str | None = None,
        issued_at: str | None = None,
        delivery_state: str = "CREATED",
    ) -> "MessageEnvelope":
        message_id = message_id or f"GSCC-MSG-{uuid.uuid4()}"
        correlation_id = correlation_id or f"GSCC-CORR-{uuid.uuid4()}"
        issued_at = issued_at or utc_now_iso()
        source_dict = dict(source)
        target_dict = dict(target)
        scope_dict = dict(scope or {})
        payload_dict = dict(payload or {})
        delivery = {
            "requires_ack": bool(requires_ack),
            "expires_at": expires_at,
            "state": delivery_state,
        }
        base = {
            "schema": SCHEMA,
            "message_id": message_id,
            "correlation_id": correlation_id,
            "kind": kind,
            "type": type,
            "issued_at": issued_at,
            "source": source_dict,
            "target": target_dict,
            "scope": scope_dict,
            "payload": payload_dict,
            "delivery": delivery,
        }
        idempotency_key = idempotency_key or deterministic_key(base)
        return cls(
            schema=SCHEMA,
            message_id=message_id,
            correlation_id=correlation_id,
            kind=kind,
            type=type,
            issued_at=issued_at,
            source=source_dict,
            target=target_dict,
            scope=scope_dict,
            payload=payload_dict,
            delivery=delivery,
            idempotency_key=idempotency_key,
        ).validated()

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "MessageEnvelope":
        if not isinstance(raw, Mapping):
            raise GSCCError("GSCC message must be an object")
        required = {
            "schema", "message_id", "correlation_id", "kind", "type", "issued_at",
            "source", "target", "scope", "payload", "delivery", "idempotency_key",
        }
        missing = sorted(required - set(raw))
        if missing:
            raise GSCCError(f"GSCC message missing required fields: {','.join(missing)}")
        return cls(
            schema=str(raw["schema"]),
            message_id=str(raw["message_id"]),
            correlation_id=str(raw["correlation_id"]),
            kind=str(raw["kind"]),
            type=str(raw["type"]),
            issued_at=str(raw["issued_at"]),
            source=_require_object("source", raw["source"]),
            target=_require_object("target", raw["target"]),
            scope=_require_object("scope", raw["scope"]),
            payload=_require_object("payload", raw["payload"]),
            delivery=_require_object("delivery", raw["delivery"]),
            idempotency_key=str(raw["idempotency_key"]),
        ).validated()

    def validated(self) -> "MessageEnvelope":
        if self.schema != SCHEMA:
            raise GSCCError(f"unsupported GSCC schema: {self.schema}")
        for name, value in (("message_id", self.message_id), ("correlation_id", self.correlation_id), ("idempotency_key", self.idempotency_key)):
            if not value.strip():
                raise GSCCError(f"{name} must be non-empty")
        _validate_type(self.kind, self.type)
        parse_utc(self.issued_at)
        _validate_identity_object("source", self.source)
        _validate_identity_object("target", self.target)
        assert_secretless(self.scope, "scope")
        assert_secretless(self.payload, "payload")
        assert_secretless(self.delivery, "delivery")
        state = self.delivery.get("state", "CREATED")
        if state not in DELIVERY_STATES:
            raise GSCCError(f"unknown delivery state: {state}")
        expires_at = self.delivery.get("expires_at")
        if expires_at is not None:
            parse_utc(str(expires_at))
        if self.kind == "CAPABILITIES":
            values = self.payload.get("capabilities")
            if not isinstance(values, list):
                raise GSCCError("CAPABILITIES HELLO requires payload.capabilities array")
            validate_capabilities(values)
        if self.kind == "ACK":
            acked = self.payload.get("command_message_id")
            if not isinstance(acked, str) or not acked:
                raise GSCCError("ACK requires payload.command_message_id")
            ack_state = self.payload.get("state")
            if ack_state not in DELIVERY_STATES:
                raise GSCCError("ACK requires a supported payload.state")
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "message_id": self.message_id,
            "correlation_id": self.correlation_id,
            "idempotency_key": self.idempotency_key,
            "kind": self.kind,
            "type": self.type,
            "issued_at": self.issued_at,
            "source": dict(self.source),
            "target": dict(self.target),
            "scope": dict(self.scope),
            "payload": dict(self.payload),
            "delivery": dict(self.delivery),
        }

    def serialize(self) -> str:
        return canonical_json(self.to_dict())

    def is_expired(self, now: datetime | None = None) -> bool:
        expires_at = self.delivery.get("expires_at")
        if not expires_at:
            return False
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        return parse_utc(str(expires_at)) <= now.astimezone(timezone.utc)


@dataclass
class DeliveryTracker:
    message_id: str
    state: str = "CREATED"
    history: list[str] = field(default_factory=lambda: ["CREATED"])

    def transition(self, state: str) -> str:
        if state not in DELIVERY_STATES:
            raise DeliveryTransitionError(f"unknown delivery state: {state}")
        if self.state in TERMINAL_DELIVERY_STATES:
            if state == self.state:
                return self.state
            raise DeliveryTransitionError(f"terminal delivery state {self.state} cannot transition")
        allowed = ALLOWED_DELIVERY_TRANSITIONS.get(self.state, frozenset())
        if state not in allowed:
            raise DeliveryTransitionError(f"invalid delivery transition: {self.state} -> {state}")
        self.state = state
        self.history.append(state)
        return state

    def expire_if_needed(self, message: MessageEnvelope, now: datetime | None = None) -> bool:
        if message.is_expired(now) and self.state not in TERMINAL_DELIVERY_STATES:
            self.transition("EXPIRED")
            return True
        return False

    def mark_no_response(self) -> str:
        if self.state not in {"DISPATCHED", "DELIVERED"}:
            raise DeliveryTransitionError("NO_RESPONSE is only valid after dispatch/delivery")
        return self.transition("NO_RESPONSE")


class IdempotencyStore:
    def __init__(self) -> None:
        self._keys: dict[str, Any] = {}
        self._message_ids: dict[str, Any] = {}

    def seen(self, message: MessageEnvelope) -> bool:
        return message.idempotency_key in self._keys or message.message_id in self._message_ids

    def record(self, message: MessageEnvelope, result: Any = None) -> None:
        self._keys[message.idempotency_key] = result
        self._message_ids[message.message_id] = result

    def result(self, message: MessageEnvelope) -> Any:
        if message.idempotency_key in self._keys:
            return self._keys[message.idempotency_key]
        return self._message_ids.get(message.message_id)
