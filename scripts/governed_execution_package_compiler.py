#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any

from governed_execution_engine import (
    ROOT,
    REGISTRY_PATH,
    SNAPSHOT_PATH,
    ExecutionError,
    compile_plan,
    load_json,
)

SERVER_MODEL_PATH = ROOT / ".governance" / "control-plane-state" / "server-knowledge-model.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
DOMAIN_RE = re.compile(r"^(?=.{4,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{1,62}$")
LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")

SERVER_INTENT_INPUTS = {
    "CREATE_PROJECT_DIRECTORY": ["server_id"],
    "CREATE_SUBDOMAIN": ["server_id", "parent_domain", "subdomain_label"],
    "CREATE_NEW_DOMAIN_BINDING": ["server_id", "domain"],
    "ALLOCATE_APPLICATION_PORT": ["server_id"],
    "CONFIGURE_REVERSE_PROXY": ["server_id", "domain", "backend_target"],
    "PROVISION_TLS": ["server_id", "domain"],
    "CREATE_DATABASE": ["server_id", "database_engine"],
    "BIND_REPOSITORY_TO_SERVER_PROJECT": ["server_id", "repository", "expected_head"],
    "DEPLOY_APPLICATION": ["server_id", "repository", "expected_head"],
    "CONFIGURE_ENV_AND_SECRETS": ["server_id", "repository", "expected_head"],
    "CONFIGURE_PROCESS_OR_SERVICE": ["server_id"],
    "CONFIGURE_SCHEDULED_JOB": ["server_id", "cadence"],
    "CONFIGURE_OBSERVABILITY": ["server_id"],
    "CONFIGURE_BACKUP_AND_ROLLBACK": ["server_id"],
    "PRODUCTION_ATTESTATION": ["server_id"],
}

CREDENTIAL_INPUTS = {
    "MINT_GITHUB_APP_INSTALLATION_TOKEN": ["target_owner"],
    "PROVISION_GITHUB_SECRET": ["repository", "secret_name", "value_ref"],
    "MINT_EPHEMERAL_SSH_CERTIFICATE": ["repository", "expected_head"],
    "CREATE_OR_BIND_SERVER_APPLICATION_SECRET": ["server_id"],
    "CREATE_DATABASE_CREDENTIAL": ["server_id", "database_engine"],
    "CREATE_DNS_AUTOMATION_CREDENTIAL": ["dns_provider"],
    "ROTATE_CREDENTIAL": ["credential_type"],
    "REVOKE_CREDENTIAL": ["credential_type"],
    "VERIFY_SECRET_OR_CREDENTIAL_WITHOUT_READBACK": ["credential_type"],
}


def _lookup_tool(snapshot: dict, name: str) -> dict | None:
    for item in ((snapshot.get("catalogue") or {}).get("tools") or []):
        if item.get("name") == name:
            return item
    return None


def _tool_accepts_project(snapshot: dict, name: str, project_id: str) -> bool:
    tool = _lookup_tool(snapshot, name)
    if not tool:
        return False
    for field in tool.get("input_fields") or []:
        if field.get("name") == "project":
            enum = field.get("enum")
            return not enum or project_id in enum
    return False


def _observed_domains(server_inventory: dict | None, server_id: str) -> tuple[str, list[str]]:
    if not isinstance(server_inventory, dict):
        return "NOT_PROVIDED", []
    server = ((server_inventory.get("servers") or {}).get(server_id)) or {}
    observation = server.get("DOMAINS_VHOSTS") or {}
    facts = observation.get("facts") or {}
    domains = facts.get("domains") or []
    if not isinstance(domains, list):
        domains = []
    return str(observation.get("status") or "UNKNOWN"), [d for d in domains if isinstance(d, str)]


def _github_secret_exists(github_metadata: dict | None, name: str, environment: str | None) -> bool | None:
    if not isinstance(github_metadata, dict):
        return None
    if environment:
        for item in github_metadata.get("environments") or []:
            if item.get("name") == environment:
                secrets = ((item.get("secrets") or {}).get("items")) or []
                return any(x.get("name") == name for x in secrets if isinstance(x, dict))
        return False
    secrets = ((github_metadata.get("repository_secrets") or {}).get("items")) or []
    return any(x.get("name") == name for x in secrets if isinstance(x, dict))


def _authority(request: dict, required_authority: str, side_effecting: bool) -> dict:
    supplied = copy.deepcopy(request.get("authority") or {})
    if not side_effecting:
        supplied.setdefault("approved", False)
        supplied.setdefault("grants", ["READ_ONLY_DISCOVERY_AUTHORITY"])
        supplied.setdefault("scope", {"project_id": request.get("project_id")})
        supplied.setdefault("decision_ref", request.get("decision_ref"))
        return supplied
    supplied.setdefault("approved", False)
    supplied.setdefault("grants", [])
    supplied.setdefault("scope", {"project_id": request.get("project_id"), "server_id": request.get("server_id")})
    supplied.setdefault("decision_ref", request.get("decision_ref"))
    return supplied


def _base_package(request: dict, spec: dict) -> dict:
    params = copy.deepcopy(request.get("parameters") or {})
    for key in (
        "repository", "server_id", "environment", "target_owner", "target_account_type",
        "parent_domain", "subdomain_label", "domain", "backend_target", "database_engine",
        "cadence", "dns_provider", "credential_type", "secret_name", "value_ref",
    ):
        if key in request and key not in params:
            params[key] = copy.deepcopy(request[key])

    package = {
        "schema_version": "1.0.0",
        "operation_id": request.get("operation_id") or request.get("request_id") or f"PLAN-{request['intent']}",
        "intent": request["intent"],
        "project_id": request["project_id"],
        "authority": _authority(request, spec["required_authority"], bool(spec.get("side_effecting"))),
        "parameters": params,
        "bindings": {
            "capabilities": {},
            "credentials": {},
            "steps": {"preflight": [], "execute": [], "verify": [], "rollback": []},
        },
    }
    for key in ("repository", "expected_head", "server_id", "environment"):
        if request.get(key) is not None:
            package[key] = request[key]
    if spec.get("handler") == "MCP_RECIPE":
        package["bindings"]["credentials"]["MCP_AUTH_TOKEN"] = {
            "secret_ref": "env:GOVERNED_MCP_AUTH_TOKEN"
        }
    return package


def _required_inputs(request: dict, registry: dict, spec: dict) -> list[str]:
    intent = request["intent"]
    params = request.get("parameters") or {}
    values = dict(params)
    values.update({k: v for k, v in request.items() if v is not None})

    if spec.get("handler") == "GITHUB_REST_OPERATION":
        required = ((registry.get("github_operation_allowlist") or {}).get(intent) or {}).get("required_parameters") or []
    elif intent in SERVER_INTENT_INPUTS:
        required = SERVER_INTENT_INPUTS[intent]
    elif intent in CREDENTIAL_INPUTS:
        required = CREDENTIAL_INPUTS[intent]
    else:
        required = []

    missing = [key for key in required if values.get(key) in (None, "")]
    if spec.get("side_effecting") and values.get("repository") and intent != "GITHUB_CREATE_REPOSITORY_FROM_TEMPLATE":
        if not values.get("expected_head"):
            missing.append("expected_head")
    return sorted(set(missing))


def _bind_current_mcp(package: dict, request: dict, snapshot: dict, notes: list[dict]) -> None:
    intent = request["intent"]
    server_id = request.get("server_id")
    project_id = request["project_id"]
    steps = package["bindings"]["steps"]

    if intent == "DEPLOY_APPLICATION" and server_id == "S2":
        if not _tool_accepts_project(snapshot, "deploy_project_s2", project_id):
            notes.append({
                "kind": "BLOCKER",
                "code": "PROJECT_NOT_IN_CURRENT_MCP_DEPLOY_REGISTRY",
                "project_id": project_id,
                "tool": "deploy_project_s2",
            })
            return
        steps["preflight"].append({
            "backend": "MCP_DIRECT",
            "capability": "SERVER_REPOSITORY_CHANGE",
            "tool": "git_status_project_s2",
            "arguments": {"project": project_id},
        })
        steps["execute"].append({
            "backend": "MCP_DIRECT",
            "capability": "DEPLOYMENT_RUNTIME_CHANGE",
            "tool": "deploy_project_s2",
            "arguments": {"project": project_id},
        })
        steps["verify"].append({
            "backend": "MCP_DIRECT",
            "capability": "SERVER_REPOSITORY_CHANGE",
            "tool": "git_status_project_s2",
            "arguments": {"project": project_id},
        })
        package["rollback_policy"] = "NO_AUTOMATIC_ROLLBACK_APPROVED"
        notes.append({"kind": "AUTO_BIND", "code": "S2_PROJECT_DEPLOY_BINDING", "tool": "deploy_project_s2"})

    elif intent == "PRODUCTION_ATTESTATION" and server_id in {"S1", "S2"}:
        suffix = server_id.lower()
        steps["preflight"].append({
            "backend": "MCP_DIRECT",
            "capability": "SERVER_RUNTIME_OBSERVATION",
            "tool": f"check_disk_{suffix}",
            "arguments": {},
        })
        for tool in (f"docker_status_{suffix}", f"pm2_status_{suffix}"):
            steps["verify"].append({
                "backend": "MCP_DIRECT",
                "capability": "SERVER_RUNTIME_OBSERVATION",
                "tool": tool,
                "arguments": {},
            })
        steps["verify"].append({
            "backend": "MCP_DIRECT",
            "capability": "DOMAIN_WEB_OBSERVATION",
            "tool": f"list_domains_{suffix}",
            "arguments": {},
        })
        domain = request.get("domain") or (request.get("parameters") or {}).get("domain")
        if domain:
            steps["verify"].append({
                "backend": "MCP_DIRECT",
                "capability": "DOMAIN_WEB_OBSERVATION",
                "tool": "curl_domain",
                "arguments": {"domain": domain},
            })
        package["rollback_policy"] = "READ_ONLY_NOT_APPLICABLE"
        notes.append({"kind": "AUTO_BIND", "code": f"{server_id}_PRODUCTION_READ_ATTESTATION"})


def compile_request(
    request: dict,
    *,
    registry: dict,
    snapshot: dict,
    server_model: dict,
    server_inventory: dict | None = None,
    github_metadata: dict | None = None,
) -> dict:
    if request.get("schema_version") != "1.0.0":
        raise ValueError("REQUEST_SCHEMA_VERSION_UNSUPPORTED")
    intent = request.get("intent")
    project_id = request.get("project_id")
    if intent not in (registry.get("intents") or {}):
        raise ValueError("INTENT_NOT_REGISTERED")
    if not isinstance(project_id, str) or not project_id:
        raise ValueError("PROJECT_ID_REQUIRED")

    spec = registry["intents"][intent]
    missing_inputs = _required_inputs(request, registry, spec)
    notes: list[dict[str, Any]] = []
    package = _base_package(request, spec)

    if intent == "CREATE_SUBDOMAIN":
        parent = request.get("parent_domain") or (request.get("parameters") or {}).get("parent_domain")
        label = request.get("subdomain_label") or (request.get("parameters") or {}).get("subdomain_label")
        if parent and label:
            parent = str(parent).lower().strip()
            label = str(label).lower().strip()
            if not DOMAIN_RE.fullmatch(parent):
                raise ValueError("PARENT_DOMAIN_INVALID")
            if not LABEL_RE.fullmatch(label):
                raise ValueError("SUBDOMAIN_LABEL_INVALID")
            fqdn = f"{label}.{parent}"
            package["parameters"]["domain"] = fqdn
            package["parameters"]["parent_domain"] = parent
            package["parameters"]["subdomain_label"] = label
            status, observed = _observed_domains(server_inventory, str(request.get("server_id") or ""))
            notes.append({
                "kind": "KNOWLEDGE",
                "code": "PARENT_DOMAIN_OBSERVATION",
                "status": status,
                "parent_domain": parent,
                "observed_on_server": parent in observed,
            })

    if intent == "PROVISION_GITHUB_SECRET":
        name = request.get("secret_name") or (request.get("parameters") or {}).get("secret_name")
        environment = request.get("environment") or (request.get("parameters") or {}).get("environment")
        exists = _github_secret_exists(github_metadata, str(name or ""), environment)
        if exists is not None:
            notes.append({
                "kind": "RESOURCE_CLASSIFICATION",
                "resource": "GITHUB_SECRET",
                "classification": "ALIGN_OR_ROTATE" if exists else "CREATE",
                "secret_name": name,
                "environment": environment,
                "value_read_back": False,
            })

    _bind_current_mcp(package, request, snapshot, notes)

    recipes = {
        item.get("intent"): item
        for item in (server_model.get("operation_recipes") or [])
        if isinstance(item, dict)
    }
    recipe = recipes.get(intent)
    required_inventory = copy.deepcopy((recipe or {}).get("required_inventory") or [])

    if missing_inputs:
        return {
            "schema_version": "1.0.0",
            "authority_id": "CP-EXECUTION-001",
            "request_id": request.get("request_id"),
            "intent": intent,
            "status": "NEEDS_INPUT",
            "missing_inputs": missing_inputs,
            "required_inventory": required_inventory,
            "notes": notes,
            "package": package,
            "mcp_intake_required": False,
        }

    try:
        plan = compile_plan(package, registry, snapshot)
    except ExecutionError as exc:
        return {
            "schema_version": "1.0.0",
            "authority_id": "CP-EXECUTION-001",
            "request_id": request.get("request_id"),
            "intent": intent,
            "status": "BLOCKED_VALIDATION",
            "failure_code": exc.code,
            "failure_detail": exc.detail,
            "required_inventory": required_inventory,
            "notes": notes,
            "package": package,
            "mcp_intake_required": False,
        }

    blockers = list(plan.get("missing_capabilities_or_bindings") or [])
    notes_blockers = [n.get("code") for n in notes if n.get("kind") == "BLOCKER"]
    blockers.extend(x for x in notes_blockers if x)
    status = "READY" if plan.get("executable_now") and not notes_blockers else "BLOCKED"

    return {
        "schema_version": "1.0.0",
        "authority_id": "CP-EXECUTION-001",
        "request_id": request.get("request_id"),
        "intent": intent,
        "status": status,
        "required_inventory": required_inventory,
        "blockers": sorted(set(blockers)),
        "notes": notes,
        "package": package,
        "plan": plan,
        "mcp_intake_required": False,
        "intake_policy": "CREATE_ONLY_LATER_FOR_CONCRETE_REQUIRED_MISSING_CAPABILITY",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile a project requirement into a governed execution package.")
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--server-inventory", type=Path)
    parser.add_argument("--github-metadata", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    request = load_json(args.request)
    server_inventory = load_json(args.server_inventory) if args.server_inventory else None
    github_metadata = load_json(args.github_metadata) if args.github_metadata else None
    result = compile_request(
        request,
        registry=load_json(REGISTRY_PATH),
        snapshot=load_json(SNAPSHOT_PATH),
        server_model=load_json(SERVER_MODEL_PATH),
        server_inventory=server_inventory,
        github_metadata=github_metadata,
    )
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        output = args.output.resolve()
        if ROOT not in output.parents:
            raise SystemExit("OUTPUT_PATH_OUTSIDE_REPOSITORY")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
