#!/usr/bin/env python3
"""Owner alias registration on canonical GACR projection — fail closed regression."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import gacr_owner_alias as owner
import gacr_host_issue_ingress as host
import gacr_continuity_coordination as coord

SID="session-2f8d5707f376e4b45ab7797b"
IDENTITY="GSCC-ID-68711b0e5e84a6a651d0e2a3"
CONN="GSCC-CONN-9ffbf5fd55615c6ae9dd5832c30e6918"
C="GRT-CONT-20261014-CHAINFLOW-POC-01"
HEAD="a"*40


def docs():
    return (
        {"schema_version":"1.0.0","revision":2,"items":[
            {"continuity_id":C,"repository":owner.CANONICAL_REPO,
             "coordination_issue":301,"participants":[],"logical_agents":[]},
            {"continuity_id":"GRT-CONT-OTHER","repository":owner.CANONICAL_REPO,
             "coordination_issue":400,"participants":[],"logical_agents":[
                 {"logical_agent_id":"logical-previous","human_alias":"FORGE",
                  "human_alias_provenance":"OWNER_ASSIGNED"}]},
        ]},
        {"sessions":[{"session_id":SID,"agent_identity":IDENTITY,
            "repository":owner.CANONICAL_REPO,"connection_ref":CONN,
            "provider":"chatgpt","status":"ACTIVE","relay":{"state":"ACTIVE"}}]},
    )


def assign(s=None,ss=None,**kw):
    s0,ss0=docs()
    p={
        "actor":owner.OWNER,"association":"OWNER",
        "continuity_id":C,"coordination_issue":301,"session_id":SID,
        "logical_agent_id":IDENTITY,"connection_ref":CONN,"short_alias":"NOVA",
        "observed_head":HEAD,"current_head":HEAD,
        "evidence_ref":"github-issue-comment:123456",
        "arrival_issue":321,"timestamp":"2026-10-16T16:22:00Z"
    }
    p.update(kw)
    return owner.assign_owner_alias(s if s is not None else s0, ss if ss is not None else ss0,**p)


def event():
    return {"action":"created","issue":{"number":115},
        "sender":{"login":owner.OWNER},
        "comment":{"id":444445,"created_at":"2026-10-16T16:22:00Z",
            "author_association":"OWNER","user":{"login":owner.OWNER},
            "body":"/gacr-host "+json.dumps({
                "schema":"gacr-host-event/v1","event":"owner_alias_assign",
                "session_id":SID,"logical_agent_id":IDENTITY,
                "connection_ref":CONN,"short_alias":"NOVA",
                "continuity_id":C,"coordination_issue":301,
                "arrival_issue":321,"observed_head":HEAD,
            })}}


class OwnerAliasTests(unittest.TestCase):
    def test_01_new_alias_is_canonical_projection_only(self):
        old,sessions=docs()
        new,r=assign(old,sessions)
        self.assertEqual(r["status"],"OWNER_ALIAS_ASSIGNED")
        self.assertEqual(new["revision"],3)
        self.assertEqual(new["items"][0]["logical_agents"][0]["human_alias"],"NOVA")
        self.assertEqual(new["items"][0]["logical_agents"][0]["logical_agent_id"],IDENTITY)
        self.assertEqual(new["items"][0]["logical_agents"][0]["reference_session_ids"],[SID])
        self.assertEqual(len(new["items"][0]["participants"]),0)
        self.assertFalse(r["grants_claim"])
        self.assertFalse(r["grants_write"])
        self.assertEqual(len(new["items"][0]["owner_alias_history"]),1)
        self.assertEqual(old["items"][0]["logical_agents"],[])
        self.assertEqual(sessions["sessions"][0]["agent_identity"],IDENTITY)

    def test_02_owner_alias_resolution_uses_existing_session(self):
        s,session=assign()
        result=coord.resolve_logical_agent_alias_docs(s,session,alias="nova")
        self.assertEqual(result["logical_agent_id"],IDENTITY)
        self.assertEqual(result["human_alias"],"NOVA")
        self.assertEqual(result["reference_session_ids"],[SID])
        self.assertFalse(result["grants_mutation_authority"])

    def test_03_idempotent_same_owner_assignment(self):
        s,sessions=docs()
        first,_=assign(s,sessions)
        second,r=assign(first,sessions)
        self.assertIs(first,second)
        self.assertEqual(r["status"],"OWNER_ALIAS_ALREADY_ASSIGNED")
        self.assertEqual(len(second["items"][0]["owner_alias_history"]),1)

    def test_04_wrong_actor_refused(self):
        with self.assertRaisesRegex(ValueError,"AUTHENTICATED_OWNER_REQUIRED"):
            assign(actor="impostor")

    def test_05_wrong_association_refused(self):
        with self.assertRaisesRegex(ValueError,"AUTHENTICATED_OWNER_REQUIRED"):
            assign(association="NONE")

    def test_06_session_identity_mismatch_refused(self):
        with self.assertRaisesRegex(ValueError,"SESSION_IDENTITY_MISMATCH"):
            assign(logical_agent_id="GSCC-ID-99b03399dd63c4c530a619e9")

    def test_07_connection_mismatch_refused(self):
        with self.assertRaisesRegex(ValueError,"SESSION_IDENTITY_MISMATCH"):
            assign(connection_ref="GSCC-CONN-fake")

    def test_08_wrong_session_refused(self):
        with self.assertRaisesRegex(ValueError,"EXACT_CANONICAL_SESSION_REQUIRED"):
            assign(session_id="session-forge")

    def test_09_wrong_head_refused(self):
        with self.assertRaisesRegex(ValueError,"HEAD_MOVED"):
            assign(current_head="b"*40)

    def test_10_alias_collision_is_refused(self):
        with self.assertRaisesRegex(ValueError,"COLLISION_OTHER_LOGICAL_AGENT"):
            assign(short_alias="FORGE")

    def test_11_untrusted_same_name_refused(self):
        st,sessions=docs()
        st["items"][0]["logical_agents"]=[{
            "logical_agent_id":IDENTITY,"human_alias":"NOVA",
            "human_alias_provenance":"SELF_REPORTED"}]
        with self.assertRaisesRegex(ValueError,"UNTRUSTED_EXISTING_PROVENANCE"):
            assign(st,sessions)

    def test_12_second_alias_for_one_agent_refused(self):
        st,sessions=docs()
        st["items"][0]["logical_agents"]=[{
            "logical_agent_id":IDENTITY,"human_alias":"OTHER",
            "human_alias_provenance":"OWNER_ASSIGNED"}]
        with self.assertRaisesRegex(ValueError,"EXISTING_NAME_CONFLICT"):
            assign(st,sessions)

    def test_13_invalid_alias_refused(self):
        with self.assertRaisesRegex(ValueError,"FORMAT_INVALID"):
            assign(short_alias="bad spaced alias")

    def test_14_wrong_continuity_refused(self):
        with self.assertRaisesRegex(ValueError,"CONTINUITY_NOT_FOUND"):
            assign(continuity_id="GRT-CONT-UNKNOWN")

    def test_15_no_owner_proof_refused(self):
        with self.assertRaisesRegex(ValueError,"GITHUB_EVIDENCE_REQUIRED"):
            assign(evidence_ref="unverified owner request")

    def test_16_closed_session_refused(self):
        state,ss=docs()
        ss["sessions"][0]["status"]="CLOSED"
        with self.assertRaisesRegex(ValueError,"SESSION_IDENTITY_MISMATCH"):
            assign(state,ss)

    def test_17_host_event_author_and_actor_match(self):
        event_obj=event()
        p=host.parse_issue_comment_event(event_obj,{"host_issue_bridge":{
            "enabled":True,"issue_number":115,"allowed_author_associations":["OWNER"],
            "max_payload_chars":8192}})
        self.assertEqual(p["event"],"owner_alias_assign")
        self.assertEqual(p["_actor"],owner.OWNER)
        self.assertEqual(p["_association"],"OWNER")

    def test_18_host_event_spoof_refused(self):
        ev=event()
        ev["sender"]["login"]="another"
        with self.assertRaisesRegex(ValueError,"AUTHENTICATED_OWNER_REQUIRED"):
            host.parse_issue_comment_event(ev,{"host_issue_bridge":{
                "enabled":True,"issue_number":115,"allowed_author_associations":["OWNER"]}})

    def test_19_host_ingress_end_to_end_preserves_existing_store(self):
        old,sessions=docs()
        with tempfile.TemporaryDirectory() as folder:
            state_path=Path(folder)/"continuities.json"
            state_path.write_text(json.dumps(old))
            ev=event()
            p=host.parse_issue_comment_event(ev,{"host_issue_bridge":{
                "enabled":True,"issue_number":115,"allowed_author_associations":["OWNER"]}})
            with patch.object(host,"ROOT",Path(folder)),\
                 patch.object(coord,"STATE_PATH",state_path),\
                 patch.object(coord,"git_head",return_value=HEAD),\
                 patch.object(host,"active_sessions",return_value=sessions["sessions"]),\
                 patch.object(host,"evidence_processed",return_value=False):
                (Path(folder)/".template-source").write_text("")
                result=host.process(p,owner.CANONICAL_REPO)
            after=json.loads(state_path.read_text())
            self.assertEqual(result["alias"],"NOVA")
            self.assertEqual(after["items"][0]["logical_agents"][0]["logical_agent_id"],IDENTITY)
            self.assertEqual(after["items"][1],old["items"][1])
            self.assertFalse(result["grants_write"])

if __name__=="__main__":
    unittest.main()
