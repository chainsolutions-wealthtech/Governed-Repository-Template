#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from gscc_gacr.issue_control_bridge import (
    DISPATCHES_PATH,
    apply_host_control_event,
    read_json as read_control_json,
    write_json as write_control_json,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / ".governance" / "agent-relay" / "config.json"
AUTO_ATTACH = ROOT / "scripts" / "gacr_auto_attach.py"
CORE = ROOT / "scripts" / "governed_agent_continuity_relay.py"
TELEMETRY = ROOT / "scripts" / "gacr_agent_telemetry.py"

PREFIX = "/gacr-host "
SCHEMA = "gacr-host-event/v1"
EVENTS = {"attach", "heartbeat", "action", "interrupt", "command_ack", "challenge_response"}
ACTION_PHASES = {"STARTED", "COMPLETED", "FAILED", "CANCELLED"}
INTERRUPTION_CODES = {
    "CLIENT_DISCONNECTED",
    "PROVIDER_TIMEOUT",
    "TOOL_FAILURE",
    "AGENT_ERROR",
    "USER_CANCELLED",
    "NETWORK_LOSS",
    "PROCESS_EXITED",
    "UNKNOWN",
}
AUTHORIZED_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}
ENTRY_ACTIONS = {
    "CREATE_NEW_REPOSITORY",
    "ADOPT_EXISTING_REPOSITORY",
    "MAP_EXISTING_PROJECT",
    "LAB_EVOLUTION",
    "CONTINUE_GOVERNED_WORK",
    "UNKNOWN",
}
CONNECTION_INTENTS = {
    "OBSERVE",
    "CONTEXT_INTAKE",
    "INFORMATION_INTAKE",
    "WORK_REQUEST",
    "CODE_CHANGE",
    "REVIEW",
    "INFRASTRUCTURE",
    "UNKNOWN",
}
FORBIDDEN_KEY_FRAGMENTS = ("token", "secret", "password", "private_key", "cookie", "authorization")
ALLOWED_KEYS = {
    "schema",
    "event",
    "session_id",
    "agent",
    "provider",
    "provider_ref",
    "provider_url",
    "connection_ref",
    "client_instance_id",
    "bridge_registration_ref",
    "observed_head",
    "branch",
    "task_id",
    "pull_request",
    "agent_role",
    "entry_action",
    "connection_intent",
    "capabilities",
    "wake_channels",
    "action_id",
    "action_label",
    "action_phase",
    "tool_name",
    "tool_call_id",
    "outcome",
    "written_head",
    "checkpoint_ref",
    "interruption_code",
    "dispatch_id",
    "command_id",
    "correlation_id",
    "delivery_state",
    "challenge_id",
    "nonce",
    "challenge_status",
}


def read_json(path: Path, default=None):
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def state_paths() -> tuple[Path, Path]:
    if (ROOT / ".template-source").exists():
        base = ROOT / ".governance" / "control-plane-state"
        return base / "gacr-sessions.json", base / "gacr-beacons.json"
    base = ROOT / ".governance"
    return base / "sessions" / "sessions.json", base / "agent-relay" / "beacons.json"


def assert_safe(value: object, path: str = "payload") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in FORBIDDEN_KEY_FRAGMENTS):
                raise ValueError(f"forbidden host-event key: {path}.{key}")
            if lowered in {"message", "messages", "transcript", "conversation_text", "prompt", "response_text"}:
                raise ValueError(f"transcript-like host-event key forbidden: {path}.{key}")
            assert_safe(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_safe(child, f"{path}[{index}]")
    elif isinstance(value, str):
        if len(value) > 2048:
            raise ValueError(f"host-event value too long at {path}")
        if "-----BEGIN PRIVATE KEY-----" in value or value.startswith("ghp_") or value.startswith("github_pat_"):
            raise ValueError(f"secret-like host-event value at {path}")


def parse_issue_comment_event(event: dict, config: dict) -> dict | None:
    bridge = config.get("host_issue_bridge") or {}
    if not bridge.get("enabled", False):
        return None
    if event.get("action") != "created":
        return None

    issue = event.get("issue") or {}
    configured_issue = bridge.get("issue_number")
    if configured_issue not in (None, "", 0):
        if int(issue.get("number") or 0) != int(configured_issue):
            return None
    else:
        expected_title = str(bridge.get("issue_title") or "").strip()
        if not expected_title or str(issue.get("title") or "").strip() != expected_title:
            return None

    comment = event.get("comment") or {}
    body = str(comment.get("body") or "")
    if not body.startswith(PREFIX):
        return None

    association = str(comment.get("author_association") or "").upper()
    allowed = set(bridge.get("allowed_author_associations") or AUTHORIZED_ASSOCIATIONS)
    if association not in allowed:
        raise ValueError(f"unauthorized host-event author association: {association or 'UNKNOWN'}")

    encoded = body[len(PREFIX):].strip()
    if not encoded or len(encoded) > int(bridge.get("max_payload_chars") or 8192):
        raise ValueError("invalid host-event payload size")
    payload = json.loads(encoded)
    if not isinstance(payload, dict):
        raise ValueError("host-event payload must be a JSON object")
    if payload.get("schema") != SCHEMA:
        raise ValueError("unsupported host-event schema")
    unknown = sorted(set(payload) - ALLOWED_KEYS)
    if unknown:
        raise ValueError(f"unsupported host-event fields: {','.join(unknown)}")
    assert_safe(payload)

    kind = str(payload.get("event") or "").lower()
    if kind not in EVENTS:
        raise ValueError("unsupported host-event type")
    if kind == "action" and payload.get("action_phase") not in ACTION_PHASES:
        raise ValueError("host action requires a supported action_phase")
    if kind == "interrupt" and payload.get("interruption_code") not in INTERRUPTION_CODES:
        raise ValueError("host interrupt requires a supported interruption_code")
    entry_action = payload.get("entry_action")
    if entry_action is not None and entry_action not in ENTRY_ACTIONS:
        raise ValueError("unsupported host-event entry_action")
    connection_intent = payload.get("connection_intent")
    if connection_intent is not None and connection_intent not in CONNECTION_INTENTS:
        raise ValueError("unsupported host-event connection_intent")

    if kind == "command_ack":
        for key in ("session_id", "dispatch_id", "command_id", "correlation_id", "delivery_state"):
            if payload.get(key) in (None, ""):
                raise ValueError(f"host command_ack requires {key}")
    if kind == "challenge_response":
        for key in ("session_id", "dispatch_id", "command_id", "correlation_id", "challenge_id", "nonce", "challenge_status"):
            if payload.get(key) in (None, ""):
                raise ValueError(f"host challenge_response requires {key}")
    for list_field in ("capabilities", "wake_channels"):
        if list_field in payload and not isinstance(payload.get(list_field), list):
            raise ValueError(f"{list_field} must be a JSON array")
    if isinstance(payload.get("capabilities"), list) and len(payload["capabilities"]) > 32:
        raise ValueError("too many host-event capabilities")
    if isinstance(payload.get("wake_channels"), list) and len(payload["wake_channels"]) > 8:
        raise ValueError("too many host-event wake channels")

    comment_id = comment.get("id")
    if not comment_id:
        raise ValueError("host-event comment id unavailable")
    payload["_comment_id"] = str(comment_id)
    payload["_evidence_ref"] = f"github-issue-comment:{comment_id}"
    payload["_actor"] = ((comment.get("user") or {}).get("login") or (event.get("sender") or {}).get("login"))
    payload["_observed_at"] = comment.get("created_at")
    return payload


def active_sessions() -> list[dict]:
    sessions_path, _ = state_paths()
    return read_json(sessions_path, {"sessions": []}).get("sessions", [])


def resolve_session(payload: dict, repository: str) -> dict | None:
    session_id = payload.get("session_id")
    matches = []
    for session in active_sessions():
        if session.get("repository") != repository:
            continue
        relay_state = (session.get("relay") or {}).get("state")
        if session.get("status") == "CLOSED" or relay_state in {"CLOSED", "HANDOFF_STALLED"}:
            continue
        if session_id:
            if session.get("session_id") == session_id:
                matches.append(session)
            continue
        matched = False
        provider_ref = payload.get("provider_ref")
        if provider_ref and session.get("provider_conversation_ref") == provider_ref:
            matched = True
        connection_ref = payload.get("connection_ref")
        if connection_ref and session.get("connection_ref") == connection_ref:
            matched = True
        client_instance_id = payload.get("client_instance_id")
        if client_instance_id and session.get("client_instance_id") == client_instance_id:
            matched = True
        if matched:
            matches.append(session)

    unique = {item.get("session_id"): item for item in matches if item.get("session_id")}
    if len(unique) > 1:
        raise ValueError("host-event session resolution is ambiguous")
    return next(iter(unique.values()), None)


def evidence_processed(evidence_ref: str) -> bool:
    _, beacons_path = state_paths()
    store = read_json(beacons_path, {"items": []})
    return any(item.get("evidence_ref") == evidence_ref for item in store.get("items", []))


def now_iso_from_event(payload: dict) -> str:
    value = payload.get("_observed_at")
    if value:
        return str(value)
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def add(args: list[str], flag: str, value) -> None:
    if value in (None, "", []):
        return
    args.extend([flag, str(value)])


def run_script(path: Path, args: list[str]) -> str:
    cp = subprocess.run([sys.executable, str(path), *args], cwd=ROOT, text=True, capture_output=True)
    if cp.stdout:
        print(cp.stdout, end="")
    if cp.stderr:
        print(cp.stderr, file=sys.stderr, end="")
    if cp.returncode != 0:
        raise RuntimeError(f"{path.name} failed with exit {cp.returncode}")
    return cp.stdout


def ensure_session(payload: dict, repository: str) -> dict:
    existing = resolve_session(payload, repository)
    explicit_provider = payload.get("provider")
    if existing:
        existing_provider = existing.get("provider")
        if explicit_provider not in (None, "", "other") and existing_provider in (None, "", "other"):
            args: list[str] = []
            add(args, "--agent", payload.get("agent") or existing.get("agent_identity") or "conversation-agent")
            add(args, "--provider", explicit_provider)
            add(args, "--provider-ref", payload.get("provider_ref"))
            add(args, "--provider-url", payload.get("provider_url"))
            add(args, "--connection-ref", payload.get("connection_ref") or existing.get("connection_ref"))
            add(args, "--client-instance-id", payload.get("client_instance_id") or existing.get("client_instance_id"))
            add(args, "--bridge-registration-ref", payload.get("bridge_registration_ref") or existing.get("bridge_registration_ref"))
            add(args, "--repository", repository)
            add(args, "--observed-head", payload.get("observed_head"))
            add(args, "--branch", payload.get("branch") or (existing.get("relay") or {}).get("branch") or "main")
            add(args, "--task-id", payload.get("task_id"))
            add(args, "--pull-request", payload.get("pull_request"))
            add(args, "--agent-role", payload.get("agent_role"))
            add(args, "--entry-action", payload.get("entry_action"))
            add(args, "--connection-intent", payload.get("connection_intent"))
            add(args, "--source", "EXPLICIT_CLIENT")
            run_script(AUTO_ATTACH, args)
            enriched = resolve_session(payload, repository)
            if not enriched:
                raise RuntimeError("host-event provider enrichment completed but session could not be resolved")
            return enriched
        if explicit_provider not in (None, "", "other", existing_provider) and existing_provider not in (None, "", "other"):
            raise ValueError("provider conflict on host-event session")
        return existing

    if not any(payload.get(key) for key in ("provider_ref", "provider_url", "connection_ref", "client_instance_id")):
        raise ValueError("host-event cannot auto-attach without provider_ref/provider_url/connection_ref/client_instance_id")

    args: list[str] = []
    add(args, "--agent", payload.get("agent") or "conversation-agent")
    add(args, "--provider", payload.get("provider") or "other")
    add(args, "--provider-ref", payload.get("provider_ref"))
    add(args, "--provider-url", payload.get("provider_url"))
    add(args, "--connection-ref", payload.get("connection_ref"))
    add(args, "--client-instance-id", payload.get("client_instance_id"))
    add(args, "--bridge-registration-ref", payload.get("bridge_registration_ref"))
    add(args, "--repository", repository)
    add(args, "--observed-head", payload.get("observed_head"))
    add(args, "--branch", payload.get("branch") or "main")
    add(args, "--task-id", payload.get("task_id"))
    add(args, "--pull-request", payload.get("pull_request"))
    add(args, "--agent-role", payload.get("agent_role"))
    add(args, "--entry-action", payload.get("entry_action"))
    add(args, "--connection-intent", payload.get("connection_intent"))
    add(args, "--source", "EXPLICIT_CLIENT")
    for capability in payload.get("capabilities") or []:
        add(args, "--capability", capability)
    for channel in payload.get("wake_channels") or ["POLL_REPOSITORY"]:
        add(args, "--wake-channel", channel)
    run_script(AUTO_ATTACH, args)

    attached = resolve_session(payload, repository)
    if not attached:
        raise RuntimeError("host-event auto-attach completed but session could not be resolved")
    return attached


def marker_beacon(session_id: str, payload: dict, event_type: str) -> None:
    args = [
        "beacon",
        "--session-id", session_id,
        "--event-type", event_type,
        "--source", "CLIENT_EMITTER",
        "--evidence-ref", payload["_evidence_ref"],
    ]
    add(args, "--action-id", payload.get("action_id"))
    add(args, "--action-label", payload.get("action_label"))
    add(args, "--action-phase", payload.get("action_phase"))
    add(args, "--tool-name", payload.get("tool_name"))
    add(args, "--tool-call-id", payload.get("tool_call_id"))
    add(args, "--outcome", payload.get("outcome"))
    add(args, "--written-head", payload.get("written_head"))
    add(args, "--checkpoint-ref", payload.get("checkpoint_ref"))
    add(args, "--interruption-code", payload.get("interruption_code"))
    run_script(TELEMETRY, args)


def process(payload: dict, repository: str) -> dict:
    evidence_ref = payload["_evidence_ref"]
    if evidence_processed(evidence_ref):
        return {
            "status": "GACR_HOST_EVENT_ALREADY_PROCESSED",
            "evidence_ref": evidence_ref,
            "event": payload.get("event"),
        }

    kind = payload["event"]
    if kind in {"command_ack", "challenge_response"}:
        session = resolve_session(payload, repository)
        if not session:
            raise ValueError("host control response requires an existing canonical session")
        session_id = session["session_id"]
        store = read_control_json(DISPATCHES_PATH, {"schema_version": "1.0.0", "revision": 0, "items": []})
        control_result = apply_host_control_event(
            store,
            payload,
            evidence_ref=evidence_ref,
            observed_at=now_iso_from_event(payload),
        )
        write_control_json(DISPATCHES_PATH, store)
        marker_beacon(session_id, payload, "COMMAND_ACK" if kind == "command_ack" else "CHALLENGE_RESPONSE")
        if kind == "challenge_response" and control_result.get("fresh_liveness") is True:
            hb = [
                "heartbeat",
                "--session-id", session_id,
                "--source", "CLIENT_EMITTER",
                "--action", "HOST_CHALLENGE_RESPONSE",
                "--evidence", evidence_ref,
            ]
            add(hb, "--observed-head", payload.get("observed_head"))
            run_script(CORE, hb)
        run_script(TELEMETRY, ["correlate"])
        run_script(TELEMETRY, ["forensics", "--session-id", session_id])
        return {
            "status": "GACR_HOST_CONTROL_EVENT_PROCESSED",
            "event": kind,
            "session_id": session_id,
            "evidence_ref": evidence_ref,
            "control": control_result,
            "transport": "GITHUB_ISSUE_COMMENT",
            "provenance": "CLIENT_EMITTER",
        }

    session = ensure_session(payload, repository)
    session_id = session["session_id"]

    if kind == "attach":
        marker_beacon(session_id, payload, "HOST_ATTACH_RECEIPT")
    elif kind == "heartbeat":
        args = [
            "heartbeat",
            "--session-id", session_id,
            "--source", "CLIENT_EMITTER",
            "--action", payload.get("action_label") or "HOST_HEARTBEAT",
            "--evidence", evidence_ref,
        ]
        add(args, "--observed-head", payload.get("observed_head"))
        run_script(CORE, args)
        marker_beacon(session_id, payload, "HOST_HEARTBEAT_RECEIPT")
    elif kind == "action":
        hb = [
            "heartbeat",
            "--session-id", session_id,
            "--source", "CLIENT_EMITTER",
            "--action", payload.get("action_label") or "HOST_ACTION",
            "--evidence", evidence_ref,
        ]
        add(hb, "--observed-head", payload.get("observed_head"))
        run_script(CORE, hb)
        marker_beacon(session_id, payload, "ACTION_TRACE")
    elif kind == "interrupt":
        marker_beacon(session_id, payload, "INTERRUPTION_SIGNAL")

    run_script(TELEMETRY, ["correlate"])
    run_script(TELEMETRY, ["forensics", "--session-id", session_id])
    return {
        "status": "GACR_HOST_EVENT_PROCESSED",
        "event": kind,
        "session_id": session_id,
        "evidence_ref": evidence_ref,
        "transport": "GITHUB_ISSUE_COMMENT",
        "provenance": "CLIENT_EMITTER",
    }


def main() -> None:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise SystemExit("GACR_HOST_ISSUE_INGRESS_FAILED: GITHUB_EVENT_PATH unavailable")
    event = read_json(Path(event_path))
    config = read_json(CONFIG_PATH)
    try:
        payload = parse_issue_comment_event(event, config)
        if payload is None:
            print(json.dumps({"status": "GACR_HOST_EVENT_IGNORED"}, indent=2))
            return
        repository = str(os.environ.get("GITHUB_REPOSITORY") or ((event.get("repository") or {}).get("full_name") or ""))
        if repository.count("/") != 1:
            raise ValueError("repository identity unavailable")
        result = process(payload, repository)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as exc:
        raise SystemExit(f"GACR_HOST_ISSUE_INGRESS_FAILED: {exc}") from exc


if __name__ == "__main__":
    main()
