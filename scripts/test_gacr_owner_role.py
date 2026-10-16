#!/usr/bin/env python3
"""Owner role is provenance-backed intent; never a lease, claim or write grant."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import gacr_owner_role as role
import gacr_owner_alias as alias
import gacr_capacity_dispatch as cap
import gacr_continuity_bus as bus
import gacr_host_issue_ingress as host

SID="session-2f8d5707f376e4b45ab7797b"
ID="GSCC-ID-68711b0e5e84a6a651d0e2a3"
CONN="GSCC-CONN-9ffbf5fd55615c6ae9dd5832c30e6918"
CID="GRT-CONT-20261014-CHAINFLOW-POC-01"
HEAD="b"*40


def docs():
    return (
      {"schema_version":"1.0.0","revision":5,"items":[{
        "continuity_id":CID,"repository":alias.CANONICAL_REPO,"coordination_issue":301,
        "participants":[],
        "logical_agents":[{
            "logical_agent_id":ID,"human_alias":"NOVA",
            "human_alias_provenance":"OWNER_ASSIGNED",
            "reference_session_ids":[SID],
            "alias_evidence_ref":"github-issue-comment:6220103789",
        }],
      }]},
      {"sessions":[{
        "session_id":SID,"agent_identity":ID,
        "repository":alias.CANONICAL_REPO,"connection_ref":CONN,
        "status":"ACTIVE","agent_role":"qualification-client",
        "relay":{"state":"ACTIVE"},
      }]},
    )


def assign(st=None, ss=None, **kw):
    a,b=docs()
    payload={
      "actor":alias.OWNER,"association":"OWNER",
      "continuity_id":CID,"coordination_issue":301,"session_id":SID,
      "logical_agent_id":ID,"connection_ref":CONN,
      "agent_role":"CODE_AGENT","work_items":list(role.WORK_ITEMS),
      "observed_head":HEAD,"current_head":HEAD,
      "evidence_ref":"github-issue-comment:222",
      "timestamp":"2026-10-16T16:39:00Z",
    }
    payload.update(kw)
    return role.assign_owner_role(st if st is not None else a,ss if ss is not None else b,**payload)


class RoleSafety(unittest.TestCase):
    def test_01_owner_role_preserves_alias_and_session(self):
        st,ss=docs()
        next_,r=assign(st,ss)
        x=next_["items"][0]["logical_agents"][0]
        self.assertEqual(x["human_alias"],"NOVA")
        self.assertEqual(x["owner_assigned_role"],"CODE_AGENT")
        self.assertEqual(x["owner_work_items"],list(role.WORK_ITEMS))
        self.assertEqual(next_["revision"],6)
        self.assertEqual(len(next_["items"][0]["participants"]),0)
        self.assertEqual(ss["sessions"][0]["agent_role"],"qualification-client")
        self.assertFalse(r["grants_write"])
        self.assertFalse(r["grants_claim"])
        self.assertFalse(r["grants_lease"])
    def test_02_owner_duplicate_is_idempotent(self):
        st,ss=docs()
        a,_=assign(st,ss)
        b,r=assign(a,ss)
        self.assertIs(a,b)
        self.assertEqual(r["status"],"OWNER_ROLE_ALREADY_ASSIGNED")
    def test_03_wrong_actor(self):
        with self.assertRaisesRegex(ValueError,"AUTHENTICATION_REQUIRED"):
            assign(actor="impostor")
    def test_04_wrong_logical_id(self):
        with self.assertRaisesRegex(ValueError,"CANONICAL_BINDING_MISMATCH"):
            assign(logical_agent_id="GSCC-ID-99b03399dd63c4c530a619e9")
    def test_05_wrong_session(self):
        with self.assertRaisesRegex(ValueError,"SESSION_MISSING"):
            assign(session_id="session-other")
    def test_06_wrong_connection(self):
        with self.assertRaisesRegex(ValueError,"CANONICAL_BINDING_MISMATCH"):
            assign(connection_ref="OTHER")
    def test_07_owner_scope_locked_to_chainflow(self):
        with self.assertRaisesRegex(ValueError,"EXACT_WORK_SCOPE_REQUIRED"):
            assign(work_items=["GMC-G01-T01"])
    def test_08_head_drift(self):
        with self.assertRaisesRegex(ValueError,"HEAD_MOVED"):
            assign(current_head="a"*40)
    def test_09_other_continuity(self):
        with self.assertRaisesRegex(ValueError,"CONTINUITY_MISMATCH"):
            assign(continuity_id="other")
    def test_10_name_required_before_role(self):
        st,ss=docs()
        st["items"][0]["logical_agents"][0]["human_alias"]="FORGE"
        with self.assertRaisesRegex(ValueError,"OWNER_ALIAS_REQUIRED"):
            assign(st,ss)
    def test_11_second_conflicting_role(self):
        st,ss=docs()
        st["items"][0]["logical_agents"][0]["owner_assigned_role"]="REVIEWER"
        with self.assertRaisesRegex(ValueError,"CONFLICTING_PREVIOUS_ASSIGNMENT"):
            assign(st,ss)
    def test_12_role_survives_projection(self):
        st,ss=docs()
        updated,_=assign(st,ss)
        bus.project_logical_agents_docs(updated,ss)
        g=updated["items"][0]["logical_agents"][0]
        self.assertEqual(g["owner_assigned_role"],"CODE_AGENT")
        self.assertEqual(g["owner_work_items"],list(role.WORK_ITEMS))
        self.assertFalse(g["grants_mutation_authority"])
    def test_13_capacity_sees_owner_role_intent(self):
        st,ss=docs()
        updated,_=assign(st,ss)
        profile=cap._owner_role_profile(ss["sessions"][0],updated)
        self.assertEqual(profile["agent_role"],"CODE_AGENT")
        self.assertEqual(profile["work_items"],list(role.WORK_ITEMS))
    def test_14_scope_restricts_gmc_tasks(self):
        candidate={
            "agent_role":"CODE_AGENT","repository":alias.CANONICAL_REPO,
            "capabilities":[],"authority_grants":[],
            "owner_work_items":list(role.WORK_ITEMS),
        }
        ok,reasons=cap._candidate_compatible(candidate,{
            "work_item_id":"GMC-G01-T01","repository":alias.CANONICAL_REPO,
            "allowed_agent_roles":["CODE_AGENT"],
        })
        self.assertFalse(ok)
        self.assertIn("OUTSIDE_OWNER_SCOPED_WORK_ITEMS",reasons)
        yes,rs=cap._candidate_compatible(candidate,{
            "work_item_id":"GR-000302/PREP-003","repository":alias.CANONICAL_REPO,
            "allowed_agent_roles":["CODE_AGENT"],
        })
        self.assertTrue(yes,rs)
    def test_15_invalid_provenance_never_dispatches(self):
        st,ss=docs()
        updated,_=assign(st,ss)
        updated["items"][0]["logical_agents"][0]["owner_role_provenance"]="SELF_REPORTED"
        self.assertEqual(cap._owner_role_profile(ss["sessions"][0],updated),{"conflict":True})
    def test_16_host_owner_actor_required(self):
        payload={
          "schema":"gacr-host-event/v1","event":"owner_role_assign",
          "session_id":SID,"logical_agent_id":ID,"connection_ref":CONN,
          "continuity_id":CID,"coordination_issue":301,
          "agent_role":"CODE_AGENT","work_items":list(role.WORK_ITEMS),
          "observed_head":HEAD,
        }
        e={"action":"created","issue":{"number":115},
           "sender":{"login":"forgery"},
           "comment":{"id":99901,"author_association":"OWNER",
             "user":{"login":alias.OWNER},
             "body":"/gacr-host "+json.dumps(payload)}}
        cfg={"host_issue_bridge":{"enabled":True,"issue_number":115,"allowed_author_associations":["OWNER"]}}
        with self.assertRaisesRegex(ValueError,"AUTHENTICATION_REQUIRED"):
            host.parse_issue_comment_event(e,cfg)
        e["sender"]["login"]=alias.OWNER
        verified=host.parse_issue_comment_event(e,cfg)
        self.assertEqual(verified["event"],"owner_role_assign")
        self.assertEqual(verified["_actor"],alias.OWNER)
    def test_17_unchanged_canonical_session(self):
        st,ss=docs()
        baseline=copy.deepcopy(ss)
        assign(st,ss)
        self.assertEqual(ss,baseline)

if __name__=="__main__":
    unittest.main()
