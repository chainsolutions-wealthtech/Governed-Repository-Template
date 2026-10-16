#!/usr/bin/env python3
"""Read-only GACR dispatcher audit in LAB; characterize risks, not claim fixes."""
from __future__ import annotations
import copy
import unittest

import gacr_capacity_dispatch as d
from test_gacr_capacity_dispatch import session, live_signal, release_beacon, availability_beacon


class GacrDispatcherLabCharacterization(unittest.TestCase):
    def test_01_missing_f1_blocks_only_that_session(self):
        if not d.TEMPLATE_SOURCE:
            self.skipTest("source-only dispatch gate")
        params = dict(
            sessions_doc={"sessions": [session("s-no-f1"), session("s-f1")]},
            claims_doc={"claims": []},
            beacons_doc={"items": [
                availability_beacon("s-no-f1", "AVAILABLE"),
                release_beacon("s-f1"),
                availability_beacon("s-f1", "AVAILABLE"),
            ]},
            correlations_doc={"items": []},
            signal_projection=live_signal(),
            continuities_doc={"items": []},
        )
        blocked = d.session_capacity_projection("s-no-f1", **params)
        allowed = d.session_capacity_projection("s-f1", **params)
        self.assertIn("F1_RELEASE_NOT_VERIFIED", blocked["dispatch_blockers"])
        self.assertFalse(blocked["eligible_for_new_work"])
        self.assertNotIn("F1_RELEASE_NOT_VERIFIED", allowed["dispatch_blockers"])
        self.assertTrue(allowed["eligible_for_new_work"])

    def test_02_f1_beacon_reference_only_is_trusted_locally(self):
        # KNOWN GAP: F1 authenticity is not verified in this projection.
        if not d.TEMPLATE_SOURCE:
            self.skipTest("source-only dispatch gate")
        beacon = release_beacon("s1")
        beacon["evidence_ref"] = "unverified-placeholder"
        p = d.session_capacity_projection(
            "s1", sessions_doc={"sessions": [session("s1")]},
            claims_doc={"claims": []},
            beacons_doc={"items": [beacon, availability_beacon("s1", "AVAILABLE")]},
            correlations_doc={"items": []}, signal_projection=live_signal(),
            continuities_doc={"items": []},
        )
        self.assertTrue(p["f1_release_verified"])
        self.assertEqual(p["f1_release_evidence"]["evidence_ref"], "unverified-placeholder")

    def test_03_accept_reuses_stale_offer_requirements(self):
        # KNOWN GAP: no role/capability revalidation at accept. No write grant.
        store = {"revision": 7, "items": [{
            "dispatch_id": "lab-offer-1", "dispatch_kind": "WORK_OFFER",
            "status": "READY", "target_session_id": "review-session",
            "work_item_id": "code-task", "allowed_agent_roles": ["CODE_AGENT"],
            "required_capabilities": ["CODE"], "required_authorities": ["CODE_SCOPE"],
        }]}
        old = (d.read_json, d.write_json, d.session_capacity_projection,
               d.agent_pool_projection, d.TEMPLATE_SOURCE)
        writes = []
        try:
            d.read_json = lambda path, default=None: (
                store if path == d.DISPATCHES_PATH else
                {"claims": []} if path == d.CLAIMS_PATH else default or {}
            )
            d.write_json = lambda path, document: writes.append(copy.deepcopy(document))
            d.session_capacity_projection = lambda sid: {
                "availability_state": "AVAILABLE", "eligible_for_new_work": True,
            }
            d.agent_pool_projection = lambda: {"items": [{
                "session_id": "review-session", "logical_agent_id": "reviewer",
                "agent_role": "REVIEWER", "capabilities": ["REVIEW"],
                "authority_grants": [], "eligible_for_new_work": True,
                "in_flight_action": None,
            }]}
            d.TEMPLATE_SOURCE = False
            receipt = d.accept_work_offer("lab-offer-1", "review-session")
            self.assertEqual(receipt["status"], "WORK_OFFER_ACCEPTED_PENDING_CLAIM")
            self.assertFalse(receipt["dispatch"]["grants_write_authority"])
            self.assertFalse(receipt["dispatch"]["claim_created"])
            self.assertEqual(len(writes), 1)
        finally:
            (d.read_json, d.write_json, d.session_capacity_projection,
             d.agent_pool_projection, d.TEMPLATE_SOURCE) = old

    def test_04_offer_cancel_only_impacts_unavailable_target(self):
        offers = {"items": [
            {"dispatch_id": "not-ready", "dispatch_kind": "WORK_OFFER",
             "status": "READY", "target_session_id": "s1"},
            {"dispatch_id": "keep-ready", "dispatch_kind": "WORK_OFFER",
             "status": "READY", "target_session_id": "s2"},
        ]}
        canceled = d._cancel_unavailable_target_offers(
            offers, {"items": [
                {"session_id": "s1", "eligible_for_new_work": False},
                {"session_id": "s2", "eligible_for_new_work": True},
            ]}, "2026-10-17T00:00:00+00:00")
        self.assertEqual([x["dispatch_id"] for x in canceled], ["not-ready"])
        self.assertEqual(offers["items"][1]["status"], "READY")

    def test_05_source_work_queue_is_still_gmc_only(self):
        if not d.TEMPLATE_SOURCE:
            self.skipTest("source-only queue")
        graph = d.canonical_work_document()
        self.assertEqual(graph["source"], d.SOURCE_WORK_KIND)
        self.assertEqual(graph["global_task_id"], "GMC-01")
        self.assertEqual(graph["work_package_id"], "GMC-G01")
        self.assertTrue(graph["planning_only"])
        self.assertFalse(graph["implementation_authorized"])
        pending = [x for x in graph["items"] if x.get("queue_state") == "REGISTERED_PENDING_F1"]
        self.assertTrue(pending)
        self.assertTrue(all(x["status"] == "BLOCKED" for x in pending))

    def test_06_plan_does_not_grant_code_or_claim(self):
        p = d.parallel_work_dispatch_plan(
            work_doc={"source": "LAB-TEST", "items": [{
                "work_item_id": "LAB-1", "status": "READY",
                "dependencies": [], "collision_domains": ["lab-1"],
                "required_capabilities": ["CODE"], "allowed_agent_roles": ["CODE_AGENT"],
            }]},
            claims_doc={"claims": []},
            dispatches_doc={"items": []},
            pool={"items": [{
                "session_id": "test-session", "logical_agent_id": "test-agent",
                "eligible_for_new_work": True, "agent_role": "CODE_AGENT",
                "capabilities": ["CODE"],
            }]},
        )
        self.assertEqual(len(p["assignments"]), 1)
        self.assertFalse(p["write_authority_granted"])
        self.assertFalse(p["claim_transfer_performed"])
        self.assertTrue(p["assignments"][0]["requires_claim_after_acceptance"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
