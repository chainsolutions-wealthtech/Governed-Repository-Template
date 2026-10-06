#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, MutableMapping

EVENT_TYPE="gscc_provider_first_touch"
SCHEMA="gscc-provider-first-touch-envelope/v1"
UNAVAILABLE={"", "UNAVAILABLE", "UNKNOWN", "NOT_EXPOSED", "NOT_ACCESSIBLE", None}

def _clean(value: Any) -> Any:
    if isinstance(value, str):
        value=value.strip()
    return value

def _stable_identity(identity: dict[str,Any]) -> tuple[str,str] | None:
    for key in ("conversation_ref","session_ref","connection_ref"):
        value=_clean(identity.get(key))
        if value not in UNAVAILABLE:
            return key,str(value)
    return None

def _marker_key(provider:str,repository:str,identity:dict[str,Any])->str | None:
    stable=_stable_identity(identity)
    if not stable:
        return None
    kind,value=stable
    return f"{provider}:{repository}:{kind}:{value}"

def build_envelope(event:dict[str,Any])->dict[str,Any]:
    provider=str(_clean(event.get("provider") or ""))
    transport=str(_clean(event.get("transport") or ""))
    repository=str(_clean(event.get("repository") or ""))
    identity=event.get("identity") if isinstance(event.get("identity"),dict) else {}
    if not provider:
        raise ValueError("provider required")
    if not transport:
        raise ValueError("transport required")
    if repository.count("/") != 1:
        raise ValueError("repository must use owner/name")
    envelope={
        "schema":SCHEMA,
        "provider":provider,
        "transport":transport,
        "repository":repository,
        "identity":{
            "conversation_ref":identity.get("conversation_ref","UNAVAILABLE"),
            "session_ref":identity.get("session_ref","UNAVAILABLE"),
            "connection_ref":identity.get("connection_ref","UNAVAILABLE"),
        },
        "direct_github_functions_used":True,
        "codex_used":False,
        "repository_mutated":False,
        "secret_accessed":False,
        "token_exposed":False,
        "identity_status":"STABLE" if _stable_identity(identity) else "UNRESOLVED",
        "tool":{
            "name":event.get("tool_name"),
            "operation":event.get("operation"),
            "category":event.get("category"),
            "success":event.get("success",True),
        },
    }
    for key in (
        "actor","model","branch","observed_head","repository_id","repository_owner",
        "repository_owner_id","repository_owner_type","repository_visibility",
        "default_branch","transport_type","transport_surface","connector_name",
        "connector_type","connector_version","github_tool_surface","observed_at",
    ):
        value=event.get(key)
        if value not in (None,""):
            envelope[key]=value
    if isinstance(event.get("capabilities"),dict):
        envelope["capabilities"]=event["capabilities"]
    if isinstance(event.get("unavailable"),dict):
        envelope["unavailable"]=event["unavailable"]
    return envelope

def send_dispatch(repository:str,envelope:dict[str,Any],token:str,api_base:str="https://api.github.com")->int:
    owner,name=repository.split("/",1)
    url=f"{api_base.rstrip('/')}/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(name)}/dispatches"
    payload=json.dumps({"event_type":EVENT_TYPE,"client_payload":envelope},separators=(",",":"),ensure_ascii=False).encode("utf-8")
    req=urllib.request.Request(url,method="POST",data=payload,headers={
        "Accept":"application/vnd.github+json",
        "Authorization":f"Bearer {token}",
        "User-Agent":"gscc-provider-first-tool-hook/1",
        "X-GitHub-Api-Version":"2022-11-28",
        "Content-Type":"application/json",
    })
    with urllib.request.urlopen(req,timeout=20) as response:
        return int(response.status)

@dataclass
class FirstToolHook:
    emitted: MutableMapping[str,bool]=field(default_factory=dict)

    def maybe_emit_first_touch(
        self,
        event:dict[str,Any],
        *,
        token:str|None=None,
        dispatch_fn=send_dispatch,
    )->dict[str,Any]:
        if event.get("first_tool_call") is False:
            return {
                "status":"NOT_FIRST_TOOL_CALL",
                "event_type":EVENT_TYPE,
                "mutation_authority_granted":False,
            }
        envelope=build_envelope(event)
        marker=_marker_key(envelope["provider"],envelope["repository"],envelope["identity"])
        if marker is not None and self.emitted.get(marker):
            return {
                "status":"FIRST_TOUCH_ALREADY_EMITTED",
                "marker":marker or "UNRESOLVED",
                "event_type":EVENT_TYPE,
                "mutation_authority_granted":False,
            }
        runtime_token=(token or os.environ.get("GITHUB_TOKEN") or "").strip()
        if not runtime_token:
            raise RuntimeError("GitHub transport credential unavailable")
        status=dispatch_fn(envelope["repository"],envelope,runtime_token)
        if status not in {200,201,202,204}:
            raise RuntimeError(f"provider first-touch dispatch returned HTTP {status}")
        if marker is not None:
            self.emitted[marker]=True
        return {
            "status":"FIRST_TOUCH_EMITTED",
            "marker":marker,
            "event_type":EVENT_TYPE,
            "http_status":status,
            "envelope":envelope,
            "mutation_authority_granted":False,
        }

def main()->None:
    p=argparse.ArgumentParser(description="Provider first GitHub tool-call hook")
    p.add_argument("--event",required=True,help="JSON event file for the first GitHub tool call")
    p.add_argument("--state-file",help="optional host-local idempotency marker file")
    p.add_argument("--dry-run",action="store_true")
    a=p.parse_args()
    event=json.loads(Path(a.event).read_text(encoding="utf-8"))
    state:dict[str,bool]={}
    if a.state_file and Path(a.state_file).exists():
        loaded=json.loads(Path(a.state_file).read_text(encoding="utf-8"))
        if isinstance(loaded,dict):
            state={str(k):bool(v) for k,v in loaded.items()}
    hook=FirstToolHook(state)
    if a.dry_run:
        env=build_envelope(event)
        result={"status":"DRY_RUN","event_type":EVENT_TYPE,"envelope":env,"mutation_authority_granted":False}
    else:
        result=hook.maybe_emit_first_touch(event)
        if a.state_file:
            Path(a.state_file).write_text(json.dumps(dict(hook.emitted),indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
