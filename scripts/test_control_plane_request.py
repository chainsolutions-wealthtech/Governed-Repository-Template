#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from governed_request import apply_answer, apply_evidence, new_request

SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40
SHA_D = "d" * 40


def materialize(expected: Any) -> Any:
    if isinstance(expected, dict):
        return {key: materialize(value) for key, value in expected.items()}
    if isinstance(expected, list):
        return [] if expected == [] else ["selftest"]
    if isinstance(expected, bool) or isinstance(expected, int):
        return expected
    if isinstance(expected, str) and expected.startswith("<") and expected.endswith(">"):
        token = expected[1:-1]
        if token == "40-hex-sha":
            return "f" * 40
        if token == "integer":
            return 1
        if token == "array":
            return ["selftest"]
        if token == "boolean":
            return True
        if token in {"integer-or-null", "boolean-or-null"}:
            return None
        if token == "optional":
            return "observed"
        if token == "branch":
            return "main"
        if token == "version":
            return "2.3.0"
        if token == "id":
            return "123456"
        if token == "status":
            return "DISCOVERY_REQUIRED"
        if token == "PASS-or-documented-baseline":
            return "PASS"
        return "selftest"
    return expected


def answer_required(state: dict, values: dict[str, Any]) -> dict:
    guard = 0
    while state["next_request"] and state["next_request"]["kind"] in {"QUESTION", "AGENT_REQUEST"}:
        guard += 1
        if guard > 40:
            raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: question loop")
        field = state["next_request"]["field"]
        if field not in values:
            raise SystemExit(f"CONTROL_PLANE_SELFTEST_FAILED: missing fixture for {field}")
        state = apply_answer(state, field, values[field])
    return state


def approve_and_execute(state: dict) -> dict:
    if state["next_request"]["kind"] == "PLAN_APPROVAL":
        state = apply_answer(state, "plan_approved", True)
    elif state["next_request"]["kind"] != "ACTION_REQUEST":
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: plan/action request not available")

    guard = 0
    while state["next_request"] and state["next_request"]["kind"] == "ACTION_REQUEST":
        guard += 1
        if guard > 20:
            raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: action loop")
        current = state["next_request"]
        evidence = materialize(current["required_evidence"])
        state = apply_evidence(state, current["action_id"], "PASS", evidence)
    if state["status"] != "HANDOFF_READY":
        raise SystemExit(f"CONTROL_PLANE_SELFTEST_FAILED: expected HANDOFF_READY, got {state['status']}")
    return state


def run_case(name: str, values: dict[str, Any], expected_target: str, expected_operation: str) -> dict:
    state = new_request(f"SELFTEST-{name}", "selftest-agent", "test", f"case {name}")
    state = answer_required(state, values)
    if state["status"] not in {"PLAN_READY", "EXECUTING_PREPARATION"}:
        raise SystemExit(f"CONTROL_PLANE_SELFTEST_FAILED: {name} plan/action not ready")
    state = approve_and_execute(state)
    handoff = state["handoff"]
    if handoff["target_repository"] != expected_target:
        raise SystemExit(f"CONTROL_PLANE_SELFTEST_FAILED: {name} target mismatch")
    if handoff["allowed_next_operation"] != expected_operation:
        raise SystemExit(f"CONTROL_PLANE_SELFTEST_FAILED: {name} next operation mismatch")
    return state


def main() -> None:
    create_sequence = new_request("SELFTEST-CREATE-SEQUENCE", "agent", "test", None)
    if create_sequence["next_request"]["field"] != "entry_action":
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: create sequence entry action missing")
    create_sequence = apply_answer(create_sequence, "entry_action", "CREATE_NEW_REPOSITORY")
    if create_sequence["next_request"]["field"] != "creation_target_owner":
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: create must ask owner immediately")
    if create_sequence["next_request"].get("choices") != ["chainsolutions-wealthtech", "Wealthtechinnovations", "Patricked"]:
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: create owner choices are incorrect")
    create_sequence = apply_answer(create_sequence, "creation_target_owner", "chainsolutions-wealthtech")
    if create_sequence["next_request"]["field"] != "repository_name":
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: create must ask repository name second")
    create_sequence = apply_answer(create_sequence, "repository_name", "sequence-selftest")
    if create_sequence["next_request"]["kind"] != "ACTION_REQUEST":
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: create must proceed directly to creation action")
    if create_sequence["next_request"]["action_id"] != "PREP-001":
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: create action PREP-001 missing")
    if create_sequence["next_request"].get("target") != "chainsolutions-wealthtech/sequence-selftest":
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: create target is incorrect")

    create = run_case(
        "create",
        {
            "entry_action": "CREATE_NEW_REPOSITORY",
            "creation_target_owner": "chainsolutions-wealthtech",
            "repository_name": "control-plane-create-selftest",
        },
        "chainsolutions-wealthtech/control-plane-create-selftest",
        "DISCOVER_PROJECT_BASELINE",
    )
    if create["handoff"]["expected_head_sha"] is None:
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: create handoff missing head")

    adopt = run_case(
        "adopt",
        {
            "entry_action": "ADOPT_EXISTING_REPOSITORY",
            "connection_intent": "CODE_CHANGE",
            "objective": "Adopt governance without overwriting existing project content",
            "target_repository": "chainsolutions-wealthtech/existing-project",
            "target_observation": {
                "exists": True,
                "default_branch": "main",
                "head_sha": SHA_A,
                "governance_detected": False,
                "workflows_detected": 2,
            },
            "integration_strategy": "DIRECT_CANONICAL_IF_AUTHORIZED",
            "adoption_authority": True,
        },
        "chainsolutions-wealthtech/existing-project",
        "CONTINUE_GOVERNED_WORK",
    )
    if not any(item["name"] == "APPLY_ADDITIVE_GOVERNANCE" for item in adopt["execution_plan"]):
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: adoption apply action missing")

    mapping = run_case(
        "map",
        {
            "entry_action": "MAP_EXISTING_PROJECT",
            "connection_intent": "REVIEW",
            "objective": "Map current architecture and design a target architecture",
            "target_repository": "chainsolutions-wealthtech/mapped-project",
            "target_observation": {
                "exists": True,
                "default_branch": "main",
                "head_sha": SHA_B,
                "governance_detected": True,
            },
            "mapping_scope": "CURRENT_AND_TARGET",
            "target_architecture_requested": True,
            "mapping_write_authority": False,
        },
        "chainsolutions-wealthtech/mapped-project",
        "APPLY_MAPPING_ARTIFACTS_OR_BEGIN_IMPLEMENTATION_IF_AUTHORIZED",
    )
    if not any(item["name"] == "BUILD_TARGET_ARCHITECTURE_AND_GAP" for item in mapping["execution_plan"]):
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: mapping target/gap action missing")

    lab = run_case(
        "lab",
        {
            "entry_action": "LAB_EVOLUTION",
            "connection_intent": "CODE_CHANGE",
            "objective": "Create an isolated laboratory evolution branch",
            "target_repository": "chainsolutions-wealthtech/lab-project",
            "target_observation": {
                "exists": True,
                "default_branch": "main",
                "head_sha": SHA_C,
                "governance_detected": True,
                "branch_protection_known": True,
            },
            "lab_branch_name": "claude/control-plane-selftest",
            "pr_required": True,
            "lab_authority": True,
        },
        "chainsolutions-wealthtech/lab-project",
        "BEGIN_LAB_EVOLUTION",
    )
    if lab["handoff"]["target_branch"] != "claude/control-plane-selftest":
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: lab branch missing from handoff")

    continuation = run_case(
        "continue",
        {
            "entry_action": "CONTINUE_GOVERNED_WORK",
            "connection_intent": "CODE_CHANGE",
            "objective": "Resume an existing governed work item",
            "target_repository": "chainsolutions-wealthtech/governed-project",
            "target_observation": {
                "exists": True,
                "default_branch": "main",
                "head_sha": SHA_D,
                "governance_detected": True,
                "next_action": "WORK-NEXT-001",
            },
            "existing_next_action": "WORK-NEXT-001",
        },
        "chainsolutions-wealthtech/governed-project",
        "WORK-NEXT-001",
    )
    if continuation["handoff"]["expected_head_sha"] is None:
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: continuation missing head")

    denied = new_request("SELFTEST-DENIED", "agent", "test", None)
    denied_values = {
        "entry_action": "ADOPT_EXISTING_REPOSITORY",
        "connection_intent": "CODE_CHANGE",
        "objective": "Denied adoption",
        "target_repository": "chainsolutions-wealthtech/denied-adoption",
        "target_observation": {
            "exists": True,
            "default_branch": "main",
            "head_sha": SHA_A,
            "governance_detected": False,
            "workflows_detected": 0,
        },
        "integration_strategy": "DIRECT_CANONICAL_IF_AUTHORIZED",
        "adoption_authority": False,
    }
    denied = answer_required(denied, denied_values)
    if denied["status"] != "HOLD_FOR_REVIEW":
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: authority denial did not hold")

    invalid = new_request("SELFTEST-EVIDENCE", "agent", "test", None)
    invalid = answer_required(invalid, {
        "entry_action": "CONTINUE_GOVERNED_WORK",
        "connection_intent": "CODE_CHANGE",
        "objective": "Evidence validation",
        "target_repository": "chainsolutions-wealthtech/governed-project",
        "target_observation": {
            "exists": True,
            "default_branch": "main",
            "head_sha": SHA_D,
            "governance_detected": True,
            "next_action": "WORK-NEXT-001",
        },
        "existing_next_action": "WORK-NEXT-001",
    })
    invalid = apply_answer(invalid, "plan_approved", True)
    try:
        apply_evidence(invalid, invalid["next_request"]["action_id"], "PASS", {})
    except ValueError:
        pass
    else:
        raise SystemExit("CONTROL_PLANE_SELFTEST_FAILED: empty evidence was accepted")

    print("GOVERNED_CONTROL_PLANE_REQUEST_SELFTEST_PASS")


if __name__ == "__main__":
    main()
