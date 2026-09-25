#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--initialization-commit-sha", required=True)
    args = p.parse_args()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    receipt_path = ROOT / ".governance" / "bootstrap-receipt.json"
    state_path = ROOT / ".governance" / "bootstrap-state.json"
    memory_path = ROOT / ".governance" / "canonical-memory" / "current.json"

    receipt = read_json(receipt_path)
    state = read_json(state_path)
    memory = read_json(memory_path)

    receipt["initialization_commit_sha"] = args.initialization_commit_sha
    receipt["validation"] = "PASS"
    receipt["attested_at"] = now

    state["status"] = "PASS"
    state["attested_initialization_commit_sha"] = args.initialization_commit_sha
    state["attested_at"] = now

    memory["observed_head_sha"] = args.initialization_commit_sha
    memory["freshness"] = "ATTESTED"
    memory["current_checkpoint"] = "bootstrap"
    memory["canonical_revision"] = max(1, int(memory.get("canonical_revision", 0)))
    memory["work_revision"] = max(1, int(memory.get("work_revision", 0)))

    write_json(receipt_path, receipt)
    write_json(state_path, state)
    write_json(memory_path, memory)

    print(f"BOOTSTRAP_ATTESTATION_PASS: {args.initialization_commit_sha}")


if __name__ == "__main__":
    main()
