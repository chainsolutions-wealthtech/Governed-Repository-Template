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


def read_json(repo: Path, relative: str) -> dict:
    return json.loads((repo / relative).read_text(encoding="utf-8"))


def write_json(repo: Path, relative: str, value: dict) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_synthetic_template_fixture(repo: Path) -> None:
    """Remove instantiated-client state from this synthetic routing test.

    The self-test may run from either the central template source or from an
    already-initialized/upgraded client. It must therefore build its own
    deterministic template fixture rather than inherit real project work,
    claims, sessions or canonical-memory pointers from the repository that is
    executing the test.
    """
    (repo / ".template-source").write_text("INTENT_SELFTEST_TEMPLATE_SOURCE\n", encoding="utf-8")

    profile = read_json(repo, ".governance/profile.json")
    profile.update({
        "template_source": True,
        "initialized": False,
        "repository": "{{REPOSITORY}}",
        "project_name": "{{PROJECT_NAME}}",
        "project_type": "{{PROJECT_TYPE}}",
        "owner": "{{OWNER}}",
        "canonical_branch": "{{CANONICAL_BRANCH}}",
        "initialized_at": "{{INITIALIZED_AT}}",
        "initialization_mode": "TEMPLATE_BOOTSTRAP",
    })
    write_json(repo, ".governance/profile.json", profile)

    write_json(repo, ".governance/work/work-items.json", {
        "schema_version": "1.0.0",
        "revision": 0,
        "items": [{
            "work_item_id": "WORK-INIT-001",
            "title": "Initialize project governance",
            "status": "READY",
            "priority": 1000,
            "sequence": 1,
            "dependencies": [],
            "collision_domains": ["governance-state"],
            "next_action": "INITIALIZE_PROJECT_GOVERNANCE",
        }],
    })
    write_json(repo, ".governance/work/claims.json", {
        "schema_version": "1.0.0",
        "revision": 0,
        "claims": [],
    })
    write_json(repo, ".governance/sessions/sessions.json", {
        "schema_version": "1.0.0",
        "revision": 0,
        "sessions": [],
    })
    write_json(repo, ".governance/canonical-memory/current.json", {
        "schema_version": "1.0.0",
        "repository": "{{REPOSITORY}}",
        "canonical_branch": "{{CANONICAL_BRANCH}}",
        "canonical_revision": 0,
        "work_revision": 0,
        "observed_head_sha": "TO_CAPTURE",
        "current_checkpoint": None,
        "current_handoff": None,
        "next_action": "INITIALIZE_PROJECT_GOVERNANCE",
        "blockers": [],
        "freshness": "TEMPLATE_SOURCE",
    })


def start(repo: Path, env: dict[str, str], agent: str, ref: str, intent: str | None, entry_action: str = "CONTINUE_GOVERNED_WORK") -> dict:
    args = [
        "scripts/governance_agent.py", "session-start",
        "--agent", agent,
        "--provider", "other",
        "--connection-ref", ref,
        "--entry-action", entry_action,
    ]
    if intent:
        args.extend(["--intent", intent])
    result = python(repo, *args, env=env)
    return json.loads(result.stdout)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="governance-intent-selftest-") as tmp:
        target = Path(tmp) / "repo"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))

        build_synthetic_template_fixture(target)

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

        work = read_json(target, ".governance/work/work-items.json")
        items = {item.get("work_item_id"): item for item in work.get("items", [])}
        if set(items) != {"WORK-INIT-001", "WORK-DISCOVER-001"}:
            raise SystemExit(
                "INTENT_SELFTEST_FAILED: synthetic work fixture contaminated: "
                + ",".join(sorted(items))
            )
        if items["WORK-INIT-001"].get("status") != "DONE":
            raise SystemExit("INTENT_SELFTEST_FAILED: synthetic init work item not completed")
        if items["WORK-DISCOVER-001"].get("status") != "READY":
            raise SystemExit("INTENT_SELFTEST_FAILED: synthetic discovery work item not ready")

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
            raise SystemExit("INTENT_SELFTEST_FAILED: unexpected synthetic work item")

        python(target, "scripts/validate_governance.py", env=env)
        print("CONNECTION_INTENT_SELFTEST_PASS")


if __name__ == "__main__":
    main()
