#!/usr/bin/env python3
"""Collect bounded S1/S2 facts through MCP read surfaces; write only to stdout.

KBI-04C emits transient, deliberately partial observations. KBI-04D is responsible
for deciding whether and how normalized facts may enter canonical memory.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import pathlib
import re
import urllib.error
from datetime import datetime, timezone
from typing import Callable

from control_plane_mcp_capability_snapshot import (
    DEFAULT_ENDPOINT, call_tool, post, rpc, rpc_result, tool_content_json,
)

DEFAULT_SNAPSHOT = pathlib.Path(".governance/control-plane-state/mcp-capability-snapshot.json")
DOMAIN = re.compile(r"(?=.{4,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{1,62}$")
OBSERVATIONS = (
    ("list_domains", "DOMAINS_VHOSTS", "domains"),
    ("docker_status", "RUNTIMES", "docker_status"),
    ("pm2_status", "RUNTIMES", "pm2_status"),
    ("check_disk", "CAPACITY", "disk"),
    ("list_backups", "BACKUP_RECOVERY", "backups"),
)
STATES = {"running", "stopped", "exited", "online", "offline", "errored", "error"}


def collection_plan(snapshot: dict, live_tools: list[dict]) -> list[dict]:
    if snapshot.get("authority_id") != "CP-MCP-CAP-001":
        raise ValueError("SNAPSHOT_AUTHORITY_INVALID")
    catalogue = snapshot.get("catalogue") or {}
    source_tools = {item.get("name"): item for item in catalogue.get("tools", []) if isinstance(item, dict)}
    live_by_name = {item.get("name"): item for item in live_tools if isinstance(item, dict)}
    capability_map = snapshot.get("capability_map") or {}
    plan = []
    for server in ("S1", "S2"):
        for prefix, domain, slot in OBSERVATIONS:
            name = f"{prefix}_{server.lower()}"
            source = source_tools.get(name) or {}
            live = live_by_name.get(name) or {}
            annotations = live.get("annotations") if isinstance(live.get("annotations"), dict) else {}
            capability_id = "DOMAIN_WEB_OBSERVATION" if prefix == "list_domains" else "SERVER_RUNTIME_OBSERVATION"
            capability = capability_map.get(capability_id) or {}
            candidates = [
                candidate for candidate in capability.get("candidate_tools", [])
                if isinstance(candidate, dict) and candidate.get("tool") == name
            ]
            candidate_safe = (
                capability.get("kind") == "OBSERVATION" and len(candidates) == 1
                and candidates[0].get("surface") == "read"
                and candidates[0].get("authority_required") == "READ_ONLY_DISCOVERY_AUTHORITY"
                and (candidates[0].get("scope") or {}).get("mode") == "GENERIC"
            )
            fields = source.get("input_fields")
            no_required_arguments = isinstance(fields, list) and not any(
                isinstance(field, dict) and field.get("required") for field in fields
            )
            safe = (
                source.get("surface") == "read"
                and bool(live)
                and candidate_safe
                and sum(t.get("name") == name for t in catalogue.get("tools", []) if isinstance(t, dict)) == 1
                and sum(t.get("name") == name for t in live_tools if isinstance(t, dict)) == 1
                and no_required_arguments
                and annotations.get("readOnlyHint") is not False
                and annotations.get("destructiveHint") is not True
            )
            plan.append({
                "server": server, "domain": domain, "slot": slot, "tool": name,
                "status": "READY" if safe else "BLOCKED",
            })
    return plan


def domain_facts(payload):
    candidates = payload.get("domains") if isinstance(payload, dict) else payload
    if isinstance(payload, dict) and isinstance(payload.get("text"), str):
        candidates = payload["text"].splitlines()
    if not isinstance(candidates, list):
        return None
    if len(candidates) > 200:
        return None
    domains = []
    for item in candidates:
        name = item.get("domain") or item.get("name") if isinstance(item, dict) else item
        if isinstance(name, str) and DOMAIN.fullmatch(name.lower().strip()):
            domains.append(name.lower().strip())
    return {"domains": sorted(set(domains))}


def runtime_facts(payload, slot: str):
    key, count_key = ("containers", "container_count") if slot == "docker_status" else ("apps", "process_count")
    items = payload.get(key) if isinstance(payload, dict) else None
    if not isinstance(items, list):
        return None
    counts: dict[str, int] = {}
    for item in items:
        state = item.get("status") or item.get("state") if isinstance(item, dict) else None
        normalized = state.lower() if isinstance(state, str) else "unknown"
        normalized = normalized if normalized in STATES else "unknown"
        counts[normalized] = counts.get(normalized, 0) + 1
    return {count_key: len(items), "states": dict(sorted(counts.items()))}


def disk_facts(payload):
    if not isinstance(payload, dict):
        return None
    items = payload.get("filesystems") or payload.get("mounts")
    if not isinstance(items, list):
        items = [payload]
    percentages = []
    for item in items:
        if not isinstance(item, dict):
            continue
        value = item.get("used_percent", item.get("percent_used"))
        if isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value) and 0 <= value <= 100:
            percentages.append(value)
    return {"max_disk_used_percent": max(percentages)} if percentages else None


def backup_facts(payload):
    items = payload.get("backups") if isinstance(payload, dict) else payload
    return {"backup_count": len(items)} if isinstance(items, list) else None


def extract_facts(payload, slot: str):
    if slot == "domains":
        return domain_facts(payload)
    if slot in ("docker_status", "pm2_status"):
        return runtime_facts(payload, slot)
    if slot == "disk":
        return disk_facts(payload)
    return backup_facts(payload)


def collect_inventory(
    snapshot: dict, live_tools: list[dict], invoke: Callable[[str], dict], *, observed_at: str,
) -> dict:
    servers = {server: {"RUNTIMES": {}} for server in ("S1", "S2")}
    plan = collection_plan(snapshot, live_tools)
    for item in plan:
        observation = {"status": "UNKNOWN_DISCOVERABLE", "tool": item["tool"], "facts": {}}
        if item["status"] == "READY":
            try:
                response = invoke(item["tool"])
                if not rpc_result(response).get("isError"):
                    facts = extract_facts(tool_content_json(response), item["slot"])
                    if facts is not None:
                        observation.update(status="KNOWN_CURRENT", facts=facts)
            except Exception:
                # Remote errors can include credential or host material; never copy them.
                pass
        target = servers[item["server"]]
        if item["domain"] == "RUNTIMES":
            target["RUNTIMES"][item["slot"]] = observation
        else:
            target[item["domain"]] = observation
    return {
        "schema_version": "1.0.0",
        "authority_id": "CP-SERVER-KNOWLEDGE-001",
        "slice": "KBI-04C",
        "status": "PARTIAL_BOUNDED_OBSERVATION",
        "observed_at": observed_at,
        "source": {
            "snapshot_authority_id": snapshot["authority_id"],
            "snapshot_observed_at": snapshot.get("observed_at"),
            "catalogue_digest": (snapshot.get("catalogue") or {}).get("catalogue_digest"),
            "method": "LIVE_MCP_READ_ONLY_TOOL_INTERSECTION",
        },
        "mutation_authority_granted": False,
        "secret_values_persisted": False,
        "servers": servers,
        "unobserved_inventory_domains": [
            "SERVER_IDENTITY", "HOSTING_STACK", "NETWORK", "DNS", "TLS", "FILESYSTEM_LAYOUT",
            "PORTS_SERVICES", "DATABASES", "GIT_DEPLOYMENT", "SECRETS_ENV",
            "PROCESS_SCHEDULING", "OBSERVABILITY", "SECURITY_ACCESS", "PROJECT_MAPPINGS",
            "MCP_SURFACES",
        ],
    }


def live_collect(snapshot: dict, endpoint: str, token: str) -> dict:
    init, session = post(endpoint, token, {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": "governed-server-inventory", "version": "1.0"},
        },
    })
    if not session or not rpc_result(init):
        raise RuntimeError("MCP_INITIALIZATION_FAILED")
    try:
        post(endpoint, token, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, session)
    except (urllib.error.URLError, RuntimeError):
        pass
    response, session = rpc(endpoint, token, session, 2, "tools/list", {})
    tools = rpc_result(response).get("tools")
    if not isinstance(tools, list):
        raise RuntimeError("MCP_LIVE_CATALOGUE_MISSING")
    request_id = 2

    def invoke(name: str) -> dict:
        nonlocal request_id
        request_id += 1
        return call_tool(endpoint, token, session, request_id, name)

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return collect_inventory(snapshot, tools, invoke, observed_at=timestamp)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=pathlib.Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--endpoint", default=os.environ.get("GOVERNED_MCP_URL") or DEFAULT_ENDPOINT)
    args = parser.parse_args()
    token = os.environ.get("GOVERNED_MCP_AUTH_TOKEN")
    if not token:
        raise SystemExit("KBI_04C_BLOCKED:GOVERNED_MCP_AUTH_TOKEN_MISSING")
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        result = live_collect(snapshot, args.endpoint, token)
    except (OSError, ValueError, RuntimeError, urllib.error.URLError) as exc:
        raise SystemExit(f"KBI_04C_FAILED:{type(exc).__name__}") from None
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
