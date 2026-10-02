#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone

from gscc_observable_arrival import should_skip_github_arrival
from gscc_gacr.issue_control_bridge import (
    apply_host_control_event,
    build_liveness_challenge_dispatch,
    canonical_control_evidence,
    render_issue_challenge_comment,
)

NOW = datetime(2026, 10, 2, 13, 30, 0, tzinfo=timezone.utc)
REPOSITORY = "chainsolutions-wealthtech/Governed-Repository-Template"
SESSION_ID = "session-control-live"


def session():
    return {
        "session_id": SESSION_ID,
        "repository": REPOSITORY,
        "status": "ACTIVE",
        "connection_ref": "gscc-observable:test",
        "capabilities": ["GACR_AUTO_ATTACH", "GACR_PRESENCE_FIRST"],
        "relay": {
            "state": "ACTIVE",
            "lease_expires_at": "2026-10-02T14:00:00+00:00",
            "branch": "governance/gscc-admission-harvester",
        },
    }


def test_build_challenge_is_safe_bounded_and_non_authorizing():
    item = build_liveness_challenge_dispatch(
        session(),
        now=NOW,
        ttl_seconds=60,
        issue_number=115,
        nonce="nonce-test-001",
    )
    assert item["schema"] == "gscc-control-dispatch/v1", item
    assert item["kind"] == "CONTROL_CHALLENGE", item
    assert item["status"] == "READY", item
    assert item["target_session_id"] == SESSION_ID, item
    assert item["delivery_modes"] == ["GITHUB_ISSUE_COMMENT"], item
    assert item["command"]["command_type"] == "LIVENESS_CHALLENGE", item
    assert item["command"]["payload"]["nonce"] == "nonce-test-001", item
    assert item["mutation_authority_granted"] is False, item
    assert item["invocation_authority_granted"] is False, item


def test_issue_comment_is_bounded_and_contains_no_authority():
    item = build_liveness_challenge_dispatch(
        session(), now=NOW, ttl_seconds=60, issue_number=115, nonce="nonce-test-002"
    )
    body = render_issue_challenge_comment(item)
    assert body.startswith("/gscc-control-command "), body
    assert "LIVENESS_CHALLENGE" in body, body
    assert SESSION_ID in body, body
    assert "mutation_authority" not in body.lower(), body
    assert "authorization" not in body.lower(), body
    assert "token" not in body.lower(), body


def test_ack_then_challenge_response_produces_canonical_control_proof():
    item = build_liveness_challenge_dispatch(
        session(), now=NOW, ttl_seconds=60, issue_number=115, nonce="nonce-test-003"
    )
    store = {"schema_version": "1.0.0", "revision": 0, "items": [item]}
    command = item["command"]

    ack = apply_host_control_event(
        store,
        {
            "event": "command_ack",
            "session_id": SESSION_ID,
            "dispatch_id": item["dispatch_id"],
            "command_id": command["command_id"],
            "correlation_id": command["correlation_id"],
            "delivery_state": "ACKNOWLEDGED",
        },
        evidence_ref="github-issue-comment:700001",
        observed_at="2026-10-02T13:30:10+00:00",
    )
    assert ack["status"] == "ACKNOWLEDGED", ack
    assert item["status"] == "ACKNOWLEDGED", item

    response = apply_host_control_event(
        store,
        {
            "event": "challenge_response",
            "session_id": SESSION_ID,
            "dispatch_id": item["dispatch_id"],
            "command_id": command["command_id"],
            "correlation_id": command["correlation_id"],
            "challenge_id": command["payload"]["challenge_id"],
            "nonce": command["payload"]["nonce"],
            "challenge_status": "ACK",
        },
        evidence_ref="github-issue-comment:700002",
        observed_at="2026-10-02T13:30:20+00:00",
    )
    assert response["status"] == "COMPLETED", response
    assert response["fresh_liveness"] is True, response
    assert item["status"] == "COMPLETED", item

    proof = canonical_control_evidence(
        store,
        session_id=SESSION_ID,
        now=datetime(2026, 10, 2, 13, 30, 30, tzinfo=timezone.utc),
    )
    assert proof["capabilities"]["status"] == "VERIFIED", proof
    assert set(["COMMAND_RECEIVE", "COMMAND_ACK", "CHALLENGE_RESPONSE"]).issubset(
        set(proof["capabilities"]["verified"])
    ), proof
    assert proof["control_channel"]["status"] == "VERIFIED", proof
    assert proof["control_channel"]["evidence_ref"] == "github-issue-comment:700002", proof


def test_mismatch_and_response_without_ack_fail_closed():
    item = build_liveness_challenge_dispatch(
        session(), now=NOW, ttl_seconds=60, issue_number=115, nonce="nonce-test-004"
    )
    store = {"schema_version": "1.0.0", "revision": 0, "items": [item]}
    command = item["command"]

    try:
        apply_host_control_event(
            store,
            {
                "event": "challenge_response",
                "session_id": SESSION_ID,
                "dispatch_id": item["dispatch_id"],
                "command_id": command["command_id"],
                "correlation_id": command["correlation_id"],
                "challenge_id": command["payload"]["challenge_id"],
                "nonce": command["payload"]["nonce"],
                "challenge_status": "ACK",
            },
            evidence_ref="github-issue-comment:700003",
            observed_at="2026-10-02T13:30:15+00:00",
        )
    except ValueError as exc:
        assert "ACK" in str(exc).upper(), exc
    else:
        raise AssertionError("challenge response without prior ACK must fail")

    apply_host_control_event(
        store,
        {
            "event": "command_ack",
            "session_id": SESSION_ID,
            "dispatch_id": item["dispatch_id"],
            "command_id": command["command_id"],
            "correlation_id": command["correlation_id"],
            "delivery_state": "ACKNOWLEDGED",
        },
        evidence_ref="github-issue-comment:700004",
        observed_at="2026-10-02T13:30:16+00:00",
    )
    try:
        apply_host_control_event(
            store,
            {
                "event": "challenge_response",
                "session_id": SESSION_ID,
                "dispatch_id": item["dispatch_id"],
                "command_id": command["command_id"],
                "correlation_id": command["correlation_id"],
                "challenge_id": command["payload"]["challenge_id"],
                "nonce": "wrong-nonce",
                "challenge_status": "ACK",
            },
            evidence_ref="github-issue-comment:700005",
            observed_at="2026-10-02T13:30:20+00:00",
        )
    except ValueError as exc:
        assert "NONCE" in str(exc).upper(), exc
    else:
        raise AssertionError("nonce mismatch must fail")


def test_expired_session_or_challenge_cannot_be_verified():
    expired_session = session()
    expired_session["relay"]["lease_expires_at"] = "2026-10-02T13:00:00+00:00"
    try:
        build_liveness_challenge_dispatch(
            expired_session, now=NOW, ttl_seconds=60, issue_number=115, nonce="nonce-test-005"
        )
    except ValueError as exc:
        assert "LEASE" in str(exc).upper(), exc
    else:
        raise AssertionError("expired session lease must fail")

    item = build_liveness_challenge_dispatch(
        session(), now=NOW, ttl_seconds=10, issue_number=115, nonce="nonce-test-006"
    )
    store = {"schema_version": "1.0.0", "revision": 0, "items": [item]}
    command = item["command"]
    try:
        apply_host_control_event(
            store,
            {
                "event": "command_ack",
                "session_id": SESSION_ID,
                "dispatch_id": item["dispatch_id"],
                "command_id": command["command_id"],
                "correlation_id": command["correlation_id"],
                "delivery_state": "ACKNOWLEDGED",
            },
            evidence_ref="github-issue-comment:700006",
            observed_at="2026-10-02T13:30:20+00:00",
        )
    except ValueError as exc:
        assert "EXPIRED" in str(exc).upper(), exc
    else:
        raise AssertionError("expired challenge must fail")



def test_control_issue_comments_do_not_create_observable_arrival_sessions():
    env = {"GITHUB_EVENT_NAME": "issue_comment", "GITHUB_ACTOR": "github-actions[bot]"}
    request = {"comment": {"body": "/gscc-control {\"schema\":\"gscc-control-request/v1\"}"}}
    command = {"comment": {"body": "/gscc-control-command {\"schema\":\"gscc-control-command/v1\"}"}}
    assert should_skip_github_arrival(request, env) == "INTERNAL_GSCC_CONTROL_ISSUE_BRIDGE"
    assert should_skip_github_arrival(command, env) == "INTERNAL_GSCC_CONTROL_ISSUE_BRIDGE"


def main():
    test_build_challenge_is_safe_bounded_and_non_authorizing()
    test_issue_comment_is_bounded_and_contains_no_authority()
    test_ack_then_challenge_response_produces_canonical_control_proof()
    test_mismatch_and_response_without_ack_fail_closed()
    test_expired_session_or_challenge_cannot_be_verified()
    test_control_issue_comments_do_not_create_observable_arrival_sessions()
    print("GSCC_ISSUE_CONTROL_BRIDGE_TESTS_OK")


if __name__ == "__main__":
    main()
