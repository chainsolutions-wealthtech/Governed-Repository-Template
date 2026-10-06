#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA="gscc-first-touch-observable-packet/v1"
UNAVAILABLE_MARKERS={None,"","UNAVAILABLE","UNKNOWN","NOT_EXPOSED","NOT_ACCESSIBLE"}

EXPECTED={
  "provider":["provider","provider_product","provider_family"],
  "agent":["agent_type","agent_name","agent_role","runtime","surface","channel","execution_mode","model","model_family","model_variant","thinking_mode","reasoning_effort"],
  "client":["client_instance_id","client_type","application","application_version","device_type","platform","locale","language","timezone"],
  "session":["conversation_id","conversation_ref","session_id","session_ref","run_id","task_id","job_id","workspace_id","workspace_name","thread_id","turn_id","message_id","parent_message_id","interaction_sequence"],
  "connection":["connection_ref","connection_ref_origin","gscc_arrival_ref","transport_subject_ref","connection_method","surface_class","transport","transport_type","transport_layer","transport_surface","connector_name","connector_type","connector_version","api_proxy","direct_connector","github_tool_surface","user_agent","region"],
  "tool":["name","operation","category","success"],
  "github":["repository_full_name","repository_id","owner_login","owner_id","visibility","default_branch","branch","head_sha","actor_login","actor_id","permissions","installation_id"],
  "request":["request_id","correlation_id","trace_id","idempotency_key","issued_at","observed_at"]
}

def _value(source:dict[str,Any], key:str)->Any:
    value=source.get(key,"UNAVAILABLE")
    if value is None or value == "":
        return "UNAVAILABLE"
    if isinstance(value, str) and value in {"UNAVAILABLE","UNKNOWN","NOT_EXPOSED","NOT_ACCESSIBLE"}:
        return "UNAVAILABLE"
    return value

def _status(value:Any)->str:
    if value=="UNAVAILABLE":
        return "UNAVAILABLE"
    if value is None:
        return "UNKNOWN"
    return "PRESENT_VALID"


def _provider_envelope_to_host(payload:dict[str,Any])->dict[str,Any]:
    """Flatten the canonical provider First Touch envelope without inventing values."""
    if payload.get("schema") != "gscc-provider-first-touch-envelope/v1":
        return payload

    context=payload.get("provider_context") if isinstance(payload.get("provider_context"),dict) else {}
    agent=context.get("agent") if isinstance(context.get("agent"),dict) else {}
    client=context.get("client") if isinstance(context.get("client"),dict) else {}
    session=context.get("session") if isinstance(context.get("session"),dict) else {}
    connection=context.get("connection") if isinstance(context.get("connection"),dict) else {}
    request=context.get("request") if isinstance(context.get("request"),dict) else {}
    identity=payload.get("identity") if isinstance(payload.get("identity"),dict) else {}
    tool=payload.get("tool") if isinstance(payload.get("tool"),dict) else {}

    host={
      "provider":payload.get("provider","UNAVAILABLE"),
      "provider_product":agent.get("provider_product","UNAVAILABLE"),
      "provider_family":agent.get("provider_family","UNAVAILABLE"),
      "agent_type":agent.get("agent_type","UNAVAILABLE"),
      "agent_name":agent.get("agent_name","UNAVAILABLE"),
      "agent_role":agent.get("agent_role","UNAVAILABLE"),
      "runtime":agent.get("agent_runtime",connection.get("runtime","UNAVAILABLE")),
      "surface":agent.get("agent_surface","UNAVAILABLE"),
      "channel":agent.get("agent_channel","UNAVAILABLE"),
      "execution_mode":agent.get("agent_execution_mode","UNAVAILABLE"),
      "model":agent.get("model","UNAVAILABLE"),
      "model_family":agent.get("model_family","UNAVAILABLE"),
      "model_variant":agent.get("model_variant","UNAVAILABLE"),
      "thinking_mode":agent.get("thinking_mode","UNAVAILABLE"),
      "reasoning_effort":agent.get("reasoning_effort","UNAVAILABLE"),
      "client_instance_id":client.get("client_instance_id","UNAVAILABLE"),
      "client_type":client.get("client_type","UNAVAILABLE"),
      "application":client.get("application","UNAVAILABLE"),
      "application_version":client.get("application_version","UNAVAILABLE"),
      "device_type":client.get("device_type","UNAVAILABLE"),
      "platform":client.get("platform","UNAVAILABLE"),
      "locale":client.get("locale","UNAVAILABLE"),
      "language":client.get("language","UNAVAILABLE"),
      "timezone":client.get("timezone","UNAVAILABLE"),
      "run_id":session.get("run_id","UNAVAILABLE"),
      "task_id":session.get("task_id","UNAVAILABLE"),
      "job_id":session.get("job_id","UNAVAILABLE"),
      "thread_id":session.get("thread_id","UNAVAILABLE"),
      "turn_id":session.get("turn_id","UNAVAILABLE"),
      "message_id":session.get("message_id","UNAVAILABLE"),
      "parent_message_id":session.get("parent_message_id","UNAVAILABLE"),
      "interaction_sequence":session.get("interaction_sequence","UNAVAILABLE"),
      "connection_method":connection.get("connection_method","UNAVAILABLE"),
      "surface_class":connection.get("surface_class","UNAVAILABLE"),
      "transport":payload.get("transport",connection.get("transport_name","UNAVAILABLE")),
      "transport_type":connection.get("transport_type","UNAVAILABLE"),
      "transport_layer":connection.get("transport_layer","UNAVAILABLE"),
      "transport_surface":connection.get("transport_surface","UNAVAILABLE"),
      "connector_name":connection.get("connector_name","UNAVAILABLE"),
      "connector_type":connection.get("connector_type","UNAVAILABLE"),
      "connector_version":connection.get("connector_version","UNAVAILABLE"),
      "api_proxy":connection.get("api_proxy","UNAVAILABLE"),
      "direct_connector":connection.get("direct_connector","UNAVAILABLE"),
      "github_tool_surface":connection.get("github_tool_surface","UNAVAILABLE"),
      "user_agent":connection.get("user_agent","UNAVAILABLE"),
      "region":connection.get("region","UNAVAILABLE"),
      "actor":agent.get("public_identity","UNAVAILABLE"),
      "request_id":request.get("request_id","UNAVAILABLE"),
      "correlation_id":request.get("correlation_id","UNAVAILABLE"),
      "trace_id":request.get("trace_id","UNAVAILABLE"),
      "idempotency_key":request.get("idempotency_key","UNAVAILABLE"),
      "issued_at":request.get("issued_at","UNAVAILABLE"),
      "observed_at":request.get("observed_at","UNAVAILABLE"),
      "connection_ref_origin":identity.get("connection_ref_origin","UNAVAILABLE"),
      "gscc_arrival_ref":((payload.get("gscc_arrival") or {}).get("arrival_ref","UNAVAILABLE") if isinstance(payload.get("gscc_arrival"),dict) else "UNAVAILABLE"),
      "transport_subject_ref":((payload.get("gscc_arrival") or {}).get("transport_subject_ref","UNAVAILABLE") if isinstance(payload.get("gscc_arrival"),dict) else "UNAVAILABLE"),
      "identity":{
        "conversation_id":identity.get("conversation_id",session.get("conversation_id","UNAVAILABLE")),
        "conversation_ref":identity.get("conversation_ref",session.get("conversation_ref","UNAVAILABLE")),
        "session_id":identity.get("session_id",session.get("session_id","UNAVAILABLE")),
        "session_ref":identity.get("session_ref",session.get("session_ref","UNAVAILABLE")),
        "connection_ref":identity.get("connection_ref",connection.get("connection_ref","UNAVAILABLE")),
        "workspace_id":identity.get("workspace_id",session.get("workspace_id","UNAVAILABLE")),
        "workspace_name":identity.get("workspace_name",session.get("workspace_name","UNAVAILABLE"))
      },
      "tool":tool,
    }
    return host

def _github_enriched_to_metadata(payload:dict[str,Any])->dict[str,Any]:
    if "repository_observation" not in payload:
        return payload
    repo=payload.get("repository_observation") if isinstance(payload.get("repository_observation"),dict) else {}
    owner=repo.get("owner") if isinstance(repo.get("owner"),dict) else {}
    return {
      "id":repo.get("id","UNAVAILABLE"),
      "repository_full_name":repo.get("full_name",payload.get("repository","UNAVAILABLE")),
      "owner":{
        "login":owner.get("login",payload.get("repository_owner","UNAVAILABLE")),
        "id":owner.get("id",payload.get("repository_owner_id","UNAVAILABLE")),
      },
      "permissions":repo.get("permissions",payload.get("permissions","UNAVAILABLE")),
      "default_branch":repo.get("default_branch",payload.get("default_branch","UNAVAILABLE")),
      "visibility":repo.get("visibility",payload.get("repository_visibility","UNAVAILABLE")),
      "branch":payload.get("branch","UNAVAILABLE"),
      "head_sha":payload.get("observed_head","UNAVAILABLE"),
    }

def extract(host:dict[str,Any], github:dict[str,Any])->dict[str,Any]:
    host=_provider_envelope_to_host(host)
    github=_github_enriched_to_metadata(github)
    tool=host.get("tool") if isinstance(host.get("tool"),dict) else {}
    identity=host.get("identity") if isinstance(host.get("identity"),dict) else {}
    sections={}

    provider={
      "provider":_value(host,"provider"),
      "provider_product":_value(host,"provider_product"),
      "provider_family":_value(host,"provider_family")
    }
    agent={k:_value(host,k) for k in EXPECTED["agent"]}
    client={k:_value(host,k) for k in EXPECTED["client"]}
    session={k:_value(identity,k) if k in identity else _value(host,k) for k in EXPECTED["session"]}
    connection={k:_value(identity,k) if k=="connection_ref" and k in identity else _value(host,k) for k in EXPECTED["connection"]}
    tool_out={
      "name":_value(tool,"name"),
      "operation":_value(tool,"operation"),
      "category":_value(tool,"category"),
      "success":tool.get("success","UNAVAILABLE")
    }
    owner=github.get("owner") if isinstance(github.get("owner"),dict) else {}
    github_out={
      "repository_full_name":_value(github,"repository_full_name"),
      "repository_id":github.get("id","UNAVAILABLE"),
      "owner_login":owner.get("login","UNAVAILABLE"),
      "owner_id":owner.get("id","UNAVAILABLE"),
      "visibility":_value(github,"visibility"),
      "default_branch":_value(github,"default_branch"),
      "branch":_value(host,"branch") if _value(host,"branch")!="UNAVAILABLE" else _value(github,"branch"),
      "head_sha":_value(host,"observed_head") if _value(host,"observed_head")!="UNAVAILABLE" else _value(github,"head_sha"),
      "actor_login":_value(host,"actor"),
      "actor_id":_value(host,"actor_id"),
      "permissions":github.get("permissions","UNAVAILABLE"),
      "installation_id":_value(host,"installation_id")
    }
    request={k:_value(host,k) for k in EXPECTED["request"]}

    sections.update(provider=provider,agent=agent,client=client,session=session,connection=connection,tool=tool_out,github=github_out,request=request)

    observations={}
    present=0
    unavailable=0
    for section_name, values in sections.items():
        for field, value in values.items():
            path=f"{section_name}.{field}"
            status=_status(value)
            observations[path]={"value":value,"status":status,"source":"HOST" if section_name!="github" else "GITHUB"}
            if status=="PRESENT_VALID":
                present+=1
            elif status=="UNAVAILABLE":
                unavailable+=1

    identity_candidates=[]
    for path in ("session.conversation_ref","session.session_ref","connection.connection_ref","client.client_instance_id"):
        row=observations.get(path)
        if row and row["status"]=="PRESENT_VALID":
            identity_candidates.append({"field":path,"value":row["value"]})

    identity_strength="STRONG" if identity_candidates else "UNRESOLVED"
    classification="FIRST_TOUCH_CANDIDATE" if identity_candidates else "UNRESOLVED"

    return {
      "schema":SCHEMA,
      "sections":sections,
      "observations":observations,
      "summary":{
        "expected_field_count":sum(len(v) for v in EXPECTED.values()),
        "present_valid_count":present,
        "unavailable_count":unavailable,
        "silent_missing_count":0,
        "complete_accounting":True
      },
      "identity":{
        "candidates":identity_candidates,
        "strength":identity_strength,
        "classification":classification
      },
      "mutation_authority_granted":False
    }

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--host",required=True)
    p.add_argument("--github",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    host=json.loads(Path(a.host).read_text(encoding="utf-8"))
    github=json.loads(Path(a.github).read_text(encoding="utf-8"))
    result=extract(host,github)
    Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
