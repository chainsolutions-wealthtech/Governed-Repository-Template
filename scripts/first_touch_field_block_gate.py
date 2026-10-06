#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DB_ROOT = ROOT / ".governance" / "control-plane-db"
CATALOG_PATH = ROOT / ".governance" / "control-plane-state" / "first-touch-field-block-gate-catalog.json"


def jdump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def value_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def load_catalog(path: Path = CATALOG_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != "first-touch-field-block-gate-catalog/v1":
        raise ValueError("unsupported first-touch field/block/gate catalogue")
    return value


def install_schema(conn: sqlite3.Connection) -> None:
    migration = DB_ROOT / "007_first_touch_field_block_gate.sql"
    conn.executescript(migration.read_text(encoding="utf-8"))


def insert_catalog(conn: sqlite3.Connection, catalog: dict[str, Any] | None = None) -> None:
    catalog = catalog or load_catalog()
    for block in catalog["blocks"]:
        conn.execute(
            "INSERT OR REPLACE INTO first_touch_evidence_blocks(block_id,ordinal,label,owner_layer,purpose) VALUES(?,?,?,?,?)",
            (block["block_id"], block["ordinal"], block["label"], block["owner_layer"], block["purpose"]),
        )
    for gate in catalog["gates"]:
        conn.execute(
            "INSERT OR REPLACE INTO first_touch_process_gates(gate_id,ordinal,phase,owner_layer,label,unlock_effect,authority_effect) VALUES(?,?,?,?,?,?,?)",
            (gate["gate_id"], gate["ordinal"], gate["phase"], gate["owner_layer"], gate["label"], gate["unlock_effect"], gate["authority_effect"]),
        )
    for gate_id, reqs in catalog["requirements"].items():
        for block_id, requirement, minimum_status in reqs:
            conn.execute(
                "INSERT OR REPLACE INTO first_touch_gate_requirements(gate_id,block_id,requirement,minimum_status) VALUES(?,?,?,?)",
                (gate_id, block_id, requirement, minimum_status),
            )
    for rule in catalog["rules"]:
        conn.execute(
            "INSERT OR REPLACE INTO first_touch_field_assignment_rules(rule_id,priority,match_kind,pattern,block_id,usage_purpose,stage_hint) VALUES(?,?,?,?,?,?,?)",
            (rule["rule_id"], rule["priority"], rule["match_kind"], rule["pattern"], rule["block_id"], rule["usage_purpose"], rule.get("stage_hint")),
        )


def _walk(value: Any, path: str = "$", parent: str | None = None, key_name: str | None = None, array_index: int | None = None):
    yield path, parent, key_name, array_index, value
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path != "$" else f"$.{key}"
            yield from _walk(child, child_path, path, str(key), None)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]", path, None, index)


def _rule_matches(path: str, rule: dict[str, Any]) -> bool:
    kind = rule["match_kind"]
    pattern = rule["pattern"]
    if kind == "FALLBACK":
        return True
    if kind == "PREFIX":
        return path.startswith(pattern)
    if kind == "CONTAINS":
        return pattern.lower() in path.lower()
    if kind == "REGEX":
        return bool(re.search(pattern, path))
    raise ValueError(f"unknown match kind: {kind}")


def _status_rank(status: str) -> int:
    return {
        "EMPTY": 0,
        "UNAVAILABLE": 0,
        "PARTIAL": 1,
        "PRESENT": 2,
        "SUFFICIENT": 3,
        "VERIFIED": 4,
        "STALE": 1,
        "CONFLICTING": 1,
    }[status]


def ingest_capture(
    conn: sqlite3.Connection,
    capture: dict[str, Any],
    *,
    source_ref: str | None = None,
    evaluated_at: str | None = None,
) -> dict[str, Any]:
    catalog = load_catalog()
    insert_catalog(conn, catalog)

    capture_id = str(capture.get("capture_id") or "")
    if not capture_id:
        raise ValueError("capture_id required")
    raw = json.dumps(capture, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    nodes = list(_walk(capture))
    terminal_count = sum(not isinstance(value, (dict, list)) for *_, value in nodes)
    attempts = capture.get("api_attempts") if isinstance(capture.get("api_attempts"), list) else []

    conn.execute(
        "INSERT OR REPLACE INTO first_touch_capture_records("
        "capture_id,schema_id,observed_at,repository,actor,capture_digest,raw_json,raw_json_sha256,"
        "node_count,terminal_value_count,api_attempt_count,source_ref) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            capture_id,
            str(capture.get("schema") or "UNKNOWN"),
            capture.get("observed_at"),
            capture.get("repository"),
            capture.get("actor"),
            capture.get("capture_digest"),
            raw,
            hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            len(nodes),
            terminal_count,
            len(attempts),
            source_ref,
        ),
    )

    conn.execute("DELETE FROM first_touch_capture_nodes WHERE capture_id=?", (capture_id,))
    conn.execute("DELETE FROM first_touch_field_block_membership WHERE capture_id=?", (capture_id,))
    conn.execute("DELETE FROM first_touch_capture_api_attempts WHERE capture_id=?", (capture_id,))
    conn.execute("DELETE FROM first_touch_capture_block_status WHERE capture_id=?", (capture_id,))
    conn.execute("DELETE FROM first_touch_gate_evaluations WHERE capture_id=?", (capture_id,))

    path_values: dict[str, Any] = {}
    for ordinal, (path, parent, key_name, array_index, value) in enumerate(nodes, start=1):
        path_values[path] = value
        conn.execute(
            "INSERT INTO first_touch_capture_nodes(capture_id,node_ordinal,json_path,parent_path,key_name,array_index,value_type,is_terminal,value_json) VALUES(?,?,?,?,?,?,?,?,?)",
            (capture_id, ordinal, path, parent, key_name, array_index, value_type(value), int(not isinstance(value, (dict, list))), jdump(value)),
        )

    for ordinal, attempt in enumerate(attempts, start=1):
        conn.execute(
            "INSERT INTO first_touch_capture_api_attempts(capture_id,attempt_ordinal,name,url,http_status,response_json) VALUES(?,?,?,?,?,?)",
            (capture_id, ordinal, attempt.get("name"), attempt.get("url"), attempt.get("http_status"), jdump(attempt.get("response"))),
        )

    rules = sorted(catalog["rules"], key=lambda item: item["priority"])
    block_paths: dict[str, set[str]] = {block["block_id"]: set() for block in catalog["blocks"]}
    block_terminal_paths: dict[str, set[str]] = {block["block_id"]: set() for block in catalog["blocks"]}

    for path, _, _, _, value in nodes:
        for rule in rules:
            if _rule_matches(path, rule):
                conn.execute(
                    "INSERT OR IGNORE INTO first_touch_field_block_membership(capture_id,json_path,block_id,rule_id,usage_purpose) VALUES(?,?,?,?,?)",
                    (capture_id, path, rule["block_id"], rule["rule_id"], rule["usage_purpose"]),
                )
                block_paths[rule["block_id"]].add(path)
                if not isinstance(value, (dict, list)):
                    block_terminal_paths[rule["block_id"]].add(path)

    # Every path must be represented by the fallback raw/provenance block.
    unmapped = conn.execute(
        "SELECT COUNT(*) FROM first_touch_capture_nodes n WHERE n.capture_id=? AND NOT EXISTS ("
        "SELECT 1 FROM first_touch_field_block_membership m WHERE m.capture_id=n.capture_id AND m.json_path=n.json_path)",
        (capture_id,),
    ).fetchone()[0]
    if unmapped:
        raise ValueError(f"capture contains {unmapped} nodes without any block membership")

    negative_markers = ("UNAVAILABLE", "UNKNOWN", "NOT_EXPOSED", "NOT PROVEN", "NOT_ACCESSIBLE", "REDACTED_VALUE")
    for block in catalog["blocks"]:
        block_id = block["block_id"]
        paths = block_paths[block_id]
        terminals = block_terminal_paths[block_id]
        if not paths:
            status = "EMPTY"
        else:
            values = [path_values[p] for p in terminals]
            if values and all(any(marker in str(v).upper() for marker in negative_markers) for v in values):
                status = "UNAVAILABLE"
            elif block_id == "B00":
                status = "VERIFIED"
            elif len(terminals) >= 2:
                status = "SUFFICIENT"
            else:
                status = "PRESENT"
        evidence = {
            "paths": sorted(paths),
            "terminal_paths": sorted(terminals),
            "authority_granted": False,
            "classification_is_evidence_only": True,
        }
        conn.execute(
            "INSERT INTO first_touch_capture_block_status(capture_id,block_id,status,field_count,terminal_field_count,evidence_json) VALUES(?,?,?,?,?,?)",
            (capture_id, block_id, status, len(paths), len(terminals), jdump(evidence)),
        )

    block_status = {
        row[0]: row[1]
        for row in conn.execute(
            "SELECT block_id,status FROM first_touch_capture_block_status WHERE capture_id=?",
            (capture_id,),
        )
    }
    now = evaluated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    ready_gates = []
    for gate in catalog["gates"]:
        gate_id = gate["gate_id"]
        missing = []
        satisfied = []
        for block_id, requirement, minimum in catalog["requirements"].get(gate_id, []):
            status = block_status.get(block_id, "EMPTY")
            if requirement == "REQUIRED" and _status_rank(status) < _status_rank(minimum):
                missing.append({"block_id": block_id, "status": status, "minimum_status": minimum})
            else:
                satisfied.append({"block_id": block_id, "status": status, "requirement": requirement})
        if missing:
            status = "EVIDENCE_PARTIAL" if satisfied else "BLOCKED"
        else:
            status = "EVIDENCE_READY_FOR_CANONICAL_VALIDATION"
            ready_gates.append(gate_id)
        conn.execute(
            "INSERT INTO first_touch_gate_evaluations(capture_id,gate_id,status,missing_blocks_json,satisfied_blocks_json,evaluated_at) VALUES(?,?,?,?,?,?)",
            (capture_id, gate_id, status, jdump(missing), jdump(satisfied), now),
        )

    return {
        "capture_id": capture_id,
        "node_count": len(nodes),
        "terminal_value_count": terminal_count,
        "membership_count": conn.execute(
            "SELECT COUNT(*) FROM first_touch_field_block_membership WHERE capture_id=?",
            (capture_id,),
        ).fetchone()[0],
        "ready_for_canonical_validation": ready_gates,
        "authority_granted": False,
    }


def build_capture_database(capture_path: Path, output_path: Path, *, source_ref: str | None = None) -> dict[str, Any]:
    if output_path.exists():
        output_path.unlink()
    capture = json.loads(capture_path.read_text(encoding="utf-8"))
    conn = sqlite3.connect(output_path)
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        install_schema(conn)
        summary = ingest_capture(conn, capture, source_ref=source_ref)
        conn.commit()
        fk = conn.execute("PRAGMA foreign_key_check").fetchall()
        if fk:
            raise ValueError(f"foreign key violations: {fk}")
        terminal = conn.execute(
            "SELECT terminal_value_count FROM first_touch_capture_records WHERE capture_id=?",
            (summary["capture_id"],),
        ).fetchone()[0]
        b00 = conn.execute(
            "SELECT COUNT(DISTINCT json_path) FROM first_touch_field_block_membership WHERE capture_id=? AND block_id='B00'",
            (summary["capture_id"],),
        ).fetchone()[0]
        total = conn.execute(
            "SELECT node_count FROM first_touch_capture_records WHERE capture_id=?",
            (summary["capture_id"],),
        ).fetchone()[0]
        if b00 != total:
            raise ValueError(f"B00 preservation mismatch: {b00} != {total}")
        summary["terminal_value_count"] = terminal
        summary["all_nodes_preserved_in_B00"] = True
        return summary
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize first-touch capture into field/block/gate SQLite")
    parser.add_argument("--capture", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--source-ref")
    args = parser.parse_args()
    summary = build_capture_database(Path(args.capture), Path(args.output), source_ref=args.source_ref)
    print(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
