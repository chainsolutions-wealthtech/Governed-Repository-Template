#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from local_governed_entry import complete_baseline
from local_entry_issue_bridge import api, extract_state, persist, render

ROOT=Path(__file__).resolve().parents[1]

def readj(rel):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))
def writej(rel,v):
    p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def run(*args,check=True):
    return subprocess.run(list(args),cwd=ROOT,text=True,capture_output=True,check=check)
def bullets(v):
    return "\n".join("- "+str(x) for x in v) if v else "- None declared"

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--issue-number",type=int,required=True);args=ap.parse_args()
    profile=readj(".governance/profile.json");repo=profile["repository"];branch=profile["canonical_branch"]
    issue=api("GET",f"/repos/{repo}/issues/{args.issue_number}");state=extract_state(issue.get("body"))
    if (state.get("next_request") or {}).get("kind")!="APPLY_BASELINE":
        raise SystemExit("LOCAL_BASELINE_SKIPPED")
    expected=state["expected_head_sha"]
    run("git","fetch","origin",branch);remote=run("git","rev-parse","FETCH_HEAD").stdout.strip()
    if remote!=expected:
        api("POST",f"/repos/{repo}/issues/{args.issue_number}/comments",{"body":f"### LOCAL HEAD_MOVED\n\nExpected {expected}, remote {remote}. Baseline write stopped; reconcile then retry /local-execute."})
        raise SystemExit(3)

    a=state["answers"];now=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    session_id=f"LOCAL-{args.issue_number:06d}-S1";scope=a["project_scope"]

    (ROOT/"PROJECT_CONTEXT.md").write_text(
        f"# PROJECT_CONTEXT\n\n- Repository: {repo}\n- Project: {profile['project_name']}\n- Owner: {profile['owner']}\n- Canonical branch: {branch}\n- Baseline subject HEAD: {expected}\n"
        f"- First governed agent: {a['agent_identity']} via {a['provider']}\n\n## Mission\n\n{a['project_mission']}\n\n## Scope\n\n### In scope\n{bullets(scope['in_scope'])}\n\n"
        f"### Out of scope\n{bullets(scope['out_of_scope'])}\n\n## Architecture / stack\n\nProfile selection: {a['project_profile']}. See docs/ARCHITECTURE.md.\n\n"
        f"## Infrastructure / deployment\n\nDeclared baseline status: {a['infrastructure_status']}.\n\n## External systems\n\n{bullets(a['external_systems'])}\n\n"
        f"## Initial constraints\n\n{bullets(a['constraints'])}\n\n## Governed repository setup\n\nWorkflow model: {a.get('workflow_model') or 'NOT_SELECTED'}\nMCP linked: {a.get('link_mcp_server') is True}\nDomain binding: {json.dumps(a.get('domain_binding'),ensure_ascii=False)}\n",encoding="utf-8")

    (ROOT/"docs/ARCHITECTURE.md").write_text(
        f"# ARCHITECTURE\n\n## Baseline\n\n- Subject HEAD: {expected}\n- Status: {a['architecture_status']}\n- Project profile: {a['project_profile']}\n\n"
        f"## Current architecture\n\n{a['architecture_notes']}\n\n## Required future detail\n\n- system context\n- components/modules\n- data stores\n- external integrations\n"
        "- trust boundaries\n- deployment topology\n- observability\n- rollback/recovery\n- architectural constraints\n\n"
        "No planned profile is evidence of implementation. Architecture changes that invalidate a durable decision require an ADR.\n",encoding="utf-8")

    pp=readj(".governance/project-profile.json")
    if a["project_profile"]=="DEFER":
        pp["selected_profile"]=None;pp["selection_status"]="DISCOVERY_REQUIRED"
    else:
        pp["selected_profile"]=a["project_profile"];pp["selection_status"]="SELECTED"
    writej(".governance/project-profile.json",pp)

    infra=readj(".governance/infrastructure-intent.json")
    infra["baseline_declaration"]=a["infrastructure_status"]
    if a["infrastructure_status"]=="NO_INFRASTRUCTURE_YET":
        infra["status"]="PLANNED_NOT_PROVISIONED"
        for k in ["server_status","domain_status","directory_status"]: infra["deployment_target"][k]="NOT_PROVISIONED"
    elif a["infrastructure_status"]=="UNKNOWN_TO_DISCOVER":
        infra["status"]="PLANNED_NOT_PROVISIONED"
        for k in ["server_status","domain_status","directory_status"]: infra["deployment_target"][k]="DISCOVERY_REQUIRED"
    else:
        infra["status"]="DISCOVERY_REQUIRED"
        for k in ["server_status","domain_status","directory_status"]: infra["deployment_target"][k]="DISCOVERY_REQUIRED"
    setup=state.get("setup_package") or {}
    workflow=readj(".governance/workflow-model.json")
    workflow["repository"]=repo
    workflow["selected_model"]=a.get("workflow_model")
    writej(".governance/workflow-model.json",workflow)

    access=readj(".governance/access-plan.json")
    access["repository"]=repo
    access["status"]="CONFIGURED"
    if a.get("link_mcp_server"):
        access["mcp"]["project_write"]=[]
        access["mcp"]["write_activation"]="REQUIRES_MCP_PROJECT_REGISTRATION_AND_EXPLICIT_AUTHORITY"
    writej(".governance/access-plan.json",access)

    binding=readj(".governance/mcp-binding.json")
    binding["repository"]=repo
    binding["linked"]=a.get("link_mcp_server") is True
    if binding["linked"]:
        binding["status"]="DISCOVERED_READONLY" if state.get("mcp_discovery") else "ACCESS_CONFIGURED"
        binding["transport"]=a.get("mcp_transport")
        binding["endpoint"]=a.get("mcp_endpoint")
        binding["ssh_connection_profile"]=a.get("ssh_connection_profile")
        binding["credential_names"]=[x["name"] for x in setup.get("mcp",{}).get("credential_requirements",[])]
        binding["discovery_status"]="PASS" if state.get("mcp_discovery") else "NOT_RUN"
        binding["discovery_observed_at"]=(state.get("mcp_discovery") or {}).get("observed_at")
        binding["domain_strategy"]=a.get("domain_strategy")
        binding["domain_binding"]=a.get("domain_binding")
        binding["project_registration_status"]="UNVERIFIED"
        binding["write_tools_status"]="DISABLED_UNTIL_REGISTERED_AND_AUTHORIZED"
        infra["server_access"]["preferred"]="DIRECT_MCP" if a.get("mcp_transport") in {"DIRECT_MCP_TOKEN","BOTH"} else "SSH"
        infra["server_access"]["fallback"]="SSH" if a.get("mcp_transport") in {"BOTH","DIRECT_MCP_TOKEN"} else None
        infra["server_access"]["status"]="DISCOVERED_READONLY" if state.get("mcp_discovery") else "ACCESS_CONFIGURED"
        if a.get("domain_binding"):
            infra["deployment_target"]["domain"]=a["domain_binding"].get("domain")
            infra["deployment_target"]["domain_status"]="OBSERVED_EXISTING" if a["domain_binding"].get("mode")=="EXISTING" else ("PROVISIONING_REQUIRED" if a["domain_binding"].get("mode")=="CREATE_NEW" else "DISCOVERY_REQUIRED")
    writej(".governance/mcp-binding.json",binding)
    writej(".governance/infrastructure-intent.json",infra)

    local=readj(".governance/local-entry/state.json")
    local.update({"status":"PROJECT_BASELINE_READY","first_agent_completed":True,"first_agent_session_id":session_id,
                  "baseline_subject_head":expected,"baseline_completed_at":now,"last_local_entry_issue":args.issue_number})
    writej(".governance/local-entry/state.json",local)
    writej(".governance/local-entry/receipt.json",{"schema_version":"1.0.0","repository":repo,"request_id":state["request_id"],
        "session_id":session_id,"baseline_subject_head":expected,"project_profile_status":pp["selection_status"],
        "next_action":"EXECUTE_FIRST_PROJECT_WORK_ITEM","completed_at":now})

    sessions=readj(".governance/sessions/sessions.json")
    sessions["revision"]=int(sessions.get("revision",0))+1
    sessions.setdefault("sessions",[]).append({"session_id":session_id,"agent_identity":a["agent_identity"],"provider":a["provider"],
      "provider_conversation_ref":None,"provider_conversation_ref_provenance":"UNAVAILABLE","connection_ref":f"github-issue:{args.issue_number}",
      "repository":repo,"starting_head_sha":expected,"last_observed_head_sha":expected,"status":"ACTIVE","created_at":now,"last_seen_at":now,
      "connection_intent":a["connection_intent"],"connection_intent_provenance":"PROVIDED_BY_CLIENT",
      "entry_action":"CONTINUE_GOVERNED_WORK","entry_action_provenance":"PROVIDED_BY_CLIENT"})
    writej(".governance/sessions/sessions.json",sessions)

    work=readj(".governance/work/work-items.json");items=work.setdefault("items",[])
    for item in items:
        if item.get("work_item_id")=="WORK-DISCOVER-001": item["status"]="DONE"
    if not any(x.get("work_item_id")=="WORK-PROJECT-001" for x in items):
        items.append({"work_item_id":"WORK-PROJECT-001","title":a["first_work_objective"],"status":"READY","priority":800,
                      "sequence":3,"dependencies":["WORK-DISCOVER-001"],"collision_domains":["project-work"],
                      "next_action":"EXECUTE_FIRST_PROJECT_WORK_ITEM"})
    work["revision"]=int(work.get("revision",0))+1;writej(".governance/work/work-items.json",work)

    mem=readj(".governance/canonical-memory/current.json")
    mem.update({"observed_head_sha":expected,"current_checkpoint":"first-agent-baseline","current_handoff":None,
                "next_action":"EXECUTE_FIRST_PROJECT_WORK_ITEM","freshness":"BASELINE_READY","blockers":[]})
    mem["canonical_revision"]=int(mem.get("canonical_revision",0))+1;mem["work_revision"]=int(mem.get("work_revision",0))+1
    writej(".governance/canonical-memory/current.json",mem)

    (ROOT/"STATUS.md").write_text(
        f"# STATUS — État courant\n\n> State: PROJECT_BASELINE_READY\n\n- Repository: {repo}\n- Branch: {branch}\n- Baseline subject HEAD: {expected}\n"
        f"- First governed session: {session_id}\n- Governance validation: PASS_PENDING_COMMIT\n- Next action: EXECUTE_FIRST_PROJECT_WORK_ITEM\n\n"
        f"First project objective: {a['first_work_objective']}\n",encoding="utf-8")
    (ROOT/"NEXT_ACTION.md").write_text(
        "# NEXT_ACTION — Point de reprise unique\n\nNEXT_ACTION = EXECUTE_FIRST_PROJECT_WORK_ITEM\nSTATE = READY\n\n"
        f"## Work item\n\nWORK-PROJECT-001 — {a['first_work_objective']}\n\nBefore write: reobserve online HEAD and reconcile if moved.\n",encoding="utf-8")
    (ROOT/"CURRENT_ITERATION.md").write_text(
        f"# CURRENT_ITERATION — LOOP-PROJECT-001\n\n## Objective\n\n{a['first_work_objective']}\n\n## Entry criteria\n\n"
        "- first-agent baseline committed\n- governance validation green\n- online HEAD reobserved before write\n\n## Exit criteria\n\n"
        "- project-specific acceptance criteria satisfied\n- regression checks green\n- durable state synchronized\n",encoding="utf-8")
    (ROOT/"HANDOFF.md").write_text(
        f"# HANDOFF — Reprise inter-agent\n\n- Repository: {repo}\n- Branch: {branch}\n- Baseline subject HEAD: {expected}\n- Active session: {session_id}\n"
        "- Current work item: WORK-PROJECT-001\n- Next action: EXECUTE_FIRST_PROJECT_WORK_ITEM\n\nReobserve remote HEAD before any write.\n",encoding="utf-8")
    (ROOT/"LOOP_STATE.md").write_text(
        json.dumps({"loop_id":"LOOP-PROJECT-001","state":"IN_PROGRESS","phase":"PLAN","repository":repo,"canonical_branch":branch,
                    "baseline_head":expected,"next_action":"EXECUTE_FIRST_PROJECT_WORK_ITEM","last_verification":"FIRST_AGENT_BASELINE_APPROVED"},indent=2)+"\n",encoding="utf-8")

    with (ROOT/"SUIVI.md").open("a",encoding="utf-8") as h:
        h.write(f"\n## {now} — First-agent project baseline\n\n- Session: {session_id}\n- Baseline subject HEAD: {expected}\n- Profile: {a['project_profile']}\n- Next action: EXECUTE_FIRST_PROJECT_WORK_ITEM\n")
    with (ROOT/"WORK_LOG.md").open("a",encoding="utf-8") as h:
        h.write(f"\n## {now} — FIRST_AGENT_BASELINE\n\n- Result: PASS_PENDING_COMMIT\n- Session: {session_id}\n- Subject HEAD: {expected}\n")

    cp=run(sys.executable,"scripts/validate_governance.py",check=False)
    if cp.returncode!=0:
        api("POST",f"/repos/{repo}/issues/{args.issue_number}/comments",{"body":"### Local baseline validation failed\n\n"+cp.stdout+cp.stderr})
        raise SystemExit(cp.returncode)

    run("git","config","user.name","github-actions[bot]");run("git","config","user.email","41898282+github-actions[bot]@users.noreply.github.com")
    run("git","add","-A");run("git","commit","-m","governance: establish first-agent project baseline")
    new_head=run("git","rev-parse","HEAD").stdout.strip()
    run("git","fetch","origin",branch);remote2=run("git","rev-parse","FETCH_HEAD").stdout.strip()
    if remote2!=expected: raise SystemExit("HEAD_MOVED_AFTER_BASELINE_BUILD")
    run("git","push","origin",f"HEAD:{branch}")

    issue2=api("GET",f"/repos/{repo}/issues/{args.issue_number}");state2=extract_state(issue2.get("body"))
    state2=complete_baseline(state2,new_head,session_id);persist(args.issue_number,issue2.get("body"),state2)
    api("POST",f"/repos/{repo}/issues/{args.issue_number}/comments",{"body":render(state2)})

if __name__=="__main__": main()
