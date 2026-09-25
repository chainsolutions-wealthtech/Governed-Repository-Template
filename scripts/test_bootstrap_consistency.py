#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_REPOSITORY = "chainsolutions-wealthtech/governance-template-selftest"
INPUT_HEAD = "1" * 40
INITIALIZATION_HEAD = "2" * 40


def run(repo: Path, *args: str, env: dict[str, str]) -> None:
    subprocess.run([sys.executable, *args], cwd=repo, env=env, check=True)


def read_json(repo: Path, relative: str) -> dict:
    return json.loads((repo / relative).read_text(encoding="utf-8"))


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="governance-bootstrap-selftest-") as tmp:
        target = Path(tmp) / "repo"
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )

        # Build an explicit template-source fixture so this self-test is portable
        # when executed from either the central template or an instantiated repository.
        (target / ".template-source").write_text("SELFTEST_TEMPLATE_SOURCE\n", encoding="utf-8")

        profile_path = target / ".governance" / "profile.json"
        profile = read_json(target, ".governance/profile.json")
        profile.update({
            "template_source": True,
            "initialized": False,
            "repository": "TO_INITIALIZE",
            "project_name": "TO_INITIALIZE",
            "project_type": "TO_INITIALIZE",
            "owner": "TO_INITIALIZE",
            "canonical_branch": "main",
            "initialized_at": None,
            "initialization_mode": "TEMPLATE_BOOTSTRAP",
        })
        profile_path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")

        local_entry_path = target / ".governance" / "local-entry" / "state.json"
        local_entry = read_json(target, ".governance/local-entry/state.json")
        local_entry.update({
            "repository": "{{REPOSITORY}}",
            "status": "WAITING_FOR_FIRST_AGENT",
            "first_agent_completed": False,
            "first_agent_session_id": None,
            "baseline_subject_head": None,
            "baseline_completed_at": None,
            "last_local_entry_issue": None,
        })
        local_entry_path.write_text(json.dumps(local_entry, indent=2) + "\n", encoding="utf-8")

        env = os.environ.copy()
        env.update({
            "GITHUB_REPOSITORY": TEST_REPOSITORY,
            "GITHUB_REF_NAME": "main",
            "GITHUB_SHA": INPUT_HEAD,
            "GITHUB_RUN_ID": "SELFTEST",
        })

        run(target, "scripts/auto_bootstrap.py", env=env)
        if (target / ".template-source").exists():
            raise SystemExit("SELFTEST_FAILED: template marker survived auto bootstrap")

        run(
            target,
            "scripts/finalize_bootstrap.py",
            "--initialization-commit-sha",
            INITIALIZATION_HEAD,
            env=env,
        )
        run(target, "scripts/validate_governance.py", "--bootstrap-attestation", env=env)

        receipt = read_json(target, ".governance/bootstrap-receipt.json")
        state = read_json(target, ".governance/bootstrap-state.json")
        memory = read_json(target, ".governance/canonical-memory/current.json")
        status = (target / "STATUS.md").read_text(encoding="utf-8")
        loop_state = (target / "LOOP_STATE.md").read_text(encoding="utf-8")
        work_log = (target / "WORK_LOG.md").read_text(encoding="utf-8")
        suivi = (target / "SUIVI.md").read_text(encoding="utf-8")
        project_profile = read_json(target, ".governance/project-profile.json")
        infrastructure = read_json(target, ".governance/infrastructure-intent.json")
        intent_policy = read_json(target, ".governance/connection-intent-policy.json")

        checks = {
            "receipt_validation": receipt.get("validation") == "PASS",
            "receipt_subject": receipt.get("attestation_subject_sha") == INITIALIZATION_HEAD,
            "bootstrap_status": state.get("status") == "PASS",
            "bootstrap_subject": state.get("attestation_subject_sha") == INITIALIZATION_HEAD,
            "memory_freshness": memory.get("freshness") == "ATTESTED",
            "memory_subject": memory.get("bootstrap_attestation_subject_sha") == INITIALIZATION_HEAD,
            "status_validation": "- Governance validation: `PASS`" in status,
            "status_freshness": "- Governance freshness: `ATTESTED`" in status,
            "status_subject": f"- Attested initialization commit: `{INITIALIZATION_HEAD}`" in status,
            "loop_next_action": '"next_action": "DISCOVER_PROJECT_BASELINE"' in loop_state,
            "loop_attested": '"last_verification": "GOVERNANCE_BOOTSTRAP_ATTESTED"' in loop_state,
            "work_log_pass": "- Result: `PASS`" in work_log,
            "work_log_attested": "- Bootstrap attestation: `PASS`" in work_log,
            "suivi_state": "- State: `GOVERNANCE_INITIALIZED_BASELINE_REQUIRED`" in suivi,
            "suivi_attested": "- Bootstrap attestation: `PASS`" in suivi,
            "project_profile_repo": project_profile.get("repository") == TEST_REPOSITORY,
            "project_profile_discovery": project_profile.get("selection_status") == "DISCOVERY_REQUIRED",
            "project_profile_candidate": project_profile.get("organization_default_candidate") == "chainsolutions-fullstack-web",
            "planned_node": project_profile.get("profiles", {}).get("chainsolutions-fullstack-web", {}).get("planned_stack", {}).get("backend", {}).get("runtime") == "Node.js",
            "planned_next": project_profile.get("profiles", {}).get("chainsolutions-fullstack-web", {}).get("planned_stack", {}).get("frontend", {}).get("framework") == "Next.js",
            "planned_postgres": project_profile.get("profiles", {}).get("chainsolutions-fullstack-web", {}).get("planned_stack", {}).get("database", {}).get("engine") == "PostgreSQL",
            "infrastructure_repo": infrastructure.get("repository") == TEST_REPOSITORY,
            "infrastructure_unprovisioned": infrastructure.get("status") == "PLANNED_NOT_PROVISIONED",
            "server_discovery": infrastructure.get("deployment_target", {}).get("server_status") == "DISCOVERY_REQUIRED",
            "directory_discovery": infrastructure.get("deployment_target", {}).get("directory_status") == "DISCOVERY_REQUIRED",
            "direct_mcp": infrastructure.get("server_access", {}).get("preferred") == "DIRECT_MCP",
            "ssh_fallback": infrastructure.get("server_access", {}).get("fallback") == "SSH",
            "no_repo_credentials": infrastructure.get("server_access", {}).get("credentials_in_repository") == "FORBIDDEN",
            "unknown_intent_closed": intent_policy.get("intents", {}).get("UNKNOWN", {}).get("may_dispatch_mutable_work") is False,
            "information_ne_code": intent_policy.get("intents", {}).get("INFORMATION_INTAKE", {}).get("may_dispatch_mutable_work") is False,
        }
        failed = [name for name, ok in checks.items() if not ok]
        if failed:
            raise SystemExit("SELFTEST_FAILED: " + ", ".join(failed))

        print("BOOTSTRAP_CONSISTENCY_SELFTEST_PASS")


if __name__ == "__main__":
    main()
