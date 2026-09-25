#!/usr/bin/env python3
from __future__ import annotations
import argparse, base64, json, os, urllib.error, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CENTRAL="chainsolutions-wealthtech/Governed-Repository-Template"

def gh(token,method,path,payload=None,allow_404=False):
    req=urllib.request.Request("https://api.github.com"+path,method=method,
      headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"governed-local-entry-upgrader"},
      data=json.dumps(payload).encode() if payload is not None else None)
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            raw=r.read().decode();return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body=exc.read().decode(errors="replace")
        if allow_404 and exc.code==404:return None
        raise RuntimeError(f"GitHub API {method} {path} failed: {exc.code} {body}") from exc

def target_text(token,target,path):
    obj=gh(token,"GET",f"/repos/{target}/contents/{path}",allow_404=True)
    if not obj:return None
    return base64.b64decode(obj["content"]).decode("utf-8")

def append_once(text,marker,addition):
    if marker in text:return text
    return text.rstrip()+"\n\n"+addition.strip()+"\n"

def main():
    p=argparse.ArgumentParser();p.add_argument("--target-repository",required=True);p.add_argument("--expected-head",required=True);p.add_argument("--issue-number",type=int)
    a=p.parse_args();target=a.target_repository;owner,name=target.split("/",1)
    token=os.environ["GOVERNED_TARGET_TOKEN"]
    info=gh(token,"GET",f"/repos/{target}");branch=info.get("default_branch") or "main"
    ref=gh(token,"GET",f"/repos/{target}/git/ref/heads/{branch}");head=ref["object"]["sha"]
    if head!=a.expected_head: raise SystemExit(f"HEAD_MOVED: expected={a.expected_head} remote={head}")
    commit=gh(token,"GET",f"/repos/{target}/git/commits/{head}");base_tree=commit["tree"]["sha"]

    static_paths=[
      ".governance/local-entry-policy.json","schemas/local-entry-request.schema.json","schemas/local-entry-receipt.schema.json",
      "schemas/infrastructure-intent.schema.json","docs/LOCAL_GOVERNED_ENTRY.md","scripts/local_governed_entry.py",
      "scripts/local_entry_issue_bridge.py","scripts/local_entry_apply_baseline.py","scripts/test_local_governed_entry.py",
      "scripts/validate_governance.py","scripts/adopt_existing_repository.py",".github/workflows/governed-local-entry.yml",
      ".github/ISSUE_TEMPLATE/governed-local-entry.yml",".github/workflows/governance-ci.yml",
      ".github/workflows/governance-auto-bootstrap.yml",".governance/TEMPLATE_MANIFEST.json",
      ".governance/repository-creation-executor.json"
    ]
    updates={p:(ROOT/p).read_text(encoding="utf-8") for p in static_paths}

    local=json.loads((ROOT/".governance/local-entry/state.json").read_text(encoding="utf-8"))
    local.update({"repository":target,"status":"WAITING_FOR_FIRST_AGENT","first_agent_completed":False,
      "first_agent_session_id":None,"baseline_subject_head":None,"baseline_completed_at":None,"last_local_entry_issue":None})
    updates[".governance/local-entry/state.json"]=json.dumps(local,ensure_ascii=False,indent=2)+"\n"

    profile=json.loads(target_text(token,target,".governance/profile.json"))
    source_profile=json.loads((ROOT/".governance/profile.json").read_text(encoding="utf-8"))
    for k in ["local_control_plane","first_agent_baseline","local_entry_head_guard","local_entry_state_external_to_canonical_truth"]:
        profile.setdefault("policies",{})[k]=source_profile["policies"][k]
    for k in ["local_governed_entry","first_agent_baseline_workflow","subsequent_agent_local_routing"]:
        profile.setdefault("automation",{})[k]=source_profile["automation"][k]
    updates[".governance/profile.json"]=json.dumps(profile,ensure_ascii=False,indent=2)+"\n"

    docs={
      "00_START_HERE.md":("## Local governed entry","## Local governed entry\n\nDans un repository cible initialisé, le point d'entrée préféré d'un agent est le workflow local décrit dans docs/LOCAL_GOVERNED_ENTRY.md. Le premier agent après bootstrap doit terminer FIRST_AGENT_BOOTSTRAP avant tout travail fonctionnel mutable."),
      "AGENTS.md":("## Repository-local control plane","## Repository-local control plane\n\nAfter central handoff, start local work through a [Governed Local Entry] issue or repository_dispatch: governed_local_start. The first agent is routed through FIRST_AGENT_BOOTSTRAP; later agents are routed through NORMAL_GOVERNED_ENTRY. Do not bypass a pending first-agent baseline."),
      "docs/AUTOMATION.md":("## Repository-local agent entry","## Repository-local agent entry\n\nInitialized target repositories include .github/workflows/governed-local-entry.yml. It accepts a local-entry issue or repository_dispatch: governed_local_start, persists one-question-at-a-time state in the issue, and applies the approved first-agent baseline under an exact-HEAD guard."),
      "SOURCE_OF_TRUTH.md":("## Local entry operational state","## Local entry operational state\n\nA [Governed Local Entry] issue is orchestration state, not canonical project truth. Once the approved first-agent baseline is committed, the versioned repository files and machine projections become authoritative according to the normal hierarchy.")
    }
    for path,(marker,addition) in docs.items():
        updates[path]=append_once(target_text(token,target,path) or "",marker,addition)

    change=target_text(token,target,"CHANGELOG.md") or "# CHANGELOG\n"
    updates["CHANGELOG.md"]=append_once(change,"## Governance Automation V2.4.0","## Governance Automation V2.4.0\n\n- Added repository-local governed agent entry point.\n- Added FIRST_AGENT_BOOTSTRAP guided baseline.\n- Added NORMAL_GOVERNED_ENTRY routing for subsequent agents.\n- Added exact-HEAD guarded automatic baseline commit.")

    entries=[]
    for path,text in updates.items():
        blob=gh(token,"POST",f"/repos/{target}/git/blobs",{"content":text,"encoding":"utf-8"})
        entries.append({"path":path,"mode":"100644","type":"blob","sha":blob["sha"]})
    tree=gh(token,"POST",f"/repos/{target}/git/trees",{"base_tree":base_tree,"tree":entries})
    new_commit=gh(token,"POST",f"/repos/{target}/git/commits",{"message":"governance: upgrade repository-local agent entry to v2.4","tree":tree["sha"],"parents":[head]})
    gh(token,"PATCH",f"/repos/{target}/git/refs/heads/{branch}",{"sha":new_commit["sha"],"force":False})

    issue=a.issue_number
    central_token=os.environ.get("GITHUB_TOKEN")
    if issue and central_token:
        gh(central_token,"POST",f"/repos/{CENTRAL}/issues/{issue}/comments",{"body":f"### Local entry upgrade applied\n\nTarget: {target}\nPrevious HEAD: {head}\nUpgrade commit: {new_commit['sha']}\nVersion: 2.4.0"})
    print(json.dumps({"status":"LOCAL_ENTRY_UPGRADE_APPLIED","target":target,"old_head":head,"new_head":new_commit["sha"]}))

if __name__=="__main__":main()
