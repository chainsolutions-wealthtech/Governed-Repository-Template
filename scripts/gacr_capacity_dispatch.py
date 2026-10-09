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
CONTROL_TASKS_PATH = GOV / "control-plane-state" / "tasks.json"
GMC_BLUEPRINT_PATH = GOV / "control-plane-state" / "governance-model-execution-blueprint.json"
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
CANONICAL_AGENT_ROLES = {"INTAKER", "SUPERVISOR", "CODE_AGENT", "REVIEWER"}
SOURCE_WORK_KIND = "CONTROL_PLANE_CANONICAL_TASK_GRAPH"


def read_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return default or {}
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return default or {}
    return json.loads(text)


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
        "require_f1_release_for_source_work": bool(dispatch.get("require_f1_release_for_source_work", True)),
        "require_canonical_role_for_source_work": bool(dispatch.get("require_canonical_role_for_source_work", True)),
        "canonical_source_work_queue": bool(dispatch.get("canonical_source_work_queue", True)),
    }


def _logical_agent_id(session: dict) -> str | None:
    value = session.get("logical_agent_id") or session.get("agent_identity")
    value = str(value or "").strip()
    return value or None


def _capacity_key(item: dict) -> str:
    logical_agent_id = str(item.get("logical_agent_id") or "").strip()
    if logical_agent_id:
        return "logical-agent:" + logical_agent_id
    return "session:" + str(item.get("session_id") or "UNAVAILABLE")


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


def _latest_f1_release(items: list[dict]) -> dict | None:
    for item in reversed(items):
        if item.get("event_type") == "F1_RELEASED" and item.get("evidence_ref"):
            return {
                "beacon_id": item.get("beacon_id"),
                "observed_at": item.get("observed_at"),
                "evidence_ref": item.get("evidence_ref"),
                "checkpoint_ref": item.get("checkpoint_ref"),
            }
    return None


def _latest_declared_work_profile(items: list[dict]) -> dict:
    role = purpose = work_kind = None
    role_ref = purpose_ref = work_ref = None
    for item in reversed(items):
        if role is None and item.get("agent_role_provenance") == "DECLARED_BY_EVENT":
            value = item.get("agent_role")
            if value in CANONICAL_AGENT_ROLES:
                role, role_ref = value, item.get("beacon_id")
        if purpose is None and item.get("entry_purpose_provenance") == "DECLARED_BY_EVENT":
            purpose, purpose_ref = item.get("entry_purpose"), item.get("beacon_id")
        if work_kind is None and item.get("work_kind_provenance") == "DECLARED_BY_EVENT":
            work_kind, work_ref = item.get("work_kind"), item.get("beacon_id")
        if role is not None and purpose is not None and work_kind is not None:
            break
    return {
        "agent_role": role,
        "entry_purpose": purpose,
        "work_kind": work_kind,
        "role_evidence_ref": role_ref,
        "purpose_evidence_ref": purpose_ref,
        "work_kind_evidence_ref": work_ref,
    }


def _latest_declared_capabilities(items: list[dict]) -> list[str]:
    for item in reversed(items):
        if item.get("capabilities_provenance") == "DECLARED_BY_EVENT":
            return sorted(set(item.get("capabilities") or []))
    return []


def _interruption_is_current(interruption: dict | None, availability: dict | None) -> bool:
    if not interruption:
        return False
    if not availability:
        return True
    return str(interruption.get("observed_at") or "") >= str(availability.get("observed_at") or "")


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
    interruption_current = interruption if _interruption_is_current(interruption, explicit) else None
    f1_release = _latest_f1_release(related)
    declaration = _latest_declared_work_profile(related)
    declared_capabilities = _latest_declared_capabilities(related)
    active_claims = _active_claims(claims_doc, session_id)
    relay = session.get("relay") or {}
    liveness = (signal.get("liveness") or {}).get("state") or "UNKNOWN"
    progress = (signal.get("progress") or {}).get("state") or "UNKNOWN"

    state = "UNKNOWN"
    reason = "NO_EXPLICIT_CAPACITY_SIGNAL"

    if session.get("status") == "CLOSED" or relay.get("state") in TERMINAL_RELAY_STATES or liveness == "TERMINAL":
        state = "TERMINAL"
        reason = "SESSION_TERMINAL"
    elif interruption_current and interruption_current.get("code") in EXPLICIT_BLOCK_INTERRUPTION_MAP:
        state = EXPLICIT_BLOCK_INTERRUPTION_MAP[interruption_current["code"]]
        reason = interruption_current["code"]
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

    blockers=[]
    if TEMPLATE_SOURCE and cfg["require_f1_release_for_source_work"] and not f1_release:
        blockers.append("F1_RELEASE_NOT_VERIFIED")
    if TEMPLATE_SOURCE and cfg["require_canonical_role_for_source_work"] and not declaration.get("agent_role"):
        blockers.append("CANONICAL_AGENT_ROLE_NOT_DECLARED")

    eligible = (
        state in set(cfg["available_states"])
        and live_enough
        and not active_claims
        and not actions.get("in_flight_action")
        and (explicit_available or standby_available or not explicit_required)
        and not blockers
    )

    effective_capabilities = sorted(set(session.get("capabilities") or []) | set(declared_capabilities))
    effective_role = declaration.get("agent_role") or session.get("agent_role")
    logical_agent_id = _logical_agent_id(session)
    value = {
        "session_id": session_id,
        "logical_agent_id": logical_agent_id,
        "logical_agent_id_provenance": (
            "CANONICAL_GACR_AGENT_IDENTITY"
            if logical_agent_id else "UNAVAILABLE"
        ),
        "generated_at": generated_at or telemetry.now_iso(),
        "repository": session.get("repository"),
        "provider": session.get("provider"),
        "client_instance_id": session.get("client_instance_id"),
        "agent_role": effective_role,
        "declared_work_profile": declaration,
        "capabilities": effective_capabilities,
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
        "effective_interruption": interruption_current,
        "f1_release_verified": bool(f1_release),
        "f1_release_evidence": f1_release,
        "dispatch_blockers": blockers,
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
    logical_groups: dict[str, dict] = {}
    cfg = config()
    for item in items:
        state = item.get("availability_state") or "UNKNOWN"
        counts[state] = counts.get(state, 0) + 1
        key = _capacity_key(item)
        group = logical_groups.setdefault(key, {
            "capacity_key": key,
            "logical_agent_id": item.get("logical_agent_id"),
            "logical_agent_id_provenance": item.get("logical_agent_id_provenance"),
            "session_ids": [],
            "eligible_session_ids": [],
            "active_claim_count": 0,
            "in_flight_session_ids": [],
            "automatic_offer_capacity_limit": cfg["max_parallel_offers_per_session"],
            "provider_private_limit_inference": False,
        })
        group["session_ids"].append(item.get("session_id"))
        if item.get("eligible_for_new_work"):
            group["eligible_session_ids"].append(item.get("session_id"))
        group["active_claim_count"] += int(item.get("active_claim_count") or 0)
        if item.get("in_flight_action"):
            group["in_flight_session_ids"].append(item.get("session_id"))

    logical_agents = []
    for key in sorted(logical_groups):
        group = logical_groups[key]
        group["session_ids"] = sorted(x for x in group["session_ids"] if x)
        group["eligible_session_ids"] = sorted(x for x in group["eligible_session_ids"] if x)
        group["in_flight_session_ids"] = sorted(x for x in group["in_flight_session_ids"] if x)
        group["session_count"] = len(group["session_ids"])
        occupied = len(set(group["in_flight_session_ids"])) + int(group["active_claim_count"])
        group["automatic_offer_capacity_remaining"] = max(
            0, int(group["automatic_offer_capacity_limit"]) - occupied
        )
        group["sessions_are_independent_capacity_units"] = not bool(
            group.get("logical_agent_id") and group["session_count"] > 1
        )
        logical_agents.append(group)

    return {
        "process": "GACR",
        "model": "AGENT_CAPACITY_POOL",
        "generated_at": generated_at or telemetry.now_iso(),
        "counts": counts,
        "eligible_session_ids": [x["session_id"] for x in items if x.get("eligible_for_new_work")],
        "eligible_capacity_keys": sorted({
            _capacity_key(x) for x in items if x.get("eligible_for_new_work")
        }),
        "logical_agents": logical_agents,
        "items": items,
        "provider_private_limit_inference": False,
        "source_f1_release_required": TEMPLATE_SOURCE and config()["require_f1_release_for_source_work"],
    }


def _source_control_plane_work_document() -> dict:
    tasks=read_json(CONTROL_TASKS_PATH, {"items":[]})
    active=[x for x in tasks.get("items",[]) if x.get("status")=="IN_PROGRESS"]
    if len(active)!=1:
        return {
            "schema_version":"1.0.0",
            "source":SOURCE_WORK_KIND,
            "source_status":"AMBIGUOUS_ACTIVE_GLOBAL_TASK",
            "items":[],
            "active_task_ids":[x.get("id") for x in active],
        }

    global_task=active[0]
    if global_task.get("id")!="GMC-01":
        return {
            "schema_version":"1.0.0",
            "source":SOURCE_WORK_KIND,
            "source_status":"ACTIVE_GLOBAL_TASK_NOT_YET_PROJECTABLE",
            "items":[],
            "global_task_id":global_task.get("id"),
        }

    blueprint=read_json(GMC_BLUEPRINT_PATH, {})
    release=blueprint.get("release_state") or {}
    package_id=release.get("released_work_package")
    if release.get("status")!="GMC_A_RELEASED" or package_id!="GMC-G01":
        return {
            "schema_version":"1.0.0",
            "source":SOURCE_WORK_KIND,
            "source_status":"GMC_WORK_PACKAGE_NOT_RELEASED",
            "items":[],
            "global_task_id":"GMC-01",
        }

    group=next((x for x in blueprint.get("groups",[]) if x.get("group_id")==package_id),None)
    if not group:
        return {
            "schema_version":"1.0.0",
            "source":SOURCE_WORK_KIND,
            "source_status":"RELEASED_GMC_WORK_PACKAGE_MISSING",
            "items":[],
            "global_task_id":"GMC-01",
            "work_package_id":package_id,
        }

    raw_tasks=group.get("atomic_tasks") or []
    done={x.get("task_id") for x in raw_tasks if x.get("status") in DONE_WORK_STATUSES}
    items=[]
    for sequence, raw in enumerate(raw_tasks, start=1):
        task_id=raw.get("task_id")
        dependencies=list(raw.get("depends_on") or [])
        if raw.get("status") in DONE_WORK_STATUSES:
            status="DONE"
        elif all(dep in done for dep in dependencies):
            status="READY"
        else:
            status="BLOCKED"
        items.append({
            "work_item_id":task_id,
            "task_id":task_id,
            "title":raw.get("title") or raw.get("action"),
            "status":status,
            "priority":1000-sequence,
            "sequence":sequence,
            "dependencies":dependencies,
            "collision_domains":[f"governance-model:{package_id}"],
            "required_capabilities":list(raw.get("required_capabilities") or []),
            "required_authorities":list(raw.get("required_authorities") or []),
            "allowed_agent_roles":list(raw.get("allowed_agent_roles") or ["CODE_AGENT"]),
            "repository":telemetry.repository_name(),
            "global_task_id":"GMC-01",
            "work_package_id":package_id,
            "planning_only":bool(group.get("planning_only",True)),
            "implementation_authorized":bool(group.get("implementation_authorized",False)),
            "hold_if":raw.get("hold_if"),
            "done_when":raw.get("done_when"),
            "evidence_required":raw.get("evidence_required") or [],
            "work_source":SOURCE_WORK_KIND,
        })

    return {
        "schema_version":"1.0.0",
        "source":SOURCE_WORK_KIND,
        "source_status":"READY",
        "global_task_id":"GMC-01",
        "work_package_id":package_id,
        "planning_only":bool(group.get("planning_only",True)),
        "implementation_authorized":bool(group.get("implementation_authorized",False)),
        "items":items,
    }


def canonical_work_document() -> dict:
    cfg=config()
    if TEMPLATE_SOURCE and cfg["canonical_source_work_queue"]:
        return _source_control_plane_work_document()
    doc=read_json(WORK_ITEMS_PATH, {"items":[]})
    return {
        **doc,
        "source":"REPOSITORY_LOCAL_WORK_ITEMS",
        "source_status":"READY",
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


def _candidate_compatible(candidate: dict, item: dict) -> tuple[bool, list[str]]:
    reasons = []
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


PENDING_WORK_OFFER_STATUSES = {"READY", "ACCEPTED_PENDING_CLAIM"}


def _pending_offer_capacity_counts(dispatches_doc: dict, pool_items: list[dict]) -> dict[str, int]:
    session_capacity_key = {
        item.get("session_id"): _capacity_key(item)
        for item in pool_items
        if item.get("session_id")
    }
    counts: dict[str, int] = {}
    for item in dispatches_doc.get("items", []):
        if item.get("dispatch_kind") != "WORK_OFFER":
            continue
        if item.get("status") not in PENDING_WORK_OFFER_STATUSES:
            continue
        capacity_key = item.get("capacity_key")
        if not capacity_key:
            logical_agent_id = str(item.get("target_logical_agent_id") or "").strip()
            if logical_agent_id:
                capacity_key = "logical-agent:" + logical_agent_id
            else:
                capacity_key = session_capacity_key.get(item.get("target_session_id"))
        if not capacity_key:
            continue
        counts[str(capacity_key)] = counts.get(str(capacity_key), 0) + 1
    return counts


def parallel_work_dispatch_plan(
    *,
    generated_at: str | None = None,
    work_doc: dict | None = None,
    claims_doc: dict | None = None,
    pool: dict | None = None,
    dispatches_doc: dict | None = None,
) -> dict:
    work_doc = work_doc or canonical_work_document()
    claims_doc = claims_doc or read_json(CLAIMS_PATH, {"claims": []})
    pool = pool or agent_pool_projection(generated_at=generated_at)
    dispatches_doc = dispatches_doc or {"items": []}
    by_id = {item.get("work_item_id"): item for item in work_doc.get("items", []) if item.get("work_item_id")}
    ready = [item for item in work_doc.get("items", []) if item.get("status") == "READY"]
    ready.sort(key=lambda item: (-int(item.get("priority") or 0), int(item.get("sequence") or 0), str(item.get("work_item_id") or "")))

    active_claims = _active_claims(claims_doc)
    pending_offers = [
        item for item in dispatches_doc.get("items", [])
        if item.get("dispatch_kind") == "WORK_OFFER"
        and item.get("status") in PENDING_WORK_OFFER_STATUSES
    ]
    claimed_work = {item.get("work_item_id") for item in active_claims}
    offered_work = {
        item.get("work_item_id")
        for item in pending_offers
        if item.get("work_item_id")
    }
    occupied_domains = _active_collision_domains(claims_doc)
    planned_domains: set[str] = set()
    cfg = config()
    planned_per_session: dict[str, int] = {}
    planned_per_capacity: dict[str, int] = {}
    pool_items = pool.get("items", [])
    pending_offer_capacity_counts = _pending_offer_capacity_counts(dispatches_doc, pool_items)
    session_capacity_key = {
        item.get("session_id"): _capacity_key(item)
        for item in pool_items
        if item.get("session_id")
    }
    occupied_sessions_per_capacity: dict[str, set[str]] = {}
    for claim in active_claims:
        claim_session_id = claim.get("session_id")
        capacity_key = session_capacity_key.get(claim_session_id)
        if capacity_key and claim_session_id:
            occupied_sessions_per_capacity.setdefault(capacity_key, set()).add(claim_session_id)
    for pool_item in pool_items:
        if pool_item.get("in_flight_action") and pool_item.get("session_id"):
            capacity_key = _capacity_key(pool_item)
            occupied_sessions_per_capacity.setdefault(capacity_key, set()).add(pool_item["session_id"])
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
        if work_item_id in offered_work:
            unassigned.append({"work_item_id": work_item_id, "reason": "OFFER_ALREADY_PENDING"})
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
            capacity_key = _capacity_key(candidate)
            occupied_logical_slots = (
                len(occupied_sessions_per_capacity.get(capacity_key, set()))
                + pending_offer_capacity_counts.get(capacity_key, 0)
            )
            if (
                occupied_logical_slots + planned_per_capacity.get(capacity_key, 0)
                >= cfg["max_parallel_offers_per_session"]
            ):
                reason = (
                    "LOGICAL_AGENT_OFFER_CAPACITY_REACHED"
                    if candidate.get("logical_agent_id")
                    else "SESSION_OFFER_CAPACITY_REACHED"
                )
                evaluations.append({
                    "session_id": session_id,
                    "logical_agent_id": candidate.get("logical_agent_id"),
                    "status": "INELIGIBLE",
                    "reasons": [reason],
                })
                continue
            if planned_per_session.get(session_id, 0) >= cfg["max_parallel_offers_per_session"]:
                evaluations.append({
                    "session_id": session_id,
                    "logical_agent_id": candidate.get("logical_agent_id"),
                    "status": "INELIGIBLE",
                    "reasons": ["SESSION_OFFER_CAPACITY_REACHED"],
                })
                continue
            compatible, reasons = _candidate_compatible(candidate, item)
            evaluations.append({
                "session_id": session_id,
                "logical_agent_id": candidate.get("logical_agent_id"),
                "status": "ELIGIBLE" if compatible else "INELIGIBLE",
                "reasons": reasons,
            })
            if compatible:
                eligible.append(candidate)

        if not eligible:
            unassigned.append({"work_item_id": work_item_id, "reason": "NO_COMPATIBLE_AVAILABLE_AGENT", "evaluations": evaluations})
            continue

        eligible.sort(key=lambda candidate: (
            planned_per_capacity.get(_capacity_key(candidate), 0),
            planned_per_session.get(candidate.get("session_id"), 0),
            str(candidate.get("session_id") or ""),
        ))
        selected = eligible[0]
        session_id = selected["session_id"]
        capacity_key = _capacity_key(selected)
        planned_per_session[session_id] = planned_per_session.get(session_id, 0) + 1
        planned_per_capacity[capacity_key] = planned_per_capacity.get(capacity_key, 0) + 1
        planned_domains.update(domains)

        assignments.append({
            "work_item_id": work_item_id,
            "task_id": item.get("task_id") or work_item_id,
            "title": item.get("title"),
            "target_session_id": session_id,
            "target_logical_agent_id": selected.get("logical_agent_id"),
            "capacity_key": capacity_key,
            "target_client_instance_id": selected.get("client_instance_id"),
            "collision_domains": sorted(domains),
            "required_capabilities": sorted(set(item.get("required_capabilities") or [])),
            "required_authorities": sorted(set(item.get("required_authorities") or [])),
            "allowed_agent_roles": sorted(set(item.get("allowed_agent_roles") or [])),
            "global_task_id":item.get("global_task_id"),
            "work_package_id":item.get("work_package_id"),
            "planning_only":item.get("planning_only"),
            "implementation_authorized":item.get("implementation_authorized"),
            "work_source":item.get("work_source") or work_doc.get("source"),
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
        "work_source":work_doc.get("source"),
        "work_source_status":work_doc.get("source_status"),
        "global_task_id":work_doc.get("global_task_id"),
        "work_package_id":work_doc.get("work_package_id"),
        "assignments": assignments,
        "unassigned": unassigned,
        "parallel_assignment_count": len(assignments),
        "occupied_collision_domains": sorted(occupied_domains),
        "planned_collision_domains": sorted(planned_domains),
        "pending_offer_capacity_counts": dict(sorted(pending_offer_capacity_counts.items())),
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


def _cancel_unavailable_target_offers(store: dict, pool: dict, timestamp: str) -> list[dict]:
    availability = {
        item.get("session_id"): bool(item.get("eligible_for_new_work"))
        for item in pool.get("items", [])
        if item.get("session_id")
    }
    cancelled = []
    for item in store.get("items", []):
        if item.get("dispatch_kind") != "WORK_OFFER":
            continue
        if item.get("status") not in PENDING_WORK_OFFER_STATUSES:
            continue
        target_session_id = item.get("target_session_id")
        if target_session_id and availability.get(target_session_id) is True:
            continue
        item["status"] = "CANCELLED"
        item["offer_status"] = "CANCELLED"
        item["cancelled_at"] = timestamp
        item["cancellation_reason"] = "TARGET_SESSION_UNAVAILABLE"
        item["claim_created"] = False
        item["grants_write_authority"] = False
        cancelled.append(item)
    return cancelled


def _cancel_stale_source_offers(store:dict, canonical_doc:dict, timestamp:str)->list[dict]:
    if not TEMPLATE_SOURCE:
        return []
    valid={x.get("work_item_id") for x in canonical_doc.get("items",[]) if x.get("status")=="READY"}
    cancelled=[]
    for item in store.get("items",[]):
        if item.get("dispatch_kind")!="WORK_OFFER":
            continue
        if item.get("status") not in {"READY","ACCEPTED_PENDING_CLAIM"}:
            continue
        if item.get("work_source")!=SOURCE_WORK_KIND or item.get("work_item_id") not in valid:
            item["status"]="CANCELLED"
            item["offer_status"]="CANCELLED"
            item["cancelled_at"]=timestamp
            item["cancellation_reason"]="SOURCE_CONTROL_PLANE_CANONICAL_TASK_SOURCE_REQUIRED"
            item["claim_created"]=False
            item["grants_write_authority"]=False
            cancelled.append(item)
    return cancelled


def dispatch_ready_work(*, generated_at: str | None = None) -> dict:
    timestamp=generated_at or telemetry.now_iso()
    canonical_doc=canonical_work_document()
    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    store = read_json(DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    pool = agent_pool_projection(generated_at=timestamp)
    source_cancelled=_cancel_stale_source_offers(store,canonical_doc,timestamp)
    target_cancelled=_cancel_unavailable_target_offers(store,pool,timestamp)
    cancelled = source_cancelled + [
        item for item in target_cancelled if item not in source_cancelled
    ]
    changes=list(cancelled)
    plan = parallel_work_dispatch_plan(
        generated_at=timestamp,
        work_doc=canonical_doc,
        pool=pool,
        dispatches_doc=store,
    )

    for assignment in plan.get("assignments",[]):
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
            "generated_at": timestamp,
        })
        item = {
            "dispatch_id": dispatch_id,
            "dispatch_kind": "WORK_OFFER",
            "status": "READY",
            "offer_status": "PENDING_ACCEPTANCE",
            "created_at": timestamp,
            "target_session_id": target_session_id,
            "target_logical_agent_id": assignment.get("target_logical_agent_id"),
            "capacity_key": assignment.get("capacity_key"),
            "target_client_instance_id": session.get("client_instance_id"),
            "work_item_id": work_item_id,
            "task_id": assignment.get("task_id"),
            "global_task_id":assignment.get("global_task_id"),
            "work_package_id":assignment.get("work_package_id"),
            "planning_only":assignment.get("planning_only"),
            "implementation_authorized":assignment.get("implementation_authorized"),
            "work_source":assignment.get("work_source"),
            "collision_domains": assignment.get("collision_domains") or [],
            "required_capabilities": assignment.get("required_capabilities") or [],
            "required_authorities": assignment.get("required_authorities") or [],
            "allowed_agent_roles": assignment.get("allowed_agent_roles") or [],
            "delivery_modes": _delivery_modes(session),
            "requires_f1_release":TEMPLATE_SOURCE,
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
    return {
        "changed":len(changes),
        "items":changes,
        "cancelled_count":len(cancelled),
        "created_offer_count":len(changes)-len(cancelled),
        "plan":plan,
    }


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

    pool = agent_pool_projection()
    target_pool_item = next(
        (entry for entry in pool.get("items", []) if entry.get("session_id") == session_id),
        None,
    )
    if not target_pool_item:
        raise ValueError("target session missing from canonical capacity pool")
    target_capacity_key = _capacity_key(target_pool_item)
    sibling_session_ids = {
        entry.get("session_id")
        for entry in pool.get("items", [])
        if entry.get("session_id")
        and _capacity_key(entry) == target_capacity_key
    }

    active_sibling_claims = [
        claim for claim in _active_claims(read_json(CLAIMS_PATH, {"claims": []}))
        if claim.get("session_id") in sibling_session_ids
    ]
    if active_sibling_claims:
        raise ValueError("logical agent capacity already occupied by active canonical claim")

    sibling_in_flight = [
        entry.get("session_id")
        for entry in pool.get("items", [])
        if entry.get("session_id") in sibling_session_ids
        and entry.get("session_id") != session_id
        and entry.get("in_flight_action")
    ]
    if sibling_in_flight:
        raise ValueError("logical agent capacity already occupied by sibling in-flight action")

    other_pending_offers = [
        offer for offer in store.get("items", [])
        if offer.get("dispatch_kind") == "WORK_OFFER"
        and offer.get("status") in PENDING_WORK_OFFER_STATUSES
        and offer.get("dispatch_id") != dispatch_id
        and offer.get("target_session_id") in sibling_session_ids
    ]
    if other_pending_offers:
        raise ValueError("logical agent capacity already occupied by another pending work offer")

    if TEMPLATE_SOURCE:
        current=canonical_work_document()
        work=next((x for x in current.get("items",[]) if x.get("work_item_id")==item.get("work_item_id")),None)
        if not work or work.get("status")!="READY":
            raise ValueError("canonical source work item no longer READY")
        if item.get("work_source")!=SOURCE_WORK_KIND:
            raise ValueError("source work offer does not originate from canonical task graph")

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
    dispatches = read_json(DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    print(json.dumps(
        parallel_work_dispatch_plan(dispatches_doc=dispatches),
        indent=2,
        ensure_ascii=False,
    ))


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
