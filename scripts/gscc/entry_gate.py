from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping

from .protocol import assert_secretless

ENTRY_SCHEMA = "gscc-entry-context/v1"

ENTRY_REQUIRED_POST_FIELDS = (
    "provider",
    "agent_identity",
    "client_instance_id",
    "connection_ref",
    "connection_method",
    "surface_class",
    "function_surface",
    "capabilities",
)

ENTRY_REQUIRED_GET_FIELDS = (
    "repository",
    "repository_owner",
    "repository_name",
    "default_branch",
    "requested_ref",
    "observed_head_sha",
)

GET_VERIFIED_FIELDS = frozenset(ENTRY_REQUIRED_GET_FIELDS)

OPTIONAL_PROVIDER_FIELDS = (
    "model_runtime",
    "host_instance_id",
    "client_type",
    "client_version",
    "conversation_ref",
    "transport",
    "protocol_version",
    "authentication_class",
    "permission_scopes",
)

ENTRY_STATUSES = frozenset({"ENTRY_CONTEXT_OPEN", "ENTRY_CONTEXT_CLOSED"})


def _iso(value: datetime | str | None) -> str:
    if value is None:
        value = datetime.now(timezone.utc)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()
    if not isinstance(value, str) or not value.strip():
        raise ValueError("observed_at must be a non-empty datetime/string")
    return value.strip()


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value != "UNAVAILABLE"
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True


def _digest(value: Mapping[str, Any]) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _field_record(*, value: Any, source_method: str, observed_at: str) -> dict[str, Any]:
    return {
        "value": value,
        "status": "OBSERVED",
        "source_method": source_method,
        "provenance": "HOST_POST" if source_method == "POST" else "VERIFIED_GET",
        "observed_at": observed_at,
    }


def complete_entry_context(
    *,
    post_data: Mapping[str, Any] | None,
    get_data: Mapping[str, Any] | None,
    observed_at: datetime | str | None = None,
) -> dict[str, Any]:
    """Merge host-supplied POST facts with independently observed GET facts.

    GET wins for repository/Git verification fields. The returned receipt never
    grants function invocation or repository mutation authority. Entry opens only
    after every required POST and GET fact is present and secretless.
    """
    post = dict(post_data or {})
    observed = dict(get_data or {})
    assert_secretless(post, "entry.post")
    assert_secretless(observed, "entry.get")

    unavailable_raw = post.pop("unavailable", {})
    if unavailable_raw is None:
        unavailable_raw = {}
    if not isinstance(unavailable_raw, Mapping):
        raise ValueError("unavailable must be an object")
    assert_secretless(unavailable_raw, "entry.unavailable")

    at = _iso(observed_at)
    fields: dict[str, dict[str, Any]] = {}

    for key, value in post.items():
        if _present(value):
            fields[str(key)] = _field_record(value=value, source_method="POST", observed_at=at)

    # Observed GET facts are authoritative for all facts they can independently verify.
    for key, value in observed.items():
        if _present(value):
            fields[str(key)] = _field_record(value=value, source_method="GET", observed_at=at)

    required = list(ENTRY_REQUIRED_POST_FIELDS) + list(ENTRY_REQUIRED_GET_FIELDS)
    missing = [key for key in required if key not in fields or not _present(fields[key].get("value"))]

    unavailable: dict[str, dict[str, Any]] = {}
    for key, reason in unavailable_raw.items():
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f"unavailable reason must be non-empty: {key}")
        unavailable[str(key)] = {
            "status": "UNAVAILABLE",
            "reason": reason.strip(),
            "source_method": "POST",
            "observed_at": at,
        }

    open_entry = not missing
    status = "ENTRY_CONTEXT_OPEN" if open_entry else "ENTRY_CONTEXT_CLOSED"
    result: dict[str, Any] = {
        "schema": ENTRY_SCHEMA,
        "status": status,
        "reason_code": "ENTRY_CONTEXT_COMPLETE" if open_entry else "REQUIRED_ENTRY_DATA_MISSING",
        "entry_open": open_entry,
        "repository_entry_allowed": open_entry,
        "required_post_fields": list(ENTRY_REQUIRED_POST_FIELDS),
        "required_get_fields": list(ENTRY_REQUIRED_GET_FIELDS),
        "missing_required": missing,
        "fields": fields,
        "unavailable": unavailable,
        "observed_at": at,
        "source_summary": {
            "post_field_count": sum(1 for item in fields.values() if item["source_method"] == "POST"),
            "get_field_count": sum(1 for item in fields.values() if item["source_method"] == "GET"),
        },
        "invocation_authority_granted": False,
        "mutation_authority_granted": False,
        "entry_receipt": None,
    }

    material = {key: value for key, value in result.items() if key != "entry_receipt"}
    result["context_digest"] = _digest(material)
    if open_entry:
        receipt_material = {
            "schema": ENTRY_SCHEMA,
            "connection_ref": fields["connection_ref"]["value"],
            "repository": fields["repository"]["value"],
            "requested_ref": fields["requested_ref"]["value"],
            "observed_head_sha": fields["observed_head_sha"]["value"],
            "context_digest": result["context_digest"],
            "observed_at": at,
        }
        result["entry_receipt"] = f"GSCC-ENTRY-{_digest(receipt_material)}"
    return result


def validate_entry_context_receipt(
    receipt: Mapping[str, Any] | None,
    *,
    connection_ref: str,
    observed_head_sha: str,
    repository: str | None = None,
) -> tuple[bool, str]:
    if not isinstance(receipt, Mapping):
        return False, "GSCC_ENTRY_CONTEXT_REQUIRED"
    if receipt.get("schema") != ENTRY_SCHEMA:
        return False, "GSCC_ENTRY_CONTEXT_SCHEMA_INVALID"
    if receipt.get("status") != "ENTRY_CONTEXT_OPEN" or receipt.get("entry_open") is not True:
        return False, "GSCC_ENTRY_CONTEXT_CLOSED"
    if receipt.get("missing_required"):
        return False, "GSCC_ENTRY_CONTEXT_INCOMPLETE"
    token = receipt.get("entry_receipt")
    if not isinstance(token, str) or not token.startswith("GSCC-ENTRY-"):
        return False, "GSCC_ENTRY_RECEIPT_REQUIRED"

    fields = receipt.get("fields")
    if not isinstance(fields, Mapping):
        return False, "GSCC_ENTRY_FIELDS_REQUIRED"

    def value(name: str) -> Any:
        item = fields.get(name)
        return item.get("value") if isinstance(item, Mapping) else None

    if value("connection_ref") != connection_ref:
        return False, "GSCC_ENTRY_CONNECTION_MISMATCH"
    if value("observed_head_sha") != observed_head_sha:
        return False, "GSCC_ENTRY_HEAD_MISMATCH"
    if repository is not None and value("repository") != repository:
        return False, "GSCC_ENTRY_REPOSITORY_MISMATCH"
    return True, "GSCC_ENTRY_CONTEXT_VALIDATED"
