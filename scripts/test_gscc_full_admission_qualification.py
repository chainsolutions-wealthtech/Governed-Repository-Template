#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone

from gscc.admission import (
    InMemoryAdmissionStore,
    evaluate_access_grant,
    evaluate_admission,
    validate_access_grant,
)
from gscc.admission_harvester import harvest_qualification_evidence
from gscc_gacr.issue_control_bridge import (
    apply_host_control_event,
    build_liveness_challenge_dispatch,
)

NOW = datetime(2026, 10, 2, 13, 50, 30, tzinfo=timezone.utc)
HEAD = "a" * 40
REPOSITORY = "chainsolutions-wealthtech/Governed-Repository-Template"


def envelope(requested_capabilities):
    return {
        "schema": "gscc-admission-envelope/v1",
        "request": {
            "request_id": "admreq-full-001",
            "correlation_id": "corr-full-001",
            "idempotency_key": "idem-full-001",
            "issued_at": "2026-10-02T13:49:58+00:00",
            "observed_at": "2026-10-02T13:49:59+00:00",
        },
        "agent": {
            "agent_type": "conversation-agent",
            "provider": "chatgpt",
            "requested_role": "implementer",
        },
        "client": {
            "client_instance_id": "client-full-001",
            "client_type": "chat-client",
        },
        "session": {"conversation_ref": "UNAVAILABLE"},
        "connection": {
            "connection_ref": "connection-full-001",
            "connection_method": "gscc-controlled-host-gateway",
            "surface_class": "CONTROLLED_INSTRUMENTABLE",
            "wake_channels": ["POLL_REPOSITORY"],
        },
        "target": {
            "repository": REPOSITORY,
            "requested_branch": "main",
        },
        "intent": {
            "entry_action": "REPOSITORY_ACCESS",
            "connection_intent": "READ_ONLY_DISCOVERY",
            "requested_capabilities": list(requested_capabilities),
        },
        "continuity": {},
        "control_capabilities": {
            "heartbeat": True,
            "command_receive": True,
            "command_ack": True,
            "challenge_response": True,
        },
    }


def sessions():
    return {
        "schema_version": "1.0.0",
        "revision": 1,
        "sessions": [{
            "session_id": "session-full-live",
            "repository": REPOSITORY,
            "status": "ACTIVE",
            "connection_ref": "connection-full-001",
            "client_instance_id": "client-full-001",
            "provider": "chatgpt",
            "created_at": "2026-10-02T13:40:00+00:00",
            "last_seen_at": "2026-10-02T13:50:20+00:00",
            "last_observed_head_sha": HEAD,
            "capabilities": ["GACR_AUTO_ATTACH", "GACR_PRESENCE_FIRST"],
            "surface_class": "CONTROLLED_INSTRUMENTABLE",
            "connection_method": "gscc-controlled-host-gateway",
            "relay": {
                "state": "ACTIVE",
                "last_heartbeat_at": "2026-10-02T13:49:50+00:00",
                "lease_expires_at": "2026-10-02T14:20:00+00:00",
                "branch": "main",
                "task_id": None,
            },
        }],
    }


def fake_github(url: str):
    if url.endswith("/repos/" + REPOSITORY):
        return {
            "id": 1386478935,
            "full_name": REPOSITORY,
            "owner": {"login": "chainsolutions-wealthtech"},
            "visibility": "public",
            "default_branch": "main",
            "permissions": {"pull": True, "push": True, "admin": True},
        }
    if url.endswith("/repos/" + REPOSITORY + "/branches/main"):
        return {"name": "main", "commit": {"sha": HEAD}}
    raise AssertionError(url)


def dispatches():
    raw_session = sessions()["sessions"][0]
    item = build_liveness_challenge_dispatch(
        raw_session,
        now=datetime(2026, 10, 2, 13, 50, 0, tzinfo=timezone.utc),
        ttl_seconds=60,
        issue_number=115,
        nonce="nonce-full-001",
    )
    store = {"schema_version": "1.0.0", "revision": 0, "items": [item]}
    command = item["command"]
    apply_host_control_event(
        store,
        {
            "event": "command_ack",
            "session_id": raw_session["session_id"],
            "dispatch_id": item["dispatch_id"],
            "command_id": command["command_id"],
            "correlation_id": command["correlation_id"],
            "delivery_state": "ACKNOWLEDGED",
        },
        evidence_ref="github-issue-comment:800001",
        observed_at="2026-10-02T13:50:10+00:00",
    )
    apply_host_control_event(
        store,
        {
            "event": "challenge_response",
            "session_id": raw_session["session_id"],
            "dispatch_id": item["dispatch_id"],
            "command_id": command["command_id"],
            "correlation_id": command["correlation_id"],
            "challenge_id": command["payload"]["challenge_id"],
            "nonce": command["payload"]["nonce"],
            "challenge_status": "ACK",
        },
        evidence_ref="github-issue-comment:800002",
        observed_at="2026-10-02T13:50:20+00:00",
    )
    return store


def governance():
    return {
        "00_START_HERE.md": "start",
        "GOVERNANCE.md": "governance",
        "docs/control-plane/GSCC_ADMISSION_ACCESS_GATE.md": "admission",
        "docs/control-plane/GACR_PROGRAM.md": "gacr",
    }


def access_policy():
    return {
        "schema": "gscc-admission-access-policy/v1",
        "authority_id": "GSCC-ADMISSION-ACCESS-POLICY-001",
        "default_decision": "DENY",
        "read_only_requested_capabilities": [
            "READ_REPOSITORY",
            "READ_GOVERNANCE",
            "READ_STATUS",
            "READ_CONTEXT",
            "READ_CAPABILITIES",
        ],
        "read_only_authority_class": "READ_ONLY_DISCOVERY_AUTHORITY",
        "constraints": {
            "direct_main_write": False,
            "mutation": False,
            "merge": False,
            "deployment": False,
            "exact_head_required": True,
            "active_session_required": True,
            "control_channel_required": True,
            "gse_verified_required": True,
        },
        "operational_or_mutation_authority_policy": "EXPLICIT_SEPARATE_GOVERNANCE_EVIDENCE_REQUIRED",
        "invocation_authority_granted": False,
        "mutation_authority_granted": False,
    }


def harvest(admission):
    return harvest_qualification_evidence(
        admission,
        github_request_fn=fake_github,
        sessions=sessions(),
        claims={"claims": []},
        tasks={"items": []},
        dispatches=dispatches(),
        governance_documents=governance(),
        access_policy_document=access_policy(),
        now=NOW,
    )


def test_full_read_only_path_issues_bounded_access_grant():
    admission = evaluate_admission(
        envelope(["READ_REPOSITORY"]),
        store=InMemoryAdmissionStore(),
        now=NOW,
    )
    assert admission["status"] == "PREAUTHORIZED", admission

    evidence = harvest(admission)
    assert evidence["status"] == "QUALIFICATION_EVIDENCE_COMPLETE", evidence
    assert evidence["missing_canonical_evidence"] == [], evidence
    assert evidence["capabilities"]["status"] == "VERIFIED", evidence
    assert evidence["control_channel"]["status"] == "VERIFIED", evidence
    assert evidence["gse_initial_state"]["status"] == "VERIFIED", evidence
    assert evidence["access_policy"]["status"] == "ALLOW", evidence

    grant = evaluate_access_grant(admission, evidence, now=NOW)
    assert grant["status"] == "AUTHORIZED", grant
    assert grant["access_class"] == "GOVERNED_FUNCTION_EXPOSURE_ELIGIBLE", grant
    assert grant["allowed_authority_classes"] == ["READ_ONLY_DISCOVERY_AUTHORITY"], grant
    assert grant["invocation_authority_granted"] is False, grant
    assert grant["mutation_authority_granted"] is False, grant

    validated = validate_access_grant(
        grant,
        connection_ref=grant["connection_ref"],
        repository=REPOSITORY,
        requested_head=HEAD,
        session_id="session-full-live",
        now=NOW,
    )
    assert validated["status"] == "VALIDATED", validated


def test_mutation_request_never_reaches_access_grant_under_baseline_policy():
    admission = evaluate_admission(
        envelope(["WRITE_REPOSITORY"]),
        store=InMemoryAdmissionStore(),
        now=NOW,
    )
    assert admission["status"] == "PREAUTHORIZED", admission
    evidence = harvest(admission)
    assert evidence["access_policy"]["status"] == "PENDING" or evidence["access_policy"]["status"] == "DENY", evidence
    assert "access_policy" in evidence["missing_canonical_evidence"], evidence

    decision = evaluate_access_grant(admission, evidence, now=NOW)
    assert decision["status"] != "AUTHORIZED", decision
    assert decision["access_class"] == "NOT_AUTHORIZED", decision
    assert decision["mutation_authority_granted"] is False, decision


def main():
    test_full_read_only_path_issues_bounded_access_grant()
    test_mutation_request_never_reaches_access_grant_under_baseline_policy()
    print("GSCC_FULL_ADMISSION_QUALIFICATION_TESTS_OK")


if __name__ == "__main__":
    main()
