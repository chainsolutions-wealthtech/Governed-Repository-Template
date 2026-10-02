#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone

from gscc_gacr.admission_gse_projection import project_admission_gse_state

NOW = datetime(2026, 10, 2, 13, 30, 30, tzinfo=timezone.utc)
SESSION_ID = "session-gse-live"
HEAD = "a" * 40


def session():
    return {
        "session_id": SESSION_ID,
        "repository": "chainsolutions-wealthtech/Governed-Repository-Template",
        "status": "ACTIVE",
        "created_at": "2026-10-02T13:20:00+00:00",
        "last_seen_at": "2026-10-02T13:30:20+00:00",
        "last_observed_head_sha": HEAD,
        "connection_ref": "gscc-observable:gse-test",
        "relay": {
            "state": "ACTIVE",
            "last_heartbeat_at": "2026-10-02T13:29:50+00:00",
            "lease_expires_at": "2026-10-02T14:00:00+00:00",
            "branch": "governance/gscc-admission-harvester",
            "task_id": None,
        },
    }


def control_proof():
    return {
        "capabilities": {
            "status": "VERIFIED",
            "verified": ["COMMAND_RECEIVE", "COMMAND_ACK", "CHALLENGE_RESPONSE"],
            "evidence_ref": "github-issue-comment:700002",
            "observed_at": "2026-10-02T13:30:20+00:00",
        },
        "control_channel": {
            "status": "VERIFIED",
            "state": "REACHABLE",
            "evidence_ref": "github-issue-comment:700002",
            "observed_at": "2026-10-02T13:30:20+00:00",
        },
    }


def test_live_control_proof_projects_verified_gse_admission_state():
    state = project_admission_gse_state(session(), control_proof(), now=NOW)
    assert state["schema"] == "gscc-gse-admission-state/v1", state
    assert state["session_id"] == SESSION_ID, state
    assert state["presence"] == "PRESENT", state
    assert state["liveness"] == "VERIFIED", state
    assert state["control_reachability"] == "REACHABLE", state
    assert state["observed_head"] == HEAD, state
    assert state["evidence_ref"] == "github-issue-comment:700002", state
    assert state["source"] == "GSE_SESSION_STATE_ENGINE", state
    assert state["mutation_authority_granted"] is False, state


def test_stale_control_proof_does_not_project_verified_liveness():
    stale_now = datetime(2026, 10, 2, 13, 40, 0, tzinfo=timezone.utc)
    state = project_admission_gse_state(session(), control_proof(), now=stale_now)
    assert state["liveness"] != "VERIFIED", state
    assert state["control_reachability"] == "REACHABLE", state
    assert state["status"] == "GSE_ADMISSION_STATE_INCOMPLETE", state


def test_unverified_control_proof_fails_closed():
    proof = control_proof()
    proof["control_channel"]["status"] = "UNAVAILABLE"
    state = project_admission_gse_state(session(), proof, now=NOW)
    assert state["status"] == "GSE_ADMISSION_STATE_INCOMPLETE", state
    assert state["control_reachability"] == "UNAVAILABLE", state
    assert state["mutation_authority_granted"] is False, state


def main():
    test_live_control_proof_projects_verified_gse_admission_state()
    test_stale_control_proof_does_not_project_verified_liveness()
    test_unverified_control_proof_fails_closed()
    print("GSCC_ADMISSION_GSE_PROJECTION_TESTS_OK")


if __name__ == "__main__":
    main()
