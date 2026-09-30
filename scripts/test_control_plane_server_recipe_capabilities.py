#!/usr/bin/env python3
"""Tests for the KBI-04E recipe/capability projection."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from control_plane_server_recipe_capabilities import build_matrix

MODEL = json.loads((ROOT / ".governance/control-plane-state/server-knowledge-model.json").read_text())
SNAPSHOT = json.loads((ROOT / ".governance/control-plane-state/mcp-capability-snapshot.json").read_text())
INVENTORY = json.loads((ROOT / ".governance/control-plane-state/server-inventory-facts.json").read_text())


class RecipeCapabilityTests(unittest.TestCase):
    def test_maps_every_recipe_requirement_without_claiming_mutation_readiness(self):
        # Catches a mapper that skips recipe requirements or treats a snapshot as live authority.
        matrix = build_matrix(MODEL, SNAPSHOT, INVENTORY)
        self.assertEqual(len(matrix["recipes"]), 15)
        self.assertFalse(matrix["execution_authority_granted"])
        self.assertFalse(matrix["live_tool_attestation"])
        recipes = {item["recipe_id"]: item for item in matrix["recipes"]}
        subdomain = {item["capability_id"]: item for item in recipes["SRV-OP-002"]["capabilities"]}
        self.assertEqual(set(subdomain), {"WEB_HOSTING_CHANGE", "DOMAIN_DNS_CHANGE", "TLS_CHANGE"})
        self.assertEqual(subdomain["DOMAIN_DNS_CHANGE"]["status"], "CAPABILITY_UNDEFINED")
        self.assertEqual(subdomain["WEB_HOSTING_CHANGE"]["status"], "NO_MUTATION_CANDIDATE")
        self.assertEqual(subdomain["TLS_CHANGE"]["status"], "NO_MUTATION_CANDIDATE")
        self.assertTrue(all(not item["execution_ready"] for recipe in matrix["recipes"] for item in recipe["capabilities"]))
        self.assertEqual(matrix["source"]["catalogue_digest"], SNAPSHOT["catalogue"]["catalogue_digest"])

    def test_project_scoped_tool_is_not_generic_and_read_preflight_is_not_mutation(self):
        # Catches a mapper that claims a Git pull for arbitrary new projects such as Ekyc.
        recipes = {item["recipe_id"]: item for item in build_matrix(MODEL, SNAPSHOT, INVENTORY)["recipes"]}
        binding = {item["capability_id"]: item for item in recipes["SRV-OP-008"]["capabilities"]}
        self.assertEqual(binding["SERVER_REPOSITORY_CHANGE"]["status"], "PROJECT_SCOPED_ONLY")
        self.assertTrue(all(tool["surface"] == "scoped-write" and tool["scope"] == "PROJECT_REGISTRY_SCOPED"
                            for tool in binding["SERVER_REPOSITORY_CHANGE"]["candidate_tools"]))
        self.assertNotIn("git_status_project_s2", [tool["tool"] for tool in binding["SERVER_REPOSITORY_CHANGE"]["candidate_tools"]])
        self.assertEqual(binding["MCP_PROJECT_BINDING_CHANGE"]["status"], "CAPABILITY_UNDEFINED")
        self.assertEqual(
            build_matrix(MODEL, SNAPSHOT, INVENTORY)["scope_constraints"],
            ["DEPLOYMENT_RUNTIME_CHANGE", "SERVER_REPOSITORY_CHANGE"],
        )

    def test_observation_candidates_do_not_satisfy_inventory_or_live_gate(self):
        # Catches a mapper that confuses an available read tool with an observed server fact.
        recipes = {item["recipe_id"]: item for item in build_matrix(MODEL, SNAPSHOT, INVENTORY)["recipes"]}
        attest = {item["capability_id"]: item for item in recipes["SRV-OP-015"]["capabilities"]}
        self.assertEqual(attest["SERVER_RUNTIME_OBSERVATION"]["status"], "GENERIC_SNAPSHOT_CANDIDATE")
        self.assertEqual(attest["DOMAIN_WEB_OBSERVATION"]["status"], "GENERIC_SNAPSHOT_CANDIDATE")
        self.assertEqual({item["status"] for item in recipes["SRV-OP-015"]["inventory"]}, {"NO_PERSISTED_OBSERVATION"})
        self.assertEqual(recipes["SRV-OP-015"]["inventory"][0]["known_slot_count"], 0)

    def test_catalogue_contradiction_fails_closed(self):
        # Catches promoting an advertised capability when its tool catalogue contradicts it.
        snapshot = copy.deepcopy(SNAPSHOT)
        tool = next(item for item in snapshot["catalogue"]["tools"] if item["name"] == "docker_status_s1")
        tool["surface"] = "scoped-write"
        recipes = {item["recipe_id"]: item for item in build_matrix(MODEL, snapshot, INVENTORY)["recipes"]}
        attest = {item["capability_id"]: item for item in recipes["SRV-OP-015"]["capabilities"]}
        self.assertEqual(attest["SERVER_RUNTIME_OBSERVATION"]["status"], "CATALOGUE_CONTRADICTION")
        self.assertEqual(attest["SERVER_RUNTIME_OBSERVATION"]["candidate_tools"], [])

    def test_write_surface_with_read_only_authority_cannot_satisfy_mutation(self):
        # Catches trusting a write-looking surface with the wrong authority class.
        snapshot = copy.deepcopy(SNAPSHOT)
        candidate = next(item for item in snapshot["capability_map"]["SERVER_REPOSITORY_CHANGE"]["candidate_tools"]
                         if item["tool"] == "git_pull_project_s2")
        catalogue_tool = next(item for item in snapshot["catalogue"]["tools"] if item["name"] == "git_pull_project_s2")
        candidate["authority_required"] = "READ_ONLY_DISCOVERY_AUTHORITY"
        catalogue_tool["authority_required"] = "READ_ONLY_DISCOVERY_AUTHORITY"
        recipes = {item["recipe_id"]: item for item in build_matrix(MODEL, snapshot, INVENTORY)["recipes"]}
        binding = {item["capability_id"]: item for item in recipes["SRV-OP-008"]["capabilities"]}
        self.assertEqual(binding["SERVER_REPOSITORY_CHANGE"]["status"], "CATALOGUE_CONTRADICTION")

    def test_derived_matrix_is_deterministic_and_does_not_copy_project_ids(self):
        # Catches duplicating volatile project registry entries into a second authority.
        first = build_matrix(MODEL, SNAPSHOT, INVENTORY)
        second = build_matrix(MODEL, SNAPSHOT, INVENTORY)
        self.assertEqual(first, second)
        serialized = json.dumps(first)
        self.assertNotIn("brvmchainsolution", serialized)
        self.assertNotIn("project_ids", serialized)
        self.assertEqual(first["source"]["server_inventory_revision"], 0)


if __name__ == "__main__":
    unittest.main()
