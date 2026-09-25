#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_REPOSITORY = "chainsolutions-wealthtech/Governed-Repository-Template"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git_head() -> str:
    cp = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False)
    return cp.stdout.strip() if cp.returncode == 0 else "UNKNOWN"


def args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repository")
    p.add_argument("--project-name")
    p.add_argument("--project-type")
    p.add_argument("--project-profile", choices=["generic","application","chainsolutions-fullstack-web","data-platform"])
    p.add_argument("--repository-scope", choices=["ORGANIZATION","PERSONAL_ACCOUNT","OTHER_AUTHORIZED_OWNER","OWNER_AGNOSTIC"])
    p.add_argument("--owner")
    p.add_argument("--canonical-branch")
    return p.parse_args()


def main() -> None:
    a = args()
    repository = a.repository or os.getenv("GITHUB_REPOSITORY")
    if not repository or "/" not in repository:
        raise SystemExit("AUTO_BOOTSTRAP_FAILED: repository is unavailable")
    if repository == TEMPLATE_REPOSITORY:
        print("AUTO_BOOTSTRAP_SKIPPED: template repository is immutable source mode")
        return

    org, repo_name = repository.split("/", 1)
    project_name = a.project_name or os.getenv("GOVERNANCE_PROJECT_NAME") or repo_name
    project_type = a.project_type or os.getenv("GOVERNANCE_PROJECT_TYPE") or "generic"
    owner = a.owner or os.getenv("GOVERNANCE_OWNER") or f"@{org}"
    project_profile = a.project_profile or os.getenv("GOVERNANCE_PROJECT_PROFILE")
    repository_scope = a.repository_scope or os.getenv("GOVERNANCE_REPOSITORY_SCOPE") or "OWNER_AGNOSTIC"
    canonical_branch = (
        a.canonical_branch
        or os.getenv("GOVERNANCE_CANONICAL_BRANCH")
        or os.getenv("GITHUB_REF_NAME")
        or "main"
    )
    input_head = os.getenv("GITHUB_SHA") or git_head()
    initialized_at = now()

    marker = ROOT / ".template-source"
    profile_path = ROOT / ".governance" / "profile.json"
    profile = read_json(profile_path)

    if marker.exists():
        cp = subprocess.run([
            sys.executable,
            str(ROOT / "scripts" / "initialize_governance.py"),
            "--repository", repository,
            "--project-name", project_name,
            "--project-type", project_type,
            *(["--project-profile", project_profile] if project_profile else []),
            "--repository-scope", repository_scope,
            "--owner", owner,
            "--canonical-branch", canonical_branch,
        ], cwd=ROOT, check=False)
        if cp.returncode != 0:
            raise SystemExit(cp.returncode)
        profile = read_json(profile_path)
    elif profile.get("initialized") is True:
        print("AUTO_BOOTSTRAP_IDEMPOTENT: repository already initialized")
        return
    else:
        raise SystemExit("AUTO_BOOTSTRAP_FAILED: no template marker and profile is not initialized")

    state_path = ROOT / ".governance" / "bootstrap-state.json"
    state = read_json(state_path)
    revision = max(1, int(state.get("bootstrap_revision", 0)))

    receipt = {
        "schema_version": "1.0.0",
        "repository": repository,
        "project_name": project_name,
        "project_type": project_type,
        "owner": owner,
        "canonical_branch": canonical_branch,
        "bootstrap_revision": revision,
        "initialized": True,
        "validation": "PENDING",
        "input_head_sha": input_head,
        "initialization_commit_sha": None,
        "template_repository": TEMPLATE_REPOSITORY,
        "template_revision": read_json(ROOT / ".governance" / "TEMPLATE_MANIFEST.json").get("template_version") or os.getenv("GOVERNANCE_TEMPLATE_REVISION"),
        "github_run_id": os.getenv("GITHUB_RUN_ID"),
        "generated_at": initialized_at,
        "next_action": "DISCOVER_PROJECT_BASELINE",
    }
    receipt_path = ROOT / ".governance" / "bootstrap-receipt.json"
    write_json(receipt_path, receipt)

    state.update({
        "status": "INITIALIZED_PENDING_ATTESTATION",
        "initialized": True,
        "repository": repository,
        "canonical_branch": canonical_branch,
        "bootstrap_revision": revision,
        "last_receipt": str(receipt_path.relative_to(ROOT)),
    })
    write_json(state_path, state)

    memory_path = ROOT / ".governance" / "canonical-memory" / "current.json"
    memory = read_json(memory_path)
    memory.update({
        "repository": repository,
        "canonical_branch": canonical_branch,
        "canonical_revision": max(1, int(memory.get("canonical_revision", 0))),
        "work_revision": max(1, int(memory.get("work_revision", 0))),
        "observed_head_sha": input_head,
        "next_action": "DISCOVER_PROJECT_BASELINE",
        "freshness": "INITIALIZED_PENDING_ATTESTATION",
        "blockers": [],
    })
    write_json(memory_path, memory)

    work_path = ROOT / ".governance" / "work" / "work-items.json"
    work = read_json(work_path)
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
    write_json(work_path, work)

    (ROOT / "NEXT_ACTION.md").write_text(
        "# NEXT_ACTION — Point de reprise unique\n\n"
        "```text\nNEXT_ACTION = DISCOVER_PROJECT_BASELINE\nSTATE = READY\n```\n\n"
        "## Action\n\n"
        "Lire les autorités du dépôt, observer le HEAD exact, inventorier l'existant, résoudre ou différer explicitement le profil technique, découvrir l'état de l'infrastructure sans rien inventer, puis capturer une baseline avant tout travail fonctionnel.\n\n"
        "## Done when\n\n"
        "- profil projet sélectionné ou explicitement laissé en découverte ;\n"
        "- serveur, domaine, répertoire et base observés ou explicitement laissés non résolus ;\n"
        "- voie d'accès serveur classée DIRECT_MCP, SSH fallback ou indisponible ;\n"
        "- contexte projet complété ;\n"
        "- architecture initiale décrite ;\n"
        "- baseline HEAD/CI enregistrée ;\n"
        "- risques et dépendances initiaux enregistrés ;\n"
        "- première action fonctionnelle unique définie.\n",
        encoding="utf-8",
    )
    (ROOT / "STATUS.md").write_text(
        "# STATUS — État courant\n\n"
        "> State: `GOVERNANCE_INITIALIZED_BASELINE_REQUIRED`\n\n"
        f"- Repository: `{repository}`\n"
        f"- Branch: `{canonical_branch}`\n"
        f"- Bootstrap input HEAD: `{input_head}`\n"
        "- Governance validation: `PENDING_ATTESTATION`\n"
        "- Next action: `DISCOVER_PROJECT_BASELINE`\n\n"
        "No production, deployment, compliance, legal, financial or operational status is implied.\n",
        encoding="utf-8",
    )
    (ROOT / "HANDOFF.md").write_text(
        "# HANDOFF — Reprise inter-agent\n\n"
        f"- Repository: `{repository}`\n"
        f"- Branch: `{canonical_branch}`\n"
        f"- Bootstrap input HEAD: `{input_head}`\n"
        "- Current work item: `WORK-DISCOVER-001`\n"
        "- Next action: `DISCOVER_PROJECT_BASELINE`\n\n"
        "Before any write: reobserve the exact online HEAD. If it moved, reconcile intervening work first.\n",
        encoding="utf-8",
    )

    cp = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_governance.py")], cwd=ROOT, check=False)
    if cp.returncode != 0:
        raise SystemExit(cp.returncode)

    receipt["validation"] = "PASS"
    write_json(receipt_path, receipt)
    print(f"AUTO_BOOTSTRAP_PASS: {repository} -> DISCOVER_PROJECT_BASELINE")


if __name__ == "__main__":
    main()
