#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from gscc.admission import evaluate_admission, evaluate_access_grant
from gscc.admission_harvester import harvest_qualification_evidence
from gscc.first_touch_store import project_to_gse
from gscc_post_q1_gate_router import route_gate
from gscc_gacr.issue_control_bridge import apply_host_control_event
from gscc_gacr.admission_gse_projection import project_pre_gacr_admission_gse_state
from gacr_continuity_coordination import default_state as default_continuity_state, resolve_logical_agent_alias_docs

ROOT=Path(__file__).resolve().parents[1]
MIGRATION=ROOT/".governance"/"control-plane-db"/"011_gscc_session_runtime.sql"
CONTINUITY_STATE=ROOT/".governance"/"control-plane-state"/"gacr-continuities.json"
SESSIONS_STATE=ROOT/".governance"/"control-plane-state"/"gacr-sessions.json"
FORENSICS_STATE=ROOT/".governance"/"control-plane-state"/"gacr-forensics.json"

def now_iso()->str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _id(prefix:str,*parts:Any)->str:
    raw=":".join(str(x) for x in parts)
    return prefix+hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

def _load_runtime(conn:sqlite3.Connection, runtime_id:str)->dict[str,Any]:
    row=conn.execute("SELECT runtime_id,run_id,arrival_ref,identity_id,capture_id,issue_number,connection_ref,state,admission_json,capability_evidence_json,control_evidence_json,gse_state_json,qualification_evidence_json,access_grant_json,last_gate,next_gate,created_at,updated_at FROM gscc_session_runtime WHERE runtime_id=?",(runtime_id,)).fetchone()
    if not row: raise ValueError("runtime not found")
    keys=("runtime_id","run_id","arrival_ref","identity_id","capture_id","issue_number","connection_ref","state","admission_json","capability_evidence_json","control_evidence_json","gse_state_json","qualification_evidence_json","access_grant_json","last_gate","next_gate","created_at","updated_at")
    return dict(zip(keys,row))

def _packet(conn:sqlite3.Connection, run_id:str)->tuple[dict[str,Any],dict[str,Any]]:
    row=conn.execute(
      "SELECT r.capture_id,r.identity_id,r.classification,p.packet_json FROM gscc_entry_pipeline_runs r JOIN gscc_observable_packets p ON p.packet_id=r.packet_id WHERE r.run_id=? AND r.entry_status='ENTRY_READY_FOR_Q1'",
      (run_id,),
    ).fetchone()
    if not row: raise ValueError("READY_FOR_Q1 entry run required")
    return {"capture_id":row[0],"identity_id":row[1],"classification":row[2]},json.loads(row[3])

def _route(db:Path,runtime_id:str,gate:str,outcome:str,evidence:dict[str,Any],identity_id:str)->dict[str,Any]:
    return route_gate(db,route_run_id=f"{runtime_id}:{gate}",current_gate=gate,observed_outcome=outcome,entry_run_id=runtime_id,identity_id=identity_id,evidence=evidence)

def _requested_alias(packet:dict[str,Any])->str|None:
    request=(packet.get("sections") or {}).get("request") or {}
    value=request.get("logical_agent_alias")
    if value in (None,"","UNAVAILABLE","UNKNOWN","NOT_EXPOSED","NOT_ACCESSIBLE"):
        return None
    return str(value).strip()


def _session_logical_agent_id(session:dict[str,Any])->str|None:
    value=session.get("logical_agent_id") or session.get("agent_identity")
    return str(value).strip() if value not in (None,"") else None


def _session_connection_values(session:dict[str,Any])->set[str]:
    values=set()
    value=session.get("connection_ref")
    if value not in (None,"","UNAVAILABLE"):
        values.add(str(value))
    for context in session.get("provider_contexts") or []:
        if not isinstance(context,dict):
            continue
        value=context.get("connection_ref")
        if value not in (None,"","UNAVAILABLE"):
            values.add(str(value))
    return values


def resolve_alias_binding_intent(packet:dict[str,Any], sessions:dict[str,Any], continuity_state:dict[str,Any])->dict[str,Any]|None:
    alias=_requested_alias(packet)
    if not alias:
        return None
    result=resolve_logical_agent_alias_docs(continuity_state,sessions,alias=alias)
    return {
        "status":"ALIAS_RESOLVED_AT_GACR_Q2",
        "requested_alias":result["human_alias"],
        "logical_agent_id":result["logical_agent_id"],
        "routing_status":result.get("routing_status"),
        "resolved_target_session_id":result.get("resolved_target_session_id"),
        "reference_session_ids":result.get("reference_session_ids") or [],
        "continuity_memberships":result.get("continuity_memberships") or [],
        "projection_only":True,
        "grants_task_authority":False,
        "grants_claim":False,
        "grants_mutation_authority":False,
    }


def resolve_alias_attach_proof(
    packet:dict[str,Any],
    sessions:dict[str,Any],
    continuity_state:dict[str,Any],
    forensics:dict[str,Any],
)->dict[str,Any]|None:
    intent=resolve_alias_binding_intent(packet,sessions,continuity_state)
    if intent is None:
        return None

    repository=((packet.get("sections") or {}).get("github") or {}).get("repository_full_name")
    memberships=[
        item for item in (intent.get("continuity_memberships") or [])
        if item.get("repository")==repository and item.get("continuity_id")
    ]
    continuity_ids=sorted({str(item["continuity_id"]) for item in memberships})
    if len(continuity_ids)!=1:
        raise ValueError(
            "GSCC_ALIAS_BINDING_FAILED: exactly one canonical continuity required "
            f"alias={intent.get('requested_alias')} continuities={continuity_ids}"
        )
    continuity_id=continuity_ids[0]

    reference_session_ids=sorted({
        str(value)
        for value in (intent.get("reference_session_ids") or [])
        if str(value).strip()
    })
    if len(reference_session_ids)!=1:
        raise ValueError(
            "GSCC_ALIAS_BINDING_FAILED: exactly one reference session required "
            f"alias={intent.get('requested_alias')} references={reference_session_ids}"
        )
    reference_session_id=reference_session_ids[0]
    reference=next(
        (item for item in sessions.get("sessions",[]) if item.get("session_id")==reference_session_id),
        None,
    )
    if reference is None:
        raise ValueError("GSCC_ALIAS_BINDING_FAILED: reference session missing")
    if _session_logical_agent_id(reference)!=intent.get("logical_agent_id"):
        raise ValueError("GSCC_ALIAS_BINDING_FAILED: reference logical-agent mismatch")
    if reference.get("repository")!=repository:
        raise ValueError("GSCC_ALIAS_BINDING_FAILED: reference repository mismatch")

    candidates=[]
    for item in forensics.get("items",[]):
        if not isinstance(item,dict) or item.get("session_id")!=reference_session_id:
            continue
        resume=item.get("resume_point") or {}
        completed=((item.get("actions") or {}).get("last_action_completed") or {})
        checkpoint_match=(
            item.get("last_checkpoint_ref")==continuity_id
            or resume.get("checkpoint_ref")==continuity_id
            or completed.get("checkpoint_ref")==continuity_id
        )
        if not checkpoint_match:
            continue
        evidence=[]
        if resume.get("checkpoint_ref")==continuity_id and resume.get("evidence_ref"):
            evidence.append(("GACR_FORENSICS_RESUME_POINT",resume["evidence_ref"]))
        if item.get("last_checkpoint_ref")==continuity_id and item.get("last_evidence_ref"):
            evidence.append(("GACR_FORENSICS_LAST_EVIDENCE",item["last_evidence_ref"]))
        if completed.get("checkpoint_ref")==continuity_id and completed.get("evidence_ref"):
            evidence.append(("GACR_FORENSICS_COMPLETED_ACTION",completed["evidence_ref"]))
        if evidence:
            candidates.append((
                str(item.get("generated_at") or ""),
                str(item.get("forensic_id") or ""),
                item,
                evidence,
            ))
    if not candidates:
        raise ValueError(
            "GSCC_ALIAS_BINDING_FAILED: canonical continuity checkpoint evidence unavailable"
        )
    candidates.sort(key=lambda value:(value[0],value[1]),reverse=True)
    _,_,forensic,evidence=candidates[0]
    evidence_source,evidence_ref=evidence[0]

    return {
        "status":"SAME_LOGICAL_AGENT_PROOF_READY",
        "requested_alias":intent["requested_alias"],
        "logical_agent_id":intent["logical_agent_id"],
        "same_logical_agent_session_id":reference_session_id,
        "continuity_id":continuity_id,
        "continuity_evidence_ref":evidence_ref,
        "continuity_evidence_source":evidence_source,
        "forensic_id":forensic.get("forensic_id"),
        "reference_session_status":reference.get("status"),
        "reference_relay_state":(reference.get("relay") or {}).get("state"),
        "reference_active_claim_count":len(
            ((forensic.get("work") or {}).get("active_claims") or [])
        ),
        "projection_only":True,
        "grants_task_authority":False,
        "grants_claim":False,
        "grants_mutation_authority":False,
    }


def _admission(packet:dict[str,Any], arrival_ref:str, connection_ref:str, runtime_id:str)->dict[str,Any]:
    s=packet["sections"]; agent=s["agent"]; github=s["github"]; req=s["request"]
    observed=req.get("observed_at")
    if observed in (None,"","UNAVAILABLE"): observed=now_iso()
    return {
      "schema":"gscc-admission-envelope/v1",
      "request":{
        "request_id":_id("GSCC-REQ-",arrival_ref),
        "correlation_id":_id("GSCC-CORR-",arrival_ref),
        "idempotency_key":_id("GSCC-IDEM-",arrival_ref),
        "issued_at":observed,
        "observed_at":observed,
      },
      "agent":{
        "agent_type":agent.get("agent_type") if agent.get("agent_type") not in (None,"UNAVAILABLE") else "conversation-agent",
        "provider":s["provider"].get("provider"),
        "requested_role":"qualification-client",
      },
      "client":{
        "client_instance_id":_id("GSCC-CLIENT-",arrival_ref),
        "client_type":"gscc-arrival-transport",
      },
      "session":{"conversation_ref":s["session"].get("conversation_ref","UNAVAILABLE")},
      "connection":{
        "connection_ref":connection_ref,
        "connection_method":"gscc-first-touch-issue" if s["connection"].get("connection_ref_origin")=="GSCC_MINTED_GITHUB_ISSUE" else "gscc-first-touch-runtime",
        "surface_class":"CONTROLLED_INSTRUMENTABLE",
        "wake_channels":["POLL_REPOSITORY"],
      },
      "target":{
        "repository":github.get("repository_full_name"),
        "requested_branch":github.get("branch") or github.get("default_branch"),
      },
      "intent":{
        "entry_action":"REPOSITORY_ACCESS",
        "connection_intent":"READ_ONLY_DISCOVERY",
        "requested_capabilities":["READ_REPOSITORY","READ_GOVERNANCE","READ_STATUS","READ_CONTEXT","READ_CAPABILITIES"],
      },
      "continuity":{
        "requested_logical_agent_alias":_requested_alias(packet),
        "alias_request_provenance":"OWNER_SUPPLIED_ENTRY_INTENT" if _requested_alias(packet) else "NOT_REQUESTED",
        "alias_grants_authority":False,
      },
      "control_capabilities":{
        "heartbeat":True,
        "command_receive":True,
        "command_ack":True,
        "challenge_response":True,
      },
    }

def _pre_gse_dispatch(runtime:dict[str,Any], packet:dict[str,Any])->dict[str,Any]:
    issued=datetime.now(timezone.utc).replace(microsecond=0)
    expires=issued+timedelta(minutes=5)
    seed=f"{runtime['runtime_id']}:{runtime['connection_ref']}:{issued.isoformat()}"
    nonce=_id("GSCC-NONCE-",seed)
    command_id=_id("GSCC-CMD-",seed)
    challenge_id=_id("GSCC-CH-",seed,command_id)
    correlation_id=_id("GSCC-CORR-",command_id,challenge_id)
    dispatch_id=_id("GSCC-CTRL-",runtime["runtime_id"],command_id)
    return {
      "schema":"gscc-control-dispatch/v1",
      "dispatch_id":dispatch_id,
      "kind":"CONTROL_CHALLENGE",
      "status":"READY",
      "target_session_id":runtime["identity_id"],
      "target_connection_ref":runtime["connection_ref"],
      "repository":packet["sections"]["github"].get("repository_full_name"),
      "branch":packet["sections"]["github"].get("branch"),
      "issue_number":runtime["issue_number"],
      "created_at":issued.isoformat(),
      "expires_at":expires.isoformat(),
      "command":{
        "schema":"gscc-control-command/v1",
        "message_id":_id("GSCC-MSG-",dispatch_id),
        "command_id":command_id,
        "correlation_id":correlation_id,
        "command_type":"LIVENESS_CHALLENGE",
        "target_session_id":runtime["identity_id"],
        "issued_at":issued.isoformat(),
        "expires_at":expires.isoformat(),
        "requires_ack":True,
        "payload":{"challenge_id":challenge_id,"nonce":nonce,"issued_at":issued.isoformat(),"expires_at":expires.isoformat()},
      },
      "ack":None,"response":None,
      "invocation_authority_granted":False,"mutation_authority_granted":False,
      "target_layer":"GSCC_PRE_GSE_LOGICAL_SESSION",
    }

def prepare(db:Path,run_id:str,issue_number:int)->dict[str,Any]:
    conn=sqlite3.connect(db); conn.execute("PRAGMA foreign_keys=ON")
    try:
      conn.executescript(MIGRATION.read_text(encoding="utf-8"))
      entry,packet=_packet(conn,run_id)
      connsec=packet["sections"]["connection"]
      arrival_ref=connsec.get("gscc_arrival_ref")
      connection_ref=connsec.get("connection_ref")
      if arrival_ref in (None,"","UNAVAILABLE") or connection_ref in (None,"","UNAVAILABLE"):
          raise ValueError("GSCC arrival identity required")
      runtime_id=_id("GSCC-RUNTIME-",arrival_ref)
      admission=evaluate_admission(_admission(packet,arrival_ref,connection_ref,runtime_id))
      if admission.get("status")!="PREAUTHORIZED":
          raise ValueError(f"admission blocked:{admission.get('reason_code')}")
      created=now_iso()
      conn.execute(
        "INSERT OR REPLACE INTO gscc_session_runtime(runtime_id,run_id,arrival_ref,identity_id,capture_id,issue_number,connection_ref,state,admission_json,last_gate,next_gate,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (runtime_id,run_id,arrival_ref,entry["identity_id"],entry["capture_id"],issue_number,connection_ref,"QUALIFYING",json.dumps(admission,sort_keys=True),"Q1","Q3",created,created),
      )
      conn.commit()
    finally: conn.close()

    identity_id=entry["identity_id"]
    _route(db,runtime_id,"Q1","Q1_VERIFIED",{"admission_id":admission.get("admission_id")},identity_id)
    docs={}
    for p in ("00_GSCC_ENTRY.md","GOVERNANCE.md","docs/control-plane/GSCC_ADMISSION_ACCESS_GATE.md","docs/control-plane/GACR_PROGRAM.md"):
        text=(ROOT/p).read_text(encoding="utf-8"); docs[p]=hashlib.sha256(text.encode()).hexdigest()
    _route(db,runtime_id,"Q3","Q3_VERIFIED",{"documents":docs},identity_id)
    github=packet["sections"]["github"]
    _route(db,runtime_id,"Q4","Q4_VERIFIED",{"repository":github.get("repository_full_name"),"head":github.get("head_sha")},identity_id)
    if github.get("head_sha") in (None,"","UNAVAILABLE"): raise ValueError("exact head unavailable")
    _route(db,runtime_id,"Q5","Q5_VERIFIED",{"head":github.get("head_sha")},identity_id)
    capability={
      "status":"VERIFIED",
      "verified":["READ_REPOSITORY","CONTROLLED_ISSUE_INGRESS"],
      "declared":["COMMAND_RECEIVE","COMMAND_ACK","CHALLENGE_RESPONSE"],
      "evidence_ref":f"gscc-arrival:{arrival_ref}",
      "source":"GSCC_LIVE_FIRST_TOUCH_INGRESS",
    }
    _route(db,runtime_id,"Q8","Q8_VERIFIED",capability,identity_id)

    conn=sqlite3.connect(db)
    try:
      runtime=_load_runtime(conn,runtime_id)
      dispatch=_pre_gse_dispatch(runtime,packet)
      row_id=_id("GSCC-Q9-",runtime_id)
      conn.execute("INSERT OR REPLACE INTO gscc_pre_gse_control_challenges(challenge_row_id,runtime_id,issue_number,dispatch_json,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",(row_id,runtime_id,issue_number,json.dumps(dispatch,sort_keys=True),"READY",created,created))
      conn.execute("UPDATE gscc_session_runtime SET state='WAITING_Q9_ACK',capability_evidence_json=?,last_gate='Q8',next_gate='Q9',updated_at=? WHERE runtime_id=?",(json.dumps(capability,sort_keys=True),now_iso(),runtime_id))
      conn.commit()
    finally: conn.close()
    return {"schema":"gscc-session-runtime/v1","runtime_id":runtime_id,"state":"WAITING_Q9_ACK","last_gate":"Q8","next_gate":"Q9","dispatch":dispatch,"authority_granted":False}

def control(
    db:Path,
    runtime_id:str,
    payload:dict[str,Any],
    observed_at:str,
    *,
    sessions_path:Path=SESSIONS_STATE,
    continuity_path:Path=CONTINUITY_STATE,
    forensics_path:Path=FORENSICS_STATE,
)->dict[str,Any]:
    conn=sqlite3.connect(db)
    try:
      rt=_load_runtime(conn,runtime_id)
      row=conn.execute("SELECT challenge_row_id,dispatch_json,status FROM gscc_pre_gse_control_challenges WHERE runtime_id=?",(runtime_id,)).fetchone()
      if not row: raise ValueError("Q9 challenge missing")
      store={"schema_version":"1.0.0","revision":0,"items":[json.loads(row[1])]}
      result=apply_host_control_event(store,payload,evidence_ref=f"gscc-runtime:{runtime_id}:{payload.get('event')}",observed_at=observed_at)
      dispatch=store["items"][0]; state=rt["state"]
      if payload.get("event")=="command_ack":
          new_state="WAITING_Q9_RESPONSE"
          conn.execute("UPDATE gscc_pre_gse_control_challenges SET dispatch_json=?,status='ACKNOWLEDGED',updated_at=? WHERE challenge_row_id=?",(json.dumps(dispatch,sort_keys=True),now_iso(),row[0]))
          conn.execute("UPDATE gscc_session_runtime SET state=?,updated_at=? WHERE runtime_id=?",(new_state,now_iso(),runtime_id))
          conn.commit()
          return {"runtime_id":runtime_id,"state":new_state,"result":result,"next_gate":"Q9","authority_granted":False}
      if result.get("fresh_liveness") is not True: raise ValueError("fresh challenge response required")
      control_evidence={
        "status":"VERIFIED","state":"REACHABLE","evidence_ref":f"gscc-runtime:{runtime_id}:challenge",
        "dispatch_id":dispatch["dispatch_id"],"command_id":dispatch["command"]["command_id"],"challenge_id":dispatch["command"]["payload"]["challenge_id"],
        "source":"GSCC_PRE_GSE_ISSUE_CHALLENGE","observed_at":observed_at,
      }
      capability=json.loads(rt["capability_evidence_json"])
      capability["verified"]=sorted(set(capability.get("verified",[])+["COMMAND_RECEIVE","COMMAND_ACK","CHALLENGE_RESPONSE"]))
      capability["evidence_ref"]=control_evidence["evidence_ref"]
      conn.execute("UPDATE gscc_pre_gse_control_challenges SET dispatch_json=?,status='COMPLETED',updated_at=? WHERE challenge_row_id=?",(json.dumps(dispatch,sort_keys=True),now_iso(),row[0]))
      conn.execute("UPDATE gscc_session_runtime SET state='Q9_VERIFIED',capability_evidence_json=?,control_evidence_json=?,last_gate='Q9',next_gate='Q10_GSE',updated_at=? WHERE runtime_id=?",(json.dumps(capability,sort_keys=True),json.dumps(control_evidence,sort_keys=True),now_iso(),runtime_id))
      conn.commit()
    finally: conn.close()

    _route(db,runtime_id,"Q9","Q9_VERIFIED",control_evidence,rt["identity_id"])
    conn=sqlite3.connect(db)
    try:
      entry,packet=_packet(conn,rt["run_id"])
      admission=json.loads(rt["admission_json"])
      github=packet["sections"]["github"]
      baseline={"status":"OBSERVED","repository":github.get("repository_full_name"),"observed_head":github.get("head_sha"),"requested_branch":github.get("branch"),"evidence_ref":f"gscc-runtime:{runtime_id}:baseline"}
      gse_state=project_pre_gacr_admission_gse_state(
          admission,
          baseline,
          {"capabilities":capability,"control_channel":control_evidence},
          requested_logical_agent_alias=_requested_alias(packet),
      )
      projection=project_to_gse(conn,identity_id=rt["identity_id"],capture_id=rt["capture_id"],classification=entry["classification"])
      alias_attach_proof=None
      if _requested_alias(packet):
          sessions=(
              json.loads(sessions_path.read_text(encoding="utf-8"))
              if sessions_path.exists() else {"sessions":[]}
          )
          continuity_state=(
              json.loads(continuity_path.read_text(encoding="utf-8"))
              if continuity_path.exists() else default_continuity_state()
          )
          forensics=(
              json.loads(forensics_path.read_text(encoding="utf-8"))
              if forensics_path.exists() else {"items":[]}
          )
          alias_attach_proof=resolve_alias_attach_proof(
              packet,sessions,continuity_state,forensics
          )
      conn.execute(
        "INSERT OR REPLACE INTO gscc_session_bindings(binding_id,arrival_ref,identity_id,gse_identity_id,gacr_session_id,connection_ref,binding_status,binding_level,evidence_ref,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (_id("GSCC-BIND-",rt["arrival_ref"]),rt["arrival_ref"],rt["identity_id"],rt["identity_id"],None,rt["connection_ref"],"GSE_VERIFIED",None,gse_state.get("evidence_ref"),now_iso(),now_iso()),
      )
      conn.execute("UPDATE gscc_session_runtime SET state='GSE_VERIFIED_WAITING_GACR',gse_state_json=?,last_gate='Q10_GSE',next_gate='Q2_GACR',updated_at=? WHERE runtime_id=?",(json.dumps(gse_state,sort_keys=True),now_iso(),runtime_id))
      conn.commit()
    finally: conn.close()
    _route(db,runtime_id,"Q10_GSE","Q10_GSE_VERIFIED",gse_state,rt["identity_id"])
    gacr_attach={
      "schema":"gacr-host-event/v1","event":"attach","provider":packet["sections"]["provider"].get("provider"),
      "connection_ref":rt["connection_ref"],"client_instance_id":_id("GSCC-CLIENT-",rt["arrival_ref"]),
      "agent":alias_attach_proof["logical_agent_id"] if alias_attach_proof else rt["identity_id"],
      "logical_agent_alias":_requested_alias(packet),
      "observed_head":packet["sections"]["github"].get("head_sha"),"branch":packet["sections"]["github"].get("branch"),
      "capabilities":["GACR_AUTO_ATTACH","GACR_PRESENCE_FIRST","COMMAND_RECEIVE","COMMAND_ACK","CHALLENGE_RESPONSE"],
      "wake_channels":["POLL_REPOSITORY"],"last_evidence":control_evidence["evidence_ref"],
      "entry_action":"CONTINUE_GOVERNED_WORK","connection_intent":"OBSERVE","agent_role":"qualification-client",
    }
    if alias_attach_proof:
      gacr_attach.update({
        "same_logical_agent_session_id":alias_attach_proof["same_logical_agent_session_id"],
        "continuity_id":alias_attach_proof["continuity_id"],
        "continuity_evidence_ref":alias_attach_proof["continuity_evidence_ref"],
      })
    return {
      "runtime_id":runtime_id,"state":"GSE_VERIFIED_WAITING_GACR","last_gate":"Q10_GSE","next_gate":"Q2_GACR",
      "gse_state":gse_state,"gse_projection":projection,
      "logical_agent_alias_attach_proof":alias_attach_proof,
      "gacr_attach":gacr_attach,
      "authority_granted":False,
    }


def bind_gacr(
    db:Path,
    runtime_id:str,
    sessions_path:Path,
    current_head:str,
    continuity_path:Path=CONTINUITY_STATE,
)->dict[str,Any]:
    conn=sqlite3.connect(db)
    try:
      rt=_load_runtime(conn,runtime_id)
      if rt["state"]!="GSE_VERIFIED_WAITING_GACR":
          raise ValueError("runtime is not waiting for GACR binding")
      sessions=json.loads(sessions_path.read_text(encoding="utf-8"))
      matches=[
        s for s in (sessions.get("sessions") or [])
        if isinstance(s,dict)
        and rt["connection_ref"] in _session_connection_values(s)
        and s.get("status")=="ACTIVE"
        and ((s.get("relay") or {}).get("state")=="ACTIVE")
      ]
      if len(matches)!=1:
          raise ValueError("exactly one active GACR session required")
      session=matches[0]
      sid=session.get("session_id")
      if not sid: raise ValueError("GACR session id missing")
      entry,packet=_packet(conn,rt["run_id"])
      continuity_state=(
          json.loads(continuity_path.read_text(encoding="utf-8"))
          if continuity_path.exists()
          else default_continuity_state()
      )
      alias_resolution=resolve_alias_binding_intent(packet,sessions,continuity_state)
      if alias_resolution:
          actual_logical_id=_session_logical_agent_id(session)
          if actual_logical_id != alias_resolution["logical_agent_id"]:
              raise ValueError(
                  "GACR alias/session mismatch: "
                  f"alias={alias_resolution['requested_alias']} "
                  f"resolved={alias_resolution['logical_agent_id']} "
                  f"session={actual_logical_id or 'UNAVAILABLE'}"
              )
      conn.execute(
        "UPDATE gscc_session_bindings SET gacr_session_id=?,binding_status='GACR_BOUND',binding_level='EXACT',evidence_ref=?,updated_at=? WHERE arrival_ref=?",
        (sid,f"gacr-session:{sid}",now_iso(),rt["arrival_ref"]),
      )
      conn.commit()
    finally: conn.close()

    _route(
      db,runtime_id,"Q2_GACR","Q2_GACR_VERIFIED",
      {"session_id":sid,"connection_ref":rt["connection_ref"],"logical_agent_alias_resolution":alias_resolution},
      rt["identity_id"],
    )

    admission=json.loads(rt["admission_json"])
    capability=json.loads(rt["capability_evidence_json"])
    control_evidence=json.loads(rt["control_evidence_json"])
    gse_state=json.loads(rt["gse_state_json"])
    github=packet["sections"]["github"]
    repository=github.get("repository_full_name")
    branch=github.get("branch") or github.get("default_branch")

    def fake_github(url:str):
        if url.endswith("/repos/"+repository):
            return {
              "id":github.get("repository_id"),
              "full_name":repository,
              "owner":{"login":github.get("owner_login")},
              "visibility":github.get("visibility"),
              "default_branch":github.get("default_branch"),
              "permissions":github.get("permissions"),
            }
        if "/branches/" in url:
            return {"name":branch,"commit":{"sha":current_head}}
        raise ValueError(f"unexpected github observation URL:{url}")

    governance={}
    for p in ("00_START_HERE.md","GOVERNANCE.md","docs/control-plane/GSCC_ADMISSION_ACCESS_GATE.md","docs/control-plane/GACR_PROGRAM.md"):
        governance[p]=(ROOT/p).read_text(encoding="utf-8")
    claims=json.loads((ROOT/".governance/control-plane-state/gacr-claims.json").read_text(encoding="utf-8"))
    tasks=json.loads((ROOT/".governance/control-plane-state/tasks.json").read_text(encoding="utf-8"))
    access_policy=json.loads((ROOT/".governance/agent-relay/gscc-admission-access-policy.json").read_text(encoding="utf-8"))

    evidence=harvest_qualification_evidence(
      admission,
      github_request_fn=fake_github,
      sessions=sessions,
      claims=claims,
      tasks=tasks,
      governance_documents=governance,
      target_repository=repository,
      requested_branch=branch,
      capability_evidence=capability,
      control_evidence=control_evidence,
      gse_state=gse_state,
      access_policy_document=access_policy,
    )
    if evidence.get("session",{}).get("status")!="BOUND":
        raise ValueError("canonical GACR session not bound in qualification")
    if evidence.get("task",{}).get("status") not in {"RECONCILED","NOT_REQUIRED"}:
        raise ValueError("Q6 task reconciliation incomplete")
    _route(db,runtime_id,"Q6","Q6_VERIFIED",evidence["task"],rt["identity_id"])
    if evidence.get("claim",{}).get("status") not in {"RECONCILED","NOT_REQUIRED"}:
        raise ValueError("Q7 claim reconciliation incomplete")
    _route(db,runtime_id,"Q7","Q7_VERIFIED",evidence["claim"],rt["identity_id"])
    if evidence.get("access_policy",{}).get("status")!="ALLOW":
        raise ValueError("Q11 access policy did not allow")
    _route(db,runtime_id,"Q11","Q11_VERIFIED",evidence["access_policy"],rt["identity_id"])
    grant=evaluate_access_grant(admission,evidence)
    if grant.get("status")!="AUTHORIZED":
        raise ValueError(f"Q12 access grant blocked:{grant.get('reason_code')}")
    _route(db,runtime_id,"Q12","Q12_VERIFIED",{"grant_id":grant.get("grant_id"),"access_class":grant.get("access_class")},rt["identity_id"])

    conn=sqlite3.connect(db)
    try:
      conn.execute("UPDATE gscc_session_runtime SET state='READY_FOR_F1',qualification_evidence_json=?,access_grant_json=?,last_gate='Q12',next_gate='F1',updated_at=? WHERE runtime_id=?",(json.dumps(evidence,sort_keys=True),json.dumps(grant,sort_keys=True),now_iso(),runtime_id))
      conn.commit()
    finally: conn.close()
    return {
      "runtime_id":runtime_id,"state":"READY_FOR_F1","last_gate":"Q12","next_gate":"F1",
      "gacr_session_id":sid,"access_grant":grant,
      "logical_agent_alias_resolution":alias_resolution,
      "start_here_status":"NOT_YET_APPLICABLE",
      "authority_granted":False,
    }


def release_f1(db:Path,runtime_id:str,receipt:dict[str,Any],current_head:str)->dict[str,Any]:
    conn=sqlite3.connect(db)
    try:
      rt=_load_runtime(conn,runtime_id)
      if rt["state"]!="READY_FOR_F1":
          raise ValueError("runtime is not ready for F1 release")
      if receipt.get("schema")!="gscc-function-exposure-receipt/v1":
          raise ValueError("F1 receipt schema invalid")
      if receipt.get("status")!="VALIDATED" or receipt.get("exposable") is not True:
          raise ValueError("F1 exposure not validated")
      if receipt.get("reason_code")!="EXPOSURE_VALIDATED":
          raise ValueError("F1 exposure reason invalid")
      if receipt.get("connection_ref")!=rt["connection_ref"]:
          raise ValueError("F1 connection_ref mismatch")
      grant=json.loads(rt["access_grant_json"] or "{}")
      if receipt.get("access_grant_id")!=grant.get("grant_id"):
          raise ValueError("F1 access grant mismatch")
      if receipt.get("requested_head")!=current_head:
          raise ValueError("F1 current head mismatch")
      if grant.get("bound_head")!=current_head:
          raise ValueError("F1 grant head mismatch")
      row=conn.execute(
          "SELECT gacr_session_id,binding_status,binding_level FROM gscc_session_bindings WHERE arrival_ref=?",
          (rt["arrival_ref"],),
      ).fetchone()
      if not row or row[1]!="GACR_BOUND" or row[2]!="EXACT":
          raise ValueError("exact GACR binding required for release")
      gacr_session_id=row[0]
      if not gacr_session_id or receipt.get("session_id")!=gacr_session_id or grant.get("session_id")!=gacr_session_id:
          raise ValueError("F1 GACR session mismatch")
      route_authority=receipt.get("route_authority") or {}
      if route_authority.get("session_id")!=gacr_session_id:
          raise ValueError("F1 route authority session mismatch")
      exposure_ref=receipt.get("exposure_receipt")
      if not isinstance(exposure_ref,str) or not exposure_ref.startswith("GSCC-EXPOSURE-"):
          raise ValueError("F1 exposure receipt reference missing")
      evidence={
        "exposure_receipt":exposure_ref,
        "tool_name":receipt.get("tool_name"),
        "surface":receipt.get("surface"),
        "connection_ref":rt["connection_ref"],
        "gacr_session_id":gacr_session_id,
        "access_grant_id":grant.get("grant_id"),
        "head":current_head,
      }
    finally:
      conn.close()

    _route(db,runtime_id,"F1","F1_VERIFIED",evidence,rt["identity_id"])
    release_evidence={
      "schema":"gscc-normal-governance-release/v1",
      "runtime_id":runtime_id,
      "arrival_ref":rt["arrival_ref"],
      "identity_id":rt["identity_id"],
      "connection_ref":rt["connection_ref"],
      "gacr_session_id":gacr_session_id,
      "f1_exposure_receipt":exposure_ref,
      "released_head":current_head,
      "next_authority":"00_START_HERE.md",
      "status":"RELEASED",
    }
    _route(db,runtime_id,"00_START_HERE.md","RELEASED",release_evidence,rt["identity_id"])

    conn=sqlite3.connect(db)
    try:
      conn.execute(
        "UPDATE gscc_session_runtime SET state='RELEASED_TO_NORMAL_GOVERNANCE',last_gate='00_START_HERE.md',next_gate=NULL,updated_at=? WHERE runtime_id=?",
        (now_iso(),runtime_id),
      )
      conn.commit()
    finally:
      conn.close()
    return {
      "schema":"gscc-normal-governance-release/v1",
      "runtime_id":runtime_id,
      "state":"RELEASED_TO_NORMAL_GOVERNANCE",
      "last_gate":"00_START_HERE.md",
      "next_gate":None,
      "start_here_status":"APPLICABLE",
      "gacr_session_id":gacr_session_id,
      "connection_ref":rt["connection_ref"],
      "exposure_receipt":exposure_ref,
      "released_head":current_head,
      "release_evidence":release_evidence,
      "authority_granted":False,
    }

def main()->None:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
    a=sub.add_parser("prepare"); a.add_argument("--db",required=True); a.add_argument("--run-id",required=True); a.add_argument("--issue-number",required=True,type=int)
    b=sub.add_parser("control"); b.add_argument("--db",required=True); b.add_argument("--runtime-id",required=True); b.add_argument("--payload-json",required=True); b.add_argument("--observed-at",required=True)
    g=sub.add_parser("bind-gacr"); g.add_argument("--db",required=True); g.add_argument("--runtime-id",required=True); g.add_argument("--sessions",required=True); g.add_argument("--current-head",required=True)
    r=sub.add_parser("release-f1"); r.add_argument("--db",required=True); r.add_argument("--runtime-id",required=True); r.add_argument("--receipt-json",required=True); r.add_argument("--current-head",required=True)
    s=sub.add_parser("status"); s.add_argument("--db",required=True); s.add_argument("--runtime-id",required=True)
    args=p.parse_args()
    if args.command=="prepare": result=prepare(Path(args.db),args.run_id,args.issue_number)
    elif args.command=="control": result=control(Path(args.db),args.runtime_id,json.loads(args.payload_json),args.observed_at)
    elif args.command=="bind-gacr": result=bind_gacr(Path(args.db),args.runtime_id,Path(args.sessions),args.current_head)
    elif args.command=="release-f1": result=release_f1(Path(args.db),args.runtime_id,json.loads(args.receipt_json),args.current_head)
    else:
        conn=sqlite3.connect(args.db)
        try: result=_load_runtime(conn,args.runtime_id)
        finally: conn.close()
    print(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True))

if __name__=="__main__": main()
