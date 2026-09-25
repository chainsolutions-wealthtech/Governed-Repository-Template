#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1]

CRITICAL_MACHINE_PATHS = {
    ".governance/profile.json",
    ".governance/bootstrap-state.json",
    ".governance/canonical-memory/current.json",
    ".governance/sessions/sessions.json",
    ".governance/work/work-items.json",
    ".governance/work/claims.json",
    ".governance/intake/cursor.json",
    ".governance/project-profile.json",
    ".governance/infrastructure-intent.json",
    ".governance/connection-intent-policy.json",
    ".governance/entry-action-policy.json",
    ".governance/repository-scope-policy.json",
}

EXCLUDED = {
    ".template-source",
    ".github/workflows/governance-auto-bootstrap.yml",
    ".github/workflows/governed-control-plane.yml",
    ".github/ISSUE_TEMPLATE/governed-request.yml",
    ".governance/bootstrap-receipt.json",
}


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_git(target: Path, *args: str) -> str:
    cp = subprocess.run(["git", *args], cwd=target, text=True, capture_output=True, check=False)
    if cp.returncode != 0:
        raise SystemExit(f"ADOPTION_FAILED: git {' '.join(args)}: {cp.stderr.strip()}")
    return cp.stdout.strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def template_paths() -> list[str]:
    manifest = json.loads((SOURCE_ROOT / ".governance" / "TEMPLATE_MANIFEST.json").read_text(encoding="utf-8"))
    paths: list[str] = []
    for values in manifest.get("categories", {}).values():
        for relative in values:
            if relative not in EXCLUDED and relative not in paths:
                paths.append(relative)
    for schema in sorted((SOURCE_ROOT / "schemas").glob("*.json")):
        relative = str(schema.relative_to(SOURCE_ROOT))
        if relative not in paths:
            paths.append(relative)

    for relative in [
        ".governance/profile.json",
        ".governance/TEMPLATE_MANIFEST.json",
        "README.md",
        "PROJECT_CONTEXT.md",
        "STATUS.md",
        "SUIVI.md",
        "TODO.md",
        "NEXT_ACTION.md",
        "LOOP_STATE.md",
        "CURRENT_ITERATION.md",
        "WORK_LOG.md",
        "HANDOFF.md",
        "CHANGELOG.md",
        "ACCEPTANCE_CRITERIA.md",
    ]:
        if relative not in paths:
            paths.append(relative)
    return [p for p in paths if (SOURCE_ROOT / p).is_file()]


def render_text(data: bytes, replacements: dict[str, str]) -> bytes:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    for key, value in replacements.items():
        text = text.replace("{{" + key + "}}", value)
    return text.encode("utf-8")


def plan(target: Path, replacements: dict[str, str]) -> dict:
    entries = []
    blockers = []
    for relative in template_paths():
        source = SOURCE_ROOT / relative
        destination = target / relative
        rendered = render_text(source.read_bytes(), replacements)
        if not destination.exists():
            action = "ADD"
        else:
            existing = destination.read_bytes()
            if existing == rendered:
                action = "REUSE"
            elif relative in CRITICAL_MACHINE_PATHS:
                action = "CONFLICT_HOLD_FOR_REVIEW"
                blockers.append(relative)
            else:
                action = "PRESERVE_EXISTING"
        entries.append({
            "path": relative,
            "action": action,
            "source_sha256": sha256(rendered),
            "existing_sha256": sha256(destination.read_bytes()) if destination.is_file() else None,
        })
    return {"entries": entries, "blocking_conflicts": blockers}


def initialize_added_machine_state(target: Path, args: argparse.Namespace, head: str, branch: str, added_files: list[str]) -> None:
    now = utcnow()

    profile_path = target / ".governance" / "profile.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    profile.update({
        "template_source": False,
        "initialized": True,
        "repository": args.repository,
        "project_name": args.project_name or args.repository.split("/", 1)[-1],
        "project_type": args.project_type,
        "owner": args.owner or f"@{args.repository.split('/', 1)[0]}",
        "canonical_branch": branch,
        "initialized_at": now,
        "initialization_mode": "EXISTING_REPOSITORY_ADOPTION",
    })
    profile_path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")

    project_profile_path = target / ".governance" / "project-profile.json"
    project_profile = json.loads(project_profile_path.read_text(encoding="utf-8"))
    project_profile["repository"] = args.repository
    project_profile_path.write_text(json.dumps(project_profile, indent=2) + "\n", encoding="utf-8")

    infra_path = target / ".governance" / "infrastructure-intent.json"
    infra = json.loads(infra_path.read_text(encoding="utf-8"))
    infra["repository"] = args.repository
    infra.setdefault("github_binding", {})["repository"] = args.repository
    infra_path.write_text(json.dumps(infra, indent=2) + "\n", encoding="utf-8")

    scope_path = target / ".governance" / "repository-scope-policy.json"
    scope = json.loads(scope_path.read_text(encoding="utf-8"))
    scope["current_repository_scope"] = args.repository_scope
    scope["target_owner"] = args.repository.split("/", 1)[0]
    scope["target_scope"] = args.repository_scope
    scope_path.write_text(json.dumps(scope, indent=2) + "\n", encoding="utf-8")

    control_plane_path = target / ".governance" / "control-plane-policy.json"
    control_plane = json.loads(control_plane_path.read_text(encoding="utf-8"))
    control_plane["current_role"] = control_plane["client_role_after_instantiation"]
    control_plane["client_repository"] = args.repository
    control_plane_path.write_text(json.dumps(control_plane, indent=2) + "\n", encoding="utf-8")

    local_entry_path = target / ".governance" / "local-entry" / "state.json"
    local_entry = json.loads(local_entry_path.read_text(encoding="utf-8"))
    local_entry.update({
        "repository": args.repository,
        "status": "WAITING_FOR_FIRST_AGENT",
        "first_agent_completed": False,
        "first_agent_session_id": None,
        "baseline_subject_head": None,
        "baseline_completed_at": None,
        "last_local_entry_issue": None,
    })
    local_entry_path.write_text(json.dumps(local_entry, indent=2) + "\n", encoding="utf-8")

    mcp_binding_path = target / ".governance" / "mcp-binding.json"
    mcp_binding = json.loads(mcp_binding_path.read_text(encoding="utf-8"))
    mcp_binding.update({
        "repository": args.repository,
        "linked": False,
        "status": "UNCONFIGURED",
        "transport": None,
        "endpoint": None,
        "ssh_connection_profile": None,
        "credential_names": [],
        "discovery_status": "NOT_RUN",
        "discovery_observed_at": None,
        "domain_strategy": None,
        "domain_binding": None,
        "project_registration_status": "UNKNOWN",
        "write_tools_status": "DISABLED_UNTIL_REGISTERED_AND_AUTHORIZED",
    })
    mcp_binding_path.write_text(json.dumps(mcp_binding, indent=2) + "\n", encoding="utf-8")

    access_plan_path = target / ".governance" / "access-plan.json"
    access_plan = json.loads(access_plan_path.read_text(encoding="utf-8"))
    access_plan["repository"] = args.repository
    access_plan["status"] = "DISCOVERY_REQUIRED"
    access_plan_path.write_text(json.dumps(access_plan, indent=2) + "\n", encoding="utf-8")

    workflow_model_path = target / ".governance" / "workflow-model.json"
    workflow_model = json.loads(workflow_model_path.read_text(encoding="utf-8"))
    workflow_model["repository"] = args.repository
    workflow_model["selected_model"] = None
    workflow_model_path.write_text(json.dumps(workflow_model, indent=2) + "\n", encoding="utf-8")

    bootstrap_path = target / ".governance" / "bootstrap-state.json"
    bootstrap = json.loads(bootstrap_path.read_text(encoding="utf-8"))
    bootstrap.update({
        "status": "ADOPTED_EXISTING_REPOSITORY",
        "initialized": True,
        "repository": args.repository,
        "canonical_branch": branch,
        "bootstrap_revision": 1,
        "last_receipt": ".governance/adoption-receipt.json",
    })
    bootstrap_path.write_text(json.dumps(bootstrap, indent=2) + "\n", encoding="utf-8")

    memory_path = target / ".governance" / "canonical-memory" / "current.json"
    memory = json.loads(memory_path.read_text(encoding="utf-8"))
    memory.update({
        "repository": args.repository,
        "canonical_branch": branch,
        "canonical_revision": 1,
        "work_revision": 1,
        "observed_head_sha": head,
        "current_checkpoint": "adoption",
        "current_handoff": None,
        "next_action": "DISCOVER_PROJECT_BASELINE",
        "blockers": [],
        "freshness": "ADOPTION_ATTESTED",
    })
    memory_path.write_text(json.dumps(memory, indent=2) + "\n", encoding="utf-8")

    work_path = target / ".governance" / "work" / "work-items.json"
    work = json.loads(work_path.read_text(encoding="utf-8"))
    for item in work.get("items", []):
        if item.get("work_item_id") == "WORK-INIT-001":
            item["status"] = "DONE"
        elif item.get("work_item_id") == "WORK-DISCOVER-001":
            item["status"] = "READY"
    work["revision"] = max(int(work.get("revision", 0)), 1)
    work_path.write_text(json.dumps(work, indent=2) + "\n", encoding="utf-8")

    adoption_dir = target / ".governance" / "adoption"
    adoption_dir.mkdir(parents=True, exist_ok=True)
    state = {
        "schema_version": "1.0.0",
        "status": "ADOPTED",
        "repository": args.repository,
        "observed_head_sha": head,
        "canonical_branch": branch,
        "adopted_at": now,
        "non_destructive": True,
        "existing_files_overwritten": 0,
    }
    (adoption_dir / "state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    receipt = {
        "schema_version": "1.0.0",
        "repository": args.repository,
        "observed_head_sha": head,
        "canonical_branch": branch,
        "adopted_at": now,
        "mode": "EXISTING_REPOSITORY_ADOPTION",
        "added_files": sorted(added_files),
        "preservation_contract": "NO_EXISTING_FILE_OVERWRITE",
        "next_action": "DISCOVER_PROJECT_BASELINE",
    }
    (target / ".governance" / "adoption-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Plan or apply additive governance adoption to an existing Git repository.")
    p.add_argument("--target", required=True)
    p.add_argument("--repository", required=True)
    p.add_argument("--project-name")
    p.add_argument("--project-type", default="existing")
    p.add_argument("--owner")
    p.add_argument("--repository-scope", choices=["ORGANIZATION", "PERSONAL_ACCOUNT", "OTHER_AUTHORIZED_OWNER", "OWNER_AGNOSTIC"], default="OWNER_AGNOSTIC")
    p.add_argument("--mode", choices=["plan", "apply"], default="plan")
    p.add_argument("--expected-head")
    args = p.parse_args()

    target = Path(args.target).resolve()
    if not (target / ".git").exists():
        raise SystemExit("ADOPTION_FAILED: target is not a Git repository")

    head = run_git(target, "rev-parse", "HEAD")
    branch = run_git(target, "branch", "--show-current") or "DETACHED"
    replacements = {
        "REPOSITORY": args.repository,
        "PROJECT_NAME": args.project_name or args.repository.split("/", 1)[-1],
        "PROJECT_TYPE": args.project_type,
        "OWNER": args.owner or f"@{args.repository.split('/', 1)[0]}",
        "CANONICAL_BRANCH": branch,
        "INITIALIZED_AT": utcnow(),
    }
    result = plan(target, replacements)
    report = {
        "status": "PLAN",
        "repository": args.repository,
        "target": str(target),
        "observed_head_sha": head,
        "branch": branch,
        **result,
    }

    if args.mode == "plan":
        print(json.dumps(report, indent=2))
        return

    if not args.expected_head:
        raise SystemExit("ADOPTION_FAILED: --expected-head is required in apply mode")
    if args.expected_head != head:
        raise SystemExit(f"ADOPTION_FAILED: HEAD_MOVED expected={args.expected_head} current={head}")
    if run_git(target, "status", "--porcelain"):
        raise SystemExit("ADOPTION_FAILED: target worktree must be clean before additive apply")
    if result["blocking_conflicts"]:
        raise SystemExit("ADOPTION_HOLD_FOR_REVIEW: critical machine conflicts: " + ", ".join(result["blocking_conflicts"]))

    added = []
    for entry in result["entries"]:
        if entry["action"] != "ADD":
            continue
        relative = entry["path"]
        source = SOURCE_ROOT / relative
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(render_text(source.read_bytes(), replacements))
        added.append(relative)

    initialize_added_machine_state(target, args, head, branch, added)
    report.update({
        "status": "APPLIED_ADDITIVELY",
        "added_files": sorted(added),
        "existing_files_overwritten": 0,
        "next_action": "REVIEW_DIFF_VALIDATE_AND_COMMIT_ON_AUTHORIZED_BRANCH",
    })
    adoption_dir = target / ".governance" / "adoption"
    adoption_dir.mkdir(parents=True, exist_ok=True)
    (adoption_dir / "plan.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
