#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("GACR_ROOT") or Path(__file__).resolve().parents[1]).resolve()
GOV = ROOT / ".governance"
TEMPLATE_SOURCE = (ROOT / ".template-source").exists()

if TEMPLATE_SOURCE:
    SESSIONS_PATH = GOV / "control-plane-state" / "gacr-sessions.json"
    CLAIMS_PATH = GOV / "control-plane-state" / "gacr-claims.json"
    BEACONS_PATH = GOV / "control-plane-state" / "gacr-beacons.json"
    DISPATCHES_PATH = GOV / "control-plane-state" / "gacr-dispatches.json"
    ROSTER_PATH = GOV / "control-plane-state" / "gacr-agent-roster.json"
    TASKS_PATH = GOV / "control-plane-state" / "tasks.json"
else:
    SESSIONS_PATH = GOV / "sessions" / "sessions.json"
    CLAIMS_PATH = GOV / "work" / "claims.json"
    BEACONS_PATH = GOV / "agent-relay" / "beacons.json"
    DISPATCHES_PATH = GOV / "agent-relay" / "dispatches.json"
    ROSTER_PATH = GOV / "agent-relay" / "roster.json"
    TASKS_PATH = GOV / "work" / "work-items.json"

CODE_AGENT_ROLES = {"CODE_AGENT", "CODER", "CODE-AGENT", "IMPLEMENTER", "DEVELOPER"}
OPEN_CLAIM_STATES = {"ACTIVE", "CLAIMED", "IN_PROGRESS"}
OPEN_DISPATCH_STATES = {"PLANNED", "OFFERED", "DELIVERED", "ACKNOWLEDGED"}
TERMINAL_SESSION_STATES = {"CLOSED", "TERMINAL", "COMPLETED", "CANCELLED"}
STALLED_SESSION_STATES = {"STALLED", "TAKEOVER_READY", "HANDOFF_STALLED"}
LIMIT_WORKLOADS = {"RATE_LIMITED", "QUOTA_LIMITED", "CONTEXT_LIMITED"}
WAITING_WORKLOADS = {"WAITING_FOR_INPUT", "WAITING_FOR_AUTHORITY", "WAITING_FOR_REVIEW", "BLOCKED"}
AVAILABLE_WORKLOADS = {"IDLE", "WAITING_FOR_WORK"}
WORKING_WORKLOADS = {"WORKING", "CHECKPOINTING"}
LIMIT_INTERRUPTION_CODES = {
    "PROVIDER_RATE_LIMIT", "TOOL_RATE_LIMIT", "USAGE_LIMIT", "QUOTA_LIMIT", "CONTEXT_LIMIT"
}
WAIT_INTERRUPTION_CODES = {
    "WAITING_FOR_AUTHORITY", "WAITING_FOR_INPUT", "WAITING_FOR_REVIEW", "EXTERNAL_DEPENDENCY"
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def read_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return default or {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _items(store: dict[str, Any], *keys: str) -> list[dict[str, Any]]:
    for key in keys:
        value = store.get(key)
        if isinstance(value, list):
            return value
    return []


def _session_id(item: dict[str, Any]) -> str | None:
    value = item.get("session_id")
    return value if isinstance(value, str) and value else None


def latest_beacon_for_session(session_id: str, beacons: dict[str, Any]) -> dict[str, Any] | None:
    rows = [
        item for item in _items(beacons, "items")
        if item.get("session_id") == session_id
    ]
    if not rows:
        return None
    rows.sort(key=lambda x: (x.get("observed_at") or "", x.get("beacon_id") or ""))
    return rows[-1]


def latest_idle_challenge(session_id: str, dispatches: dict[str, Any]) -> dict[str, Any] | None:
    rows = []
    for item in _items(dispatches, "items"):
        if item.get("target_session_id") != session_id:
            continue
        response = item.get("response") or {}
        if response.get("challenge_status") != "IDLE":
            continue
        rows.append(item)
    if not rows:
        return None
    rows.sort(key=lambda x: (
        (x.get("response") or {}).get("observed_at") or x.get("completed_at") or x.get("created_at") or "",
        x.get("dispatch_id") or "",
    ))
    return rows[-1]


def active_claims_for_session(session_id: str, claims: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item for item in _items(claims, "claims")
        if item.get("session_id") == session_id
        and str(item.get("status") or "").upper() in OPEN_CLAIM_STATES
    ]


def active_claim_domains(claims: dict[str, Any]) -> set[str]:
    domains: set[str] = set()
    for item in _items(claims, "claims"):
        if str(item.get("status") or "").upper() not in OPEN_CLAIM_STATES:
            continue
        for domain in item.get("collision_domains") or []:
            if domain:
                domains.add(str(domain))
    return domains


def open_dispatch_task_ids(dispatches: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for item in _items(dispatches, "items"):
        if item.get("schema") != "gacr-work-dispatch/v1":
            continue
        if str(item.get("status") or "").upper() not in OPEN_DISPATCH_STATES:
            continue
        task_id = item.get("task_id")
        if task_id:
            ids.add(str(task_id))
    return ids


def _role_key(session: dict[str, Any], beacon: dict[str, Any] | None) -> str:
    role = (beacon or {}).get("agent_role") or session.get("agent_role") or "UNKNOWN"
    return str(role).strip().upper().replace(" ", "_")


def _is_code_agent(session: dict[str, Any], beacon: dict[str, Any] | None) -> bool:
    role = _role_key(session, beacon)
    capabilities = {
        str(x).strip().upper()
        for x in ((beacon or {}).get("capabilities") or session.get("capabilities") or [])
        if str(x).strip()
    }
    return role in CODE_AGENT_ROLES or "CODE_AGENT" in capabilities or "CODE_IMPLEMENTATION" in capabilities


def classify_agent(
    session: dict[str, Any],
    beacons: dict[str, Any],
    claims: dict[str, Any],
    dispatches: dict[str, Any],
) -> dict[str, Any]:
    session_id = _session_id(session)
    if not session_id:
        raise ValueError("session missing session_id")

    beacon = latest_beacon_for_session(session_id, beacons)
    active_claims = active_claims_for_session(session_id, claims)
    relay = session.get("relay") or {}
    session_status = str(session.get("status") or "UNKNOWN").upper()
    relay_state = str(relay.get("state") or "UNKNOWN").upper()
    workload_state = str((beacon or {}).get("workload_state") or "UNKNOWN").upper()
    interruption_code = str((beacon or {}).get("interruption_code") or "").upper()
    blocker_code = str((beacon or {}).get("blocker_code") or "").upper() or None
    explicit_idle = latest_idle_challenge(session_id, dispatches)

    max_parallel = (beacon or {}).get("max_parallel_tasks")
    if max_parallel is None:
        max_parallel = session.get("max_parallel_tasks")
    try:
        max_parallel = int(max_parallel) if max_parallel is not None else 1
    except (TypeError, ValueError):
        max_parallel = 1
    max_parallel = max(0, max_parallel)

    explicit_capacity = (beacon or {}).get("capacity_slots")
    if explicit_capacity is not None:
        try:
            free_slots = max(0, int(explicit_capacity))
        except (TypeError, ValueError):
            free_slots = 0
    else:
        free_slots = max(0, max_parallel - len(active_claims))

    code_agent = _is_code_agent(session, beacon)
    reasons: list[str] = []
    scheduler_state = "UNKNOWN"
    availability_provenance = "DERIVED_FROM_SESSION"

    if session_status in TERMINAL_SESSION_STATES or relay_state in TERMINAL_SESSION_STATES:
        scheduler_state = "TERMINAL"
        reasons.append("SESSION_TERMINAL")
    elif session_status == "STALLED" or relay_state in STALLED_SESSION_STATES:
        scheduler_state = "STALLED"
        reasons.append("SESSION_OR_RELAY_STALLED")
    elif workload_state in LIMIT_WORKLOADS or interruption_code in LIMIT_INTERRUPTION_CODES:
        scheduler_state = "LIMITED"
        reasons.append(workload_state if workload_state in LIMIT_WORKLOADS else interruption_code)
        availability_provenance = "EXPLICIT_BEACON"
    elif workload_state in WAITING_WORKLOADS or interruption_code in WAIT_INTERRUPTION_CODES:
        scheduler_state = "WAITING"
        reasons.append(blocker_code or workload_state or interruption_code)
        availability_provenance = "EXPLICIT_BEACON"
    elif workload_state in WORKING_WORKLOADS or active_claims:
        scheduler_state = "ACTIVE"
        reasons.append("EXPLICIT_WORKING" if workload_state in WORKING_WORKLOADS else "ACTIVE_CLAIM")
        availability_provenance = "EXPLICIT_BEACON" if workload_state in WORKING_WORKLOADS else "CANONICAL_CLAIM"
    elif workload_state in AVAILABLE_WORKLOADS:
        scheduler_state = "AVAILABLE"
        reasons.append(workload_state)
        availability_provenance = "EXPLICIT_BEACON"
    elif explicit_idle is not None:
        scheduler_state = "AVAILABLE"
        reasons.append("LIVENESS_CHALLENGE_IDLE")
        availability_provenance = "EXPLICIT_CHALLENGE_RESPONSE"
    elif session_status == "ACTIVE" and relay_state in {"ACTIVE", "STANDBY", "UNKNOWN"} and not active_claims:
        scheduler_state = "UNCONFIRMED_AVAILABLE"
        reasons.append("ALIVE_WITHOUT_ACTIVE_CLAIM_BUT_NO_EXPLICIT_IDLE")
    elif session_status in {"QUIET", "SUSPECTED_STALL"}:
        scheduler_state = "WAITING"
        reasons.append(session_status)
    else:
        reasons.append("NO_SAFE_AVAILABILITY_SIGNAL")

    eligible = bool(code_agent and scheduler_state == "AVAILABLE" and free_slots > 0)

    return {
        "session_id": session_id,
        "agent_identity": session.get("agent_identity"),
        "provider": session.get("provider"),
        "agent_role": (beacon or {}).get("agent_role") or session.get("agent_role"),
        "code_agent": code_agent,
        "session_status": session_status,
        "relay_state": relay_state,
        "workload_state": workload_state,
        "scheduler_state": scheduler_state,
        "eligible_for_new_work": eligible,
        "availability_provenance": availability_provenance,
        "reasons": reasons,
        "blocker_code": blocker_code,
        "interruption_code": interruption_code or None,
        "retry_after_at": (beacon or {}).get("retry_after_at"),
        "active_claim_count": len(active_claims),
        "active_claim_ids": [x.get("claim_id") for x in active_claims if x.get("claim_id")],
        "active_work_item_ids": [x.get("work_item_id") for x in active_claims if x.get("work_item_id")],
        "max_parallel_tasks": max_parallel,
        "free_capacity_slots": free_slots,
        "wake_channels": session.get("wake_channels") or ["POLL_REPOSITORY"],
        "bridge_registration_ref": session.get("bridge_registration_ref"),
        "last_seen_at": session.get("last_seen_at"),
        "last_heartbeat_at": relay.get("last_heartbeat_at"),
        "last_beacon_at": (beacon or {}).get("observed_at"),
        "last_beacon_id": (beacon or {}).get("beacon_id"),
    }


def build_roster(
    sessions: dict[str, Any],
    beacons: dict[str, Any],
    claims: dict[str, Any],
    dispatches: dict[str, Any],
) -> dict[str, Any]:
    agents = [
        classify_agent(session, beacons, claims, dispatches)
        for session in _items(sessions, "sessions")
        if session.get("session_id")
    ]
    agents.sort(key=lambda x: (x.get("scheduler_state") or "", x.get("session_id") or ""))
    summary: dict[str, int] = {}
    for agent in agents:
        key = str(agent.get("scheduler_state") or "UNKNOWN")
        summary[key] = summary.get(key, 0) + 1
    return {
        "schema": "gacr-agent-roster/v1",
        "generated_at": now_iso(),
        "projection_only": True,
        "authority_granted": False,
        "summary": summary,
        "code_agents_total": sum(1 for x in agents if x.get("code_agent")),
        "code_agents_available": sum(1 for x in agents if x.get("eligible_for_new_work")),
        "agents": agents,
    }


def persist_roster(roster: dict[str, Any]) -> dict[str, Any]:
    previous = read_json(ROSTER_PATH, {"schema_version": "1.0.0", "revision": 0, "agents": []})
    stable_previous = {
        "summary": previous.get("summary") or {},
        "code_agents_total": previous.get("code_agents_total", 0),
        "code_agents_available": previous.get("code_agents_available", 0),
        "agents": previous.get("agents") or [],
    }
    stable_new = {
        "summary": roster.get("summary") or {},
        "code_agents_total": roster.get("code_agents_total", 0),
        "code_agents_available": roster.get("code_agents_available", 0),
        "agents": roster.get("agents") or [],
    }
    revision = int(previous.get("revision") or 0)
    if stable_previous != stable_new:
        revision += 1
    persisted = {
        "schema_version": "1.0.0",
        "schema": "gacr-agent-roster/v1",
        "revision": revision,
        **roster,
    }
    write_json(ROSTER_PATH, persisted)
    return persisted


def _task_rows(task_store: dict[str, Any]) -> list[dict[str, Any]]:
    return _items(task_store, "items", "work_items")


def _task_id(task: dict[str, Any]) -> str:
    return str(task.get("id") or task.get("work_item_id") or "")


def _task_status(task: dict[str, Any]) -> str:
    return str(task.get("status") or "UNKNOWN").upper()


def _task_dependencies(task: dict[str, Any]) -> list[str]:
    raw = task.get("depends_on")
    if raw is None:
        raw = task.get("dependencies")
    deps: list[str] = []
    for value in raw or []:
        if isinstance(value, dict):
            candidate = value.get("id") or value.get("work_item_id")
        else:
            candidate = value
        if candidate:
            deps.append(str(candidate))
    return deps


def _dispatch_policy(task: dict[str, Any]) -> dict[str, Any]:
    value = task.get("dispatch_policy")
    return value if isinstance(value, dict) else {}


def _collision_domains(task: dict[str, Any]) -> list[str]:
    policy = _dispatch_policy(task)
    raw = policy.get("collision_domains")
    if not raw:
        raw = task.get("collision_domains")
    if not raw and task.get("collision_domain"):
        raw = [task.get("collision_domain")]
    if not raw:
        raw = [_task_id(task)]
    return sorted({str(x) for x in raw if x})


def _required_capabilities(task: dict[str, Any]) -> set[str]:
    policy = _dispatch_policy(task)
    return {
        str(x).strip().upper()
        for x in (policy.get("required_capabilities") or task.get("required_capabilities") or [])
        if str(x).strip()
    }


def _allowed_roles(task: dict[str, Any]) -> set[str]:
    policy = _dispatch_policy(task)
    roles = policy.get("allowed_agent_roles") or task.get("allowed_agent_roles") or ["CODE_AGENT"]
    return {str(x).strip().upper().replace(" ", "_") for x in roles if str(x).strip()}


def task_evaluation(
    task: dict[str, Any],
    tasks_by_id: dict[str, dict[str, Any]],
    active_domains: set[str],
    open_dispatch_ids: set[str],
    *,
    explicit_selection: bool,
) -> dict[str, Any]:
    task_id = _task_id(task)
    status = _task_status(task)
    policy = _dispatch_policy(task)
    reasons: list[str] = []
    enabled = bool(policy.get("enabled") is True)
    if not explicit_selection and not enabled:
        reasons.append("DISPATCH_POLICY_NOT_ENABLED")
    if status not in {"READY", "PLANNED", "IN_PROGRESS"}:
        reasons.append(f"STATUS_{status}_NOT_DISPATCHABLE")
    if task_id in open_dispatch_ids:
        reasons.append("OPEN_DISPATCH_EXISTS")

    dependencies = _task_dependencies(task)
    unresolved: list[str] = []
    for dep in dependencies:
        dep_task = tasks_by_id.get(dep)
        if dep_task is None:
            unresolved.append(dep)
            continue
        if _task_status(dep_task) not in {"DONE", "SUPERSEDED"}:
            unresolved.append(dep)
    if unresolved:
        reasons.append("UNRESOLVED_DEPENDENCIES")

    domains = _collision_domains(task)
    collisions = sorted(set(domains) & active_domains)
    if collisions:
        reasons.append("ACTIVE_COLLISION_DOMAIN")

    return {
        "task_id": task_id,
        "status": status,
        "dispatch_policy_enabled": enabled,
        "explicit_selection": explicit_selection,
        "dependencies": dependencies,
        "unresolved_dependencies": unresolved,
        "collision_domains": domains,
        "active_collisions": collisions,
        "required_capabilities": sorted(_required_capabilities(task)),
        "allowed_agent_roles": sorted(_allowed_roles(task)),
        "priority": int(policy.get("priority") or 100),
        "group_id": policy.get("group_id") or task.get("parent_or_program") or task.get("integration_slot"),
        "ready": not reasons,
        "reasons": reasons,
        "next_action": task.get("next_action"),
        "objective": task.get("objective"),
    }


def _agent_capabilities(agent: dict[str, Any], session: dict[str, Any]) -> set[str]:
    return {
        str(x).strip().upper()
        for x in (session.get("capabilities") or [])
        if str(x).strip()
    }


def plan_dispatch(
    *,
    sessions: dict[str, Any],
    beacons: dict[str, Any],
    claims: dict[str, Any],
    dispatches: dict[str, Any],
    task_store: dict[str, Any],
    explicit_task_ids: list[str] | None = None,
    auto: bool = False,
    max_assignments: int = 50,
) -> dict[str, Any]:
    roster = build_roster(sessions, beacons, claims, dispatches)
    sessions_by_id = {
        str(x.get("session_id")): x
        for x in _items(sessions, "sessions")
        if x.get("session_id")
    }
    agents = [x for x in roster["agents"] if x.get("eligible_for_new_work")]
    agents.sort(key=lambda x: (-int(x.get("free_capacity_slots") or 0), x.get("session_id") or ""))

    rows = _task_rows(task_store)
    tasks_by_id = {_task_id(x): x for x in rows if _task_id(x)}
    explicit_set = {str(x) for x in (explicit_task_ids or []) if str(x)}
    selected_rows: list[dict[str, Any]] = []
    if explicit_set:
        missing = sorted(explicit_set - set(tasks_by_id))
        if missing:
            raise ValueError(f"unknown task ids: {','.join(missing)}")
        selected_rows.extend(tasks_by_id[x] for x in sorted(explicit_set))
    if auto:
        for task in rows:
            if _task_id(task) in explicit_set:
                continue
            if _dispatch_policy(task).get("enabled") is True:
                selected_rows.append(task)

    active_domains = active_claim_domains(claims)
    open_ids = open_dispatch_task_ids(dispatches)
    evaluations = [
        task_evaluation(
            task,
            tasks_by_id,
            active_domains,
            open_ids,
            explicit_selection=_task_id(task) in explicit_set,
        )
        for task in selected_rows
    ]
    evaluations.sort(key=lambda x: (int(x.get("priority") or 100), x.get("task_id") or ""))

    agent_capacity = {
        str(x["session_id"]): int(x.get("free_capacity_slots") or 0)
        for x in agents
    }
    planned_domains = set(active_domains)
    assignments: list[dict[str, Any]] = []

    for task_eval in evaluations:
        if len(assignments) >= max_assignments:
            break
        if not task_eval.get("ready"):
            continue
        task_domains = set(task_eval.get("collision_domains") or [])
        if task_domains & planned_domains:
            task_eval["ready"] = False
            task_eval["reasons"] = list(task_eval.get("reasons") or []) + ["PLANNED_COLLISION_DOMAIN"]
            continue

        chosen = None
        for agent in agents:
            session_id = str(agent["session_id"])
            if agent_capacity.get(session_id, 0) <= 0:
                continue
            session = sessions_by_id.get(session_id) or {}
            role = _role_key(session, latest_beacon_for_session(session_id, beacons))
            allowed_roles = set(task_eval.get("allowed_agent_roles") or ["CODE_AGENT"])
            role_allowed = role in allowed_roles or (
                "CODE_AGENT" in allowed_roles and bool(agent.get("code_agent"))
            )
            if not role_allowed:
                continue
            required = set(task_eval.get("required_capabilities") or [])
            if not required.issubset(_agent_capabilities(agent, session)):
                continue
            chosen = agent
            break

        if chosen is None:
            task_eval["ready"] = False
            task_eval["reasons"] = list(task_eval.get("reasons") or []) + ["NO_ELIGIBLE_CODE_AGENT"]
            continue

        session_id = str(chosen["session_id"])
        agent_capacity[session_id] -= 1
        planned_domains.update(task_domains)
        assignments.append({
            "task_id": task_eval["task_id"],
            "target_session_id": session_id,
            "agent_identity": chosen.get("agent_identity"),
            "agent_role": chosen.get("agent_role"),
            "group_id": task_eval.get("group_id"),
            "collision_domains": task_eval.get("collision_domains") or [],
            "required_capabilities": task_eval.get("required_capabilities") or [],
            "next_action": task_eval.get("next_action"),
            "objective": task_eval.get("objective"),
            "selection_reason": "ELIGIBLE_CODE_AGENT_AVAILABLE_AND_COLLISION_FREE",
            "claim_required_before_execution": True,
            "grants_mutation_authority": False,
        })

    return {
        "schema": "gacr-parallel-dispatch-plan/v1",
        "generated_at": now_iso(),
        "auto_mode": auto,
        "explicit_task_ids": sorted(explicit_set),
        "assignments": assignments,
        "task_evaluations": evaluations,
        "roster": roster,
        "authority_granted": False,
    }


def persist_dispatch_plan(plan: dict[str, Any], dispatches: dict[str, Any], sessions: dict[str, Any]) -> dict[str, Any]:
    store = dispatches
    store.setdefault("schema_version", "1.0.0")
    store.setdefault("revision", 0)
    store.setdefault("items", [])
    existing = {
        (x.get("task_id"), x.get("target_session_id"))
        for x in store["items"]
        if x.get("schema") == "gacr-work-dispatch/v1"
        and str(x.get("status") or "").upper() in OPEN_DISPATCH_STATES
    }
    sessions_by_id = {
        str(x.get("session_id")): x
        for x in _items(sessions, "sessions")
        if x.get("session_id")
    }
    created: list[dict[str, Any]] = []
    for assignment in plan.get("assignments") or []:
        key = (assignment.get("task_id"), assignment.get("target_session_id"))
        if key in existing:
            continue
        session = sessions_by_id.get(str(assignment.get("target_session_id"))) or {}
        delivery_modes = ["POLL_REPOSITORY"]
        wake = set(session.get("wake_channels") or [])
        if "REPOSITORY_DISPATCH" in wake:
            delivery_modes.append("REPOSITORY_DISPATCH")
        if "EXTERNAL_BRIDGE" in wake and session.get("bridge_registration_ref"):
            delivery_modes.append("EXTERNAL_BRIDGE")
        seed = {
            "task_id": assignment.get("task_id"),
            "target_session_id": assignment.get("target_session_id"),
            "collision_domains": assignment.get("collision_domains"),
        }
        item = {
            "schema": "gacr-work-dispatch/v1",
            "dispatch_id": "GACR-WORK-" + digest(seed)[:24],
            "kind": "WORK_ASSIGNMENT_OFFER",
            "status": "OFFERED",
            **assignment,
            "delivery_modes": delivery_modes,
            "bridge_registration_ref": session.get("bridge_registration_ref"),
            "created_at": now_iso(),
            "requires_claim_before_execution": True,
            "requires_exact_head_reobservation_before_mutation": True,
            "invocation_authority_granted": False,
            "mutation_authority_granted": False,
            "projection_only_until_claim": True,
        }
        store["items"].append(item)
        existing.add(key)
        created.append(item)
    if created:
        store["revision"] = int(store.get("revision") or 0) + 1
        write_json(DISPATCHES_PATH, store)
    return {
        "created_count": len(created),
        "created": created,
        "dispatch_store_revision": store.get("revision", 0),
    }


def load_all() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    beacons = read_json(BEACONS_PATH, {"items": []})
    claims = read_json(CLAIMS_PATH, {"claims": []})
    dispatches = read_json(DISPATCHES_PATH, {"items": []})
    if TEMPLATE_SOURCE:
        task_store = read_json(TASKS_PATH, {"items": []})
    else:
        task_store = read_json(TASKS_PATH, {"work_items": []})
    return sessions, beacons, claims, dispatches, task_store


def cmd_roster(args: argparse.Namespace) -> None:
    sessions, beacons, claims, dispatches, _ = load_all()
    roster = build_roster(sessions, beacons, claims, dispatches)
    if args.persist:
        roster = persist_roster(roster)
    print(json.dumps(roster, indent=2, ensure_ascii=False))


def cmd_plan(args: argparse.Namespace) -> None:
    sessions, beacons, claims, dispatches, task_store = load_all()
    plan = plan_dispatch(
        sessions=sessions,
        beacons=beacons,
        claims=claims,
        dispatches=dispatches,
        task_store=task_store,
        explicit_task_ids=args.task_id,
        auto=args.auto,
        max_assignments=args.max_assignments,
    )
    if args.persist_roster:
        plan["persisted_roster"] = persist_roster(plan["roster"])
    print(json.dumps(plan, indent=2, ensure_ascii=False))


def cmd_dispatch(args: argparse.Namespace) -> None:
    if not args.auto and not args.task_id:
        raise SystemExit("GACR_PARALLEL_DISPATCH_FAILED: dispatch requires --auto or --task-id")
    sessions, beacons, claims, dispatches, task_store = load_all()
    plan = plan_dispatch(
        sessions=sessions,
        beacons=beacons,
        claims=claims,
        dispatches=dispatches,
        task_store=task_store,
        explicit_task_ids=args.task_id,
        auto=args.auto,
        max_assignments=args.max_assignments,
    )
    roster = persist_roster(plan["roster"]) if args.persist_roster else plan["roster"]
    persisted = persist_dispatch_plan(plan, dispatches, sessions)
    print(json.dumps({
        "status": "PARALLEL_DISPATCH_COMPLETE",
        "plan": {k: v for k, v in plan.items() if k != "roster"},
        "roster": roster,
        "persistence": persisted,
    }, indent=2, ensure_ascii=False))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="GACR availability roster and dependency/collision-safe parallel work dispatcher"
    )
    sub = p.add_subparsers(dest="command", required=True)

    roster = sub.add_parser("roster")
    roster.add_argument("--persist", action="store_true")
    roster.set_defaults(fn=cmd_roster)

    for name, fn in (("plan", cmd_plan), ("dispatch", cmd_dispatch)):
        q = sub.add_parser(name)
        q.add_argument("--auto", action="store_true")
        q.add_argument("--task-id", action="append")
        q.add_argument("--max-assignments", type=int, default=50)
        q.add_argument("--persist-roster", action="store_true")
        q.set_defaults(fn=fn)
    return p


def main() -> None:
    args = parser().parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
