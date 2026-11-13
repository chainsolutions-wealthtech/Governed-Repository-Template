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
from control_plane_cug_bootstrap_handoff import prepare
from control_plane_cug_local_gate import observe_gate
from local_governed_entry import CUG_MCP_ENDPOINT, advance_cug_machine_answers, encode_state, mark_credentials_verified, new_request, record_mcp_discovery
from mcp_repository_discovery import discover_direct
from test_local_governed_entry import first_base
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
            assert state["project_continuity_id"] == "WT-PROJECT-GRT-1386478935-GR-000099"
            assert IDENTITY not in state
            for action in state["execution_plan"][:1]:
                action_id = action["id"]
                evidence = {k: "planned" if isinstance(v, str) and v.startswith("<") else v
                            for k, v in action["required_evidence"].items()}
                evidence.update({k: head for k, v in action["required_evidence"].items() if v == "<40-hex-sha>"})
                if action_id == "PREP-001":
                    rejected(lambda: apply_evidence(state, action_id, "PASS", evidence),
                             "PROJECT_CONTINUITY_GITHUB_EVIDENCE_REQUIRED")
                    evidence["github_repository_id"] = 123456
                state = apply_evidence(state, action_id, "PASS", evidence)
            identity = from_github(repo, 123456, request_id="GR-000099")
            init = "b" * 40
            final = "c" * 40
            prefix = f"/repos/{repo}"
            receipt = {"repository": repo, "canonical_branch": "main",
                "template_repository": bridge.CONTROL_PLANE_REPOSITORY, "input_head_sha": head,
                "initialized": True, "validation": "PASS", "initialization_commit_sha": init,
                "attestation_subject_sha": init, "attestation_model": "CHILD_COMMIT_ATTESTS_INITIALIZATION_COMMIT",
                "github_run_id": "31", "template_revision": "2.8.6"}
            observations = {
                prefix: {"id": 123456, "full_name": repo, "default_branch": "main"},
                prefix+"/git/ref/heads/main": {"object": {"sha": final}},
                prefix+f"/contents/.governance/bootstrap-receipt.json?ref={final}": {
                    "encoding": "base64", "content": base64.b64encode(json.dumps(receipt).encode()).decode()},
                prefix+f"/commits/{final}": {"sha": final, "parents": [{"sha": init}]},
                prefix+f"/commits/{init}": {"sha": init, "parents": [{"sha": head}]},
                prefix+"/actions/runs/31": {"id": 31, "repository": {"id": 123456}, "head_sha": head,
                    "path": ".github/workflows/governance-auto-bootstrap.yml", "status": "completed", "conclusion": "success"},
                prefix+"/actions/runs/31/jobs": {"jobs": [{"name": "bootstrap", "conclusion": "success",
                    "steps": [{"name": "Verify remote bootstrap attestation", "conclusion": "skipped"}]}]},
            }
            def observe(path, **kwargs):
                return observations[path]
            rejected(lambda: prepare(state, repo, observe, attempts=1), "CUG_BOOTSTRAP_ATTESTATION_STEP_UNVERIFIED")
            observations[prefix+"/actions/runs/31/jobs"]["jobs"][0]["steps"][0]["conclusion"] = "success"
            state = prepare(state, repo, observe, attempts=1)
            head = final
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
            patch.object(local, "api", side_effect=lambda method, path, payload=None: [] if "?state=" in path else {"number": 9, "body": "Test"}), \
            patch.object(local, "persist") as persist, patch.object(local, "emit_outputs"), redirect_stdout(StringIO()):
        local.dispatch_start({"sender": {"type": "Bot"}, "client_payload": payloads[0]})
        assert persist.call_args.args[-1][IDENTITY] == identity
    verify_identity({"id": 5417646, "client_id": "sample", "slug": "test-cug"}, "sample", login)
    rejected(lambda: verify_identity({"id": 1, "client_id": "sample", "slug": "test-cug"}, "sample", login),
             "CUG_APP_IDENTITY_MISMATCH")
    questionnaire = {k: v for k, v in first_base()["answers"].items() if k != "initial_context"}
    questionnaire.update(baseline_approved=True, setup_repository_now=True, link_mcp_server=True,
        mcp_transport="DIRECT_MCP_TOKEN", mcp_discovery_scope="INFRASTRUCTURE_AND_DOMAIN_READONLY",
        domain_strategy="NO_DOMAIN_YET", runtime_mutation_policy="READ_ONLY_DISCOVERY",
        mcp_discovery_approved=True, production_server_selection="DECIDE_LATER",
        domain_intent="NO_PUBLIC_DOMAIN", workflow_model="STANDARD_GOVERNED_FLOW", setup_approved=True)
    first = new_request("LOCAL-000009", repo, head, True, continuity=identity)
    first["cug_machine_answers"] = questionnaire
    waiting = advance_cug_machine_answers(first)
    assert waiting["next_request"]["kind"] == "CREDENTIAL_GATE"
    assert waiting["answers"]["mcp_endpoint"] == CUG_MCP_ENDPOINT
    state["cug_machine_answers"] = questionnaire
    marker = "<!-- GRT_PROJECT_REQUEST:GR-000099 -->"
    body = f"{marker}\n<!-- GOVERNED_LOCAL_ENTRY_STATE:{encode_state(waiting)} -->"
    def local_read(path):
        if path == f"/repos/{repo}":
            return {"id": 123456, "full_name": repo, "private": True}
        return [{"number": 9, "title": "[Governed Local Entry] test", "user": {"login": "github-actions[bot]"}, "body": body}]
    assert observe_gate(state, repo, head, local_read, attempts=1) == ("READY", 9)
    rejected(lambda: observe_gate(state, repo, "e" * 40, local_read, attempts=1),
             "CUG_LOCAL_GATE_PROOF_INVALID")
    discovery_state = mark_credentials_verified(waiting)
    assert discovery_state["next_request"]["kind"] == "MCP_DISCOVERY"
    def mcp_result(endpoint, token, payload, session_id=None, **options):
        assert endpoint == CUG_MCP_ENDPOINT and options["reject_redirects"]
        return {"id": payload.get("id"), "result": {"content": []}}, "fixture-session"
    with patch("mcp_repository_discovery.post", side_effect=mcp_result):
        direct = discover_direct(CUG_MCP_ENDPOINT, "fixture-only", reject_redirects=True)
    assert direct["status"] == "PASS"
    with patch("mcp_repository_discovery.post", return_value=({"id": 1, "error": {}}, "fixture-session")):
        try:
            discover_direct(CUG_MCP_ENDPOINT, "fixture-only", reject_redirects=True)
        except RuntimeError as exc:
            assert str(exc) == "CUG_MCP_INITIALIZATION_UNVERIFIED"
        else:
            raise AssertionError("MCP error accepted as successful discovery")
    applied = advance_cug_machine_answers(record_mcp_discovery(discovery_state,
        {"status": "PASS", "selected_transport": "DIRECT_MCP_TOKEN", "direct_mcp": direct}))
    assert applied["next_request"]["kind"] == "APPLY_BASELINE"
    assert applied[IDENTITY] == identity
    rejected(lambda: advance_cug_machine_answers({**first, "cug_machine_answers": {"mcp_endpoint": "https://example.org"}}),
             "CUG_MACHINE_ANSWERS_INVALID")
    partial = {**questionnaire}
    del partial["baseline_approved"]
    unanswered = advance_cug_machine_answers({**first, "cug_machine_answers": partial})
    assert unanswered["next_request"]["field"] == "baseline_approved"
    print("CUG_PROJECT_CONTINUITY_SELFTEST_PASS")


if __name__ == "__main__":
    main()
