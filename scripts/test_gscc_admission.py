#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from gscc.admission import InMemoryAdmissionStore, evaluate_access_grant, evaluate_admission, evaluate_issue_comment_admission, resolve_admission_session_binding, validate_access_grant


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "gscc-admission-gate.yml"

NOW = datetime(2026, 10, 2, 12, 0, 0, tzinfo=timezone.utc)


def envelope(**overrides):
    value = {
        "schema": "gscc-admission-envelope/v1",
        "request": {
            "request_id": "admreq-test-001",
            "correlation_id": "corr-test-001",
            "idempotency_key": "idem-test-001",
            "issued_at": "2026-10-02T11:59:58+00:00",
            "observed_at": "2026-10-02T11:59:59+00:00",
        },
        "agent": {
            "agent_type": "conversation-agent",
            "provider": "chatgpt",
            "requested_role": "implementer",
        },
        "client": {
            "client_instance_id": "client-test-001",
            "client_type": "chat-client",
        },
        "session": {
            "conversation_ref": "UNAVAILABLE",
        },
        "connection": {
            "connection_ref": "connection-test-001",
            "connection_method": "gscc-controlled-host-gateway",
            "surface_class": "CONTROLLED_INSTRUMENTABLE",
            "wake_channels": ["POLL_REPOSITORY"],
        },
        "target": {
            "repository": "chainsolutions-wealthtech/Governed-Repository-Template",
            "requested_branch": "main",
        },
        "intent": {
            "entry_action": "REPOSITORY_ACCESS",
            "connection_intent": "IMPLEMENT_TASK",
            "requested_capabilities": ["READ_REPOSITORY"],
        },
        "continuity": {},
        "control_capabilities": {
            "heartbeat": True,
            "command_receive": True,
            "command_ack": True,
            "challenge_response": True,
            "checkpoint_report": True,
            "progress_report": True,
            "context_report": True,
            "reobserve_head": True,
        },
    }
    for key, replacement in overrides.items():
        value[key] = replacement
    return value


def test_valid_envelope_is_only_preauthorized():
    result = evaluate_admission(envelope(), store=InMemoryAdmissionStore(), now=NOW)
    assert result["status"] == "PREAUTHORIZED", result
    assert result["repository_access"] == "NOT_YET_GRANTED", result
    assert result["mutation_authority_granted"] is False, result
    assert result["admission_id"].startswith("GSCC-ADM-"), result


def test_missing_required_field_is_incomplete():
    data = envelope()
    del data["agent"]["provider"]
    result = evaluate_admission(data, store=InMemoryAdmissionStore(), now=NOW)
    assert result["status"] == "ADMISSION_INCOMPLETE", result
    assert "agent.provider" in result["missing_fields"], result
    assert result["repository_access"] == "NOT_YET_GRANTED", result


def test_secret_material_fails_closed():
    data = envelope()
    data["client"]["access_token"] = "super-secret"
    result = evaluate_admission(data, store=InMemoryAdmissionStore(), now=NOW)
    assert result["status"] == "ADMISSION_DENIED", result
    assert result["reason_code"] == "FORBIDDEN_MATERIAL", result
    assert result["repository_access"] == "NOT_YET_GRANTED", result


def test_unavailable_provider_private_reference_is_allowed():
    result = evaluate_admission(envelope(), store=InMemoryAdmissionStore(), now=NOW)
    assert result["status"] == "PREAUTHORIZED", result
    assert result["provider_private_identity_inferred"] is False, result


def test_idempotent_replay_reuses_same_admission():
    store = InMemoryAdmissionStore()
    first = evaluate_admission(envelope(), store=store, now=NOW)
    second = evaluate_admission(envelope(), store=store, now=NOW)
    assert second["admission_id"] == first["admission_id"], (first, second)
    assert second["replay"] is True, second
    assert len(store.records) == 1, store.records



def qualification(admission):
    return {
        "session": {
            "status": "BOUND",
            "session_id": "session-live",
            "connection_ref": admission["connection_ref"],
        },
        "governance_read": {
            "status": "COMPLETED",
            "documents": [
                {"path": "GOVERNANCE.md", "digest": "g" * 64},
                {"path": "docs/control-plane/GSCC_ADMISSION_ACCESS_GATE.md", "digest": "a" * 64},
            ],
        },
        "repository_baseline": {
            "status": "OBSERVED",
            "repository": admission["repository"],
            "observed_head": "a" * 40,
        },
        "task": {"status": "RECONCILED", "task_id": "TASK-TEST-1"},
        "claim": {"status": "RECONCILED", "claim_id": "CLAIM-TEST-1"},
        "capabilities": {"status": "VERIFIED"},
        "control_channel": {"status": "VERIFIED"},
        "gse_initial_state": {
            "presence": "PRESENT",
            "liveness": "VERIFIED",
            "control_reachability": "REACHABLE",
        },
        "access_policy": {
            "status": "ALLOW",
            "allowed_authority_classes": ["READ_ONLY_DISCOVERY_AUTHORITY"],
            "constraints": {"direct_main_write": False, "merge": False},
        },
    }


_legacy_qualification_fixture = qualification


def seal_qualification(value):
    value.pop("harvest_digest", None)
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    value["harvest_digest"] = hashlib.sha256(raw).hexdigest()
    return value


def qualification(admission):
    value = _legacy_qualification_fixture(admission)
    value["schema"] = "gscc-qualification-evidence/v1"
    value["harvested_by"] = "GSCC_ADMISSION_HARVESTER"
    return seal_qualification(value)


def test_noncanonical_caller_qualification_evidence_is_denied():
    admission = evaluate_admission(envelope(), store=InMemoryAdmissionStore(), now=NOW)
    result = evaluate_access_grant(
        admission,
        {"session": {"status": "BOUND", "session_id": "fake", "connection_ref": admission["connection_ref"]}},
        now=NOW,
    )
    assert result["status"] == "ADMISSION_DENIED", result
    assert result["reason_code"] == "QUALIFICATION_EVIDENCE_NOT_CANONICAL", result


def test_receipt_carries_safe_context_and_field_provenance():
    result = evaluate_admission(envelope(), store=InMemoryAdmissionStore(), now=NOW)
    assert result["admission_context"]["agent"]["provider"] == "chatgpt", result
    provider = result["field_provenance"]["agent.provider"]
    assert provider["source_method"] == "POST", provider
    assert provider["provenance"] == "DECLARED_BY_AGENT_OR_CLIENT", provider
    model = result["field_provenance"]["agent.model_runtime"]
    assert model["status"] == "UNAVAILABLE", model
    assert model["reason"] == "NOT_EXPOSED_BY_PROVIDER", model
    assert model["provenance"] == "PROVIDER_PRIVATE_UNAVAILABLE", model


def test_incomplete_qualification_cannot_issue_access_grant():
    admission = evaluate_admission(envelope(), store=InMemoryAdmissionStore(), now=NOW)
    evidence = qualification(admission)
    evidence["governance_read"] = {"status": "PENDING", "documents": []}
    seal_qualification(evidence)
    result = evaluate_access_grant(admission, evidence, now=NOW)
    assert result["status"] == "QUALIFICATION_IN_PROGRESS", result
    assert "governance_read" in result["missing_qualification"], result
    assert result["invocation_authority_granted"] is False, result
    assert result["mutation_authority_granted"] is False, result


def test_complete_qualification_issues_bounded_access_grant():
    admission = evaluate_admission(envelope(), store=InMemoryAdmissionStore(), now=NOW)
    result = evaluate_access_grant(admission, qualification(admission), now=NOW)
    assert result["schema"] == "gscc-access-grant/v1", result
    assert result["status"] == "AUTHORIZED", result
    assert result["access_class"] == "GOVERNED_FUNCTION_EXPOSURE_ELIGIBLE", result
    assert result["grant_id"].startswith("GSCC-GRANT-"), result
    assert result["admission_id"] == admission["admission_id"], result
    assert result["session_id"] == "session-live", result
    assert result["connection_ref"] == admission["connection_ref"], result
    assert result["repository"] == admission["repository"], result
    assert result["bound_head"] == "a" * 40, result
    assert result["invocation_authority_granted"] is False, result
    assert result["mutation_authority_granted"] is False, result


def test_access_grant_validation_is_binding_and_expiry_sensitive():
    admission = evaluate_admission(envelope(), store=InMemoryAdmissionStore(), now=NOW)
    grant = evaluate_access_grant(admission, qualification(admission), now=NOW)

    valid = validate_access_grant(
        grant,
        connection_ref=admission["connection_ref"],
        repository=admission["repository"],
        requested_head="a" * 40,
        session_id="session-live",
        now=NOW,
    )
    assert valid["status"] == "VALIDATED", valid

    wrong_head = validate_access_grant(
        grant,
        connection_ref=admission["connection_ref"],
        repository=admission["repository"],
        requested_head="b" * 40,
        session_id="session-live",
        now=NOW,
    )
    assert wrong_head["reason_code"] == "ACCESS_GRANT_HEAD_MISMATCH", wrong_head

    expired = validate_access_grant(
        grant,
        connection_ref=admission["connection_ref"],
        repository=admission["repository"],
        requested_head="a" * 40,
        session_id="session-live",
        now=datetime(2026, 10, 2, 13, 0, 0, tzinfo=timezone.utc),
    )
    assert expired["reason_code"] == "ACCESS_GRANT_EXPIRED", expired



def test_admission_workflow_exposes_only_governed_admission_and_qualification():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "gscc_admission_request" in text, text
    assert "gscc_access_qualification_request" in text, text
    assert "admission_envelope_json" in text, text
    assert "qualification_evidence_json" in text, text
    assert "python3 scripts/gscc/admission.py evaluate" in text, text
    assert "python3 scripts/gscc/admission.py qualify" in text, text
    assert "contents: read" in text, text
    assert "contents: write" not in text, text


def test_admission_cli_exists_without_repository_mutation_surface():
    source = (ROOT / "scripts" / "gscc" / "admission.py").read_text(encoding="utf-8")
    assert 'sub.add_parser("evaluate")' in source, source
    assert 'sub.add_parser("qualify")' in source, source
    assert "update_file" not in source, source
    assert "create_branch" not in source, source
    assert "merge_pull_request" not in source, source



def issue_comment_event(body, *, issue_number=161, association="MEMBER", comment_id=700001):
    return {
        "issue": {"number": issue_number},
        "comment": {
            "id": comment_id,
            "body": body,
            "author_association": association,
            "user": {"login": "Wealthtechinnovations"},
        },
        "repository": {"full_name": "chainsolutions-wealthtech/Governed-Repository-Template"},
    }


def test_issue_comment_admission_bridge_accepts_only_bounded_safe_ingress():
    payload = json.dumps(envelope(), separators=(",", ":"))
    result = evaluate_issue_comment_admission(
        issue_comment_event("/gscc-admission " + payload),
        expected_issue_number=161,
        now=NOW,
    )
    assert result["status"] == "PREAUTHORIZED", result
    assert result["repository_access"] == "NOT_YET_GRANTED", result
    assert result["transport"] == "GITHUB_ISSUE_COMMENT", result
    assert result["transport_event_ref"] == "issue-comment:700001", result
    assert result["mutation_authority_granted"] is False, result


def test_issue_comment_admission_bridge_fails_closed_on_wrong_issue_or_actor():
    payload = json.dumps(envelope(), separators=(",", ":"))
    wrong_issue = evaluate_issue_comment_admission(
        issue_comment_event("/gscc-admission " + payload, issue_number=999),
        expected_issue_number=161,
        now=NOW,
    )
    assert wrong_issue["status"] == "ADMISSION_DENIED", wrong_issue
    assert wrong_issue["reason_code"] == "ADMISSION_INGRESS_ISSUE_MISMATCH", wrong_issue

    wrong_actor = evaluate_issue_comment_admission(
        issue_comment_event("/gscc-admission " + payload, association="NONE"),
        expected_issue_number=161,
        now=NOW,
    )
    assert wrong_actor["status"] == "ADMISSION_DENIED", wrong_actor
    assert wrong_actor["reason_code"] == "ADMISSION_INGRESS_ACTOR_NOT_AUTHORIZED", wrong_actor


def test_issue_comment_admission_workflow_is_bound_to_dedicated_issue():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "issue_comment:" in text, text
    assert "created" in text, text
    assert "/gscc-admission " in text, text
    assert "161" in text, text
    assert "OWNER" in text and "MEMBER" in text and "COLLABORATOR" in text, text
    assert "python3 scripts/gscc/admission.py issue-comment" in text, text
    assert "contents: write" not in text, text



def admission_receipt_for_binding(**overrides):
    value = {
        "schema": "gscc-admission-receipt/v1",
        "status": "PREAUTHORIZED",
        "admission_id": "GSCC-ADM-" + ("a" * 64),
        "request_id": "admreq-bind-001",
        "connection_ref": "declared-connection-001",
        "client_instance_id": "github-observable:chainsolutions-wealthtech/Governed-Repository-Template:Wealthtechinnovations",
        "provider": "chatgpt",
        "requested_branch": "main",
        "repository": "chainsolutions-wealthtech/Governed-Repository-Template",
        "transport": "GITHUB_ISSUE_COMMENT",
        "transport_author_login": "Wealthtechinnovations",
        "repository_access": "NOT_YET_GRANTED",
        "invocation_authority_granted": False,
        "mutation_authority_granted": False,
    }
    value.update(overrides)
    return value


def gacr_sessions_for_binding(*, duplicate=False):
    base = {
        "session_id": "session-canonical-live",
        "repository": "chainsolutions-wealthtech/Governed-Repository-Template",
        "status": "ACTIVE",
        "connection_ref": "gscc-observable:chainsolutions-wealthtech/Governed-Repository-Template:Wealthtechinnovations:ref:main",
        "client_instance_id": "github-observable:chainsolutions-wealthtech/Governed-Repository-Template:Wealthtechinnovations",
        "provider": "other",
        "branch": "main",
        "surface_class": "GITHUB_EVENT_VISIBLE",
        "connection_method": "gscc-github-event-gateway",
        "relay": {"state": "ACTIVE", "branch": "main"},
    }
    sessions = [base]
    if duplicate:
        sessions.append({**base, "session_id": "session-canonical-second"})
    return {"sessions": sessions}


def test_session_binding_prefers_exact_connection_ref():
    receipt = admission_receipt_for_binding(
        connection_ref="gscc-observable:chainsolutions-wealthtech/Governed-Repository-Template:Wealthtechinnovations:ref:main"
    )
    result = resolve_admission_session_binding(receipt, gacr_sessions_for_binding(), now=NOW)
    assert result["status"] == "BOUND", result
    assert result["correlation"] == "EXACT", result
    assert result["session_id"] == "session-canonical-live", result
    assert result["canonical_connection_ref"].startswith("gscc-observable:"), result


def test_session_binding_uses_unique_strong_observable_anchor_without_rewriting_admission():
    receipt = admission_receipt_for_binding()
    result = resolve_admission_session_binding(receipt, gacr_sessions_for_binding(), now=NOW)
    assert result["status"] == "BOUND", result
    assert result["correlation"] == "STRONG", result
    assert result["admission_connection_ref"] == "declared-connection-001", result
    assert result["canonical_connection_ref"] != result["admission_connection_ref"], result
    assert result["session_id"] == "session-canonical-live", result


def test_session_binding_fails_closed_when_ambiguous_or_missing():
    receipt = admission_receipt_for_binding()
    ambiguous = resolve_admission_session_binding(receipt, gacr_sessions_for_binding(duplicate=True), now=NOW)
    assert ambiguous["status"] == "UNBOUND", ambiguous
    assert ambiguous["reason_code"] == "ADMISSION_SESSION_BIND_AMBIGUOUS", ambiguous

    missing = resolve_admission_session_binding(receipt, {"sessions": []}, now=NOW)
    assert missing["status"] == "UNBOUND", missing
    assert missing["reason_code"] == "ADMISSION_SESSION_BIND_NOT_FOUND", missing


def test_access_grant_accepts_only_attested_admission_to_canonical_session_binding():
    admission = admission_receipt_for_binding()
    binding = resolve_admission_session_binding(admission, gacr_sessions_for_binding(), now=NOW)
    evidence = qualification(admission)
    evidence["session"] = {
        "status": "BOUND",
        "session_id": binding["session_id"],
        "connection_ref": binding["canonical_connection_ref"],
        "admission_connection_ref": binding["admission_connection_ref"],
        "binding_level": binding["correlation"],
        "binding_evidence_ref": binding["binding_evidence_ref"],
    }
    evidence["repository_baseline"]["observed_head"] = "a" * 40
    seal_qualification(evidence)
    result = evaluate_access_grant(admission, evidence, now=NOW)
    assert result["status"] == "AUTHORIZED", result
    assert result["connection_ref"] == binding["canonical_connection_ref"], result
    assert result["admission_connection_ref"] == "declared-connection-001", result


def main():
    test_valid_envelope_is_only_preauthorized()
    test_missing_required_field_is_incomplete()
    test_secret_material_fails_closed()
    test_unavailable_provider_private_reference_is_allowed()
    test_idempotent_replay_reuses_same_admission()
    test_receipt_carries_safe_context_and_field_provenance()
    test_noncanonical_caller_qualification_evidence_is_denied()
    test_incomplete_qualification_cannot_issue_access_grant()
    test_complete_qualification_issues_bounded_access_grant()
    test_access_grant_validation_is_binding_and_expiry_sensitive()
    test_admission_workflow_exposes_only_governed_admission_and_qualification()
    test_admission_cli_exists_without_repository_mutation_surface()
    test_issue_comment_admission_bridge_accepts_only_bounded_safe_ingress()
    test_issue_comment_admission_bridge_fails_closed_on_wrong_issue_or_actor()
    test_issue_comment_admission_workflow_is_bound_to_dedicated_issue()
    test_session_binding_prefers_exact_connection_ref()
    test_session_binding_uses_unique_strong_observable_anchor_without_rewriting_admission()
    test_session_binding_fails_closed_when_ambiguous_or_missing()
    test_access_grant_accepts_only_attested_admission_to_canonical_session_binding()
    print("GSCC_ADMISSION_TESTS_OK")


if __name__ == "__main__":
    main()