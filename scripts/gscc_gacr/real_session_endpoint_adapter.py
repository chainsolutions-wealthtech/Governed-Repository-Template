from __future__ import annotations

from copy import deepcopy
from typing import Any

try:
    from scripts.gscc import InMemoryTransport, MessageEnvelope, SessionEndpoint
except ModuleNotFoundError:
    from gscc import InMemoryTransport, MessageEnvelope, SessionEndpoint

from .contract import EndpointExchange


class GSCCSessionControlEndpoint:
    """Adapt a real GSCC SessionEndpoint to the GACR control harness endpoint seam.

    This bridge owns no GACR authority and no canonical state. It only translates
    control commands into GSCC COMMAND envelopes and translates GSCC ACK/challenge
    events back into the control adapter's exchange shape.
    """

    def __init__(
        self,
        endpoint: SessionEndpoint,
        transport: InMemoryTransport,
        *,
        challenge_status: str = "ACK",
    ) -> None:
        if endpoint.transport is not transport:
            raise ValueError("endpoint and transport must reference the same GSCC transport")
        session_id = endpoint.source.get("session_id")
        if not session_id:
            raise ValueError("GSCC SessionEndpoint source.session_id is required")
        self.endpoint = endpoint
        self.transport = transport
        self.session_id = str(session_id)
        self.challenge_status = challenge_status
        self._seen_challenge_nonces: set[str] = set()

    @staticmethod
    def _control_ack(command: dict[str, Any], message: MessageEnvelope | None) -> dict[str, Any] | None:
        if message is None:
            return None
        state = str(message.payload.get("state") or "ACKNOWLEDGED")
        return {
            "event": "COMMAND_ACK",
            "message_id": message.message_id,
            "command_id": command["command_id"],
            "correlation_id": command["correlation_id"],
            "target_session_id": command["target_session_id"],
            "ack_status": "ACK" if state == "ACKNOWLEDGED" else state,
            "delivery_state": state,
        }

    @staticmethod
    def _control_response(command: dict[str, Any], message: MessageEnvelope | None) -> dict[str, Any] | None:
        if message is None:
            return None
        payload = dict(message.payload)
        payload.pop("command_message_id", None)
        return {
            "response_type": message.type,
            "message_id": message.message_id,
            "command_id": command["command_id"],
            "correlation_id": command["correlation_id"],
            "target_session_id": command["target_session_id"],
            **payload,
        }

    def _handle(self, command: MessageEnvelope) -> dict[str, Any]:
        self.endpoint.ack_command(command, state="ACKNOWLEDGED")
        if command.type != "LIVENESS_CHALLENGE":
            return {"status": "ACKNOWLEDGED"}

        nonce = command.payload.get("nonce")
        challenge_id = command.payload.get("challenge_id")
        replay = nonce in self._seen_challenge_nonces
        if not replay:
            self._seen_challenge_nonces.add(str(nonce))

        status = "REPLAY" if replay else self.challenge_status
        self.endpoint.respond_challenge(
            command,
            challenge_id=challenge_id,
            nonce=nonce,
            challenge_status=status,
            replay=replay,
            fresh_liveness=(not replay and status != "UNSUPPORTED"),
            delivery_state="ACKNOWLEDGED",
        )
        return {"status": status, "replay": replay}

    def send(self, command: dict[str, Any]) -> EndpointExchange:
        if command.get("target_session_id") != self.session_id:
            return EndpointExchange(delivered=False, terminal_state="FAILED", detail="WRONG_TARGET")

        message = MessageEnvelope.create(
            kind="COMMAND",
            type=str(command["command_type"]),
            source={"system": "gacr"},
            target={"session_id": self.session_id},
            scope=dict(self.endpoint.scope),
            payload={
                **deepcopy(command.get("payload") or {}),
                "control_command_id": command["command_id"],
            },
            requires_ack=bool(command.get("requires_ack", True)),
            expires_at=command.get("expires_at"),
            correlation_id=str(command["correlation_id"]),
            message_id=str(command["message_id"]),
            idempotency_key=f"gscc-control:{command['command_id']}",
            issued_at=str(command["issued_at"]),
        )

        start = len(self.transport.sent)
        self.transport.inject(message)
        results = self.endpoint.receive_commands(self._handle)
        emitted = self.transport.sent[start:]

        ack_message = next((item for item in emitted if item.kind == "ACK" and item.type == "COMMAND_ACK"), None)
        response_message = next((item for item in emitted if item.kind == "EVENT" and item.type == "CHALLENGE_RESPONSE"), None)

        status = results[0]["status"] if results else "DELIVERED"
        if status == "EXPIRED":
            terminal = "EXPIRED"
        elif status == "UNSUPPORTED":
            terminal = "UNSUPPORTED"
        else:
            terminal = "COMPLETED"

        return EndpointExchange(
            delivered=True,
            ack=self._control_ack(command, ack_message),
            response=self._control_response(command, response_message),
            execution_started=(status == "EXECUTED"),
            terminal_state=terminal,
            detail="GSCC_SESSION_ENDPOINT",
        )
