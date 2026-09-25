#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {
    ROOT / "scripts" / "initialize_governance.py",
}

TEXT_SUFFIXES = {".md", ".json", ".yml", ".yaml", ".txt"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Initialize a governed repository created from the Chainsolutions template.")
    p.add_argument("--repository", required=True, help="owner/name")
    p.add_argument("--project-name", required=True)
    p.add_argument("--project-type", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("--canonical-branch", default="main")
    return p.parse_args()


def replace_in_file(path: Path, mapping: dict[str, str]) -> None:
    if path in EXCLUDED or path.suffix not in TEXT_SUFFIXES:
        return
    text = path.read_text(encoding="utf-8")
    new = text
    for key, value in mapping.items():
        new = new.replace(key, value)
    if new != text:
        path.write_text(new, encoding="utf-8")


def main() -> None:
    args = parse_args()
    initialized_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    mapping = {
        "{{REPOSITORY}}": args.repository,
        "{{PROJECT_NAME}}": args.project_name,
        "{{PROJECT_TYPE}}": args.project_type,
        "{{OWNER}}": args.owner,
        "{{CANONICAL_BRANCH}}": args.canonical_branch,
        "{{INITIALIZED_AT}}": initialized_at,
    }

    for path in ROOT.rglob("*"):
        if path.is_file():
            replace_in_file(path, mapping)

    profile_path = ROOT / ".governance" / "profile.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    profile.update({
        "template_source": False,
        "initialized": True,
        "repository": args.repository,
        "project_name": args.project_name,
        "project_type": args.project_type,
        "owner": args.owner,
        "canonical_branch": args.canonical_branch,
        "initialized_at": initialized_at,
    })
    profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _read_json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _head() -> str:
        value = os.getenv("GITHUB_SHA")
        if value:
            return value
        cp = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False)
        return cp.stdout.strip() if cp.returncode == 0 else "UNKNOWN"

    input_head = _head()

    bootstrap_state_path = ROOT / ".governance" / "bootstrap-state.json"
    bootstrap_state = _read_json(bootstrap_state_path)
    bootstrap_state.update({
        "status": "INITIALIZED_PENDING_ATTESTATION",
        "initialized": True,
        "repository": args.repository,
        "canonical_branch": args.canonical_branch,
        "bootstrap_revision": int(bootstrap_state.get("bootstrap_revision", 0)) + 1,
        "last_receipt": ".governance/bootstrap-receipt.json",
    })
    _write_json(bootstrap_state_path, bootstrap_state)

    receipt = {
        "schema_version": "1.0.0",
        "repository": args.repository,
        "project_name": args.project_name,
        "project_type": args.project_type,
        "owner": args.owner,
        "canonical_branch": args.canonical_branch,
        "bootstrap_revision": bootstrap_state["bootstrap_revision"],
        "initialized": True,
        "validation": "PENDING_ATTESTATION",
        "input_head_sha": input_head,
        "initialization_commit_sha": None,
        "template_repository": "chainsolutions-wealthtech/Governed-Repository-Template",
        "template_revision": None,
        "generated_at": initialized_at,
        "next_action": "DISCOVER_PROJECT_BASELINE",
    }
    _write_json(ROOT / ".governance" / "bootstrap-receipt.json", receipt)

    memory_path = ROOT / ".governance" / "canonical-memory" / "current.json"
    memory = _read_json(memory_path)
    memory.update({
        "repository": args.repository,
        "canonical_branch": args.canonical_branch,
        "canonical_revision": max(1, int(memory.get("canonical_revision", 0))),
        "work_revision": max(1, int(memory.get("work_revision", 0))),
        "observed_head_sha": input_head,
        "next_action": "DISCOVER_PROJECT_BASELINE",
        "freshness": "INITIALIZED_PENDING_ATTESTATION",
        "blockers": [],
    })
    _write_json(memory_path, memory)

    work_path = ROOT / ".governance" / "work" / "work-items.json"
    work = _read_json(work_path)
    items = list(work.get("items", []))
    for item in items:
        if item.get("work_item_id") == "WORK-INIT-001":
            item["status"] = "DONE"
    if not any(item.get("work_item_id") == "WORK-DISCOVER-001" for item in items):
        items.append({
            "work_item_id": "WORK-DISCOVER-001",
            "title": "Discover and capture the project baseline",
            "status": "READY",
            "priority": 900,
            "sequence": 2,
            "dependencies": ["WORK-INIT-001"],
            "collision_domains": ["governance-state"],
            "next_action": "DISCOVER_PROJECT_BASELINE",
        })
    work["revision"] = int(work.get("revision", 0)) + 1
    work["items"] = items
    _write_json(work_path, work)

    marker = ROOT / ".template-source"
    if marker.exists():
        marker.unlink()

    unresolved = []
    pattern = re.compile(r"\{\{[A-Z0-9_]+\}\}")
    for path in ROOT.rglob("*"):
        if not path.is_file() or path in EXCLUDED or path.suffix not in TEXT_SUFFIXES:
            continue
        hits = sorted(set(pattern.findall(path.read_text(encoding="utf-8"))))
        if hits:
            unresolved.append((str(path.relative_to(ROOT)), hits))

    if unresolved:
        print("Initialization completed with unresolved placeholders:")
        for path, hits in unresolved:
            print(f"- {path}: {', '.join(hits)}")
        raise SystemExit(2)

    print(f"Governance initialized for {args.repository}")
    print("Next: complete PROJECT_CONTEXT.md, docs/ARCHITECTURE.md, ACCEPTANCE_CRITERIA.md and NEXT_ACTION.md")


if __name__ == "__main__":
    main()
