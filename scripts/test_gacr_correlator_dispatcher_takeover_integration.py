#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
import tempfile
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import gacr_agent_telemetry as telemetry
import governed_agent_continuity_relay as relay


def assert_true(value, message):
    if not value:
        raise SystemExit("GACR_CORRELATOR_DISPATCHER_INTEGRATION_TEST_FAILED: " + message)


def session(
    session_id,
    *,
    status="ACTIVE",
    relay_state=None,
    repository="owner/repo",
    provider="chatgpt",
    provider_ref=None,
    client_instance_id=None,
    connection_ref=None,
    connection_fingerprint=None,
    actor=None,
    installation_id=None,
    task_id=None,
    branch="feature/gacr",
    pull_request=21,
    capabilities=None,
    authority_grants=None,
    agent_role=None,
    wake_channels=None,
    created_at="2026-10-02T02:00:00+00:00",
):
    return {
        "session_id": session_id,
        "agent_identity": session_id,
        "provider": provider,
        "provider_conversation_ref": provider_ref,
        "client_instance_id": client_instance_id,
        "connection_ref": connection_ref,
        "connection_fingerprint": connection_fingerprint,
        "repository": repository,
        "status": status,
        "created_at": created_at,
        "last_seen_at": "2026-10-02T02:10:00+00:00",
        "last_observed_head_sha": "a" * 40,
        "github_actor": actor,
        "github_installation_id": installation_id,
        "capabilities": capabilities or [],
        "authority_grants": authority_grants,
        "agent_role": agent_role,
        "wake_channels": wake_channels or ["POLL_REPOSITORY"],
        "relay": {
            "process": "GACR",
            "state": relay_state or status,
            "task_id": task_id,
            "branch": branch,
            "pull_request": pull_request,
            "last_heartbeat_at": "2026-10-02T02:10:00+00:00",
            "lease_expires_at": "2026-10-02T02:40:00+00:00",
        },
    }


def beacon(**overrides):
    value = {
        "beacon_id": "GACR-B-test00000001",
        "repository": "owner/repo",
        "session_id": None,
        "provider": None,
        "provider_conversation_ref": None,
        "client_instance_id": None,
        "connection_ref": None,
        "connection_fingerprint": None,
        "task_id": None,
        "branch": None,
        "pull_request": None,
        "observed_head_sha": None,
        "written_head_sha": None,
        "observed_at": "2026-10-02T02:12:00+00:00",
        "github": {
            "environment": {},
            "event": {},
        },
    }
    value.update(overrides)
    return value



def correlation_contract_tests():
    a = session(
        "session-a",
        provider_ref="conv-a",
        client_instance_id="client-a",
        connection_ref="conn-a",
        connection_fingerprint="GACR-FP1-a",
        actor="actor-shared",
        installation_id=1001,
        task_id="TASK-A",
        branch="feature/a",
        pull_request=31,
    )
    b = session(
        "session-b",
        provider_ref="conv-b",
        client_instance_id="client-b",
        connection_ref="conn-b",
        connection_fingerprint="GACR-FP1-b",
        actor="actor-shared",
        installation_id=1001,
        task_id="TASK-B",
        branch="feature/b",
        pull_request=32,
        created_at="2026-10-02T02:01:00+00:00",
    )
    sessions = {"sessions": [a, b]}
    claims = {"claims": []}

    exact = telemetry.correlate_beacon(
        beacon(session_id="session-a", provider="chatgpt", provider_conversation_ref="conv-a"),
        sessions,
        claims,
    )
    assert_true(exact["level"] == "EXACT", "explicit matching session/provider anchors must be EXACT")
    assert_true(exact["selected_session_id"] == "session-a", "EXACT must select the unique session")
    assert_true(exact["confidence"]["rule_id"] == "EXACT_DIRECT_ANCHOR", "EXACT rule must be auditable")

    strong = telemetry.correlate_beacon(
        beacon(
            provider="chatgpt",
            connection_fingerprint="GACR-FP1-a",
            task_id="TASK-A",
            branch="feature/a",
        ),
        sessions,
        claims,
    )
    assert_true(strong["level"] == "STRONG", "fingerprint plus compatible context should be STRONG")
    assert_true(strong["selected_session_id"] == "session-a", "unique STRONG may select")
    assert_true(strong["confidence"]["numeric_score"] is None, "correlation confidence must not invent numeric truth")
    assert_true(strong["provider_identity_inferred"] is False, "fingerprint must never become provider identity")

    probable = telemetry.correlate_beacon(
        beacon(task_id="TASK-A", branch="feature/a"),
        sessions,
        claims,
    )
    assert_true(probable["level"] == "PROBABLE", "task+branch without a strong anchor should remain PROBABLE")
    assert_true(probable["selected_session_id"] is None, "PROBABLE must not select")
    assert_true(probable["binding_status"] == "UNBOUND_ACTIVITY", "PROBABLE activity remains unbound")

    same_actor = telemetry.correlate_beacon(
        beacon(github={"environment": {"GITHUB_ACTOR": "actor-shared"}, "event": {}}),
        sessions,
        claims,
    )
    assert_true(same_actor["level"] == "AMBIGUOUS", "same actor across multiple live sessions must be AMBIGUOUS")
    assert_true(same_actor["selected_session_id"] is None, "multi-session same actor must fail closed")

    different_branch = telemetry.correlate_beacon(
        beacon(branch="feature/b", task_id="TASK-B"),
        sessions,
        claims,
    )
    assert_true(different_branch["level"] == "PROBABLE", "same repo/different branch context must not become EXACT")
    assert_true(different_branch["selected_session_id"] is None, "branch context alone never silently binds")

    client_exact = telemetry.correlate_beacon(
        beacon(branch="feature/a", client_instance_id="client-b"),
        sessions,
        claims,
    )
    assert_true(client_exact["level"] == "EXACT", "explicit client_instance_id is a direct operational anchor")
    assert_true(client_exact["selected_session_id"] == "session-b", "client anchor must beat unrelated branch context")

    missing_provider_ref = telemetry.correlate_beacon(
        beacon(provider="chatgpt", connection_fingerprint="GACR-FP1-b", branch="feature/b"),
        sessions,
        claims,
    )
    assert_true(missing_provider_ref["level"] == "STRONG", "fingerprint can strengthen without provider ref")
    assert_true(missing_provider_ref["selected_session_id"] == "session-b", "unique fingerprint match may STRONG-select")
    assert_true(missing_provider_ref.get("provider_conversation_ref") is None, "correlation output must not fabricate provider ref")

    conflict = telemetry.correlate_beacon(
        beacon(
            session_id="session-a",
            provider="claude",
            provider_conversation_ref="conv-b",
        ),
        sessions,
        claims,
    )
    assert_true(conflict["level"] == "AMBIGUOUS", "conflicting explicit provider/session anchors must fail closed")
    assert_true(conflict["selected_session_id"] is None, "conflicting provider evidence must not select")

    terminal = deepcopy(a)
    terminal["status"] = "CLOSED"
    terminal["relay"]["state"] = "CLOSED"
    unknown = telemetry.correlate_beacon(
        beacon(session_id="session-a"),
        {"sessions": [terminal]},
        claims,
    )
    assert_true(unknown["level"] == "UNKNOWN", "terminal session must be excluded")
    assert_true(unknown["candidate_session_ids"] == [], "terminal session must not remain a candidate")
    assert_true(unknown["binding_status"] == "UNBOUND_ACTIVITY", "unmatched activity is explicitly unbound")

    collision_a = session("session-c1", task_id="TASK-C", branch="feature/c", pull_request=77)
    collision_b = session("session-c2", task_id="TASK-C", branch="feature/c", pull_request=77, created_at="2026-10-02T02:02:00+00:00")
    ambiguous = telemetry.correlate_beacon(
        beacon(task_id="TASK-C", branch="feature/c", pull_request=77),
        {"sessions": [collision_a, collision_b]},
        claims,
    )
    assert_true(ambiguous["level"] == "AMBIGUOUS", "indistinguishable contextual candidates must be AMBIGUOUS")
    assert_true(ambiguous["selected_session_id"] is None, "AMBIGUOUS must not select")


def dispatcher_contract_tests():
    predecessor = session(
        "session-a",
        status="STALLED",
        relay_state="TAKEOVER_READY",
        task_id="TASK-GACR-1",
        branch="feature/gacr",
        pull_request=41,
    )
    eligible = session(
        "session-b",
        status="STANDBY",
        relay_state="STANDBY",
        task_id=None,
        branch="main",
        pull_request=None,
        capabilities=["WRITE_CODE", "GACR_TAKEOVER"],
        authority_grants=["MUTATE_REPOSITORY"],
        agent_role="IMPLEMENTER",
        wake_channels=["POLL_REPOSITORY", "REPOSITORY_DISPATCH"],
        created_at="2026-10-02T02:03:00+00:00",
    )
    missing_cap = session(
        "session-c",
        status="STANDBY",
        relay_state="STANDBY",
        task_id=None,
        branch="main",
        pull_request=None,
        capabilities=["GACR_TAKEOVER"],
        authority_grants=["MUTATE_REPOSITORY"],
        agent_role="IMPLEMENTER",
        created_at="2026-10-02T02:04:00+00:00",
    )
    unknown_authority = session(
        "session-d",
        status="STANDBY",
        relay_state="STANDBY",
        task_id=None,
        branch="main",
        pull_request=None,
        capabilities=["WRITE_CODE", "GACR_TAKEOVER"],
        authority_grants=None,
        agent_role="IMPLEMENTER",
        created_at="2026-10-02T02:05:00+00:00",
    )
    busy = session(
        "session-e",
        status="STANDBY",
        relay_state="STANDBY",
        task_id=None,
        branch="main",
        pull_request=None,
        capabilities=["WRITE_CODE", "GACR_TAKEOVER"],
        authority_grants=["MUTATE_REPOSITORY"],
        agent_role="IMPLEMENTER",
        created_at="2026-10-02T02:06:00+00:00",
    )
    wrong_task = session(
        "session-f",
        status="STANDBY",
        relay_state="STANDBY",
        task_id="TASK-OTHER",
        branch="feature/other",
        pull_request=None,
        capabilities=["WRITE_CODE", "GACR_TAKEOVER"],
        authority_grants=["MUTATE_REPOSITORY"],
        agent_role="IMPLEMENTER",
        created_at="2026-10-02T02:07:00+00:00",
    )
    sessions = {"sessions": [predecessor, eligible, missing_cap, unknown_authority, busy, wrong_task]}
    claims = {"claims": [
        {
            "session_id": "session-a",
            "work_item_id": "WORK-GACR-1",
            "collision_domains": ["gacr-correlator"],
            "status": "ACTIVE",
            "claimed_head_sha": "a" * 40,
        },
        {
            "session_id": "session-e",
            "work_item_id": "WORK-OTHER",
            "collision_domains": ["other-domain"],
            "status": "ACTIVE",
            "claimed_head_sha": "a" * 40,
        },
    ]}
    work = {"items": [
        {
            "work_item_id": "DEP-GACR-1",
            "status": "DONE",
            "dependencies": [],
            "collision_domains": [],
        },
        {
            "work_item_id": "WORK-GACR-1",
            "status": "IN_PROGRESS",
            "dependencies": ["DEP-GACR-1"],
            "collision_domains": ["gacr-correlator"],
            "required_capabilities": ["WRITE_CODE"],
            "required_authorities": ["MUTATE_REPOSITORY"],
            "allowed_agent_roles": ["IMPLEMENTER"],
        },
        {
            "work_item_id": "WORK-OTHER",
            "status": "IN_PROGRESS",
            "dependencies": [],
            "collision_domains": ["other-domain"],
        },
    ]}
    takeover = {
        "takeover_id": "GACR-T-feedfacecafe",
        "stalled_session_id": "session-a",
        "status": "READY_FOR_RECONCILIATION",
        "work_item_id": "WORK-GACR-1",
        "task_id": "TASK-GACR-1",
        "branch": "feature/gacr",
        "pull_request": 41,
        "last_observed_head_sha": "a" * 40,
    }

    decision = telemetry.select_compatible_standby(
        sessions,
        claims,
        work,
        takeover,
    )
    by_id = {x["session_id"]: x for x in decision["evaluations"]}
    assert_true(decision["selected_session_id"] == "session-b", "only eligible standby must be selected")
    assert_true(by_id["session-b"]["status"] == "ELIGIBLE", "eligible candidate classification")
    assert_true(by_id["session-c"]["status"] == "INELIGIBLE", "missing required capability is ineligible")
    assert_true(by_id["session-d"]["status"] == "AMBIGUOUS", "unproven required authority must fail closed as ambiguous")
    assert_true(by_id["session-e"]["status"] == "BLOCKED", "standby with an active claim is blocked")
    assert_true(by_id["session-f"]["status"] == "INELIGIBLE", "different bound task/work scope is ineligible")
    assert_true(decision["selection_method"] == "DETERMINISTIC_CATEGORICAL_ORDER", "ranking must be deterministic/auditable")
    assert_true(decision["grants_write_authority"] is False, "selection/offer must never grant write")

    blocked_work = deepcopy(work)
    next(x for x in blocked_work["items"] if x["work_item_id"] == "DEP-GACR-1")["status"] = "BLOCKED"
    blocked = telemetry.select_compatible_standby(sessions, claims, blocked_work, takeover)
    assert_true(blocked["selected_session_id"] is None, "unmet dependencies must block takeover selection")
    assert_true(all(x["status"] != "ELIGIBLE" for x in blocked["evaluations"]), "no candidate eligible while dependency is blocked")


def takeover_contract_tests():
    t0 = datetime(2026, 10, 2, 2, 0, tzinfo=timezone.utc)
    config = {
        "stalled_after_seconds": 1800,
        "suspected_stall_after_seconds": 900,
        "takeover": {"auto_offer_to_compatible_standby": True},
    }
    predecessor = session(
        "session-a",
        status="STALLED",
        relay_state="TAKEOVER_READY",
        task_id="TASK-GACR-1",
        branch="feature/gacr",
        pull_request=41,
    )
    predecessor["relay"]["last_action"] = "STALL_DETECTED"
    successor = session(
        "session-b",
        status="STANDBY",
        relay_state="STANDBY",
        task_id=None,
        branch="main",
        pull_request=None,
        capabilities=["WRITE_CODE", "GACR_TAKEOVER"],
        authority_grants=["MUTATE_REPOSITORY"],
        agent_role="IMPLEMENTER",
    )
    sessions = {"schema_version": "1.0.0", "revision": 0, "sessions": [predecessor, successor]}
    claims = {"schema_version": "1.0.0", "revision": 0, "claims": [{
        "session_id": "session-a",
        "work_item_id": "WORK-GACR-1",
        "collision_domains": ["gacr-correlator"],
        "status": "ACTIVE",
        "claimed_head_sha": "a" * 40,
    }]}
    work = {"items": [{
        "work_item_id": "WORK-GACR-1",
        "status": "IN_PROGRESS",
        "dependencies": [],
        "collision_domains": ["gacr-correlator"],
        "required_capabilities": ["WRITE_CODE"],
        "required_authorities": ["MUTATE_REPOSITORY"],
        "allowed_agent_roles": ["IMPLEMENTER"],
    }]}
    takeovers = {"schema_version": "1.0.0", "revision": 0, "items": [{
        "takeover_id": "GACR-T-feedfacecafe",
        "stalled_session_id": "session-a",
        "offered_to_session_id": "session-b",
        "accepted_by_session_id": None,
        "status": "OFFERED",
        "created_at": relay.iso(t0),
        "work_item_id": "WORK-GACR-1",
        "task_id": "TASK-GACR-1",
        "branch": "feature/gacr",
        "pull_request": 41,
        "last_observed_head_sha": "a" * 40,
    }]}
    forensics = {"items": [{
        "session_id": "session-a",
        "generated_at": "2026-10-02T02:30:00+00:00",
        "liveness": {"last_heartbeat_at": "2026-10-02T02:00:00+00:00"},
        "actions": {
            "last_action_completed": {"action_id": "action-1", "action_label": "edit correlator"},
            "in_flight_action": {"action_id": "action-2", "action_label": "open PR"},
        },
        "last_checkpoint_ref": "CHK-GACR-1",
        "last_evidence_ref": "ci:fixture",
        "resume_point": {
            "last_observed_head_sha": "a" * 40,
            "last_written_head_sha": "b" * 40,
            "checkpoint_ref": "CHK-GACR-1",
            "evidence_ref": "ci:fixture",
            "collision_domains": ["gacr-correlator"],
            "requires_exact_head_reobservation": True,
            "may_replay_in_flight_action_without_reconciliation": False,
        },
    }]}

    package = telemetry.build_takeover_package(
        "session-a",
        "session-b",
        sessions_doc=sessions,
        claims_doc=claims,
        work_doc=work,
        takeovers_doc=takeovers,
        forensics_doc=forensics,
    )
    assert_true(package["predecessor_session_id"] == "session-a", "B discovers predecessor A")
    assert_true(package["successor_candidate_session_id"] == "session-b", "package targets successor B")
    assert_true(package["task_id"] == "TASK-GACR-1", "same task preserved")
    assert_true(package["branch"] == "feature/gacr", "same branch preserved")
    assert_true(package["last_completed_action"]["action_id"] == "action-1", "stopping point includes last completed action")
    assert_true(package["action_in_flight"]["action_id"] == "action-2", "stopping point includes in-flight action")
    assert_true(package["checkpoint_ref"] == "CHK-GACR-1", "checkpoint included")
    assert_true(package["exact_head_required"] is True, "package requires exact HEAD")
    assert_true(package["replay_policy"] == "RECONCILE_BEFORE_REPLAY", "unresolved in-flight action is never blindly replayed")
    assert_true(package["provider_conversation_ref"] is None, "provider conversation ref omitted/unavailable when not supplied")
    assert_true(
        "LIVENESS_PROGRESS_CONTEXT_SHARED_INTEGRATION_REQUIRED" in package["known_unknowns"],
        "package must expose missing Worker B context instead of recreating liveness/progress",
    )

    try:
        relay.accept_takeover_docs(
            config,
            sessions,
            claims,
            takeovers,
            stalled_session_id="session-a",
            successor_session_id="session-b",
            reconciled_head_sha="b" * 40,
            actual_work_head_sha="c" * 40,
            timestamp=t0 + timedelta(seconds=1),
        )
        raise SystemExit("GACR_CORRELATOR_DISPATCHER_INTEGRATION_TEST_FAILED: mismatch must reject")
    except ValueError:
        pass
    assert_true(claims["claims"][0]["session_id"] == "session-a", "claim remains with A after rejected HEAD mismatch")

    accepted = relay.accept_takeover_docs(
        config,
        sessions,
        claims,
        takeovers,
        stalled_session_id="session-a",
        successor_session_id="session-b",
        reconciled_head_sha="c" * 40,
        actual_work_head_sha="c" * 40,
        timestamp=t0 + timedelta(seconds=2),
    )
    assert_true(accepted["status"] == "TAKEOVER_ACCEPTED", "exact HEAD permits acceptance")
    assert_true(claims["claims"][0]["session_id"] == "session-b", "claim transfers only after acceptance")
    assert_true(predecessor["status"] == "CLOSED", "A becomes terminal")
    assert_true(successor["relay"]["state"] == "ACTIVE", "B becomes active")
    assert_true(successor["relay"]["task_id"] == "TASK-GACR-1", "B continues same task")

    try:
        relay.heartbeat_docs(
            config,
            sessions,
            session_id="session-a",
            observed_head="c" * 40,
            action="LATE_HEARTBEAT",
            evidence=None,
            timestamp=t0 + timedelta(seconds=3),
        )
        raise SystemExit("GACR_CORRELATOR_DISPATCHER_INTEGRATION_TEST_FAILED: late A heartbeat resurrected ownership")
    except ValueError:
        pass


def harness_contract_tests():
    harness = importlib.import_module("gacr_e2e_takeover_harness")
    spec = harness.harness_spec()
    assert_true(spec["live_proof_status"] == "NOT_EXECUTED", "prepared harness must not claim ultimate live proof")
    assert_true(spec["shared_integration_required"] is True, "Workers A/B adapters remain an explicit shared integration")
    assert_true(spec["worker_api_contract"] == "GACR_WORKER_ADAPTER_V1", "future Worker A/B API contract is explicit")
    assert_true(spec["shared_worker_contracts"]["worker_a"]["source_pr"] == 128, "Worker A adapter must target PR #128")
    assert_true("observe_presence" in spec["shared_worker_contracts"]["worker_a"]["apis"], "Worker A Presence API must be reused")
    assert_true(spec["shared_worker_contracts"]["worker_b"]["source_pr"] == 127, "Worker B adapter must target PR #127")
    assert_true("worker_c_integration_projection" in spec["shared_worker_contracts"]["worker_b"]["apis"], "Worker B C-projection API must be reused")
    required = [
        "AGENT_A_FIRST_TOUCH",
        "AGENT_A_WORK",
        "LIVENESS_PROGRESS",
        "CONTROLLED_STOP",
        "SUSPECTED_STALL",
        "STALLED",
        "TAKEOVER_READY",
        "AGENT_B_CONTEXT",
        "PREDECESSOR_RECONSTRUCTION",
        "EXACT_HEAD",
        "TAKEOVER_ACCEPT",
        "CONTINUATION",
    ]
    assert_true(spec["scenario_steps"] == required, "final E2E sequence must stay frozen")


def main():
    correlation_contract_tests()
    dispatcher_contract_tests()
    takeover_contract_tests()
    harness_contract_tests()
    print("GACR_CORRELATOR_DISPATCHER_TAKEOVER_INTEGRATION_TEST_PASS")


if __name__ == "__main__":
    main()
