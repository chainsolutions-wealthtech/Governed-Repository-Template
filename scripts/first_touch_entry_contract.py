#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from gscc.first_touch_store import find_identity, project_to_gse, register_first_touch

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/".governance"/"control-plane-state"/"first-touch-entry-contract.json"

def rank(s:str)->int:
    return {"EMPTY":0,"UNAVAILABLE":0,"PARTIAL":1,"PRESENT":2,"SUFFICIENT":3,"VERIFIED":4,"STALE":1,"CONFLICTING":1}.get(s,0)

def anchor_digest(anchor:str)->str:
    return hashlib.sha256(anchor.encode("utf-8")).hexdigest()

def discover_identity(capture_path:Path|None):
    if capture_path is None:
        return "UNKNOWN", None
    capture=json.loads(capture_path.read_text(encoding="utf-8"))
    event=capture.get("github_event") or {}
    comment=event.get("comment") or {}
    body=str(comment.get("body") or "").strip()
    for prefix in ("/gscc-admission ", "/gscc-first-touch "):
        if body.startswith(prefix):
            try:
                env=json.loads(body[len(prefix):].strip())
            except Exception:
                continue
            session=env.get("session") or {}
            connection=env.get("connection") or {}
            client=env.get("client") or {}
            conversation_ref=session.get("conversation_ref") or session.get("provider_conversation_ref")
            if conversation_ref and str(conversation_ref).upper() not in {"UNAVAILABLE","UNKNOWN","NOT_EXPOSED"}:
                return "EXACT", f"provider_conversation_ref:{conversation_ref}"
            connection_ref=connection.get("connection_ref")
            if connection_ref and str(connection_ref).upper() not in {"UNAVAILABLE","UNKNOWN","NOT_EXPOSED"}:
                return "STRONG", f"provider_connection_ref:{connection_ref}"
            client_id=client.get("client_instance_id")
            if client_id and str(client_id).upper() not in {"UNAVAILABLE","UNKNOWN","NOT_EXPOSED"}:
                return "STRONG", f"conversation_scoped_client_instance_id:{client_id}"
    return "WEAK", None

def evaluate(completeness_path:Path, db_path:Path, *, identity_strength:str, identity_anchor:str|None, first_touch_seen:bool):
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    comp=json.loads(completeness_path.read_text(encoding="utf-8"))
    conn=sqlite3.connect(db_path)
    try:
        row=conn.execute("SELECT capture_id FROM first_touch_capture_records ORDER BY rowid DESC LIMIT 1").fetchone()
        if not row:
            raise ValueError("no capture in database")
        capture_id=row[0]
        statuses=dict(conn.execute(
            "SELECT block_id,status FROM first_touch_capture_block_status WHERE capture_id=?",
            (capture_id,),
        ).fetchall())
    finally:
        conn.close()

    reasons=[]
    if not comp.get("complete_accounting"):
        reasons.append("INCOMPLETE_ACCOUNTING")
    if int(comp.get("silent_missing_count",0)) != 0:
        reasons.append("SILENT_MISSING_FIELDS")
    if identity_strength not in contract["conversation_identity"]["accepted_strengths"]:
        reasons.append("INSUFFICIENT_CONVERSATION_IDENTITY")
    if not identity_anchor:
        reasons.append("MISSING_CONVERSATION_IDENTITY_ANCHOR")

    missing_blocks=[]
    for block_id, minimum in contract["critical_blocks"].items():
        status=statuses.get(block_id,"EMPTY")
        if rank(status) < rank(minimum):
            missing_blocks.append({"block_id":block_id,"status":status,"minimum":minimum})
    if missing_blocks:
        reasons.append("REQUIRED_ENTRY_BLOCKS_UNSATISFIED")

    classification="CONTINUATION" if first_touch_seen else "FIRST_TOUCH"
    if reasons and not first_touch_seen:
        classification="UNRESOLVED_ENTRY"

    return {
        "schema":"first-touch-entry-contract-evaluation/v1",
        "loop_name":"GSCC–GSE–GACR Connection Loop",
        "capture_id":capture_id,
        "classification":classification,
        "identity_strength":identity_strength,
        "identity_anchor":identity_anchor,
        "identity_anchor_sha256":anchor_digest(identity_anchor) if identity_anchor else None,
        "first_touch_seen":first_touch_seen,
        "common_entry_blocks":{b:statuses.get(b,"EMPTY") for b in contract["common_entry_blocks"]},
        "missing_critical_blocks":missing_blocks,
        "complete_accounting":bool(comp.get("complete_accounting")),
        "silent_missing_count":int(comp.get("silent_missing_count",0)),
        "status":"ENTRY_READY_FOR_Q1" if not reasons else "ENTRY_BLOCKED",
        "reasons":reasons,
        "create_first_touch_snapshot":(not reasons and not first_touch_seen),
        "authority_granted":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--completeness",required=True)
    p.add_argument("--db",required=True)
    p.add_argument("--identity-strength",choices=["EXACT","STRONG","WEAK","AMBIGUOUS","UNKNOWN"])
    p.add_argument("--identity-anchor")
    p.add_argument("--capture")
    p.add_argument("--output",required=True)
    a=p.parse_args()

    strength=a.identity_strength
    anchor=a.identity_anchor
    if not strength:
        strength, discovered_anchor=discover_identity(Path(a.capture) if a.capture else None)
        if not anchor:
            anchor=discovered_anchor

    db_path=Path(a.db)
    conn=sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        seen=find_identity(conn,anchor) is not None if anchor else False
    finally:
        conn.close()

    result=evaluate(
        Path(a.completeness),
        db_path,
        identity_strength=strength or "UNKNOWN",
        identity_anchor=anchor,
        first_touch_seen=seen,
    )

    if result["status"]=="ENTRY_READY_FOR_Q1":
        conn=sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            identity=register_first_touch(
                conn,
                anchor=str(anchor),
                identity_strength=str(strength),
                capture_id=str(result["capture_id"]),
            )
            projection=project_to_gse(
                conn,
                identity_id=identity["identity_id"],
                capture_id=str(result["capture_id"]),
                classification=identity["classification"],
            )
            conn.commit()
        finally:
            conn.close()
        result["classification"]=identity["classification"]
        result["first_touch_seen"]=identity["classification"]=="CONTINUATION"
        result["create_first_touch_snapshot"]=identity["classification"]=="FIRST_TOUCH"
        result["gscc_identity_id"]=identity["identity_id"]
        result["gscc_first_capture_id"]=identity["first_capture_id"]
        result["gse_projection"]={
            "event_type":projection["event_type"],
            "revision":projection["revision"],
            "identity_id":projection["identity_id"],
            "gacr_required":projection["gacr_required"],
        }

    Path(a.output).write_text(
        json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
