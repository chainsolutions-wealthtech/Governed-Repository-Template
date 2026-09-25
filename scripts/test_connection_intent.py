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
TEST_REPOSITORY = "chainsolutions-wealthtech/governance-intent-selftest"


def cp(repo: Path, *args: str, env: dict[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=check,
    )


def python(repo: Path, *args: str, env: dict[str, str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return cp(repo, sys.executable, *args, env=env, check=check)


def start(repo: Path, env: dict[str, str], agent: str, ref: str, intent: str | None) -> dict:
    args = [
        "scripts/governance_agent.py", "session-start",
        "--agent", agent,
        "--provider", "other",
        "--connection-ref", ref,
    ]
    if intent:
        args.extend(["--intent", intent])
    result = python(repo, *args, env=env)
    return json.loads(result.stdout)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="governance-intent-selftest-") as tmp:
        target = Path(tmp) / "repo"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))

        cp(target, "git", "init", "-b", "main")
        cp(target, "git", "config", "user.name", "Governance Selftest")
        cp(target, "git", "config", "user.email", "selftest@example.invalid")
        cp(target, "git", "add", "-A")
        cp(target, "git", "commit", "-m", "template selftest baseline")

        env = os.environ.copy()
        env.update({
            "GITHUB_REPOSITORY": TEST_REPOSITORY,
            "GITHUB_REF_NAME": "main",
        })

        python(target, "scripts/auto_bootstrap.py", env=env)

        info = start(target, env, "info-agent", "info-1", "INFORMATION_INTAKE")
        if info.get("intent_route") != "INTAKE" or info.get("may_dispatch_mutable_work") is not False:
            raise SystemExit("INTENT_SELFTEST_FAILED: information intake routing")
        info_dispatch = python(
            target,
            "scripts/governance_agent.py", "dispatch",
            "--session-id", info["session"]["session_id"],
            env=env,
            check=False,
        )
        if info_dispatch.returncode != 5:
            raise SystemExit("INTENT_SELFTEST_FAILED: information intake received mutable dispatch")
        blocked = json.loads(info_dispatch.stdout)
        if blocked.get("status") != "INTENT_BLOCKS_MUTABLE_DISPATCH":
            raise SystemExit("INTENT_SELFTEST_FAILED: information intake block status")

        unknown = start(target, env, "unknown-agent", "unknown-1", None)
        if unknown.get("intent_route") != "RESOLVE_CONNECTION_INTENT":
            raise SystemExit("INTENT_SELFTEST_FAILED: unknown intent did not fail closed")
        unknown_dispatch = python(
            target,
            "scripts/governance_agent.py", "dispatch",
            "--session-id", unknown["session"]["session_id"],
            env=env,
            check=False,
        )
        if unknown_dispatch.returncode != 5:
            raise SystemExit("INTENT_SELFTEST_FAILED: unknown intent received mutable dispatch")

        coder = start(target, env, "code-agent", "code-1", "CODE_CHANGE")
        if coder.get("may_dispatch_mutable_work") is not True:
            raise SystemExit("INTENT_SELFTEST_FAILED: code intent not eligible")
        code_dispatch = python(
            target,
            "scripts/governance_agent.py", "dispatch",
            "--session-id", coder["session"]["session_id"],
            env=env,
        )
        assigned = json.loads(code_dispatch.stdout)
        if assigned.get("status") != "ASSIGN":
            raise SystemExit("INTENT_SELFTEST_FAILED: code intent was not dispatched")
        if assigned.get("work_item", {}).get("work_item_id") != "WORK-DISCOVER-001":
            raise SystemExit("INTENT_SELFTEST_FAILED: unexpected work item")

        python(target, "scripts/validate_governance.py", env=env)
        print("CONNECTION_INTENT_SELFTEST_PASS")


if __name__ == "__main__":
    main()
