#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request

STATE_RE = re.compile(r"<!-- GOVERNED_LOCAL_ENTRY_STATE:([A-Za-z0-9_-]+) -->")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38}[A-Za-z0-9])?/[A-Za-z0-9_.-]{1,100}$")
SECRET_NAME = "GOVERNED_MCP_AUTH_TOKEN"


def emit_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(f"{name}={value}\n")


def fail(code: str) -> None:
    emit_output("failure_code", code)
    raise SystemExit(code)


def api(token: str, method: str, path: str) -> dict:
    request = urllib.request.Request(
        "https://api.github.com" + path,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "governed-mcp-credential-provisioner",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {path} failed: {exc.code} {body}") from exc


def decode_state(issue_body: str | None) -> dict:
    match = STATE_RE.search(issue_body or "")
    if not match:
        raise RuntimeError("LOCAL_ENTRY_STATE_MISSING")
    value = match.group(1)
    padded = value + "=" * ((4 - len(value) % 4) % 4)
    state = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))
    if not isinstance(state, dict):
        raise RuntimeError("LOCAL_ENTRY_STATE_INVALID")
    return state


def validate_requirements(state: dict) -> bool:
    next_request = state.get("next_request") or {}
    if next_request.get("kind") != "CREDENTIAL_GATE":
        return False
    requirements = next_request.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        raise RuntimeError("CREDENTIAL_GATE_REQUIREMENTS_INVALID")
    normalized = []
    for item in requirements:
        if not isinstance(item, dict):
            raise RuntimeError("CREDENTIAL_GATE_REQUIREMENTS_INVALID")
        normalized.append((item.get("kind"), item.get("name")))
    allowed = {("secret", SECRET_NAME)}
    if not set(normalized).issubset(allowed):
        raise RuntimeError("CREDENTIAL_REQUIREMENTS_UNSUPPORTED")
    return ("secret", SECRET_NAME) in normalized


def set_repository_secret(token: str, repository: str, value: str) -> None:
    if not value or len(value) > 16384:
        raise RuntimeError("MCP_AUTH_TOKEN_SOURCE_INVALID")
    env = os.environ.copy()
    env["GH_TOKEN"] = token
    completed = subprocess.run(
        ["gh", "secret", "set", SECRET_NAME, "--repo", repository, "--app", "actions"],
        input=value,
        text=True,
        capture_output=True,
        env=env,
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout or "gh secret set failed")[:2000]
        raise RuntimeError(f"MCP_AUTH_TOKEN_PROVISION_FAILED:{message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-repository", required=True)
    parser.add_argument("--target-issue", required=True, type=int)
    parser.add_argument("--expected-head", required=True)
    args = parser.parse_args()

    if not REPOSITORY_RE.fullmatch(args.target_repository):
        raise SystemExit("MCP_CREDENTIAL_TARGET_INVALID")
    if args.target_issue < 1:
        raise SystemExit("MCP_CREDENTIAL_ISSUE_INVALID")
    if not SHA_RE.fullmatch(args.expected_head):
        raise SystemExit("MCP_CREDENTIAL_EXPECTED_HEAD_INVALID")

    target_token = os.environ.get("GOVERNED_TARGET_TOKEN")
    if not target_token:
        fail("TARGET_TOKEN_MISSING")

    try:
        repository = api(target_token, "GET", f"/repos/{args.target_repository}")
        branch = repository.get("default_branch") or "main"
        ref = api(
            target_token,
            "GET",
            f"/repos/{args.target_repository}/git/ref/heads/{urllib.parse.quote(branch, safe='')}",
        )
    except RuntimeError:
        fail("TARGET_GITHUB_CONTEXT_READ_FAILED")
    remote_head = ((ref.get("object") or {}).get("sha"))
    if remote_head != args.expected_head:
        fail("TARGET_HEAD_MOVED")

    try:
        issue = api(
            target_token,
            "GET",
            f"/repos/{args.target_repository}/issues/{args.target_issue}",
        )
    except RuntimeError:
        fail("TARGET_ISSUE_READ_FAILED")
    try:
        state = decode_state(issue.get("body"))
    except (RuntimeError, ValueError, json.JSONDecodeError):
        fail("TARGET_LOCAL_STATE_DECODE_FAILED")
    if state.get("repository") != args.target_repository:
        fail("LOCAL_ENTRY_REPOSITORY_MISMATCH")
    if state.get("expected_head_sha") != args.expected_head:
        fail("LOCAL_STATE_HEAD_MOVED")

    try:
        credential_required = validate_requirements(state)
    except RuntimeError:
        fail("TARGET_CREDENTIAL_GATE_CONTRACT_INVALID")

    if not credential_required:
        emit_output("failure_code", "NONE")
        print(json.dumps({
            "status": "MCP_CREDENTIAL_PROVISION_NOT_REQUIRED",
            "target_repository": args.target_repository,
            "target_issue": args.target_issue,
            "expected_head": args.expected_head,
        }))
        return

    source_secret = os.environ.get(SECRET_NAME)
    if not source_secret:
        transport=(state.get("answers") or {}).get("mcp_transport")
        if transport=="BOTH":
            emit_output("failure_code", "NONE")
            emit_output("provisioning_status", "DEFERRED_TO_SSH_FALLBACK")
            print(json.dumps({
                "status": "MCP_CREDENTIAL_PROVISION_DEFERRED",
                "reason": "CONTROL_PLANE_MCP_AUTH_TOKEN_MISSING",
                "fallback": "SSH_OIDC_READONLY",
                "target_repository": args.target_repository,
                "target_issue": args.target_issue,
                "expected_head": args.expected_head,
                "secret_value_exposed": False,
            }))
            return
        fail("CONTROL_PLANE_MCP_AUTH_TOKEN_MISSING")

    try:
        set_repository_secret(target_token, args.target_repository, source_secret)
    except RuntimeError:
        fail("TARGET_MCP_SECRET_WRITE_FAILED")

    try:
        metadata = api(
            target_token,
            "GET",
            f"/repos/{args.target_repository}/actions/secrets/{SECRET_NAME}",
        )
    except RuntimeError:
        fail("TARGET_MCP_SECRET_ATTESTATION_READ_FAILED")
    if metadata.get("name") != SECRET_NAME:
        fail("MCP_CREDENTIAL_PROVISION_ATTESTATION_FAILED")

    emit_output("failure_code", "NONE")
    emit_output("provisioning_status", "PROVISIONED")
    print(json.dumps({
        "status": "MCP_CREDENTIAL_PROVISIONED",
        "target_repository": args.target_repository,
        "target_issue": args.target_issue,
        "expected_head": args.expected_head,
        "secret_name": SECRET_NAME,
        "secret_value_exposed": False,
    }))


if __name__ == "__main__":
    main()
