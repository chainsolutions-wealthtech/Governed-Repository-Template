#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

SCHEMA="gscc-first-touch-handoff/v1"

def build_handoff(entry_path:Path, db_path:Path)->dict:
    entry=json.loads(entry_path.read_text(encoding="utf-8"))
    if entry.get("status")!="ENTRY_READY_FOR_Q1":
        return {
            "schema":SCHEMA,
            "status":"HANDOFF_BLOCKED",
            "reason":"ENTRY_NOT_READY_FOR_Q1",
            "entry_status":entry.get("status"),
            "classification":entry.get("classification"),
            "authority_granted":False,
        }

    identity_id=entry.get("gscc_identity_id")
    capture_id=entry.get("capture_id")
    if not identity_id or not capture_id:
        raise ValueError("GSCC identity and capture required")

    conn=sqlite3.connect(db_path)
    try:
        row=conn.execute(
            "SELECT identity_id,identity_strength,first_capture_id,last_capture_id,status "
            "FROM gscc_conversation_identities WHERE identity_id=?",
            (identity_id,),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        raise ValueError("GSCC identity missing from canonical first-touch store")

    return {
        "schema":SCHEMA,
        "status":"READY_FOR_Q1",
        "loop_name":"GSCC–GSE–GACR Connection Loop",
        "classification":entry.get("classification"),
        "identity_id":row[0],
        "identity_strength":row[1],
        "capture_id":capture_id,
        "first_capture_id":row[2],
        "last_capture_id":row[3],
        "identity_status":row[4],
        "next_gate":"Q1",
        "gscc_state":"FIRST_TOUCH_ESTABLISHED",
        "gse_state":"PENDING_Q10",
        "gacr_state":"NOT_YET_ENTERED",
        "gse_must_not_precede_q1":True,
        "gacr_must_not_precede_q10":True,
        "authority_granted":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--entry",required=True)
    p.add_argument("--db",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result=build_handoff(Path(a.entry),Path(a.db))
    Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
