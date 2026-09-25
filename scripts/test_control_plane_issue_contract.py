#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

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

    evidence = parse_command('/governed-evidence\n{"action_id":"PREP-001","result":"PASS","evidence":{"created":true}}')
    if evidence is None or evidence[0] != "evidence" or evidence[1]["action_id"] != "PREP-001":
        raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: evidence parsing")

    workflow = (ROOT / ".github" / "workflows" / "governed-control-plane.yml").read_text(encoding="utf-8")
    required = [
        "github.repository == 'chainsolutions-wealthtech/Governed-Repository-Template'",
        "issues: write",
        "github.actor != 'github-actions[bot]'",
        "python3 scripts/control_plane_issue_bridge.py",
    ]
    for fragment in required:
        if fragment not in workflow:
            raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: workflow boundary missing: " + fragment)

    issue_form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "governed-request.yml").read_text(encoding="utf-8")
    if 'title: "[Governed Request] "' not in issue_form:
        raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: governed issue title missing")

    initializer = (ROOT / "scripts" / "initialize_governance.py").read_text(encoding="utf-8")
    if 'control_plane.get("source_only_paths", [])' not in initializer:
        raise SystemExit("CONTROL_PLANE_ISSUE_SELFTEST_FAILED: client source-only removal missing")

    print("GOVERNED_CONTROL_PLANE_ISSUE_SELFTEST_PASS")


if __name__ == "__main__":
    main()
