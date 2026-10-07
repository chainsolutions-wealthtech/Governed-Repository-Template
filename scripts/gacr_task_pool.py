#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
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
BLUEPRINT_PATH = GOV / "control-plane-state" / "governance-model-execution-blueprint.json"

OPEN_DISPATCH = {"READY", "ACCEPTED_PENDING_CLAIM", "ACTIVATED"}
REQUEUE_REASONS = {
    "PROVIDER_RATE_LIMIT",
    "PROVIDER_QUOTA_EXHAUSTED",
    "CONTEXT_LIMIT",
    "WAITING_FOR_INPUT",
    "DEPENDENCY_BLOCKED",
    "VOLUNTARY_HANDOFF",
    "MANUAL_SUPERVISOR_REQUEUE",
}


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


def git_head() -> str:
    cp = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False)
    if cp.returncode != 0 or not cp.stdout.strip():
        raise ValueError("exact git HEAD unavailable")
    return cp.stdout.strip()


def context_packet_id(work_item_id: str) -> str:
    raw = json.dumps({"work_item_id": work_item_id, "revision": "R9"}, sort_keys=True).encode()
    return "GACR-CTX-" + hashlib.sha256(raw).hexdigest()[:20]


def claim_id(dispatch_id: str, session_id: str) -> str:
    return "GACR-C-" + hashlib.sha256(f"{dispatch_id}|{session_id}".encode()).hexdigest()[:20]


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
        "version": "GACR-R9",
        "before_mutation": [
            "READ_CONTEXT_PACKET_REFERENCES",
            "REOBSERVE_EXACT_HEAD",
            "ACCEPT_WORK_OFFER_WITH_OBSERVED_HEAD",
            "OBTAIN_CANONICAL_CLAIM",
        ],
        "during_work": [
            "ACTION_TRACE_STARTED",
            "HEARTBEAT_OR_ACTIVITY_EVIDENCE",
            "ACTION_TRACE_COMPLETED_WITH_EVIDENCE",
        ],
        "on_block": [
            "EXPLICIT_AVAILABILITY_OR_INTERRUPTION_REASON",
            "CHECKPOINT_AND_HANDOFF_IF_AGENT_CAN_RESPOND",
        ],
        "on_voluntary_stop": [
            "CHECKPOINT_REF",
            "HANDOFF_REF",
            "EVIDENCE_REF",
            "RELINQUISH_CLAIM_FOR_REQUEUE",
        ],
        "on_completion": [
            "UPDATE_CANONICAL_TASK_AUTHORITY",
            "FINAL_EVIDENCE",
            "CHECKPOINT_OR_HANDOFF",
            "RELEASE_CLAIM",
        ],
        "abrupt_loss": "GACR_FORENSICS_TAKEOVER_EXACT_HEAD_RECONCILIATION",
        "forbidden": [
            "RAW_CONVERSATION_CONTENT_PERSISTENCE",
            "INTERNAL_REASONING_PERSISTENCE",
            "BLIND_REPLAY_OF_IN_FLIGHT_ACTION",
            "MUTATION_WITHOUT_CLAIM_AND_APPLICABLE_AUTHORITY",
        ],
    }


def _active_claims(claims: dict) -> list[dict]:
    values = [x for x in claims.get("claims", []) if x.get("status") == "ACTIVE"]
    values.sort(key=lambda x: (str(x.get("created_at") or ""), str(x.get("claim_id") or "")))
    return values


def _claims_for_work(claims: dict, work_item_id: str) -> list[dict]:
    return [
        x for x in _active_claims(claims)
        if x.get("work_item_id") == work_item_id or x.get("task_id") == work_item_id
    ]


def _claims_for_session(claims: dict, session_id: str) -> list[dict]:
    return [x for x in _active_claims(claims) if x.get("session_id") == session_id]


def _claim_history(claims: dict, work_item_id: str) -> list[dict]:
    values = [
        x for x in claims.get("claims", [])
        if x.get("work_item_id") == work_item_id or x.get("task_id") == work_item_id
    ]
    values.sort(key=lambda x: (str(x.get("created_at") or ""), str(x.get("claim_id") or "")))
    fields = (
        "claim_id", "session_id", "status", "created_at", "released_at",
        "claimed_head_sha", "final_head_sha", "release_reason",
        "checkpoint_ref", "handoff_ref", "evidence_ref", "dispatch_id",
    )
    return [{key: item.get(key) for key in fields} for item in values]


def _dispatch_history(dispatches: dict, work_item_id: str) -> list[dict]:
    values = [
        x for x in dispatches.get("items", [])
        if x.get("work_item_id") == work_item_id or x.get("task_id") == work_item_id
    ]
    values.sort(key=lambda x: (str(x.get("created_at") or ""), str(x.get("dispatch_id") or "")))
    fields = (
        "dispatch_id", "dispatch_kind", "status", "offer_status",
        "target_session_id", "created_at", "accepted_at", "claim_created",
        "claim_id", "requeued_at", "requeue_reason",
    )
    return [{key: item.get(key) for key in fields} for item in values]


def _takeover_history(takeovers: dict, work_item_id: str) -> list[dict]:
    values = [
        x for x in takeovers.get("items", [])
        if x.get("work_item_id") == work_item_id or x.get("task_id") == work_item_id
    ]
    values.sort(key=lambda x: (str(x.get("created_at") or ""), str(x.get("takeover_id") or "")))
    fields = (
        "takeover_id", "stalled_session_id", "offered_to_session_id",
        "accepted_by_session_id", "status", "created_at", "last_observed_head_sha",
    )
    return [{key: item.get(key) for key in fields} for item in values]


def _forensics_for_sessions(forensics: dict, session_ids: set[str]) -> list[dict]:
    values = [x for x in forensics.get("items", []) if x.get("session_id") in session_ids]
    values.sort(key=lambda x: (str(x.get("generated_at") or ""), str(x.get("forensic_id") or "")))
    fields = (
        "forensic_id", "session_id", "classification", "generated_at",
        "resume_point", "last_checkpoint_ref", "last_evidence_ref",
    )
    return [{key: item.get(key) for key in fields} for item in values]


def _open_dispatch(dispatches: dict, work_item_id: str) -> dict | None:
    values = [
        x for x in dispatches.get("items", [])
        if x.get("dispatch_kind") == "WORK_OFFER"
        and (x.get("work_item_id") == work_item_id or x.get("task_id") == work_item_id)
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


def _blueprint_context(task_id: str) -> dict:
    if not TEMPLATE_SOURCE:
        return {}
    blueprint = read_json(BLUEPRINT_PATH, {})
    for group in blueprint.get("groups", []):
        for task in group.get("atomic_tasks", []) or []:
            if task.get("task_id") != task_id:
                continue
            return {
                "method": task.get("method"),
                "where_to_look": list(group.get("where_to_look") or []),
                "search_order": list(group.get("search_order") or []),
                "inputs": list(group.get("inputs") or []),
                "group_objective": group.get("objective"),
                "hold_if": task.get("hold_if"),
                "done_when": task.get("done_when"),
                "evidence_required": list(task.get("evidence_required") or group.get("evidence_requirements") or []),
            }
    return {}


def _pool_state(
    item: dict,
    *,
    sessions: dict,
    claims: dict,
    dispatches: dict,
) -> tuple[str, dict | None]:
    work_item_id = item.get("work_item_id") or item.get("task_id")
    active = _claims_for_work(claims, work_item_id)
    if active:
        claim = active[-1]
        if _session_stalled(sessions, claim.get("session_id")):
            return "RECOVERY_READY", claim
        return "ACTIVE", claim
    dispatch = _open_dispatch(dispatches, work_item_id)
    if dispatch:
        if dispatch.get("status") == "ACCEPTED_PENDING_CLAIM":
            return "ACCEPTED_PENDING_CLAIM", None
        if dispatch.get("status") == "ACTIVATED":
            return "ACTIVE", None
        return "OFFERED", None
    if item.get("status") == "READY":
        return "READY", None
    return "BLOCKED", None


def _context_packet(
    item: dict,
    *,
    pool_state: str,
    active_claim: dict | None,
    claims: dict,
    dispatches: dict,
    takeovers: dict,
    forensics: dict,
) -> dict:
    work_item_id = item.get("work_item_id") or item.get("task_id")
    blueprint = _blueprint_context(item.get("task_id") or work_item_id)
    claim_history = _claim_history(claims, work_item_id)
    dispatch_history = _dispatch_history(dispatches, work_item_id)
    takeover_history = _takeover_history(takeovers, work_item_id)
    predecessor_sessions = {
        str(x.get("session_id")) for x in claim_history if x.get("session_id")
    }
    predecessor_sessions.update({
        str(x.get("stalled_session_id"))
        for x in takeover_history if x.get("stalled_session_id")
    })
    forensic_history = _forensics_for_sessions(forensics, predecessor_sessions)

    read_first = source_read_first() if TEMPLATE_SOURCE else client_read_first()
    for ref in blueprint.get("where_to_look", []):
        if ref and ref not in read_first:
            read_first.append(ref)

    packet = {
        "schema": "gacr-contextual-task-packet/v1",
        "packet_id": context_packet_id(work_item_id),
        "subject": {
            "work_item_id": work_item_id,
            "task_id": item.get("task_id") or work_item_id,
            "title": item.get("title"),
            "global_task_id": item.get("global_task_id"),
            "work_package_id": item.get("work_package_id"),
            "work_source": item.get("work_source"),
            "canonical_status": item.get("status"),
            "pool_state": pool_state,
        },
        "execution_contract": {
            "planning_only": bool(item.get("planning_only", False)),
            "implementation_authorized": bool(item.get("implementation_authorized", False)),
            "dependencies": list(item.get("dependencies") or []),
            "collision_domains": sorted(set(item.get("collision_domains") or [])),
            "required_capabilities": sorted(set(item.get("required_capabilities") or [])),
            "required_authorities": sorted(set(item.get("required_authorities") or [])),
            "allowed_agent_roles": sorted(set(item.get("allowed_agent_roles") or [])),
            "requires_f1_release": bool(item.get("requires_f1_release", TEMPLATE_SOURCE)),
            "exact_head_required_before_claim_and_mutation": True,
            "offer_ne_claim_ne_authority": True,
            "claim_ne_business_authority": True,
        },
        "method": {
            "instructions": blueprint.get("method") or item.get("method"),
            "search_order": blueprint.get("search_order") or list(item.get("search_order") or []),
            "required_read_refs": read_first,
            "inputs": blueprint.get("inputs") or list(item.get("inputs") or []),
            "evidence_required": blueprint.get("evidence_required") or list(item.get("evidence_required") or []),
            "done_when": blueprint.get("done_when") or item.get("done_when"),
            "hold_if": blueprint.get("hold_if") or item.get("hold_if"),
            "group_objective": blueprint.get("group_objective"),
        },
        "history": {
            "completeness_contract": "READ_REFERENCED_CANONICAL_HISTORY_BEFORE_MUTATION",
            "claim_history": claim_history,
            "dispatch_history": dispatch_history,
            "takeover_history": takeover_history,
            "forensics_history": forensic_history,
        },
        "continuity": {
            "active_claim_id": active_claim.get("claim_id") if active_claim else None,
            "predecessor_session_id": active_claim.get("session_id") if active_claim and pool_state == "RECOVERY_READY" else None,
            "resume_mode": "TAKEOVER_RECONCILIATION" if pool_state == "RECOVERY_READY" else "NORMAL_CLAIM",
            "blind_replay_forbidden": True,
            "successor_exact_head_reconciliation_required": True,
        },
        "trace_contract": trace_contract(),
        "privacy": {
            "raw_conversation_content_persisted": False,
            "assistant_internal_workings_persisted": False,
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
    work = capacity.canonical_work_document()

    items = []
    for raw in work.get("items", []):
        if raw.get("status") in {"DONE", "COMPLETED", "PASS", "CLOSED"}:
            continue
        work_item_id = raw.get("work_item_id") or raw.get("task_id")
        if not work_item_id:
            continue
        state, active_claim = _pool_state(raw, sessions=sessions, claims=claims, dispatches=dispatches)
        packet = _context_packet(
            raw,
            pool_state=state,
            active_claim=active_claim,
            claims=claims,
            dispatches=dispatches,
            takeovers=takeovers,
            forensics=forensics,
        )
        items.append({
            **raw,
            "pool_state": state,
            "context_packet_id": packet["packet_id"],
            "context_packet": packet,
        })

    order = {
        "RECOVERY_READY": 0,
        "READY": 1,
        "ACCEPTED_PENDING_CLAIM": 2,
        "OFFERED": 3,
        "ACTIVE": 4,
        "BLOCKED": 5,
    }
    items.sort(key=lambda x: (order.get(x["pool_state"], 99), str(x.get("work_item_id") or "")))

    waves: list[dict] = []
    for item in [x for x in items if x["pool_state"] == "READY"]:
        domains = set(item.get("collision_domains") or [])
        for wave in waves:
            occupied = set(wave["collision_domains"])
            if domains & occupied:
                continue
            wave["work_item_ids"].append(item.get("work_item_id"))
            wave["collision_domains"] = sorted(occupied | domains)
            break
        else:
            waves.append({
                "wave": len(waves) + 1,
                "work_item_ids": [item.get("work_item_id")],
                "collision_domains": sorted(domains),
            })

    counts: dict[str, int] = {}
    for item in items:
        counts[item["pool_state"]] = counts.get(item["pool_state"], 0) + 1

    value = {
        "schema": "gacr-contextual-task-pool/v1",
        "process": "GACR",
        "model": "CONTEXTUAL_CONTINUOUS_TASK_POOL",
        "revision_authority": "CP-AGENT-RELAY-001-R9",
        "generated_at": generated_at or telemetry.now_iso(),
        "work_source": work.get("source"),
        "work_source_status": work.get("source_status"),
        "global_task_id": work.get("global_task_id"),
        "work_package_id": work.get("work_package_id"),
        "counts": counts,
        "dispatchable_work_item_ids": [x.get("work_item_id") for x in items if x["pool_state"] == "READY"],
        "recovery_work_item_ids": [x.get("work_item_id") for x in items if x["pool_state"] == "RECOVERY_READY"],
        "collision_free_waves": waves,
        "items": items,
        "authority": {
            "projection_only": True,
            "dispatcher_authority": "CP-AGENT-RELAY-001-R8",
            "canonical_task_sources_unchanged": True,
            "grants_write_authority": False,
            "claim_required": True,
            "exact_head_required": True,
        },
    }
    telemetry.assert_secretless(value)
    return value


def _semantic_projection(value: dict) -> dict:
    return {key: val for key, val in value.items() if key not in {"generated_at", "revision", "semantic_digest"}}


def refresh_task_pool() -> dict:
    old = read_json(POOL_PATH, {"revision": 0})
    new = build_task_pool_projection()
    digest = hashlib.sha256(
        json.dumps(_semantic_projection(new), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if old.get("semantic_digest") == digest:
        return {"changed": 0, "revision": old.get("revision", 0), "projection": old}
    new["revision"] = int(old.get("revision", 0)) + 1
    new["semantic_digest"] = digest
    write_json(POOL_PATH, new)
    return {"changed": 1, "revision": new["revision"], "projection": new}


def enrich_work_offers() -> dict:
    projection = refresh_task_pool()["projection"]
    by_id = {x.get("work_item_id"): x for x in projection.get("items", [])}
    dispatches = read_json(capacity.DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    changed = []
    for item in dispatches.get("items", []):
        if item.get("dispatch_kind") != "WORK_OFFER":
            continue
        pool_item = by_id.get(item.get("work_item_id"))
        if not pool_item:
            continue
        packet = pool_item.get("context_packet")
        if item.get("context_packet") == packet and item.get("trace_contract") == trace_contract():
            continue
        item["context_packet_id"] = pool_item.get("context_packet_id")
        item["context_packet"] = packet
        item["trace_contract"] = trace_contract()
        item["contextual_pool_revision_authority"] = "CP-AGENT-RELAY-001-R9"
        changed.append(item.get("dispatch_id"))
    if changed:
        dispatches["revision"] = int(dispatches.get("revision", 0)) + 1
        write_json(capacity.DISPATCHES_PATH, dispatches)
    return {"changed": len(changed), "dispatch_ids": changed}


def activate_accepted_offers() -> dict:
    projection = refresh_task_pool()["projection"]
    by_id = {x.get("work_item_id"): x for x in projection.get("items", [])}
    dispatches = read_json(capacity.DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    claims = read_json(capacity.CLAIMS_PATH, {"schema_version": "1.0.0", "revision": 0, "claims": []})
    sessions = read_json(capacity.SESSIONS_PATH, {"sessions": []})
    current_head = git_head()
    occupied = {
        domain
        for claim in _active_claims(claims)
        for domain in claim.get("collision_domains", [])
        if domain
    }
    changed = []
    blocker_changed = False

    for dispatch in dispatches.get("items", []):
        if dispatch.get("dispatch_kind") != "WORK_OFFER":
            continue
        if dispatch.get("status") != "ACCEPTED_PENDING_CLAIM" or dispatch.get("claim_created") is True:
            continue
        work_item_id = dispatch.get("work_item_id")
        pool_item = by_id.get(work_item_id)
        if not pool_item or pool_item.get("canonical_status") == "DONE":
            if dispatch.get("claim_activation_blocker") != "CANONICAL_WORK_NOT_AVAILABLE":
                dispatch["claim_activation_blocker"] = "CANONICAL_WORK_NOT_AVAILABLE"
                blocker_changed = True
            continue
        accepted_head = dispatch.get("accepted_observed_head_sha")
        if not accepted_head:
            if dispatch.get("claim_activation_blocker") != "ACCEPTED_HEAD_UNAVAILABLE":
                dispatch["claim_activation_blocker"] = "ACCEPTED_HEAD_UNAVAILABLE"
                blocker_changed = True
            continue
        if accepted_head != current_head:
            if dispatch.get("claim_activation_blocker") != "HEAD_MOVED_RECONCILE_REQUIRED" or dispatch.get("current_head_sha") != current_head:
                dispatch["claim_activation_blocker"] = "HEAD_MOVED_RECONCILE_REQUIRED"
                dispatch["current_head_sha"] = current_head
                blocker_changed = True
            continue
        session_id = dispatch.get("target_session_id")
        if _claims_for_session(claims, session_id):
            if dispatch.get("claim_activation_blocker") != "SESSION_ALREADY_HAS_ACTIVE_CLAIM":
                dispatch["claim_activation_blocker"] = "SESSION_ALREADY_HAS_ACTIVE_CLAIM"
                blocker_changed = True
            continue
        domains = set(dispatch.get("collision_domains") or [])
        if domains & occupied:
            if dispatch.get("claim_activation_blocker") != "COLLISION_DOMAIN_BUSY":
                dispatch["claim_activation_blocker"] = "COLLISION_DOMAIN_BUSY"
                blocker_changed = True
            continue

        session = telemetry.session_by_id(sessions, session_id)
        if not session:
            if dispatch.get("claim_activation_blocker") != "SESSION_NOT_FOUND":
                dispatch["claim_activation_blocker"] = "SESSION_NOT_FOUND"
                blocker_changed = True
            continue

        cid = claim_id(dispatch["dispatch_id"], session_id)
        claim = {
            "claim_id": cid,
            "session_id": session_id,
            "work_item_id": work_item_id,
            "task_id": dispatch.get("task_id") or work_item_id,
            "work_source": dispatch.get("work_source"),
            "global_task_id": dispatch.get("global_task_id"),
            "work_package_id": dispatch.get("work_package_id"),
            "collision_domains": sorted(domains),
            "status": "ACTIVE",
            "claimed_head_sha": current_head,
            "branch": (session.get("relay") or {}).get("branch"),
            "created_at": telemetry.now_iso(),
            "dispatch_id": dispatch.get("dispatch_id"),
            "checkpoint_ref": None,
            "handoff_ref": None,
            "evidence_ref": dispatch.get("acceptance_evidence_ref"),
            "trace_contract_version": "GACR-R9",
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
        dispatch.pop("current_head_sha", None)
        session.setdefault("relay", {})["task_id"] = dispatch.get("task_id") or work_item_id
        session["relay"]["last_action"] = "WORK_CLAIM_ACTIVATED"
        changed.append({"dispatch_id": dispatch.get("dispatch_id"), "claim_id": cid, "work_item_id": work_item_id})

    if changed:
        claims["revision"] = int(claims.get("revision", 0)) + 1
        sessions["revision"] = int(sessions.get("revision", 0)) + 1
        write_json(capacity.CLAIMS_PATH, claims)
        write_json(capacity.SESSIONS_PATH, sessions)
    if changed or blocker_changed:
        dispatches["revision"] = int(dispatches.get("revision", 0)) + 1
        write_json(capacity.DISPATCHES_PATH, dispatches)

    return {"changed": len(changed), "items": changed, "current_head_sha": current_head}


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
    if not re.fullmatch(r"[0-9a-f]{40}", observed_head):
        raise ValueError("requeue requires a valid observed git SHA")

    claims = read_json(capacity.CLAIMS_PATH, {"schema_version": "1.0.0", "revision": 0, "claims": []})
    claim = next((x for x in claims.get("claims", []) if x.get("claim_id") == claim_id_value), None)
    if not claim or claim.get("status") != "ACTIVE":
        raise ValueError("active claim not found")
    if claim.get("session_id") != session_id:
        raise ValueError("claim session mismatch")

    control_head = git_head()
    claim["status"] = "RELEASED_FOR_REQUEUE"
    claim["released_at"] = telemetry.now_iso()
    claim["release_reason"] = reason_code
    claim["final_head_sha"] = observed_head
    claim["control_plane_head_at_requeue"] = control_head
    claim["successor_exact_head_reconciliation_required"] = True
    claim["checkpoint_ref"] = checkpoint_ref
    claim["handoff_ref"] = handoff_ref
    claim["evidence_ref"] = evidence_ref

    dispatches = read_json(capacity.DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    for dispatch in dispatches.get("items", []):
        if dispatch.get("claim_id") == claim_id_value or dispatch.get("dispatch_id") == claim.get("dispatch_id"):
            dispatch["status"] = "REQUEUED"
            dispatch["offer_status"] = "REQUEUED"
            dispatch["requeued_at"] = telemetry.now_iso()
            dispatch["requeue_reason"] = reason_code
            dispatch["checkpoint_ref"] = checkpoint_ref
            dispatch["handoff_ref"] = handoff_ref
            dispatch["evidence_ref"] = evidence_ref
            dispatch["claim_created"] = False

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
    refreshed = refresh_task_pool()
    return {
        "status": "WORK_RELINQUISHED_FOR_REQUEUE",
        "claim_id": claim_id_value,
        "work_item_id": claim.get("work_item_id"),
        "reason_code": reason_code,
        "checkpoint_ref": checkpoint_ref,
        "handoff_ref": handoff_ref,
        "evidence_ref": evidence_ref,
        "observed_head_sha": observed_head,
        "control_plane_head_at_requeue": control_head,
        "successor_exact_head_reconciliation_required": True,
        "pool_revision": refreshed.get("revision"),
    }


def cycle() -> dict:
    first = refresh_task_pool()
    enriched_before = enrich_work_offers()
    activated = activate_accepted_offers()
    second = refresh_task_pool()
    enriched_after = enrich_work_offers()
    return {
        "status": "GACR_CONTEXTUAL_TASK_POOL_CYCLE_COMPLETE",
        "pool_revision": second.get("revision"),
        "pool_changed": int(first.get("changed", 0)) + int(second.get("changed", 0)),
        "dispatches_enriched": int(enriched_before.get("changed", 0)) + int(enriched_after.get("changed", 0)),
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
    p = argparse.ArgumentParser(description="GACR R9 contextual continuous task pool")
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
