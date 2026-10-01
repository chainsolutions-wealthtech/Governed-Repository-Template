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
from urllib.parse import urlparse

from gacr_agent_telemetry import record_beacon, correlate_all, dispatch_open_takeovers

ROOT = Path(os.environ.get("GACR_ROOT") or Path(__file__).resolve().parents[1]).resolve()
GOV = ROOT / ".governance"
TEMPLATE_SOURCE = (ROOT / ".template-source").exists()
CONFIG_PATH = GOV / "agent-relay" / "config.json"
WORK_PATH = GOV / "work" / "work-items.json"

if TEMPLATE_SOURCE:
    SESSIONS_PATH = GOV / "control-plane-state" / "gacr-sessions.json"
    CLAIMS_PATH = GOV / "control-plane-state" / "gacr-claims.json"
    TAKEOVERS_PATH = GOV / "control-plane-state" / "gacr-takeovers.json"
else:
    SESSIONS_PATH = GOV / "sessions" / "sessions.json"
    CLAIMS_PATH = GOV / "work" / "claims.json"
    TAKEOVERS_PATH = GOV / "agent-relay" / "takeovers.json"

ACTIVEISH = {"ACTIVE", "SUSPECTED_STALL", "STALLED", "TAKEOVER_READY", "STANDBY"}
TERMINAL_RELAY = {"HANDOFF_STALLED", "CLOSED"}
PROVIDERS = {"chatgpt", "claude", "codex", "github-actions", "human", "other"}


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def git_head() -> str | None:
    cp = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False)
    return cp.stdout.strip() if cp.returncode == 0 else None


def git_branch() -> str | None:
    cp = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, text=True, capture_output=True, check=False)
    return cp.stdout.strip() if cp.returncode == 0 else None


def remote_branch_head(branch: str) -> str | None:
    if not branch:
        return git_head()
    cp = subprocess.run(["git", "fetch", "--quiet", "origin", branch], cwd=ROOT, text=True, capture_output=True, check=False)
    if cp.returncode != 0:
        return None
    cp = subprocess.run(["git", "rev-parse", "FETCH_HEAD"], cwd=ROOT, text=True, capture_output=True, check=False)
    return cp.stdout.strip() if cp.returncode == 0 else None


def repository_name() -> str:
    env = os.environ.get("GITHUB_REPOSITORY")
    if env:
        return env
    cp = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, text=True, capture_output=True, check=False)
    if cp.returncode == 0:
        url = cp.stdout.strip()
        m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
        if m:
            return m.group(1)
    profile = GOV / "profile.json"
    if profile.exists():
        value = read_json(profile).get("repository")
        if value and "{{" not in value:
            return value
    return "UNKNOWN_REPOSITORY"


def conversation_ref(provider: str, provider_ref: str | None, provider_url: str | None) -> tuple[str | None, str | None]:
    if provider_ref:
        return provider_ref.strip(), "PROVIDED_BY_CLIENT"
    if provider_url and provider == "chatgpt":
        parsed = urlparse(provider_url)
        m = re.fullmatch(r"/c/([A-Za-z0-9-]+)", parsed.path.rstrip("/"))
        if parsed.netloc in {"chatgpt.com", "www.chatgpt.com"} and m:
            return m.group(1), "EXTRACTED_FROM_EXPLICIT_URL"
    return None, "UNAVAILABLE"


def reconstruct_url(provider: str, ref: str | None) -> str | None:
    if not ref:
        return None
    if provider == "chatgpt":
        return f"https://chatgpt.com/c/{ref}"
    return None


def stable_session_id(repository: str, agent: str, provider: str, strongest_ref: str) -> str:
    raw = json.dumps({
        "repository": repository,
        "agent": agent,
        "provider": provider,
        "strongest_ref": strongest_ref,
    }, sort_keys=True)
    return "session-" + hashlib.sha256(raw.encode()).hexdigest()[:24]


def takeover_id(session_id: str, created_at: str) -> str:
    raw = f"{session_id}|{created_at}".encode()
    return "GACR-T-" + hashlib.sha256(raw).hexdigest()[:12]


def load_all() -> tuple[dict, dict, dict, dict, dict]:
    return (
        read_json(CONFIG_PATH),
        read_json(SESSIONS_PATH),
        read_json(CLAIMS_PATH),
        read_json(WORK_PATH),
        read_json(TAKEOVERS_PATH),
    )


def relay(session: dict) -> dict:
    return session.setdefault("relay", {})


def ensure_relay(session: dict, config: dict, timestamp: datetime, standby: bool | None = None) -> dict:
    r = relay(session)
    if not r:
        base_state = "STANDBY" if standby else "ACTIVE"
        r.update({
            "process": "GACR",
            "state": base_state,
            "last_heartbeat_at": iso(timestamp),
            "lease_expires_at": iso(timestamp + timedelta(seconds=int(config["stalled_after_seconds"]))),
            "last_action": "REGISTER",
            "task_id": None,
            "branch": None,
            "pull_request": None,
        })
    return r


def active_claims_for(claims_doc: dict, session_id: str) -> list[dict]:
    return [
        c for c in claims_doc.get("claims", [])
        if c.get("session_id") == session_id and c.get("status") == "ACTIVE"
    ]


def find_compatible_standby(sessions_doc: dict, stalled: dict) -> dict | None:
    candidates = []
    for s in sessions_doc.get("sessions", []):
        if s.get("session_id") == stalled.get("session_id"):
            continue
        r = s.get("relay") or {}
        if s.get("status") != "STANDBY" or r.get("state") != "STANDBY":
            continue
        if s.get("repository") != stalled.get("repository"):
            continue
        candidates.append(s)
    candidates.sort(key=lambda s: (s.get("created_at") or "", s.get("session_id") or ""))
    return candidates[0] if candidates else None


def register_docs(
    config: dict,
    sessions_doc: dict,
    *,
    repository: str,
    agent: str,
    provider: str,
    provider_ref: str | None,
    provider_url: str | None,
    connection_ref: str | None,
    observed_head: str | None,
    branch: str | None,
    task_id: str | None,
    pull_request: int | None,
    standby: bool,
    client_instance_id: str | None = None,
    agent_role: str | None = None,
    capabilities: list[str] | None = None,
    wake_channels: list[str] | None = None,
    bridge_registration_ref: str | None = None,
    timestamp: datetime,
) -> tuple[dict, str]:
    if provider not in PROVIDERS:
        raise ValueError("unsupported provider")
    ref, provenance = conversation_ref(provider, provider_ref, provider_url)
    sessions = sessions_doc.setdefault("sessions", [])

    matches = []
    if ref:
        matches = [
            s for s in sessions
            if s.get("repository") == repository
            and s.get("provider") == provider
            and s.get("provider_conversation_ref") == ref
            and (s.get("relay") or {}).get("state") not in TERMINAL_RELAY
        ]
    elif connection_ref:
        matches = [
            s for s in sessions
            if s.get("repository") == repository
            and s.get("connection_ref") == connection_ref
            and (s.get("relay") or {}).get("state") not in TERMINAL_RELAY
        ]

    if len(matches) > 1:
        raise ValueError("ambiguous existing relay session")

    if matches:
        session = matches[0]
        relay_state = (session.get("relay") or {}).get("state")
        if relay_state == "HANDOFF_STALLED":
            raise ValueError("predecessor ownership already transferred")
        if relay_state in {"STALLED", "TAKEOVER_READY"}:
            raise ValueError("stalled session requires governed reconciliation before resume")
        resolution = "RESUME"
    else:
        strongest_ref = (
            f"provider:{ref}" if ref
            else f"connection:{connection_ref}" if connection_ref
            else f"local:{agent}:{observed_head}:{iso(timestamp)}"
        )
        session = {
            "session_id": stable_session_id(repository, agent, provider, strongest_ref),
            "agent_identity": agent,
            "provider": provider,
            "provider_conversation_ref": ref,
            "provider_conversation_ref_provenance": provenance,
            "connection_ref": connection_ref,
            "entry_action": "UNKNOWN",
            "entry_action_provenance": "DEFAULT_UNKNOWN",
            "connection_intent": "UNKNOWN",
            "connection_intent_provenance": "DEFAULT_UNKNOWN",
            "repository": repository,
            "starting_head_sha": observed_head,
            "last_observed_head_sha": observed_head,
            "status": "STANDBY" if standby else "ACTIVE",
            "created_at": iso(timestamp),
            "last_seen_at": iso(timestamp),
            "client_instance_id": client_instance_id,
            "agent_role": agent_role,
            "capabilities": sorted(set(capabilities or [])),
            "wake_channels": sorted(set(wake_channels or [])),
            "bridge_registration_ref": bridge_registration_ref,
        }
        sessions.append(session)
        resolution = "CREATE"

    r = ensure_relay(session, config, timestamp, standby)
    desired = "STANDBY" if standby else "ACTIVE"
    session["status"] = desired
    session["last_seen_at"] = iso(timestamp)
    if observed_head:
        session["last_observed_head_sha"] = observed_head
    if ref:
        session["provider_conversation_ref"] = ref
        session["provider_conversation_ref_provenance"] = provenance
    if client_instance_id:
        session["client_instance_id"] = client_instance_id
    if agent_role:
        session["agent_role"] = agent_role
    if capabilities:
        session["capabilities"] = sorted(set((session.get("capabilities") or []) + capabilities))
    if wake_channels:
        session["wake_channels"] = sorted(set((session.get("wake_channels") or []) + wake_channels))
    if bridge_registration_ref:
        session["bridge_registration_ref"] = bridge_registration_ref
    if provider_url and config.get("external_conversation_reference", {}).get("persist_full_url") is True:
        session["provider_conversation_url"] = provider_url
    elif "provider_conversation_url" in session and config.get("external_conversation_reference", {}).get("persist_full_url") is not True:
        session.pop("provider_conversation_url", None)

    r.update({
        "process": "GACR",
        "state": desired,
        "last_heartbeat_at": iso(timestamp),
        "lease_expires_at": iso(timestamp + timedelta(seconds=int(config["stalled_after_seconds"]))),
        "last_action": "REGISTER" if resolution == "CREATE" else "RESUME",
        "task_id": task_id if task_id is not None else r.get("task_id"),
        "branch": branch if branch is not None else r.get("branch"),
        "pull_request": pull_request if pull_request is not None else r.get("pull_request"),
    })

    sessions_doc["revision"] = int(sessions_doc.get("revision", 0)) + 1
    return session, resolution


def heartbeat_docs(
    config: dict,
    sessions_doc: dict,
    *,
    session_id: str,
    observed_head: str | None,
    action: str | None,
    evidence: str | None,
    timestamp: datetime,
) -> dict:
    session = next((s for s in sessions_doc.get("sessions", []) if s.get("session_id") == session_id), None)
    if not session:
        raise ValueError("session not found")
    r = ensure_relay(session, config, timestamp)
    if r.get("state") == "HANDOFF_STALLED":
        raise ValueError("predecessor cannot resume after takeover")
    if r.get("state") in {"STALLED", "TAKEOVER_READY"}:
        raise ValueError("stalled session requires governed reconciliation before heartbeat")
    desired = "STANDBY" if session.get("status") == "STANDBY" else "ACTIVE"
    session["status"] = desired
    session["last_seen_at"] = iso(timestamp)
    if observed_head:
        session["last_observed_head_sha"] = observed_head
    r["state"] = desired
    r["last_heartbeat_at"] = iso(timestamp)
    r["lease_expires_at"] = iso(timestamp + timedelta(seconds=int(config["stalled_after_seconds"])))
    if action:
        r["last_action"] = action
    else:
        r["last_action"] = "HEARTBEAT"
    if evidence:
        r["last_evidence"] = evidence
    sessions_doc["revision"] = int(sessions_doc.get("revision", 0)) + 1
    return session


def scan_docs(
    config: dict,
    sessions_doc: dict,
    claims_doc: dict,
    takeovers_doc: dict,
    *,
    timestamp: datetime,
) -> dict:
    suspect_after = int(config["suspected_stall_after_seconds"])
    stalled_after = int(config["stalled_after_seconds"])
    changes = {"suspected": [], "stalled": [], "takeovers_created": [], "offers": []}

    open_by_stalled = {
        x.get("stalled_session_id"): x
        for x in takeovers_doc.get("items", [])
        if x.get("status") in {"READY_FOR_RECONCILIATION", "OFFERED"}
    }

    for session in sessions_doc.get("sessions", []):
        r = session.get("relay") or {}
        if r.get("process") != "GACR":
            continue
        if r.get("state") in TERMINAL_RELAY or r.get("state") == "STANDBY":
            continue
        last = parse_time(r.get("last_heartbeat_at") or session.get("last_seen_at"))
        if not last:
            continue
        age = (timestamp - last).total_seconds()

        if age >= stalled_after:
            if r.get("state") not in {"STALLED", "TAKEOVER_READY"}:
                session["status"] = "STALLED"
                r["state"] = "STALLED"
                r["stalled_at"] = iso(timestamp)
                r["last_action"] = "STALL_DETECTED"
                changes["stalled"].append(session["session_id"])

            item = open_by_stalled.get(session["session_id"])
            if item is None:
                claims = active_claims_for(claims_doc, session["session_id"])
                created = iso(timestamp)
                item = {
                    "takeover_id": takeover_id(session["session_id"], created),
                    "stalled_session_id": session["session_id"],
                    "offered_to_session_id": None,
                    "accepted_by_session_id": None,
                    "status": "READY_FOR_RECONCILIATION",
                    "created_at": created,
                    "accepted_at": None,
                    "work_item_id": claims[0].get("work_item_id") if len(claims) == 1 else None,
                    "task_id": r.get("task_id"),
                    "branch": r.get("branch"),
                    "pull_request": r.get("pull_request"),
                    "last_observed_head_sha": session.get("last_observed_head_sha"),
                    "reconciled_head_sha": None,
                    "active_claim_count": len(claims),
                }
                takeovers_doc.setdefault("items", []).append(item)
                open_by_stalled[session["session_id"]] = item
                changes["takeovers_created"].append(item["takeover_id"])

            if config.get("takeover", {}).get("auto_offer_to_compatible_standby") is True and not item.get("offered_to_session_id"):
                standby = find_compatible_standby(sessions_doc, session)
                if standby:
                    item["offered_to_session_id"] = standby["session_id"]
                    item["status"] = "OFFERED"
                    changes["offers"].append({
                        "takeover_id": item["takeover_id"],
                        "standby_session_id": standby["session_id"],
                    })
            r["state"] = "TAKEOVER_READY"
            session["status"] = "STALLED"
        elif age >= suspect_after:
            if r.get("state") == "ACTIVE":
                r["state"] = "SUSPECTED_STALL"
                changes["suspected"].append(session["session_id"])
        elif r.get("state") == "SUSPECTED_STALL":
            r["state"] = "ACTIVE"

    if any(changes.values()):
        sessions_doc["revision"] = int(sessions_doc.get("revision", 0)) + 1
        takeovers_doc["revision"] = int(takeovers_doc.get("revision", 0)) + 1
        takeovers_doc["last_scan_at"] = iso(timestamp)
    return changes


def accept_takeover_docs(
    config: dict,
    sessions_doc: dict,
    claims_doc: dict,
    takeovers_doc: dict,
    *,
    stalled_session_id: str,
    successor_session_id: str,
    reconciled_head_sha: str,
    actual_work_head_sha: str,
    timestamp: datetime,
) -> dict:
    predecessor = next((s for s in sessions_doc.get("sessions", []) if s.get("session_id") == stalled_session_id), None)
    successor = next((s for s in sessions_doc.get("sessions", []) if s.get("session_id") == successor_session_id), None)
    if not predecessor or not successor:
        raise ValueError("predecessor or successor session not found")
    pr = predecessor.get("relay") or {}
    sr = successor.get("relay") or {}
    if pr.get("state") not in {"STALLED", "TAKEOVER_READY"}:
        raise ValueError("predecessor is not stalled")
    if successor.get("status") != "STANDBY" or sr.get("state") != "STANDBY":
        raise ValueError("successor is not standby")
    if predecessor.get("repository") != successor.get("repository"):
        raise ValueError("cross-repository takeover forbidden")
    if reconciled_head_sha != actual_work_head_sha:
        raise ValueError("takeover exact-head reconciliation failed")

    item = next((
        x for x in takeovers_doc.get("items", [])
        if x.get("stalled_session_id") == stalled_session_id
        and x.get("status") in {"READY_FOR_RECONCILIATION", "OFFERED"}
    ), None)
    if not item:
        raise ValueError("takeover queue item not found")
    offered = item.get("offered_to_session_id")
    if offered and offered != successor_session_id:
        raise ValueError("takeover offered to another standby session")

    if active_claims_for(claims_doc, successor_session_id):
        raise ValueError("successor already owns an active claim")

    transferred = []
    for claim in claims_doc.get("claims", []):
        if claim.get("session_id") == stalled_session_id and claim.get("status") == "ACTIVE":
            claim["transferred_from_session_id"] = stalled_session_id
            claim["session_id"] = successor_session_id
            claim["claimed_head_sha"] = actual_work_head_sha
            claim["transferred_at"] = iso(timestamp)
            transferred.append(claim.get("work_item_id"))

    predecessor["status"] = "CLOSED"
    pr["state"] = "HANDOFF_STALLED"
    pr["handoff_at"] = iso(timestamp)
    pr["successor_session_id"] = successor_session_id

    successor["status"] = "ACTIVE"
    successor["last_seen_at"] = iso(timestamp)
    successor["last_observed_head_sha"] = actual_work_head_sha
    sr["state"] = "ACTIVE"
    sr["last_heartbeat_at"] = iso(timestamp)
    sr["lease_expires_at"] = iso(timestamp + timedelta(seconds=int(config["stalled_after_seconds"])))
    sr["last_action"] = "TAKEOVER_ACCEPTED"
    sr["predecessor_session_id"] = stalled_session_id
    if not sr.get("task_id"):
        sr["task_id"] = pr.get("task_id")
    if not sr.get("branch"):
        sr["branch"] = pr.get("branch")
    if sr.get("pull_request") is None:
        sr["pull_request"] = pr.get("pull_request")

    item["accepted_by_session_id"] = successor_session_id
    item["status"] = "ACCEPTED"
    item["accepted_at"] = iso(timestamp)
    item["reconciled_head_sha"] = actual_work_head_sha

    sessions_doc["revision"] = int(sessions_doc.get("revision", 0)) + 1
    claims_doc["revision"] = int(claims_doc.get("revision", 0)) + 1
    takeovers_doc["revision"] = int(takeovers_doc.get("revision", 0)) + 1

    return {
        "status": "TAKEOVER_ACCEPTED",
        "takeover_id": item["takeover_id"],
        "predecessor_session_id": stalled_session_id,
        "successor_session_id": successor_session_id,
        "reconciled_head_sha": actual_work_head_sha,
        "transferred_work_items": transferred,
        "may_continue_mutable_work": True,
    }


def save(sessions_doc: dict, claims_doc: dict, takeovers_doc: dict) -> None:
    write_json(SESSIONS_PATH, sessions_doc)
    write_json(CLAIMS_PATH, claims_doc)
    write_json(TAKEOVERS_PATH, takeovers_doc)


def command_register(a: argparse.Namespace) -> None:
    config, sessions, claims, work, takeovers = load_all()
    timestamp = now_utc()
    head = a.observed_head or git_head()
    branch = a.branch or git_branch()
    session, resolution = register_docs(
        config, sessions,
        repository=a.repository or repository_name(),
        agent=a.agent,
        provider=a.provider,
        provider_ref=a.provider_ref,
        provider_url=a.provider_url,
        connection_ref=a.connection_ref,
        observed_head=head,
        branch=branch,
        task_id=a.task_id,
        pull_request=a.pull_request,
        standby=a.standby,
        client_instance_id=a.client_instance_id,
        agent_role=a.agent_role,
        capabilities=a.capability or [],
        wake_channels=a.wake_channel or [],
        bridge_registration_ref=a.bridge_registration_ref,
        timestamp=timestamp,
    )
    save(sessions, claims, takeovers)
    record_beacon(session=session, event_type="REGISTER" if resolution == "CREATE" else "RESUME")
    correlate_all()
    ref = session.get("provider_conversation_ref")
    print(json.dumps({
        "status": resolution,
        "process": "GACR",
        "session": session,
        "reconstructed_provider_url": reconstruct_url(session.get("provider"), ref),
    }, indent=2, ensure_ascii=False))


def command_heartbeat(a: argparse.Namespace) -> None:
    config, sessions, claims, work, takeovers = load_all()
    session = heartbeat_docs(
        config, sessions,
        session_id=a.session_id,
        observed_head=a.observed_head or git_head(),
        action=a.action,
        evidence=a.evidence,
        timestamp=now_utc(),
    )
    save(sessions, claims, takeovers)
    record_beacon(session=session, event_type="HEARTBEAT")
    correlate_all()
    print(json.dumps({"status": "HEARTBEAT_RECORDED", "session": session}, indent=2, ensure_ascii=False))


def command_scan(_: argparse.Namespace) -> None:
    config, sessions, claims, work, takeovers = load_all()
    changes = scan_docs(config, sessions, claims, takeovers, timestamp=now_utc())
    save(sessions, claims, takeovers)
    correlation = correlate_all()
    dispatch = dispatch_open_takeovers()
    print(json.dumps({
        "status": "SUPERVISOR_SCAN_COMPLETE",
        "changes": changes,
        "correlation": correlation,
        "dispatch": dispatch,
    }, indent=2, ensure_ascii=False))


def command_status(_: argparse.Namespace) -> None:
    config, sessions, claims, work, takeovers = load_all()
    rendered = []
    for s in sessions.get("sessions", []):
        r = s.get("relay")
        if not r:
            continue
        rendered.append({
            "session_id": s.get("session_id"),
            "agent": s.get("agent_identity"),
            "provider": s.get("provider"),
            "provider_conversation_ref": s.get("provider_conversation_ref"),
            "provider_url": reconstruct_url(s.get("provider"), s.get("provider_conversation_ref")),
            "repository": s.get("repository"),
            "status": s.get("status"),
            "relay_state": r.get("state"),
            "task_id": r.get("task_id"),
            "branch": r.get("branch"),
            "pull_request": r.get("pull_request"),
            "last_heartbeat_at": r.get("last_heartbeat_at"),
            "lease_expires_at": r.get("lease_expires_at"),
            "active_claims": [c.get("work_item_id") for c in active_claims_for(claims, s.get("session_id"))],
        })
    print(json.dumps({
        "process": "GACR",
        "sessions": rendered,
        "takeovers": takeovers.get("items", []),
    }, indent=2, ensure_ascii=False))


def command_identify(a: argparse.Namespace) -> None:
    _, sessions, _, _, _ = load_all()
    ref, _ = conversation_ref(a.provider, a.provider_ref, a.provider_url)
    matches = [
        s for s in sessions.get("sessions", [])
        if s.get("provider") == a.provider and s.get("provider_conversation_ref") == ref
    ]
    print(json.dumps({
        "status": "FOUND" if matches else "NOT_FOUND",
        "provider": a.provider,
        "provider_ref": ref,
        "provider_url": reconstruct_url(a.provider, ref),
        "sessions": matches,
    }, indent=2, ensure_ascii=False))


def command_takeover_plan(a: argparse.Namespace) -> None:
    _, sessions, claims, _, takeovers = load_all()
    predecessor = next((s for s in sessions.get("sessions", []) if s.get("session_id") == a.stalled_session_id), None)
    if not predecessor:
        raise SystemExit("GACR_TAKEOVER_PLAN_FAILED: stalled session not found")
    r = predecessor.get("relay") or {}
    item = next((x for x in takeovers.get("items", []) if x.get("stalled_session_id") == a.stalled_session_id and x.get("status") in {"READY_FOR_RECONCILIATION","OFFERED"}), None)
    branch = r.get("branch")
    actual = remote_branch_head(branch) if branch else git_head()
    print(json.dumps({
        "status": "TAKEOVER_PLAN",
        "stalled_session_id": a.stalled_session_id,
        "task_id": r.get("task_id"),
        "branch": branch,
        "pull_request": r.get("pull_request"),
        "predecessor_last_observed_head_sha": predecessor.get("last_observed_head_sha"),
        "actual_work_head_sha": actual,
        "active_claims": active_claims_for(claims, a.stalled_session_id),
        "takeover": item,
        "next_action": "RECONCILE_BRANCH_PR_AND_ACCEPT_TAKEOVER",
        "may_write": False,
    }, indent=2, ensure_ascii=False))


def command_takeover_accept(a: argparse.Namespace) -> None:
    config, sessions, claims, work, takeovers = load_all()
    predecessor = next((s for s in sessions.get("sessions", []) if s.get("session_id") == a.stalled_session_id), None)
    if not predecessor:
        raise SystemExit("GACR_TAKEOVER_FAILED: predecessor not found")
    branch = (predecessor.get("relay") or {}).get("branch")
    actual = remote_branch_head(branch) if branch else git_head()
    if not actual:
        raise SystemExit("GACR_TAKEOVER_FAILED: unable to observe work HEAD")
    result = accept_takeover_docs(
        config, sessions, claims, takeovers,
        stalled_session_id=a.stalled_session_id,
        successor_session_id=a.successor_session_id,
        reconciled_head_sha=a.reconciled_head,
        actual_work_head_sha=actual,
        timestamp=now_utc(),
    )
    save(sessions, claims, takeovers)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="GACR — Governed Agent Continuity Relay")
    sub = p.add_subparsers(dest="command", required=True)

    reg = sub.add_parser("register")
    reg.add_argument("--agent", required=True)
    reg.add_argument("--provider", choices=sorted(PROVIDERS), required=True)
    reg.add_argument("--provider-ref")
    reg.add_argument("--provider-url")
    reg.add_argument("--connection-ref")
    reg.add_argument("--repository")
    reg.add_argument("--observed-head")
    reg.add_argument("--branch")
    reg.add_argument("--task-id")
    reg.add_argument("--pull-request", type=int)
    reg.add_argument("--standby", action="store_true")
    reg.add_argument("--client-instance-id")
    reg.add_argument("--agent-role")
    reg.add_argument("--capability", action="append")
    reg.add_argument("--wake-channel", action="append", choices=["POLL_REPOSITORY","REPOSITORY_DISPATCH","EXTERNAL_BRIDGE"])
    reg.add_argument("--bridge-registration-ref")
    reg.set_defaults(fn=command_register)

    hb = sub.add_parser("heartbeat")
    hb.add_argument("--session-id", required=True)
    hb.add_argument("--observed-head")
    hb.add_argument("--action")
    hb.add_argument("--evidence")
    hb.set_defaults(fn=command_heartbeat)

    scan = sub.add_parser("scan")
    scan.set_defaults(fn=command_scan)

    status = sub.add_parser("status")
    status.set_defaults(fn=command_status)

    identify = sub.add_parser("identify")
    identify.add_argument("--provider", choices=sorted(PROVIDERS), required=True)
    identify.add_argument("--provider-ref")
    identify.add_argument("--provider-url")
    identify.set_defaults(fn=command_identify)

    plan = sub.add_parser("takeover-plan")
    plan.add_argument("--stalled-session-id", required=True)
    plan.set_defaults(fn=command_takeover_plan)

    takeover = sub.add_parser("takeover-accept")
    takeover.add_argument("--stalled-session-id", required=True)
    takeover.add_argument("--successor-session-id", required=True)
    takeover.add_argument("--reconciled-head", required=True)
    takeover.set_defaults(fn=command_takeover_accept)

    return p


def main() -> None:
    args = parser().parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
