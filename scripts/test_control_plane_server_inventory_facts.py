#!/usr/bin/env python3
"""Behavioral tests for the KBI-04D source-only inventory projection."""
from __future__ import annotations

import copy
import importlib.util
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from control_plane_server_inventory_facts import normalize_inventory, validate_inventory_state

SNAPSHOT = json.loads((ROOT / ".governance/control-plane-state/mcp-capability-snapshot.json").read_text())
MODEL = json.loads((ROOT / ".governance/control-plane-state/server-knowledge-model.json").read_text())
SEED = json.loads((ROOT / ".governance/control-plane-state/server-inventory-facts.json").read_text())


def observation(at="2026-09-30T10:00:00+00:00"):
    servers = {}
    for server in ("S1", "S2"):
        suffix = server.lower()
        servers[server] = {
            "RUNTIMES": {
                "docker_status": {"status": "UNKNOWN_DISCOVERABLE", "tool": f"docker_status_{suffix}", "facts": {}},
                "pm2_status": {"status": "UNKNOWN_DISCOVERABLE", "tool": f"pm2_status_{suffix}", "facts": {}},
            },
            "DOMAINS_VHOSTS": {"status": "UNKNOWN_DISCOVERABLE", "tool": f"list_domains_{suffix}", "facts": {}},
            "CAPACITY": {"status": "UNKNOWN_DISCOVERABLE", "tool": f"check_disk_{suffix}", "facts": {}},
            "BACKUP_RECOVERY": {"status": "UNKNOWN_DISCOVERABLE", "tool": f"list_backups_{suffix}", "facts": {}},
        }
    servers["S1"]["DOMAINS_VHOSTS"].update(status="KNOWN_CURRENT", facts={"domains": ["example.org"]})
    servers["S1"]["RUNTIMES"]["docker_status"].update(status="KNOWN_CURRENT", facts={"container_count": 2, "states": {"running": 1, "exited": 1}})
    servers["S1"]["CAPACITY"].update(status="KNOWN_CURRENT", facts={"max_disk_used_percent": 45.5})
    servers["S1"]["BACKUP_RECOVERY"].update(status="KNOWN_CURRENT", facts={"backup_count": 0})
    return {
        "schema_version": "1.0.0", "authority_id": "CP-SERVER-KNOWLEDGE-001", "slice": "KBI-04C",
        "status": "PARTIAL_BOUNDED_OBSERVATION", "observed_at": at,
        "source": {
            "snapshot_authority_id": "CP-MCP-CAP-001", "snapshot_observed_at": SNAPSHOT["observed_at"],
            "catalogue_digest": SNAPSHOT["catalogue"]["catalogue_digest"],
            "method": "LIVE_MCP_READ_ONLY_TOOL_INTERSECTION",
        },
        "mutation_authority_granted": False, "secret_values_persisted": False,
        "servers": servers,
        "unobserved_inventory_domains": [
            "SERVER_IDENTITY", "HOSTING_STACK", "NETWORK", "DNS", "TLS", "FILESYSTEM_LAYOUT",
            "PORTS_SERVICES", "DATABASES", "GIT_DEPLOYMENT", "SECRETS_ENV", "PROCESS_SCHEDULING",
            "OBSERVABILITY", "SECURITY_ACCESS", "PROJECT_MAPPINGS", "MCP_SURFACES",
        ],
    }


class InventoryFactsTests(unittest.TestCase):
    def normalize(self, incoming, state=SEED):
        return normalize_inventory(incoming, state, SNAPSHOT, MODEL, now="2026-09-30T12:00:00+00:00")

    def test_known_fact_has_bounded_value_provenance_and_freshness(self):
        # Catches a reducer that drops source metadata or promotes unknown slots.
        result = self.normalize(observation())
        facts = {item["fact_id"]: item for item in result["facts"]}
        self.assertEqual(len(facts), 10)
        domain = facts["S1:DOMAINS_VHOSTS:domains"]
        self.assertEqual(domain["value"], {"domains": ["example.org"]})
        self.assertEqual(domain["status"], "KNOWN_CURRENT")
        self.assertEqual(domain["freshness_class"], "REFRESH_BEFORE_MUTATION")
        self.assertEqual(domain["known_from"]["source_tool"], "list_domains_s1")
        self.assertEqual(domain["known_from"]["catalogue_digest"], SNAPSHOT["catalogue"]["catalogue_digest"])
        self.assertEqual(facts["S2:DOMAINS_VHOSTS:domains"]["status"], "UNKNOWN_DISCOVERABLE")
        self.assertIsNone(facts["S2:DOMAINS_VHOSTS:domains"]["value"])
        self.assertEqual(facts["S1:CAPACITY:disk"]["freshness_class"], "LIVE_BEFORE_DEPLOY")
        self.assertFalse(result["execution_authority_granted"])
        self.assertFalse(result["secret_values_persisted"])
        validate_inventory_state(result, MODEL)

    def test_replay_is_idempotent_and_conflicting_same_time_fails(self):
        # Catches duplicate revision advances or contradictory facts accepted at one timestamp.
        first = self.normalize(observation())
        self.assertEqual(self.normalize(observation(), first), first)
        changed = observation()
        changed["servers"]["S1"]["DOMAINS_VHOSTS"]["facts"]["domains"] = ["other.example.org"]
        with self.assertRaises(ValueError):
            self.normalize(changed, first)

    def test_failed_refresh_stales_previous_value_and_discards_partial_candidate(self):
        # Catches stale data being presented as current or partial candidate being trusted.
        first = self.normalize(observation())
        next_input = observation("2026-09-30T11:00:00+00:00")
        next_input["servers"]["S1"]["DOMAINS_VHOSTS"].update(
            status="PARTIAL_BOUNDED", facts={"domains": ["other.example.org"]}
        )
        result = self.normalize(next_input, first)
        domain = {item["fact_id"]: item for item in result["facts"]}["S1:DOMAINS_VHOSTS:domains"]
        self.assertEqual(domain["status"], "KNOWN_STALE")
        self.assertEqual(domain["value"], {"domains": ["example.org"]})
        self.assertEqual(domain["last_attempt"]["status"], "PARTIAL_BOUNDED")
        self.assertNotIn("other.example.org", json.dumps(result))
        self.assertEqual(result["revision"], 2)

    def test_rejects_untrusted_snapshot_timestamp_and_unexpected_fields(self):
        # Catches laundering raw tool output or accepting a mismatched capability catalogue.
        incoming = observation()
        incoming["source"]["catalogue_digest"] = "0" * 64
        with self.assertRaises(ValueError):
            self.normalize(incoming)
        incoming = observation("2026-09-30T00:00:00+00:00")
        with self.assertRaises(ValueError):
            self.normalize(incoming)
        incoming = observation()
        incoming["servers"]["S1"]["RUNTIMES"]["docker_status"]["facts"]["container_name"] = "secret-container"
        with self.assertRaises(ValueError):
            self.normalize(incoming)
        incoming = observation()
        incoming["servers"]["S1"]["DOMAINS_VHOSTS"]["facts"]["domains"] = ["/srv/secret"]
        with self.assertRaises(ValueError):
            self.normalize(incoming)

    def test_rejects_tampered_persistent_state(self):
        # Catches edited source-memory data feeding the relational projection.
        state = self.normalize(observation())
        broken = copy.deepcopy(state)
        broken["facts"][0]["value"] = {"private_key": "unsafe"}
        with self.assertRaises(ValueError):
            validate_inventory_state(broken, MODEL)
        changed_value = copy.deepcopy(state)
        domain = next(item for item in changed_value["facts"] if item["fact_id"] == "S1:DOMAINS_VHOSTS:domains")
        domain["value"] = {"domains": ["other.example.org"]}
        with self.assertRaises(ValueError):
            validate_inventory_state(changed_value, MODEL)

    def test_rejects_a_tool_not_classified_as_read_only(self):
        # Catches importing a forged success via a changed or unclassified MCP tool.
        snapshot = copy.deepcopy(SNAPSHOT)
        tool = next(item for item in snapshot["catalogue"]["tools"] if item["name"] == "list_domains_s1")
        tool["surface"] = "write"
        with self.assertRaises(ValueError):
            normalize_inventory(observation(), SEED, snapshot, MODEL, now="2026-09-30T12:00:00+00:00")

    def test_cli_cas_guard_and_relational_projection(self):
        # Catches bypassing revision guard or losing provenance when materializing SQLite.
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            incoming = directory / "observation.json"
            state_path = directory / "facts.json"
            db_path = directory / "control-plane.sqlite"
            incoming.write_text(json.dumps(observation()), encoding="utf-8")
            state_path.write_text(json.dumps(SEED), encoding="utf-8")
            command = [sys.executable, str(ROOT / "scripts/control_plane_server_inventory_facts.py"),
                       "--input", str(incoming), "--output", str(state_path), "--expected-revision", "0"]
            accepted = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            recorded = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(recorded["revision"], 1)
            rejected = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(json.loads(state_path.read_text(encoding="utf-8")), recorded)
            module_spec = importlib.util.spec_from_file_location("materialize", ROOT / ".governance/control-plane-db/materialize.py")
            materialize = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(materialize)
            materialize.build(db_path, inventory_path=state_path)
            with sqlite3.connect(db_path) as conn:
                rows = conn.execute("SELECT fact_id,status,value_json,freshness_class,known_from_json "
                                    "FROM server_inventory_facts WHERE fact_id='S1:DOMAINS_VHOSTS:domains'").fetchall()
                self.assertEqual(len(rows), 1)
                self.assertEqual(json.loads(rows[0][2]), {"domains": ["example.org"]})
                self.assertEqual(rows[0][3], "REFRESH_BEFORE_MUTATION")
                self.assertEqual(json.loads(rows[0][4])["source_tool"], "list_domains_s1")


if __name__ == "__main__":
    unittest.main()
