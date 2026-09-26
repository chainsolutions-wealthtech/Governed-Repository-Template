#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_ROOT = ROOT / ".governance" / "control-plane-db"

def jdump(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))

def insert_case_data(conn, catalog):
    for item in catalog["cases"]:
        conn.execute(
            "INSERT INTO framework_cases(case_id,label,ordinal,kind,status,source_authority) VALUES(?,?,?,?,?,?)",
            (item["case_id"], item["label"], item["ordinal"], item["kind"], item["status"], item.get("source_authority")),
        )
    for item in catalog.get("modes", []):
        conn.execute(
            "INSERT INTO modes(mode_id,case_id,label,description,is_default) VALUES(?,?,?,?,?)",
            (item["mode_id"], item.get("case_id"), item["label"], item.get("description"), int(item.get("is_default",0))),
        )

def insert_replay(conn, replay):
    previous = None
    for ordinal, phase in enumerate(replay["phases"]):
        conn.execute(
            "INSERT INTO case_phases(phase_id,case_id,ordinal,label,status,owner_feedback_hook,source_authority) VALUES(?,?,?,?,?,?,?)",
            (phase["id"], replay["case_id"], ordinal, phase["name"], phase["status"], jdump(phase.get("owner_feedback")) if "owner_feedback" in phase else None, replay["authority"]),
        )
        for dep in phase.get("depends_on", []):
            conn.execute("INSERT INTO phase_dependencies(phase_id,depends_on_phase_id) VALUES(?,?)",(phase["id"],dep))
        if previous and not phase.get("depends_on") and ordinal > 0:
            conn.execute("INSERT OR IGNORE INTO phase_dependencies(phase_id,depends_on_phase_id) VALUES(?,?)",(phase["id"],previous))
        previous = phase["id"]

def insert_questions_activities(conn, catalog):
    for q in catalog.get("questions", []):
        conn.execute(
            "INSERT INTO questions(question_id,case_id,phase_id,field_key,prompt,response_type,required,required_when_json,validation_rule,source_authority) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (q["question_id"],q.get("case_id"),q.get("phase_id"),q["field_key"],q["prompt"],q["response_type"],int(q.get("required",1)),jdump(q.get("required_when")) if q.get("required_when") is not None else None,q.get("validation_rule"),q.get("source_authority")),
        )
        for ordinal, option in enumerate(q.get("options", [])):
            conn.execute(
                "INSERT INTO question_options(option_id,question_id,value_json,label,ordinal) VALUES(?,?,?,?,?)",
                (f'{q["question_id"]}-OPT-{ordinal+1}',q["question_id"],jdump(option),str(option),ordinal+1),
            )
    for a in catalog.get("activities", []):
        conn.execute(
            "INSERT INTO activities(activity_id,case_id,phase_id,kind,label,mutation_class,required_authority,required_evidence_json,source_authority) VALUES(?,?,?,?,?,?,?,?,?)",
            (a["activity_id"],a["case_id"],a.get("phase_id"),a["kind"],a["label"],a["mutation_class"],a.get("required_authority"),jdump(a.get("required_evidence",[])),a.get("source_authority")),
        )

def insert_runtime(conn, seed):
    for r in seed.get("repositories", []):
        conn.execute("INSERT INTO repositories(repository_id,full_name,role,canonical_branch,current_head_sha,source_ref) VALUES(?,?,?,?,?,?)",
                     (r["repository_id"],r["full_name"],r["role"],r.get("canonical_branch"),r.get("current_head_sha"),r.get("source_ref")))
    for run in seed.get("runs", []):
        conn.execute("INSERT INTO runs(run_id,case_id,repository_id,status,current_phase_id,source_issue,started_at,completed_at,parent_run_id) VALUES(?,?,?,?,?,?,?,?,?)",
                     (run["run_id"],run["case_id"],run.get("repository_id"),run["status"],run.get("current_phase_id"),run.get("source_issue"),run.get("started_at"),run.get("completed_at"),run.get("parent_run_id")))
    for d in seed.get("decisions", []):
        conn.execute("INSERT INTO decisions(decision_id,scope_type,scope_id,decision_key,value_json,status,source_ref,decided_at) VALUES(?,?,?,?,?,?,?,?)",
                     (d["decision_id"],d["scope_type"],d["scope_id"],d["decision_key"],jdump(d["value"]),d["status"],d.get("source_ref"),d.get("decided_at")))
    for cp in seed.get("checkpoints", []):
        conn.execute("INSERT INTO checkpoints(checkpoint_id,run_id,phase_id,subject_head_sha,state,next_action,payload_json,source_ref,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                     (cp["checkpoint_id"],cp.get("run_id"),cp.get("phase_id"),cp.get("subject_head_sha"),cp["state"],cp.get("next_action"),jdump(cp.get("payload",{})),cp.get("source_ref"),cp.get("created_at")))
    for i in seed.get("intakes", []):
        conn.execute("INSERT INTO intakes(intake_id,originating_case_id,originating_run_id,target_system,status,summary,source_ref,created_at) VALUES(?,?,?,?,?,?,?,?)",
                     (i["intake_id"],i.get("originating_case_id"),i.get("originating_run_id"),i["target_system"],i["status"],i["summary"],i.get("source_ref"),i.get("created_at")))

def validate(conn):
    conn.execute("PRAGMA foreign_key_check")
    fk = conn.fetchall() if False else []
    if conn.execute("PRAGMA foreign_key_check").fetchall():
        raise SystemExit("CONTROL_PLANE_DB_FAILED: foreign key violation")
    cases = conn.execute("SELECT COUNT(*) FROM framework_cases WHERE kind='STRUCTURING_CASE'").fetchone()[0]
    if cases != 4:
        raise SystemExit(f"CONTROL_PLANE_DB_FAILED: expected 4 structuring cases, got {cases}")
    active = conn.execute("SELECT phase_id FROM case_phases WHERE case_id='CREATE_NEW_REPOSITORY' AND status='IN_PROGRESS'").fetchall()
    if active != [("C1-12",)]:
        raise SystemExit(f"CONTROL_PLANE_DB_FAILED: CASE1 active phase mismatch: {active}")
    next_phase = conn.execute("SELECT current_phase_id FROM runs WHERE run_id='CASE1-PILOT-GOUVERN'").fetchone()
    if next_phase != ("C1-12",):
        raise SystemExit("CONTROL_PLANE_DB_FAILED: pilot run current phase mismatch")
    mcp_choices = [json.loads(r[0]) for r in conn.execute(
        "SELECT value_json FROM question_options WHERE question_id='C1-Q-MCP-TRANSPORT' ORDER BY ordinal"
    ).fetchall()]
    if mcp_choices != ["DIRECT_MCP_TOKEN","SSH","BOTH"]:
        raise SystemExit(f"CONTROL_PLANE_DB_FAILED: MCP choices mismatch: {mcp_choices}")
    if conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0] < 15:
        raise SystemExit("CONTROL_PLANE_DB_FAILED: question catalog unexpectedly small")
    if conn.execute("SELECT COUNT(*) FROM activities").fetchone()[0] < 8:
        raise SystemExit("CONTROL_PLANE_DB_FAILED: activity catalog unexpectedly small")
    for table in ["agent_sessions","agent_activity_events"]:
        conn.execute(f"SELECT 1 FROM {table} LIMIT 1")
    print("CONTROL_PLANE_DB_VALIDATION_PASS")
    print("cases=4")
    print(f"questions={conn.execute('SELECT COUNT(*) FROM questions').fetchone()[0]}")
    print(f"activities={conn.execute('SELECT COUNT(*) FROM activities').fetchone()[0]}")
    print(f"current_phase={active[0][0]}")

def build(path: Path):
    catalog = json.loads((DB_ROOT/"catalog.json").read_text(encoding="utf-8"))
    seed = json.loads((DB_ROOT/"runtime-seed.json").read_text(encoding="utf-8"))
    replay = json.loads((ROOT/".governance"/"control-plane-state"/"case1-replay.json").read_text(encoding="utf-8"))
    conn = sqlite3.connect(path)
    try:
        for migration in sorted(DB_ROOT.glob("[0-9][0-9][0-9]_*.sql")):
            conn.executescript(migration.read_text(encoding="utf-8"))
        conn.execute("INSERT INTO schema_meta(key,value) VALUES('schema_version','1.1.0')")
        insert_case_data(conn,catalog)
        insert_replay(conn,replay)
        insert_questions_activities(conn,catalog)
        insert_runtime(conn,seed)
        conn.commit()
        validate(conn)
    finally:
        conn.close()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output")
    args=parser.parse_args()
    if args.output:
        path=Path(args.output).resolve()
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists(): path.unlink()
        build(path)
        print(f"database={path}")
    else:
        with tempfile.TemporaryDirectory(prefix="control-plane-db-") as tmp:
            build(Path(tmp)/"control-plane.sqlite")

if __name__=="__main__":
    main()
