#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / ".governance"
PROFILE = GOV / "profile.json"
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
    "docs/AUTOMATION.md",
    "docs/MULTI_AGENT_COORDINATION.md",
    "docs/INFORMATION_INTAKE.md",
    ".governance/profile.json",
    ".governance/TEMPLATE_MANIFEST.json",
    ".governance/bootstrap-state.json",
    ".governance/canonical-memory/current.json",
    ".governance/work/work-items.json",
    ".governance/work/claims.json",
    ".governance/sessions/sessions.json",
    ".governance/intake/cursor.json",
    "schemas/project-state.schema.json",
    "schemas/loop-state.schema.json",
    "schemas/next-action.schema.json",
    "schemas/bootstrap-receipt.schema.json",
    "schemas/session.schema.json",
    "schemas/work-item.schema.json",
    "schemas/work-claim.schema.json",
    "schemas/session-checkpoint.schema.json",
    "schemas/session-handoff.schema.json",
    "schemas/intake.schema.json",
    "scripts/initialize_governance.py",
    "scripts/auto_bootstrap.py",
    "scripts/finalize_bootstrap.py",
    "scripts/governance_agent.py",
    ".github/workflows/governance-ci.yml",
    ".github/workflows/governance-auto-bootstrap.yml",
]

PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def fail(message: str) -> None:
    raise SystemExit(f"GOVERNANCE_VALIDATION_FAILED: {message}")


def load(path: str) -> dict:
    try:
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {path}: {exc}")


def validate_policies(profile: dict) -> None:
    policies = profile.get("policies") or {}
    exact = {
        "force_push": "FORBIDDEN",
        "history_rewrite": "FORBIDDEN",
        "zero_regression": "REQUIRED",
        "verify_before_write": "REQUIRED",
        "verify_after_write": "REQUIRED",
        "observed_state_ne_assumed_state": "REQUIRED",
        "head_moved_reconciliation": "REQUIRED",
        "single_writer_per_collision_domain": "REQUIRED",
        "unknown_provider_identity": "NULL_NEVER_INVENT",
        "intake_ne_canonical_memory": "REQUIRED",
        "intake_ne_work_item": "REQUIRED",
        "contradiction": "HOLD_FOR_REVIEW",
        "automation_fail_closed": "REQUIRED",
        "runtime_authority_inference": "FORBIDDEN",
    }
    for key, expected in exact.items():
        if policies.get(key) != expected:
            fail(f"policy {key} must be {expected}, got {policies.get(key)!r}")


def validate_machine_state(profile: dict, template_mode: bool) -> None:
    bootstrap = load(".governance/bootstrap-state.json")
    memory = load(".governance/canonical-memory/current.json")
    work = load(".governance/work/work-items.json")
    claims = load(".governance/work/claims.json")
    sessions = load(".governance/sessions/sessions.json")
    cursor = load(".governance/intake/cursor.json")

    if not isinstance(work.get("items"), list):
        fail("work-items.json items must be an array")
    if not isinstance(claims.get("claims"), list):
        fail("claims.json claims must be an array")
    if not isinstance(sessions.get("sessions"), list):
        fail("sessions.json sessions must be an array")
    if not isinstance(cursor.get("pending_intake_ids"), list):
        fail("intake cursor pending_intake_ids must be an array")

    ids = [item.get("work_item_id") for item in work["items"]]
    if len(ids) != len(set(ids)):
        fail("duplicate work item id")

    active_claim_domains: dict[str, str] = {}
    known_items = set(ids)
    for claim in claims["claims"]:
        if claim.get("work_item_id") not in known_items:
            fail(f"claim references unknown work item {claim.get('work_item_id')}")
        if claim.get("status") == "ACTIVE":
            for domain in claim.get("collision_domains", []):
                previous = active_claim_domains.get(domain)
                if previous and previous != claim.get("session_id"):
                    fail(f"collision domain {domain} has multiple active writers")
                active_claim_domains[domain] = claim.get("session_id")

    if int(cursor.get("reconciled_through_sequence", 0)) > int(cursor.get("latest_sequence", 0)):
        fail("intake reconciled sequence exceeds latest sequence")

    if template_mode:
        if bootstrap.get("status") != "TEMPLATE_SOURCE" or bootstrap.get("initialized") is not False:
            fail("template bootstrap state must remain TEMPLATE_SOURCE/uninitialized")
        if memory.get("freshness") != "TEMPLATE_SOURCE":
            fail("template canonical memory must remain TEMPLATE_SOURCE")
        return

    if bootstrap.get("initialized") is not True:
        fail("instantiated bootstrap state is not initialized")

    receipt_path = ROOT / ".governance" / "bootstrap-receipt.json"
    if not receipt_path.exists():
        fail("instantiated repository is missing bootstrap receipt")
    receipt = load(".governance/bootstrap-receipt.json")
    if receipt.get("repository") != profile.get("repository"):
        fail("bootstrap receipt repository does not match profile")
    if receipt.get("initialized") is not True:
        fail("bootstrap receipt is not initialized")

    if memory.get("repository") != profile.get("repository"):
        fail("canonical memory repository does not match profile")
    if memory.get("canonical_branch") != profile.get("canonical_branch"):
        fail("canonical memory branch does not match profile")
    if int(memory.get("canonical_revision", 0)) < 1:
        fail("canonical revision must be >= 1 after initialization")
    if int(memory.get("work_revision", 0)) < 1:
        fail("work revision must be >= 1 after initialization")
    if not memory.get("next_action"):
        fail("canonical memory next_action is required")


def validate_placeholders() -> None:
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


def validate_python_automation() -> None:
    for relative in [
        "scripts/initialize_governance.py",
        "scripts/auto_bootstrap.py",
        "scripts/finalize_bootstrap.py",
        "scripts/governance_agent.py",
        "scripts/validate_governance.py",
    ]:
        path = ROOT / relative
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except SyntaxError as exc:
            fail(f"invalid Python automation {relative}: {exc}")


def main() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        fail("missing required files: " + ", ".join(missing))

    profile = load(".governance/profile.json")
    validate_policies(profile)
    validate_python_automation()

    template_mode = TEMPLATE_MARKER.exists()
    if template_mode:
        if profile.get("template_source") is not True:
            fail("template source marker exists but profile.template_source is not true")
        if profile.get("initialized") is not False:
            fail("template source must not be initialized")
        validate_machine_state(profile, True)
        print("GOVERNANCE_VALIDATION_PASS: template source mode v2")
        return

    if profile.get("template_source") is True:
        fail("instantiated repository still marked as template_source")
    if profile.get("initialized") is not True:
        fail("instantiated repository is not initialized")
    if profile.get("repository") in {None, "", "TO_INITIALIZE"}:
        fail("repository not initialized")
    if profile.get("canonical_branch") in {None, "", "TO_INITIALIZE"}:
        fail("canonical_branch not initialized")

    validate_placeholders()
    validate_machine_state(profile, False)
    print("GOVERNANCE_VALIDATION_PASS: instantiated repository mode v2")


if __name__ == "__main__":
    main()
