#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "gscc-provider-repository-enrichment/v1"

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _get_json(url: str, token: str) -> tuple[int, Any]:
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "gscc-provider-repository-enrichment/1",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            data = response.read()
            return int(response.status), json.loads(data.decode("utf-8")) if data else None
    except urllib.error.HTTPError as exc:
        body = exc.read()
        try:
            payload = json.loads(body.decode("utf-8")) if body else None
        except Exception:
            payload = None
        return int(exc.code), payload

def _evidence(value: Any, source_ref: str, observed_at: str, *, reason: str | None = None) -> dict[str, Any]:
    return {
        "value": value,
        "source": "repository_observed",
        "confidence": "exact",
        "reason": reason,
        "observed_at": observed_at,
        "evidence_ref": source_ref,
    }

def enrich_envelope(envelope: dict[str, Any], token: str, *, api_base: str = "https://api.github.com", observed_at: str | None = None, request_fn=_get_json) -> dict[str, Any]:
    observed_at = observed_at or utc_now()
    repository = str(envelope.get("repository") or "").strip()
    if repository.count("/") != 1:
        raise ValueError("repository must use owner/name")
    owner, name = repository.split("/", 1)
    root = f"{api_base.rstrip('/')}/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(name)}"

    enriched = json.loads(json.dumps(envelope))
    attempts: list[dict[str, Any]] = []
    repository_data: dict[str, Any] = {}
    branch_data: dict[str, Any] = {}
    commit_data: dict[str, Any] = {}
    workflows_data: dict[str, Any] = {}
    runs_data: dict[str, Any] = {}

    def call(label: str, url: str) -> Any:
        status, payload = request_fn(url, token)
        attempts.append({
            "operation": label,
            "method": "GET",
            "endpoint": url.split("api.github.com")[-1] if "api.github.com" in url else url,
            "http_status": status,
            "success": 200 <= status < 300,
            "observed_at": observed_at,
        })
        return payload if 200 <= status < 300 else None

    repository_data = call("repository_metadata", root) or {}
    default_branch = repository_data.get("default_branch") or enriched.get("branch") or "main"
    branch_data = call("default_branch", f"{root}/branches/{urllib.parse.quote(str(default_branch), safe='')}") or {}
    observed_head = ((branch_data.get("commit") or {}).get("sha") if isinstance(branch_data, dict) else None) or enriched.get("observed_head")
    if observed_head:
        commit_data = call("commit", f"{root}/commits/{urllib.parse.quote(str(observed_head), safe='')}") or {}
    workflows_data = call("actions_workflows", f"{root}/actions/workflows?per_page=100") or {}
    runs_data = call("actions_runs", f"{root}/actions/runs?per_page=20") or {}

    repo_owner = repository_data.get("owner") if isinstance(repository_data.get("owner"), dict) else {}
    permissions = repository_data.get("permissions") if isinstance(repository_data.get("permissions"), dict) else {}
    commit_obj = commit_data.get("commit") if isinstance(commit_data.get("commit"), dict) else {}
    commit_author = commit_obj.get("author") if isinstance(commit_obj.get("author"), dict) else {}
    commit_committer = commit_obj.get("committer") if isinstance(commit_obj.get("committer"), dict) else {}
    tree = commit_obj.get("tree") if isinstance(commit_obj.get("tree"), dict) else {}
    parents = commit_data.get("parents") if isinstance(commit_data.get("parents"), list) else []
    stats = commit_data.get("stats") if isinstance(commit_data.get("stats"), dict) else {}

    enriched.update({
        "repository_id": repository_data.get("id", enriched.get("repository_id", "UNAVAILABLE")),
        "repository_owner": repo_owner.get("login", enriched.get("repository_owner", owner)),
        "repository_owner_id": repo_owner.get("id", enriched.get("repository_owner_id", "UNAVAILABLE")),
        "repository_owner_type": repo_owner.get("type", enriched.get("repository_owner_type", "UNAVAILABLE")),
        "repository_visibility": repository_data.get("visibility", enriched.get("repository_visibility", "UNAVAILABLE")),
        "default_branch": repository_data.get("default_branch", enriched.get("default_branch", "UNAVAILABLE")),
        "branch": default_branch,
        "observed_head": observed_head or "UNAVAILABLE",
    })

    enriched["repository_observation"] = {
        "id": repository_data.get("id", "UNAVAILABLE"),
        "name": repository_data.get("name", name),
        "full_name": repository_data.get("full_name", repository),
        "owner": {
            "login": repo_owner.get("login", owner),
            "id": repo_owner.get("id", "UNAVAILABLE"),
            "type": repo_owner.get("type", "UNAVAILABLE"),
        },
        "visibility": repository_data.get("visibility", "UNAVAILABLE"),
        "private": repository_data.get("private", "UNAVAILABLE"),
        "archived": repository_data.get("archived", "UNAVAILABLE"),
        "fork": repository_data.get("fork", "UNAVAILABLE"),
        "default_branch": repository_data.get("default_branch", "UNAVAILABLE"),
        "size": repository_data.get("size", "UNAVAILABLE"),
        "html_url": repository_data.get("html_url", "UNAVAILABLE"),
        "clone_url": repository_data.get("clone_url", "UNAVAILABLE"),
        "git_url": repository_data.get("git_url", "UNAVAILABLE"),
        "created_at": repository_data.get("created_at", "UNAVAILABLE"),
        "updated_at": repository_data.get("updated_at", "UNAVAILABLE"),
        "pushed_at": repository_data.get("pushed_at", "UNAVAILABLE"),
        "language": repository_data.get("language", "UNAVAILABLE"),
        "topics": repository_data.get("topics", []),
        "is_template": repository_data.get("is_template", "UNAVAILABLE"),
        "permissions": {
            "admin": permissions.get("admin", "UNAVAILABLE"),
            "maintain": permissions.get("maintain", "UNAVAILABLE"),
            "push": permissions.get("push", "UNAVAILABLE"),
            "pull": permissions.get("pull", "UNAVAILABLE"),
            "triage": permissions.get("triage", "UNAVAILABLE"),
            "source": "github_actions_repository_token_observation",
        },
    }

    enriched["git_observation"] = {
        "branch_name": default_branch,
        "head_sha": observed_head or "UNAVAILABLE",
        "branch_protected": branch_data.get("protected", "UNAVAILABLE") if isinstance(branch_data, dict) else "UNAVAILABLE",
        "commit_sha": commit_data.get("sha", observed_head or "UNAVAILABLE"),
        "commit_parent_shas": [p.get("sha") for p in parents if isinstance(p, dict) and p.get("sha")],
        "commit_tree_sha": tree.get("sha", "UNAVAILABLE"),
        "commit_message": commit_obj.get("message", "UNAVAILABLE"),
        "commit_author_name": commit_author.get("name", "UNAVAILABLE"),
        "commit_author_email": commit_author.get("email", "UNAVAILABLE"),
        "commit_author_date": commit_author.get("date", "UNAVAILABLE"),
        "commit_committer_name": commit_committer.get("name", "UNAVAILABLE"),
        "commit_committer_email": commit_committer.get("email", "UNAVAILABLE"),
        "commit_committer_date": commit_committer.get("date", "UNAVAILABLE"),
        "commit_html_url": commit_data.get("html_url", "UNAVAILABLE"),
        "commit_api_url": commit_data.get("url", "UNAVAILABLE"),
        "commit_comment_count": commit_obj.get("comment_count", "UNAVAILABLE"),
        "commit_signature_verified": ((commit_obj.get("verification") or {}).get("verified") if isinstance(commit_obj.get("verification"), dict) else "UNAVAILABLE"),
        "commit_signature_reason": ((commit_obj.get("verification") or {}).get("reason") if isinstance(commit_obj.get("verification"), dict) else "UNAVAILABLE"),
        "commit_files_changed": len(commit_data.get("files") or []) if isinstance(commit_data.get("files"), list) else "UNAVAILABLE",
        "commit_additions": stats.get("additions", "UNAVAILABLE"),
        "commit_deletions": stats.get("deletions", "UNAVAILABLE"),
    }

    workflows = workflows_data.get("workflows") if isinstance(workflows_data.get("workflows"), list) else []
    runs = runs_data.get("workflow_runs") if isinstance(runs_data.get("workflow_runs"), list) else []
    enriched["permissions"] = {
        "admin": permissions.get("admin", "UNAVAILABLE"),
        "maintain": permissions.get("maintain", "UNAVAILABLE"),
        "push": permissions.get("push", "UNAVAILABLE"),
        "pull": permissions.get("pull", "UNAVAILABLE"),
        "triage": permissions.get("triage", "UNAVAILABLE"),
        "source": "github_actions_repository_token_observation",
        "observed_at": observed_at,
    }
    enriched["git"] = {
        "branch": default_branch,
        "head": observed_head or "UNAVAILABLE",
        "ref": f"refs/heads/{default_branch}",
        "ref_name": default_branch,
        "ref_type": "branch",
        "ref_sha": observed_head or "UNAVAILABLE",
        "default_branch_sha": observed_head or "UNAVAILABLE",
        "branch_protected": branch_data.get("protected", "UNAVAILABLE") if isinstance(branch_data, dict) else "UNAVAILABLE",
    }
    enriched["commit"] = {
        "sha": commit_data.get("sha", observed_head or "UNAVAILABLE"),
        "parent_sha": (parents[0].get("sha") if parents and isinstance(parents[0], dict) else "UNAVAILABLE"),
        "parent_shas": [p.get("sha") for p in parents if isinstance(p, dict) and p.get("sha")],
        "tree_sha": tree.get("sha", "UNAVAILABLE"),
        "message": commit_obj.get("message", "UNAVAILABLE"),
        "author_name": commit_author.get("name", "UNAVAILABLE"),
        "author_email": commit_author.get("email", "UNAVAILABLE"),
        "author_date": commit_author.get("date", "UNAVAILABLE"),
        "committer_name": commit_committer.get("name", "UNAVAILABLE"),
        "committer_email": commit_committer.get("email", "UNAVAILABLE"),
        "committer_date": commit_committer.get("date", "UNAVAILABLE"),
        "html_url": commit_data.get("html_url", "UNAVAILABLE"),
        "api_url": commit_data.get("url", "UNAVAILABLE"),
        "comment_count": commit_obj.get("comment_count", "UNAVAILABLE"),
        "signature_verified": ((commit_obj.get("verification") or {}).get("verified") if isinstance(commit_obj.get("verification"), dict) else "UNAVAILABLE"),
        "signature_reason": ((commit_obj.get("verification") or {}).get("reason") if isinstance(commit_obj.get("verification"), dict) else "UNAVAILABLE"),
        "verification_status": ((commit_obj.get("verification") or {}).get("verified") if isinstance(commit_obj.get("verification"), dict) else "UNAVAILABLE"),
        "files_changed": len(commit_data.get("files") or []) if isinstance(commit_data.get("files"), list) else "UNAVAILABLE",
        "additions": stats.get("additions", "UNAVAILABLE"),
        "deletions": stats.get("deletions", "UNAVAILABLE"),
    }
    enriched["tree"] = {
        "sha": tree.get("sha", "UNAVAILABLE"),
        "url": tree.get("url", "UNAVAILABLE"),
    }
    enriched["repository_state"] = {
        "observed_head": observed_head or "UNAVAILABLE",
        "observed_default_branch": repository_data.get("default_branch", "UNAVAILABLE"),
        "observed_branch": default_branch,
        "observed_tree": tree.get("sha", "UNAVAILABLE"),
        "observed_parent": (parents[0].get("sha") if parents and isinstance(parents[0], dict) else "UNAVAILABLE"),
        "observed_last_commit_message": commit_obj.get("message", "UNAVAILABLE"),
        "observed_last_commit_author": commit_author.get("name", "UNAVAILABLE"),
        "observed_last_commit_time": commit_author.get("date", "UNAVAILABLE"),
    }

    enriched["actions_observation"] = {
        "workflow_count": workflows_data.get("total_count", len(workflows)),
        "workflows": [
            {
                "id": w.get("id"),
                "name": w.get("name"),
                "path": w.get("path"),
                "state": w.get("state"),
            }
            for w in workflows[:100] if isinstance(w, dict)
        ],
        "recent_runs": [
            {
                "id": r.get("id"),
                "name": r.get("name"),
                "event": r.get("event"),
                "status": r.get("status"),
                "conclusion": r.get("conclusion"),
                "head_branch": r.get("head_branch"),
                "head_sha": r.get("head_sha"),
                "run_number": r.get("run_number"),
                "run_attempt": r.get("run_attempt"),
                "created_at": r.get("created_at"),
                "updated_at": r.get("updated_at"),
            }
            for r in runs[:20] if isinstance(r, dict)
        ],
    }

    latest_run = runs[0] if runs and isinstance(runs[0], dict) else {}
    enriched["workflow"] = {
        "workflow_id": latest_run.get("workflow_id", "UNAVAILABLE"),
        "name": latest_run.get("name", "UNAVAILABLE"),
        "run_id": latest_run.get("id", "UNAVAILABLE"),
        "run_number": latest_run.get("run_number", "UNAVAILABLE"),
        "run_attempt": latest_run.get("run_attempt", "UNAVAILABLE"),
        "run_status": latest_run.get("status", "UNAVAILABLE"),
        "run_conclusion": latest_run.get("conclusion", "UNAVAILABLE"),
        "event": latest_run.get("event", "UNAVAILABLE"),
        "head_sha": latest_run.get("head_sha", "UNAVAILABLE"),
        "head_branch": latest_run.get("head_branch", "UNAVAILABLE"),
        "created_at": latest_run.get("created_at", "UNAVAILABLE"),
        "updated_at": latest_run.get("updated_at", "UNAVAILABLE"),
    }

    enriched["repository_enrichment"] = {
        "schema": SCHEMA,
        "status": "ENRICHED",
        "observed_at": observed_at,
        "source": "GITHUB_REPOSITORY_ACTIONS_READS",
        "api_attempts": attempts,
        "provider_required_to_supply_repository_facts": False,
        "mutation_authority_granted": False,
    }
    enriched.setdefault("observed_at", observed_at)
    return enriched

def main() -> None:
    p = argparse.ArgumentParser(description="Enrich minimal Provider First Touch signal from repository-observable GitHub state")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    token = (os.environ.get("GITHUB_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("GITHUB_TOKEN required for repository enrichment")
    envelope = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(envelope, dict):
        raise ValueError("provider signal must be a JSON object")
    enriched = enrich_envelope(envelope, token)
    Path(args.output).write_text(json.dumps(enriched, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": enriched["repository_enrichment"]["status"],
        "repository": enriched.get("repository"),
        "observed_head": enriched.get("observed_head"),
        "mutation_authority_granted": False,
    }, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
