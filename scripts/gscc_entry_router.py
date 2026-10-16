#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ROUTER_PATH = ROOT / ".governance" / "gscc-entry-router.json"


def load_router(path: Path = ROUTER_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "gscc-entry-router/v1":
        raise ValueError("unsupported GSCC entry router schema")
    return payload


def route(
    current: str, outcome: str | None = None, *,
    path: Path = ROUTER_PATH,
    entry_file: str | None = None,
    mission: str | None = None,
    read_github=None,
    expected_head: str | None = None,
) -> dict[str, Any]:
    # Explicit, authenticated Door B is selected before the existing GSCC
    # state machine; all ordinary/current callers remain on unchanged Door A.
    if current == "ARRIVAL" and entry_file == "00_DIRECT_OWNER_ENTRY.md":
        from repository_entry_router import select_entry
        return select_entry(
            entry_file, mission, read_github=read_github,
            expected_head=expected_head,
        )
    router = load_router(path)
    step = next((row for row in router["routes"] if row["current"] == current), None)
    if step is None:
        raise ValueError(f"unknown GSCC entry router current step: {current}")

    success_outcomes = step.get("success_outcomes") or {}
    failure_outcomes = step.get("failure_outcomes") or {}

    if outcome is None:
        next_step = step.get("next_step")
    elif outcome in success_outcomes:
        next_step = success_outcomes[outcome]
    elif outcome in failure_outcomes:
        next_step = failure_outcomes[outcome]
    elif outcome == step.get("success_outcome"):
        next_step = step.get("next_step")
    elif outcome == step.get("failure_outcome"):
        next_step = step.get("failure_step")
    else:
        next_step = step.get("failure_step") or "BLOCK_UNRESOLVED"

    return {
        "schema": "gscc-entry-route-decision/v1",
        "authority": router["authority"],
        "current": current,
        "action": step["action"],
        "target": step.get("target"),
        "observed_outcome": outcome,
        "next_step": next_step,
        "required": True,
        "fail_closed": bool(router.get("fail_closed", True)),
        "execute_next_automatically": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", required=True)
    parser.add_argument("--outcome")
    parser.add_argument("--entry-file")
    parser.add_argument("--mission")
    parser.add_argument("--expected-head")
    args = parser.parse_args()
    reader = None
    if args.entry_file == "00_DIRECT_OWNER_ENTRY.md":
        from repository_entry_router import github_reader
        import os
        token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
        if token:
            reader = github_reader(token)
    decision = route(
        args.current, args.outcome, entry_file=args.entry_file,
        mission=args.mission, read_github=reader,
        expected_head=args.expected_head,
    )
    print(json.dumps(decision, indent=2, ensure_ascii=False, sort_keys=True))
    if decision.get("entry") == "DIRECT" and decision.get("status") != "DIRECT_OWNER_VERIFIED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
