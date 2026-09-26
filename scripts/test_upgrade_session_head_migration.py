#!/usr/bin/env python3
from __future__ import annotations

import copy

import control_plane_upgrade_local_entry as upgrade

OLD = "a" * 40
CURRENT = "b" * 40
NEW = "c" * 40


def make_issue(head: str, revision: int = 22) -> dict:
    state = {
        "schema_version": "1.1.0",
        "request_id": "LOCAL-TEST",
        "repository": "owner/repo",
        "mode": "FIRST_AGENT_BOOTSTRAP",
        "status": "MCP_CREDENTIAL_REQUIRED",
        "phase": "MCP_CREDENTIAL_GATE",
        "revision": revision,
        "expected_head_sha": head,
        "answers": {"project_mission": "preserve me"},
        "next_request": {"kind": "CREDENTIAL_GATE"},
        "baseline_package": {"project_mission": "preserve me"},
        "handoff": None,
        "hold_reason": None,
        "setup_package": None,
        "mcp_discovery": None,
        "credentials_verified": False,
    }
    marker = upgrade.encode_local_issue_state(state)
    return {
        "number": 7,
        "title": "[Governed Local Entry] Test",
        "body": f"Initial\n\n<!-- GOVERNED_LOCAL_ENTRY_STATE:{marker} -->\n",
    }


def run_case(messages: list[str]) -> tuple[list[dict], list[dict]]:
    patched = []
    comments = []
    issue = make_issue(OLD)

    def fake_gh(token, method, path, payload=None, allow_404=False):
        if method == "GET" and "/issues?state=open" in path:
            return [copy.deepcopy(issue)]
        if method == "GET" and "/compare/" in path:
            return {
                "status": "ahead",
                "merge_base_commit": {"sha": OLD},
                "commits": [{"commit": {"message": message}} for message in messages],
            }
        if method == "PATCH" and path.endswith("/issues/7"):
            patched.append(copy.deepcopy(payload))
            return {}
        if method == "POST" and path.endswith("/issues/7/comments"):
            comments.append(copy.deepcopy(payload))
            return {}
        raise AssertionError((method, path, payload))

    original = upgrade.gh
    upgrade.gh = fake_gh
    try:
        migrated = upgrade.migrate_open_local_entry_heads("token", "owner/repo", CURRENT, NEW)
    finally:
        upgrade.gh = original

    if messages and all(m.splitlines()[0].startswith(upgrade.UPGRADE_PREFIX) for m in messages):
        assert len(migrated) == 1
    else:
        assert migrated == []
    return patched, comments


def main() -> None:
    patched, comments = run_case([
        "governance: upgrade repository-local setup to v2.6.3",
        "governance: upgrade repository-local setup to v2.6.4",
        "governance: upgrade repository-local setup to v2.6.5",
    ])
    assert len(patched) == 1
    assert len(comments) == 1
    state = upgrade.decode_local_issue_state(patched[0]["body"])
    assert state["expected_head_sha"] == NEW
    assert state["revision"] == 23
    assert state["answers"]["project_mission"] == "preserve me"
    assert state["baseline_package"]["project_mission"] == "preserve me"

    patched_bad, comments_bad = run_case([
        "governance: upgrade repository-local setup to v2.6.3",
        "feat: unrelated project mutation",
    ])
    assert patched_bad == []
    assert comments_bad == []

    source = open(upgrade.__file__, "r", encoding="utf-8").read()
    assert 'local.update({"repository":target,"status":"WAITING_FOR_FIRST_AGENT"' not in source
    assert 'existing_local=target_text(token,target,".governance/local-entry/state.json")' in source

    print("UPGRADE_SESSION_HEAD_MIGRATION_SELFTEST_PASS")


if __name__ == "__main__":
    main()
