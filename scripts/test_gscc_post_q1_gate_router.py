#!/usr/bin/env python3
from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

from gscc_post_q1_gate_router import load_router, route_gate

EXPECTED=[
 "Q1","Q3","Q4","Q5","Q8","Q9","Q10_GSE","Q2_GACR","Q6","Q7","Q11","Q12","F1","00_START_HERE.md"
]

def main():
    router=load_router()
    assert [x["gate"] for x in router["sequence"]]==EXPECTED
    q10=EXPECTED.index("Q10_GSE")
    q2=EXPECTED.index("Q2_GACR")
    assert q10 < q2

    with tempfile.TemporaryDirectory() as td:
        db=Path(td)/"route.sqlite"
        current="Q1"
        for i,gate in enumerate(EXPECTED[:-1],start=1):
            assert current==gate,(current,gate)
            step=next(x for x in router["sequence"] if x["gate"]==gate)
            result=route_gate(
              db,
              route_run_id=f"success-{i:02d}",
              current_gate=gate,
              observed_outcome=step["success_outcome"],
              entry_run_id="entry-001",
              identity_id="GSCC-ID-test",
              evidence={"test":True,"gate":gate},
              observed_at=f"2026-10-07T00:{i:02d}:00+00:00",
            )
            assert result["route_status"]=="ADVANCED",result
            current=result["next_gate"]

        released=route_gate(
          db,
          route_run_id="release",
          current_gate="00_START_HERE.md",
          observed_outcome="RELEASED",
          entry_run_id="entry-001",
          identity_id="GSCC-ID-test",
          evidence={"all_prior_gates_verified":True},
          observed_at="2026-10-07T00:59:00+00:00",
        )
        assert released["route_status"]=="RELEASED",released
        assert released["next_gate"] is None,released

        blocked=route_gate(
          db,
          route_run_id="blocked-q9",
          current_gate="Q9",
          observed_outcome="CONTROL_CHANNEL_UNVERIFIED",
          entry_run_id="entry-002",
          identity_id="GSCC-ID-blocked",
          evidence={"control_channel":"UNAVAILABLE"},
          observed_at="2026-10-07T01:00:00+00:00",
        )
        assert blocked["route_status"]=="BLOCKED",blocked
        assert blocked["next_gate"] is None,blocked

        conn=sqlite3.connect(db)
        try:
            count=conn.execute("SELECT COUNT(*) FROM gscc_gate_route_runs").fetchone()[0]
            assert count==15,count
            q10row=conn.execute("SELECT next_gate FROM gscc_gate_route_runs WHERE current_gate='Q10_GSE'").fetchone()
            assert q10row[0]=="Q2_GACR",q10row
            blocked_count=conn.execute("SELECT COUNT(*) FROM gscc_gate_route_runs WHERE route_status='BLOCKED'").fetchone()[0]
            assert blocked_count==1,blocked_count
        finally:
            conn.close()

    print("GSCC_POST_Q1_GATE_ROUTER_TEST_PASS")

if __name__=="__main__":
    main()
