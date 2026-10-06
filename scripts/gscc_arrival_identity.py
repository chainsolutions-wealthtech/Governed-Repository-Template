#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, os
from pathlib import Path
from typing import Any

SCHEMA="gscc-arrival-identity/v1"
UNAVAILABLE={None,"","UNAVAILABLE","UNKNOWN","NOT_EXPOSED","NOT_ACCESSIBLE"}

def _clean(v:Any)->Any:
    return "UNAVAILABLE" if v in UNAVAILABLE else v

def _ref(prefix:str, material:str)->str:
    return prefix+hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]

def mint(envelope:dict[str,Any], event:dict[str,Any], *, run_id:str|None=None, run_attempt:str|None=None)->dict[str,Any]:
    out=json.loads(json.dumps(envelope))
    identity=out.get("identity") if isinstance(out.get("identity"),dict) else {}
    repository=event.get("repository") if isinstance(event.get("repository"),dict) else {}
    issue=event.get("issue") if isinstance(event.get("issue"),dict) else {}
    repo_full=str(repository.get("full_name") or out.get("repository") or "")
    repo_id=repository.get("id") or "UNAVAILABLE"

    existing=_clean(identity.get("connection_ref"))
    if existing!="UNAVAILABLE":
        origin="PROVIDER_OR_CLIENT_SUPPLIED"
        arrival_ref=str(existing)
        resumable=True
        transport_subject_ref="UNAVAILABLE"
    elif issue.get("id") and issue.get("number"):
        material=f"github-issue:{repo_id}:{issue['id']}"
        arrival_ref=_ref("GSCC-CONN-",material)
        origin="GSCC_MINTED_GITHUB_ISSUE"
        resumable=True
        transport_subject_ref=f"github-issue:{repo_full}#{issue['number']}"
    else:
        rid=str(run_id or os.environ.get("GITHUB_RUN_ID") or "UNAVAILABLE")
        attempt=str(run_attempt or os.environ.get("GITHUB_RUN_ATTEMPT") or "1")
        material=f"github-run:{repo_id}:{rid}:{attempt}"
        arrival_ref=_ref("GSCC-CONN-",material)
        origin="GSCC_MINTED_GITHUB_RUN"
        resumable=False
        transport_subject_ref=f"github-run:{rid}:{attempt}"

    identity=dict(identity)
    identity["connection_ref"]=arrival_ref
    identity["connection_ref_origin"]=origin
    out["identity"]=identity
    state_scope="arrival-"+hashlib.sha256(arrival_ref.encode("utf-8")).hexdigest()[:24]
    out["gscc_arrival"]={
      "schema":SCHEMA,
      "arrival_ref":arrival_ref,
      "state_scope":state_scope,
      "connection_ref":arrival_ref,
      "origin":origin,
      "resumable":resumable,
      "transport_subject_ref":transport_subject_ref,
      "repository":repo_full or out.get("repository","UNAVAILABLE"),
      "provider_private_identity_inferred":False,
    }
    return out

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--envelope",required=True)
    p.add_argument("--event",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--run-id")
    p.add_argument("--run-attempt")
    a=p.parse_args()
    env=json.loads(Path(a.envelope).read_text(encoding="utf-8"))
    event=json.loads(Path(a.event).read_text(encoding="utf-8"))
    result=mint(env,event,run_id=a.run_id,run_attempt=a.run_attempt)
    Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"GSCC_ARRIVAL_IDENTITY_READY","gscc_arrival":result["gscc_arrival"]},indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
