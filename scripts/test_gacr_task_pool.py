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
            "dispatches": self.base / "dispatches.json",
            "takeovers": self.base / "takeovers.json",
            "forensics": self.base / "forensics.json",
            "pool": self.base / "task-pool.json",
            "blueprint": self.base / "blueprint.json",
        }
        self.orig = {
            "template_source": pool.TEMPLATE_SOURCE,
            "pool_path": pool.POOL_PATH,
            "blueprint_path": pool.BLUEPRINT_PATH,
            "sessions": capacity.SESSIONS_PATH,
            "claims": capacity.CLAIMS_PATH,
            "dispatches": capacity.DISPATCHES_PATH,
            "takeovers": telemetry.TAKEOVERS_PATH,
            "forensics": telemetry.FORENSICS_PATH,
            "tele_sessions": telemetry.SESSIONS_PATH,
            "tele_claims": telemetry.CLAIMS_PATH,
            "tele_dispatches": telemetry.DISPATCHES_PATH,
            "canonical_work": capacity.canonical_work_document,
            "git_head": pool.git_head,
        }
        pool.TEMPLATE_SOURCE = True
        pool.POOL_PATH = self.paths["pool"]
        pool.BLUEPRINT_PATH = self.paths["blueprint"]
        capacity.SESSIONS_PATH = self.paths["sessions"]
        capacity.CLAIMS_PATH = self.paths["claims"]
        capacity.DISPATCHES_PATH = self.paths["dispatches"]
        telemetry.SESSIONS_PATH = self.paths["sessions"]
        telemetry.CLAIMS_PATH = self.paths["claims"]
        telemetry.DISPATCHES_PATH = self.paths["dispatches"]
        telemetry.TAKEOVERS_PATH = self.paths["takeovers"]
        telemetry.FORENSICS_PATH = self.paths["forensics"]
        pool.git_head = lambda: "a" * 40

        self.work_doc = {
            "schema_version": "1.0.0",
            "source": "CONTROL_PLANE_CANONICAL_TASK_GRAPH",
            "source_status": "READY",
            "global_task_id": "GMC-01",
            "work_package_id": "GMC-G01",
            "items": [
                {
                    "work_item_id": "GMC-G01-T01",
                    "task_id": "GMC-G01-T01",
                    "title": "Inventory authorities",
                    "status": "READY",
                    "priority": 999,
                    "sequence": 1,
                    "dependencies": [],
                    "collision_domains": ["governance-model:GMC-G01"],
                    "required_capabilities": [],
                    "required_authorities": [],
                    "allowed_agent_roles": ["CODE_AGENT"],
                    "global_task_id": "GMC-01",
                    "work_package_id": "GMC-G01",
                    "planning_only": True,
                    "implementation_authorized": False,
                    "hold_if": "Critical contradiction",
                    "done_when": "Inventory complete",
                    "evidence_required": ["source path/ref"],
                    "work_source": "CONTROL_PLANE_CANONICAL_TASK_GRAPH",
                },
                {
                    "work_item_id": "GMC-G01-T02",
                    "task_id": "GMC-G01-T02",
                    "title": "Classify authorities",
                    "status": "BLOCKED",
                    "priority": 998,
                    "sequence": 2,
                    "dependencies": ["GMC-G01-T01"],
                    "collision_domains": ["governance-model:GMC-G01"],
                    "allowed_agent_roles": ["CODE_AGENT"],
                    "global_task_id": "GMC-01",
                    "work_package_id": "GMC-G01",
                    "planning_only": True,
                    "implementation_authorized": False,
                    "work_source": "CONTROL_PLANE_CANONICAL_TASK_GRAPH",
                },
            ],
        }
        capacity.canonical_work_document = lambda: json.loads(json.dumps(self.work_doc))
        self.write("sessions", {"schema_version": "1.0.0", "revision": 0, "sessions": []})
        self.write("claims", {"schema_version": "1.0.0", "revision": 0, "claims": []})
        self.write("dispatches", {"schema_version": "1.0.0", "revision": 0, "items": []})
        self.write("takeovers", {"schema_version": "1.0.0", "revision": 0, "items": []})
        self.write("forensics", {"schema_version": "1.0.0", "revision": 0, "items": []})
        self.write("pool", {"schema": "gacr-contextual-task-pool/v1", "revision": 0, "items": [], "semantic_digest": None})
        self.write("blueprint", {
            "groups": [{
                "group_id": "GMC-G01",
                "objective": "Separate model from strategies",
                "where_to_look": ["docs/control-plane/CANONICAL_ARCHITECTURE.md"],
                "search_order": ["authorities/docs", "machine state"],
                "inputs": ["CP-ARCH-001"],
                "atomic_tasks": [{
                    "task_id": "GMC-G01-T01",
                    "method": "Observe → extract → preserve provenance.",
                    "evidence_required": ["source path/ref"],
                    "done_when": "Inventory complete",
                    "hold_if": "Critical contradiction",
                }],
            }]
        })

    def tearDown(self):
        pool.TEMPLATE_SOURCE = self.orig["template_source"]
        pool.POOL_PATH = self.orig["pool_path"]
        pool.BLUEPRINT_PATH = self.orig["blueprint_path"]
        capacity.SESSIONS_PATH = self.orig["sessions"]
        capacity.CLAIMS_PATH = self.orig["claims"]
        capacity.DISPATCHES_PATH = self.orig["dispatches"]
        telemetry.SESSIONS_PATH = self.orig["tele_sessions"]
        telemetry.CLAIMS_PATH = self.orig["tele_claims"]
        telemetry.DISPATCHES_PATH = self.orig["tele_dispatches"]
        telemetry.TAKEOVERS_PATH = self.orig["takeovers"]
        telemetry.FORENSICS_PATH = self.orig["forensics"]
        capacity.canonical_work_document = self.orig["canonical_work"]
        pool.git_head = self.orig["git_head"]
        self.tmp.cleanup()

    def write(self, key: str, value: dict) -> None:
        self.paths[key].write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def read(self, key: str) -> dict:
        return json.loads(self.paths[key].read_text(encoding="utf-8"))

    def session(self, session_id: str, *, stalled: bool = False) -> dict:
        return {
            "session_id": session_id,
            "repository": "chainsolutions-wealthtech/Governed-Repository-Template",
            "provider": "chatgpt",
            "client_instance_id": "client-" + session_id,
            "status": "STALLED" if stalled else "ACTIVE",
            "relay": {
                "state": "TAKEOVER_READY" if stalled else "ACTIVE",
                "branch": "main",
                "task_id": None,
            },
        }

    def test_projection_preserves_r8_source_and_adds_context(self):
        projection = pool.build_task_pool_projection(generated_at="2026-10-07T03:00:00+00:00")
        by_id = {x["work_item_id"]: x for x in projection["items"]}
        self.assertEqual(projection["authority"]["dispatcher_authority"], "CP-AGENT-RELAY-001-R8")
        self.assertEqual(by_id["GMC-G01-T01"]["pool_state"], "READY")
        self.assertEqual(by_id["GMC-G01-T02"]["pool_state"], "BLOCKED")
        packet = by_id["GMC-G01-T01"]["context_packet"]
        self.assertEqual(packet["execution_contract"]["implementation_authorized"], False)
        self.assertIn("docs/control-plane/CURRENT_STATE.md", packet["method"]["required_read_refs"])
        self.assertIn("docs/control-plane/CANONICAL_ARCHITECTURE.md", packet["method"]["required_read_refs"])
        self.assertEqual(packet["method"]["instructions"], "Observe → extract → preserve provenance.")
        self.assertTrue(packet["continuity"]["successor_exact_head_reconciliation_required"])
        self.assertFalse(packet["privacy"]["raw_conversation_content_persisted"])
        self.assertFalse(packet["privacy"]["assistant_internal_workings_persisted"])

    def test_collision_free_waves_never_place_overlapping_domains_together(self):
        self.work_doc["items"] = [
            {**self.work_doc["items"][0], "work_item_id": "A", "task_id": "A", "collision_domains": ["d1"]},
            {**self.work_doc["items"][0], "work_item_id": "B", "task_id": "B", "collision_domains": ["d1"]},
            {**self.work_doc["items"][0], "work_item_id": "C", "task_id": "C", "collision_domains": ["d2"]},
        ]
        projection = pool.build_task_pool_projection()
        self.assertGreaterEqual(len(projection["collision_free_waves"]), 2)
        for wave in projection["collision_free_waves"]:
            ids = wave["work_item_ids"]
            self.assertFalse("A" in ids and "B" in ids)

    def test_existing_r8_offer_is_enriched_not_redispatched(self):
        self.write("sessions", {"sessions": [self.session("session-code")]})
        self.write("dispatches", {"revision": 1, "items": [{
            "dispatch_id": "GACR-W-demo",
            "dispatch_kind": "WORK_OFFER",
            "status": "READY",
            "offer_status": "PENDING_ACCEPTANCE",
            "target_session_id": "session-code",
            "work_item_id": "GMC-G01-T01",
            "task_id": "GMC-G01-T01",
            "work_source": "CONTROL_PLANE_CANONICAL_TASK_GRAPH",
            "collision_domains": ["governance-model:GMC-G01"],
            "claim_created": False,
        }]})
        result = pool.enrich_work_offers()
        self.assertEqual(result["changed"], 1)
        offer = self.read("dispatches")["items"][0]
        self.assertEqual(offer["contextual_pool_revision_authority"], "CP-AGENT-RELAY-001-R9")
        self.assertEqual(offer["context_packet"]["subject"]["work_item_id"], "GMC-G01-T01")
        self.assertNotIn("target_session_id", offer["context_packet"]["subject"])

    def test_acceptance_without_observed_head_cannot_claim(self):
        self.write("sessions", {"sessions": [self.session("session-code")]})
        self.write("dispatches", {"revision": 1, "items": [{
            "dispatch_id": "GACR-W-nohead",
            "dispatch_kind": "WORK_OFFER",
            "status": "ACCEPTED_PENDING_CLAIM",
            "offer_status": "ACCEPTED",
            "target_session_id": "session-code",
            "work_item_id": "GMC-G01-T01",
            "task_id": "GMC-G01-T01",
            "work_source": "CONTROL_PLANE_CANONICAL_TASK_GRAPH",
            "collision_domains": ["governance-model:GMC-G01"],
            "claim_created": False,
        }]})
        result = pool.activate_accepted_offers()
        self.assertEqual(result["changed"], 0)
        self.assertEqual(self.read("claims")["claims"], [])
        self.assertEqual(self.read("dispatches")["items"][0]["claim_activation_blocker"], "ACCEPTED_HEAD_UNAVAILABLE")

    def test_exact_head_acceptance_activates_one_claim_without_authority_widening(self):
        self.write("sessions", {"revision": 0, "sessions": [self.session("session-code")]})
        self.write("dispatches", {"revision": 1, "items": [{
            "dispatch_id": "GACR-W-head",
            "dispatch_kind": "WORK_OFFER",
            "status": "ACCEPTED_PENDING_CLAIM",
            "offer_status": "ACCEPTED",
            "target_session_id": "session-code",
            "work_item_id": "GMC-G01-T01",
            "task_id": "GMC-G01-T01",
            "work_source": "CONTROL_PLANE_CANONICAL_TASK_GRAPH",
            "global_task_id": "GMC-01",
            "work_package_id": "GMC-G01",
            "collision_domains": ["governance-model:GMC-G01"],
            "claim_created": False,
            "accepted_observed_head_sha": "a"*40,
            "acceptance_evidence_ref": "github-issue-comment:1",
        }]})
        result = pool.activate_accepted_offers()
        self.assertEqual(result["changed"], 1)
        claim = self.read("claims")["claims"][0]
        self.assertEqual(claim["status"], "ACTIVE")
        self.assertEqual(claim["claimed_head_sha"], "a"*40)
        self.assertFalse(claim["grants_mutation_authority"])
        self.assertFalse(claim["grants_business_authority"])
        dispatch = self.read("dispatches")["items"][0]
        self.assertTrue(dispatch["claim_created"])
        self.assertEqual(dispatch["status"], "ACTIVATED")

    def test_head_move_blocks_claim(self):
        self.write("sessions", {"sessions": [self.session("session-code")]})
        self.write("dispatches", {"revision": 1, "items": [{
            "dispatch_id": "GACR-W-stale",
            "dispatch_kind": "WORK_OFFER",
            "status": "ACCEPTED_PENDING_CLAIM",
            "offer_status": "ACCEPTED",
            "target_session_id": "session-code",
            "work_item_id": "GMC-G01-T01",
            "collision_domains": ["governance-model:GMC-G01"],
            "claim_created": False,
            "accepted_observed_head_sha": "b"*40,
        }]})
        result = pool.activate_accepted_offers()
        self.assertEqual(result["changed"], 0)
        self.assertEqual(self.read("dispatches")["items"][0]["claim_activation_blocker"], "HEAD_MOVED_RECONCILE_REQUIRED")

    def test_responsive_relinquish_returns_same_canonical_work_with_handoff_history(self):
        self.write("sessions", {"revision": 0, "sessions": [self.session("session-code")]})
        self.write("claims", {"revision": 1, "claims": [{
            "claim_id": "GACR-C-demo",
            "session_id": "session-code",
            "work_item_id": "GMC-G01-T01",
            "task_id": "GMC-G01-T01",
            "collision_domains": ["governance-model:GMC-G01"],
            "status": "ACTIVE",
            "claimed_head_sha": "a"*40,
            "created_at": "2026-10-07T02:00:00+00:00",
            "dispatch_id": "GACR-W-demo",
        }]})
        self.write("dispatches", {"revision": 1, "items": [{
            "dispatch_id": "GACR-W-demo",
            "dispatch_kind": "WORK_OFFER",
            "status": "ACTIVATED",
            "target_session_id": "session-code",
            "work_item_id": "GMC-G01-T01",
            "claim_id": "GACR-C-demo",
            "claim_created": True,
        }]})
        result = pool.relinquish_claim(
            claim_id_value="GACR-C-demo",
            session_id="session-code",
            reason_code="CONTEXT_LIMIT",
            observed_head="c"*40,
            checkpoint_ref="CHK-1",
            handoff_ref="HANDOFF-1",
            evidence_ref="EVIDENCE-1",
        )
        self.assertEqual(result["status"], "WORK_RELINQUISHED_FOR_REQUEUE")
        released = self.read("claims")["claims"][0]
        self.assertEqual(released["status"], "RELEASED_FOR_REQUEUE")
        self.assertEqual(released["checkpoint_ref"], "CHK-1")
        self.assertTrue(released["successor_exact_head_reconciliation_required"])
        projection = pool.build_task_pool_projection()
        item = next(x for x in projection["items"] if x["work_item_id"] == "GMC-G01-T01")
        self.assertEqual(item["pool_state"], "READY")
        self.assertEqual(item["context_packet"]["history"]["claim_history"][-1]["release_reason"], "CONTEXT_LIMIT")
        self.assertEqual(item["context_packet"]["history"]["claim_history"][-1]["handoff_ref"], "HANDOFF-1")

    def test_stalled_claim_becomes_recovery_ready_with_forensics(self):
        self.write("sessions", {"sessions": [self.session("session-old", stalled=True)]})
        self.write("claims", {"revision": 1, "claims": [{
            "claim_id": "GACR-C-old",
            "session_id": "session-old",
            "work_item_id": "GMC-G01-T01",
            "task_id": "GMC-G01-T01",
            "collision_domains": ["governance-model:GMC-G01"],
            "status": "ACTIVE",
            "claimed_head_sha": "a"*40,
            "created_at": "2026-10-07T02:00:00+00:00",
        }]})
        self.write("takeovers", {"items": [{
            "takeover_id": "T-1",
            "stalled_session_id": "session-old",
            "work_item_id": "GMC-G01-T01",
            "status": "READY_FOR_RECONCILIATION",
            "created_at": "2026-10-07T02:30:00+00:00",
            "last_observed_head_sha": "a"*40,
        }]})
        self.write("forensics", {"items": [{
            "forensic_id": "F-1",
            "session_id": "session-old",
            "classification": "LEASE_EXPIRED_STALL",
            "generated_at": "2026-10-07T02:31:00+00:00",
            "last_checkpoint_ref": "CHK-old",
            "last_evidence_ref": "E-old",
            "resume_point": {
                "checkpoint_ref": "CHK-old",
                "last_observed_head_sha": "a"*40,
                "requires_exact_head_reobservation": True,
                "may_replay_in_flight_action_without_reconciliation": False,
            },
        }]})
        projection = pool.build_task_pool_projection()
        item = next(x for x in projection["items"] if x["work_item_id"] == "GMC-G01-T01")
        self.assertEqual(item["pool_state"], "RECOVERY_READY")
        packet = item["context_packet"]
        self.assertEqual(packet["continuity"]["resume_mode"], "TAKEOVER_RECONCILIATION")
        self.assertEqual(packet["history"]["takeover_history"][0]["takeover_id"], "T-1")
        self.assertEqual(packet["history"]["forensics_history"][0]["forensic_id"], "F-1")
        self.assertTrue(packet["continuity"]["blind_replay_forbidden"])

    def test_relinquish_requires_complete_trace(self):
        with self.assertRaises(ValueError):
            pool.relinquish_claim(
                claim_id_value="x",
                session_id="s",
                reason_code="CONTEXT_LIMIT",
                observed_head="a"*40,
                checkpoint_ref="",
                handoff_ref="",
                evidence_ref="",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
