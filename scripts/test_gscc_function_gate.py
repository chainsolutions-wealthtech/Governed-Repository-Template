#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import gscc_function_gate as gate

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / ".governance/control-plane-state/mcp-capability-snapshot.json").read_text(encoding="utf-8"))
WORKFLOW = ROOT / ".github/workflows/gscc-function-gate.yml"
EXECUTION_WORKFLOW = ROOT / ".github/workflows/governed-execution.yml"


def check(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def tool(name: str) -> dict:
    for item in SNAPSHOT["catalogue"]["tools"]:
        if item.get("name") == name:
            return item
    raise AssertionError(f"missing fixture tool {name}")


def sample_package() -> dict:
    return {
        "schema_version": "1.0.0",
        "operation_id": "TEST-GSCC-FUNCTION-GATE",
        "intent": "DEPLOY_APPLICATION",
        "project_id": "brvmchainsolution",
        "repository": "chainsolutions-wealthtech/Governed-Repository-Template",
        "expected_head": "a" * 40,
        "authority": {
            "approved": True,
            "grants": ["SCOPED_DEPLOY"],
            "scope": {"project_id": "brvmchainsolution", "server_id": "S2"},
            "decision_ref": "TEST-DECISION",
        },
        "parameters": {},
        "bindings": {
            "capabilities": {},
            "credentials": {},
            "steps": {
                "preflight": [{
                    "backend": "MCP_DIRECT",
                    "capability": "SERVER_RUNTIME_OBSERVATION",
                    "tool": "docker_status_s2",
                    "arguments": {},
                }],
                "execute": [{
                    "backend": "MCP_DIRECT",
                    "capability": "DEPLOYMENT_RUNTIME_CHANGE",
                    "tool": "deploy_project_s2",
                    "arguments": {"project": "brvmchainsolution"},
                }],
                "verify": [{
                    "backend": "MCP_DIRECT",
                    "capability": "SERVER_RUNTIME_OBSERVATION",
                    "tool": "docker_status_s2",
                    "arguments": {},
                }],
                "rollback": [],
            },
        },
    }


def main() -> None:
    source_head = "b" * 40
    read_tool = tool("docker_status_s2")
    write_tool = tool("deploy_project_s2")

    envelope = gate.build_function_envelope(
        snapshot=SNAPSHOT,
        function_name="deploy_project_s2",
        repository="chainsolutions-wealthtech/Governed-Repository-Template",
        source_head=source_head,
        operation_id="OP-1",
        intent="DEPLOY_APPLICATION",
        capability="DEPLOYMENT_RUNTIME_CHANGE",
        phase="execute",
        arguments={"project": "brvmchainsolution"},
        session_id="session-test",
        connection_ref="gscc:test",
    )
    check(envelope["function_name"] == "deploy_project_s2", "function name")
    check(envelope["contract_digest"] == write_tool["contract_digest"], "contract digest")
    check(envelope["surface"] == write_tool["surface"], "surface")
    check(envelope["authority_required"] == write_tool["authority_required"], "authority class")
    check(envelope["argument_keys"] == ["project"], "argument keys only")
    check("arguments" not in envelope, "raw arguments must not be forwarded")
    check("project" not in json.dumps(envelope.get("argument_value_digest", "")), "argument values stay opaque")
    check(envelope["source_head"] == source_head, "exact source head")
    check(envelope["session_id"] == "session-test", "session binding")
    check(envelope["connection_ref"] == "gscc:test", "connection binding")

    route = gate.route_for_function(envelope)
    expected = [
        "GSCC_ATTACH_OR_RESUME",
        "FUNCTION_CONTRACT_ATTEST",
        "CONTEXT_BIND",
        "CAPABILITY_MATCH",
        "AUTHORITY_CLASSIFY",
        "CLAIM_COLLISION_CHECK",
        "EXACT_HEAD_CHECK",
        "PREFLIGHT",
        "INVOCATION_GATE",
        "EXECUTE_IF_SEPARATELY_AUTHORIZED",
        "VERIFY",
        "VALIDATION_RECEIPT",
    ]
    check(route["steps"] == expected, "end-to-end route")
    check(route["mutation_authority_granted"] is False, "route never grants mutation authority")

    receipt = gate.validate_exposure(
        snapshot=SNAPSHOT,
        function_name="docker_status_s2",
        repository="chainsolutions-wealthtech/Governed-Repository-Template",
        source_head=source_head,
        expected_contract_digest=read_tool["contract_digest"],
    )
    check(receipt["status"] == "VALIDATED_FOR_GOVERNED_EXPOSURE", "read tool exposure validation")
    check(receipt["gscc_required_for_every_invocation"] is True, "every invocation must re-enter GSCC")
    check(receipt["mutation_authority_granted"] is False, "exposure != mutation authority")
    check(receipt["invocation_authority_granted"] is False, "exposure != invocation authority")
    check(receipt["validation_digest"], "receipt digest")

    try:
        gate.validate_exposure(
            snapshot=SNAPSHOT,
            function_name="docker_status_s2",
            repository="chainsolutions-wealthtech/Governed-Repository-Template",
            source_head=source_head,
            expected_contract_digest="0" * 64,
        )
    except gate.FunctionGateError as exc:
        check(exc.code == "FUNCTION_CONTRACT_MOVED", "contract mismatch fail-closed")
    else:
        raise AssertionError("contract mismatch accepted")

    try:
        gate.validate_exposure(
            snapshot=SNAPSHOT,
            function_name="not_a_real_tool",
            repository="chainsolutions-wealthtech/Governed-Repository-Template",
            source_head=source_head,
        )
    except gate.FunctionGateError as exc:
        check(exc.code == "FUNCTION_NOT_IN_CANONICAL_CATALOGUE", "unknown tool fail-closed")
    else:
        raise AssertionError("unknown tool accepted")

    package_receipt = gate.validate_package(
        snapshot=SNAPSHOT,
        package=sample_package(),
        repository="chainsolutions-wealthtech/Governed-Repository-Template",
        source_head=source_head,
    )
    check(package_receipt["status"] == "GSCC_FUNCTION_PATH_VALIDATED", "package gate")
    check(package_receipt["function_count"] == 2, "deduplicate repeated tool use")
    check(set(package_receipt["functions"]) == {"docker_status_s2", "deploy_project_s2"}, "all MCP functions covered")
    check(package_receipt["route_complete"] is True, "route complete")
    check(package_receipt["mutation_authority_granted"] is False, "gate does not grant package mutation authority")

    event = gate.gscc_context_event(
        package_receipt,
        source={"session_id": "session-test", "client_instance_id": "client-test"},
        target={"system": "gscc"},
    )
    check(event.kind == "EVENT" and event.type == "CONTEXT_UPDATE", "canonical GSCC event")
    check(event.payload["function_gate"]["status"] == "GSCC_FUNCTION_PATH_VALIDATED", "receipt enters GSCC")
    serialized = event.serialize()
    for forbidden in ("password", "private_key", "raw_prompt", "transcript", "chain_of_thought"):
        check(forbidden not in serialized.lower(), f"forbidden payload field {forbidden}")

    for item in (read_tool, write_tool):
        check(item.get("governed_exposure_gate") == "GSCC_REQUIRED", "catalogue must mark GSCC gate")
        check(item.get("governed_exposure_status") == "REQUIRES_RUNTIME_VALIDATION", "catalogue is not execution authority")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for marker in (
        "workflow_call:",
        "workflow_dispatch:",
        "repository_dispatch:",
        "gscc_function_gate",
        "expected_source_head",
        "gscc_function_gate.py",
        "GSCC_FUNCTION_GATE_REQUIRES_CANONICAL_MAIN",
        "actions/upload-artifact",
    ):
        check(marker in workflow, f"function gate workflow missing {marker}")

    execution = EXECUTION_WORKFLOW.read_text(encoding="utf-8")
    for marker in (
        "function-gate:",
        "uses: ./.github/workflows/gscc-function-gate.yml",
        "needs: function-gate",
        "GSCC_FUNCTION_GATE_VALIDATION_DIGEST",
    ):
        check(marker in execution, f"governed execution missing mandatory gate {marker}")

    print("GSCC_UNIVERSAL_FUNCTION_GATE_TEST_PASS")


if __name__ == "__main__":
    main()
