#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone

from gscc.admission_access_policy import evaluate_access_policy

NOW = datetime(2026, 10, 2, 13, 50, 0, tzinfo=timezone.utc)


def policy():
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
    }


def admission(*caps):
    return {
        "schema": "gscc-admission-receipt/v1",
        "status": "PREAUTHORIZED",
        "admission_id": "GSCC-ADM-test",
        "repository": "chainsolutions-wealthtech/Governed-Repository-Template",
        "connection_ref": "connection-test",
        "admission_context": {
            "intent": {
                "entry_action": "REPOSITORY_ACCESS",
                "connection_intent": "READ_ONLY_DISCOVERY",
                "requested_capabilities": list(caps or ("READ_REPOSITORY",)),
            }
        },
    }


def prerequisites():
    return {
        "session": {"status": "BOUND", "session_id": "session-live", "connection_ref": "connection-test"},
        "repository_baseline": {
            "status": "OBSERVED",
            "repository": "chainsolutions-wealthtech/Governed-Repository-Template",
            "observed_head": "a" * 40,
        },
        "capabilities": {
            "status": "VERIFIED",
            "verified": ["COMMAND_RECEIVE", "COMMAND_ACK", "CHALLENGE_RESPONSE"],
            "evidence_ref": "github-issue-comment:700002",
        },
        "control_channel": {
            "status": "VERIFIED",
            "state": "REACHABLE",
            "evidence_ref": "github-issue-comment:700002",
        },
        "gse_initial_state": {
            "schema": "gscc-gse-admission-state/v1",
            "status": "VERIFIED",
            "presence": "PRESENT",
            "liveness": "VERIFIED",
            "control_reachability": "REACHABLE",
            "evidence_ref": "github-issue-comment:700002",
        },
    }


def test_read_only_policy_allows_only_read_discovery_class():
    result = evaluate_access_policy(admission("READ_REPOSITORY"), policy(), prerequisites(), now=NOW)
    assert result["status"] == "ALLOW", result
    assert result["allowed_authority_classes"] == ["READ_ONLY_DISCOVERY_AUTHORITY"], result
    assert result["constraints"]["mutation"] is False, result
    assert result["constraints"]["direct_main_write"] is False, result
    assert result["invocation_authority_granted"] is False, result
    assert result["mutation_authority_granted"] is False, result
    assert result["evidence_ref"].startswith("gscc-access-policy:"), result


def test_unknown_or_mutating_requested_capability_denies_by_default():
    for cap in ("WRITE_REPOSITORY", "MERGE_PULL_REQUEST", "DEPLOY", "ADMIN"):
        result = evaluate_access_policy(admission(cap), policy(), prerequisites(), now=NOW)
        assert result["status"] == "DENY", (cap, result)
        assert result["allowed_authority_classes"] == [], (cap, result)


def test_missing_control_or_gse_keeps_policy_pending():
    pre = prerequisites()
    pre["control_channel"] = {"status": "UNAVAILABLE"}
    result = evaluate_access_policy(admission("READ_REPOSITORY"), policy(), pre, now=NOW)
    assert result["status"] == "PENDING", result
    assert result["allowed_authority_classes"] == [], result

    pre = prerequisites()
    pre["gse_initial_state"]["liveness"] = "QUIET"
    result = evaluate_access_policy(admission("READ_REPOSITORY"), policy(), pre, now=NOW)
    assert result["status"] == "PENDING", result
    assert result["allowed_authority_classes"] == [], result


def test_policy_never_grants_operational_or_mutation_authority():
    result = evaluate_access_policy(admission("READ_REPOSITORY"), policy(), prerequisites(), now=NOW)
    assert "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED" not in result["allowed_authority_classes"], result
    assert "GOVERNED_OPERATIONAL_AUTHORITY_REQUIRED" not in result["allowed_authority_classes"], result
    assert result["invocation_authority_granted"] is False, result
    assert result["mutation_authority_granted"] is False, result


def main():
    test_read_only_policy_allows_only_read_discovery_class()
    test_unknown_or_mutating_requested_capability_denies_by_default()
    test_missing_control_or_gse_keeps_policy_pending()
    test_policy_never_grants_operational_or_mutation_authority()
    print("GSCC_ADMISSION_ACCESS_POLICY_TESTS_OK")


if __name__ == "__main__":
    main()
