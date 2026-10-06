#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_SCRIPT = ROOT / "scripts" / "first_touch_expected_field_registry.py"
REGISTRY_PATH = ROOT / ".governance" / "control-plane-state" / "first-touch-expected-field-registry.json"


def load_registry_module():
    spec = importlib.util.spec_from_file_location("first_touch_expected_field_registry", REGISTRY_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _norm(value: str) -> str:
    value = value.strip().strip(chr(96))
    value = re.sub(r"[^A-Za-z0-9_.:/-]+", "_", value)
    return value.strip("_").lower()


def _walk(value: Any, path: str = "$"):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path != "$" else f"$.{key}"
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _capture_index(capture: dict[str, Any]) -> tuple[dict[str, list[tuple[str, Any]]], int]:
    index: dict[str, list[tuple[str, Any]]] = defaultdict(list)
    terminal_count = 0
    for path, value in _walk(capture):
        if isinstance(value, (dict, list)):
            continue
        terminal_count += 1
        full = _norm(path.removeprefix("$."))
        leaf = re.sub(r"\[\d+\]$", "", path.rsplit(".", 1)[-1])
        leaf = _norm(leaf)
        if full:
            index[full].append((path, value))
        if leaf:
            index[leaf].append((path, value))

    aliases = {
        "repository": ["repository", "github_event.repository.full_name", "api_attempts.response.full_name"],
        "repository_id": ["github_event.repository.id", "api_attempts.response.id", "environment.github_repository_id"],
        "repository_node_id": ["github_event.repository.node_id", "api_attempts.response.node_id"],
        "organization": ["github_event.repository.owner.login", "environment.github_repository_owner"],
        "organization_id": ["github_event.repository.owner.id", "environment.github_repository_owner_id"],
        "authenticated_github_actor": ["actor", "github_event.sender.login", "environment.github_actor"],
        "authenticated_github_actor_id": ["github_event.sender.id", "environment.github_actor_id"],
        "github_actor": ["actor", "github_event.sender.login", "environment.github_actor"],
        "github_actor_id": ["github_event.sender.id", "environment.github_actor_id"],
        "default_branch": ["github_event.repository.default_branch", "api_attempts.response.default_branch"],
        "first_touch_observed_head": ["environment.github_sha"],
        "head": ["environment.github_sha"],
        "branch": ["environment.github_ref_name", "environment.github_head_ref"],
        "event_type": ["environment.github_event_name", "subject.event_name"],
        "workflow_run_id": ["environment.github_run_id"],
        "run_attempt": ["environment.github_run_attempt"],
        "job_id": ["environment.github_job"],
        "issue_number": ["subject.issue_number", "github_event.issue.number"],
        "pull_request_number": ["subject.pull_request_number", "github_event.pull_request.number"],
        "github_installation_id": ["github_event.installation.id"],
        "installation_id": ["github_event.installation.id"],
    }
    for target, sources in aliases.items():
        for source in sources:
            for item in index.get(_norm(source), []):
                index[_norm(target)].append(item)
    return index, terminal_count


def _match_capture_field(field_id: str, index: dict[str, list[tuple[str, Any]]]):
    candidates = [
        _norm(field_id),
        _norm(field_id.split(".")[-1]),
        _norm(field_id.replace("github.", "")),
        _norm(field_id.replace("repository.", "")),
        _norm(field_id.replace("git.", "")),
        _norm(field_id.replace("workflow.", "")),
    ]
    for candidate in candidates:
        values = index.get(candidate)
        if values:
            path, value = values[0]
            if value is None:
                return {"status": "UNAVAILABLE", "value": None, "source": f"first-touch-capture:{path}"}
            rendered = str(value).upper()
            if rendered in {"UNAVAILABLE", "UNKNOWN", "NOT_EXPOSED", "NOT EXPOSED", "NOT PROVEN"}:
                return {"status": "UNAVAILABLE" if "UNAVAILABLE" in rendered else "UNKNOWN", "value": value, "source": f"first-touch-capture:{path}"}
            return {"status": "OBSERVED", "value": value, "source": f"first-touch-capture:{path}"}
    return None


def build_packet(observation_path: Path | None, output_path: Path, *, capture_path: Path | None = None):
    if not REGISTRY_PATH.exists():
        mod = load_registry_module()
        mod.main()
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    observed: dict[str, Any] = {}
    current: dict[str, Any] = {}
    if observation_path is not None:
        observed = json.loads(observation_path.read_text(encoding="utf-8"))
        current = observed.get("fields", {})

    capture: dict[str, Any] = {}
    capture_index: dict[str, list[tuple[str, Any]]] = {}
    capture_terminal_count = 0
    if capture_path is not None:
        capture = json.loads(capture_path.read_text(encoding="utf-8"))
        capture_index, capture_terminal_count = _capture_index(capture)

    rows=[]
    for expected in registry["expected_observations"]:
        field_id=expected["field_id"]
        live=current.get(field_id)
        if live is None and capture_index:
            live = _match_capture_field(field_id, capture_index)
        if live:
            status=live["status"]
            value=live.get("value")
            source=live.get("source")
        elif expected["source_kind"]=="TOOL_SCHEMA":
            status="SCHEMA_AVAILABLE"
            value=None
            source=expected["source_path"]
        elif expected["source_kind"]=="PROBE_REFERENCE":
            status="REFERENCE_ONLY"
            value=None
            source=expected["source_path"]
        else:
            status="UNKNOWN"
            value=None
            source="NO_LIVE_VALUE_OBSERVED"
        rows.append({
            **expected,
            "status":status,
            "value":value,
            "evidence_source":source,
        })

    # Every terminal node from the actual First Touch capture is also preserved
    # as live observed evidence even if it has no historical registry alias yet.
    capture_rows=[]
    if capture:
        for path, value in _walk(capture):
            if isinstance(value, (dict, list)):
                continue
            capture_rows.append({
                "observation_id": f"capture:{path}",
                "field_id": _norm(path.removeprefix("$.")),
                "source_kind": "LIVE_CAPTURE_NODE",
                "source_path": str(capture_path),
                "source_line": None,
                "status": "OBSERVED" if value is not None else "UNAVAILABLE",
                "value": value,
                "evidence_source": f"first-touch-capture:{path}",
            })

    counts=Counter(row["status"] for row in rows)
    silent=[row for row in rows if not row.get("status")]
    packet={
        "schema":"first-touch-connection-completeness/v1",
        "capture_id": capture.get("capture_id"),
        "source_comment_id":observed.get("source_comment_id"),
        "request_id":observed.get("request_id"),
        "correlation_id":observed.get("correlation_id"),
        "connection_ref":observed.get("connection_ref"),
        "expected_observation_count":len(rows),
        "registry_field_count":registry["field_count"],
        "capture_terminal_value_count":capture_terminal_count,
        "captured_live_node_count":len(capture_rows),
        "total_accounted_items":len(rows)+len(capture_rows),
        "status_counts":dict(sorted(counts.items())),
        "silent_missing_count":len(silent),
        "complete_accounting":len(silent)==0,
        "live_value_count":sum(1 for row in rows if row["status"]=="OBSERVED"),
        "explicit_unavailable_count":sum(1 for row in rows if row["status"]=="UNAVAILABLE"),
        "rows":rows,
        "live_capture_rows":capture_rows,
        "authority_granted":False,
    }
    output_path.write_text(json.dumps(packet,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    return packet


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--observation")
    p.add_argument("--capture")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    if not args.observation and not args.capture:
        p.error("one of --observation or --capture is required")
    packet=build_packet(
        Path(args.observation) if args.observation else None,
        Path(args.output),
        capture_path=Path(args.capture) if args.capture else None,
    )
    print(json.dumps({
        "status":"FIRST_TOUCH_CONNECTION_COMPLETENESS_BUILT",
        "expected_observation_count":packet["expected_observation_count"],
        "registry_field_count":packet["registry_field_count"],
        "capture_terminal_value_count":packet["capture_terminal_value_count"],
        "captured_live_node_count":packet["captured_live_node_count"],
        "total_accounted_items":packet["total_accounted_items"],
        "status_counts":packet["status_counts"],
        "silent_missing_count":packet["silent_missing_count"],
        "complete_accounting":packet["complete_accounting"],
    },indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
