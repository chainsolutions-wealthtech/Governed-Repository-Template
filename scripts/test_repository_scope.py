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


def run(repo: Path, *args: str, env: dict[str, str]) -> None:
    subprocess.run(list(args), cwd=repo, env=env, text=True, capture_output=True, check=True)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="personal-scope-selftest-") as tmp:
        target = Path(tmp) / "repo"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
        env = os.environ.copy()

        # Recreate template-source preconditions so the scope test is portable
        # from both the central template and an already-instantiated repository.
        (target / ".template-source").write_text("SELFTEST_TEMPLATE_SOURCE\n", encoding="utf-8")
        profile_path = target / ".governance" / "profile.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
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
        local_entry = json.loads(local_entry_path.read_text(encoding="utf-8"))
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

        run(target, "git", "init", "-b", "main", env=env)
        run(target, "git", "config", "user.name", "Scope Selftest", env=env)
        run(target, "git", "config", "user.email", "scope@example.invalid", env=env)
        run(target, "git", "add", "-A", env=env)
        run(target, "git", "commit", "-m", "baseline", env=env)

        env.update({
            "GITHUB_REPOSITORY": "personal-owner/governance-selftest",
            "GITHUB_REF_NAME": "main",
            "GOVERNANCE_REPOSITORY_SCOPE": "PERSONAL_ACCOUNT",
        })
        run(target, sys.executable, "scripts/auto_bootstrap.py", env=env)
        scope = json.loads((target / ".governance" / "repository-scope-policy.json").read_text(encoding="utf-8"))
        if scope.get("target_owner") != "personal-owner":
            raise SystemExit("REPOSITORY_SCOPE_SELFTEST_FAILED: personal owner not captured")
        if scope.get("target_scope") != "PERSONAL_ACCOUNT":
            raise SystemExit("REPOSITORY_SCOPE_SELFTEST_FAILED: personal scope not persisted")
        profile = json.loads((target / ".governance" / "profile.json").read_text(encoding="utf-8"))
        if profile.get("repository") != "personal-owner/governance-selftest":
            raise SystemExit("REPOSITORY_SCOPE_SELFTEST_FAILED: repository binding incorrect")
        print("REPOSITORY_SCOPE_SELFTEST_PASS")


if __name__ == "__main__":
    main()
