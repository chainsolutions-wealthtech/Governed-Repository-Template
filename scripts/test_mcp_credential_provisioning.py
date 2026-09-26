#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from control_plane_provision_mcp_credential import SECRET_NAME, validate_requirements

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    control_plane_workflow = ROOT / ".github/workflows/governed-control-plane.yml"
    if not control_plane_workflow.exists():
        print("MCP_CREDENTIAL_PROVISION_SELFTEST_SKIP: target client has no central control-plane workflow")
        return

    required = {
        "next_request": {
            "kind": "CREDENTIAL_GATE",
            "requirements": [{"kind": "secret", "name": SECRET_NAME}],
        }
    }
    if validate_requirements(required) is not True:
        raise SystemExit("MCP_CREDENTIAL_PROVISION_SELFTEST_FAILED: expected token requirement")

    not_required = {"next_request": {"kind": "MCP_DISCOVERY", "requirements": []}}
    if validate_requirements(not_required) is not False:
        raise SystemExit("MCP_CREDENTIAL_PROVISION_SELFTEST_FAILED: non-gate must be no-op")

    unsupported = {
        "next_request": {
            "kind": "CREDENTIAL_GATE",
            "requirements": [{"kind": "secret", "name": "UNSUPPORTED_SECRET"}],
        }
    }
    try:
        validate_requirements(unsupported)
    except RuntimeError as exc:
        if str(exc) != "CREDENTIAL_REQUIREMENTS_UNSUPPORTED":
            raise
    else:
        raise SystemExit("MCP_CREDENTIAL_PROVISION_SELFTEST_FAILED: unsupported secret accepted")

    workflow = (ROOT / ".github/workflows/governed-control-plane.yml").read_text(encoding="utf-8")
    bridge = (ROOT / "scripts/control_plane_issue_bridge.py").read_text(encoding="utf-8")
    provisioner = (ROOT / "scripts/control_plane_provision_mcp_credential.py").read_text(encoding="utf-8")

    for fragment in [
        "permission-secrets: write",
        "permission-issues: read",
        "control_plane_provision_mcp_credential.py",
        "GOVERNED_MCP_AUTH_TOKEN",
        "local_command_kind == 'execute'",
        "continue-on-error: true",
        "Report governed MCP credential provisioning failure",
        "steps.mcp-credential.outcome == 'failure'",
        "steps.mcp-credential.outcome == 'success'",
    ]:
        if fragment not in workflow:
            raise SystemExit("MCP_CREDENTIAL_PROVISION_SELFTEST_FAILED: workflow contract " + fragment)

    if "local_command_kind=" not in bridge:
        raise SystemExit("MCP_CREDENTIAL_PROVISION_SELFTEST_FAILED: command kind output missing")

    for fragment in [
        "gh",
        "secret",
        "set",
        "CONTROL_PLANE_MCP_AUTH_TOKEN_MISSING",
        "MCP_CREDENTIAL_PROVISION_ATTESTATION_FAILED",
        "secret_value_exposed",
        "HEAD_MOVED",
        "LOCAL_STATE_HEAD_MOVED",
        "failure_code",
        "CONTROL_PLANE_MCP_AUTH_TOKEN_MISSING",
        "TARGET_MCP_SECRET_WRITE_FAILED",
        "TARGET_MCP_SECRET_ATTESTATION_READ_FAILED",
    ]:
        if fragment not in provisioner:
            raise SystemExit("MCP_CREDENTIAL_PROVISION_SELFTEST_FAILED: provisioner contract " + fragment)

    if "--body" in provisioner:
        raise SystemExit("MCP_CREDENTIAL_PROVISION_SELFTEST_FAILED: secret must not be placed on command line")
    if "print(source_secret)" in provisioner or "json.dumps(source_secret)" in provisioner:
        raise SystemExit("MCP_CREDENTIAL_PROVISION_SELFTEST_FAILED: secret logging forbidden")

    print("MCP_CREDENTIAL_PROVISION_SELFTEST_PASS")


if __name__ == "__main__":
    main()
