#!/usr/bin/env python3
"""Regression coverage for GR302 in-place HEAD reconciliation."""
from __future__ import annotations

import copy
import json
import unittest
from unittest.mock import patch

import control_plane_issue_bridge as bridge
from governed_gr302_reconciliation import (
    reconcile_stale_lab_plan, BRANCH, REPO, OLD_HEAD
)
from governed_request import apply_answer, apply_evidence, encode_state

NEW_HEAD = "9" * 40
OWNER = "Wealthtechinnovations"


def held():
    return {
        "schema_version": "1.0.0", "request_id": "GR-000302", "revision": 12,
        "status": "EXECUTING_PREPARATION", "phase": "PREP-003",
        "handoff": None, "hold_reason": None,
        "answers": {
            "target_repository": REPO, "entry_action": "LAB_EVOLUTION",
            "lab_branch_name": BRANCH, "lab_authority": True, "plan_approved": True,
            "target_observation": {"exists": True, "default_branch": "main",
                                   "head_sha": OLD_HEAD, "governance_detected": True},
        },
        "next_request": {"kind": "ACTION_REQUEST", "action_id": "PREP-003"},
        "evidence": [
            {"action_id": "PREP-001", "result": "PASS",
             "evidence": {"canonical_head_sha": OLD_HEAD}},
            {"action_id": "PREP-002", "result": "PASS",
             "evidence": {"baseline_ready": True}},
        ],
        "execution_plan": [
            {"id": "PREP-001", "name": "RECONFIRM_CANONICAL_BASELINE", "status": "DONE",
             "required_evidence": {"canonical_head_sha": OLD_HEAD}},
            {"id": "PREP-002", "name": "CAPTURE_LAB_BASELINE", "status": "DONE",
             "required_evidence": {"baseline_ready": True}},
            {"id": "PREP-003", "name": "CREATE_LAB_BRANCH", "status": "PENDING",
             "required_evidence": {"branch": BRANCH, "base_head_sha": OLD_HEAD, "created": True}},
            {"id": "PREP-004", "name": "VERIFY_LAB_ISOLATION", "status": "PENDING",
             "required_evidence": {"lab_branch": BRANCH}},
        ],
    }


def reconcile(state=None, **kw):
    args = {
        "expected_revision": 12, "expected_head": NEW_HEAD,
        "observed_head": NEW_HEAD, "owner_actor": OWNER,
        "event_author": OWNER, "author_association": "MEMBER",
        "branch_absent": True,
        "observation_evidence": "github-issue-comment:123456789",
        "reason": "Owner rebaseline after HEAD drift, without any mutation grant.",
    }
    args.update(kw)
    return reconcile_stale_lab_plan(state if state is not None else held(), **args)


class GR302TransitionTests(unittest.TestCase):
    def test_01_history_and_prior_proofs_immutable(self):
        old = held()
        before = copy.deepcopy(old)
        new = reconcile(old)
        self.assertEqual(old, before)
        self.assertEqual(new["revision"], 13)
        self.assertEqual(new["status"], "WAITING_FOR_PLAN_APPROVAL")
        self.assertEqual(new["phase"], "PLAN_APPROVAL")
        self.assertEqual([x["id"] for x in new["execution_plan"]],
                         ["PREP-001", "PREP-002", "PREP-002R", "PREP-003", "PREP-004"])
        self.assertEqual([x["status"] for x in new["execution_plan"]],
                         ["DONE", "DONE", "PENDING", "PENDING", "PENDING"])
        self.assertEqual(new["evidence"], before["evidence"])
        self.assertEqual(new["preparation_reconciliation_history"][0]["old_plan"],
                         before["execution_plan"])
        self.assertNotIn("plan_approved", new["answers"])
        self.assertFalse(new["preparation_reconciliation_history"][0]["grants_write"])
        self.assertTrue(new["gr302_reconciliation_pending"]["no_mutation_authority"])

    def test_02_stale_revision_fails(self):
        with self.assertRaisesRegex(ValueError, "REVISION"): reconcile(expected_revision=11)

    def test_03_head_drift_fails(self):
        with self.assertRaisesRegex(ValueError, "HEAD"): reconcile(observed_head="8" * 40)

    def test_04_created_branch_fails(self):
        with self.assertRaisesRegex(ValueError, "BRANCH_ABSENCE"): reconcile(branch_absent=False)

    def test_05_spoofed_actor_fails(self):
        with self.assertRaisesRegex(ValueError, "AUTHENTICATION"): reconcile(owner_actor="intruder")

    def test_06_spoofed_comment_fails(self):
        with self.assertRaisesRegex(ValueError, "AUTHENTICATION"): reconcile(event_author="intruder")

    def test_07_bad_author_association_fails(self):
        with self.assertRaisesRegex(ValueError, "AUTHENTICATION"): reconcile(author_association="NONE")

    def test_08_other_phase_fails(self):
        s = held(); s["phase"] = "PREP-004"
        with self.assertRaisesRegex(ValueError, "PREP003"): reconcile(s)

    def test_09_already_done_fails(self):
        s = held(); s["execution_plan"][2]["status"] = "DONE"
        with self.assertRaisesRegex(ValueError, "PLAN_MISMATCH"): reconcile(s)

    def test_10_missing_prior_proofs_fails(self):
        s = held(); s["evidence"] = []
        with self.assertRaisesRegex(ValueError, "EVIDENCE"): reconcile(s)

    def test_11_unapproved_initial_plan_fails(self):
        s = held(); s["answers"].pop("plan_approved")
        with self.assertRaisesRegex(ValueError, "PREP003"): reconcile(s)

    def test_12_wrong_gr_fails(self):
        s = held(); s["request_id"] = "GR-000284"
        with self.assertRaisesRegex(ValueError, "PREP003"): reconcile(s)

    def test_13_unverified_evidence_fails(self):
        with self.assertRaisesRegex(ValueError, "OBSERVATION"): reconcile(observation_evidence="fake")

    def test_14_replay_fails(self):
        with self.assertRaisesRegex(ValueError, "REVISION"): reconcile(reconcile())

    def test_15_original_head_fails(self):
        with self.assertRaisesRegex(ValueError, "NO_HEAD_CHANGE"): reconcile(
            expected_head=OLD_HEAD, observed_head=OLD_HEAD)

    def test_16_no_mutation_on_rejection(self):
        src = held(); old = copy.deepcopy(src)
        with self.assertRaises(ValueError): reconcile(src, owner_actor="forged")
        self.assertEqual(src, old)

    def test_17_owner_approval_resumes_from_read_step(self):
        new = apply_answer(reconcile(), "plan_approved", True)
        self.assertEqual(new["status"], "EXECUTING_PREPARATION")
        self.assertEqual(new["phase"], "PREP-002R")
        self.assertFalse(any(x["id"] == "PREP-003" and x["status"] == "DONE"
                             for x in new["execution_plan"]))

    def test_18_real_readonly_proof_advances_not_lab(self):
        new = apply_answer(reconcile(), "plan_approved", True)
        proof = new["execution_plan"][2]["required_evidence"]
        result = apply_evidence(new, "PREP-002R", "PASS", proof)
        self.assertEqual(result["phase"], "PREP-003")
        self.assertEqual(result["execution_plan"][3]["status"], "PENDING")
        self.assertEqual(result["execution_plan"][3]["required_evidence"]["base_head_sha"], NEW_HEAD)

    def test_19_other_branch_fails(self):
        s = held(); s["answers"]["lab_branch_name"] = "lab/foreign"
        with self.assertRaisesRegex(ValueError, "PREP003"): reconcile(s)

    def test_20_unproven_target_plan_fails(self):
        s = held(); s["execution_plan"][2]["required_evidence"]["base_head_sha"] = NEW_HEAD
        with self.assertRaisesRegex(ValueError, "PLAN_MISMATCH"): reconcile(s)

    def test_21_reapproval_is_not_grant(self):
        new = apply_answer(reconcile(), "plan_approved", True)
        j = new["preparation_reconciliation_history"][-1]
        self.assertFalse(j["grants_claim"] or j["grants_lease"] or j["creates_lab"]
                         or j["grants_write"] or j["grants_merge_authority"])


class GR302BridgeTests(unittest.TestCase):
    def setUp(self):
        self.old = held()
        self.body = "GR 302\n\n<!-- GOVERNED_REQUEST_STATE:" + encode_state(self.old) + " -->\n"
        self.calls = []
        self.event = {
            "issue": {"number": 302, "title": "[Governed Request] CHAINFLOW GR302",
                      "body": self.body},
            "sender": {"login": OWNER},
            "comment": {"id": 123456789, "user": {"login": OWNER},
                        "author_association": "MEMBER",
                        "body": "/governed-reconcile-gr302 " + json.dumps({
                            "expected_revision": 12, "expected_head": NEW_HEAD,
                            "reason": "Owner-approved safe GR302 HEAD reconciliation."})},
        }

    def fake_api(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        if method == "GET" and path.endswith("/issues/302"):
            return {"number": 302, "body": self.body}
        if method == "GET" and path.endswith("/branches/main"):
            return {"commit": {"sha": NEW_HEAD}}
        if method == "GET" and "/branches/lab%2Fchainflow-live-poc" in path:
            raise RuntimeError(f"GitHub API GET {path} failed: 404 not found")
        if method == "PATCH" and path.endswith("/issues/302"):
            self.body = payload["body"]
            return {"number": 302}
        if method == "POST" and path.endswith("/issues/302/comments"):
            return {"id": 44}
        raise AssertionError((method, path))

    def call(self):
        with patch.object(bridge, "api", side_effect=self.fake_api):
            bridge.handle_comment(self.event)

    def test_22_command_updates_only_same_issue_marker(self):
        self.call()
        new = bridge.extract_state(self.body)
        self.assertEqual(new["revision"], 13)
        self.assertEqual(new["phase"], "PLAN_APPROVAL")
        self.assertEqual(new["evidence"], self.old["evidence"])
        self.assertEqual(len([x for x in self.calls if x[0] == "PATCH"]), 1)

    def test_23_spoof_fails_before_patch(self):
        self.event["comment"]["user"]["login"] = "intruder"
        self.call()
        self.assertFalse(any(x[0] == "PATCH" for x in self.calls))

    def test_24_head_moved_fails_before_patch(self):
        self.event["comment"]["body"] = self.event["comment"]["body"].replace(
            NEW_HEAD, "8"*40)
        self.call()
        self.assertFalse(any(x[0] == "PATCH" for x in self.calls))

    def test_25_branch_permission_failure_not_absence(self):
        old_api = self.fake_api
        def deny(method, path, payload=None):
            if "/branches/lab%2Fchainflow-live-poc" in path:
                raise RuntimeError(f"GitHub API GET {path} failed: 403 forbidden")
            return old_api(method, path, payload)
        with patch.object(bridge, "api", side_effect=deny):
            bridge.handle_comment(self.event)
        self.assertFalse(any(x[0] == "PATCH" for x in self.calls))

    def test_26_duplicate_command_fails_after_first(self):
        self.call()
        self.calls.clear()
        self.call()
        self.assertEqual(len([x for x in self.calls if x[0] == "PATCH"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
