#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gacr_agent_telemetry as telemetry
import gacr_capacity_dispatch as capacity
import gacr_task_pool as pool


class TaskPoolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.paths = {
            "sessions": self.base / "sessions.json",
            "claims": self.base / "claims.json",
            "beacons": self.base / "beacons.json",
            "correlations": self.base / "correlations.json",
            "dispatches": self.base / "dispatches.json",
            "takeovers": self.base / "takeovers.json",
            "forensics": self.base / "forensics.json",
            "work": self.base / "work-items.json",
            "tasks": self.base / "tasks.json",
            "blueprint": self.base / "blueprint.json",
            "pool": self.base / "task-pool.json",
        }
        self.original = {
            "pool_TEMPLATE_SOURCE": pool.TEMPLATE_SOURCE,
            "pool_POOL_PATH": pool.POOL_PATH,
            "pool_WORK_ITEMS_PATH": pool.WORK_ITEMS_PATH,
            "pool_TASKS_PATH": pool.TASKS_PATH,
            "pool_BLUEPRINT_PATH": pool.BLUEPRINT_PATH,
            "capacity_SESSIONS_PATH": capacity.SESSIONS_PATH,
            "capacity_CLAIMS_PATH": capacity.CLAIMS_PATH,
            "capacity_BEACONS_PATH": capacity.BEACONS_PATH,
            "capacity_CORRELATIONS_PATH": capacity.CORRELATIONS_PATH,
            "capacity_DISPATCHES_PATH": capacity.DISPATCHES_PATH,
            "telemetry_TAKEOVERS_PATH": telemetry.TAKEOVERS_PATH,
            "telemetry_FORENSICS_PATH": telemetry.FORENSICS_PATH,
            "telemetry_SESSIONS_PATH": telemetry.SESSIONS_PATH,
            "telemetry_CLAIMS_PATH": telemetry.CLAIMS_PATH,
            "telemetry_BEACONS_PATH": telemetry.BEACONS_PATH,
            "telemetry_CORRELATIONS_PATH": telemetry.CORRELATIONS_PATH,
            "capacity_agent_pool_projection": capacity.agent_pool_projection,
            "capacity_config": capacity.config,
            "pool_git_head": pool.git_head,
        }
        pool.TEMPLATE_SOURCE = True
        pool.POOL_PATH = self.paths["pool"]
        pool.WORK_ITEMS_PATH = self.paths["work"]
        pool.TASKS_PATH = self.paths["tasks"]
        pool.BLUEPRINT_PATH = self.paths["blueprint"]
        capacity.SESSIONS_PATH = self.paths["sessions"]
        capacity.CLAIMS_PATH = self.paths["claims"]
        capacity.BEACONS_PATH = self.paths["beacons"]
        capacity.CORRELATIONS_PATH = self.paths["correlations"]
        capacity.DISPATCHES_PATH = self.paths["dispatches"]
        telemetry.SESSIONS_PATH = self.paths["sessions"]
        telemetry.CLAIMS_PATH = self.paths["claims"]
        telemetry.BEACONS_PATH = self.paths["beacons"]
        telemetry.CORRELATIONS_PATH = self.paths["correlations"]
        telemetry.TAKEOVERS_PATH = self.paths["takeovers"]
        telemetry.FORENSICS_PATH = self.paths["forensics"]
        capacity.config = lambda: {
            "max_parallel_offers_per_session": 1,
            "available_states": ["AVAILABLE", "WAITING"],
            "require_explicit_availability": True,
        }
        pool.git_head = lambda: "a" * 40
        self._write_defaults()

    def tearDown(self):
        pool.TEMPLATE_SOURCE = self.original["pool_TEMPLATE_SOURCE"]
        pool.POOL_PATH = self.original["pool_POOL_PATH"]
        pool.WORK_ITEMS_PATH = self.original["pool_WORK_ITEMS_PATH"]
        pool.TASKS_PATH = self.original["pool_TASKS_PATH"]
        pool.BLUEPRINT_PATH = self.original["pool_BLUEPRINT_PATH"]
        capacity.SESSIONS_PATH = self.original["capacity_SESSIONS_PATH"]
        capacity.CLAIMS_PATH = self.original["capacity_CLAIMS_PATH"]
        capacity.BEACONS_PATH = self.original["capacity_BEACONS_PATH"]
        capacity.CORRELATIONS_PATH = self.original["capacity_CORRELATIONS_PATH"]
        capacity.DISPATCHES_PATH = self.original["capacity_DISPATCHES_PATH"]
        telemetry.TAKEOVERS_PATH = self.original["telemetry_TAKEOVERS_PATH"]
        telemetry.FORENSICS_PATH = self.original["telemetry_FORENSICS_PATH"]
        telemetry.SESSIONS_PATH = self.original["telemetry_SESSIONS_PATH"]
        telemetry.CLAIMS_PATH = self.original["telemetry_CLAIMS_PATH"]
        telemetry.BEACONS_PATH = self.original["telemetry_BEACONS_PATH"]
        telemetry.CORRELATIONS_PATH = self.original["telemetry_CORRELATIONS_PATH"]
        capacity.agent_pool_projection = self.original["capacity_agent_pool_projection"]
        capacity.config = self.original["capacity_config"]
        pool.git_head = self.original["pool_git_head"]
        self.tmp.cleanup()

    def write(self, key: str, value: dict) -> None:
        self.paths[key].write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def read(self, key: str) -> dict:
        return json.loads(self.paths[key].read_text(encoding="utf-8"))

    def _write_defaults(self):
        self.write("sessions", {"schema_version": "1.0.0", "revision": 0, "sessions": []})
        self.write("claims", {"schema_version": "1.0.0", "revision": 0, "claims": []})
        self.write("beacons", {"schema_version": "1.0.0", "revision": 0, "items": []})
        self.write("correlations", {"schema_version": "1.0.0", "revision": 0, "items": []})
        self.write("dispatches", {"schema_version": "1.0.0", "revision": 0, "items": []})
        self.write("takeovers", {"schema_version": "1.0.0", "revision": 0, "items": []})
        self.write("forensics", {"schema_version": "1.0.0", "revision": 0, "items": []})
        self.write("work", {"revision": 0, "items": []})
        self.write("tasks", {
            "revision": 1,
            "items": [{"id": "GMC-01", "status": "IN_PROGRESS"}],
        })
        self.write("blueprint", {
            "status": "PLANNING_ONLY",
            "groups": [{
                "group_id": "GMC-G01",
                "legacy_id": "GMC-01",
                "status": "PLANNED",
                "planning_only": True,
                "implementation_authorized": False,
                "objective": "Separate model from strategies.",
                "where_to_look": ["docs/control-plane/CANONICAL_ARCHITECTURE.md"],
                "search_order": ["authorities/docs", "machine state"],
                "inputs": ["CP-ARCH-001"],
                "atomic_tasks": [
                    {
                        "task_id": "GMC-G01-T01",
                        "title": "Inventory authorities.",
                        "status": "PLANNED",
                        "planning_only": True,
                        "implementation_authorized": False,
                        "depends_on": [],
                        "method": "Observe → extract → preserve provenance.",
                        "evidence_required": ["source path/ref"],
                        "done_when": "Inventory complete.",
                        "hold_if": "Critical contradiction.",
                    },
                    {
                        "task_id": "GMC-G01-T02",
                        "title": "Classify authorities.",
                        "status": "PLANNED",
                        "planning_only": True,
                        "implementation_authorized": False,
                        "depends_on": ["GMC-G01-T01"],
                        "method": "Classify with provenance.",
                        "evidence_required": ["classification rationale"],
                        "done_when": "Classification complete.",
                        "hold_if": "Missing provenance.",
                    },
                ],
            }],
        })
        self.write("pool", {
            "schema": "gacr-contextual-task-pool/v1",
            "revision": 0,
            "items": [],
            "semantic_digest": None,
        })

    def session(self, session_id: str, role: str, status: str = "ACTIVE") -> dict:
        return {
            "session_id": session_id,
            "repository": "chainsolutions-wealthtech/Governed-Repository-Template",
            "provider": "chatgpt",
            "agent_role": role,
            "status": status,
            "client_instance_id": "client-" + session_id,
            "capabilities": [],
            "authority_grants": [],
            "wake_channels": ["POLL_REPOSITORY"],
            "relay": {
                "process": "GACR",
                "state": "TAKEOVER_READY" if status == "STALLED" else "ACTIVE",
                "task_id": None,
                "branch": "main",
            },
        }

    def test_blueprint_projection_is_dependency_safe_and_contextual(self):
        projection = pool.build_task_pool_projection(generated_at="2026-10-07T03:00:00+00:00")
        by_id = {x["subject_id"]: x for x in projection["items"]}
        self.assertEqual(by_id["GMC-G01-T01"]["pool_state"], "READY")
        self.assertEqual(by_id["GMC-G01-T02"]["pool_state"], "BLOCKED")
        packet = by_id["GMC-G01-T01"]["context_packet"]
        self.assertEqual(packet["subject"]["entry_purpose"], "WORK_ON_CONTROL_PLANE")
        self.assertEqual(packet["subject"]["work_kind"], "EXECUTE_EXISTING_TASK")
        self.assertIn("docs/control-plane/CURRENT_STATE.md", packet["method"]["required_read_refs"])
        self.assertIn("docs/control-plane/CANONICAL_ARCHITECTURE.md", packet["method"]["required_read_refs"])
        self.assertTrue(packet["execution_contract"]["exact_head_required_before_claim_and_mutation"])
        self.assertEqual(packet["privacy"]["raw_prompts_included"], False)
        self.assertNotIn("transcript", json.dumps(packet).lower())

    def test_collision_free_waves_separate_overlapping_items(self):
        self.write("work", {"revision": 1, "items": [
            {"work_item_id": "A", "title": "A", "status": "READY", "priority": 3, "sequence": 1, "dependencies": [], "collision_domains": ["d1"]},
            {"work_item_id": "B", "title": "B", "status": "READY", "priority": 2, "sequence": 2, "dependencies": [], "collision_domains": ["d1"]},
            {"work_item_id": "C", "title": "C", "status": "READY", "priority": 1, "sequence": 3, "dependencies": [], "collision_domains": ["d2"]},
        ]})
        projection = pool.build_task_pool_projection()
        waves = projection["collision_free_waves"]
        first = set(waves[0]["subject_ids"])
        self.assertTrue({"A", "C"}.issubset(first) or {"B", "C"}.issubset(first))
        self.assertGreaterEqual(len(waves), 2)

    def test_source_dispatch_requires_compatible_role_and_embeds_context(self):
        sessions = {
            "schema_version": "1.0.0",
            "revision": 0,
            "sessions": [
                self.session("session-qualification", "qualification-client"),
                self.session("session-coder", "implementer"),
            ],
        }
        self.write("sessions", sessions)
        capacity.agent_pool_projection = lambda: {
            "items": [
                {
                    "session_id": "session-qualification",
                    "client_instance_id": "client-q",
                    "agent_role": "qualification-client",
                    "capabilities": [],
                    "authority_grants": [],
                    "eligible_for_new_work": True,
                },
                {
                    "session_id": "session-coder",
                    "client_instance_id": "client-c",
                    "agent_role": "implementer",
                    "capabilities": [],
                    "authority_grants": [],
                    "eligible_for_new_work": True,
                },
            ]
        }
        result = pool.dispatch_contextual_source_tasks()
        self.assertEqual(result["changed"], 1)
        offer = result["items"][0]
        self.assertEqual(offer["target_session_id"], "session-coder")
        self.assertEqual(offer["work_item_id"], "GMC-G01-T01")
        self.assertEqual(offer["context_packet"]["subject"]["subject_id"], "GMC-G01-T01")
        evaluations = {x["session_id"]: x for x in offer["compatibility_evaluations"]}
        self.assertEqual(evaluations["session-qualification"]["status"], "INELIGIBLE")
        self.assertEqual(evaluations["session-coder"]["status"], "ELIGIBLE")

    def test_acceptance_without_head_does_not_activate_claim(self):
        self.write("sessions", {"schema_version": "1.0.0", "revision": 0, "sessions": [self.session("session-coder", "implementer")]})
        self.write("dispatches", {"schema_version": "1.0.0", "revision": 1, "items": [{
            "dispatch_id": "D1",
            "dispatch_kind": "WORK_OFFER",
            "status": "ACCEPTED_PENDING_CLAIM",
            "offer_status": "ACCEPTED",
            "target_session_id": "session-coder",
            "work_item_id": "GMC-G01-T01",
            "task_id": "GMC-G01-T01",
            "collision_domains": ["control-plane:GMC-G01:serial"],
            "claim_created": False,
        }]})
        result = pool.activate_accepted_offers()
        self.assertEqual(result["changed"], 0)
        self.assertEqual(self.read("claims")["claims"], [])
        self.assertEqual(self.read("dispatches")["items"][0]["claim_activation_blocker"], "ACCEPTED_HEAD_UNAVAILABLE")

    def test_exact_head_acceptance_activates_claim_then_relinquish_requeues_with_history(self):
        self.write("sessions", {"schema_version": "1.0.0", "revision": 0, "sessions": [self.session("session-coder", "implementer")]})
        self.write("dispatches", {"schema_version": "1.0.0", "revision": 1, "items": [{
            "dispatch_id": "D2",
            "dispatch_kind": "WORK_OFFER",
            "status": "ACCEPTED_PENDING_CLAIM",
            "offer_status": "ACCEPTED",
            "target_session_id": "session-coder",
            "work_item_id": "GMC-G01-T01",
            "task_id": "GMC-G01-T01",
            "collision_domains": ["control-plane:GMC-G01:serial"],
            "claim_created": False,
            "accepted_observed_head_sha": "a" * 40,
            "acceptance_evidence_ref": "issue-comment:1",
        }]})
        activated = pool.activate_accepted_offers()
        self.assertEqual(activated["changed"], 1)
        claim = self.read("claims")["claims"][0]
        self.assertEqual(claim["status"], "ACTIVE")
        self.assertEqual(claim["claimed_head_sha"], "a" * 40)
        self.assertFalse(claim["grants_mutation_authority"])

        result = pool.relinquish_claim(
            claim_id_value=claim["claim_id"],
            session_id="session-coder",
            reason_code="CONTEXT_LIMIT",
            observed_head="a" * 40,
            checkpoint_ref="CHK-1",
            handoff_ref="HANDOFF-1",
            evidence_ref="EVIDENCE-1",
        )
        self.assertEqual(result["status"], "WORK_RELINQUISHED_FOR_REQUEUE")
        released = self.read("claims")["claims"][0]
        self.assertEqual(released["status"], "RELEASED_FOR_REQUEUE")
        projection = pool.build_task_pool_projection()
        item = next(x for x in projection["items"] if x["subject_id"] == "GMC-G01-T01")
        self.assertEqual(item["pool_state"], "READY")
        history = item["context_packet"]["history"]["claim_history"]
        self.assertEqual(history[-1]["release_reason"], "CONTEXT_LIMIT")
        self.assertEqual(history[-1]["checkpoint_ref"], "CHK-1")
        self.assertEqual(history[-1]["handoff_ref"], "HANDOFF-1")

    def test_recovery_ready_contains_takeover_and_forensics(self):
        stalled = self.session("session-old", "implementer", status="STALLED")
        self.write("sessions", {"schema_version": "1.0.0", "revision": 0, "sessions": [stalled]})
        self.write("claims", {"schema_version": "1.0.0", "revision": 1, "claims": [{
            "claim_id": "C1",
            "session_id": "session-old",
            "work_item_id": "GMC-G01-T01",
            "task_id": "GMC-G01-T01",
            "collision_domains": ["control-plane:GMC-G01:serial"],
            "status": "ACTIVE",
            "claimed_head_sha": "a" * 40,
            "created_at": "2026-10-07T02:00:00+00:00",
        }]})
        self.write("takeovers", {"schema_version": "1.0.0", "revision": 1, "items": [{
            "takeover_id": "T1",
            "stalled_session_id": "session-old",
            "status": "READY_FOR_RECONCILIATION",
            "created_at": "2026-10-07T02:30:00+00:00",
            "work_item_id": "GMC-G01-T01",
            "task_id": "GMC-G01-T01",
            "last_observed_head_sha": "a" * 40,
        }]})
        self.write("forensics", {"schema_version": "1.0.0", "revision": 1, "items": [{
            "forensic_id": "F1",
            "session_id": "session-old",
            "classification": "LEASE_EXPIRED_STALL",
            "generated_at": "2026-10-07T02:31:00+00:00",
            "last_checkpoint_ref": "CHK-OLD",
            "last_evidence_ref": "E-OLD",
            "resume_point": {
                "checkpoint_ref": "CHK-OLD",
                "last_observed_head_sha": "a" * 40,
                "requires_exact_head_reobservation": True,
                "may_replay_in_flight_action_without_reconciliation": False,
            },
        }]})
        projection = pool.build_task_pool_projection()
        item = next(x for x in projection["items"] if x["subject_id"] == "GMC-G01-T01")
        self.assertEqual(item["pool_state"], "RECOVERY_READY")
        packet = item["context_packet"]
        self.assertEqual(packet["continuity"]["resume_mode"], "TAKEOVER_RECONCILIATION")
        self.assertEqual(packet["history"]["takeover_history"][0]["takeover_id"], "T1")
        self.assertEqual(packet["history"]["forensics_history"][0]["forensic_id"], "F1")
        self.assertTrue(packet["continuity"]["blind_replay_forbidden"])

    def test_relinquish_requires_full_handoff_trace(self):
        with self.assertRaises(ValueError):
            pool.relinquish_claim(
                claim_id_value="missing",
                session_id="session-x",
                reason_code="CONTEXT_LIMIT",
                observed_head="a" * 40,
                checkpoint_ref="",
                handoff_ref="",
                evidence_ref="",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
