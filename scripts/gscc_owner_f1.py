#!/usr/bin/env python3
"""Owner Door-A F1 release using signed GitHub event identity and the EXISTING GSCC runtime.

Admission is not a work claim. Native GitHub operations remain subject to the
connected actor's real permissions, branch rules and per-operation validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import urllib.parse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from gscc.admission import validate_access_grant
from gscc.admission_harvester import github_get_json
from gscc_session_runtime import _load_runtime, _route, _session_connection_values, now_iso

# Shared allowlist with the explicit Direct Owner entry; never a second owner registry.
OWNER_POLICY_PATH = Path(__file__).resolve().parents[1] / ".governance" / "repository-entry-gates.json"
_OWNER_POLICY = json.loads(OWNER_POLICY_PATH.read_text(encoding="utf-8"))
if _OWNER_POLICY.get("schema") != "repository-entry-gates/v1":
    raise ValueError("CANONICAL_OWNER_ALLOWLIST_REQUIRED")
OWNER_LOGINS = frozenset(_OWNER_POLICY.get("authenticated_owner_logins") or [])
if not OWNER_LOGINS:
    raise ValueError("CANONICAL_OWNER_ALLOWLIST_EMPTY")
OWNER_OPERATIONS = (
    "read", "review", "supervise", "intake", "plan", "create_branch",
    "create_file", "update_file", "create_pull_request", "review_pull_request",
)
OWNER_ROLES = ("CODE_AGENT", "SUPERVISOR", "INTAKER", "REVIEWER", "PLANNER_AGENT")
OWNER_CLASS = "OWNER_NATIVE_GITHUB_OPERATIONS_ELIGIBLE"


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def verify_owner_event(
    event: dict[str, Any],
    *,
    issue_number: int,
    repository: str,
    branch: str,
    current_head: str,
    github_request_fn: Callable[[str], dict[str, Any]],
    github_actor: str,
    runtime_id: str | None = None,
) -> dict[str, Any]:
    """Only GitHub-signed issue_comment context is accepted by the workflow.

    The event is never accepted from a comment body or caller-supplied role.
    GET /users, GET /repos and GET branch verify account ID/repository/HEAD.
    Repo permission for each WRITE is independently enforced by GitHub at use.
    """
    issue = event.get("issue") or {}
    comment = event.get("comment") or {}
    sender = event.get("sender") or {}
    issue_user = issue.get("user") or {}
    comment_user = comment.get("user") or {}
    repo_event = event.get("repository") or {}
    login = comment_user.get("login")
    actor_id = comment_user.get("id")
    owner_created_issue = (issue_user.get("login") == login
                           and issue_user.get("id") == actor_id)
    raw_command = comment.get("body") or ""
    explicitly_approved = raw_command.startswith("/gscc-owner-f1-approve ")
    if explicitly_approved:
        try:
            approved_request = json.loads(
                raw_command[len("/gscc-owner-f1-approve "):].strip()
            )
        except (ValueError, TypeError):
            raise ValueError("OWNER_F1_APPROVAL_PAYLOAD_INVALID") from None
        if (not isinstance(approved_request, dict)
                or set(approved_request) != {"runtime_id"}
                or not isinstance(approved_request["runtime_id"], str)
                or not runtime_id
                or approved_request["runtime_id"] != runtime_id):
            raise ValueError("OWNER_F1_APPROVAL_RUNTIME_MISMATCH")
    if not owner_created_issue and not explicitly_approved:
        raise ValueError("OWNER_F1_DELEGATED_ARRIVAL_REQUIRES_EXPLICIT_OWNER_APPROVAL")
    if not (
        isinstance(login, str) and login in OWNER_LOGINS
        and github_actor == login
        and sender.get("login") == login
        and sender.get("id") == actor_id
        and isinstance(issue_user.get("login"), str)
        and isinstance(issue_user.get("id"), int)
        and issue.get("number") == issue_number
        and repo_event.get("full_name") == repository
        and isinstance(comment.get("id"), int)
        and isinstance(actor_id, int)
        and event.get("action") == "created"
    ):
        raise ValueError("OWNER_F1_SIGNED_GITHUB_ACTOR_OR_ISSUE_BINDING_REQUIRED")
    account = github_request_fn("https://api.github.com/users/" + urllib.parse.quote(login, safe=""))
    if account.get("login") != login or account.get("id") != actor_id:
        raise ValueError("OWNER_F1_GITHUB_ACCOUNT_IDENTITY_MISMATCH")
    repo = github_request_fn("https://api.github.com/repos/" + repository)
    if repo.get("full_name") != repository or not repo.get("id"):
        raise ValueError("OWNER_F1_REPOSITORY_IDENTITY_MISMATCH")
    observed = github_request_fn(
        "https://api.github.com/repos/" + repository + "/branches/" +
        urllib.parse.quote(branch, safe="")
    )
    sha = (observed.get("commit") or {}).get("sha")
    if not (isinstance(current_head, str) and len(current_head) == 40
            and all(ch in "0123456789abcdef" for ch in current_head)
            and sha == current_head):
        raise ValueError("OWNER_F1_EXACT_LIVE_HEAD_REQUIRED")
    return {
        "schema": "gscc-owner-github-identity-proof/v1",
        "status": "VERIFIED",
        "actor_login": login,
        "actor_id": actor_id,
        "repository": repository,
        "repository_id": str(repo["id"]),
        "branch": branch,
        "observed_head": sha,
        "issue_number": issue_number,
        "comment_id": comment["id"],
        "source": "GITHUB_SIGNED_ISSUE_COMMENT_AND_GITHUB_API_GET",
        "native_permissions": "CHECKED_BY_GITHUB_AT_EACH_OPERATION",
        "proof_ref": f"github-issue-comment:{comment['id']}",
        "approval_mode": (
            "OWNER_SELF_ENTRY" if owner_created_issue
            else "EXPLICIT_OWNER_APPROVAL_FOR_OTHER_AGENT"
        ),
        "owner_created_issue": owner_created_issue,
        "approved_runtime_id": runtime_id if explicitly_approved else None,
        "subject_issue_author": issue_user.get("login"),
    }


def issue_owner_grant(
    previous: dict[str, Any],
    *,
    admission: dict[str, Any],
    runtime: dict[str, Any],
    session_id: str,
    proof: dict[str, Any],
    now: datetime,
) -> dict[str, Any]:
    if not all((
        previous.get("schema") == "gscc-access-grant/v1",
        previous.get("status") == "AUTHORIZED",
        previous.get("admission_id") == admission.get("admission_id"),
        previous.get("session_id") == session_id,
        previous.get("connection_ref") == runtime.get("connection_ref"),
        previous.get("repository") == admission.get("repository"),
        proof.get("status") == "VERIFIED",
        proof.get("repository") == admission.get("repository"),
        proof.get("actor_login") in OWNER_LOGINS,
        proof.get("observed_head"),
    )):
        raise ValueError("OWNER_F1_CANONICAL_Q12_GRANT_AND_SESSION_REQUIRED")
    issued = now.astimezone(timezone.utc).replace(microsecond=0)
    context = {
        "previous_grant_id": previous["grant_id"],
        "admission_id": previous["admission_id"],
        "session_id": session_id,
        "connection_ref": runtime["connection_ref"],
        "repository": admission["repository"],
        "head": proof["observed_head"],
        "proof": proof["proof_ref"],
        "issued_at": issued.isoformat(),
    }
    is_owner_self = proof.get("owner_created_issue") is True
    if not is_owner_self and (
        proof.get("approval_mode") != "EXPLICIT_OWNER_APPROVAL_FOR_OTHER_AGENT"
        or not proof.get("approved_runtime_id")
    ):
        raise ValueError("OWNER_F1_DELEGATION_PROOF_NOT_SCOPED")
    # Approval of another agent's admission never inherits owner privileges.
    mode_fields = ({
        "allowed_authority_classes": sorted(
            set(previous.get("allowed_authority_classes") or [])
            | {OWNER_CLASS, "READ_ONLY_DISCOVERY_AUTHORITY"}
        ),
        "allowed_native_github_operations": list(OWNER_OPERATIONS),
        "allowed_agent_roles": list(OWNER_ROLES),
        "active_role": "CODE_AGENT",
        "role_change_after_admission_allowed": True,
        "owner_permission_model": "NATIVE_GITHUB_PER_OPERATION_NOT_REPOSITORY_ROLE_ESCALATION",
    } if is_owner_self else {
        "allowed_authority_classes": [
            cls for cls in (previous.get("allowed_authority_classes") or [])
            if cls != OWNER_CLASS
        ],
        "allowed_native_github_operations":
            list(previous.get("allowed_native_github_operations") or []),
        "allowed_agent_roles": list(previous.get("allowed_agent_roles") or []),
        "active_role": previous.get("active_role"),
        "role_change_after_admission_allowed":
            previous.get("role_change_after_admission_allowed", False),
        "owner_permission_model": "OWNER_APPROVAL_DOES_NOT_DELEGATE_OWNER_GITHUB_PRIVILEGES",
    })
    grant = deepcopy(previous)
    grant.update(
        grant_id="GSCC-GRANT-" + digest(context),
        bound_head=proof["observed_head"],
        issued_at=issued.isoformat(),
        expires_at=(issued + timedelta(minutes=15)).isoformat(),
        task_id=None if previous.get("task_id") is None else previous["task_id"],
        claim_id=previous.get("claim_id"),
        access_class="GOVERNED_FUNCTION_EXPOSURE_ELIGIBLE",
        owner_identity_evidence_ref=proof["proof_ref"],
        owner_actor_login=proof["actor_login"],
        owner_actor_id=proof["actor_id"],
        owner_approval_mode=proof["approval_mode"],
        approved_subject_identity_id=runtime.get("identity_id"),
        **mode_fields,
        constraints={
            **(previous.get("constraints") or {}),
            "github_native_permissions_enforced": True,
            "branch_protections_enforced": True,
            "ci_enforced": True,
            "no_force_push": True,
            "f1_admission_requires_work_item": False,
            "f1_admission_requires_claim": False,
            "f1_admission_requires_work_lease": False,
            "mutation_requires_native_github_permission": True,
            "direct_main_write": (
                "SUBJECT_TO_NATIVE_GITHUB_PROTECTION" if is_owner_self
                else False
            ),
        },
        invocation_authority_granted=False,
        mutation_authority_granted=False,
    )
    return grant


def release_owner_f1(
    db: Path, runtime_id: str, event: dict[str, Any], current_head: str,
    *,
    sessions: dict[str, Any],
    github_request_fn: Callable[[str], dict[str, Any]],
    github_actor: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    with sqlite3.connect(db) as conn:
        runtime = _load_runtime(conn, runtime_id)
        if runtime["state"] != "READY_FOR_F1":
            raise ValueError("OWNER_F1_EXISTING_READY_FOR_F1_RUNTIME_REQUIRED")
        binding = conn.execute(
            "SELECT gacr_session_id,binding_status,binding_level,connection_ref "
            "FROM gscc_session_bindings WHERE arrival_ref=? AND identity_id=?",
            (runtime["arrival_ref"], runtime["identity_id"]),
        ).fetchall()
        if len(binding) != 1 or binding[0][1:3] != ("GACR_BOUND", "EXACT"):
            raise ValueError("OWNER_F1_CANONICAL_EXACT_GACR_BINDING_REQUIRED")
        session_id = binding[0][0]
        if binding[0][3] != runtime["connection_ref"]:
            raise ValueError("OWNER_F1_GACR_CONNECTION_MISMATCH")
        matches = [
            s for s in sessions.get("sessions", [])
            if isinstance(s, dict) and s.get("session_id") == session_id
            and runtime["connection_ref"] in _session_connection_values(s)
            and s.get("status") == "ACTIVE"
        ]
        if len(matches) != 1:
            raise ValueError("OWNER_F1_ACTIVE_CANONICAL_SESSION_REQUIRED")
        admission = json.loads(runtime["admission_json"] or "{}")
        if admission.get("status") != "PREAUTHORIZED" or not admission.get("admission_id"):
            raise ValueError("OWNER_F1_CANONICAL_ADMISSION_REQUIRED")
        branch = ((admission.get("admission_context") or {}).get("target") or {}).get("requested_branch")
        if not branch:
            raise ValueError("OWNER_F1_ADMISSION_BRANCH_REQUIRED")
        proof = verify_owner_event(
            event, issue_number=runtime["issue_number"], repository=admission["repository"],
            branch=branch, current_head=current_head,
            github_request_fn=github_request_fn, github_actor=github_actor,
            runtime_id=runtime_id,
        )
        previous = json.loads(runtime["access_grant_json"] or "{}")
        grant = issue_owner_grant(
            previous, admission=admission, runtime=runtime, session_id=session_id,
            proof=proof, now=now,
        )
        verified = validate_access_grant(
            grant, connection_ref=runtime["connection_ref"],
            repository=admission["repository"], requested_head=current_head,
            session_id=session_id, now=now,
        )
        if verified.get("status") != "VALIDATED":
            raise ValueError("OWNER_F1_ACCESS_GRANT_INVALID:" + str(verified.get("reason_code")))
        receipt_material = {
            "schema": "gscc-owner-f1-admission-receipt/v1",
            "runtime_id": runtime_id,
            "admission_id": grant["admission_id"],
            "session_id": session_id,
            "connection_ref": runtime["connection_ref"],
            "grant_id": grant["grant_id"],
            "head": current_head,
            "proof_ref": proof["proof_ref"],
            "verified_at": now.isoformat(),
            "approval_mode": proof["approval_mode"],
            "subject_identity_id": runtime["identity_id"],
        }
        f1_receipt = {
            **receipt_material,
            "status": "VERIFIED",
            "receipt_id": "GSCC-OWNER-F1-" + digest(receipt_material),
            "github_native_operations_subject_to_permissions": True,
            "work_claim_required_for_admission": False,
        }
        evidence = {
            "owner_f1_receipt": f1_receipt,
            "access_grant_id": grant["grant_id"],
            "identity_proof": proof,
            "head": current_head,
            "no_task_or_claim_required_for_admission": True,
        }
        # Fail closed on a concurrently modified arrival; do not create a second
        # GSCC session, claim, lease, dispatcher, or inferred function exposure.
        conn.execute(
            "UPDATE gscc_session_runtime SET access_grant_json=?,updated_at=? "
            "WHERE runtime_id=? AND state='READY_FOR_F1' AND access_grant_json=?",
            (json.dumps(grant, sort_keys=True), now_iso(),
             runtime_id, runtime["access_grant_json"]),
        )
        if conn.execute("SELECT changes()").fetchone()[0] != 1:
            raise ValueError("OWNER_F1_CONCURRENT_GRANT_CHANGED")
        conn.commit()

    _route(db, runtime_id, "F1", "F1_VERIFIED", evidence, runtime["identity_id"])
    release_evidence = {
        "schema": "gscc-normal-governance-release/v1",
        "runtime_id": runtime_id,
        "arrival_ref": runtime["arrival_ref"],
        "identity_id": runtime["identity_id"],
        "connection_ref": runtime["connection_ref"],
        "gacr_session_id": session_id,
        "f1_exposure_receipt": None,
        "owner_f1_admission_receipt": f1_receipt["receipt_id"],
        "owner_approval_mode": proof["approval_mode"],
        "access_grant_id": grant["grant_id"],
        "released_head": current_head,
        "next_authority": "00_START_HERE.md",
        "status": "RELEASED",
    }
    _route(db, runtime_id, "00_START_HERE.md", "RELEASED",
           release_evidence, runtime["identity_id"])
    with sqlite3.connect(db) as conn:
        conn.execute(
            "UPDATE gscc_session_runtime SET state='RELEASED_TO_NORMAL_GOVERNANCE',"
            "last_gate='00_START_HERE.md',next_gate=NULL,updated_at=? "
            "WHERE runtime_id=? AND state='READY_FOR_F1'",
            (now_iso(), runtime_id),
        )
        if conn.execute("SELECT changes()").fetchone()[0] != 1:
            raise ValueError("OWNER_F1_CONCURRENT_RELEASE_CHANGED")
        conn.commit()
    return {
        "schema": "gscc-normal-governance-release/v1",
        "state": "RELEASED_TO_NORMAL_GOVERNANCE",
        "runtime_id": runtime_id,
        "gacr_session_id": session_id,
        "connection_ref": runtime["connection_ref"],
        "released_head": current_head,
        "start_here_status": "APPLICABLE",
        "next_authority": "00_START_HERE.md",
        "owner_f1_receipt": f1_receipt,
        "owner_approval_mode": proof["approval_mode"],
        "access_grant": grant,
        "release_evidence": release_evidence,
        "authority_granted": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Signed owner Door-A F1 admission")
    parser.add_argument("--db", required=True)
    parser.add_argument("--runtime-id", required=True)
    parser.add_argument("--sessions", required=True)
    parser.add_argument("--current-head", required=True)
    args = parser.parse_args()
    if os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("GITHUB_EVENT_NAME") != "issue_comment":
        raise SystemExit("OWNER_F1_TRUSTED_GITHUB_ACTIONS_ISSUE_EVENT_REQUIRED")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise SystemExit("OWNER_F1_SIGNED_GITHUB_EVENT_PATH_REQUIRED")
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    repository = (event.get("repository") or {}).get("full_name")
    if repository != os.environ.get("GITHUB_REPOSITORY"):
        raise SystemExit("OWNER_F1_GITHUB_EVENT_REPOSITORY_MISMATCH")
    sessions = json.loads(Path(args.sessions).read_text(encoding="utf-8"))
    result = release_owner_f1(
        Path(args.db), args.runtime_id, event, args.current_head,
        sessions=sessions,
        github_request_fn=lambda url: github_get_json(url, token=os.environ.get("GITHUB_TOKEN")),
        github_actor=os.environ.get("GITHUB_ACTOR", ""),
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
