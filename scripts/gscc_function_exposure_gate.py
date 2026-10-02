#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gscc.entry_gate import validate_entry_context_receipt
from gscc_observable_arrival import build_github_arrival_facts, should_skip_github_arrival

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SNAPSHOT = ROOT / ".governance" / "control-plane-state" / "mcp-capability-snapshot.json"
DEFAULT_SESSIONS = ROOT / ".governance" / "control-plane-state" / "gacr-sessions.json"

GSCC_CONNECTION_METHODS = {
    "gscc-github-event-gateway",
    "gscc-controlled-host-gateway",
}
CONTROLLED_SURFACES = {
    "GITHUB_EVENT_VISIBLE",
    "CONTROLLED_INSTRUMENTABLE",
}
ROUTE_STAGES = [
    "GSCC_ENTRY_CONTEXT",
    "GSCC_SESSION_BIND",
    "CONNECTION_ENVELOPE",
    "EXACT_HEAD_OBSERVATION",
    "ENTRY_ACTION_RESOLUTION",
    "CAPABILITY_SNAPSHOT_LOAD",
    "FUNCTION_CONTRACT_MATCH",
    "AUTHORITY_VALIDATION",
    "LIVE_PREFLIGHT_IF_REQUIRED",
    "EXPOSURE_RECEIPT",
    "PRE_CALL_REVALIDATION",
]
SECRETISH_KEYS = {
    "secret",
    "password",
    "token",
    "private_key",
    "authorization",
    "authorization_header",
    "cookie",
    "raw_prompt",
    "raw_transcript",
    "chain_of_thought",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON object required: {path}")
    return data


def _safe_evidence(value: Any) -> None:
    if value is None:
        return
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).lower()
            if any(part in lowered for part in SECRETISH_KEYS):