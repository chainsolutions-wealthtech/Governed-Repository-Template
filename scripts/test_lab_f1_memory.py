#!/usr/bin/env python3
"""LAB-local canonical memory integrity; never mutates registries."""
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTINUITY="GRT-CONT-20261017-F1RECOVERY-001"
BASE=ROOT/"docs"/"labs"/CONTINUITY
REGISTERS=["OBSERVATIONS","CHRONOLOGY","DECISIONS","TASK_CANDIDATES","CHECKPOINT"]


def read(name):
    return json.loads((BASE/(name+".json")).read_text(encoding="utf-8"))


def validate():
    for name in REGISTERS:
        data=read(name)
        assert data["continuity_id"]==CONTINUITY,(name,"wrong continuity")
        assert data["revision"]>=1,(name,"bad revision")
    observations=read("OBSERVATIONS")
    ids=[x["id"] for x in observations["items"]]
    assert len(ids)==len(set(ids)), "duplicate observation ID"
    assert [x["sequence"] for x in observations["items"]]==list(range(1,len(ids)+1))
    for o in observations["items"]:
        assert o["continuity_id"]==CONTINUITY
        assert o["id"].startswith(CONTINUITY+"-OBS-")
        assert o["status"] in {"CONFIRMED_CODE","CONFIRMED_SIMULATION","RISK_TO_VERIFY","HYPOTHESIS","DISPROVED"}
        assert o["source_refs"] and all(x.startswith("https://github.com/") for x in o["source_refs"])
        assert o["limitation"],"caveat required"
    events=read("CHRONOLOGY")["events"]
    assert [x["seq"] for x in events]==list(range(1,len(events)+1))
    assert len({x["event_id"] for x in events})==len(events)
    assert all(x["source_ref"] for x in events)
    dec=read("DECISIONS")["items"]
    assert len({x["decision_id"] for x in dec})==len(dec)
    assert all(x["does_not_grant_execution_authority"] for x in dec)
    tasks=read("TASK_CANDIDATES")
    assert tasks["status"]=="NOT_A_CANONICAL_TASK_QUEUE"
    assert tasks["approval"]=="NONE" and tasks["claims_created"]==0
    assert tasks["dispatcher"]=="NOT_CONNECTED"
    assert len({t["candidate_id"] for t in tasks["items"]})==len(tasks["items"])
    for task in tasks["items"]:
        assert task["state"]=="ANALYZE_ONLY"
        assert task["work_item_id"] is None and task["task_claim_id"] is None
        assert task["execution_authorized"] is False
        assert all(x in ids for x in task["observation_refs"])
    state=read("CHECKPOINT")
    assert state["phase"]=="OBSERVE_DOCUMENT_ANALYZE"
    assert state["task_dispatch_status"]=="NOT_AUTHORIZED"
    assert state["merge_status"]=="NOT_MERGED"
    assert state["session_id"] is None
    assert (BASE/"MEMORY.md").exists()
    return {"observations":len(ids),"events":len(events),"decisions":len(dec),"candidates":len(tasks["items"])}


class LabMemoryTests(unittest.TestCase):
    def test_integrity(self):
        self.assertGreater(validate()["observations"],0)
    def test_candidate_cannot_be_dispatched(self):
        data=read("TASK_CANDIDATES")
        self.assertTrue(all(t["work_item_id"] is None for t in data["items"]))
        self.assertFalse(any(t["execution_authorized"] for t in data["items"]))
    def test_provenance_not_fabricated(self):
        events=read("CHRONOLOGY")["events"]
        self.assertTrue(all(event["occurred_at"] is None or
                            event["occurred_at_provenance"] != "EXACT_TIME_NOT_CAPTURED_IN_THIS_REGISTER"
                            for event in events))


if __name__=="__main__":
    unittest.main(verbosity=2)
