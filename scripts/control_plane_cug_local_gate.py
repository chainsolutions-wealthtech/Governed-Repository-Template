"""Follow the existing local CREDENTIAL_GATE for a CUG creation request."""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time

from control_plane_issue_bridge import api, extract_state
from control_plane_local_start import gh
from control_plane_provision_mcp_credential import decode_state
from governed_request import CONTROL_PLANE_REPOSITORY
from local_governed_entry import CUG_MCP_ENDPOINT
from project_continuity import IDENTITY, validate_projection


def observe_gate(state, target, expected_head, read, *, wait=time.sleep, attempts=12):
    identity = state[IDENTITY]
    repo = read(f"/repos/{target}")
    if repo.get("full_name") != target or repo.get("private") is not True:
        raise ValueError("CUG_LOCAL_GATE_TARGET_MISMATCH")
    validate_projection(identity, target, repo.get("id"))
    marker = f"<!-- GRT_PROJECT_REQUEST:{state['request_id']} -->"
    for attempt in range(attempts):
        issues = read(f"/repos/{target}/issues?state=open&per_page=100")
        hits = [issue for issue in issues if not issue.get("pull_request")
                and str(issue.get("title") or "").startswith("[Governed Local Entry]")
                and (issue.get("user") or {}).get("login") == "github-actions[bot]"
                and marker in (issue.get("body") or "").splitlines()
                and "<!-- GOVERNED_LOCAL_ENTRY_STATE:" in (issue.get("body") or "")]
        if len(hits) > 1:
            raise ValueError("CUG_LOCAL_GATE_MULTIPLE_MATCHES")
        if hits:
            issue = hits[0]
            local = decode_state(issue.get("body"))
            if (local.get(IDENTITY) != identity or local.get("repository") != target
                    or local.get("cug_machine_answers") != state["cug_machine_answers"]):
                raise ValueError("CUG_LOCAL_GATE_STATE_MISMATCH")
            if (local.get("next_request") or {}).get("kind") != "CREDENTIAL_GATE":
                return ("NO_CREDENTIAL_GATE", None)
            answers = local.get("answers") or {}
            if (local.get("expected_head_sha") != expected_head
                    or answers.get("mcp_endpoint") != CUG_MCP_ENDPOINT
                    or answers.get("mcp_transport") != "DIRECT_MCP_TOKEN"
                    or answers.get("mcp_discovery_approved") is not True):
                raise ValueError("CUG_LOCAL_GATE_PROOF_INVALID")
            number = issue.get("number")
            if type(number) is not int or number < 1:
                raise ValueError("CUG_LOCAL_GATE_ISSUE_INVALID")
            return ("READY", number)
        if attempt + 1 < attempts:
            wait(5)
    return ("LOCAL_ENTRY_NOT_OBSERVED", None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-number", type=int, required=True)
    args = parser.parse_args()
    issue = api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{args.issue_number}")
    state = extract_state(issue.get("body"))
    if state.get("credential_provider") != "CUG" or state.get("status") != "HANDOFF_READY":
        raise SystemExit("CUG_LOCAL_GATE_REQUEST_NOT_AUTHORIZED")
    if "cug_machine_answers" not in state:
        return
    handoff = state["handoff"]
    target, head = handoff["target_repository"], handoff["expected_head_sha"]
    if target != os.getenv("GOVERNED_CUG_AUTOMATED_PRIVATE_TARGET"):
        raise SystemExit("CUG_AUTOMATED_LOCAL_TARGET_NOT_AUTHORIZED")
    status, number = observe_gate(state, target, head, lambda path: gh("GET", path))
    if status != "READY":
        print(status)
        return
    common = ["--target-repository", target, "--target-issue", str(number), "--expected-head", head]
    env = os.environ.copy()
    subprocess.run([sys.executable, "scripts/control_plane_provision_mcp_credential.py", *common],
                   check=True, env=env)
    env.pop("GOVERNED_MCP_AUTH_TOKEN", None)
    command = base64.urlsafe_b64encode(json.dumps({"kind": "execute"}).encode()).decode()
    subprocess.run([sys.executable, "scripts/control_plane_local_command.py", *common,
                    "--source-issue", str(args.issue_number), "--command-b64", command],
                   check=True, env=env)


if __name__ == "__main__":
    main()
