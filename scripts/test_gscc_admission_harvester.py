#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone

from gscc.admission_harvester import (
    harvest_qualification_evidence,
    normalize_unavailable,
    observe_repository,
    resolve_gacr_session,
)

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
        connection_ref="connection-test-001",
        repository=REPOSITORY,
        now=NOW,
    )
    assert session["status"] == "BOUND", session
    assert session["session_id"] == "session-live", session
    assert session["connection_envelope"]["schema"] == "gacr-connection-envelope/v1", session
    assert session["provenance"]["source"] == "GACR_CANONICAL_SESSION_STORE", session


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


def main():
    test_repository_facts_are_get_observed()
    test_gacr_session_is_bound_from_canonical_store()
    test_unavailable_is_structured_not_silent()
    test_harvest_uses_canonical_sources_and_fails_closed_on_missing_gse_control()
    test_caller_repository_claim_cannot_override_get_observation()
    print("GSCC_ADMISSION_HARVESTER_TESTS_OK")


if __name__ == "__main__":
    main()
