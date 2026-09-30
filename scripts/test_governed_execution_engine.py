#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import os
import tempfile
from pathlib import Path

import governed_execution_engine as gee

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = gee.load_json(gee.REGISTRY_PATH)
SNAPSHOT = gee.load_json(gee.SNAPSHOT_PATH)

SERVER_INTENTS = {
    "CREATE_PROJECT_DIRECTORY",
    "CREATE_SUBDOMAIN",
    "CREATE_NEW_DOMAIN_BINDING",
    "ALLOCATE_APPLICATION_PORT",
    "CONFIGURE_REVERSE_PROXY",
    "PROVISION_TLS",
    "CREATE_DATABASE",
    "BIND_REPOSITORY_TO_SERVER_PROJECT",
    "DEPLOY_APPLICATION",
    "CONFIGURE_ENV_AND_SECRETS",
    "CONFIGURE_PROCESS_OR_SERVICE",
    "CONFIGURE_SCHEDULED_JOB",
    "CONFIGURE_OBSERVABILITY",
    "CONFIGURE_BACKUP_AND_ROLLBACK",
    "PRODUCTION_ATTESTATION",
}
IDENTITY_INTENTS = {
    "DISCOVER_CREDENTIAL_REQUIREMENT",
    "MINT_GITHUB_APP_INSTALLATION_TOKEN",
    "PROVISION_GITHUB_SECRET",
    "MINT_EPHEMERAL_SSH_CERTIFICATE",
    "CREATE_OR_BIND_SERVER_APPLICATION_SECRET",
    "CREATE_DATABASE_CREDENTIAL",
    "CREATE_DNS_AUTOMATION_CREDENTIAL",
    "ROTATE_CREDENTIAL",
    "REVOKE_CREDENTIAL",
    "VERIFY_SECRET_OR_CREDENTIAL_WITHOUT_READBACK",
}


def package(intent: str, *, approved: bool | None = None, project_id: str = "brvmchainsolution") -> dict:
    spec = REGISTRY["intents"][intent]
    if approved is None:
        approved = bool(spec["side_effecting"])
    grants = [spec["required_authority"]] if approved else []
    return {
        "schema_version": "1.0.0",
        "operation_id": f"TEST-{intent}",
        "intent": intent,
        "project_id": project_id,
        "authority": {
            "approved": approved,
            "grants": grants,
            "scope": {"project_id": project_id},
            "decision_ref": "TEST-DECISION-001" if approved else None,
        },
        "parameters": {},
        "bindings": {"capabilities": {}, "credentials": {}, "steps": {}},
    }


def assert_registry_complete() -> None:
    intents = set(REGISTRY["intents"])
    expected = SERVER_INTENTS | IDENTITY_INTENTS
    if intents != expected:
        raise SystemExit(f"EXECUTION_ENGINE_TEST_FAILED: registry mismatch missing={expected-intents} extra={intents-expected}")
    for intent, spec in REGISTRY["intents"].items():
        if spec["handler"] not in {
            "MCP_RECIPE", "PLAN_ONLY", "GITHUB_APP_TOKEN", "GITHUB_SECRET",
            "SSH_OIDC_CERT", "CREDENTIAL_LIFECYCLE", "CREDENTIAL_VERIFY",
        }:
            raise SystemExit(f"EXECUTION_ENGINE_TEST_FAILED: handler missing {intent}")
        if "required_authority" not in spec or "side_effecting" not in spec:
            raise SystemExit(f"EXECUTION_ENGINE_TEST_FAILED: incomplete spec {intent}")


def assert_all_intents_compile_without_side_effect() -> None:
    for intent, spec in REGISTRY["intents"].items():
        p = package(intent)
        # MCP recipes with current missing capabilities are expected to compile into a blocked plan.
        result = gee.execute(p, do_execute=False, registry=REGISTRY, snapshot=SNAPSHOT)
        if result["mode"] != "DRY_RUN":
            raise SystemExit(f"EXECUTION_ENGINE_TEST_FAILED: {intent} did not stay dry-run")
        if result["status"] not in {"READY", "BLOCKED_MISSING_CAPABILITY"}:
            raise SystemExit(f"EXECUTION_ENGINE_TEST_FAILED: {intent} unexpected dry-run status {result['status']}")
        if result["secret_values_persisted"] is not False:
            raise SystemExit(f"EXECUTION_ENGINE_TEST_FAILED: {intent} secret persistence")


def assert_current_mcp_gap_is_fail_closed() -> None:
    p = package("CREATE_SUBDOMAIN")
    result = gee.execute(p, do_execute=False, registry=REGISTRY, snapshot=SNAPSHOT)
    if result["status"] != "BLOCKED_MISSING_CAPABILITY":
        raise SystemExit("EXECUTION_ENGINE_TEST_FAILED: CREATE_SUBDOMAIN should be blocked until generic web/DNS/TLS writes exist")
    missing = set(result["plan"]["missing_capabilities_or_bindings"])
    if not {"WEB_HOSTING_CHANGE", "DOMAIN_DNS_CHANGE", "TLS_CHANGE"} & missing:
        raise SystemExit("EXECUTION_ENGINE_TEST_FAILED: subdomain capability gaps not explicit")


def assert_available_deploy_can_be_bound() -> None:
    p = package("DEPLOY_APPLICATION", project_id="brvmchainsolution")
    p["bindings"]["steps"] = {
        "preflight": [],
        "execute": [{
            "backend": "MCP_DIRECT",
            "capability": "DEPLOYMENT_RUNTIME_CHANGE",
            "tool": "deploy_project_s2",
            "arguments": {"project_id": "brvmchainsolution"},
        }],
        "verify": [],
        "rollback": [],
    }
    result = gee.execute(p, do_execute=False, registry=REGISTRY, snapshot=SNAPSHOT)
    if result["status"] != "READY":
        raise SystemExit(f"EXECUTION_ENGINE_TEST_FAILED: known scoped deployment should compile READY {result}")


def assert_production_attestation_can_bind_reads() -> None:
    p = package("PRODUCTION_ATTESTATION", approved=False, project_id="brvmchainsolution")
    p["bindings"]["steps"] = {
        "preflight": [{
            "backend": "MCP_DIRECT",
            "capability": "SERVER_RUNTIME_OBSERVATION",
            "tool": "docker_status_s2",
            "arguments": {},
        }],
        "execute": [],
        "verify": [{
            "backend": "MCP_DIRECT",
            "capability": "DOMAIN_WEB_OBSERVATION",
            "tool": "list_domains_s2",
            "arguments": {},
        }],
        "rollback": [],
    }
    result = gee.execute(p, do_execute=False, registry=REGISTRY, snapshot=SNAPSHOT)
    if result["status"] != "READY":
        raise SystemExit("EXECUTION_ENGINE_TEST_FAILED: production attestation read path should be ready")


def assert_authority_gate() -> None:
    p = package("DEPLOY_APPLICATION", approved=False)
    try:
        gee.execute(p, do_execute=False, registry=REGISTRY, snapshot=SNAPSHOT)
    except gee.ExecutionError as exc:
        if exc.code != "EXECUTION_AUTHORITY_NOT_APPROVED":
            raise
    else:
        raise SystemExit("EXECUTION_ENGINE_TEST_FAILED: mutation accepted without authority")


def assert_secret_in_package_rejected() -> None:
    p = package("PROVISION_GITHUB_SECRET")
    p["parameters"] = {
        "repository": "owner/repo",
        "secret_name": "EXAMPLE",
        "secret_value": "must-never-live-here",
    }
    try:
        gee.execute(p, do_execute=False, registry=REGISTRY, snapshot=SNAPSHOT)
    except gee.ExecutionError as exc:
        if exc.code != "PACKAGE_CONTAINS_SECRET_VALUE":
            raise
    else:
        raise SystemExit("EXECUTION_ENGINE_TEST_FAILED: plaintext secret package accepted")


def assert_redaction() -> None:
    value = gee.redact({
        "token": "sensitive",
        "nested": {"password": "sensitive", "safe": "ok"},
        "secret_ref": "env:SAFE_REFERENCE",
    })
    if value["token"] != "***REDACTED***" or value["nested"]["password"] != "***REDACTED***":
        raise SystemExit("EXECUTION_ENGINE_TEST_FAILED: redaction")
    if value["secret_ref"] != "env:SAFE_REFERENCE":
        raise SystemExit("EXECUTION_ENGINE_TEST_FAILED: secret reference should remain visible")


class FakeMcpClient:
    calls: list[tuple[str, dict]] = []
    fail_tool: str | None = None

    def __init__(self, endpoint: str, token: str):
        self.endpoint = endpoint
        self.token = token

    def call_tool(self, name: str, arguments: dict) -> dict:
        FakeMcpClient.calls.append((name, copy.deepcopy(arguments)))
        if name == FakeMcpClient.fail_tool:
            raise gee.ExecutionError("FAKE_TOOL_FAILURE", name)
        return {"result": {"ok": True, "tool": name}}


def assert_mcp_execute_and_verify() -> None:
    original_client = gee.McpClient
    old_token = os.environ.get("GOVERNED_MCP_AUTH_TOKEN")
    old_url = os.environ.get("GOVERNED_MCP_URL")
    try:
        gee.McpClient = FakeMcpClient
        FakeMcpClient.calls = []
        FakeMcpClient.fail_tool = None
        os.environ["GOVERNED_MCP_AUTH_TOKEN"] = "test-only-not-persisted"
        os.environ["GOVERNED_MCP_URL"] = "https://mcp.example.test/mcp"
        p = package("DEPLOY_APPLICATION", project_id="brvmchainsolution")
        p["bindings"]["steps"] = {
            "preflight": [],
            "execute": [{
                "capability": "DEPLOYMENT_RUNTIME_CHANGE",
                "tool": "deploy_project_s2",
                "arguments": {"project_id": "brvmchainsolution"},
            }],
            "verify": [{
                "capability": "SERVER_RUNTIME_OBSERVATION",
                "tool": "docker_status_s2",
                "arguments": {},
            }],
            "rollback": [],
        }
        result = gee.execute(p, do_execute=True, registry=REGISTRY, snapshot=SNAPSHOT)
        if result["status"] != "PASS":
            raise SystemExit(f"EXECUTION_ENGINE_TEST_FAILED: fake MCP execution {result}")
        if [name for name, _ in FakeMcpClient.calls] != ["deploy_project_s2", "docker_status_s2"]:
            raise SystemExit("EXECUTION_ENGINE_TEST_FAILED: MCP execute/verify order")
        serialized = json.dumps(result)
        if "test-only-not-persisted" in serialized:
            raise SystemExit("EXECUTION_ENGINE_TEST_FAILED: MCP token leaked into receipt")
    finally:
        gee.McpClient = original_client
        if old_token is None:
            os.environ.pop("GOVERNED_MCP_AUTH_TOKEN", None)
        else:
            os.environ["GOVERNED_MCP_AUTH_TOKEN"] = old_token
        if old_url is None:
            os.environ.pop("GOVERNED_MCP_URL", None)
        else:
            os.environ["GOVERNED_MCP_URL"] = old_url


def assert_head_moved_fails_before_side_effect() -> None:
    original_head = gee.current_repository_head
    original_target = gee._target_token
    try:
        gee.current_repository_head = lambda token, repository: "b" * 40
        gee._target_token = lambda runtime, generated, parameters: "fake-token"
        p = package("PROVISION_GITHUB_SECRET")
        p["repository"] = "owner/repo"
        p["expected_head"] = "a" * 40
        p["parameters"] = {
            "repository": "owner/repo",
            "secret_name": "EXAMPLE",
            "value_ref": "generated:32",
        }
        result = gee.execute(p, do_execute=True, registry=REGISTRY, snapshot=SNAPSHOT)
        if result["failure_code"] != "HEAD_MOVED" or result["status"] != "FAILED_NO_SIDE_EFFECT_CONFIRMED":
            raise SystemExit("EXECUTION_ENGINE_TEST_FAILED: HEAD_MOVED not fail-closed")
    finally:
        gee.current_repository_head = original_head
        gee._target_token = original_target


def assert_rollback_after_verify_failure() -> None:
    # Use a synthetic snapshot extension only inside the unit test to prove the generic rollback mechanism.
    snapshot = copy.deepcopy(SNAPSHOT)
    snapshot["capability_map"]["TEST_MUTATION"] = {
        "availability": "AVAILABLE_GENERIC",
        "candidate_tools": [{"tool": "test_mutate", "scope": {"mode": "GENERIC", "project_ids": []}}],
    }
    snapshot["capability_map"]["TEST_VERIFY"] = {
        "availability": "AVAILABLE_GENERIC",
        "candidate_tools": [{"tool": "test_verify", "scope": {"mode": "GENERIC", "project_ids": []}}],
    }
    snapshot["capability_map"]["TEST_ROLLBACK"] = {
        "availability": "AVAILABLE_GENERIC",
        "candidate_tools": [{"tool": "test_rollback", "scope": {"mode": "GENERIC", "project_ids": []}}],
    }
    registry = copy.deepcopy(REGISTRY)
    registry["intents"]["TEST_ROLLBACK_INTENT"] = {
        "handler": "MCP_RECIPE",
        "required_authority": "SCOPED_RUNTIME_WRITE",
        "required_capabilities": ["TEST_MUTATION"],
        "side_effecting": True,
        "phases": ["preflight", "execute", "verify", "rollback"],
    }
    p = {
        "schema_version": "1.0.0",
        "operation_id": "TEST-ROLLBACK",
        "intent": "TEST_ROLLBACK_INTENT",
        "project_id": "test-project",
        "authority": {"approved": True, "grants": ["SCOPED_RUNTIME_WRITE"], "scope": {}, "decision_ref": "D1"},
        "parameters": {},
        "bindings": {
            "capabilities": {},
            "credentials": {},
            "steps": {
                "preflight": [],
                "execute": [{"capability": "TEST_MUTATION", "tool": "test_mutate", "arguments": {}}],
                "verify": [{"capability": "TEST_VERIFY", "tool": "test_verify", "arguments": {}}],
                "rollback": [{"capability": "TEST_ROLLBACK", "tool": "test_rollback", "arguments": {}}],
            },
        },
    }

    original_client = gee.McpClient
    old_token = os.environ.get("GOVERNED_MCP_AUTH_TOKEN")
    old_url = os.environ.get("GOVERNED_MCP_URL")
    try:
        gee.McpClient = FakeMcpClient
        FakeMcpClient.calls = []
        FakeMcpClient.fail_tool = "test_verify"
        os.environ["GOVERNED_MCP_AUTH_TOKEN"] = "test-only"
        os.environ["GOVERNED_MCP_URL"] = "https://mcp.example.test/mcp"
        result = gee.execute(p, do_execute=True, registry=registry, snapshot=snapshot)
        if result["status"] != "FAILED_ROLLED_BACK":
            raise SystemExit(f"EXECUTION_ENGINE_TEST_FAILED: rollback status {result}")
        if [name for name, _ in FakeMcpClient.calls] != ["test_mutate", "test_verify", "test_rollback"]:
            raise SystemExit("EXECUTION_ENGINE_TEST_FAILED: rollback sequence")
    finally:
        gee.McpClient = original_client
        FakeMcpClient.fail_tool = None
        if old_token is None:
            os.environ.pop("GOVERNED_MCP_AUTH_TOKEN", None)
        else:
            os.environ["GOVERNED_MCP_AUTH_TOKEN"] = old_token
        if old_url is None:
            os.environ.pop("GOVERNED_MCP_URL", None)
        else:
            os.environ["GOVERNED_MCP_URL"] = old_url


def assert_secret_reference_runtime_only() -> None:
    runtime = gee.RuntimeSecretStore()
    generated = {}
    old = os.environ.get("TEST_EXECUTION_SECRET")
    try:
        os.environ["TEST_EXECUTION_SECRET"] = "value-never-serialized"
        if gee.resolve_secret_reference("env:TEST_EXECUTION_SECRET", runtime, generated) != "value-never-serialized":
            raise SystemExit("EXECUTION_ENGINE_TEST_FAILED: env secret resolution")
        generated_value = gee.resolve_secret_reference("generated:32", runtime, generated)
        if len(generated_value) < 32:
            raise SystemExit("EXECUTION_ENGINE_TEST_FAILED: generated secret too short")
        runtime.put("TOKEN", "runtime-value")
        if gee.resolve_secret_reference("runtime:TOKEN", runtime, generated) != "runtime-value":
            raise SystemExit("EXECUTION_ENGINE_TEST_FAILED: runtime secret resolution")
    finally:
        runtime.clear()
        if old is None:
            os.environ.pop("TEST_EXECUTION_SECRET", None)
        else:
            os.environ["TEST_EXECUTION_SECRET"] = old


def main() -> None:
    assert_registry_complete()
    assert_all_intents_compile_without_side_effect()
    assert_current_mcp_gap_is_fail_closed()
    assert_available_deploy_can_be_bound()
    assert_production_attestation_can_bind_reads()
    assert_authority_gate()
    assert_secret_in_package_rejected()
    assert_redaction()
    assert_mcp_execute_and_verify()
    assert_head_moved_fails_before_side_effect()
    assert_rollback_after_verify_failure()
    assert_secret_reference_runtime_only()
    print("GOVERNED_EXECUTION_ENGINE_TEST_PASS")


if __name__ == "__main__":
    main()
