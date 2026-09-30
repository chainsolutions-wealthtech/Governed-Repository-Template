#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / ".governance" / "control-plane-state" / "knowledge-base.json"


def main() -> None:
    kb = json.loads(PATH.read_text(encoding="utf-8"))

    if kb.get("authority_id") != "CP-KNOWLEDGE-001":
        raise SystemExit("KNOWLEDGE_BASE_TEST_FAILED: authority")
    if kb.get("execution_authority_granted") is not False:
        raise SystemExit("KNOWLEDGE_BASE_TEST_FAILED: knowledge must not grant execution")
    for key in [
        "secrets_persisted",
        "server_connection_coordinates_persisted",
        "server_filesystem_paths_persisted",
    ]:
        if kb.get(key) is not False:
            raise SystemExit(f"KNOWLEDGE_BASE_TEST_FAILED: unsafe persistence {key}")

    layers = {item["id"]: item for item in kb.get("knowledge_layers") or []}
    required = {
        "TARGET_GOVERNANCE_MODEL",
        "QUESTION_DECISION_MODEL",
        "MCP_CAPABILITY_MODEL",
        "SERVER_ORGANIZATION_KNOWLEDGE",
        "PROJECT_FACTS",
        "OWNER_DECISIONS",
        "OBSERVED_CONVENTIONS",
        "OPERATIONAL_EVIDENCE",
    }
    if required - set(layers):
        raise SystemExit("KNOWLEDGE_BASE_TEST_FAILED: missing knowledge layers")

    if layers["OPERATIONAL_EVIDENCE"]["freshness"] != "LIVE_OR_BOUNDED_TTL":
        raise SystemExit("KNOWLEDGE_BASE_TEST_FAILED: operational evidence freshness")
    if layers["OWNER_DECISIONS"]["reuse"] != "DO_NOT_REASK_UNLESS_CONTEXT_CHANGE_INVALIDATES_DECISION":
        raise SystemExit("KNOWLEDGE_BASE_TEST_FAILED: owner decision reuse")

    contract = kb.get("project_memory_contract") or {}
    if "OWNER_DECISION" not in contract.get("fact_kinds", []):
        raise SystemExit("KNOWLEDGE_BASE_TEST_FAILED: owner decisions not first-class")
    if "CONTRADICTED" not in contract.get("statuses", []):
        raise SystemExit("KNOWLEDGE_BASE_TEST_FAILED: contradiction status missing")

    prohibited = " ".join(contract.get("never_store") or [])
    for marker in ["secret_value", "private_key", "bearer_token", "server_connection_coordinates"]:
        if marker not in prohibited:
            raise SystemExit(f"KNOWLEDGE_BASE_TEST_FAILED: missing prohibition {marker}")

    serialized = PATH.read_text(encoding="utf-8")
    for leak in ["/var/www/", "/opt/apps/", "PRIVATE KEY", "Bearer "]:
        if leak in serialized:
            raise SystemExit(f"KNOWLEDGE_BASE_TEST_FAILED: unsafe seed leak {leak}")

    subjects = {item["subject_id"]: item for item in kb.get("seed_subjects") or []}
    for subject in ["CONTROL_PLANE_TEMPLATE", "CASE1_EKYC", "AFRICAFUNDS_REFERENCE", "SERVER_S1", "SERVER_S2"]:
        if subject not in subjects:
            raise SystemExit(f"KNOWLEDGE_BASE_TEST_FAILED: missing seed subject {subject}")

    if subjects["AFRICAFUNDS_REFERENCE"].get("use") != "REFERENCE_FIXTURE_ONLY_NOT_HARDCODED_PRODUCT_LOGIC":
        raise SystemExit("KNOWLEDGE_BASE_TEST_FAILED: AfricaFunds hard-code boundary")
    if subjects["SERVER_S1"].get("coordinates_persisted") is not False:
        raise SystemExit("KNOWLEDGE_BASE_TEST_FAILED: S1 coordinate safety")
    if subjects["SERVER_S2"].get("coordinates_persisted") is not False:
        raise SystemExit("KNOWLEDGE_BASE_TEST_FAILED: S2 coordinate safety")

    planned = {item["id"]: item["status"] for item in kb.get("future_incremental_work") or []}
    for item in ["KBI-03", "KBI-04", "KBI-05", "KBI-06", "KBI-07"]:
        if planned.get(item) != "PLANNED":
            raise SystemExit(f"KNOWLEDGE_BASE_TEST_FAILED: {item} must remain planned")

    print("CONTROL_PLANE_KNOWLEDGE_BASE_TEST_PASS")


if __name__ == "__main__":
    main()
