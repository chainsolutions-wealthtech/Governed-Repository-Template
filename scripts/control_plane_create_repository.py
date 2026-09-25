#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request

from governed_request import apply_evidence
from control_plane_issue_bridge import (
    CONTROL_PLANE_REPOSITORY,
    api as control_plane_api,
    extract_state,
    persist_state,
    render_response,
)

TEMPLATE_OWNER = "chainsolutions-wealthtech"
TEMPLATE_REPO = "Governed-Repository-Template"

TOKEN_ENV_BY_LABEL = {
    "chainsolutions-wealthtech": "GOVERNED_CREATOR_WEALTHTECH_TOKEN",
    "Wealthtechinnovations": "GOVERNED_CREATOR_WEALTHTECH_TOKEN",
    "Patricked": "GOVERNED_CREATOR_PATRICKED_TOKEN",
}
CANONICAL_OWNER_BY_LABEL = {
    "chainsolutions-wealthtech": "chainsolutions-wealthtech",
    "Wealthtechinnovations": "Wealthtechinnovations",
    "Patricked": "Patricked-code",
}
PRINCIPAL_BY_LABEL = {
    "chainsolutions-wealthtech": "Wealthtechinnovations",
    "Wealthtechinnovations": "Wealthtechinnovations",
    "Patricked": "Patricked-code",
}
SCOPE_BY_LABEL = {
    "chainsolutions-wealthtech": "ORGANIZATION",
    "Wealthtechinnovations": "PERSONAL_ACCOUNT",
    "Patricked": "PERSONAL_ACCOUNT",
}


def github_api(token: str, method: str, path: str, payload: dict | None = None, allow_404: bool = False) -> dict | None:
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "governed-repository-create-executor",
        },
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if allow_404 and exc.code == 404:
            return None
        raise RuntimeError(f"GitHub API {method} {path} failed: {exc.code} {body}") from exc


def comment(issue_number: int, body: str) -> None:
    control_plane_api(
        "POST",
        f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{issue_number}/comments",
        {"body": body},
    )


def fail_without_advancing(issue_number: int, reason: str) -> None:
    comment(
        issue_number,
        "### Governed Repository creation executor — BLOCKED\n\n"
        + reason
        + "\n\nAucune preuve PASS n'a été fabriquée et l'état reste sur PREP-001. "
          "Après correction de l'autorité/credential, commenter `/governed-execute` pour réessayer.",
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--issue-number", type=int, required=True)
    args = p.parse_args()

    issue = control_plane_api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{args.issue_number}")
    state = extract_state(issue.get("body"))
    next_request = state.get("next_request") or {}

    if state.get("answers", {}).get("entry_action") != "CREATE_NEW_REPOSITORY":
        raise SystemExit("CREATE_EXECUTOR_SKIPPED: request is not CREATE_NEW_REPOSITORY")
    if next_request.get("kind") != "ACTION_REQUEST" or next_request.get("action_id") != "PREP-001":
        raise SystemExit("CREATE_EXECUTOR_SKIPPED: request is not waiting on PREP-001")

    answers = state["answers"]
    owner_label = answers["creation_target_owner"]
    repository_name = answers["repository_name"]
    visibility = answers["visibility"]

    token_env = TOKEN_ENV_BY_LABEL[owner_label]
    token = os.environ.get(token_env)
    if not token:
        fail_without_advancing(args.issue_number, f"Secret requis absent: `{token_env}`.")
        return

    expected_principal = PRINCIPAL_BY_LABEL[owner_label]
    canonical_owner = CANONICAL_OWNER_BY_LABEL[owner_label]
    scope = SCOPE_BY_LABEL[owner_label]
    full_name = f"{canonical_owner}/{repository_name}"

    user = github_api(token, "GET", "/user")
    login = (user or {}).get("login")
    if login != expected_principal:
        fail_without_advancing(
            args.issue_number,
            f"Le credential `{token_env}` s'authentifie comme `{login}`, attendu `{expected_principal}`.",
        )
        return

    template = github_api(token, "GET", f"/repos/{TEMPLATE_OWNER}/{TEMPLATE_REPO}")
    if not template or template.get("is_template") is not True:
        fail_without_advancing(
            args.issue_number,
            "Le credential ne peut pas lire le template privé ou le repository source n'est plus marqué template.",
        )
        return

    existing = github_api(token, "GET", f"/repos/{canonical_owner}/{repository_name}", allow_404=True)
    if existing is not None:
        fail_without_advancing(args.issue_number, f"Le repository cible `{full_name}` existe déjà.")
        return

    if scope == "ORGANIZATION":
        membership = github_api(
            token,
            "GET",
            f"/user/memberships/orgs/{canonical_owner}",
            allow_404=True,
        )
        if not membership or membership.get("state") != "active":
            fail_without_advancing(
                args.issue_number,
                f"Le principal `{login}` n'a pas une adhésion active vérifiée à `{canonical_owner}`.",
            )
            return

    created = github_api(
        token,
        "POST",
        f"/repos/{TEMPLATE_OWNER}/{TEMPLATE_REPO}/generate",
        {
            "owner": canonical_owner,
            "name": repository_name,
            "include_all_branches": False,
            "private": visibility == "private",
        },
    )

    if not created or created.get("full_name") != full_name:
        raise RuntimeError("GitHub generate-from-template response did not match expected target")

    default_branch = created.get("default_branch") or "main"
    commit = github_api(token, "GET", f"/repos/{canonical_owner}/{repository_name}/commits/{default_branch}")
    initial_head = (commit or {}).get("sha")
    if not isinstance(initial_head, str) or len(initial_head) != 40:
        raise RuntimeError("unable to observe initial target HEAD after creation")

    evidence = {
        "repository": full_name,
        "template_repository": f"{TEMPLATE_OWNER}/{TEMPLATE_REPO}",
        "repository_scope": scope,
        "visibility": visibility,
        "created": True,
        "initial_head_sha": initial_head,
    }
    state = apply_evidence(state, "PREP-001", "PASS", evidence)
    persist_state(args.issue_number, issue.get("body"), state)
    comment(args.issue_number, render_response(state))


if __name__ == "__main__":
    main()
