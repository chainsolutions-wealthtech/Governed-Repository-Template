#!/usr/bin/env python3
from __future__ import annotations
import json, os, re, subprocess, urllib.error, urllib.request
from pathlib import Path
from local_governed_entry import answer, decode_state, encode_state, mark_credentials_verified, new_request

ROOT=Path(__file__).resolve().parents[1]
TITLE_PREFIX="[Governed Local Entry]"
MARKER_RE=re.compile(r"\n?<!-- GOVERNED_LOCAL_ENTRY_STATE:([A-Za-z0-9_-]+) -->\s*$",re.S)

def api(method,path,payload=None):
    token=os.environ["GITHUB_TOKEN"]
    req=urllib.request.Request(f"https://api.github.com{path}",method=method,
      headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"governed-local-entry"},
      data=json.dumps(payload).encode() if payload is not None else None)
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            raw=r.read().decode();return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body=exc.read().decode(errors="replace");raise RuntimeError(f"GitHub API {method} {path} failed: {exc.code} {body}") from exc

def strip_marker(body): return MARKER_RE.sub("",body or "").rstrip()
def extract_state(body):
    m=MARKER_RE.search(body or "")
    if not m: raise ValueError("local entry state marker missing")
    return decode_state(m.group(1))
def persist(number,body,state):
    clean=strip_marker(body);enc=encode_state(state)
    api("PATCH",f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{number}",{"body":clean+f"\n\n<!-- GOVERNED_LOCAL_ENTRY_STATE:{enc} -->\n"})

def head():
    cp=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,text=True,capture_output=True,check=True);return cp.stdout.strip()
def read_json(rel):return json.loads((ROOT/rel).read_text(encoding="utf-8"))

def first_agent_required():
    local=read_json(".governance/local-entry/state.json")
    memory=read_json(".governance/canonical-memory/current.json")
    return local.get("first_agent_completed") is not True and memory.get("next_action")=="DISCOVER_PROJECT_BASELINE"

def parse_command(body):
    s=(body or "").strip()
    if s=="/local-execute": return ("execute",{})
    if s.startswith("/local-answer"):
        return ("answer",json.loads(s[len("/local-answer"):].strip()))
    return None

def pretty(v):return json.dumps(v,ensure_ascii=False,indent=2)
def render(state):
    n=state.get("next_request") or {}
    lines=[f"## Local Governed Entry — {state['request_id']}","",f"- Mode: `{state['mode']}`",f"- Status: `{state['status']}`",f"- Phase: `{state['phase']}`",f"- Revision: `{state['revision']}`",""]
    if n:
        lines += [f"### {n.get('kind')}","",n.get("text",""),""]
        if n.get("choices") is not None:
            lines += ["Choix autorisés:",""]+[f"- `{json.dumps(x,ensure_ascii=False)}`" for x in n["choices"]]+[""]
        if n.get("kind") in {"QUESTION","PLAN_APPROVAL"}:
            lines += ["Répondre avec:","","```text","/local-answer",pretty({"field":n["field"],"value":"<value>"}),"```",""]
            if n.get("plan") is not None: lines += ["Baseline proposée:","","```json",pretty(n["plan"]),"```",""]
        elif n.get("kind")=="APPLY_BASELINE":
            lines += ["La baseline approuvée va être appliquée automatiquement sous garde du HEAD exact.",""]
        elif n.get("kind")=="HANDOFF":
            lines += ["```json",pretty(n.get("handoff")),"```",""]
    if state.get("status")=="HOLD_FOR_REVIEW": lines += ["### HOLD_FOR_REVIEW","",state.get("hold_reason") or "Blocked"]
    return "\n".join(lines)

def emit_outputs(state,number):
    out=os.environ.get("GITHUB_OUTPUT")
    if not out:return
    kind=(state.get("next_request") or {}).get("kind")
    apply=kind=="APPLY_BASELINE"
    discover=kind=="MCP_DISCOVERY"
    with open(out,"a",encoding="utf-8") as h:
        h.write(f"apply_required={'true' if apply else 'false'}\n")
        h.write(f"mcp_discovery_required={'true' if discover else 'false'}\n")
        h.write(f"issue_number={number}\nexpected_head={state.get('expected_head_sha','')}\n")

def opened(event):
    issue=event["issue"]
    if not str(issue.get("title","")).startswith(TITLE_PREFIX):return
    if (ROOT/".template-source").exists():return
    n=issue["number"];rid=f"LOCAL-{n:06d}"
    s=new_request(rid,os.environ["GITHUB_REPOSITORY"],head(),first_agent_required(),strip_marker(issue.get("body")))
    persist(n,issue.get("body"),s);api("POST",f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{n}/comments",{"body":render(s)});emit_outputs(s,n)

def commented(event):
    issue=event["issue"]
    if not str(issue.get("title","")).startswith(TITLE_PREFIX):return
    cmd=parse_command((event.get("comment") or {}).get("body"))
    if cmd is None:return
    s=extract_state(issue.get("body"));kind,payload=cmd
    try:
        if kind=="answer":
            if set(payload)!={"field","value"}:raise ValueError("answer requires field/value")
            s=answer(s,payload["field"],payload["value"])
            persist(issue["number"],issue.get("body"),s)
            api("POST",f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{issue['number']}/comments",{"body":render(s)})
        elif kind=="execute":
            if (s.get("next_request") or {}).get("kind")=="CREDENTIAL_GATE":
                transport=s.get("answers",{}).get("mcp_transport")
                missing=[]
                if transport in {"DIRECT_MCP_TOKEN","BOTH"}:
                    if not os.environ.get("GOVERNED_MCP_URL"): missing.append("GOVERNED_MCP_URL")
                    if not os.environ.get("GOVERNED_MCP_AUTH_TOKEN"): missing.append("GOVERNED_MCP_AUTH_TOKEN")
                if transport in {"SSH","BOTH"}:
                    for name in ["GOVERNED_MCP_SSH_PRIVATE_KEY","GOVERNED_MCP_SSH_HOST","GOVERNED_MCP_SSH_USER","GOVERNED_MCP_SSH_PORT"]:
                        if not os.environ.get(name): missing.append(name)
                if missing: raise ValueError("missing GitHub Actions secret/variable: "+", ".join(missing))
                s=mark_credentials_verified(s)
                persist(issue["number"],issue.get("body"),s)
                api("POST",f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{issue['number']}/comments",{"body":render(s)})
        else: raise ValueError("unsupported command")
    except Exception as exc:
        api("POST",f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{issue['number']}/comments",{"body":f"### Local entry response refused\n\n`{type(exc).__name__}: {exc}`\n\nNo state advanced."});return
    emit_outputs(s,issue["number"])

def dispatch(event):
    p=event.get("client_payload") or {};objective=p.get("objective")
    if not isinstance(objective,str) or not objective.strip():raise SystemExit("LOCAL_DISPATCH_FAILED: objective required")
    created=api("POST",f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues",{"title":f"{TITLE_PREFIX} {str(p.get('title') or objective.splitlines()[0])[:80]}","body":f"### Initial objective\n\n{objective.strip()}\n"})
    print(json.dumps({"status":"LOCAL_ENTRY_ISSUE_CREATED","issue_number":created.get("number"),"issue_url":created.get("html_url")}))

def main():
    if os.environ.get("GITHUB_REPOSITORY")=="chainsolutions-wealthtech/Governed-Repository-Template":
        print("LOCAL_ENTRY_SKIPPED: central template source");return
    e=json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"));name=os.environ.get("GITHUB_EVENT_NAME")
    if name=="repository_dispatch" and e.get("action")=="governed_local_start":dispatch(e)
    elif name=="issues" and e.get("action")=="opened":opened(e)
    elif name=="issue_comment" and e.get("action")=="created":
        if (e.get("sender") or {}).get("login")!="github-actions[bot]":commented(e)
    else: print("LOCAL_ENTRY_SKIPPED")

if __name__=="__main__":main()
