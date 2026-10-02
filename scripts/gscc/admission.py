from __future__ import annotations

import argparse
import copy
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ADMISSION_SCHEMA = "gscc-admission-envelope/v1"
RECEIPT_SCHEMA = "gscc-admission-receipt/v1"
UNAVAILABLE = "UNAVAILABLE"

FORBIDDEN_KEY_FRAGMENTS = (
    "password",
    "secret",
    "token",
    "private_key",
    "authorization",
    "cookie",
    "raw_prompt",
    "raw_transcript",
    "raw_response",
    "raw_tool_arguments",
    "raw_tool_results",
    "chain_of_thought",
    "private_reasoning",
)

REQUIRED_FIELDS = (
    "request.request_id",
    "request.correlation_id",
    "request.idempotency_key",
    "request.issued_at",
    "request.observed_at",
    "agent.agent_type",
    "agent.provider",
    "agent.requested_role",
    "client.client_instance_id",
    "client.client_type",
    "connection.connection_ref",
    "connection.connection_method",
    "connection.surface_class",
    "target.repository",
    "intent.entry_action",
    "intent.connection_intent",
    "intent.requested_capabilities",
    "control_capabilities",
)

QUALIFICATION_SURFACE = (
    "GET_ADMISSION_STATUS",
    "GET_REQUIRED_NEXT_STEP",
    "READ_REQUIRED_GOVERNANCE",
    "OBSERVE_REPOSITORY_BASELINE",
    "SUBMIT_ADMISSION_EVIDENCE",
    "RECEIVE_GSCC_COMMAND",
    "ACK_GSCC_COMMAND",
    "RESPOND_GSCC_CHALLENGE",
)


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _path_get(value: dict[str, Any], path: str) -> Any:
    current: Any = value
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _missing_fields(envelope: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for path in REQUIRED_FIELDS:
        value = _path_get(envelope, path)
        if value is None or value == "" or value == [] or value == {}:
            missing.append(path)
    return missing


def _forbidden_path(value: Any, path: str = "") -> str | None:
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in FORBIDDEN_KEY_FRAGMENTS):
                return f"{path}.{key}".lstrip(".")
            found = _forbidden_path(item, f"{path}.{key}".lstrip("."))
            if found:
                return found
        return None
    if isinstance(value, list):
        for index, item in enumerate(value):
            found = _forbidden_path(item, f"{path}[{index}]")
            if found:
                return found
        return None
    if isinstance(value, str):
        lowered = value.lower()
        if "bearer " in lowered or "-----begin private key-----" in lowered:
            return path or "value"
    return None


def _valid_repository(value: Any) -> bool:
    return isinstance(value, str) and value.count("/") == 1 and all(part.strip() for part in value.split("/", 1))


ADMISSION_CONTEXT_FIELDS = {
    "agent": ("agent_id", "agent_identity", "agent_type", "provider", "model_runtime", "requested_role"),
    "client": ("client_instance_id", "client_type", "client_version", "host_instance_id"),
    "session": ("provider_session_ref", "provider_conversation_ref", "conversation_ref", "started_at"),
    "connection": ("connection_ref", "connection_method", "surface_class", "bridge_registration_ref", "wake_channels"),
    "target": ("repository", "requested_branch"),
    "intent": ("entry_action", "connection_intent", "task_id", "requested_capabilities"),
    "continuity": ("claim_id", "checkpoint_ref", "last_action", "last_evidence"),
}
PROVIDER_PRIVATE_OPTIONAL = {
    "agent.agent_id", "agent.agent_identity", "agent.model_runtime",
    "session.provider_session_ref", "session.provider_conversation_ref", "session.conversation_ref",
}
HOST_OPTIONAL = {"client.client_version", "client.host_instance_id", "connection.bridge_registration_ref"}


def _safe_admission_context(envelope: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    request = envelope.get("request") if isinstance(envelope.get("request"), dict) else {}
    observed_at = request.get("observed_at")
    context: dict[str, Any] = {}
    provenance: dict[str, Any] = {}

    for section, fields in ADMISSION_CONTEXT_FIELDS.items():
        source = envelope.get(section) if isinstance(envelope.get(section), dict) else {}
        projected: dict[str, Any] = {}
        for field_name in fields:
            path = f"{section}.{field_name}"
            value = source.get(field_name)
            if value not in (None, "", [], {}):
                projected[field_name] = copy.deepcopy(value)
                provenance[path] = {
                    "value": copy.deepcopy(value),
                    "provenance": "DECLARED_BY_AGENT_OR_CLIENT",
                    "source": "HOST_POST",
                    "source_method": "POST",
                    "observed_at": observed_at,
                }
            else:
                reason = (
                    "NOT_EXPOSED_BY_PROVIDER" if path in PROVIDER_PRIVATE_OPTIONAL
                    else "NOT_EXPOSED_BY_HOST" if path in HOST_OPTIONAL
                    else "NOT_YET_DECLARED"
                )
                provenance[path] = {
                    "value": UNAVAILABLE,
                    "status": UNAVAILABLE,
                    "reason": reason,
                    "provenance": (
                        "PROVIDER_PRIVATE_UNAVAILABLE"
                        if path in PROVIDER_PRIVATE_OPTIONAL
                        else "DECLARED_BY_AGENT_OR_CLIENT"
                    ),
                    "source": "HOST_POST",
                    "source_method": "POST",
                    "observed_at": observed_at,
                }
        context[section] = projected

    controls = envelope.get("control_capabilities")
    if isinstance(controls, dict):
        context["control_capabilities"] = copy.deepcopy(controls)
        for name, value in controls.items():
            provenance[f"control_capabilities.{name}"] = {
                "value": bool(value),
                "provenance": "DECLARED_BY_AGENT_OR_CLIENT",
                "source": "HOST_POST",
                "source_method": "POST",
                "observed_at": observed_at,
            }
    else:
        context["control_capabilities"] = {}

    return context, provenance


def _base_receipt(envelope: dict[str, Any], now: datetime) -> dict[str, Any]:
    request = envelope.get("request") if isinstance(envelope.get("request"), dict) else {}
    connection = envelope.get("connection") if isinstance(envelope.get("connection"), dict) else {}
    target = envelope.get("target") if isinstance(envelope.get("target"), dict) else {}
    context, field_provenance = _safe_admission_context(envelope)
    material = {
        "request_id": request.get("request_id"),
        "idempotency_key": request.get("idempotency_key"),
        "connection_ref": connection.get("connection_ref"),
        "repository": target.get("repository"),
    }
    return {
        "schema": RECEIPT_SCHEMA,
        "admission_id": f"GSCC-ADM-{_canonical_digest(material)}",
        "request_id": request.get("request_id"),
        "correlation_id": request.get("correlation_id"),
        "idempotency_key": request.get("idempotency_key"),
        "connection_ref": connection.get("connection_ref"),
        "repository": target.get("repository"),
        "admission_context": context,
        "field_provenance": field_provenance,
        "evaluated_at": now.astimezone(timezone.utc).isoformat(),
        "repository_access": "NOT_YET_GRANTED",
        "invocation_authority_granted": False,
        "mutation_authority_granted": False,
        "provider_private_identity_inferred": False,
        "replay": False,
    }


@dataclass
class InMemoryAdmissionStore:
    records: dict[str, dict[str, Any]] = field(default_factory=dict)

    def get(self, idempotency_key: str) -> dict[str, Any] | None:
        existing = self.records.get(idempotency_key)
        return copy.deepcopy(existing) if existing is not None else None

    def put(self, idempotency_key: str, receipt: dict[str, Any]) -> None:
        self.records[idempotency_key] = copy.deepcopy(receipt)



QUALIFICATION_REQUIREMENTS = {
    "session": lambda x: isinstance(x, dict) and x.get("status") == "BOUND" and bool(x.get("session_id")) and bool(x.get("connection_ref")),
    "governance_read": lambda x: isinstance(x, dict) and x.get("status") == "COMPLETED" and bool(x.get("documents")),
    "repository_baseline": lambda x: isinstance(x, dict) and x.get("status") == "OBSERVED" and bool(x.get("repository")) and bool(x.get("observed_head")),
    "task": lambda x: isinstance(x, dict) and x.get("status") in {"RECONCILED", "NOT_REQUIRED"},
    "claim": lambda x: isinstance(x, dict) and x.get("status") in {"RECONCILED", "NOT_REQUIRED"},
    "capabilities": lambda x: isinstance(x, dict) and x.get("status") == "VERIFIED",
    "control_channel": lambda x: isinstance(x, dict) and x.get("status") == "VERIFIED",
    "gse_initial_state": lambda x: (
        isinstance(x, dict)
        and x.get("presence") == "PRESENT"
        and x.get("liveness") == "VERIFIED"
        and x.get("control_reachability") == "REACHABLE"
    ),
    "access_policy": lambda x: isinstance(x, dict) and x.get("status") == "ALLOW",
}


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def evaluate_access_grant(
    admission_receipt: dict[str, Any],
    qualification_evidence: dict[str, Any],
    *,
    now: datetime | None = None,
    ttl_seconds: int = 900,
) -> dict[str, Any]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)

    base = {
        "schema": "gscc-access-decision/v1",
        "status": "QUALIFICATION_IN_PROGRESS",
        "access_class": "NOT_AUTHORIZED",
        "admission_id": admission_receipt.get("admission_id") if isinstance(admission_receipt, dict) else None,
        "connection_ref": admission_receipt.get("connection_ref") if isinstance(admission_receipt, dict) else None,
        "repository": admission_receipt.get("repository") if isinstance(admission_receipt, dict) else None,
        "invocation_authority_granted": False,
        "mutation_authority_granted": False,
        "evaluated_at": now.isoformat(),
    }

    if not isinstance(admission_receipt, dict) or admission_receipt.get("status") != "PREAUTHORIZED":
        return {
            **base,
            "status": "ADMISSION_DENIED",
            "reason_code": "PREAUTHORIZED_ADMISSION_REQUIRED",
        }

    if not isinstance(qualification_evidence, dict):
        return {
            **base,
            "reason_code": "QUALIFICATION_EVIDENCE_REQUIRED",
            "missing_qualification": sorted(QUALIFICATION_REQUIREMENTS),
        }

    forbidden = _forbidden_path(qualification_evidence)
    if forbidden:
        return {
            **base,
            "status": "ADMISSION_DENIED",
            "reason_code": "FORBIDDEN_MATERIAL",
            "forbidden_path": forbidden,
        }

    missing = [
        name
        for name, validator in QUALIFICATION_REQUIREMENTS.items()
        if not validator(qualification_evidence.get(name))
    ]
    if missing:
        return {
            **base,
            "reason_code": "QUALIFICATION_INCOMPLETE",
            "missing_qualification": missing,
        }

    session = qualification_evidence["session"]
    baseline = qualification_evidence["repository_baseline"]
    policy = qualification_evidence["access_policy"]

    if session.get("connection_ref") != admission_receipt.get("connection_ref"):
        return {
            **base,
            "status": "ADMISSION_DENIED",
            "reason_code": "QUALIFICATION_CONNECTION_MISMATCH",
        }
    if baseline.get("repository") != admission_receipt.get("repository"):
        return {
            **base,
            "status": "ADMISSION_DENIED",
            "reason_code": "QUALIFICATION_REPOSITORY_MISMATCH",
        }

    issued_at = now
    expires_at = now + timedelta(seconds=max(1, int(ttl_seconds)))
    material = {
        "admission_id": admission_receipt.get("admission_id"),
        "session_id": session.get("session_id"),
        "connection_ref": session.get("connection_ref"),
        "repository": baseline.get("repository"),
        "bound_head": baseline.get("observed_head"),
        "issued_at": issued_at.isoformat(),
    }
    task = qualification_evidence.get("task") or {}
    claim = qualification_evidence.get("claim") or {}

    return {
        "schema": "gscc-access-grant/v1",
        "grant_id": f"GSCC-GRANT-{_canonical_digest(material)}",
        "admission_id": admission_receipt.get("admission_id"),
        "session_id": session.get("session_id"),
        "connection_ref": session.get("connection_ref"),
        "repository": baseline.get("repository"),
        "status": "AUTHORIZED",
        "access_class": "GOVERNED_FUNCTION_EXPOSURE_ELIGIBLE",
        "bound_head": baseline.get("observed_head"),
        "task_id": task.get("task_id"),
        "claim_id": claim.get("claim_id"),
        "allowed_authority_classes": list(policy.get("allowed_authority_classes") or []),
        "constraints": copy.deepcopy(policy.get("constraints") or {}),
        "qualification_digest": _canonical_digest(qualification_evidence),
        "issued_at": issued_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "invocation_authority_granted": False,
        "mutation_authority_granted": False,
    }


def validate_access_grant(
    grant: dict[str, Any] | None,
    *,
    connection_ref: str,
    repository: str,
    requested_head: str,
    session_id: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)

    if not isinstance(grant, dict):
        return {"status": "WITHHELD", "reason_code": "ACCESS_GRANT_REQUIRED"}
    if grant.get("schema") != "gscc-access-grant/v1" or grant.get("status") != "AUTHORIZED":
        return {"status": "DENIED", "reason_code": "ACCESS_GRANT_INVALID"}
    required_fields = ("grant_id", "admission_id", "session_id", "connection_ref", "repository", "bound_head", "expires_at")
    if any(not grant.get(field) for field in required_fields):
        return {"status": "DENIED", "reason_code": "ACCESS_GRANT_INVALID"}
    if grant.get("connection_ref") != connection_ref:
        return {"status": "DENIED", "reason_code": "ACCESS_GRANT_CONNECTION_MISMATCH"}
    if grant.get("repository") != repository:
        return {"status": "DENIED", "reason_code": "ACCESS_GRANT_REPOSITORY_MISMATCH"}
    if grant.get("bound_head") != requested_head:
        return {"status": "DENIED", "reason_code": "ACCESS_GRANT_HEAD_MISMATCH"}
    if session_id is not None and grant.get("session_id") != session_id:
        return {"status": "DENIED", "reason_code": "ACCESS_GRANT_SESSION_MISMATCH"}

    expires_at = _parse_datetime(grant.get("expires_at"))
    if expires_at is None:
        return {"status": "DENIED", "reason_code": "ACCESS_GRANT_EXPIRY_INVALID"}
    if expires_at <= now:
        return {"status": "DENIED", "reason_code": "ACCESS_GRANT_EXPIRED"}

    return {
        "status": "VALIDATED",
        "reason_code": "ACCESS_GRANT_VALID",
        "grant_id": grant.get("grant_id"),
        "admission_id": grant.get("admission_id"),
    }


def evaluate_admission(
    envelope: dict[str, Any],
    *,
    store: InMemoryAdmissionStore | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    store = store or InMemoryAdmissionStore()

    if not isinstance(envelope, dict):
        return {
            "schema": RECEIPT_SCHEMA,
            "status": "ADMISSION_INVALID",
            "reason_code": "ENVELOPE_OBJECT_REQUIRED",
            "repository_access": "NOT_YET_GRANTED",
            "invocation_authority_granted": False,
            "mutation_authority_granted": False,
            "provider_private_identity_inferred": False,
            "replay": False,
            "evaluated_at": now.isoformat(),
        }

    receipt = _base_receipt(envelope, now)

    forbidden = _forbidden_path(envelope)
    if forbidden:
        receipt.update(
            status="ADMISSION_DENIED",
            reason_code="FORBIDDEN_MATERIAL",
            forbidden_path=forbidden,
        )
        return receipt

    if envelope.get("schema") != ADMISSION_SCHEMA:
        receipt.update(
            status="ADMISSION_INVALID",
            reason_code="UNSUPPORTED_ADMISSION_SCHEMA",
        )
        return receipt

    missing = _missing_fields(envelope)
    if missing:
        receipt.update(
            status="ADMISSION_INCOMPLETE",
            reason_code="REQUIRED_FIELD_MISSING",
            missing_fields=missing,
        )
        return receipt

    if not _valid_repository((envelope.get("target") or {}).get("repository")):
        receipt.update(
            status="ADMISSION_INVALID",
            reason_code="TARGET_REPOSITORY_INVALID",
        )
        return receipt

    idempotency_key = str((envelope.get("request") or {})["idempotency_key"])
    previous = store.get(idempotency_key)
    if previous is not None:
        previous["replay"] = True
        previous["replay_status"] = "ALREADY_PROCESSED"
        return previous

    receipt.update(
        status="PREAUTHORIZED",
        reason_code="ADMISSION_PREAUTHORIZED",
        next_step="CANONICAL_SESSION_BIND",
        allowed_surface=list(QUALIFICATION_SURFACE),
        envelope_digest=_canonical_digest(envelope),
    )
    store.put(idempotency_key, receipt)
    return receipt

def _json_object(raw: str, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{label}_JSON_INVALID:{exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"{label}_JSON_OBJECT_REQUIRED")
    return value


def _write_cli_output(value: dict[str, Any], output: str | None) -> None:
    rendered = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if output:
        Path(output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")


def _github_output(name: str, value: Any) -> None:
    path = __import__("os").environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"{name}={value}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="GSCC admission and access qualification gate")
    sub = parser.add_subparsers(dest="command", required=True)

    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--envelope-json", required=True)
    evaluate.add_argument("--output")
    evaluate.add_argument("--require-preauthorized", action="store_true")

    qualify = sub.add_parser("qualify")
    qualify.add_argument("--admission-receipt-json", required=True)
    qualify.add_argument("--qualification-evidence-json", required=True)
    qualify.add_argument("--output")
    qualify.add_argument("--require-authorized", action="store_true")

    args = parser.parse_args()

    if args.command == "evaluate":
        result = evaluate_admission(_json_object(args.envelope_json, "ADMISSION_ENVELOPE"))
        _write_cli_output(result, args.output)
        _github_output("status", result.get("status"))
        _github_output("admission_id", result.get("admission_id"))
        if args.require_preauthorized and result.get("status") != "PREAUTHORIZED":
            raise SystemExit(3)
        return

    result = evaluate_access_grant(
        _json_object(args.admission_receipt_json, "ADMISSION_RECEIPT"),
        _json_object(args.qualification_evidence_json, "QUALIFICATION_EVIDENCE"),
    )
    _write_cli_output(result, args.output)
    _github_output("status", result.get("status"))
    _github_output("grant_id", result.get("grant_id"))
    if args.require_authorized and result.get("status") != "AUTHORIZED":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
