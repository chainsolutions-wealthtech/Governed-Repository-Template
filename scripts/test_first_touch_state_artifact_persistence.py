#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path

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
    print("FIRST_TOUCH_STATE_ARTIFACT_PERSISTENCE_TEST_PASS")

if __name__=="__main__":
    main()
