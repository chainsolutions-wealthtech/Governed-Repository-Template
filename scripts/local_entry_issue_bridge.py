#!/usr/bin/env python3
from __future__ import annotations
import json, os, re, subprocess, urllib.error, urllib.parse, urllib.request
from pathlib import Path
from local_governed_entry import answer, decode_state, encode_state, mark_credentials_verified, new_request

ROOT=Path(__file__).resolve().parents[1]
TITLE_PREFIX="[Governed Local Entry]"
MARKER_RE=re.compile(r"\n?<!-- GOVERNED_LOCAL_ENTRY_STATE:([A-Za-z0-9_-]+) -->\s*$",re.S)
TRUSTED_ASSOCIATIONS={"OWNER","MEMBER","COLLABORATOR"}
MACHINE_SOURCE_REPOSITORY="chainsolutions-wealthtech/Governed-Repository-Template"

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

def trusted_actor(record):
    if not isinstance(record,dict) or record.get("author_association") not in TRUSTED_ASSOCIATIONS:
        return False
    login=((record.get("user") or {}).get("login") or "")
    if not isinstance(login,str) or not re.fullmatch(r"[A-Za-z0-9-]{1,39}",login):
        return False
    encoded=urllib.parse.quote(login,safe="")
    permission=api("GET",f"/repos/{os.environ['GITHUB_REPOSITORY']}/collaborators/{encoded}/permission").get("permission")
    return permission in {"admin","maintain","write"}

def refuse_untrusted(number):
    api("POST",f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{number}/comments",{
      "body":"### Local entry refused\n\nThis command requires a repository actor with current admin, maintain or write permission. No governed state advanced."
    })

def opened(event):
    issue=event["issue"]
    if not str(issue.get("title","")).startswith(TITLE_PREFIX):return
    if not trusted_actor(issue):
        refuse_untrusted(issue["number"]);return
    if (ROOT/".template-source").exists():return
    n=issue["number"];rid=f"LOCAL-{n:06d}"
    s=new_request(rid,os.environ["GITHUB_REPOSITORY"],head(),first_agent_required(),strip_marker(issue.get("body")))
    persist(n,issue.get("body"),s);api("POST",f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{n}/comments",{"body":render(s)});emit_outputs(s,n)

def commented(event):
    issue=event["issue"]
    if not str(issue.get("title","")).startswith(TITLE_PREFIX):return
    if not trusted_actor(event.get("comment") or {}):
        refuse_untrusted(issue["number"]);return
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
                    if not os.environ.get("GOVERNED_MCP_AUTH_TOKEN"): missing.append("GOVERNED_MCP_AUTH_TOKEN")
                if missing: raise ValueError("missing GitHub Actions secret/variable: "+", ".join(missing))
                s=mark_credentials_verified(s)
                persist(issue["number"],issue.get("body"),s)
                api("POST",f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{issue['number']}/comments",{"body":render(s)})
        else: raise ValueError("unsupported command")
    except Exception as exc:
        api("POST",f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{issue['number']}/comments",{"body":f"### Local entry response refused\n\n`{type(exc).__name__}: {exc}`\n\nNo state advanced."});return
    emit_outputs(s,issue["number"])

def dispatch_start(event):
    p=event.get("client_payload") or {};objective=p.get("objective")
    if not isinstance(objective,str) or not objective.strip():raise SystemExit("LOCAL_DISPATCH_FAILED: objective required")
    created=api("POST",f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues",{"title":f"{TITLE_PREFIX} {str(p.get('title') or objective.splitlines()[0])[:80]}","body":f"### Initial objective\n\n{objective.strip()}\n"})
    print(json.dumps({"status":"LOCAL_ENTRY_ISSUE_CREATED","issue_number":created.get("number"),"issue_url":created.get("html_url")}))

def dispatch_machine_command(event):
    p=event.get("client_payload") or {}
    sender=event.get("sender") or {}
    if sender.get("type")!="Bot":
        raise SystemExit("LOCAL_MACHINE_COMMAND_FAILED: sender must be a GitHub App bot")
    if p.get("source_repository")!=MACHINE_SOURCE_REPOSITORY:
        raise SystemExit("LOCAL_MACHINE_COMMAND_FAILED: invalid source repository")
    number=p.get("issue_number");expected=p.get("expected_head");command=p.get("command")
    if not isinstance(number,int) or number<1:
        raise SystemExit("LOCAL_MACHINE_COMMAND_FAILED: issue_number")
    if not isinstance(expected,str) or not re.fullmatch(r"[0-9a-f]{40}",expected):
        raise SystemExit("LOCAL_MACHINE_COMMAND_FAILED: expected_head")
    observed=head()
    if observed!=expected:
        raise SystemExit(f"HEAD_MOVED: expected={expected} observed={observed}")
    if not isinstance(command,dict) or command.get("kind") not in {"execute","answer"}:
        raise SystemExit("LOCAL_MACHINE_COMMAND_FAILED: command")
    issue=api("GET",f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{number}")
    if not str(issue.get("title","")).startswith(TITLE_PREFIX):
        raise SystemExit("LOCAL_MACHINE_COMMAND_FAILED: target issue")
    s=extract_state(issue.get("body"))
    if s.get("expected_head_sha")!=expected:
        raise SystemExit(f"LOCAL_STATE_HEAD_MOVED: expected={expected} state={s.get('expected_head_sha')}")
    try:
        if command["kind"]=="answer":
            if set(command)!={"kind","field","value"}:raise ValueError("answer requires kind/field/value")
            s=answer(s,command["field"],command["value"])
        else:
            if set(command)!={"kind"}:raise ValueError("execute requires only kind")
            if (s.get("next_request") or {}).get("kind")=="CREDENTIAL_GATE":
                transport=s.get("answers",{}).get("mcp_transport")
                missing=[]
                if transport in {"DIRECT_MCP_TOKEN","BOTH"} and not os.environ.get("GOVERNED_MCP_AUTH_TOKEN"):
                    missing.append("GOVERNED_MCP_AUTH_TOKEN")
                if missing:raise ValueError("missing GitHub Actions secret/variable: "+", ".join(missing))
                s=mark_credentials_verified(s)
            else:
                raise ValueError("execute is only valid at an executable local gate")
    except Exception as exc:
        api("POST",f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{number}/comments",{"body":f"### Governed machine local command refused\n\n`{type(exc).__name__}: {exc}`\n\nNo state advanced."})
        return
    persist(number,issue.get("body"),s)
    api("POST",f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{number}/comments",{"body":render(s)})
    emit_outputs(s,number)

def main():
    if os.environ.get("GITHUB_REPOSITORY")=="chainsolutions-wealthtech/Governed-Repository-Template":
        print("LOCAL_ENTRY_SKIPPED: central template source");return
    e=json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"));name=os.environ.get("GITHUB_EVENT_NAME")
    if name=="repository_dispatch" and e.get("action")=="governed_local_start":dispatch_start(e)
    elif name=="repository_dispatch" and e.get("action")=="governed_local_command":dispatch_machine_command(e)
    elif name=="issues" and e.get("action")=="opened":opened(e)
    elif name=="issue_comment" and e.get("action")=="created":
        if (e.get("sender") or {}).get("login")!="github-actions[bot]":commented(e)
    else: print("LOCAL_ENTRY_SKIPPED")

if __name__=="__main__":main()
