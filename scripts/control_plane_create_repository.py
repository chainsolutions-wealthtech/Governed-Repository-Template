#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
import time

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

CANONICAL_OWNER_BY_LABEL = {
    "chainsolutions-wealthtech": "chainsolutions-wealthtech",
    "Wealthtechinnovations": "Wealthtechinnovations",
    "Patricked": "Patricked-code",
}
SCOPE_BY_LABEL = {
    "chainsolutions-wealthtech": "ORGANIZATION",
    "Wealthtechinnovations": "PERSONAL_ACCOUNT",
    "Patricked": "PERSONAL_ACCOUNT",
}


def wait_for_initial_head(token: str, owner: str, name: str, branch: str, attempts: int = 15, delay_seconds: float = 2.0) -> str:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            commit = github_api(token, "GET", f"/repos/{owner}/{name}/commits/{branch}")
            sha = (commit or {}).get("sha")
            if isinstance(sha, str) and len(sha) == 40:
                return sha
        except RuntimeError as exc:
            last_error = exc
            if "failed: 409" not in str(exc):
                raise
        if attempt < attempts - 1:
            time.sleep(delay_seconds)
    raise RuntimeError(f"unable to observe initial target HEAD after creation: {last_error}")


def _decode_manifest(content: dict | None) -> dict | None:
    if not content:
        return None
    encoded = content.get("content")
    if not isinstance(encoded, str):
        return None
    import base64
    try:
        return json.loads(base64.b64decode(encoded).decode("utf-8"))
    except Exception:
        return None


def target_matches_governed_template(token: str, owner: str, name: str) -> bool:
    target_content = github_api(
        token,
        "GET",
        f"/repos/{owner}/{name}/contents/.governance/TEMPLATE_MANIFEST.json",
        allow_404=True,
    )
    source_content = github_api(
        token,
        "GET",
        f"/repos/{TEMPLATE_OWNER}/{TEMPLATE_REPO}/contents/.governance/TEMPLATE_MANIFEST.json",
        allow_404=True,
    )
    target_manifest = _decode_manifest(target_content)
    source_manifest = _decode_manifest(source_content)
    if not target_manifest or not source_manifest:
        return False
    return (
        target_manifest.get("template_name") == "Governed Repository Template"
        and target_manifest.get("template_name") == source_manifest.get("template_name")
        and target_manifest.get("template_version") == source_manifest.get("template_version")
    )


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

    token = os.environ.get("GOVERNED_CREATOR_TOKEN")
    if not token:
        fail_without_advancing(
            args.issue_number,
            "Token d'installation GitHub App absent: `GOVERNED_CREATOR_TOKEN`. "
            "Le workflow doit le générer à partir de l'App centrale pour le propriétaire cible.",
        )
        return

    canonical_owner = CANONICAL_OWNER_BY_LABEL[owner_label]
    scope = SCOPE_BY_LABEL[owner_label]
    full_name = f"{canonical_owner}/{repository_name}"

    template = github_api(token, "GET", f"/repos/{TEMPLATE_OWNER}/{TEMPLATE_REPO}")
    if not template or template.get("is_template") is not True:
        fail_without_advancing(
            args.issue_number,
            "Le credential ne peut pas lire le template privé ou le repository source n'est plus marqué template.",
        )
        return

    existing = github_api(token, "GET", f"/repos/{canonical_owner}/{repository_name}", allow_404=True)
    recovered_existing = False
    if existing is not None:
        if not target_matches_governed_template(token, canonical_owner, repository_name):
            fail_without_advancing(
                args.issue_number,
                f"Le repository cible `{full_name}` existe déjà et n'est pas reconnu comme une génération V2.3.3 du template gouverné.",
            )
            return
        recovered_existing = True
        created = existing
    else:
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
    initial_head = wait_for_initial_head(token, canonical_owner, repository_name, default_branch)

    evidence = {
        "repository": full_name,
        "template_repository": f"{TEMPLATE_OWNER}/{TEMPLATE_REPO}",
        "repository_scope": scope,
        "visibility": visibility,
        "created": True,
        "recovered_existing": recovered_existing,
        "initial_head_sha": initial_head,
    }
    state = apply_evidence(state, "PREP-001", "PASS", evidence)
    persist_state(args.issue_number, issue.get("body"), state)
    comment(args.issue_number, render_response(state))


if __name__ == "__main__":
    main()
