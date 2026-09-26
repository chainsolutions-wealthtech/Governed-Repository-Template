#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import control_plane_issue_bridge as bridge_module
from control_plane_issue_bridge import extract_state, parse_command, strip_marker
from governed_request import encode_state, new_request

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    state = new_request("GR-000001", "selftest", "github", "initial")
    encoded = encode_state(state)
    body = "Original issue body\n\n<!-- GOVERNED_REQUEST_STATE:" + encoded + " -->\n"
    restored = extract_state(body)
    if restored["request_id"] != "GR-000001":
        raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: state persistence")
    if strip_marker(body) != "Original issue body":
        raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: marker stripping")

    answer = parse_command('/governed-answer\n{"field":"entry_action","value":"CREATE_NEW_REPOSITORY"}')
    if answer is None or answer[0] != "answer" or answer[1]["field"] != "entry_action":
        raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: answer parsing")

    machine = parse_command('/governed-local-command\n{"target_repository":"owner/repo","issue_number":2,"expected_head":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","command":{"kind":"execute"}}')
    if machine is None or machine[0] != "local_command" or machine[1]["command"]["kind"] != "execute":
        raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: machine command parsing")

    evidence = parse_command('/governed-evidence\n{"action_id":"PREP-001","result":"PASS","evidence":{"created":true}}')
    if evidence is None or evidence[0] != "evidence" or evidence[1]["action_id"] != "PREP-001":
        raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: evidence parsing")

    policy = __import__("json").loads((ROOT / ".governance" / "control-plane-policy.json").read_text(encoding="utf-8"))
    workflow_path = ROOT / ".github" / "workflows" / "governed-control-plane.yml"
    issue_form_path = ROOT / ".github" / "ISSUE_TEMPLATE" / "governed-request.yml"

    if policy.get("current_role") == "CENTRAL_GOVERNANCE_CONTROL_PLANE":
        workflow = workflow_path.read_text(encoding="utf-8")
        required = [
            "github.repository == 'chainsolutions-wealthtech/Governed-Repository-Template'",
            "issues: write",
            "github.actor != 'github-actions[bot]'",
            "repository_dispatch:",
            "governed_request_start",
            "python3 scripts/control_plane_issue_bridge.py",
            "actions/create-github-app-token@v3",
            "GOVERNED_GITHUB_APP_CLIENT_ID",
            "GOVERNED_GITHUB_APP_PRIVATE_KEY",
            "permission-administration: write",
            "permission-contents: read",
            "scripts/control_plane_local_command.py",
            "local_command_required",
            "permission-contents: write",
            "Dispatch governed machine local command",
        ]
        for fragment in required:
            if fragment not in workflow:
                raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: workflow boundary missing: " + fragment)
        issue_form = issue_form_path.read_text(encoding="utf-8")
        if 'title: "[Governed Request] "' not in issue_form:
            raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: governed issue title missing")
    else:
        if policy.get("current_role") != "GOVERNED_TARGET_CLIENT":
            raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: invalid control plane role")
        if workflow_path.exists() or issue_form_path.exists():
            raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: source-only surface leaked into client")

    bridge = (ROOT / "scripts" / "control_plane_issue_bridge.py").read_text(encoding="utf-8")
    local_dispatcher = (ROOT / "scripts" / "control_plane_local_command.py").read_text(encoding="utf-8")
    for fragment in ["/dispatches", "governed_local_command", "HEAD_MOVED", "GOVERNED_TARGET_TOKEN"]:
        if fragment not in local_dispatcher:
            raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: machine local dispatcher missing: " + fragment)
    if "def handle_repository_dispatch" not in bridge:
        raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: repository dispatch handler missing")

    calls = []
    original_api = bridge_module.api
    try:
        def fake_api(method: str, path: str, payload: dict | None = None) -> dict:
            calls.append((method, path, payload))
            return {"number": 99, "html_url": "https://github.example.invalid/issues/99"}

        bridge_module.api = fake_api
        bridge_module.handle_repository_dispatch({
            "client_payload": {
                "objective": "Create a governed request through repository dispatch",
                "agent": "selftest-agent",
                "provider": "selftest",
                "title": "Dispatch selftest",
            }
        })
    finally:
        bridge_module.api = original_api

    if len(calls) != 1:
        raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: repository dispatch did not create exactly one issue")
    method, path, payload = calls[0]
    if method != "POST" or path != "/repos/chainsolutions-wealthtech/Governed-Repository-Template/issues":
        raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: repository dispatch issue endpoint invalid")
    if not payload or not str(payload.get("title", "")).startswith("[Governed Request]"):
        raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: repository dispatch issue title invalid")

    initializer = (ROOT / "scripts" / "initialize_governance.py").read_text(encoding="utf-8")
    if 'control_plane.get("source_only_paths", [])' not in initializer:
        raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: client source-only removal missing")

    print("GOVERNED_CONTROL_PLANE_ISSUE_SELFTEST_PASS")


if __name__ == "__main__":
    main()
