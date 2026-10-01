#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from governed_agent_continuity_relay import (
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
CHRONICLE_CURRENT = ROOT / ".governance" / "control-plane-state" / "conversation-chronicles" / "current.json"
INTERNAL_GACR_WORKFLOWS = {"Governed Agent Continuity Relay"}


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
    p = argparse.ArgumentParser(description="GACR R4 automatic continuity attachment")
    p.add_argument("--agent")
    p.add_argument("--provider", choices=["chatgpt","claude","codex","github-actions","human","other"])
    p.add_argument("--provider-ref")
    p.add_argument("--provider-url")
    p.add_argument("--connection-ref")
    p.add_argument("--client-instance-id")
    p.add_argument("--bridge-registration-ref")
    p.add_argument("--repository")
    p.add_argument("--observed-head")
    p.add_argument("--branch")
    p.add_argument("--task-id")
    p.add_argument("--pull-request", type=int)
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

    provider = a.provider or anchor.get("provider") or os.environ.get("GACR_PROVIDER") or "other"
    connection_ref = a.connection_ref or anchor.get("connection_ref")
    client_instance_id = a.client_instance_id or anchor.get("client_instance_id")
    bridge_registration_ref = a.bridge_registration_ref or anchor.get("bridge_registration_ref")
    agent = a.agent or anchor.get("agent") or os.environ.get("GACR_AGENT_IDENTITY") or os.environ.get("GITHUB_ACTOR") or "gacr-auto-attach"

    timestamp = now_utc()
    session, resolution = register_docs(
        config,
        sessions,
        repository=a.repository or repository_name(),
        agent=agent,
        provider=provider,
        provider_ref=a.provider_ref,
        provider_url=a.provider_url,
        connection_ref=connection_ref,
        observed_head=a.observed_head or git_head(),
        branch=a.branch or git_branch(),
        task_id=a.task_id,
        pull_request=a.pull_request,
        standby=a.standby,
        client_instance_id=client_instance_id,
        agent_role=a.agent_role,
        capabilities=sorted(set((a.capability or []) + ["GACR_AUTO_ATTACH"])),
        wake_channels=a.wake_channel or ["POLL_REPOSITORY"],
        bridge_registration_ref=bridge_registration_ref,
        timestamp=timestamp,
    )
    save(sessions, claims, takeovers)
    beacon = record_beacon(
        session=session,
        event_type="AUTO_ATTACH",
        source=anchor.get("source"),
        provider=provider,
        provider_ref=a.provider_ref,
        provider_url=a.provider_url,
        client_instance_id=client_instance_id,
        connection_ref=connection_ref,
        task_id=a.task_id,
        branch=a.branch or git_branch(),
        pull_request=a.pull_request,
        agent_role=a.agent_role,
        capabilities=sorted(set((a.capability or []) + ["GACR_AUTO_ATTACH"])),
    )
    correlation = correlate_all()
    print(json.dumps({
        "status": resolution,
        "process": "GACR",
        "authority": "CP-AGENT-RELAY-001-R5",
        "attachment_source": anchor.get("source"),
        "session": session,
        "beacon_id": beacon.get("beacon_id"),
        "correlation": correlation,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
