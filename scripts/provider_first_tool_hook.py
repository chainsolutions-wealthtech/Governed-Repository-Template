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

def _reported(event:dict[str,Any], key:str, default:Any="UNAVAILABLE")->Any:
    value=event.get(key, default)
    return default if value in (None, "") else value

def build_provider_context(event:dict[str,Any], identity:dict[str,Any])->dict[str,Any]:
    """Normalize only provider/host-observable facts.

    Missing provider-private facts are explicit UNAVAILABLE. No repository fact is
    inferred here; repository-owned enrichment happens after repository_dispatch.
    """
    return {
        "request":{
            "request_id":_reported(event,"request_id"),
            "correlation_id":_reported(event,"correlation_id"),
            "trace_id":_reported(event,"trace_id"),
            "idempotency_key":_reported(event,"idempotency_key"),
            "issued_at":_reported(event,"issued_at"),
            "observed_at":_reported(event,"observed_at"),
        },
        "agent":{
            "agent_type":_reported(event,"agent_type"),
            "agent_name":_reported(event,"agent_name"),
            "agent_role":_reported(event,"agent_role"),
            "agent_runtime":_reported(event,"runtime"),
            "agent_surface":_reported(event,"surface"),
            "agent_channel":_reported(event,"channel"),
            "agent_execution_mode":_reported(event,"execution_mode"),
            "provider":_reported(event,"provider"),
            "provider_family":_reported(event,"provider_family"),
            "provider_product":_reported(event,"provider_product"),
            "provider_ref":_reported(event,"provider_ref"),
            "public_identity":_reported(event,"actor"),
            "model":_reported(event,"model"),
            "model_family":_reported(event,"model_family"),
            "model_variant":_reported(event,"model_variant"),
            "thinking_mode":_reported(event,"thinking_mode"),
            "reasoning_effort":_reported(event,"reasoning_effort"),
            "direct_github_functions_used":True,
            "codex_used":bool(event.get("codex_used",False)),
            "codex_workspace_created":bool(event.get("codex_workspace_created",False)),
            "codex_task_created":bool(event.get("codex_task_created",False)),
            "github_app_codex_used":bool(event.get("github_app_codex_used",False)),
        },
        "client":{
            "client_instance_id":_reported(event,"client_instance_id"),
            "client_type":_reported(event,"client_type"),
            "application":_reported(event,"application"),
            "application_version":_reported(event,"application_version"),
            "device_type":_reported(event,"device_type"),
            "platform":_reported(event,"platform"),
            "locale":_reported(event,"locale"),
            "language":_reported(event,"language"),
            "timezone":_reported(event,"timezone"),
        },
        "session":{
            "conversation_id":identity.get("conversation_id","UNAVAILABLE"),
            "conversation_ref":identity.get("conversation_ref","UNAVAILABLE"),
            "conversation_type":_reported(event,"conversation_type"),
            "conversation_start_time":_reported(event,"conversation_start_time"),
            "first_touch_time":_reported(event,"first_touch_time"),
            "session_id":identity.get("session_id","UNAVAILABLE"),
            "session_ref":identity.get("session_ref","UNAVAILABLE"),
            "run_id":_reported(event,"run_id"),
            "task_id":_reported(event,"task_id"),
            "job_id":_reported(event,"job_id"),
            "workspace_id":identity.get("workspace_id","UNAVAILABLE"),
            "workspace_name":identity.get("workspace_name","UNAVAILABLE"),
            "thread_id":_reported(event,"thread_id"),
            "turn_id":_reported(event,"turn_id"),
            "message_id":_reported(event,"message_id"),
            "parent_message_id":_reported(event,"parent_message_id"),
            "interaction_sequence":_reported(event,"interaction_sequence"),
            "first_operation":_reported(event,"tool_name"),
            "operation_count":1,
            "new_arrival":True,
            "first_touch_consumed":False,
        },
        "connection":{
            "connection_ref":identity.get("connection_ref","UNAVAILABLE"),
            "connection_method":_reported(event,"connection_method"),
            "surface_class":_reported(event,"surface_class"),
            "transport_type":_reported(event,"transport_type"),
            "transport_name":_reported(event,"transport"),
            "transport_layer":_reported(event,"transport_layer"),
            "transport_surface":_reported(event,"transport_surface"),
            "connector_name":_reported(event,"connector_name"),
            "connector_type":_reported(event,"connector_type"),
            "connector_version":_reported(event,"connector_version"),
            "api_proxy":_reported(event,"api_proxy"),
            "direct_connector":_reported(event,"direct_connector"),
            "github_tool_surface":_reported(event,"github_tool_surface"),
            "runtime":_reported(event,"runtime"),
            "user_agent":_reported(event,"user_agent"),
            "region":_reported(event,"region"),
            "capabilities":event.get("capabilities","UNAVAILABLE"),
        },
        "negative":{
            "codex_used":bool(event.get("codex_used",False)),
            "github_app_codex_used":bool(event.get("github_app_codex_used",False)),
            "codex_workspace_created":bool(event.get("codex_workspace_created",False)),
            "codex_task_created":bool(event.get("codex_task_created",False)),
            "repository_mutated":bool(event.get("repository_mutated",False)),
            "secret_accessed":bool(event.get("secret_accessed",False)),
            "token_exposed":bool(event.get("token_exposed",False)),
            "oauth_secret_exposed":bool(event.get("oauth_secret_exposed",False)),
            "private_key_exposed":bool(event.get("private_key_exposed",False)),
            "conversation_id_exposed":identity.get("conversation_id") not in UNAVAILABLE,
            "session_id_exposed":identity.get("session_id") not in UNAVAILABLE,
            "installation_id_exposed":bool(event.get("installation_id_exposed",False)),
            "client_id_exposed":bool(event.get("client_id_exposed",False)),
            "ip_exposed":bool(event.get("ip_exposed",False)),
        },
    }

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
    normalized_identity={
        "conversation_id":identity.get("conversation_id","UNAVAILABLE"),
        "conversation_ref":identity.get("conversation_ref","UNAVAILABLE"),
        "session_id":identity.get("session_id","UNAVAILABLE"),
        "session_ref":identity.get("session_ref","UNAVAILABLE"),
        "connection_ref":identity.get("connection_ref","UNAVAILABLE"),
        "workspace_id":identity.get("workspace_id","UNAVAILABLE"),
        "workspace_name":identity.get("workspace_name","UNAVAILABLE"),
    }
    return {
        "schema":SCHEMA,
        "provider":provider,
        "transport":transport,
        "repository":repository,
        "identity":normalized_identity,
        "identity_status":"STABLE" if _stable_identity(normalized_identity) else "UNRESOLVED",
        "tool":{
            "name":event.get("tool_name","UNAVAILABLE"),
            "operation":event.get("operation","UNAVAILABLE"),
            "category":event.get("category","UNAVAILABLE"),
            "success":event.get("success",True),
        },
        "provider_context":build_provider_context(event,normalized_identity),
    }

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
            "marker":marker or "UNRESOLVED",
            "event_type":EVENT_TYPE,
            "http_status":status,
            "envelope":envelope,
            "mutation_authority_granted":False,
        }


@dataclass
class FirstTouchBeforeToolCall:
    """Callable adapter for gscc.instrument_tool(before_tool_call=...).

    One adapter instance represents one provider/client connector session.
    It emits Provider First Touch before the first instrumented tool only.
    """

    event_base: dict[str, Any]
    token: str | None = None
    dispatch_fn: Any = send_dispatch
    hook: FirstToolHook = field(default_factory=FirstToolHook)
    emitted_for_session: bool = False

    def __call__(self, tool_name: str) -> dict[str, Any]:
        if self.emitted_for_session:
            return {
                "status": "FIRST_TOUCH_ALREADY_EMITTED",
                "event_type": EVENT_TYPE,
                "mutation_authority_granted": False,
            }

        event = dict(self.event_base)
        event["first_tool_call"] = True
        event["tool_name"] = tool_name
        event.setdefault("operation", "tool_call")
        event.setdefault("category", "READ")
        event.setdefault("success", True)

        result = self.hook.maybe_emit_first_touch(
            event,
            token=self.token,
            dispatch_fn=self.dispatch_fn,
        )
        self.emitted_for_session = True
        return result


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
