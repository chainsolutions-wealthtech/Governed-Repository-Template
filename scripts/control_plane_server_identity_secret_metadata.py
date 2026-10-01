#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from governed_execution_engine import McpClient, ROOT, SNAPSHOT_PATH, load_json

IDENTITY_MODEL_PATH = ROOT / ".governance" / "control-plane-state" / "identity-secret-lifecycle.json"

SERVER_CREDENTIAL_TYPES = {
    "SSH_OIDC_EPHEMERAL_CERTIFICATE": [],
    "SERVER_SERVICE_ACCOUNT": ["SERVER_RUNTIME_CHANGE"],
    "APPLICATION_ENV_SECRET": ["SECRET_PROVISIONING"],
    "DATABASE_CREDENTIAL": ["DATABASE_CHANGE", "SECRET_PROVISIONING"],
    "DNS_PROVIDER_TOKEN": ["DOMAIN_DNS_CHANGE"],
    "TLS_PRIVATE_KEY": ["TLS_CHANGE"],
}

SERVER_PROBES = {
    "S1": ["docker_status_s1", "pm2_status_s1", "scan_mcp_secrets_s1"],
    "S2": ["docker_status_s2", "pm2_status_s2"],
}

SAFE_STATUS_VALUES = {
    "PASS", "OK", "SUCCESS", "PARTIAL", "UNKNOWN", "EMPTY",
    "KNOWN_CURRENT", "NOT_FOUND", "NO_FINDINGS",
}


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def digest_payload(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


def safe_probe_summary(tool: str, value: Any) -> dict:
    """Return structure/digest only; never persist arbitrary remote strings."""
    status = None
    if isinstance(value, dict):
        raw_status = value.get("status")
        if isinstance(raw_status, str) and raw_status.upper() in SAFE_STATUS_VALUES:
            status = raw_status.upper()
        top_keys = sorted(str(k) for k in value.keys())[:32]
        kind = "OBJECT"
        item_count = len(value)
    elif isinstance(value, list):
        top_keys = []
        kind = "ARRAY"
        item_count = len(value)
    else:
        top_keys = []
        kind = type(value).__name__.upper()
        item_count = 1
    return {
        "tool": tool,
        "status": status or "OBSERVED_RESPONSE",
        "response_kind": kind,
        "item_count": item_count,
        "top_level_keys": top_keys,
        "response_digest": digest_payload(value),
        "raw_payload_persisted": False,
    }


def tool_catalogue(snapshot: dict) -> dict[str, dict]:
    return {
        item.get("name"): item
        for item in ((snapshot.get("catalogue") or {}).get("tools") or [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }


def capability_state(snapshot: dict, capability_id: str) -> dict:
    cap = (snapshot.get("capability_map") or {}).get(capability_id)
    if not isinstance(cap, dict):
        return {"capability_id": capability_id, "status": "CAPABILITY_UNDEFINED", "candidate_tools": []}
    candidates = []
    for item in cap.get("candidate_tools") or []:
        if not isinstance(item, dict):
            continue
        candidates.append({
            "tool": item.get("tool"),
            "surface": item.get("surface"),
            "authority_required": item.get("authority_required"),
            "scope_mode": (item.get("scope") or {}).get("mode"),
        })
    availability = str(cap.get("availability") or "UNKNOWN")
    status = "AVAILABLE" if candidates and not availability.startswith("NOT_EXPOSED") else "NOT_EXPOSED"
    return {
        "capability_id": capability_id,
        "status": status,
        "availability": availability,
        "candidate_tools": candidates,
    }


def mechanism_matrix(identity_model: dict, snapshot: dict, server_id: str) -> list[dict]:
    types = {
        item["id"]: item
        for item in identity_model.get("credential_types") or []
        if isinstance(item, dict) and item.get("plane") == "SERVER_PRODUCTION_PLANE"
    }
    rows = []
    for credential_id, required_caps in SERVER_CREDENTIAL_TYPES.items():
        model = types.get(credential_id)
        if model is None:
            rows.append({
                "credential_type": credential_id,
                "status": "MODEL_MISSING",
                "server_id": server_id,
                "capabilities": [],
            })
            continue
        caps = [capability_state(snapshot, cap) for cap in required_caps]
        if credential_id == "SSH_OIDC_EPHEMERAL_CERTIFICATE":
            status = "RUNTIME_MINT_PATH_IMPLEMENTED"
        elif required_caps and all(item["status"] == "AVAILABLE" for item in caps):
            status = "MCP_CAPABILITY_AVAILABLE"
        else:
            status = "MODELLED_CAPABILITY_GAP"
        rows.append({
            "credential_type": credential_id,
            "server_id": server_id,
            "status": status,
            "lifecycle": model.get("lifecycle"),
            "creation_mode": model.get("creation"),
            "retrieval_mode": model.get("retrieval"),
            "injection_mode": model.get("injection"),
            "verification_mode": model.get("verification"),
            "rotation_mode": model.get("rotation"),
            "revocation_mode": model.get("revocation"),
            "value_persistence": model.get("value_persistence"),
            "capabilities": caps,
        })
    return rows


def build_plan(snapshot: dict, identity_model: dict, server_ids: list[str]) -> dict:
    catalogue = tool_catalogue(snapshot)
    servers = {}
    for server_id in server_ids:
        probes = []
        for name in SERVER_PROBES[server_id]:
            item = catalogue.get(name)
            probes.append({
                "tool": name,
                "available": bool(item),
                "surface": item.get("surface") if item else None,
                "authority_required": item.get("authority_required") if item else None,
                "value_readback_expected": False,
            })
        servers[server_id] = {
            "probes": probes,
            "mechanisms": mechanism_matrix(identity_model, snapshot, server_id),
        }
    return {
        "schema_version": "1.0.0",
        "authority_id": "CP-IDENTITY-SECRET-001",
        "slice": "KBI-04K",
        "mode": "READ_ONLY_METADATA_PLAN",
        "snapshot_observed_at": snapshot.get("observed_at"),
        "catalogue_digest": (snapshot.get("catalogue") or {}).get("catalogue_digest"),
        "servers": servers,
        "mutation_authority_granted": False,
        "secret_values_persisted": False,
        "server_connection_coordinates_persisted": False,
    }


def collect_live(
    plan: dict,
    *,
    client_factory: Callable[[str, str], Any],
    endpoint: str,
    token: str,
) -> dict:
    client = client_factory(endpoint, token)
    result = {
        "schema_version": "1.0.0",
        "authority_id": "CP-IDENTITY-SECRET-001",
        "slice": "KBI-04K",
        "mode": "READ_ONLY_METADATA_OBSERVATION",
        "observed_at": utcnow(),
        "source_snapshot_observed_at": plan.get("snapshot_observed_at"),
        "catalogue_digest": plan.get("catalogue_digest"),
        "servers": {},
        "mutation_authority_granted": False,
        "secret_values_persisted": False,
        "raw_remote_payload_persisted": False,
        "server_connection_coordinates_persisted": False,
    }
    for server_id, server_plan in plan["servers"].items():
        observations = []
        for probe in server_plan["probes"]:
            if not probe["available"]:
                observations.append({
                    "tool": probe["tool"],
                    "status": "NOT_EXPOSED",
                    "raw_payload_persisted": False,
                })
                continue
            if probe["surface"] != "read" or probe["authority_required"] != "READ_ONLY_DISCOVERY_AUTHORITY":
                observations.append({
                    "tool": probe["tool"],
                    "status": "UNSAFE_SURFACE_REJECTED",
                    "raw_payload_persisted": False,
                })
                continue
            try:
                remote = client.call_tool(probe["tool"], {})
                observations.append(safe_probe_summary(probe["tool"], remote))
            except Exception:
                observations.append({
                    "tool": probe["tool"],
                    "status": "OBSERVATION_FAILED",
                    "raw_payload_persisted": False,
                })
        result["servers"][server_id] = {
            "mechanisms": server_plan["mechanisms"],
            "observations": observations,
            "identity_secret_store_status": (
                "PARTIAL_BOUNDED_OBSERVATION"
                if observations
                else "UNKNOWN_DISCOVERABLE"
            ),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="KBI-04K bounded S1/S2 identity/secret mechanism mapper.")
    parser.add_argument("--server", choices=["S1", "S2", "ALL"], default="ALL")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    snapshot = load_json(SNAPSHOT_PATH)
    identity_model = load_json(IDENTITY_MODEL_PATH)
    server_ids = ["S1", "S2"] if args.server == "ALL" else [args.server]
    plan = build_plan(snapshot, identity_model, server_ids)

    if not args.live:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return

    endpoint = os.environ.get("GOVERNED_MCP_URL") or "https://mcp.wealthtechinnovations.com/mcp"
    token = os.environ.get("GOVERNED_MCP_AUTH_TOKEN")
    if not token:
        raise SystemExit("KBI_04K_BLOCKED:GOVERNED_MCP_AUTH_TOKEN_MISSING")
    observation = collect_live(
        plan,
        client_factory=McpClient,
        endpoint=endpoint,
        token=token,
    )
    print(json.dumps(observation, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
