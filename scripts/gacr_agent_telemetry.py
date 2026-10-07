#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(os.environ.get("GACR_ROOT") or Path(__file__).resolve().parents[1]).resolve()
GOV = ROOT / ".governance"
TEMPLATE_SOURCE = (ROOT / ".template-source").exists()

if TEMPLATE_SOURCE:
    SESSIONS_PATH = GOV / "control-plane-state" / "gacr-sessions.json"
    CLAIMS_PATH = GOV / "control-plane-state" / "gacr-claims.json"
    TAKEOVERS_PATH = GOV / "control-plane-state" / "gacr-takeovers.json"
    BEACONS_PATH = GOV / "control-plane-state" / "gacr-beacons.json"
    CORRELATIONS_PATH = GOV / "control-plane-state" / "gacr-correlations.json"
    DISPATCHES_PATH = GOV / "control-plane-state" / "gacr-dispatches.json"
    FORENSICS_PATH = GOV / "control-plane-state" / "gacr-forensics.json"
else:
    SESSIONS_PATH = GOV / "sessions" / "sessions.json"
    CLAIMS_PATH = GOV / "work" / "claims.json"
    TAKEOVERS_PATH = GOV / "agent-relay" / "takeovers.json"
    BEACONS_PATH = GOV / "agent-relay" / "beacons.json"
    CORRELATIONS_PATH = GOV / "agent-relay" / "correlations.json"
    DISPATCHES_PATH = GOV / "agent-relay" / "dispatches.json"
    FORENSICS_PATH = GOV / "agent-relay" / "forensics.json"

CONFIG_PATH = GOV / "agent-relay" / "config.json"

SAFE_GITHUB_ENV = (
    "GITHUB_REPOSITORY",
    "GITHUB_REPOSITORY_ID",
    "GITHUB_REPOSITORY_OWNER",
    "GITHUB_REPOSITORY_OWNER_ID",
    "GITHUB_ACTOR",
    "GITHUB_ACTOR_ID",
    "GITHUB_TRIGGERING_ACTOR",
    "GITHUB_EVENT_NAME",
    "GITHUB_REF",
    "GITHUB_REF_NAME",
    "GITHUB_REF_TYPE",
    "GITHUB_SHA",
    "GITHUB_BASE_REF",
    "GITHUB_HEAD_REF",
    "GITHUB_WORKFLOW",
    "GITHUB_WORKFLOW_REF",
    "GITHUB_RUN_ID",
    "GITHUB_RUN_NUMBER",
    "GITHUB_RUN_ATTEMPT",
    "GITHUB_JOB",
    "GITHUB_ACTION",
    "GITHUB_SERVER_URL",
    "GITHUB_API_URL",
    "GITHUB_GRAPHQL_URL",
)
FORBIDDEN_KEY_FRAGMENTS = ("token", "secret", "password", "private_key", "cookie", "authorization", "transcript", "prompt", "private_reasoning", "chain_of_thought", "raw_response", "response_body", "page_content")
ACTION_PHASES = {"STARTED", "COMPLETED", "FAILED", "CANCELLED"}
INTERRUPTION_CODES = {
    "CLIENT_DISCONNECTED","PROVIDER_TIMEOUT","TOOL_FAILURE","AGENT_ERROR","USER_CANCELLED",
    "NETWORK_LOSS","PROCESS_EXITED","PROVIDER_RATE_LIMIT","TOOL_RATE_LIMIT","USAGE_LIMIT",
    "QUOTA_LIMIT","CONTEXT_LIMIT","WAITING_FOR_AUTHORITY","WAITING_FOR_INPUT",
    "WAITING_FOR_REVIEW","EXTERNAL_DEPENDENCY","UNKNOWN"
}
UNAVAILABLE = "UNAVAILABLE"
LIVENESS_STATES = {"ACTIVE", "QUIET", "SUSPECTED_STALL", "STALLED", "UNKNOWN", "TERMINAL"}
PROGRESS_STATES = {"ADVANCING", "NO_RECENT_PROGRESS_EVIDENCE", "BLOCKED_IF_EXPLICITLY_OBSERVED", "UNKNOWN"}
LIVENESS_CHALLENGE_RESPONSES = {"ACK", "BUSY", "IDLE", "CHECKPOINTING", "TERMINATING"}
WORKLOAD_STATES = {
    "WORKING","IDLE","WAITING_FOR_WORK","WAITING_FOR_INPUT","WAITING_FOR_AUTHORITY",
    "WAITING_FOR_REVIEW","BLOCKED","RATE_LIMITED","QUOTA_LIMITED","CONTEXT_LIMITED",
    "CHECKPOINTING","TERMINATING","UNKNOWN"
}
BLOCKER_CODES = {
    "NONE","DEPENDENCY","COLLISION_DOMAIN","WAITING_FOR_INPUT","WAITING_FOR_AUTHORITY",
    "WAITING_FOR_REVIEW","PROVIDER_RATE_LIMIT","TOOL_RATE_LIMIT","USAGE_LIMIT","QUOTA_LIMIT",
    "CONTEXT_LIMIT","EXTERNAL_DEPENDENCY","TOOL_FAILURE","NETWORK_LOSS","UNKNOWN"
}
PROGRESS_EVENT_CLASSES = {
    "REPOSITORY_WRITE_ACTIVITY": "REPOSITORY_WRITE_ACTIVITY",
    "COMMIT_MUTATION": "COMMIT_MUTATION",
    "PULL_REQUEST_MUTATION": "PULL_REQUEST_MUTATION",
    "CHECKPOINT_ADVANCED": "CHECKPOINT_ADVANCED",
    "WORK_ITEM_ADVANCED": "WORK_ITEM_ADVANCED",
}
BLOCKED_EVENT_TYPES = {"WORK_BLOCKED", "BLOCKED"}
SHARED_INTEGRATION_REQUIRED = True


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def read_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return default or {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def available(value):
    return value if value not in (None, "") else UNAVAILABLE


def runtime_config() -> dict:
    config = read_json(CONFIG_PATH, {})
    return {
        "heartbeat_interval_seconds": int(config.get("heartbeat_interval_seconds", 300)),
        "suspected_stall_after_seconds": int(config.get("suspected_stall_after_seconds", 900)),
        "stalled_after_seconds": int(config.get("stalled_after_seconds", 1800)),
        "progress_recency_seconds": int(config.get("progress_recency_seconds", config.get("stalled_after_seconds", 1800))),
    }


def latest_iso(values: list[str | None]) -> str | None:
    parsed = [(parse_iso(value), value) for value in values if value]
    parsed = [(dt, value) for dt, value in parsed if dt is not None]
    if not parsed:
        return None
    parsed.sort(key=lambda pair: pair[0])
    return parsed[-1][1]


def digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def runtime_id(prefix: str, seed: object) -> str:
    return prefix + digest(seed)[:12]


def git_value(*args: str) -> str | None:
    cp = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
    return cp.stdout.strip() if cp.returncode == 0 and cp.stdout.strip() else None


def repository_name() -> str:
    env = os.environ.get("GITHUB_REPOSITORY")
    if env:
        return env
    remote = git_value("remote", "get-url", "origin")
    if remote:
        m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", remote)
        if m:
            return m.group(1)
    return "UNKNOWN_REPOSITORY"


def provider_ref_from_url(provider: str | None, value: str | None) -> str | None:
    if not provider or not value:
        return None
    if provider == "chatgpt":
        parsed = urlparse(value)
        m = re.fullmatch(r"/c/([A-Za-z0-9-]+)", parsed.path.rstrip("/"))
        if parsed.netloc in {"chatgpt.com", "www.chatgpt.com"} and m:
            return m.group(1)
    return None


def safe_event_context() -> dict:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not Path(event_path).exists():
        return {}
    raw = read_json(Path(event_path), {})
    sender = raw.get("sender") or {}
    installation = raw.get("installation") or {}
    repository = raw.get("repository") or {}
    repo_owner = repository.get("owner") or {}
    pr = raw.get("pull_request") or {}
    issue = raw.get("issue") or {}
    head = pr.get("head") or {}
    base = pr.get("base") or {}
    return {
        "sender": {
            "login": sender.get("login"),
            "id": sender.get("id"),
            "type": sender.get("type"),
        },
        "installation_id": installation.get("id"),
        "repository": {
            "id": repository.get("id"),
            "full_name": repository.get("full_name"),
            "owner_login": repo_owner.get("login"),
            "owner_id": repo_owner.get("id"),
            "default_branch": repository.get("default_branch"),
        },
        "pull_request": {
            "number": pr.get("number") or raw.get("number"),
            "head_ref": head.get("ref"),
            "head_sha": head.get("sha"),
            "base_ref": base.get("ref"),
            "base_sha": base.get("sha"),
        } if pr else None,
        "issue_number": issue.get("number"),
    }


def safe_github_context() -> dict:
    env = {key: os.environ.get(key) for key in SAFE_GITHUB_ENV if os.environ.get(key)}
    return {
        "environment": env,
        "event": safe_event_context(),
    }


def assert_secretless(value: object) -> None:
    def walk(node: object, path: str = "") -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                lowered = str(key).lower()
                if any(fragment in lowered for fragment in FORBIDDEN_KEY_FRAGMENTS):
                    raise ValueError(f"forbidden telemetry key at {path}/{key}")
                walk(child, f"{path}/{key}")
        elif isinstance(node, list):
            for index, child in enumerate(node):
                walk(child, f"{path}/{index}")
        elif isinstance(node, str):
            if "-----BEGIN PRIVATE KEY-----" in node or node.startswith("ghp_") or node.startswith("github_pat_"):
                raise ValueError(f"secret-like telemetry value at {path}")
    walk(value)


def session_by_id(sessions: dict, session_id: str | None) -> dict | None:
    if not session_id:
        return None
    return next((s for s in sessions.get("sessions", []) if s.get("session_id") == session_id), None)


def record_beacon(
    *,
    session: dict | None = None,
    event_type: str,
    provider: str | None = None,
    provider_ref: str | None = None,
    provider_url: str | None = None,
    client_instance_id: str | None = None,
    connection_ref: str | None = None,
    connection_fingerprint: str | None = None,
    claim_id: str | None = None,
    connection_envelope_digest: str | None = None,
    surface_class: str | None = None,
    presence_event: str | None = None,
    task_id: str | None = None,
    branch: str | None = None,
    pull_request: int | None = None,
    agent_role: str | None = None,
    capabilities: list[str] | None = None,
    source: str | None = None,
    observed_at: str | None = None,
    action_id: str | None = None,
    action_label: str | None = None,
    action_phase: str | None = None,
    tool_name: str | None = None,
    tool_call_id: str | None = None,
    outcome: str | None = None,
    written_head_sha: str | None = None,
    checkpoint_ref: str | None = None,
    evidence_ref: str | None = None,
    interruption_code: str | None = None,
    workload_state: str | None = None,
    blocker_code: str | None = None,
    capacity_slots: int | None = None,
    max_parallel_tasks: int | None = None,
    retry_after_at: str | None = None,
) -> dict:
    store = read_json(BEACONS_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    timestamp = observed_at or now_iso()
    if action_phase and action_phase not in ACTION_PHASES:
        raise ValueError("unsupported action phase")
    if interruption_code and interruption_code not in INTERRUPTION_CODES:
        raise ValueError("unsupported interruption code")
    if workload_state and workload_state not in WORKLOAD_STATES:
        raise ValueError("unsupported workload state")
    if blocker_code and blocker_code not in BLOCKER_CODES:
        raise ValueError("unsupported blocker code")
    if capacity_slots is not None and capacity_slots < 0:
        raise ValueError("capacity_slots must be >= 0")
    if max_parallel_tasks is not None and max_parallel_tasks < 0:
        raise ValueError("max_parallel_tasks must be >= 0")
    if retry_after_at and parse_iso(retry_after_at) is None:
        raise ValueError("retry_after_at must be ISO-8601")
    relay = (session or {}).get("relay") or {}
    resolved_provider = provider or (session or {}).get("provider")
    resolved_provider_ref = (
        provider_ref
        or provider_ref_from_url(resolved_provider, provider_url)
        or (session or {}).get("provider_conversation_ref")
    )
    resolved_branch = branch or relay.get("branch") or os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME") or git_value("branch", "--show-current")
    resolved_pr = pull_request if pull_request is not None else relay.get("pull_request")
    resolved_task = task_id or relay.get("task_id")
    github = safe_github_context()
    detected_source = source or ("GITHUB_ACTIONS" if os.environ.get("GITHUB_ACTIONS") == "true" else "LOCAL_AGENT")
    github_env = github.get("environment") or {}
    github_event = github.get("event") or {}
    resolved_actor = github_env.get("GITHUB_ACTOR") or (github_event.get("sender") or {}).get("login")
    resolved_installation = github_event.get("installation_id")
    resolved_fingerprint = connection_fingerprint or (session or {}).get("connection_fingerprint")

    envelope = {
        "observed_at": timestamp,
        "source": detected_source,
        "event_type": event_type,
        "repository": (session or {}).get("repository") or repository_name(),
        "session_id": (session or {}).get("session_id"),
        "provider": resolved_provider,
        "provider_conversation_ref": resolved_provider_ref,
        "client_instance_id": client_instance_id or (session or {}).get("client_instance_id"),
        "connection_ref": connection_ref or (session or {}).get("connection_ref"),
        "connection_fingerprint": resolved_fingerprint,
        "claim_id": claim_id,
        "connection_envelope_digest": connection_envelope_digest,
        "surface_class": surface_class or (session or {}).get("surface_class"),
        "presence_event": presence_event,
        "agent_identity": (session or {}).get("agent_identity"),
        "agent_role": agent_role or (session or {}).get("agent_role"),
        "capabilities": sorted(set(capabilities or (session or {}).get("capabilities") or [])),
        "task_id": resolved_task,
        "branch": resolved_branch,
        "pull_request": resolved_pr,
        "observed_head_sha": (session or {}).get("last_observed_head_sha") or os.environ.get("GITHUB_SHA") or git_value("rev-parse", "HEAD"),
        "action_id": action_id,
        "action_label": action_label,
        "action_phase": action_phase,
        "tool_name": tool_name,
        "tool_call_id": tool_call_id,
        "outcome": outcome,
        "written_head_sha": written_head_sha,
        "checkpoint_ref": checkpoint_ref,
        "evidence_ref": evidence_ref,
        "interruption_code": interruption_code,
        "workload_state": workload_state,
        "blocker_code": blocker_code,
        "capacity_slots": capacity_slots,
        "max_parallel_tasks": max_parallel_tasks,
        "retry_after_at": retry_after_at,
        "github_actor": resolved_actor,
        "github_installation_id": resolved_installation,
        "github_workflow": github_env.get("GITHUB_WORKFLOW"),
        "github_run_id": github_env.get("GITHUB_RUN_ID"),
        "github_run_attempt": github_env.get("GITHUB_RUN_ATTEMPT"),
        "github_job": github_env.get("GITHUB_JOB"),
        "github": github,
    }
    assert_secretless(envelope)
    context_digest = digest(envelope)
    dedupe_key = digest({
        "session_id": envelope["session_id"],
        "event_type": event_type,
        "context_digest": context_digest,
        "run_id": github.get("environment", {}).get("GITHUB_RUN_ID"),
        "run_attempt": github.get("environment", {}).get("GITHUB_RUN_ATTEMPT"),
    })
    existing = next((x for x in store.get("items", []) if x.get("dedupe_key") == dedupe_key), None)
    if existing:
        return existing
    item = {
        "beacon_id": runtime_id("GACR-B-", {"dedupe_key": dedupe_key, "observed_at": timestamp}),
        **envelope,
        "context_digest": context_digest,
        "dedupe_key": dedupe_key,
    }
    store.setdefault("items", []).append(item)
    store["revision"] = int(store.get("revision", 0)) + 1
    write_json(BEACONS_PATH, store)
    return item

def correlation_score(beacon: dict, session: dict) -> tuple[int, list[str], bool]:
    """Legacy compatibility wrapper.

    Numeric values are not Correlator authority and are not used by correlate_all.
    They remain only so existing callers can recognize excluded terminal sessions.
    """
    if beacon.get("repository") != session.get("repository") or _terminal_session(session):
        return -1, [], False
    result = correlate_beacon(beacon, {"sessions": [session]}, {"claims": []})
    level = result.get("level")
    compatibility = {"EXACT": 100, "STRONG": 7, "PROBABLE": 4, "AMBIGUOUS": 4, "UNKNOWN": 0}
    return compatibility.get(level, 0), result.get("reasons") or [], level == "EXACT"

def correlate_all() -> dict:
    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    claims = read_json(CLAIMS_PATH, {"claims": []})
    beacons = read_json(BEACONS_PATH, {"items": []})
    store = read_json(CORRELATIONS_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    known = {x.get("beacon_id"): x for x in store.get("items", [])}
    changes = []

    for beacon in beacons.get("items", []):
        result = correlate_beacon(beacon, sessions, claims)
        selected = result.get("selected_session_id")
        level = result.get("level") or "UNKNOWN"
        candidates = result.get("candidate_session_ids") or []
        reasons = result.get("reasons") or []

        previous = known.get(beacon.get("beacon_id"))
        previous_unbound = (previous or {}).get("unbound_activity")
        unbound_activity = None
        if selected is None:
            unbound_activity = {
                "observation_id": beacon.get("beacon_id"),
                "repository": beacon.get("repository"),
                "observed_at": available(beacon.get("observed_at")),
                "activity_class": available(beacon.get("event_type")),
                "safe_envelope_digest": available(beacon.get("connection_envelope_digest") or beacon.get("context_digest")),
                "candidate_session_ids": candidates[:10],
                "correlation_level": level,
                "reasons": reasons,
                "status": "UNBOUND",
                "reconciled_session_id": UNAVAILABLE,
                "reconciled_at": UNAVAILABLE,
            }
        elif previous_unbound and previous_unbound.get("status") == "UNBOUND":
            unbound_activity = {
                **previous_unbound,
                "candidate_session_ids": candidates[:10],
                "correlation_level": level,
                "reasons": reasons,
                "status": "RECONCILED",
                "reconciled_session_id": selected,
                "reconciled_at": now_iso(),
            }
        elif previous_unbound and previous_unbound.get("status") == "RECONCILED":
            if previous_unbound.get("reconciled_session_id") == selected:
                unbound_activity = previous_unbound
            else:
                unbound_activity = {
                    **previous_unbound,
                    "status": "SUPERSEDED",
                    "superseded_by_session_id": selected,
                    "superseded_at": now_iso(),
                }

        value = {
            "correlation_id": runtime_id("GACR-C-", {"beacon_id": beacon.get("beacon_id")}),
            "beacon_id": beacon.get("beacon_id"),
            **result,
            "evaluated_at": now_iso(),
        }
        if unbound_activity is not None:
            value["unbound_activity"] = unbound_activity

        stable_keys = (
            "level", "selected_session_id", "candidate_session_ids", "reasons",
            "confidence", "binding_status", "provider_identity_inferred", "provider_conversation_ref",
            "unbound_activity",
        )
        if previous:
            if {k: previous.get(k) for k in stable_keys} == {k: value.get(k) for k in stable_keys}:
                continue
            store["items"][store["items"].index(previous)] = value
        else:
            store.setdefault("items", []).append(value)
        changes.append(value)

    if changes:
        store["revision"] = int(store.get("revision", 0)) + 1
        write_json(CORRELATIONS_PATH, store)
    return {"changed": len(changes), "items": changes}

def unbound_activity_projection() -> dict:
    correlations = read_json(CORRELATIONS_PATH, {"items": []})
    items = []
    for correlation in correlations.get("items", []):
        activity = correlation.get("unbound_activity")
        if activity:
            items.append(activity)
    items.sort(key=lambda item: (str(item.get("observed_at") or ""), str(item.get("observation_id") or "")))
    return {
        "process": "GACR",
        "model": "UNBOUND_ACTIVITY",
        "derived_from": "EXISTING_BEACON_AND_CORRELATOR_STORES",
        "items": items,
    }


def compatible_standby(
    sessions: dict,
    stalled_session_id: str,
    claims_doc: dict | None = None,
    work_doc: dict | None = None,
    takeover: dict | None = None,
) -> dict | None:
    predecessor = session_by_id(sessions, stalled_session_id)
    if not predecessor:
        return None
    takeover = takeover or {
        "stalled_session_id": stalled_session_id,
        "task_id": (predecessor.get("relay") or {}).get("task_id"),
        "branch": (predecessor.get("relay") or {}).get("branch"),
        "pull_request": (predecessor.get("relay") or {}).get("pull_request"),
    }
    decision = select_compatible_standby(
        sessions,
        claims_doc or {"claims": []},
        work_doc or {"items": []},
        takeover,
    )
    return session_by_id(sessions, decision.get("selected_session_id"))

def dispatch_open_takeovers() -> dict:
    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    claims = read_json(CLAIMS_PATH, {"claims": []})
    work = read_json(GOV / "work" / "work-items.json", {"items": []})
    takeovers = read_json(TAKEOVERS_PATH, {"items": []})
    store = read_json(DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    changes = []
    takeover_changed = False

    for takeover in takeovers.get("items", []):
        if takeover.get("status") not in {"READY_FOR_RECONCILIATION", "OFFERED", "ACCEPTED"}:
            continue

        target_id = takeover.get("accepted_by_session_id") if takeover.get("status") == "ACCEPTED" else takeover.get("offered_to_session_id")
        decision = None
        if takeover.get("status") != "ACCEPTED":
            decision = select_compatible_standby(sessions, claims, work, takeover)
            selected = decision.get("selected_session_id")
            if target_id:
                evaluation = next((x for x in decision.get("evaluations", []) if x.get("session_id") == target_id), None)
                if not evaluation or evaluation.get("status") != "ELIGIBLE":
                    continue
            elif selected:
                target_id = selected
                takeover["offered_to_session_id"] = selected
                takeover["status"] = "OFFERED"
                takeover["compatibility_selection"] = {
                    "selected_session_id": selected,
                    "selection_method": decision.get("selection_method"),
                    "evaluations": decision.get("evaluations"),
                    "grants_write_authority": False,
                }
                takeover_changed = True

        if not target_id:
            continue
        target = session_by_id(sessions, target_id)
        if not target:
            continue

        existing = next((
            x for x in store.get("items", [])
            if x.get("takeover_id") == takeover.get("takeover_id")
            and x.get("target_session_id") == target_id
            and x.get("status") not in {"CANCELLED", "EXPIRED"}
        ), None)
        if existing:
            if takeover.get("status") == "ACCEPTED" and existing.get("status") != "ACTIVATED":
                existing["status"] = "ACTIVATED"
                existing["activated_at"] = now_iso()
                existing["claim_transfer_confirmed_after_accept"] = True
                changes.append(existing)
            continue

        wake_channels = set(target.get("wake_channels") or [])
        delivery = ["POLL_REPOSITORY"]
        if "REPOSITORY_DISPATCH" in wake_channels:
            delivery.append("REPOSITORY_DISPATCH")
        if "EXTERNAL_BRIDGE" in wake_channels and target.get("bridge_registration_ref"):
            delivery.append("EXTERNAL_BRIDGE")

        package = build_takeover_package(
            takeover.get("stalled_session_id"),
            target_id,
            sessions_doc=sessions,
            claims_doc=claims,
            work_doc=work,
            takeovers_doc=takeovers,
        )
        item = {
            "dispatch_id": runtime_id("GACR-D-", {"takeover_id": takeover.get("takeover_id"), "target_session_id": target_id}),
            "takeover_id": takeover.get("takeover_id"),
            "stalled_session_id": takeover.get("stalled_session_id"),
            "target_session_id": target_id,
            "target_client_instance_id": target.get("client_instance_id"),
            "bridge_registration_ref": target.get("bridge_registration_ref"),
            "status": "ACTIVATED" if takeover.get("status") == "ACCEPTED" else "READY",
            "delivery_modes": delivery,
            "created_at": now_iso(),
            "task_id": takeover.get("task_id"),
            "branch": takeover.get("branch"),
            "pull_request": takeover.get("pull_request"),
            "last_observed_head_sha": takeover.get("last_observed_head_sha"),
            "requires_exact_head_reconciliation": True,
            "may_write_before_takeover_accept": False,
            "compatibility": decision,
            "takeover_package": package,
        }
        store.setdefault("items", []).append(item)
        changes.append(item)

    if takeover_changed:
        takeovers["revision"] = int(takeovers.get("revision", 0)) + 1
        write_json(TAKEOVERS_PATH, takeovers)
    if changes:
        store["revision"] = int(store.get("revision", 0)) + 1
        write_json(DISPATCHES_PATH, store)
    return {"changed": len(changes), "items": changes}

def _session_beacons(session_id: str, beacons: dict, correlations: dict) -> list[dict]:
    selected = {x.get("beacon_id") for x in correlations.get("items", []) if x.get("selected_session_id") == session_id}
    values = [x for x in beacons.get("items", []) if x.get("session_id") == session_id or x.get("beacon_id") in selected]
    values.sort(key=lambda x: (x.get("observed_at") or "", x.get("beacon_id") or ""))
    return values


def _progress_evidence(items: list[dict]) -> list[dict]:
    evidence = []
    for item in items:
        event_type = item.get("event_type")
        phase = item.get("action_phase")
        evidence_class = None
        if event_type in BLOCKED_EVENT_TYPES:
            evidence_class = "EXPLICIT_BLOCKED"
        elif phase == "COMPLETED":
            evidence_class = "ACTION_COMPLETED"
        elif event_type in PROGRESS_EVENT_CLASSES:
            evidence_class = PROGRESS_EVENT_CLASSES[event_type]
        elif item.get("written_head_sha"):
            evidence_class = "WRITTEN_HEAD_MOVEMENT"
        elif event_type == "CHECKPOINT_ADVANCED" and item.get("checkpoint_ref"):
            evidence_class = "CHECKPOINT_ADVANCED"
        if not evidence_class:
            continue
        evidence.append({
            "class": evidence_class,
            "beacon_id": item.get("beacon_id"),
            "observed_at": item.get("observed_at"),
            "event_type": event_type,
            "action_id": item.get("action_id"),
            "action_phase": phase,
            "outcome": item.get("outcome"),
            "written_head_sha": item.get("written_head_sha"),
            "checkpoint_ref": item.get("checkpoint_ref"),
            "evidence_ref": item.get("evidence_ref"),
        })
    evidence.sort(key=lambda item: (item.get("observed_at") or "", item.get("beacon_id") or ""))
    return evidence


def session_signal_projection(session_id: str, *, generated_at: str | None = None) -> dict:
    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    beacons = read_json(BEACONS_PATH, {"items": []})
    correlations = read_json(CORRELATIONS_PATH, {"items": []})
    session = session_by_id(sessions, session_id)
    if not session:
        raise ValueError("session not found")
    timestamp = generated_at or now_iso()
    generated = parse_iso(timestamp)
    config = runtime_config()
    relay = session.get("relay") or {}
    related = _session_beacons(session_id, beacons, correlations)

    beacon_times = [item.get("observed_at") for item in related]
    last_activity = latest_iso([session.get("last_seen_at"), *beacon_times])
    last_liveness = latest_iso([
        relay.get("last_heartbeat_at"),
        session.get("last_seen_at"),
        *beacon_times,
    ])

    relay_state = relay.get("state")
    if session.get("status") == "CLOSED" or relay_state in {"CLOSED", "HANDOFF_STALLED"}:
        liveness_state = "TERMINAL"
    elif relay_state in {"STALLED", "TAKEOVER_READY"}:
        liveness_state = "STALLED"
    elif relay_state == "SUSPECTED_STALL":
        liveness_state = "SUSPECTED_STALL"
    elif not last_liveness or not generated:
        liveness_state = "UNKNOWN"
    else:
        last_liveness_dt = parse_iso(last_liveness)
        if not last_liveness_dt:
            liveness_state = "UNKNOWN"
        else:
            age = max(0.0, (generated - last_liveness_dt).total_seconds())
            if age <= config["heartbeat_interval_seconds"]:
                liveness_state = "ACTIVE"
            elif age < config["suspected_stall_after_seconds"]:
                liveness_state = "QUIET"
            elif age < config["stalled_after_seconds"]:
                liveness_state = "SUSPECTED_STALL"
            else:
                liveness_state = "STALLED"

    progress_items = _progress_evidence(related)
    last_progress_evidence = progress_items[-1] if progress_items else None
    last_progress = last_progress_evidence.get("observed_at") if last_progress_evidence else None
    if last_progress_evidence and last_progress_evidence.get("class") == "EXPLICIT_BLOCKED":
        progress_state = "BLOCKED_IF_EXPLICITLY_OBSERVED"
    elif last_progress_evidence and generated and parse_iso(last_progress):
        progress_age = max(0.0, (generated - parse_iso(last_progress)).total_seconds())
        progress_state = "ADVANCING" if progress_age <= config["progress_recency_seconds"] else "NO_RECENT_PROGRESS_EVIDENCE"
    elif related or last_liveness:
        progress_state = "NO_RECENT_PROGRESS_EVIDENCE"
    else:
        progress_state = "UNKNOWN"

    result = {
        "session_id": session_id,
        "generated_at": timestamp,
        "last_activity_at": available(last_activity),
        "last_liveness_evidence_at": available(last_liveness),
        "last_progress_at": available(last_progress),
        "liveness": {
            "state": liveness_state,
            "last_evidence_at": available(last_liveness),
            "lease_expires_at": available(relay.get("lease_expires_at")),
            "watch_relay_state": available(relay_state),
        },
        "progress": {
            "state": progress_state,
            "last_progress_at": available(last_progress),
            "last_progress_evidence": available(last_progress_evidence),
        },
    }
    assert_secretless(result)
    return result


def evaluate_liveness_challenge(
    *,
    session_id: str,
    challenge_id: str,
    response: str | None,
    observed_at: str | None = None,
) -> dict:
    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    if not session_by_id(sessions, session_id):
        raise ValueError("session not found")
    timestamp = observed_at or now_iso()
    if response is None:
        result = {
            "challenge_id": challenge_id,
            "session_id": session_id,
            "status": "LIVENESS_CHALLENGE_TIMEOUT",
            "response": UNAVAILABLE,
            "observed_at": timestamp,
            "cause": UNAVAILABLE,
            "optional": True,
        }
    else:
        normalized = response.strip().upper()
        if normalized not in LIVENESS_CHALLENGE_RESPONSES:
            raise ValueError("unsupported liveness challenge response")
        result = {
            "challenge_id": challenge_id,
            "session_id": session_id,
            "status": "LIVENESS_CHALLENGE_ACK",
            "response": normalized,
            "observed_at": timestamp,
            "cause": UNAVAILABLE,
            "optional": True,
        }
    assert_secretless(result)
    return result


def _last_value(items: list[dict], key: str):
    for item in reversed(items):
        value=item.get(key)
        if value not in (None,""):
            return value
    return None


def _action_projection(items: list[dict]) -> dict:
    last_started=last_completed=last_tool_call=None
    open_actions={}
    for item in items:
        phase=item.get("action_phase"); label=item.get("action_label"); aid=item.get("action_id") or label
        if item.get("tool_name") or item.get("tool_call_id"):
            last_tool_call={"beacon_id":item.get("beacon_id"),"observed_at":item.get("observed_at"),"tool_name":item.get("tool_name"),"tool_call_id":item.get("tool_call_id"),"action_id":item.get("action_id"),"action_label":label,"phase":phase,"outcome":item.get("outcome")}
        if phase=="STARTED":
            last_started={"beacon_id":item.get("beacon_id"),"observed_at":item.get("observed_at"),"action_id":item.get("action_id"),"action_label":label,"tool_name":item.get("tool_name"),"tool_call_id":item.get("tool_call_id")}
            if aid: open_actions[str(aid)]=last_started
        elif phase in {"COMPLETED","FAILED","CANCELLED"}:
            last_completed={"beacon_id":item.get("beacon_id"),"observed_at":item.get("observed_at"),"action_id":item.get("action_id"),"action_label":label,"phase":phase,"outcome":item.get("outcome"),"written_head_sha":item.get("written_head_sha"),"checkpoint_ref":item.get("checkpoint_ref"),"evidence_ref":item.get("evidence_ref")}
            if aid: open_actions.pop(str(aid),None)
    return {"last_action_started":last_started,"last_action_completed":last_completed,"last_tool_call":last_tool_call,"in_flight_action":list(open_actions.values())[-1] if open_actions else None}


def _interruption_classification(session: dict, generated_at: str):
    relay=session.get("relay") or {}; state=relay.get("state"); generated=parse_iso(generated_at); lease=parse_iso(relay.get("lease_expires_at"))
    expired=bool(generated and lease and generated>=lease)
    mapping={
        "HANDOFF_STALLED":("TAKEOVER_COMPLETED_AFTER_STALL","TERMINAL_PREDECESSOR"),
        "TAKEOVER_READY":("LEASE_EXPIRED_STALL","TAKEOVER_RECONCILIATION_REQUIRED"),
        "STALLED":("STALLED_STATE_OBSERVED","TAKEOVER_PREPARATION_REQUIRED"),
        "SUSPECTED_STALL":("HEARTBEAT_LATE","WAIT_OR_RESCAN"),
        "CLOSED":("SESSION_CLOSED","TERMINAL"),
        "STANDBY":("NO_INTERRUPTION_OBSERVED","STANDBY"),
    }
    if state in mapping:
        a,b=mapping[state]; return a,b,expired
    if state=="ACTIVE" and expired: return "LEASE_EXPIRED_AWAITING_WATCH_SCAN","WATCH_SCAN_REQUIRED",expired
    if state=="ACTIVE": return "NO_INTERRUPTION_OBSERVED","CONTINUE_CURRENT_SESSION",expired
    return "UNKNOWN_STATE","RECONCILIATION_REQUIRED",expired


def build_interruption_forensics(session_id: str, *, persist: bool=True, generated_at: str|None=None) -> dict:
    sessions=read_json(SESSIONS_PATH,{"sessions":[]}); claims=read_json(CLAIMS_PATH,{"claims":[]}); takeovers=read_json(TAKEOVERS_PATH,{"items":[]})
    beacons=read_json(BEACONS_PATH,{"items":[]}); correlations=read_json(CORRELATIONS_PATH,{"items":[]}); dispatches=read_json(DISPATCHES_PATH,{"items":[]})
    store=read_json(FORENSICS_PATH,{"schema_version":"1.0.0","revision":0,"items":[]}); session=session_by_id(sessions,session_id)
    if not session: raise ValueError("session not found")
    timestamp=generated_at or now_iso(); relay=session.get("relay") or {}; related=_session_beacons(session_id,beacons,correlations); actions=_action_projection(related)
    active=[{"work_item_id":c.get("work_item_id"),"collision_domains":c.get("collision_domains") or [],"claimed_head_sha":c.get("claimed_head_sha")} for c in claims.get("claims",[]) if c.get("session_id")==session_id and c.get("status")=="ACTIVE"]
    tos=[x for x in takeovers.get("items",[]) if session_id in {x.get("stalled_session_id"),x.get("offered_to_session_id"),x.get("accepted_by_session_id")}]; tos.sort(key=lambda x:(x.get("created_at") or "",x.get("takeover_id") or ""))
    ds=[x for x in dispatches.get("items",[]) if session_id in {x.get("stalled_session_id"),x.get("target_session_id")}]; ds.sort(key=lambda x:(x.get("created_at") or "",x.get("dispatch_id") or ""))
    classification,recoverability,expired=_interruption_classification(session,timestamp)
    explicit=_last_value(related,"interruption_code")
    cause={"status":"OBSERVED","code":explicit,"confidence":"DIRECT_SIGNAL","note":None} if explicit not in (None,"","UNKNOWN") else {"status":"UNOBSERVED","code":"UNOBSERVED_EXTERNAL_CAUSE","confidence":"NONE","note":"GACR never infers browser crash, provider timeout, network loss or tool failure from missing heartbeat alone."}
    last_observed=_last_value(related,"observed_head_sha") or session.get("last_observed_head_sha"); last_written=_last_value(related,"written_head_sha")
    checkpoint=_last_value(related,"checkpoint_ref"); evidence=_last_value(related,"evidence_ref") or relay.get("last_evidence")
    core={"process":"GACR","authority":"CP-AGENT-RELAY-001-R3","session_id":session_id,"repository":session.get("repository"),"classification":classification,"recoverability":recoverability,"cause":cause,
      "liveness":{"session_status":session.get("status"),"relay_state":relay.get("state"),"last_seen_at":session.get("last_seen_at"),"last_heartbeat_at":relay.get("last_heartbeat_at"),"lease_expires_at":relay.get("lease_expires_at"),"lease_expired_at_analysis":expired,"stalled_at":relay.get("stalled_at")},
      "work":{"task_id":relay.get("task_id"),"branch":relay.get("branch"),"pull_request":relay.get("pull_request"),"starting_head_sha":session.get("starting_head_sha"),"last_observed_head_sha":last_observed,"last_written_head_sha":last_written,"active_claims":active,"lock_observation":"NO_INDEPENDENT_LOCK_STORE; CLAIMS_AND_COLLISION_DOMAINS_ARE_CANONICAL"},
      "actions":actions,"last_checkpoint_ref":checkpoint,"last_evidence_ref":evidence,"last_takeover":tos[-1] if tos else None,"last_dispatch":ds[-1] if ds else None,
      "resume_point":{"task_id":relay.get("task_id"),"branch":relay.get("branch"),"pull_request":relay.get("pull_request"),"last_observed_head_sha":last_observed,"last_written_head_sha":last_written,"checkpoint_ref":checkpoint,"evidence_ref":evidence,"active_claim_work_items":[x.get("work_item_id") for x in active],"collision_domains":sorted({d for x in active for d in x.get("collision_domains",[]) if d}),"in_flight_action":actions.get("in_flight_action"),"last_completed_action":actions.get("last_action_completed"),"requires_exact_head_reobservation":True,"may_replay_in_flight_action_without_reconciliation":False},
      "evidence_counts":{"beacons":len(related),"takeovers":len(tos),"dispatches":len(ds),"active_claims":len(active)}}
    ad=digest(core); report={"forensic_id":runtime_id("GACR-F-",{"repository":session.get("repository"),"session_id":session_id}),"generated_at":timestamp,**core,"analysis_digest":ad}; assert_secretless(report)
    if persist:
        prev=next((x for x in store.get("items",[]) if x.get("session_id")==session_id),None)
        if prev and prev.get("analysis_digest")==ad: return prev
        if prev: store["items"][store["items"].index(prev)]=report
        else: store.setdefault("items",[]).append(report)
        store["revision"]=int(store.get("revision",0))+1; write_json(FORENSICS_PATH,store)
    return report


def build_forensics_all() -> dict:
    sessions=read_json(SESSIONS_PATH,{"sessions":[]}); before=read_json(FORENSICS_PATH,{"items":[]}); old={x.get("session_id"):x.get("analysis_digest") for x in before.get("items",[])}
    reports=[]; changed=0
    for session in sessions.get("sessions",[]):
        if (session.get("relay") or {}).get("process")!="GACR": continue
        report=build_interruption_forensics(session.get("session_id"),persist=True); reports.append(report)
        if old.get(session.get("session_id"))!=report.get("analysis_digest"): changed+=1
    return {"changed":changed,"items":reports}


def agent_context(session_id: str, *, generated_at: str | None = None) -> dict:
    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    claims = read_json(CLAIMS_PATH, {"claims": []})
    takeovers = read_json(TAKEOVERS_PATH, {"items": []})
    beacons = read_json(BEACONS_PATH, {"items": []})
    correlations = read_json(CORRELATIONS_PATH, {"items": []})
    dispatches = read_json(DISPATCHES_PATH, {"items": []})
    session = session_by_id(sessions, session_id)
    if not session:
        raise ValueError("session not found")

    timestamp = generated_at or now_iso()
    relay = session.get("relay") or {}
    related = _session_beacons(session_id, beacons, correlations)
    actions = _action_projection(related)
    signals = session_signal_projection(session_id, generated_at=timestamp)
    active_claims = [x for x in claims.get("claims", []) if x.get("session_id") == session_id and x.get("status") == "ACTIVE"]
    related_takeovers = [x for x in takeovers.get("items", []) if x.get("stalled_session_id") == session_id or x.get("offered_to_session_id") == session_id or x.get("accepted_by_session_id") == session_id]
    related_dispatches = [x for x in dispatches.get("items", []) if x.get("target_session_id") == session_id or x.get("stalled_session_id") == session_id]
    open_takeover = next((
        x for x in reversed(related_takeovers)
        if x.get("stalled_session_id") == session_id and x.get("status") in {"READY_FOR_RECONCILIATION", "OFFERED"}
    ), None)
    forensics = build_interruption_forensics(session_id, persist=False, generated_at=timestamp)
    beacon_ids = [x.get("beacon_id") for x in related]
    related_correlations = [
        x for x in correlations.get("items", [])
        if x.get("selected_session_id") == session_id or x.get("beacon_id") in beacon_ids
    ]
    present_sessions = []
    for peer in sessions.get("sessions", []):
        peer_relay = peer.get("relay") or {}
        if peer.get("repository") != session.get("repository"):
            continue
        if peer.get("status") == "CLOSED" or peer_relay.get("state") in {"CLOSED", "HANDOFF_STALLED"}:
            continue
        present_sessions.append({
            "session_id": peer.get("session_id"),
            "agent_identity": available(peer.get("agent_identity")),
            "session_status": available(peer.get("status")),
            "relay_state": available(peer_relay.get("state")),
        })

    context = {
        "process": "GACR",
        "contract": "GACR_AGENT_CONTEXT_V2",
        "session_id": session_id,
        "session_identity": available(session.get("agent_identity")),
        "presence": present_sessions,
        "repository": available(session.get("repository")),
        "task_id": available(relay.get("task_id")),
        "claim": available(active_claims[0] if len(active_claims) == 1 else active_claims if active_claims else None),
        "claims": active_claims,
        "branch": available(relay.get("branch")),
        "pull_request": available(relay.get("pull_request")),
        "observed_head": available(forensics.get("work", {}).get("last_observed_head_sha")),
        "written_head": available(forensics.get("work", {}).get("last_written_head_sha")),
        "last_activity_at": signals["last_activity_at"],
        "last_liveness_evidence_at": signals["last_liveness_evidence_at"],
        "last_progress_at": signals["last_progress_at"],
        "liveness": signals["liveness"],
        "progress": signals["progress"],
        "progress_evidence": signals["progress"]["last_progress_evidence"],
        "action_started": available(actions.get("last_action_started")),
        "action_completed": available(actions.get("last_action_completed")),
        "action_in_flight": available(actions.get("in_flight_action")),
        "checkpoint": available(forensics.get("last_checkpoint_ref")),
        "predecessor": available(relay.get("predecessor_session_id")),
        "takeover": {
            "eligible": bool(relay.get("state") == "TAKEOVER_READY" and open_takeover),
            "relay_state": available(relay.get("state")),
            "takeover_id": available((open_takeover or {}).get("takeover_id")),
            "status": available((open_takeover or {}).get("status")),
            "claim_preserved_until_accept": True,
        },
        "exact_head_reobservation_requirement": bool(
            forensics.get("resume_point", {}).get("requires_exact_head_reobservation", True)
        ),
        "provider_conversation_ref": available(session.get("provider_conversation_ref")),
        "known_limitations": [
            "Provider-private conversation metadata remains UNAVAILABLE unless explicitly supplied.",
            "A liveness challenge is optional and requires a real bidirectional client/gateway integration to send and receive it.",
            "Proprietary silent repository reads remain unobservable without an instrumented provider/client/gateway surface.",
            "SHARED_INTEGRATION_REQUIRED: Presence/ConnectionEnvelope binding is owned by the parallel Presence Fabric tranche.",
        ],
        "shared_integration_required": SHARED_INTEGRATION_REQUIRED,
        "session": session,
        "active_claims": active_claims,
        "takeovers": related_takeovers,
        "dispatches": related_dispatches,
        "recent_beacons": related[-10:],
        "recent_correlations": related_correlations[-10:],
        "unbound_activity": unbound_activity_projection(),
        "interruption_forensics": forensics,
        "repository_head": available(git_value("rev-parse", "HEAD")),
        "repository_branch": available(git_value("branch", "--show-current")),
        "generated_at": timestamp,
    }
    assert_secretless(context)
    return context


def interrogate_session(session_id: str, *, generated_at: str | None = None) -> dict:
    return agent_context(session_id, generated_at=generated_at)


def session_recovery_packet(session_id: str, *, generated_at: str | None = None) -> dict:
    """Build a secretless, derived continuity + addressability packet.

    This is a projection over existing canonical GACR stores. It creates no
    session, claim, routing, task, authority, or transport source of truth.
    """
    context = agent_context(session_id, generated_at=generated_at)
    session = context["session"]
    dispatches = sorted(
        context.get("dispatches") or [],
        key=lambda item: (item.get("created_at") or "", item.get("dispatch_id") or ""),
    )

    wake_channels = set(session.get("wake_channels") or [])
    for item in dispatches:
        wake_channels.update(item.get("delivery_modes") or [])

    capabilities = sorted(set(session.get("capabilities") or []))
    transport_candidates = sorted(wake_channels)
    last_dispatch = dispatches[-1] if dispatches else None

    explicit_prompt_transport = session.get("prompt_transport")
    prompt_receive_verified = (
        "PROMPT_RECEIVE" in capabilities
        or bool(explicit_prompt_transport)
    )
    addressability = {
        "session_id": session_id,
        "provider": available(session.get("provider")),
        "provider_conversation_ref": available(session.get("provider_conversation_ref")),
        "client_instance_id": available(session.get("client_instance_id")),
        "connection_ref": available(session.get("connection_ref")),
        "connection_method": available(session.get("connection_method")),
        "bridge_registration_ref": available(session.get("bridge_registration_ref")),
        "wake_channels": sorted(session.get("wake_channels") or []),
        "transport_candidates": transport_candidates,
        "capabilities": capabilities,
        "control_channel_reachability": available(session.get("control_channel_reachability")),
        "last_dispatch": available({
            "dispatch_id": last_dispatch.get("dispatch_id"),
            "status": last_dispatch.get("status"),
            "created_at": last_dispatch.get("created_at"),
            "delivery_modes": last_dispatch.get("delivery_modes") or [],
        } if last_dispatch else None),
        "targetable_via_observed_transport": bool(transport_candidates),
        "freeform_message_delivery": {
            "status": "VERIFIED_CAPABILITY" if prompt_receive_verified else "NOT_VERIFIED",
            "transport": available(explicit_prompt_transport),
            "provider_conversation_ref_alone_is_sufficient": False,
            "requires_verified_host_or_provider_transport": True,
        },
        "credentials": {
            "persisted_in_packet": False,
            "runtime_only": True,
        },
        "grants_invocation_authority": False,
        "grants_mutation_authority": False,
    }

    packet = {
        "schema": "gacr-session-recovery-packet/v1",
        "process": "GACR",
        "authority": "CP-AGENT-RELAY-001",
        "session_id": session_id,
        "generated_at": context["generated_at"],
        "addressability": addressability,
        "continuity": {
            "repository": context["repository"],
            "branch": context["branch"],
            "pull_request": context["pull_request"],
            "task_id": context["task_id"],
            "claims": context["claims"],
            "checkpoint": context["checkpoint"],
            "observed_head": context["observed_head"],
            "written_head": context["written_head"],
            "liveness": context["liveness"],
            "progress": context["progress"],
            "takeover": context["takeover"],
            "interruption_forensics": context["interruption_forensics"],
            "exact_head_reobservation_requirement": context["exact_head_reobservation_requirement"],
        },
        "provenance": {
            "session_store": str(SESSIONS_PATH.relative_to(ROOT)) if SESSIONS_PATH.is_relative_to(ROOT) else str(SESSIONS_PATH),
            "claims_store": str(CLAIMS_PATH.relative_to(ROOT)) if CLAIMS_PATH.is_relative_to(ROOT) else str(CLAIMS_PATH),
            "takeovers_store": str(TAKEOVERS_PATH.relative_to(ROOT)) if TAKEOVERS_PATH.is_relative_to(ROOT) else str(TAKEOVERS_PATH),
            "beacons_store": str(BEACONS_PATH.relative_to(ROOT)) if BEACONS_PATH.is_relative_to(ROOT) else str(BEACONS_PATH),
            "correlations_store": str(CORRELATIONS_PATH.relative_to(ROOT)) if CORRELATIONS_PATH.is_relative_to(ROOT) else str(CORRELATIONS_PATH),
            "dispatches_store": str(DISPATCHES_PATH.relative_to(ROOT)) if DISPATCHES_PATH.is_relative_to(ROOT) else str(DISPATCHES_PATH),
            "derived_projection_only": True,
        },
        "next_gate": {
            "may_resume_without_exact_head_reobservation": False,
            "may_accept_takeover_implicitly": False,
            "may_send_freeform_message_without_verified_transport": False,
        },
    }
    assert_secretless(packet)
    return packet


def worker_c_integration_projection(session_id: str, *, generated_at: str | None = None) -> dict:
    context = agent_context(session_id, generated_at=generated_at)
    return {
        "session_id": session_id,
        "liveness": context["liveness"],
        "progress": context["progress"],
        "last_activity_at": context["last_activity_at"],
        "last_liveness_evidence_at": context["last_liveness_evidence_at"],
        "last_progress_at": context["last_progress_at"],
        "unbound_activity": context["unbound_activity"],
        "agent_context": context,
        "takeover_eligibility_inputs": context["takeover"],
        "shared_integration_required": context["shared_integration_required"],
    }


def _terminal_session(session: dict) -> bool:
    relay = session.get("relay") or {}
    return session.get("status") == "CLOSED" or relay.get("state") in {"CLOSED", "HANDOFF_STALLED"}

def _specific_provider_conflict(provider: str | None, session: dict) -> bool:
    if not provider or provider in {"other", "unknown"}:
        return False
    current = session.get("provider")
    return bool(current and current not in {"other", "unknown", provider})

def _github_signal(beacon: dict, key: str):
    direct = beacon.get(key)
    if direct not in (None, ""):
        return direct
    github = beacon.get("github") or {}
    env = github.get("environment") or {}
    event = github.get("event") or {}
    mapping = {
        "github_actor": env.get("GITHUB_ACTOR") or (event.get("sender") or {}).get("login"),
        "github_installation_id": event.get("installation_id"),
        "github_workflow": env.get("GITHUB_WORKFLOW"),
        "github_run_id": env.get("GITHUB_RUN_ID"),
        "github_run_attempt": env.get("GITHUB_RUN_ATTEMPT"),
        "github_job": env.get("GITHUB_JOB"),
    }
    return mapping.get(key)

def _active_claims_by_session(claims_doc: dict, session_id: str) -> list[dict]:
    return [
        claim for claim in claims_doc.get("claims", [])
        if claim.get("session_id") == session_id and claim.get("status") == "ACTIVE"
    ]

def _contextual_evidence(beacon: dict, session: dict, claims_doc: dict) -> list[str]:
    relay = session.get("relay") or {}
    reasons: list[str] = []

    if beacon.get("connection_fingerprint") and beacon.get("connection_fingerprint") == session.get("connection_fingerprint"):
        reasons.append("CONNECTION_FINGERPRINT_MATCH")
    if beacon.get("provider") and beacon.get("provider") == session.get("provider"):
        reasons.append("PROVIDER_MATCH")
    if beacon.get("task_id") and beacon.get("task_id") == relay.get("task_id"):
        reasons.append("TASK_MATCH")
    if beacon.get("branch") and beacon.get("branch") == relay.get("branch"):
        reasons.append("BRANCH_MATCH")
    if beacon.get("pull_request") is not None and beacon.get("pull_request") == relay.get("pull_request"):
        reasons.append("PULL_REQUEST_MATCH")

    observed_head = beacon.get("observed_head_sha")
    written_head = beacon.get("written_head_sha")
    session_heads = {
        session.get("last_observed_head_sha"),
        session.get("starting_head_sha"),
    }
    session_heads.discard(None)
    for claim in _active_claims_by_session(claims_doc, session.get("session_id")):
        if claim.get("claimed_head_sha"):
            session_heads.add(claim.get("claimed_head_sha"))
    if observed_head and observed_head in session_heads:
        reasons.append("OBSERVED_HEAD_MATCH")
    if written_head and written_head in session_heads:
        reasons.append("WRITTEN_HEAD_MATCH")

    claim_id = beacon.get("claim_id")
    if claim_id:
        if any(
            claim_id in {claim.get("claim_id"), claim.get("work_item_id")}
            for claim in _active_claims_by_session(claims_doc, session.get("session_id"))
        ):
            reasons.append("CLAIM_MATCH")

    for key, reason in (
        ("github_actor", "GITHUB_ACTOR_MATCH"),
        ("github_installation_id", "GITHUB_INSTALLATION_MATCH"),
        ("github_workflow", "GITHUB_WORKFLOW_MATCH"),
        ("github_run_id", "GITHUB_RUN_MATCH"),
        ("github_run_attempt", "GITHUB_RUN_ATTEMPT_MATCH"),
        ("github_job", "GITHUB_JOB_MATCH"),
    ):
        value = _github_signal(beacon, key)
        session_value = session.get(key)
        if value not in (None, "") and session_value not in (None, "") and str(value) == str(session_value):
            reasons.append(reason)

    observed = parse_iso(beacon.get("observed_at"))
    created = parse_iso(session.get("created_at"))
    last_seen = parse_iso(session.get("last_seen_at"))
    if observed and created:
        upper = (last_seen or created)
        if created.timestamp() - 900 <= observed.timestamp() <= upper.timestamp() + 86400:
            reasons.append("TEMPORAL_WINDOW_COMPATIBLE")
    return reasons

def _evidence_tier(reasons: list[str]) -> str:
    values = set(reasons)
    if "CONNECTION_FINGERPRINT_MATCH" in values and values.intersection({
        "TASK_MATCH", "BRANCH_MATCH", "PULL_REQUEST_MATCH", "GITHUB_ACTOR_MATCH",
        "GITHUB_INSTALLATION_MATCH", "CLAIM_MATCH",
    }):
        return "STRONG"
    if {"TASK_MATCH", "BRANCH_MATCH", "PULL_REQUEST_MATCH"}.issubset(values):
        return "STRONG"
    if {"GITHUB_ACTOR_MATCH", "GITHUB_INSTALLATION_MATCH", "BRANCH_MATCH"}.issubset(values):
        return "STRONG"
    if {"GITHUB_RUN_MATCH", "GITHUB_JOB_MATCH", "BRANCH_MATCH"}.issubset(values):
        return "STRONG"
    if {"CLAIM_MATCH", "BRANCH_MATCH"}.issubset(values):
        return "STRONG"

    meaningful = values.difference({"TEMPORAL_WINDOW_COMPATIBLE", "PROVIDER_MATCH"})
    if meaningful:
        return "PROBABLE"
    return "UNKNOWN"

def _correlation_result(
    beacon: dict,
    *,
    level: str,
    selected_session_id: str | None,
    candidates: list[str],
    reasons: list[str],
    rule_id: str,
    evaluated: list[dict] | None = None,
) -> dict:
    return {
        "level": level,
        "selected_session_id": selected_session_id,
        "candidate_session_ids": candidates[:10],
        "reasons": reasons,
        "confidence": {
            "rule_id": rule_id,
            "class": level,
            "numeric_score": None,
            "auto_bind_allowed": level in {"EXACT", "STRONG"} and selected_session_id is not None,
        },
        "binding_status": "BOUND" if selected_session_id and level in {"EXACT", "STRONG"} else "UNBOUND_ACTIVITY",
        "provider_identity_inferred": False,
        "provider_conversation_ref": beacon.get("provider_conversation_ref"),
        "evaluations": evaluated or [],
    }

def correlate_beacon(beacon: dict, sessions_doc: dict, claims_doc: dict | None = None) -> dict:
    """Categorical, fail-closed Correlator.

    Classification is based on named evidence rules rather than an arbitrary
    numeric score. A connection fingerprint is only operational evidence; it
    never becomes provider identity.
    """
    claims_doc = claims_doc or {"claims": []}
    live = [
        session for session in sessions_doc.get("sessions", [])
        if session.get("repository") == beacon.get("repository") and not _terminal_session(session)
    ]
    if not live:
        return _correlation_result(
            beacon, level="UNKNOWN", selected_session_id=None, candidates=[],
            reasons=[], rule_id="UNKNOWN_NO_LIVE_REPOSITORY_SESSION",
        )

    direct_specs = (
        ("session_id", "session_id", "SESSION_ID_EXACT"),
        ("provider_conversation_ref", "provider_conversation_ref", "PROVIDER_CONVERSATION_REF_EXACT"),
        ("client_instance_id", "client_instance_id", "CLIENT_INSTANCE_ID_EXACT"),
        ("connection_ref", "connection_ref", "CONNECTION_REF_EXACT"),
    )
    direct_targets: dict[str, set[str]] = {}
    direct_reasons: dict[str, list[str]] = {}
    supplied_direct = []
    for beacon_key, session_key, reason in direct_specs:
        value = beacon.get(beacon_key)
        if value in (None, ""):
            continue
        supplied_direct.append((beacon_key, session_key, value, reason))
        matches = {
            session.get("session_id") for session in live
            if session.get(session_key) not in (None, "") and str(session.get(session_key)) == str(value)
        }
        matches.discard(None)
        if matches:
            direct_targets[beacon_key] = matches
            for sid in matches:
                direct_reasons.setdefault(sid, []).append(reason)

    # connection_ref identifies a concrete governed connection, while one
    # client_instance_id may legitimately host several concurrent connections.
    # When both anchors are supplied and overlap, restrict the process-level
    # client anchor to the connection-scoped match. If they do not overlap,
    # preserve the original conflicting-anchor behavior and fail closed.
    if "connection_ref" in direct_targets and "client_instance_id" in direct_targets:
        overlap = direct_targets["connection_ref"].intersection(direct_targets["client_instance_id"])
        if overlap:
            direct_targets["client_instance_id"] = overlap

    union = set().union(*direct_targets.values()) if direct_targets else set()
    if len(union) > 1 or any(len(values) > 1 for values in direct_targets.values()):
        return _correlation_result(
            beacon, level="AMBIGUOUS", selected_session_id=None, candidates=sorted(union),
            reasons=["CONFLICTING_EXPLICIT_ANCHORS"], rule_id="AMBIGUOUS_EXPLICIT_ANCHOR_CONFLICT",
        )

    if len(union) == 1:
        sid = next(iter(union))
        target = next(session for session in live if session.get("session_id") == sid)
        conflicts = []
        if _specific_provider_conflict(beacon.get("provider"), target):
            conflicts.append("PROVIDER_CONFLICT")
        for beacon_key, session_key, value, _ in supplied_direct:
            target_value = target.get(session_key)
            if target_value not in (None, "") and str(target_value) != str(value):
                conflicts.append(f"{beacon_key.upper()}_CONFLICT")
        if conflicts:
            candidates = sorted(set([sid] + [
                x for values in direct_targets.values() for x in values
            ]))
            return _correlation_result(
                beacon, level="AMBIGUOUS", selected_session_id=None, candidates=candidates,
                reasons=sorted(set(conflicts)), rule_id="AMBIGUOUS_EXPLICIT_FACT_CONFLICT",
            )
        return _correlation_result(
            beacon, level="EXACT", selected_session_id=sid, candidates=[sid],
            reasons=direct_reasons.get(sid, []), rule_id="EXACT_DIRECT_ANCHOR",
        )

    evaluations = []
    for session in live:
        reasons = _contextual_evidence(beacon, session, claims_doc)
        tier = _evidence_tier(reasons)
        evaluations.append({
            "session_id": session.get("session_id"),
            "tier": tier,
            "reasons": reasons,
        })

    supported = [x for x in evaluations if x["tier"] != "UNKNOWN"]
    strong = [x for x in supported if x["tier"] == "STRONG"]
    probable = [x for x in supported if x["tier"] == "PROBABLE"]

    if len(strong) == 1:
        selected = strong[0]
        return _correlation_result(
            beacon, level="STRONG", selected_session_id=selected["session_id"],
            candidates=[x["session_id"] for x in strong + probable],
            reasons=selected["reasons"], rule_id="STRONG_UNIQUE_MULTI_SIGNAL",
            evaluated=evaluations,
        )
    if len(strong) > 1:
        return _correlation_result(
            beacon, level="AMBIGUOUS", selected_session_id=None,
            candidates=[x["session_id"] for x in strong],
            reasons=["MULTIPLE_STRONG_CANDIDATES"], rule_id="AMBIGUOUS_STRONG_TIE",
            evaluated=evaluations,
        )
    if len(probable) > 1:
        return _correlation_result(
            beacon, level="AMBIGUOUS", selected_session_id=None,
            candidates=[x["session_id"] for x in probable],
            reasons=["MULTIPLE_PROBABLE_CANDIDATES"], rule_id="AMBIGUOUS_PROBABLE_TIE",
            evaluated=evaluations,
        )
    if len(probable) == 1:
        candidate = probable[0]
        return _correlation_result(
            beacon, level="PROBABLE", selected_session_id=None,
            candidates=[candidate["session_id"]], reasons=candidate["reasons"],
            rule_id="PROBABLE_CONTEXT_ONLY", evaluated=evaluations,
        )
    return _correlation_result(
        beacon, level="UNKNOWN", selected_session_id=None,
        candidates=[session.get("session_id") for session in live if session.get("session_id")],
        reasons=[], rule_id="UNKNOWN_INSUFFICIENT_EVIDENCE", evaluated=evaluations,
    )

def _work_item(work_doc: dict, work_item_id: str | None) -> dict | None:
    if not work_item_id:
        return None
    return next((item for item in work_doc.get("items", []) if item.get("work_item_id") == work_item_id), None)

def _takeover_target_context(
    sessions_doc: dict,
    claims_doc: dict,
    work_doc: dict,
    takeover: dict,
) -> dict:
    predecessor = session_by_id(sessions_doc, takeover.get("stalled_session_id"))
    predecessor_claims = _active_claims_by_session(claims_doc, takeover.get("stalled_session_id"))
    work_item_id = takeover.get("work_item_id")
    if not work_item_id and len(predecessor_claims) == 1:
        work_item_id = predecessor_claims[0].get("work_item_id")
    item = _work_item(work_doc, work_item_id)
    collision_domains = set(item.get("collision_domains") or [] if item else [])
    for claim in predecessor_claims:
        collision_domains.update(claim.get("collision_domains") or [])
    return {
        "predecessor": predecessor,
        "predecessor_claims": predecessor_claims,
        "work_item_id": work_item_id,
        "work_item": item,
        "task_id": takeover.get("task_id") or ((predecessor or {}).get("relay") or {}).get("task_id"),
        "branch": takeover.get("branch") or ((predecessor or {}).get("relay") or {}).get("branch"),
        "pull_request": takeover.get("pull_request") if takeover.get("pull_request") is not None else ((predecessor or {}).get("relay") or {}).get("pull_request"),
        "collision_domains": sorted(collision_domains),
    }

def evaluate_standby_candidate(
    candidate: dict,
    *,
    target: dict,
    claims_doc: dict,
    work_doc: dict,
    takeover: dict,
) -> dict:
    predecessor = target.get("predecessor") or {}
    relay = candidate.get("relay") or {}
    reasons: list[str] = []
    blockers: list[str] = []

    def result(status: str) -> dict:
        return {
            "session_id": candidate.get("session_id"),
            "status": status,
            "reasons": reasons,
            "blockers": blockers,
            "task_binding": relay.get("task_id"),
            "branch_binding": relay.get("branch"),
            "authority_grants_observed": candidate.get("authority_grants"),
            "capabilities": sorted(set(candidate.get("capabilities") or [])),
            "wake_channels": sorted(set(candidate.get("wake_channels") or [])),
        }

    if candidate.get("session_id") == predecessor.get("session_id"):
        reasons.append("PREDECESSOR_CANNOT_SUCCEED_ITSELF")
        return result("INELIGIBLE")
    if candidate.get("repository") != predecessor.get("repository"):
        reasons.append("REPOSITORY_MISMATCH")
        return result("INELIGIBLE")
    if candidate.get("status") != "STANDBY" or relay.get("state") != "STANDBY":
        reasons.append("SESSION_NOT_STANDBY")
        return result("INELIGIBLE")

    target_task = target.get("task_id")
    if relay.get("task_id") and target_task and relay.get("task_id") != target_task:
        reasons.append("BOUND_TO_DIFFERENT_TASK")
        return result("INELIGIBLE")

    scope = candidate.get("work_scope") or {}
    allowed_work = set(scope.get("work_item_ids") or [])
    if allowed_work and target.get("work_item_id") not in allowed_work:
        reasons.append("WORK_SCOPE_MISMATCH")
        return result("INELIGIBLE")
    allowed_branches = set(scope.get("branches") or [])
    if allowed_branches and target.get("branch") not in allowed_branches:
        reasons.append("BRANCH_SCOPE_MISMATCH")
        return result("INELIGIBLE")

    candidate_claims = _active_claims_by_session(claims_doc, candidate.get("session_id"))
    if candidate_claims:
        blockers.append("CANDIDATE_ALREADY_OWNS_ACTIVE_CLAIM")
        return result("BLOCKED")

    item = target.get("work_item") or {}
    by_id = {x.get("work_item_id"): x for x in work_doc.get("items", []) if x.get("work_item_id")}
    unmet = [
        dep for dep in item.get("dependencies") or []
        if (by_id.get(dep) or {}).get("status") != "DONE"
    ]
    if unmet:
        blockers.extend([f"DEPENDENCY_NOT_DONE:{dep}" for dep in unmet])
        return result("BLOCKED")

    target_domains = set(target.get("collision_domains") or [])
    occupied = set()
    for claim in claims_doc.get("claims", []):
        if claim.get("status") != "ACTIVE":
            continue
        if claim.get("session_id") in {predecessor.get("session_id"), candidate.get("session_id")}:
            continue
        occupied.update(claim.get("collision_domains") or [])
    collisions = sorted(target_domains.intersection(occupied))
    if collisions:
        blockers.extend([f"COLLISION_DOMAIN_OCCUPIED:{domain}" for domain in collisions])
        return result("BLOCKED")

    required_capabilities = set(item.get("required_capabilities") or takeover.get("required_capabilities") or [])
    capabilities = set(candidate.get("capabilities") or [])
    missing_capabilities = sorted(required_capabilities - capabilities)
    if missing_capabilities:
        reasons.extend([f"MISSING_CAPABILITY:{capability}" for capability in missing_capabilities])
        return result("INELIGIBLE")

    required_authorities = set(item.get("required_authorities") or takeover.get("required_authorities") or [])
    observed_authorities = candidate.get("authority_grants")
    if required_authorities and observed_authorities is None:
        reasons.append("AUTHORITY_EVIDENCE_UNAVAILABLE")
        return result("AMBIGUOUS")
    missing_authorities = sorted(required_authorities - set(observed_authorities or []))
    if missing_authorities:
        reasons.extend([f"MISSING_AUTHORITY:{authority}" for authority in missing_authorities])
        return result("INELIGIBLE")

    allowed_roles = set(item.get("allowed_agent_roles") or takeover.get("allowed_agent_roles") or [])
    role = candidate.get("agent_role")
    if allowed_roles and not role:
        reasons.append("AGENT_ROLE_UNAVAILABLE")
        return result("AMBIGUOUS")
    if allowed_roles and role not in allowed_roles:
        reasons.append("AGENT_ROLE_NOT_ALLOWED")
        return result("INELIGIBLE")

    if target_task and relay.get("task_id") == target_task:
        reasons.append("TASK_BOUND_MATCH")
    else:
        reasons.append("TASK_UNBOUND_COMPATIBLE")
    if target.get("branch") and relay.get("branch") == target.get("branch"):
        reasons.append("BRANCH_BOUND_MATCH")
    else:
        reasons.append("BRANCH_REQUIRES_RECONCILIATION")
    if target.get("pull_request") is not None and relay.get("pull_request") == target.get("pull_request"):
        reasons.append("PULL_REQUEST_BOUND_MATCH")
    if required_capabilities:
        reasons.append("REQUIRED_CAPABILITIES_PRESENT")
    if required_authorities:
        reasons.append("REQUIRED_AUTHORITY_EVIDENCE_PRESENT")
    if target_domains:
        reasons.append("COLLISION_DOMAINS_AVAILABLE")
    reasons.append("EXACT_HEAD_STILL_REQUIRED")
    return result("ELIGIBLE")

def select_compatible_standby(
    sessions_doc: dict,
    claims_doc: dict,
    work_doc: dict,
    takeover: dict,
) -> dict:
    target = _takeover_target_context(sessions_doc, claims_doc, work_doc, takeover)
    predecessor = target.get("predecessor")
    if not predecessor:
        return {
            "selected_session_id": None,
            "evaluations": [],
            "selection_method": "DETERMINISTIC_CATEGORICAL_ORDER",
            "grants_write_authority": False,
            "reason": "PREDECESSOR_NOT_FOUND",
        }

    evaluations = [
        evaluate_standby_candidate(
            candidate, target=target, claims_doc=claims_doc, work_doc=work_doc, takeover=takeover
        )
        for candidate in sessions_doc.get("sessions", [])
        if candidate.get("session_id") != predecessor.get("session_id")
    ]
    by_id = {s.get("session_id"): s for s in sessions_doc.get("sessions", [])}

    def eligibility_key(evaluation: dict):
        session = by_id.get(evaluation.get("session_id")) or {}
        relay = session.get("relay") or {}
        return (
            0 if relay.get("task_id") == target.get("task_id") and target.get("task_id") else 1,
            0 if relay.get("branch") == target.get("branch") and target.get("branch") else 1,
            0 if relay.get("pull_request") == target.get("pull_request") and target.get("pull_request") is not None else 1,
            session.get("created_at") or "",
            session.get("session_id") or "",
        )

    eligible = sorted(
        [x for x in evaluations if x.get("status") == "ELIGIBLE"],
        key=eligibility_key,
    )
    selected = eligible[0].get("session_id") if eligible else None
    for index, evaluation in enumerate(eligible, start=1):
        evaluation["eligible_rank"] = index
    return {
        "selected_session_id": selected,
        "evaluations": evaluations,
        "selection_method": "DETERMINISTIC_CATEGORICAL_ORDER",
        "grants_write_authority": False,
        "target": {
            "work_item_id": target.get("work_item_id"),
            "task_id": target.get("task_id"),
            "branch": target.get("branch"),
            "pull_request": target.get("pull_request"),
            "collision_domains": target.get("collision_domains"),
        },
    }

def _worker_b_projection_if_available(session_id: str) -> dict | None:
    """Consume Worker B's merged projection when present; never reimplement it here."""
    projection = globals().get("worker_c_integration_projection")
    if not callable(projection):
        return None
    try:
        value = projection(session_id)
    except (ValueError, KeyError):
        return None
    return value if isinstance(value, dict) else None

def _known_projection_value(value):
    return None if value in (None, "", "UNAVAILABLE") else value

def build_takeover_package(
    stalled_session_id: str,
    successor_candidate_session_id: str,
    *,
    sessions_doc: dict | None = None,
    claims_doc: dict | None = None,
    work_doc: dict | None = None,
    takeovers_doc: dict | None = None,
    forensics_doc: dict | None = None,
) -> dict:
    sessions_doc = sessions_doc or read_json(SESSIONS_PATH, {"sessions": []})
    claims_doc = claims_doc or read_json(CLAIMS_PATH, {"claims": []})
    work_doc = work_doc or read_json(GOV / "work" / "work-items.json", {"items": []})
    takeovers_doc = takeovers_doc or read_json(TAKEOVERS_PATH, {"items": []})
    forensics_doc = forensics_doc or read_json(FORENSICS_PATH, {"items": []})

    predecessor = session_by_id(sessions_doc, stalled_session_id)
    successor = session_by_id(sessions_doc, successor_candidate_session_id)
    if not predecessor or not successor:
        raise ValueError("takeover package requires predecessor and successor candidate")

    takeover = next((
        item for item in takeovers_doc.get("items", [])
        if item.get("stalled_session_id") == stalled_session_id
        and item.get("status") in {"READY_FOR_RECONCILIATION", "OFFERED", "ACCEPTED"}
    ), None) or {
        "stalled_session_id": stalled_session_id,
        "task_id": (predecessor.get("relay") or {}).get("task_id"),
        "branch": (predecessor.get("relay") or {}).get("branch"),
        "pull_request": (predecessor.get("relay") or {}).get("pull_request"),
    }
    target = _takeover_target_context(sessions_doc, claims_doc, work_doc, takeover)
    forensic = next((x for x in forensics_doc.get("items", []) if x.get("session_id") == stalled_session_id), None) or {}
    resume = forensic.get("resume_point") or {}
    actions = forensic.get("actions") or {}
    predecessor_relay = predecessor.get("relay") or {}
    work_item = target.get("work_item") or {}
    worker_b_context = _worker_b_projection_if_available(stalled_session_id)

    provider_ref = successor.get("provider_conversation_ref")
    provenance = successor.get("provider_conversation_ref_provenance")
    if provenance not in {"PROVIDED_BY_CLIENT", "EXTRACTED_FROM_EXPLICIT_URL"}:
        provider_ref = None

    evidence_refs = []
    for value in (
        forensic.get("last_evidence_ref"),
        resume.get("evidence_ref"),
        predecessor_relay.get("last_evidence"),
    ):
        if value and value not in evidence_refs:
            evidence_refs.append(value)

    known_unknowns = []
    if provider_ref is None:
        known_unknowns.append("PROVIDER_CONVERSATION_REF_UNAVAILABLE")
    if not resume.get("last_written_head_sha"):
        known_unknowns.append("LAST_WRITTEN_HEAD_UNAVAILABLE")
    if not forensic.get("generated_at"):
        known_unknowns.append("FORENSICS_GENERATION_TIME_UNAVAILABLE")
    if actions.get("in_flight_action"):
        known_unknowns.append("IN_FLIGHT_ACTION_OUTCOME_UNRESOLVED")
    if worker_b_context is None:
        known_unknowns.append("LIVENESS_PROGRESS_CONTEXT_SHARED_INTEGRATION_REQUIRED")

    last_activity_at = (
        _known_projection_value((worker_b_context or {}).get("last_activity_at"))
        or predecessor.get("last_seen_at")
        or predecessor_relay.get("last_heartbeat_at")
    )
    last_progress_at = (
        _known_projection_value((worker_b_context or {}).get("last_progress_at"))
        or (actions.get("last_action_completed") or {}).get("observed_at")
    )

    package = {
        "schema": "gacr-takeover-package/v1",
        "predecessor_session_id": stalled_session_id,
        "successor_candidate_session_id": successor_candidate_session_id,
        "repository": predecessor.get("repository"),
        "task_id": target.get("task_id"),
        "work_item_id": target.get("work_item_id"),
        "active_claims": target.get("predecessor_claims"),
        "branch": target.get("branch"),
        "pull_request": target.get("pull_request"),
        "observed_head_sha": resume.get("last_observed_head_sha") or predecessor.get("last_observed_head_sha"),
        "written_head_sha": resume.get("last_written_head_sha"),
        "last_activity_at": last_activity_at,
        "last_progress_at": last_progress_at,
        "liveness": (worker_b_context or {}).get("liveness"),
        "progress": (worker_b_context or {}).get("progress"),
        "action_in_flight": actions.get("in_flight_action"),
        "last_completed_action": actions.get("last_action_completed"),
        "checkpoint_ref": forensic.get("last_checkpoint_ref") or resume.get("checkpoint_ref"),
        "evidence_refs": evidence_refs,
        "forensics_resume_point": resume or None,
        "collision_domains": target.get("collision_domains"),
        "dependencies": [
            {
                "work_item_id": dep,
                "status": (_work_item(work_doc, dep) or {}).get("status", "UNKNOWN"),
            }
            for dep in work_item.get("dependencies") or []
        ],
        "exact_head_required": True,
        "replay_policy": "RECONCILE_BEFORE_REPLAY",
        "known_unknowns": known_unknowns,
        "provider_conversation_ref": provider_ref,
        "wake_channels": successor.get("wake_channels") or ["POLL_REPOSITORY"],
        "bridge_registration_ref": successor.get("bridge_registration_ref"),
        "may_write_before_takeover_accept": False,
        "claim_transfer_before_accept": False,
        "generated_at": now_iso(),
    }
    assert_secretless(package)
    return package

def command_beacon(a: argparse.Namespace) -> None:
    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    session = session_by_id(sessions, a.session_id)
    capabilities = [x.strip() for x in (a.capability or []) if x.strip()]
    item = record_beacon(
        session=session,
        event_type=a.event_type,
        provider=a.provider,
        provider_ref=a.provider_ref,
        provider_url=a.provider_url,
        client_instance_id=a.client_instance_id,
        connection_ref=a.connection_ref,
        connection_fingerprint=a.connection_fingerprint,
        claim_id=a.claim_id,
        connection_envelope_digest=a.connection_envelope_digest,
        surface_class=a.surface_class,
        presence_event=a.presence_event,
        task_id=a.task_id,
        branch=a.branch,
        pull_request=a.pull_request,
        agent_role=a.agent_role,
        capabilities=capabilities,
        source=a.source,
        action_id=a.action_id,
        action_label=a.action_label,
        action_phase=a.action_phase,
        tool_name=a.tool_name,
        tool_call_id=a.tool_call_id,
        outcome=a.outcome,
        written_head_sha=a.written_head,
        checkpoint_ref=a.checkpoint_ref,
        evidence_ref=a.evidence_ref,
        interruption_code=a.interruption_code,
        workload_state=a.workload_state,
        blocker_code=a.blocker_code,
        capacity_slots=a.capacity_slots,
        max_parallel_tasks=a.max_parallel_tasks,
        retry_after_at=a.retry_after_at,
    )
    print(json.dumps({"status":"BEACON_RECORDED","beacon":item},indent=2,ensure_ascii=False))

def command_correlate(_: argparse.Namespace) -> None:
    print(json.dumps({"status":"CORRELATION_COMPLETE",**correlate_all()},indent=2,ensure_ascii=False))


def command_dispatch(_: argparse.Namespace) -> None:
    print(json.dumps({"status":"DISPATCH_COMPLETE",**dispatch_open_takeovers()},indent=2,ensure_ascii=False))


def command_context(a: argparse.Namespace) -> None:
    print(json.dumps(agent_context(a.session_id),indent=2,ensure_ascii=False))


def command_recover(a: argparse.Namespace) -> None:
    print(json.dumps(session_recovery_packet(a.session_id), indent=2, ensure_ascii=False))


def command_forensics(a: argparse.Namespace) -> None:
    if a.session_id:
        print(json.dumps({"status":"FORENSICS_COMPLETE","report":build_interruption_forensics(a.session_id,persist=True)},indent=2,ensure_ascii=False))
    else:
        print(json.dumps({"status":"FORENSICS_COMPLETE",**build_forensics_all()},indent=2,ensure_ascii=False))


def command_status(_: argparse.Namespace) -> None:
    print(json.dumps({
        "beacons": read_json(BEACONS_PATH, {"items":[]}),
        "correlations": read_json(CORRELATIONS_PATH, {"items":[]}),
        "dispatches": read_json(DISPATCHES_PATH, {"items":[]}),
        "forensics": read_json(FORENSICS_PATH, {"items":[]}),
        "unbound_activity": unbound_activity_projection(),
    },indent=2,ensure_ascii=False))


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description="GACR Beacon / Correlator / Dispatcher / Interruption Forensics")
    sub=p.add_subparsers(dest="command",required=True)

    b=sub.add_parser("beacon")
    b.add_argument("--session-id")
    b.add_argument("--event-type",default="CONNECT")
    b.add_argument("--provider")
    b.add_argument("--provider-ref")
    b.add_argument("--provider-url")
    b.add_argument("--client-instance-id")
    b.add_argument("--connection-ref")
    b.add_argument("--connection-fingerprint")
    b.add_argument("--claim-id")
    b.add_argument("--connection-envelope-digest")
    b.add_argument("--surface-class")
    b.add_argument("--presence-event")
    b.add_argument("--task-id")
    b.add_argument("--branch")
    b.add_argument("--pull-request",type=int)
    b.add_argument("--agent-role")
    b.add_argument("--capability",action="append")
    b.add_argument("--source",choices=["GITHUB_ACTIONS","LOCAL_AGENT","EXTERNAL_BRIDGE","CLIENT_EMITTER","UNKNOWN"])
    b.add_argument("--action-id"); b.add_argument("--action-label"); b.add_argument("--action-phase",choices=sorted(ACTION_PHASES))
    b.add_argument("--tool-name"); b.add_argument("--tool-call-id"); b.add_argument("--outcome"); b.add_argument("--written-head")
    b.add_argument("--checkpoint-ref"); b.add_argument("--evidence-ref"); b.add_argument("--interruption-code",choices=sorted(INTERRUPTION_CODES))
    b.add_argument("--workload-state", choices=sorted(WORKLOAD_STATES))
    b.add_argument("--blocker-code", choices=sorted(BLOCKER_CODES))
    b.add_argument("--capacity-slots", type=int)
    b.add_argument("--max-parallel-tasks", type=int)
    b.add_argument("--retry-after-at")
    b.set_defaults(fn=command_beacon)

    c=sub.add_parser("correlate")
    c.set_defaults(fn=command_correlate)

    d=sub.add_parser("dispatch")
    d.set_defaults(fn=command_dispatch)

    ctx=sub.add_parser("context")
    ctx.add_argument("--session-id",required=True)
    ctx.set_defaults(fn=command_context)

    recover=sub.add_parser("recover")
    recover.add_argument("--session-id",required=True)
    recover.set_defaults(fn=command_recover)

    forensic=sub.add_parser("forensics")
    forensic.add_argument("--session-id")
    forensic.set_defaults(fn=command_forensics)

    status=sub.add_parser("status")
    status.set_defaults(fn=command_status)
    return p

def main() -> None:
    args=parser().parse_args()
    args.fn(args)


if __name__=="__main__":
    main()
