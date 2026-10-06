#!/usr/bin/env python3
from __future__ import annotations
import json, sqlite3, tempfile
from pathlib import Path

from gscc.first_touch_handoff import build_handoff

def main():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        db=root/"state.sqlite"
        entry=root/"entry.json"
        conn=sqlite3.connect(db)
        conn.execute("CREATE TABLE gscc_conversation_identities(identity_id TEXT PRIMARY KEY, identity_strength TEXT, first_capture_id TEXT, last_capture_id TEXT, status TEXT)")
        conn.execute("INSERT INTO gscc_conversation_identities VALUES(?,?,?,?,?)",("GSCC-ID-1","STRONG","CAP-1","CAP-1","FIRST_TOUCH_CONSUMED"))
        conn.commit(); conn.close()
        entry.write_text(json.dumps({
            "status":"ENTRY_READY_FOR_Q1",
            "classification":"FIRST_TOUCH",
            "gscc_identity_id":"GSCC-ID-1",
            "capture_id":"CAP-1",
        }),encoding="utf-8")
        handoff=build_handoff(entry,db)
        assert handoff["status"]=="READY_FOR_Q1", handoff
        assert handoff["next_gate"]=="Q1", handoff
        assert handoff["gse_state"]=="PENDING_Q10", handoff
        assert handoff["gacr_state"]=="NOT_YET_ENTERED", handoff
        assert handoff["authority_granted"] is False, handoff
        print("GSCC_FIRST_TOUCH_HANDOFF_TEST_PASS")

if __name__=="__main__":
    main()
