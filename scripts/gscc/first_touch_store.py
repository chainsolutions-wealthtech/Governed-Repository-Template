from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from gscc.gse_projection import apply_session_event

SCHEMA="gscc-first-touch-identity/v1"

def _digest(value:str)->str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def _identity_id(anchor:str)->str:
    return "GSCC-ID-"+_digest(anchor)[:24]

def find_identity(conn:sqlite3.Connection, anchor:str|None)->dict[str,Any]|None:
    if not anchor:
        return None
    row=conn.execute(
        "SELECT identity_id,anchor_sha256,identity_strength,first_capture_id,first_observed_at,last_capture_id,last_seen_at,status "
        "FROM gscc_conversation_identities WHERE anchor_sha256=?",
        (_digest(anchor),),
    ).fetchone()
    if not row:
        return None
    keys=("identity_id","anchor_sha256","identity_strength","first_capture_id","first_observed_at","last_capture_id","last_seen_at","status")
    return dict(zip(keys,row))

def _capture(conn:sqlite3.Connection,capture_id:str)->dict[str,Any]:
    row=conn.execute(
        "SELECT observed_at,repository,raw_json FROM first_touch_capture_records WHERE capture_id=?",
        (capture_id,),
    ).fetchone()
    if not row:
        raise ValueError("capture not found")
    return {"observed_at":row[0],"repository":row[1],"raw":json.loads(row[2])}

def register_first_touch(
    conn:sqlite3.Connection,
    *,
    anchor:str,
    identity_strength:str,
    capture_id:str,
)->dict[str,Any]:
    existing=find_identity(conn,anchor)
    capture=_capture(conn,capture_id)
    observed_at=capture["observed_at"]
    if existing:
        conn.execute(
            "UPDATE gscc_conversation_identities SET last_capture_id=?,last_seen_at=?,status='ACTIVE' WHERE identity_id=?",
            (capture_id,observed_at,existing["identity_id"]),
        )
        return {"classification":"CONTINUATION","identity_id":existing["identity_id"],"first_capture_id":existing["first_capture_id"]}

    if identity_strength not in {"EXACT","STRONG"}:
        raise ValueError("strong GSCC conversation identity required")
    identity_id=_identity_id(anchor)
    conn.execute(
        "INSERT INTO gscc_conversation_identities(identity_id,anchor_sha256,identity_strength,first_capture_id,first_observed_at,last_capture_id,last_seen_at,status) "
        "VALUES(?,?,?,?,?,?,?,'FIRST_TOUCH_CONSUMED')",
        (identity_id,_digest(anchor),identity_strength,capture_id,observed_at,capture_id,observed_at),
    )
    raw_json=json.dumps(capture["raw"],ensure_ascii=False,sort_keys=True,separators=(",",":"))
    conn.execute(
        "INSERT INTO gscc_first_touch_snapshots(identity_id,capture_id,snapshot_json,snapshot_sha256,created_at) VALUES(?,?,?,?,?)",
        (identity_id,capture_id,raw_json,_digest(raw_json),observed_at),
    )
    return {"classification":"FIRST_TOUCH","identity_id":identity_id,"first_capture_id":capture_id}

def project_to_gse(
    conn:sqlite3.Connection,
    *,
    identity_id:str,
    capture_id:str,
    classification:str,
)->dict[str,Any]:
    capture=_capture(conn,capture_id)
    raw=capture["raw"]
    env=raw.get("environment") if isinstance(raw.get("environment"),dict) else {}
    branch=env.get("GITHUB_REF_NAME")
    head=env.get("GITHUB_SHA")
    event_type="SESSION_ATTACH" if classification=="FIRST_TOUCH" else "SESSION_RESUME"
    existing=conn.execute(
        "SELECT session_twin_json,revision FROM gse_session_twins WHERE identity_id=?",
        (identity_id,),
    ).fetchone()
    previous=json.loads(existing[0]) if existing else None
    projection=apply_session_event(
        previous,
        identity_id=identity_id,
        event_type=event_type,
        observed_at=capture["observed_at"],
        repository=capture["repository"],
        branch=branch,
        observed_head=head,
        last_action="GSCC_FIRST_TOUCH" if classification=="FIRST_TOUCH" else "GSCC_CONTINUATION",
        event_id=f"{capture_id}:{event_type}",
    )
    twin=projection["session_twin"]
    revision=(int(existing[1])+1) if existing else 1
    encoded=json.dumps(twin,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    conn.execute(
        "INSERT INTO gse_session_twins(identity_id,session_twin_json,revision,last_event_type,updated_at) VALUES(?,?,?,?,?) "
        "ON CONFLICT(identity_id) DO UPDATE SET session_twin_json=excluded.session_twin_json,revision=excluded.revision,last_event_type=excluded.last_event_type,updated_at=excluded.updated_at",
        (identity_id,encoded,revision,event_type,capture["observed_at"]),
    )
    return {
        "schema":"gscc-gse-first-touch-projection/v1",
        "identity_id":identity_id,
        "event_type":event_type,
        "revision":revision,
        "session_twin":twin,
        "gacr_required":False,
        "authority_granted":False,
    }