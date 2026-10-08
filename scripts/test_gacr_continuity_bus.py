#!/usr/bin/env python3
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import gacr_continuity_bus as bus

NOW = datetime(2026, 10, 7, 22, 0, tzinfo=timezone.utc)
HEAD = "a" * 40


def session(session_id, *, bridge=False, live=True, silence_seconds=0, provider="chatgpt", provider_ref=None, agent="agent-shared"):
    heartbeat = NOW - timedelta(seconds=silence_seconds)
    return {
        "session_id": session_id,
        "status": "ACTIVE",
        "provider": provider,
        "agent_identity": agent,
        "provider_conversation_ref": provider_ref,
        "connection_ref": "connection-" + session_id,
        "client_instance_id": "client-" + session_id,
        "capabilities": ["COMMAND_RECEIVE", "COMMAND_ACK", "CHALLENGE_RESPONSE"],
        "wake_channels": ["EXTERNAL_BRIDGE", "POLL_REPOSITORY"] if bridge else ["POLL_REPOSITORY"],
        "bridge_registration_ref": "bridge-" + session_id if bridge else None,
        "relay": {
            "state": "ACTIVE",
            "last_heartbeat_at": bus.iso(heartbeat),
            "lease_expires_at": bus.iso(NOW + timedelta(minutes=30) if live else NOW - timedelta(minutes=1)),
        },
        "last_seen_at": bus.iso(heartbeat),
    }


def control_proof(session_id):
    return {
        "dispatch_id": "GSCC-CTRL-proof-" + session_id,
        "kind": "CONTROL_CHALLENGE",
        "status": "COMPLETED",
        "target_session_id": session_id,
        "command": {
            "command_type": "LIVENESS_CHALLENGE",
            "command_id": "GSCC-CMD-proof-" + session_id,
            "correlation_id": "GSCC-CORR-proof-" + session_id,
        },
        "ack": {
            "delivery_state": "ACKNOWLEDGED",
            "evidence_ref": "github-issue-comment:proof-ack",
            "observed_at": bus.iso(NOW - timedelta(seconds=5)),
        },
        "response": {
            "fresh_liveness": True,
            "evidence_ref": "github-issue-comment:proof-response",
            "observed_at": bus.iso(NOW - timedelta(seconds=4)),
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
                    "membership_state": "PERSISTENT",
                },
                {
                    "participant_id": "GACR-P-demo-b",
                    "session_id": "session-b",
                    "scope_id": "review",
                    "work_mode": "REVIEW",
                    "collision_domains": ["gacr:continuity:delivery"],
                    "status": "ACTIVE",
                    "membership_state": "PERSISTENT",
                },
                {
                    "participant_id": "GACR-P-demo-c",
                    "session_id": "session-c",
                    "scope_id": "recovery",
                    "work_mode": "READ_ONLY",
                    "collision_domains": ["gacr:continuity:delivery"],
                    "status": "YIELDED",
                    "membership_state": "PERSISTENT",
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

    endpoint_config = {
        "external_bridge": {"chatgpt_issue_bridge_live_proven": True},
        "host_issue_bridge": {
            "enabled": True,
            "issue_number": 115,
            "control_channel": {"enabled": True},
        },
    }
    for provider in ("chatgpt", "claude", "codex", "github-actions", "human", "other"):
        without_bridge = bus.provider_endpoint_descriptor(
            session("session-provider-" + provider, provider=provider),
            endpoint_config,
        )
        assert without_bridge["provider"] == provider
        assert without_bridge["provider_inbound_endpoint"]["status"] == "UNAVAILABLE"
        assert without_bridge["wake_route"]["push_capable"] is (provider == "chatgpt")
        assert without_bridge["provider_private_values_invented"] is False
        if provider == "chatgpt":
            assert without_bridge["wake_route"]["preferred"] == "GSCC_CONTROL_CHANNEL"
            assert without_bridge["wake_route"]["control_capable"] is True
        else:
            assert without_bridge["wake_route"]["preferred"] == "POLL_REPOSITORY"

        with_bridge = bus.provider_endpoint_descriptor(
            session("session-provider-bridge-" + provider, provider=provider, bridge=True),
            endpoint_config,
        )
        assert with_bridge["provider_inbound_endpoint"]["status"] == "OBSERVED"
        assert with_bridge["provider_inbound_endpoint"]["kind"] == "EXTERNAL_BRIDGE"
        assert with_bridge["wake_route"]["preferred"] == "EXTERNAL_BRIDGE"
        assert with_bridge["wake_route"]["push_capable"] is True

    control_state = base_state()
    control_sessions = {"sessions": [session("session-a"), session("session-b", bridge=True)]}
    control_dispatches = {"schema_version": "1.0.0", "revision": 0, "items": [control_proof("session-b")]}
    control_routed = bus.emit_event_docs(
        control_state,
        control_sessions,
        control_dispatches,
        continuity_id="GRT-CONT-DEMO-01",
        from_session_id="session-a",
        target_session_ids=["session-b"],
        event_kind="REVIEW_REQUEST",
        payload_ref="github-issue-comment:control-review",
        observed_head=HEAD,
        current_head=HEAD,
        evidence_ref="github-issue-comment:control-evidence",
        timestamp=NOW,
        scope_id="lab",
        collision_domains=["gacr:continuity:delivery"],
        config=endpoint_config,
    )
    control_route = control_routed["event"]["routes"][0]
    assert control_route["preferred_delivery_mode"] == "GSCC_CONTROL_CHANNEL"
    assert control_route["delivery_modes"] == ["GSCC_CONTROL_CHANNEL", "EXTERNAL_BRIDGE", "POLL_REPOSITORY"]
    control_item = next(x for x in control_dispatches["items"] if x.get("dispatch_kind") == "CONTINUITY_EVENT")
    assert control_item["preferred_delivery_mode"] == "GSCC_CONTROL_CHANNEL"
    assert control_item["status"] == "READY"
    assert control_route["control_evidence"]["transport_proven"] is True
    assert control_route["control_evidence"]["session_reachability"] == "VERIFIED"

    context_history_session = session("session-context-history", provider="chatgpt")
    current_context_id = bus.provider_context_descriptor(context_history_session)["provider_context_id"]
    context_history_session["provider_contexts"] = [
        {
            "provider_context_id": current_context_id,
            "provider": "chatgpt",
            "connection_ref": context_history_session["connection_ref"],
            "provider_native_identity_status": "UNAVAILABLE",
            "provider_private_values_invented": False,
        },
        {
            "provider_context_id": "GACR-PC-1111111111111111",
            "provider": "chatgpt",
            "connection_ref": "connection-history-2",
            "provider_native_identity_status": "UNAVAILABLE",
            "provider_private_values_invented": False,
        },
    ]
    context_history = bus.provider_context_descriptors(context_history_session)
    assert len(context_history) == 2
    assert {item["connection_ref"] for item in context_history} == {
        context_history_session["connection_ref"],
        "connection-history-2",
    }

    chatgpt_surface = bus.provider_endpoint_descriptor(
        session("session-chatgpt-surface", provider="chatgpt"),
        endpoint_config,
    )
    assert chatgpt_surface["repository_control_surface"]["status"] == "PROVEN"
    assert chatgpt_surface["repository_control_surface"]["kind"] == "GITHUB_ISSUE_CONTROL_CHANNEL"

    projection_state = base_state()
    projection_sessions = {"sessions": [
        session("session-a", silence_seconds=121, provider="chatgpt"),
        session("session-b", bridge=True, provider="claude", provider_ref="claude-conversation-1"),
        session("session-c", live=False, provider="codex", agent="agent-other"),
    ]}
    projection_sessions["sessions"][2]["status"] = "STALLED"
    projection_sessions["sessions"][2]["relay"]["state"] = "TAKEOVER_READY"
    projection_dispatches = {"schema_version": "1.0.0", "revision": 0, "items": []}
    projection_tick = bus.tick_docs(
        projection_state,
        projection_sessions,
        projection_dispatches,
        timestamp=NOW,
        early_supervision_after_seconds=120,
        config=endpoint_config,
    )
    pa, pb, pc = projection_state["items"][0]["participants"]
    assert pa["membership_state"] == "PERSISTENT"
    assert pa["liveness_state"] == "QUIET"
    assert pa["provider_endpoint"]["provider"] == "chatgpt"
    assert pa["provider_endpoint"]["provider_inbound_endpoint"]["status"] == "UNAVAILABLE"
    assert pa["provider_endpoint"]["repository_control_surface"]["status"] == "PROVEN"
    assert pa["provider_endpoint"]["repository_control_surface"]["kind"] == "GITHUB_ISSUE_CONTROL_CHANNEL"
    assert pb["membership_state"] == "PERSISTENT"
    assert pb["liveness_state"] == "LIVE"
    assert pb["provider_endpoint"]["provider"] == "claude"
    assert pb["provider_endpoint"]["provider_conversation_ref_status"] == "PRESENT"
    assert pb["provider_endpoint"]["provider_inbound_endpoint"]["status"] == "OBSERVED"
    assert pb["provider_endpoint"]["wake_route"]["push_capable"] is True
    assert pc["membership_state"] == "PERSISTENT"
    assert pc["liveness_state"] == "STALLED"
    assert pc["provider_endpoint"]["provider"] == "codex"
    assert pc["provider_endpoint"]["provider_inbound_endpoint"]["status"] == "UNAVAILABLE"
    assert pa["logical_agent_id"] == "agent-shared"
    assert pa["provider_contexts"][0]["provider_native_identity_status"] == "UNAVAILABLE"
    logical = {x["logical_agent_id"]: x for x in projection_state["items"][0]["logical_agents"]}
    assert logical["agent-shared"]["session_ids"] == ["session-a", "session-b"]
    assert logical["agent-shared"]["provider_context_count"] == 2
    assert logical["agent-other"]["session_ids"] == ["session-c"]
    assert any(x.get("state") == "PARTICIPANT_RUNTIME_PROJECTED" for x in projection_tick["changes"])
    assert any(x.get("state") == "LOGICAL_AGENT_PROJECTION_UPDATED" for x in projection_tick["changes"])

    cold_alias_state = {
        "schema_version": "1.0.0",
        "authority": "DERIVED_GACR_COORDINATION_PROJECTION",
        "projection_only": True,
        "grants_task_authority": False,
        "grants_claim": False,
        "grants_mutation_authority": False,
        "revision": 1,
        "items": [{
            "continuity_id": "GRT-CONT-ALIAS-COLD",
            "repository": "example/governed",
            "coordination_issue": 259,
            "projection_only": True,
            "participants": [],
            "logical_agents": [{
                "logical_agent_id": "agent-shared",
                "logical_agent_id_provenance": "CANONICAL_GACR_SESSION_AGENT_IDENTITY",
                "human_alias": "FORGE",
                "human_alias_provenance": "OWNER_ASSIGNED",
                "alias_evidence_ref": "github-issue-comment:owner",
                "routing_evidence_ref": "github-issue-comment:routing",
                "reference_session_ids": ["session-a"],
                "session_ids": ["session-a"],
                "provider_contexts": [],
                "projection_only": True,
                "grants_task_authority": False,
                "grants_claim": False,
                "grants_mutation_authority": False,
            }],
            "events": [],
            "last_sequence": 0,
        }],
    }
    cold_sessions = {
        "sessions": [
            session("session-a", agent="agent-shared"),
            session("session-a2", agent="agent-shared"),
        ]
    }
    cold_sessions["sessions"][1]["provider_contexts"] = [{
        "provider_context_id": "GACR-PC-bbbbbbbbbbbbbbbb",
        "provider": "chatgpt",
        "connection_ref": "connection-history-a2",
        "provider_native_identity_status": "UNAVAILABLE",
        "provider_private_values_invented": False,
    }]
    bus.project_logical_agents_docs(cold_alias_state, cold_sessions)
    cold_group = cold_alias_state["items"][0]["logical_agents"][0]
    assert cold_group["human_alias"] == "FORGE"
    assert cold_group["human_alias_provenance"] == "OWNER_ASSIGNED"
    assert cold_group["session_ids"] == ["session-a", "session-a2"]
    assert cold_group["session_count"] == 2
    assert cold_group["provider_context_count"] >= 2
    assert cold_group["grants_mutation_authority"] is False

    supervision_state = base_state()
    supervision_sessions = {"sessions": [
        session("session-a", silence_seconds=121),
        session("session-b", bridge=True),
        session("session-c", live=False),
    ]}
    original_supervision_sessions = deepcopy(supervision_sessions)
    supervision_dispatches = {"schema_version": "1.0.0", "revision": 0, "items": []}
    supervision_tick = bus.tick_docs(
        supervision_state,
        supervision_sessions,
        supervision_dispatches,
        timestamp=NOW,
        early_supervision_after_seconds=120,
    )
    supervision_changes = [x for x in supervision_tick["changes"] if x.get("state") == "EARLY_SUPERVISION_ALERT"]
    assert len(supervision_changes) == 1
    alert = supervision_state["items"][0]["supervision_alerts"][0]
    assert alert["target_session_id"] == "session-a"
    assert alert["changes_session_status"] is False
    assert alert["changes_lease"] is False
    assert alert["delivery_state"] == "FALLBACK_POLL_REQUIRED"
    assert supervision_dispatches["items"][0]["dispatch_kind"] == "CONTINUITY_SUPERVISION_ALERT"
    assert supervision_sessions == original_supervision_sessions

    second_tick = bus.tick_docs(
        supervision_state,
        supervision_sessions,
        supervision_dispatches,
        timestamp=NOW + timedelta(seconds=30),
        early_supervision_after_seconds=120,
    )
    assert not [x for x in second_tick["changes"] if x.get("state") == "EARLY_SUPERVISION_ALERT"]
    assert len(supervision_state["items"][0]["supervision_alerts"]) == 1

    refreshed_sessions = deepcopy(supervision_sessions)
    refreshed_sessions["sessions"][0]["relay"]["last_heartbeat_at"] = bus.iso(NOW + timedelta(seconds=31))
    refreshed_sessions["sessions"][0]["last_seen_at"] = bus.iso(NOW + timedelta(seconds=31))
    resolve_tick = bus.tick_docs(
        supervision_state,
        refreshed_sessions,
        supervision_dispatches,
        timestamp=NOW + timedelta(seconds=31),
        early_supervision_after_seconds=120,
    )
    assert any(x.get("state") == "RESOLVED" for x in resolve_tick["changes"])
    assert alert["state"] == "RESOLVED"
    assert refreshed_sessions["sessions"][0]["relay"]["lease_expires_at"] == original_supervision_sessions["sessions"][0]["relay"]["lease_expires_at"]

    expired_projection = session("session-expired-projection", live=False, provider="chatgpt")
    assert bus.derive_liveness_state(expired_projection, NOW) == "STALLED"

    stalled_state = base_state()
    stalled_sessions = {"sessions": [
        session("session-a"),
        session("session-b", bridge=True),
        session("session-c", live=False),
    ]}
    stalled_sessions["sessions"][0]["status"] = "STALLED"
    stalled_sessions["sessions"][0]["relay"]["state"] = "TAKEOVER_READY"
    stalled_sessions["sessions"][0]["relay"]["last_heartbeat_at"] = bus.iso(NOW - timedelta(minutes=10))
    stalled_dispatches = {"items": []}
    stalled_tick = bus.tick_docs(
        stalled_state,
        stalled_sessions,
        stalled_dispatches,
        timestamp=NOW,
        early_supervision_after_seconds=120,
    )
    assert not [x for x in stalled_tick["changes"] if x.get("state") == "EARLY_SUPERVISION_ALERT"]

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
    tick = bus.tick_docs(timeout_state, sessions, timeout_dispatch, timestamp=NOW + timedelta(seconds=6))
    assert tick["changes"][0]["state"] == "ACK_TIMEOUT"
    assert timeout_event["routes"][0]["delivery_state"] == "ACK_TIMEOUT"
    assert "POLL_REPOSITORY" in timeout_event["routes"][0]["delivery_modes"]

    print("GACR_CONTINUITY_BUS_TESTS_PASS")


if __name__ == "__main__":
    main()
