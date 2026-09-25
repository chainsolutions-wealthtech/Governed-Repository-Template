#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / ".governance"
MUTABLE_INTENTS = {"WORK_REQUEST", "CODE_CHANGE", "INFRASTRUCTURE"}


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git_head() -> str:
    cp = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False)
    if cp.returncode != 0:
        raise SystemExit("GOVERNANCE_AGENT_FAILED: unable to observe git HEAD")
    return cp.stdout.strip()


def profile() -> dict:
    value = read_json(GOV / "profile.json")
    if (ROOT / ".template-source").exists() or value.get("initialized") is not True:
        raise SystemExit("GOVERNANCE_AGENT_FAILED: repository is not an initialized instance")
    return value


def guard_expected_head(expected: str | None) -> str:
    current = git_head()
    if expected and expected != current:
        print(json.dumps({
            "status": "HEAD_MOVED",
            "expected_head_sha": expected,
            "current_head_sha": current,
            "may_write": False,
            "next_action": "REOBSERVE_RECONCILE_RECOMPUTE"
        }, indent=2))
        raise SystemExit(3)
    return current


def stable_session_id(repository: str, agent: str, provider: str, strongest_ref: str) -> str:
    raw = json.dumps({
        "repository": repository,
        "agent": agent,
        "provider": provider,
        "strongest_ref": strongest_ref,
    }, sort_keys=True)
    return "session-" + hashlib.sha256(raw.encode()).hexdigest()[:24]


def command_observe(_: argparse.Namespace) -> None:
    p = profile()
    current = git_head()
    memory = read_json(GOV / "canonical-memory" / "current.json")
    work = read_json(GOV / "work" / "work-items.json")
    claims = read_json(GOV / "work" / "claims.json")
    sessions = read_json(GOV / "sessions" / "sessions.json")
    project_profile = read_json(GOV / "project-profile.json")
    infrastructure = read_json(GOV / "infrastructure-intent.json")
    print(json.dumps({
        "status": "OBSERVED",
        "repository": p["repository"],
        "head_sha": current,
        "canonical_revision": memory.get("canonical_revision", 0),
        "work_revision": memory.get("work_revision", 0),
        "memory_observed_head_sha": memory.get("observed_head_sha"),
        "next_action": memory.get("next_action"),
        "project_profile": {
            "selection_status": project_profile.get("selection_status"),
            "selected_profile": project_profile.get("selected_profile"),
            "organization_default_candidate": project_profile.get("organization_default_candidate"),
        },
        "infrastructure": {
            "status": infrastructure.get("status"),
            "server_status": infrastructure.get("deployment_target", {}).get("server_status"),
            "directory_status": infrastructure.get("deployment_target", {}).get("directory_status"),
            "server_access": infrastructure.get("server_access"),
        },
        "active_sessions": [s for s in sessions.get("sessions", []) if s.get("status") == "ACTIVE"],
        "active_claims": [c for c in claims.get("claims", []) if c.get("status") == "ACTIVE"],
        "ready_work_items": [i for i in work.get("items", []) if i.get("status") == "READY"],
    }, ensure_ascii=False, indent=2))


def command_session_start(a: argparse.Namespace) -> None:
    p = profile()
    head = guard_expected_head(a.expected_head)
    store_path = GOV / "sessions" / "sessions.json"
    store = read_json(store_path)
    sessions = store.get("sessions", [])
    provider_ref = a.provider_ref or None
    connection_ref = a.connection_ref or None
    connection_intent = a.intent or "UNKNOWN"
    intent_provenance = "PROVIDED_BY_CLIENT" if a.intent else "DEFAULT_UNKNOWN"

    eligible = [
        s for s in sessions
        if s.get("status") == "ACTIVE"
        and s.get("repository") == p["repository"]
        and s.get("agent_identity") == a.agent
        and s.get("provider") == a.provider
    ]

    matches = []
    if provider_ref:
        matches = [s for s in eligible if s.get("provider_conversation_ref") == provider_ref]
    elif connection_ref:
        matches = [s for s in eligible if s.get("connection_ref") == connection_ref]

    if len(matches) > 1:
        print(json.dumps({"status": "AMBIGUOUS", "may_write": False, "matching_session_ids": [s["session_id"] for s in matches]}, indent=2))
        raise SystemExit(4)

    timestamp = utcnow()
    if len(matches) == 1:
        session = matches[0]
        session["last_seen_at"] = timestamp
        session["last_observed_head_sha"] = head
        if a.intent:
            session["connection_intent"] = connection_intent
            session["connection_intent_provenance"] = intent_provenance
        elif not session.get("connection_intent"):
            session["connection_intent"] = "UNKNOWN"
            session["connection_intent_provenance"] = "DEFAULT_UNKNOWN"
        resolution = "RESUME"
    else:
        strongest_ref = (
            f"provider:{provider_ref}" if provider_ref
            else f"connection:{connection_ref}" if connection_ref
            else f"local:{a.agent}:{head}:{timestamp}"
        )
        session = {
            "session_id": stable_session_id(p["repository"], a.agent, a.provider, strongest_ref),
            "agent_identity": a.agent,
            "provider": a.provider,
            "provider_conversation_ref": provider_ref,
            "provider_conversation_ref_provenance": "PROVIDED_BY_CLIENT" if provider_ref else "UNAVAILABLE",
            "connection_ref": connection_ref,
            "connection_intent": connection_intent,
            "connection_intent_provenance": intent_provenance,
            "repository": p["repository"],
            "starting_head_sha": head,
            "last_observed_head_sha": head,
            "status": "ACTIVE",
            "created_at": timestamp,
            "last_seen_at": timestamp,
        }
        sessions.append(session)
        resolution = "CREATE"

    store["revision"] = int(store.get("revision", 0)) + 1
    store["sessions"] = sessions
    write_json(store_path, store)
    policy = read_json(GOV / "connection-intent-policy.json")
    intent = session.get("connection_intent") or "UNKNOWN"
    intent_rule = policy.get("intents", {}).get(intent, policy.get("intents", {}).get("UNKNOWN", {}))
    print(json.dumps({
        "status": resolution,
        "session": session,
        "intent_route": intent_rule.get("route"),
        "may_dispatch_mutable_work": bool(intent_rule.get("may_dispatch_mutable_work")),
        "may_write": True,
    }, ensure_ascii=False, indent=2))


def dependency_done(item: dict, by_id: dict[str, dict]) -> bool:
    return all(by_id.get(dep, {}).get("status") == "DONE" for dep in item.get("dependencies", []))


def command_dispatch(a: argparse.Namespace) -> None:
    p = profile()
    head = guard_expected_head(a.expected_head)
    sessions = read_json(GOV / "sessions" / "sessions.json")
    session = next((s for s in sessions.get("sessions", []) if s.get("session_id") == a.session_id and s.get("status") == "ACTIVE"), None)
    if not session:
        raise SystemExit("DISPATCH_FAILED: active session not found")

    intent = session.get("connection_intent") or "UNKNOWN"
    if intent not in MUTABLE_INTENTS:
        policy = read_json(GOV / "connection-intent-policy.json")
        route = policy.get("intents", {}).get(intent, policy.get("intents", {}).get("UNKNOWN", {})).get("route")
        print(json.dumps({
            "status": "INTENT_BLOCKS_MUTABLE_DISPATCH",
            "connection_intent": intent,
            "route": route,
            "may_write": False,
            "next_action": "RESOLVE_CONNECTION_INTENT" if intent == "UNKNOWN" else route,
        }, indent=2))
        raise SystemExit(5)

    work_path = GOV / "work" / "work-items.json"
    claims_path = GOV / "work" / "claims.json"
    memory_path = GOV / "canonical-memory" / "current.json"
    work = read_json(work_path)
    claims_doc = read_json(claims_path)
    memory = read_json(memory_path)
    items = work.get("items", [])
    claims = claims_doc.get("claims", [])

    own = [c for c in claims if c.get("status") == "ACTIVE" and c.get("session_id") == a.session_id]
    if len(own) > 1:
        print(json.dumps({"status": "WAIT", "reason": "MULTIPLE_ACTIVE_CLAIMS", "may_write": False}, indent=2))
        raise SystemExit(4)
    if len(own) == 1:
        claim = own[0]
        if claim.get("claimed_head_sha") != head:
            print(json.dumps({
                "status": "HEAD_MOVED",
                "claimed_head_sha": claim.get("claimed_head_sha"),
                "current_head_sha": head,
                "may_write": False,
                "next_action": "REOBSERVE_RECONCILE_RECOMPUTE"
            }, indent=2))
            raise SystemExit(3)
        item = next((i for i in items if i.get("work_item_id") == claim.get("work_item_id")), None)
        print(json.dumps({"status": "CONTINUE", "work_item": item, "claim": claim, "may_write": True}, ensure_ascii=False, indent=2))
        return

    terminal = {"DONE", "CANCELLED", "SUPERSEDED"}
    if items and all(i.get("status") in terminal for i in items):
        print(json.dumps({"status": "COMPLETE", "work_item": None, "may_write": False}, indent=2))
        return

    occupied = {
        domain
        for c in claims
        if c.get("status") == "ACTIVE" and c.get("session_id") != a.session_id
        for domain in c.get("collision_domains", [])
    }
    by_id = {i["work_item_id"]: i for i in items}
    eligible = [
        i for i in items
        if i.get("status") == "READY"
        and dependency_done(i, by_id)
        and not occupied.intersection(i.get("collision_domains", []))
    ]
    eligible.sort(key=lambda i: (-int(i.get("priority", 0)), int(i.get("sequence", 0)), i.get("work_item_id", "")))
    if not eligible:
        print(json.dumps({"status": "WAIT", "reason": "NO_DEPENDENCY_AND_COLLISION_SAFE_WORK", "occupied_collision_domains": sorted(occupied), "may_write": False}, indent=2))
        return

    selected = eligible[0]
    selected["status"] = "IN_PROGRESS"
    claim = {
        "session_id": a.session_id,
        "work_item_id": selected["work_item_id"],
        "collision_domains": selected.get("collision_domains", []),
        "status": "ACTIVE",
        "claimed_head_sha": head,
        "claimed_at": utcnow(),
        "released_at": None,
    }
    claims.append(claim)
    work["revision"] = int(work.get("revision", 0)) + 1
    claims_doc["revision"] = int(claims_doc.get("revision", 0)) + 1
    claims_doc["claims"] = claims
    memory["work_revision"] = int(memory.get("work_revision", 0)) + 1
    memory["next_action"] = selected.get("next_action") or selected["work_item_id"]

    write_json(work_path, work)
    write_json(claims_path, claims_doc)
    write_json(memory_path, memory)
    print(json.dumps({"status": "ASSIGN", "work_item": selected, "claim": claim, "may_write": True}, ensure_ascii=False, indent=2))


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")[:120]


def command_checkpoint(a: argparse.Namespace) -> None:
    head = guard_expected_head(a.expected_head)
    p = profile()
    sessions_path = GOV / "sessions" / "sessions.json"
    sessions = read_json(sessions_path)
    session = next((s for s in sessions.get("sessions", []) if s.get("session_id") == a.session_id), None)
    if not session:
        raise SystemExit("CHECKPOINT_FAILED: session not found")

    timestamp = utcnow()
    checkpoint = {
        "schema_version": "1.0.0",
        "session_id": a.session_id,
        "agent": session["agent_identity"],
        "repository": p["repository"],
        "starting_head_sha": session["starting_head_sha"],
        "observed_head_sha": head,
        "work_item_id": a.work_item,
        "status": a.status,
        "files_read": a.files_read or [],
        "files_changed": a.files_changed or [],
        "evidence_refs": a.evidence or [],
        "checks_run": a.checks or [],
        "blockers": a.blocker or [],
        "next_action": a.next_action,
        "checkpoint_at": timestamp,
    }
    name = f"{timestamp.replace(':','').replace('+','-')}-{safe_name(a.session_id)}.json"
    path = GOV / "checkpoints" / name
    write_json(path, checkpoint)

    session["last_seen_at"] = timestamp
    session["last_observed_head_sha"] = head
    write_json(sessions_path, sessions)

    memory_path = GOV / "canonical-memory" / "current.json"
    memory = read_json(memory_path)
    memory["current_checkpoint"] = str(path.relative_to(ROOT))
    memory["observed_head_sha"] = head
    memory["next_action"] = a.next_action
    memory["canonical_revision"] = int(memory.get("canonical_revision", 0)) + 1
    write_json(memory_path, memory)
    print(json.dumps({"status": "CHECKPOINTED", "path": str(path.relative_to(ROOT)), "checkpoint": checkpoint}, ensure_ascii=False, indent=2))


def command_handoff(a: argparse.Namespace) -> None:
    head = guard_expected_head(a.expected_head)
    p = profile()
    sessions_path = GOV / "sessions" / "sessions.json"
    claims_path = GOV / "work" / "claims.json"
    sessions = read_json(sessions_path)
    claims_doc = read_json(claims_path)
    session = next((s for s in sessions.get("sessions", []) if s.get("session_id") == a.session_id), None)
    if not session:
        raise SystemExit("HANDOFF_FAILED: session not found")

    released = []
    timestamp = utcnow()
    for claim in claims_doc.get("claims", []):
        if claim.get("session_id") == a.session_id and claim.get("status") == "ACTIVE":
            claim["status"] = "RELEASED"
            claim["released_at"] = timestamp
            released.extend(claim.get("collision_domains", []))

    session["status"] = "CLOSED"
    session["last_seen_at"] = timestamp
    session["last_observed_head_sha"] = head
    sessions["revision"] = int(sessions.get("revision", 0)) + 1
    claims_doc["revision"] = int(claims_doc.get("revision", 0)) + 1
    write_json(sessions_path, sessions)
    write_json(claims_path, claims_doc)

    handoff = {
        "schema_version": "1.0.0",
        "from_session_id": a.session_id,
        "from_agent": session["agent_identity"],
        "repository": p["repository"],
        "completed_head_sha": head,
        "last_completed_work_item": a.work_item,
        "released_collision_domains": sorted(set(released)),
        "open_findings": a.finding or [],
        "open_dependencies": a.dependency or [],
        "next_action": a.next_action,
        "handoff_at": timestamp,
    }
    path = GOV / "handoffs" / f"{timestamp.replace(':','').replace('+','-')}-{safe_name(a.session_id)}.json"
    write_json(path, handoff)

    memory_path = GOV / "canonical-memory" / "current.json"
    memory = read_json(memory_path)
    memory["current_handoff"] = str(path.relative_to(ROOT))
    memory["observed_head_sha"] = head
    memory["next_action"] = a.next_action
    memory["canonical_revision"] = int(memory.get("canonical_revision", 0)) + 1
    write_json(memory_path, memory)
    print(json.dumps({"status": "HANDED_OFF", "path": str(path.relative_to(ROOT)), "handoff": handoff}, ensure_ascii=False, indent=2))


def command_intake(a: argparse.Namespace) -> None:
    guard_expected_head(a.expected_head)
    profile()
    cursor_path = GOV / "intake" / "cursor.json"
    cursor = read_json(cursor_path)
    sequence = int(cursor.get("latest_sequence", 0)) + 1
    intake_id = f"INTAKE-{sequence:04d}"
    digest = hashlib.sha256(a.summary.strip().encode()).hexdigest()
    intake = {
        "schema_version": "1.0.0",
        "intake_id": intake_id,
        "sequence": sequence,
        "status": "RECEIVED",
        "source_type": a.source_type,
        "source_id": a.source_id,
        "source_digest": digest,
        "observed_at": utcnow(),
        "summary": a.summary.strip(),
        "disposition": "UNASSESSED",
        "canonical_effect": False,
        "work_effect": False,
    }
    path = GOV / "intake" / f"{intake_id}.json"
    write_json(path, intake)
    cursor["latest_sequence"] = sequence
    cursor["pending_intake_ids"] = list(dict.fromkeys([*cursor.get("pending_intake_ids", []), intake_id]))
    write_json(cursor_path, cursor)
    print(json.dumps({
        "status": "REGISTERED",
        "intake": intake,
        "rule": "INTAKE_NE_CANONICAL_MEMORY_NE_WORK_ITEM",
        "next_action": "EVALUATE_INTAKE_COHERENCE"
    }, ensure_ascii=False, indent=2))


def command_intake_review(a: argparse.Namespace) -> None:
    guard_expected_head(a.expected_head)
    profile()
    path = GOV / "intake" / f"{a.intake_id}.json"
    if not path.exists():
        raise SystemExit("INTAKE_REVIEW_FAILED: intake not found")
    intake = read_json(path)
    if intake.get("status") != "RECEIVED":
        raise SystemExit("INTAKE_REVIEW_FAILED: intake is not pending")

    cursor_path = GOV / "intake" / "cursor.json"
    memory_path = GOV / "canonical-memory" / "current.json"
    cursor = read_json(cursor_path)
    memory = read_json(memory_path)
    disposition = a.disposition

    intake["disposition"] = disposition
    intake["reviewed_at"] = utcnow()
    if disposition == "CONTRADICTION":
        intake["status"] = "HOLD_FOR_REVIEW"
        intake["canonical_effect"] = False
        intake["work_effect"] = False
    elif disposition in {"DUPLICATE", "OUT_OF_SCOPE"}:
        intake["status"] = "ARCHIVED_NO_EFFECT"
        intake["canonical_effect"] = False
        intake["work_effect"] = False
    else:
        intake["status"] = "RECONCILED"
        intake["canonical_effect"] = disposition in {"COMPLEMENT", "DECISION", "FINDING", "MEMORY"}
        intake["work_effect"] = disposition == "TASK"
        if intake["canonical_effect"]:
            memory["canonical_revision"] = int(memory.get("canonical_revision", 0)) + 1
        if intake["work_effect"]:
            memory["work_revision"] = int(memory.get("work_revision", 0)) + 1

    pending = [x for x in cursor.get("pending_intake_ids", []) if x != a.intake_id]
    cursor["pending_intake_ids"] = pending
    if intake["status"] != "HOLD_FOR_REVIEW":
        reconciled = int(cursor.get("reconciled_through_sequence", 0))
        if intake["sequence"] == reconciled + 1:
            cursor["reconciled_through_sequence"] = intake["sequence"]
    cursor["canonical_revision"] = memory.get("canonical_revision", 0)
    cursor["work_revision"] = memory.get("work_revision", 0)
    cursor["last_reconciliation_digest"] = hashlib.sha256(json.dumps(intake, sort_keys=True).encode()).hexdigest()

    write_json(path, intake)
    write_json(cursor_path, cursor)
    write_json(memory_path, memory)
    print(json.dumps({
        "status": intake["status"],
        "disposition": disposition,
        "canonical_effect": intake["canonical_effect"],
        "work_effect": intake["work_effect"],
        "requires_human_review": disposition == "CONTRADICTION",
    }, indent=2))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generic governed repository multi-agent coordinator")
    sub = p.add_subparsers(dest="command", required=True)

    observe = sub.add_parser("observe")
    observe.set_defaults(fn=command_observe)

    start = sub.add_parser("session-start")
    start.add_argument("--agent", required=True)
    start.add_argument("--provider", choices=["chatgpt","claude","codex","github-actions","human","other"], required=True)
    start.add_argument("--provider-ref")
    start.add_argument("--connection-ref")
    start.add_argument("--intent", choices=["OBSERVE","CONTEXT_INTAKE","INFORMATION_INTAKE","WORK_REQUEST","CODE_CHANGE","REVIEW","INFRASTRUCTURE","UNKNOWN"])
    start.add_argument("--expected-head")
    start.set_defaults(fn=command_session_start)

    dispatch = sub.add_parser("dispatch")
    dispatch.add_argument("--session-id", required=True)
    dispatch.add_argument("--expected-head")
    dispatch.set_defaults(fn=command_dispatch)

    checkpoint = sub.add_parser("checkpoint")
    checkpoint.add_argument("--session-id", required=True)
    checkpoint.add_argument("--work-item")
    checkpoint.add_argument("--status", required=True)
    checkpoint.add_argument("--next-action", required=True)
    checkpoint.add_argument("--expected-head")
    checkpoint.add_argument("--files-read", action="append")
    checkpoint.add_argument("--files-changed", action="append")
    checkpoint.add_argument("--evidence", action="append")
    checkpoint.add_argument("--checks", action="append")
    checkpoint.add_argument("--blocker", action="append")
    checkpoint.set_defaults(fn=command_checkpoint)

    handoff = sub.add_parser("handoff")
    handoff.add_argument("--session-id", required=True)
    handoff.add_argument("--work-item")
    handoff.add_argument("--next-action", required=True)
    handoff.add_argument("--expected-head")
    handoff.add_argument("--finding", action="append")
    handoff.add_argument("--dependency", action="append")
    handoff.set_defaults(fn=command_handoff)

    intake = sub.add_parser("intake")
    intake.add_argument("--source-type", choices=["chatgpt","claude","codex","github","human","other"], required=True)
    intake.add_argument("--source-id", required=True)
    intake.add_argument("--summary", required=True)
    intake.add_argument("--expected-head")
    intake.set_defaults(fn=command_intake)

    review = sub.add_parser("intake-review")
    review.add_argument("--intake-id", required=True)
    review.add_argument("--disposition", choices=["DUPLICATE","COMPLEMENT","DECISION","FINDING","TASK","CONTRADICTION","MEMORY","OUT_OF_SCOPE"], required=True)
    review.add_argument("--expected-head")
    review.set_defaults(fn=command_intake_review)

    return p


def main() -> None:
    a = parser().parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
