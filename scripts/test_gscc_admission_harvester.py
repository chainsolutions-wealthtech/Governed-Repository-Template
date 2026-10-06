#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

from gscc.admission_harvester import (
    harvest_qualification_evidence,
    normalize_unavailable,
    observe_repository,
    resolve_gacr_session,
)

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 2, 12, 0, 0, tzinfo=timezone.utc)
REPOSITORY = "chainsolutions-wealthtech/Governed-Repository-Template"
HEAD = "a" * 40


def fake_github(url: str) -> dict:
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


def sample_admission() -> dict:
    return {
        "schema": "gscc-admission-receipt/v1",
        "status": "PREAUTHORIZED",
        "admission_id": "GSCC-ADM-test",
        "connection_ref": "connection-test-001",
        "repository": REPOSITORY,
        "admission_context": {
            "target": {"requested_branch": "main"},
            "intent": {
                "entry_action": "REPOSITORY_ACCESS",
                "connection_intent": "IMPLEMENT_TASK",
                "requested_capabilities": ["READ_REPOSITORY"],
            },
        },
    }


def sample_sessions() -> dict:
    return {
        "sessions": [{
            "session_id": "session-live",
            "connection_ref": "connection-test-001",
            "repository": REPOSITORY,
            "status": "ACTIVE",
            "last_observed_head_sha": HEAD,
            "capabilities": ["COMMAND_RECEIVE", "COMMAND_ACK"],
            "relay": {
                "state": "ACTIVE",
                "lease_expires_at": "2026-10-02T12:15:00+00:00",
                "task_id": None,
            },
            "connection_envelope": {
                "schema": "gacr-connection-envelope/v1",
                "fields": {
                    "provider": {
                        "value": "chatgpt",
                        "provenance": "CORRELATED",
                        "source": "CLIENT_OR_SESSION",
                    },
                    "HEAD": {
                        "value": HEAD,
                        "provenance": "OBSERVABLE_BY_PLATFORM",
                        "source": "REPOSITORY_SURFACE",
                    },
                },
            },
        }]
    }


def test_repository_facts_are_get_observed():
    observed = observe_repository(
        REPOSITORY,
        "main",
        request_fn=fake_github,
        observed_at=NOW,
    )
    assert observed["status"] == "OBSERVED", observed
    assert observed["repository_id"] == "1386478935", observed
    assert observed["organization"] == "chainsolutions-wealthtech", observed
    assert observed["default_branch"] == "main", observed
    assert observed["observed_head"] == HEAD, observed
    assert observed["provenance"]["source_method"] == "GET", observed
    assert observed["provenance"]["source"] == "GITHUB_API", observed


def test_gacr_session_is_bound_from_canonical_store():
    session = resolve_gacr_session(
        sample_sessions(),
        admission_receipt=sample_admission(),
        connection_ref="connection-test-001",
        repository=REPOSITORY,
        now=NOW,
    )
    assert session["status"] == "BOUND", session
    assert session["session_id"] == "session-live", session
    assert session["connection_envelope"]["schema"] == "gacr-connection-envelope/v1", session
    assert session["provenance"]["source"] == "GACR_CANONICAL_SESSION_BINDING", session
    assert session["binding_level"] == "EXACT", session
    assert session["binding_evidence_ref"].startswith("GSCC-BIND-"), session


def test_unavailable_is_structured_not_silent():
    value = normalize_unavailable("NOT_EXPOSED_BY_PROVIDER", "HOST_OR_PROVIDER", NOW)
    assert value == {
        "status": "UNAVAILABLE",
        "reason": "NOT_EXPOSED_BY_PROVIDER",
        "provenance": "PROVIDER_PRIVATE_UNAVAILABLE",
        "source": "HOST_OR_PROVIDER",
        "observed_at": "2026-10-02T12:00:00+00:00",
    }, value


def test_harvest_uses_canonical_sources_and_fails_closed_on_missing_gse_control():
    result = harvest_qualification_evidence(
        sample_admission(),
        github_request_fn=fake_github,
        sessions=sample_sessions(),
        claims={"claims": []},
        tasks={"tasks": []},
        governance_documents={
            "00_START_HERE.md": "start",
            "GOVERNANCE.md": "governance",
            "docs/control-plane/GSCC_ADMISSION_ACCESS_GATE.md": "admission",
            "docs/control-plane/GACR_PROGRAM.md": "gacr",
        },
        now=NOW,
    )
    assert result["schema"] == "gscc-qualification-evidence/v1", result
    assert result["harvested_by"] == "GSCC_ADMISSION_HARVESTER", result
    assert result["repository_baseline"]["observed_head"] == HEAD, result
    assert result["session"]["session_id"] == "session-live", result
    assert result["governance_read"]["status"] == "COMPLETED", result
    assert result["capabilities"]["status"] == "DECLARED_BUT_UNVERIFIED", result
    assert result["control_channel"]["status"] == "UNAVAILABLE", result
    assert result["gse_initial_state"]["status"] == "UNAVAILABLE", result
    assert result["status"] == "QUALIFICATION_EVIDENCE_PARTIAL", result
    assert "control_channel" in result["missing_canonical_evidence"], result
    assert "gse_initial_state" in result["missing_canonical_evidence"], result


def test_caller_repository_claim_cannot_override_get_observation():
    admission = sample_admission()
    admission["repository"] = "attacker/other"
    result = harvest_qualification_evidence(
        admission,
        target_repository=REPOSITORY,
        github_request_fn=fake_github,
        sessions=sample_sessions(),
        claims={"claims": []},
        tasks={"tasks": []},
        governance_documents={
            "00_START_HERE.md": "start",
            "GOVERNANCE.md": "governance",
            "docs/control-plane/GSCC_ADMISSION_ACCESS_GATE.md": "admission",
            "docs/control-plane/GACR_PROGRAM.md": "gacr",
        },
        now=NOW,
    )
    assert result["repository_baseline"]["repository"] == REPOSITORY, result
    assert result["repository_baseline"]["provenance"]["source_method"] == "GET", result



def test_admission_workflow_harvests_instead_of_trusting_caller_evidence():
    workflow = (ROOT / ".github" / "workflows" / "gscc-admission-gate.yml").read_text(encoding="utf-8")
    assert "gscc_entry_request" in workflow, workflow
    assert "python3 scripts/gscc/admission_harvester.py harvest" in workflow, workflow
    assert "GITHUB_TOKEN: ${{ github.token }}" in workflow, workflow
    assert "Deprecated" in workflow or "deprecated" in workflow, workflow
    assert "QUALIFICATION_EVIDENCE_JSON: ${{ github.event.client_payload.qualification_evidence_json" not in workflow, workflow


def test_gacr_head_mismatch_is_reobserved_for_access_without_rewriting_session_store():
    sessions = sample_sessions()
    sessions["sessions"][0]["last_observed_head_sha"] = "b" * 40
    original_store_head = sessions["sessions"][0]["last_observed_head_sha"]
    result = harvest_qualification_evidence(
        sample_admission(),
        github_request_fn=fake_github,
        sessions=sessions,
        claims={"claims": []},
        tasks={"tasks": []},
        governance_documents={
            "00_START_HERE.md": "start",
            "GOVERNANCE.md": "governance",
            "docs/control-plane/GSCC_ADMISSION_ACCESS_GATE.md": "admission",
            "docs/control-plane/GACR_PROGRAM.md": "gacr",
        },
        now=NOW,
    )
    assert result["session"]["status"] == "BOUND", result
    assert result["session"]["previous_observed_head"] == "b" * 40, result
    assert result["session"]["last_observed_head"] == "a" * 40, result
    reconciliation = result["session"]["head_reconciliation"]
    assert reconciliation["status"] == "REOBSERVED_CURRENT_HEAD", reconciliation
    assert reconciliation["source"] == "GITHUB_API", reconciliation
    assert reconciliation["canonical_session_store_mutated"] is False, reconciliation
    assert sessions["sessions"][0]["last_observed_head_sha"] == original_store_head, sessions
    assert "session" not in result["missing_canonical_evidence"], result


def test_harvester_direct_cli_import_path_is_valid():
    script = Path(__file__).resolve().parent / "gscc" / "admission_harvester.py"
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, (result.stdout, result.stderr)
    assert "GSCC canonical admission qualification evidence harvester" in result.stdout, result.stdout

def main():
    test_repository_facts_are_get_observed()
    test_gacr_session_is_bound_from_canonical_store()
    test_unavailable_is_structured_not_silent()
    test_harvest_uses_canonical_sources_and_fails_closed_on_missing_gse_control()
    test_caller_repository_claim_cannot_override_get_observation()
    test_admission_workflow_harvests_instead_of_trusting_caller_evidence()
    test_gacr_head_mismatch_is_reobserved_for_access_without_rewriting_session_store()
    test_harvester_direct_cli_import_path_is_valid()
    test_q10_is_verified_without_preexisting_gacr_session()
    print("GSCC_ADMISSION_HARVESTER_TESTS_OK")


if __name__ == "__main__":
    main()


def test_q10_is_verified_without_preexisting_gacr_session():
    admission = sample_admission()
    admission["admission_context"]["control_capabilities"] = {
        "command_receive": True,
        "command_ack": True,
        "challenge_response": True,
    }
    result = harvest_qualification_evidence(
        admission,
        github_request_fn=fake_github,
        sessions={"sessions": []},
        claims={"claims": []},
        tasks={"tasks": []},
        governance_documents={
            "00_START_HERE.md": "start",
            "GOVERNANCE.md": "governance",
            "docs/control-plane/GSCC_ADMISSION_ACCESS_GATE.md": "admission",
            "docs/control-plane/GACR_PROGRAM.md": "gacr",
        },
        capability_evidence={
            "status": "VERIFIED",
            "evidence_ref": "capability:q8:test",
            "observed_at": "2026-10-02T12:00:01+00:00",
        },
        control_evidence={
            "status": "VERIFIED",
            "state": "REACHABLE",
            "evidence_ref": "control:q9:test",
            "observed_at": "2026-10-02T12:00:02+00:00",
            "challenge_id": "challenge-q9-test",
        },
        now=NOW,
    )
    assert result["session"]["status"] != "BOUND", result
    assert result["gse_initial_state"]["status"] == "VERIFIED", result
    assert result["gse_initial_state"]["durable_gacr_session_required"] is False, result
    assert result["q10_status"] == "Q10_GSE_VERIFIED", result
    assert result["pre_gse_missing_canonical_evidence"] == [], result
    assert result["post_gse_gacr_required"] is True, result
    assert result["status"] == "Q10_GSE_VERIFIED_PENDING_GACR", result
    assert "session" in result["missing_canonical_evidence"], result
