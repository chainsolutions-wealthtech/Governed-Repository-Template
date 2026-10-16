#!/usr/bin/env python3
"""Same-arrival Q12 requalification. Never creates an admission, GACR identity, claim or F1 release."""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from gscc.admission import evaluate_access_grant, validate_access_grant
from gscc.admission_harvester import github_get_json, harvest_qualification_evidence, observe_repository
from gscc_gacr.issue_control_bridge import canonical_control_evidence
from gscc_session_runtime import _load_runtime, _packet, _session_connection_values, ROOT

SESSIONS = ROOT / ".governance/control-plane-state/gacr-sessions.json"
DISPATCHES = ROOT / ".governance/control-plane-state/gacr-dispatches.json"
CLAIMS = ROOT / ".governance/control-plane-state/gacr-claims.json"
TASKS = ROOT / ".governance/control-plane-state/tasks.json"
POLICY = ROOT / ".governance/agent-relay/gscc-admission-access-policy.json"
MIGRATION = ROOT / ".governance/control-plane-db/012_gscc_q12_renewal.sql"
DOCUMENTS = (
    "00_START_HERE.md", "GOVERNANCE.md",
    "docs/control-plane/GSCC_ADMISSION_ACCESS_GATE.md",
    "docs/control-plane/GACR_PROGRAM.md",
)


def _utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None
    return dt.astimezone(timezone.utc)


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("CANONICAL_STORE_OBJECT_REQUIRED")
    return value


def _fresh_control(
    dispatches: dict[str, Any],
    *,
    session_id: str,
    connection_ref: str,
    repository: str,
    previous_issued: datetime,
    now: datetime,
) -> tuple[dict[str, Any], dict[str, Any]]:
    candidates = []
    for item in dispatches.get("items") or []:
        if not isinstance(item, dict):
            continue
        command = item.get("command") or {}
        response = item.get("response") or {}
        ack = item.get("ack") or {}
        if not all((
            item.get("target_session_id") == session_id,
            item.get("target_connection_ref") == connection_ref,
            item.get("repository") == repository,
            item.get("status") == "COMPLETED",
            command.get("command_type") == "LIVENESS_CHALLENGE",
            command.get("target_session_id") == session_id,
            ack.get("delivery_state") == "ACKNOWLEDGED",
            response.get("fresh_liveness") is True,
            response.get("replay") is not True,
            isinstance(ack.get("evidence_ref"), str),
            str(ack.get("evidence_ref")).startswith("github-issue-comment:"),
            isinstance(response.get("evidence_ref"), str),
            str(response.get("evidence_ref")).startswith("github-issue-comment:"),
        )):
            continue
        issued = _utc(command.get("issued_at"))
        expires = _utc(command.get("expires_at"))
        observed = _utc(response.get("observed_at"))
        if not issued or not expires or not observed:
            continue
        if not (previous_issued < issued <= observed <= expires and observed <= now):
            continue
        if now - observed > timedelta(minutes=5):
            continue
        candidates.append((observed, str(item.get("dispatch_id")), item))
    if not candidates:
        raise ValueError("FRESH_POST_GRANT_GACR_CONTROL_PROOF_REQUIRED")
    candidates.sort(key=lambda x: (x[0], x[1]))
    chosen = candidates[-1][2]
    # Derive canonical evidence only from the verified, matched challenge,
    # not from arbitrary caller-supplied VERIFIED fields.
    evidence = canonical_control_evidence(
        {"items": [chosen]}, session_id=session_id, now=now, freshness_seconds=300
    )
    if any((evidence.get(section) or {}).get("status") != "VERIFIED"
           for section in ("capabilities", "control_channel")):
        raise ValueError("CANONICAL_CONTROL_EVIDENCE_NOT_VERIFIED")
    return evidence["capabilities"], evidence["control_channel"]


def renew_q12(
    db: Path,
    runtime_id: str,
    sessions_path: Path,
    dispatches_path: Path,
    current_head: str,
    *,
    github_request_fn: Callable[[str], dict[str, Any]],
    claims_path: Path = CLAIMS,
    tasks_path: Path = TASKS,
    policy_path: Path = POLICY,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Fail-closed Q12 requalification on one persisted READY_FOR_F1 arrival.

    A caller supplied HEAD is never trusted without a fresh GitHub observation.
    The GACR session and completed control challenge are read from canonical stores.
    """
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if re.fullmatch(r"[0-9a-f]{40}", current_head or "") is None:
        raise ValueError("CURRENT_HEAD_SHA_REQUIRED")

    sessions = _read(sessions_path)
    dispatches = _read(dispatches_path)
    claims = _read(claims_path)
    tasks = _read(tasks_path)
    policy = _read(policy_path)

    conn = sqlite3.connect(db, timeout=5)
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        conn.executescript(MIGRATION.read_text(encoding="utf-8"))
        conn.execute("BEGIN IMMEDIATE")
        runtime = _load_runtime(conn, runtime_id)
        if runtime["state"] != "READY_FOR_F1":
            raise ValueError("READY_FOR_F1_SAME_ARRIVAL_REQUIRED")
        previous = json.loads(runtime["access_grant_json"] or "{}")
        if previous.get("schema") != "gscc-access-grant/v1" or previous.get("status") != "AUTHORIZED":
            raise ValueError("PREVIOUS_CANONICAL_ACCESS_GRANT_REQUIRED")
        admission = json.loads(runtime["admission_json"] or "{}")
        _, packet = _packet(conn, runtime["run_id"])
        github = (packet.get("sections") or {}).get("github") or {}
        repository = github.get("repository_full_name")
        branch = github.get("branch") or github.get("default_branch")
        if not repository or not branch or admission.get("repository") != repository:
            raise ValueError("SAME_ARRIVAL_REPOSITORY_REQUIRED")

        row = conn.execute(
            "SELECT gacr_session_id,connection_ref,binding_status,binding_level "
            "FROM gscc_session_bindings WHERE arrival_ref=? AND identity_id=?",
            (runtime["arrival_ref"], runtime["identity_id"]),
        ).fetchall()
        if len(row) != 1 or row[0][2:] != ("GACR_BOUND", "EXACT"):
            raise ValueError("EXACT_PERSISTED_GACR_BINDING_REQUIRED")
        session_id, binding_connection, _, _ = row[0]
        if binding_connection != runtime["connection_ref"]:
            raise ValueError("PERSISTED_GACR_CONNECTION_MISMATCH")

        matches = [
            s for s in sessions.get("sessions") or []
            if isinstance(s, dict)
            and s.get("session_id") == session_id
            and runtime["connection_ref"] in _session_connection_values(s)
        ]
        if len(matches) != 1:
            raise ValueError("UNIQUE_SAME_ARRIVAL_GACR_SESSION_REQUIRED")
        session = matches[0]
        relay = session.get("relay") or {}
        if session.get("status") != "ACTIVE" or relay.get("state") != "ACTIVE":
            raise ValueError("GACR_SESSION_NOT_ACTIVE")
        if session.get("repository") != repository:
            raise ValueError("GACR_REPOSITORY_MISMATCH")
        if (session.get("branch") or relay.get("branch")) != branch:
            raise ValueError("GACR_BRANCH_MISMATCH")
        lease = _utc(relay.get("lease_expires_at"))
        if lease is None or lease <= now:
            raise ValueError("GACR_LEASE_EXPIRED")

        if previous.get("session_id") != session_id or previous.get("connection_ref") != runtime["connection_ref"]:
            raise ValueError("PREVIOUS_GRANT_BINDING_MISMATCH")
        if previous.get("admission_id") != admission.get("admission_id") or previous.get("repository") != repository:
            raise ValueError("PREVIOUS_GRANT_ADMISSION_MISMATCH")
        old_state = validate_access_grant(
            previous, connection_ref=runtime["connection_ref"], repository=repository,
            requested_head=current_head, session_id=session_id, now=now,
        )
        observed = observe_repository(
            repository, branch, request_fn=github_request_fn, observed_at=now
        )
        if observed.get("status") != "OBSERVED" or observed.get("observed_head") != current_head:
            raise ValueError("CURRENT_GITHUB_HEAD_MISMATCH")
        if old_state.get("status") == "VALIDATED":
            conn.rollback()
            return {
                "status": "ALREADY_CURRENT", "runtime_id": runtime_id,
                "access_grant_id": previous["grant_id"], "bound_head": current_head,
                "authority_granted": False, "f1_released": False,
            }
        if old_state.get("reason_code") not in {"ACCESS_GRANT_EXPIRED", "ACCESS_GRANT_HEAD_MISMATCH"}:
            raise ValueError("RENEWAL_ONLY_FOR_EXPIRED_OR_MOVED_HEAD")
        issued = _utc(previous.get("issued_at"))
        if issued is None:
            raise ValueError("PREVIOUS_GRANT_ISSUED_AT_REQUIRED")
        capabilities, control = _fresh_control(
            dispatches, session_id=session_id, connection_ref=runtime["connection_ref"],
            repository=repository, previous_issued=issued, now=now,
        )
        governance = {path: (ROOT / path).read_text(encoding="utf-8") for path in DOCUMENTS}
        fresh = harvest_qualification_evidence(
            admission,
            github_request_fn=github_request_fn,
            sessions=sessions,
            dispatches={"items": []},
            claims=claims, tasks=tasks, governance_documents=governance,
            target_repository=repository, requested_branch=branch,
            capability_evidence=capabilities, control_evidence=control,
            gse_state=None, access_policy_document=policy, now=now,
        )
        session_projection = fresh.get("session") or {}
        if session_projection.get("status") != "BOUND" or session_projection.get("session_id") != session_id:
            raise ValueError("REQUALIFIED_SAME_GACR_SESSION_REQUIRED")
        if any((fresh.get(section) or {}).get("status") not in ok for section, ok in (
            ("task", {"RECONCILED", "NOT_REQUIRED"}),
            ("claim", {"RECONCILED", "NOT_REQUIRED"}),
            ("access_policy", {"ALLOW"}),
        )):
            raise ValueError("Q6_Q7_Q11_REVALIDATION_REQUIRED")
        if (fresh.get("repository_baseline") or {}).get("observed_head") != current_head:
            raise ValueError("QUALIFICATION_HEAD_MOVED")
        new_grant = evaluate_access_grant(admission, fresh, now=now)
        if new_grant.get("status") != "AUTHORIZED":
            raise ValueError("Q12_REQUALIFICATION_DENIED:" + str(new_grant.get("reason_code")))
        if (new_grant.get("session_id") != session_id
            or new_grant.get("connection_ref") != runtime["connection_ref"]
            or new_grant.get("bound_head") != current_head
            or new_grant.get("grant_id") == previous.get("grant_id")):
            raise ValueError("RENEWED_GRANT_BINDING_OR_ID_INVALID")
        final = observe_repository(
            repository, branch, request_fn=github_request_fn, observed_at=now
        )
        if final.get("observed_head") != current_head:
            raise ValueError("HEAD_MOVED_DURING_RENEWAL")

        conn.execute(
            "INSERT INTO gscc_q12_renewal_history "
            "(runtime_id,arrival_ref,identity_id,gacr_session_id,old_grant_id,new_grant_id,"
            "old_grant_json,new_grant_json,qualification_evidence_json,control_evidence_ref,"
            "old_head,new_head,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (runtime_id, runtime["arrival_ref"], runtime["identity_id"], session_id,
             previous["grant_id"], new_grant["grant_id"], json.dumps(previous,sort_keys=True),
             json.dumps(new_grant,sort_keys=True), json.dumps(fresh,sort_keys=True),
             control["evidence_ref"], previous.get("bound_head"), current_head, now.isoformat()),
        )
        conn.execute(
            "UPDATE gscc_session_runtime SET qualification_evidence_json=?,access_grant_json=?,"
            "updated_at=? WHERE runtime_id=? AND state='READY_FOR_F1' AND access_grant_json=?",
            (json.dumps(fresh,sort_keys=True),json.dumps(new_grant,sort_keys=True),
             now.isoformat(),runtime_id,runtime["access_grant_json"]),
        )
        if conn.execute("SELECT changes()").fetchone()[0] != 1:
            raise ValueError("CONCURRENT_Q12_RENEWAL_STATE_CHANGED")
        conn.commit()
        return {
            "schema":"gscc-q12-same-arrival-renewal/v1", "status":"REQUALIFIED",
            "runtime_id":runtime_id, "arrival_ref":runtime["arrival_ref"],
            "identity_id":runtime["identity_id"], "session_id":session_id,
            "old_grant_id":previous["grant_id"], "access_grant":new_grant,
            "bound_head":current_head, "control_evidence_ref":control["evidence_ref"],
            "next_gate":"F1", "authority_granted":False, "f1_released":False,
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    p = argparse.ArgumentParser(description="Requalify Q12 for an existing READY_FOR_F1 arrival only")
    p.add_argument("--db",required=True)
    p.add_argument("--runtime-id",required=True)
    p.add_argument("--sessions",default=str(SESSIONS))
    p.add_argument("--dispatches",default=str(DISPATCHES))
    p.add_argument("--claims",default=str(CLAIMS))
    p.add_argument("--tasks",default=str(TASKS))
    p.add_argument("--policy",default=str(POLICY))
    p.add_argument("--current-head",required=True)
    args=p.parse_args()

    def github(url: str) -> dict[str, Any]:
        return github_get_json(url, token=os.environ.get("GITHUB_TOKEN"))
    output=renew_q12(
        Path(args.db),args.runtime_id,Path(args.sessions),
        Path(args.dispatches),args.current_head,github_request_fn=github,
        claims_path=Path(args.claims),tasks_path=Path(args.tasks),
        policy_path=Path(args.policy),
    )
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
