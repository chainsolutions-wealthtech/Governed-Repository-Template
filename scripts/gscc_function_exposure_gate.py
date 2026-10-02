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
                raise ValueError(f"unsafe evidence key: {key}")
            _safe_evidence(item)
    elif isinstance(value, list):
        for item in value:
            _safe_evidence(item)
    elif isinstance(value, str):
        lower = value.lower()
        if "bearer " in lower or "-----begin private key-----" in lower:
            raise ValueError("unsafe secret-like evidence value")


def _digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_arrival_route(
    *,
    repository: str,
    connection_ref: str,
    surface_class: str,
    observed_head: str | None,
) -> dict[str, Any]:
    return {
        "schema": "gscc-function-exposure-route/v1",
        "status": "LOCKED_PENDING_FUNCTION_REQUEST",
        "repository": repository,
        "connection_ref": connection_ref,
        "surface_class": surface_class,
        "observed_head": observed_head,
        "first_stage": ROUTE_STAGES[0],
        "required_stages": list(ROUTE_STAGES),
        "exposure_policy": "NOT_EXPOSED_UNTIL_VALIDATED",
        "mutation_authority_granted": False,
    }


def _tool(snapshot: dict[str, Any], tool_name: str) -> dict[str, Any] | None:
    if snapshot.get("status") != "CURRENT":
        return None
    catalogue = snapshot.get("catalogue") or {}
    if catalogue.get("status") != "CURRENT":
        return None
    for item in catalogue.get("tools") or []:
        if isinstance(item, dict) and item.get("name") == tool_name:
            return item
    return None


def _active_session(
    sessions: dict[str, Any],
    connection_ref: str,
    *,
    now: datetime,
) -> dict[str, Any] | None:
    matches: list[dict[str, Any]] = []
    for item in sessions.get("sessions") or []:
        if not isinstance(item, dict):
            continue
        if item.get("connection_ref") != connection_ref:
            continue
        if item.get("status") != "ACTIVE":
            continue
        if item.get("connection_method") not in GSCC_CONNECTION_METHODS:
            continue
        if item.get("surface_class") not in CONTROLLED_SURFACES:
            continue
        relay = item.get("relay") or {}
        if relay.get("state") != "ACTIVE":
            continue
        expiry = _parse_dt(relay.get("lease_expires_at"))
        if expiry is None or expiry <= now:
            continue
        matches.append(item)
    if len(matches) != 1:
        return None
    return matches[0]


def _base_receipt(
    *,
    tool_name: str,
    connection_ref: str,
    requested_head: str | None,
    tool: dict[str, Any] | None,
    session: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "schema": "gscc-function-exposure-receipt/v1",
        "tool_name": tool_name,
        "connection_ref": connection_ref,
        "requested_head": requested_head,
        "session_id": session.get("session_id") if session else None,
        "surface_class": session.get("surface_class") if session else None,
        "connection_method": session.get("connection_method") if session else None,
        "contract_digest": tool.get("contract_digest") if tool else None,
        "surface": tool.get("surface") if tool else None,
        "authority_required": tool.get("authority_required") if tool else None,
        "route": list(ROUTE_STAGES),
        "exposable": False,
        "mutation_authority_granted": False,
    }


def evaluate_function_exposure(
    *,
    tool_name: str,
    connection_ref: str,
    requested_head: str | None,
    authority_evidence: dict[str, Any] | None,
    snapshot: dict[str, Any],
    sessions: dict[str, Any],
    now: datetime | None = None,
) -> dict[str, Any]:
    now = (now or _now()).astimezone(timezone.utc)
    _safe_evidence(authority_evidence)

    tool = _tool(snapshot, tool_name)
    session = _active_session(sessions, connection_ref, now=now)
    result = _base_receipt(
        tool_name=tool_name,
        connection_ref=connection_ref,
        requested_head=requested_head,
        tool=tool,
        session=session,
    )
    result["evaluated_at"] = now.isoformat()

    if tool is None:
        result.update(status="DENIED", reason_code="FUNCTION_NOT_IN_CANONICAL_CATALOGUE")
        return result

    if session is None:
        result.update(status="DENIED", reason_code="GSCC_BOUND_ACTIVE_SESSION_REQUIRED")
        return result

    session_head = session.get("last_observed_head_sha")
    if requested_head and session_head and requested_head != session_head:
        result.update(status="DENIED", reason_code="EXACT_HEAD_MISMATCH")
        return result
    if not requested_head or not session_head:
        result.update(status="WITHHELD", reason_code="EXACT_HEAD_REQUIRED")
        return result

    required = tool.get("authority_required")
    if not authority_evidence:
        result.update(status="WITHHELD", reason_code="AUTHORITY_EVIDENCE_REQUIRED")
        return result
    if authority_evidence.get("granted") is not True:
        result.update(status="WITHHELD", reason_code="AUTHORITY_NOT_GRANTED")
        return result
    if authority_evidence.get("authority_class") != required:
        result.update(status="DENIED", reason_code="AUTHORITY_CLASS_MISMATCH")
        return result
    if not authority_evidence.get("evidence_ref"):
        result.update(status="WITHHELD", reason_code="AUTHORITY_EVIDENCE_REF_REQUIRED")
        return result

    mutation_like = tool.get("surface") != "read"
    if mutation_like and (snapshot.get("refresh_policy") or {}).get("pre_mutation_live_refresh_required", True):
        preflight = authority_evidence.get("live_preflight")
        if not isinstance(preflight, dict) or preflight.get("status") != "PASSED":
            result.update(status="WITHHELD", reason_code="LIVE_PREFLIGHT_REQUIRED")
            return result
        if preflight.get("observed_head") != requested_head:
            result.update(status="DENIED", reason_code="LIVE_PREFLIGHT_HEAD_MISMATCH")
            return result
        if not preflight.get("evidence_ref"):
            result.update(status="WITHHELD", reason_code="LIVE_PREFLIGHT_EVIDENCE_REF_REQUIRED")
            return result

    receipt_material = {
        "schema": result["schema"],
        "tool_name": tool_name,
        "connection_ref": connection_ref,
        "session_id": session.get("session_id"),
        "requested_head": requested_head,
        "contract_digest": tool.get("contract_digest"),
        "authority_required": required,
        "authority_evidence_ref": authority_evidence.get("evidence_ref"),
        "live_preflight_evidence_ref": (authority_evidence.get("live_preflight") or {}).get("evidence_ref"),
        "evaluated_at": result["evaluated_at"],
    }
    result.update(
        status="VALIDATED",
        reason_code="EXPOSURE_VALIDATED",
        exposable=True,
        exposure_receipt=f"GSCC-EXPOSURE-{_digest(receipt_material)}",
        authority_evidence_ref=authority_evidence.get("evidence_ref"),
        live_preflight_evidence_ref=(authority_evidence.get("live_preflight") or {}).get("evidence_ref"),
    )
    return result


def exposed_function_catalogue(
    *,
    connection_ref: str,
    requested_head: str | None,
    authority_evidence_by_tool: dict[str, dict[str, Any]],
    snapshot: dict[str, Any],
    sessions: dict[str, Any],
    now: datetime | None = None,
) -> dict[str, Any]:
    functions = []
    withheld = []
    for item in (snapshot.get("catalogue") or {}).get("tools") or []:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        name = str(item["name"])
        receipt = evaluate_function_exposure(
            tool_name=name,
            connection_ref=connection_ref,
            requested_head=requested_head,
            authority_evidence=authority_evidence_by_tool.get(name),
            snapshot=snapshot,
            sessions=sessions,
            now=now,
        )
        if receipt.get("status") == "VALIDATED":
            functions.append({
                "name": name,
                "description": item.get("description"),
                "surface": item.get("surface"),
                "authority_required": item.get("authority_required"),
                "contract_digest": item.get("contract_digest"),
                "exposure_receipt": receipt.get("exposure_receipt"),
            })
        else:
            withheld.append({
                "name": name,
                "status": receipt.get("status"),
                "reason_code": receipt.get("reason_code"),
            })
    return {
        "schema": "gscc-exposed-function-catalogue/v1",
        "connection_ref": connection_ref,
        "requested_head": requested_head,
        "functions": functions,
        "withheld": withheld,
        "policy": "ONLY_VALIDATED_FUNCTIONS_ARE_PUBLISHABLE",
    }


def _argument_digest(arguments: dict[str, Any]) -> str:
    encoded = json.dumps(arguments, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _package_mcp_invocations(package: dict[str, Any]) -> list[dict[str, Any]]:
    bindings = package.get("bindings") or {}
    steps = bindings.get("steps") or {}
    result: list[dict[str, Any]] = []
    ordinal = 0
    for phase in ("preflight", "execute", "verify", "rollback"):
        items = steps.get(phase) or []
        if not isinstance(items, list):
            raise ValueError(f"PACKAGE_STEPS_INVALID:{phase}")
        for index, step in enumerate(items):
            if not isinstance(step, dict):
                raise ValueError(f"PACKAGE_STEP_INVALID:{phase}:{index}")
            if step.get("backend", "MCP_DIRECT") != "MCP_DIRECT":
                continue
            tool_name = step.get("tool")
            if not tool_name:
                continue
            ordinal += 1
            arguments = step.get("arguments") or {}
            if not isinstance(arguments, dict):
                raise ValueError(f"PACKAGE_ARGUMENTS_INVALID:{phase}:{index}")
            result.append({
                "ordinal": ordinal,
                "phase": phase,
                "phase_index": index,
                "tool_name": str(tool_name),
                "capability": step.get("capability"),
                "argument_keys": sorted(str(key) for key in arguments),
                "argument_value_digest": _argument_digest(arguments),
            })
    return result


def build_package_route_receipt(
    *,
    snapshot: dict[str, Any],
    package: dict[str, Any],
    repository: str,
    source_head: str,
) -> dict[str, Any]:
    invocations = _package_mcp_invocations(package)
    projected: list[dict[str, Any]] = []
    for invocation in invocations:
        tool = _tool(snapshot, invocation["tool_name"])
        if tool is None:
            raise ValueError(f"FUNCTION_NOT_IN_CANONICAL_CATALOGUE:{invocation['tool_name']}")
        if tool.get("governed_exposure_gate") != "GSCC_REQUIRED":
            raise ValueError(f"FUNCTION_GSCC_GATE_NOT_REQUIRED:{invocation['tool_name']}")
        if tool.get("governed_exposure_status") != "REQUIRES_RUNTIME_VALIDATION":
            raise ValueError(f"FUNCTION_EXPOSURE_STATUS_INVALID:{invocation['tool_name']}")
        if not tool.get("contract_digest"):
            raise ValueError(f"FUNCTION_CONTRACT_DIGEST_REQUIRED:{invocation['tool_name']}")
        projected.append({
            **invocation,
            "contract_digest": tool.get("contract_digest"),
            "surface": tool.get("surface"),
            "authority_required": tool.get("authority_required"),
            "route": list(ROUTE_STAGES),
            "exposure_receipt_required": True,
            "pre_call_revalidation_required": True,
        })

    receipt: dict[str, Any] = {
        "schema": "gscc-package-function-route/v1",
        "status": "GSCC_PACKAGE_ROUTE_VALIDATED",
        "repository": repository,
        "source_head": source_head,
        "operation_id": package.get("operation_id"),
        "intent": package.get("intent"),
        "required_stages": list(ROUTE_STAGES),
        "invocations": projected,
        "invocation_count": len(projected),
        "function_count": len({item["tool_name"] for item in projected}),
        "route_validation_only": True,
        "exposure_receipt_required_before_external_publication": True,
        "pre_call_revalidation_required": True,
        "mutation_authority_granted": False,
        "invocation_authority_granted": False,
        "catalogue_presence_is_exposure_authority": False,
    }
    _safe_evidence(receipt)
    receipt["validation_digest"] = _digest(receipt)
    return receipt


def _git_head() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("SOURCE_HEAD_UNAVAILABLE")
    return proc.stdout.strip()


def _github_output(name: str, value: Any) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    rendered = str(value).lower() if isinstance(value, bool) else str(value)
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(f"{name}={rendered}\n")


def _write_output(data: dict[str, Any], output: str | None) -> None:
    raw = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if output:
        Path(output).write_text(raw, encoding="utf-8")
    print(raw, end="")


def _event_payload(path: str) -> dict[str, Any]:
    value = _load_json(path)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="GSCC mandatory function exposure gate")
    sub = parser.add_subparsers(dest="command", required=True)

    arrival = sub.add_parser("arrival-plan")
    arrival.add_argument("--event-path", default=os.environ.get("GITHUB_EVENT_PATH"))
    arrival.add_argument("--output")

    package = sub.add_parser("package-evaluate")
    package.add_argument("--package", required=True)
    package.add_argument("--repository", required=True)
    package.add_argument("--expected-source-head", required=True)
    package.add_argument("--snapshot", default=str(DEFAULT_SNAPSHOT))
    package.add_argument("--output")

    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--tool-name", required=True)
    evaluate.add_argument("--connection-ref", required=True)
    evaluate.add_argument("--observed-head", required=True)
    evaluate.add_argument("--authority-class")
    evaluate.add_argument("--authority-evidence-ref")
    evaluate.add_argument("--authority-granted", action="store_true")
    evaluate.add_argument("--live-preflight-status")
    evaluate.add_argument("--live-preflight-head")
    evaluate.add_argument("--live-preflight-evidence-ref")
    evaluate.add_argument("--snapshot", default=str(DEFAULT_SNAPSHOT))
    evaluate.add_argument("--sessions", default=str(DEFAULT_SESSIONS))
    evaluate.add_argument("--output")
    evaluate.add_argument("--require-validated", action="store_true")

    args = parser.parse_args()

    if args.command == "package-evaluate":
        actual_head = _git_head()
        if actual_head != args.expected_source_head:
            raise SystemExit(
                f"GSCC_FUNCTION_ROUTE_HEAD_MOVED:expected={args.expected_source_head}:actual={actual_head}"
            )
        receipt = build_package_route_receipt(
            snapshot=_load_json(args.snapshot),
            package=_load_json(args.package),
            repository=args.repository,
            source_head=actual_head,
        )
        _write_output(receipt, args.output)
        _github_output("route_validated", True)
        _github_output("validation_digest", receipt["validation_digest"])
        _github_output("function_count", receipt["function_count"])
        _github_output("invocation_count", receipt["invocation_count"])
        return

    if args.command == "arrival-plan":
        if not args.event_path:
            raise SystemExit("GITHUB_EVENT_PATH_REQUIRED")
        event = _event_payload(args.event_path)
        env = dict(os.environ)
        skip = should_skip_github_arrival(event, env)
        if skip:
            _write_output({
                "schema": "gscc-function-exposure-route/v1",
                "status": "SKIPPED_INTERNAL_EVENT",
                "reason_code": skip,
                "exposure_policy": "NOT_EXPOSED",
            }, args.output)
            return
        facts = build_github_arrival_facts(event, env)
        route = build_arrival_route(
            repository=facts["repository"],
            connection_ref=facts["connection_ref"],
            surface_class=facts["surface_class"],
            observed_head=facts.get("observed_head"),
        )
        _write_output(route, args.output)
        return

    evidence = None
    if args.authority_class or args.authority_evidence_ref or args.authority_granted:
        evidence = {
            "authority_class": args.authority_class,
            "evidence_ref": args.authority_evidence_ref,
            "granted": bool(args.authority_granted),
        }
        if args.live_preflight_status or args.live_preflight_head or args.live_preflight_evidence_ref:
            evidence["live_preflight"] = {
                "status": args.live_preflight_status,
                "observed_head": args.live_preflight_head,
                "evidence_ref": args.live_preflight_evidence_ref,
            }

    result = evaluate_function_exposure(
        tool_name=args.tool_name,
        connection_ref=args.connection_ref,
        requested_head=args.observed_head,
        authority_evidence=evidence,
        snapshot=_load_json(args.snapshot),
        sessions=_load_json(args.sessions),
    )
    _write_output(result, args.output)
    if args.require_validated and result.get("status") != "VALIDATED":
        raise SystemExit(3)


if __name__ == "__main__":
    main()