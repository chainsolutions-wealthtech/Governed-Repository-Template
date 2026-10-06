#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/".governance"/"control-plane-state"/"first-touch-entry-contract.json"

def rank(s:str)->int:
    return {"EMPTY":0,"UNAVAILABLE":0,"PARTIAL":1,"PRESENT":2,"SUFFICIENT":3,"VERIFIED":4,"STALE":1,"CONFLICTING":1}.get(s,0)

def evaluate(completeness_path:Path, db_path:Path, *, identity_strength:str, identity_anchor:str|None, first_touch_seen:bool):
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    comp=json.loads(completeness_path.read_text(encoding="utf-8"))
    conn=sqlite3.connect(db_path)
    try:
        row=conn.execute("SELECT capture_id FROM first_touch_capture_records ORDER BY rowid DESC LIMIT 1").fetchone()
        if not row: raise ValueError("no capture in database")
        capture_id=row[0]
        statuses=dict(conn.execute("SELECT block_id,status FROM first_touch_capture_block_status WHERE capture_id=?",(capture_id,)).fetchall())
    finally:
        conn.close()

    reasons=[]
    if not comp.get("complete_accounting"): reasons.append("INCOMPLETE_ACCOUNTING")
    if int(comp.get("silent_missing_count",0)) != 0: reasons.append("SILENT_MISSING_FIELDS")
    if identity_strength not in contract["conversation_identity"]["accepted_strengths"]:
        reasons.append("INSUFFICIENT_CONVERSATION_IDENTITY")
    if not identity_anchor:
        reasons.append("MISSING_CONVERSATION_IDENTITY_ANCHOR")

    missing_blocks=[]
    for block_id, minimum in contract["critical_blocks"].items():
        status=statuses.get(block_id,"EMPTY")
        if rank(status) < rank(minimum):
            missing_blocks.append({"block_id":block_id,"status":status,"minimum":minimum})
    if missing_blocks: reasons.append("REQUIRED_ENTRY_BLOCKS_UNSATISFIED")

    classification="CONTINUATION" if first_touch_seen else "FIRST_TOUCH"
    if reasons and not first_touch_seen:
        classification="UNRESOLVED_ENTRY"
    result={
      "schema":"first-touch-entry-contract-evaluation/v1",
      "capture_id":capture_id,
      "classification":classification,
      "identity_strength":identity_strength,
      "identity_anchor":identity_anchor,
      "first_touch_seen":first_touch_seen,
      "common_entry_blocks":{b:statuses.get(b,"EMPTY") for b in contract["common_entry_blocks"]},
      "missing_critical_blocks":missing_blocks,
      "complete_accounting":bool(comp.get("complete_accounting")),
      "silent_missing_count":int(comp.get("silent_missing_count",0)),
      "status":"ENTRY_READY_FOR_Q1" if not reasons else "ENTRY_BLOCKED",
      "reasons":reasons,
      "create_first_touch_snapshot": (not reasons and not first_touch_seen),
      "authority_granted":False
    }
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--completeness",required=True)
    p.add_argument("--db",required=True)
    p.add_argument("--identity-strength",required=True,choices=["EXACT","STRONG","WEAK","AMBIGUOUS","UNKNOWN"])
    p.add_argument("--identity-anchor")
    p.add_argument("--first-touch-seen",action="store_true")
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result=evaluate(Path(a.completeness),Path(a.db),identity_strength=a.identity_strength,identity_anchor=a.identity_anchor,first_touch_seen=a.first_touch_seen)
    Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True))

if __name__=="__main__": main()
