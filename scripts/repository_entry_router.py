#!/usr/bin/env python3
"""Repository entry selector. Door A unchanged; Door B relies on GitHub's API.

A prompt, role, claimed username, GITHUB_ACTOR or repository public status
never authenticates a user. Verification is performed using the current
GitHub credential and enforced again by GitHub on every actual write.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

from gscc_entry_router import route as gscc_route

ROOT = Path(__file__).resolve().parents[1]
POLICY_FILE = ROOT / ".governance" / "repository-entry-gates.json"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
DIRECT = "00_DIRECT_OWNER_ENTRY.md"
GOVERNED = "00_GSCC_ENTRY.md"


class AuthFailed(Exception):
    """Authenticated GitHub proof or native permission was not established."""


def policy(path: Path = POLICY_FILE) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("schema") != "repository-entry-gates/v1":
        raise ValueError("unsupported repository entry policy")
    return doc


def github_reader(token: str) -> Callable[[str], dict]:
    if not token or not isinstance(token, str):
        raise AuthFailed("GITHUB_CREDENTIAL_UNAVAILABLE")
    def read(path: str) -> dict:
        req = urllib.request.Request(
            "https://api.github.com" + path,
            headers={
                "Authorization": "Bearer " + token,
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "governed-repository-direct-owner-entry",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                body = json.loads(response.read(262144).decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
            raise AuthFailed("GITHUB_VERIFICATION_UNAVAILABLE") from exc
        if not isinstance(body, dict):
            raise AuthFailed("GITHUB_PROOF_MALFORMED")
        return body
    return read


def select_entry(
    entry_file: str | None = None,
    mission: str | None = None,
    *,
    read_github: Callable[[str], dict] | None = None,
    expected_head: str | None = None,
    policy_doc: dict | None = None,
) -> dict[str, Any]:
    """Select entry from exact explicit file, never from role or actor text alone.

    read_github is a *trusted* API adapter constructed by github_reader in CLI;
    tests supply a synthetic adapter to exercise the decision matrix.
    """
    p = policy_doc if policy_doc is not None else policy()
    requested = entry_file or p["default_entry"]
    if requested != p["direct_entry"]:
        if requested != p["default_entry"]:
            return {
                "entry": "BLOCKED", "status": "UNKNOWN_ENTRY_FILE",
                "may_write": False, "next_authority": p["default_entry"],
            }
        return {
            **gscc_route("ARRIVAL"),
            "entry": "GOVERNED", "selected_entry_file": GOVERNED,
            "requires_gscc": True, "may_write": False,
        }

    chosen_role = p["mission_roles"].get(str(mission or "").strip().upper())
    if chosen_role is None:
        return {
            "entry": "DIRECT", "status": "ROLE_DECLARATION_REQUIRED",
            "may_write": False, "authenticated": False,
            "next_authority": DIRECT, "supported_missions": sorted(p["mission_roles"]),
        }
    if read_github is None:
        return {
            "entry": "DIRECT", "status": "AUTHENTICATION_REQUIRED",
            "may_write": False, "authenticated": False,
            "next_authority": DIRECT,
        }
    repo = p["repository"]
    try:
        identity = read_github("/user")
        actor = identity.get("login")
        if not isinstance(actor, str) or not actor:
            raise AuthFailed("GITHUB_ACTOR_UNAVAILABLE")
        if actor not in p["authenticated_owner_logins"]:
            raise AuthFailed("GITHUB_OWNER_NOT_AUTHORIZED")

        details = read_github("/repos/" + repo)
        permissions = details.get("permissions")
        if details.get("full_name") != repo or not isinstance(permissions, dict):
            raise AuthFailed("GITHUB_REPOSITORY_PERMISSION_PROOF_UNAVAILABLE")
        if not all(isinstance(permissions.get(key), bool) for key in ("pull", "push")):
            raise AuthFailed("GITHUB_REPOSITORY_PERMISSION_PROOF_UNAVAILABLE")
        if not permissions["pull"]:
            raise AuthFailed("GITHUB_READ_PERMISSION_REQUIRED")

        branch = str(details.get("default_branch") or "")
        if not branch or "/" in branch or branch in {".", ".."}:
            raise AuthFailed("GITHUB_CANONICAL_BRANCH_UNAVAILABLE")
        observed = read_github("/repos/" + repo + "/commits/" + branch)
        sha = observed.get("sha")
        if not isinstance(sha, str) or not SHA40.fullmatch(sha):
            raise AuthFailed("GITHUB_HEAD_UNAVAILABLE")
        if expected_head is not None and expected_head != sha:
            raise AuthFailed("GITHUB_HEAD_MOVED")
    except (AuthFailed, KeyError) as exc:
        return {
            "entry": "DIRECT", "status": str(exc) or "GITHUB_AUTHORIZATION_BLOCKED",
            "may_write": False, "authenticated": False,
            "next_authority": DIRECT,
            "grants_gacr_claim": False, "creates_gscc_receipt": False,
        }

    can_push = permissions["push"]
    return {
        "entry": "DIRECT",
        "selected_entry_file": DIRECT,
        "status": "DIRECT_OWNER_VERIFIED",
        "authenticated": True,
        "authenticated_actor": actor,
        "actor_source": "GITHUB_REST_API_AUTHENTICATED_USER",
        "role": chosen_role["role"],
        "connection_intent": chosen_role["intent"],
        "repository": repo,
        "canonical_branch": branch,
        "observed_head": sha,
        "github_native_permissions": {"pull": True, "push": can_push},
        "may_read": True,
        "may_attempt_git_write": can_push,
        "may_attempt_direct_main_write": can_push,
        "may_write": can_push,
        "native_github_enforces_every_write": True,
        "branch_protection_bypass_granted": False,
        "main_write_success_claimed": False,
        "requires_gscc": False,
        "requires_gse": False,
        "requires_gacr": False,
        "requires_f1": False,
        "requires_preassigned_work_item": False,
        "grants_gacr_claim": False,
        "creates_gscc_receipt": False,
        "next_authority": "00_START_HERE.md",
        "next_action": (
            "EXECUTE_SCOPED_GITHUB_OPERATION_WITH_EXACT_HEAD_AND_NATIVE_CONTROLS"
            if can_push else "READ_ONLY_NATIVE_GITHUB_OPERATIONS"
        ),
        "trace": "GITHUB_NATIVE_COMMIT_PR_ISSUE_OR_REVIEW",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Select governed or direct GitHub owner repository entry")
    parser.add_argument("--entry-file", default=GOVERNED)
    parser.add_argument("--mission")
    parser.add_argument("--expected-head")
    args = parser.parse_args()
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    # Never read GITHUB_ACTOR as identity. API /user is the sole identity source.
    adapter = github_reader(token) if args.entry_file == DIRECT and token else None
    decision = select_entry(
        args.entry_file, args.mission,
        read_github=adapter, expected_head=args.expected_head,
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    if decision.get("entry") == "BLOCKED" or (
        decision.get("entry") == "DIRECT" and decision.get("status") != "DIRECT_OWNER_VERIFIED"
    ):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
