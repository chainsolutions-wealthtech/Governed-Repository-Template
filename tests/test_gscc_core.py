from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.gscc import (
    DeliveryTracker,
    GACRClientEmitterAdapter,
    GitHubDispatchTransport,
    IdempotencyStore,
    InMemoryTransport,
    MessageEnvelope,
    SessionEndpoint,
    UnsafePayloadError,
    UnsupportedMessageError,
    instrument_tool,
)
from scripts.gscc.protocol import DeliveryTransitionError

SRC = {"session_id": "session-a", "client_instance_id": "client-a", "provider": "chatgpt"}
TARGET = {"system": "gacr"}
SCOPE = {
    "repository": "chainsolutions-wealthtech/Governed-Repository-Template",
    "branch": "governance/gscc-core-v1",
    "observed_head": "a" * 40,
}


def command(command_type: str, *, message_id: str = "GSCC-MSG-CMD-1", expires_at: str | None = None) -> MessageEnvelope:
    return MessageEnvelope.create(
        kind="COMMAND", type=command_type,
        source={"system": "gacr"}, target=SRC, scope=SCOPE,
        payload={}, requires_ack=True, message_id=message_id,
        correlation_id="GSCC-CORR-1", idempotency_key=f"idem-{message_id}",
        expires_at=expires_at,
    )


class FakeEmitter:
    def __init__(self): self.calls = []
    def attach(self, **payload): self.calls.append(("attach", payload)); return {"status": "SENT"}
    def heartbeat(self, session_id, **payload): self.calls.append(("heartbeat", session_id, payload)); return {"status": "SENT"}
    def trace(self, session_id, *, action_phase, **payload): self.calls.append(("trace", session_id, action_phase, payload)); return {"status": "SENT"}
    def interrupt(self, session_id, *, interruption_code, **payload): self.calls.append(("interrupt", session_id, interruption_code, payload)); return {"status": "SENT"}


class GSCCTests(unittest.TestCase):
    def test_valid_message_accepted(self):
        msg = MessageEnvelope.create(kind="EVENT", type="HEARTBEAT", source=SRC, target=TARGET, scope=SCOPE, payload={"seq": 1})
        self.assertEqual(msg.schema, "gscc-message/v1")
        self.assertEqual(MessageEnvelope.from_dict(msg.to_dict()), msg)

    def test_unknown_kind_rejected(self):
        with self.assertRaises(UnsupportedMessageError):
            MessageEnvelope.create(kind="BOGUS", type="HEARTBEAT", source=SRC, target=TARGET)

    def test_unknown_command_rejected(self):
        with self.assertRaises(UnsupportedMessageError):
            MessageEnvelope.create(kind="COMMAND", type="DELETE_REPOSITORY", source={"system": "gacr"}, target=SRC)

    def test_event_serialization_is_deterministic(self):
        msg = MessageEnvelope.create(
            kind="EVENT", type="PROGRESS", source=SRC, target=TARGET, scope=SCOPE,
            payload={"step": 2, "status": "ADVANCING"}, message_id="m1", correlation_id="c1",
            idempotency_key="i1", issued_at="2026-10-02T04:30:00Z",
        )
        self.assertEqual(msg.serialize(), msg.serialize())
        self.assertEqual(json.loads(msg.serialize())["type"], "PROGRESS")

    def test_command_serialization(self):
        msg = command("STATUS_REQUEST")
        raw = json.loads(msg.serialize())
        self.assertEqual(raw["kind"], "COMMAND")
        self.assertTrue(raw["delivery"]["requires_ack"])

    def test_ack_correlation(self):
        transport = InMemoryTransport()
        endpoint = SessionEndpoint(transport, source=SRC, target=TARGET, scope=SCOPE, capabilities=["COMMAND_RECEIVE", "COMMAND_ACK"])
        cmd = command("PING")
        ack = endpoint.ack_command(cmd)["message"]
        self.assertEqual(ack.kind, "ACK")
        self.assertEqual(ack.correlation_id, cmd.correlation_id)
        self.assertEqual(ack.payload["command_message_id"], cmd.message_id)

    def test_capability_negotiation(self):
        transport = InMemoryTransport()
        endpoint = SessionEndpoint(transport, source=SRC, target=TARGET, scope=SCOPE, capabilities=["HEARTBEAT", "COMMAND_RECEIVE"])
        hello = endpoint.hello()["message"]
        self.assertEqual(hello.kind, "CAPABILITIES")
        self.assertEqual(hello.type, "HELLO")
        self.assertEqual(hello.payload["capabilities"], ["COMMAND_RECEIVE", "HEARTBEAT"])

    def test_unsupported_capability_is_explicit(self):
        transport = InMemoryTransport()
        endpoint = SessionEndpoint(transport, source=SRC, target=TARGET, scope=SCOPE, capabilities=["COMMAND_RECEIVE", "COMMAND_ACK"])
        transport.inject(command("LIVENESS_CHALLENGE"))
        result = endpoint.receive_commands()
        self.assertEqual(result[0]["status"], "UNSUPPORTED")
        ack = result[0]["ack"]["message"]
        self.assertEqual(ack.payload["state"], "UNSUPPORTED")
        self.assertEqual(ack.payload["reason_code"], "CHALLENGE_RESPONSE_UNAVAILABLE")

    def test_delivery_lifecycle(self):
        tracker = DeliveryTracker("m")
        for state in ["QUEUED", "DISPATCHED", "DELIVERED", "ACKNOWLEDGED", "EXECUTING", "COMPLETED"]:
            tracker.transition(state)
        self.assertEqual(tracker.state, "COMPLETED")
        with self.assertRaises(DeliveryTransitionError):
            tracker.transition("FAILED")

    def test_expiration(self):
        expired = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        msg = MessageEnvelope.create(kind="COMMAND", type="PING", source={"system": "gacr"}, target=SRC, expires_at=expired)
        tracker = DeliveryTracker(msg.message_id)
        self.assertTrue(tracker.expire_if_needed(msg))
        self.assertEqual(tracker.state, "EXPIRED")

    def test_no_response_semantics(self):
        tracker = DeliveryTracker("m")
        tracker.transition("QUEUED")
        tracker.transition("DISPATCHED")
        tracker.transition("DELIVERED")
        tracker.mark_no_response()
        self.assertEqual(tracker.state, "NO_RESPONSE")

    def test_duplicate_message_idempotence(self):
        store = IdempotencyStore()
        msg = command("PING")
        self.assertFalse(store.seen(msg))
        store.record(msg, {"ok": True})
        self.assertTrue(store.seen(msg))
        self.assertEqual(store.result(msg), {"ok": True})

    def test_duplicate_command_no_double_execution(self):
        transport = InMemoryTransport()
        endpoint = SessionEndpoint(transport, source=SRC, target=TARGET, scope=SCOPE, capabilities=["COMMAND_RECEIVE", "COMMAND_ACK"])
        cmd = command("PING")
        transport.inject(cmd)
        transport.inject(cmd)
        calls = []
        result = endpoint.receive_commands(lambda m: calls.append(m.message_id) or "done")
        self.assertEqual(calls, [cmd.message_id])
        self.assertEqual(result[0]["status"], "EXECUTED")
        self.assertEqual(result[1]["status"], "ALREADY_PROCESSED")

    def test_safe_payload_enforcement(self):
        with self.assertRaises(UnsafePayloadError):
            MessageEnvelope.create(kind="EVENT", type="CONTEXT_UPDATE", source=SRC, target=TARGET, payload={"access_token": "x"})

    def test_cookie_like_field_rejected(self):
        with self.assertRaises(UnsafePayloadError):
            MessageEnvelope.create(kind="EVENT", type="CONTEXT_UPDATE", source=SRC, target=TARGET, payload={"browser_session_cookie": "abc"})

    def test_transcript_like_field_rejected(self):
        with self.assertRaises(UnsafePayloadError):
            MessageEnvelope.create(kind="EVENT", type="CONTEXT_UPDATE", source=SRC, target=TARGET, payload={"raw_transcript": "hello"})

    def test_secret_like_value_rejected(self):
        with self.assertRaises(UnsafePayloadError):
            MessageEnvelope.create(kind="EVENT", type="CONTEXT_UPDATE", source=SRC, target=TARGET, payload={"opaque_ref": "Bearer top-secret"})

    def test_github_transport_compatibility(self):
        calls = []
        def request_fn(method, url, body):
            calls.append((method, url, body))
            return 204, b""
        transport = GitHubDispatchTransport("chainsolutions-wealthtech/Governed-Repository-Template", request_fn=request_fn)
        msg = MessageEnvelope.create(kind="EVENT", type="HEARTBEAT", source=SRC, target=TARGET, scope=SCOPE)
        result = transport.send(msg)
        self.assertEqual(result["event_type"], "gscc_event")
        self.assertEqual(calls[0][2]["client_payload"]["schema"], "gscc-message/v1")
        self.assertNotIn("Authorization", json.dumps(calls[0][2]))

    def test_existing_gacr_emitter_compatibility(self):
        fake = FakeEmitter()
        adapter = GACRClientEmitterAdapter(fake)
        msg = MessageEnvelope.create(kind="EVENT", type="HEARTBEAT", source=SRC, target=TARGET, scope=SCOPE, payload={"evidence": "safe-ref"})
        result = adapter.send(msg)
        self.assertEqual(result["status"], "SENT")
        self.assertEqual(fake.calls[0][0], "heartbeat")
        self.assertEqual(fake.calls[0][1], "session-a")

    def test_existing_gacr_emitter_resume_compatibility(self):
        emitter = FakeEmitter()
        adapter = GACRClientEmitterAdapter(emitter)
        msg = MessageEnvelope.create(
            kind="EVENT", type="SESSION_RESUME", source=SRC, target=TARGET, scope=SCOPE,
            payload={"connection_ref": "conn-a"},
        )
        adapter.send(msg)
        self.assertEqual(emitter.calls[0][0], "attach")
        self.assertEqual(emitter.calls[0][1]["connection_ref"], "conn-a")

    def test_session_endpoint_public_surface(self):
        transport = InMemoryTransport()
        endpoint = SessionEndpoint(transport, source=SRC, target=TARGET, scope=SCOPE, capabilities=["HEARTBEAT"])
        endpoint.attach(agent="worker")
        endpoint.resume(reason="restart")
        endpoint.heartbeat(seq=1)
        endpoint.activity_started(action_id="a1")
        endpoint.activity_completed(action_id="a1")
        endpoint.activity_failed(action_id="a2")
        endpoint.tool_started(tool_name="GitHub.fetch_file")
        endpoint.tool_completed(tool_name="GitHub.fetch_file")
        endpoint.tool_failed(tool_name="GitHub.fetch_file")
        endpoint.progress(checkpoint_ref="cp1")
        endpoint.blocked(reason_code="WAITING_DEPENDENCY")
        endpoint.checkpoint(checkpoint_ref="cp1")
        endpoint.context_update(context_ref="ctx1")
        endpoint.disconnect()
        self.assertEqual(len(transport.sent), 14)

    def test_tool_instrumentation_never_serializes_args_or_result(self):
        transport = InMemoryTransport()
        endpoint = SessionEndpoint(transport, source=SRC, target=TARGET, scope=SCOPE)
        wrapped = instrument_tool(endpoint, "demo.tool", lambda secret_arg: {"secret": secret_arg})
        result = wrapped("do-not-serialize-me")
        self.assertEqual(result, {"secret": "do-not-serialize-me"})
        serialized = "\n".join(m.serialize() for m in transport.sent)
        self.assertNotIn("do-not-serialize-me", serialized)
        self.assertIn("TOOL_STARTED", serialized)
        self.assertIn("TOOL_COMPLETED", serialized)


    def test_before_tool_call_runs_before_exposure_and_tool_started(self):
        transport = InMemoryTransport()
        endpoint = SessionEndpoint(transport, source=SRC, target=TARGET, scope=SCOPE)
        order = []

        def before(tool_name):
            order.append(("before", tool_name))
            return {"status": "FIRST_TOUCH_EMITTED"}

        def guard(tool_name):
            order.append(("guard", tool_name))
            return {"status": "VALIDATED", "exposable": True, "exposure_receipt": "receipt-1"}

        wrapped = instrument_tool(
            endpoint,
            "GitHub.get_repo",
            lambda: order.append(("call", "GitHub.get_repo")) or {"ok": True},
            before_tool_call=before,
            exposure_guard=guard,
        )
        result = wrapped()
        self.assertEqual(result, {"ok": True})
        self.assertEqual(order, [
            ("before", "GitHub.get_repo"),
            ("guard", "GitHub.get_repo"),
            ("call", "GitHub.get_repo"),
        ])
        types = [m.type for m in transport.sent]
        self.assertIn("TOOL_STARTED", types)
        self.assertIn("TOOL_COMPLETED", types)

    def test_unknown_capability_rejected(self):
        transport = InMemoryTransport()
        with self.assertRaises(UnsupportedMessageError):
            SessionEndpoint(transport, source=SRC, target=TARGET, capabilities=["MAGIC_WAKE"])

    def test_delivered_is_not_executed(self):
        transport = InMemoryTransport()
        endpoint = SessionEndpoint(transport, source=SRC, target=TARGET, capabilities=["COMMAND_RECEIVE"])
        transport.inject(command("PING"))
        result = endpoint.receive_commands()
        self.assertEqual(result[0]["status"], "DELIVERED")
        self.assertNotEqual(result[0]["status"], "EXECUTED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
