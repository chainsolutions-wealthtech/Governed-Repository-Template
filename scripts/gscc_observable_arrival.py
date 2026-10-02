#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Callable

from gacr_client_emitter import ClientEmitter
from gscc import GACRClientEmitterAdapter, SessionEndpoint

SUPPORTED_GITHUB_EVENTS = frozenset({
    "push",
    "create",
    "pull_request",
    "issues",
    "issue_comment",
    "pull_request_review",
    "pull_request_review_comment",
    "workflow_dispatch",
})

INTERNAL_DISPATCH_PREFIXES = ("gacr_", "gscc_")
HOST_INGRESS_PREFIX = "/gacr-host "


def _nonempty(value: Any) -> Any:
    return value if value not in (None, "", [], {}) else None


def _branch_from_ref(value: str | None) -> str | None:
    if not value:
        return None
    for prefix in ("refs/heads/", "refs/tags/"):
        if value.startswith(prefix):
            return value[len(prefix):]
    return value


def _repository(event: dict[str, Any], env: dict[str, str]) -> tuple[str, str | None, str | None]:
    repository = event.get("repository") or {}
    full_name = _nonempty(repository.get("full_name")) or _nonempty(env.get("GITHUB_REPOSITORY"))
    if not full_name or str(full_name).count("/") != 1:
        raise ValueError("observable arrival repository identity unavailable")
    owner = repository.get("owner") or {}
    organization = _nonempty(owner.get("login")) or str(full_name).split("/", 1)[0]
    repository_id = _nonempty(repository.get("id")) or _nonempty(env.get("GITHUB_REPOSITORY_ID"))
    return str(full_name), str(repository_id) if repository_id is not None else None, str(organization)


def _actor(event: dict[str, Any], env: dict[str, str]) -> str:
    sender = event.get("sender") or {}
    actor = _nonempty(sender.get("login")) or _nonempty(env.get("GITHUB_ACTOR"))
    if not actor:
        raise ValueError("observable arrival GitHub actor unavailable")
    return str(actor)


def _pull_request(event: dict[str, Any]) -> tuple[int | None, str | None, str | None, str | None]:
    pr = event.get("pull_request") or {}
    if not pr:
        return None, None, None, None
    head = pr.get("head") or {}
    base = pr.get("base") or {}
    number = _nonempty(pr.get("number")) or _nonempty(event.get("number"))
    return (
        int(number) if number is not None else None,
        _nonempty(head.get("ref")),
        _nonempty(base.get("ref")),
        _nonempty(head.get("sha")),
    )


def _issue_number(event: dict[str, Any]) -> int | None:
    issue = event.get("issue") or {}
    number = _nonempty(issue.get("number")) or _nonempty(event.get("number"))
    return int(number) if number is not None else None


def _subject(
    event_name: str,
    *,
    pull_request: int | None,
    issue_number: int | None,
    branch: str | None,
    event: dict[str, Any],
) -> str:
    if branch:
        return f"ref:{branch}"
    if pull_request is not None:
        return f"pr:{pull_request}"
    if issue_number is not None:
        return f"issue:{issue_number}"
    if event_name == "create":
        return f"{event.get('ref_type') or 'ref'}:{event.get('ref') or 'unknown'}"
    return event_name


def should_skip_github_arrival(event: dict[str, Any], env: dict[str, str]) -> str | None:
    event_name = str(env.get("GITHUB_EVENT_NAME") or "")
    actor = str(((event.get("sender") or {}).get("login") or env.get("GITHUB_ACTOR") or ""))

    if event_name == "push" and actor == "github-actions[bot]":
        return "INTERNAL_GITHUB_ACTIONS_STATE_PUSH"

    if event_name == "repository_dispatch":
        action = str(event.get("action") or "")
        if action.startswith(INTERNAL_DISPATCH_PREFIXES):
            return "INTERNAL_GACR_OR_GSCC_DISPATCH"

    if event_name == "issue_comment":
        comment = event.get("comment") or {}
        body = str(comment.get("body") or "")
        if body.startswith(HOST_INGRESS_PREFIX):
            return "INTERNAL_GACR_HOST_INGRESS"

    return None


def build_github_arrival_facts(event: dict[str, Any], env: dict[str, str]) -> dict[str, Any]:
    event_name = str(env.get("GITHUB_EVENT_NAME") or "")
    if event_name not in SUPPORTED_GITHUB_EVENTS:
        raise ValueError(f"unsupported observable GitHub arrival event: {event_name or 'UNAVAILABLE'}")

    repository, repository_id, organization = _repository(event, env)
    actor = _actor(event, env)
    pr_number, pr_branch, base_branch, pr_head = _pull_request(event)
    issue_number = _issue_number(event)

    event_ref = _branch_from_ref(_nonempty(event.get("ref")))
    branch = (
        pr_branch
        or event_ref
        or _nonempty(env.get("GITHUB_HEAD_REF"))
        or _nonempty(env.get("GITHUB_REF_NAME"))
    )
    base_branch = base_branch or _nonempty(env.get("GITHUB_BASE_REF"))
    observed_head = (
        pr_head
        or _nonempty(event.get("after"))
        or _nonempty(env.get("GITHUB_SHA"))
    )

    subject = _subject(
        event_name,
        pull_request=pr_number,
        issue_number=issue_number,
        branch=str(branch) if branch else None,
        event=event,
    )
    run_id = _nonempty(env.get("GITHUB_RUN_ID"))
    run_attempt = _nonempty(env.get("GITHUB_RUN_ATTEMPT"))
    correlation = ":".join(str(x) for x in (run_id, run_attempt) if x is not None) or None
    installation = event.get("installation") or {}

    return {
        "repository": repository,
        "repository_id": repository_id,
        "organization": organization,
        "git_provider": "github",
        "github_actor": actor,
        "github_app_installation": _nonempty(installation.get("id")),
        "agent": actor,
        "provider": None,
        "connection_ref": f"gscc-observable:{repository}:{actor}:{subject}",
        "client_instance_id": f"github-observable:{repository}:{actor}",
        "connection_method": "gscc-github-event-gateway",
        "surface_class": "GITHUB_EVENT_VISIBLE",
        "branch": str(branch) if branch else None,
        "base_branch": str(base_branch) if base_branch else None,
        "observed_head": str(observed_head) if observed_head else None,
        "pull_request": pr_number,
        "workflow_run_id": str(run_id) if run_id is not None else None,
        "run_attempt": str(run_attempt) if run_attempt is not None else None,
        "event_type": f"GSCC_OBSERVABLE_{event_name.upper()}",
        "delivery_correlation_id": correlation,
        "last_action": "GSCC_OBSERVABLE_ARRIVAL",
        "last_evidence": f"github-event:{event_name}:{correlation or subject}",
    }


def _emitter(
    repository: str,
    *,
    token: str | None,
    request_fn: Callable[..., tuple[int, bytes]] | None,
) -> ClientEmitter:
    if request_fn is None:
        return ClientEmitter(repository=repository, token=token)
    return ClientEmitter(repository=repository, token=token, request_fn=request_fn)


def _emit_arrival(
    facts: dict[str, Any],
    *,
    token: str | None = None,
    request_fn: Callable[..., tuple[int, bytes]] | None = None,
) -> dict[str, Any]:
    repository = str(facts["repository"])
    source: dict[str, Any] = {"client_instance_id": facts["client_instance_id"]}
    if facts.get("provider"):
        source["provider"] = facts["provider"]

    # Keep extended repository facts in GSCC, but do not explode the GitHub
    # repository_dispatch top-level payload. GitHub accepts at most 10 client
    # payload properties. The GACR bridge expands only an allowlisted nested
    # arrival_context after transport.
    scope = {"repository": repository}

    adapter = GACRClientEmitterAdapter(
        _emitter(repository, token=token, request_fn=request_fn)
    )
    endpoint = SessionEndpoint(
        adapter,
        source=source,
        target={"system": "gacr"},
        scope=scope,
    )

    arrival_context_keys = {
        "repository",
        "repository_id",
        "organization",
        "git_provider",
        "github_actor",
        "github_app_installation",
        "branch",
        "base_branch",
        "observed_head",
        "pull_request",
        "workflow_run_id",
        "run_attempt",
        "delivery_correlation_id",
        "last_action",
        "last_evidence",
    }
    arrival_context = {
        key: value
        for key, value in facts.items()
        if key in arrival_context_keys and value not in (None, "", [], {})
    }
    payload = {
        key: value
        for key, value in {
            "connection_ref": facts.get("connection_ref"),
            "client_instance_id": facts.get("client_instance_id"),
            "provider": facts.get("provider"),
            "provider_ref": facts.get("provider_ref"),
            "agent": facts.get("agent"),
            "surface_class": facts.get("surface_class"),
            "connection_method": facts.get("connection_method"),
            "event_type": facts.get("event_type"),
            "arrival_context": arrival_context,
        }.items()
        if value not in (None, "", [], {})
    }

    # ClientEmitter adds source=CLIENT_EMITTER. Keep one slot reserved for it.
    if len(payload) > 9:
        raise ValueError("GSCC observable arrival exceeds GitHub dispatch property budget")

    emitted = endpoint.attach(**payload)
    message = emitted["message"]
    return {
        "status": "GSCC_ARRIVAL_DISPATCHED",
        "message": message.to_dict(),
        "delivery": emitted["delivery"],
        "surface_class": facts["surface_class"],
        "connection_ref": facts["connection_ref"],
    }


def emit_github_arrival(
    event: dict[str, Any],
    env: dict[str, str],
    *,
    token: str | None = None,
    request_fn: Callable[..., tuple[int, bytes]] | None = None,
) -> dict[str, Any]:
    reason = should_skip_github_arrival(event, env)
    if reason:
        return {
            "status": "GSCC_ARRIVAL_SKIPPED",
            "reason": reason,
            "mutation_authority_granted": False,
        }
    facts = build_github_arrival_facts(event, env)
    return _emit_arrival(facts, token=token, request_fn=request_fn)


def emit_controlled_arrival(
    *,
    repository: str,
    connection_ref: str,
    client_instance_id: str,
    provider: str | None = None,
    provider_ref: str | None = None,
    agent: str | None = None,
    branch: str | None = None,
    observed_head: str | None = None,
    token: str | None = None,
    request_fn: Callable[..., tuple[int, bytes]] | None = None,
) -> dict[str, Any]:
    if not connection_ref or not client_instance_id:
        raise ValueError("controlled GSCC arrival requires stable connection_ref and client_instance_id")
    if repository.count("/") != 1:
        raise ValueError("repository must use owner/name")

    facts = {
        "repository": repository,
        "organization": repository.split("/", 1)[0],
        "git_provider": "github",
        "agent": agent,
        "provider": provider,
        "provider_ref": provider_ref,
        "connection_ref": connection_ref,
        "client_instance_id": client_instance_id,
        "connection_method": "gscc-controlled-host-gateway",
        "surface_class": "CONTROLLED_INSTRUMENTABLE",
        "branch": branch,
        "observed_head": observed_head,
        "event_type": "GSCC_CONTROLLED_FIRST_TOUCH",
        "last_action": "GSCC_CONTROLLED_ARRIVAL",
        "last_evidence": "gscc-controlled-host:first-touch",
    }
    return _emit_arrival(facts, token=token, request_fn=request_fn)


def _read_event(path: str | None) -> dict[str, Any]:
    if not path:
        raise ValueError("GITHUB_EVENT_PATH unavailable")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("GitHub event payload must be an object")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="GSCC observable repository-arrival gateway")
    sub = parser.add_subparsers(dest="mode", required=True)

    sub.add_parser("github-event")

    controlled = sub.add_parser("controlled")
    controlled.add_argument("--repository", required=True)
    controlled.add_argument("--connection-ref", required=True)
    controlled.add_argument("--client-instance-id", required=True)
    controlled.add_argument("--provider")
    controlled.add_argument("--provider-ref")
    controlled.add_argument("--agent")
    controlled.add_argument("--branch")
    controlled.add_argument("--observed-head")

    args = parser.parse_args()

    if args.mode == "github-event":
        event = _read_event(os.environ.get("GITHUB_EVENT_PATH"))
        result = emit_github_arrival(
            event,
            dict(os.environ),
            token=os.environ.get("GITHUB_TOKEN"),
        )
    else:
        result = emit_controlled_arrival(
            repository=args.repository,
            connection_ref=args.connection_ref,
            client_instance_id=args.client_instance_id,
            provider=args.provider,
            provider_ref=args.provider_ref,
            agent=args.agent,
            branch=args.branch,
            observed_head=args.observed_head,
            token=os.environ.get("GITHUB_TOKEN"),
        )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()