#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, urllib.request
from datetime import datetime, timezone
from local_governed_entry import record_mcp_discovery
from local_entry_issue_bridge import api, extract_state, persist, render

def parse_mcp_body(raw:str):
    raw=raw.strip()
    if not raw:return {}
    if raw.startswith("{"):return json.loads(raw)
    events=[]
    for line in raw.splitlines():
        if line.startswith("data:"):
            data=line[5:].strip()
            if data:
                try: events.append(json.loads(data))
                except Exception: pass
    return events[-1] if events else {"raw":raw[:12000]}

def post(endpoint,token,payload,session_id=None):
    headers={"Authorization":f"Bearer {token}","Content-Type":"application/json","Accept":"application/json, text/event-stream","User-Agent":"governed-repository-mcp-discovery"}
    if session_id: headers["Mcp-Session-Id"]=session_id
    req=urllib.request.Request(endpoint,method="POST",headers=headers,data=json.dumps(payload).encode())
    with urllib.request.urlopen(req,timeout=30) as r:
        return parse_mcp_body(r.read().decode(errors="replace")), r.headers.get("Mcp-Session-Id") or session_id

def call_tool(endpoint,token,session_id,idx,name):
    payload={"jsonrpc":"2.0","id":idx,"method":"tools/call","params":{"name":name,"arguments":{}}}
    res,_=post(endpoint,token,payload,session_id)
    return res

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--issue-number",type=int,required=True);args=ap.parse_args()
    repo=os.environ["GITHUB_REPOSITORY"]
    issue=api("GET",f"/repos/{repo}/issues/{args.issue_number}");state=extract_state(issue.get("body"))
    if (state.get("next_request") or {}).get("kind")!="MCP_DISCOVERY": raise SystemExit("MCP_DISCOVERY_SKIPPED")
    transport=state.get("answers",{}).get("mcp_transport")
    if transport=="SSH":
        api("POST",f"/repos/{repo}/issues/{args.issue_number}/comments",{"body":"### MCP discovery blocked\n\nSSH-only mode requires the governed server-side forced-command adapter. Arbitrary shell is forbidden. Use DIRECT_MCP_TOKEN or BOTH until that adapter is installed."})
        raise SystemExit(4)
    endpoint=os.environ.get("GOVERNED_MCP_URL") or state.get("answers",{}).get("mcp_endpoint")
    token=os.environ.get("GOVERNED_MCP_AUTH_TOKEN")
    if not endpoint or not token: raise SystemExit("MCP_DISCOVERY_CREDENTIAL_MISSING")
    init={"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"governed-repository-bootstrap","version":"1.0"}}}
    init_res,session=post(endpoint,token,init)
    try: post(endpoint,token,{"jsonrpc":"2.0","method":"notifications/initialized","params":{}},session)
    except Exception: pass
    tools=["ping","get_project_context","list_domains_s1","list_domains_s2","get_write_tools_context"]
    observed={}
    for i,name in enumerate(tools,start=2):
        try: observed[name]={"status":"PASS","result":call_tool(endpoint,token,session,i,name)}
        except Exception as exc: observed[name]={"status":"ERROR","error":str(exc)[:1000]}
    evidence={"transport":"DIRECT_MCP_TOKEN","endpoint":endpoint,"observed_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"initialize":init_res,"tools":observed}
    state2=record_mcp_discovery(state,evidence)
    persist(args.issue_number,issue.get("body"),state2)
    api("POST",f"/repos/{repo}/issues/{args.issue_number}/comments",{"body":render(state2)})

if __name__=="__main__":main()
