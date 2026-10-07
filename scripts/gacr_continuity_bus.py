#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(os.environ.get("GACR_ROOT") or Path(__file__).resolve().parents[1]).resolve()
GOV = ROOT / ".governance"
TEMPLATE_SOURCE = (ROOT / ".template-source").exists()

if TEMPLATE_SOURCE:
    STATE_PATH = GOV / "control-plane-state" / "gacr-continuities.json"
    SESSIONS_PATH = GOV / "control-plane-state" / "gacr-sessions.json"
    DISPATCHES_PATH = GOV / "control-plane-state" / "gacr-dispatches.json"
else:
    STATE_PATH = GOV / "agent-relay" / "continuities.json"
    SESSIONS_PATH = GOV / "sessions" / "sessions.json"
    DISPATCHES_PATH = GOV / "agent-relay" / "dispatches.json"

EVENT_KINDS = {
    "INSTRUCTION", "ACK", "REQUEST", "RESPONSE", "RESULT", "REVIEW_REQUEST",
    "REVIEW_RESULT", "SCOPE_UPDATE", "YIELD", "HANDOFF", "BLOCKER",
    "RECOVERY_REQUEST", "LOOP_TICK",
}
FINAL_EVENT_STATES = {"RESPONDED", "EXPIRED", "CANCELLED"}
FINAL_ROUTE_STATES = {"RESPONDED", "EXPIRED", "CANCELLED"}
PUSH_MODE = "EXTERNAL_BRIDGE"
FALLBACK_MODE = "POLL_REPOSITORY"
EARLY_SUPERVISION_AFTER_SECONDS = 120
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,191}$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)


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


def require_safe_id(name: str, value: str) -> str:
    value = str(value or "").strip()
    if not SAFE_ID.fullmatch(value):
        raise ValueError(f"CONTINUITY_BUS_FAILED: invalid {name}")
    return value


def require_exact_head(observed_head: str, current_head: str | None) -> None:
    if not SHA40.fullmatch(str(observed_head or "")):
        raise ValueError("CONTINUITY_BUS_FAILED: observed_head must be a 40-hex SHA")
    if not current_head or not SHA40.fullmatch(current_head):
        raise ValueError("CONTINUITY_BUS_FAILED: current repository HEAD unavailable")
    if observed_head != current_head:
        raise ValueError(f"HEAD_MOVED: observed={observed_head} current={current_head}")


def session_by_id(sessions_doc: dict, session_id: str) -> dict:
    session = next((x for x in sessions_doc.get("sessions", []) if x.get("session_id") == session_id), None)
    if not session:
        raise ValueError(f"CONTINUITY_BUS_FAILED: session not found: {session_id}")
    return session


def session_live(session: dict, timestamp: datetime) -> bool:
    relay = session.get("relay") or {}
    expiry = parse_time(relay.get("lease_expires_at"))
    return session.get("status") == "ACTIVE" and relay.get("state") == "ACTIVE" and expiry is not None and expiry > timestamp


def require_live_emitter(sessions_doc: dict, session_id: str, timestamp: datetime) -> dict:
    session = session_by_id(sessions_doc, session_id)
    if not session_live(session, timestamp):
        raise ValueError("CONTINUITY_BUS_FAILED: emitting session must have a fresh ACTIVE lease")
    return session


def continuity_item(state: dict, continuity_id: str) -> dict:
    item = next((x for x in state.get("items", []) if x.get("continuity_id") == continuity_id), None)
    if not item:
        raise ValueError("CONTINUITY_BUS_FAILED: continuity_id not found; declare shared scope first")
    if item.get("projection_only") is not True:
        raise ValueError("CONTINUITY_BUS_FAILED: continuity state must remain projection-only")
    item.setdefault("events", [])
    item.setdefault("last_sequence", 0)
    return item


def active_participant(item: dict, session_id: str, scope_id: str | None) -> dict | None:
    candidates = [p for p in item.get("participants", []) if p.get("session_id") == session_id and p.get("status") == "ACTIVE"]
    if scope_id:
        candidates = [p for p in candidates if p.get("scope_id") == scope_id]
    if len(candidates) > 1 and not scope_id:
        raise ValueError("CONTINUITY_BUS_FAILED: scope_id required because emitter has multiple active scopes")
    return candidates[0] if candidates else None


def continuity_member(item: dict, session_id: str) -> dict | None:
    return next((p for p in item.get("participants", []) if p.get("session_id") == session_id), None)


def make_event_id(continuity_id: str, sequence: int, from_session_id: str, created_at: str) -> str:
    raw = f"{continuity_id}|{sequence}|{from_session_id}|{created_at}".encode()
    return "GACR-E-" + hashlib.sha256(raw).hexdigest()[:16]


def make_dispatch_id(event_id: str, target_session_id: str) -> str:
    return "GACR-D-" + hashlib.sha256(f"{event_id}|{target_session_id}".encode()).hexdigest()[:16]


def make_supervision_alert_id(continuity_id: str, target_session_id: str, last_signal_at: str) -> str:
    raw = f"{continuity_id}|{target_session_id}|{last_signal_at}".encode()
    return "GACR-SA-" + hashlib.sha256(raw).hexdigest()[:16]


def make_supervision_dispatch_id(alert_id: str) -> str:
    return "GACR-D-" + hashlib.sha256(f"supervision|{alert_id}".encode()).hexdigest()[:16]


def session_signal_time(session: dict) -> datetime | None:
    relay = session.get("relay") or {}
    candidates = [parse_time(relay.get("last_heartbeat_at")), parse_time(session.get("last_seen_at"))]
    values = [x for x in candidates if x is not None]
    return max(values) if values else None


def normalize_targets(values: list[str]) -> list[str]:
    targets = sorted({str(x).strip() for x in values if str(x).strip()})
    if not targets:
        raise ValueError("CONTINUITY_BUS_FAILED: target_session_ids required")
    return targets


def normalize_domains(values: list[str] | None) -> list[str]:
    domains = sorted({str(x).strip() for x in (values or []) if str(x).strip()})
    if not domains:
        raise ValueError("CONTINUITY_BUS_FAILED: collision_domains required")
    for value in domains:
        require_safe_id("collision_domain", value)
    return domains


def delivery_choice(target: dict, timestamp: datetime) -> tuple[str, bool]:
    live = session_live(target, timestamp)
    channels = set(target.get("wake_channels") or [])
    if live and PUSH_MODE in channels and str(target.get("bridge_registration_ref") or "").strip():
        return PUSH_MODE, live
    return FALLBACK_MODE, live


def emit_event_docs(
    state: dict,
    sessions_doc: dict,
    dispatches_doc: dict,
    *,
    continuity_id: str,
    from_session_id: str,
    target_session_ids: list[str],
    event_kind: str,
    payload_ref: str,
    observed_head: str,
    current_head: str | None,
    evidence_ref: str,
    timestamp: datetime,
    scope_id: str | None = None,
    collision_domains: list[str] | None = None,
    requires_ack: bool = True,
    correlation_id: str | None = None,
    reply_to_event_id: str | None = None,
    expires_at: str | None = None,
    ack_timeout_seconds: int = 300,
) -> dict:
    continuity_id = require_safe_id("continuity_id", continuity_id)
    if event_kind not in EVENT_KINDS:
        raise ValueError("CONTINUITY_BUS_FAILED: unsupported event_kind")
    if not str(payload_ref or "").strip() or not str(evidence_ref or "").strip():
        raise ValueError("CONTINUITY_BUS_FAILED: payload_ref and evidence_ref required")
    if scope_id:
        scope_id = require_safe_id("scope_id", scope_id)
    domains = normalize_domains(collision_domains)
    require_exact_head(observed_head, current_head)
    require_live_emitter(sessions_doc, from_session_id, timestamp)

    item = continuity_item(state, continuity_id)
    participant = active_participant(item, from_session_id, scope_id)
    if participant is None:
        raise ValueError("CONTINUITY_BUS_FAILED: emitter must own an active declared continuity scope")
    if set(domains) - set(participant.get("collision_domains") or []):
        raise ValueError("CONTINUITY_BUS_FAILED: event collision domains exceed emitter declared scope")

    expiry = parse_time(expires_at) if expires_at else timestamp + timedelta(hours=4)
    if expiry is None or expiry <= timestamp:
        raise ValueError("CONTINUITY_BUS_FAILED: expires_at must be in the future")

    sequence = int(item.get("last_sequence") or 0) + 1
    created_at = iso(timestamp)
    eid = make_event_id(continuity_id, sequence, from_session_id, created_at)
    correlation = str(correlation_id or eid)
    routes = []

    for target_id in normalize_targets(target_session_ids):
        if continuity_member(item, target_id) is None:
            raise ValueError(f"TARGET_NOT_MEMBER_OF_CONTINUITY: {target_id}")
        target = session_by_id(sessions_doc, target_id)
        preferred, target_live = delivery_choice(target, timestamp)
        did = make_dispatch_id(eid, target_id)
        route_state = "ROUTED" if preferred == PUSH_MODE else "FALLBACK_POLL_REQUIRED"
        modes = [FALLBACK_MODE] if preferred == FALLBACK_MODE else [PUSH_MODE, FALLBACK_MODE]
        route = {
            "target_session_id": target_id,
            "dispatch_id": did,
            "preferred_delivery_mode": preferred,
            "delivery_modes": modes,
            "delivery_state": route_state,
            "target_live_at_route": target_live,
            "bridge_registration_ref": target.get("bridge_registration_ref"),
            "routed_at": created_at,
            "delivered_at": None,
            "ack_deadline_at": None,
            "acknowledged_at": None,
            "responded_at": None,
            "evidence_ref": None,
        }
        routes.append(route)
        dispatches_doc.setdefault("items", []).append({
            "dispatch_id": did,
            "dispatch_kind": "CONTINUITY_EVENT",
            "status": "READY" if preferred == PUSH_MODE else "FALLBACK_POLL_REQUIRED",
            "repository": item.get("repository"),
            "target_session_id": target_id,
            "target_client_instance_id": target.get("client_instance_id"),
            "bridge_registration_ref": target.get("bridge_registration_ref"),
            "delivery_modes": modes,
            "continuity_id": continuity_id,
            "continuity_event_id": eid,
            "continuity_sequence": sequence,
            "correlation_id": correlation,
            "reply_to_event_id": reply_to_event_id,
            "event_kind": event_kind,
            "payload_ref": str(payload_ref).strip(),
            "requires_ack": bool(requires_ack),
            "observed_head_sha": observed_head,
            "scope_id": scope_id,
            "collision_domains": domains,
            "created_at": created_at,
            "expires_at": iso(expiry),
            "idempotency_key": did,
            "projection_only": True,
            "grants_task_authority": False,
            "grants_claim": False,
            "grants_mutation_authority": False,
        })

    event = {
        "event_id": eid,
        "continuity_id": continuity_id,
        "sequence": sequence,
        "correlation_id": correlation,
        "reply_to_event_id": reply_to_event_id,
        "from_session_id": from_session_id,
        "target_session_ids": [r["target_session_id"] for r in routes],
        "event_kind": event_kind,
        "created_at": created_at,
        "expires_at": iso(expiry),
        "requires_ack": bool(requires_ack),
        "ack_timeout_seconds": int(ack_timeout_seconds),
        "observed_head_sha": observed_head,
        "scope_id": scope_id,
        "collision_domains": domains,
        "payload_ref": str(payload_ref).strip(),
        "provenance": str(evidence_ref).strip(),
        "state": "ROUTED" if any(r["preferred_delivery_mode"] == PUSH_MODE for r in routes) else "FALLBACK_POLL_REQUIRED",
        "routes": routes,
        "responses": [],
        "projection_only": True,
        "grants_task_authority": False,
        "grants_claim": False,
        "grants_mutation_authority": False,
    }
    item["events"].append(event)
    item["last_sequence"] = sequence
    item["updated_at"] = created_at
    state["revision"] = int(state.get("revision", 0)) + 1
    dispatches_doc["revision"] = int(dispatches_doc.get("revision", 0)) + 1
    return {"status": "CONTINUITY_EVENT_ROUTED", "event": event, "heartbeat_transferred": False, "grants_mutation_authority": False}


def event_by_id(state: dict, continuity_id: str, event_id: str) -> tuple[dict, dict]:
    item = continuity_item(state, continuity_id)
    event = next((x for x in item.get("events", []) if x.get("event_id") == event_id), None)
    if not event:
        raise ValueError("CONTINUITY_BUS_FAILED: event not found")
    return item, event


def route_for(event: dict, session_id: str) -> dict:
    route = next((x for x in event.get("routes", []) if x.get("target_session_id") == session_id), None)
    if not route:
        raise ValueError("CONTINUITY_BUS_FAILED: session is not an event target")
    return route


def mark_delivery_docs(state: dict, *, continuity_id: str, event_id: str, target_session_id: str, delivery_state: str, timestamp: datetime, evidence_ref: str | None = None) -> dict:
    _, event = event_by_id(state, continuity_id, event_id)
    route = route_for(event, target_session_id)
    if route.get("delivery_state") in FINAL_ROUTE_STATES:
        return {"status": "NOOP_FINAL_ROUTE"}
    route["delivery_state"] = delivery_state
    route["evidence_ref"] = evidence_ref or route.get("evidence_ref")
    if delivery_state == "DELIVERED":
        route["delivered_at"] = iso(timestamp)
        if event.get("requires_ack"):
            route["ack_deadline_at"] = iso(timestamp + timedelta(seconds=int(event.get("ack_timeout_seconds") or 300)))
    elif delivery_state == "FALLBACK_POLL_REQUIRED" and FALLBACK_MODE not in route.setdefault("delivery_modes", []):
        route["delivery_modes"].append(FALLBACK_MODE)
    states = {r.get("delivery_state") for r in event.get("routes", [])}
    if states and states <= {"DELIVERED", "ACKED", "RESPONDED"}:
        event["state"] = "DELIVERED"
    elif "FALLBACK_POLL_REQUIRED" in states:
        event["state"] = "FALLBACK_POLL_REQUIRED"
    state["revision"] = int(state.get("revision", 0)) + 1
    return {"status": "CONTINUITY_DELIVERY_UPDATED", "delivery_state": delivery_state}


def ack_event_docs(state: dict, sessions_doc: dict, *, continuity_id: str, event_id: str, session_id: str, observed_head: str, current_head: str | None, evidence_ref: str, timestamp: datetime) -> dict:
    require_exact_head(observed_head, current_head)
    require_live_emitter(sessions_doc, session_id, timestamp)
    _, event = event_by_id(state, continuity_id, event_id)
    route = route_for(event, session_id)
    if route.get("delivery_state") in FINAL_ROUTE_STATES:
        raise ValueError("CONTINUITY_BUS_FAILED: event route already final")
    route["delivery_state"] = "ACKED"
    route["acknowledged_at"] = iso(timestamp)
    route["evidence_ref"] = evidence_ref
    event.setdefault("responses", []).append({"kind": "ACK", "session_id": session_id, "created_at": iso(timestamp), "evidence_ref": evidence_ref})
    if {r.get("delivery_state") for r in event.get("routes", [])} <= {"ACKED", "RESPONDED"}:
        event["state"] = "ACKED"
    state["revision"] = int(state.get("revision", 0)) + 1
    return {"status": "CONTINUITY_EVENT_ACKED", "event_id": event_id, "session_id": session_id, "heartbeat_transferred": False}


def respond_event_docs(state: dict, sessions_doc: dict, *, continuity_id: str, event_id: str, session_id: str, response_ref: str, observed_head: str, current_head: str | None, evidence_ref: str, timestamp: datetime) -> dict:
    require_exact_head(observed_head, current_head)
    require_live_emitter(sessions_doc, session_id, timestamp)
    if not str(response_ref or "").strip():
        raise ValueError("CONTINUITY_BUS_FAILED: response_ref required")
    _, event = event_by_id(state, continuity_id, event_id)
    route = route_for(event, session_id)
    if route.get("delivery_state") in FINAL_ROUTE_STATES:
        raise ValueError("CONTINUITY_BUS_FAILED: event route already final")
    route["delivery_state"] = "RESPONDED"
    route["responded_at"] = iso(timestamp)
    route["evidence_ref"] = evidence_ref
    event.setdefault("responses", []).append({"kind": "RESPONSE", "session_id": session_id, "created_at": iso(timestamp), "response_ref": str(response_ref).strip(), "evidence_ref": evidence_ref})
    states = {r.get("delivery_state") for r in event.get("routes", [])}
    event["state"] = "RESPONDED" if states <= {"RESPONDED"} else "ACKED"
    state["revision"] = int(state.get("revision", 0)) + 1
    return {"status": "CONTINUITY_EVENT_RESPONDED", "event_id": event_id, "session_id": session_id, "heartbeat_transferred": False}


def mark_supervision_delivery_docs(
    state: dict,
    *,
    continuity_id: str,
    alert_id: str,
    delivery_state: str,
    timestamp: datetime,
    evidence_ref: str | None = None,
) -> dict:
    item = continuity_item(state, continuity_id)
    alert = next((x for x in item.get("supervision_alerts", []) if x.get("alert_id") == alert_id), None)
    if not alert:
        raise ValueError("CONTINUITY_BUS_FAILED: supervision alert not found")
    alert["delivery_state"] = delivery_state
    alert["delivery_evidence_ref"] = evidence_ref or alert.get("delivery_evidence_ref")
    if delivery_state == "DELIVERED":
        alert["delivered_at"] = iso(timestamp)
    elif delivery_state == "FALLBACK_POLL_REQUIRED":
        alert["fallback_at"] = iso(timestamp)
    state["revision"] = int(state.get("revision", 0)) + 1
    return {"status": "CONTINUITY_SUPERVISION_DELIVERY_UPDATED", "alert_id": alert_id, "delivery_state": delivery_state}


def reconcile_early_supervision_docs(
    state: dict,
    sessions_doc: dict,
    dispatches_doc: dict,
    *,
    timestamp: datetime,
    early_supervision_after_seconds: int = EARLY_SUPERVISION_AFTER_SECONDS,
) -> list[dict]:
    changes = []
    if early_supervision_after_seconds <= 0:
        raise ValueError("CONTINUITY_BUS_FAILED: early supervision threshold must be positive")
    session_index = {s.get("session_id"): s for s in sessions_doc.get("sessions", []) if s.get("session_id")}

    for item in state.get("items", []):
        alerts = item.setdefault("supervision_alerts", [])
        for participant in item.get("participants", []):
            if participant.get("status") != "ACTIVE":
                continue
            target_id = participant.get("session_id")
            session = session_index.get(target_id)
            if not session:
                continue

            open_alert = next((a for a in alerts if a.get("target_session_id") == target_id and a.get("state") == "OPEN"), None)
            relay = session.get("relay") or {}
            canonical_active = session.get("status") == "ACTIVE" and relay.get("state") == "ACTIVE"
            last_signal = session_signal_time(session)

            if not canonical_active:
                if open_alert:
                    open_alert["state"] = "SUPERSEDED_BY_CANONICAL_LIVENESS_STATE"
                    open_alert["resolved_at"] = iso(timestamp)
                    open_alert["resolution"] = "CANONICAL_GACR_STATE_OWNS_RECOVERY"
                    for dispatch in dispatches_doc.get("items", []):
                        if dispatch.get("supervision_alert_id") == open_alert.get("alert_id") and dispatch.get("status") not in {"DELIVERED", "RESOLVED", "CANCELLED"}:
                            dispatch["status"] = "CANCELLED"
                    changes.append({"alert_id": open_alert.get("alert_id"), "target_session_id": target_id, "state": open_alert["state"]})
                continue

            if last_signal is None:
                continue
            silence_seconds = max(0, int((timestamp - last_signal).total_seconds()))

            if silence_seconds <= early_supervision_after_seconds:
                if open_alert and last_signal > parse_time(open_alert.get("detected_at")):
                    open_alert["state"] = "RESOLVED"
                    open_alert["resolved_at"] = iso(timestamp)
                    open_alert["resolution"] = "FRESH_SESSION_SIGNAL_OBSERVED"
                    for dispatch in dispatches_doc.get("items", []):
                        if dispatch.get("supervision_alert_id") == open_alert.get("alert_id") and dispatch.get("status") not in {"DELIVERED", "RESOLVED", "CANCELLED"}:
                            dispatch["status"] = "RESOLVED"
                    changes.append({"alert_id": open_alert.get("alert_id"), "target_session_id": target_id, "state": "RESOLVED"})
                continue

            if open_alert:
                continue

            preferred, target_live = delivery_choice(session, timestamp)
            alert_id = make_supervision_alert_id(item["continuity_id"], target_id, iso(last_signal))
            dispatch_id = make_supervision_dispatch_id(alert_id)
            delivery_modes = [FALLBACK_MODE] if preferred == FALLBACK_MODE else [PUSH_MODE, FALLBACK_MODE]
            dispatch_status = "READY" if preferred == PUSH_MODE else "FALLBACK_POLL_REQUIRED"
            alert = {
                "alert_id": alert_id,
                "target_session_id": target_id,
                "participant_id": participant.get("participant_id"),
                "scope_id": participant.get("scope_id"),
                "detected_at": iso(timestamp),
                "last_signal_at": iso(last_signal),
                "silence_seconds_at_detection": silence_seconds,
                "threshold_seconds": int(early_supervision_after_seconds),
                "canonical_lease_expires_at": relay.get("lease_expires_at"),
                "state": "OPEN",
                "action": "EARLY_SUPERVISION_ALERT",
                "dispatch_id": dispatch_id,
                "preferred_delivery_mode": preferred,
                "delivery_modes": delivery_modes,
                "delivery_state": dispatch_status,
                "target_live_at_detection": target_live,
                "projection_only": True,
                "changes_session_status": False,
                "changes_lease": False,
                "grants_task_authority": False,
                "grants_claim": False,
                "grants_mutation_authority": False,
            }
            alerts.append(alert)
            dispatches_doc.setdefault("items", []).append({
                "dispatch_id": dispatch_id,
                "dispatch_kind": "CONTINUITY_SUPERVISION_ALERT",
                "status": dispatch_status,
                "repository": item.get("repository"),
                "target_session_id": target_id,
                "target_client_instance_id": session.get("client_instance_id"),
                "bridge_registration_ref": session.get("bridge_registration_ref"),
                "delivery_modes": delivery_modes,
                "continuity_id": item.get("continuity_id"),
                "supervision_alert_id": alert_id,
                "scope_id": participant.get("scope_id"),
                "payload_ref": f"continuity:{item.get('continuity_id')}:supervision:{alert_id}",
                "created_at": iso(timestamp),
                "expires_at": relay.get("lease_expires_at"),
                "idempotency_key": dispatch_id,
                "projection_only": True,
                "changes_session_status": False,
                "changes_lease": False,
                "grants_task_authority": False,
                "grants_claim": False,
                "grants_mutation_authority": False,
            })
            changes.append({"alert_id": alert_id, "target_session_id": target_id, "state": "EARLY_SUPERVISION_ALERT", "delivery_mode": preferred})
    return changes


def tick_docs(
    state: dict,
    sessions_doc: dict,
    dispatches_doc: dict,
    *,
    timestamp: datetime,
    early_supervision_after_seconds: int = EARLY_SUPERVISION_AFTER_SECONDS,
) -> dict:
    changes = reconcile_early_supervision_docs(
        state,
        sessions_doc,
        dispatches_doc,
        timestamp=timestamp,
        early_supervision_after_seconds=early_supervision_after_seconds,
    )
    for item in state.get("items", []):
        for event in item.get("events", []):
            if event.get("state") in FINAL_EVENT_STATES:
                continue
            expiry = parse_time(event.get("expires_at"))
            if expiry and timestamp >= expiry:
                event["state"] = "EXPIRED"
                for route in event.get("routes", []):
                    if route.get("delivery_state") not in FINAL_ROUTE_STATES:
                        route["delivery_state"] = "EXPIRED"
                for dispatch in dispatches_doc.get("items", []):
                    if dispatch.get("continuity_event_id") == event.get("event_id") and dispatch.get("status") not in {"DELIVERED", "ACKED", "RESPONDED"}:
                        dispatch["status"] = "EXPIRED"
                changes.append({"event_id": event.get("event_id"), "state": "EXPIRED"})
                continue
            for route in event.get("routes", []):
                if route.get("delivery_state") != "DELIVERED" or not event.get("requires_ack"):
                    continue
                deadline = parse_time(route.get("ack_deadline_at"))
                if deadline and timestamp >= deadline:
                    route["delivery_state"] = "ACK_TIMEOUT"
                    if FALLBACK_MODE not in route.setdefault("delivery_modes", []):
                        route["delivery_modes"].append(FALLBACK_MODE)
                    event["state"] = "ACK_TIMEOUT"
                    for dispatch in dispatches_doc.get("items", []):
                        if dispatch.get("dispatch_id") == route.get("dispatch_id"):
                            dispatch["status"] = "ACK_TIMEOUT"
                            dispatch["fallback_mode"] = FALLBACK_MODE
                    changes.append({"event_id": event.get("event_id"), "target_session_id": route.get("target_session_id"), "state": "ACK_TIMEOUT"})
    if changes:
        state["revision"] = int(state.get("revision", 0)) + 1
        dispatches_doc["revision"] = int(dispatches_doc.get("revision", 0)) + 1
    return {"status": "CONTINUITY_LOOP_TICK", "changes": changes}


def load_runtime() -> tuple[dict, dict, dict]:
    return (
        read_json(STATE_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []}),
        read_json(SESSIONS_PATH, {"sessions": []}),
        read_json(DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []}),
    )


def save_runtime(state: dict, dispatches: dict) -> None:
    write_json(STATE_PATH, state)
    write_json(DISPATCHES_PATH, dispatches)


def command_emit(a):
    state, sessions, dispatches = load_runtime()
    result = emit_event_docs(state, sessions, dispatches, continuity_id=a.continuity_id, from_session_id=a.from_session_id, target_session_ids=a.target_session_id, event_kind=a.event_kind, payload_ref=a.payload_ref, observed_head=a.observed_head, current_head=git_head(), evidence_ref=a.evidence_ref, timestamp=now_utc(), scope_id=a.scope_id, collision_domains=a.collision_domain, requires_ack=a.requires_ack, correlation_id=a.correlation_id, reply_to_event_id=a.reply_to_event_id, expires_at=a.expires_at, ack_timeout_seconds=a.ack_timeout_seconds)
    save_runtime(state, dispatches)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_ack(a):
    state, sessions, dispatches = load_runtime()
    result = ack_event_docs(state, sessions, continuity_id=a.continuity_id, event_id=a.event_id, session_id=a.session_id, observed_head=a.observed_head, current_head=git_head(), evidence_ref=a.evidence_ref, timestamp=now_utc())
    save_runtime(state, dispatches)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_respond(a):
    state, sessions, dispatches = load_runtime()
    result = respond_event_docs(state, sessions, continuity_id=a.continuity_id, event_id=a.event_id, session_id=a.session_id, response_ref=a.response_ref, observed_head=a.observed_head, current_head=git_head(), evidence_ref=a.evidence_ref, timestamp=now_utc())
    save_runtime(state, dispatches)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_tick(a):
    state, sessions, dispatches = load_runtime()
    result = tick_docs(
        state,
        sessions,
        dispatches,
        timestamp=now_utc(),
        early_supervision_after_seconds=a.early_supervision_after_seconds,
    )
    save_runtime(state, dispatches)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_status(a):
    state, _, dispatches = load_runtime()
    item = next((x for x in state.get("items", []) if x.get("continuity_id") == a.continuity_id), None)
    event = next((x for x in (item or {}).get("events", []) if x.get("event_id") == a.event_id), None) if a.event_id else None
    print(json.dumps({"status": "FOUND" if item else "NOT_FOUND", "continuity": item if not a.event_id else None, "event": event, "dispatches": [d for d in dispatches.get("items", []) if d.get("continuity_id") == a.continuity_id and (not a.event_id or d.get("continuity_event_id") == a.event_id)], "projection_only": True, "grants_mutation_authority": False}, indent=2, ensure_ascii=False))


def parser():
    p = argparse.ArgumentParser(description="Push-first derived GACR continuity bus")
    sub = p.add_subparsers(dest="command", required=True)
    emit = sub.add_parser("emit")
    emit.add_argument("--continuity-id", required=True)
    emit.add_argument("--from-session-id", required=True)
    emit.add_argument("--target-session-id", action="append", required=True)
    emit.add_argument("--event-kind", choices=sorted(EVENT_KINDS), required=True)
    emit.add_argument("--payload-ref", required=True)
    emit.add_argument("--observed-head", required=True)
    emit.add_argument("--evidence-ref", required=True)
    emit.add_argument("--scope-id")
    emit.add_argument("--collision-domain", action="append", required=True)
    emit.add_argument("--correlation-id")
    emit.add_argument("--reply-to-event-id")
    emit.add_argument("--expires-at")
    emit.add_argument("--ack-timeout-seconds", type=int, default=300)
    emit.add_argument("--requires-ack", action=argparse.BooleanOptionalAction, default=True)
    emit.set_defaults(fn=command_emit)
    ack = sub.add_parser("ack")
    ack.add_argument("--continuity-id", required=True)
    ack.add_argument("--event-id", required=True)
    ack.add_argument("--session-id", required=True)
    ack.add_argument("--observed-head", required=True)
    ack.add_argument("--evidence-ref", required=True)
    ack.set_defaults(fn=command_ack)
    respond = sub.add_parser("respond")
    respond.add_argument("--continuity-id", required=True)
    respond.add_argument("--event-id", required=True)
    respond.add_argument("--session-id", required=True)
    respond.add_argument("--response-ref", required=True)
    respond.add_argument("--observed-head", required=True)
    respond.add_argument("--evidence-ref", required=True)
    respond.set_defaults(fn=command_respond)
    tick = sub.add_parser("tick")
    tick.add_argument("--early-supervision-after-seconds", type=int, default=EARLY_SUPERVISION_AFTER_SECONDS)
    tick.set_defaults(fn=command_tick)
    status = sub.add_parser("status")
    status.add_argument("--continuity-id", required=True)
    status.add_argument("--event-id")
    status.set_defaults(fn=command_status)
    return p


def main():
    a = parser().parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
