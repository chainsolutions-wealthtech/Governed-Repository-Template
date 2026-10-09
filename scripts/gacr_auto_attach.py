#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from governed_agent_continuity_relay import (
    conversation_ref,
    git_branch,
    git_head,
    load_all,
    now_utc,
    register_docs,
    repository_name,
    save,
)
from gacr_agent_telemetry import correlate_all, record_beacon

ROOT = Path(os.environ.get("GACR_ROOT") or Path(__file__).resolve().parents[1]).resolve()
GOV = ROOT / ".governance"
TEMPLATE_SOURCE = (ROOT / ".template-source").exists()
CHRONICLE_CURRENT = GOV / "control-plane-state" / "conversation-chronicles" / "current.json"
if TEMPLATE_SOURCE:
    CONTINUITIES_PATH = GOV / "control-plane-state" / "gacr-continuities.json"
    FORENSICS_PATH = GOV / "control-plane-state" / "gacr-forensics.json"
    BEACONS_PATH = GOV / "control-plane-state" / "gacr-beacons.json"
else:
    CONTINUITIES_PATH = GOV / "agent-relay" / "continuities.json"
    FORENSICS_PATH = GOV / "agent-relay" / "forensics.json"
    BEACONS_PATH = GOV / "agent-relay" / "beacons.json"
INTERNAL_GACR_WORKFLOWS = {"Governed Agent Continuity Relay"}


ENVELOPE_SCHEMA = "gacr-connection-envelope/v1"
FINGERPRINT_VERSION = "gacr-connection-fingerprint/v1"
UNAVAILABLE = "UNAVAILABLE"
SURFACE_CLASSES = {
    "CONTROLLED_INSTRUMENTABLE",
    "GITHUB_EVENT_VISIBLE",
    "PROPRIETARY_SILENT",
}
PROVENANCE_CLASSES = {
    "OBSERVABLE_BY_PLATFORM",
    "DECLARED_BY_AGENT_OR_CLIENT",
    "DERIVED_SAFE",
    "CORRELATED",
    "PROVIDER_PRIVATE_UNAVAILABLE",
}
TERMINAL_RELAY_STATES = {"CLOSED", "HANDOFF_STALLED"}
FORBIDDEN_PRESENCE_KEY_FRAGMENTS = (
    "token",
    "secret",
    "password",
    "private_key",
    "cookie",
    "authorization",
    "transcript",
    "prompt",
    "private_reasoning",
    "chain_of_thought",
    "raw_response",
    "response_body",
    "page_content",
)


def validate_presence_observation(value: object) -> None:
    """Reject secrets, raw conversational content and provider-private payloads."""

    def walk(node: object, path: str = "observation") -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                lowered = str(key).lower()
                if any(fragment in lowered for fragment in FORBIDDEN_PRESENCE_KEY_FRAGMENTS):
                    raise ValueError(f"forbidden presence key at {path}/{key}")
                walk(child, f"{path}/{key}")
        elif isinstance(node, list):
            for index, child in enumerate(node):
                walk(child, f"{path}/{index}")
        elif isinstance(node, str):
            stripped = node.strip()
            if (
                "-----BEGIN PRIVATE KEY-----" in node
                or stripped.startswith("ghp_")
                or stripped.startswith("github_pat_")
                or stripped.startswith("sk-")
                or stripped.lower().startswith("bearer ")
            ):
                raise ValueError(f"secret-like presence value at {path}")

    walk(value)


def _event_facts() -> dict:
    """Read only an allowlisted subset of a GitHub event, never the raw payload."""
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not Path(event_path).exists():
        return {}
    try:
        raw = read_json(Path(event_path))
    except (OSError, ValueError, json.JSONDecodeError):
        return {}

    repository = raw.get("repository") or {}
    owner = repository.get("owner") or {}
    sender = raw.get("sender") or {}
    installation = raw.get("installation") or {}
    pr = raw.get("pull_request") or {}
    workflow_run = raw.get("workflow_run") or {}
    workflow_job = raw.get("workflow_job") or {}
    head = pr.get("head") or {}
    base = pr.get("base") or {}

    return {
        "repository_id": repository.get("id"),
        "repository": repository.get("full_name"),
        "organization": owner.get("login"),
        "github_actor": sender.get("login"),
        "github_app_or_installation": installation.get("id"),
        "branch": head.get("ref"),
        "base_branch": base.get("ref"),
        "head": head.get("sha"),
        "pull_request": pr.get("number") or raw.get("number") if pr else None,
        "workflow_run_id": workflow_run.get("id"),
        "job_id": workflow_job.get("id"),
    }


def _as_unavailable(value):
    if value is None or value == "":
        return UNAVAILABLE
    return value


def _field(value, provenance: str, source: str) -> dict:
    if provenance not in PROVENANCE_CLASSES:
        raise ValueError(f"unsupported provenance class: {provenance}")
    return {
        "value": _as_unavailable(value),
        "provenance": provenance,
        "source": source,
    }


def _parse_permissions(value: str | None):
    if not value:
        return None
    parsed = json.loads(value)
    if not isinstance(parsed, (dict, list)):
        raise ValueError("permissions must be an explicitly supplied JSON object or array")
    validate_presence_observation(parsed)
    return parsed


def _surface_class(args: argparse.Namespace, anchor: dict) -> str:
    if args.surface_class:
        if args.surface_class not in SURFACE_CLASSES:
            raise ValueError("unsupported surface class")
        return args.surface_class
    if anchor.get("source") == "GITHUB_ACTIONS":
        return "GITHUB_EVENT_VISIBLE"
    return "CONTROLLED_INSTRUMENTABLE"


def _connection_method(args: argparse.Namespace, anchor: dict, surface_class: str) -> str | None:
    if args.connection_method:
        return args.connection_method
    source = anchor.get("source")
    if source == "CONVERSATION_CHRONICLE":
        return "conversation-chronicle"
    if source == "GITHUB_ACTIONS":
        return "github-actions-event"
    if source in {"EXPLICIT_CLIENT", "CLIENT_EMITTER", "PRESENCE_FABRIC"}:
        return "controlled-client-adapter"
    if surface_class == "PROPRIETARY_SILENT":
        return None
    return "controlled-repository-surface"


def _time_bucket(value: str, seconds: int) -> str:
    dt = parse_time(value)
    if dt is None:
        raise ValueError("observed_at must be an ISO-8601 timestamp")
    epoch = int(dt.timestamp())
    bucket = epoch - (epoch % max(1, seconds))
    return datetime.fromtimestamp(bucket, timezone.utc).replace(microsecond=0).isoformat()


def _provider_ref(provider: str | None, provider_ref: str | None, provider_url: str | None) -> str | None:
    normalized_provider = provider or "other"
    ref, _ = conversation_ref(normalized_provider, provider_ref, provider_url)
    return ref


def build_presence_observation(args: argparse.Namespace, anchor: dict, config: dict) -> dict:
    event = _event_facts()
    observed_at = args.observed_at or now_utc().replace(microsecond=0).isoformat()
    repository = args.repository or event.get("repository") or repository_name()
    repository_id = args.repository_id or os.environ.get("GITHUB_REPOSITORY_ID") or event.get("repository_id")

    organization = args.organization or event.get("organization")
    organization_provenance = "OBSERVABLE_BY_PLATFORM"
    if not organization and repository and repository != "UNKNOWN_REPOSITORY" and "/" in repository:
        organization = repository.split("/", 1)[0]
        organization_provenance = "DERIVED_SAFE"

    surface_class = _surface_class(args, anchor)

    git_provider = args.git_provider
    git_provider_provenance = "OBSERVABLE_BY_PLATFORM"
    if not git_provider and (
        str(os.environ.get("GITHUB_SERVER_URL") or "").startswith("https://github")
        or os.environ.get("GITHUB_REPOSITORY")
        or event.get("repository")
    ):
        git_provider = "github"
        git_provider_provenance = "DERIVED_SAFE"

    github_actor = args.github_actor or event.get("github_actor") or os.environ.get("GITHUB_ACTOR")
    github_app_or_installation = args.github_app_installation or event.get("github_app_or_installation")
    provider_connector_app_id = args.provider_connector_app_id
    provider_connector_client_id = args.provider_connector_client_id
    provider_connector_installation_id = args.provider_connector_installation_id or event.get("github_app_or_installation")
    provider_connector_slug = args.provider_connector_slug

    connection_method = _connection_method(args, anchor, surface_class)
    connection_method_provenance = "OBSERVABLE_BY_PLATFORM" if args.connection_method else "DERIVED_SAFE"

    if args.agent:
        agent_identity = args.agent
        agent_identity_provenance = "DECLARED_BY_AGENT_OR_CLIENT"
    elif anchor.get("source") == "GITHUB_ACTIONS" and anchor.get("agent"):
        agent_identity = anchor.get("agent")
        agent_identity_provenance = "OBSERVABLE_BY_PLATFORM"
    elif anchor.get("agent"):
        agent_identity = anchor.get("agent")
        agent_identity_provenance = "DERIVED_SAFE"
    elif os.environ.get("GACR_AGENT_IDENTITY"):
        agent_identity = os.environ.get("GACR_AGENT_IDENTITY")
        agent_identity_provenance = "DECLARED_BY_AGENT_OR_CLIENT"
    else:
        agent_identity = github_actor
        agent_identity_provenance = "OBSERVABLE_BY_PLATFORM"

    if args.provider or os.environ.get("GACR_PROVIDER"):
        provider = args.provider or os.environ.get("GACR_PROVIDER")
        provider_provenance = "DECLARED_BY_AGENT_OR_CLIENT"
    elif anchor.get("provider"):
        provider = anchor.get("provider")
        provider_provenance = "OBSERVABLE_BY_PLATFORM" if anchor.get("source") == "GITHUB_ACTIONS" else "DERIVED_SAFE"
    else:
        provider = None
        provider_provenance = "PROVIDER_PRIVATE_UNAVAILABLE"

    provider_ref = _provider_ref(provider, args.provider_ref, args.provider_url)
    provider_ref_provenance = (
        "DECLARED_BY_AGENT_OR_CLIENT" if provider_ref else "PROVIDER_PRIVATE_UNAVAILABLE"
    )

    client_instance_id = args.client_instance_id or anchor.get("client_instance_id")
    client_instance_provenance = (
        "DECLARED_BY_AGENT_OR_CLIENT"
        if args.client_instance_id
        else "OBSERVABLE_BY_PLATFORM"
        if anchor.get("source") == "GITHUB_ACTIONS"
        else "DERIVED_SAFE"
    )
    connection_ref = args.connection_ref or anchor.get("connection_ref")
    connection_ref_provenance = (
        "DECLARED_BY_AGENT_OR_CLIENT"
        if args.connection_ref
        else "OBSERVABLE_BY_PLATFORM"
        if anchor.get("source") == "GITHUB_ACTIONS"
        else "DERIVED_SAFE"
    )

    permissions = _parse_permissions(args.permissions_json)
    capabilities = sorted(set(args.capability or [])) if args.capability else None

    field_provenance = {
        "client_instance_id": client_instance_provenance,
        "provider": provider_provenance,
        "agent_identity": agent_identity_provenance,
        "agent_type_or_model": "DECLARED_BY_AGENT_OR_CLIENT" if args.agent_type_model else "PROVIDER_PRIVATE_UNAVAILABLE",
        "repository": "OBSERVABLE_BY_PLATFORM",
        "repository_id": "OBSERVABLE_BY_PLATFORM",
        "organization": organization_provenance,
        "git_provider": git_provider_provenance,
        "github_actor": "OBSERVABLE_BY_PLATFORM",
        "github_app_or_installation": "OBSERVABLE_BY_PLATFORM",
        "provider_connector_app_id": "DECLARED_BY_AGENT_OR_CLIENT" if provider_connector_app_id else "PROVIDER_PRIVATE_UNAVAILABLE",
        "provider_connector_client_id": "DECLARED_BY_AGENT_OR_CLIENT" if provider_connector_client_id else "PROVIDER_PRIVATE_UNAVAILABLE",
        "provider_connector_installation_id": (
            "DECLARED_BY_AGENT_OR_CLIENT" if args.provider_connector_installation_id
            else "OBSERVABLE_BY_PLATFORM" if provider_connector_installation_id
            else "PROVIDER_PRIVATE_UNAVAILABLE"
        ),
        "provider_connector_slug": "DECLARED_BY_AGENT_OR_CLIENT" if provider_connector_slug else "PROVIDER_PRIVATE_UNAVAILABLE",
        "connection_method": connection_method_provenance,
        "permissions": "DECLARED_BY_AGENT_OR_CLIENT" if permissions is not None else "OBSERVABLE_BY_PLATFORM",
        "capabilities": "DECLARED_BY_AGENT_OR_CLIENT",
        "entry_action": "DECLARED_BY_AGENT_OR_CLIENT",
        "connection_intent": "DECLARED_BY_AGENT_OR_CLIENT",
        "task_id": "DECLARED_BY_AGENT_OR_CLIENT",
        "claim_id": "DECLARED_BY_AGENT_OR_CLIENT",
        "branch": "OBSERVABLE_BY_PLATFORM",
        "base_branch": "OBSERVABLE_BY_PLATFORM",
        "HEAD": "OBSERVABLE_BY_PLATFORM",
        "PR": "OBSERVABLE_BY_PLATFORM",
        "workflow_run_id": "OBSERVABLE_BY_PLATFORM",
        "job_id": "OBSERVABLE_BY_PLATFORM",
        "run_attempt": "OBSERVABLE_BY_PLATFORM",
        "event_type": "OBSERVABLE_BY_PLATFORM",
        "delivery_or_correlation_id": "OBSERVABLE_BY_PLATFORM",
        "heartbeat_seq": "DECLARED_BY_AGENT_OR_CLIENT",
        "provider_conversation_ref": provider_ref_provenance,
        "provider_conversation_url": "PROVIDER_PRIVATE_UNAVAILABLE",
        "checkpoint": "DECLARED_BY_AGENT_OR_CLIENT",
        "last_action": "DECLARED_BY_AGENT_OR_CLIENT",
        "last_evidence": "DECLARED_BY_AGENT_OR_CLIENT",
        "connection_ref": connection_ref_provenance,
    }

    observation = {
        "observed_at": observed_at,
        "surface_class": surface_class,
        "source": args.source or anchor.get("source") or "PRESENCE_FABRIC",
        "field_provenance": field_provenance,
        "repository": repository,
        "repository_id": repository_id,
        "organization": organization,
        "git_provider": git_provider,
        "github_actor": github_actor,
        "github_app_or_installation": github_app_or_installation,
        "provider_connector_app_id": provider_connector_app_id,
        "provider_connector_client_id": provider_connector_client_id,
        "provider_connector_installation_id": provider_connector_installation_id,
        "provider_connector_slug": provider_connector_slug,
        "connection_method": connection_method,
        "agent_identity": agent_identity,
        "agent_type_or_model": args.agent_type_model,
        "provider": provider,
        "provider_ref": provider_ref,
        "provider_url_supplied": bool(args.provider_url),
        "client_instance_id": client_instance_id,
        "connection_ref": connection_ref,
        "permissions": permissions,
        "capabilities": capabilities,
        "entry_action": args.entry_action,
        "connection_intent": args.connection_intent,
        "task_id": args.task_id,
        "claim_id": args.claim_id,
        "branch": args.branch or event.get("branch") or git_branch(),
        "base_branch": args.base_branch or event.get("base_branch") or os.environ.get("GITHUB_BASE_REF"),
        "head": args.observed_head or event.get("head") or git_head(),
        "pull_request": args.pull_request if args.pull_request is not None else event.get("pull_request"),
        "workflow_run_id": args.workflow_run_id or event.get("workflow_run_id") or os.environ.get("GITHUB_RUN_ID"),
        "job_id": args.job_id or event.get("job_id"),
        "run_attempt": args.run_attempt or os.environ.get("GITHUB_RUN_ATTEMPT"),
        "event_type": args.event_type or os.environ.get("GITHUB_EVENT_NAME") or "REPOSITORY_ACCESS",
        "delivery_or_correlation_id": args.delivery_correlation_id,
        "heartbeat_seq": args.heartbeat_seq,
        "checkpoint": args.checkpoint,
        "last_action": args.last_action,
        "last_evidence": args.last_evidence,
        "agent_role": args.agent_role,
        "wake_channels": list(args.wake_channel or []),
        "bridge_registration_ref": args.bridge_registration_ref or anchor.get("bridge_registration_ref"),
        "standby": bool(args.standby),
    }
    validate_presence_observation(observation)
    return observation
def _fingerprint_payload(observation: dict, config: dict, *, first_head=None, first_observed_at=None) -> dict:
    bucket_seconds = int((config.get("presence_fabric") or {}).get("first_touch_time_bucket_seconds", 300))
    observed_at = first_observed_at or observation["observed_at"]
    actor_key = observation.get("github_app_or_installation") or observation.get("github_actor")
    return {
        "version": FINGERPRINT_VERSION,
        "repository_key": observation.get("repository_id") or observation.get("repository") or UNAVAILABLE,
        "surface_class": observation.get("surface_class") or UNAVAILABLE,
        "actor_or_app_key": actor_key or UNAVAILABLE,
        "client_instance_id_if_supplied": observation.get("client_instance_id") or UNAVAILABLE,
        "connection_ref_if_supplied": observation.get("connection_ref") or UNAVAILABLE,
        "task_id_if_known": observation.get("task_id") or UNAVAILABLE,
        "claim_id_if_known": observation.get("claim_id") or UNAVAILABLE,
        "branch_if_known": observation.get("branch") or UNAVAILABLE,
        "pull_request_if_known": observation.get("pull_request") if observation.get("pull_request") is not None else UNAVAILABLE,
        "first_observed_head": first_head or observation.get("head") or UNAVAILABLE,
        "first_touch_time_bucket": _time_bucket(observed_at, bucket_seconds),
    }


def _fingerprint(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "GACR-FP1-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _live_sessions(sessions_doc: dict, repository: str) -> list[dict]:
    result = []
    for session in sessions_doc.get("sessions", []):
        relay_state = (session.get("relay") or {}).get("state")
        if session.get("repository") != repository:
            continue
        if session.get("status") == "CLOSED" or relay_state in TERMINAL_RELAY_STATES:
            continue
        result.append(session)
    return result


def _candidate_sessions(sessions_doc: dict, observation: dict) -> list[dict]:
    provider_ref = observation.get("provider_ref")
    connection_ref = observation.get("connection_ref")
    client_instance_id = observation.get("client_instance_id")
    candidates: dict[str, dict] = {}

    for session in _live_sessions(sessions_doc, observation["repository"]):
        matched = False
        if provider_ref and session.get("provider_conversation_ref") == provider_ref:
            matched = True
        if connection_ref and session.get("connection_ref") == connection_ref:
            matched = True

        # A client instance may host multiple concurrent connections. It is an
        # exact anchor only when no conflicting, more-specific connection_ref
        # is present. Never collapse a new connection into an old session merely
        # because they share the same client process/browser integration.
        if client_instance_id and session.get("client_instance_id") == client_instance_id:
            session_connection_ref = session.get("connection_ref")
            if not connection_ref or session_connection_ref in {None, "", connection_ref}:
                matched = True

        if matched:
            candidates[session["session_id"]] = session

    return sorted(candidates.values(), key=lambda x: x.get("session_id") or "")
def _requires_governed_reconciliation(session: dict) -> bool:
    relay_state = (session.get("relay") or {}).get("state")
    return session.get("status") == "STALLED" or relay_state == "TAKEOVER_READY"


def _stalled_unbound(session: dict, *, fingerprint: str | None, anchor: dict | None) -> dict:
    return {
        "state": "UNBOUND",
        "reason": "STALLED_SESSION_REQUIRES_GOVERNED_RECONCILIATION",
        "selected_session": None,
        "candidate_session_ids": [session["session_id"]],
        "connection_fingerprint": fingerprint,
        "presence_anchor": anchor,
    }


def _stable_anchor_present(observation: dict) -> bool:
    return any(
        observation.get(key)
        for key in ("connection_ref", "client_instance_id", "provider_ref")
    )


def bind_presence(sessions_doc: dict, observation: dict, config: dict) -> dict:
    if observation.get("surface_class") == "PROPRIETARY_SILENT":
        return {
            "state": "UNBOUND",
            "reason": "PROPRIETARY_SILENT_NOT_OBSERVABLE",
            "selected_session": None,
            "candidate_session_ids": [],
            "connection_fingerprint": None,
            "presence_anchor": None,
        }

    candidates = _candidate_sessions(sessions_doc, observation)
    if len(candidates) > 1:
        return {
            "state": "AMBIGUOUS",
            "reason": "MULTIPLE_STABLE_ANCHOR_MATCHES",
            "selected_session": None,
            "candidate_session_ids": [s["session_id"] for s in candidates],
            "connection_fingerprint": None,
            "presence_anchor": None,
        }

    if len(candidates) == 1:
        session = candidates[0]
        anchor = session.get("presence_anchor")
        fingerprint = session.get("connection_fingerprint")
        if not anchor:
            anchor = _fingerprint_payload(
                observation,
                config,
                first_head=session.get("starting_head_sha") or session.get("last_observed_head_sha"),
                first_observed_at=session.get("created_at") or observation["observed_at"],
            )
        if not fingerprint:
            fingerprint = _fingerprint(anchor)
        if _requires_governed_reconciliation(session):
            return _stalled_unbound(session, fingerprint=fingerprint, anchor=anchor)
        return {
            "state": "BOUND",
            "reason": "STABLE_ANCHOR_RESUME",
            "selected_session": session,
            "candidate_session_ids": [session["session_id"]],
            "connection_fingerprint": fingerprint,
            "presence_anchor": anchor,
        }

    if not _stable_anchor_present(observation):
        return {
            "state": "UNBOUND",
            "reason": "INSUFFICIENT_STABLE_INSTANCE_ANCHOR",
            "selected_session": None,
            "candidate_session_ids": [],
            "connection_fingerprint": None,
            "presence_anchor": None,
        }

    anchor = _fingerprint_payload(observation, config)
    fingerprint = _fingerprint(anchor)
    fingerprint_matches = [
        session
        for session in _live_sessions(sessions_doc, observation["repository"])
        if session.get("connection_fingerprint") == fingerprint
    ]
    if len(fingerprint_matches) > 1:
        return {
            "state": "AMBIGUOUS",
            "reason": "FINGERPRINT_COLLISION",
            "selected_session": None,
            "candidate_session_ids": [s["session_id"] for s in fingerprint_matches],
            "connection_fingerprint": fingerprint,
            "presence_anchor": anchor,
        }
    if len(fingerprint_matches) == 1:
        session = fingerprint_matches[0]
        selected_anchor = session.get("presence_anchor") or anchor
        if _requires_governed_reconciliation(session):
            return _stalled_unbound(session, fingerprint=fingerprint, anchor=selected_anchor)
        return {
            "state": "BOUND",
            "reason": "FINGERPRINT_EXACT",
            "selected_session": session,
            "candidate_session_ids": [session["session_id"]],
            "connection_fingerprint": fingerprint,
            "presence_anchor": selected_anchor,
        }

    return {
        "state": "CREATE",
        "reason": "NEW_STABLE_ANCHOR",
        "selected_session": None,
        "candidate_session_ids": [],
        "connection_fingerprint": fingerprint,
        "presence_anchor": anchor,
    }


def _same_logical_agent_sessions(sessions_doc: dict, observation: dict) -> list[dict]:
    agent_identity = str(observation.get("agent_identity") or "").strip()
    repository = observation.get("repository")
    if not agent_identity or not repository:
        return []
    return sorted(
        [
            session for session in sessions_doc.get("sessions", [])
            if session.get("repository") == repository
            and session.get("agent_identity") == agent_identity
        ],
        key=lambda item: item.get("session_id") or "",
    )


def _continuity_proof(
    *,
    reference_session_id: str,
    continuity_id: str,
    evidence_ref: str,
) -> dict | None:
    if CONTINUITIES_PATH.exists():
        continuity_doc = read_json(CONTINUITIES_PATH)
        for item in continuity_doc.get("items", []):
            if item.get("continuity_id") != continuity_id:
                continue
            for participant in item.get("participants", []):
                if participant.get("session_id") != reference_session_id:
                    continue
                if participant.get("membership_state") == "TERMINAL":
                    continue
                refs = {
                    participant.get("evidence_ref"),
                    participant.get("coordination_state_ref"),
                    participant.get("handoff_ref"),
                }
                if evidence_ref in refs:
                    return {
                        "source": "CONTINUITY_MEMBERSHIP",
                        "continuity_id": continuity_id,
                        "reference_session_id": reference_session_id,
                        "evidence_ref": evidence_ref,
                    }
            handoff = item.get("last_handoff") or {}
            if handoff.get("session_id") == reference_session_id and evidence_ref in {
                handoff.get("evidence_ref"),
                handoff.get("handoff_ref"),
            }:
                return {
                    "source": "CONTINUITY_HANDOFF",
                    "continuity_id": continuity_id,
                    "reference_session_id": reference_session_id,
                    "evidence_ref": evidence_ref,
                }

    if FORENSICS_PATH.exists():
        forensic_doc = read_json(FORENSICS_PATH)
        for item in forensic_doc.get("items", []):
            if item.get("session_id") != reference_session_id:
                continue
            resume = item.get("resume_point") or {}
            checkpoint_match = (
                item.get("last_checkpoint_ref") == continuity_id
                or resume.get("checkpoint_ref") == continuity_id
            )
            if not checkpoint_match:
                continue
            refs = {
                item.get("last_evidence_ref"),
                resume.get("evidence_ref"),
            }
            completed = ((item.get("actions") or {}).get("last_action_completed") or {})
            if completed.get("checkpoint_ref") == continuity_id:
                refs.add(completed.get("evidence_ref"))
            if evidence_ref in refs:
                return {
                    "source": "GACR_FORENSICS_CHECKPOINT",
                    "continuity_id": continuity_id,
                    "reference_session_id": reference_session_id,
                    "evidence_ref": evidence_ref,
                    "forensic_id": item.get("forensic_id"),
                }

    if BEACONS_PATH.exists():
        beacon_doc = read_json(BEACONS_PATH)
        for item in beacon_doc.get("items", []):
            if (
                item.get("session_id") == reference_session_id
                and item.get("checkpoint_ref") == continuity_id
                and item.get("evidence_ref") == evidence_ref
            ):
                return {
                    "source": "GACR_BEACON_CHECKPOINT",
                    "continuity_id": continuity_id,
                    "reference_session_id": reference_session_id,
                    "evidence_ref": evidence_ref,
                    "beacon_id": item.get("beacon_id"),
                }
    return None


def _same_logical_agent_gate(
    args: argparse.Namespace,
    sessions_doc: dict,
    observation: dict,
    binding: dict,
) -> dict | None:
    if binding.get("state") != "CREATE":
        return None

    same_agent = _same_logical_agent_sessions(sessions_doc, observation)
    requested = any([
        args.same_logical_agent_session_id,
        args.continuity_id,
        args.continuity_evidence_ref,
    ])
    if not same_agent and not requested:
        return None

    candidate_ids = [item.get("session_id") for item in same_agent if item.get("session_id")]
    if not requested:
        return {
            "allowed": False,
            "reason": "LOGICAL_AGENT_REUSE_REQUIRES_EXPLICIT_CONTINUITY_PROOF",
            "candidate_session_ids": candidate_ids,
        }

    required = {
        "same_logical_agent_session_id": args.same_logical_agent_session_id,
        "continuity_id": args.continuity_id,
        "continuity_evidence_ref": args.continuity_evidence_ref,
        "agent": args.agent,
        "connection_ref": args.connection_ref,
    }
    missing = sorted(key for key, value in required.items() if value in {None, ""})
    if missing:
        return {
            "allowed": False,
            "reason": "INCOMPLETE_SAME_LOGICAL_AGENT_PROOF:" + ",".join(missing),
            "candidate_session_ids": candidate_ids,
        }
    if args.claim_id:
        return {
            "allowed": False,
            "reason": "SAME_LOGICAL_AGENT_ATTACH_CANNOT_INHERIT_CLAIM",
            "candidate_session_ids": candidate_ids,
        }

    reference = next(
        (item for item in sessions_doc.get("sessions", [])
         if item.get("session_id") == args.same_logical_agent_session_id),
        None,
    )
    if reference is None:
        return {
            "allowed": False,
            "reason": "SAME_LOGICAL_AGENT_REFERENCE_SESSION_NOT_FOUND",
            "candidate_session_ids": candidate_ids,
        }
    if reference.get("repository") != observation.get("repository"):
        return {
            "allowed": False,
            "reason": "SAME_LOGICAL_AGENT_REFERENCE_REPOSITORY_MISMATCH",
            "candidate_session_ids": candidate_ids,
        }
    if reference.get("agent_identity") != observation.get("agent_identity"):
        return {
            "allowed": False,
            "reason": "SAME_LOGICAL_AGENT_IDENTITY_MISMATCH",
            "candidate_session_ids": candidate_ids,
        }
    if reference.get("connection_ref") == args.connection_ref:
        return {
            "allowed": False,
            "reason": "SAME_LOGICAL_AGENT_REQUIRES_NEW_RUNTIME_SURFACE",
            "candidate_session_ids": candidate_ids,
        }
    connection_owners = [
        item.get("session_id")
        for item in sessions_doc.get("sessions", [])
        if item.get("connection_ref") == args.connection_ref
    ]
    if connection_owners:
        return {
            "allowed": False,
            "reason": "RUNTIME_SURFACE_ALREADY_BOUND",
            "candidate_session_ids": sorted(x for x in connection_owners if x),
        }

    proof = _continuity_proof(
        reference_session_id=str(args.same_logical_agent_session_id),
        continuity_id=str(args.continuity_id),
        evidence_ref=str(args.continuity_evidence_ref),
    )
    if proof is None:
        return {
            "allowed": False,
            "reason": "CANONICAL_CONTINUITY_PROOF_NOT_FOUND",
            "candidate_session_ids": candidate_ids,
        }

    return {
        "allowed": True,
        "reason": "EXPLICIT_CANONICAL_CONTINUITY_PROOF",
        "candidate_session_ids": candidate_ids,
        "reference_session": reference,
        "continuity_id": str(args.continuity_id),
        "evidence_ref": str(args.continuity_evidence_ref),
        "proof": proof,
    }


def _provider_context_id(session_id: str, connection_ref: str | None, provider_ref: str | None, client_instance_id: str | None) -> str:
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


def _record_provider_context(session: dict, observation: dict) -> dict:
    provenance = observation.get("field_provenance") or {}
    connection_ref = observation.get("connection_ref") or session.get("connection_ref")
    provider_ref = observation.get("provider_ref") or session.get("provider_conversation_ref")
    client_instance_id = observation.get("client_instance_id") or session.get("client_instance_id")
    context_id = _provider_context_id(str(session.get("session_id") or ""), connection_ref, provider_ref, client_instance_id)
    observed_at = observation.get("observed_at")
    record = {
        "provider_context_id": context_id,
        "provider_context_id_provenance": "DERIVED_GACR_SESSION_CONTEXT",
        "provider": observation.get("provider") or session.get("provider") or "other",
        "provider_conversation_ref": provider_ref,
        "provider_conversation_ref_status": "PRESENT" if provider_ref else "UNAVAILABLE",
        "provider_conversation_ref_provenance": provenance.get("provider_conversation_ref") if provider_ref else "PROVIDER_PRIVATE_UNAVAILABLE",
        "client_instance_id": client_instance_id,
        "client_instance_id_provenance": provenance.get("client_instance_id") or "CORRELATED",
        "connection_ref": connection_ref,
        "connection_ref_provenance": provenance.get("connection_ref") or "CORRELATED",
        "runtime_surface_ref": connection_ref if str(connection_ref or "").startswith("GRT-SURFACE-") else None,
        "runtime_surface_ref_provenance": "REPOSITORY_MINTED" if str(connection_ref or "").startswith("GRT-SURFACE-") else None,
        "provider_connector_app_id": observation.get("provider_connector_app_id"),
        "provider_connector_app_id_provenance": provenance.get("provider_connector_app_id"),
        "provider_connector_client_id": observation.get("provider_connector_client_id"),
        "provider_connector_client_id_provenance": provenance.get("provider_connector_client_id"),
        "provider_connector_installation_id": observation.get("provider_connector_installation_id"),
        "provider_connector_installation_id_provenance": provenance.get("provider_connector_installation_id"),
        "provider_connector_slug": observation.get("provider_connector_slug"),
        "provider_connector_slug_provenance": provenance.get("provider_connector_slug"),
        "provider_native_identity_status": "PRESENT" if provider_ref else "UNAVAILABLE",
        "provider_private_values_invented": False,
        "first_seen_at": observed_at,
        "last_seen_at": observed_at,
        "seen_count": 1,
    }
    contexts = session.setdefault("provider_contexts", [])
    existing = next((item for item in contexts if item.get("provider_context_id") == context_id), None)
    if existing is None:
        contexts.append(record)
        contexts.sort(key=lambda item: item.get("provider_context_id") or "")
        return record
    first_seen = existing.get("first_seen_at") or observed_at
    seen_count = int(existing.get("seen_count") or 0) + 1
    for key, value in record.items():
        if value not in (None, "", "UNAVAILABLE"):
            existing[key] = value
    existing["first_seen_at"] = first_seen
    existing["last_seen_at"] = observed_at
    existing["seen_count"] = seen_count
    existing["provider_private_values_invented"] = False
    return existing


def _claim_for_session(claims_doc: dict, session_id: str | None) -> dict | None:
    if not session_id:
        return None
    active = [
        item for item in claims_doc.get("claims", [])
        if item.get("session_id") == session_id and item.get("status") == "ACTIVE"
    ]
    if len(active) == 1:
        return active[0]
    return None


def build_connection_envelope(
    observation: dict,
    *,
    session: dict | None,
    claims_doc: dict,
    connection_fingerprint: str | None,
    presence_event: str,
    config: dict,
) -> dict:
    relay = (session or {}).get("relay") or {}
    provenance = observation.get("field_provenance") or {}

    def p(name: str, fallback: str) -> str:
        return provenance.get(name) or fallback

    claim = _claim_for_session(claims_doc, (session or {}).get("session_id"))
    explicit_claim_id = observation.get("claim_id")
    correlated_claim_id = (claim or {}).get("claim_id") or (claim or {}).get("work_item_id")
    claim_id = explicit_claim_id or correlated_claim_id

    provider_ref = observation.get("provider_ref") or (session or {}).get("provider_conversation_ref")
    persist_url = bool((config.get("external_conversation_reference") or {}).get("persist_full_url"))
    provider_url = (session or {}).get("provider_conversation_url") if persist_url else None

    fields = {
        "gacr_session_id": _field((session or {}).get("session_id"), "CORRELATED", "PRESENCE_BINDER"),
        "client_instance_id": _field(
            observation.get("client_instance_id") or (session or {}).get("client_instance_id"),
            p("client_instance_id", "CORRELATED") if observation.get("client_instance_id") else "CORRELATED",
            "CLIENT_OR_ADAPTER_OR_SESSION",
        ),
        "provider": _field(
            observation.get("provider")
            or ((session or {}).get("provider") if (session or {}).get("provider") not in {None, "", "other"} else None),
            p("provider", "CORRELATED") if observation.get("provider") else "CORRELATED",
            "CLIENT_OR_SESSION",
        ),
        "agent_identity": _field(
            observation.get("agent_identity") or (session or {}).get("agent_identity"),
            p("agent_identity", "CORRELATED") if observation.get("agent_identity") else "CORRELATED",
            "CLIENT_OR_SESSION",
        ),
        "agent_type_or_model": _field(
            observation.get("agent_type_or_model"),
            p("agent_type_or_model", "PROVIDER_PRIVATE_UNAVAILABLE"),
            "CLIENT_OR_PROVIDER_PRIVATE",
        ),
        "repository": _field(observation.get("repository"), p("repository", "OBSERVABLE_BY_PLATFORM"), "REPOSITORY_SURFACE"),
        "repository_id": _field(observation.get("repository_id"), p("repository_id", "OBSERVABLE_BY_PLATFORM"), "REPOSITORY_SURFACE"),
        "organization": _field(
            observation.get("organization"),
            p("organization", "OBSERVABLE_BY_PLATFORM"),
            "REPOSITORY_IDENTITY",
        ),
        "git_provider": _field(observation.get("git_provider"), p("git_provider", "DERIVED_SAFE"), "REPOSITORY_SURFACE"),
        "github_actor": _field(observation.get("github_actor"), p("github_actor", "OBSERVABLE_BY_PLATFORM"), "GITHUB_EVENT_OR_GATEWAY"),
        "github_app_or_installation": _field(
            observation.get("github_app_or_installation"),
            p("github_app_or_installation", "OBSERVABLE_BY_PLATFORM"),
            "GITHUB_EVENT_OR_GATEWAY",
        ),
        "provider_connector_app_id": _field(
            observation.get("provider_connector_app_id"),
            p("provider_connector_app_id", "PROVIDER_PRIVATE_UNAVAILABLE"),
            "CLIENT_OR_CONNECTOR_SURFACE",
        ),
        "provider_connector_client_id": _field(
            observation.get("provider_connector_client_id"),
            p("provider_connector_client_id", "PROVIDER_PRIVATE_UNAVAILABLE"),
            "CLIENT_OR_CONNECTOR_SURFACE",
        ),
        "provider_connector_installation_id": _field(
            observation.get("provider_connector_installation_id"),
            p("provider_connector_installation_id", "PROVIDER_PRIVATE_UNAVAILABLE"),
            "CLIENT_OR_CONNECTOR_SURFACE",
        ),
        "provider_connector_slug": _field(
            observation.get("provider_connector_slug"),
            p("provider_connector_slug", "PROVIDER_PRIVATE_UNAVAILABLE"),
            "CLIENT_OR_CONNECTOR_SURFACE",
        ),
        "connection_method": _field(observation.get("connection_method"), p("connection_method", "DERIVED_SAFE"), "PRESENCE_OBSERVER"),
        "permissions": _field(
            observation.get("permissions"),
            p("permissions", "OBSERVABLE_BY_PLATFORM"),
            "EXPLICIT_ADAPTER_ONLY",
        ),
        "capabilities": _field(
            observation.get("capabilities") or (session or {}).get("capabilities"),
            p("capabilities", "DECLARED_BY_AGENT_OR_CLIENT") if observation.get("capabilities") else "CORRELATED",
            "CLIENT_OR_ADAPTER_OR_SESSION",
        ),
        "entry_action": _field(observation.get("entry_action"), p("entry_action", "DECLARED_BY_AGENT_OR_CLIENT"), "CLIENT_OR_ADAPTER"),
        "connection_intent": _field(observation.get("connection_intent"), p("connection_intent", "DECLARED_BY_AGENT_OR_CLIENT"), "CLIENT_OR_ADAPTER"),
        "task_id": _field(
            observation.get("task_id") or relay.get("task_id"),
            p("task_id", "DECLARED_BY_AGENT_OR_CLIENT") if observation.get("task_id") else "CORRELATED",
            "CLIENT_OR_SESSION",
        ),
        "claim_id": _field(
            claim_id,
            p("claim_id", "DECLARED_BY_AGENT_OR_CLIENT") if explicit_claim_id else "CORRELATED",
            "CLIENT_OR_CANONICAL_CLAIMS",
        ),
        "branch": _field(observation.get("branch") or relay.get("branch"), p("branch", "OBSERVABLE_BY_PLATFORM"), "REPOSITORY_SURFACE"),
        "base_branch": _field(observation.get("base_branch"), p("base_branch", "OBSERVABLE_BY_PLATFORM"), "REPOSITORY_SURFACE"),
        "HEAD": _field(observation.get("head"), p("HEAD", "OBSERVABLE_BY_PLATFORM"), "REPOSITORY_SURFACE"),
        "PR": _field(
            observation.get("pull_request") if observation.get("pull_request") is not None else relay.get("pull_request"),
            p("PR", "OBSERVABLE_BY_PLATFORM"),
            "REPOSITORY_SURFACE",
        ),
        "workflow_run_id": _field(observation.get("workflow_run_id"), p("workflow_run_id", "OBSERVABLE_BY_PLATFORM"), "GITHUB_EVENT"),
        "job_id": _field(observation.get("job_id"), p("job_id", "OBSERVABLE_BY_PLATFORM"), "GITHUB_EVENT"),
        "run_attempt": _field(observation.get("run_attempt"), p("run_attempt", "OBSERVABLE_BY_PLATFORM"), "GITHUB_EVENT"),
        "event_type": _field(observation.get("event_type"), p("event_type", "OBSERVABLE_BY_PLATFORM"), "REPOSITORY_SURFACE"),
        "delivery_or_correlation_id": _field(
            observation.get("delivery_or_correlation_id"),
            p("delivery_or_correlation_id", "OBSERVABLE_BY_PLATFORM"),
            "CONTROLLED_SURFACE",
        ),
        "connected_at": _field((session or {}).get("created_at"), "CORRELATED", "GACR_SESSION"),
        "last_seen_at": _field((session or {}).get("last_seen_at") or observation.get("observed_at"), "CORRELATED", "GACR_SESSION"),
        "heartbeat_seq": _field(observation.get("heartbeat_seq"), p("heartbeat_seq", "DECLARED_BY_AGENT_OR_CLIENT"), "CLIENT_OR_ADAPTER"),
        "lease_expires_at": _field(relay.get("lease_expires_at"), "CORRELATED", "GACR_WATCH"),
        "provider_conversation_ref": _field(
            provider_ref,
            p("provider_conversation_ref", "PROVIDER_PRIVATE_UNAVAILABLE") if provider_ref else "PROVIDER_PRIVATE_UNAVAILABLE",
            "CLIENT_OR_PROVIDER_PRIVATE",
        ),
        "provider_conversation_url": _field(
            provider_url,
            "DECLARED_BY_AGENT_OR_CLIENT" if provider_url else "PROVIDER_PRIVATE_UNAVAILABLE",
            "NOT_PERSISTED_UNLESS_POLICY_ALLOWS",
        ),
        "checkpoint": _field(observation.get("checkpoint"), p("checkpoint", "DECLARED_BY_AGENT_OR_CLIENT"), "CLIENT_OR_ADAPTER"),
        "last_action": _field(
            observation.get("last_action") or relay.get("last_action"),
            p("last_action", "DECLARED_BY_AGENT_OR_CLIENT") if observation.get("last_action") else "CORRELATED",
            "CLIENT_OR_GACR_SESSION",
        ),
        "last_evidence": _field(
            observation.get("last_evidence") or relay.get("last_evidence"),
            p("last_evidence", "DECLARED_BY_AGENT_OR_CLIENT") if observation.get("last_evidence") else "CORRELATED",
            "CLIENT_OR_GACR_SESSION",
        ),
        "connection_fingerprint": _field(connection_fingerprint, "DERIVED_SAFE", FINGERPRINT_VERSION),
    }
    envelope = {
        "schema": ENVELOPE_SCHEMA,
        "surface_class": observation.get("surface_class"),
        "presence_event": presence_event,
        "observed_at": observation.get("observed_at"),
        "fields": fields,
    }
    validate_presence_observation(envelope)
    return envelope


def _envelope_digest(envelope: dict) -> str:
    raw = json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def observe_presence(args: argparse.Namespace, config: dict, sessions: dict, claims: dict, takeovers: dict, anchor: dict) -> dict:
    observation = build_presence_observation(args, anchor, config)
    binding = bind_presence(sessions, observation, config)
    same_logical_agent = _same_logical_agent_gate(args, sessions, observation, binding)
    if same_logical_agent is not None and not same_logical_agent.get("allowed"):
        binding = {
            "state": "UNBOUND",
            "reason": same_logical_agent["reason"],
            "selected_session": None,
            "candidate_session_ids": same_logical_agent.get("candidate_session_ids") or [],
            "connection_fingerprint": binding.get("connection_fingerprint"),
            "presence_anchor": binding.get("presence_anchor"),
        }

    if binding["state"] in {"AMBIGUOUS", "UNBOUND"}:
        presence_event = "UNBOUND_ACTIVITY"
        envelope = build_connection_envelope(
            observation,
            session=None,
            claims_doc=claims,
            connection_fingerprint=binding.get("connection_fingerprint"),
            presence_event=presence_event,
            config=config,
        )
        beacon = record_beacon(
            session=None,
            event_type="UNBOUND_ACTIVITY",
            source="PRESENCE_FABRIC",
            provider=observation.get("provider"),
            provider_ref=observation.get("provider_ref"),
            client_instance_id=observation.get("client_instance_id"),
            connection_ref=observation.get("connection_ref"),
            task_id=observation.get("task_id"),
            branch=observation.get("branch"),
            pull_request=observation.get("pull_request"),
            capabilities=observation.get("capabilities"),
            observed_at=observation.get("observed_at"),
            connection_fingerprint=binding.get("connection_fingerprint"),
            connection_envelope_digest=_envelope_digest(envelope),
            surface_class=observation.get("surface_class"),
            presence_event=presence_event,
        )
        correlation = correlate_all()
        return {
            "status": "UNBOUND_ACTIVITY",
            "identity_resolution": "UNRESOLVED_SURFACE",
            "process": "GACR",
            "authority": "CP-AGENT-RELAY-001-PRESENCE-FIRST",
            "presence_event": presence_event,
            "surface_class": observation.get("surface_class"),
            "binding": {
                "state": binding["state"],
                "reason": binding["reason"],
                "selected_session_id": UNAVAILABLE,
                "candidate_session_ids": binding.get("candidate_session_ids") or [],
            },
            "connection_fingerprint": binding.get("connection_fingerprint") or UNAVAILABLE,
            "connection_envelope": envelope,
            "beacon_id": beacon.get("beacon_id"),
            "correlation": correlation,
        }

    selected = binding.get("selected_session")
    selected_provider_ref_before = (selected or {}).get("provider_conversation_ref")
    selected_connection_ref_before = (selected or {}).get("connection_ref")
    fingerprint = binding["connection_fingerprint"]
    presence_anchor = binding["presence_anchor"]

    effective_connection_ref = observation.get("connection_ref")
    if not effective_connection_ref and observation.get("provider_ref") is None:
        effective_connection_ref = f"presence:{fingerprint}"

    provider_for_core = observation.get("provider") or (selected or {}).get("provider") or "other"
    agent_for_core = observation.get("agent_identity") or (selected or {}).get("agent_identity") or "gacr-presence-observer"

    session, resolution = register_docs(
        config,
        sessions,
        repository=observation["repository"],
        agent=agent_for_core,
        provider=provider_for_core,
        provider_ref=observation.get("provider_ref"),
        provider_url=args.provider_url,
        connection_ref=effective_connection_ref,
        observed_head=observation.get("head"),
        branch=observation.get("branch"),
        task_id=observation.get("task_id"),
        pull_request=observation.get("pull_request"),
        standby=observation.get("standby", False),
        client_instance_id=observation.get("client_instance_id"),
        agent_role=observation.get("agent_role"),
        capabilities=sorted(set((observation.get("capabilities") or []) + ["GACR_AUTO_ATTACH", "GACR_PRESENCE_FIRST"])),
        wake_channels=observation.get("wake_channels") or ["POLL_REPOSITORY"],
        bridge_registration_ref=observation.get("bridge_registration_ref"),
        timestamp=parse_time(observation["observed_at"]) or now_utc(),
    )

    session["connection_fingerprint"] = fingerprint
    session["connection_fingerprint_version"] = FINGERPRINT_VERSION
    session["presence_anchor"] = presence_anchor
    if same_logical_agent is not None:
        if resolution != "CREATE":
            raise ValueError("GACR_SAME_LOGICAL_AGENT_FAILED: expected a new canonical session")
        reference = same_logical_agent["reference_session"]
        session["logical_agent_id"] = reference.get("agent_identity")
        session["logical_agent_relationship"] = "NEW_SESSION_SAME_LOGICAL_AGENT"
        session["logical_agent_reference_session_id"] = reference.get("session_id")
        session["logical_agent_continuity_id"] = same_logical_agent["continuity_id"]
        session["logical_agent_evidence_ref"] = same_logical_agent["evidence_ref"]
        session["logical_agent_evidence_source"] = (same_logical_agent.get("proof") or {}).get("source")
        session["logical_agent_authority_inherited"] = False
        session["logical_agent_claim_inherited"] = False
        session["logical_agent_takeover_accepted"] = False
    session["surface_class"] = observation.get("surface_class")
    session["connection_method"] = observation.get("connection_method")
    provider_context = _record_provider_context(session, observation)
    if observation.get("github_actor"):
        session["github_actor"] = observation["github_actor"]
    for route_field in ("entry_action", "connection_intent"):
        incoming = observation.get(route_field)
        if incoming in (None, ""):
            continue
        if resolution == "CREATE":
            session[route_field] = incoming
            session[f"{route_field}_provenance"] = "PROVIDED_BY_CLIENT"
            continue
        current = session.get(route_field)
        if current != incoming:
            raise ValueError(
                f"GACR_ROUTE_RECONCILIATION_REQUIRED:{route_field}:current={current or UNAVAILABLE}:requested={incoming}"
            )

    if same_logical_agent is not None:
        identity_resolution = "NEW_SESSION_SAME_LOGICAL_AGENT"
        presence_event = "PRESENCE_NEW_SESSION_SAME_LOGICAL_AGENT"
    elif resolution == "CREATE":
        identity_resolution = "NEW_LOGICAL_AGENT"
        presence_event = "PRESENCE_FIRST_TOUCH"
    elif (
        (observation.get("provider_ref") and observation.get("provider_ref") != selected_provider_ref_before)
        or (
            observation.get("connection_ref")
            and selected_connection_ref_before
            and observation.get("connection_ref") != selected_connection_ref_before
        )
    ):
        identity_resolution = "NEW_PROVIDER_CONTEXT_SAME_LOGICAL_AGENT"
        presence_event = "PRESENCE_RESUME"
    else:
        identity_resolution = "SAME_SESSION_RESUME"
        presence_event = "PRESENCE_RESUME"
    envelope = build_connection_envelope(
        observation,
        session=session,
        claims_doc=claims,
        connection_fingerprint=fingerprint,
        presence_event=presence_event,
        config=config,
    )
    session["connection_envelope"] = envelope
    save(sessions, claims, takeovers)

    beacon = record_beacon(
        session=session,
        event_type="AUTO_ATTACH",
        source=anchor.get("source") or observation.get("source") or "PRESENCE_FABRIC",
        provider=observation.get("provider"),
        provider_ref=observation.get("provider_ref"),
        client_instance_id=observation.get("client_instance_id"),
        connection_ref=effective_connection_ref,
        task_id=observation.get("task_id"),
        branch=observation.get("branch"),
        pull_request=observation.get("pull_request"),
        agent_role=observation.get("agent_role"),
        capabilities=sorted(set((observation.get("capabilities") or []) + ["GACR_AUTO_ATTACH", "GACR_PRESENCE_FIRST"])),
        observed_at=observation.get("observed_at"),
        checkpoint_ref=(
            same_logical_agent.get("continuity_id")
            if same_logical_agent is not None else observation.get("checkpoint")
        ),
        evidence_ref=(
            same_logical_agent.get("evidence_ref")
            if same_logical_agent is not None else observation.get("last_evidence")
        ),
        connection_fingerprint=fingerprint,
        connection_envelope_digest=_envelope_digest(envelope),
        surface_class=observation.get("surface_class"),
        presence_event=presence_event,
    )
    correlation = correlate_all()
    return {
        "status": "NEW_SESSION_SAME_LOGICAL_AGENT" if same_logical_agent is not None else resolution,
        "identity_resolution": identity_resolution,
        "core_session_resolution": resolution,
        "process": "GACR",
        "authority": "CP-AGENT-RELAY-001-PRESENCE-FIRST",
        "attachment_source": anchor.get("source"),
        "presence_event": presence_event,
        "surface_class": observation.get("surface_class"),
        "binding": {
            "state": "BOUND",
            "reason": binding["reason"],
            "selected_session_id": session.get("session_id"),
            "candidate_session_ids": binding.get("candidate_session_ids") or [session.get("session_id")],
        },
        "connection_fingerprint": fingerprint,
        "connection_envelope": envelope,
        "provider_context": provider_context,
        "session": session,
        "logical_agent_binding": (
            {
                "logical_agent_id": session.get("logical_agent_id"),
                "relationship": "NEW_SESSION_SAME_LOGICAL_AGENT",
                "reference_session_id": session.get("logical_agent_reference_session_id"),
                "continuity_id": session.get("logical_agent_continuity_id"),
                "evidence_ref": session.get("logical_agent_evidence_ref"),
                "evidence_source": session.get("logical_agent_evidence_source"),
                "claim_inherited": False,
                "mutation_authority_inherited": False,
                "takeover_accepted": False,
            }
            if same_logical_agent is not None else None
        ),
        "beacon_id": beacon.get("beacon_id"),
        "correlation": correlation,
    }


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def chronicle_anchor(max_age_seconds: int, prefer: bool = False) -> dict | None:
    if not CHRONICLE_CURRENT.exists():
        return None
    pointer = read_json(CHRONICLE_CURRENT)
    if pointer.get("status") != "ACTIVE":
        return None
    updated = parse_time(((pointer.get("updated_at") or {}).get("value")))
    if not prefer:
        if not updated:
            return None
        age = (datetime.now(timezone.utc) - updated).total_seconds()
        if age < 0 or age > max_age_seconds:
            return None
    state_path = pointer.get("state_path")
    if not state_path:
        return None
    state_file = ROOT / state_path
    if not state_file.exists():
        return None
    state = read_json(state_file)
    session = state.get("current_session")
    chronicle_id = pointer.get("chronicle_id") or state.get("chronicle_id")
    if not chronicle_id or not session:
        return None
    return {
        "source": "CONVERSATION_CHRONICLE",
        "connection_ref": f"chronicle:{chronicle_id}:{session}",
        "client_instance_id": f"chronicle:{chronicle_id}",
        "bridge_registration_ref": chronicle_id,
        "agent": "conversation-agent",
        "provider": None,
        "chronicle_id": chronicle_id,
        "chronicle_session": session,
    }


def github_anchor() -> dict | None:
    # GACR's own workflow is transport/runtime infrastructure, not a new agent.
    if (os.environ.get("GITHUB_WORKFLOW") or "").strip() in INTERNAL_GACR_WORKFLOWS:
        return None
    repository = os.environ.get("GITHUB_REPOSITORY")
    actor = os.environ.get("GITHUB_ACTOR")
    if not repository or not actor:
        return None
    run_id = os.environ.get("GITHUB_RUN_ID")
    run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT")
    sha = os.environ.get("GITHUB_SHA")
    strongest = ":".join(x for x in [run_id, run_attempt, sha] if x) or "unknown-run"
    return {
        "source": "GITHUB_ACTIONS",
        "connection_ref": f"github-actions:{repository}:{actor}:{strongest}",
        "client_instance_id": f"github-actor:{actor}",
        "bridge_registration_ref": None,
        "agent": actor,
        "provider": "github-actions",
    }


def choose_anchor(args: argparse.Namespace, config: dict) -> dict | None:
    explicit = args.connection_ref or args.provider_ref or args.provider_url or args.client_instance_id
    if explicit:
        return {
            "source": args.source or "EXPLICIT_CLIENT",
            "connection_ref": args.connection_ref,
            "client_instance_id": args.client_instance_id,
            "bridge_registration_ref": args.bridge_registration_ref,
            "agent": args.agent,
            "provider": args.provider,
        }

    max_age = int((config.get("auto_attachment") or {}).get("chronicle_freshness_seconds", 3600))
    chronicle = chronicle_anchor(max_age, prefer=args.prefer_chronicle)
    if chronicle:
        return chronicle

    github = github_anchor()
    if github:
        return github

    return None


def main() -> None:
    p = argparse.ArgumentParser(description="GACR Presence-First automatic continuity attachment")
    p.add_argument("--agent")
    p.add_argument("--provider", choices=["chatgpt","claude","codex","github-actions","human","other"])
    p.add_argument("--provider-ref")
    p.add_argument("--provider-url")
    p.add_argument("--connection-ref")
    p.add_argument("--client-instance-id")
    p.add_argument("--bridge-registration-ref")
    p.add_argument("--same-logical-agent-session-id")
    p.add_argument("--continuity-id")
    p.add_argument("--continuity-evidence-ref")
    p.add_argument("--repository")
    p.add_argument("--repository-id")
    p.add_argument("--organization")
    p.add_argument("--git-provider")
    p.add_argument("--github-actor")
    p.add_argument("--github-app-installation")
    p.add_argument("--provider-connector-app-id")
    p.add_argument("--provider-connector-client-id")
    p.add_argument("--provider-connector-installation-id")
    p.add_argument("--provider-connector-slug")
    p.add_argument("--connection-method")
    p.add_argument("--surface-class", choices=sorted(SURFACE_CLASSES))
    p.add_argument("--agent-type-model")
    p.add_argument("--permissions-json")
    p.add_argument("--observed-head")
    p.add_argument("--branch")
    p.add_argument("--base-branch")
    p.add_argument("--task-id")
    p.add_argument("--claim-id")
    p.add_argument("--pull-request", type=int)
    p.add_argument("--workflow-run-id")
    p.add_argument("--job-id")
    p.add_argument("--run-attempt")
    p.add_argument("--event-type")
    p.add_argument("--delivery-correlation-id")
    p.add_argument("--observed-at")
    p.add_argument("--heartbeat-seq", type=int)
    p.add_argument("--checkpoint")
    p.add_argument("--last-action")
    p.add_argument("--last-evidence")
    p.add_argument("--entry-action", choices=[
        "CREATE_NEW_REPOSITORY",
        "ADOPT_EXISTING_REPOSITORY",
        "MAP_EXISTING_PROJECT",
        "LAB_EVOLUTION",
        "CONTINUE_GOVERNED_WORK",
        "UNKNOWN",
    ])
    p.add_argument("--connection-intent", choices=[
        "OBSERVE",
        "CONTEXT_INTAKE",
        "INFORMATION_INTAKE",
        "WORK_REQUEST",
        "CODE_CHANGE",
        "REVIEW",
        "INFRASTRUCTURE",
        "UNKNOWN",
    ])
    p.add_argument("--standby", action="store_true")
    p.add_argument("--agent-role")
    p.add_argument("--capability", action="append")
    p.add_argument("--wake-channel", action="append", choices=["POLL_REPOSITORY","REPOSITORY_DISPATCH","EXTERNAL_BRIDGE"])
    p.add_argument("--source")
    p.add_argument("--prefer-chronicle", action="store_true")
    p.add_argument("--allow-unobservable-skip", action="store_true")
    a = p.parse_args()

    config, sessions, claims, _work, takeovers = load_all()
    if not (config.get("auto_attachment") or {}).get("enabled", False):
        raise SystemExit("GACR_AUTO_ATTACH_DISABLED")

    anchor = choose_anchor(a, config)
    if anchor is None:
        if a.allow_unobservable_skip:
            correlation = correlate_all()
            print(json.dumps({
                "status": "GACR_AUTO_ATTACH_SKIPPED",
                "process": "GACR",
                "authority": "CP-AGENT-RELAY-001-R5",
                "reason": "NO_EXTERNAL_AGENT_ANCHOR",
                "attachment_created": False,
                "correlation": correlation,
            }, indent=2, ensure_ascii=False))
            return
        raise SystemExit("GACR_AUTO_ATTACH_UNOBSERVABLE: no explicit client, fresh chronicle or external GitHub execution anchor")

    result = observe_presence(a, config, sessions, claims, takeovers, anchor)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
