from __future__ import annotations

from copy import deepcopy
from typing import Any

from .contract import EndpointExchange, UNAVAILABLE


class FakeSessionEndpoint:
    """Deterministic GSCC-compatible endpoint used only by tests/harnesses.

    It owns no repository authority and persists nothing.
    """

    def __init__(
        self,
        session_id: str,
        *,
        scenarios: dict[str, str] | None = None,
        status: dict[str, Any] | None = None,
        progress: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
        checkpoint: dict[str, Any] | None = None,
        blocker: dict[str, Any] | None = None,
        handoff: dict[str, Any] | None = None,
        observed_head: str = UNAVAILABLE,
    ) -> None:
        self.session_id = session_id
        self.scenarios = dict(scenarios or {})
        self.status_payload = dict(status or {})
        self.progress_payload = dict(progress or {})
        self.context_payload = dict(context or {})
        self.checkpoint_payload = dict(checkpoint or {})
        self.blocker_payload = dict(blocker or {})
        self.handoff_payload = dict(handoff or {})
        self.observed_head = observed_head
        self.paused = False
        self._seen_command_ids: set[str] = set()
        self._seen_challenge_nonces: set[str] = set()
        self._last_command: dict[str, Any] | None = None
        self._last_exchange: EndpointExchange | None = None

    def configure(self, command_type: str, scenario: str) -> None:
        self.scenarios[command_type] = scenario

    def receive(self) -> dict[str, Any] | None:
        return deepcopy(self._last_command)

    def ack(self) -> dict[str, Any] | None:
        if self._last_exchange is None:
            return None
        return deepcopy(self._last_exchange.ack)

    def respond(self) -> dict[str, Any] | None:
        if self._last_exchange is None:
            return None
        return deepcopy(self._last_exchange.response)

    def _ack(self, command: dict[str, Any], *, status: str = "ACK") -> dict[str, Any]:
        return {
            "event": "COMMAND_ACK",
            "message_id": f"ack:{command['message_id']}",
            "command_id": command["command_id"],
            "correlation_id": command["correlation_id"],
            "target_session_id": command["target_session_id"],
            "ack_status": status,
        }

    def _response(
        self,
        command: dict[str, Any],
        response_type: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "response_type": response_type,
            "message_id": f"response:{command['message_id']}",
            "command_id": command["command_id"],
            "correlation_id": command["correlation_id"],
            "target_session_id": command["target_session_id"],
            **deepcopy(payload),
        }

    def _result(
        self,
        command: dict[str, Any],
        *,
        response_type: str | None = None,
        payload: dict[str, Any] | None = None,
        execution_started: bool = False,
        terminal_state: str = "COMPLETED",
        ack_status: str = "ACK",
    ) -> EndpointExchange:
        response = None
        if response_type is not None:
            response = self._response(command, response_type, payload or {})
        return EndpointExchange(
            delivered=True,
            ack=self._ack(command, status=ack_status),
            response=response,
            execution_started=execution_started,
            terminal_state=terminal_state,
        )

    def send(self, command: dict[str, Any]) -> EndpointExchange:
        self._last_command = deepcopy(command)
        if command["target_session_id"] != self.session_id:
            exchange = EndpointExchange(delivered=False, terminal_state="FAILED", detail="WRONG_TARGET")
            self._last_exchange = exchange
            return exchange

        command_id = command["command_id"]
        if command_id in self._seen_command_ids:
            exchange = EndpointExchange(
                delivered=True,
                ack=self._ack(command),
                response=self._response(
                    command,
                    "DUPLICATE_COMMAND",
                    {"idempotent": True, "executed_again": False},
                ),
                terminal_state="COMPLETED",
                detail="DUPLICATE_COMMAND_IDEMPOTENT",
            )
            self._last_exchange = exchange
            return exchange

        self._seen_command_ids.add(command_id)
        kind = command["command_type"]
        scenario = self.scenarios.get(kind, "ACK")

        if scenario == "NO_RESPONSE":
            exchange = EndpointExchange(delivered=True, terminal_state=None, detail="NO_RESPONSE")
            self._last_exchange = exchange
            return exchange
        if scenario == "FAILED":
            exchange = self._result(command, terminal_state="FAILED", execution_started=True)
            self._last_exchange = exchange
            return exchange
        if scenario == "DECLINED":
            exchange = self._result(command, terminal_state="DECLINED")
            self._last_exchange = exchange
            return exchange
        if scenario == "EXPIRED":
            exchange = EndpointExchange(delivered=True, terminal_state="EXPIRED", detail="ENDPOINT_EXPIRED")
            self._last_exchange = exchange
            return exchange
        if scenario == "UNSUPPORTED" and kind != "LIVENESS_CHALLENGE":
            exchange = self._result(command, terminal_state="UNSUPPORTED", ack_status="UNSUPPORTED")
            self._last_exchange = exchange
            return exchange

        if kind == "PING":
            exchange = self._result(command)
        elif kind == "LIVENESS_CHALLENGE":
            payload = command.get("payload") or {}
            nonce = payload.get("nonce")
            challenge_id = payload.get("challenge_id")
            if nonce in self._seen_challenge_nonces:
                exchange = self._result(
                    command,
                    response_type="CHALLENGE_RESPONSE",
                    payload={
                        "event": "CHALLENGE_RESPONSE",
                        "challenge_id": challenge_id,
                        "nonce": nonce,
                        "challenge_status": "REPLAY",
                        "replay": True,
                        "fresh_liveness": False,
                    },
                    terminal_state="COMPLETED",
                )
            else:
                self._seen_challenge_nonces.add(nonce)
                challenge_status = scenario if scenario in {
                    "ACK", "BUSY", "IDLE", "CHECKPOINTING", "TERMINATING", "UNSUPPORTED"
                } else "ACK"
                exchange = self._result(
                    command,
                    response_type="CHALLENGE_RESPONSE",
                    payload={
                        "event": "CHALLENGE_RESPONSE",
                        "challenge_id": challenge_id,
                        "nonce": nonce,
                        "challenge_status": challenge_status,
                        "replay": False,
                        "fresh_liveness": challenge_status != "UNSUPPORTED",
                    },
                    terminal_state="UNSUPPORTED" if challenge_status == "UNSUPPORTED" else "COMPLETED",
                )
        elif kind == "STATUS_REQUEST":
            payload = {
                "current_state": self.status_payload.get("current_state", UNAVAILABLE),
                "current_action": self.status_payload.get("current_action", UNAVAILABLE),
                "current_tool": self.status_payload.get("current_tool", UNAVAILABLE),
                "observed_head": self.status_payload.get("observed_head", self.observed_head),
                "last_progress_at": self.status_payload.get("last_progress_at", UNAVAILABLE),
                "blocker": self.status_payload.get("blocker", UNAVAILABLE),
            }
            exchange = self._result(command, response_type="STATUS_RESPONSE", payload=payload)
        elif kind == "PROGRESS_REQUEST":
            payload = {
                "last_progress_at": self.progress_payload.get("last_progress_at", UNAVAILABLE),
                "progress_marker": self.progress_payload.get("progress_marker", UNAVAILABLE),
                "checkpoint_ref": self.progress_payload.get("checkpoint_ref", UNAVAILABLE),
                "work_item_ref": self.progress_payload.get("work_item_ref", UNAVAILABLE),
            }
            exchange = self._result(command, response_type="PROGRESS_RESPONSE", payload=payload)
        elif kind == "CONTEXT_REQUEST":
            payload = {
                "objective_ref": self.context_payload.get("objective_ref", UNAVAILABLE),
                "current_phase": self.context_payload.get("current_phase", UNAVAILABLE),
                "current_action": self.context_payload.get("current_action", UNAVAILABLE),
                "last_checkpoint": self.context_payload.get("last_checkpoint", UNAVAILABLE),
                "next_action": self.context_payload.get("next_action", UNAVAILABLE),
                "repository": self.context_payload.get("repository", UNAVAILABLE),
                "branch": self.context_payload.get("branch", UNAVAILABLE),
                "observed_head": self.context_payload.get("observed_head", self.observed_head),
            }
            exchange = self._result(command, response_type="CONTEXT_RESPONSE", payload=payload)
        elif kind == "CHECKPOINT_REQUEST":
            payload = {
                "checkpoint_ref": self.checkpoint_payload.get("checkpoint_ref", UNAVAILABLE),
                "current_action": self.checkpoint_payload.get("current_action", UNAVAILABLE),
                "observed_head": self.checkpoint_payload.get("observed_head", self.observed_head),
            }
            exchange = self._result(
                command,
                response_type="CHECKPOINT_RESPONSE",
                payload=payload,
                execution_started=True,
            )
        elif kind == "REOBSERVE_HEAD":
            exchange = self._result(
                command,
                response_type="HEAD_OBSERVATION",
                payload={"observed_head": self.observed_head, "mutation_authority_granted": False},
            )
        elif kind == "REPORT_BLOCKER":
            payload = {
                "blocked": self.blocker_payload.get("blocked", UNAVAILABLE),
                "blocker_class": self.blocker_payload.get("blocker_class", UNAVAILABLE),
                "blocker_ref": self.blocker_payload.get("blocker_ref", UNAVAILABLE),
            }
            exchange = self._result(command, response_type="BLOCKER_RESPONSE", payload=payload)
        elif kind == "SUPERVISOR_INSTRUCTION":
            exchange = self._result(
                command,
                response_type="INSTRUCTION_RESULT",
                payload={"outcome": "COMPLETED"},
                execution_started=True,
            )
        elif kind == "PAUSE":
            self.paused = True
            exchange = self._result(
                command,
                response_type="SESSION_CONTROL_RESULT",
                payload={"paused": True, "mutation_authority_granted": False},
                execution_started=True,
            )
        elif kind == "RESUME":
            self.paused = False
            exchange = self._result(
                command,
                response_type="SESSION_CONTROL_RESULT",
                payload={"paused": False, "mutation_authority_granted": False},
                execution_started=True,
            )
        elif kind == "HANDOFF_PREPARE":
            payload = {
                "checkpoint_ref": self.handoff_payload.get("checkpoint_ref", UNAVAILABLE),
                "current_action": self.handoff_payload.get("current_action", UNAVAILABLE),
                "observed_head": self.handoff_payload.get("observed_head", self.observed_head),
                "safe_context_ref": self.handoff_payload.get("safe_context_ref", UNAVAILABLE),
                "session_closed": False,
            }
            exchange = self._result(
                command,
                response_type="HANDOFF_PREPARE_RESPONSE",
                payload=payload,
                execution_started=True,
            )
        elif kind == "TAKEOVER_OFFER":
            exchange = self._result(
                command,
                response_type="TAKEOVER_OFFER_RECEIPT",
                payload={
                    "offer_received": True,
                    "may_write": False,
                    "requires_exact_head_reconciliation": True,
                    "requires_takeover_accept": True,
                    "claim_transferred": False,
                },
            )
        else:
            exchange = self._result(command, terminal_state="UNSUPPORTED", ack_status="UNSUPPORTED")

        self._last_exchange = exchange
        return exchange
