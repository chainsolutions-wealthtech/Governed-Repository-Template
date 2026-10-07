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
            "issue_title": "[GACR Host Bridge] Provider event ingress",
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
        "entry_action": "CONTINUE_GOVERNED_WORK",
        "connection_intent": "OBSERVE",
    }
    parsed = g.parse_issue_comment_event(event(body(valid)), config())
    assert_true(parsed is not None, "valid host event parsed")
    assert_true(parsed["_evidence_ref"] == "github-issue-comment:9001", "comment id becomes evidence id")
    assert_true(parsed["_actor"] == "agent-user", "actor captured")
    assert_true(parsed["entry_action"] == "CONTINUE_GOVERNED_WORK", "canonical entry action preserved")
    assert_true(parsed["connection_intent"] == "OBSERVE", "canonical connection intent preserved")

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

    invalid_entry = dict(valid)
    invalid_entry["entry_action"] = "REPOSITORY_ACCESS"
    expect_error(
        lambda: g.parse_issue_comment_event(event(body(invalid_entry), comment_id=9002), config()),
        "entry_action",
    )

    invalid_intent = dict(valid)
    invalid_intent["connection_intent"] = "READ_ONLY_DISCOVERY"
    expect_error(
        lambda: g.parse_issue_comment_event(event(body(invalid_intent), comment_id=9003), config()),
        "connection_intent",
    )

    availability_payload = {
        "schema": g.SCHEMA,
        "event": "availability",
        "session_id": "session-1",
        "availability_state": "RATE_LIMITED",
        "availability_reason_code": "PROVIDER_RATE_LIMIT",
    }
    parsed_availability = g.parse_issue_comment_event(
        event(body(availability_payload), comment_id=9004),
        config(),
    )
    assert_true(parsed_availability["availability_state"] == "RATE_LIMITED", "availability state parsed")
    invalid_availability = dict(availability_payload)
    invalid_availability["availability_state"] = "MAYBE"
    expect_error(
        lambda: g.parse_issue_comment_event(event(body(invalid_availability), comment_id=9005), config()),
        "availability_state",
    )

    work_offer_payload = {
        "schema": g.SCHEMA,
        "event": "work_offer_accept",
        "session_id": "session-1",
        "dispatch_id": "GACR-W-demo",
    }
    parsed_work_offer = g.parse_issue_comment_event(
        event(body(work_offer_payload), comment_id=9006),
        config(),
    )
    assert_true(parsed_work_offer["dispatch_id"] == "GACR-W-demo", "work offer dispatch id parsed")
    missing_dispatch = dict(work_offer_payload)
    del missing_dispatch["dispatch_id"]
    expect_error(
        lambda: g.parse_issue_comment_event(event(body(missing_dispatch), comment_id=9007), config()),
        "dispatch_id",
    )

    work_relinquish_payload = {
        "schema": g.SCHEMA,
        "event": "work_relinquish",
        "session_id": "session-1",
        "claim_id": "GACR-C-demo",
        "reason_code": "CONTEXT_LIMIT",
        "observed_head": "f" * 40,
        "checkpoint_ref": "CHK-demo",
        "handoff_ref": "HANDOFF-demo",
    }
    parsed_relinquish = g.parse_issue_comment_event(
        event(body(work_relinquish_payload), comment_id=9008),
        config(),
    )
    assert_true(parsed_relinquish["claim_id"] == "GACR-C-demo", "relinquish claim parsed")
    missing_handoff = dict(work_relinquish_payload)
    del missing_handoff["handoff_ref"]
    expect_error(
        lambda: g.parse_issue_comment_event(event(body(missing_handoff), comment_id=9009), config()),
        "handoff_ref",
    )

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

    route_calls = []
    original_active_sessions_route = g.active_sessions
    original_run_route = g.run_script
    try:
        attached_route_session = {
            "session_id": "session-route",
            "repository": "example/governed",
            "provider": "chatgpt",
            "connection_ref": "chronicle:demo:route",
            "client_instance_id": "chronicle:route",
            "status": "ACTIVE",
            "entry_action": "CONTINUE_GOVERNED_WORK",
            "connection_intent": "OBSERVE",
            "relay": {"state": "ACTIVE", "branch": "main"},
        }
        route_reads = {"count": 0}

        def route_sessions():
            route_reads["count"] += 1
            return [] if route_reads["count"] == 1 else [attached_route_session]

        g.active_sessions = route_sessions
        g.run_script = lambda path, args: route_calls.append((path.name, list(args))) or ""
        route_payload = {
            "provider": "chatgpt",
            "connection_ref": "chronicle:demo:route",
            "client_instance_id": "chronicle:route",
            "observed_head": "e" * 40,
            "branch": "main",
            "entry_action": "CONTINUE_GOVERNED_WORK",
            "connection_intent": "OBSERVE",
        }
        resolved_route = g.ensure_session(route_payload, "example/governed")
        assert_true(resolved_route["session_id"] == "session-route", "new host route session attached")
        auto_attach_calls = [args for name, args in route_calls if name == "gacr_auto_attach.py"]
        assert_true(len(auto_attach_calls) == 1, "new host session uses one canonical auto-attach")
        auto_args = auto_attach_calls[0]
        assert_true("--entry-action" in auto_args and "CONTINUE_GOVERNED_WORK" in auto_args, "entry action forwarded")
        assert_true("--connection-intent" in auto_args and "OBSERVE" in auto_args, "connection intent forwarded")
    finally:
        g.active_sessions = original_active_sessions_route
        g.run_script = original_run_route

    provider_calls = []
    original_active_sessions_provider = g.active_sessions
    original_run_provider = g.run_script
    try:
        generic_session = {
            "session_id": "session-provider",
            "repository": "example/governed",
            "provider": "other",
            "provider_conversation_ref": None,
            "connection_ref": "chronicle:demo:session-provider",
            "client_instance_id": "chronicle:demo-provider",
            "agent_identity": "conversation-agent",
            "status": "ACTIVE",
            "relay": {"state": "ACTIVE", "branch": "main"},
        }
        enriched_session = dict(generic_session)
        enriched_session["provider"] = "chatgpt"
        reads = {"count": 0}
        def provider_sessions():
            reads["count"] += 1
            return [generic_session] if reads["count"] == 1 else [enriched_session]
        g.active_sessions = provider_sessions
        g.run_script = lambda path, args: provider_calls.append((path.name, list(args))) or ""
        payload_provider = {
            "provider": "chatgpt",
            "connection_ref": "chronicle:demo:session-provider",
            "client_instance_id": "chronicle:demo-provider",
            "observed_head": "d" * 40,
            "entry_action": "CONTINUE_GOVERNED_WORK",
            "connection_intent": "OBSERVE",
        }
        resolved_provider = g.ensure_session(payload_provider, "example/governed")
        assert_true(resolved_provider["provider"] == "chatgpt", "host provider enrichment should return enriched session")
        assert_true(any(name == "gacr_auto_attach.py" and "--provider" in args and "chatgpt" in args for name, args in provider_calls), "host provider enrichment must reuse auto-attach path")
        provider_auto_args = next(args for name, args in provider_calls if name == "gacr_auto_attach.py")
        assert_true("--entry-action" not in provider_auto_args, "provider enrichment must not resolve entry action")
        assert_true("--connection-intent" not in provider_auto_args, "provider enrichment must not resolve connection intent")
    finally:
        g.active_sessions = original_active_sessions_provider
        g.run_script = original_run_provider

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
