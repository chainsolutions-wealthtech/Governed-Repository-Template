#!/usr/bin/env python3
"""Offline proof of intake, exact-HEAD continuity and CUG identity checks."""
from __future__ import annotations

import base64
from contextlib import redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

import control_plane_issue_bridge as bridge
import control_plane_local_start as starter
import local_entry_issue_bridge as local
from project_continuity import IDENTITY, from_github, validate_projection
from governed_request import apply_evidence
from verify_cug_app import verify_identity


def rejected(call, message):
    try:
        call()
    except (ValueError, SystemExit) as exc:
        assert message in str(exc), exc
    else:
        raise AssertionError(f"Expected refusal {message}")


def main():
    repo = "Patricked-code/fixture"
    head = "a" * 40
    login = "test-cug[bot]"
    request = {"sender": {"login": login}, "client_payload": {
        "objective": "Prepare test project", "creation": {
            "owner": "Patricked", "name": "fixture", "visibility": "private",
        },
    }}
    issued = []
    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp) / "output"
        def fake_api(method, path, payload=None):
            if method == "POST" and path.endswith("/issues"):
                return {"number": 99, "body": payload["body"]}
            return {}
        with patch.dict(os.environ, {"GITHUB_OUTPUT": str(output), "GOVERNED_CUG_BOT_LOGIN": login}), \
                patch.object(bridge, "api", fake_api), \
                patch.object(bridge, "persist_state", side_effect=lambda *args: issued.append(args[-1])), \
                redirect_stdout(StringIO()):
            rejected(lambda: bridge.handle_repository_dispatch({**request, "sender": {"login": "other[bot]"}}),
                     "CUG_CONTROL_PLANE_DISPATCH_ACTOR_NOT_AUTHORIZED")
            assert not issued
            bridge.handle_repository_dispatch(request)
            assert "executor_required=true" in output.read_text()
            assert "use_cug=true" in output.read_text()
            state = issued[0]
            assert state["request_id"] == "GR-000099"
            for action in state["execution_plan"]:
                action_id = action["id"]
                evidence = {k: "planned" if isinstance(v, str) and v.startswith("<") else v
                            for k, v in action["required_evidence"].items()}
                evidence.update({k: head for k, v in action["required_evidence"].items() if v == "<40-hex-sha>"})
                if action_id == "PREP-001":
                    rejected(lambda: apply_evidence(state, action_id, "PASS", evidence),
                             "PROJECT_CONTINUITY_GITHUB_EVIDENCE_REQUIRED")
                    evidence["github_repository_id"] = 123456
                state = apply_evidence(state, action_id, "PASS", evidence)
            identity = from_github(repo, 123456)
            assert state[IDENTITY] == state["handoff"][IDENTITY] == identity
            rejected(lambda: bridge.emit_executor_outputs(state, 99, local_start_payload={
                "target_repository": repo, "expected_head": "b" * 40, "objective": "Test",
            }), "PROJECT_CONTINUITY_HANDOFF_REQUIRED")
            bridge.emit_executor_outputs(state, 99, local_start_payload={
                "target_repository": repo, "expected_head": head, "objective": "Test",
            })
            captured = dict(line.split("=", 1) for line in output.read_text().splitlines())
            assert json.loads(base64.urlsafe_b64decode(captured["local_start_continuity_b64"])) == identity
    payloads = []
    def fake_target(method, path, payload=None):
        if method == "POST":
            payloads.append(payload["client_payload"])
        return {"full_name": repo, "id": 123456, "default_branch": "main", "object": {"sha": head}}
    with patch.object(starter, "gh", fake_target), patch.object(sys, "argv", [
        "starter", "--target-repository", repo, "--expected-head", head,
        "--objective-b64", captured["local_start_objective_b64"], "--source-issue", "99",
        "--continuity-b64", captured["local_start_continuity_b64"],
    ]), redirect_stdout(StringIO()):
        starter.main()
    assert payloads[0][IDENTITY] == identity
    assert validate_projection(identity, "Other/renamed", 123456)["project_continuity_id"] == identity["project_continuity_id"]
    rejected(lambda: validate_projection(identity, repo, 123457), "PROJECT_CONTINUITY_PROJECTION_MISMATCH")
    rejected(lambda: validate_projection({**identity, "server_binding_status": "ACTIVE"}, repo, 123456),
             "PROJECT_CONTINUITY_PROJECTION_MISMATCH")
    with patch.dict(os.environ, {"GITHUB_REPOSITORY": repo, "GITHUB_REPOSITORY_ID": "123456"}), \
            patch.object(local, "head", return_value=head), patch.object(local, "read_json", return_value={}), \
            patch.object(local, "first_agent_required", return_value=True), \
            patch.object(local, "api", return_value={"number": 9, "body": "Test"}), \
            patch.object(local, "persist") as persist, patch.object(local, "emit_outputs"), redirect_stdout(StringIO()):
        local.dispatch_start({"sender": {"type": "Bot"}, "client_payload": payloads[0]})
        assert persist.call_args.args[-1][IDENTITY] == identity
    verify_identity({"id": 5417646, "client_id": "sample", "slug": "test-cug"}, "sample", login)
    rejected(lambda: verify_identity({"id": 1, "client_id": "sample", "slug": "test-cug"}, "sample", login),
             "CUG_APP_IDENTITY_MISMATCH")
    print("CUG_PROJECT_CONTINUITY_SELFTEST_PASS")


if __name__ == "__main__":
    main()
