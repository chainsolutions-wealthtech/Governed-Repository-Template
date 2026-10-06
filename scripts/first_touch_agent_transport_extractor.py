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
  "connection":["connection_ref","connection_method","surface_class","transport","transport_type","transport_layer","transport_surface","connector_name","connector_type","connector_version","api_proxy","direct_connector","github_tool_surface","user_agent","region"],
  "tool":["name","operation","category","success"],
  "github":["repository_full_name","repository_id","owner_login","owner_id","visibility","default_branch","branch","head_sha","actor_login","actor_id","permissions","installation_id"],
  "request":["request_id","correlation_id","trace_id","idempotency_key","issued_at","observed_at"]
}

def _value(source:dict[str,Any], key:str)->Any:
    value=source.get(key,"UNAVAILABLE")
    return "UNAVAILABLE" if value in UNAVAILABLE_MARKERS else value

def _status(value:Any)->str:
    if value=="UNAVAILABLE":
        return "UNAVAILABLE"
    if value is None:
        return "UNKNOWN"
    return "PRESENT_VALID"

def extract(host:dict[str,Any], github:dict[str,Any])->dict[str,Any]:
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
      "branch":_value(host,"branch"),
      "head_sha":_value(host,"observed_head"),
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
