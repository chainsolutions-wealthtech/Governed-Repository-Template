#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from gscc_observable_arrival import (
    build_github_arrival_facts,
    emit_controlled_arrival,
    emit_github_arrival,
    should_skip_github_arrival,
)

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "gscc-observable-arrival.yml"


def assert_true(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def fake_request(calls: list[dict]):
    def request(method: str, url: str, token: str, *, body=None, timeout: int = 15):
        calls.append({
            "method": method,
            "url": url,
            "token_present": bool(token),
            "body": body,
            "timeout": timeout,
        })
        return 204, b""
    return request


def main() -> None:
    event = {
        "repository": {
            "id": 1386478935,
            "full_name": "chainsolutions-wealthtech/Governed-Repository-Template",
            "owner": {"login": "chainsolutions-wealthtech"},
        },
        "sender": {"login": "fresh-provider-actor"},
        "pull_request": {
            "number": 777,
            "head": {"ref": "work/fresh-agent", "sha": "a" * 40},
            "base": {"ref": "main"},
        },
        "number": 777,
        # Deliberate unsafe/unneeded fields: the gateway must never persist or
        # forward these because it reads only an allowlisted event projection.
        "raw_prompt": "must-not-leave-event-file",
        "authorization": "Bearer must-not-leave-event-file",
    }
    env = {
        "GITHUB_EVENT_NAME": "pull_request",
        "GITHUB_RUN_ID": "40000000001",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_SHA": "b" * 40,
    }

    facts = build_github_arrival_facts(event, env)
    assert_true(facts["surface_class"] == "GITHUB_EVENT_VISIBLE", "GitHub arrival surface must be event-visible")
    assert_true(facts["repository"] == "chainsolutions-wealthtech/Governed-Repository-Template", "repository identity")
    assert_true(facts["github_actor"] == "fresh-provider-actor", "platform actor must be observed")
    assert_true(facts["branch"] == "work/fresh-agent", "PR head branch must be observed")
    assert_true(facts["base_branch"] == "main", "PR base branch must be observed")
    assert_true(facts["observed_head"] == "a" * 40, "PR head SHA must be observed")
    assert_true(facts["pull_request"] == 777, "PR number must be observed")
    assert_true(facts["connection_method"] == "gscc-github-event-gateway", "GSCC gateway must be explicit")
    assert_true(facts["connection_ref"].startswith("gscc-observable:"), "stable safe observable anchor")
    assert_true("raw_prompt" not in json.dumps(facts), "raw prompt must not enter safe projection")
    assert_true("Bearer" not in json.dumps(facts), "authorization data must not enter safe projection")

    calls: list[dict] = []
    result = emit_github_arrival(
        event,
        env,
        token="runtime-only-token",
        request_fn=fake_request(calls),
    )
    assert_true(result["status"] == "GSCC_ARRIVAL_DISPATCHED", "arrival must dispatch through GSCC")
    assert_true(result["message"]["kind"] == "EVENT", "GSCC kind")
    assert_true(result["message"]["type"] == "SESSION_ATTACH", "first observable arrival must be a GSCC attach event")
    assert_true(result["message"]["target"]["system"] == "gacr", "GSCC target must be GACR")
    assert_true(len(calls) == 1, "one observable arrival must create one downstream dispatch")
    call = calls[0]
    assert_true(call["method"] == "POST", "repository dispatch method")
    assert_true(call["token_present"], "runtime transport credential is required but never persisted")
    assert_true(call["body"]["event_type"] == "gacr_auto-attach", "GSCC compatibility path must reuse canonical GACR auto-attach")
    payload = call["body"]["client_payload"]
    assert_true(payload["source"] == "CLIENT_EMITTER", "GACR compatibility provenance")
    assert_true(payload["surface_class"] == "GITHUB_EVENT_VISIBLE", "surface class forwarded")
    assert_true(payload["connection_method"] == "gscc-github-event-gateway", "GSCC connection method forwarded")
    assert_true(payload["github_actor"] == "fresh-provider-actor", "observable actor forwarded")
    assert_true(payload["event_type"] == "GSCC_OBSERVABLE_PULL_REQUEST", "safe event class forwarded")
    assert_true(payload["last_action"] == "GSCC_OBSERVABLE_ARRIVAL", "arrival action marker")
    assert_true("mutation_authority_granted" not in payload, "presence transport must not grant write authority")
    serialized = json.dumps(call["body"])
    assert_true("runtime-only-token" not in serialized, "transport credential must never enter payload")
    assert_true("must-not-leave-event-file" not in serialized, "unsafe raw event fields must never enter payload")

    controlled_calls: list[dict] = []
    controlled = emit_controlled_arrival(
        repository="chainsolutions-wealthtech/Governed-Repository-Template",
        connection_ref="provider-host:fresh-agent-a",
        client_instance_id="provider-host-client-a",
        provider="chatgpt",
        agent="fresh-agent-a",
        branch="main",
        observed_head="c" * 40,
        token="runtime-only-token",
        request_fn=fake_request(controlled_calls),
    )
    assert_true(controlled["message"]["type"] == "SESSION_ATTACH", "controlled first touch must enter GSCC")
    controlled_payload = controlled_calls[0]["body"]["client_payload"]
    assert_true(controlled_payload["surface_class"] == "CONTROLLED_INSTRUMENTABLE", "controlled host is instrumentable")
    assert_true(controlled_payload["provider"] == "chatgpt", "declared provider preserved")
    assert_true(controlled_payload["connection_ref"] == "provider-host:fresh-agent-a", "stable host connection preserved")
    assert_true("provider_ref" not in controlled_payload, "provider-private ref stays absent unless supplied")

    internal = {
        "repository": event["repository"],
        "sender": {"login": "github-actions[bot]"},
        "ref": "refs/heads/main",
        "after": "d" * 40,
    }
    assert_true(
        should_skip_github_arrival(internal, {"GITHUB_EVENT_NAME": "push"}) == "INTERNAL_GITHUB_ACTIONS_STATE_PUSH",
        "internal state persistence push must not recursively create GSCC arrival",
    )

    dispatch = {
        "repository": event["repository"],
        "sender": {"login": "fresh-provider-actor"},
        "action": "gacr_auto-attach",
    }
    assert_true(
        should_skip_github_arrival(dispatch, {"GITHUB_EVENT_NAME": "repository_dispatch"}) == "INTERNAL_GACR_OR_GSCC_DISPATCH",
        "GSCC/GACR dispatch must not recurse into a new arrival",
    )

    text = WORKFLOW.read_text(encoding="utf-8")
    for trigger in (
        "push:",
        "create:",
        "pull_request:",
        "issues:",
        "issue_comment:",
        "pull_request_review:",
        "pull_request_review_comment:",
        "workflow_dispatch:",
    ):
        assert_true(trigger in text, f"workflow must observe {trigger}")
    assert_true("repository_dispatch:" not in text, "gateway workflow must not recursively trigger on its own dispatch")
    assert_true("python3 scripts/gscc_observable_arrival.py github-event" in text, "workflow must enter GSCC gateway")
    assert_true("contents: write" in text, "repository_dispatch requires bounded write permission")

    print("GSCC_OBSERVABLE_ARRIVAL_GATEWAY_TEST_PASS")


if __name__ == "__main__":
    main()
