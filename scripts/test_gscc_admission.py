#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone

from gscc.admission import InMemoryAdmissionStore, evaluate_admission


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


def main():
    test_valid_envelope_is_only_preauthorized()
    test_missing_required_field_is_incomplete()
    test_secret_material_fails_closed()
    test_unavailable_provider_private_reference_is_allowed()
    test_idempotent_replay_reuses_same_admission()
    print("GSCC_ADMISSION_TESTS_OK")


if __name__ == "__main__":
    main()
