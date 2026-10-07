#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import signal
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable

DEFAULT_API_BASE = "https://api.github.com"
DEFAULT_HEARTBEAT_SECONDS = 300
EVENTS = {"gacr_auto-attach", "gacr_heartbeat", "gacr_beacon"}
ACTION_PHASES = {"STARTED", "COMPLETED", "FAILED", "CANCELLED"}
INTERRUPTION_CODES = {
    "CLIENT_DISCONNECTED",
    "PROVIDER_TIMEOUT",
    "TOOL_FAILURE",
    "AGENT_ERROR",
    "USER_CANCELLED",
    "NETWORK_LOSS",
    "PROCESS_EXITED",
    "PROVIDER_RATE_LIMIT",
    "TOOL_RATE_LIMIT",
    "USAGE_LIMIT",
    "QUOTA_LIMIT",
    "CONTEXT_LIMIT",
    "WAITING_FOR_AUTHORITY",
    "WAITING_FOR_INPUT",
    "WAITING_FOR_REVIEW",
    "EXTERNAL_DEPENDENCY",
    "UNKNOWN",
}
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
FORBIDDEN_KEY_FRAGMENTS = ("token", "secret", "password", "private_key", "cookie", "authorization")


def compact(value: dict) -> bytes:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def assert_safe_payload(value: object, path: str = "payload") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in FORBIDDEN_KEY_FRAGMENTS):
                raise ValueError(f"forbidden client payload key: {path}.{key}")
            assert_safe_payload(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_safe_payload(child, f"{path}[{index}]")


def repository_name(value: str | None = None) -> str:
    repository = (value or os.environ.get("GITHUB_REPOSITORY") or "").strip()
    parts = repository.split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError("repository must use owner/name")
    return repository


def runtime_token() -> str:
    for name in ("GACR_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        value = (os.environ.get(name) or "").strip()
        if value:
            return value
    raise RuntimeError("GACR client transport credential is unavailable")


def github_request(
    method: str,
    url: str,
    token: str,
    *,
    body: dict | None = None,
    timeout: int = 15,
) -> tuple[int, bytes]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "gacr-client-emitter/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        url,
        method=method,
        data=compact(body) if body is not None else None,
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status), response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"GACR GitHub transport HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("GACR GitHub transport unavailable") from exc


def send_repository_dispatch(
    repository: str,
    event_type: str,
    client_payload: dict,
    *,
    token: str | None = None,
    api_base: str = DEFAULT_API_BASE,
    request_fn: Callable[..., tuple[int, bytes]] = github_request,
) -> int:
    repository = repository_name(repository)
    if event_type not in EVENTS:
        raise ValueError("unsupported GACR client event")
    assert_safe_payload(client_payload)
    body = {"event_type": event_type, "client_payload": client_payload}
    owner, name = repository.split("/", 1)
    url = f"{api_base.rstrip('/')}/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(name)}/dispatches"
    status, _ = request_fn("POST", url, token or runtime_token(), body=body)
    if status < 200 or status >= 300:
        raise RuntimeError(f"GACR repository dispatch returned HTTP {status}")
    return status


def fetch_json_file(
    repository: str,
    path: str,
    *,
    ref: str = "main",
    token: str | None = None,
    api_base: str = DEFAULT_API_BASE,
    request_fn: Callable[..., tuple[int, bytes]] = github_request,
) -> dict:
    repository = repository_name(repository)
    owner, name = repository.split("/", 1)
    encoded_path = "/".join(urllib.parse.quote(part) for part in path.split("/"))
    url = f"{api_base.rstrip('/')}/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(name)}/contents/{encoded_path}?ref={urllib.parse.quote(ref)}"
    status, raw = request_fn("GET", url, token or runtime_token())
    if status < 200 or status >= 300:
        raise RuntimeError(f"GACR content fetch returned HTTP {status}")
    envelope = json.loads(raw.decode("utf-8"))
    if envelope.get("encoding") != "base64":
        raise RuntimeError("GACR content response is not base64")
    payload = base64.b64decode((envelope.get("content") or "").replace("\n", ""))
    return json.loads(payload.decode("utf-8"))


def select_session(
    sessions_doc: dict,
    *,
    repository: str,
    connection_ref: str | None,
    provider: str | None = None,
    provider_ref: str | None = None,
) -> dict | None:
    matches = []
    for session in sessions_doc.get("sessions", []):
        if session.get("repository") != repository:
            continue
        if (session.get("relay") or {}).get("state") in {"HANDOFF_STALLED", "CLOSED"}:
            continue
        if provider_ref and session.get("provider_conversation_ref") == provider_ref:
            matches.append(session)
            continue
        if connection_ref and session.get("connection_ref") == connection_ref:
            if provider and session.get("provider") not in {None, "", "other", provider}:
                continue
            matches.append(session)
    unique = {item.get("session_id"): item for item in matches if item.get("session_id")}
    if len(unique) > 1:
        raise RuntimeError("GACR client session resolution is ambiguous")
    return next(iter(unique.values()), None)


def select_wake_events(
    dispatches_doc: dict,
    *,
    session_id: str | None,
    client_instance_id: str | None,
) -> list[dict]:
    values = []
    for item in dispatches_doc.get("items", []):
        if item.get("status") not in {"READY", "ACTIVATED"}:
            continue
        if session_id and item.get("target_session_id") == session_id:
            values.append(item)
            continue
        if client_instance_id and item.get("target_client_instance_id") == client_instance_id:
            values.append(item)
    values.sort(key=lambda item: (item.get("created_at") or "", item.get("dispatch_id") or ""))
    return values


@dataclass
class ClientEmitter:
    repository: str
    token: str | None = None
    api_base: str = DEFAULT_API_BASE
    dry_run: bool = False
    request_fn: Callable[..., tuple[int, bytes]] = github_request

    def emit(self, event_type: str, payload: dict) -> dict:
        payload = {key: value for key, value in payload.items() if value not in (None, "", [])}
        payload["source"] = "CLIENT_EMITTER"
        assert_safe_payload(payload)
        envelope = {"event_type": event_type, "client_payload": payload}
        if self.dry_run:
            return {"status": "DRY_RUN", **envelope}
        status = send_repository_dispatch(
            self.repository,
            event_type,
            payload,
            token=self.token,
            api_base=self.api_base,
            request_fn=self.request_fn,
        )
        return {"status": "SENT", "http_status": status, **envelope}

    def attach(self, **payload) -> dict:
        return self.emit("gacr_auto-attach", payload)

    def heartbeat(self, session_id: str, **payload) -> dict:
        return self.emit("gacr_heartbeat", {"session_id": session_id, **payload})

    def trace(self, session_id: str, *, action_phase: str, **payload) -> dict:
        if action_phase not in ACTION_PHASES:
            raise ValueError("unsupported action phase")
        return self.emit(
            "gacr_beacon",
            {
                "session_id": session_id,
                "event_type": "ACTION_TRACE",
                "action_phase": action_phase,
                **payload,
            },
        )

    def interrupt(self, session_id: str, *, interruption_code: str, **payload) -> dict:
        if interruption_code not in INTERRUPTION_CODES:
            raise ValueError("unsupported interruption code")
        return self.emit(
            "gacr_beacon",
            {
                "session_id": session_id,
                "event_type": "INTERRUPTION_SIGNAL",
                "interruption_code": interruption_code,
                **payload,
            },
        )

    def fetch(self, path: str, *, ref: str = "main") -> dict:
        return fetch_json_file(
            self.repository,
            path,
            ref=ref,
            token=self.token,
            api_base=self.api_base,
            request_fn=self.request_fn,
        )


def daemon_loop(
    emitter: ClientEmitter,
    *,
    session_id: str,
    observed_head: str | None,
    interval_seconds: float,
    cycles: int,
    action_label: str | None,
    evidence: str | None,
    poll_wake: bool,
    dispatches_path: str,
    ref: str,
    client_instance_id: str | None,
    sleep_fn: Callable[[float], None] = time.sleep,
    output_fn: Callable[[dict], None] | None = None,
) -> None:
    stop = {"value": False, "code": None}

    def on_signal(signum, _frame):
        stop["value"] = True
        stop["code"] = "USER_CANCELLED" if signum == signal.SIGINT else "PROCESS_EXITED"

    previous_int = signal.signal(signal.SIGINT, on_signal)
    previous_term = signal.signal(signal.SIGTERM, on_signal)
    emitted = 0
    try:
        while not stop["value"] and (cycles <= 0 or emitted < cycles):
            result = emitter.heartbeat(
                session_id,
                observed_head=observed_head,
                action_label=action_label or "CLIENT_HEARTBEAT",
                evidence=evidence,
            )
            emitted += 1
            if output_fn:
                output_fn(result)
            if poll_wake and not emitter.dry_run:
                store = emitter.fetch(dispatches_path, ref=ref)
                wakes = select_wake_events(
                    store,
                    session_id=session_id,
                    client_instance_id=client_instance_id,
                )
                if wakes and output_fn:
                    output_fn({"status": "WAKE_AVAILABLE", "items": wakes})
            if not stop["value"] and (cycles <= 0 or emitted < cycles):
                sleep_fn(interval_seconds)
    finally:
        signal.signal(signal.SIGINT, previous_int)
        signal.signal(signal.SIGTERM, previous_term)
        if stop["code"]:
            try:
                result = emitter.interrupt(
                    session_id,
                    interruption_code=stop["code"],
                    action_label="CLIENT_EMITTER_SIGNAL",
                )
                if output_fn:
                    output_fn(result)
            except Exception as exc:
                if output_fn:
                    output_fn({"status": "INTERRUPTION_SIGNAL_FAILED", "error": str(exc)})


def add_transport_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repository")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--dry-run", action="store_true")


def emitter_from_args(args: argparse.Namespace) -> ClientEmitter:
    return ClientEmitter(
        repository=repository_name(args.repository),
        token=None if args.dry_run else runtime_token(),
        api_base=args.api_base,
        dry_run=args.dry_run,
    )


def output(value: dict) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False), flush=True)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="GACR R5 client liveness and trace emitter")
    sub = p.add_subparsers(dest="command", required=True)

    attach = sub.add_parser("attach")
    add_transport_args(attach)
    attach.add_argument("--agent")
    attach.add_argument("--provider", choices=["chatgpt","claude","codex","github-actions","human","other"])
    attach.add_argument("--provider-ref")
    attach.add_argument("--provider-url")
    attach.add_argument("--connection-ref")
    attach.add_argument("--client-instance-id")
    attach.add_argument("--bridge-registration-ref")
    attach.add_argument("--observed-head")
    attach.add_argument("--branch")
    attach.add_argument("--task-id")
    attach.add_argument("--pull-request", type=int)
    attach.add_argument("--agent-role")
    attach.add_argument("--capabilities")
    attach.add_argument("--wake-channels")

    heartbeat = sub.add_parser("heartbeat")
    add_transport_args(heartbeat)
    heartbeat.add_argument("--session-id", required=True)
    heartbeat.add_argument("--observed-head")
    heartbeat.add_argument("--action-label")
    heartbeat.add_argument("--evidence")
    heartbeat.add_argument("--workload-state", choices=sorted(WORKLOAD_STATES))
    heartbeat.add_argument("--blocker-code", choices=sorted(BLOCKER_CODES))
    heartbeat.add_argument("--capacity-slots", type=int)
    heartbeat.add_argument("--max-parallel-tasks", type=int)
    heartbeat.add_argument("--retry-after-at")

    trace = sub.add_parser("trace")
    add_transport_args(trace)
    trace.add_argument("--session-id", required=True)
    trace.add_argument("--action-id")
    trace.add_argument("--action-label")
    trace.add_argument("--action-phase", choices=sorted(ACTION_PHASES), required=True)
    trace.add_argument("--tool-name")
    trace.add_argument("--tool-call-id")
    trace.add_argument("--outcome")
    trace.add_argument("--written-head")
    trace.add_argument("--checkpoint-ref")
    trace.add_argument("--evidence-ref")
    trace.add_argument("--observed-head")

    interrupt = sub.add_parser("interrupt")
    add_transport_args(interrupt)
    interrupt.add_argument("--session-id", required=True)
    interrupt.add_argument("--interruption-code", choices=sorted(INTERRUPTION_CODES), required=True)
    interrupt.add_argument("--action-label")
    interrupt.add_argument("--evidence-ref")

    daemon = sub.add_parser("daemon")
    add_transport_args(daemon)
    daemon.add_argument("--session-id", required=True)
    daemon.add_argument("--observed-head")
    daemon.add_argument("--interval-seconds", type=float, default=DEFAULT_HEARTBEAT_SECONDS)
    daemon.add_argument("--cycles", type=int, default=0)
    daemon.add_argument("--action-label")
    daemon.add_argument("--evidence")
    daemon.add_argument("--poll-wake", action="store_true")
    daemon.add_argument("--dispatches-path", default=".governance/agent-relay/dispatches.json")
    daemon.add_argument("--ref", default="main")
    daemon.add_argument("--client-instance-id")

    resolve = sub.add_parser("resolve-session")
    add_transport_args(resolve)
    resolve.add_argument("--connection-ref")
    resolve.add_argument("--provider")
    resolve.add_argument("--provider-ref")
    resolve.add_argument("--sessions-path", default=".governance/sessions/sessions.json")
    resolve.add_argument("--ref", default="main")

    wake = sub.add_parser("poll-wake")
    add_transport_args(wake)
    wake.add_argument("--session-id")
    wake.add_argument("--client-instance-id")
    wake.add_argument("--dispatches-path", default=".governance/agent-relay/dispatches.json")
    wake.add_argument("--ref", default="main")

    return p


def main() -> None:
    args = parser().parse_args()
    emitter = emitter_from_args(args)

    if args.command == "attach":
        output(emitter.attach(
            agent=args.agent,
            provider=args.provider,
            provider_ref=args.provider_ref,
            provider_url=args.provider_url,
            connection_ref=args.connection_ref,
            client_instance_id=args.client_instance_id,
            bridge_registration_ref=args.bridge_registration_ref,
            observed_head=args.observed_head,
            branch=args.branch,
            task_id=args.task_id,
            pull_request=args.pull_request,
            agent_role=args.agent_role,
            capabilities=args.capabilities,
            wake_channels=args.wake_channels,
        ))
    elif args.command == "heartbeat":
        output(emitter.heartbeat(
            args.session_id,
            observed_head=args.observed_head,
            action_label=args.action_label or "CLIENT_HEARTBEAT",
            evidence=args.evidence,
            workload_state=args.workload_state,
            blocker_code=args.blocker_code,
            capacity_slots=args.capacity_slots,
            max_parallel_tasks=args.max_parallel_tasks,
            retry_after_at=args.retry_after_at,
        ))
    elif args.command == "trace":
        output(emitter.trace(
            args.session_id,
            action_phase=args.action_phase,
            action_id=args.action_id,
            action_label=args.action_label,
            tool_name=args.tool_name,
            tool_call_id=args.tool_call_id,
            outcome=args.outcome,
            written_head=args.written_head,
            checkpoint_ref=args.checkpoint_ref,
            evidence_ref=args.evidence_ref,
            observed_head=args.observed_head,
        ))
    elif args.command == "interrupt":
        output(emitter.interrupt(
            args.session_id,
            interruption_code=args.interruption_code,
            action_label=args.action_label or "CLIENT_INTERRUPTION",
            evidence_ref=args.evidence_ref,
        ))
    elif args.command == "daemon":
        daemon_loop(
            emitter,
            session_id=args.session_id,
            observed_head=args.observed_head,
            interval_seconds=args.interval_seconds,
            cycles=args.cycles,
            action_label=args.action_label,
            evidence=args.evidence,
            poll_wake=args.poll_wake,
            dispatches_path=args.dispatches_path,
            ref=args.ref,
            client_instance_id=args.client_instance_id,
            output_fn=output,
        )
    elif args.command == "resolve-session":
        if emitter.dry_run:
            raise SystemExit("resolve-session requires GitHub read transport")
        store = emitter.fetch(args.sessions_path, ref=args.ref)
        session = select_session(
            store,
            repository=emitter.repository,
            connection_ref=args.connection_ref,
            provider=args.provider,
            provider_ref=args.provider_ref,
        )
        output({"status": "SESSION_RESOLVED" if session else "SESSION_NOT_FOUND", "session": session})
    elif args.command == "poll-wake":
        if emitter.dry_run:
            raise SystemExit("poll-wake requires GitHub read transport")
        store = emitter.fetch(args.dispatches_path, ref=args.ref)
        output({
            "status": "WAKE_POLL_COMPLETE",
            "items": select_wake_events(
                store,
                session_id=args.session_id,
                client_instance_id=args.client_instance_id,
            ),
        })


if __name__ == "__main__":
    main()
