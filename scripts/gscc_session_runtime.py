#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from gscc.admission import evaluate_admission, evaluate_access_grant
from gscc.first_touch_store import project_to_gse
from gscc_post_q1_gate_router import route_gate
from gscc_gacr.issue_control_bridge import apply_host_control_event
from gscc_gacr.admission_gse_projection import project_pre_gacr_admission_gse_state

ROOT=Path(__file__).resolve().parents[1]
MIGRATION=ROOT/".governance"/"control-plane-db"/"011_gscc_session_runtime.sql"

def now_iso()->str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _id(prefix:str,*parts:Any)->str:
    raw=":".join(str(x) for x in parts)
    return prefix+hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

def _load_runtime(conn:sqlite3.Connection, runtime_id:str)->dict[str,Any]:
    row=conn.execute("SELECT runtime_id,run_id,arrival_ref,identity_id,capture_id,issue_number,connection_ref,state,admission_json,capability_evidence_json,control_evidence_json,gse_state_json,access_grant_json,last_gate,next_gate,created_at,updated_at FROM gscc_session_runtime WHERE runtime_id=?",(runtime_id,)).fetchone()
    if not row: raise ValueError("runtime not found")
    keys=("runtime_id","run_id","arrival_ref","identity_id","capture_id","issue_number","connection_ref","state","admission_json","capability_evidence_json","control_evidence_json","gse_state_json","access_grant_json","last_gate","next_gate","created_at","updated_at")
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
      "continuity":{},
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

def control(db:Path,runtime_id:str,payload:dict[str,Any],observed_at:str)->dict[str,Any]:
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
      gse_state=project_pre_gacr_admission_gse_state(admission,baseline,{"capabilities":capability,"control_channel":control_evidence})
      projection=project_to_gse(conn,identity_id=rt["identity_id"],capture_id=rt["capture_id"],classification=entry["classification"])
      conn.execute(
        "INSERT OR REPLACE INTO gscc_session_bindings(binding_id,arrival_ref,identity_id,gse_identity_id,gacr_session_id,connection_ref,binding_status,binding_level,evidence_ref,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (_id("GSCC-BIND-",rt["arrival_ref"]),rt["arrival_ref"],rt["identity_id"],rt["identity_id"],None,rt["connection_ref"],"GSE_VERIFIED",None,gse_state.get("evidence_ref"),now_iso(),now_iso()),
      )
      conn.execute("UPDATE gscc_session_runtime SET state='GSE_VERIFIED_WAITING_GACR',gse_state_json=?,last_gate='Q10_GSE',next_gate='Q2_GACR',updated_at=? WHERE runtime_id=?",(json.dumps(gse_state,sort_keys=True),now_iso(),runtime_id))
      conn.commit()
    finally: conn.close()
    _route(db,runtime_id,"Q10_GSE","Q10_GSE_VERIFIED",gse_state,rt["identity_id"])
    return {
      "runtime_id":runtime_id,"state":"GSE_VERIFIED_WAITING_GACR","last_gate":"Q10_GSE","next_gate":"Q2_GACR",
      "gse_state":gse_state,"gse_projection":projection,
      "gacr_attach":{
        "schema":"gacr-host-event/v1","event":"attach","provider":packet["sections"]["provider"].get("provider"),
        "connection_ref":rt["connection_ref"],"client_instance_id":_id("GSCC-CLIENT-",rt["arrival_ref"]),
        "agent":rt["identity_id"],"observed_head":packet["sections"]["github"].get("head_sha"),"branch":packet["sections"]["github"].get("branch"),
        "capabilities":["GACR_AUTO_ATTACH","GACR_PRESENCE_FIRST","COMMAND_RECEIVE","COMMAND_ACK","CHALLENGE_RESPONSE"],
        "wake_channels":["POLL_REPOSITORY"],"last_evidence":control_evidence["evidence_ref"],
      },
      "authority_granted":False,
    }

def main()->None:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
    a=sub.add_parser("prepare"); a.add_argument("--db",required=True); a.add_argument("--run-id",required=True); a.add_argument("--issue-number",required=True,type=int)
    b=sub.add_parser("control"); b.add_argument("--db",required=True); b.add_argument("--runtime-id",required=True); b.add_argument("--payload-json",required=True); b.add_argument("--observed-at",required=True)
    s=sub.add_parser("status"); s.add_argument("--db",required=True); s.add_argument("--runtime-id",required=True)
    args=p.parse_args()
    if args.command=="prepare": result=prepare(Path(args.db),args.run_id,args.issue_number)
    elif args.command=="control": result=control(Path(args.db),args.runtime_id,json.loads(args.payload_json),args.observed_at)
    else:
        conn=sqlite3.connect(args.db)
        try: result=_load_runtime(conn,args.runtime_id)
        finally: conn.close()
    print(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True))

if __name__=="__main__": main()
