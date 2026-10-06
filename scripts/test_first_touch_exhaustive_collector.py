#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from first_touch_exhaustive_collector import build_capture

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "gscc-observable-arrival.yml"


def fake_request(url: str, token: str | None):
    if url.endswith("/repos/chainsolutions-wealthtech/Governed-Repository-Template"):
        return 200, {
            "id": 1386478935,
            "full_name": "chainsolutions-wealthtech/Governed-Repository-Template",
            "permissions": {"admin": True, "maintain": True, "push": True, "triage": True, "pull": True},
        }
    if "/collaborators/fresh-provider-actor/permission" in url:
        return 200, {"permission": "admin", "user": {"login": "fresh-provider-actor", "id": 123}}
    if url.endswith("/issues/321"):
        return 200, {
            "id": 987654,
            "number": 321,
            "node_id": "I_test",
            "title": "first touch",
            "body": "user-visible body retained",
            "user": {"login": "fresh-provider-actor"},
        }
    if "/actions/runs/40000000009/jobs" in url:
        return 200, {"total_count": 1, "jobs": [{"id": 444, "name": "arrival"}]}
    if "/actions/runs/40000000009" in url:
        return 200, {"id": 40000000009, "event": "issues", "head_branch": "main"}
    if url.endswith("/installation"):
        return 403, {"message": "Resource not accessible by integration"}
    if url.endswith("/actions/permissions"):
        return 200, {"enabled": True, "allowed_actions": "all"}
    raise AssertionError(url)


def main():
    event = {
        "repository": {
            "id": 1386478935,
            "full_name": "chainsolutions-wealthtech/Governed-Repository-Template",
            "owner": {"login": "chainsolutions-wealthtech", "id": 299685687},
        },
        "sender": {"login": "fresh-provider-actor", "id": 123},
        "issue": {
            "id": 987654,
            "number": 321,
            "node_id": "I_test",
            "title": "first touch",
            "body": "user-visible body retained",
            "performed_via_github_app": {"slug": "chatgpt-codex-connector"},
        },
        "number": 321,
        "extra_unexpected_field": {"nested": [1, 2, 3]},
        "another_unknown_scalar": "preserve-me",
    }
    env = {
        "GITHUB_EVENT_NAME": "issues",
        "GITHUB_REPOSITORY": "chainsolutions-wealthtech/Governed-Repository-Template",
        "GITHUB_REPOSITORY_ID": "1386478935",
        "GITHUB_ACTOR": "fresh-provider-actor",
        "GITHUB_RUN_ID": "40000000009",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_SHA": "a" * 40,
        "GITHUB_REF_NAME": "main",
        "GITHUB_API_URL": "https://api.github.com",
        "RUNNER_NAME": "GitHub Actions 1000000000",
        "PATH": "/usr/bin:/bin",
        "UNRELATED_ENV": "must-not-be-in-capture",
    }
    capture = build_capture(
        event,
        env,
        request_fn=fake_request,
        observed_at="2026-10-06T02:50:00+00:00",
    )

    assert capture["schema"] == "first-touch-exhaustive-capture/v1"
    assert capture["repository"] == "chainsolutions-wealthtech/Governed-Repository-Template"
    assert capture["actor"] == "fresh-provider-actor"
    assert capture["subject"]["issue_number"] == 321
    assert capture["github_event"]["extra_unexpected_field"] == {"nested": [1, 2, 3]}
    assert capture["github_event"]["another_unknown_scalar"] == "preserve-me"
    assert capture["github_event"]["issue"]["body"] == "user-visible body retained"
    assert capture["environment"]["RUNNER_NAME"] == "GitHub Actions 1000000000"
    assert "UNRELATED_ENV" not in capture["environment"]
    assert capture["mutation_authority_granted"] is False
    assert capture["interpretation_applied"] is False

    attempts = {item["name"]: item for item in capture["api_attempts"]}
    assert attempts["repository"]["http_status"] == 200
    assert attempts["actor_repository_permission"]["response"]["permission"] == "admin"
    assert attempts["issue"]["response"]["node_id"] == "I_test"
    assert attempts["workflow_run_jobs"]["response"]["jobs"][0]["id"] == 444
    assert attempts["repository_installation"]["http_status"] == 403
    assert attempts["repository_actions_permissions"]["response"]["enabled"] is True

    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "python3 scripts/first_touch_exhaustive_collector.py github-event" in workflow
    assert "actions/upload-artifact@" in workflow
    assert "first-touch-capture-" in workflow
    assert "Enter canonical GSCC arrival gateway" in workflow
    assert workflow.index("Capture exhaustive first-touch evidence") < workflow.index("Enter canonical GSCC arrival gateway")

    print("FIRST_TOUCH_EXHAUSTIVE_COLLECTOR_TEST_PASS")


if __name__ == "__main__":
    main()
