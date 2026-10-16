#!/usr/bin/env python3
"""Candidate alias at First Touch is never permission to reuse a GACR identity."""
from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from gscc_session_runtime import (
    resolve_alias_binding_intent, resolve_alias_attach_proof,
    _build_gacr_attach_payload, prepare, resume_gacr_attach,
)
from gscc_persisted_entry_pipeline import run_pipeline
from gscc_arrival_identity import mint
from test_gscc_per_arrival_identity_session_runtime import (
    base_envelope, issue_event, pass_q9, GITHUB, REPO,
)

ALIAS="CHAINFLOW-CODE_AGENT-NEW-01"
EMPTY={"schema_version":"1.0.0","items":[]}
EMPTY_SESSIONS={"sessions":[]}
CANONICAL={
  "schema_version":"1.0.0",
  "items":[{
    "continuity_id":"GRT-CONT-EXISTING",
    "repository":REPO,
    "logical_agents":[{
      "human_alias":"FORGE",
      "human_alias_provenance":"OWNER_ASSIGNED",
      "logical_agent_id":"logical-forge",
      "reference_session_ids":["session-forge"],
    }],
  }],
}
SESSION={
    "session_id":"session-forge",
    "agent_identity":"logical-forge",
    "repository":REPO,
    "status":"STALLED",
    "relay":{"state":"TAKEOVER_READY"},
}


def packet(alias=ALIAS,role="CODE_AGENT_CANDIDATE"):
    return {"sections":{
      "request":{"logical_agent_alias":alias},
      "agent":{"agent_role":role},
      "github":{"repository_full_name":REPO},
    }}


class CandidateAliasPolicy(unittest.TestCase):
    def test_01_unknown_first_touch_candidate_is_not_bound(self):
        self.assertIsNone(resolve_alias_binding_intent(
            packet(), EMPTY_SESSIONS, EMPTY, classification="FIRST_TOUCH"
        ))

    def test_02_no_new_identity_authority_is_minted(self):
        self.assertIsNone(resolve_alias_attach_proof(
            packet(),EMPTY_SESSIONS,EMPTY,{"items":[]},classification="FIRST_TOUCH"
        ))

    def test_03_missing_classification_fails(self):
        with self.assertRaisesRegex(ValueError,"LOGICAL_AGENT_ALIAS_UNKNOWN"):
            resolve_alias_binding_intent(packet(),EMPTY_SESSIONS,EMPTY)

    def test_04_continuation_unknown_alias_fails(self):
        with self.assertRaisesRegex(ValueError,"LOGICAL_AGENT_ALIAS_UNKNOWN"):
            resolve_alias_binding_intent(
                packet(),EMPTY_SESSIONS,EMPTY,classification="CONTINUATION"
            )

    def test_05_first_touch_with_non_candidate_role_fails(self):
        with self.assertRaisesRegex(ValueError,"LOGICAL_AGENT_ALIAS_UNKNOWN"):
            resolve_alias_binding_intent(
                packet(role="CODE_AGENT"),EMPTY_SESSIONS,EMPTY,
                classification="FIRST_TOUCH",
            )

    def test_06_existing_owner_alias_cannot_be_borrowed_by_candidate(self):
        with self.assertRaisesRegex(ValueError,"NEW_CANDIDATE_ALIAS_ALREADY_CANONICAL"):
            resolve_alias_binding_intent(
                packet(alias="FORGE"),{"sessions":[SESSION]},CANONICAL,
                classification="FIRST_TOUCH",
            )

    def test_07_existing_alias_without_candidate_role_keeps_original_resolution(self):
        result=resolve_alias_binding_intent(
            packet(alias="FORGE",role="CODE_AGENT"),
            {"sessions":[SESSION]},CANONICAL,classification="FIRST_TOUCH",
        )
        self.assertEqual(result["logical_agent_id"],"logical-forge")
        self.assertFalse(result["grants_mutation_authority"])

    def test_08_invalid_alias_fails(self):
        with self.assertRaisesRegex(ValueError,"invalid logical_agent_alias"):
            resolve_alias_binding_intent(
                packet(alias="invalid alias with spaces"),EMPTY_SESSIONS,
                EMPTY,classification="FIRST_TOUCH",
            )

    def test_09_untrusted_existing_alias_fails(self):
        untrusted=json.loads(json.dumps(CANONICAL))
        untrusted["items"][0]["logical_agents"][0]["human_alias"]=ALIAS
        untrusted["items"][0]["logical_agents"][0]["human_alias_provenance"]="SELF_REPORTED"
        with self.assertRaisesRegex(ValueError,"LOGICAL_AGENT_ALIAS_UNTRUSTED"):
            resolve_alias_binding_intent(
                packet(),EMPTY_SESSIONS,untrusted,classification="FIRST_TOUCH"
            )

    def test_10_canonical_ambiguity_fails(self):
        ambiguous=json.loads(json.dumps(CANONICAL))
        ambiguous["items"][0]["logical_agents"].append({
            "human_alias":"FORGE","human_alias_provenance":"OWNER_ASSIGNED",
            "logical_agent_id":"another-forge",
        })
        with self.assertRaisesRegex(ValueError,"LOGICAL_AGENT_ALIAS_AMBIGUOUS"):
            resolve_alias_binding_intent(
                packet(alias="FORGE"),{"sessions":[SESSION]},
                ambiguous,classification="FIRST_TOUCH",
            )

    def test_11_existing_alias_never_silently_resumes_as_candidate(self):
        with self.assertRaisesRegex(ValueError,"NEW_CANDIDATE_ALIAS_ALREADY_CANONICAL"):
            resolve_alias_attach_proof(
                packet(alias="FORGE"),{"sessions":[SESSION]},CANONICAL,
                {"items":[]},classification="FIRST_TOUCH",
            )

    def test_12_empty_alias_is_not_a_binding(self):
        self.assertIsNone(resolve_alias_binding_intent(
            packet(alias="UNAVAILABLE"),EMPTY_SESSIONS,EMPTY,
            classification="FIRST_TOUCH",
        ))

    def test_13_explicit_unknown_candidate_alone_does_not_grant_mutation(self):
        rt={"identity_id":"GSCC-ID-new","connection_ref":"GSCC-CONN-new",
            "arrival_ref":"GSCC-ARRIVAL-new"}
        p=packet()
        p["sections"].update({
            "provider":{"provider":"chatgpt"},
            "github":{"repository_full_name":REPO,"head_sha":"a"*40,"branch":"main"},
        })
        result=_build_gacr_attach_payload(rt,p,{"evidence_ref":"gscc-control:verified"},None)
        self.assertEqual(result["agent"],rt["identity_id"])
        self.assertNotIn("same_logical_agent_session_id",result)
        self.assertNotIn("continuity_id",result)
        self.assertEqual(result["connection_ref"],rt["connection_ref"])


class PersistedNewAgentRecovery(unittest.TestCase):
    def test_14_real_first_touch_q9_then_gse_and_resume_without_borrowing_agent(self):
        env=base_envelope(ALIAS)
        env["provider_context"]["agent"]["agent_role"]="CODE_AGENT_CANDIDATE"
        arrival=mint(env,issue_event(1321001,321),run_id="q9-candidate-arrival-321")
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            db=folder/"arrival.sqlite"
            p=run_pipeline(
                arrival,GITHUB,db,run_id="q9-candidate-321",
                observed_at="2026-10-16T15:10:00+00:00",
            )
            self.assertEqual(p["classification"],"FIRST_TOUCH")
            runtime=prepare(db,"q9-candidate-321",321)
            session_path=folder/"sessions.json"
            continuity_path=folder/"continuities.json"
            forensic_path=folder/"forensics.json"
            session_path.write_text(json.dumps({"sessions":[SESSION]}))
            continuity_path.write_text(json.dumps(CANONICAL))
            forensic_path.write_text(json.dumps({"items":[]}))
            result=pass_q9(
                db,runtime,sessions_path=session_path,
                continuity_path=continuity_path,forensics_path=forensic_path,
            )
            self.assertEqual(result["state"],"GSE_VERIFIED_WAITING_GACR")
            self.assertIsNone(result["logical_agent_alias_attach_proof"])
            with sqlite3.connect(db) as conn:
                real_gscc_identity=conn.execute(
                    "SELECT identity_id FROM gscc_session_runtime WHERE runtime_id=?",
                    (runtime["runtime_id"],),
                ).fetchone()[0]
            self.assertEqual(result["gacr_attach"]["agent"],real_gscc_identity)
            self.assertNotIn("same_logical_agent_session_id",result["gacr_attach"])
            self.assertNotIn("continuity_id",result["gacr_attach"])
            resume=resume_gacr_attach(
                db,runtime["runtime_id"],sessions_path=session_path,
                continuity_path=continuity_path,forensics_path=forensic_path,
            )
            self.assertEqual(resume["gacr_attach"],result["gacr_attach"])
            self.assertFalse(resume["authority_granted"])
            with sqlite3.connect(db) as conn:
                state=conn.execute(
                    "SELECT state FROM gscc_session_runtime WHERE runtime_id=?",
                    (runtime["runtime_id"],),
                ).fetchone()[0]
                self.assertEqual(state,"GSE_VERIFIED_WAITING_GACR")
                rows=conn.execute(
                    "SELECT COUNT(*) FROM gscc_session_bindings WHERE arrival_ref=?",
                    (arrival["gscc_arrival"]["arrival_ref"],),
                ).fetchone()[0]
                self.assertEqual(rows,1)

if __name__=="__main__":
    unittest.main()
