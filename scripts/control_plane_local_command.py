#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import urllib.error
import urllib.request

CENTRAL = "chainsolutions-wealthtech/Governed-Repository-Template"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def gh(method: str, path: str, payload: dict | None = None) -> dict:
    token = os.environ["GOVERNED_TARGET_TOKEN"]
    request = urllib.request.Request(
        "https://api.github.com" + path,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "governed-machine-local-command",
        },
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {path} failed: {exc.code} {body}") from exc


def decode_command(value: str) -> dict:
    padded = value + "=" * ((4 - len(value) % 4) % 4)
    command = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))
    if not isinstance(command, dict) or command.get("kind") not in {"execute", "answer"}:
        raise ValueError("invalid local command")
    if command["kind"] == "execute" and set(command) != {"kind"}:
        raise ValueError("execute command must contain only kind")
    if command["kind"] == "answer" and set(command) != {"kind", "field", "value"}:
        raise ValueError("answer command must contain kind, field and value")
    return command


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-repository", required=True)
    parser.add_argument("--target-issue", required=True, type=int)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--command-b64", required=True)
    parser.add_argument("--source-issue", required=True, type=int)
    args = parser.parse_args()

    if "/" not in args.target_repository:
        raise SystemExit("LOCAL_COMMAND_TARGET_INVALID")
    if args.target_issue < 1 or args.source_issue < 1:
        raise SystemExit("LOCAL_COMMAND_ISSUE_INVALID")
    if not SHA_RE.fullmatch(args.expected_head):
        raise SystemExit("LOCAL_COMMAND_EXPECTED_HEAD_INVALID")

    command = decode_command(args.command_b64)
    repo = gh("GET", f"/repos/{args.target_repository}")
    branch = repo.get("default_branch") or "main"
    ref = gh("GET", f"/repos/{args.target_repository}/git/ref/heads/{branch}")
    remote_head = ref["object"]["sha"]
    if remote_head != args.expected_head:
        raise SystemExit(f"HEAD_MOVED: expected={args.expected_head} remote={remote_head}")

    gh(
        "POST",
        f"/repos/{args.target_repository}/dispatches",
        {
            "event_type": "governed_local_command",
            "client_payload": {
                "source_repository": CENTRAL,
                "source_issue": args.source_issue,
                "issue_number": args.target_issue,
                "expected_head": args.expected_head,
                "command": command,
            },
        },
    )
    print(json.dumps({
        "status": "GOVERNED_LOCAL_COMMAND_DISPATCHED",
        "target_repository": args.target_repository,
        "target_issue": args.target_issue,
        "expected_head": args.expected_head,
        "command_kind": command["kind"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
