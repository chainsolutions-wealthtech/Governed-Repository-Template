#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import gacr_agent_telemetry as telemetry

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / ".governance"
TEMPLATE_SOURCE = (ROOT / ".template-source").exists()

SESSIONS_PATH = telemetry.SESSIONS_PATH
CLAIMS_PATH = telemetry.CLAIMS_PATH
BEACONS_PATH = telemetry.BEACONS_PATH
CORRELATIONS_PATH = telemetry.CORRELATIONS_PATH
DISPATCHES_PATH = telemetry.DISPATCHES_PATH
WORK_ITEMS_PATH = GOV / "work" / "work-items.json"
CONFIG_PATH = GOV / "agent-relay" / "config.json"

AVAILABILITY_STATES = {
    "AVAILABLE",
    "WAITING",
    "BUSY",
    "BLOCKED",
    "RATE_LIMITED",
    "QUOTA_BLOCKED",
    "CHECKPOINTING",
    "TERMINATING",
    "STALLED",
    "TERMINAL",
    "UNKNOWN",
}
DISPATCHABLE_STATES = {"AVAILABLE", "WAITING"}
EXPLICIT_BLOCK_INTERRUPTION_MAP = {
    "PROVIDER_RATE_LIMIT": "RATE_LIMITED",
    "PROVIDER_QUOTA_EXHAUSTED": "QUOTA_BLOCKED",
    "CONTEXT_LIMIT": "BLOCKED",
    "WAITING_FOR_INPUT": "BLOCKED",
    "DEPENDENCY_BLOCKED": "BLOCKED",
}
TERMINAL_RELAY_STATES = {"CLOSED", "HANDOFF_STALLED"}
DONE_WORK_STATUSES = {"DONE", "COMPLETED", "PASS", "CLOSED"}


def read_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return default or {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def config() -> dict:
    raw = read_json(CONFIG_PATH, {})
    dispatch = raw.get("capacity_dispatch") or {}
    return {
        "max_parallel_offers_per_session": int(dispatch.get("max_parallel_offers_per_session", 1)),
        "available_states": list(dispatch.get("available_states") or sorted(DISPATCHABLE_STATES)),
        "require_explicit_availability": bool(dispatch.get("require_explicit_availability", True)),
        "require_explicit_work_compatibility": bool(dispatch.get("require_explicit_work_compatibility", True)),
    }


def _active_claims(claims_doc: dict, session_id: str | None = None) -> list[dict]:
    values = [
        item for item in claims_doc.get("claims", [])
        if item.get("status") == "ACTIVE"
        and (session_id is None or item.get("session_id") == session_id)
    ]
    values.sort(key=lambda item: (str(item.get("work_item_id") or ""), str(item.get("claim_id") or "")))
    return values


def _related_beacons(session_id: str, beacons_doc: dict, correlations_doc: dict) -> list[dict]:
    return telemetry._session_beacons(session_id, beacons_doc, correlations_doc)


def _latest_explicit_availability(items: list[dict]) -> dict | None:
    for item in reversed(items):
        state = item.get("availability_state")
        if state:
            return {
                "state": state,
                "reason_code": item.get("availability_reason_code") or "UNSPECIFIED",
                "observed_at": item.get("observed_at"),
                "beacon_id": item.get("beacon_id"),
                "provenance": "EXPLICIT_AGENT_OR_PROVIDER_SIGNAL",
            }
    return None


def _latest_interruption(items: list[dict]) -> dict | None:
    for item in reversed(items):
        code = item.get("interruption_code")
        if code:
            return {
                "code": code,
                "observed_at": item.get("observed_at"),
                "beacon_id": item.get("beacon_id"),
            }
    return None


def session_capacity_projection(
    session_id: str,
    *,
    generated_at: str | None = None,
    sessions_doc: dict | None = None,
    claims_doc: dict | None = None,
    beacons_doc: dict | None = None,
    correlations_doc: dict | None = None,
    signal_projection: dict | None = None,
) -> dict:
    sessions_doc = sessions_doc or read_json(SESSIONS_PATH, {"sessions": []})
    claims_doc = claims_doc or read_json(CLAIMS_PATH, {"claims": []})
    beacons_doc = beacons_doc or read_json(BEACONS_PATH, {"items": []})
    correlations_doc = correlations_doc or read_json(CORRELATIONS_PATH, {"items": []})
    session = telemetry.session_by_id(sessions_doc, session_id)
    if not session:
        raise ValueError("session not found")

    signal = signal_projection or telemetry.session_signal_projection(session_id, generated_at=generated_at)
    related = _related_beacons(session_id, beacons_doc, correlations_doc)
    actions = telemetry._action_projection(related)
    explicit = _latest_explicit_availability(related)
    interruption = _latest_interruption(related)
    active_claims = _active_claims(claims_doc, session_id)
    relay = session.get("relay") or {}
    liveness = (signal.get("liveness") or {}).get("state") or "UNKNOWN"
    progress = (signal.get("progress") or {}).get("state") or "UNKNOWN"

    state = "UNKNOWN"
    reason = "NO_EXPLICIT_CAPACITY_SIGNAL"

    if session.get("status") == "CLOSED" or relay.get("state") in TERMINAL_RELAY_STATES or liveness == "TERMINAL":
        state = "TERMINAL"
        reason = "SESSION_TERMINAL"
    elif interruption and interruption.get("code") in EXPLICIT_BLOCK_INTERRUPTION_MAP:
        state = EXPLICIT_BLOCK_INTERRUPTION_MAP[interruption["code"]]
        reason = interruption["code"]
    elif explicit and explicit.get("state") in {"RATE_LIMITED", "QUOTA_BLOCKED", "BLOCKED", "CHECKPOINTING", "TERMINATING"}:
        state = explicit["state"]
        reason = explicit.get("reason_code") or "EXPLICIT_CAPACITY_SIGNAL"
    elif liveness in {"STALLED", "SUSPECTED_STALL"}:
        state = "STALLED"
        reason = f"LIVENESS_{liveness}"
    elif active_claims or actions.get("in_flight_action"):
        state = "BUSY"
        reason = "ACTIVE_CLAIM_OR_IN_FLIGHT_ACTION"
    elif explicit and explicit.get("state") in {"AVAILABLE", "WAITING", "BUSY"}:
        state = explicit["state"]
        reason = explicit.get("reason_code") or "EXPLICIT_CAPACITY_SIGNAL"
    elif relay.get("state") == "STANDBY":
        state = "AVAILABLE"
        reason = "CANONICAL_STANDBY_STATE"

    cfg = config()
    live_enough = liveness in {"ACTIVE", "QUIET"} or relay.get("state") == "STANDBY"
    explicit_required = cfg["require_explicit_availability"]
    explicit_available = bool(explicit and explicit.get("state") in set(cfg["available_states"]))
    standby_available = relay.get("state") == "STANDBY"
    eligible = (
        state in set(cfg["available_states"])
        and live_enough
        and not active_claims
        and not actions.get("in_flight_action")
        and (explicit_available or standby_available or not explicit_required)
    )

    value = {
        "session_id": session_id,
        "generated_at": generated_at or telemetry.now_iso(),
        "repository": session.get("repository"),
        "provider": session.get("provider"),
        "client_instance_id": session.get("client_instance_id"),
        "agent_role": session.get("agent_role"),
        "capabilities": sorted(set(session.get("capabilities") or [])),
        "authority_grants": sorted(set(session.get("authority_grants") or [])),
        "relay_state": relay.get("state"),
        "task_id": relay.get("task_id"),
        "branch": relay.get("branch"),
        "pull_request": relay.get("pull_request"),
        "liveness_state": liveness,
        "progress_state": progress,
        "availability_state": state,
        "availability_reason": reason,
        "explicit_availability": explicit,
        "latest_interruption": interruption,
        "active_claim_count": len(active_claims),
        "active_claims": [
            {
                "claim_id": item.get("claim_id"),
                "work_item_id": item.get("work_item_id"),
                "collision_domains": item.get("collision_domains") or [],
            }
            for item in active_claims
        ],
        "in_flight_action": actions.get("in_flight_action"),
        "eligible_for_new_work": eligible,
        "eligibility_requires_offer_acceptance": True,
        "grants_write_authority": False,
    }
    telemetry.assert_secretless(value)
    return value


def agent_pool_projection(*, generated_at: str | None = None) -> dict:
    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    claims = read_json(CLAIMS_PATH, {"claims": []})
    beacons = read_json(BEACONS_PATH, {"items": []})
    correlations = read_json(CORRELATIONS_PATH, {"items": []})
    items = []
    for session in sessions.get("sessions", []):
        session_id = session.get("session_id")
        if not session_id:
            continue
        items.append(session_capacity_projection(
            session_id,
            generated_at=generated_at,
            sessions_doc=sessions,
            claims_doc=claims,
            beacons_doc=beacons,
            correlations_doc=correlations,
        ))
    items.sort(key=lambda item: (0 if item.get("eligible_for_new_work") else 1, str(item.get("session_id") or "")))
    counts: dict[str, int] = {}
    for item in items:
        state = item.get("availability_state") or "UNKNOWN"
        counts[state] = counts.get(state, 0) + 1
    return {
        "process": "GACR",
        "model": "AGENT_CAPACITY_POOL",
        "generated_at": generated_at or telemetry.now_iso(),
        "counts": counts,
        "eligible_session_ids": [x["session_id"] for x in items if x.get("eligible_for_new_work")],
        "items": items,
        "provider_private_limit_inference": False,
    }


def _dependencies_satisfied(item: dict, by_id: dict[str, dict]) -> tuple[bool, list[str]]:
    unresolved = []
    for dep in item.get("dependencies") or []:
        dependency = by_id.get(dep)
        if not dependency or dependency.get("status") not in DONE_WORK_STATUSES:
            unresolved.append(dep)
    return not unresolved, unresolved


def _active_collision_domains(claims_doc: dict) -> set[str]:
    return {
        domain
        for claim in _active_claims(claims_doc)
        for domain in (claim.get("collision_domains") or [])
        if domain
    }


def _work_has_explicit_compatibility_scope(item: dict) -> bool:
    return any(
        item.get(field)
        for field in ("allowed_agent_roles", "required_capabilities", "required_authorities", "target_session_id")
    )


def _candidate_compatible(candidate: dict, item: dict) -> tuple[bool, list[str]]:
    reasons = []
    target_session_id = item.get("target_session_id")
    if target_session_id and target_session_id != candidate.get("session_id"):
        reasons.append("TARGET_SESSION_MISMATCH")
    required_capabilities = set(item.get("required_capabilities") or [])
    missing_capabilities = sorted(required_capabilities - set(candidate.get("capabilities") or []))
    if missing_capabilities:
        reasons.extend([f"MISSING_CAPABILITY:{value}" for value in missing_capabilities])

    required_authorities = set(item.get("required_authorities") or [])
    missing_authorities = sorted(required_authorities - set(candidate.get("authority_grants") or []))
    if missing_authorities:
        reasons.extend([f"MISSING_AUTHORITY:{value}" for value in missing_authorities])

    allowed_roles = set(item.get("allowed_agent_roles") or [])
    role = candidate.get("agent_role")
    if allowed_roles and role not in allowed_roles:
        reasons.append("AGENT_ROLE_NOT_ALLOWED")

    repository = item.get("repository")
    if repository and repository != candidate.get("repository"):
        reasons.append("REPOSITORY_MISMATCH")

    return not reasons, reasons


def parallel_work_dispatch_plan(
    *,
    generated_at: str | None = None,
    work_doc: dict | None = None,
    claims_doc: dict | None = None,
    pool: dict | None = None,
) -> dict:
    work_doc = work_doc or read_json(WORK_ITEMS_PATH, {"items": []})
    claims_doc = claims_doc or read_json(CLAIMS_PATH, {"claims": []})
    pool = pool or agent_pool_projection(generated_at=generated_at)
    by_id = {item.get("work_item_id"): item for item in work_doc.get("items", []) if item.get("work_item_id")}
    ready = [item for item in work_doc.get("items", []) if item.get("status") == "READY"]
    ready.sort(key=lambda item: (-int(item.get("priority") or 0), int(item.get("sequence") or 0), str(item.get("work_item_id") or "")))

    active_claims = _active_claims(claims_doc)
    claimed_work = {item.get("work_item_id") for item in active_claims}
    occupied_domains = _active_collision_domains(claims_doc)
    planned_domains: set[str] = set()
    cfg = config()
    planned_per_session: dict[str, int] = {}
    assignments = []
    unassigned = []

    candidates = [item for item in pool.get("items", []) if item.get("eligible_for_new_work")]

    for item in ready:
        work_item_id = item.get("work_item_id")
        if not work_item_id:
            continue
        if work_item_id in claimed_work:
            unassigned.append({"work_item_id": work_item_id, "reason": "ALREADY_CLAIMED"})
            continue

        if cfg["require_explicit_work_compatibility"] and not _work_has_explicit_compatibility_scope(item):
            unassigned.append({
                "work_item_id": work_item_id,
                "reason": "WORK_COMPATIBILITY_SCOPE_UNDECLARED",
            })
            continue

        deps_ok, unresolved = _dependencies_satisfied(item, by_id)
        if not deps_ok:
            unassigned.append({"work_item_id": work_item_id, "reason": "DEPENDENCIES_UNRESOLVED", "dependencies": unresolved})
            continue

        domains = set(item.get("collision_domains") or [])
        collision = sorted(domains & (occupied_domains | planned_domains))
        if collision:
            unassigned.append({"work_item_id": work_item_id, "reason": "COLLISION_DOMAIN_BUSY", "collision_domains": collision})
            continue

        evaluations = []
        eligible = []
        for candidate in candidates:
            session_id = candidate.get("session_id")
            if planned_per_session.get(session_id, 0) >= cfg["max_parallel_offers_per_session"]:
                evaluations.append({"session_id": session_id, "status": "INELIGIBLE", "reasons": ["SESSION_OFFER_CAPACITY_REACHED"]})
                continue
            compatible, reasons = _candidate_compatible(candidate, item)
            evaluations.append({
                "session_id": session_id,
                "status": "ELIGIBLE" if compatible else "INELIGIBLE",
                "reasons": reasons,
            })
            if compatible:
                eligible.append(candidate)

        if not eligible:
            unassigned.append({"work_item_id": work_item_id, "reason": "NO_COMPATIBLE_AVAILABLE_AGENT", "evaluations": evaluations})
            continue

        eligible.sort(key=lambda candidate: (
            planned_per_session.get(candidate.get("session_id"), 0),
            str(candidate.get("session_id") or ""),
        ))
        selected = eligible[0]
        session_id = selected["session_id"]
        planned_per_session[session_id] = planned_per_session.get(session_id, 0) + 1
        planned_domains.update(domains)

        assignments.append({
            "work_item_id": work_item_id,
            "task_id": item.get("task_id") or work_item_id,
            "title": item.get("title"),
            "target_session_id": session_id,
            "target_client_instance_id": selected.get("client_instance_id"),
            "collision_domains": sorted(domains),
            "required_capabilities": sorted(set(item.get("required_capabilities") or [])),
            "required_authorities": sorted(set(item.get("required_authorities") or [])),
            "allowed_agent_roles": sorted(set(item.get("allowed_agent_roles") or [])),
            "evaluations": evaluations,
            "requires_offer_acceptance": True,
            "requires_claim_after_acceptance": True,
            "requires_exact_head_reconciliation": True,
            "grants_write_authority": False,
        })

    value = {
        "process": "GACR",
        "model": "PARALLEL_WORK_DISPATCH_PLAN",
        "generated_at": generated_at or telemetry.now_iso(),
        "assignments": assignments,
        "unassigned": unassigned,
        "parallel_assignment_count": len(assignments),
        "occupied_collision_domains": sorted(occupied_domains),
        "planned_collision_domains": sorted(planned_domains),
        "claim_transfer_performed": False,
        "write_authority_granted": False,
    }
    telemetry.assert_secretless(value)
    return value


def _delivery_modes(session: dict) -> list[str]:
    channels = set(session.get("wake_channels") or [])
    modes = ["POLL_REPOSITORY"]
    if "REPOSITORY_DISPATCH" in channels:
        modes.append("REPOSITORY_DISPATCH")
    return modes


def dispatch_ready_work(*, generated_at: str | None = None) -> dict:
    plan = parallel_work_dispatch_plan(generated_at=generated_at)
    if not plan.get("assignments"):
        return {"changed": 0, "items": [], "plan": plan}

    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    store = read_json(DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    changes = []

    for assignment in plan["assignments"]:
        work_item_id = assignment["work_item_id"]
        target_session_id = assignment["target_session_id"]
        existing = next((
            item for item in store.get("items", [])
            if item.get("dispatch_kind") == "WORK_OFFER"
            and item.get("work_item_id") == work_item_id
            and item.get("target_session_id") == target_session_id
            and item.get("status") in {"READY", "ACCEPTED_PENDING_CLAIM", "ACTIVATED"}
        ), None)
        if existing:
            continue
        session = telemetry.session_by_id(sessions, target_session_id)
        if not session:
            continue
        dispatch_id = telemetry.runtime_id("GACR-W-", {
            "work_item_id": work_item_id,
            "target_session_id": target_session_id,
            "generated_at": generated_at or telemetry.now_iso(),
        })
        item = {
            "dispatch_id": dispatch_id,
            "dispatch_kind": "WORK_OFFER",
            "status": "READY",
            "offer_status": "PENDING_ACCEPTANCE",
            "created_at": generated_at or telemetry.now_iso(),
            "target_session_id": target_session_id,
            "target_client_instance_id": session.get("client_instance_id"),
            "work_item_id": work_item_id,
            "task_id": assignment.get("task_id"),
            "collision_domains": assignment.get("collision_domains") or [],
            "required_capabilities": assignment.get("required_capabilities") or [],
            "required_authorities": assignment.get("required_authorities") or [],
            "allowed_agent_roles": assignment.get("allowed_agent_roles") or [],
            "delivery_modes": _delivery_modes(session),
            "requires_offer_acceptance": True,
            "requires_claim_after_acceptance": True,
            "requires_exact_head_reconciliation": True,
            "may_write_before_acceptance": False,
            "claim_created": False,
            "grants_write_authority": False,
        }
        store.setdefault("items", []).append(item)
        changes.append(item)

    if changes:
        store["revision"] = int(store.get("revision", 0)) + 1
        write_json(DISPATCHES_PATH, store)
    return {"changed": len(changes), "items": changes, "plan": plan}


def accept_work_offer(dispatch_id: str, session_id: str) -> dict:
    store = read_json(DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    item = next((x for x in store.get("items", []) if x.get("dispatch_id") == dispatch_id), None)
    if not item:
        raise ValueError("work offer dispatch not found")
    if item.get("dispatch_kind") != "WORK_OFFER":
        raise ValueError("dispatch is not a work offer")
    if item.get("target_session_id") != session_id:
        raise ValueError("work offer target session mismatch")
    if item.get("status") not in {"READY", "ACCEPTED_PENDING_CLAIM"}:
        raise ValueError("work offer is not accept-ready")

    capacity = session_capacity_projection(session_id)
    if capacity.get("availability_state") not in DISPATCHABLE_STATES:
        raise ValueError(f"session no longer available: {capacity.get('availability_state')}")
    if not capacity.get("eligible_for_new_work"):
        raise ValueError("session no longer eligible for new work")

    item["status"] = "ACCEPTED_PENDING_CLAIM"
    item["offer_status"] = "ACCEPTED"
    item["accepted_at"] = telemetry.now_iso()
    item["accepted_by_session_id"] = session_id
    item["claim_created"] = False
    item["requires_claim_after_acceptance"] = True
    item["may_write_before_acceptance"] = False
    item["grants_write_authority"] = False
    store["revision"] = int(store.get("revision", 0)) + 1
    write_json(DISPATCHES_PATH, store)
    return {
        "status": "WORK_OFFER_ACCEPTED_PENDING_CLAIM",
        "dispatch": item,
        "next_required_action": "CREATE_CANONICAL_WORK_CLAIM_AND_RECONCILE_EXACT_HEAD",
    }


def command_pool(_: argparse.Namespace) -> None:
    print(json.dumps(agent_pool_projection(), indent=2, ensure_ascii=False))


def command_plan(_: argparse.Namespace) -> None:
    print(json.dumps(parallel_work_dispatch_plan(), indent=2, ensure_ascii=False))


def command_dispatch(_: argparse.Namespace) -> None:
    print(json.dumps({"status": "WORK_DISPATCH_COMPLETE", **dispatch_ready_work()}, indent=2, ensure_ascii=False))


def command_accept(args: argparse.Namespace) -> None:
    print(json.dumps(accept_work_offer(args.dispatch_id, args.session_id), indent=2, ensure_ascii=False))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="GACR capacity pool and parallel work dispatcher")
    sub = p.add_subparsers(dest="command", required=True)
    pool = sub.add_parser("pool")
    pool.set_defaults(fn=command_pool)
    plan = sub.add_parser("plan-work")
    plan.set_defaults(fn=command_plan)
    dispatch = sub.add_parser("dispatch-work")
    dispatch.set_defaults(fn=command_dispatch)
    accept = sub.add_parser("accept-work")
    accept.add_argument("--dispatch-id", required=True)
    accept.add_argument("--session-id", required=True)
    accept.set_defaults(fn=command_accept)
    return p


def main() -> None:
    args = parser().parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
