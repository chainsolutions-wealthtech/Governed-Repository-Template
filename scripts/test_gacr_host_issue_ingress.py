#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gacr_host_issue_ingress", ROOT / "scripts" / "gacr_host_issue_ingress.py")
g = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = g
SPEC.loader.exec_module(g)


def assert_true(value, message: str) -> None:
    if not value:
        raise AssertionError(message)


def expect_error(fn, contains: str) -> None:
    try:
        fn()
        raise AssertionError(f"expected error containing {contains!r}")
    except Exception as exc:
        if isinstance(exc, AssertionError):
            raise
        assert_true(contains in str(exc), f"expected {contains!r} in {exc!r}")


def config() -> dict:
    return {
        "host_issue_bridge": {
            "enabled": True,
            "issue_number": 115,
            "allowed_author_associations": ["OWNER", "MEMBER", "COLLABORATOR"],
            "max_payload_chars": 8192,
        }
    }


def event(body: str, *, issue_number: int = 115, association: str = "MEMBER", comment_id: int = 9001) -> dict:
    return {
        "action": "created",
        "issue": {"number": issue_number, "title": "[GACR Host Bridge] Provider event ingress"},
        "comment": {
            "id": comment_id,
            "body": body,
            "author_association": association,
            "user": {"login": "agent-user"},
        },
        "sender": {"login": "agent-user"},
        "repository": {"full_name": "example/governed"},
    }


def body(payload: dict) -> str:
    return g.PREFIX + json.dumps(payload, separators=(",", ":"))


def main() -> None:
    valid = {
        "schema": g.SCHEMA,
        "event": "action",
        "connection_ref": "chronicle:demo:session-1",
        "client_instance_id": "chronicle:demo",
        "provider": "chatgpt",
        "action_id": "action-1",
        "action_label": "inspect repository",
        "action_phase": "STARTED",
        "tool_name": "github-connector",
        "tool_call_id": "call-1",
        "observed_head": "a" * 40,
    }
    parsed = g.parse_issue_comment_event(event(body(valid)), config())
    assert_true(parsed is not None, "valid host event parsed")
    assert_true(parsed["_evidence_ref"] == "github-issue-comment:9001", "comment id becomes evidence id")
    assert_true(parsed["_actor"] == "agent-user", "actor captured")

    assert_true(
        g.parse_issue_comment_event(event(body(valid), issue_number=114), config()) is None,
        "wrong issue ignored",
    )

    client_config = config()
    client_config["host_issue_bridge"]["issue_number"] = None
    parsed_by_title = g.parse_issue_comment_event(event(body(valid), issue_number=777), client_config)
    assert_true(parsed_by_title is not None, "client title fallback accepts repository-local issue number")
    wrong_title_event = event(body(valid), issue_number=777)
    wrong_title_event["issue"]["title"] = "Unrelated issue"
    assert_true(
        g.parse_issue_comment_event(wrong_title_event, client_config) is None,
        "client title fallback rejects unrelated issue title",
    )
    expect_error(
        lambda: g.parse_issue_comment_event(event(body(valid), association="NONE"), config()),
        "unauthorized",
    )

    unsafe = dict(valid)
    unsafe["api_token"] = "never"
    expect_error(lambda: g.parse_issue_comment_event(event(body(unsafe)), config()), "unsupported host-event fields")

    transcript = dict(valid)
    transcript["message"] = "raw transcript"
    expect_error(lambda: g.parse_issue_comment_event(event(body(transcript)), config()), "unsupported host-event fields")

    bad_phase = dict(valid)
    bad_phase["action_phase"] = "RUNNING"
    expect_error(lambda: g.parse_issue_comment_event(event(body(bad_phase)), config()), "supported action_phase")

    sessions = [
        {
            "session_id": "session-1",
            "repository": "example/governed",
            "provider": "other",
            "provider_conversation_ref": None,
            "connection_ref": "chronicle:demo:session-1",
            "client_instance_id": "chronicle:demo",
            "status": "ACTIVE",
            "relay": {"state": "ACTIVE"},
        }
    ]
    original_active_sessions = g.active_sessions
    g.active_sessions = lambda: sessions
    try:
        resolved = g.resolve_session(valid, "example/governed")
        assert_true(resolved and resolved["session_id"] == "session-1", "connection resolves existing session")
    finally:
        g.active_sessions = original_active_sessions

    calls = []
    original_processed = g.evidence_processed
    original_ensure = g.ensure_session
    original_run = g.run_script
    original_marker = g.marker_beacon
    try:
        g.evidence_processed = lambda evidence_ref: False
        g.ensure_session = lambda payload, repository: {"session_id": "session-1"}
        g.run_script = lambda path, args: calls.append((path.name, list(args))) or ""
        g.marker_beacon = lambda session_id, payload, event_type: calls.append(("marker", [session_id, event_type, payload["_evidence_ref"]]))
        payload = dict(parsed)
        result = g.process(payload, "example/governed")
        assert_true(result["status"] == "GACR_HOST_EVENT_PROCESSED", "action processed")
        assert_true(result["session_id"] == "session-1", "action stays on resolved session")
        assert_true(any(name == "governed_agent_continuity_relay.py" and args[0] == "heartbeat" for name, args in calls), "action renews heartbeat")
        assert_true(any(name == "marker" and args[1] == "ACTION_TRACE" for name, args in calls), "action trace emitted")
        assert_true(any(name == "gacr_agent_telemetry.py" and args[0] == "correlate" for name, args in calls), "correlation refreshed")
        assert_true(any(name == "gacr_agent_telemetry.py" and args[0] == "forensics" for name, args in calls), "forensics refreshed")

        g.evidence_processed = lambda evidence_ref: True
        calls.clear()
        replay = g.process(payload, "example/governed")
        assert_true(replay["status"] == "GACR_HOST_EVENT_ALREADY_PROCESSED", "same comment is idempotent")
        assert_true(not calls, "idempotent replay performs no mutation command")
    finally:
        g.evidence_processed = original_processed
        g.ensure_session = original_ensure
        g.run_script = original_run
        g.marker_beacon = original_marker

    print("GACR_HOST_ISSUE_INGRESS_TEST_PASS")


if __name__ == "__main__":
    main()
