from __future__ import annotations

from copy import deepcopy
from typing import Any

try:
    from scripts.gscc import InMemoryTransport, MessageEnvelope, SessionEndpoint
except ModuleNotFoundError:
    from gscc import InMemoryTransport, MessageEnvelope, SessionEndpoint

from .contract import EndpointExchange, UNAVAILABLE


class GSCCSessionControlEndpoint:
    """Adapt a real GSCC SessionEndpoint to the GACR control endpoint seam.

    This bridge owns no GACR authority and no canonical state. Commands are
    delivered through the real GSCC SessionEndpoint. Query responses are bounded,
    safe session snapshots returned by the endpoint handler; they are not new
    GSCC protocol event types and they do not grant mutation authority.
    """

    def __init__(
        self,
        endpoint: SessionEndpoint,
        transport: InMemoryTransport,
        *,
        challenge_status: str = "ACK",
        status: dict[str, Any] | None = None,
        progress: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
        checkpoint: dict[str, Any] | None = None,
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
        self.status_payload = dict(status or {})
        self.progress_payload = dict(progress or {})
        self.context_payload = dict(context or {})
        self.checkpoint_payload = dict(checkpoint or {})
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

    @staticmethod
    def _handler_response(command: dict[str, Any], result: Any) -> dict[str, Any] | None:
        if not isinstance(result, dict) or not result.get("response_type"):
            return None
        payload = deepcopy(result)
        response_type = str(payload.pop("response_type"))
        return {
            "response_type": response_type,
            "message_id": f"response:{command['message_id']}",
            "command_id": command["command_id"],
            "correlation_id": command["correlation_id"],
            "target_session_id": command["target_session_id"],
            **payload,
        }

    def _query_snapshot(self, command: MessageEnvelope) -> dict[str, Any] | None:
        if command.type == "STATUS_REQUEST":
            return {
                "response_type": "STATUS_RESPONSE",
                "current_state": self.status_payload.get("current_state", UNAVAILABLE),
                "current_action": self.status_payload.get("current_action", UNAVAILABLE),
                "current_tool": self.status_payload.get("current_tool", UNAVAILABLE),
                "observed_head": self.status_payload.get(
                    "observed_head", self.endpoint.scope.get("observed_head", UNAVAILABLE)
                ),
                "last_progress_at": self.status_payload.get("last_progress_at", UNAVAILABLE),
                "blocker": self.status_payload.get("blocker", UNAVAILABLE),
            }
        if command.type == "PROGRESS_REQUEST":
            return {
                "response_type": "PROGRESS_RESPONSE",
                "last_progress_at": self.progress_payload.get("last_progress_at", UNAVAILABLE),
                "progress_marker": self.progress_payload.get("progress_marker", UNAVAILABLE),
                "checkpoint_ref": self.progress_payload.get("checkpoint_ref", UNAVAILABLE),
                "work_item_ref": self.progress_payload.get("work_item_ref", UNAVAILABLE),
            }
        if command.type == "CONTEXT_REQUEST":
            return {
                "response_type": "CONTEXT_RESPONSE",
                "objective_ref": self.context_payload.get("objective_ref", UNAVAILABLE),
                "current_phase": self.context_payload.get("current_phase", UNAVAILABLE),
                "current_action": self.context_payload.get("current_action", UNAVAILABLE),
                "last_checkpoint": self.context_payload.get("last_checkpoint", UNAVAILABLE),
                "next_action": self.context_payload.get("next_action", UNAVAILABLE),
                "repository": self.context_payload.get(
                    "repository", self.endpoint.scope.get("repository", UNAVAILABLE)
                ),
                "branch": self.context_payload.get(
                    "branch", self.endpoint.scope.get("branch", UNAVAILABLE)
                ),
                "observed_head": self.context_payload.get(
                    "observed_head", self.endpoint.scope.get("observed_head", UNAVAILABLE)
                ),
            }
        if command.type == "CHECKPOINT_REQUEST":
            return {
                "response_type": "CHECKPOINT_RESPONSE",
                "checkpoint_ref": self.checkpoint_payload.get("checkpoint_ref", UNAVAILABLE),
                "current_action": self.checkpoint_payload.get("current_action", UNAVAILABLE),
                "observed_head": self.checkpoint_payload.get(
                    "observed_head", self.endpoint.scope.get("observed_head", UNAVAILABLE)
                ),
            }
        return None

    def _handle(self, command: MessageEnvelope) -> dict[str, Any]:
        self.endpoint.ack_command(command, state="ACKNOWLEDGED")

        query = self._query_snapshot(command)
        if query is not None:
            return query

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
        response_message = next(
            (item for item in emitted if item.kind == "EVENT" and item.type == "CHALLENGE_RESPONSE"),
            None,
        )

        result = results[0] if results else {}
        status = result.get("status", "DELIVERED")
        if status == "EXPIRED":
            terminal = "EXPIRED"
        elif status == "UNSUPPORTED":
            terminal = "UNSUPPORTED"
        else:
            terminal = "COMPLETED"

        response = self._control_response(command, response_message)
        if response is None:
            response = self._handler_response(command, result.get("result"))

        return EndpointExchange(
            delivered=True,
            ack=self._control_ack(command, ack_message),
            response=response,
            execution_started=(status == "EXECUTED"),
            terminal_state=terminal,
            detail="GSCC_SESSION_ENDPOINT",
        )
