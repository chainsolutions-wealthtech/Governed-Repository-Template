#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from local_governed_entry import answer, complete_baseline, decode_state, encode_state, new_request

ROOT=Path(__file__).resolve().parents[1]

def main():
    s=new_request("LOCAL-1","owner/repo","a"*40,True,"first agent")
    expected=[
      ("agent_identity","ChatGPT"),("provider","CHATGPT"),("connection_intent","WORK_REQUEST"),
      ("project_mission","Build the governed project"),("project_scope",{"in_scope":["core"],"out_of_scope":["later"]}),
      ("project_profile","chainsolutions-fullstack-web"),("architecture_status","NEW_EMPTY_PROJECT"),
      ("architecture_notes","Governance only; no project code yet."),("infrastructure_status","NO_INFRASTRUCTURE_YET"),
      ("external_systems",[]),("constraints",["zero regression"]),("first_work_objective","Create the first project feature")
    ]
    for field,value in expected:
        if s["next_request"]["field"]!=field: raise SystemExit(f"LOCAL_ENTRY_SELFTEST_FAILED: expected {field}")
        s=answer(s,field,value)
    if s["next_request"]["field"]!="baseline_approved": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: approval missing")
    s=answer(s,"baseline_approved",True)
    if s["next_request"]["kind"]!="APPLY_BASELINE": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: apply missing")
    s=complete_baseline(s,"b"*40,"LOCAL-000001-S1")
    if s["status"]!="LOCAL_HANDOFF_READY": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: first handoff")
    if decode_state(encode_state(s))["handoff"]["session_id"]!="LOCAL-000001-S1": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: persistence")

    n=new_request("LOCAL-2","owner/repo","c"*40,False,"later agent")
    for field,value in [
      ("agent_identity","Claude"),("provider","CLAUDE"),("connection_intent","CODE_CHANGE"),
      ("local_entry_action","CONTINUE_GOVERNED_WORK"),("requested_objective","Continue current work")
    ]:
        if n["next_request"]["field"]!=field: raise SystemExit(f"LOCAL_ENTRY_SELFTEST_FAILED: normal expected {field}")
        n=answer(n,field,value)
    if n["status"]!="LOCAL_HANDOFF_READY": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: normal handoff")

    wf=(ROOT/".github/workflows/governed-local-entry.yml").read_text(encoding="utf-8")
    for fragment in ["governed_local_start","contents: write","issues: write","local_entry_apply_baseline.py","github.repository != 'chainsolutions-wealthtech/Governed-Repository-Template'"]:
        if fragment not in wf: raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: workflow contract "+fragment)
    print("LOCAL_GOVERNED_ENTRY_SELFTEST_PASS")

if __name__=="__main__": main()
