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
TEST_REPOSITORY = "chainsolutions-wealthtech/entry-router-selftest"


def run(repo: Path, *args: str, env: dict[str, str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), cwd=repo, env=env, text=True, capture_output=True, check=check)


def py(repo: Path, *args: str, env: dict[str, str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(repo, sys.executable, *args, env=env, check=check)


def start(repo: Path, env: dict[str, str], ref: str, action: str | None, intent: str = "CODE_CHANGE") -> dict:
    args = [
        "scripts/governance_agent.py", "session-start",
        "--agent", "router-agent",
        "--provider", "other",
        "--connection-ref", ref,
        "--intent", intent,
    ]
    if action:
        args.extend(["--entry-action", action])
    return json.loads(py(repo, *args, env=env).stdout)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="entry-router-selftest-") as tmp:
        target = Path(tmp) / "repo"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
        run(target, "git", "init", "-b", "main", env=os.environ.copy())
        run(target, "git", "config", "user.name", "Governance Selftest", env=os.environ.copy())
        run(target, "git", "config", "user.email", "selftest@example.invalid", env=os.environ.copy())
        run(target, "git", "add", "-A", env=os.environ.copy())
        run(target, "git", "commit", "-m", "baseline", env=os.environ.copy())

        env = os.environ.copy()
        env.update({"GITHUB_REPOSITORY": TEST_REPOSITORY, "GITHUB_REF_NAME": "main"})
        py(target, "scripts/auto_bootstrap.py", env=env)

        questionnaire = json.loads(py(target, "scripts/governance_agent.py", "entry-actions", env=env).stdout)
        if questionnaire.get("status") != "ENTRY_ACTION_QUESTIONNAIRE":
            raise SystemExit("ENTRY_ROUTER_SELFTEST_FAILED: questionnaire unavailable")
        actions = questionnaire.get("actions") or {}
        required = {
            "CREATE_NEW_REPOSITORY",
            "ADOPT_EXISTING_REPOSITORY",
            "MAP_EXISTING_PROJECT",
            "LAB_EVOLUTION",
            "CONTINUE_GOVERNED_WORK",
            "UNKNOWN",
        }
        if set(actions) != required:
            raise SystemExit("ENTRY_ROUTER_SELFTEST_FAILED: incomplete action list")

        unknown = start(target, env, "unknown-entry", None)
        if unknown.get("entry_action_status") != "ENTRY_ACTION_REQUIRED":
            raise SystemExit("ENTRY_ROUTER_SELFTEST_FAILED: missing action did not trigger questionnaire")
        blocked = py(
            target, "scripts/governance_agent.py", "dispatch",
            "--session-id", unknown["session"]["session_id"], env=env, check=False
        )
        if blocked.returncode != 6 or json.loads(blocked.stdout).get("status") != "ENTRY_ACTION_REQUIRED":
            raise SystemExit("ENTRY_ROUTER_SELFTEST_FAILED: unresolved action received dispatch")

        for action, expected in [
            ("CREATE_NEW_REPOSITORY", "ENTRY_ACTION_SPECIAL_FLOW"),
            ("ADOPT_EXISTING_REPOSITORY", "ENTRY_ACTION_SPECIAL_FLOW"),
            ("MAP_EXISTING_PROJECT", "ENTRY_ACTION_READ_ONLY"),
            ("LAB_EVOLUTION", "LAB_BRANCH_REQUIRED"),
        ]:
            session = start(target, env, action.lower(), action)
            result = py(
                target, "scripts/governance_agent.py", "dispatch",
                "--session-id", session["session"]["session_id"], env=env, check=False
            )
            payload = json.loads(result.stdout)
            if result.returncode != 6 or payload.get("status") != expected:
                raise SystemExit(f"ENTRY_ROUTER_SELFTEST_FAILED: {action} routing")

        normal = start(target, env, "continue", "CONTINUE_GOVERNED_WORK")
        result = py(
            target, "scripts/governance_agent.py", "dispatch",
            "--session-id", normal["session"]["session_id"], env=env
        )
        payload = json.loads(result.stdout)
        if payload.get("status") != "ASSIGN":
            raise SystemExit("ENTRY_ROUTER_SELFTEST_FAILED: governed continuation cannot dispatch")

        print("ENTRY_ACTION_ROUTER_SELFTEST_PASS")


if __name__ == "__main__":
    main()
