#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone

from gscc_gacr.admission_gse_projection import project_admission_gse_state, project_pre_gacr_admission_gse_state

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
    assert state["control_reachability"] == "UNKNOWN", state
    assert state["mutation_authority_granted"] is False, state



def test_post_challenge_heartbeat_newer_than_response_preserves_control_proof():
    live = session()
    live["last_seen_at"] = "2026-10-02T13:30:29+00:00"
    live["relay"]["last_heartbeat_at"] = "2026-10-02T13:30:29+00:00"
    proof = control_proof()
    proof["control_channel"]["observed_at"] = "2026-10-02T13:30:20+00:00"
    proof["capabilities"]["observed_at"] = "2026-10-02T13:30:20+00:00"

    state = project_admission_gse_state(
        live,
        proof,
        now=datetime(2026, 10, 2, 13, 30, 40, tzinfo=timezone.utc),
    )
    assert state["status"] == "VERIFIED", state
    assert state["presence"] == "PRESENT", state
    assert state["liveness"] == "VERIFIED", state
    assert state["control_reachability"] == "REACHABLE", state


def main():
    test_live_control_proof_projects_verified_gse_admission_state()
    test_stale_control_proof_does_not_project_verified_liveness()
    test_unverified_control_proof_fails_closed()
    test_post_challenge_heartbeat_newer_than_response_preserves_control_proof()
    test_pre_gacr_projection_requires_no_durable_session()
    print("GSCC_ADMISSION_GSE_PROJECTION_TESTS_OK")


if __name__ == "__main__":
    main()


def test_pre_gacr_projection_requires_no_durable_session():
    admission = {
        "admission_id": "GSCC-ADM-PRE-GACR-1",
        "connection_ref": "conn-pre-gacr-1",
        "repository": "chainsolutions-wealthtech/Governed-Repository-Template",
        "evaluated_at": "2026-10-06T06:10:00+00:00",
    }
    baseline = {
        "status": "OBSERVED",
        "repository": admission["repository"],
        "requested_branch": "main",
        "default_branch": "main",
        "observed_head": "a"*40,
        "observed_at": "2026-10-06T06:10:00+00:00",
    }
    control = {
        "capabilities": {"status": "VERIFIED", "evidence_ref": "cap:1"},
        "control_channel": {
            "status": "VERIFIED",
            "state": "REACHABLE",
            "evidence_ref": "ctrl:1",
            "observed_at": "2026-10-06T06:10:01+00:00",
            "challenge_id": "challenge-1",
        },
    }
    state = project_pre_gacr_admission_gse_state(admission, baseline, control)
    assert state["status"] == "VERIFIED", state
    assert state["session_id"] == admission["connection_ref"], state
    assert state["durable_gacr_session_required"] is False, state
    assert state["presence"] == "PRESENT", state
    assert state["liveness"] == "VERIFIED", state
    assert state["control_reachability"] == "REACHABLE", state
