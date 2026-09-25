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
