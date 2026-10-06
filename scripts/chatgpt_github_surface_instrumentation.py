#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Mapping

from gscc.instrumentation import instrument_tool
from gscc.session_endpoint import SessionEndpoint

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SURFACE_SNAPSHOT = (
    ROOT / ".governance" / "control-plane-state" / "chatgpt-github-tool-schema-snapshot.json"
)
PLUGIN_PREFIX = "mcp__GitHub__"


def canonical_github_tool_names(snapshot_path: str | Path = DEFAULT_SURFACE_SNAPSHOT) -> list[str]:
    payload = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
    if payload.get("schema") != "chatgpt-github-tool-schema-snapshot/v1":
        raise ValueError("unsupported ChatGPT GitHub tool snapshot schema")
    names = sorted(
        {
            str(row.get("tool"))
            for row in payload.get("fields") or []
            if isinstance(row, dict) and row.get("tool")
        }
    )
    declared = payload.get("github_tool_count")
    if isinstance(declared, int) and declared != len(names):
        raise ValueError(
            f"GitHub tool snapshot count mismatch: declared={declared} observed={len(names)}"
        )
    return names


def instrument_github_plugin_surface(
    endpoint: SessionEndpoint,
    tool_functions: Mapping[str, Callable[..., Any]],
    *,
    before_tool_call: Callable[[str], dict[str, Any] | None] | None = None,
    exposure_guard: Callable[[str], dict[str, Any]] | None = None,
    snapshot_path: str | Path = DEFAULT_SURFACE_SNAPSHOT,
    require_complete_surface: bool = True,
) -> dict[str, Callable[..., Any]]:
    """Instrument the complete ChatGPT GitHub plugin tool surface.

    The runtime may expose keys either as short names (get_repo) or as the
    provider-visible names (mcp__GitHub__get_repo). Returned keys preserve the
    supplied runtime mapping. Every wrapped call uses the provider-visible name
    for GSCC lifecycle evidence and the shared before_tool_call First Touch hook.
    """
    expected = canonical_github_tool_names(snapshot_path)
    wrapped: dict[str, Callable[..., Any]] = {}
    missing: list[str] = []

    for short_name in expected:
        full_name = f"{PLUGIN_PREFIX}{short_name}"
        runtime_key: str | None = None
        if full_name in tool_functions:
            runtime_key = full_name
        elif short_name in tool_functions:
            runtime_key = short_name

        if runtime_key is None:
            missing.append(short_name)
            continue

        fn = tool_functions[runtime_key]
        wrapped[runtime_key] = instrument_tool(
            endpoint,
            full_name,
            fn,
            before_tool_call=before_tool_call,
            exposure_guard=exposure_guard,
        )

    if require_complete_surface and missing:
        raise ValueError(
            "ChatGPT GitHub plugin surface incomplete: " + ",".join(missing)
        )

    return wrapped
