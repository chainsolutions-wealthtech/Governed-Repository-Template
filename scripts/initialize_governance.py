#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
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
