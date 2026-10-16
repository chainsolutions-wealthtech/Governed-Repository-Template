#!/usr/bin/env python3
"""No grant by HOLD reopening; original request, decision and evidence survive."""
from __future__ import annotations
import copy
import json
import unittest

import control_plane_issue_bridge as bridge
from governed_hold_review import reexamine_authority_hold
from governed_request import new_request, apply_answer, encode_state

REPO="chainsolutions-wealthtech/Governed-Repository-Template"
OWNER="Wealthtechinnovations"
OLD="a"*40
HEAD="b"*40

def held():
    state=new_request("GR-000284","original-agent","github","same GR")
    answers={
        "entry_action":"LAB_EVOLUTION",
        "connection_intent":"CODE_CHANGE",
        "objective":"Q12 renewal technical recovery on existing arrival",
        "target_repository":REPO,
        "target_observation":{"exists":True,"default_branch":"main","head_sha":OLD,"governance_detected":True},
        "lab_branch_name":"lab/gr284-existing",
        "pr_required":True,"lab_authority":False,
    }
    while (state.get("next_request") or {}).get("field") in answers:
        field=state["next_request"]["field"]
        state=apply_answer(state,field,answers[field])
    assert state["status"]=="HOLD_FOR_REVIEW",state
    return state

def reopen(state,**kwargs):
    p={"expected_revision":state["revision"],"expected_head":HEAD,"observed_head":HEAD,
       "owner_actor":OWNER,"author_association":"MEMBER",
       "evidence_refs":["github-pr:316","github-pr:317","github-pr:318"],
       "reason":"Owner review after the three merged maintenance corrections."}
    p.update(kwargs)
    return reexamine_authority_hold(state,**p)

class HoldReviewTests(unittest.TestCase):
    def setUp(self): self.original=held()

    def test_01_preserves_identity_denial_revision_and_history(self):
        revised=reopen(self.original)
        self.assertEqual(revised["request_id"],"GR-000284")
        self.assertEqual(revised["agent"],self.original["agent"])
        self.assertEqual(revised["revision"],self.original["revision"]+1)
        self.assertEqual(revised["status"],"WAITING_FOR_ANSWER")
        self.assertEqual(revised["next_request"]["field"],"target_observation")
        self.assertNotIn("lab_authority",revised["answers"])
        self.assertNotIn("target_observation",revised["answers"])
        self.assertEqual(revised["hold_review_history"][0]["previous"]["authority_answer"],False)
        self.assertEqual(revised["hold_review_history"][0]["previous"]["target_observation"]["head_sha"],OLD)
        self.assertFalse(revised["hold_review_history"][0]["grants_mutation_authority"])
    def test_02_stale_revision(self):
        with self.assertRaisesRegex(ValueError,"STALE_REVISION"):
            reopen(self.original,expected_revision=self.original["revision"]-1)
    def test_03_head_drift(self):
        with self.assertRaisesRegex(ValueError,"HEAD_MOVED"):
            reopen(self.original,observed_head=OLD)
    def test_04_invalid_head(self):
        with self.assertRaisesRegex(ValueError,"HEAD_INVALID"):
            reopen(self.original,expected_head="invalid")
    def test_05_wrong_actor(self):
        with self.assertRaisesRegex(ValueError,"OWNER_AUTHENTICATION"):
            reopen(self.original,owner_actor="any-coder")
    def test_06_wrong_author_association(self):
        with self.assertRaisesRegex(ValueError,"OWNER_AUTHENTICATION"):
            reopen(self.original,author_association="NONE")
    def test_07_bogus_evidence(self):
        with self.assertRaisesRegex(ValueError,"MERGED_PR_REFERENCES"):
            reopen(self.original,evidence_refs=["github-pr:bogus"])
    def test_08_duplicate_evidence(self):
        with self.assertRaisesRegex(ValueError,"MERGED_PR_REFERENCES"):
            reopen(self.original,evidence_refs=["github-pr:316","github-pr:316"])
    def test_09_wrong_phase(self):
        state=copy.deepcopy(self.original)
        state["phase"]="PLAN_APPROVAL"
        with self.assertRaisesRegex(ValueError,"AUTHORITY_ONLY"):
            reopen(state)
    def test_10_prior_execution_denied(self):
        state=copy.deepcopy(self.original)
        state["execution_plan"]=[{"id":"PREP-001","status":"DONE"}]
        with self.assertRaisesRegex(ValueError,"NO_PRIOR_EXECUTION"):
            reopen(state)
    def test_11_replay_denied(self):
        state=reopen(self.original)
        with self.assertRaisesRegex(ValueError,"AUTHORITY_ONLY"):
            reopen(state)
    def test_12_cannot_answer_during_hold_without_review(self):
        with self.assertRaisesRegex(ValueError,"unexpected answer"):
            apply_answer(self.original,"lab_authority",True)
    def test_13_new_baseline_then_new_owner_question(self):
        state=reopen(self.original)
        state=apply_answer(state,"target_observation",{"exists":True,"default_branch":"main","head_sha":HEAD,"governance_detected":True})
        self.assertEqual(state["next_request"]["field"],"lab_authority")
        state=apply_answer(state,"lab_authority",True)
        self.assertEqual(state["status"],"PLAN_READY")
        self.assertEqual(state["next_request"]["field"],"plan_approved")
        self.assertTrue(state["hold_review_pending"]["no_write_grant"])
        self.assertEqual(state["hold_review_history"][0]["previous"]["authority_answer"],False)
    def test_14_second_denial_retains_first(self):
        state=reopen(self.original)
        state=apply_answer(state,"target_observation",{"exists":True,"default_branch":"main","head_sha":HEAD,"governance_detected":True})
        state=apply_answer(state,"lab_authority",False)
        self.assertEqual(state["status"],"HOLD_FOR_REVIEW")
        self.assertEqual(len(state["hold_review_history"]),1)
    def test_15_reason_required(self):
        with self.assertRaisesRegex(ValueError,"REASON_REQUIRED"):
            reopen(self.original,reason="")
    def test_16_cannot_mutate_original(self):
        before=copy.deepcopy(self.original)
        reopen(self.original)
        self.assertEqual(before,self.original)

class BridgeReviewTests(unittest.TestCase):
    def setUp(self):
        self.calls=[]
        self.state=held()
        self.body="Original issue\n\n<!-- GOVERNED_REQUEST_STATE:"+encode_state(self.state)+" -->\n"
        self.event={"issue":{"number":284,"title":"[Governed Request] F1 Q12"},
          "sender":{"login":OWNER},
          "comment":{"user":{"login":OWNER},"author_association":"MEMBER",
             "body":"/governed-review-hold "+json.dumps({
               "expected_revision":self.state["revision"],"expected_head":HEAD,
               "reason":"Owner review after three merged maintenance corrections.",
               "evidence_refs":["github-pr:316","github-pr:317","github-pr:318"]})}}
    def api(self,method,path,payload=None):
        self.calls.append((method,path,payload))
        if method=="GET" and path.endswith("/issues/284"):
            return {"number":284,"body":self.body}
        if method=="GET" and path.endswith("/branches/main"):
            return {"commit":{"sha":HEAD}}
        if method=="GET" and path == "/repos/"+REPO:
            return {"full_name":REPO,"default_branch":"main"}
        if method=="GET" and "/pulls/" in path:
            return {"number":int(path.rsplit("/",1)[-1]),"merged_at":"2026-10-16T05:00:00Z","base":{"ref":"main"}}
        if method=="PATCH":
            self.body=payload["body"]
            return {}
        if method=="POST":
            return {"id":1000+len(self.calls)}
        raise AssertionError((method,path))
    def call(self):
        old=bridge.api
        bridge.api=self.api
        try: bridge.handle_comment(self.event)
        finally: bridge.api=old
    def test_17_bridge_changes_same_marker_and_comments(self):
        self.call()
        self.assertEqual(bridge.extract_state(self.body)["next_request"]["field"],"target_observation")
        self.assertEqual(len([x for x in self.calls if x[0]=="PATCH"]),1)
        self.assertEqual(len([x for x in self.calls if x[0]=="POST"]),2)
    def test_18_spoofed_actor_cannot_patch(self):
        self.event["comment"]["user"]["login"]="other"
        self.call()
        self.assertFalse(any(x[0]=="PATCH" for x in self.calls))
    def test_19_unmerged_pr_cannot_patch(self):
        orig=self.api
        def fake(method,path,payload=None):
            if method=="GET" and "/pulls/" in path:
                return {"number":int(path.rsplit("/",1)[-1]),"merged_at":None,"base":{"ref":"main"}}
            return orig(method,path,payload)
        self.api=fake
        self.call()
        self.assertFalse(any(x[0]=="PATCH" for x in self.calls))
    def test_20_wrong_live_head_cannot_patch(self):
        orig=self.api
        def fake(method,path,payload=None):
            if method=="GET" and path.endswith("/branches/main"):
                return {"commit":{"sha":OLD}}
            return orig(method,path,payload)
        self.api=fake
        self.call()
        self.assertFalse(any(x[0]=="PATCH" for x in self.calls))

    def _reply(self, field, value, actor=OWNER):
        self.event["issue"]["body"]=self.body
        self.event["sender"]["login"]=actor
        self.event["comment"]["user"]["login"]=actor
        self.event["comment"]["body"]="/governed-answer "+json.dumps({
            "field":field,"value":value,
        })
        self.calls.clear()
        self.call()

    def test_21_forged_target_observation_is_refused(self):
        self.call()
        self._reply("target_observation", {
            "exists":True,"default_branch":"main",
            "head_sha":OLD,"governance_detected":True,
        })
        self.assertEqual(bridge.extract_state(self.body)["next_request"]["field"],"target_observation")
        self.assertFalse(any(x[0]=="PATCH" for x in self.calls))

    def test_22_other_actor_cannot_set_lab_authority(self):
        self.call()
        self._reply("target_observation", {
            "exists":True,"default_branch":"main",
            "head_sha":HEAD,"governance_detected":True,
        })
        self.assertEqual(bridge.extract_state(self.body)["next_request"]["field"],"lab_authority")
        self._reply("lab_authority",True,actor="other-agent")
        self.assertEqual(bridge.extract_state(self.body)["next_request"]["field"],"lab_authority")
        self.assertFalse(any(x[0]=="PATCH" for x in self.calls))

    def test_23_owner_reanswer_does_not_execute_preparation(self):
        self.call()
        self._reply("target_observation", {
            "exists":True,"default_branch":"main",
            "head_sha":HEAD,"governance_detected":True,
        })
        self._reply("lab_authority",True)
        updated=bridge.extract_state(self.body)
        self.assertEqual(updated["status"],"PLAN_READY")
        self.assertEqual(updated["next_request"]["field"],"plan_approved")
        self.assertFalse(updated["hold_review_history"][-1]["grants_lab_authority"])
        self.assertTrue(all(item["status"]=="PENDING" for item in updated["execution_plan"]))

if __name__=="__main__":
    unittest.main()
