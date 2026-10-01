#!/usr/bin/env python3
from __future__ import annotations
import copy
from pathlib import Path
from local_governed_entry import answer, both_discovery_needs_refresh, complete_baseline, decode_state, encode_state, mark_credentials_verified, new_request, observed_domains_for_server, reconcile_both_smart_routing, reconcile_legacy_discovery_authority, reconcile_setup_question_order, record_mcp_discovery, record_mcp_discovery_failure, require_mcp_discovery_refresh

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
    if s["next_request"]["kind"]!="PLAN_APPROVAL" or s["next_request"].get("field")!="mcp_discovery_approved":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: discovery approval gate")
    if s.get("credentials_verified") is not False:
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: configuration must not verify credentials or execute discovery")
    s=answer_expected(s,"mcp_discovery_approved",True)
    if s["next_request"]["kind"]!="CREDENTIAL_GATE": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: credential gate")
    s=mark_credentials_verified(s)
    if s["next_request"]["kind"]!="MCP_DISCOVERY": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: discovery gate")
    s=record_mcp_discovery(s,{
      "observed_at":"2026-09-25T00:00:00+00:00",
      "tools":{
        "list_domains_s1":{
          "status":"PASS",
          "result":{"result":{"content":[{"type":"text","text":"/var/www/vhosts/example.com/app.example.com\n/var/www/vhosts/system/api.example.com"}]}}
        }
      }
    })
    if s["next_request"]["field"]!="production_server_selection":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: fresh project must choose production server before domain")
    if "S1" not in s["next_request"].get("choices",[]):
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: observed S1 candidate missing")
    s=answer_expected(s,"production_server_selection","S1")
    if s["next_request"]["field"]!="domain_binding" or s["next_request"].get("selected_server")!="S1":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: domain question must be scoped to selected server")
    if "example.com" not in s["next_request"].get("observed_domains",[]):
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: selected-server domain inventory not reused")
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
    if ssh["next_request"]["kind"]!="PLAN_APPROVAL" or ssh["next_request"].get("field")!="mcp_discovery_approved":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: SSH configuration must stop at discovery approval")
    ssh=answer_expected(ssh,"mcp_discovery_approved",True)
    if ssh["next_request"]["kind"]!="MCP_DISCOVERY":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: approved SSH-only discovery must not require persistent credentials")
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
    if both["next_request"]["kind"]!="PLAN_APPROVAL" or both["next_request"].get("field")!="mcp_discovery_approved":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: BOTH configuration must stop at discovery approval")
    discovery_plan=both["next_request"].get("plan") or {}
    routing=discovery_plan.get("routing") or {}
    if discovery_plan.get("mutation_authority") is not False or discovery_plan.get("transport")!="BOTH":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: discovery plan must be read-only and preserve transport")
    if discovery_plan.get("configured_transports")!=["DIRECT_MCP_TOKEN","SSH"] or routing.get("mode")!="DUAL_READY_SMART_ROUTING":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: BOTH must configure two independent routes")
    if routing.get("simultaneous_execution_required") is not False or routing.get("one_successful_route_satisfies_current_discovery") is not True:
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: BOTH must not require coupled execution")
    legacy=copy.deepcopy(both)
    legacy["status"]="MCP_DISCOVERY_FAILED_RETRYABLE"
    legacy["phase"]="MCP_DISCOVERY"
    legacy["next_request"]={"kind":"MCP_DISCOVERY","id":"MCP_DISCOVERY","text":"legacy"}
    legacy["mcp_discovery"]={"status":"ERROR","failure_code":"LEGACY_PREAPPROVAL_NETWORK_ATTEMPT"}
    legacy=reconcile_legacy_discovery_authority(legacy)
    if legacy["next_request"]["kind"]!="PLAN_APPROVAL" or legacy["next_request"].get("field")!="mcp_discovery_approved":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: legacy discovery state must migrate back to explicit approval")
    if legacy.get("mcp_discovery") is not None or not legacy.get("mcp_discovery_history"):
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: legacy discovery evidence must be archived, not treated as current authority")
    both=answer_expected(both,"mcp_discovery_approved",True)
    if both["next_request"]["kind"]!="MCP_DISCOVERY":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: approved BOTH must allow secretless SSH discovery fallback")
    if both.get("credentials_verified") is not True:
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: BOTH mandatory credential gate should be satisfied by secretless fallback")
    endpoint_failed=record_mcp_discovery_failure(both,{
      "status":"ERROR",
      "failure_code":"HTTP Error 404: Not Found",
      "transport":"BOTH",
      "endpoint":"https://mcp.example.test/",
      "retryable":True
    })
    if endpoint_failed["status"]!="WAITING_FOR_SETUP_ANSWER" or endpoint_failed["next_request"].get("field")!="mcp_endpoint":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: HTTP 404 must reopen MCP endpoint correction")
    endpoint_failed=answer_expected(endpoint_failed,"mcp_endpoint","https://mcp.example.test/mcp")
    if endpoint_failed["next_request"]["kind"]!="PLAN_APPROVAL" or endpoint_failed["next_request"].get("field")!="mcp_discovery_approved" or endpoint_failed.get("mcp_discovery") is not None:
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: corrected MCP endpoint must require renewed discovery approval")
    if endpoint_failed.get("hold_reason") is not None:
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: corrected MCP endpoint must clear hold")
    endpoint_failed=answer_expected(endpoint_failed,"mcp_discovery_approved",True)
    if endpoint_failed["next_request"]["kind"]!="MCP_DISCOVERY":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: reapproved corrected endpoint must return to discovery")
    endpoint_history=endpoint_failed.get("mcp_discovery_history") or []
    if len(endpoint_history)!=1 or endpoint_history[0]["evidence"].get("failure_code")!="HTTP Error 404: Not Found":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: endpoint correction must archive failed discovery evidence")
    if endpoint_failed["answers"]["mcp_endpoint"]!="https://mcp.example.test/mcp":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: corrected MCP endpoint not persisted")

    ssh_profile_failed=record_mcp_discovery_failure(both,{
      "status":"ERROR",
      "failure_code":"SSH_PROFILE_MISMATCH",
      "transport":"BOTH",
      "endpoint":"https://mcp.example.test/mcp",
      "observed_ssh_profile":{"host":"212.227.212.33","port":22,"user":"root","source":"SIGNED_MCP_SSH_BROKER_RESPONSE"},
      "direct_mcp":{"status":"PASS"},
      "retryable":True
    })
    if ssh_profile_failed["status"]!="WAITING_FOR_SETUP_ANSWER" or ssh_profile_failed["phase"]!="Q_SSH_PROFILE_RECOVERY":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: SSH profile mismatch must reopen profile recovery")
    request=ssh_profile_failed["next_request"]
    if request.get("field")!="ssh_connection_profile" or request.get("observed_ssh_profile",{}).get("host")!="212.227.212.33":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: signed broker SSH profile evidence must be exposed for recovery")
    ssh_profile_failed=answer_expected(ssh_profile_failed,"ssh_connection_profile",{"host":"212.227.212.33","port":22,"user":"root"})
    if ssh_profile_failed["next_request"]["kind"]!="PLAN_APPROVAL" or ssh_profile_failed["next_request"].get("field")!="mcp_discovery_approved":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: corrected SSH profile must require renewed discovery approval")
    if ssh_profile_failed.get("mcp_discovery") is not None or ssh_profile_failed.get("hold_reason") is not None:
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: SSH profile correction must clear current failed discovery")
    profile_history=ssh_profile_failed.get("mcp_discovery_history") or []
    if len(profile_history)!=1 or profile_history[0].get("reason")!="SSH_PROFILE_CORRECTION_AFTER_SIGNED_BROKER_MISMATCH":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: SSH profile correction must archive mismatch evidence")
    if ssh_profile_failed["answers"].get("mcp_discovery_approved") is not None:
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: material SSH profile correction must invalidate prior discovery approval")
    corrected_plan=ssh_profile_failed["next_request"].get("plan") or {}
    if corrected_plan.get("ssh_connection_profile")!={"host":"212.227.212.33","port":22,"user":"root"}:
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: corrected SSH profile must flow into renewed discovery plan")

    legacy_both=copy.deepcopy(ssh_profile_failed)
    legacy_both["answers"].pop("mcp_discovery_approved",None)
    legacy_both["mcp_discovery"]=None
    legacy_both["status"]="WAITING_FOR_DISCOVERY_APPROVAL"
    legacy_both["phase"]="MCP_DISCOVERY_APPROVAL"
    legacy_both["next_request"]={"kind":"PLAN_APPROVAL","id":"Q_MCP_DISCOVERY_APPROVAL","field":"mcp_discovery_approved"}
    legacy_both["mcp_discovery_history"]=[{
      "reason":"SSH_PROFILE_CORRECTION_AFTER_SIGNED_BROKER_MISMATCH",
      "evidence":{
        "status":"ERROR",
        "failure_code":"SSH_PROFILE_MISMATCH",
        "transport":"BOTH",
        "endpoint":"https://mcp.example.test/mcp",
        "observed_at":"2026-09-30T00:00:00+00:00",
        "direct_mcp":{"status":"PASS","tools":{"ping":{"status":"PASS"},"get_project_context":{"status":"PASS"}}},
        "observed_ssh_profile":{"host":"212.227.212.33","port":22,"user":"root","source":"SIGNED_MCP_SSH_BROKER_RESPONSE"}
      }
    }]
    migrated=reconcile_both_smart_routing(legacy_both)
    if migrated.get("mcp_discovery",{}).get("selected_transport")!="DIRECT_MCP_TOKEN":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: authorized legacy direct PASS must migrate as current smart route")
    if migrated.get("mcp_discovery",{}).get("alternate_transport_status")!="CONFIGURED_NOT_ATTESTED":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: corrected SSH route must remain alternate and independently attestable")
    if (migrated.get("next_request") or {}).get("field")!="production_server_selection":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: fresh smart-routing migration must return to production server choice before domain")

    failed=record_mcp_discovery_failure(both,{
      "status":"ERROR",
      "failure_code":"SSH_CERTIFICATE_BROKER_FORBIDDEN",
      "transport":"BOTH",
      "retryable":True
    })
    if failed["status"]!="MCP_DISCOVERY_FAILED_RETRYABLE" or failed["next_request"]["kind"]!="MCP_DISCOVERY":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: retryable discovery failure state")
    if failed["mcp_discovery"]["failure_code"]!="SSH_CERTIFICATE_BROKER_FORBIDDEN":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: failure evidence lost")
    recovered=record_mcp_discovery(failed,{
      "status":"PASS",
      "degraded":False,
      "transport":"BOTH",
      "routing_mode":"DUAL_READY_SMART_ROUTING",
      "selected_transport":"SSH",
      "fallback_used":True,
      "simultaneous_execution_required":False,
      "direct_mcp":{"status":"UNAVAILABLE_CREDENTIAL"},
      "ssh_certificate":{"status":"PASS"}
    })
    if recovered["next_request"]["field"]!="production_server_selection":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: discovery retry did not resume at production server choice")
    recovered=answer_expected(recovered,"production_server_selection","DECIDE_LATER")
    recovered=answer_expected(recovered,"domain_binding",{"mode":"UNRESOLVED"})
    recovered=answer_expected(recovered,"workflow_model","STANDARD_GOVERNED_FLOW")
    if recovered["next_request"]["field"]!="setup_approved":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: expected setup approval after successful smart fallback")
    if both_discovery_needs_refresh(recovered,True):
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: alternate direct availability must not force coupled rediscovery")
    setup_routing=(recovered.get("setup_package") or {}).get("mcp",{}).get("routing_strategy") or {}
    if setup_routing.get("mode")!="DUAL_READY_SMART_ROUTING" or setup_routing.get("simultaneous_execution_required") is not False:
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: setup package lost smart routing")

    ekyc_like=copy.deepcopy(migrated)
    ekyc_like["answers"].pop("production_server_selection",None)
    ekyc_like["phase"]="Q_DOMAIN_BINDING"
    ekyc_like["status"]="WAITING_FOR_SETUP_ANSWER"
    ekyc_like["next_request"]={"kind":"QUESTION","id":"Q_DOMAIN_BINDING","field":"domain_binding"}
    reordered=reconcile_setup_question_order(ekyc_like)
    if reordered["phase"]!="Q_PRODUCTION_SERVER_SELECTION":
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: Ekyc-like legacy domain gate not reordered")
    if reordered["next_request"].get("execution_authority_granted") is not False:
        raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: production server decision granted execution authority")

    n=new_request("LOCAL-2","owner/repo","c"*40,False,"later agent")
    for field,value in [
      ("agent_identity","Claude"),("provider","CLAUDE"),("connection_intent","CODE_CHANGE"),
      ("local_entry_action","CONTINUE_GOVERNED_WORK"),("requested_objective","Continue current work")
    ]: n=answer_expected(n,field,value)
    if n["status"]!="LOCAL_HANDOFF_READY": raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: normal handoff")

    wf=(ROOT/".github/workflows/governed-local-entry.yml").read_text(encoding="utf-8")
    if (ROOT/".template-source").exists():
        control_plane_wf=(ROOT/".github/workflows/governed-control-plane.yml").read_text(encoding="utf-8")
        local_start_token_block=control_plane_wf.split("- name: Mint target-owner token for machine local start",1)[1].split("- name: Dispatch governed machine local start",1)[0]
        if "permission-contents: write" not in local_start_token_block:
            raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: machine local start token must have Contents write for repository_dispatch")
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
                     'SSH_BROKER_BASE_URL = "https://mcp.wealthtechinnovations.com"',"SSH_DISCOVERY_REQUIRED_PROBE_FAILED",
                     "SSH_CERTIFICATE_BROKER_FORBIDDEN","record_mcp_discovery_failure"]:
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
        'dispatch_machine_command(e)',
        'LOCAL_ENTRY_ISSUE_CREATED_AND_INITIALIZED',
        'invalid source repository',
        'sender must be a GitHub App bot',
        'elif gate=="MCP_DISCOVERY"',
        'MCP discovery retry requested',
        'both_discovery_needs_refresh',
        'DIRECT_CREDENTIAL_BECAME_AVAILABLE',
        'BOTH discovery refresh required'
    ]:
        if fragment not in bridge:
            raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: local entry actor authorization "+fragment)
    for fragment in ['"DISCOVERY_PARTIAL"','binding["discovery_status"]=discovery_status or "NOT_RUN"']:
        if fragment not in apply:
            raise SystemExit("LOCAL_ENTRY_SELFTEST_FAILED: discovery status preservation "+fragment)
    print("LOCAL_GOVERNED_ENTRY_SELFTEST_PASS")

if __name__=="__main__": main()
