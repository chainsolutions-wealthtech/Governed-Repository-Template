#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import pathlib
import urllib.error
import urllib.request
from datetime import datetime, timezone

AUTHORITY_ID = "CP-MCP-CAP-001"
DEFAULT_ENDPOINT = "https://mcp.wealthtechinnovations.com/mcp"
DEFAULT_OUTPUT = ".governance/control-plane-state/mcp-capability-snapshot.json"
MAX_TOOLS = 500
MAX_RESOURCES = 500

CAPABILITY_MODEL = {
    "GIT_REPOSITORY_OBSERVATION": {
        "kind": "OBSERVATION",
        "target_fields": [
            "provider", "repository.exists", "repository.visibility", "repository.default_branch",
            "repository.head", "repository.workflows", "repository.rulesets",
            "repository.required_checks", "repository.webhooks"
        ],
        "resolution_order": [
            "DIRECT_GIT_OBSERVATION", "PERSISTED_PROJECT_MEMORY",
            "MCP_READ_ONLY_IF_PROVIDER_SURFACE_REQUIRED", "ASK_OWNER_ONLY_IF_UNRESOLVED"
        ],
        "preferred_tools": [
            "github_get_repository_state", "github_get_branch_state", "github_get_tree",
            "github_get_workflow_runs", "github_get_rulesets", "github_get_required_checks",
            "github_get_webhooks", "github_get_deployments"
        ],
        "missing_surface_action": "USE_DIRECT_GIT_PROVIDER_BEFORE_MCP_CAPABILITY_REQUEST",
    },
    "GOVERNANCE_STATE_OBSERVATION": {
        "kind": "OBSERVATION",
        "target_fields": [
            "governance.present", "governance.current_state", "governance.next_action",
            "governance.work_queue", "governance.sessions", "governance.locks"
        ],
        "resolution_order": [
            "REPOSITORY_GOVERNANCE_FILES", "PERSISTED_PROJECT_MEMORY",
            "MCP_READ_ONLY_DISCOVERY", "ASK_OWNER_ONLY_IF_CONFLICT_OR_DECISION"
        ],
        "preferred_tools": [
            "mcp_get_current_state_inventory", "mcp_get_live_state", "mcp_get_work_queue",
            "mcp_get_governed_context", "mcp_get_governed_session", "mcp_list_governed_sessions"
        ],
        "missing_surface_action": "KEEP_REPOSITORY_AUTHORITIES_AS_PRIMARY_SOURCE",
    },
    "PROJECT_INFRASTRUCTURE_MAPPING": {
        "kind": "OBSERVATION",
        "target_fields": [
            "mcp.project_registration", "infrastructure.server_binding",
            "infrastructure.logical_server", "domain.existing_bindings",
            "runtime.available_write_surfaces"
        ],
        "resolution_order": [
            "PERSISTED_PROJECT_MEMORY", "MCP_READ_ONLY_DISCOVERY",
            "ASK_OWNER_ONLY_FOR_TARGET_DECISION_OR_UNRESOLVED_FACT"
        ],
        "preferred_tools": [
            "get_project_context", "get_write_tools_context"
        ],
        "missing_surface_action": "PREPARE_READ_ONLY_CAPABILITY_REQUEST_ONLY_IF_PROJECT_NEEDS_IT",
    },
    "DOMAIN_WEB_OBSERVATION": {
        "kind": "OBSERVATION",
        "target_fields": [
            "domain.existing", "domain.server", "web.https_reachable", "web.current_binding"
        ],
        "resolution_order": [
            "PERSISTED_PROJECT_MEMORY", "MCP_READ_ONLY_DISCOVERY",
            "ASK_OWNER_ONLY_FOR_DOMAIN_NAMING_DECISION"
        ],
        "preferred_tools": ["list_domains_s1", "list_domains_s2", "curl_domain"],
        "missing_surface_action": "PREPARE_READ_ONLY_CAPABILITY_REQUEST_ONLY_IF_PROJECT_NEEDS_IT",
    },
    "SERVER_RUNTIME_OBSERVATION": {
        "kind": "OBSERVATION",
        "target_fields": [
            "runtime.container_engine", "runtime.process_manager", "runtime.health",
            "runtime.capacity", "runtime.backup_presence"
        ],
        "resolution_order": [
            "PERSISTED_PROJECT_MEMORY", "MCP_READ_ONLY_DISCOVERY",
            "ASK_OWNER_ONLY_IF_RUNTIME_TARGET_IS_A_DECISION"
        ],
        "preferred_tools": [
            "docker_status_s1", "docker_status_s2", "pm2_status_s1", "pm2_status_s2",
            "check_disk_s1", "check_disk_s2", "list_backups_s1", "list_backups_s2"
        ],
        "missing_surface_action": "PREPARE_READ_ONLY_CAPABILITY_REQUEST_ONLY_IF_PROJECT_NEEDS_IT",
    },
    "DATABASE_READ_OBSERVATION": {
        "kind": "OBSERVATION",
        "target_fields": [
            "database.exists", "database.engine", "database.schema_state"
        ],
        "resolution_order": [
            "REPOSITORY_CONFIGURATION", "PERSISTED_PROJECT_MEMORY",
            "MCP_READ_ONLY_IF_PROJECT_REGISTERED", "ASK_OWNER_ONLY_IF_DATABASE_CHOICE_IS_UNRESOLVED"
        ],
        "preferred_tools": ["run_sql_readonly_s2", "brvm_run_sql_readonly_s2"],
        "missing_surface_action": "PREPARE_PROJECT_SCOPED_READ_CAPABILITY_REQUEST_IF_NEEDED",
    },
    "GIT_REPOSITORY_CHANGE": {
        "kind": "MUTATION",
        "target_fields": [
            "repository.branch_change", "repository.file_change", "repository.pull_request",
            "repository.merge"
        ],
        "resolution_order": ["PREPARE_OPERATION", "VERIFY_EXACT_HEAD", "VERIFY_AUTHORITY", "EXECUTE"],
        "preferred_tools": [
            "github_create_branch", "github_create_commit", "github_create_or_update_file",
            "github_create_pull_request", "github_mark_pr_ready", "github_merge_pull_request"
        ],
        "missing_surface_action": "PREPARE_SCOPED_CAPABILITY_REQUEST_ONLY_WHEN_OPERATION_IS_REQUIRED",
    },
    "GOVERNED_TASK_COORDINATION": {
        "kind": "OPERATIONAL",
        "target_fields": [
            "work.next_task", "work.claim", "work.state_transition", "work.lock"
        ],
        "resolution_order": ["LOAD_CANONICAL_STATE", "VERIFY_AUTHORITY", "EXECUTE_EXISTING_LOOP_ENGINEERING"],
        "preferred_tools": [
            "mcp_reconcile_governed_context", "mcp_reconcile_agent_intent",
            "mcp_claim_next_governed_task", "mcp_transition_governed_task",
            "mcp_acquire_governed_lock", "mcp_release_governed_lock"
        ],
        "missing_surface_action": "USE_REPOSITORY_LOCAL_LOOP_ENGINEERING_IF_MCP_COORDINATION_NOT_REQUIRED",
    },
    "SERVER_REPOSITORY_CHANGE": {
        "kind": "MUTATION",
        "target_fields": [
            "runtime.repository_sync", "runtime.work_branch", "runtime.repo_script"
        ],
        "resolution_order": ["VERIFY_PROJECT_MAPPING", "VERIFY_AUTHORITY", "LIVE_PREFLIGHT", "EXECUTE"],
        "preferred_tools": [
            "git_status_project_s2", "git_pull_project_s2", "exec_repo_script_s2"
        ],
        "missing_surface_action": "PREPARE_SCOPED_CAPABILITY_REQUEST_ONLY_WHEN_OPERATION_IS_REQUIRED",
    },
    "SERVER_FILESYSTEM_CHANGE": {
        "kind": "MUTATION",
        "target_fields": [
            "runtime.directory_create", "runtime.file_write", "runtime.file_delete",
            "runtime.permissions"
        ],
        "resolution_order": [
            "VERIFY_PROJECT_MAPPING", "VERIFY_TARGET_PATH", "VERIFY_AUTHORITY",
            "LIVE_PREFLIGHT", "EXECUTE"
        ],
        "preferred_tools": [],
        "missing_surface_action": "PREPARE_SCOPED_CAPABILITY_REQUEST_ONLY_WHEN_OPERATION_IS_REQUIRED",
    },
    "WEB_HOSTING_CHANGE": {
        "kind": "MUTATION",
        "target_fields": [
            "web.vhost", "web.reverse_proxy", "web.runtime_port_binding", "web.healthcheck"
        ],
        "resolution_order": [
            "VERIFY_DOMAIN_AND_SERVER", "VERIFY_RUNTIME", "VERIFY_AUTHORITY",
            "LIVE_PREFLIGHT", "EXECUTE"
        ],
        "preferred_tools": [],
        "missing_surface_action": "PREPARE_SCOPED_CAPABILITY_REQUEST_ONLY_WHEN_OPERATION_IS_REQUIRED",
    },
    "TLS_CHANGE": {
        "kind": "MUTATION",
        "target_fields": ["web.tls_certificate", "web.tls_renewal"],
        "resolution_order": [
            "VERIFY_DNS", "VERIFY_WEB_BINDING", "VERIFY_AUTHORITY", "LIVE_PREFLIGHT", "EXECUTE"
        ],
        "preferred_tools": [],
        "missing_surface_action": "PREPARE_SCOPED_CAPABILITY_REQUEST_ONLY_WHEN_OPERATION_IS_REQUIRED",
    },
    "DEPLOYMENT_RUNTIME_CHANGE": {
        "kind": "MUTATION",
        "target_fields": [
            "deployment.build", "deployment.deploy", "deployment.restart",
            "deployment.rollback", "deployment.production_attestation"
        ],
        "resolution_order": [
            "VERIFY_EXACT_SOURCE", "VERIFY_PROJECT_MAPPING", "VERIFY_AUTHORITY",
            "LIVE_PREFLIGHT", "EXECUTE", "VERIFY", "EVIDENCE"
        ],
        "preferred_tools": ["deploy_project_s2"],
        "missing_surface_action": "PREPARE_SCOPED_CAPABILITY_REQUEST_ONLY_WHEN_OPERATION_IS_REQUIRED",
    },
}

CASE_CAPABILITY_SEQUENCE = {
    "CREATE_NEW_REPOSITORY": [
        "GIT_REPOSITORY_OBSERVATION", "GOVERNANCE_STATE_OBSERVATION",
        "PROJECT_INFRASTRUCTURE_MAPPING", "DOMAIN_WEB_OBSERVATION",
        "SERVER_RUNTIME_OBSERVATION", "GIT_REPOSITORY_CHANGE",
        "SERVER_FILESYSTEM_CHANGE", "WEB_HOSTING_CHANGE", "TLS_CHANGE",
        "DEPLOYMENT_RUNTIME_CHANGE"
    ],
    "ADOPT_EXISTING_REPOSITORY": [
        "GIT_REPOSITORY_OBSERVATION", "GOVERNANCE_STATE_OBSERVATION",
        "PROJECT_INFRASTRUCTURE_MAPPING", "DOMAIN_WEB_OBSERVATION",
        "SERVER_RUNTIME_OBSERVATION", "DATABASE_READ_OBSERVATION",
        "GIT_REPOSITORY_CHANGE", "SERVER_REPOSITORY_CHANGE",
        "SERVER_FILESYSTEM_CHANGE", "WEB_HOSTING_CHANGE", "TLS_CHANGE",
        "DEPLOYMENT_RUNTIME_CHANGE"
    ],
    "MAP_EXISTING_PROJECT": [
        "GIT_REPOSITORY_OBSERVATION", "GOVERNANCE_STATE_OBSERVATION",
        "PROJECT_INFRASTRUCTURE_MAPPING", "DOMAIN_WEB_OBSERVATION",
        "SERVER_RUNTIME_OBSERVATION", "DATABASE_READ_OBSERVATION"
    ],
    "LAB_EVOLUTION": [
        "GIT_REPOSITORY_OBSERVATION", "GOVERNANCE_STATE_OBSERVATION",
        "GIT_REPOSITORY_CHANGE", "PROJECT_INFRASTRUCTURE_MAPPING",
        "SERVER_RUNTIME_OBSERVATION", "DEPLOYMENT_RUNTIME_CHANGE"
    ],
    "CONTINUE_GOVERNED_WORK": [
        "GOVERNANCE_STATE_OBSERVATION", "GIT_REPOSITORY_OBSERVATION",
        "GOVERNED_TASK_COORDINATION", "PROJECT_INFRASTRUCTURE_MAPPING"
    ],
}

TAG_KEYWORDS = {
    "GOVERNANCE": (
        "governed", "governance", "session", "task", "lock", "context", "checkpoint",
        "handoff", "intake", "approval", "intent", "coordination", "state"
    ),
    "REPOSITORY": ("git", "github", "repo", "repository", "branch", "commit", "pull request", "pr "),
    "SERVER_RUNTIME": (
        "s1", "s2", "server", "runtime", "docker", "container", "pm2", "systemd",
        "process", "restart", "ssh"
    ),
    "DOMAIN_NETWORK": (
        "domain", "dns", "nginx", "plesk", "host", "http", "https", "tls",
        "certificate", "reverse proxy", "network"
    ),
    "DEPLOYMENT": ("deploy", "deployment", "build", "release", "rollout", "rollback", "health"),
    "DATABASE": ("sql", "database", "postgres", "db ", "migration"),
    "SECURITY_IDENTITY": (
        "oidc", "auth", "identity", "permission", "credential", "secret", "certificate",
        "principal", "scope"
    ),
    "OBSERVABILITY": ("log", "status", "health", "metric", "audit", "evidence", "attest"),
    "DISCOVERY": ("get", "list", "inventory", "catalog", "discover", "read", "inspect", "observe"),
}


def parse_body(raw: str):
    value = raw.strip()
    if not value:
        return {}
    if value.startswith("{"):
        return json.loads(value)
    events = []
    for line in value.splitlines():
        if line.startswith("data:"):
            data = line[5:].strip()
            if not data:
                continue
            try:
                events.append(json.loads(data))
            except json.JSONDecodeError:
                continue
    return events[-1] if events else {"raw": value[:12000]}


def post(endpoint: str, token: str, payload: dict, session_id: str | None = None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": "governed-template-mcp-capability-snapshot",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    request = urllib.request.Request(
        endpoint,
        method="POST",
        headers=headers,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise RuntimeError("MCP_CAPABILITY_RESPONSE_TOO_LARGE")
        return parse_body(raw.decode(errors="replace")), response.headers.get("Mcp-Session-Id") or session_id


def rpc(endpoint: str, token: str, session_id: str | None, request_id: int, method: str, params: dict | None = None):
    payload = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        payload["params"] = params
    result, session_id = post(endpoint, token, payload, session_id)
    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(f"MCP_RPC_ERROR:{method}:{json.dumps(result['error'], ensure_ascii=False)[:500]}")
    return result, session_id


def call_tool(endpoint: str, token: str, session_id: str, request_id: int, name: str, arguments: dict | None = None):
    result, _ = rpc(
        endpoint,
        token,
        session_id,
        request_id,
        "tools/call",
        {"name": name, "arguments": arguments or {}},
    )
    return result


def rpc_result(value):
    return value.get("result", {}) if isinstance(value, dict) else {}


def tool_content_json(value):
    result = rpc_result(value)
    content = result.get("content", []) if isinstance(result, dict) else []
    texts = [entry.get("text") for entry in content if isinstance(entry, dict) and isinstance(entry.get("text"), str)]
    for text in texts:
        stripped = text.strip()
        if not stripped:
            continue
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            continue
    return {"text": "\n".join(texts)[:12000]} if texts else {}


def compact_server_context(value):
    payload = tool_content_json(value)
    servers = payload.get("servers", {}) if isinstance(payload, dict) else {}
    result = {}
    for key, server in list(servers.items())[:20]:
        if not isinstance(server, dict):
            continue
        domains = server.get("protectedDomains")
        result[str(key)] = {
            "id": server.get("id") or key,
            "label": server.get("label"),
            "protected_domains": list(domains)[:200] if isinstance(domains, list) else [],
            "connection_coordinates_persisted": False,
            "live_connection_refresh_required_before_server_operation": True,
        }
    return result


def compact_write_context(value):
    payload = tool_content_json(value)
    if not isinstance(payload, dict):
        return {}
    raw_projects = payload.get("projects")
    project_ids = []
    reserved = {"path", "note", "server", "host", "domain", "url"}
    if isinstance(raw_projects, str):
        for line in raw_projects.splitlines():
            if not line or line[:1].isspace() or ":" not in line:
                continue
            candidate = line.split(":", 1)[0].strip()
            if (
                candidate
                and candidate.lower() not in reserved
                and all(ch.isalnum() or ch in "._-" for ch in candidate)
            ):
                project_ids.append(candidate)
    return {
        "mode": payload.get("mode"),
        "free_shell": payload.get("free_shell"),
        "run_command_s1": payload.get("run_command_s1"),
        "run_command_s2": payload.get("run_command_s2"),
        "sql": payload.get("sql"),
        "project_ids": sorted(set(project_ids))[:500],
        "project_paths_persisted": False,
    }


def normalize_surface(value):
    return value if value in {"read", "operational-write", "scoped-write"} else "unknown"


def authority_for_surface(surface: str):
    if surface == "read":
        return "READ_ONLY_DISCOVERY_AUTHORITY"
    if surface in {"operational-write", "scoped-write"}:
        return "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED"
    return "AUTHORITY_CLASSIFICATION_REQUIRED"


def classify_tool(tool: dict):
    haystack = " ".join(
        str(tool.get(key) or "") for key in ("name", "title", "description")
    ).lower()
    tags = []
    for tag, words in TAG_KEYWORDS.items():
        if any(word in haystack for word in words):
            tags.append(tag)
    return sorted(set(tags or ["OTHER"]))


def summarize_input_schema(schema):
    if not isinstance(schema, dict):
        return []
    properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
    required = set(schema.get("required") or [])
    fields = []
    for name in sorted(properties)[:100]:
        prop = properties.get(name)
        if not isinstance(prop, dict):
            prop = {}
        item = {
            "name": name,
            "type": prop.get("type"),
            "required": name in required,
        }
        enum = prop.get("enum")
        if isinstance(enum, list) and len(enum) <= 20 and all(isinstance(v, (str, int, float, bool)) or v is None for v in enum):
            item["enum"] = enum
        fields.append(item)
    return fields


def normalize_tool(tool: dict, inventory_tool: dict | None = None):
    inventory_tool = inventory_tool or {}
    annotations = tool.get("annotations") if isinstance(tool.get("annotations"), dict) else {}
    surface = normalize_surface(inventory_tool.get("surface") or tool.get("surface"))
    read_only_hint = annotations.get("readOnlyHint")
    destructive_hint = annotations.get("destructiveHint")
    schema = tool.get("inputSchema") if isinstance(tool.get("inputSchema"), dict) else inventory_tool.get("inputSchema")
    normalized = {
        "name": tool.get("name") or inventory_tool.get("name"),
        "title": tool.get("title") or inventory_tool.get("title"),
        "description": tool.get("description") or inventory_tool.get("description"),
        "surface": surface,
        "authority_required": authority_for_surface(surface),
        "read_only_hint": read_only_hint if isinstance(read_only_hint, bool) else inventory_tool.get("readOnlyHint"),
        "destructive_hint": destructive_hint if isinstance(destructive_hint, bool) else inventory_tool.get("destructiveHint"),
        "contract_digest": inventory_tool.get("contractDigest"),
        "input_fields": summarize_input_schema(schema),
    }
    normalized["tags"] = classify_tool(normalized)
    return normalized


def normalize_resource(resource: dict):
    return {
        "name": resource.get("name"),
        "title": resource.get("title"),
        "description": resource.get("description"),
        "uri": resource.get("uri"),
        "mime_type": resource.get("mimeType"),
        "annotations": resource.get("annotations") if isinstance(resource.get("annotations"), dict) else {},
    }


def tool_project_scope(tool: dict):
    name = str(tool.get("name") or "")
    fields = tool.get("input_fields") if isinstance(tool.get("input_fields"), list) else []
    project_field = next((item for item in fields if isinstance(item, dict) and item.get("name") == "project"), None)
    if isinstance(project_field, dict) and isinstance(project_field.get("enum"), list):
        return {
            "mode": "PROJECT_REGISTRY_SCOPED",
            "project_ids": [str(value) for value in project_field["enum"] if isinstance(value, str)][:100],
        }
    if name.startswith(("sadiaaf_", "legacy_vhost_", "legacy_funds_", "nigeria_", "amf_registry_", "brvm_")):
        return {"mode": "PROJECT_SPECIFIC", "project_ids": []}
    if name.startswith(("mcp_build_", "mcp_sync_", "mcp_typecheck_", "restart_mcp_", "patch_mcp_", "read_mcp_", "search_mcp_", "scan_mcp_")):
        return {"mode": "MCP_SELF", "project_ids": ["Patricked-code/MCP"]}
    return {"mode": "GENERIC", "project_ids": []}


def capability_candidates(capability_id: str, tools: list[dict]):
    spec = CAPABILITY_MODEL[capability_id]
    by_name = {tool.get("name"): tool for tool in tools if tool.get("name")}
    candidates = []
    for name in spec.get("preferred_tools", []):
        tool = by_name.get(name)
        if not tool:
            continue
        scope = tool_project_scope(tool)
        candidates.append({
            "tool": name,
            "surface": tool.get("surface"),
            "authority_required": tool.get("authority_required"),
            "scope": scope,
        })
    generic = [item for item in candidates if item["scope"]["mode"] == "GENERIC"]
    registry = [item for item in candidates if item["scope"]["mode"] == "PROJECT_REGISTRY_SCOPED"]
    project_specific = [item for item in candidates if item["scope"]["mode"] in {"PROJECT_SPECIFIC", "MCP_SELF"}]
    if generic:
        availability = "AVAILABLE_GENERIC"
    elif registry:
        availability = "AVAILABLE_PROJECT_REGISTRY_SCOPED"
    elif project_specific:
        availability = "AVAILABLE_ONLY_PROJECT_SPECIFIC"
    else:
        availability = "NOT_EXPOSED_BY_CURRENT_MCP_CATALOGUE"
    return {
        "availability": availability,
        "candidate_tools": candidates,
        "missing_surface_action": spec.get("missing_surface_action"),
    }


def derive_capability_map(tools: list[dict]):
    result = {}
    for capability_id, spec in CAPABILITY_MODEL.items():
        candidates = capability_candidates(capability_id, tools)
        result[capability_id] = {
            "kind": spec["kind"],
            "target_fields": list(spec.get("target_fields", [])),
            "resolution_order": list(spec.get("resolution_order", [])),
            **candidates,
        }
    return result


def derive_case_operation_map(tools: list[dict]):
    capabilities = derive_capability_map(tools)
    mapping = {}
    for case_id, sequence in CASE_CAPABILITY_SEQUENCE.items():
        steps = []
        observable_fields = []
        owner_question_fields = []
        for order, capability_id in enumerate(sequence, start=1):
            capability = capabilities[capability_id]
            fields = list(capability.get("target_fields", []))
            observable_fields.extend(fields)
            if capability["kind"] == "MUTATION":
                question_policy = "PREPARE_OPERATION_AND_AUTHORITY;_DO_NOT_ASK_TECHNICAL_FACTS_ALREADY_OBSERVABLE"
            elif capability["kind"] == "OBSERVATION":
                question_policy = "OBSERVE_FIRST;_ASK_OWNER_ONLY_IF_UNRESOLVED_OR_DECISION"
            else:
                question_policy = "USE_EXISTING_GOVERNED_STATE_AND_AUTHORITY"
            steps.append({
                "order": order,
                "capability": capability_id,
                "kind": capability["kind"],
                "availability": capability["availability"],
                "candidate_tools": [item["tool"] for item in capability["candidate_tools"]],
                "required_authorities": sorted({
                    item.get("authority_required") for item in capability["candidate_tools"]
                    if item.get("authority_required")
                }),
                "target_fields": fields,
                "resolution_order": capability["resolution_order"],
                "question_policy": question_policy,
                "missing_surface_action": capability["missing_surface_action"],
            })
            if capability["kind"] == "MUTATION":
                owner_question_fields.extend(fields)
        mapping[case_id] = {
            "mode": "CAPABILITY_FIRST_ADAPTIVE_QUESTION_PLANNING",
            "sequence": steps,
            "observable_target_fields": sorted(set(observable_fields)),
            "owner_question_candidates": sorted(set(owner_question_fields)),
            "owner_question_rule": (
                "DO_NOT_ASK_IF_FRESH_OBSERVATION_OR_PERSISTED_OWNER_DECISION_ALREADY_RESOLVES_FIELD;"
                "ASK_ONLY_FOR_UNRESOLVED_OWNER_DECISION_OR_NON_DISCOVERABLE_FACT"
            ),
            "pre_mutation_live_refresh_required": True,
            "tool_metadata_source": "catalogue.tools",
            "capability_metadata_source": "capability_map",
        }
    return mapping


def build_snapshot(
    *,
    endpoint: str,
    observed_at: str,
    source_head: str | None,
    init_response: dict,
    tools_response: dict,
    resources_response: dict,
    inventory_response: dict,
    project_context_response: dict,
    write_context_response: dict,
    prior_snapshot: dict | None = None,
):
    init = rpc_result(init_response)
    inventory = tool_content_json(inventory_response)
    if not isinstance(inventory, dict):
        inventory = {}
    inventory_catalogue = inventory.get("catalogue") if isinstance(inventory.get("catalogue"), dict) else {}
    inventory_tools = inventory_catalogue.get("tools") if isinstance(inventory_catalogue.get("tools"), list) else []
    inventory_by_name = {
        item.get("name"): item for item in inventory_tools
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }

    protocol_tools = rpc_result(tools_response).get("tools", [])
    normalized_tools = []
    if isinstance(protocol_tools, list):
        for item in protocol_tools[:MAX_TOOLS]:
            if isinstance(item, dict):
                normalized_tools.append(normalize_tool(item, inventory_by_name.get(item.get("name"))))
    if not normalized_tools:
        for item in inventory_tools[:MAX_TOOLS]:
            if isinstance(item, dict):
                normalized_tools.append(normalize_tool(item, item))
    normalized_tools.sort(key=lambda item: item.get("name") or "")

    protocol_resources = rpc_result(resources_response).get("resources", [])
    resources = [
        normalize_resource(item) for item in protocol_resources[:MAX_RESOURCES]
        if isinstance(item, dict)
    ] if isinstance(protocol_resources, list) else []

    server_info = init.get("serverInfo") if isinstance(init.get("serverInfo"), dict) else {}
    protocol_version = init.get("protocolVersion")
    source = inventory.get("source") if isinstance(inventory.get("source"), dict) else {}
    counts = {
        "tools": len(normalized_tools),
        "resources": len(resources),
        "read": sum(1 for item in normalized_tools if item.get("surface") == "read"),
        "operational_write": sum(1 for item in normalized_tools if item.get("surface") == "operational-write"),
        "scoped_write": sum(1 for item in normalized_tools if item.get("surface") == "scoped-write"),
        "unknown_surface": sum(1 for item in normalized_tools if item.get("surface") == "unknown"),
    }
    prior_sequence = int((prior_snapshot or {}).get("refresh_sequence") or 0)
    return {
        "schema_version": "1.0.0",
        "authority_id": AUTHORITY_ID,
        "authority_type": "MCP_CAPABILITY_SNAPSHOT",
        "scope": "CONTROL_PLANE_SOURCE_ONLY",
        "status": "CURRENT" if normalized_tools else "PARTIAL",
        "observed_at": observed_at,
        "refresh_sequence": prior_sequence + 1,
        "endpoint": endpoint,
        "standing_readonly_refresh_authority": True,
        "mutation_authority_granted": False,
        "secrets_persisted": False,
        "refresh_policy": {
            "mode": "EVENT_AND_NEED_BASED",
            "automatic_periodic_polling": False,
            "refresh_triggers": [
                "MISSING_SNAPSHOT",
                "CAPABILITY_REQUIRED_NOT_PRESENT",
                "CATALOGUE_DIGEST_CONTRADICTION",
                "SOURCE_HEAD_OR_RUNTIME_REVISION_CONTRADICTION",
                "PRE_MUTATION_CAPABILITY_ATTESTATION",
                "OWNER_OR_AGENT_REQUESTED_REFRESH",
            ],
            "pre_mutation_live_refresh_required": True,
            "material_capability_change_requires_replanning": True,
        },
        "provenance": {
            "method": "LIVE_READ_ONLY_MCP_DISCOVERY",
            "source_repository": "chainsolutions-wealthtech/Governed-Repository-Template",
            "source_head": source_head,
            "mcp_repository": inventory.get("repository") or "Patricked-code/MCP",
            "mcp_github_head": source.get("githubHead"),
            "mcp_runtime_revision": source.get("runtimeRevision"),
            "mcp_live_state_version": source.get("liveStateVersion"),
            "inventory_digest": source.get("inventoryDigest"),
            "catalogue_digest": source.get("catalogueDigest") or inventory_catalogue.get("catalogueDigest"),
        },
        "mcp_server": {
            "name": server_info.get("name"),
            "version": server_info.get("version"),
            "protocol_version": protocol_version,
        },
        "servers": compact_server_context(project_context_response),
        "catalogue": {
            "status": "CURRENT" if normalized_tools else "PARTIAL",
            "counts": counts,
            "catalogue_version": inventory_catalogue.get("catalogueVersion"),
            "catalogue_digest": inventory_catalogue.get("catalogueDigest") or source.get("catalogueDigest"),
            "tools": normalized_tools,
            "resources": resources,
        },
        "write_context_summary": compact_write_context(write_context_response),
        "capability_map": derive_capability_map(normalized_tools),
        "case_operation_map": derive_case_operation_map(normalized_tools),
        "question_resolution_contract": {
            "principle": "OBSERVE_AND_REUSE_BEFORE_ASK",
            "source_priority": [
                "FRESH_DIRECT_REPOSITORY_OBSERVATION",
                "FRESH_PERSISTED_PROJECT_MEMORY",
                "PRIOR_OWNER_DECISION",
                "AUTHORIZED_MCP_READ_ONLY_DISCOVERY",
                "ASK_OWNER"
            ],
            "ask_owner_only_when": [
                "OWNER_DECISION_REQUIRED",
                "FACT_NOT_DISCOVERABLE_WITH_AVAILABLE_AUTHORITY",
                "CONTRADICTORY_AUTHORITIES_REQUIRE_OWNER_RESOLUTION"
            ],
            "never_reask_fresh_resolved_fact": True,
            "answers_feed_existing_project_model_and_loop_engineering": True,
        },
        "operation_planning_contract": {
            "pipeline": [
                "CASE_OR_WORK_ITEM",
                "REQUIRED_CAPABILITY",
                "SNAPSHOT_MATCH",
                "REFRESH_IF_REQUIRED",
                "CANDIDATE_TOOL_SELECTION",
                "AUTHORITY_CHECK",
                "PREPARED_OPERATION",
                "EXISTING_LOOP_ENGINEERING",
                "LIVE_PREFLIGHT",
                "EXECUTE_IF_AUTHORIZED",
                "EVIDENCE",
            ],
            "snapshot_is_execution_authority": False,
            "write_tool_presence_implies_write_authority": False,
            "tool_selection_must_recheck_live_authority_before_mutation": True,
            "parallel_engine": False,
        },
        "relational_projection": {
            "status": "PENDING_PROJECTION_GMC_INTEGRATION",
            "decision_id": "CPD-033",
        },
        "contradictions": inventory.get("contradictions", [])[:100] if isinstance(inventory.get("contradictions"), list) else [],
    }


def load_prior(path: pathlib.Path):
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def live_snapshot(endpoint: str, token: str, source_head: str | None, prior_snapshot: dict):
    initialize = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "governed-template-capability-snapshot", "version": "1.0"},
        },
    }
    init_response, session = post(endpoint, token, initialize)
    if not session:
        raise RuntimeError("MCP_SESSION_ID_MISSING")
    try:
        post(endpoint, token, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, session)
    except Exception:
        pass
    tools_response, session = rpc(endpoint, token, session, 2, "tools/list", {})
    resources_response, session = rpc(endpoint, token, session, 3, "resources/list", {})
    inventory_response = call_tool(endpoint, token, session, 4, "mcp_get_current_state_inventory")
    project_context_response = call_tool(endpoint, token, session, 5, "get_project_context")
    write_context_response = call_tool(endpoint, token, session, 6, "get_write_tools_context")
    ping_response = call_tool(endpoint, token, session, 7, "ping")
    ping_payload = tool_content_json(ping_response)
    if not ping_payload and "wealthtech_ssh_bridge_ok" not in json.dumps(ping_response):
        raise RuntimeError("MCP_CAPABILITY_PING_FAILED")

    observed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return build_snapshot(
        endpoint=endpoint,
        observed_at=observed_at,
        source_head=source_head,
        init_response=init_response,
        tools_response=tools_response,
        resources_response=resources_response,
        inventory_response=inventory_response,
        project_context_response=project_context_response,
        write_context_response=write_context_response,
        prior_snapshot=prior_snapshot,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default=os.environ.get("GOVERNED_MCP_URL") or DEFAULT_ENDPOINT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    token = os.environ.get("GOVERNED_MCP_AUTH_TOKEN")
    if not token:
        raise SystemExit("MCP_CAPABILITY_REFRESH_BLOCKED:GOVERNED_MCP_AUTH_TOKEN_MISSING")
    output = pathlib.Path(args.output)
    prior = load_prior(output)
    try:
        snapshot = live_snapshot(args.endpoint, token, os.environ.get("GITHUB_SHA"), prior)
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"MCP_CAPABILITY_REFRESH_FAILED:{type(exc).__name__}:{str(exc)[:500]}") from exc
    finally:
        token = ""

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "MCP_CAPABILITY_SNAPSHOT_REFRESHED",
        "authority_id": snapshot["authority_id"],
        "observed_at": snapshot["observed_at"],
        "refresh_sequence": snapshot["refresh_sequence"],
        "tools": snapshot["catalogue"]["counts"]["tools"],
        "resources": snapshot["catalogue"]["counts"]["resources"],
        "catalogue_digest": snapshot["catalogue"]["catalogue_digest"],
        "mutation_authority_granted": False,
        "secrets_persisted": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
