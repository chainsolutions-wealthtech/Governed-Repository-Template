#!/usr/bin/env python3
from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

from provider_first_tool_hook import build_envelope
from gscc_persisted_entry_pipeline import run_pipeline

GITHUB={
 "id":1386478935,
 "repository_full_name":"chainsolutions-wealthtech/Governed-Repository-Template",
 "owner":{"login":"chainsolutions-wealthtech","id":299685687},
 "permissions":{"admin":True,"maintain":True,"pull":True,"push":True,"triage":True},
 "default_branch":"main",
 "visibility":"public"
}

def provider(connection_ref:str):
    return build_envelope({
      "provider":"chatgpt",
      "provider_product":"ChatGPT",
      "provider_family":"OpenAI",
      "transport":"chatgpt-github-direct",
      "repository":"chainsolutions-wealthtech/Governed-Repository-Template",
      "runtime":"chatgpt-runtime",
      "surface":"text",
      "channel":"text",
      "execution_mode":"direct-tool",
      "model":"GPT-5.6 Sol",
      "connector_name":"GitHub",
      "connector_type":"native",
      "actor":"Wealthtechinnovations",
      "branch":"main",
      "observed_head":"a"*40,
      "identity":{
        "conversation_ref":"UNAVAILABLE",
        "session_ref":"UNAVAILABLE",
        "connection_ref":connection_ref,
      },
      "tool_name":"mcp__GitHub__get_repo",
      "operation":"read_repository",
      "category":"READ",
      "success":True,
    })

def main():
    with tempfile.TemporaryDirectory() as td:
        db=Path(td)/"control-plane.sqlite"

        first=run_pipeline(
          provider("conn-pipeline-12345678"),
          GITHUB,
          db,
          run_id="pipeline-first",
          observed_at="2026-10-07T00:00:00+00:00",
        )
        assert first["stored_in_database"] is True, first
        assert first["classification"]=="FIRST_TOUCH", first
        assert first["entry_status"]=="ENTRY_READY_FOR_Q1", first
        assert first["next_gate"]=="Q1", first
        assert first["gse_state"]=="NOT_YET_ENTERED", first
        assert first["gacr_state"]=="NOT_YET_ENTERED", first

        second=run_pipeline(
          provider("conn-pipeline-12345678"),
          GITHUB,
          db,
          run_id="pipeline-continuation",
          observed_at="2026-10-07T00:01:00+00:00",
        )
        assert second["classification"]=="CONTINUATION", second
        assert second["entry_status"]=="ENTRY_READY_FOR_Q1", second
        assert second["next_gate"]=="Q1", second

        conn=sqlite3.connect(db)
        try:
            assert conn.execute("SELECT COUNT(*) FROM gscc_observable_packets").fetchone()[0]==2
            assert conn.execute("SELECT COUNT(*) FROM gscc_entry_pipeline_runs").fetchone()[0]==2
            assert conn.execute("SELECT COUNT(*) FROM first_touch_capture_records").fetchone()[0]==2
            assert conn.execute("SELECT COUNT(*) FROM gscc_conversation_identities").fetchone()[0]==1
            assert conn.execute("SELECT COUNT(*) FROM gscc_first_touch_snapshots").fetchone()[0]==1
            assert conn.execute("SELECT COUNT(*) FROM gse_session_twins").fetchone()[0]==0
            q1=conn.execute("SELECT COUNT(*) FROM gscc_entry_pipeline_runs WHERE next_gate='Q1'").fetchone()[0]
            assert q1==2
        finally:
            conn.close()

        unresolved=build_envelope({
          "provider":"chatgpt",
          "transport":"chatgpt-github-direct",
          "repository":"chainsolutions-wealthtech/Governed-Repository-Template",
          "identity":{
            "conversation_ref":"UNAVAILABLE",
            "session_ref":"UNAVAILABLE",
            "connection_ref":"UNAVAILABLE",
          },
          "tool_name":"mcp__GitHub__get_repo",
          "operation":"read_repository",
          "category":"READ",
          "success":True,
        })
        blocked=run_pipeline(
          unresolved,GITHUB,db,
          run_id="pipeline-unresolved",
          observed_at="2026-10-07T00:02:00+00:00",
        )
        assert blocked["entry_status"]=="ENTRY_BLOCKED", blocked
        assert blocked["next_gate"] is None, blocked
        assert blocked["stored_in_database"] is True, blocked

        print("GSCC_PERSISTED_ENTRY_PIPELINE_TEST_PASS")

if __name__=="__main__":
    main()
