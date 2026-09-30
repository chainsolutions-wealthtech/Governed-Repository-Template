#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from control_plane_mcp_capability_snapshot import (
    AUTHORITY_ID,
    authority_for_surface,
    build_snapshot,
    classify_tool,
    derive_capability_map,
    derive_case_operation_map,
)


def envelope(result):
    return {"jsonrpc": "2.0", "id": 1, "result": result}


def tool_envelope(payload):
    return envelope({"content": [{"type": "text", "text": json.dumps(payload)}]})


def main():
    if authority_for_surface("read") != "READ_ONLY_DISCOVERY_AUTHORITY":
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: read authority")
    if authority_for_surface("scoped-write") != "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED":
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: scoped write authority")
    if authority_for_surface("operational-write") != "GOVERNED_OPERATIONAL_AUTHORITY_REQUIRED":
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: operational authority")
    tags = classify_tool({"name": "deploy_project_s2", "description": "Deploy repository on S2 runtime"})
    if not {"DEPLOYMENT", "REPOSITORY", "SERVER_RUNTIME"}.intersection(tags):
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: tool classification")

    inventory = {
        "repository": "Patricked-code/MCP",
        "source": {
            "githubHead": "a" * 40,
            "runtimeRevision": "a" * 40,
            "liveStateVersion": 12,
            "inventoryDigest": "inv",
            "catalogueDigest": "cat",
        },
        "catalogue": {
            "catalogueVersion": 1,
            "catalogueDigest": "cat",
            "tools": [
                {"name": "ping", "title": "Ping", "description": "Read health", "surface": "read", "contractDigest": "1"},
                {"name": "github_get_repository_state", "title": "Repo", "description": "Read repository state", "surface": "read", "contractDigest": "2"},
                {"name": "github_create_branch", "title": "Branch", "description": "Create governed branch", "surface": "scoped-write", "contractDigest": "3"},
                {"name": "get_project_context", "title": "Context", "description": "Read project server/domain context", "surface": "read", "contractDigest": "4"},
                {"name": "list_domains_s1", "title": "Domains", "description": "List domains S1", "surface": "read", "contractDigest": "5"},
                {"name": "docker_status_s1", "title": "Docker", "description": "Read Docker status S1", "surface": "read", "contractDigest": "6"},
                {"name": "deploy_project_s2", "title": "Deploy", "description": "Deploy repository on S2", "surface": "scoped-write", "contractDigest": "7"},
                {"name": "mcp_get_current_state_inventory", "title": "State", "description": "Read governed current state inventory", "surface": "read", "contractDigest": "8"},
                {"name": "mcp_claim_next_governed_task", "title": "Claim", "description": "Claim next governed task", "surface": "operational-write", "contractDigest": "9"},
            ],
        },
        "contradictions": [],
    }
    snapshot = build_snapshot(
        endpoint="https://mcp.example.test/mcp",
        observed_at="2026-09-30T00:00:00+00:00",
        source_head="b" * 40,
        init_response=envelope({"protocolVersion": "2025-06-18", "serverInfo": {"name": "bridge", "version": "1"}}),
        tools_response=envelope({"tools": [
            {"name": "ping", "title": "Ping", "description": "Read health", "annotations": {"readOnlyHint": True, "destructiveHint": False}, "inputSchema": {}},
            {"name": "github_get_repository_state", "title": "Repo", "description": "Read repository state", "annotations": {"readOnlyHint": True, "destructiveHint": False}, "inputSchema": {"type": "object", "properties": {"organization": {"type": "string"}, "repository": {"type": "string"}}, "required": ["organization", "repository"]}},
            {"name": "github_create_branch", "title": "Branch", "description": "Create governed branch", "annotations": {"readOnlyHint": False, "destructiveHint": False}, "inputSchema": {"type": "object", "properties": {"organization": {"type": "string"}, "repository": {"type": "string"}, "branch": {"type": "string"}, "baseSha": {"type": "string"}}, "required": ["organization", "repository", "branch", "baseSha"]}},
            {"name": "get_project_context", "title": "Context", "description": "Read project server/domain context", "annotations": {"readOnlyHint": True, "destructiveHint": False}, "inputSchema": {}},
            {"name": "list_domains_s1", "title": "Domains", "description": "List domains S1", "annotations": {"readOnlyHint": True, "destructiveHint": False}, "inputSchema": {}},
            {"name": "docker_status_s1", "title": "Docker", "description": "Read Docker status S1", "annotations": {"readOnlyHint": True, "destructiveHint": False}, "inputSchema": {}},
            {"name": "deploy_project_s2", "title": "Deploy", "description": "Deploy repository on S2", "annotations": {"readOnlyHint": False, "destructiveHint": True}, "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "enum": ["demo"]}}, "required": ["project"]}},
            {"name": "mcp_get_current_state_inventory", "title": "State", "description": "Read governed current state inventory", "annotations": {"readOnlyHint": True, "destructiveHint": False}, "inputSchema": {}},
            {"name": "mcp_claim_next_governed_task", "title": "Claim", "description": "Claim next governed task", "annotations": {"readOnlyHint": False, "destructiveHint": False}, "inputSchema": {"type": "object"}},
        ]}),
        resources_response=envelope({"resources": [{"name": "inventory", "uri": "mcp://wealthtech/current-state/inventory", "mimeType": "application/json"}]}),
        inventory_response=tool_envelope(inventory),
        project_context_response=tool_envelope({"servers": {
            "s1": {"id": "s1", "label": "S1", "host": "212.227.212.33", "port": 22, "username": "root", "privateKeyPath": "/SECRET", "protectedDomains": ["example.test"]},
        }}),
        write_context_response=tool_envelope({"mode": "scoped-write-tools", "free_shell": False, "run_command_s1": False, "run_command_s2": False, "sql": "SELECT uniquement", "projects": "demo: Demo project\n  path: /var/www/demo\n  note: bounded project\nsecond_project: Second project\n  path: /srv/second"}),
        prior_snapshot={"refresh_sequence": 4},
    )
    if snapshot["authority_id"] != AUTHORITY_ID or snapshot["refresh_sequence"] != 5:
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: identity/sequence")
    if snapshot["mutation_authority_granted"] is not False or snapshot["secrets_persisted"] is not False:
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: authority/secrets")
    if any(key in snapshot["servers"]["s1"] for key in ("host","port","username","privateKeyPath")):
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: server connection coordinates leaked")
    if snapshot["servers"]["s1"].get("connection_coordinates_persisted") is not False:
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: server coordinate policy")
    if snapshot["write_context_summary"].get("project_ids") != ["demo", "second_project"]:
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: project id summary / metadata-line filtering")
    if snapshot["write_context_summary"].get("project_paths_persisted") is not False:
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: project paths policy")
    if snapshot["catalogue"]["counts"]["tools"] != 9:
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: tool count")
    deploy = next(item for item in snapshot["catalogue"]["tools"] if item["name"] == "deploy_project_s2")
    if deploy["surface"] != "scoped-write" or deploy["authority_required"] != "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED":
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: write tool authority")
    capabilities = derive_capability_map(snapshot["catalogue"]["tools"])
    if capabilities["SERVER_FILESYSTEM_CHANGE"]["availability"] != "NOT_EXPOSED_BY_CURRENT_MCP_CATALOGUE":
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: missing generic server filesystem surface must remain explicit")
    database_cap = capabilities["DATABASE_READ_OBSERVATION"]
    if database_cap["availability"] != "AVAILABLE_ONLY_PROJECT_SPECIFIC":
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: project-specific database observation scope")
    deploy_cap = capabilities["DEPLOYMENT_RUNTIME_CHANGE"]
    if deploy_cap["availability"] != "AVAILABLE_PROJECT_REGISTRY_SCOPED":
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: project-registry scoped deployment classification")
    if deploy_cap["candidate_tools"][0]["scope"].get("project_ids") != ["demo"]:
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: deployment registry scope")

    mapping = derive_case_operation_map(snapshot["catalogue"]["tools"])
    adopt = mapping["ADOPT_EXISTING_REPOSITORY"]
    if adopt["pre_mutation_live_refresh_required"] is not True:
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: mapping refresh gate")
    if len(adopt["sequence"]) > 12:
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: case mapping must remain capability-sized, not tool-sized")
    first = adopt["sequence"][0]
    if first["capability"] != "GIT_REPOSITORY_OBSERVATION" or first["question_policy"] != "OBSERVE_FIRST;_ASK_OWNER_ONLY_IF_UNRESOLVED_OR_DECISION":
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: observation-first adaptive questionnaire")
    fs = next(step for step in adopt["sequence"] if step["capability"] == "SERVER_FILESYSTEM_CHANGE")
    if fs["availability"] != "NOT_EXPOSED_BY_CURRENT_MCP_CATALOGUE" or fs["missing_surface_action"] != "PREPARE_SCOPED_CAPABILITY_REQUEST_ONLY_WHEN_OPERATION_IS_REQUIRED":
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: missing capability request planning")
    if "repository.exists" not in adopt["observable_target_fields"]:
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: observed repository facts must feed questionnaire")
    if snapshot["question_resolution_contract"]["never_reask_fresh_resolved_fact"] is not True:
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: resolved facts must not be re-asked")
    if "input_schema" in deploy or not isinstance(deploy.get("input_fields"), list):
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: compact input field summary")
    if snapshot["relational_projection"]["status"] != "PENDING_PROJECTION_GMC_INTEGRATION":
        raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: relational projection")

    serialized = json.dumps(snapshot)
    for forbidden in ["/SECRET", "privateKeyPath", "Authorization: Bearer", "212.227.212.33", "/var/www/"]:
        if forbidden in serialized:
            raise SystemExit("MCP_CAPABILITY_SNAPSHOT_SELFTEST_FAILED: secret-like data leaked")

    print("MCP_CAPABILITY_SNAPSHOT_SELFTEST_PASS")


if __name__ == "__main__":
    main()
