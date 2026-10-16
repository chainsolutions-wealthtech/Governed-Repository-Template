#!/usr/bin/env python3
"""Audited re-use of a merged historic LAB; reject false created=true evidence."""
from __future__ import annotations

import copy
import json
import unittest

import control_plane_issue_bridge as bridge
from governed_hold_review import reexamine_authority_hold
from governed_plan_reconciliation import reconcile_existing_merged_lab
from governed_request import new_request, apply_answer, apply_evidence, encode_state, decode_state

REPO = "chainsolutions-wealthtech/Governed-Repository-Template"
LAB = "lab/codeagent-gscc-f1-q12-renewal-284"
H_OLD = "a" * 40
H_NEW = "b" * 40
H_LAB = "c" * 40
H_MERGED = "d" * 40

PR = {"number": 316, "merged_at": "2026-10-16T01:00:00Z",
      "merge_commit_sha": H_MERGED,
      "head": {"ref": LAB}, "base": {"ref": "main"}}


def ready_plan() -> dict:
    state = new_request("GR-000284", "Wealthtechinnovations", "github", "Q12 F1 recovery")
    values = {
        "entry_action": "LAB_EVOLUTION",
        "connection_intent": "WORK_REQUEST",
        "objective": "Q12 recovery on same arrival and existing lab without regression",
        "target_repository": REPO,
        "target_observation": {"exists": True, "default_branch": "main",
                               "head_sha": H_OLD, "governance_detected": True},
        "lab_branch_name": LAB, "pr_required": True, "lab_authority": False,
    }
    while (state.get("next_request") or {}).get("field") in values:
        field = state["next_request"]["field"]
        state = apply_answer(state, field, values[field])
    assert state["status"] == "HOLD_FOR_REVIEW", state
    state = reexamine_authority_hold(
        state, expected_revision=state["revision"], expected_head=H_NEW,
        observed_head=H_NEW, owner_actor="Wealthtechinnovations",
        author_association="MEMBER", evidence_refs=["github-pr:316"],
        reason="Owner review with verified pre-existing merged work.",
    )
    state = apply_answer(state, "target_observation", {
        "exists": True, "default_branch": "main",
        "head_sha": H_NEW, "governance_detected": True,
    })
    state = apply_answer(state, "lab_authority", True)
    assert state["status"] == "PLAN_READY" and state["revision"] >= 10, state
    return state


def reconcile(state, **options):
    params = dict(
        expected_revision=state["revision"], expected_main_head=H_NEW,
        live_main_head=H_NEW, owner_actor="Wealthtechinnovations",
        author_association="MEMBER", branch_head=H_LAB,
        merged_pr=copy.deepcopy(PR),
        reason="Historic LAB was already created and merged; re-use read-only.",
    )
    params.update(options)
    return reconcile_existing_merged_lab(state, **params)


class StateTests(unittest.TestCase):
    def setUp(self):
        self.original = ready_plan()

    def test_01_new_plan_is_all_read_only(self):
        updated = reconcile(self.original)
        self.assertEqual(updated["request_id"], "GR-000284")
        self.assertEqual(updated["revision"], self.original["revision"] + 1)
        self.assertEqual(updated["status"], "WAITING_FOR_PLAN_APPROVAL")
        self.assertEqual(updated["next_request"]["field"], "plan_approved")
        self.assertEqual(len(updated["execution_plan"]), 4)
        self.assertTrue(all(x["status"] == "PENDING" for x in updated["execution_plan"]))
        self.assertTrue(all(x["mutation_class"] != "TARGET_BRANCH_CREATE"
                            for x in updated["execution_plan"]))
        self.assertEqual(updated["execution_plan"][2]["name"], "REUSE_VERIFY_EXISTING_LAB_BRANCH")
        self.assertFalse(updated["execution_plan"][2]["required_evidence"]["created_in_this_plan"])
        self.assertTrue(updated["plan_reconciliation_pending"]["no_mutation_authority"])

    def test_02_original_plan_and_hold_history_survive(self):
        updated = reconcile(self.original)
        self.assertEqual(updated["hold_review_history"], self.original["hold_review_history"])
        self.assertEqual(updated["agent"], self.original["agent"])
        history = updated["plan_reconciliation_history"][-1]
        self.assertEqual(history["superseded_plan"][2]["name"], "CREATE_LAB_BRANCH")
        self.assertEqual(history["superseded_plan"][2]["status"], "PENDING")
        self.assertFalse(history["grants_write"])
        self.assertFalse(history["creates_lab"])

    def test_03_no_implicit_approval(self):
        updated = reconcile(self.original)
        self.assertNotIn("plan_approved", updated["answers"])
        updated = apply_answer(updated, "plan_approved", True)
        self.assertEqual(updated["status"], "EXECUTING_PREPARATION")
        self.assertEqual(updated["next_request"]["action_id"], "PREP-001")

    def test_04_stale_revision_refused(self):
        with self.assertRaisesRegex(ValueError, "REVISION_DRIFT"):
            reconcile(self.original, expected_revision=self.original["revision"] - 1)

    def test_05_new_head_drift_refused(self):
        with self.assertRaisesRegex(ValueError, "MAIN_HEAD_MOVED"):
            reconcile(self.original, live_main_head=H_OLD)

    def test_06_wrong_owner_refused(self):
        with self.assertRaisesRegex(ValueError, "OWNER_REQUIRED"):
            reconcile(self.original, owner_actor="other-coder")

    def test_07_untrusted_actor_association_refused(self):
        with self.assertRaisesRegex(ValueError, "OWNER_REQUIRED"):
            reconcile(self.original, author_association="NONE")

    def test_08_missing_merged_pr_refused(self):
        with self.assertRaisesRegex(ValueError, "PR316_PROVENANCE"):
            reconcile(self.original, merged_pr={**PR, "merged_at": None})

    def test_09_different_branch_refused(self):
        with self.assertRaisesRegex(ValueError, "PR316_PROVENANCE"):
            reconcile(self.original, merged_pr={**PR, "head": {"ref": "lab/other"}})

    def test_10_approved_plan_refused(self):
        state = copy.deepcopy(self.original)
        state = apply_answer(state, "plan_approved", True)
        with self.assertRaisesRegex(ValueError, "UNAPPROVED_ORIGINAL_GR"):
            reconcile(state)

    def test_11_wrong_plan_status_refused(self):
        state = copy.deepcopy(self.original)
        state["execution_plan"][2]["status"] = "DONE"
        with self.assertRaisesRegex(ValueError, "OLD_CREATE_PLAN"):
            reconcile(state)

    def test_12_forged_target_identity_refused(self):
        state = copy.deepcopy(self.original)
        state["request_id"] = "GR-999999"
        with self.assertRaisesRegex(ValueError, "UNAPPROVED_ORIGINAL_GR"):
            reconcile(state)

    def test_13_history_immutability_of_source(self):
        before = copy.deepcopy(self.original)
        reconcile(self.original)
        self.assertEqual(self.original, before)

    def test_14_reconciliation_repeat_allowed_only_before_execution(self):
        first = reconcile(self.original)
        again = reconcile(first)
        self.assertEqual(again["revision"], first["revision"] + 1)
        self.assertEqual(len(again["plan_reconciliation_history"]), 2)
        first_approved = apply_answer(first, "plan_approved", True)
        with self.assertRaisesRegex(ValueError, "UNAPPROVED_ORIGINAL_GR"):
            reconcile(first_approved)

    def test_15_no_new_lab_handoff_after_readonly_completion(self):
        state = reconcile(self.original)
        state = apply_answer(state, "plan_approved", True)
        while state["status"] == "EXECUTING_PREPARATION":
            current = state["next_request"]
            evidence = current["required_evidence"]
            state = apply_evidence(state, current["action_id"], "PASS", evidence)
        self.assertEqual(state["status"], "HANDOFF_READY")
        self.assertEqual(state["handoff"]["allowed_next_operation"],
                         "VERIFY_LIVE_SAME_ARRIVAL_Q12_F1_WITH_SEPARATE_GACR_AUTHORITY")


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.original = ready_plan()
        self.body = "Original issue\n\n<!-- GOVERNED_REQUEST_STATE:" + encode_state(self.original) + " -->\n"
        self.calls = []
        self.event = {
            "issue": {"number": 284, "title": "[Governed Request] F1 Q12",
                      "body": self.body},
            "sender": {"login": "Wealthtechinnovations"},
            "comment": {
                "user": {"login": "Wealthtechinnovations"},
                "author_association": "MEMBER",
                "body": "/governed-reconcile-plan " + json.dumps({
                    "expected_revision": self.original["revision"],
                    "expected_head": H_NEW,
                    "reason": "Historic LAB already merged, no second creation is allowed."
                })
            }
        }
    def api(self,method,path,payload=None):
        self.calls.append((method,path,payload))
        if method=="GET" and path.endswith("/issues/284"):
            return {"number": 284, "body": self.body}
        if method=="GET" and path.endswith("/branches/main"):
            return {"commit":{"sha":H_NEW}}
        if method=="GET" and path.endswith("/branches/lab%2Fcodeagent-gscc-f1-q12-renewal-284"):
            return {"commit":{"sha":H_LAB}}
        if method=="GET" and path.endswith("/pulls/316"):
            return copy.deepcopy(PR)
        if method=="PATCH":
            self.body=payload["body"]
            return {}
        if method=="POST":
            return {"id": len(self.calls)}
        raise AssertionError((method,path))
    def invoke(self):
        old=bridge.api
        bridge.api=self.api
        try: bridge.handle_comment(self.event)
        finally: bridge.api=old
    def test_16_real_bridge_changes_same_issue_marker(self):
        self.invoke()
        updated=bridge.extract_state(self.body)
        self.assertEqual(updated["next_request"]["field"], "plan_approved")
        self.assertEqual(updated["plan_reconciliation_history"][0]["merged_pr"],316)
        self.assertEqual(len([c for c in self.calls if c[0]=="PATCH"]),1)

    def test_17_bridge_rejects_actor_spoof_without_patch(self):
        self.event["comment"]["user"]["login"]="other"
        self.invoke()
        self.assertEqual(len([x for x in self.calls if x[0]=="PATCH"]),0)

    def test_18_bridge_rejects_head_drift_without_patch(self):
        old=self.api
        def override(method,path,payload=None):
            if method=="GET" and path.endswith("/branches/main"):
                return {"commit":{"sha":H_OLD}}
            return old(method,path,payload)
        self.api=override
        self.invoke()
        self.assertFalse(any(c[0]=="PATCH" for c in self.calls))

    def test_19_bridge_rejects_unmerged_pr_without_patch(self):
        old=self.api
        def override(method,path,payload=None):
            if method=="GET" and path.endswith("/pulls/316"):
                return {**PR,"merged_at":None}
            return old(method,path,payload)
        self.api=override
        self.invoke()
        self.assertFalse(any(c[0]=="PATCH" for c in self.calls))

    def test_20_evidence_never_accepts_false_creation(self):
        self.invoke()
        state=bridge.extract_state(self.body)
        state=apply_answer(state,"plan_approved",True)
        self.body="Original issue\n\n<!-- GOVERNED_REQUEST_STATE:"+encode_state(state)+" -->\n"
        self.event["issue"]["body"]=self.body
        self.event["comment"]["body"]="/governed-evidence "+json.dumps({
            "action_id":"PREP-001","result":"PASS",
            "evidence":{"canonical_branch":"main","canonical_head_sha":H_OLD}
        })
        self.calls=[]
        self.invoke()
        self.assertFalse(any(c[0]=="PATCH" for c in self.calls))

    def test_21_evidence_is_live_verifiable_for_preexisting_branch(self):
        self.invoke()
        state=bridge.extract_state(self.body)
        state=apply_answer(state,"plan_approved",True)
        for i in range(4):
            action=state["next_request"]["action_id"]
            evidence=state["next_request"]["required_evidence"]
            self.body="Original issue\n\n<!-- GOVERNED_REQUEST_STATE:"+encode_state(state)+" -->\n"
            self.event["issue"]["body"]=self.body
            self.event["comment"]["body"]="/governed-evidence "+json.dumps({
                "action_id":action,"result":"PASS","evidence":evidence
            })
            self.calls=[]
            self.invoke()
            state=bridge.extract_state(self.body)
        self.assertEqual(state["status"],"HANDOFF_READY")
        self.assertTrue(state["plan_reconciliation_pending"]["no_mutation_authority"])


if __name__=="__main__":
    unittest.main()
