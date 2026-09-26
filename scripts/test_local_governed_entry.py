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

    ssh=first_base()
    ssh=answer_expected(ssh,"baseline_approved",True)
    ssh=answer_expected(ssh,"setup_repository_now",True)
    ssh=answer_expected(ssh,"link_mcp_server",True)
    ssh=answer_expected(ssh,"mcp_transport","SSH")
    ssh=answer_expected(ssh,"mcp_endpoint","https://mcp.example.test/mcp")
    ssh=answer_expected(ssh,"ssh_connection_profile",{"host":"212.227.212.33","user":"root","port":22})
    ssh=answer_expected(ssh,"mcp_discovery_scope","FULL_GOVERNED_MAPPING")
    ssh=answer_expected(ssh,"domain_strategy","DISCOVER_EXISTING_THEN_PROPOSE")
    ssh=answer_expected(ssh,"runtime_mutation_policy","EXPLICIT_APPROVAL_FOR_SCOPED_WRITE")
    if ssh["next_request"]["kind"]!="MCP_DISCOVERY":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: SSH-only must not require persistent credentials")
    if ssh.get("credentials_verified") is not True:
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: SSH-only credential state")
    if any(item.get("name")=="GOVERNED_MCP_SSH_PRIVATE_KEY" for item in (ssh.get("setup_package") or {}).get("mcp",{}).get("credential_requirements",[])):
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: persistent SSH secret forbidden")

    both=first_base()
    both=answer_expected(both,"baseline_approved",True)
    both=answer_expected(both,"setup_repository_now",True)
    both=answer_expected(both,"link_mcp_server",True)
    both=answer_expected(both,"mcp_transport","BOTH")
    both=answer_expected(both,"mcp_endpoint","https://mcp.example.test/mcp")
    both=answer_expected(both,"ssh_connection_profile",{"host":"212.227.212.33","user":"root","port":22})
    both=answer_expected(both,"mcp_discovery_scope","FULL_GOVERNED_MAPPING")
    both=answer_expected(both,"domain_strategy","DISCOVER_EXISTING_THEN_PROPOSE")
    both=answer_expected(both,"runtime_mutation_policy","EXPLICIT_APPROVAL_FOR_SCOPED_WRITE")
    if both["next_request"]["kind"]!="MCP_DISCOVERY":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: BOTH must allow secretless SSH discovery fallback")
    if both.get("credentials_verified") is not True:
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: BOTH mandatory credential gate should be satisfied by secretless fallback")

    n=new_request("LOCAL-2","owner/repo","c"*40,False,"later agent")
    for field,value in [
      ("agent_identity","Claude"),("provider","CLAUDE"),("connection_intent","CODE_CHANGE"),
      ("local_entry_action","CONTINUE_GOVERNED_WORK"),("requested_objective","Continue current work")
    ]: n=answer_expected(n,field,value)
    if n["status"]!="LOCAL_HANDOFF_READY": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: normal handoff")

    wf=(ROOT/".github/workflows/governed-local-entry.yml").read_text(encoding="utf-8")
    discovery=(ROOT/"scripts/mcp_repository_discovery.py").read_text(encoding="utf-8")
    policy=(ROOT/".governance/mcp-connection-policy.json").read_text(encoding="utf-8")
    bridge=(ROOT/"scripts/local_entry_issue_bridge.py").read_text(encoding="utf-8")
    apply=(ROOT/"scripts/local_entry_apply_baseline.py").read_text(encoding="utf-8")
    for fragment in ["governed_local_start","governed_local_command","GOVERNED_MCP_AUTH_TOKEN","id-token: write","mcp_repository_discovery.py","local_entry_apply_baseline.py"]:
        if fragment not in wf: raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: workflow contract "+fragment)
    if "GOVERNED_MCP_SSH_PRIVATE_KEY" in wf or "GOVERNED_MCP_SSH_PRIVATE_KEY" in policy:
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: persistent repository SSH private key must be absent")
    if 'missing.append("GOVERNED_MCP_URL")' in bridge:
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: captured MCP endpoint must not require duplicate Actions variable")
    for fragment in ["/access/github/repository-ssh/certificate","StrictHostKeyChecking=yes","ssh-keygen","GITHUB_OIDC_EPHEMERAL_SSH_CERTIFICATE",
                     'SSH_BROKER_BASE_URL = "https://mcp.wealthtechinnovations.com"',"SSH_DISCOVERY_REQUIRED_PROBE_FAILED"]:
        if fragment not in discovery:
            raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: ephemeral SSH discovery contract "+fragment)
    for fragment in [
        'TRUSTED_ASSOCIATIONS={"OWNER","MEMBER","COLLABORATOR"}',
        "trusted_actor(event.get(\"comment\") or {})",
        "/collaborators/{encoded}/permission",
        'permission in {"admin","maintain","write"}',
        'MACHINE_SOURCE_REPOSITORY="chainsolutions-wealthtech/Governed-Repository-Template"',
        'sender.get("type")!="Bot"',
        '"LOCAL_STATE_HEAD_MOVED',
        'dispatch_machine_command(e)'
    ]:
        if fragment not in bridge:
            raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: local entry actor authorization "+fragment)
    for fragment in ['"DISCOVERY_PARTIAL"','binding["discovery_status"]=discovery_status or "NOT_RUN"']:
        if fragment not in apply:
            raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: discovery status preservation "+fragment)
    print("LOCAL_GOVERNED_ENTRY_SELFTEST_PASS")

if __name__=="__main__": main()
