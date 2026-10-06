#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
ROUTER_PATH=ROOT/".governance"/"gscc-post-q1-router.json"
MIGRATION=ROOT/".governance"/"control-plane-db"/"009_gscc_post_q1_gate_route.sql"

def now_iso()->str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def load_router()->dict[str,Any]:
    payload=json.loads(ROUTER_PATH.read_text(encoding="utf-8"))
    if payload.get("schema")!="gscc-post-q1-router/v1":
        raise ValueError("unsupported post-Q1 router schema")
    return payload

def route_gate(
    db_path:Path,
    *,
    route_run_id:str,
    current_gate:str,
    observed_outcome:str|None=None,
    entry_run_id:str|None=None,
    identity_id:str|None=None,
    evidence:dict[str,Any]|None=None,
    observed_at:str|None=None,
)->dict[str,Any]:
    observed_at=observed_at or now_iso()
    router=load_router()
    step=next((x for x in router["sequence"] if x["gate"]==current_gate),None)
    if step is None:
        raise ValueError(f"unknown post-Q1 gate: {current_gate}")

    success=step["success_outcome"]
    if current_gate=="00_START_HERE.md":
        status="RELEASED" if observed_outcome in (None,"RELEASED") else "BLOCKED"
        next_gate=None
    elif observed_outcome is None:
        status="PENDING"
        next_gate=current_gate
    elif observed_outcome==success:
        status="ADVANCED"
        next_gate=step["next_gate"]
    else:
        status="BLOCKED"
        next_gate=None

    db_path.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(db_path)
    try:
        conn.executescript(MIGRATION.read_text(encoding="utf-8"))
        conn.execute(
          "INSERT OR REPLACE INTO gscc_gate_route_runs("
          "route_run_id,entry_run_id,identity_id,current_gate,owner_layer,action,implementation,"
          "observed_outcome,route_status,next_gate,evidence_json,started_at,completed_at,authority_granted"
          ") VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,0)",
          (
            route_run_id,entry_run_id,identity_id,current_gate,step["owner_layer"],step["action"],step["implementation"],
            observed_outcome,status,next_gate,
            json.dumps(evidence or {},ensure_ascii=False,sort_keys=True),
            observed_at,now_iso(),
          ),
        )
        conn.commit()
    finally:
        conn.close()

    return {
      "schema":"gscc-post-q1-route-decision/v1",
      "route_run_id":route_run_id,
      "current_gate":current_gate,
      "owner_layer":step["owner_layer"],
      "action":step["action"],
      "implementation":step["implementation"],
      "observed_outcome":observed_outcome,
      "route_status":status,
      "next_gate":next_gate,
      "fail_closed":True,
      "stored_in_database":True,
      "authority_granted":False,
    }

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--db",required=True)
    p.add_argument("--route-run-id",required=True)
    p.add_argument("--current-gate",required=True)
    p.add_argument("--outcome")
    p.add_argument("--entry-run-id")
    p.add_argument("--identity-id")
    p.add_argument("--evidence-json")
    p.add_argument("--observed-at")
    a=p.parse_args()
    evidence=json.loads(a.evidence_json) if a.evidence_json else {}
    result=route_gate(
      Path(a.db),
      route_run_id=a.route_run_id,
      current_gate=a.current_gate,
      observed_outcome=a.outcome,
      entry_run_id=a.entry_run_id,
      identity_id=a.identity_id,
      evidence=evidence,
      observed_at=a.observed_at,
    )
    print(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
