#!/usr/bin/env python3
"""Read-only reconstruction of one governed logical agent.

This module composes existing GSCC/GSE/GACR authorities. It never admits the
current arrival, resumes a session, creates a claim, dispatches work, or grants
mutation authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


UNAVAILABLE = "UNAVAILABLE"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def state_dir(root: Path) -> Path:
    source = root / ".governance" / "control-plane-state"
    if (root / ".template-source").exists() or source.exists():
        return source
    return root / ".governance" / "agent-relay"


def load_manifest(root: Path) -> dict:
    path = root / ".governance" / "agent-reconstruction-skeleton.json"
    if not path.exists():
        raise ValueError("RECONSTRUCTION_SKELETON_MISSING")
    value = read_json(path, {})
    if value.get("schema") != "agent-reconstruction-skeleton/v1":
        raise ValueError("RECONSTRUCTION_SKELETON_SCHEMA_INVALID")
    if value.get("projection_only") is not True:
        raise ValueError("RECONSTRUCTION_SKELETON_MUST_BE_PROJECTION_ONLY")
    return value


def _logical_id(session: dict) -> str | None:
    value = session.get("logical_agent_id") or session.get("agent_identity")
    value = str(value or "").strip()
    return value or None


def _logical_entries(continuities: dict) -> list[tuple[dict, dict]]:
    rows = []
    for continuity in continuities.get("items", []):
        if not isinstance(continuity, dict):
            continue
        for logical in continuity.get("logical_agents") or []:
            if isinstance(logical, dict) and logical.get("logical_agent_id"):
                rows.append((continuity, logical))
    return rows


def resolve_target(
    sessions_doc: dict,
    continuities_doc: dict,
    *,
    logical_agent_id: str | None,
    alias: str | None,
    session_id: str | None,
) -> tuple[str, dict]:
    supplied = [bool(logical_agent_id), bool(alias), bool(session_id)]
    if sum(supplied) != 1:
        raise ValueError("EXACTLY_ONE_SELECTOR_REQUIRED")

    sessions = sessions_doc.get("sessions", [])
    entries = _logical_entries(continuities_doc)

    if logical_agent_id:
        target = logical_agent_id.strip()
        evidence = {"selector":"logical_agent_id","value":target}
    elif session_id:
        session = next((s for s in sessions if s.get("session_id") == session_id), None)
        if session is None:
            raise ValueError("SESSION_NOT_FOUND")
        target = _logical_id(session)
        if not target:
            raise ValueError("SESSION_LOGICAL_AGENT_ID_UNAVAILABLE")
        evidence = {"selector":"session_id","value":session_id}
    else:
        wanted = alias.strip().casefold()
        matches = {
            str(logical.get("logical_agent_id"))
            for _, logical in entries
            if str(logical.get("human_alias") or "").strip().casefold() == wanted
        }
        if not matches:
            raise ValueError("ALIAS_NOT_FOUND")
        if len(matches) != 1:
            raise ValueError("ALIAS_AMBIGUOUS")
        target = next(iter(matches))
        evidence = {"selector":"human_alias","value":alias}

    known = any(_logical_id(s) == target for s in sessions) or any(
        logical.get("logical_agent_id") == target for _, logical in entries
    )
    if not known:
        raise ValueError("LOGICAL_AGENT_NOT_FOUND")
    return target, evidence


def pick(obj: dict, keys: list[str]) -> dict:
    return {key: obj.get(key) for key in keys if key in obj}


def session_projection(session: dict) -> dict:
    relay = session.get("relay") or {}
    provider_contexts = [
        {
            **pick(ctx, [
                "provider_context_id",
                "provider_context_id_provenance",
                "provider",
                "provider_conversation_ref",
                "provider_conversation_ref_status",
                "provider_conversation_ref_provenance",
                "client_instance_id",
                "connection_ref",
                "runtime_surface_ref",
                "runtime_surface_ref_provenance",
                "provider_connector_app_id",
                "provider_connector_client_id",
                "provider_connector_installation_id",
                "provider_connector_slug",
                "provider_native_identity_status",
                "first_seen_at",
                "last_seen_at",
                "seen_count",
            ]),
            "provider_private_values_invented": False,
        }
        for ctx in (session.get("provider_contexts") or [])
        if isinstance(ctx, dict)
    ]
    return {
        "session_id": session.get("session_id"),
        "logical_agent_id": _logical_id(session) or UNAVAILABLE,
        "status": session.get("status"),
        "provider": session.get("provider"),
        "provider_conversation_ref": session.get("provider_conversation_ref"),
        "provider_conversation_ref_provenance": session.get("provider_conversation_ref_provenance"),
        "connection_ref": session.get("connection_ref"),
        "client_instance_id": session.get("client_instance_id"),
        "agent_role": session.get("agent_role"),
        "capabilities": list(session.get("capabilities") or []),
        "wake_channels": list(session.get("wake_channels") or []),
        "bridge_registration_ref": session.get("bridge_registration_ref"),
        "last_observed_head_sha": session.get("last_observed_head_sha"),
        "provider_contexts": provider_contexts,
        "relay": pick(relay, [
            "state",
            "last_heartbeat_at",
            "lease_expires_at",
            "last_action",
            "task_id",
            "branch",
            "pull_request",
            "last_evidence",
            "stalled_at",
        ]),
    }


def continuity_projection(item: dict, logical_agent_id: str, session_ids: set[str]) -> dict:
    logical = next(
        (entry for entry in item.get("logical_agents") or [] if entry.get("logical_agent_id") == logical_agent_id),
        None,
    )
    participants = [
        pick(p, [
            "participant_id",
            "session_id",
            "scope_id",
            "declared_role",
            "work_mode",
            "membership_state",
            "liveness_state",
            "collision_domains",
            "evidence_ref",
        ])
        for p in (item.get("participants") or [])
        if p.get("session_id") in session_ids
    ]
    events = []
    for event in item.get("events") or []:
        routes = event.get("routes") or []
        touches = (
            event.get("from_session_id") in session_ids
            or any(route.get("target_session_id") in session_ids for route in routes)
        )
        if touches:
            events.append(pick(event, [
                "event_id",
                "sequence",
                "event_kind",
                "from_session_id",
                "payload_ref",
                "state",
                "requires_ack",
                "correlation_id",
                "reply_to_event_id",
                "created_at",
                "expires_at",
            ]))
    return {
        "continuity_id": item.get("continuity_id"),
        "repository": item.get("repository"),
        "coordination_issue": item.get("coordination_issue"),
        "human_alias": (logical or {}).get("human_alias"),
        "human_alias_provenance": (logical or {}).get("human_alias_provenance"),
        "scope_ids": sorted(set((logical or {}).get("scope_ids") or [])),
        "participants": participants,
        "events": events,
        "projection_only": True,
        "grants_task_authority": False,
        "grants_claim": False,
        "grants_mutation_authority": False,
    }


def related_document_summary(path: Path, doc: dict, needles: set[str]) -> dict:
    encoded = json.dumps(doc, sort_keys=True, ensure_ascii=False)
    related = any(needle and needle in encoded for needle in needles)
    summary_keys = [
        "schema_version",
        "revision",
        "status",
        "checkpoint",
        "checkpoint_id",
        "handoff_id",
        "current_task",
        "active_task",
        "next_action",
    ]
    return {
        "path": str(path),
        "related": related,
        "summary": pick(doc, summary_keys),
    }


def recommended_next_action(sessions: list[dict]) -> str:
    active = [s for s in sessions if s.get("status") == "ACTIVE" and (s.get("relay") or {}).get("state") == "ACTIVE"]
    if active:
        return "REENTER_VIA_GSCC_AND_RESUME_ONLY_IF_CURRENT_ARRIVAL_CORRELATES"
    stalled = [
        s for s in sessions
        if s.get("status") == "STALLED" or (s.get("relay") or {}).get("state") == "TAKEOVER_READY"
    ]
    if stalled:
        return "REENTER_VIA_GSCC_THEN_GOVERNED_RECONCILIATION_OR_NEW_SESSION_SAME_LOGICAL_AGENT"
    if sessions:
        return "REENTER_VIA_GSCC_AND_REEVALUATE_CANONICAL_BINDING"
    return "ENTER_VIA_GSCC_AS_FIRST_TOUCH_OR_UNRESOLVED"


def build_reconstruction(
    root: Path,
    *,
    logical_agent_id: str | None = None,
    alias: str | None = None,
    session_id: str | None = None,
) -> dict:
    root = root.resolve()
    manifest = load_manifest(root)
    state = state_dir(root)

    sessions_doc = read_json(state / "gacr-sessions.json", {"revision":0,"sessions":[]})
    continuities_doc = read_json(state / "gacr-continuities.json", {"revision":0,"items":[]})
    claims_doc = read_json(state / "gacr-claims.json", {"revision":0,"claims":[]})
    dispatches_doc = read_json(state / "gacr-dispatches.json", {"revision":0,"items":[]})
    takeovers_doc = read_json(state / "gacr-takeovers.json", {"revision":0,"items":[]})
    forensics_doc = read_json(state / "gacr-forensics.json", {"revision":0,"items":[]})
    beacons_doc = read_json(state / "gacr-beacons.json", {"revision":0,"items":[]})
    correlations_doc = read_json(state / "gacr-correlations.json", {"revision":0,"items":[]})
    checkpoint_doc = read_json(state / "checkpoint.json", {})
    handoff_doc = read_json(state / "handoff.json", {})

    target, selector = resolve_target(
        sessions_doc,
        continuities_doc,
        logical_agent_id=logical_agent_id,
        alias=alias,
        session_id=session_id,
    )

    continuity_entries = [
        (item, logical)
        for item, logical in _logical_entries(continuities_doc)
        if logical.get("logical_agent_id") == target
    ]
    referenced_session_ids = {
        sid
        for _, logical in continuity_entries
        for sid in (logical.get("session_ids") or logical.get("reference_session_ids") or [])
        if sid
    }
    sessions = [
        session
        for session in sessions_doc.get("sessions", [])
        if _logical_id(session) == target or session.get("session_id") in referenced_session_ids
    ]
    sessions.sort(key=lambda item: str(item.get("session_id") or ""))
    session_ids = {session.get("session_id") for session in sessions if session.get("session_id")}

    aliases = sorted({
        str(logical.get("human_alias"))
        for _, logical in continuity_entries
        if logical.get("human_alias")
    })

    continuities = [
        continuity_projection(item, target, session_ids)
        for item, _ in continuity_entries
    ]

    claims = [
        pick(item, [
            "claim_id",
            "session_id",
            "work_item_id",
            "status",
            "collision_domains",
            "claimed_head_sha",
            "transferred_from_session_id",
            "transferred_at",
        ])
        for item in claims_doc.get("claims", [])
        if item.get("session_id") in session_ids
    ]

    session_ref_keys = [
        "target_session_id",
        "source_session_id",
        "from_session_id",
        "accepted_by_session_id",
        "offered_to_session_id",
        "stalled_session_id",
        "successor_session_id",
    ]
    dispatches = [
        pick(item, [
            "dispatch_id",
            "dispatch_kind",
            "status",
            "offer_status",
            "target_session_id",
            "target_logical_agent_id",
            "source_session_id",
            "from_session_id",
            "accepted_by_session_id",
            "work_item_id",
            "task_id",
            "continuity_id",
            "continuity_event_id",
            "event_kind",
            "collision_domains",
            "delivery_modes",
            "preferred_delivery_mode",
            "created_at",
            "delivered_at",
            "delivery_evidence_ref",
        ])
        for item in dispatches_doc.get("items", [])
        if any(item.get(key) in session_ids for key in session_ref_keys)
    ]

    takeovers = [
        pick(item, [
            "takeover_id",
            "stalled_session_id",
            "offered_to_session_id",
            "accepted_by_session_id",
            "successor_session_id",
            "status",
            "work_item_id",
            "task_id",
            "branch",
            "pull_request",
            "active_claim_count",
            "recoverable_work_authority",
            "work_authority_source",
            "may_continue_mutable_work",
            "created_at",
            "accepted_at",
        ])
        for item in takeovers_doc.get("items", [])
        if any(
            item.get(key) in session_ids
            for key in [
                "stalled_session_id",
                "offered_to_session_id",
                "accepted_by_session_id",
                "successor_session_id",
            ]
        )
    ]

    forensics = [
        pick(item, [
            "forensic_id",
            "session_id",
            "classification",
            "recoverability",
            "last_checkpoint_ref",
            "last_evidence_ref",
            "resume_point",
            "actions",
            "observed_at",
        ])
        for item in forensics_doc.get("items", [])
        if item.get("session_id") in session_ids
    ]

    beacons = [
        pick(item, [
            "beacon_id",
            "session_id",
            "event_type",
            "provider",
            "provider_ref",
            "client_instance_id",
            "connection_ref",
            "checkpoint_ref",
            "evidence_ref",
            "observed_at",
            "created_at",
        ])
        for item in beacons_doc.get("items", [])
        if item.get("session_id") in session_ids
    ][-20:]

    correlations = [
        pick(item, [
            "correlation_id",
            "beacon_id",
            "level",
            "selected_session_id",
            "candidate_session_ids",
            "reasons",
            "observed_at",
        ])
        for item in correlations_doc.get("items", [])
        if item.get("selected_session_id") in session_ids
        or bool(set(item.get("candidate_session_ids") or []) & session_ids)
    ][-20:]

    collision_domains = sorted({
        domain
        for item in claims + continuities
        for domain in (
            item.get("collision_domains")
            or [
                d
                for participant in item.get("participants", [])
                for d in (participant.get("collision_domains") or [])
            ]
        )
        if domain
    })
    task_ids = sorted({
        value
        for session in sessions
        for value in [(session.get("relay") or {}).get("task_id")]
        if value
    } | {
        value
        for item in dispatches + takeovers
        for value in [item.get("task_id")]
        if value
    })
    work_item_ids = sorted({
        value
        for item in claims + dispatches + takeovers
        for value in [item.get("work_item_id")]
        if value
    })

    needles = set(session_ids) | {target} | {item.get("continuity_id") for item in continuities if item.get("continuity_id")}
    projected_sessions = [session_projection(session) for session in sessions]

    return {
        "schema":"gacr-agent-reconstruction/v1",
        "status":"RECONSTRUCTED",
        "projection_only":True,
        "grants_admission":False,
        "grants_task_authority":False,
        "grants_claim":False,
        "grants_mutation_authority":False,
        "selector":selector,
        "block":{
            "name":"AGENT_RECONSTRUCTION_BLOCK",
            "block_key":target,
            "new_block_id_minted":False,
            "logical_agent_id":target,
            "human_aliases":aliases,
            "session_ids":sorted(session_ids),
            "session_count":len(session_ids),
            "provider_context_count":sum(len(s.get("provider_contexts") or []) for s in projected_sessions),
        },
        "sessions":projected_sessions,
        "continuities":continuities,
        "communication_bus":{
            "continuity_ids":sorted(item.get("continuity_id") for item in continuities if item.get("continuity_id")),
            "coordination_issues":sorted({
                item.get("coordination_issue") for item in continuities if item.get("coordination_issue") is not None
            }),
            "routing_order":list((manifest.get("bus_contract") or {}).get("routing_order") or []),
            "event_count":sum(len(item.get("events") or []) for item in continuities),
            "new_bus_created":False,
        },
        "work_links":{
            "task_ids":task_ids,
            "work_item_ids":work_item_ids,
            "claim_ids":sorted(item.get("claim_id") for item in claims if item.get("claim_id")),
            "dispatch_ids":sorted(item.get("dispatch_id") for item in dispatches if item.get("dispatch_id")),
            "collision_domains":collision_domains,
        },
        "claims":claims,
        "dispatches":dispatches,
        "takeovers":takeovers,
        "forensics":forensics,
        "beacons":beacons,
        "correlations":correlations,
        "repository_resume":{
            "checkpoint":related_document_summary(state / "checkpoint.json", checkpoint_doc, needles),
            "handoff":related_document_summary(state / "handoff.json", handoff_doc, needles),
        },
        "reconstruction_path":manifest.get("stages") or [],
        "canonical_source_revisions":{
            "sessions":int(sessions_doc.get("revision",0)),
            "continuities":int(continuities_doc.get("revision",0)),
            "claims":int(claims_doc.get("revision",0)),
            "dispatches":int(dispatches_doc.get("revision",0)),
            "takeovers":int(takeovers_doc.get("revision",0)),
            "forensics":int(forensics_doc.get("revision",0)),
            "beacons":int(beacons_doc.get("revision",0)),
            "correlations":int(correlations_doc.get("revision",0)),
        },
        "recommended_next_action":recommended_next_action(sessions),
        "current_arrival_rule":"RECONSTRUCTION_DOES_NOT_BIND_CURRENT_ARRIVAL_RUN_GSCC_GSE_GACR_F1",
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Read-only governed logical-agent reconstruction")
    p.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--logical-agent-id")
    group.add_argument("--alias")
    group.add_argument("--session-id")
    p.add_argument("--compact", action="store_true")
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        value = build_reconstruction(
            Path(args.root),
            logical_agent_id=args.logical_agent_id,
            alias=args.alias,
            session_id=args.session_id,
        )
    except ValueError as exc:
        print(json.dumps({
            "schema":"gacr-agent-reconstruction-error/v1",
            "status":"FAIL_CLOSED",
            "error":str(exc),
            "grants_admission":False,
            "grants_claim":False,
            "grants_mutation_authority":False,
        }, ensure_ascii=False))
        return 2
    print(json.dumps(value, indent=None if args.compact else 2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
