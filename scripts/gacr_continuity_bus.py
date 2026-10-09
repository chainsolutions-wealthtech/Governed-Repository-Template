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

from gacr_continuity_coordination import resolve_logical_agent_alias_docs

ROOT = Path(os.environ.get("GACR_ROOT") or Path(__file__).resolve().parents[1]).resolve()
GOV = ROOT / ".governance"
TEMPLATE_SOURCE = (ROOT / ".template-source").exists()
CONFIG_PATH = GOV / "agent-relay" / "config.json"

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
FINAL_EVENT_STATES = {"ACKED", "RESPONDED", "EXPIRED", "CANCELLED"}
FINAL_ROUTE_STATES = {"RESPONDED", "EXPIRED", "CANCELLED"}
NON_REGRESSIBLE_ROUTE_STATES = {"ACKED", "RESPONDED", "EXPIRED", "CANCELLED"}
CONTROL_MODE = "GSCC_CONTROL_CHANNEL"
PUSH_MODE = "EXTERNAL_BRIDGE"
FALLBACK_MODE = "POLL_REPOSITORY"
CONTROL_REQUIRED_CAPABILITIES = {"COMMAND_RECEIVE", "COMMAND_ACK"}
CONTROL_EVIDENCE_FRESHNESS_SECONDS = 900
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


def canonical_control_evidence_for_session(
    dispatches_doc: dict,
    session_id: str,
    timestamp: datetime,
    *,
    freshness_seconds: int = CONTROL_EVIDENCE_FRESHNESS_SECONDS,
) -> dict:
    candidates = []
    for item in dispatches_doc.get("items", []):
        if not isinstance(item, dict) or item.get("target_session_id") != session_id:
            continue
        command = item.get("command") or {}
        if command.get("command_type") != "LIVENESS_CHALLENGE":
            continue
        if item.get("status") != "COMPLETED":
            continue
        ack = item.get("ack") or {}
        response = item.get("response") or {}
        if ack.get("delivery_state") != "ACKNOWLEDGED" or response.get("fresh_liveness") is not True:
            continue
        observed = parse_time(response.get("observed_at"))
        if observed is None or (timestamp - observed).total_seconds() > int(freshness_seconds):
            continue
        candidates.append(item)
    candidates.sort(key=lambda item: ((item.get("response") or {}).get("observed_at") or "", item.get("dispatch_id") or ""))
    if not candidates:
        return {
            "status": "UNAVAILABLE",
            "session_reachability": "UNVERIFIED",
            "evidence_ref": None,
            "dispatch_id": None,
        }
    item = candidates[-1]
    response = item.get("response") or {}
    return {
        "status": "VERIFIED",
        "session_reachability": "VERIFIED",
        "evidence_ref": response.get("evidence_ref"),
        "dispatch_id": item.get("dispatch_id"),
        "observed_at": response.get("observed_at"),
    }


def control_channel_route_evidence(
    target: dict,
    dispatches_doc: dict,
    config: dict | None,
    timestamp: datetime,
) -> dict:
    config = config or {}
    host_bridge = config.get("host_issue_bridge") or {}
    control = host_bridge.get("control_channel") or {}
    external_bridge = config.get("external_bridge") or {}
    declared = set(target.get("capabilities") or [])
    transport_proven = (
        target.get("provider") == "chatgpt"
        and bool(host_bridge.get("enabled"))
        and bool(control.get("enabled"))
        and bool(external_bridge.get("chatgpt_issue_bridge_live_proven"))
    )
    capability_ready = CONTROL_REQUIRED_CAPABILITIES <= declared
    session_evidence = canonical_control_evidence_for_session(dispatches_doc, str(target.get("session_id") or ""), timestamp)
    return {
        "status": "AVAILABLE" if transport_proven and capability_ready else "UNAVAILABLE",
        "transport_proven": transport_proven,
        "declared_capabilities_sufficient": capability_ready,
        "required_capabilities": sorted(CONTROL_REQUIRED_CAPABILITIES),
        "session_reachability": session_evidence.get("session_reachability"),
        "session_evidence_ref": session_evidence.get("evidence_ref"),
        "session_dispatch_id": session_evidence.get("dispatch_id"),
        "provenance": "GACR_HOST_ISSUE_BRIDGE_LIVE_PROOF" if transport_proven else "UNAVAILABLE",
        "provider_private_endpoint": False,
    }


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


def derive_liveness_state(
    session: dict,
    timestamp: datetime,
    *,
    quiet_after_seconds: int = EARLY_SUPERVISION_AFTER_SECONDS,
) -> str:
    relay = session.get("relay") or {}
    status = str(session.get("status") or "UNKNOWN")
    relay_state = str(relay.get("state") or "UNKNOWN")
    if status == "CLOSED" or relay_state == "CLOSED":
        return "UNREACHABLE"
    if status == "STALLED" or relay_state in {"STALLED", "TAKEOVER_READY", "HANDOFF_STALLED"}:
        return "STALLED"
    if status == "SUSPECTED_STALL" or relay_state == "SUSPECTED_STALL":
        return "SUSPECTED_STALL"
    if status == "STANDBY" or relay_state == "STANDBY":
        return "QUIET"
    expiry = parse_time(relay.get("lease_expires_at"))
    if status == "ACTIVE" and relay_state == "ACTIVE" and expiry is not None and expiry <= timestamp:
        return "STALLED"
    if status == "ACTIVE" and relay_state == "ACTIVE":
        signal = session_signal_time(session)
        if signal is None:
            return "UNKNOWN"
        return "LIVE" if (timestamp - signal).total_seconds() <= quiet_after_seconds else "QUIET"
    return "UNKNOWN"


def provider_endpoint_descriptor(session: dict, config: dict | None = None) -> dict:
    config = config or {}
    provider = str(session.get("provider") or "other")
    provider_ref = session.get("provider_conversation_ref")
    wake_channels = sorted(set(session.get("wake_channels") or []))
    bridge_ref = session.get("bridge_registration_ref")
    external_bridge = config.get("external_bridge") or {}
    host_bridge = config.get("host_issue_bridge") or {}

    push_capable = "EXTERNAL_BRIDGE" in wake_channels and bool(str(bridge_ref or "").strip())
    if push_capable:
        inbound = {
            "status": "OBSERVED",
            "kind": "EXTERNAL_BRIDGE",
            "endpoint_ref": bridge_ref,
            "provenance": "SESSION_REGISTRATION",
            "reason": None,
        }
    else:
        inbound = {
            "status": "UNAVAILABLE",
            "kind": None,
            "endpoint_ref": None,
            "provenance": "PROVIDER_PRIVATE_UNAVAILABLE",
            "reason": "NO_REGISTERED_PROVIDER_INBOUND_ENDPOINT",
        }

    repository_control = {
        "status": "AVAILABLE",
        "kind": "POLL_REPOSITORY",
        "endpoint_ref": None,
        "provenance": "GACR_CANONICAL_FALLBACK",
    }
    control_cfg = host_bridge.get("control_channel") or {}
    control_capable = False
    if provider == "chatgpt" and external_bridge.get("chatgpt_issue_bridge_live_proven") and host_bridge.get("enabled"):
        issue_number = host_bridge.get("issue_number")
        repository_control = {
            "status": "PROVEN",
            "kind": "GITHUB_ISSUE_CONTROL_CHANNEL",
            "endpoint_ref": f"issue:{issue_number}" if issue_number else None,
            "provenance": "GACR_HOST_ISSUE_BRIDGE_LIVE_PROOF",
        }
        control_capable = bool(control_cfg.get("enabled")) and CONTROL_REQUIRED_CAPABILITIES <= set(session.get("capabilities") or [])

    return {
        "provider": provider,
        "provider_conversation_ref_status": "PRESENT" if provider_ref else "UNAVAILABLE",
        "provider_conversation_ref": provider_ref if provider_ref else None,
        "provider_inbound_endpoint": inbound,
        "repository_control_surface": repository_control,
        "wake_route": {
            "preferred": CONTROL_MODE if control_capable else "EXTERNAL_BRIDGE" if push_capable else "POLL_REPOSITORY",
            "push_capable": bool(control_capable or push_capable),
            "wake_channels": wake_channels,
            "control_capable": control_capable,
        },
        "connection_ref": session.get("connection_ref"),
        "bridge_registration_ref": bridge_ref,
        "provider_private_values_invented": False,
    }


def _provider_context_projection_id(session_id: str, connection_ref: str | None, provider_ref: str | None, client_instance_id: str | None) -> str:
    raw = json.dumps(
        {
            "session_id": session_id,
            "connection_ref": connection_ref or None,
            "provider_conversation_ref": provider_ref or None,
            "client_instance_id": client_instance_id or None,
        },
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    )
    return "GACR-PC-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def provider_context_descriptor(session: dict) -> dict:
    envelope = session.get("connection_envelope") or {}
    fields = envelope.get("fields") or {}
    def field_value(name: str):
        value = (fields.get(name) or {}).get("value")
        return None if value in {None, "", "UNAVAILABLE"} else value
    provider = str(session.get("provider") or "other")
    provider_ref = session.get("provider_conversation_ref")
    connection_ref = session.get("connection_ref")
    client_instance_id = session.get("client_instance_id")
    context_id = _provider_context_projection_id(str(session.get("session_id") or ""), connection_ref, provider_ref, client_instance_id)
    repository_surface_ref = field_value("github_app_or_installation")
    runtime_surface_ref = connection_ref if str(connection_ref or "").startswith("GRT-SURFACE-") else None
    return {
        "provider_context_id": context_id,
        "provider_context_id_provenance": "DERIVED_GACR_PROJECTION",
        "session_id": session.get("session_id"),
        "provider": provider,
        "provider_conversation_ref": provider_ref if provider_ref else None,
        "provider_conversation_ref_status": "PRESENT" if provider_ref else "UNAVAILABLE",
        "client_instance_id": client_instance_id,
        "connection_ref": connection_ref,
        "runtime_surface_ref": runtime_surface_ref,
        "runtime_surface_ref_provenance": "REPOSITORY_MINTED" if runtime_surface_ref else None,
        "repository_surface_ref": repository_surface_ref,
        "repository_surface_ref_provenance": (fields.get("github_app_or_installation") or {}).get("provenance") if repository_surface_ref else None,
        "provider_connector_app_id": field_value("provider_connector_app_id"),
        "provider_connector_client_id": field_value("provider_connector_client_id"),
        "provider_connector_installation_id": field_value("provider_connector_installation_id"),
        "provider_connector_slug": field_value("provider_connector_slug"),
        "provider_native_identity_status": "PRESENT" if provider_ref else "UNAVAILABLE",
        "provider_private_values_invented": False,
    }


def provider_context_descriptors(session: dict) -> list[dict]:
    projected = provider_context_descriptor(session)
    contexts: dict[str, dict] = {}
    for item in session.get("provider_contexts") or []:
        if not isinstance(item, dict) or not item.get("provider_context_id"):
            continue
        value = dict(item)
        value["session_id"] = session.get("session_id")
        value["provider_private_values_invented"] = False
        contexts[value["provider_context_id"]] = value
    if projected["provider_context_id"] in contexts:
        merged = dict(projected)
        merged.update(contexts[projected["provider_context_id"]])
        contexts[projected["provider_context_id"]] = merged
    else:
        contexts[projected["provider_context_id"]] = projected
    return [contexts[key] for key in sorted(contexts)]

def project_logical_agents_docs(state: dict, sessions_doc: dict) -> list[dict]:
    changes = []
    session_index = {s.get("session_id"): s for s in sessions_doc.get("sessions", []) if s.get("session_id")}
    sessions_by_logical_agent: dict[str, list[dict]] = {}
    for session in sessions_doc.get("sessions", []):
        logical_agent_id = session.get("logical_agent_id") or session.get("agent_identity")
        if logical_agent_id:
            sessions_by_logical_agent.setdefault(str(logical_agent_id), []).append(session)

    for item in state.get("items", []):
        groups: dict[str, dict] = {}

        # Owner aliases are durable logical-agent metadata in the existing
        # continuity projection. Preserve them even with zero active participants.
        for existing in item.get("logical_agents") or []:
            if (
                existing.get("human_alias")
                and existing.get("human_alias_provenance") == "OWNER_ASSIGNED"
                and existing.get("logical_agent_id")
            ):
                logical_agent_id = str(existing["logical_agent_id"])
                groups[logical_agent_id] = {
                    "logical_agent_id": logical_agent_id,
                    "logical_agent_id_provenance": (
                        existing.get("logical_agent_id_provenance")
                        or "CANONICAL_GACR_SESSION_AGENT_IDENTITY"
                    ),
                    "human_alias": existing.get("human_alias"),
                    "human_alias_provenance": "OWNER_ASSIGNED",
                    "alias_evidence_ref": existing.get("alias_evidence_ref"),
                    "routing_evidence_ref": existing.get("routing_evidence_ref"),
                    "reference_session_ids": sorted({
                        str(x) for x in (existing.get("reference_session_ids") or [])
                        if str(x).strip()
                    }),
                    "session_ids": [],
                    "participant_ids": [],
                    "scope_ids": [],
                    "provider_contexts": [],
                    "projection_only": True,
                    "grants_task_authority": False,
                    "grants_claim": False,
                    "grants_mutation_authority": False,
                }

        for participant in item.get("participants", []):
            session = session_index.get(participant.get("session_id"))
            logical_agent_id = (
                (session or {}).get("logical_agent_id")
                or (session or {}).get("agent_identity")
            )
            if logical_agent_id:
                participant["logical_agent_id"] = logical_agent_id
                participant["logical_agent_id_provenance"] = "CANONICAL_GACR_SESSION_AGENT_IDENTITY"
            else:
                participant["logical_agent_id"] = "UNAVAILABLE"
                participant["logical_agent_id_provenance"] = "CANONICAL_GACR_AGENT_IDENTITY_UNAVAILABLE"
            contexts = provider_context_descriptors(session) if session else []
            participant["provider_contexts"] = contexts
            if not logical_agent_id:
                continue
            logical_agent_id = str(logical_agent_id)
            group = groups.setdefault(logical_agent_id, {
                "logical_agent_id": logical_agent_id,
                "logical_agent_id_provenance": "CANONICAL_GACR_SESSION_AGENT_IDENTITY",
                "session_ids": [],
                "participant_ids": [],
                "scope_ids": [],
                "provider_contexts": [],
                "projection_only": True,
                "grants_task_authority": False,
                "grants_claim": False,
                "grants_mutation_authority": False,
            })
            group["session_ids"].append(participant.get("session_id"))
            group["participant_ids"].append(participant.get("participant_id"))
            group["scope_ids"].append(participant.get("scope_id"))
            group["provider_contexts"].extend(contexts)

        # Once an owner alias identifies a logical agent, reconstruct all of its
        # canonical sessions/provider contexts on cold start without promoting
        # those sessions to continuity participants or granting authority.
        for logical_agent_id, group in groups.items():
            if group.get("human_alias_provenance") != "OWNER_ASSIGNED":
                continue
            for session in sessions_by_logical_agent.get(logical_agent_id, []):
                group["session_ids"].append(session.get("session_id"))
                group["provider_contexts"].extend(provider_context_descriptors(session))

        projected = []
        for logical_agent_id in sorted(groups):
            group = groups[logical_agent_id]
            group["session_ids"] = sorted({x for x in group["session_ids"] if x})
            group["participant_ids"] = sorted({x for x in group["participant_ids"] if x})
            group["scope_ids"] = sorted({x for x in group["scope_ids"] if x})
            dedup = {}
            for context in group["provider_contexts"]:
                if context.get("provider_context_id"):
                    dedup[context["provider_context_id"]] = context
            group["provider_contexts"] = [dedup[key] for key in sorted(dedup)]
            group["session_count"] = len(group["session_ids"])
            group["provider_context_count"] = len(group["provider_contexts"])
            projected.append(group)
        if item.get("logical_agents") != projected:
            item["logical_agents"] = projected
            changes.append({
                "continuity_id": item.get("continuity_id"),
                "state": "LOGICAL_AGENT_PROJECTION_UPDATED",
                "logical_agent_count": len(projected),
            })
    return changes


def project_participant_runtime_docs(
    state: dict,
    sessions_doc: dict,
    *,
    timestamp: datetime,
    config: dict | None = None,
    quiet_after_seconds: int = EARLY_SUPERVISION_AFTER_SECONDS,
) -> list[dict]:
    changes = []
    session_index = {s.get("session_id"): s for s in sessions_doc.get("sessions", []) if s.get("session_id")}
    for item in state.get("items", []):
        for participant in item.get("participants", []):
            session = session_index.get(participant.get("session_id"))
            participant["membership_state"] = "PERSISTENT"
            if not session:
                projection = {
                    "liveness_state": "UNKNOWN",
                    "canonical_session_status": "UNAVAILABLE",
                    "canonical_relay_state": "UNAVAILABLE",
                    "lease_expires_at": None,
                    "last_signal_at": None,
                    "logical_agent_id": participant.get("logical_agent_id") or "UNAVAILABLE",
                    "logical_agent_id_provenance": "CANONICAL_SESSION_NOT_FOUND",
                    "provider_contexts": [],
                    "provider_endpoint": {
                        "provider": "other",
                        "provider_conversation_ref_status": "UNAVAILABLE",
                        "provider_conversation_ref": None,
                        "provider_inbound_endpoint": {
                            "status": "UNAVAILABLE",
                            "kind": None,
                            "endpoint_ref": None,
                            "provenance": "PROVIDER_PRIVATE_UNAVAILABLE",
                            "reason": "CANONICAL_SESSION_NOT_FOUND",
                        },
                        "repository_control_surface": {
                            "status": "AVAILABLE",
                            "kind": "POLL_REPOSITORY",
                            "endpoint_ref": None,
                            "provenance": "GACR_CANONICAL_FALLBACK",
                        },
                        "wake_route": {
                            "preferred": "POLL_REPOSITORY",
                            "push_capable": False,
                            "wake_channels": [],
                        },
                        "connection_ref": None,
                        "bridge_registration_ref": None,
                        "provider_private_values_invented": False,
                    },
                }
            else:
                relay = session.get("relay") or {}
                signal = session_signal_time(session)
                projection = {
                    "logical_agent_id": session.get("agent_identity") or "UNAVAILABLE",
                    "logical_agent_id_provenance": (
                        "CANONICAL_GACR_SESSION_AGENT_IDENTITY"
                        if session.get("agent_identity") else "CANONICAL_GACR_AGENT_IDENTITY_UNAVAILABLE"
                    ),
                    "provider_contexts": provider_context_descriptors(session),
                    "liveness_state": derive_liveness_state(session, timestamp, quiet_after_seconds=quiet_after_seconds),
                    "canonical_session_status": session.get("status"),
                    "canonical_relay_state": relay.get("state"),
                    "lease_expires_at": relay.get("lease_expires_at"),
                    "last_signal_at": iso(signal) if signal else None,
                    "provider_endpoint": provider_endpoint_descriptor(session, config),
                }

            changed = False
            for key, value in projection.items():
                if participant.get(key) != value:
                    participant[key] = value
                    changed = True
            if changed:
                participant["runtime_projection_observed_at"] = iso(timestamp)
                changes.append({
                    "participant_id": participant.get("participant_id"),
                    "session_id": participant.get("session_id"),
                    "logical_agent_id": participant.get("logical_agent_id"),
                    "state": "PARTICIPANT_RUNTIME_PROJECTED",
                    "membership_state": "PERSISTENT",
                    "liveness_state": participant.get("liveness_state"),
                    "provider_endpoint_status": (participant.get("provider_endpoint") or {}).get("provider_inbound_endpoint", {}).get("status"),
                })
    changes.extend(project_logical_agents_docs(state, sessions_doc))
    return changes


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


def delivery_choice(
    target: dict,
    timestamp: datetime,
    dispatches_doc: dict | None = None,
    config: dict | None = None,
) -> tuple[str, bool, dict]:
    live = session_live(target, timestamp)
    control_evidence = control_channel_route_evidence(target, dispatches_doc or {}, config, timestamp)
    if live and control_evidence.get("status") == "AVAILABLE":
        return CONTROL_MODE, live, control_evidence
    channels = set(target.get("wake_channels") or [])
    if live and PUSH_MODE in channels and str(target.get("bridge_registration_ref") or "").strip():
        return PUSH_MODE, live, control_evidence
    return FALLBACK_MODE, live, control_evidence


def delivery_modes_for(preferred: str, target: dict) -> list[str]:
    if preferred == CONTROL_MODE:
        modes = [CONTROL_MODE]
        if "EXTERNAL_BRIDGE" in set(target.get("wake_channels") or []) and str(target.get("bridge_registration_ref") or "").strip():
            modes.append(PUSH_MODE)
        modes.append(FALLBACK_MODE)
        return modes
    if preferred == PUSH_MODE:
        return [PUSH_MODE, FALLBACK_MODE]
    return [FALLBACK_MODE]


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
    config: dict | None = None,
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
        preferred, target_live, control_evidence = delivery_choice(target, timestamp, dispatches_doc, config)
        did = make_dispatch_id(eid, target_id)
        route_state = "FALLBACK_POLL_REQUIRED" if preferred == FALLBACK_MODE else "ROUTED"
        modes = delivery_modes_for(preferred, target)
        route = {
            "target_session_id": target_id,
            "dispatch_id": did,
            "preferred_delivery_mode": preferred,
            "delivery_modes": modes,
            "delivery_state": route_state,
            "target_live_at_route": target_live,
            "bridge_registration_ref": target.get("bridge_registration_ref"),
            "control_evidence": control_evidence,
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
            "status": "READY" if preferred != FALLBACK_MODE else "FALLBACK_POLL_REQUIRED",
            "repository": item.get("repository"),
            "preferred_delivery_mode": preferred,
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
        "state": "ROUTED" if any(r["preferred_delivery_mode"] != FALLBACK_MODE for r in routes) else "FALLBACK_POLL_REQUIRED",
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
    config: dict | None = None,
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
            lease_expiry = parse_time(relay.get("lease_expires_at"))
            canonical_active = (
                session.get("status") == "ACTIVE"
                and relay.get("state") == "ACTIVE"
                and lease_expiry is not None
                and lease_expiry > timestamp
            )
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

            if open_alert:
                alert_signal = parse_time(open_alert.get("last_signal_at"))
                if alert_signal is not None and last_signal > alert_signal:
                    open_alert["state"] = "RESOLVED"
                    open_alert["resolved_at"] = iso(timestamp)
                    open_alert["resolution"] = "FRESH_SESSION_SIGNAL_OBSERVED"
                    for dispatch in dispatches_doc.get("items", []):
                        if dispatch.get("supervision_alert_id") == open_alert.get("alert_id") and dispatch.get("status") not in {"DELIVERED", "RESOLVED", "CANCELLED"}:
                            dispatch["status"] = "RESOLVED"
                    changes.append({"alert_id": open_alert.get("alert_id"), "target_session_id": target_id, "state": "RESOLVED"})
                    open_alert = None

            silence_seconds = max(0, int((timestamp - last_signal).total_seconds()))

            if silence_seconds <= early_supervision_after_seconds:
                continue

            if open_alert:
                continue

            preferred, target_live, control_evidence = delivery_choice(session, timestamp, dispatches_doc, config)
            alert_id = make_supervision_alert_id(item["continuity_id"], target_id, iso(last_signal))
            dispatch_id = make_supervision_dispatch_id(alert_id)
            delivery_modes = delivery_modes_for(preferred, session)
            dispatch_status = "READY" if preferred != FALLBACK_MODE else "FALLBACK_POLL_REQUIRED"
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
                "control_evidence": control_evidence,
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
                "preferred_delivery_mode": preferred,
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


def _reconcile_parent_event_state(event: dict) -> str:
    states = {route.get("delivery_state") for route in event.get("routes", [])}
    if not states:
        return str(event.get("state") or "ROUTED")
    if states <= {"RESPONDED"}:
        return "RESPONDED"
    if states <= {"ACKED", "RESPONDED"}:
        return "ACKED"
    if states <= {"DELIVERED", "ACKED", "RESPONDED"}:
        return "DELIVERED"
    if "FALLBACK_POLL_REQUIRED" in states:
        return "FALLBACK_POLL_REQUIRED"
    return "ROUTED"


def reconcile_dispatch_delivery_docs(state: dict, dispatches_doc: dict, *, timestamp: datetime) -> list[dict]:
    changes = []
    dispatch_index = {
        item.get("dispatch_id"): item
        for item in dispatches_doc.get("items", [])
        if isinstance(item, dict) and item.get("dispatch_id")
    }
    for continuity in state.get("items", []):
        for event in continuity.get("events", []):
            for route in event.get("routes", []):
                dispatch = dispatch_index.get(route.get("dispatch_id"))
                if not dispatch:
                    continue
                status = dispatch.get("status")
                if status == "DISPATCHED" and route.get("delivery_state") == "ROUTED":
                    route["delivery_state"] = "DELIVERED"
                    route["delivered_at"] = dispatch.get("delivered_at") or iso(timestamp)
                    route["evidence_ref"] = dispatch.get("delivery_evidence_ref") or route.get("evidence_ref")
                    if event.get("requires_ack"):
                        route["ack_deadline_at"] = iso(
                            (parse_time(route["delivered_at"]) or timestamp)
                            + timedelta(seconds=int(event.get("ack_timeout_seconds") or 300))
                        )
                    changes.append({"event_id": event.get("event_id"), "target_session_id": route.get("target_session_id"), "state": "DELIVERED"})
                elif status == "ACKNOWLEDGED" and route.get("delivery_state") in {"ROUTED", "DELIVERED"}:
                    route["delivery_state"] = "ACKED"
                    route["acknowledged_at"] = ((dispatch.get("ack") or {}).get("observed_at") or iso(timestamp))
                    route["evidence_ref"] = ((dispatch.get("ack") or {}).get("evidence_ref") or route.get("evidence_ref"))
                    changes.append({"event_id": event.get("event_id"), "target_session_id": route.get("target_session_id"), "state": "ACKED"})
                elif (
                    status == "FALLBACK_POLL_REQUIRED"
                    and route.get("delivery_state") not in NON_REGRESSIBLE_ROUTE_STATES
                    and route.get("delivery_state") != "FALLBACK_POLL_REQUIRED"
                ):
                    route["delivery_state"] = "FALLBACK_POLL_REQUIRED"
                    if FALLBACK_MODE not in route.setdefault("delivery_modes", []):
                        route["delivery_modes"].append(FALLBACK_MODE)
                    changes.append({"event_id": event.get("event_id"), "target_session_id": route.get("target_session_id"), "state": "FALLBACK_POLL_REQUIRED"})
            parent_state = _reconcile_parent_event_state(event)
            if event.get("state") != parent_state:
                event["state"] = parent_state
                changes.append({"event_id": event.get("event_id"), "state": parent_state})
        alerts = continuity.get("supervision_alerts") or []
        for alert in alerts:
            dispatch = dispatch_index.get(alert.get("dispatch_id"))
            if not dispatch:
                continue
            status = dispatch.get("status")
            if status in {"DISPATCHED", "ACKNOWLEDGED", "COMPLETED"} and alert.get("delivery_state") in {"READY", "ROUTED"}:
                alert["delivery_state"] = "DELIVERED"
                alert["delivered_at"] = dispatch.get("delivered_at") or iso(timestamp)
                alert["delivery_evidence_ref"] = dispatch.get("delivery_evidence_ref")
                changes.append({"alert_id": alert.get("alert_id"), "target_session_id": alert.get("target_session_id"), "state": "DELIVERED"})
            elif status == "FALLBACK_POLL_REQUIRED" and alert.get("delivery_state") != "FALLBACK_POLL_REQUIRED":
                alert["delivery_state"] = "FALLBACK_POLL_REQUIRED"
                changes.append({"alert_id": alert.get("alert_id"), "target_session_id": alert.get("target_session_id"), "state": "FALLBACK_POLL_REQUIRED"})
    return changes


def tick_docs(
    state: dict,
    sessions_doc: dict,
    dispatches_doc: dict,
    *,
    timestamp: datetime,
    early_supervision_after_seconds: int = EARLY_SUPERVISION_AFTER_SECONDS,
    config: dict | None = None,
) -> dict:
    changes = project_participant_runtime_docs(
        state,
        sessions_doc,
        timestamp=timestamp,
        config=config,
        quiet_after_seconds=early_supervision_after_seconds,
    )
    changes.extend(reconcile_early_supervision_docs(
        state,
        sessions_doc,
        dispatches_doc,
        timestamp=timestamp,
        early_supervision_after_seconds=early_supervision_after_seconds,
        config=config,
    ))
    changes.extend(reconcile_dispatch_delivery_docs(state, dispatches_doc, timestamp=timestamp))
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


def resolve_event_targets(
    state: dict,
    sessions: dict,
    *,
    continuity_id: str,
    target_session_ids: list[str] | None = None,
    target_logical_agent_alias: str | None = None,
) -> tuple[list[str], dict | None]:
    raw_targets = [str(x).strip() for x in (target_session_ids or []) if str(x).strip()]
    explicit = normalize_targets(raw_targets) if raw_targets else []
    alias = str(target_logical_agent_alias or "").strip()
    if explicit and alias:
        raise ValueError("CONTINUITY_BUS_FAILED: choose target_session_id or target_logical_agent_alias, not both")
    if explicit:
        return explicit, None
    if not alias:
        raise ValueError("CONTINUITY_BUS_FAILED: at least one target is required")
    resolution = resolve_logical_agent_alias_docs(
        state,
        sessions,
        alias=alias,
        continuity_id=continuity_id,
    )
    if resolution.get("routing_status") != "ROUTABLE_EXACT_SESSION":
        raise ValueError(
            "CONTINUITY_BUS_FAILED: logical agent alias is not uniquely routable: "
            + str(resolution.get("routing_status") or "UNRESOLVED")
        )
    target = resolution.get("resolved_target_session_id")
    if not target:
        raise ValueError("CONTINUITY_BUS_FAILED: logical agent alias resolved no target session")
    return [str(target)], {
        "target_kind": "LOGICAL_AGENT_ALIAS",
        "requested_alias": resolution.get("human_alias"),
        "logical_agent_id": resolution.get("logical_agent_id"),
        "resolved_target_session_id": target,
        "routing_status": resolution.get("routing_status"),
        "projection_only": True,
        "grants_task_authority": False,
        "grants_claim": False,
        "grants_mutation_authority": False,
    }


def command_emit(a):
    state, sessions, dispatches = load_runtime()
    config = read_json(CONFIG_PATH, {})
    targets, alias_resolution = resolve_event_targets(
        state,
        sessions,
        continuity_id=a.continuity_id,
        target_session_ids=a.target_session_id,
        target_logical_agent_alias=a.target_logical_agent_alias,
    )
    result = emit_event_docs(state, sessions, dispatches, continuity_id=a.continuity_id, from_session_id=a.from_session_id, target_session_ids=targets, event_kind=a.event_kind, payload_ref=a.payload_ref, observed_head=a.observed_head, current_head=git_head(), evidence_ref=a.evidence_ref, timestamp=now_utc(), scope_id=a.scope_id, collision_domains=a.collision_domain, requires_ack=a.requires_ack, correlation_id=a.correlation_id, reply_to_event_id=a.reply_to_event_id, expires_at=a.expires_at, ack_timeout_seconds=a.ack_timeout_seconds, config=config)
    result["target_resolution"] = alias_resolution
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
    config = read_json(CONFIG_PATH, {})
    result = tick_docs(
        state,
        sessions,
        dispatches,
        timestamp=now_utc(),
        early_supervision_after_seconds=a.early_supervision_after_seconds,
        config=config,
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
    emit.add_argument("--target-session-id", action="append")
    emit.add_argument("--target-logical-agent-alias")
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
