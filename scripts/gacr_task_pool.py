#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import gacr_agent_telemetry as telemetry
import gacr_capacity_dispatch as capacity

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / ".governance"
TEMPLATE_SOURCE = (ROOT / ".template-source").exists()

POOL_PATH = (
    GOV / "control-plane-state" / "gacr-task-pool.json"
    if TEMPLATE_SOURCE
    else GOV / "agent-relay" / "task-pool.json"
)
WORK_ITEMS_PATH = GOV / "work" / "work-items.json"
TASKS_PATH = GOV / "control-plane-state" / "tasks.json"
BLUEPRINT_PATH = GOV / "control-plane-state" / "governance-model-execution-blueprint.json"
CHECKPOINT_PATH = GOV / "control-plane-state" / "checkpoint.json"
HANDOFF_PATH = GOV / "control-plane-state" / "handoff.json"

DONE = {"DONE", "COMPLETED", "PASS", "CLOSED", "SUPERSEDED"}
OPEN_DISPATCH = {"READY", "ACCEPTED_PENDING_CLAIM", "ACTIVATED"}
OPEN_TAKEOVER = {"READY_FOR_RECONCILIATION", "OFFERED", "ACCEPTED"}
REQUEUE_REASONS = {
    "PROVIDER_RATE_LIMIT",
    "PROVIDER_QUOTA_EXHAUSTED",
    "CONTEXT_LIMIT",
    "WAITING_FOR_INPUT",
    "DEPENDENCY_BLOCKED",
    "VOLUNTARY_HANDOFF",
    "MANUAL_SUPERVISOR_REQUEUE",
}
ROLE_ALIASES = {
    "implementer": "CODE_AGENT",
    "code_agent": "CODE_AGENT",
    "coder": "CODE_AGENT",
    "continuation-supervisor": "SUPERVISOR",
    "supervisor": "SUPERVISOR",
    "reviewer": "REVIEWER",
    "intaker": "INTAKER",
}


def read_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return default or {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def git_head() -> str:
    cp = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False)
    if cp.returncode != 0 or not cp.stdout.strip():
        raise ValueError("exact git HEAD unavailable")
    return cp.stdout.strip()


def packet_id(subject_id: str, source_kind: str) -> str:
    raw = json.dumps({"subject_id": subject_id, "source_kind": source_kind}, sort_keys=True).encode()
    return "GACR-CTX-" + hashlib.sha256(raw).hexdigest()[:20]


def claim_id(dispatch_id: str, session_id: str) -> str:
    raw = f"{dispatch_id}|{session_id}".encode()
    return "GACR-C-" + hashlib.sha256(raw).hexdigest()[:20]


def canonical_role(role: str | None) -> str | None:
    if not role:
        return None
    return ROLE_ALIASES.get(str(role).strip().lower(), str(role).strip().upper())


def source_read_first() -> list[str]:
    return [
        "00_START_HERE.md",
        "AGENTS.md",
        "docs/control-plane/CURRENT_STATE.md",
        "docs/control-plane/MASTER_SYSTEM_MAP.md",
        "docs/control-plane/REQUIREMENTS_ROADMAP.md",
        "docs/control-plane/NEXT_ACTION.md",
        "docs/control-plane/TASKS.md",
        "docs/control-plane/PROGRAM.md",
        "docs/control-plane/DECISIONS_LOG.md",
        "docs/control-plane/SUIVI.md",
        ".governance/control-plane-state/checkpoint.json",
        ".governance/control-plane-state/handoff.json",
    ]


def client_read_first() -> list[str]:
    return [
        "AGENTS.md",
        "docs/AUTOMATION.md",
        "docs/MULTI_AGENT_COORDINATION.md",
        ".governance/canonical-memory/current.json",
        ".governance/work/work-items.json",
        ".governance/work/claims.json",
        ".governance/sessions/sessions.json",
    ]


def trace_contract() -> dict:
    return {
        "version": "GACR-R8",
        "mandatory_before_mutation": [
            "READ_CONTEXT_PACKET_REFERENCES",
            "REOBSERVE_EXACT_HEAD",
            "ACCEPT_WORK_OFFER",
            "CREATE_CANONICAL_CLAIM",
        ],
        "mandatory_during_work": [
            "ACTION_TRACE_STARTED",
            "HEARTBEAT_OR_ACTIVITY_EVIDENCE",
            "ACTION_TRACE_COMPLETED_WITH_EVIDENCE",
        ],
        "mandatory_on_block": [
            "EXPLICIT_AVAILABILITY_OR_INTERRUPTION_REASON",
            "CHECKPOINT_AND_HANDOFF_IF_AGENT_CAN_STILL_RESPOND",
        ],
        "mandatory_on_voluntary_stop": [
            "CHECKPOINT_REF",
            "HANDOFF_REF",
            "EVIDENCE_REF",
            "RELINQUISH_CLAIM_FOR_REQUEUE",
        ],
        "mandatory_on_completion": [
            "CANONICAL_SUBJECT_STATUS_UPDATED_BY_ITS_OWN_AUTHORITY",
            "FINAL_EVIDENCE",
            "CHECKPOINT_OR_HANDOFF",
            "CLAIM_RELEASE_AFTER_CANONICAL_COMPLETION",
        ],
        "abrupt_loss_behavior": "GACR_FORENSICS_PLUS_EXACT_HEAD_TAKEOVER",
        "forbidden": [
            "RAW_PROMPT_PERSISTENCE",
            "TRANSCRIPT_PERSISTENCE",
            "PRIVATE_REASONING_PERSISTENCE",
            "BLIND_REPLAY_OF_IN_FLIGHT_ACTION",
            "WRITE_WITHOUT_CLAIM_AND_EXACT_HEAD",
        ],
    }


def _active_claims(claims: dict, subject_id: str | None = None) -> list[dict]:
    values = [
        x for x in claims.get("claims", [])
        if x.get("status") == "ACTIVE"
        and (subject_id is None or x.get("work_item_id") == subject_id or x.get("task_id") == subject_id)
    ]
    values.sort(key=lambda x: (str(x.get("created_at") or ""), str(x.get("claim_id") or "")))
    return values


def _active_claims_for_session(claims: dict, session_id: str) -> list[dict]:
    values = [
        x for x in claims.get("claims", [])
        if x.get("status") == "ACTIVE" and x.get("session_id") == session_id
    ]
    values.sort(key=lambda x: (str(x.get("created_at") or ""), str(x.get("claim_id") or "")))
    return values


def _subject_claim_history(claims: dict, subject_id: str) -> list[dict]:
    values = [
        x for x in claims.get("claims", [])
        if x.get("work_item_id") == subject_id or x.get("task_id") == subject_id
    ]
    values.sort(key=lambda x: (str(x.get("created_at") or ""), str(x.get("claim_id") or "")))
    return [
        {
            "claim_id": x.get("claim_id"),
            "session_id": x.get("session_id"),
            "status": x.get("status"),
            "created_at": x.get("created_at"),
            "released_at": x.get("released_at"),
            "claimed_head_sha": x.get("claimed_head_sha"),
            "final_head_sha": x.get("final_head_sha"),
            "release_reason": x.get("release_reason"),
            "checkpoint_ref": x.get("checkpoint_ref"),
            "handoff_ref": x.get("handoff_ref"),
            "evidence_ref": x.get("evidence_ref"),
        }
        for x in values
    ]


def _subject_dispatch_history(dispatches: dict, subject_id: str) -> list[dict]:
    values = [
        x for x in dispatches.get("items", [])
        if x.get("work_item_id") == subject_id or x.get("task_id") == subject_id
    ]
    values.sort(key=lambda x: (str(x.get("created_at") or ""), str(x.get("dispatch_id") or "")))
    return [
        {
            "dispatch_id": x.get("dispatch_id"),
            "dispatch_kind": x.get("dispatch_kind"),
            "status": x.get("status"),
            "offer_status": x.get("offer_status"),
            "target_session_id": x.get("target_session_id"),
            "created_at": x.get("created_at"),
            "accepted_at": x.get("accepted_at"),
            "claim_created": x.get("claim_created"),
        }
        for x in values
    ]


def _subject_takeovers(takeovers: dict, subject_id: str) -> list[dict]:
    values = [
        x for x in takeovers.get("items", [])
        if x.get("work_item_id") == subject_id or x.get("task_id") == subject_id
    ]
    values.sort(key=lambda x: (str(x.get("created_at") or ""), str(x.get("takeover_id") or "")))
    return [
        {
            "takeover_id": x.get("takeover_id"),
            "stalled_session_id": x.get("stalled_session_id"),
            "offered_to_session_id": x.get("offered_to_session_id"),
            "accepted_by_session_id": x.get("accepted_by_session_id"),
            "status": x.get("status"),
            "created_at": x.get("created_at"),
            "last_observed_head_sha": x.get("last_observed_head_sha"),
        }
        for x in values
    ]


def _forensics_for_sessions(forensics: dict, session_ids: set[str]) -> list[dict]:
    values = [
        x for x in forensics.get("items", [])
        if x.get("session_id") in session_ids
    ]
    values.sort(key=lambda x: (str(x.get("generated_at") or ""), str(x.get("forensic_id") or "")))
    return [
        {
            "forensic_id": x.get("forensic_id"),
            "session_id": x.get("session_id"),
            "classification": x.get("classification"),
            "generated_at": x.get("generated_at"),
            "resume_point": x.get("resume_point"),
            "last_checkpoint_ref": x.get("last_checkpoint_ref"),
            "last_evidence_ref": x.get("last_evidence_ref"),
        }
        for x in values
    ]


def _latest_open_dispatch(dispatches: dict, subject_id: str) -> dict | None:
    values = [
        x for x in dispatches.get("items", [])
        if (x.get("work_item_id") == subject_id or x.get("task_id") == subject_id)
        and x.get("dispatch_kind") == "WORK_OFFER"
        and x.get("status") in OPEN_DISPATCH
    ]
    values.sort(key=lambda x: str(x.get("created_at") or ""))
    return values[-1] if values else None


def _session_stalled(sessions: dict, session_id: str | None) -> bool:
    if not session_id:
        return False
    session = telemetry.session_by_id(sessions, session_id)
    if not session:
        return True
    relay = session.get("relay") or {}
    return session.get("status") == "STALLED" or relay.get("state") in {"STALLED", "TAKEOVER_READY", "HANDOFF_STALLED"}


def _dependencies_satisfied(dep_ids: list[str], statuses: dict[str, str]) -> tuple[bool, list[str]]:
    unresolved = [dep for dep in dep_ids if statuses.get(dep) not in DONE]
    return not unresolved, unresolved


def _generic_work_units(work: dict) -> list[dict]:
    by_id = {x.get("work_item_id"): x for x in work.get("items", []) if x.get("work_item_id")}
    statuses = {key: str(value.get("status") or "") for key, value in by_id.items()}
    units = []
    for item in work.get("items", []):
        subject_id = item.get("work_item_id")
        if not subject_id or item.get("status") in DONE:
            continue
        deps = list(item.get("dependencies") or [])
        deps_ok, unresolved = _dependencies_satisfied(deps, statuses)
        units.append({
            "subject_id": subject_id,
            "task_id": item.get("task_id") or subject_id,
            "source_kind": "CANONICAL_WORK_ITEM",
            "source_ref": ".governance/work/work-items.json",
            "title": item.get("title"),
            "action": item.get("next_action"),
            "objective": item.get("objective"),
            "canonical_status": item.get("status"),
            "dependencies": deps,
            "dependencies_satisfied": deps_ok,
            "unresolved_dependencies": unresolved,
            "collision_domains": sorted(set(item.get("collision_domains") or [])),
            "required_capabilities": sorted(set(item.get("required_capabilities") or [])),
            "required_authorities": sorted(set(item.get("required_authorities") or [])),
            "allowed_agent_roles": sorted(set(item.get("allowed_agent_roles") or [])),
            "planning_only": False,
            "implementation_authorized": True,
            "method": item.get("method") or "Observe → claim → execute → validate → record evidence → checkpoint/handoff.",
            "evidence_required": list(item.get("evidence_required") or []),
            "done_when": item.get("done_when"),
            "hold_if": item.get("hold_if"),
            "where_to_look": list(item.get("where_to_look") or []),
            "search_order": list(item.get("search_order") or []),
            "entry_purpose": item.get("entry_purpose"),
            "work_kind": item.get("work_kind"),
        })
    return units


def _source_blueprint_units(tasks: dict, blueprint: dict) -> list[dict]:
    if not TEMPLATE_SOURCE:
        return []
    active_legacy = {
        x.get("id") for x in tasks.get("items", [])
        if x.get("status") == "IN_PROGRESS"
    }
    groups = []
    for group in blueprint.get("groups", []):
        if group.get("legacy_id") in active_legacy or group.get("status") == "IN_PROGRESS":
            groups.append(group)

    units = []
    for group in groups:
        atomic = group.get("atomic_tasks") or []
        statuses = {x.get("task_id"): str(x.get("status") or "") for x in atomic if x.get("task_id")}
        for task in atomic:
            task_id = task.get("task_id")
            if not task_id or task.get("status") in DONE:
                continue
            deps = list(task.get("depends_on") or [])
            deps_ok, unresolved = _dependencies_satisfied(deps, statuses)
            domains = task.get("collision_domains") or group.get("collision_domains") or [f"control-plane:{group.get('group_id')}:serial"]
            roles = task.get("allowed_agent_roles") or ["CODE_AGENT", "IMPLEMENTER", "SUPERVISOR", "REVIEWER"]
            units.append({
                "subject_id": task_id,
                "task_id": task_id,
                "source_kind": "CONTROL_PLANE_BLUEPRINT_TASK",
                "source_ref": ".governance/control-plane-state/governance-model-execution-blueprint.json",
                "parent_id": group.get("group_id"),
                "legacy_parent_id": group.get("legacy_id"),
                "title": task.get("title"),
                "action": task.get("action"),
                "objective": group.get("objective"),
                "canonical_status": task.get("status"),
                "dependencies": deps,
                "dependencies_satisfied": deps_ok,
                "unresolved_dependencies": unresolved,
                "collision_domains": sorted(set(domains)),
                "required_capabilities": sorted(set(task.get("required_capabilities") or [])),
                "required_authorities": sorted(set(task.get("required_authorities") or [])),
                "allowed_agent_roles": sorted(set(roles)),
                "planning_only": bool(task.get("planning_only", group.get("planning_only", False))),
                "implementation_authorized": bool(task.get("implementation_authorized", group.get("implementation_authorized", False))),
                "method": task.get("method"),
                "evidence_required": list(task.get("evidence_required") or group.get("evidence_requirements") or []),
                "done_when": task.get("done_when"),
                "hold_if": task.get("hold_if"),
                "where_to_look": list(group.get("where_to_look") or []),
                "search_order": list(group.get("search_order") or []),
                "inputs": list(group.get("inputs") or []),
                "entry_purpose": "WORK_ON_CONTROL_PLANE",
                "work_kind": "EXECUTE_EXISTING_TASK",
            })
    return units


def _state_for_unit(
    unit: dict,
    *,
    claims: dict,
    sessions: dict,
    dispatches: dict,
    takeovers: dict,
) -> tuple[str, dict | None]:
    active_claims = _active_claims(claims, unit["subject_id"])
    if active_claims:
        claim = active_claims[-1]
        if _session_stalled(sessions, claim.get("session_id")):
            return "RECOVERY_READY", claim
        return "ACTIVE", claim
    dispatch = _latest_open_dispatch(dispatches, unit["subject_id"])
    if dispatch:
        if dispatch.get("status") == "ACCEPTED_PENDING_CLAIM":
            return "ACCEPTED_PENDING_CLAIM", None
        if dispatch.get("status") == "ACTIVATED":
            return "ACTIVE", None
        return "OFFERED", None
    if not unit.get("dependencies_satisfied"):
        return "BLOCKED", None
    if unit.get("canonical_status") in {"READY", "PLANNED", "IN_PROGRESS"}:
        return "READY", None
    return "BLOCKED", None


def _context_packet(
    unit: dict,
    *,
    state: str,
    active_claim: dict | None,
    claims: dict,
    dispatches: dict,
    takeovers: dict,
    forensics: dict,
) -> dict:
    subject_id = unit["subject_id"]
    claim_history = _subject_claim_history(claims, subject_id)
    dispatch_history = _subject_dispatch_history(dispatches, subject_id)
    takeover_history = _subject_takeovers(takeovers, subject_id)
    predecessor_sessions = {
        str(x.get("session_id"))
        for x in claim_history
        if x.get("session_id")
    }
    predecessor_sessions.update({
        str(x.get("stalled_session_id"))
        for x in takeover_history
        if x.get("stalled_session_id")
    })
    forensics_history = _forensics_for_sessions(forensics, predecessor_sessions)

    task_specific = list(unit.get("where_to_look") or [])
    read_first = source_read_first() if TEMPLATE_SOURCE else client_read_first()
    required_refs = []
    for ref in read_first + task_specific:
        if ref and ref not in required_refs:
            required_refs.append(ref)

    history_refs = (
        [
            "docs/control-plane/SUIVI.md",
            "docs/control-plane/DECISIONS_LOG.md",
            ".governance/control-plane-state/checkpoint.json",
            ".governance/control-plane-state/handoff.json",
            ".governance/control-plane-state/gacr-beacons.json",
            ".governance/control-plane-state/gacr-forensics.json",
            ".governance/control-plane-state/gacr-dispatches.json",
            ".governance/control-plane-state/gacr-claims.json",
            ".governance/control-plane-state/gacr-takeovers.json",
        ]
        if TEMPLATE_SOURCE
        else [
            ".governance/canonical-memory/current.json",
            ".governance/agent-relay/beacons.json",
            ".governance/agent-relay/forensics.json",
            ".governance/agent-relay/dispatches.json",
            ".governance/work/claims.json",
            ".governance/agent-relay/takeovers.json",
        ]
    )

    packet = {
        "schema": "gacr-contextual-task-packet/v1",
        "packet_id": packet_id(subject_id, unit["source_kind"]),
        "subject": {
            "subject_id": subject_id,
            "task_id": unit.get("task_id"),
            "source_kind": unit.get("source_kind"),
            "source_ref": unit.get("source_ref"),
            "parent_id": unit.get("parent_id"),
            "title": unit.get("title"),
            "action": unit.get("action"),
            "objective": unit.get("objective"),
            "canonical_status": unit.get("canonical_status"),
            "pool_state": state,
            "entry_purpose": unit.get("entry_purpose"),
            "work_kind": unit.get("work_kind"),
        },
        "execution_contract": {
            "planning_only": unit.get("planning_only"),
            "implementation_authorized": unit.get("implementation_authorized"),
            "dependencies": unit.get("dependencies") or [],
            "unresolved_dependencies": unit.get("unresolved_dependencies") or [],
            "collision_domains": unit.get("collision_domains") or [],
            "required_capabilities": unit.get("required_capabilities") or [],
            "required_authorities": unit.get("required_authorities") or [],
            "allowed_agent_roles": unit.get("allowed_agent_roles") or [],
            "exact_head_required_before_claim_and_mutation": True,
            "work_offer_grants_write_authority": False,
            "claim_grants_only_collision_ownership_not_business_authority": True,
        },
        "method": {
            "instructions": unit.get("method"),
            "search_order": unit.get("search_order") or [],
            "required_read_refs": required_refs,
            "evidence_required": unit.get("evidence_required") or [],
            "done_when": unit.get("done_when"),
            "hold_if": unit.get("hold_if"),
        },
        "history": {
            "completeness_contract": "READ_REFERENCED_CANONICAL_HISTORY_BEFORE_MUTATION",
            "canonical_history_refs": history_refs,
            "claim_history": claim_history,
            "dispatch_history": dispatch_history,
            "takeover_history": takeover_history,
            "forensics_history": forensics_history,
        },
        "continuity": {
            "active_claim_id": active_claim.get("claim_id") if active_claim else None,
            "predecessor_session_id": active_claim.get("session_id") if active_claim and state == "RECOVERY_READY" else None,
            "resume_mode": "TAKEOVER_RECONCILIATION" if state == "RECOVERY_READY" else "NORMAL_CLAIM",
            "blind_replay_forbidden": True,
            "exact_head_reobservation_required": True,
        },
        "trace_contract": trace_contract(),
        "privacy": {
            "raw_prompts_included": False,
            "transcripts_included": False,
            "private_reasoning_included": False,
            "provider_private_identity_inference": False,
        },
    }
    telemetry.assert_secretless(packet)
    return packet


def build_task_pool_projection(*, generated_at: str | None = None) -> dict:
    sessions = read_json(capacity.SESSIONS_PATH, {"sessions": []})
    claims = read_json(capacity.CLAIMS_PATH, {"claims": []})
    dispatches = read_json(capacity.DISPATCHES_PATH, {"items": []})
    takeovers = read_json(telemetry.TAKEOVERS_PATH, {"items": []})
    forensics = read_json(telemetry.FORENSICS_PATH, {"items": []})
    work = read_json(WORK_ITEMS_PATH, {"items": []})
    tasks = read_json(TASKS_PATH, {"items": []}) if TEMPLATE_SOURCE else {"items": []}
    blueprint = read_json(BLUEPRINT_PATH, {"groups": []}) if TEMPLATE_SOURCE else {"groups": []}

    units = _generic_work_units(work) + _source_blueprint_units(tasks, blueprint)
    items = []
    for unit in units:
        state, active_claim = _state_for_unit(
            unit,
            claims=claims,
            sessions=sessions,
            dispatches=dispatches,
            takeovers=takeovers,
        )
        context = _context_packet(
            unit,
            state=state,
            active_claim=active_claim,
            claims=claims,
            dispatches=dispatches,
            takeovers=takeovers,
            forensics=forensics,
        )
        items.append({
            **unit,
            "pool_state": state,
            "context_packet_id": context["packet_id"],
            "context_packet": context,
        })

    state_order = {
        "RECOVERY_READY": 0,
        "READY": 1,
        "ACCEPTED_PENDING_CLAIM": 2,
        "OFFERED": 3,
        "ACTIVE": 4,
        "BLOCKED": 5,
    }
    items.sort(key=lambda x: (state_order.get(x["pool_state"], 99), str(x["subject_id"])))

    ready = [x for x in items if x["pool_state"] == "READY"]
    waves: list[dict] = []
    for item in ready:
        domains = set(item.get("collision_domains") or [])
        placed = False
        for wave in waves:
            occupied = set(wave["collision_domains"])
            if domains & occupied:
                continue
            wave["subject_ids"].append(item["subject_id"])
            wave["collision_domains"] = sorted(occupied | domains)
            placed = True
            break
        if not placed:
            waves.append({
                "wave": len(waves) + 1,
                "subject_ids": [item["subject_id"]],
                "collision_domains": sorted(domains),
            })

    counts: dict[str, int] = {}
    for item in items:
        counts[item["pool_state"]] = counts.get(item["pool_state"], 0) + 1

    value = {
        "schema": "gacr-contextual-task-pool/v1",
        "process": "GACR",
        "model": "CONTEXTUAL_CONTINUOUS_TASK_POOL",
        "generated_at": generated_at or telemetry.now_iso(),
        "source_mode": "CONTROL_PLANE_SOURCE" if TEMPLATE_SOURCE else "GOVERNED_CLIENT",
        "counts": counts,
        "dispatchable_subject_ids": [x["subject_id"] for x in items if x["pool_state"] == "READY"],
        "recovery_subject_ids": [x["subject_id"] for x in items if x["pool_state"] == "RECOVERY_READY"],
        "collision_free_waves": waves,
        "items": items,
        "authority": {
            "projection_only": True,
            "canonical_task_sources_unchanged": True,
            "grants_write_authority": False,
            "claim_required": True,
            "exact_head_required": True,
        },
    }
    telemetry.assert_secretless(value)
    return value


def _semantic_projection(value: dict) -> dict:
    return {
        key: val for key, val in value.items()
        if key not in {"generated_at", "revision", "semantic_digest"}
    }


def refresh_task_pool() -> dict:
    old = read_json(POOL_PATH, {"schema": "gacr-contextual-task-pool/v1", "revision": 0, "items": []})
    new = build_task_pool_projection()
    semantic = _semantic_projection(new)
    digest = hashlib.sha256(json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    old_digest = old.get("semantic_digest")
    if old_digest == digest:
        return {"changed": 0, "path": str(POOL_PATH.relative_to(ROOT)), "revision": old.get("revision", 0), "projection": old}
    new["revision"] = int(old.get("revision", 0)) + 1
    new["semantic_digest"] = digest
    write_json(POOL_PATH, new)
    return {"changed": 1, "path": str(POOL_PATH.relative_to(ROOT)), "revision": new["revision"], "projection": new}


def _candidate_for_context(candidate: dict, item: dict) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    required_caps = set(item.get("required_capabilities") or [])
    missing_caps = sorted(required_caps - set(candidate.get("capabilities") or []))
    reasons.extend([f"MISSING_CAPABILITY:{x}" for x in missing_caps])

    required_auth = set(item.get("required_authorities") or [])
    missing_auth = sorted(required_auth - set(candidate.get("authority_grants") or []))
    reasons.extend([f"MISSING_AUTHORITY:{x}" for x in missing_auth])

    allowed = set(item.get("allowed_agent_roles") or [])
    role = canonical_role(candidate.get("agent_role"))
    if allowed and role not in allowed:
        reasons.append(f"AGENT_ROLE_NOT_ALLOWED:{role or 'UNAVAILABLE'}")
    return not reasons, reasons


def dispatch_contextual_source_tasks() -> dict:
    if not TEMPLATE_SOURCE:
        return {"changed": 0, "items": [], "reason": "CLIENT_WORK_ITEMS_DISPATCHED_BY_R7"}
    refresh = refresh_task_pool()
    pool = refresh["projection"]
    candidates = [
        x for x in capacity.agent_pool_projection().get("items", [])
        if x.get("eligible_for_new_work")
    ]
    claims = read_json(capacity.CLAIMS_PATH, {"claims": []})
    sessions = read_json(capacity.SESSIONS_PATH, {"sessions": []})
    dispatches = read_json(capacity.DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    occupied = {
        domain
        for claim in _active_claims(claims)
        for domain in claim.get("collision_domains", [])
    }
    for item in dispatches.get("items", []):
        if item.get("dispatch_kind") == "WORK_OFFER" and item.get("status") in {"READY", "ACCEPTED_PENDING_CLAIM"}:
            occupied.update(item.get("collision_domains") or [])

    cfg = capacity.config()
    outstanding_by_session: dict[str, int] = {}
    for item in dispatches.get("items", []):
        if item.get("dispatch_kind") == "WORK_OFFER" and item.get("status") in {"READY", "ACCEPTED_PENDING_CLAIM"}:
            sid = item.get("target_session_id")
            if sid:
                outstanding_by_session[sid] = outstanding_by_session.get(sid, 0) + 1

    changes = []
    for item in pool.get("items", []):
        if item.get("source_kind") != "CONTROL_PLANE_BLUEPRINT_TASK" or item.get("pool_state") != "READY":
            continue
        subject_id = item["subject_id"]
        existing = _latest_open_dispatch(dispatches, subject_id)
        if existing:
            continue
        domains = set(item.get("collision_domains") or [])
        if domains & occupied:
            continue

        evaluations = []
        eligible = []
        for candidate in candidates:
            sid = candidate.get("session_id")
            if outstanding_by_session.get(sid, 0) >= cfg["max_parallel_offers_per_session"]:
                evaluations.append({"session_id": sid, "status": "INELIGIBLE", "reasons": ["SESSION_OFFER_CAPACITY_REACHED"]})
                continue
            ok, reasons = _candidate_for_context(candidate, item)
            evaluations.append({"session_id": sid, "status": "ELIGIBLE" if ok else "INELIGIBLE", "reasons": reasons})
            if ok:
                eligible.append(candidate)
        if not eligible:
            continue
        eligible.sort(key=lambda x: (outstanding_by_session.get(x.get("session_id"), 0), str(x.get("session_id") or "")))
        selected = eligible[0]
        sid = selected["session_id"]
        session = telemetry.session_by_id(sessions, sid)
        if not session:
            continue
        dispatch_id = telemetry.runtime_id("GACR-W-", {
            "work_item_id": subject_id,
            "target_session_id": sid,
            "source_kind": item.get("source_kind"),
        })
        offer = {
            "dispatch_id": dispatch_id,
            "dispatch_kind": "WORK_OFFER",
            "status": "READY",
            "offer_status": "PENDING_ACCEPTANCE",
            "created_at": telemetry.now_iso(),
            "target_session_id": sid,
            "target_client_instance_id": session.get("client_instance_id"),
            "work_item_id": subject_id,
            "task_id": item.get("task_id"),
            "source_kind": item.get("source_kind"),
            "source_ref": item.get("source_ref"),
            "collision_domains": item.get("collision_domains") or [],
            "required_capabilities": item.get("required_capabilities") or [],
            "required_authorities": item.get("required_authorities") or [],
            "allowed_agent_roles": item.get("allowed_agent_roles") or [],
            "delivery_modes": capacity._delivery_modes(session),
            "requires_offer_acceptance": True,
            "requires_claim_after_acceptance": True,
            "requires_exact_head_reconciliation": True,
            "may_write_before_acceptance": False,
            "claim_created": False,
            "grants_write_authority": False,
            "context_packet_id": item.get("context_packet_id"),
            "context_packet": item.get("context_packet"),
            "trace_contract": trace_contract(),
            "compatibility_evaluations": evaluations,
        }
        dispatches.setdefault("items", []).append(offer)
        outstanding_by_session[sid] = outstanding_by_session.get(sid, 0) + 1
        occupied.update(domains)
        changes.append(offer)

    if changes:
        dispatches["revision"] = int(dispatches.get("revision", 0)) + 1
        write_json(capacity.DISPATCHES_PATH, dispatches)
    return {"changed": len(changes), "items": changes}


def enrich_existing_dispatches() -> dict:
    refresh = refresh_task_pool()
    pool = refresh["projection"]
    by_subject = {x.get("subject_id"): x for x in pool.get("items", [])}
    dispatches = read_json(capacity.DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    changed = []
    for item in dispatches.get("items", []):
        subject_id = item.get("work_item_id") or item.get("task_id")
        pool_item = by_subject.get(subject_id)
        if not pool_item:
            continue
        if item.get("context_packet_id") == pool_item.get("context_packet_id") and item.get("context_packet") == pool_item.get("context_packet"):
            continue
        item["source_kind"] = pool_item.get("source_kind")
        item["source_ref"] = pool_item.get("source_ref")
        item["context_packet_id"] = pool_item.get("context_packet_id")
        item["context_packet"] = pool_item.get("context_packet")
        item["trace_contract"] = trace_contract()
        changed.append(item.get("dispatch_id"))
    if changed:
        dispatches["revision"] = int(dispatches.get("revision", 0)) + 1
        write_json(capacity.DISPATCHES_PATH, dispatches)
    return {"changed": len(changed), "dispatch_ids": changed}


def activate_accepted_offers() -> dict:
    refresh = refresh_task_pool()
    pool = refresh["projection"]
    by_subject = {x.get("subject_id"): x for x in pool.get("items", [])}
    dispatches = read_json(capacity.DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    claims = read_json(capacity.CLAIMS_PATH, {"schema_version": "1.0.0", "revision": 0, "claims": []})
    sessions = read_json(capacity.SESSIONS_PATH, {"sessions": []})
    current_head = git_head()
    occupied = {
        domain
        for claim in _active_claims(claims)
        for domain in claim.get("collision_domains", [])
    }
    changes = []

    for dispatch in dispatches.get("items", []):
        if dispatch.get("dispatch_kind") != "WORK_OFFER" or dispatch.get("status") != "ACCEPTED_PENDING_CLAIM" or dispatch.get("claim_created") is True:
            continue
        subject_id = dispatch.get("work_item_id") or dispatch.get("task_id")
        pool_item = by_subject.get(subject_id)
        if not pool_item:
            dispatch["claim_activation_blocker"] = "TASK_NOT_IN_CURRENT_POOL"
            continue
        accepted_head = dispatch.get("accepted_observed_head_sha")
        if not accepted_head:
            dispatch["claim_activation_blocker"] = "ACCEPTED_HEAD_UNAVAILABLE"
            continue
        if accepted_head != current_head:
            dispatch["claim_activation_blocker"] = "HEAD_MOVED_RECONCILE_REQUIRED"
            dispatch["current_head_sha"] = current_head
            continue
        sid = dispatch.get("target_session_id")
        if _active_claims_for_session(claims, sid):
            dispatch["claim_activation_blocker"] = "SESSION_ALREADY_HAS_ACTIVE_CLAIM"
            continue
        domains = set(dispatch.get("collision_domains") or [])
        if domains & occupied:
            dispatch["claim_activation_blocker"] = "COLLISION_DOMAIN_BUSY"
            continue

        cid = claim_id(dispatch["dispatch_id"], sid)
        claim = {
            "claim_id": cid,
            "session_id": sid,
            "work_item_id": subject_id,
            "task_id": dispatch.get("task_id") or subject_id,
            "claim_subject_kind": pool_item.get("source_kind"),
            "source_ref": pool_item.get("source_ref"),
            "collision_domains": sorted(domains),
            "status": "ACTIVE",
            "claimed_head_sha": current_head,
            "created_at": telemetry.now_iso(),
            "dispatch_id": dispatch.get("dispatch_id"),
            "checkpoint_ref": None,
            "handoff_ref": None,
            "evidence_ref": dispatch.get("acceptance_evidence_ref"),
            "trace_contract_version": "GACR-R8",
            "grants_business_authority": False,
            "grants_mutation_authority": False,
        }
        claims.setdefault("claims", []).append(claim)
        occupied.update(domains)
        dispatch["status"] = "ACTIVATED"
        dispatch["claim_created"] = True
        dispatch["claim_id"] = cid
        dispatch["claim_activated_at"] = telemetry.now_iso()
        dispatch.pop("claim_activation_blocker", None)

        session = telemetry.session_by_id(sessions, sid)
        if session:
            session.setdefault("relay", {})["task_id"] = dispatch.get("task_id") or subject_id
            session["relay"]["last_action"] = "WORK_CLAIM_ACTIVATED"
        changes.append({"dispatch_id": dispatch.get("dispatch_id"), "claim_id": cid, "subject_id": subject_id})

    if changes:
        claims["revision"] = int(claims.get("revision", 0)) + 1
        dispatches["revision"] = int(dispatches.get("revision", 0)) + 1
        sessions["revision"] = int(sessions.get("revision", 0)) + 1
        write_json(capacity.CLAIMS_PATH, claims)
        write_json(capacity.DISPATCHES_PATH, dispatches)
        write_json(capacity.SESSIONS_PATH, sessions)
    else:
        # Persist blocker details only when they changed from absent to present.
        write_json(capacity.DISPATCHES_PATH, dispatches)
    return {"changed": len(changes), "items": changes, "current_head_sha": current_head}


def relinquish_claim(
    *,
    claim_id_value: str,
    session_id: str,
    reason_code: str,
    observed_head: str,
    checkpoint_ref: str,
    handoff_ref: str,
    evidence_ref: str,
) -> dict:
    if reason_code not in REQUEUE_REASONS:
        raise ValueError("unsupported requeue reason")
    if not checkpoint_ref or not handoff_ref or not evidence_ref:
        raise ValueError("requeue requires checkpoint_ref, handoff_ref and evidence_ref")
    current_head = git_head()
    if observed_head != current_head:
        raise ValueError("requeue exact-head reconciliation failed")

    claims = read_json(capacity.CLAIMS_PATH, {"schema_version": "1.0.0", "revision": 0, "claims": []})
    claim = next((x for x in claims.get("claims", []) if x.get("claim_id") == claim_id_value), None)
    if not claim or claim.get("status") != "ACTIVE":
        raise ValueError("active claim not found")
    if claim.get("session_id") != session_id:
        raise ValueError("claim session mismatch")

    claim["status"] = "RELEASED_FOR_REQUEUE"
    claim["released_at"] = telemetry.now_iso()
    claim["release_reason"] = reason_code
    claim["final_head_sha"] = current_head
    claim["checkpoint_ref"] = checkpoint_ref
    claim["handoff_ref"] = handoff_ref
    claim["evidence_ref"] = evidence_ref

    dispatches = read_json(capacity.DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    for dispatch in dispatches.get("items", []):
        if dispatch.get("claim_id") == claim_id_value or dispatch.get("dispatch_id") == claim.get("dispatch_id"):
            dispatch["status"] = "REQUEUED"
            dispatch["requeued_at"] = telemetry.now_iso()
            dispatch["requeue_reason"] = reason_code
            dispatch["checkpoint_ref"] = checkpoint_ref
            dispatch["handoff_ref"] = handoff_ref
            dispatch["evidence_ref"] = evidence_ref

    sessions = read_json(capacity.SESSIONS_PATH, {"sessions": []})
    session = telemetry.session_by_id(sessions, session_id)
    if session:
        session.setdefault("relay", {})["task_id"] = None
        session["relay"]["last_action"] = "WORK_RELINQUISHED_FOR_REQUEUE"

    claims["revision"] = int(claims.get("revision", 0)) + 1
    dispatches["revision"] = int(dispatches.get("revision", 0)) + 1
    sessions["revision"] = int(sessions.get("revision", 0)) + 1
    write_json(capacity.CLAIMS_PATH, claims)
    write_json(capacity.DISPATCHES_PATH, dispatches)
    write_json(capacity.SESSIONS_PATH, sessions)
    refresh = refresh_task_pool()
    return {
        "status": "WORK_RELINQUISHED_FOR_REQUEUE",
        "claim_id": claim_id_value,
        "subject_id": claim.get("work_item_id") or claim.get("task_id"),
        "reason_code": reason_code,
        "checkpoint_ref": checkpoint_ref,
        "handoff_ref": handoff_ref,
        "evidence_ref": evidence_ref,
        "pool_revision": refresh.get("revision"),
    }


def cycle() -> dict:
    first = refresh_task_pool()
    enriched_before = enrich_existing_dispatches()
    source_dispatch = dispatch_contextual_source_tasks()
    activated = activate_accepted_offers()
    second = refresh_task_pool()
    enriched_after = enrich_existing_dispatches()
    return {
        "status": "GACR_CONTEXTUAL_TASK_POOL_CYCLE_COMPLETE",
        "pool_changed": int(first.get("changed", 0)) + int(second.get("changed", 0)),
        "pool_revision": second.get("revision"),
        "dispatches_enriched": int(enriched_before.get("changed", 0)) + int(enriched_after.get("changed", 0)),
        "source_offers_created": source_dispatch.get("changed", 0),
        "claims_activated": activated.get("changed", 0),
    }


def command_show(_: argparse.Namespace) -> None:
    print(json.dumps(build_task_pool_projection(), indent=2, ensure_ascii=False))


def command_refresh(_: argparse.Namespace) -> None:
    result = refresh_task_pool()
    print(json.dumps({k: v for k, v in result.items() if k != "projection"}, indent=2, ensure_ascii=False))


def command_cycle(_: argparse.Namespace) -> None:
    print(json.dumps(cycle(), indent=2, ensure_ascii=False))


def command_activate(_: argparse.Namespace) -> None:
    print(json.dumps(activate_accepted_offers(), indent=2, ensure_ascii=False))


def command_relinquish(args: argparse.Namespace) -> None:
    print(json.dumps(relinquish_claim(
        claim_id_value=args.claim_id,
        session_id=args.session_id,
        reason_code=args.reason_code,
        observed_head=args.observed_head,
        checkpoint_ref=args.checkpoint_ref,
        handoff_ref=args.handoff_ref,
        evidence_ref=args.evidence_ref,
    ), indent=2, ensure_ascii=False))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="GACR contextual continuous task pool")
    sub = p.add_subparsers(dest="command", required=True)
    show = sub.add_parser("show")
    show.set_defaults(fn=command_show)
    refresh = sub.add_parser("refresh")
    refresh.set_defaults(fn=command_refresh)
    cyc = sub.add_parser("cycle")
    cyc.set_defaults(fn=command_cycle)
    activate = sub.add_parser("activate-accepted")
    activate.set_defaults(fn=command_activate)
    relinquish = sub.add_parser("relinquish")
    relinquish.add_argument("--claim-id", required=True)
    relinquish.add_argument("--session-id", required=True)
    relinquish.add_argument("--reason-code", required=True, choices=sorted(REQUEUE_REASONS))
    relinquish.add_argument("--observed-head", required=True)
    relinquish.add_argument("--checkpoint-ref", required=True)
    relinquish.add_argument("--handoff-ref", required=True)
    relinquish.add_argument("--evidence-ref", required=True)
    relinquish.set_defaults(fn=command_relinquish)
    return p


def main() -> None:
    args = parser().parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
