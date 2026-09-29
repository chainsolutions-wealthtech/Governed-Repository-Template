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

CASE_TAGS = {
    "CREATE_NEW_REPOSITORY": {
        "GOVERNANCE", "REPOSITORY", "DISCOVERY", "SERVER_RUNTIME", "DOMAIN_NETWORK",
        "DEPLOYMENT", "SECURITY_IDENTITY"
    },
    "ADOPT_EXISTING_REPOSITORY": {
        "GOVERNANCE", "REPOSITORY", "DISCOVERY", "SERVER_RUNTIME", "DOMAIN_NETWORK",
        "DEPLOYMENT", "DATABASE", "OBSERVABILITY", "SECURITY_IDENTITY"
    },
    "MAP_EXISTING_PROJECT": {
        "GOVERNANCE", "REPOSITORY", "DISCOVERY", "SERVER_RUNTIME", "DOMAIN_NETWORK",
        "DATABASE", "OBSERVABILITY"
    },
    "LAB_EVOLUTION": {
        "GOVERNANCE", "REPOSITORY", "DISCOVERY", "SERVER_RUNTIME", "DEPLOYMENT",
        "OBSERVABILITY"
    },
    "CONTINUE_GOVERNED_WORK": {
        "GOVERNANCE", "REPOSITORY", "DISCOVERY", "OBSERVABILITY", "DEPLOYMENT",
        "SERVER_RUNTIME"
    },
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
    if isinstance(raw_projects, str):
        for line in raw_projects.splitlines():
            stripped = line.strip()
            if ":" not in stripped:
                continue
            candidate = stripped.split(":", 1)[0].strip()
            if candidate and all(ch.isalnum() or ch in "._-" for ch in candidate):
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


def normalize_tool(tool: dict, inventory_tool: dict | None = None):
    inventory_tool = inventory_tool or {}
    annotations = tool.get("annotations") if isinstance(tool.get("annotations"), dict) else {}
    surface = normalize_surface(inventory_tool.get("surface") or tool.get("surface"))
    read_only_hint = annotations.get("readOnlyHint")
    destructive_hint = annotations.get("destructiveHint")
    normalized = {
        "name": tool.get("name") or inventory_tool.get("name"),
        "title": tool.get("title") or inventory_tool.get("title"),
        "description": tool.get("description") or inventory_tool.get("description"),
        "surface": surface,
        "authority_required": authority_for_surface(surface),
        "read_only_hint": read_only_hint if isinstance(read_only_hint, bool) else inventory_tool.get("readOnlyHint"),
        "destructive_hint": destructive_hint if isinstance(destructive_hint, bool) else inventory_tool.get("destructiveHint"),
        "contract_digest": inventory_tool.get("contractDigest"),
        "input_schema": tool.get("inputSchema") if isinstance(tool.get("inputSchema"), dict) else inventory_tool.get("inputSchema"),
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


def derive_case_operation_map(tools: list[dict]):
    mapping = {}
    for case_id, desired_tags in CASE_TAGS.items():
        candidates = []
        for tool in tools:
            tags = set(tool.get("tags") or [])
            if not tags.intersection(desired_tags):
                continue
            candidates.append({
                "tool": tool.get("name"),
                "surface": tool.get("surface"),
                "tags": sorted(tags.intersection(desired_tags)),
                "authority_required": tool.get("authority_required"),
                "planning_only": True,
            })
        candidates.sort(key=lambda item: (
            0 if item["surface"] == "read" else 1,
            item.get("tool") or "",
        ))
        mapping[case_id] = {
            "mode": "PLANNING_CANDIDATES_NOT_EXECUTION_AUTHORITY",
            "candidate_tools": candidates,
            "pre_mutation_live_refresh_required": True,
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
        "case_operation_map": derive_case_operation_map(normalized_tools),
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
