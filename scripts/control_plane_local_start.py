#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request

CENTRAL = "chainsolutions-wealthtech/Governed-Repository-Template"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

def gh(method: str, path: str, payload: dict | None = None) -> dict:
    token = os.environ["GOVERNED_TARGET_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com" + path,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "governed-machine-local-start",
        },
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw=r.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body=exc.read().decode("utf-8",errors="replace")
        raise RuntimeError(f"GitHub API {method} {path} failed: {exc.code} {body}") from exc

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--target-repository",required=True)
    p.add_argument("--expected-head",required=True)
    p.add_argument("--objective",required=True)
    p.add_argument("--source-issue",required=True,type=int)
    args=p.parse_args()
    if "/" not in args.target_repository:
        raise SystemExit("LOCAL_START_TARGET_INVALID")
    if not SHA_RE.fullmatch(args.expected_head):
        raise SystemExit("LOCAL_START_EXPECTED_HEAD_INVALID")
    if not args.objective.strip():
        raise SystemExit("LOCAL_START_OBJECTIVE_REQUIRED")
    info=gh("GET",f"/repos/{args.target_repository}")
    branch=info.get("default_branch") or "main"
    ref=gh("GET",f"/repos/{args.target_repository}/git/ref/heads/{branch}")
    remote=ref["object"]["sha"]
    if remote!=args.expected_head:
        raise SystemExit(f"HEAD_MOVED: expected={args.expected_head} remote={remote}")
    gh("POST",f"/repos/{args.target_repository}/dispatches",{
      "event_type":"governed_local_start",
      "client_payload":{
        "source_repository":CENTRAL,
        "source_issue":args.source_issue,
        "expected_head":args.expected_head,
        "objective":args.objective.strip()
      }
    })
    print(json.dumps({
      "status":"GOVERNED_LOCAL_START_DISPATCHED",
      "target_repository":args.target_repository,
      "expected_head":args.expected_head
    },ensure_ascii=False))

if __name__=="__main__":
    main()
