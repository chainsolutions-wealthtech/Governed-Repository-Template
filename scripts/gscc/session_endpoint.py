from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .protocol import (
    MessageEnvelope,
    IdempotencyStore,
    validate_capabilities,
)
from .transport import Transport


COMMAND_CAPABILITY = {
    "PING": None,
    "LIVENESS_CHALLENGE": "CHALLENGE_RESPONSE",
    "STATUS_REQUEST": "STATUS_RESPONSE",
    "PROGRESS_REQUEST": "PROGRESS_REPORT",
    "CONTEXT_REQUEST": "CONTEXT_REPORT",
    "CHECKPOINT_REQUEST": "CHECKPOINT_REPORT",
    "REOBSERVE_HEAD": None,
    "REPORT_BLOCKER": None,
    "PAUSE": None,
    "RESUME": None,
    "SUPERVISOR_INSTRUCTION": None,
    "HANDOFF_PREPARE": "CHECKPOINT_REPORT",
    "TAKEOVER_OFFER": "TAKEOVER_RECEIVE",
}


class SessionEndpoint:
    def __init__(
        self,
        transport: Transport,
        *,
        source: dict[str, Any],
        target: dict[str, Any],
        scope: dict[str, Any] | None = None,
        capabilities: list[str] | tuple[str, ...] = (),
        idempotency_store: IdempotencyStore | None = None,
    ) -> None:
        self.transport = transport
        self.source = dict(source)
        self.target = dict(target)
        self.scope = dict(scope or {})
        self.capabilities = frozenset(validate_capabilities(capabilities))
        self.idempotency_store = idempotency_store or IdempotencyStore()

    def _emit_event(self, event_type: str, payload: dict[str, Any] | None = None, *, requires_ack: bool = False) -> dict[str, Any]:
        message = MessageEnvelope.create(
            kind="EVENT", type=event_type, source=self.source, target=self.target,
            scope=self.scope, payload=payload or {}, requires_ack=requires_ack,
        )
        return {"message": message, "delivery": self.transport.send(message)}

    def attach(self, **payload: Any) -> dict[str, Any]: return self._emit_event("SESSION_ATTACH", payload, requires_ack=True)
    def resume(self, **payload: Any) -> dict[str, Any]: return self._emit_event("SESSION_RESUME", payload, requires_ack=True)
    def heartbeat(self, **payload: Any) -> dict[str, Any]: return self._emit_event("HEARTBEAT", payload)
    def activity_started(self, **payload: Any) -> dict[str, Any]: return self._emit_event("ACTIVITY_STARTED", payload)
    def activity_completed(self, **payload: Any) -> dict[str, Any]: return self._emit_event("ACTIVITY_COMPLETED", payload)
    def activity_failed(self, **payload: Any) -> dict[str, Any]: return self._emit_event("ACTIVITY_FAILED", payload)
    def tool_started(self, **payload: Any) -> dict[str, Any]: return self._emit_event("TOOL_STARTED", payload)
    def tool_completed(self, **payload: Any) -> dict[str, Any]: return self._emit_event("TOOL_COMPLETED", payload)
    def tool_failed(self, **payload: Any) -> dict[str, Any]: return self._emit_event("TOOL_FAILED", payload)
    def progress(self, **payload: Any) -> dict[str, Any]: return self._emit_event("PROGRESS", payload)
    def blocked(self, **payload: Any) -> dict[str, Any]: return self._emit_event("BLOCKED", payload)
    def checkpoint(self, **payload: Any) -> dict[str, Any]: return self._emit_event("CHECKPOINT", payload)
    def context_update(self, **payload: Any) -> dict[str, Any]: return self._emit_event("CONTEXT_UPDATE", payload)

    def hello(self) -> dict[str, Any]:
        message = MessageEnvelope.create(
            kind="CAPABILITIES", type="HELLO", source=self.source, target=self.target,
            scope=self.scope, payload={"capabilities": sorted(self.capabilities)}, requires_ack=True,
        )
        return {"message": message, "delivery": self.transport.send(message)}

    def ack_command(self, command: MessageEnvelope, *, state: str = "ACKNOWLEDGED", reason_code: str | None = None) -> dict[str, Any]:
        command.validated()
        if command.kind != "COMMAND":
            raise ValueError("ack_command requires a COMMAND message")
        payload: dict[str, Any] = {"command_message_id": command.message_id, "state": state}
        if reason_code:
            payload["reason_code"] = reason_code
        ack = MessageEnvelope.create(
            kind="ACK", type="COMMAND_ACK", source=self.source, target=command.source,
            scope=self.scope, payload=payload, correlation_id=command.correlation_id,
        )
        return {"message": ack, "delivery": self.transport.send(ack)}

    def respond_challenge(self, command: MessageEnvelope, **payload: Any) -> dict[str, Any]:
        if command.kind != "COMMAND" or command.type != "LIVENESS_CHALLENGE":
            raise ValueError("respond_challenge requires LIVENESS_CHALLENGE")
        message = MessageEnvelope.create(
            kind="EVENT", type="CHALLENGE_RESPONSE", source=self.source, target=command.source,
            scope=self.scope, payload={"command_message_id": command.message_id, **payload},
            correlation_id=command.correlation_id,
        )
        return {"message": message, "delivery": self.transport.send(message)}

    def receive_commands(self, handler: Callable[[MessageEnvelope], Any] | None = None) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        selector = {}
        if self.source.get("session_id"):
            selector["session_id"] = self.source["session_id"]
        elif self.source.get("client_instance_id"):
            selector["client_instance_id"] = self.source["client_instance_id"]
        else:
            selector = dict(self.source)
        for command in self.transport.receive(target=selector):
            command.validated()
            if command.kind != "COMMAND":
                continue
            if self.idempotency_store.seen(command):
                results.append({"status": "ALREADY_PROCESSED", "message_id": command.message_id, "result": self.idempotency_store.result(command)})
                continue
            if command.is_expired():
                result = {"status": "EXPIRED", "message_id": command.message_id}
                self.idempotency_store.record(command, result)
                results.append(result)
                continue
            if "COMMAND_RECEIVE" not in self.capabilities:
                ack = self.ack_command(command, state="UNSUPPORTED", reason_code="COMMAND_RECEIVE_UNAVAILABLE")
                result = {"status": "UNSUPPORTED", "message_id": command.message_id, "ack": ack}
                self.idempotency_store.record(command, result)
                results.append(result)
                continue
            required = COMMAND_CAPABILITY.get(command.type)
            if required and required not in self.capabilities:
                ack = self.ack_command(command, state="UNSUPPORTED", reason_code=f"{required}_UNAVAILABLE")
                result = {"status": "UNSUPPORTED", "message_id": command.message_id, "ack": ack}
                self.idempotency_store.record(command, result)
                results.append(result)
                continue
            if handler is None:
                result = {"status": "DELIVERED", "message_id": command.message_id, "command": command}
            else:
                value = handler(command)
                result = {"status": "EXECUTED", "message_id": command.message_id, "result": value}
            self.idempotency_store.record(command, result)
            results.append(result)
        return results

    def disconnect(self, *, reason: str = "CLIENT_DISCONNECTED") -> dict[str, Any]:
        return self._emit_event("INTERRUPTION", {"interruption_code": reason})
