#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import urllib.error
import urllib.request
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GOV = ROOT / ".governance"
TEMPLATE_SOURCE = (ROOT / ".template-source").exists()
CONFIG_PATH = GOV / "agent-relay" / "config.json"
SESSIONS_PATH = (
    GOV / "control-plane-state" / "gacr-sessions.json"
    if TEMPLATE_SOURCE else GOV / "sessions" / "sessions.json"
)
DISPATCHES_PATH = (
    GOV / "control-plane-state" / "gacr-dispatches.json"
    if TEMPLATE_SOURCE else GOV / "agent-relay" / "dispatches.json"
)

COMMAND_SCHEMA = "gscc-control-command/v1"
DISPATCH_SCHEMA = "gscc-control-dispatch/v1"
REQUEST_PREFIX = "/gscc-control "
COMMAND_PREFIX = "/gscc-control-command "
VERIFIED_CONTROL_CAPABILITIES = ["COMMAND_RECEIVE", "COMMAND_ACK", "CHALLENGE_RESPONSE"]
CHALLENGE_STATUSES = {"ACK", "BUSY", "IDLE", "CHECKPOINTING", "TERMINATING", "UNSUPPORTED"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _parse(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _id(prefix: str, value: Any) -> str:
    return prefix + _digest(value)[:24]


def read_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return deepcopy(default or {})
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _live_session(session: dict[str, Any], now: datetime) -> None:
    if session.get("status") != "ACTIVE":
        raise ValueError("GACR session is not ACTIVE")
    relay = session.get("relay") if isinstance(session.get("relay"), dict) else {}
    if relay.get("state") != "ACTIVE":
        raise ValueError("GACR relay is not ACTIVE")
    expiry = _parse(relay.get("lease_expires_at"))
    if expiry is None or expiry <= now:
        raise ValueError("GACR session lease is expired or unavailable")
    if not session.get("session_id") or not session.get("connection_ref"):
        raise ValueError("GACR session identity incomplete")


def build_liveness_challenge_dispatch(
    session: dict[str, Any],
    *,
    now: datetime | None = None,
    ttl_seconds: int = 60,
    issue_number: int = 115,
    nonce: str | None = None,
) -> dict[str, Any]:
    now = (now or _now()).astimezone(timezone.utc)
    _live_session(session, now)
    ttl = max(1, min(int(ttl_seconds), 300))
    expires = now + timedelta(seconds=ttl)
    nonce = nonce or secrets.token_urlsafe(24)
    seed = {
        "session_id": session["session_id"],
        "connection_ref": session["connection_ref"],
        "issued_at": _iso(now),
        "nonce": nonce,
    }
    command_id = _id("GSCC-CMD-", seed)
    challenge_id = _id("GSCC-CH-", {**seed, "command_id": command_id})
    correlation_id = _id("GSCC-CORR-", {"command_id": command_id, "challenge_id": challenge_id})
    message_id = _id("GSCC-MSG-", {"command_id": command_id, "correlation_id": correlation_id})
    dispatch_id = _id("GSCC-CTRL-", {"message_id": message_id, "target": session["session_id"]})
    command = {
        "schema": COMMAND_SCHEMA,
        "message_id": message_id,
        "command_id": command_id,
        "correlation_id": correlation_id,
        "command_type": "LIVENESS_CHALLENGE",
        "target_session_id": session["session_id"],
        "issued_at": _iso(now),
        "expires_at": _iso(expires),
        "requires_ack": True,
        "payload": {
            "challenge_id": challenge_id,
            "nonce": nonce,
            "issued_at": _iso(now),
            "expires_at": _iso(expires),
        },
    }
    return {
        "schema": DISPATCH_SCHEMA,
        "dispatch_id": dispatch_id,
        "kind": "CONTROL_CHALLENGE",
        "status": "READY",
        "target_session_id": session["session_id"],
        "target_connection_ref": session["connection_ref"],
        "repository": session.get("repository"),
        "branch": (session.get("relay") or {}).get("branch"),
        "issue_number": int(issue_number),
        "delivery_modes": ["GITHUB_ISSUE_COMMENT"],
        "created_at": _iso(now),
        "expires_at": _iso(expires),
        "command": command,
        "ack": None,
        "response": None,
        "invocation_authority_granted": False,
        "mutation_authority_granted": False,
    }


def render_issue_challenge_comment(item: dict[str, Any]) -> str:
    if item.get("kind") != "CONTROL_CHALLENGE":
        raise ValueError("control challenge dispatch required")
    command = item.get("command") or {}
    payload = {
        "schema": command.get("schema"),
        "dispatch_id": item.get("dispatch_id"),
        "message_id": command.get("message_id"),
        "command_id": command.get("command_id"),
        "correlation_id": command.get("correlation_id"),
        "command_type": command.get("command_type"),
        "target_session_id": command.get("target_session_id"),
        "challenge_id": (command.get("payload") or {}).get("challenge_id"),
        "nonce": (command.get("payload") or {}).get("nonce"),
        "issued_at": command.get("issued_at"),
        "expires_at": command.get("expires_at"),
        "requires_ack": True,
    }
    return COMMAND_PREFIX + json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def _dispatch(store: dict[str, Any], dispatch_id: str) -> dict[str, Any]:
    matches = [
        item for item in (store.get("items") or [])
        if isinstance(item, dict) and item.get("dispatch_id") == dispatch_id
    ]
    if len(matches) != 1:
        raise ValueError("control dispatch not found or ambiguous")
    item = matches[0]
    if item.get("kind") != "CONTROL_CHALLENGE":
        raise ValueError("dispatch is not a control challenge")
    return item


def _validate_common(item: dict[str, Any], payload: dict[str, Any], observed: datetime) -> dict[str, Any]:
    command = item.get("command") or {}
    if payload.get("session_id") != item.get("target_session_id"):
        raise ValueError("target session mismatch")
    for key in ("command_id", "correlation_id"):
        if payload.get(key) != command.get(key):
            raise ValueError(f"{key} mismatch")
    expiry = _parse(item.get("expires_at") or command.get("expires_at"))
    if expiry is None or observed > expiry:
        item["status"] = "EXPIRED"
        raise ValueError("control challenge expired")
    return command


def apply_host_control_event(
    store: dict[str, Any],
    payload: dict[str, Any],
    *,
    evidence_ref: str,
    observed_at: str,
) -> dict[str, Any]:
    observed = _parse(observed_at)
    if observed is None:
        raise ValueError("observed_at is invalid")
    event = str(payload.get("event") or "")
    if event not in {"command_ack", "challenge_response"}:
        raise ValueError("unsupported host control event")
    item = _dispatch(store, str(payload.get("dispatch_id") or ""))
    command = _validate_common(item, payload, observed)

    if event == "command_ack":
        state = str(payload.get("delivery_state") or "")
        if state not in {"ACKNOWLEDGED", "UNSUPPORTED"}:
            raise ValueError("unsupported command ACK delivery state")
        ack = {
            "delivery_state": state,
            "evidence_ref": evidence_ref,
            "observed_at": _iso(observed),
        }
        item["ack"] = ack
        item["status"] = "ACKNOWLEDGED" if state == "ACKNOWLEDGED" else "UNSUPPORTED"
        store["revision"] = int(store.get("revision", 0)) + 1
        return {"status": item["status"], "dispatch_id": item["dispatch_id"], "ack": deepcopy(ack)}

    ack = item.get("ack")
    if not isinstance(ack, dict) or ack.get("delivery_state") != "ACKNOWLEDGED":
        raise ValueError("challenge response requires prior ACKNOWLEDGED")
    challenge = command.get("payload") or {}
    if payload.get("challenge_id") != challenge.get("challenge_id"):
        raise ValueError("challenge_id mismatch")
    if payload.get("nonce") != challenge.get("nonce"):
        raise ValueError("nonce mismatch")
    status = str(payload.get("challenge_status") or "")
    if status not in CHALLENGE_STATUSES:
        raise ValueError("unsupported challenge status")
    if item.get("response"):
        return {
            "status": "ALREADY_COMPLETED",
            "dispatch_id": item["dispatch_id"],
            "fresh_liveness": False,
            "replay": True,
        }
    fresh = status != "UNSUPPORTED"
    response = {
        "challenge_status": status,
        "challenge_id": challenge.get("challenge_id"),
        "fresh_liveness": fresh,
        "replay": False,
        "evidence_ref": evidence_ref,
        "observed_at": _iso(observed),
    }
    item["response"] = response
    item["status"] = "COMPLETED" if fresh else "UNSUPPORTED"
    item["completed_at"] = _iso(observed)
    store["revision"] = int(store.get("revision", 0)) + 1
    return {
        "status": item["status"],
        "dispatch_id": item["dispatch_id"],
        "fresh_liveness": fresh,
        "replay": False,
        "response": deepcopy(response),
    }


def canonical_control_evidence(
    store: dict[str, Any],
    *,
    session_id: str,
    now: datetime | None = None,
    freshness_seconds: int = 900,
) -> dict[str, Any]:
    now = (now or _now()).astimezone(timezone.utc)
    candidates = []
    for item in store.get("items") or []:
        if not isinstance(item, dict):
            continue
        if item.get("kind") != "CONTROL_CHALLENGE" or item.get("target_session_id") != session_id:
            continue
        if item.get("status") != "COMPLETED":
            continue
        ack = item.get("ack") or {}
        response = item.get("response") or {}
        if ack.get("delivery_state") != "ACKNOWLEDGED" or response.get("fresh_liveness") is not True:
            continue
        observed = _parse(response.get("observed_at"))
        if observed is None or (now - observed).total_seconds() > freshness_seconds:
            continue
        candidates.append(item)
    candidates.sort(key=lambda item: ((item.get("response") or {}).get("observed_at") or "", item.get("dispatch_id") or ""))
    if not candidates:
        return {
            "capabilities": {
                "status": "UNAVAILABLE",
                "reason": "CANONICAL_CONTROL_CHALLENGE_EVIDENCE_REQUIRED",
                "verified": [],
            },
            "control_channel": {
                "status": "UNAVAILABLE",
                "reason": "CANONICAL_CONTROL_CHALLENGE_EVIDENCE_REQUIRED",
            },
        }
    item = candidates[-1]
    response = item["response"]
    evidence_ref = response["evidence_ref"]
    return {
        "capabilities": {
            "status": "VERIFIED",
            "verified": list(VERIFIED_CONTROL_CAPABILITIES),
            "evidence_ref": evidence_ref,
            "dispatch_id": item["dispatch_id"],
            "provenance": "OBSERVABLE_BY_PLATFORM",
            "source": "GSCC_ISSUE_CONTROL_CHALLENGE",
            "observed_at": response["observed_at"],
        },
        "control_channel": {
            "status": "VERIFIED",
            "state": "REACHABLE",
            "evidence_ref": evidence_ref,
            "dispatch_id": item["dispatch_id"],
            "command_id": item["command"]["command_id"],
            "challenge_id": item["command"]["payload"]["challenge_id"],
            "provenance": "OBSERVABLE_BY_PLATFORM",
            "source": "GSCC_ISSUE_CONTROL_CHALLENGE",
            "observed_at": response["observed_at"],
        },
    }


def _find_session(session_id: str) -> dict[str, Any]:
    sessions = read_json(SESSIONS_PATH, {"sessions": []})
    matches = [x for x in sessions.get("sessions") or [] if isinstance(x, dict) and x.get("session_id") == session_id]
    if len(matches) != 1:
        raise ValueError("target GACR session not found or ambiguous")
    return matches[0]


def create_challenge(
    session_id: str,
    *,
    ttl_seconds: int = 60,
    issue_number: int | None = None,
    nonce: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = (now or _now()).astimezone(timezone.utc)
    config = read_json(CONFIG_PATH, {})
    host = config.get("host_issue_bridge") or {}
    issue_number = int(issue_number or host.get("issue_number") or 0)
    if issue_number <= 0:
        raise ValueError("host issue bridge issue number unavailable")
    session = _find_session(session_id)
    store = read_json(DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    for item in store.get("items") or []:
        if (
            isinstance(item, dict)
            and item.get("kind") == "CONTROL_CHALLENGE"
            and item.get("target_session_id") == session_id
            and item.get("status") in {"READY", "DISPATCHED", "ACKNOWLEDGED"}
            and (_parse(item.get("expires_at")) or now) > now
        ):
            return item
    item = build_liveness_challenge_dispatch(
        session,
        now=now,
        ttl_seconds=ttl_seconds,
        issue_number=issue_number,
        nonce=nonce,
    )
    store.setdefault("items", []).append(item)
    store["revision"] = int(store.get("revision", 0)) + 1
    write_json(DISPATCHES_PATH, store)
    return item


def _github_post_comment(repository: str, issue_number: int, body: str, token: str) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{repository}/issues/{issue_number}/comments"
    request = urllib.request.Request(
        url,
        method="POST",
        data=json.dumps({"body": body}, ensure_ascii=False).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "gscc-issue-control-bridge",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            value = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GitHub issue control delivery failed HTTP {exc.code}") from exc
    if not isinstance(value, dict) or not value.get("id"):
        raise RuntimeError("GitHub issue control delivery response invalid")
    return value


def deliver_pending(*, repository: str, token: str, now: datetime | None = None) -> dict[str, Any]:
    now = (now or _now()).astimezone(timezone.utc)
    store = read_json(DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
    delivered = []
    for item in store.get("items") or []:
        if not isinstance(item, dict) or item.get("kind") != "CONTROL_CHALLENGE" or item.get("status") != "READY":
            continue
        expiry = _parse(item.get("expires_at"))
        if expiry is None or expiry <= now:
            item["status"] = "EXPIRED"
            continue
        response = _github_post_comment(repository, int(item["issue_number"]), render_issue_challenge_comment(item), token)
        item["status"] = "DISPATCHED"
        item["delivered_at"] = _iso(now)
        item["delivery_evidence_ref"] = f"github-issue-comment:{response['id']}"
        delivered.append(item["dispatch_id"])
    if delivered:
        store["revision"] = int(store.get("revision", 0)) + 1
        write_json(DISPATCHES_PATH, store)
    return {"status": "GSCC_CONTROL_DELIVERY_COMPLETE", "dispatch_ids": delivered, "count": len(delivered)}


def main() -> None:
    parser = argparse.ArgumentParser(description="GSCC issue-comment control transport over canonical GACR dispatches")
    sub = parser.add_subparsers(dest="command", required=True)
    challenge = sub.add_parser("challenge")
    challenge.add_argument("--session-id", required=True)
    challenge.add_argument("--ttl-seconds", type=int, default=60)
    challenge.add_argument("--issue-number", type=int)
    challenge.add_argument("--nonce")
    deliver = sub.add_parser("deliver")
    evidence = sub.add_parser("evidence")
    evidence.add_argument("--session-id", required=True)
    args = parser.parse_args()

    if args.command == "challenge":
        item = create_challenge(
            args.session_id,
            ttl_seconds=args.ttl_seconds,
            issue_number=args.issue_number,
            nonce=args.nonce,
        )
        print(json.dumps({"status": "GSCC_CONTROL_CHALLENGE_READY", "dispatch": item}, indent=2, ensure_ascii=False))
    elif args.command == "deliver":
        repository = str(os.environ.get("GITHUB_REPOSITORY") or "")
        token = str(os.environ.get("GITHUB_TOKEN") or "")
        if repository.count("/") != 1 or not token:
            raise SystemExit("GSCC_CONTROL_DELIVERY_CONFIG_REQUIRED")
        print(json.dumps(deliver_pending(repository=repository, token=token), indent=2, ensure_ascii=False))
    else:
        store = read_json(DISPATCHES_PATH, {"items": []})
        print(json.dumps(canonical_control_evidence(store, session_id=args.session_id), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
