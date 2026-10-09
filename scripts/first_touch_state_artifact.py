#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import json
import os
import sqlite3
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

STATE_NAME_PREFIX="first-touch-state-"

RUNTIME_STATE_RANK={
    "WAITING_Q9_ACK":10,
    "WAITING_Q9_RESPONSE":20,
    "WAITING_Q9_RECHALLENGE_ACK":25,
    "WAITING_Q9_RECHALLENGE_RESPONSE":26,
    "Q9_VERIFIED":30,
    "GSE_VERIFIED_WAITING_GACR":40,
    "READY_FOR_F1":50,
    "RELEASED_TO_NORMAL_GOVERNANCE":60,
}


def _request_json(url:str, token:str):
    req=urllib.request.Request(url,headers={
        "Accept":"application/vnd.github+json",
        "Authorization":f"Bearer {token}",
        "X-GitHub-Api-Version":"2022-11-28",
        "User-Agent":"gscc-first-touch-state",
    })
    with urllib.request.urlopen(req,timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _artifact_blob(download_url:str, token:str)->bytes:
    req=urllib.request.Request(download_url,headers={
        "Authorization":f"Bearer {token}",
        "Accept":"application/vnd.github+json",
        "User-Agent":"gscc-first-touch-state",
    })
    opener=urllib.request.build_opener(_NoRedirect)
    try:
        response=opener.open(req,timeout=20)
    except urllib.error.HTTPError as exc:
        if exc.code not in {301,302,303,307,308}:
            raise
        location=exc.headers.get("Location")
        if not location:
            raise
    else:
        location=response.headers.get("Location")
        if not location:
            return response.read()
    clean=urllib.request.Request(location,headers={"User-Agent":"gscc-first-touch-state"})
    with urllib.request.urlopen(clean,timeout=30) as response:
        return response.read()


def _state_db_from_blob(blob:bytes)->bytes|None:
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        candidate=next((n for n in archive.namelist() if n.endswith("first-touch-capture.sqlite")),None)
        return archive.read(candidate) if candidate else None


def _runtime_snapshot(db_blob:bytes|None)->dict:
    if not db_blob:
        return {"inspectable":False,"reason":"NO_STATE_DB","rank":-1}
    tmp=None
    try:
        with tempfile.NamedTemporaryFile(prefix="gscc-state-",suffix=".sqlite",delete=False) as fh:
            fh.write(db_blob)
            tmp=Path(fh.name)
        conn=sqlite3.connect(tmp)
        try:
            tables={row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "gscc_session_runtime" not in tables:
                return {"inspectable":False,"reason":"NO_SESSION_RUNTIME_TABLE","rank":-1}
            row=conn.execute(
                "SELECT runtime_id,state,COALESCE(updated_at,created_at,''),last_gate "
                "FROM gscc_session_runtime "
                "ORDER BY COALESCE(updated_at,created_at,'') DESC, runtime_id DESC LIMIT 1"
            ).fetchone()
            if not row:
                return {"inspectable":False,"reason":"NO_SESSION_RUNTIME_ROW","rank":-1}
            runtime_id,state,updated_at,last_gate=row
            return {
                "inspectable":True,
                "runtime_id":runtime_id,
                "state":state,
                "updated_at":updated_at or "",
                "last_gate":last_gate,
                "rank":RUNTIME_STATE_RANK.get(state,0),
            }
        finally:
            conn.close()
    except (sqlite3.DatabaseError, zipfile.BadZipFile, OSError) as exc:
        return {"inspectable":False,"reason":"STATE_DB_INSPECTION_FAILED","error":str(exc),"rank":-1}
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)


def _candidate_key(candidate:dict)->tuple:
    snap=candidate.get("runtime_snapshot") or {}
    # Runtime progression outranks artifact creation order. This prevents a later
    # workflow retry carrying stale Q9 state from replacing a prior Q12/F1 state.
    return (
        int(snap.get("rank",-1)),
        str(snap.get("updated_at") or ""),
        str(candidate.get("created_at") or ""),
        int(candidate.get("id") or 0),
    )


def restore_latest(repository:str, current_run_id:str, output:Path, token:str, *, scope:str|None=None)->dict:
    encoded=urllib.parse.quote(repository,safe="/")
    url=f"https://api.github.com/repos/{encoded}/actions/artifacts?per_page=100"
    payload=_request_json(url,token)
    prefix=STATE_NAME_PREFIX if not scope else f"{STATE_NAME_PREFIX}{scope}-"
    artifacts=[
        x for x in payload.get("artifacts",[])
        if str(x.get("name") or "").startswith(prefix)
        and not x.get("expired")
        and str((x.get("workflow_run") or {}).get("id") or "") != str(current_run_id)
    ]
    if not artifacts:
        return {"status":"NO_PRIOR_STATE"}

    evaluated=[]
    for artifact in artifacts:
        blob=_artifact_blob(artifact["archive_download_url"],token)
        db_blob=_state_db_from_blob(blob)
        evaluated.append({
            **artifact,
            "_db_blob":db_blob,
            "runtime_snapshot":_runtime_snapshot(db_blob),
        })

    inspectable=[x for x in evaluated if (x.get("runtime_snapshot") or {}).get("inspectable")]
    selectable=inspectable or [x for x in evaluated if x.get("_db_blob") is not None]
    if not selectable:
        return {
            "status":"PRIOR_ARTIFACTS_HAVE_NO_STATE_DB",
            "evaluated_artifact_ids":[x.get("id") for x in evaluated],
        }

    selected=max(selectable,key=_candidate_key)
    output.write_bytes(selected["_db_blob"])
    snapshot=selected.get("runtime_snapshot") or {}
    return {
        "status":"RESTORED",
        "artifact_id":selected.get("id"),
        "artifact_name":selected.get("name"),
        "selection_policy":"MOST_ADVANCED_RUNTIME_STATE_THEN_RUNTIME_UPDATED_AT",
        "runtime_id":snapshot.get("runtime_id"),
        "runtime_state":snapshot.get("state"),
        "runtime_last_gate":snapshot.get("last_gate"),
        "runtime_updated_at":snapshot.get("updated_at"),
        "runtime_state_rank":snapshot.get("rank"),
        "candidate_count":len(evaluated),
    }


def merge_previous(current:Path, previous:Path)->dict:
    if not previous.exists():
        return {"status":"NO_PRIOR_STATE"}
    conn=sqlite3.connect(current)
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        conn.execute("ATTACH DATABASE ? AS previous",(str(previous),))
        tables={row[0] for row in conn.execute("SELECT name FROM previous.sqlite_master WHERE type='table'")}
        required={"gscc_conversation_identities","gscc_first_touch_snapshots","gse_session_twins","first_touch_capture_records"}
        if not required <= tables:
            return {"status":"PRIOR_SCHEMA_INCOMPATIBLE","missing":sorted(required-tables)}
        first_ids=[row[0] for row in conn.execute("SELECT first_capture_id FROM previous.gscc_conversation_identities")]
        last_ids=[row[0] for row in conn.execute("SELECT last_capture_id FROM previous.gscc_conversation_identities")]
        packet_capture_ids=[]
        if "gscc_observable_packets" in tables:
            packet_capture_ids=[row[0] for row in conn.execute("SELECT capture_id FROM previous.gscc_observable_packets")]
        pipeline_capture_ids=[]
        if "gscc_entry_pipeline_runs" in tables:
            pipeline_capture_ids=[row[0] for row in conn.execute("SELECT capture_id FROM previous.gscc_entry_pipeline_runs")]
        for capture_id in sorted(set(first_ids+last_ids+packet_capture_ids+pipeline_capture_ids)):
            conn.execute(
                "INSERT OR IGNORE INTO first_touch_capture_records SELECT * FROM previous.first_touch_capture_records WHERE capture_id=?",
                (capture_id,),
            )
        conn.execute("INSERT OR IGNORE INTO gscc_conversation_identities SELECT * FROM previous.gscc_conversation_identities")
        conn.execute("INSERT OR IGNORE INTO gscc_first_touch_snapshots SELECT * FROM previous.gscc_first_touch_snapshots")
        conn.execute("INSERT OR IGNORE INTO gse_session_twins SELECT * FROM previous.gse_session_twins")
        if "gscc_observable_packets" in tables:
            conn.execute("INSERT OR IGNORE INTO gscc_observable_packets SELECT * FROM previous.gscc_observable_packets")
        if "gscc_entry_pipeline_runs" in tables:
            conn.execute("INSERT OR IGNORE INTO gscc_entry_pipeline_runs SELECT * FROM previous.gscc_entry_pipeline_runs")
        if "gscc_gate_route_runs" in tables:
            conn.execute("INSERT OR IGNORE INTO gscc_gate_route_runs SELECT * FROM previous.gscc_gate_route_runs")
        if "gscc_arrival_instances" in tables:
            conn.execute("INSERT OR IGNORE INTO gscc_arrival_instances SELECT * FROM previous.gscc_arrival_instances")
        if "gscc_arrival_events" in tables:
            conn.execute("INSERT OR IGNORE INTO gscc_arrival_events SELECT * FROM previous.gscc_arrival_events")
        if "gscc_session_bindings" in tables:
            conn.execute("INSERT OR IGNORE INTO gscc_session_bindings SELECT * FROM previous.gscc_session_bindings")
        if "gscc_session_runtime" in tables:
            conn.execute("INSERT OR IGNORE INTO gscc_session_runtime SELECT * FROM previous.gscc_session_runtime")
        if "gscc_pre_gse_control_challenges" in tables:
            conn.execute("INSERT OR IGNORE INTO gscc_pre_gse_control_challenges SELECT * FROM previous.gscc_pre_gse_control_challenges")
        count=conn.execute("SELECT COUNT(*) FROM gscc_conversation_identities").fetchone()[0]
        conn.commit()
        return {"status":"MERGED","identity_count":count}
    finally:
        conn.close()


def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="command",required=True)
    r=sub.add_parser("restore")
    r.add_argument("--repository",required=True); r.add_argument("--run-id",required=True); r.add_argument("--output",required=True); r.add_argument("--scope")
    m=sub.add_parser("merge")
    m.add_argument("--current",required=True); m.add_argument("--previous",required=True)
    a=p.parse_args()
    if a.command=="restore":
        token=os.environ.get("GITHUB_TOKEN")
        if not token: raise SystemExit("GITHUB_TOKEN unavailable")
        result=restore_latest(a.repository,a.run_id,Path(a.output),token,scope=a.scope)
    else:
        result=merge_previous(Path(a.current),Path(a.previous))
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
