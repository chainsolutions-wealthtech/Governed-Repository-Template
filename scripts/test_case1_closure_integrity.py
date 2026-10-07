#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def fail(msg: str) -> None:
    raise SystemExit("CASE1_CLOSURE_INTEGRITY_FAILED: " + msg)

def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def main() -> None:
    tasks = load(".governance/control-plane-state/tasks.json")
    replay = load(".governance/control-plane-state/case1-replay.json")
    catalog = load(".governance/control-plane-db/catalog.json")
    seed = load(".governance/control-plane-db/runtime-seed.json")
    current = load(".governance/control-plane-state/current.json")
    checkpoint = load(".governance/control-plane-state/checkpoint.json")
    handoff = load(".governance/control-plane-state/handoff.json")

    active = [x.get("id") for x in tasks.get("items", []) if x.get("status") == "IN_PROGRESS"]
    if active != ["GMC-01"]:
        fail(f"expected only GMC-01 active, got {active}")

    p12 = next((x for x in tasks.get("items", []) if x.get("id") == "P12-S6"), None)
    if not p12 or p12.get("status") != "DONE":
        fail("P12-S6 must be DONE")

    parent = next((x for x in tasks.get("items", []) if x.get("id") == "C1-13-I-B"), None)
    if not parent or parent.get("status") != "DONE":
        fail("C1-13-I-B historical parent must be reconciled DONE")

    orphan = [
        x.get("id") for x in tasks.get("items", [])
        if str(x.get("id") or "").startswith("C1-")
        and x.get("status") in {"IN_PROGRESS", "BLOCKED"}
    ]
    if orphan:
        fail(f"executable/blocked CASE1 orphan tasks remain: {orphan}")

    if replay.get("current_status") != "DONE":
        fail("CASE1 replay must be DONE")
    c14 = next((x for x in replay.get("phases", []) if x.get("id") == "C1-14"), None)
    if not c14 or c14.get("status") != "DONE":
        fail("C1-14 must be DONE")
    if (replay.get("case_completion") or {}).get("status") != "CREATE_NEW_REPOSITORY_CASE_COMPLETE":
        fail("CASE1 completion marker missing")

    case = next((x for x in catalog.get("cases", []) if x.get("case_id") == "CREATE_NEW_REPOSITORY"), None)
    if not case or case.get("status") != "DONE":
        fail("CREATE_NEW_REPOSITORY catalogue status must be DONE")

    run = next((x for x in seed.get("runs", []) if x.get("run_id") == "CASE1-PILOT-GOUVERN"), None)
    if not run or run.get("status") != "DONE" or run.get("current_phase_id") is not None:
        fail(f"relational CASE1 run must be DONE with null current phase: {run}")

    if not any(x.get("decision_id") == "CPD-073" for x in seed.get("decisions", [])):
        fail("CPD-073 missing from relational projection")
    if not any(x.get("checkpoint_id") == "CP-CHECKPOINT-20261007-023" for x in seed.get("checkpoints", [])):
        fail("CASE1 closure checkpoint missing")
    if not any(x.get("handoff_id") == "CP-HANDOFF-20261007-023" for x in seed.get("handoffs", [])):
        fail("GMC handoff missing")
    if not any(x.get("intake_id") == "MCP-201" for x in seed.get("intakes", [])):
        fail("external MCP#201 intake/history missing")

    if current.get("active_program") != "GOVERNANCE_MODEL_CATALOGUE":
        fail("current active programme must be Governance Model Catalogue")
    if current.get("unique_next_action") != "GMC_01_SEPARATE_GOVERNANCE_MODEL_FROM_APPLICATION_STRATEGIES":
        fail("current next action mismatch")
    if checkpoint.get("state") != "CREATE_NEW_REPOSITORY_CASE_COMPLETE_GMC_A_RELEASED":
        fail("checkpoint closure state mismatch")
    if handoff.get("unique_next_action") != "GMC_01_SEPARATE_GOVERNANCE_MODEL_FROM_APPLICATION_STRATEGIES":
        fail("handoff next action mismatch")

    print("CASE1_CLOSURE_INTEGRITY_PASS")

if __name__ == "__main__":
    main()
