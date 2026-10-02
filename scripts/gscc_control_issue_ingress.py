#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / ".governance" / "agent-relay" / "config.json"
BRIDGE = ROOT / "scripts" / "gscc_gacr" / "issue_control_bridge.py"
PREFIX = "/gscc-control "
SCHEMA = "gscc-control-request/v1"
AUTHORIZED_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON object required")
    return value


def parse(event: dict, config: dict) -> dict | None:
    if event.get("action") != "created":
        return None
    bridge = config.get("host_issue_bridge") or {}
    issue = event.get("issue") or {}
    if int(issue.get("number") or 0) != int(bridge.get("issue_number") or 0):
        return None
    comment = event.get("comment") or {}
    body = str(comment.get("body") or "")
    if not body.startswith(PREFIX):
        return None
    association = str(comment.get("author_association") or "").upper()
    allowed = set(bridge.get("allowed_author_associations") or AUTHORIZED_ASSOCIATIONS)
    if association not in allowed:
        raise ValueError("unauthorized GSCC control request actor")
    payload = json.loads(body[len(PREFIX):].strip())
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        raise ValueError("unsupported GSCC control request schema")
    if payload.get("event") != "challenge_request":
        raise ValueError("unsupported GSCC control request event")
    if not payload.get("session_id"):
        raise ValueError("session_id is required")
    ttl = int(payload.get("ttl_seconds") or 60)
    if ttl < 1 or ttl > 300:
        raise ValueError("ttl_seconds out of bounds")
    return {"session_id": str(payload["session_id"]), "ttl_seconds": ttl}


def main() -> None:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise SystemExit("GSCC_CONTROL_ISSUE_INGRESS_FAILED: GITHUB_EVENT_PATH unavailable")
    event = read_json(Path(event_path))
    config = read_json(CONFIG_PATH)
    try:
        payload = parse(event, config)
        if payload is None:
            print(json.dumps({"status": "GSCC_CONTROL_REQUEST_IGNORED"}, indent=2))
            return
        cp = subprocess.run(
            [sys.executable, str(BRIDGE), "challenge", "--session-id", payload["session_id"], "--ttl-seconds", str(payload["ttl_seconds"])],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if cp.stdout:
            print(cp.stdout, end="")
        if cp.stderr:
            print(cp.stderr, file=sys.stderr, end="")
        if cp.returncode != 0:
            raise RuntimeError(f"issue_control_bridge.py failed with exit {cp.returncode}")
        output = os.environ.get("GITHUB_OUTPUT")
        if output:
            with open(output, "a", encoding="utf-8") as handle:
                handle.write("command=control-challenge\n")
    except Exception as exc:
        raise SystemExit(f"GSCC_CONTROL_ISSUE_INGRESS_FAILED: {exc}") from exc


if __name__ == "__main__":
    main()
