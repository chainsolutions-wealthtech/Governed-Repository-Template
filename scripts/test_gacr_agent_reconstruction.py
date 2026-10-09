#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "gacr_agent_reconstruction.py"
MANIFEST = REPO_ROOT / ".governance" / "agent-reconstruction-skeleton.json"


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def run(root: Path, *args: str):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def assert_true(value, message: str) -> None:
    if not value:
        raise AssertionError(message)


def validate_repository_contract() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert_true(manifest["schema"] == "agent-reconstruction-skeleton/v1", "manifest schema")
    assert_true(manifest["projection_only"] is True, "manifest projection only")
    assert_true(manifest["grants_mutation_authority"] is False, "manifest grants no mutation authority")
    stages = manifest["stages"]
    assert_true(stages[0]["authority"] == "00_GSCC_ENTRY.md", "path begins at GSCC entry")
    assert_true(stages[-1]["authority"] == "00_START_HERE.md", "path returns to START_HERE")
    required = {
        "scripts/gscc_persisted_entry_pipeline.py",
        "scripts/gse/session_state_engine.py",
        "scripts/gacr_auto_attach.py",
        "scripts/gacr_agent_reconstruction.py",
        "scripts/gacr_continuity_bus.py",
        "scripts/gacr_capacity_dispatch.py",
        "scripts/governed_agent_continuity_relay.py",
    }
    for path in required:
        assert_true((REPO_ROOT / path).exists(), f"missing skeleton authority {path}")
    entry = (REPO_ROOT / "00_GSCC_ENTRY.md").read_text(encoding="utf-8")
    start = (REPO_ROOT / "00_START_HERE.md").read_text(encoding="utf-8")
    docs = (REPO_ROOT / "docs" / "control-plane" / "AGENT_RECONSTRUCTION_SKELETON.md").read_text(encoding="utf-8")
    assert_true("gacr_agent_reconstruction.py" in entry, "GSCC entry exposes reconstruction aid")
    assert_true("gacr_agent_reconstruction.py" in start, "START_HERE exposes reconstruction view")
    assert_true("RECONSTRUCTION != ADMISSION" in docs, "authority separation documented")


def fixture(root: Path) -> None:
    (root / ".template-source").write_text("source\n", encoding="utf-8")
    (root / ".governance").mkdir(parents=True, exist_ok=True)
    (root / ".governance" / "agent-reconstruction-skeleton.json").write_text(
        MANIFEST.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    state = root / ".governance" / "control-plane-state"
    logical = "GSCC-ID-forge-test"
    write(state / "gacr-continuities.json", {
        "revision": 7,
        "items": [{
            "continuity_id": "GRT-CONT-TEST-01",
            "repository": "example/repo",
            "coordination_issue": 259,
            "logical_agents": [{
                "logical_agent_id": logical,
                "human_alias": "FORGE",
                "human_alias_provenance": "OWNER_ASSIGNED",
                "session_ids": ["session-a", "session-b"],
                "scope_ids": ["lab"],
            }],
            "participants": [{
                "participant_id": "participant-a",
                "session_id": "session-a",
                "scope_id": "lab",
                "declared_role": "CODE_AGENT",
                "work_mode": "WRITE_LAB_ONLY",
                "membership_state": "PERSISTENT",
                "collision_domains": ["domain-a"],
                "evidence_ref": "github-issue-comment:1",
            }],
            "events": [{
                "event_id": "event-a",
                "sequence": 1,
                "event_kind": "REVIEW_REQUEST",
                "from_session_id": "session-a",
                "payload_ref": "github-issue-comment:2",
                "state": "ACKED",
                "routes": [{"target_session_id":"session-b"}],
            }],
        }],
    })
    write(state / "gacr-sessions.json", {
        "revision": 11,
        "sessions": [
            {
                "session_id":"session-a",
                "agent_identity":logical,
                "status":"ACTIVE",
                "provider":"chatgpt",
                "provider_conversation_ref":None,
                "provider_conversation_ref_provenance":"UNAVAILABLE",
                "connection_ref":"surface-a",
                "client_instance_id":"client-a",
                "agent_role":"CODE_AGENT",
                "capabilities":["CODE","COMMAND_RECEIVE"],
                "wake_channels":["POLL_REPOSITORY"],
                "last_observed_head_sha":"a"*40,
                "provider_contexts":[
                    {
                        "provider_context_id":"GACR-PC-aaaaaaaaaaaaaaaa",
                        "provider":"chatgpt",
                        "connection_ref":"surface-a",
                        "provider_native_identity_status":"UNAVAILABLE",
                        "provider_private_values_invented":False,
                    },
                    {
                        "provider_context_id":"GACR-PC-bbbbbbbbbbbbbbbb",
                        "provider":"chatgpt",
                        "connection_ref":"surface-a-2",
                        "provider_native_identity_status":"UNAVAILABLE",
                        "provider_private_values_invented":False,
                    },
                ],
                "relay":{
                    "state":"ACTIVE",
                    "lease_expires_at":"2099-01-01T00:00:00+00:00",
                    "last_action":"WORK_ACTIVE",
                    "task_id":"TASK-1",
                    "branch":"lab/test",
                    "pull_request":263,
                },
            },
            {
                "session_id":"session-b",
                "agent_identity":logical,
                "status":"STALLED",
                "provider":"chatgpt",
                "provider_conversation_ref":None,
                "provider_conversation_ref_provenance":"UNAVAILABLE",
                "connection_ref":"surface-b",
                "client_instance_id":"client-b",
                "agent_role":"qualification-client",
                "capabilities":["COMMAND_RECEIVE"],
                "wake_channels":["POLL_REPOSITORY"],
                "last_observed_head_sha":"b"*40,
                "provider_contexts":[],
                "relay":{
                    "state":"TAKEOVER_READY",
                    "last_action":"STALL_DETECTED",
                    "task_id":None,
                },
            },
        ],
    })
    write(state / "gacr-claims.json", {
        "revision":3,
        "claims":[{
            "claim_id":"claim-a",
            "session_id":"session-a",
            "work_item_id":"WORK-1",
            "status":"ACTIVE",
            "collision_domains":["domain-a"],
            "claimed_head_sha":"a"*40,
        }],
    })
    write(state / "gacr-dispatches.json", {
        "revision":4,
        "items":[{
            "dispatch_id":"dispatch-a",
            "dispatch_kind":"WORK_OFFER",
            "status":"READY",
            "target_session_id":"session-b",
            "target_logical_agent_id":logical,
            "work_item_id":"WORK-2",
            "collision_domains":["domain-b"],
        }],
    })
    write(state / "gacr-takeovers.json", {
        "revision":2,
        "items":[{
            "takeover_id":"takeover-a",
            "stalled_session_id":"session-b",
            "offered_to_session_id":"session-a",
            "status":"READY_FOR_RECONCILIATION",
            "active_claim_count":0,
            "may_continue_mutable_work":False,
        }],
    })
    write(state / "gacr-forensics.json", {
        "revision":2,
        "items":[{
            "forensic_id":"forensic-b",
            "session_id":"session-b",
            "classification":"INTERRUPTION_OBSERVED",
            "recoverability":"GOVERNED_RECONCILIATION_REQUIRED",
            "last_checkpoint_ref":"GRT-CONT-TEST-01",
            "last_evidence_ref":"github-issue-comment:3",
            "resume_point":{"checkpoint_ref":"GRT-CONT-TEST-01"},
        }],
    })
    write(state / "gacr-beacons.json", {
        "revision":1,
        "items":[{
            "beacon_id":"beacon-a",
            "session_id":"session-a",
            "event_type":"AUTO_ATTACH",
            "provider":"chatgpt",
            "connection_ref":"surface-a",
            "observed_at":"2026-10-09T00:00:00+00:00",
        }],
    })
    write(state / "gacr-correlations.json", {
        "revision":1,
        "items":[{
            "correlation_id":"corr-a",
            "beacon_id":"beacon-a",
            "level":"EXACT",
            "selected_session_id":"session-a",
            "candidate_session_ids":["session-a"],
        }],
    })
    write(state / "checkpoint.json", {
        "checkpoint":"GRT-CONT-TEST-01",
        "next_action":"CONTINUE_TEST",
        "session_id":"session-a",
    })
    write(state / "handoff.json", {
        "handoff_id":"HANDOFF-TEST-01",
        "status":"READY",
        "session_id":"session-b",
    })


def test_reconstruction() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        fixture(root)

        by_alias = run(root, "--alias", "FORGE")
        assert_true(by_alias.returncode == 0, by_alias.stderr or by_alias.stdout)
        value = json.loads(by_alias.stdout)
        assert_true(value["status"] == "RECONSTRUCTED", "reconstructed")
        assert_true(value["block"]["logical_agent_id"] == "GSCC-ID-forge-test", "logical id")
        assert_true(value["block"]["new_block_id_minted"] is False, "no new block id")
        assert_true(value["block"]["session_ids"] == ["session-a","session-b"], "two sessions")
        assert_true(value["block"]["provider_context_count"] == 2, "provider context history")
        assert_true(value["communication_bus"]["continuity_ids"] == ["GRT-CONT-TEST-01"], "continuity bus")
        assert_true(value["communication_bus"]["coordination_issues"] == [259], "coordination issue")
        assert_true(value["work_links"]["claim_ids"] == ["claim-a"], "claim link")
        assert_true(value["work_links"]["dispatch_ids"] == ["dispatch-a"], "dispatch link")
        assert_true(value["takeovers"][0]["may_continue_mutable_work"] is False, "takeover no synthetic authority")
        assert_true(value["repository_resume"]["checkpoint"]["related"] is True, "checkpoint relation")
        assert_true(value["repository_resume"]["handoff"]["related"] is True, "handoff relation")
        assert_true(value["grants_admission"] is False, "reconstruction grants no admission")
        assert_true(value["grants_claim"] is False, "reconstruction grants no claim")
        assert_true(value["grants_mutation_authority"] is False, "reconstruction grants no mutation")
        assert_true("REENTER_VIA_GSCC" in value["recommended_next_action"], "safe reentry")

        by_logical = run(root, "--logical-agent-id", "GSCC-ID-forge-test")
        by_session = run(root, "--session-id", "session-b")
        assert_true(json.loads(by_logical.stdout)["block"]["block_key"] == value["block"]["block_key"], "logical selector same block")
        assert_true(json.loads(by_session.stdout)["block"]["block_key"] == value["block"]["block_key"], "session selector same block")

        unknown = run(root, "--alias", "UNKNOWN")
        assert_true(unknown.returncode == 2, "unknown alias fails closed")
        assert_true(json.loads(unknown.stdout)["error"] == "ALIAS_NOT_FOUND", "unknown alias error")

        continuity = json.loads((root / ".governance" / "control-plane-state" / "gacr-continuities.json").read_text())
        continuity["items"].append({
            "continuity_id":"GRT-CONT-TEST-02",
            "logical_agents":[{
                "logical_agent_id":"GSCC-ID-other",
                "human_alias":"FORGE",
                "session_ids":[],
            }],
        })
        write(root / ".governance" / "control-plane-state" / "gacr-continuities.json", continuity)
        ambiguous = run(root, "--alias", "FORGE")
        assert_true(ambiguous.returncode == 2, "ambiguous alias fails closed")
        assert_true(json.loads(ambiguous.stdout)["error"] == "ALIAS_AMBIGUOUS", "ambiguous alias error")


def test_source_forge_projection_if_available() -> None:
    if not (REPO_ROOT / ".template-source").exists():
        return
    continuity_path = REPO_ROOT / ".governance" / "control-plane-state" / "gacr-continuities.json"
    if not continuity_path.exists():
        return
    continuity = json.loads(continuity_path.read_text(encoding="utf-8"))
    forge_ids = {
        str(logical.get("logical_agent_id"))
        for item in continuity.get("items", [])
        for logical in (item.get("logical_agents") or [])
        if str(logical.get("human_alias") or "").casefold() == "forge"
        and logical.get("logical_agent_id")
    }
    if not forge_ids:
        return
    assert_true(len(forge_ids) == 1, "source FORGE alias must remain exact")
    result = run(REPO_ROOT, "--alias", "FORGE", "--compact")
    assert_true(result.returncode == 0, result.stderr or result.stdout)
    value = json.loads(result.stdout)
    expected = next(iter(forge_ids))
    assert_true(value["block"]["logical_agent_id"] == expected, "live FORGE logical identity")
    assert_true(value["block"]["session_count"] >= 1, "live FORGE has reconstructable session history")
    assert_true(value["communication_bus"]["continuity_ids"], "live FORGE retains continuity bus")
    assert_true(value["grants_admission"] is False, "live reconstruction grants no admission")
    assert_true(value["grants_claim"] is False, "live reconstruction grants no claim")
    assert_true(value["grants_mutation_authority"] is False, "live reconstruction grants no mutation authority")
    assert_true(
        value["current_arrival_rule"] == "RECONSTRUCTION_DOES_NOT_BIND_CURRENT_ARRIVAL_RUN_GSCC_GSE_GACR_F1",
        "live reconstruction cannot impersonate prior provider context",
    )


def main() -> None:
    validate_repository_contract()
    test_reconstruction()
    test_source_forge_projection_if_available()
    print("GACR_AGENT_RECONSTRUCTION_SKELETON_PASS")


if __name__ == "__main__":
    main()
