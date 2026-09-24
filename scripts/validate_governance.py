#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / ".governance" / "profile.json"
TEMPLATE_MARKER = ROOT / ".template-source"

REQUIRED = [
    "00_START_HERE.md",
    "GOVERNANCE.md",
    "AGENTS.md",
    "SOURCE_OF_TRUTH.md",
    "PROJECT_CONTEXT.md",
    "STATUS.md",
    "SUIVI.md",
    "TODO.md",
    "NEXT_ACTION.md",
    "LOOP_STATE.md",
    "CURRENT_ITERATION.md",
    "LOOP_ENGINEERING.md",
    "WORK_LOG.md",
    "HANDOFF.md",
    "CHANGELOG.md",
    "ASSUMPTIONS.md",
    "CONSTRAINTS.md",
    "RISKS.md",
    "DEPENDENCIES.md",
    "ACCEPTANCE_CRITERIA.md",
    "DEFINITION_OF_DONE.md",
    "docs/ARCHITECTURE.md",
    "docs/DECISIONS.md",
    ".governance/profile.json",
    ".governance/TEMPLATE_MANIFEST.json",
    "schemas/project-state.schema.json",
    "schemas/loop-state.schema.json",
    "schemas/next-action.schema.json",
]

FORBIDDEN_POLICY_VALUES = {
    "force_push": {"ALLOWED", "REQUIRED"},
    "history_rewrite": {"ALLOWED", "REQUIRED"},
}

PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def fail(message: str) -> None:
    raise SystemExit(f"GOVERNANCE_VALIDATION_FAILED: {message}")


def main() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        fail("missing required files: " + ", ".join(missing))

    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    policies = profile.get("policies") or {}

    for key, forbidden in FORBIDDEN_POLICY_VALUES.items():
        if policies.get(key) in forbidden:
            fail(f"unsafe policy value: {key}={policies.get(key)}")

    if policies.get("force_push") != "FORBIDDEN":
        fail("force_push must remain FORBIDDEN")
    if policies.get("history_rewrite") != "FORBIDDEN":
        fail("history_rewrite must remain FORBIDDEN")
    if policies.get("zero_regression") != "REQUIRED":
        fail("zero_regression must remain REQUIRED")
    if policies.get("verify_before_write") != "REQUIRED" or policies.get("verify_after_write") != "REQUIRED":
        fail("verification before and after write must remain REQUIRED")

    is_template_source = TEMPLATE_MARKER.exists()
    if is_template_source:
        if profile.get("template_source") is not True:
            fail("template source marker exists but profile.template_source is not true")
        print("GOVERNANCE_VALIDATION_PASS: template source mode")
        return

    if profile.get("template_source") is True:
        fail("instantiated repository still marked as template_source")
    if profile.get("initialized") is not True:
        fail("instantiated repository is not initialized")

    unresolved = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix not in {".md", ".json", ".yml", ".yaml", ".txt"}:
            continue
        hits = sorted(set(PLACEHOLDER.findall(path.read_text(encoding="utf-8", errors="replace"))))
        if hits:
            unresolved.append(f"{path.relative_to(ROOT)}:{','.join(hits)}")
    if unresolved:
        fail("unresolved placeholders: " + " | ".join(unresolved))

    if profile.get("repository") in {None, "", "TO_INITIALIZE"}:
        fail("repository not initialized")
    if profile.get("canonical_branch") in {None, "", "TO_INITIALIZE"}:
        fail("canonical_branch not initialized")

    print("GOVERNANCE_VALIDATION_PASS: instantiated repository mode")


if __name__ == "__main__":
    main()
