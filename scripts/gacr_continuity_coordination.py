#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("GACR_ROOT") or Path(__file__).resolve().parents[1]).resolve()
GOV = ROOT / ".governance"
TEMPLATE_SOURCE = (ROOT / ".template-source").exists()

if TEMPLATE_SOURCE:
    STATE_PATH = GOV / "control-plane-state" / "gacr-continuities.json"
    SESSIONS_PATH = GOV / "control-plane-state" / "gacr-sessions.json"
    CLAIMS_PATH = GOV / "control-plane-state" / "gacr-claims.json"
else:
    STATE_PATH = GOV / "agent-relay" / "continuities.json"
    SESSIONS_PATH = GOV / "sessions" / "sessions.json"
    CLAIMS_PATH = GOV / "work" / "claims.json"

WORK_MODES = {"READ_ONLY", "WRITE", "REVIEW"}
ACTIVE_SESSION_STATES = {"ACTIVE"}
ACTIVE_RELAY_STATES = {"ACTIVE"}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,191}$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
LOGICAL_AGENT_ALIAS = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{1,63}$")
OWNER_ALIAS_PROVENANCE = "OWNER_ASSIGNED"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return default or {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def git_head() -> str | None:
    cp = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False)
    return cp.stdout.strip() if cp.returncode == 0 and cp.stdout.strip() else None


def default_state() -> dict:
    return {
        "schema_version": "1.0.0",
        "authority": "DERIVED_GACR_COORDINATION_PROJECTION",
        "projection_only": True,
        "grants_task_authority": False,
        "grants_claim": False,
        "grants_mutation_authority": False,
        "revision": 0,
        "items": [],
    }


def participant_id(continuity_id: str, session_id: str, scope_id: str) -> str:
    raw = f"{continuity_id}|{session_id}|{scope_id}".encode("utf-8")
    return "GACR-P-" + hashlib.sha256(raw).hexdigest()[:12]


def coordination_state_ref(state: dict, continuity_id: str) -> str:
    continuity_id = require_id("continuity_id", continuity_id)
    revision = int(state.get("revision", 0))
    raw = f"{continuity_id}|revision:{revision}".encode("utf-8")
    return "GACR-CS-" + hashlib.sha256(raw).hexdigest()[:16]


def normalize_logical_agent_alias(value: str) -> str:
    alias = str(value or "").strip()
    if not LOGICAL_AGENT_ALIAS.fullmatch(alias):
        raise ValueError("CONTINUITY_COORDINATION_FAILED: invalid logical_agent_alias")
    return alias.upper()


def resolve_logical_agent_alias_docs(
    state: dict,
    sessions_doc: dict,
    *,
    alias: str,
    continuity_id: str | None = None,
) -> dict:
    alias_key = normalize_logical_agent_alias(alias)
    scoped_continuity_id = require_id("continuity_id", continuity_id) if continuity_id else None
    matches: list[dict] = []
    invalid_provenance = []

    for item in state.get("items", []):
        if scoped_continuity_id and item.get("continuity_id") != scoped_continuity_id:
            continue
        for logical_agent in item.get("logical_agents") or []:
            stored_alias = logical_agent.get("human_alias")
            if not stored_alias:
                continue
            try:
                stored_key = normalize_logical_agent_alias(stored_alias)
            except ValueError:
                continue
            if stored_key != alias_key:
                continue
            provenance = logical_agent.get("human_alias_provenance")
            if provenance != OWNER_ALIAS_PROVENANCE:
                invalid_provenance.append({
                    "continuity_id": item.get("continuity_id"),
                    "logical_agent_id": logical_agent.get("logical_agent_id"),
                    "human_alias_provenance": provenance,
                })
                continue
            logical_agent_id = str(logical_agent.get("logical_agent_id") or "").strip()
            if not logical_agent_id:
                continue
            matches.append({
                "continuity_id": item.get("continuity_id"),
                "coordination_issue": item.get("coordination_issue"),
                "repository": item.get("repository"),
                "logical_agent_id": logical_agent_id,
                "logical_agent_id_provenance": logical_agent.get("logical_agent_id_provenance"),
                "human_alias": stored_key,
                "human_alias_provenance": provenance,
                "alias_evidence_ref": logical_agent.get("alias_evidence_ref"),
                "routing_evidence_ref": logical_agent.get("routing_evidence_ref"),
                "reference_session_ids": sorted({
                    str(x) for x in (logical_agent.get("reference_session_ids") or [])
                    if str(x).strip()
                }),
            })

    if invalid_provenance and not matches:
        raise ValueError("LOGICAL_AGENT_ALIAS_UNTRUSTED: owner-assigned provenance required")
    if not matches:
        raise ValueError(f"LOGICAL_AGENT_ALIAS_UNKNOWN: {alias_key}")

    logical_ids = sorted({item["logical_agent_id"] for item in matches})
    if len(logical_ids) != 1:
        raise ValueError(
            "LOGICAL_AGENT_ALIAS_AMBIGUOUS: "
            + alias_key
            + " -> "
            + ",".join(logical_ids)
        )

    logical_agent_id = logical_ids[0]
    canonical_sessions = []
    provider_contexts = []
    for session in sessions_doc.get("sessions", []):
        session_logical_id = session.get("logical_agent_id") or session.get("agent_identity")
        if session_logical_id != logical_agent_id:
            continue
        contexts = [
            dict(context)
            for context in (session.get("provider_contexts") or [])
            if isinstance(context, dict)
        ]
        canonical_sessions.append({
            "session_id": session.get("session_id"),
            "status": session.get("status"),
            "relay_state": (session.get("relay") or {}).get("state"),
            "provider": session.get("provider"),
            "provider_conversation_ref_status": (
                "PRESENT" if session.get("provider_conversation_ref") else "UNAVAILABLE"
            ),
            "connection_ref": session.get("connection_ref"),
            "client_instance_id": session.get("client_instance_id"),
            "provider_context_count": len(contexts),
        })
        for context in contexts:
            value = dict(context)
            value["session_id"] = session.get("session_id")
            value["provider_private_values_invented"] = False
            provider_contexts.append(value)

    canonical_sessions.sort(key=lambda item: str(item.get("session_id") or ""))
    provider_contexts.sort(
        key=lambda item: (
            str(item.get("session_id") or ""),
            str(item.get("provider_context_id") or ""),
        )
    )
    reference_session_ids = sorted({
        ref
        for match in matches
        for ref in match.get("reference_session_ids") or []
    })
    return {
        "status": "LOGICAL_AGENT_ALIAS_RESOLVED",
        "human_alias": alias_key,
        "human_alias_provenance": OWNER_ALIAS_PROVENANCE,
        "logical_agent_id": logical_agent_id,
        "continuity_memberships": sorted(
            matches,
            key=lambda item: (str(item.get("continuity_id") or ""), int(item.get("coordination_issue") or 0)),
        ),
        "reference_session_ids": reference_session_ids,
        "sessions": canonical_sessions,
        "provider_contexts": provider_contexts,
        "session_count": len(canonical_sessions),
        "provider_context_count": len(provider_contexts),
        "projection_only": True,
        "grants_task_authority": False,
        "grants_claim": False,
        "grants_mutation_authority": False,
    }


def normalize_domains(values: list[str] | None) -> list[str]:
    domains = sorted({str(value).strip() for value in (values or []) if str(value).strip()})
    if not domains:
        raise ValueError("CONTINUITY_COORDINATION_FAILED: collision_domains required")
    for value in domains:
        if not SAFE_ID.fullmatch(value):
            raise ValueError(f"CONTINUITY_COORDINATION_FAILED: unsafe collision domain {value!r}")
    return domains


def require_id(name: str, value: str) -> str:
    value = str(value or "").strip()
    if not SAFE_ID.fullmatch(value):
        raise ValueError(f"CONTINUITY_COORDINATION_FAILED: invalid {name}")
    return value


def require_exact_head(observed_head: str, current_head: str | None) -> None:
    if not SHA40.fullmatch(str(observed_head or "")):
        raise ValueError("CONTINUITY_COORDINATION_FAILED: observed_head must be a 40-hex SHA")
    if not current_head or not SHA40.fullmatch(current_head):
        raise ValueError("CONTINUITY_COORDINATION_FAILED: current repository HEAD unavailable")
    if observed_head != current_head:
        raise ValueError(f"HEAD_MOVED: observed={observed_head} current={current_head}")


def canonical_session(sessions_doc: dict, session_id: str) -> dict:
    session = next((item for item in sessions_doc.get("sessions", []) if item.get("session_id") == session_id), None)
    if not session:
        raise ValueError("CONTINUITY_COORDINATION_FAILED: canonical session not found")
    relay = session.get("relay") or {}
    if session.get("status") not in ACTIVE_SESSION_STATES or relay.get("state") not in ACTIVE_RELAY_STATES:
        raise ValueError(
            "CONTINUITY_COORDINATION_FAILED: session must be ACTIVE; stalled/takeover/standby sessions require governed reconciliation"
        )
    return session


def foreign_claim_conflicts(claims_doc: dict, session_id: str, domains: set[str]) -> list[dict]:
    conflicts = []
    for claim in claims_doc.get("claims", []):
        if claim.get("status") != "ACTIVE" or claim.get("session_id") == session_id:
            continue
        claim_domains = set(claim.get("collision_domains") or [])
        overlap = sorted(domains & claim_domains)
        if overlap:
            conflicts.append({
                "claim_id": claim.get("claim_id"),
                "session_id": claim.get("session_id"),
                "work_item_id": claim.get("work_item_id"),
                "collision_domains": overlap,
            })
    return conflicts


def continuity_item(state: dict, continuity_id: str, repository: str, coordination_issue: int, timestamp: str) -> dict:
    item = next((entry for entry in state.setdefault("items", []) if entry.get("continuity_id") == continuity_id), None)
    if item:
        if item.get("repository") not in {None, repository}:
            raise ValueError("CONTINUITY_COORDINATION_FAILED: continuity_id belongs to another repository")
        existing_issue = item.get("coordination_issue")
        if existing_issue not in {None, coordination_issue}:
            raise ValueError("CONTINUITY_COORDINATION_FAILED: continuity coordination issue mismatch")
        return item
    item = {
        "continuity_id": continuity_id,
        "repository": repository,
        "coordination_issue": coordination_issue,
        "created_at": timestamp,
        "updated_at": timestamp,
        "projection_only": True,
        "grants_task_authority": False,
        "grants_claim": False,
        "grants_mutation_authority": False,
        "participants": [],
        "last_handoff": None,
    }
    state["items"].append(item)
    return item


def declare_scope_docs(
    state: dict,
    sessions_doc: dict,
    claims_doc: dict,
    *,
    repository: str,
    continuity_id: str,
    coordination_issue: int,
    coordination_state_ref: str,
    session_id: str,
    declared_role: str | None,
    scope_id: str,
    work_mode: str,
    collision_domains: list[str],
    observed_head: str,
    current_head: str | None,
    evidence_ref: str,
    timestamp: str,
) -> dict:
    continuity_id = require_id("continuity_id", continuity_id)
    scope_id = require_id("scope_id", scope_id)
    if not isinstance(coordination_issue, int) or coordination_issue <= 0:
        raise ValueError("CONTINUITY_COORDINATION_FAILED: positive coordination_issue required")
    coordination_state_ref = str(coordination_state_ref or "").strip()
    if not coordination_state_ref:
        raise ValueError("CONTINUITY_COORDINATION_FAILED: coordination_state_ref required")
    expected_state_ref = globals()["coordination_state_ref"](state, continuity_id)
    if coordination_state_ref != expected_state_ref:
        raise ValueError(
            f"STALE_COORDINATION_STATE_REF: observed={coordination_state_ref} expected={expected_state_ref}"
        )
    if work_mode not in WORK_MODES:
        raise ValueError("CONTINUITY_COORDINATION_FAILED: unsupported work_mode")
    domains = normalize_domains(collision_domains)
    require_exact_head(observed_head, current_head)
    canonical_session(sessions_doc, session_id)

    item = continuity_item(state, continuity_id, repository, coordination_issue, timestamp)
    participants = item.setdefault("participants", [])
    active = [p for p in participants if p.get("status") == "ACTIVE"]
    same = next((p for p in active if p.get("session_id") == session_id and p.get("scope_id") == scope_id), None)

    for other in active:
        if same is other:
            continue
        if other.get("session_id") != session_id and other.get("scope_id") == scope_id:
            raise ValueError(
                f"CONTINUITY_SCOPE_COLLISION: scope_id {scope_id} already active in session {other.get('session_id')}"
            )
        if work_mode == "WRITE" and other.get("work_mode") == "WRITE":
            overlap = sorted(set(domains) & set(other.get("collision_domains") or []))
            if overlap:
                raise ValueError(
                    "CONTINUITY_WRITER_COLLISION: overlapping active writer domains " + ",".join(overlap)
                )

    claim_conflicts = []
    if work_mode == "WRITE":
        claim_conflicts = foreign_claim_conflicts(claims_doc, session_id, set(domains))
        if claim_conflicts:
            raise ValueError(
                "FOREIGN_CANONICAL_CLAIM_COLLISION: " +
                ",".join(sorted({d for item in claim_conflicts for d in item["collision_domains"]}))
            )

    record = {
        "participant_id": participant_id(continuity_id, session_id, scope_id),
        "session_id": session_id,
        "declared_role": declared_role,
        "scope_id": scope_id,
        "work_mode": work_mode,
        "collision_domains": domains,
        "observed_head_sha": observed_head,
        "coordination_state_ref": coordination_state_ref,
        "status": "ACTIVE",
        "membership_state": "PERSISTENT",
        "declared_at": same.get("declared_at") if same else timestamp,
        "last_updated_at": timestamp,
        "evidence_ref": evidence_ref,
        "handoff_ref": None,
        "grants_task_authority": False,
        "grants_claim": False,
        "grants_mutation_authority": False,
    }
    if same:
        same.clear()
        same.update(record)
    else:
        participants.append(record)

    item["updated_at"] = timestamp
    state["revision"] = int(state.get("revision", 0)) + 1
    next_state_ref = globals()["coordination_state_ref"](state, continuity_id)
    return {
        "status": "CONTINUITY_SCOPE_DECLARED",
        "continuity_id": continuity_id,
        "participant": record,
        "accepted_coordination_state_ref": coordination_state_ref,
        "next_coordination_state_ref": next_state_ref,
        "canonical_claim_conflicts": claim_conflicts,
        "authority_preserved": True,
        "grants_task_authority": False,
        "grants_claim": False,
        "grants_mutation_authority": False,
    }


def yield_scope_docs(
    state: dict,
    sessions_doc: dict,
    *,
    continuity_id: str,
    session_id: str,
    scope_id: str,
    observed_head: str,
    current_head: str | None,
    handoff_ref: str,
    evidence_ref: str,
    timestamp: str,
) -> dict:
    continuity_id = require_id("continuity_id", continuity_id)
    scope_id = require_id("scope_id", scope_id)
    require_exact_head(observed_head, current_head)
    canonical_session(sessions_doc, session_id)
    handoff_ref = str(handoff_ref or "").strip()
    if not handoff_ref:
        raise ValueError("CONTINUITY_COORDINATION_FAILED: handoff_ref required")

    item = next((entry for entry in state.get("items", []) if entry.get("continuity_id") == continuity_id), None)
    if not item:
        raise ValueError("CONTINUITY_COORDINATION_FAILED: continuity_id not found")
    participant = next((
        p for p in item.get("participants", [])
        if p.get("session_id") == session_id and p.get("scope_id") == scope_id and p.get("status") == "ACTIVE"
    ), None)
    if not participant:
        raise ValueError("CONTINUITY_COORDINATION_FAILED: active participant scope not found")

    participant["status"] = "YIELDED"
    participant["membership_state"] = "PERSISTENT"
    participant["yielded_at"] = timestamp
    participant["last_updated_at"] = timestamp
    participant["observed_head_sha"] = observed_head
    participant["handoff_ref"] = handoff_ref
    participant["evidence_ref"] = evidence_ref
    item["last_handoff"] = {
        "session_id": session_id,
        "scope_id": scope_id,
        "handoff_ref": handoff_ref,
        "observed_head_sha": observed_head,
        "yielded_at": timestamp,
        "evidence_ref": evidence_ref,
    }
    item["updated_at"] = timestamp
    state["revision"] = int(state.get("revision", 0)) + 1
    return {
        "status": "CONTINUITY_SCOPE_YIELDED",
        "continuity_id": continuity_id,
        "session_id": session_id,
        "scope_id": scope_id,
        "handoff_ref": handoff_ref,
        "claims_changed": False,
        "authority_transferred": False,
        "grants_mutation_authority": False,
    }


def load_runtime() -> tuple[dict, dict, dict]:
    return (
        read_json(STATE_PATH, default_state()),
        read_json(SESSIONS_PATH, {"sessions": []}),
        read_json(CLAIMS_PATH, {"claims": []}),
    )


def command_declare(a: argparse.Namespace) -> None:
    state, sessions, claims = load_runtime()
    result = declare_scope_docs(
        state,
        sessions,
        claims,
        repository=a.repository or os.environ.get("GITHUB_REPOSITORY") or "UNKNOWN_REPOSITORY",
        continuity_id=a.continuity_id,
        coordination_issue=a.coordination_issue,
        coordination_state_ref=a.coordination_state_ref,
        session_id=a.session_id,
        declared_role=a.declared_role,
        scope_id=a.scope_id,
        work_mode=a.work_mode,
        collision_domains=a.collision_domain,
        observed_head=a.observed_head,
        current_head=git_head(),
        evidence_ref=a.evidence_ref,
        timestamp=now_iso(),
    )
    write_json(STATE_PATH, state)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_yield(a: argparse.Namespace) -> None:
    state, sessions, _ = load_runtime()
    result = yield_scope_docs(
        state,
        sessions,
        continuity_id=a.continuity_id,
        session_id=a.session_id,
        scope_id=a.scope_id,
        observed_head=a.observed_head,
        current_head=git_head(),
        handoff_ref=a.handoff_ref,
        evidence_ref=a.evidence_ref,
        timestamp=now_iso(),
    )
    write_json(STATE_PATH, state)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_status(a: argparse.Namespace) -> None:
    state, _, _ = load_runtime()
    item = next((entry for entry in state.get("items", []) if entry.get("continuity_id") == a.continuity_id), None)
    current_state_ref = coordination_state_ref(state, a.continuity_id)
    print(json.dumps({
        "status": "FOUND" if item else "NOT_FOUND",
        "continuity_id": a.continuity_id,
        "state_revision": int(state.get("revision", 0)),
        "coordination_state_ref": current_state_ref,
        "continuity": item,
        "projection_authority": {
            "projection_only": True,
            "grants_task_authority": False,
            "grants_claim": False,
            "grants_mutation_authority": False,
        },
    }, indent=2, ensure_ascii=False))


def command_resolve_alias(a: argparse.Namespace) -> None:
    state = read_json(STATE_PATH, default_state())
    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    result = resolve_logical_agent_alias_docs(
        state,
        sessions,
        alias=a.alias,
        continuity_id=a.continuity_id,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="GACR shared continuity coordination projection")
    sub = p.add_subparsers(dest="command", required=True)

    declare = sub.add_parser("declare")
    declare.add_argument("--repository")
    declare.add_argument("--session-id", required=True)
    declare.add_argument("--continuity-id", required=True)
    declare.add_argument("--coordination-issue", required=True, type=int)
    declare.add_argument("--coordination-state-ref", required=True)
    declare.add_argument("--declared-role")
    declare.add_argument("--scope-id", required=True)
    declare.add_argument("--work-mode", choices=sorted(WORK_MODES), required=True)
    declare.add_argument("--collision-domain", action="append", required=True)
    declare.add_argument("--observed-head", required=True)
    declare.add_argument("--evidence-ref", required=True)
    declare.set_defaults(fn=command_declare)

    release = sub.add_parser("yield")
    release.add_argument("--session-id", required=True)
    release.add_argument("--continuity-id", required=True)
    release.add_argument("--scope-id", required=True)
    release.add_argument("--observed-head", required=True)
    release.add_argument("--handoff-ref", required=True)
    release.add_argument("--evidence-ref", required=True)
    release.set_defaults(fn=command_yield)

    status = sub.add_parser("status")
    status.add_argument("--continuity-id", required=True)
    status.set_defaults(fn=command_status)

    resolve_alias = sub.add_parser("resolve-alias")
    resolve_alias.add_argument("--alias", required=True)
    resolve_alias.add_argument("--continuity-id")
    resolve_alias.set_defaults(fn=command_resolve_alias)
    return p


def main() -> None:
    args = parser().parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
