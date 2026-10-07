#!/usr/bin/env python3
from __future__ import annotations

import base64
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gacr_client_emitter", ROOT / "scripts" / "gacr_client_emitter.py")
g = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = g
SPEC.loader.exec_module(g)


def assert_true(value, message: str) -> None:
    if not value:
        raise AssertionError(message)


def main() -> None:
    sent = []

    def fake_request(method, url, token, *, body=None, timeout=15):
        sent.append({"method": method, "url": url, "token": token, "body": body})
        return 204, b""

    emitter = g.ClientEmitter(
        repository="example/governed",
        token="runtime-only",
        api_base="https://api.example.test",
        request_fn=fake_request,
    )

    attach = emitter.attach(
        agent="client-agent",
        provider="chatgpt",
        provider_ref="conversation-123",
        connection_ref="client:one",
        client_instance_id="client-one",
        observed_head="a"*40,
        branch="main",
    )
    assert_true(attach["status"] == "SENT", "attach sent")
    assert_true(sent[-1]["body"]["event_type"] == "gacr_auto-attach", "attach event")
    assert_true(sent[-1]["body"]["client_payload"]["source"] == "CLIENT_EMITTER", "client provenance")
    assert_true("runtime-only" not in json.dumps(sent[-1]["body"]), "credential never enters payload")

    hb = emitter.heartbeat(
        "session-1",
        observed_head="b"*40,
        action_label="CLIENT_HEARTBEAT",
        workload_state="WAITING_FOR_WORK",
        capacity_slots=1,
        max_parallel_tasks=1,
    )
    assert_true(hb["status"] == "SENT", "heartbeat sent")
    assert_true(sent[-1]["body"]["event_type"] == "gacr_heartbeat", "heartbeat event")
    assert_true(sent[-1]["body"]["client_payload"]["session_id"] == "session-1", "heartbeat session")
    assert_true(sent[-1]["body"]["client_payload"]["workload_state"] == "WAITING_FOR_WORK", "heartbeat workload state")
    assert_true(sent[-1]["body"]["client_payload"]["capacity_slots"] == 1, "heartbeat capacity")

    trace = emitter.trace(
        "session-1",
        action_phase="STARTED",
        action_id="action-1",
        action_label="review repository",
        tool_name="github",
        tool_call_id="tool-1",
    )
    assert_true(trace["client_payload"]["event_type"] == "ACTION_TRACE", "trace event type")
    assert_true(trace["client_payload"]["action_phase"] == "STARTED", "trace phase")
    assert_true(trace["client_payload"]["source"] == "CLIENT_EMITTER", "trace provenance")

    interrupted = emitter.interrupt(
        "session-1",
        interruption_code="NETWORK_LOSS",
        action_label="network observer",
    )
    assert_true(interrupted["client_payload"]["event_type"] == "INTERRUPTION_SIGNAL", "interrupt event")
    assert_true(interrupted["client_payload"]["interruption_code"] == "NETWORK_LOSS", "interrupt code")

    try:
        g.assert_safe_payload({"api_token": "x"})
        raise AssertionError("unsafe key accepted")
    except ValueError:
        pass

    daemon_events = []
    dry = g.ClientEmitter(repository="example/governed", dry_run=True)
    g.daemon_loop(
        dry,
        session_id="session-1",
        observed_head="c"*40,
        interval_seconds=0,
        cycles=3,
        action_label=None,
        evidence=None,
        poll_wake=False,
        dispatches_path=".governance/agent-relay/dispatches.json",
        ref="main",
        client_instance_id="client-one",
        sleep_fn=lambda _: None,
        output_fn=daemon_events.append,
    )
    assert_true(len(daemon_events) == 3, "daemon emits requested heartbeat cycles")
    assert_true(all(x["event_type"] == "gacr_heartbeat" for x in daemon_events), "daemon heartbeat only")
    assert_true(all(x["client_payload"]["source"] == "CLIENT_EMITTER" for x in daemon_events), "daemon provenance")

    sessions = {
        "sessions": [
            {
                "session_id": "session-1",
                "repository": "example/governed",
                "provider": "other",
                "provider_conversation_ref": None,
                "connection_ref": "client:one",
                "relay": {"state": "ACTIVE"},
            }
        ]
    }
    resolved = g.select_session(
        sessions,
        repository="example/governed",
        connection_ref="client:one",
        provider="chatgpt",
        provider_ref=None,
    )
    assert_true(resolved and resolved["session_id"] == "session-1", "connection session resolves before provider enrichment")

    dispatches = {
        "items": [
            {
                "dispatch_id": "GACR-D-000000000001",
                "status": "READY",
                "target_session_id": "session-1",
                "target_client_instance_id": "client-one",
                "created_at": "2026-10-02T00:00:00+00:00",
            },
            {
                "dispatch_id": "GACR-D-000000000002",
                "status": "CANCELLED",
                "target_session_id": "session-1",
                "created_at": "2026-10-02T00:01:00+00:00",
            },
        ]
    }
    wakes = g.select_wake_events(dispatches, session_id="session-1", client_instance_id=None)
    assert_true(len(wakes) == 1 and wakes[0]["dispatch_id"].endswith("1"), "only actionable wake returned")

    content_doc = {"items": [{"dispatch_id": "GACR-D-test"}]}
    contents_api = json.dumps({
        "encoding": "base64",
        "content": base64.b64encode(json.dumps(content_doc).encode()).decode(),
    }).encode()

    def fake_get(method, url, token, *, body=None, timeout=15):
        assert_true(method == "GET", "content fetch uses GET")
        assert_true(body is None, "content fetch sends no body")
        return 200, contents_api

    fetched = g.fetch_json_file(
        "example/governed",
        ".governance/agent-relay/dispatches.json",
        token="runtime-only",
        api_base="https://api.example.test",
        request_fn=fake_get,
    )
    assert_true(fetched == content_doc, "content fetch decodes GitHub response")

    print("GACR_CLIENT_EMITTER_TEST_PASS")


if __name__ == "__main__":
    main()
