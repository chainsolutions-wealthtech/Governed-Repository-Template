#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from local_governed_entry import answer, complete_baseline, decode_state, encode_state, mark_credentials_verified, new_request, record_mcp_discovery

ROOT=Path(__file__).resolve().parents[1]

def answer_expected(s,field,value):
    if (s.get("next_request") or {}).get("field")!=field:
        raise SystemExit(f"LOCAL_ENTRY_SELFTEST_FAILED: expected {field}, got {(s.get('next_request') or {}).get('field')}")
    return answer(s,field,value)

def first_base():
    s=new_request("LOCAL-1","owner/repo","a"*40,True,"first agent")
    for field,value in [
      ("agent_identity","ChatGPT"),("provider","CHATGPT"),("connection_intent","WORK_REQUEST"),
      ("project_mission","Build the governed project"),("project_scope",{"in_scope":["core"],"out_of_scope":["later"]}),
      ("project_profile","application"),("architecture_status","NEW_EMPTY_PROJECT"),
      ("architecture_notes","No application code yet."),("infrastructure_status","NO_INFRASTRUCTURE_YET"),
      ("external_systems",[]),("constraints",["zero regression"]),("first_work_objective","Create first feature")
    ]: s=answer_expected(s,field,value)
    return s

def main():
    s=first_base()
    s=answer_expected(s,"baseline_approved",True)
    s=answer_expected(s,"setup_repository_now",True)
    s=answer_expected(s,"link_mcp_server",True)
    s=answer_expected(s,"mcp_transport","DIRECT_MCP_TOKEN")
    s=answer_expected(s,"mcp_endpoint","https://mcp.example.test/mcp")
    s=answer_expected(s,"mcp_discovery_scope","FULL_GOVERNED_MAPPING")
    s=answer_expected(s,"domain_strategy","DISCOVER_EXISTING_THEN_PROPOSE")
    s=answer_expected(s,"runtime_mutation_policy","EXPLICIT_APPROVAL_FOR_SCOPED_WRITE")
    if s["next_request"]["kind"]!="CREDENTIAL_GATE": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: credential gate")
    s=mark_credentials_verified(s)
    if s["next_request"]["kind"]!="MCP_DISCOVERY": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: discovery gate")
    s=record_mcp_discovery(s,{"observed_at":"2026-09-25T00:00:00+00:00","tools":{"list_domains_s1":{"status":"PASS"}}})
    s=answer_expected(s,"domain_binding",{"mode":"UNRESOLVED"})
    s=answer_expected(s,"workflow_model","REGULATORY_AFRICAFUNDS_GOVERNED_FLOW")
    if s["next_request"]["field"]!="setup_approved": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: setup approval")
    s=answer_expected(s,"setup_approved",True)
    if s["next_request"]["kind"]!="APPLY_BASELINE": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: apply missing")
    s=complete_baseline(s,"b"*40,"LOCAL-000001-S1")
    if s["status"]!="LOCAL_HANDOFF_READY": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: first handoff")
    persisted=decode_state(encode_state(s))
    if persisted["handoff"]["setup"]["workflow_model"]!="REGULATORY_AFRICAFUNDS_GOVERNED_FLOW":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: setup persistence")

    n=new_request("LOCAL-2","owner/repo","c"*40,False,"later agent")
    for field,value in [
      ("agent_identity","Claude"),("provider","CLAUDE"),("connection_intent","CODE_CHANGE"),
      ("local_entry_action","CONTINUE_GOVERNED_WORK"),("requested_objective","Continue current work")
    ]: n=answer_expected(n,field,value)
    if n["status"]!="LOCAL_HANDOFF_READY": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: normal handoff")

    wf=(ROOT/".github/workflows/governed-local-entry.yml").read_text(encoding="utf-8")
    for fragment in ["governed_local_start","GOVERNED_MCP_AUTH_TOKEN","mcp_repository_discovery.py","local_entry_apply_baseline.py"]:
        if fragment not in wf: raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: workflow contract "+fragment)
    print("LOCAL_GOVERNED_ENTRY_SELFTEST_PASS")

if __name__=="__main__": main()
