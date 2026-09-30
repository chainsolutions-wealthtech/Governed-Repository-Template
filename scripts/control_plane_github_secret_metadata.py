#!/usr/bin/env python3
"""KBI-04J: transient read-only GitHub capability and secret-metadata mapping.

Only GET endpoints are used. Responses are reduced to an explicit metadata
allowlist; secret values, token scopes and write authority are never inferred.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Callable

REPOSITORY = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38}[A-Za-z0-9])?/[A-Za-z0-9_.-]{1,100}$")
SECRET_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,99}$")
ENVIRONMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,99}$")
BRANCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,99}$")
TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
MAX_PAGES = 5


def safe_secret_metadata(item):
    if not isinstance(item, dict) or not isinstance(item.get("name"), str):
        return None
    name = item["name"]
    if not SECRET_NAME.fullmatch(name):
        return None
    result = {"name": name}
    for key in ("created_at", "updated_at"):
        value = item.get(key)
        if isinstance(value, str) and TIMESTAMP.fullmatch(value):
            result[key] = value
    return result


def read_collection(get_json: Callable[[str], dict], path: str, key: str, normalize) -> dict:
    items = []
    expected = None
    try:
        for page in range(1, MAX_PAGES + 1):
            payload = get_json(f"{path}?per_page=100&page={page}")
            if not isinstance(payload, dict) or not isinstance(payload.get(key), list):
                return {"status": "UNKNOWN_ACCESS_UNAVAILABLE", "items": []}
            total = payload.get("total_count")
            if not isinstance(total, int) or isinstance(total, bool) or total < 0:
                return {"status": "UNKNOWN_ACCESS_UNAVAILABLE", "items": []}
            if expected is not None and expected != total:
                return {"status": "UNKNOWN_ACCESS_UNAVAILABLE", "items": []}
            expected = total
            for raw in payload[key]:
                compact = normalize(raw)
                if compact is not None:
                    items.append(compact)
            if len(payload[key]) < 100 or page * 100 >= total:
                status = "KNOWN_CURRENT" if len(items) == total else "PARTIAL_BOUNDED"
                return {"status": status, "items": items}
        return {"status": "PARTIAL_BOUNDED", "items": items}
    except Exception:
        # API errors can contain URLs, credential details or private messages.
        return {"status": "UNKNOWN_ACCESS_UNAVAILABLE", "items": []}


def safe_environment(item):
    if not isinstance(item, dict):
        return None
    name = item.get("name")
    return {"name": name} if isinstance(name, str) and ENVIRONMENT.fullmatch(name) and ".." not in name else None


def collect_github_metadata(
    repository: str, get_json: Callable[[str], dict], *, observed_at: str,
) -> dict:
    if not REPOSITORY.fullmatch(repository) or ".." in repository:
        raise ValueError("REPOSITORY_INVALID")
    base = f"/repos/{repository}"
    try:
        raw = get_json(base)
        if not isinstance(raw, dict) or raw.get("full_name", "").lower() != repository.lower():
            raise ValueError("REPOSITORY_MISMATCH")
        branch = raw.get("default_branch")
        repo = {
            "status": "KNOWN_CURRENT", "default_branch": branch if isinstance(branch, str) and BRANCH.fullmatch(branch) else None,
            "visibility": "private" if raw.get("private") is True else "public" if raw.get("private") is False else "UNKNOWN",
        }
    except Exception:
        repo = {"status": "UNKNOWN_ACCESS_UNAVAILABLE"}
    repo_secrets = read_collection(get_json, base + "/actions/secrets", "secrets", safe_secret_metadata)
    org_secrets = read_collection(get_json, base + "/actions/organization-secrets", "secrets", safe_secret_metadata)
    environment_list = read_collection(get_json, base + "/environments", "environments", safe_environment)
    environments = []
    for item in environment_list["items"]:
        name = item["name"]
        path = base + "/environments/" + urllib.parse.quote(name, safe="") + "/secrets"
        environments.append({
            "name": name,
            "secrets": read_collection(get_json, path, "secrets", safe_secret_metadata),
        })
    return {
        "schema_version": "1.0.0", "authority_id": "CP-IDENTITY-SECRET-001",
        "slice": "KBI-04J", "observed_at": observed_at, "repository": repository,
        "status": "PARTIAL_READ_ONLY_METADATA",
        "repository_state": repo,
        "read_capabilities": {
            "repository": repo["status"],
            "repository_secret_metadata": repo_secrets["status"],
            "shared_organization_secret_metadata": org_secrets["status"],
            "environment_list": environment_list["status"],
            "environment_secret_metadata": {
                item["name"]: item["secrets"]["status"] for item in environments
            },
        },
        "repository_secrets": repo_secrets,
        "shared_organization_secrets": org_secrets,
        "environment_list_status": environment_list["status"],
        "environments": environments,
        "write_capability": "NOT_ATTESTED_BY_READ_PROBE",
        "mutation_authority_granted": False,
        "secret_values_persisted": False,
    }


def github_get(token: str, path: str) -> dict:
    if not path.startswith("/repos/"):
        raise ValueError("PATH_NOT_ALLOWED")
    request = urllib.request.Request(
        "https://api.github.com" + path,
        method="GET",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "governed-identity-secret-metadata",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ValueError("RESPONSE_TOO_LARGE")
    return json.loads(raw)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    args = parser.parse_args()
    token = os.environ.get("GOVERNED_GITHUB_READ_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("KBI_04J_BLOCKED:GOVERNED_GITHUB_READ_TOKEN_MISSING")
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    try:
        result = collect_github_metadata(args.repository, lambda path: github_get(token, path), observed_at=timestamp)
    except ValueError:
        raise SystemExit("KBI_04J_BLOCKED:REPOSITORY_INVALID") from None
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
