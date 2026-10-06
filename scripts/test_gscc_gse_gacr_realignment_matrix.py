#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / ".governance/control-plane-state/gscc-gse-gacr-realignment.json"
CURRENT = ROOT / ".governance/control-plane-state/first-touch-field-block-gate-catalog.json"
POST_Q1_ROUTER = ROOT / ".governance/gscc-post-q1-router.json"


def load(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def main():
    target = load(TARGET)
    current = load(CURRENT)
    post_q1 = load(POST_Q1_ROUTER)

    assert target["schema"] == "gscc-gse-gacr-realignment/v1"
    assert target["issue"] == 199
    assert target["layer_order"] == [
        "CAPTURE", "GSCC", "GSE", "GACR", "GOVERNED_REPOSITORY"
    ]

    blocks = {item["block_id"]: item for item in target["blocks"]}
    gates = {item["gate_id"]: item for item in target["gates"]}
    current_blocks = {item["block_id"]: item for item in current["blocks"]}
    current_gates = {item["gate_id"]: item for item in current["gates"]}

    # Stable catalogue identifiers are preserved: realignment changes semantics/
    # dependency placement without losing the existing evidence inventory.
    assert set(blocks) == set(current_blocks) == {f"B{i:02d}" for i in range(31)}
    assert set(gates) == set(current_gates)
    assert len(gates) == 17

    # The target ordering is dependency-driven, not inferred from legacy Q number.
    ranks = {gate_id: item["target_rank"] for gate_id, item in gates.items()}
    assert ranks["Q10"] < ranks["Q2"], ranks
    assert ranks["Q10"] < ranks["Q6"], ranks
    assert ranks["Q10"] < ranks["Q7"], ranks
    assert ranks["Q2"] < ranks["Q11"], ranks
    assert ranks["Q7"] < ranks["Q11"], ranks

    # Initial GSE interpretation must be buildable before durable GACR continuity.
    assert gates["Q10"]["target_owner_layer"] == "GSE"
    assert gates["Q10"]["target_phase"] == "GSE"
    assert blocks["B04"]["target_primary_layer"] == "GSCC"
    assert blocks["B12"]["target_primary_layer"] == "GSCC"
    assert blocks["B26"]["target_primary_layer"] == "GACR"
    assert blocks["B11"]["target_role"] == "SPLIT"
    assert blocks["B13"]["target_role"] == "SPLIT"

    target_q10_inputs = set(target["target_q10_required_inputs"])
    assert target_q10_inputs == {"B04", "B05", "B06", "B12", "B13"}
    forbidden = set(target["target_q10_forbidden_hard_prerequisites"])
    assert forbidden == {
        "GACR_SESSION_ID",
        "GACR_ACTIVE_LEASE",
        "B26_DURABLE_CONTINUITY",
    }

    # Downstream governed execution remains a separate authority boundary.
    downstream = target["preserved_downstream"]
    assert downstream == [
        "GOVERNED_REPOSITORY",
        "GOVERNED_LOCAL_ENTRY",
        "FIRST_AGENT_BOOTSTRAP",
        "NORMAL_GOVERNED_ENTRY",
        "EXISTING_GOVERNED_WORKFLOW",
    ]

    assert [item["gate"] for item in post_q1["sequence"]] == [
        "Q1", "Q3", "Q4", "Q5", "Q8", "Q9", "Q10_GSE", "Q2_GACR",
        "Q6", "Q7", "Q11", "Q12", "F1", "00_START_HERE.md",
    ]
    assert post_q1["sequence"][6]["owner_layer"] == "GSE"
    assert post_q1["sequence"][7]["owner_layer"] == "GACR"

    # Baseline proof: the current PR #198 catalogue still contains the exact
    # dependency inversion this realignment is meant to repair. This assertion
    # intentionally documents CURRENT, not TARGET, and will be revised in the
    # runtime/catalogue correction tranche.
    assert current_gates["Q2"]["owner_layer"] == "GACR"
    assert current_gates["Q2"]["ordinal"] < current_gates["Q10"]["ordinal"]
    assert current_gates["Q6"]["owner_layer"] == "GACR"
    assert current_gates["Q7"]["owner_layer"] == "GACR"

    current_q10_required = {
        row[0]
        for row in current["requirements"]["Q10"]
        if row[1] == "REQUIRED"
    }
    assert "B11" in current_q10_required
    assert "B26" in current_q10_required
    assert current_blocks["B11"]["owner_layer"] == "GACR"
    assert current_blocks["B26"]["owner_layer"] == "GACR"

    print("GSCC_GSE_GACR_REALIGNMENT_MATRIX_TEST_PASS")


if __name__ == "__main__":
    main()
