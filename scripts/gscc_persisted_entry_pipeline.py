#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from first_touch_agent_transport_extractor import extract
from first_touch_connection_completeness import build_packet as build_completeness
from first_touch_field_block_gate import ingest_capture, install_schema, insert_catalog
from first_touch_entry_contract import evaluate
from gscc.first_touch_store import find_identity, register_first_touch
from gscc.first_touch_handoff import build_handoff

ROOT=Path(__file__).resolve().parents[1]
MIGRATION=ROOT/".governance"/"control-plane-db"/"008_gscc_observable_entry_pipeline.sql"
IDENTITY_MIGRATION=ROOT/".governance"/"control-plane-db"/"010_gscc_arrival_session_identity.sql"

def now_iso()->str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def digest(value:str)->str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def packet_identity(packet:dict[str,Any])->tuple[str,str|None]:
    candidates=packet.get("identity",{}).get("candidates",[])
    if not candidates:
        return "UNKNOWN",None
    sections=packet.get("sections") if isinstance(packet.get("sections"),dict) else {}
    connection=sections.get("connection") if isinstance(sections.get("connection"),dict) else {}
    origin=connection.get("connection_ref_origin")
    first=candidates[0]
    field=str(first.get("field") or "")
    value=first.get("value")
    if not value:
        return "UNKNOWN",None
    family={
      "session.conversation_ref":"provider_conversation_ref",
      "session.session_ref":"provider_session_ref",
      "client.client_instance_id":"conversation_scoped_client_instance_id",
    }.get(field)
    if field=="connection.connection_ref":
        family="gscc_arrival_ref" if isinstance(origin,str) and origin.startswith("GSCC_MINTED_") else "provider_connection_ref"
    if not family:
        return "WEAK",None
    return "STRONG",f"{family}:{value}"

def packet_to_capture(packet:dict[str,Any], github:dict[str,Any], *, capture_id:str, observed_at:str)->dict[str,Any]:
    sections=packet.get("sections") if isinstance(packet.get("sections"),dict) else {}
    github_section=sections.get("github") if isinstance(sections.get("github"),dict) else {}
    provider_section=sections.get("provider") if isinstance(sections.get("provider"),dict) else {}
    agent_section=sections.get("agent") if isinstance(sections.get("agent"),dict) else {}
    connection_section=sections.get("connection") if isinstance(sections.get("connection"),dict) else {}
    session_section=sections.get("session") if isinstance(sections.get("session"),dict) else {}
    client_section=sections.get("client") if isinstance(sections.get("client"),dict) else {}
    tool_section=sections.get("tool") if isinstance(sections.get("tool"),dict) else {}

    repository=github_section.get("repository_full_name")
    actor=github_section.get("actor_login")
    branch=github_section.get("branch")
    head=github_section.get("head_sha")
    connection_ref=connection_section.get("connection_ref")
    conversation_ref=session_section.get("conversation_ref")
    session_ref=session_section.get("session_ref")
    client_instance_id=client_section.get("client_instance_id")

    def clean(value:Any)->Any:
        return None if value in (None,"","UNAVAILABLE","UNKNOWN") else value

    return {
      "schema":"first-touch-exhaustive-capture/v1",
      "capture_id":capture_id,
      "observed_at":observed_at,
      "repository":clean(repository),
      "actor":clean(actor),
      "provider":clean(provider_section.get("provider")),
      "safe_ingress":{
        "schema":"gscc-first-touch-safe-ingress/v1",
        "status":"VALID" if any(clean(x) for x in (conversation_ref,session_ref,connection_ref,client_instance_id)) else "INVALID",
        "ingress_type":"FIRST_TOUCH",
        "connection_ref":clean(connection_ref),
        "client_instance_id":clean(client_instance_id),
        "conversation_ref":clean(conversation_ref),
        "provider_conversation_ref":clean(conversation_ref),
        "session_ref":clean(session_ref),
        "source":"GSCC_OBSERVABLE_PACKET",
        "source_method":"PROVIDER_ENVELOPE_PLUS_GITHUB",
        "observed_at":observed_at,
        "freeform_body_persisted":False,
      },
      "github_event":{
        "event_type":"provider_first_tool",
        "sender":{"login":clean(actor)},
        "repository":{
          "id":github_section.get("repository_id"),
          "full_name":clean(repository),
          "default_branch":clean(github_section.get("default_branch")),
          "owner":{
            "login":clean(github_section.get("owner_login")),
            "id":github_section.get("owner_id"),
          },
        },
        "first_tool":tool_section,
      },
      "environment":{
        "GITHUB_EVENT_NAME":"provider_first_tool",
        "GITHUB_REPOSITORY":clean(repository),
        "GITHUB_ACTOR":clean(actor),
        "GITHUB_REF_NAME":clean(branch),
        "GITHUB_SHA":clean(head),
      },
      "observable_packet":packet,
      "api_attempts":[
        {
          "name":"repository_metadata",
          "http_status":200,
          "response":github,
        }
      ],
      "admission":{"phase":"PRE_Q1","status":"OBSERVABLE_PACKET_PERSISTED"},
      "mutation_authority_granted":False,
      "interpretation_applied":False,
    }

def install_pipeline_schema(conn:sqlite3.Connection)->None:
    install_schema(conn)
    insert_catalog(conn)
    conn.executescript(MIGRATION.read_text(encoding="utf-8"))
    conn.executescript(IDENTITY_MIGRATION.read_text(encoding="utf-8"))

def run_pipeline(provider_envelope:dict[str,Any], github:dict[str,Any], db_path:Path, *, run_id:str, observed_at:str|None=None)->dict[str,Any]:
    observed_at=observed_at or now_iso()
    packet=extract(provider_envelope,github)
    packet_id=f"PKT-{digest(run_id)[:20]}"
    capture_id=f"FTC-{digest(run_id+':capture')[:20]}"
    capture=packet_to_capture(packet,github,capture_id=capture_id,observed_at=observed_at)

    db_path.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        install_pipeline_schema(conn)
        ingest_capture(conn,capture,source_ref=f"pipeline:{run_id}",evaluated_at=observed_at)
        conn.commit()
    finally:
        conn.close()

    with tempfile.TemporaryDirectory(prefix="gscc-entry-pipeline-") as td:
        root=Path(td)
        cap_path=root/"capture.json"
        complete_path=root/"completeness.json"
        cap_path.write_text(json.dumps(capture,ensure_ascii=False,sort_keys=True),encoding="utf-8")
        completeness=build_completeness(None,complete_path,capture_path=cap_path)

        strength,anchor=packet_identity(packet)
        conn=sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            seen=find_identity(conn,anchor) is not None if anchor else False
        finally:
            conn.close()

        entry=evaluate(
            complete_path,
            db_path,
            identity_strength=strength,
            identity_anchor=anchor,
            first_touch_seen=seen,
        )

    classification=entry["classification"]
    identity_id=None
    handoff=None

    conn=sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        install_pipeline_schema(conn)
        packet_json=json.dumps(packet,ensure_ascii=False,sort_keys=True,separators=(",",":"))
        sections=packet.get("sections") if isinstance(packet.get("sections"),dict) else {}
        connection_section=sections.get("connection") if isinstance(sections.get("connection"),dict) else {}
        arrival_ref=connection_section.get("gscc_arrival_ref")
        connection_ref=connection_section.get("connection_ref")
        connection_origin=connection_section.get("connection_ref_origin")
        subject_ref=connection_section.get("transport_subject_ref")
        if arrival_ref not in (None,"","UNAVAILABLE"):
            conn.execute(
              "INSERT INTO gscc_arrival_instances(arrival_ref,connection_ref,connection_ref_origin,transport_subject_ref,repository,resumable,identity_id,first_run_id,last_run_id,first_seen_at,last_seen_at,status,provider_private_identity_inferred) "
              "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,0) "
              "ON CONFLICT(arrival_ref) DO UPDATE SET last_run_id=excluded.last_run_id,last_seen_at=excluded.last_seen_at,status=excluded.status",
              (
                arrival_ref,connection_ref,connection_origin,subject_ref,capture.get("repository"),
                1 if str(connection_origin)=="GSCC_MINTED_GITHUB_ISSUE" else 0,
                None,run_id,run_id,observed_at,observed_at,"OBSERVED",
              ),
            )
            conn.execute(
              "INSERT OR REPLACE INTO gscc_arrival_events(event_id,arrival_ref,run_id,event_type,gate_id,status,evidence_json,observed_at) VALUES(?,?,?,?,?,?,?,?)",
              (
                f"{run_id}:ARRIVAL",arrival_ref,run_id,"ARRIVAL_CAPTURE",None,"OBSERVED",
                json.dumps({"packet_id":packet_id,"capture_id":capture_id},sort_keys=True),observed_at,
              ),
            )

        conn.execute(
          "INSERT OR REPLACE INTO gscc_observable_packets(packet_id,capture_id,schema_id,repository,observed_at,identity_strength,classification,packet_json,packet_sha256,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
          (
            packet_id,capture_id,packet.get("schema","UNKNOWN"),capture.get("repository"),observed_at,
            strength,classification,packet_json,digest(packet_json),observed_at,
          ),
        )

        if entry["status"]=="ENTRY_READY_FOR_Q1":
            identity=register_first_touch(
                conn,
                anchor=str(anchor),
                identity_strength=strength,
                capture_id=capture_id,
            )
            classification=identity["classification"]
            identity_id=identity["identity_id"]
            if arrival_ref not in (None,"","UNAVAILABLE"):
                conn.execute(
                  "UPDATE gscc_arrival_instances SET identity_id=?,status='IDENTITY_BOUND',last_seen_at=? WHERE arrival_ref=?",
                  (identity_id,observed_at,arrival_ref),
                )
            entry["classification"]=classification
            entry["gscc_identity_id"]=identity_id
            entry["gscc_first_capture_id"]=identity["first_capture_id"]
            entry["next_gate"]="Q1"
            conn.commit()

            entry_path=Path(tempfile.gettempdir())/f"{run_id}-entry.json"
            entry_path.write_text(json.dumps(entry),encoding="utf-8")
            try:
                handoff=build_handoff(entry_path,db_path)
            finally:
                entry_path.unlink(missing_ok=True)

        blocked=entry.get("reasons") or []
        next_gate=(handoff or {}).get("next_gate") if handoff else None
        handoff_status=(handoff or {}).get("status") if handoff else None
        conn.execute(
          "INSERT OR REPLACE INTO gscc_entry_pipeline_runs(run_id,packet_id,capture_id,identity_id,classification,entry_status,handoff_status,next_gate,blocked_reason_json,started_at,completed_at,authority_granted) VALUES(?,?,?,?,?,?,?,?,?,?,?,0)",
          (
            run_id,packet_id,capture_id,identity_id,classification,entry["status"],handoff_status,next_gate,
            json.dumps(blocked,ensure_ascii=False,sort_keys=True),observed_at,now_iso(),
          ),
        )
        conn.commit()
    finally:
        conn.close()

    return {
      "schema":"gscc-persisted-entry-pipeline/v1",
      "run_id":run_id,
      "packet_id":packet_id,
      "capture_id":capture_id,
      "packet_summary":packet["summary"],
      "identity_strength":strength,
      "identity_anchor_present":bool(anchor),
      "classification":classification,
      "entry_status":entry["status"],
      "handoff":handoff,
      "next_gate":(handoff or {}).get("next_gate") if handoff else None,
      "blocked_reasons":entry.get("reasons") or [],
      "stored_in_database":True,
      "gse_state":"NOT_YET_ENTERED",
      "gacr_state":"NOT_YET_ENTERED",
      "authority_granted":False,
    }

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--provider-envelope",required=True)
    p.add_argument("--github",required=True)
    p.add_argument("--db",required=True)
    p.add_argument("--run-id",required=True)
    p.add_argument("--observed-at")
    a=p.parse_args()
    result=run_pipeline(
      json.loads(Path(a.provider_envelope).read_text(encoding="utf-8")),
      json.loads(Path(a.github).read_text(encoding="utf-8")),
      Path(a.db),
      run_id=a.run_id,
      observed_at=a.observed_at,
    )
    print(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
