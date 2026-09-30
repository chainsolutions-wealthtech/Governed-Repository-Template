#!/usr/bin/env python3
"""Derive KBI-04E recipe/tool gaps from versioned source authorities.

The matrix is read-only planning evidence, not a live tools/list or authority grant.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from control_plane_server_inventory_facts import validate_inventory_state

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / ".governance/control-plane-state/server-knowledge-model.json"
SNAPSHOT = ROOT / ".governance/control-plane-state/mcp-capability-snapshot.json"
INVENTORY = ROOT / ".governance/control-plane-state/server-inventory-facts.json"


def classify_capability(capability_id, capability_map, catalogue):
    capability = capability_map.get(capability_id)
    if capability is None:
        return {"capability_id": capability_id, "status": "CAPABILITY_UNDEFINED",
                "candidate_tools": [], "execution_ready": False}
    kind = capability.get("kind")
    if kind not in {"OBSERVATION", "MUTATION"} or not isinstance(capability.get("candidate_tools"), list):
        raise ValueError("KBI_04E_CAPABILITY_MODEL_INVALID")
    valid = []
    contradiction = False
    for candidate in capability["candidate_tools"]:
        if not isinstance(candidate, dict) or not isinstance(candidate.get("tool"), str):
            contradiction = True
            continue
        name = candidate["tool"]
        matches = catalogue.get(name, [])
        if len(matches) != 1 or any(candidate.get(key) != matches[0].get(key) for key in ("surface", "authority_required")):
            contradiction = True
            continue
        mode = (candidate.get("scope") or {}).get("mode")
        if mode not in {"GENERIC", "PROJECT_REGISTRY_SCOPED", "PROJECT_SPECIFIC"}:
            contradiction = True
            continue
        required_surface = "read" if kind == "OBSERVATION" else "scoped-write"
        required_authority = ("READ_ONLY_DISCOVERY_AUTHORITY" if kind == "OBSERVATION"
                              else "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED")
        if candidate["surface"] == required_surface and candidate["authority_required"] != required_authority:
            contradiction = True
            continue
        if candidate["surface"] != required_surface:
            # Read-only preflight does not satisfy a mutation requirement.
            continue
        valid.append({"tool": name, "surface": candidate["surface"], "scope": mode})
    if contradiction:
        status = "CATALOGUE_CONTRADICTION"
        valid = []
    elif any(item["scope"] == "GENERIC" for item in valid):
        status = "GENERIC_SNAPSHOT_CANDIDATE"
    elif valid:
        status = "PROJECT_SCOPED_ONLY" if all(item["scope"] == "PROJECT_REGISTRY_SCOPED" for item in valid) else "PROJECT_SPECIFIC_ONLY"
    else:
        status = "NO_OBSERVATION_CANDIDATE" if kind == "OBSERVATION" else "NO_MUTATION_CANDIDATE"
    return {
        "capability_id": capability_id,
        "status": status,
        "candidate_tools": sorted(valid, key=lambda item: item["tool"]),
        "execution_ready": False,
    }


def build_matrix(model, snapshot, inventory):
    if model.get("authority_id") != "CP-SERVER-KNOWLEDGE-001" or snapshot.get("authority_id") != "CP-MCP-CAP-001":
        raise ValueError("KBI_04E_AUTHORITY_MISMATCH")
    if snapshot.get("mutation_authority_granted") is not False or inventory.get("execution_authority_granted") is not False:
        raise ValueError("KBI_04E_AUTHORITY_UNSAFE")
    validate_inventory_state(inventory, model)
    digest = (snapshot.get("catalogue") or {}).get("catalogue_digest")
    if not isinstance(digest, str) or len(digest) != 64 or snapshot.get("observed_at") is None:
        raise ValueError("KBI_04E_SNAPSHOT_INVALID")
    catalogue = {}
    for tool in snapshot["catalogue"]["tools"]:
        if not isinstance(tool, dict):
            raise ValueError("KBI_04E_CATALOGUE_INVALID")
        catalogue.setdefault(tool.get("name"), []).append(tool)
    map_by_id = snapshot.get("capability_map") or {}
    domains = {item["id"]: item["freshness"] for item in model["inventory_domains"]}
    known = {}
    for fact in inventory["facts"]:
        if fact["status"] == "KNOWN_CURRENT":
            known[fact["domain_id"]] = known.get(fact["domain_id"], 0) + 1
    recipes = []
    for recipe in model["operation_recipes"]:
        requested = recipe["required_capabilities"]
        required_inventory = recipe["required_inventory"]
        if not isinstance(requested, list) or not requested or len(requested) != len(set(requested)) or not isinstance(required_inventory, list) or any(domain not in domains for domain in required_inventory):
            raise ValueError("KBI_04E_RECIPE_REQUIREMENTS_INVALID")
        capabilities = [classify_capability(item, map_by_id, catalogue) for item in requested]
        inventory_slots = [
            {"domain_id": domain, "status": "BOUNDED_OBSERVATION" if known.get(domain, 0) else "NO_PERSISTED_OBSERVATION",
             "known_slot_count": known.get(domain, 0), "freshness_class": domains[domain], "execution_ready": False}
            for domain in required_inventory
        ]
        recipes.append({
            "recipe_id": recipe["id"], "intent": recipe["intent"],
            "inventory": inventory_slots, "capabilities": capabilities,
        })
    gaps = sorted({item["capability_id"] for recipe in recipes for item in recipe["capabilities"]
                   if item["status"] in {"CAPABILITY_UNDEFINED", "NO_MUTATION_CANDIDATE", "NO_OBSERVATION_CANDIDATE", "CATALOGUE_CONTRADICTION"}})
    scoped = sorted({item["capability_id"] for recipe in recipes for item in recipe["capabilities"]
                     if item["status"] in {"PROJECT_SCOPED_ONLY", "PROJECT_SPECIFIC_ONLY"}})
    return {
        "schema_version": "1.0.0", "slice": "KBI-04E", "status": "DERIVED_PLANNING_MATRIX",
        "source": {"server_model_authority_id": model["authority_id"],
                   "snapshot_authority_id": snapshot["authority_id"],
                   "snapshot_observed_at": snapshot["observed_at"],
                   "catalogue_digest": digest,
                   "server_inventory_revision": inventory["revision"]},
        "live_tool_attestation": False, "execution_authority_granted": False,
        "recipes": recipes, "capability_gaps": gaps, "scope_constraints": scoped,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=MODEL)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    parser.add_argument("--inventory", type=Path, default=INVENTORY)
    args = parser.parse_args()
    try:
        matrix = build_matrix(
            json.loads(args.model.read_text(encoding="utf-8")),
            json.loads(args.snapshot.read_text(encoding="utf-8")),
            json.loads(args.inventory.read_text(encoding="utf-8")),
        )
    except (OSError, KeyError, TypeError, ValueError):
        raise SystemExit("KBI_04E_SOURCE_INVALID") from None
    print(json.dumps(matrix, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
