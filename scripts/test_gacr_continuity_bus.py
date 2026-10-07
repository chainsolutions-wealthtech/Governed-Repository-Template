#!/usr/bin/env python3
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import gacr_continuity_bus as bus

NOW = datetime(2026, 10, 7, 22, 0, tzinfo=timezone.utc)
HEAD = "a" * 40


def session(session_id, *, bridge=False, live=True):
    return {
        "session_id": session_id,
        "status": "ACTIVE",
        "client_instance_id": "client-" + session_id,
        "wake_channels": ["EXTERNAL_BRIDGE", "POLL_REPOSITORY"] if bridge else ["POLL_REPOSITORY"],
        "bridge_registration_ref": "bridge-" + session_id if bridge else None,
        "relay": {
            "state": "ACTIVE",
            "last_heartbeat_at": bus.iso(NOW),
            "lease_expires_at": bus.iso(NOW + timedelta(minutes=30) if live else NOW - timedelta(minutes=1)),
        },
    }


def base_state():
    return {
        "schema_version": "1.0.0",
        "authority": "DERIVED_GACR_COORDINATION_PROJECTION",
        "projection_only": True,
        "grants_task_authority": False,
        "grants_claim": False,
        "grants_mutation_authority": False,
        "revision": 0,
        "items": [{
            "continuity_id": "GRT-CONT-DEMO-01",
            "repository": "example/governed",
            "coordination_issue": 259,
            "projection_only": True,
            "participants": [
                {
                    "participant_id": "GACR-P-demo-a",
                    "session_id": "session-a",
                    "scope_id": "lab",
                    "work_mode": "WRITE",
                    "collision_domains": ["gacr:continuity:projection", "gacr:continuity:delivery"],
                    "status": "ACTIVE",
                },
                {
                    "participant_id": "GACR-P-demo-b",
                    "session_id": "session-b",
                    "scope_id": "review",
                    "work_mode": "REVIEW",
                    "collision_domains": ["gacr:continuity:delivery"],
                    "status": "ACTIVE",
                },
                {
                    "participant_id": "GACR-P-demo-c",
                    "session_id": "session-c",
                    "scope_id": "recovery",
                    "work_mode": "READ_ONLY",
                    "collision_domains": ["gacr:continuity:delivery"],
                    "status": "YIELDED",
                },
            ],
            "events": [],
            "last_sequence": 0,
        }],
    }


def expect_error(fn, needle):
    try:
        fn()
    except Exception as exc:
        assert needle in str(exc), (needle, str(exc))
        return
    raise AssertionError("expected error: " + needle)


def main():
    sessions = {"sessions": [session("session-a"), session("session-b", bridge=True), session("session-c", live=False)]}
    original_sessions = deepcopy(sessions)
    state = base_state()
    dispatches = {"schema_version": "1.0.0", "revision": 0, "items": []}

    routed = bus.emit_event_docs(
        state, sessions, dispatches,
        continuity_id="GRT-CONT-DEMO-01",
        from_session_id="session-a",
        target_session_ids=["session-b"],
        event_kind="REQUEST",
        payload_ref="github-issue-comment:100",
        observed_head=HEAD,
        current_head=HEAD,
        evidence_ref="github-issue-comment:101",
        timestamp=NOW,
        scope_id="lab",
        collision_domains=["gacr:continuity:delivery"],
        requires_ack=True,
    )
    event = routed["event"]
    route = event["routes"][0]
    assert route["preferred_delivery_mode"] == "EXTERNAL_BRIDGE"
    assert dispatches["items"][0]["status"] == "READY"
    assert routed["heartbeat_transferred"] is False
    assert sessions == original_sessions

    bus.mark_delivery_docs(
        state,
        continuity_id="GRT-CONT-DEMO-01",
        event_id=event["event_id"],
        target_session_id="session-b",
        delivery_state="DELIVERED",
        timestamp=NOW + timedelta(seconds=1),
        evidence_ref="bridge:delivered",
    )
    assert route["delivery_state"] == "DELIVERED"
    assert route["ack_deadline_at"]

    acked = bus.ack_event_docs(
        state, sessions,
        continuity_id="GRT-CONT-DEMO-01",
        event_id=event["event_id"],
        session_id="session-b",
        observed_head=HEAD,
        current_head=HEAD,
        evidence_ref="github-issue-comment:102",
        timestamp=NOW + timedelta(seconds=2),
    )
    assert acked["status"] == "CONTINUITY_EVENT_ACKED"
    assert acked["heartbeat_transferred"] is False

    responded = bus.respond_event_docs(
        state, sessions,
        continuity_id="GRT-CONT-DEMO-01",
        event_id=event["event_id"],
        session_id="session-b",
        response_ref="github-issue-comment:103",
        observed_head=HEAD,
        current_head=HEAD,
        evidence_ref="github-issue-comment:103",
        timestamp=NOW + timedelta(seconds=3),
    )
    assert responded["status"] == "CONTINUITY_EVENT_RESPONDED"
    assert event["state"] == "RESPONDED"

    fallback = bus.emit_event_docs(
        state, sessions, dispatches,
        continuity_id="GRT-CONT-DEMO-01",
        from_session_id="session-a",
        target_session_ids=["session-c"],
        event_kind="INSTRUCTION",
        payload_ref="github-issue-comment:200",
        observed_head=HEAD,
        current_head=HEAD,
        evidence_ref="github-issue-comment:201",
        timestamp=NOW,
        scope_id="lab",
        collision_domains=["gacr:continuity:delivery"],
    )
    assert fallback["event"]["routes"][0]["preferred_delivery_mode"] == "POLL_REPOSITORY"
    assert fallback["event"]["routes"][0]["delivery_state"] == "FALLBACK_POLL_REQUIRED"
    assert sessions == original_sessions

    expect_error(
        lambda: bus.emit_event_docs(
            base_state(), sessions, {"items": []},
            continuity_id="GRT-CONT-DEMO-01",
            from_session_id="session-a",
            target_session_ids=["session-b"],
            event_kind="REQUEST",
            payload_ref="ref",
            observed_head="b" * 40,
            current_head=HEAD,
            evidence_ref="evidence",
            timestamp=NOW,
            scope_id="lab",
            collision_domains=["gacr:continuity:delivery"],
        ),
        "HEAD_MOVED",
    )

    outsider_sessions = deepcopy(sessions)
    outsider_sessions["sessions"].append(session("session-outsider", bridge=True))
    expect_error(
        lambda: bus.emit_event_docs(
            base_state(), outsider_sessions, {"items": []},
            continuity_id="GRT-CONT-DEMO-01",
            from_session_id="session-a",
            target_session_ids=["session-outsider"],
            event_kind="REQUEST",
            payload_ref="ref-outsider",
            observed_head=HEAD,
            current_head=HEAD,
            evidence_ref="evidence-outsider",
            timestamp=NOW,
            scope_id="lab",
            collision_domains=["gacr:continuity:delivery"],
        ),
        "TARGET_NOT_MEMBER_OF_CONTINUITY",
    )

    timeout_state = base_state()
    timeout_dispatch = {"items": []}
    timeout_event = bus.emit_event_docs(
        timeout_state, sessions, timeout_dispatch,
        continuity_id="GRT-CONT-DEMO-01",
        from_session_id="session-a",
        target_session_ids=["session-b"],
        event_kind="REQUEST",
        payload_ref="ref-timeout",
        observed_head=HEAD,
        current_head=HEAD,
        evidence_ref="evidence-timeout",
        timestamp=NOW,
        scope_id="lab",
        collision_domains=["gacr:continuity:delivery"],
        ack_timeout_seconds=5,
    )["event"]
    bus.mark_delivery_docs(
        timeout_state,
        continuity_id="GRT-CONT-DEMO-01",
        event_id=timeout_event["event_id"],
        target_session_id="session-b",
        delivery_state="DELIVERED",
        timestamp=NOW,
    )
    tick = bus.tick_docs(timeout_state, timeout_dispatch, timestamp=NOW + timedelta(seconds=6))
    assert tick["changes"][0]["state"] == "ACK_TIMEOUT"
    assert timeout_event["routes"][0]["delivery_state"] == "ACK_TIMEOUT"
    assert "POLL_REPOSITORY" in timeout_event["routes"][0]["delivery_modes"]

    print("GACR_CONTINUITY_BUS_TESTS_PASS")


if __name__ == "__main__":
    main()
