#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
    "docs/PROJECT_PROFILES.md",
    "docs/INFRASTRUCTURE_BOOTSTRAP.md",
    "docs/CONNECTION_INTENT.md",
    ".governance/profile.json",
    ".governance/TEMPLATE_MANIFEST.json",
    ".governance/bootstrap-state.json",
    ".governance/canonical-memory/current.json",
    ".governance/work/work-items.json",
    ".governance/work/claims.json",
    ".governance/sessions/sessions.json",
    ".governance/intake/cursor.json",
    ".governance/project-profile.json",
    ".governance/infrastructure-intent.json",
    ".governance/connection-intent-policy.json",
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
    "schemas/project-profile.schema.json",
    "schemas/infrastructure-intent.schema.json",
    "schemas/connection-intent.schema.json",
    "scripts/initialize_governance.py",
    "scripts/auto_bootstrap.py",
    "scripts/finalize_bootstrap.py",
    "scripts/governance_agent.py",
    "scripts/validate_governance.py",
    "scripts/test_bootstrap_consistency.py",
    "scripts/test_connection_intent.py",
    ".github/workflows/governance-ci.yml",
    ".github/workflows/governance-auto-bootstrap.yml",
]

PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
ATTESTATION_MODEL = "CHILD_COMMIT_ATTESTS_INITIALIZATION_COMMIT"
CONNECTION_INTENTS = {
    "OBSERVE",
    "CONTEXT_INTAKE",
    "INFORMATION_INTAKE",
    "WORK_REQUEST",
    "CODE_CHANGE",
    "REVIEW",
    "INFRASTRUCTURE",
    "UNKNOWN",
}
MUTABLE_INTENTS = {"WORK_REQUEST", "CODE_CHANGE", "INFRASTRUCTURE"}


def fail(message: str) -> None:
    raise SystemExit(f"GOVERNANCE_VALIDATION_FAILED: {message}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--bootstrap-attestation",
        action="store_true",
        help="Require the strict bootstrap-finalization invariants used by the zero-touch workflow.",
    )
    return p.parse_args()


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
        "planned_ne_implemented": "REQUIRED",
        "infrastructure_facts_require_observation": "REQUIRED",
        "credentials_in_repository": "FORBIDDEN",
        "connection_intent_fail_closed": "REQUIRED",
        "context_intake_ne_code_permission": "REQUIRED",
        "intent_ne_authority": "REQUIRED",
    }
    for key, expected in exact.items():
        if policies.get(key) != expected:
            fail(f"policy {key} must be {expected}, got {policies.get(key)!r}")


def validate_project_and_connection_intent(profile: dict, template_mode: bool) -> None:
    project_profile = load(".governance/project-profile.json")
    infrastructure = load(".governance/infrastructure-intent.json")
    intent_policy = load(".governance/connection-intent-policy.json")
    sessions = load(".governance/sessions/sessions.json")

    if project_profile.get("selection_status") not in {"DISCOVERY_REQUIRED", "SELECTED", "HOLD_FOR_REVIEW"}:
        fail("invalid project-profile selection_status")
    selected = project_profile.get("selected_profile")
    profiles = project_profile.get("profiles") or {}
    if selected is not None and selected not in profiles:
        fail("selected project profile is not defined")
    if project_profile.get("organization_default_candidate") not in profiles:
        fail("organization default candidate is not defined")
    candidate = profiles.get("chainsolutions-fullstack-web") or {}
    stack = candidate.get("planned_stack") or {}
    if stack.get("backend", {}).get("runtime") != "Node.js":
        fail("Chainsolutions fullstack candidate must plan Node.js runtime")
    if stack.get("frontend", {}).get("framework") != "Next.js":
        fail("Chainsolutions fullstack candidate must plan Next.js frontend")
    if stack.get("database", {}).get("engine") != "PostgreSQL":
        fail("Chainsolutions fullstack candidate must plan PostgreSQL")
    if stack.get("backend", {}).get("status") != "PLANNED":
        fail("planned backend must not be represented as implemented")

    if infrastructure.get("server_access", {}).get("preferred") != "DIRECT_MCP":
        fail("direct MCP must be preferred server transport")
    if infrastructure.get("server_access", {}).get("fallback") != "SSH":
        fail("SSH must remain the governed fallback transport")
    if infrastructure.get("server_access", {}).get("credentials_in_repository") != "FORBIDDEN":
        fail("infrastructure intent must forbid repository credentials")
    if infrastructure.get("deployment_target", {}).get("provisioning_if_missing") != "PLANNED_REQUIRES_AUTHORITY":
        fail("missing deployment resources must require authority before provisioning")

    intents = intent_policy.get("intents") or {}
    if set(intents) != CONNECTION_INTENTS:
        fail("connection intent policy does not define the complete intent set")
    for name, rule in intents.items():
        expected_mutable = name in MUTABLE_INTENTS
        if bool(rule.get("may_dispatch_mutable_work")) != expected_mutable:
            fail(f"connection intent {name} mutable dispatch policy is invalid")
    if intents["UNKNOWN"].get("route") != "RESOLVE_CONNECTION_INTENT":
        fail("UNKNOWN connection intent must fail closed")
    if intents["CONTEXT_INTAKE"].get("may_dispatch_mutable_work") is not False:
        fail("context intake must never imply code permission")
    if intents["INFORMATION_INTAKE"].get("may_dispatch_mutable_work") is not False:
        fail("information intake must never imply code permission")

    for session in sessions.get("sessions", []):
        intent = session.get("connection_intent")
        if intent not in CONNECTION_INTENTS:
            fail(f"session has invalid connection intent {intent!r}")
        provenance = session.get("connection_intent_provenance")
        if provenance not in {"PROVIDED_BY_CLIENT", "DEFAULT_UNKNOWN"}:
            fail("session connection intent provenance is invalid")

    if not template_mode:
        repository = profile.get("repository")
        if project_profile.get("repository") != repository:
            fail("project profile repository does not match governance profile")
        if infrastructure.get("repository") != repository:
            fail("infrastructure intent repository does not match governance profile")
        if infrastructure.get("github_binding", {}).get("repository") != repository:
            fail("infrastructure GitHub binding does not match governance profile")


def validate_machine_state(profile: dict, template_mode: bool, require_bootstrap_attestation: bool = False) -> None:
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

    bootstrap_status = bootstrap.get("status")
    if bootstrap_status not in {"INITIALIZED_PENDING_ATTESTATION", "PASS"}:
        fail(f"unexpected instantiated bootstrap status {bootstrap_status!r}")

    if require_bootstrap_attestation:
        if bootstrap_status != "PASS":
            fail("strict bootstrap attestation requires bootstrap status PASS")
        initialization_sha = receipt.get("initialization_commit_sha")
        if not isinstance(initialization_sha, str) or not SHA40.fullmatch(initialization_sha):
            fail("strict bootstrap attestation requires a valid initialization_commit_sha")
        if receipt.get("validation") != "PASS":
            fail("strict bootstrap attestation requires receipt validation PASS")
        if receipt.get("attestation_subject_sha") != initialization_sha:
            fail("receipt attestation subject does not match initialization commit")
        if receipt.get("attestation_model") != ATTESTATION_MODEL:
            fail("receipt attestation model is invalid")
        if bootstrap.get("attested_initialization_commit_sha") != initialization_sha:
            fail("bootstrap-state attested initialization commit does not match receipt")
        if bootstrap.get("attestation_subject_sha") != initialization_sha:
            fail("bootstrap-state attestation subject does not match receipt")
        if bootstrap.get("attestation_model") != ATTESTATION_MODEL:
            fail("bootstrap-state attestation model is invalid")
        if memory.get("bootstrap_attestation_subject_sha") != initialization_sha:
            fail("canonical memory bootstrap attestation subject does not match receipt")
        if memory.get("attestation_model") != ATTESTATION_MODEL:
            fail("canonical memory attestation model is invalid")
        if memory.get("freshness") != "ATTESTED":
            fail("strict bootstrap attestation requires canonical memory freshness ATTESTED")
        if memory.get("current_checkpoint") != "bootstrap":
            fail("strict bootstrap attestation requires bootstrap checkpoint")

        status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
        required_status_fragments = [
            "> State: `GOVERNANCE_INITIALIZED_BASELINE_REQUIRED`",
            f"- Repository: `{profile.get('repository')}`",
            f"- Branch: `{profile.get('canonical_branch')}`",
            f"- Attested initialization commit: `{initialization_sha}`",
            "- Governance validation: `PASS`",
            "- Governance freshness: `ATTESTED`",
            f"- Next action: `{memory.get('next_action')}`",
        ]
        missing_status = [fragment for fragment in required_status_fragments if fragment not in status]
        if missing_status:
            fail("STATUS.md is not synchronized with bootstrap attestation: " + " | ".join(missing_status))

        next_action = (ROOT / "NEXT_ACTION.md").read_text(encoding="utf-8")
        expected_next_action = f"NEXT_ACTION = {memory.get('next_action')}"
        if expected_next_action not in next_action:
            fail("NEXT_ACTION.md does not match canonical memory after bootstrap attestation")

        loop_state = (ROOT / "LOOP_STATE.md").read_text(encoding="utf-8")
        required_loop_fragments = [
            f'"repository": "{profile.get("repository")}"',
            f'"canonical_branch": "{profile.get("canonical_branch")}"',
            f'"next_action": "{memory.get("next_action")}"',
            '"last_verification": "GOVERNANCE_BOOTSTRAP_ATTESTED"',
        ]
        missing_loop = [fragment for fragment in required_loop_fragments if fragment not in loop_state]
        if missing_loop:
            fail("LOOP_STATE.md is not synchronized with bootstrap attestation: " + " | ".join(missing_loop))

        work_log = (ROOT / "WORK_LOG.md").read_text(encoding="utf-8")
        if "- Result: `PASS`" not in work_log or "- Bootstrap attestation: `PASS`" not in work_log:
            fail("WORK_LOG.md does not record successful bootstrap attestation")

        suivi = (ROOT / "SUIVI.md").read_text(encoding="utf-8")
        required_suivi_fragments = [
            "- State: `GOVERNANCE_INITIALIZED_BASELINE_REQUIRED`",
            "- Bootstrap attestation: `PASS`",
            "- Next action: `DISCOVER_PROJECT_BASELINE`",
        ]
        missing_suivi = [fragment for fragment in required_suivi_fragments if fragment not in suivi]
        if missing_suivi:
            fail("SUIVI.md is not synchronized with bootstrap attestation: " + " | ".join(missing_suivi))

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
        "scripts/test_bootstrap_consistency.py",
        "scripts/test_connection_intent.py",
    ]:
        path = ROOT / relative
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except SyntaxError as exc:
            fail(f"invalid Python automation {relative}: {exc}")


def main() -> None:
    args = parse_args()
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
        validate_project_and_connection_intent(profile, True)
        validate_machine_state(profile, True, args.bootstrap_attestation)
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
    validate_project_and_connection_intent(profile, False)
    validate_machine_state(profile, False, args.bootstrap_attestation)
    print("GOVERNANCE_VALIDATION_PASS: instantiated repository mode v2")


if __name__ == "__main__":
    main()
