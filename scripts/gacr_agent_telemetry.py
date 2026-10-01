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
FORBIDDEN_KEY_FRAGMENTS = ("token", "secret", "password", "private_key", "cookie", "authorization")
ACTION_PHASES = {"STARTED", "COMPLETED", "FAILED", "CANCELLED"}
INTERRUPTION_CODES = {"CLIENT_DISCONNECTED","PROVIDER_TIMEOUT","TOOL_FAILURE","AGENT_ERROR","USER_CANCELLED","NETWORK_LOSS","PROCESS_EXITED","UNKNOWN"}


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
) -> dict:
    store = read_json(BEACONS_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    timestamp = observed_at or now_iso()
    if action_phase and action_phase not in ACTION_PHASES:
        raise ValueError("unsupported action phase")
    if interruption_code and interruption_code not in INTERRUPTION_CODES:
        raise ValueError("unsupported interruption code")
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
    if beacon.get("repository") != session.get("repository"):
        return -1, [], False
    relay = session.get("relay") or {}
    reasons: list[str] = []
    exact = False
    if beacon.get("session_id") and beacon.get("session_id") == session.get("session_id"):
        reasons.append("SESSION_ID_EXACT")
        exact = True
    if beacon.get("provider_conversation_ref") and beacon.get("provider_conversation_ref") == session.get("provider_conversation_ref"):
        reasons.append("PROVIDER_CONVERSATION_REF_EXACT")
        exact = True
    if beacon.get("client_instance_id") and beacon.get("client_instance_id") == session.get("client_instance_id"):
        reasons.append("CLIENT_INSTANCE_ID_EXACT")
        exact = True
    if beacon.get("connection_ref") and beacon.get("connection_ref") == session.get("connection_ref"):
        reasons.append("CONNECTION_REF_EXACT")
        exact = True
    if exact:
        return 100, reasons, True

    score = 0
    if beacon.get("branch") and beacon.get("branch") == relay.get("branch"):
        score += 4
        reasons.append("BRANCH_MATCH")
    if beacon.get("pull_request") is not None and beacon.get("pull_request") == relay.get("pull_request"):
        score += 4
        reasons.append("PULL_REQUEST_MATCH")
    if beacon.get("task_id") and beacon.get("task_id") == relay.get("task_id"):
        score += 4
        reasons.append("TASK_MATCH")
    if beacon.get("observed_head_sha") and beacon.get("observed_head_sha") == session.get("last_observed_head_sha"):
        score += 3
        reasons.append("HEAD_MATCH")
    github_actor = ((beacon.get("github") or {}).get("environment") or {}).get("GITHUB_ACTOR")
    if github_actor and github_actor == session.get("github_actor"):
        score += 2
        reasons.append("GITHUB_ACTOR_MATCH")
    return score, reasons, False


def correlate_all() -> dict:
    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    beacons = read_json(BEACONS_PATH, {"items": []})
    store = read_json(CORRELATIONS_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    known = {x.get("beacon_id"): x for x in store.get("items", [])}
    changes = []

    for beacon in beacons.get("items", []):
        scored = []
        for session in sessions.get("sessions", []):
            score, reasons, exact = correlation_score(beacon, session)
            if score >= 0:
                scored.append((score, exact, session.get("session_id"), reasons))
        scored.sort(key=lambda x: (-x[0], x[2] or ""))
        level = "UNKNOWN"
        selected = None
        candidates = [x[2] for x in scored if x[2]]
        reasons: list[str] = []
        if scored:
            top = scored[0]
            ties = [x for x in scored if x[0] == top[0]]
            reasons = top[3]
            if top[1] and len(ties) == 1:
                level = "EXACT"
                selected = top[2]
            elif len(ties) > 1 and top[0] >= 4:
                level = "AMBIGUOUS"
            elif top[0] >= 7:
                level = "STRONG"
                selected = top[2]
            elif top[0] >= 4:
                level = "PROBABLE"
            else:
                level = "UNKNOWN"

        value = {
            "correlation_id": runtime_id("GACR-C-", {"beacon_id": beacon.get("beacon_id")}),
            "beacon_id": beacon.get("beacon_id"),
            "level": level,
            "selected_session_id": selected,
            "candidate_session_ids": candidates[:10],
            "reasons": reasons,
            "evaluated_at": now_iso(),
        }
        previous = known.get(beacon.get("beacon_id"))
        if previous:
            if {k: previous.get(k) for k in ("level","selected_session_id","candidate_session_ids","reasons")} == {k: value.get(k) for k in ("level","selected_session_id","candidate_session_ids","reasons")}:
                continue
            index = store["items"].index(previous)
            store["items"][index] = value
        else:
            store.setdefault("items", []).append(value)
        changes.append(value)

    if changes:
        store["revision"] = int(store.get("revision", 0)) + 1
        write_json(CORRELATIONS_PATH, store)
    return {"changed": len(changes), "items": changes}


def compatible_standby(sessions: dict, stalled_session_id: str) -> dict | None:
    predecessor = session_by_id(sessions, stalled_session_id)
    if not predecessor:
        return None
    values = []
    for session in sessions.get("sessions", []):
        relay = session.get("relay") or {}
        if session.get("session_id") == stalled_session_id:
            continue
        if session.get("repository") != predecessor.get("repository"):
            continue
        if session.get("status") != "STANDBY" or relay.get("state") != "STANDBY":
            continue
        values.append(session)
    values.sort(key=lambda s: (s.get("created_at") or "", s.get("session_id") or ""))
    return values[0] if values else None


def dispatch_open_takeovers() -> dict:
    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    takeovers = read_json(TAKEOVERS_PATH, {"items": []})
    store = read_json(DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    changes = []

    for takeover in takeovers.get("items", []):
        if takeover.get("status") not in {"READY_FOR_RECONCILIATION", "OFFERED", "ACCEPTED"}:
            continue
        target_id = takeover.get("offered_to_session_id")
        if not target_id and takeover.get("status") != "ACCEPTED":
            standby = compatible_standby(sessions, takeover.get("stalled_session_id"))
            target_id = standby.get("session_id") if standby else None
        if not target_id:
            continue
        target = session_by_id(sessions, target_id)
        if not target:
            continue
        existing = next((x for x in store.get("items", []) if x.get("takeover_id") == takeover.get("takeover_id") and x.get("target_session_id") == target_id and x.get("status") not in {"CANCELLED","EXPIRED"}), None)
        if existing:
            if takeover.get("status") == "ACCEPTED" and existing.get("status") != "ACTIVATED":
                existing["status"] = "ACTIVATED"
                existing["activated_at"] = now_iso()
                changes.append(existing)
            continue

        wake_channels = set(target.get("wake_channels") or [])
        delivery = ["POLL_REPOSITORY"]
        if "REPOSITORY_DISPATCH" in wake_channels:
            delivery.append("REPOSITORY_DISPATCH")
        if "EXTERNAL_BRIDGE" in wake_channels and target.get("bridge_registration_ref"):
            delivery.append("EXTERNAL_BRIDGE")

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
        }
        store.setdefault("items", []).append(item)
        changes.append(item)

    if changes:
        store["revision"] = int(store.get("revision", 0)) + 1
        write_json(DISPATCHES_PATH, store)
    return {"changed": len(changes), "items": changes}



def _session_beacons(session_id: str, beacons: dict, correlations: dict) -> list[dict]:
    selected = {x.get("beacon_id") for x in correlations.get("items", []) if x.get("selected_session_id") == session_id}
    values = [x for x in beacons.get("items", []) if x.get("session_id") == session_id or x.get("beacon_id") in selected]
    values.sort(key=lambda x: (x.get("observed_at") or "", x.get("beacon_id") or ""))
    return values


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


def agent_context(session_id: str) -> dict:
    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    claims = read_json(CLAIMS_PATH, {"claims": []})
    takeovers = read_json(TAKEOVERS_PATH, {"items": []})
    beacons = read_json(BEACONS_PATH, {"items": []})
    correlations = read_json(CORRELATIONS_PATH, {"items": []})
    dispatches = read_json(DISPATCHES_PATH, {"items": []})
    forensics = read_json(FORENSICS_PATH, {"items": []})
    session = session_by_id(sessions, session_id)
    if not session:
        raise ValueError("session not found")
    beacon_ids = [x.get("beacon_id") for x in beacons.get("items", []) if x.get("session_id") == session_id]
    related_correlations = [x for x in correlations.get("items", []) if x.get("selected_session_id") == session_id or x.get("beacon_id") in beacon_ids]
    return {
        "process": "GACR",
        "session": session,
        "active_claims": [x for x in claims.get("claims", []) if x.get("session_id") == session_id and x.get("status") == "ACTIVE"],
        "takeovers": [x for x in takeovers.get("items", []) if x.get("stalled_session_id") == session_id or x.get("offered_to_session_id") == session_id or x.get("accepted_by_session_id") == session_id],
        "dispatches": [x for x in dispatches.get("items", []) if x.get("target_session_id") == session_id or x.get("stalled_session_id") == session_id],
        "recent_beacons": [x for x in beacons.get("items", []) if x.get("session_id") == session_id][-10:],
        "recent_correlations": related_correlations[-10:],
        "interruption_forensics": next((x for x in forensics.get("items", []) if x.get("session_id") == session_id), None),
        "repository_head": git_value("rev-parse", "HEAD"),
        "repository_branch": git_value("branch", "--show-current"),
        "generated_at": now_iso(),
    }


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
    )
    print(json.dumps({"status":"BEACON_RECORDED","beacon":item},indent=2,ensure_ascii=False))


def command_correlate(_: argparse.Namespace) -> None:
    print(json.dumps({"status":"CORRELATION_COMPLETE",**correlate_all()},indent=2,ensure_ascii=False))


def command_dispatch(_: argparse.Namespace) -> None:
    print(json.dumps({"status":"DISPATCH_COMPLETE",**dispatch_open_takeovers()},indent=2,ensure_ascii=False))


def command_context(a: argparse.Namespace) -> None:
    print(json.dumps(agent_context(a.session_id),indent=2,ensure_ascii=False))


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
    b.add_argument("--task-id")
    b.add_argument("--branch")
    b.add_argument("--pull-request",type=int)
    b.add_argument("--agent-role")
    b.add_argument("--capability",action="append")
    b.add_argument("--source",choices=["GITHUB_ACTIONS","LOCAL_AGENT","EXTERNAL_BRIDGE","CLIENT_EMITTER","UNKNOWN"])
    b.add_argument("--action-id"); b.add_argument("--action-label"); b.add_argument("--action-phase",choices=sorted(ACTION_PHASES))
    b.add_argument("--tool-name"); b.add_argument("--tool-call-id"); b.add_argument("--outcome"); b.add_argument("--written-head")
    b.add_argument("--checkpoint-ref"); b.add_argument("--evidence-ref"); b.add_argument("--interruption-code",choices=sorted(INTERRUPTION_CODES))
    b.set_defaults(fn=command_beacon)

    c=sub.add_parser("correlate")
    c.set_defaults(fn=command_correlate)

    d=sub.add_parser("dispatch")
    d.set_defaults(fn=command_dispatch)

    ctx=sub.add_parser("context")
    ctx.add_argument("--session-id",required=True)
    ctx.set_defaults(fn=command_context)

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
