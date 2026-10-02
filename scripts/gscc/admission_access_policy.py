from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

POLICY_SCHEMA = "gscc-admission-access-policy/v1"
READ_ONLY_AUTHORITY = "READ_ONLY_DISCOVERY_AUTHORITY"


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _requested_capabilities(admission_receipt: dict[str, Any]) -> list[str]:
    context = admission_receipt.get("admission_context")
    if not isinstance(context, dict):
        return []
    intent = context.get("intent")
    if not isinstance(intent, dict):
        return []
    values = intent.get("requested_capabilities")
    if not isinstance(values, list):
        return []
    return sorted({str(value) for value in values if value not in (None, "")})


def _base(policy: dict[str, Any], now: datetime) -> dict[str, Any]:
    authority_id = str(policy.get("authority_id") or "UNAVAILABLE")
    policy_digest = _digest(policy)
    return {
        "schema": "gscc-access-policy-decision/v1",
        "status": "DENY",
        "authority_id": authority_id,
        "policy_digest": policy_digest,
        "allowed_authority_classes": [],
        "constraints": deepcopy(policy.get("constraints") or {}),
        "provenance": "OBSERVABLE_BY_PLATFORM",
        "source": "GOVERNANCE_ACCESS_POLICY",
        "observed_at": _iso(now),
        "invocation_authority_granted": False,
        "mutation_authority_granted": False,
    }


def evaluate_access_policy(
    admission_receipt: dict[str, Any],
    policy: dict[str, Any],
    prerequisites: dict[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if not isinstance(policy, dict) or policy.get("schema") != POLICY_SCHEMA:
        raise ValueError("canonical GSCC admission access policy required")
    if policy.get("default_decision") != "DENY":
        raise ValueError("GSCC admission access policy must default DENY")
    if policy.get("read_only_authority_class") != READ_ONLY_AUTHORITY:
        raise ValueError("baseline policy may authorize only READ_ONLY_DISCOVERY_AUTHORITY")

    result = _base(policy, now)
    if not isinstance(admission_receipt, dict) or admission_receipt.get("status") != "PREAUTHORIZED":
        result["reason"] = "PREAUTHORIZED_ADMISSION_REQUIRED"
        return result

    requested = _requested_capabilities(admission_receipt)
    result["requested_capabilities"] = requested
    if not requested:
        result["reason"] = "REQUESTED_CAPABILITIES_REQUIRED"
        return result

    allowed_requested = set(policy.get("read_only_requested_capabilities") or [])
    unsupported = sorted(set(requested) - allowed_requested)
    if unsupported:
        result["reason"] = "REQUESTED_CAPABILITY_NOT_ALLOWED_BY_BASELINE_POLICY"
        result["unsupported_requested_capabilities"] = unsupported
        return result

    session = prerequisites.get("session") if isinstance(prerequisites, dict) else None
    baseline = prerequisites.get("repository_baseline") if isinstance(prerequisites, dict) else None
    capabilities = prerequisites.get("capabilities") if isinstance(prerequisites, dict) else None
    control = prerequisites.get("control_channel") if isinstance(prerequisites, dict) else None
    gse = prerequisites.get("gse_initial_state") if isinstance(prerequisites, dict) else None

    missing: list[str] = []
    if not isinstance(session, dict) or session.get("status") != "BOUND" or not session.get("session_id"):
        missing.append("session")
    if not isinstance(baseline, dict) or baseline.get("status") != "OBSERVED" or not baseline.get("observed_head"):
        missing.append("repository_baseline")
    if not isinstance(capabilities, dict) or capabilities.get("status") != "VERIFIED" or not capabilities.get("evidence_ref"):
        missing.append("capabilities")
    if (
        not isinstance(control, dict)
        or control.get("status") != "VERIFIED"
        or control.get("state") != "REACHABLE"
        or not control.get("evidence_ref")
    ):
        missing.append("control_channel")
    if (
        not isinstance(gse, dict)
        or gse.get("schema") != "gscc-gse-admission-state/v1"
        or gse.get("status") != "VERIFIED"
        or gse.get("presence") != "PRESENT"
        or gse.get("liveness") != "VERIFIED"
        or gse.get("control_reachability") != "REACHABLE"
        or not gse.get("evidence_ref")
    ):
        missing.append("gse_initial_state")

    if missing:
        result["status"] = "PENDING"
        result["reason"] = "ACCESS_POLICY_PRECONDITIONS_INCOMPLETE"
        result["missing_preconditions"] = missing
        return result

    result["status"] = "ALLOW"
    result["reason"] = "READ_ONLY_DISCOVERY_BASELINE_ALLOWED"
    result["allowed_authority_classes"] = [READ_ONLY_AUTHORITY]
    material = {
        "authority_id": result["authority_id"],
        "policy_digest": result["policy_digest"],
        "admission_id": admission_receipt.get("admission_id"),
        "session_id": session.get("session_id"),
        "repository": baseline.get("repository"),
        "observed_head": baseline.get("observed_head"),
        "requested_capabilities": requested,
        "control_evidence_ref": control.get("evidence_ref"),
        "gse_evidence_ref": gse.get("evidence_ref"),
    }
    result["decision_digest"] = _digest(material)
    result["evidence_ref"] = f"gscc-access-policy:{result['authority_id']}:{result['decision_digest']}"
    return result
