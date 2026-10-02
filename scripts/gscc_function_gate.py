#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from gscc.protocol import MessageEnvelope, assert_secretless, canonical_json

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / ".governance" / "control-plane-state" / "mcp-capability-snapshot.json"

ROUTE_STEPS = [
    "GSCC_ATTACH_OR_RESUME",
    "FUNCTION_CONTRACT_ATTEST",
    "CONTEXT_BIND",
    "CAPABILITY_MATCH",
    "AUTHORITY_CLASSIFY",
    "CLAIM_COLLISION_CHECK",
    "EXACT_HEAD_CHECK",
    "PREFLIGHT",
    "INVOCATION_GATE",
    "EXECUTE_IF_SEPARATELY_AUTHORIZED",
    "VERIFY",
    "VALIDATION_RECEIPT",
]

MCP_PHASES = ("preflight", "execute", "verify", "rollback")
KNOWN_SURFACES = {"read", "operational-write", "scoped-write"}
KNOWN_AUTHORITY_CLASSES = {
    "READ_ONLY_DISCOVERY_AUTHORITY",
    "GOVERNED_OPERATIONAL_AUTHORITY_REQUIRED",
    "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
}


class FunctionGateError(RuntimeError):
    def __init__(self, code: str, detail: str | None = None):
        super().__init__(code if detail is None else f"{code}:{detail}")
        self.code = code
        self.detail = detail


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FunctionGateError("JSON_OBJECT_REQUIRED", str(path))
    return value


def _digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _tool_index(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tools = (((snapshot.get("catalogue") or {}).get("tools")) or [])
    return {
        str(item["name"]): item
        for item in tools
        if isinstance(item, dict) and item.get("name")
    }


def _capabilities_for_tool(snapshot: dict[str, Any], function_name: str) -> list[str]:
    result: list[str] = []
    for capability, spec in (snapshot.get("capability_map") or {}).items():
        if not isinstance(spec, dict):
            continue
        for candidate in spec.get("candidate_tools") or []:
            if isinstance(candidate, dict) and candidate.get("tool") == function_name:
                result.append(str(capability))
                break
    return sorted(set(result))


def _project_scope(snapshot: dict[str, Any], function_name: str) -> dict[str, Any]:
    for spec in (snapshot.get("capability_map") or {}).values():
        if not isinstance(spec, dict):
            continue
        for candidate in spec.get("candidate_tools") or []:
            if isinstance(candidate, dict) and candidate.get("tool") == function_name:
                scope = candidate.get("scope")
                if isinstance(scope, dict):
                    return dict(scope)
    return {"mode": "UNAVAILABLE", "project_ids": []}


def _require_tool(snapshot: dict[str, Any], function_name: str) -> dict[str, Any]:
    tool = _tool_index(snapshot).get(function_name)
    if not tool:
        raise FunctionGateError("FUNCTION_NOT_IN_CANONICAL_CATALOGUE", function_name)
    digest = tool.get("contract_digest")
    if not isinstance(digest, str) or len(digest) < 32:
        raise FunctionGateError("FUNCTION_CONTRACT_DIGEST_UNAVAILABLE", function_name)
    surface = tool.get("surface")
    if surface not in KNOWN_SURFACES:
        raise FunctionGateError("FUNCTION_SURFACE_UNCLASSIFIED", function_name)
    authority = tool.get("authority_required")
    if authority not in KNOWN_AUTHORITY_CLASSES:
        raise FunctionGateError("FUNCTION_AUTHORITY_UNCLASSIFIED", function_name)
    return tool


def build_function_envelope(
    *,
    snapshot: dict[str, Any],
    function_name: str,
    repository: str,
    source_head: str,
    operation_id: str | None = None,
    intent: str | None = None,
    capability: str | None = None,
    phase: str | None = None,
    arguments: dict[str, Any] | None = None,
    session_id: str | None = None,
    connection_ref: str | None = None,
) -> dict[str, Any]:
    tool = _require_tool(snapshot, function_name)
    arguments = dict(arguments or {})
    # Values remain opaque. GSCC gets the contract, field names and a digest
    # sufficient for correlation/idempotence, never raw argument values.
    value_digest = _digest(arguments)
    envelope = {
        "schema": "gscc-function-envelope/v1",
        "repository": repository,
        "source_head": source_head,
        "function_name": function_name,
        "contract_digest": tool["contract_digest"],
        "surface": tool["surface"],
        "authority_required": tool["authority_required"],
        "read_only_hint": tool.get("read_only_hint"),
        "destructive_hint": tool.get("destructive_hint"),
        "input_fields": tool.get("input_fields") or [],
        "catalogue_tags": tool.get("tags") or [],
        "catalogue_capabilities": _capabilities_for_tool(snapshot, function_name),
        "project_scope": _project_scope(snapshot, function_name),
        "operation_id": operation_id,
        "intent": intent,
        "capability": capability,
        "phase": phase,
        "argument_keys": sorted(str(key) for key in arguments),
        "argument_value_digest": value_digest,
        "session_id": session_id,
        "connection_ref": connection_ref,
        "snapshot_authority_id": snapshot.get("authority_id"),
        "snapshot_observed_at": snapshot.get("observed_at"),
        "snapshot_catalogue_digest": ((snapshot.get("catalogue") or {}).get("catalogue_digest")),
        "governed_exposure_gate": tool.get("governed_exposure_gate") or "GSCC_REQUIRED",
        "governed_exposure_status": tool.get("governed_exposure_status") or "REQUIRES_RUNTIME_VALIDATION",
    }
    envelope = {key: value for key, value in envelope.items() if value not in (None, "", [])}
    assert_secretless(envelope)
    return envelope


def route_for_function(envelope: dict[str, Any]) -> dict[str, Any]:
    assert_secretless(envelope)
    return {
        "schema": "gscc-function-route/v1",
        "function_name": envelope["function_name"],
        "contract_digest": envelope["contract_digest"],
        "source_head": envelope["source_head"],
        "steps": list(ROUTE_STEPS),
        "current_step": "GSCC_ATTACH_OR_RESUME",
        "terminal_success_step": "VALIDATION_RECEIPT",
        "fail_closed": True,
        "gscc_required_for_every_invocation": True,
        "exposure_validation_is_invocation_authority": False,
        "exposure_validation_is_mutation_authority": False,
        "mutation_authority_granted": False,
        "invocation_authority_granted": False,
    }


def validate_exposure(
    *,
    snapshot: dict[str, Any],
    function_name: str,
    repository: str,
    source_head: str,
    expected_contract_digest: str | None = None,
) -> dict[str, Any]:
    tool = _require_tool(snapshot, function_name)
    if expected_contract_digest and tool["contract_digest"] != expected_contract_digest:
        raise FunctionGateError(
            "FUNCTION_CONTRACT_MOVED",
            f"{function_name}:expected={expected_contract_digest}:observed={tool['contract_digest']}",
        )
    envelope = build_function_envelope(
        snapshot=snapshot,
        function_name=function_name,
        repository=repository,
        source_head=source_head,
    )
    route = route_for_function(envelope)
    base = {
        "schema": "gscc-function-validation-receipt/v1",
        "status": "VALIDATED_FOR_GOVERNED_EXPOSURE",
        "repository": repository,
        "source_head": source_head,
        "function_name": function_name,
        "contract_digest": tool["contract_digest"],
        "surface": tool["surface"],
        "authority_required": tool["authority_required"],
        "route": route,
        "gscc_required_for_every_invocation": True,
        "workflow_required": True,
        "mutation_authority_granted": False,
        "invocation_authority_granted": False,
        "sensitive_values_persisted": False,
    }
    base["validation_digest"] = _digest(base)
    return base


def _package_steps(package: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    steps = (((package.get("bindings") or {}).get("steps")) or {})
    result: list[tuple[str, dict[str, Any]]] = []
    for phase in MCP_PHASES:
        for raw in steps.get(phase) or []:
            if not isinstance(raw, dict):
                continue
            if raw.get("backend", "MCP_DIRECT") != "MCP_DIRECT":
                continue
            if raw.get("tool"):
                result.append((phase, raw))
    return result


def validate_package(
    *,
    snapshot: dict[str, Any],
    package: dict[str, Any],
    repository: str,
    source_head: str,
    session_id: str | None = None,
    connection_ref: str | None = None,
) -> dict[str, Any]:
    functions: dict[str, dict[str, Any]] = {}
    invocations: list[dict[str, Any]] = []
    for phase, step in _package_steps(package):
        function_name = str(step["tool"])
        receipt = validate_exposure(
            snapshot=snapshot,
            function_name=function_name,
            repository=repository,
            source_head=source_head,
        )
        functions.setdefault(function_name, receipt)
        envelope = build_function_envelope(
            snapshot=snapshot,
            function_name=function_name,
            repository=repository,
            source_head=source_head,
            operation_id=package.get("operation_id"),
            intent=package.get("intent"),
            capability=step.get("capability"),
            phase=phase,
            arguments=step.get("arguments") if isinstance(step.get("arguments"), dict) else {},
            session_id=session_id,
            connection_ref=connection_ref,
        )
        invocations.append({
            "phase": phase,
            "function_name": function_name,
            "envelope": envelope,
            "route": route_for_function(envelope),
        })

    receipt = {
        "schema": "gscc-package-function-gate/v1",
        "status": "GSCC_FUNCTION_PATH_VALIDATED",
        "repository": repository,
        "source_head": source_head,
        "operation_id": package.get("operation_id"),
        "intent": package.get("intent"),
        "functions": sorted(functions),
        "function_count": len(functions),
        "invocation_count": len(invocations),
        "invocations": invocations,
        "route_complete": all(item["route"]["steps"][-1] == "VALIDATION_RECEIPT" for item in invocations),
        "workflow_required": True,
        "gscc_required_for_every_invocation": True,
        "mutation_authority_granted": False,
        "invocation_authority_granted": False,
        "sensitive_values_persisted": False,
    }
    receipt["validation_digest"] = _digest(receipt)
    return receipt


def gscc_context_event(
    receipt: dict[str, Any],
    *,
    source: dict[str, Any],
    target: dict[str, Any],
) -> MessageEnvelope:
    payload = {
        "function_gate": receipt,
        "route_owner": "GSCC",
        "mutation_authority_granted": False,
        "invocation_authority_granted": False,
    }
    return MessageEnvelope.create(
        kind="EVENT",
        type="CONTEXT_UPDATE",
        source=source,
        target=target,
        scope={
            "repository": receipt.get("repository"),
            "observed_head": receipt.get("source_head"),
            "operation_id": receipt.get("operation_id"),
        },
        payload=payload,
        requires_ack=True,
    )


def _git_head() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise FunctionGateError("SOURCE_HEAD_UNAVAILABLE")
    return proc.stdout.strip()


def _emit_output(name: str, value: Any) -> None:
    text = str(value).lower() if isinstance(value, bool) else str(value)
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"{name}={text}\n")
    else:
        print(f"{name}={text}")


def _write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="GSCC universal function exposure/invocation gate")
    sub = parser.add_subparsers(dest="mode", required=True)

    pkg = sub.add_parser("package")
    pkg.add_argument("--package", required=True)
    pkg.add_argument("--repository", required=True)
    pkg.add_argument("--expected-source-head", required=True)
    pkg.add_argument("--snapshot", default=str(SNAPSHOT_PATH))
    pkg.add_argument("--receipt", required=True)
    pkg.add_argument("--session-id")
    pkg.add_argument("--connection-ref")

    fn = sub.add_parser("function")
    fn.add_argument("--function-name", required=True)
    fn.add_argument("--repository", required=True)
    fn.add_argument("--expected-source-head", required=True)
    fn.add_argument("--expected-contract-digest")
    fn.add_argument("--snapshot", default=str(SNAPSHOT_PATH))
    fn.add_argument("--receipt", required=True)

    args = parser.parse_args()
    actual = _git_head()
    if actual != args.expected_source_head:
        raise SystemExit(f"GSCC_FUNCTION_GATE_HEAD_MOVED:expected={args.expected_source_head}:actual={actual}")

    snapshot = load_json(Path(args.snapshot))
    if args.mode == "package":
        package = load_json(Path(args.package))
        receipt = validate_package(
            snapshot=snapshot,
            package=package,
            repository=args.repository,
            source_head=actual,
            session_id=args.session_id,
            connection_ref=args.connection_ref,
        )
    else:
        receipt = validate_exposure(
            snapshot=snapshot,
            function_name=args.function_name,
            repository=args.repository,
            source_head=actual,
            expected_contract_digest=args.expected_contract_digest,
        )

    assert_secretless(receipt)
    _write_receipt(Path(args.receipt), receipt)
    _emit_output("validated", True)
    _emit_output("status", receipt["status"])
    _emit_output("validation_digest", receipt["validation_digest"])
    _emit_output("function_count", receipt.get("function_count", 1))
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()