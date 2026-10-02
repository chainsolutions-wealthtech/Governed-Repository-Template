from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
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


def _base_receipt(envelope: dict[str, Any], now: datetime) -> dict[str, Any]:
    request = envelope.get("request") if isinstance(envelope.get("request"), dict) else {}
    connection = envelope.get("connection") if isinstance(envelope.get("connection"), dict) else {}
    target = envelope.get("target") if isinstance(envelope.get("target"), dict) else {}
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
