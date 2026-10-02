from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
from typing import Any

from .contract import (
    COMMANDS,
    DELIVERY_STATES,
    TERMINAL_STATES,
    Clock,
    ControlValidationError,
    EndpointExchange,
    IdSource,
    iso,
    parse_iso,
    random_id_source,
    utc_now,
    validate_safe_payload,
)


class GacrControlAdapter:
    """In-memory control-plane adapter.

    COMMAND DELIVERY != MUTATION AUTHORITY.
    This class intentionally owns no claims, sessions, takeovers, repository
    writes, or canonical GACR stores.
    """

    def __init__(
        self,
        *,
        clock: Clock = utc_now,
        id_source: IdSource = random_id_source,
        default_ttl_seconds: int = 60,
    ) -> None:
        self.clock = clock
        self.id_source = id_source
        self.default_ttl_seconds = default_ttl_seconds
        self._records: dict[str, dict[str, Any]] = {}
        self._accepted_acks: set[tuple[str, str, str]] = set()

    def target_session(self, endpoint: Any, target_session_id: str) -> str:
        actual = getattr(endpoint, "session_id", None)
        if not actual or actual != target_session_id:
            raise ControlValidationError("invalid target session")
        return actual

    def build_command(
        self,
        command_type: str,
        target_session_id: str,
        *,
        payload: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        requires_ack: bool = True,
        ttl_seconds: int | None = None,
    ) -> dict[str, Any]:
        if command_type not in COMMANDS:
            raise ControlValidationError("unsupported command")
        if not target_session_id:
            raise ControlValidationError("target_session_id is required")
        payload = deepcopy(payload or {})
        validate_safe_payload(payload)
        now = self.clock()
        ttl = self.default_ttl_seconds if ttl_seconds is None else int(ttl_seconds)
        if ttl <= 0:
            raise ControlValidationError("ttl_seconds must be positive")
        command = {
            "schema": "gscc-gacr-control-command/v1",
            "message_id": self.id_source("message"),
            "correlation_id": correlation_id or self.id_source("correlation"),
            "command_id": self.id_source("command"),
            "command_type": command_type,
            "target_session_id": target_session_id,
            "issued_at": iso(now),
            "expires_at": iso(now + timedelta(seconds=ttl)),
            "requires_ack": bool(requires_ack),
            "payload": payload,
            "mutation_authority_granted": False,
        }
        if command_type == "LIVENESS_CHALLENGE":
            if not payload.get("challenge_id") or not payload.get("nonce"):
                raise ControlValidationError("liveness challenge requires challenge_id and nonce")
            if not payload.get("issued_at") or not payload.get("expires_at"):
                raise ControlValidationError("liveness challenge payload requires issued_at and expires_at")
        if command_type == "TAKEOVER_OFFER":
            required = {
                "may_write": False,
                "requires_exact_head_reconciliation": True,
                "requires_takeover_accept": True,
            }
            for key, expected in required.items():
                if payload.get(key) is not expected:
                    raise ControlValidationError(f"TAKEOVER_OFFER requires {key}={expected!r}")

        self._records[command["command_id"]] = {
            "command": deepcopy(command),
            "state": "CREATED",
            "history": [
                {"at": iso(now), "state": "CREATED", "detail": "COMMAND_BUILT"}
            ],
            "ack": None,
            "response": None,
            "dispatch_count": 0,
        }
        return deepcopy(command)

    def _record(self, command_id: str, state: str, detail: str) -> None:
        if state not in DELIVERY_STATES:
            raise ControlValidationError("invalid delivery state")
        record = self._records[command_id]
        current = record["state"]
        if current == "EXPIRED" and state == "EXECUTING":
            raise ControlValidationError("expired command cannot execute")
        record["state"] = state
        record["history"].append({"at": iso(self.clock()), "state": state, "detail": detail})

    def record_delivery(self, command_id: str, state: str = "DELIVERED", detail: str = "DELIVERY") -> None:
        self._record(command_id, state, detail)

    def reject_invalid_target(self, command: dict[str, Any], actual_target: str | None) -> None:
        command_id = command["command_id"]
        self._record(command_id, "FAILED", f"INVALID_TARGET:{actual_target or 'UNAVAILABLE'}")
        raise ControlValidationError("invalid target session")

    def reject_invalid_correlation(self, command: dict[str, Any], received: dict[str, Any]) -> None:
        command_id = command["command_id"]
        self._record(command_id, "FAILED", "INVALID_CORRELATION")
        raise ControlValidationError("invalid command correlation")

    def record_ack(self, command: dict[str, Any], ack: dict[str, Any]) -> dict[str, Any]:
        command_id = command["command_id"]
        expected = (
            command_id,
            command["correlation_id"],
            command["target_session_id"],
        )
        received = (
            ack.get("command_id"),
            ack.get("correlation_id"),
            ack.get("target_session_id"),
        )
        if received != expected:
            self.reject_invalid_correlation(command, ack)
        if ack.get("event") != "COMMAND_ACK":
            self.reject_invalid_correlation(command, ack)
        key = expected
        if key in self._accepted_acks:
            self._records[command_id]["history"].append({
                "at": iso(self.clock()),
                "state": self._records[command_id]["state"],
                "detail": "DUPLICATE_ACK_IDEMPOTENT",
            })
            return deepcopy(self._records[command_id])
        self._accepted_acks.add(key)
        self._records[command_id]["ack"] = deepcopy(ack)
        self._record(command_id, "ACKNOWLEDGED", "COMMAND_ACK_ACCEPTED")
        return deepcopy(self._records[command_id])

    def record_response(self, command: dict[str, Any], response: dict[str, Any]) -> None:
        expected = (
            command["command_id"],
            command["correlation_id"],
            command["target_session_id"],
        )
        received = (
            response.get("command_id"),
            response.get("correlation_id"),
            response.get("target_session_id"),
        )
        if received != expected:
            self.reject_invalid_correlation(command, response)
        validate_safe_payload(response)
        self._records[command["command_id"]]["response"] = deepcopy(response)

    def expire_command(self, command_id: str) -> dict[str, Any]:
        record = self._records[command_id]
        if record["state"] in TERMINAL_STATES:
            return deepcopy(record)
        if self.clock() < parse_iso(record["command"]["expires_at"]):
            return deepcopy(record)
        state = "NO_RESPONSE" if record["state"] == "DELIVERED" else "EXPIRED"
        self._record(command_id, state, "COMMAND_DEADLINE_REACHED")
        return deepcopy(record)

    def dispatch_command(self, command: dict[str, Any], endpoint: Any) -> dict[str, Any]:
        command_id = command.get("command_id")
        if command_id not in self._records:
            raise ControlValidationError("command was not built by this adapter")
        record = self._records[command_id]
        if record["command"] != command:
            raise ControlValidationError("command payload changed after build")

        if record["dispatch_count"] > 0:
            record["history"].append({
                "at": iso(self.clock()),
                "state": record["state"],
                "detail": "DUPLICATE_COMMAND_IDEMPOTENT",
            })
            return deepcopy(record)

        try:
            self.target_session(endpoint, command["target_session_id"])
        except ControlValidationError:
            self.reject_invalid_target(command, getattr(endpoint, "session_id", None))
        if self.clock() >= parse_iso(command["expires_at"]):
            self._record(command_id, "EXPIRED", "EXPIRED_BEFORE_DISPATCH")
            return deepcopy(record)

        record["dispatch_count"] += 1
        self._record(command_id, "QUEUED", "TARGET_VALIDATED")
        self._record(command_id, "DISPATCHED", "ENDPOINT_SEND")
        exchange: EndpointExchange = endpoint.send(deepcopy(command))
        if not exchange.delivered:
            self._record(command_id, "FAILED", exchange.detail or "DELIVERY_REJECTED")
            return deepcopy(record)

        self._record(command_id, "DELIVERED", exchange.detail or "ENDPOINT_DELIVERED")

        if exchange.ack is not None:
            self.record_ack(command, exchange.ack)

        if exchange.response is not None:
            self.record_response(command, exchange.response)

        if exchange.execution_started:
            self._record(command_id, "EXECUTING", "ENDPOINT_EXECUTION_STARTED")

        if exchange.terminal_state is not None:
            if exchange.terminal_state not in TERMINAL_STATES:
                raise ControlValidationError("endpoint returned invalid terminal state")
            self._record(command_id, exchange.terminal_state, "ENDPOINT_TERMINAL_STATE")

        return deepcopy(record)

    def record_external_ack(self, command_id: str, ack: dict[str, Any]) -> dict[str, Any]:
        return self.record_ack(self._records[command_id]["command"], ack)

    def record_external_response(self, command_id: str, response: dict[str, Any]) -> dict[str, Any]:
        command = self._records[command_id]["command"]
        self.record_response(command, response)
        return deepcopy(self._records[command_id])

    def snapshot(self, command_id: str) -> dict[str, Any]:
        return deepcopy(self._records[command_id])

    def audit_trail(self, command_id: str) -> list[dict[str, Any]]:
        return deepcopy(self._records[command_id]["history"])
