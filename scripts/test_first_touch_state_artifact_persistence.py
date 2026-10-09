#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import sqlite3
import tempfile
import zipfile
from pathlib import Path

import first_touch_state_artifact as artifact_state
from first_touch_field_block_gate import install_schema
from first_touch_state_artifact import merge_previous

ROOT=Path(__file__).resolve().parents[1]


def install_all(path:Path):
    conn=sqlite3.connect(path)
    try:
        install_schema(conn)
        for name in ("008_gscc_observable_entry_pipeline.sql","009_gscc_post_q1_gate_route.sql"):
            conn.executescript((ROOT/".governance"/"control-plane-db"/name).read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()


def seed_previous(path:Path):
    conn=sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        raw=json.dumps({"capture_id":"FTC-previous"})
        conn.execute(
            "INSERT INTO first_touch_capture_records(capture_id,schema_id,observed_at,repository,actor,capture_digest,raw_json,raw_json_sha256,node_count,terminal_value_count,api_attempt_count,source_ref) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            ("FTC-previous","first-touch-exhaustive-capture/v1","2026-10-07T00:00:00+00:00","owner/repo","actor",None,raw,"sha",1,1,0,"test"),
        )
        conn.execute(
            "INSERT INTO gscc_conversation_identities(identity_id,anchor_sha256,identity_strength,first_capture_id,first_observed_at,last_capture_id,last_seen_at,status) VALUES(?,?,?,?,?,?,?,?)",
            ("GSCC-ID-1","anchorhash","STRONG","FTC-previous","2026-10-07T00:00:00+00:00","FTC-previous","2026-10-07T00:00:00+00:00","FIRST_TOUCH_CONSUMED"),
        )
        conn.execute(
            "INSERT INTO gscc_first_touch_snapshots(identity_id,capture_id,snapshot_json,snapshot_sha256,created_at) VALUES(?,?,?,?,?)",
            ("GSCC-ID-1","FTC-previous",raw,"snapsha","2026-10-07T00:00:00+00:00"),
        )
        conn.execute(
            "INSERT INTO gscc_observable_packets(packet_id,capture_id,schema_id,repository,observed_at,identity_strength,classification,packet_json,packet_sha256,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
            ("PKT-1","FTC-previous","gscc-first-touch-observable-packet/v1","owner/repo","2026-10-07T00:00:00+00:00","STRONG","FIRST_TOUCH","{}","pktsha","2026-10-07T00:00:00+00:00"),
        )
        conn.execute(
            "INSERT INTO gscc_entry_pipeline_runs(run_id,packet_id,capture_id,identity_id,classification,entry_status,handoff_status,next_gate,blocked_reason_json,started_at,completed_at,authority_granted) VALUES(?,?,?,?,?,?,?,?,?,?,?,0)",
            ("RUN-1","PKT-1","FTC-previous","GSCC-ID-1","FIRST_TOUCH","ENTRY_READY_FOR_Q1","READY_FOR_Q1","Q1","[]","2026-10-07T00:00:00+00:00","2026-10-07T00:00:01+00:00"),
        )
        conn.execute(
            "INSERT INTO gscc_gate_route_runs(route_run_id,entry_run_id,identity_id,current_gate,owner_layer,action,implementation,observed_outcome,route_status,next_gate,evidence_json,started_at,completed_at,authority_granted) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,0)",
            ("ROUTE-1","RUN-1","GSCC-ID-1","Q1","GSCC","VALIDATE","test","Q1_VERIFIED","ADVANCED","Q3","{}","2026-10-07T00:00:01+00:00","2026-10-07T00:00:02+00:00"),
        )
        conn.commit()
    finally:
        conn.close()


def zipped_runtime_state(root:Path,name:str,state:str,updated_at:str)->bytes:
    db=root/f"{name}.sqlite"
    conn=sqlite3.connect(db)
    try:
        conn.execute(
            "CREATE TABLE gscc_session_runtime("
            "runtime_id TEXT PRIMARY KEY,state TEXT,last_gate TEXT,created_at TEXT,updated_at TEXT)"
        )
        gate={
            "WAITING_Q9_ACK":"Q9",
            "WAITING_Q9_RESPONSE":"Q9",
            "WAITING_Q9_RECHALLENGE_ACK":"Q9",
            "WAITING_Q9_RECHALLENGE_RESPONSE":"Q9",
            "READY_FOR_F1":"Q12",
            "RELEASED_TO_NORMAL_GOVERNANCE":"00_START_HERE.md",
        }.get(state,state)
        conn.execute(
            "INSERT INTO gscc_session_runtime(runtime_id,state,last_gate,created_at,updated_at) VALUES(?,?,?,?,?)",
            ("GSCC-RUNTIME-test",state,gate,"2026-10-07T00:00:00+00:00",updated_at),
        )
        conn.commit()
    finally:
        conn.close()
    out=io.BytesIO()
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as archive:
        archive.write(db,arcname="provider-first-touch-capture.sqlite")
    return out.getvalue()


def test_restore_prefers_advanced_runtime_state(root:Path)->None:
    q12=zipped_runtime_state(root,"q12","READY_FOR_F1","2026-10-07T02:20:00+00:00")
    stale_q9=zipped_runtime_state(root,"q9","WAITING_Q9_ACK","2026-10-07T02:30:00+00:00")
    artifacts={
        "artifacts":[
            {
                "id":1,
                "name":"first-touch-state-arrival-test-q12",
                "created_at":"2026-10-07T02:21:00Z",
                "expired":False,
                "archive_download_url":"memory://q12",
                "workflow_run":{"id":101},
            },
            {
                "id":2,
                "name":"first-touch-state-arrival-test-q9",
                "created_at":"2026-10-07T02:31:00Z",
                "expired":False,
                "archive_download_url":"memory://q9",
                "workflow_run":{"id":102},
            },
        ]
    }
    old_request=artifact_state._request_json
    old_blob=artifact_state._artifact_blob
    try:
        artifact_state._request_json=lambda _url,_token: artifacts
        artifact_state._artifact_blob=lambda url,_token: {"memory://q12":q12,"memory://q9":stale_q9}[url]
        output=root/"restored.sqlite"
        result=artifact_state.restore_latest("owner/repo","999",output,"token",scope="arrival-test")
        assert result["status"]=="RESTORED",result
        assert result["artifact_id"]==1,result
        assert result["runtime_state"]=="READY_FOR_F1",result
        assert result["selection_policy"]=="MOST_ADVANCED_RUNTIME_STATE_THEN_RUNTIME_UPDATED_AT",result
        conn=sqlite3.connect(output)
        try:
            assert conn.execute("SELECT state FROM gscc_session_runtime").fetchone()[0]=="READY_FOR_F1"
        finally:
            conn.close()
    finally:
        artifact_state._request_json=old_request
        artifact_state._artifact_blob=old_blob


def test_restore_prefers_rechallenge_over_older_ack_state(root:Path)->None:
    old_ack=zipped_runtime_state(
        root,"old-ack","WAITING_Q9_RESPONSE","2026-10-07T02:30:00+00:00"
    )
    refreshed=zipped_runtime_state(
        root,"rechallenge","WAITING_Q9_RECHALLENGE_ACK","2026-10-07T02:31:00+00:00"
    )
    artifacts={
        "artifacts":[
            {
                "id":11,
                "name":"first-touch-state-arrival-retry-old",
                "created_at":"2026-10-07T02:30:10Z",
                "expired":False,
                "archive_download_url":"memory://old-ack",
                "workflow_run":{"id":201},
            },
            {
                "id":12,
                "name":"first-touch-state-arrival-retry-rechallenge",
                "created_at":"2026-10-07T02:31:10Z",
                "expired":False,
                "archive_download_url":"memory://rechallenge",
                "workflow_run":{"id":202},
            },
        ]
    }
    old_request=artifact_state._request_json
    old_blob=artifact_state._artifact_blob
    try:
        artifact_state._request_json=lambda _url,_token: artifacts
        artifact_state._artifact_blob=lambda url,_token: {
            "memory://old-ack":old_ack,
            "memory://rechallenge":refreshed,
        }[url]
        output=root/"restored-rechallenge.sqlite"
        result=artifact_state.restore_latest(
            "owner/repo","999",output,"token",scope="arrival-retry"
        )
        assert result["artifact_id"]==12,result
        assert result["runtime_state"]=="WAITING_Q9_RECHALLENGE_ACK",result
        assert result["runtime_state_rank"]>artifact_state.RUNTIME_STATE_RANK["WAITING_Q9_RESPONSE"],result
    finally:
        artifact_state._request_json=old_request
        artifact_state._artifact_blob=old_blob


def main():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        previous=root/"previous.sqlite"
        current=root/"current.sqlite"
        install_all(previous)
        install_all(current)
        seed_previous(previous)
        result=merge_previous(current,previous)
        assert result["status"]=="MERGED",result
        conn=sqlite3.connect(current)
        try:
            assert conn.execute("SELECT COUNT(*) FROM gscc_conversation_identities").fetchone()[0]==1
            assert conn.execute("SELECT COUNT(*) FROM gscc_first_touch_snapshots").fetchone()[0]==1
            assert conn.execute("SELECT COUNT(*) FROM gscc_observable_packets").fetchone()[0]==1
            assert conn.execute("SELECT COUNT(*) FROM gscc_entry_pipeline_runs").fetchone()[0]==1
            assert conn.execute("SELECT COUNT(*) FROM gscc_gate_route_runs").fetchone()[0]==1
        finally:
            conn.close()
        test_restore_prefers_advanced_runtime_state(root)
        test_restore_prefers_rechallenge_over_older_ack_state(root)
    print("FIRST_TOUCH_STATE_ARTIFACT_PERSISTENCE_TEST_PASS")


if __name__=="__main__":
    main()
