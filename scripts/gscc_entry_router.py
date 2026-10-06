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


def route(current: str, outcome: str | None = None, *, path: Path = ROUTER_PATH) -> dict[str, Any]:
    router = load_router(path)
    step = next((row for row in router["routes"] if row["current"] == current), None)
    if step is None:
        raise ValueError(f"unknown GSCC entry router current step: {current}")

    if outcome is None:
        next_step = step.get("next_step")
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
    args = parser.parse_args()
    print(json.dumps(route(args.current, args.outcome), indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
