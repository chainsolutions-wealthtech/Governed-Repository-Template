#!/usr/bin/env python3
from __future__ import annotations

import os
import sys

import control_plane_create_repository as executor
from governed_request import apply_answer, encode_state, new_request


def state_for(owner_label: str, name: str, visibility: str) -> dict:
    state = new_request("SELFTEST-CREATE-EXECUTOR", "agent", "test", None)
    state = apply_answer(state, "entry_action", "CREATE_NEW_REPOSITORY")
    state = apply_answer(state, "creation_target_owner", owner_label)
    state = apply_answer(state, "repository_name", name)
    state = apply_answer(state, "visibility", visibility)
    if state["next_request"].get("action_id") != "PREP-001":
        raise SystemExit("CREATE_EXECUTOR_SELFTEST_FAILED: PREP-001 not ready")
    return state


def run_case(owner_label: str, canonical_owner: str, principal: str, token_env: str, visibility: str) -> None:
    state = state_for(owner_label, "executor-selftest", visibility)
    issue_body = "selftest\n\n<!-- GOVERNED_REQUEST_STATE:" + encode_state(state) + " -->\n"
    captured = {"persisted": None, "comments": [], "generate_payload": None, "paths": []}

    original_cp_api = executor.control_plane_api
    original_github_api = executor.github_api
    original_persist = executor.persist_state
    original_comment = executor.comment
    original_argv = sys.argv[:]
    old_env = dict(os.environ)

    def fake_cp_api(method: str, path: str, payload: dict | None = None):
        if method == "GET" and path.endswith("/issues/99"):
            return {"number": 99, "body": issue_body}
        captured["comments"].append((method, path, payload))
        return {}

    def fake_github_api(token: str, method: str, path: str, payload: dict | None = None, allow_404: bool = False):
        captured["paths"].append((method, path))
        if method == "GET" and path == "/user":
            return {"login": principal}
        if method == "GET" and path == "/repos/chainsolutions-wealthtech/Governed-Repository-Template":
            return {"is_template": True, "full_name": "chainsolutions-wealthtech/Governed-Repository-Template"}
        if method == "GET" and path == f"/repos/{canonical_owner}/executor-selftest":
            return None
        if method == "GET" and path == f"/user/memberships/orgs/{canonical_owner}":
            return {"state": "active"}
        if method == "POST" and path == "/repos/chainsolutions-wealthtech/Governed-Repository-Template/generate":
            captured["generate_payload"] = payload
            return {"full_name": f"{canonical_owner}/executor-selftest", "default_branch": "main"}
        if method == "GET" and path == f"/repos/{canonical_owner}/executor-selftest/commits/main":
            return {"sha": "e" * 40}
        raise AssertionError(f"unexpected GitHub API call: {method} {path}")

    try:
        executor.control_plane_api = fake_cp_api
        executor.github_api = fake_github_api
        executor.persist_state = lambda issue_number, body, new_state: captured.__setitem__("persisted", new_state)
        executor.comment = lambda issue_number, body: captured["comments"].append(("COMMENT", issue_number, body))
        os.environ.clear()
        os.environ.update(old_env)
        os.environ[token_env] = "selftest-token"
        sys.argv = ["control_plane_create_repository.py", "--issue-number", "99"]
        executor.main()
    finally:
        executor.control_plane_api = original_cp_api
        executor.github_api = original_github_api
        executor.persist_state = original_persist
        executor.comment = original_comment
        sys.argv = original_argv
        os.environ.clear()
        os.environ.update(old_env)

    payload = captured["generate_payload"]
    if not payload:
        raise SystemExit("CREATE_EXECUTOR_SELFTEST_FAILED: generate endpoint not called")
    if payload.get("owner") != canonical_owner:
        raise SystemExit("CREATE_EXECUTOR_SELFTEST_FAILED: canonical owner mismatch")
    if payload.get("private") is not (visibility == "private"):
        raise SystemExit("CREATE_EXECUTOR_SELFTEST_FAILED: visibility mismatch")
    if payload.get("include_all_branches") is not False:
        raise SystemExit("CREATE_EXECUTOR_SELFTEST_FAILED: include_all_branches must be false")

    persisted = captured["persisted"]
    if not persisted:
        raise SystemExit("CREATE_EXECUTOR_SELFTEST_FAILED: state was not persisted")
    if persisted["evidence"][0]["evidence"]["repository"] != f"{canonical_owner}/executor-selftest":
        raise SystemExit("CREATE_EXECUTOR_SELFTEST_FAILED: repository evidence mismatch")
    if persisted["evidence"][0]["evidence"]["visibility"] != visibility:
        raise SystemExit("CREATE_EXECUTOR_SELFTEST_FAILED: visibility evidence mismatch")
    if persisted["next_request"].get("action_id") != "PREP-002":
        raise SystemExit("CREATE_EXECUTOR_SELFTEST_FAILED: executor did not advance to PREP-002")


def main() -> None:
    run_case(
        owner_label="chainsolutions-wealthtech",
        canonical_owner="chainsolutions-wealthtech",
        principal="Wealthtechinnovations",
        token_env="GOVERNED_CREATOR_WEALTHTECH_TOKEN",
        visibility="private",
    )
    run_case(
        owner_label="Wealthtechinnovations",
        canonical_owner="Wealthtechinnovations",
        principal="Wealthtechinnovations",
        token_env="GOVERNED_CREATOR_WEALTHTECH_TOKEN",
        visibility="public",
    )
    run_case(
        owner_label="Patricked",
        canonical_owner="Patricked-code",
        principal="Patricked-code",
        token_env="GOVERNED_CREATOR_PATRICKED_TOKEN",
        visibility="private",
    )
    print("REPOSITORY_CREATION_EXECUTOR_SELFTEST_PASS")


if __name__ == "__main__":
    main()
