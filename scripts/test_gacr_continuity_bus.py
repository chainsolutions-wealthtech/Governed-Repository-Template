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

    fallback_preserve_state = base_state()
    fallback_preserve_dispatches = {"schema_version": "1.0.0", "revision": 0, "items": []}
    fallback_preserve_event = bus.emit_event_docs(
        fallback_preserve_state, sessions, fallback_preserve_dispatches,
        continuity_id="GRT-CONT-DEMO-01",
        from_session_id="session-a",
        target_session_ids=["session-b"],
        event_kind="REQUEST",
        payload_ref="github-issue-comment:poll-preserve",
        observed_head=HEAD,
        current_head=HEAD,
        evidence_ref="github-issue-comment:poll-preserve",
        timestamp=NOW,
        scope_id="lab",
        collision_domains=["gacr:continuity:delivery"],
    )["event"]
    fallback_route = fallback_preserve_event["routes"][0]
    fallback_dispatch = next(
        item for item in fallback_preserve_dispatches["items"]
        if item.get("dispatch_id") == fallback_route["dispatch_id"]
    )
    fallback_dispatch["status"] = "FALLBACK_POLL_REQUIRED"
    fallback_route["delivery_state"] = "FALLBACK_POLL_REQUIRED"
    poll_ack = bus.ack_event_docs(
        fallback_preserve_state, sessions,
        continuity_id="GRT-CONT-DEMO-01",
        event_id=fallback_preserve_event["event_id"],
        session_id="session-b",
        observed_head=HEAD,
        current_head=HEAD,
        evidence_ref="github-issue-comment:poll-ack",
        timestamp=NOW + timedelta(seconds=4),
    )
    assert poll_ack["status"] == "CONTINUITY_EVENT_ACKED"
    bus.tick_docs(
        fallback_preserve_state, sessions, fallback_preserve_dispatches,
        timestamp=NOW + timedelta(seconds=5),
    )
    assert fallback_route["delivery_state"] == "ACKED", "fallback dispatch must not overwrite polling ACK"

    fallback_response_state = base_state()
    fallback_response_dispatches = {"schema_version": "1.0.0", "revision": 0, "items": []}
    fallback_response_event = bus.emit_event_docs(
        fallback_response_state, sessions, fallback_response_dispatches,
        continuity_id="GRT-CONT-DEMO-01",
        from_session_id="session-a",
        target_session_ids=["session-b"],
        event_kind="REQUEST",
        payload_ref="github-issue-comment:poll-response",
        observed_head=HEAD,
        current_head=HEAD,
        evidence_ref="github-issue-comment:poll-response",
        timestamp=NOW,
        scope_id="lab",
        collision_domains=["gacr:continuity:delivery"],
    )["event"]
    fallback_response_route = fallback_response_event["routes"][0]
    fallback_response_dispatch = next(
        item for item in fallback_response_dispatches["items"]
        if item.get("dispatch_id") == fallback_response_route["dispatch_id"]
    )
    fallback_response_dispatch["status"] = "FALLBACK_POLL_REQUIRED"
    fallback_response_route["delivery_state"] = "FALLBACK_POLL_REQUIRED"
    poll_response = bus.respond_event_docs(
        fallback_response_state, sessions,
        continuity_id="GRT-CONT-DEMO-01",
        event_id=fallback_response_event["event_id"],
        session_id="session-b",
        response_ref="github-issue-comment:poll-response-value",
        observed_head=HEAD,
        current_head=HEAD,
        evidence_ref="github-issue-comment:poll-response-evidence",
        timestamp=NOW + timedelta(seconds=4),
    )
    assert poll_response["status"] == "CONTINUITY_EVENT_RESPONDED"
    bus.tick_docs(
        fallback_response_state, sessions, fallback_response_dispatches,
        timestamp=NOW + timedelta(seconds=5),
    )
    assert fallback_response_route["delivery_state"] == "RESPONDED", "fallback dispatch must not overwrite polling response"

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
        if provider == "chatgpt":
            assert with_bridge["wake_route"]["preferred"] == "GSCC_CONTROL_CHANNEL"
            assert with_bridge["wake_route"]["control_capable"] is True
        else:
            assert with_bridge["wake_route"]["preferred"] == "EXTERNAL_BRIDGE"
        assert with_bridge["wake_route"]["push_capable"] is True

    alias_state = base_state()
    alias_state["items"][0]["logical_agents"] = [{
        "logical_agent_id": "agent-forge",
        "human_alias": "FORGE",
        "human_alias_provenance": "OWNER_ASSIGNED",
        "reference_session_ids": ["session-b"],
        "session_ids": ["session-b"],
        "provider_contexts": [],
        "projection_only": True,
        "grants_task_authority": False,
        "grants_claim": False,
        "grants_mutation_authority": False,
    }]
    alias_sessions = {
        "sessions": [
            session("session-a", agent="agent-emitter"),
            session("session-b", agent="agent-forge"),
            session("session-c", live=False, agent="agent-other"),
        ]
    }
    alias_targets, alias_resolution = bus.resolve_event_targets(
        alias_state,
        alias_sessions,
        continuity_id="GRT-CONT-DEMO-01",
        target_logical_agent_alias="forge",
    )
    assert alias_targets == ["session-b"]
    assert alias_resolution["logical_agent_id"] == "agent-forge"
    assert alias_resolution["grants_mutation_authority"] is False
    alias_emit_dispatches = {"schema_version": "1.0.0", "revision": 0, "items": []}
    alias_emitted = bus.emit_event_docs(
        alias_state, alias_sessions, alias_emit_dispatches,
        continuity_id="GRT-CONT-DEMO-01",
        from_session_id="session-a",
        target_session_ids=alias_targets,
        event_kind="INSTRUCTION",
        payload_ref="github-issue-comment:alias-instruction",
        observed_head=HEAD,
        current_head=HEAD,
        evidence_ref="github-issue-comment:alias-evidence",
        timestamp=NOW,
        scope_id="lab",
        collision_domains=["gacr:continuity:delivery"],
    )
    assert alias_emitted["event"]["routes"][0]["target_session_id"] == "session-b"

    try:
        bus.resolve_event_targets(
            alias_state, alias_sessions,
            continuity_id="GRT-CONT-DEMO-01",
            target_logical_agent_alias="UNKNOWN",
        )
    except ValueError as exc:
        assert "LOGICAL_AGENT_ALIAS_UNKNOWN" in str(exc)
    else:
        raise AssertionError("unknown logical-agent alias must fail closed")

    ambiguous_alias_sessions = deepcopy(alias_sessions)
    ambiguous_alias_sessions["sessions"][2] = session("session-c", agent="agent-forge")
    try:
        bus.resolve_event_targets(
            alias_state, ambiguous_alias_sessions,
            continuity_id="GRT-CONT-DEMO-01",
            target_logical_agent_alias="FORGE",
        )
    except ValueError as exc:
        assert "not uniquely routable" in str(exc)
    else:
        raise AssertionError("multiple active sessions under alias must fail closed")

    try:
        bus.resolve_event_targets(
            alias_state, alias_sessions,
            continuity_id="GRT-CONT-DEMO-01",
            target_session_ids=["session-b"],
            target_logical_agent_alias="FORGE",
        )
    except ValueError as exc:
        assert "choose target_session_id or target_logical_agent_alias" in str(exc)
    else:
        raise AssertionError("mixed direct and alias targets must fail closed")

    control_state = base_state()
    control_sessions = {"sessions": [session("session-a"), session("session-b", bridge=True)]}
    control_sessions["sessions"][1]["relay"]["lease_expires_at"] = bus.iso(NOW + timedelta(hours=6))
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
    control_event = control_routed["event"]
    control_route = control_event["routes"][0]
    assert control_route["preferred_delivery_mode"] == "GSCC_CONTROL_CHANNEL"
    assert control_route["delivery_modes"] == ["GSCC_CONTROL_CHANNEL", "EXTERNAL_BRIDGE", "POLL_REPOSITORY"]
    control_item = next(x for x in control_dispatches["items"] if x.get("dispatch_kind") == "CONTINUITY_EVENT")
    assert control_item["preferred_delivery_mode"] == "GSCC_CONTROL_CHANNEL"
    assert control_item["status"] == "READY"
    assert control_route["control_evidence"]["transport_proven"] is True
    assert control_route["control_evidence"]["session_reachability"] == "VERIFIED"

    control_item["status"] = "DISPATCHED"
    control_item["delivered_at"] = bus.iso(NOW + timedelta(seconds=1))
    control_item["delivery_evidence_ref"] = "github-issue-comment:delivered"
    bus.reconcile_dispatch_delivery_docs(
        control_state, control_dispatches, timestamp=NOW + timedelta(seconds=1)
    )
    assert control_route["delivery_state"] == "DELIVERED"
    assert control_event["state"] == "DELIVERED", "B12 delivery advances parent event"

    control_item["status"] = "ACKNOWLEDGED"
    control_item["ack"] = {
        "delivery_state":"ACKNOWLEDGED",
        "observed_at":bus.iso(NOW + timedelta(seconds=2)),
        "evidence_ref":"github-issue-comment:ack",
    }
    bus.reconcile_dispatch_delivery_docs(
        control_state, control_dispatches, timestamp=NOW + timedelta(seconds=2)
    )
    assert control_route["delivery_state"] == "ACKED"
    assert control_event["state"] == "ACKED", "B12 ACK advances parent event"

    # ACK is terminal for expiry/reconciliation but remains respondable by the
    # explicit response path because ACKED is not a FINAL_ROUTE_STATE.
    bus.tick_docs(
        control_state, control_sessions, control_dispatches,
        timestamp=NOW + timedelta(hours=5),
        config=endpoint_config,
    )
    assert control_event["state"] == "ACKED", "acknowledged event must not expire as stale"
    responded_after_ack = bus.respond_event_docs(
        control_state, control_sessions,
        continuity_id="GRT-CONT-DEMO-01",
        event_id=control_event["event_id"],
        session_id="session-b",
        response_ref="github-issue-comment:response-after-ack",
        observed_head=HEAD,
        current_head=HEAD,
        evidence_ref="github-issue-comment:response-after-ack",
        timestamp=NOW + timedelta(hours=5, seconds=1),
    )
    assert responded_after_ack["status"] == "CONTINUITY_EVENT_RESPONDED"
    assert control_event["state"] == "RESPONDED"

    context_history_session = session("session-context-history", provider="chatgpt")
    current_context_id = bus.provider_context_descriptor(context_history_session)["provider_context_id"]
    expected_context_id = "GACR-PC-" + __import__("hashlib").sha256(
        __import__("json").dumps(
            {
                "session_id": "session-context-history",
                "connection_ref": context_history_session["connection_ref"],
                "provider_conversation_ref": context_history_session.get("provider_conversation_ref"),
                "client_instance_id": context_history_session["client_instance_id"],
            },
            sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()[:16]
    assert current_context_id == expected_context_id, "continuity projection must share auto-attach provider-context identity recipe"
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

    delayed_refresh_state = base_state()
    delayed_refresh_sessions = {"sessions": [
        session("session-a", silence_seconds=200),
        session("session-b", bridge=True),
        session("session-c", live=False),
    ]}
    delayed_refresh_dispatches = {"schema_version": "1.0.0", "revision": 0, "items": []}
    bus.tick_docs(
        delayed_refresh_state,
        delayed_refresh_sessions,
        delayed_refresh_dispatches,
        timestamp=NOW,
        early_supervision_after_seconds=120,
    )
    first_delayed_alert = delayed_refresh_state["items"][0]["supervision_alerts"][0]
    new_signal = NOW + timedelta(seconds=10)
    delayed_refresh_sessions["sessions"][0]["relay"]["last_heartbeat_at"] = bus.iso(new_signal)
    delayed_refresh_sessions["sessions"][0]["last_seen_at"] = bus.iso(new_signal)
    delayed_refresh_sessions["sessions"][0]["relay"]["lease_expires_at"] = bus.iso(NOW + timedelta(minutes=30))
    delayed_tick = bus.tick_docs(
        delayed_refresh_state,
        delayed_refresh_sessions,
        delayed_refresh_dispatches,
        timestamp=NOW + timedelta(seconds=150),
        early_supervision_after_seconds=120,
    )
    assert first_delayed_alert["state"] == "RESOLVED", "newer signal must resolve obsolete alert even when new silence already exceeds threshold"
    delayed_open = [
        item for item in delayed_refresh_state["items"][0]["supervision_alerts"]
        if item.get("state") == "OPEN"
        and item.get("target_session_id") == "session-a"
    ]
    assert len(delayed_open) == 1, "new silence interval receives a fresh supervision alert for the refreshed session"
    assert delayed_open[0]["last_signal_at"] == bus.iso(new_signal), "replacement alert is keyed to the newer signal"
    assert any(
        item.get("state") == "OPEN" and item.get("target_session_id") == "session-b"
        for item in delayed_refresh_state["items"][0]["supervision_alerts"]
    ), "an independently silent session may receive its own supervision alert in the same tick"
    assert any(x.get("state") == "RESOLVED" for x in delayed_tick["changes"])
    assert any(x.get("state") == "EARLY_SUPERVISION_ALERT" for x in delayed_tick["changes"])

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
