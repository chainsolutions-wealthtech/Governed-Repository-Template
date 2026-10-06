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
    context["control_capabilities"] = copy.deepcopy(controls) if isinstance(controls, dict) else {}
    if isinstance(controls, dict):
        for name, value in controls.items():
            provenance[f"control_capabilities.{name}"] = {
                "value": bool(value),
                "provenance": "DECLARED_BY_AGENT_OR_CLIENT",
                "source": "HOST_POST",
                "source_method": "POST",
                "observed_at": observed_at,
            }
    return context, provenance


def _base_receipt(envelope: dict[str, Any], now: datetime) -> dict[str, Any]:
    request = envelope.get("request") if isinstance(envelope.get("request"), dict) else {}
    agent = envelope.get("agent") if isinstance(envelope.get("agent"), dict) else {}
    client = envelope.get("client") if isinstance(envelope.get("client"), dict) else {}
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
        "client_instance_id": client.get("client_instance_id"),
        "provider": agent.get("provider"),
        "requested_role": agent.get("requested_role"),
        "requested_branch": target.get("requested_branch"),
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




SESSION_BINDING_SCHEMA = "gscc-admission-session-binding/v1"
STRONG_BIND_FRESHNESS_SECONDS = 300


def _active_gacr_sessions(
    sessions: dict[str, Any],
    repository: str,
    *,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    result: list[dict[str, Any]] = []
    for item in (sessions.get("sessions") or []):
        if not isinstance(item, dict):
            continue
        if item.get("repository") != repository:
            continue
        if item.get("status") != "ACTIVE":
            continue
        relay = item.get("relay") if isinstance(item.get("relay"), dict) else {}
        if relay.get("state") != "ACTIVE":
            continue
        lease_expires_at = _parse_datetime(relay.get("lease_expires_at"))
        if lease_expires_at is None or lease_expires_at <= now:
            continue
        if not item.get("session_id") or not item.get("connection_ref"):
            continue
        result.append(item)
    return result


def _binding_result(
    admission_receipt: dict[str, Any],
    session: dict[str, Any],
    *,
    correlation: str,
    now: datetime,
    reasons: list[str],
) -> dict[str, Any]:
    material = {
        "admission_id": admission_receipt.get("admission_id"),
        "session_id": session.get("session_id"),
        "admission_connection_ref": admission_receipt.get("connection_ref"),
        "canonical_connection_ref": session.get("connection_ref"),
        "correlation": correlation,
        "reasons": reasons,
    }
    return {
        "schema": SESSION_BINDING_SCHEMA,
        "status": "BOUND",
        "correlation": correlation,
        "admission_id": admission_receipt.get("admission_id"),
        "session_id": session.get("session_id"),
        "repository": admission_receipt.get("repository"),
        "admission_connection_ref": admission_receipt.get("connection_ref"),
        "canonical_connection_ref": session.get("connection_ref"),
        "binding_evidence_ref": f"GSCC-BIND-{_canonical_digest(material)}",
        "binding_reasons": reasons,
        "bound_at": now.astimezone(timezone.utc).isoformat(),
        "repository_access": "NOT_YET_GRANTED",
        "invocation_authority_granted": False,
        "mutation_authority_granted": False,
    }


def resolve_admission_session_binding(
    admission_receipt: dict[str, Any],
    sessions: dict[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)

    base = {
        "schema": SESSION_BINDING_SCHEMA,
        "status": "UNBOUND",
        "admission_id": admission_receipt.get("admission_id") if isinstance(admission_receipt, dict) else None,
        "repository": admission_receipt.get("repository") if isinstance(admission_receipt, dict) else None,
        "admission_connection_ref": admission_receipt.get("connection_ref") if isinstance(admission_receipt, dict) else None,
        "repository_access": "NOT_YET_GRANTED",
        "invocation_authority_granted": False,
        "mutation_authority_granted": False,
        "evaluated_at": now.isoformat(),
    }
    if not isinstance(admission_receipt, dict) or admission_receipt.get("status") != "PREAUTHORIZED":
        return {**base, "reason_code": "PREAUTHORIZED_ADMISSION_REQUIRED"}
    if not isinstance(sessions, dict):
        return {**base, "reason_code": "ADMISSION_SESSION_STORE_INVALID"}

    repository = admission_receipt.get("repository")
    if not repository:
        return {**base, "reason_code": "ADMISSION_REPOSITORY_REQUIRED"}

    candidates = _active_gacr_sessions(sessions, str(repository), now=now)
    admission_connection_ref = admission_receipt.get("connection_ref")

    exact = [s for s in candidates if s.get("connection_ref") == admission_connection_ref]
    if len(exact) == 1:
        return _binding_result(
            admission_receipt,
            exact[0],
            correlation="EXACT",
            now=now,
            reasons=["EXACT_CONNECTION_REF"],
        )
    if len(exact) > 1:
        return {
            **base,
            "reason_code": "ADMISSION_SESSION_BIND_AMBIGUOUS",
            "candidate_session_ids": sorted(str(s.get("session_id")) for s in exact),
            "correlation": "AMBIGUOUS",
        }

    requested_branch = admission_receipt.get("requested_branch")
    admission_client = admission_receipt.get("client_instance_id")
    transport_actor = admission_receipt.get("transport_author_login")
    admission_time = _parse_datetime(admission_receipt.get("evaluated_at"))

    strong: list[tuple[dict[str, Any], list[str]]] = []
    for session in candidates:
        relay = session.get("relay") if isinstance(session.get("relay"), dict) else {}
        session_branch = session.get("branch") or relay.get("branch")
        if requested_branch and session_branch != requested_branch:
            continue

        reasons: list[str] = []
        client_match = bool(admission_client) and session.get("client_instance_id") == admission_client
        if client_match:
            reasons.append("CLIENT_INSTANCE_MATCH")

        actor = session.get("github_actor") or session.get("agent_identity")
        actor_match = bool(transport_actor) and actor == transport_actor
        if actor_match:
            reasons.append("TRANSPORT_ACTOR_MATCH")

        freshness_match = False
        last_seen = _parse_datetime(session.get("last_seen_at"))
        if admission_time is not None and last_seen is not None:
            delta = abs((last_seen - admission_time).total_seconds())
            freshness_match = delta <= STRONG_BIND_FRESHNESS_SECONDS
            if freshness_match:
                reasons.append("BOUNDED_TIME_PROXIMITY")

        if requested_branch:
            reasons.append("REQUESTED_BRANCH_MATCH")

        # A stable client anchor is sufficient when unique. For provider issue
        # ingress, actor identity must also be temporally close to the admission
        # event so old sessions for the same repository actor are not selected.
        if client_match or (actor_match and freshness_match):
            strong.append((session, reasons))

    if len(strong) == 1:
        session, reasons = strong[0]
        return _binding_result(
            admission_receipt,
            session,
            correlation="STRONG",
            now=now,
            reasons=reasons,
        )
    if len(strong) > 1:
        return {
            **base,
            "reason_code": "ADMISSION_SESSION_BIND_AMBIGUOUS",
            "candidate_session_ids": sorted(str(s.get("session_id")) for s, _ in strong),
            "correlation": "AMBIGUOUS",
        }
    return {
        **base,
        "reason_code": "ADMISSION_SESSION_BIND_NOT_FOUND",
        "candidate_session_ids": [],
        "correlation": "UNKNOWN",
    }


INITIAL_GSE_QUALIFICATION_REQUIREMENTS = {
    "governance_read": lambda x: isinstance(x, dict) and x.get("status") == "COMPLETED" and bool(x.get("documents")),
    "repository_baseline": lambda x: isinstance(x, dict) and x.get("status") == "OBSERVED" and bool(x.get("repository")) and bool(x.get("observed_head")),
    "capabilities": lambda x: isinstance(x, dict) and x.get("status") == "VERIFIED",
    "control_channel": lambda x: isinstance(x, dict) and x.get("status") == "VERIFIED",
    "gse_initial_state": lambda x: (
        isinstance(x, dict)
        and x.get("status") == "VERIFIED"
        and x.get("presence") == "PRESENT"
        and x.get("liveness") == "VERIFIED"
        and x.get("control_reachability") == "REACHABLE"
        and x.get("durable_gacr_session_required") is False
    ),
}


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

    if (
        qualification_evidence.get("schema") != "gscc-qualification-evidence/v1"
        or qualification_evidence.get("harvested_by") != "GSCC_ADMISSION_HARVESTER"
    ):
        return {
            **base,
            "status": "ADMISSION_DENIED",
            "reason_code": "QUALIFICATION_EVIDENCE_NOT_CANONICAL",
        }

    supplied_digest = qualification_evidence.get("harvest_digest")
    digest_material = copy.deepcopy(qualification_evidence)
    digest_material.pop("harvest_digest", None)
    if not isinstance(supplied_digest, str) or supplied_digest != _canonical_digest(digest_material):
        return {
            **base,
            "status": "ADMISSION_DENIED",
            "reason_code": "QUALIFICATION_EVIDENCE_DIGEST_MISMATCH",
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

    admission_connection_ref = admission_receipt.get("connection_ref")
    canonical_connection_ref = session.get("connection_ref")
    if canonical_connection_ref != admission_connection_ref:
        if (
            session.get("admission_connection_ref") != admission_connection_ref
            or session.get("binding_level") not in {"EXACT", "STRONG"}
            or not session.get("binding_evidence_ref")
        ):
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

    admission_context = admission_receipt.get("admission_context") if isinstance(admission_receipt.get("admission_context"), dict) else {}
    intent_context = admission_context.get("intent") if isinstance(admission_context.get("intent"), dict) else {}
    entry_action = intent_context.get("entry_action")
    connection_intent = intent_context.get("connection_intent")

    issued_at = now
    expires_at = now + timedelta(seconds=max(1, int(ttl_seconds)))
    material = {
        "admission_id": admission_receipt.get("admission_id"),
        "session_id": session.get("session_id"),
        "connection_ref": session.get("connection_ref"),
        "admission_connection_ref": admission_receipt.get("connection_ref"),
        "binding_level": session.get("binding_level") or ("EXACT" if session.get("connection_ref") == admission_receipt.get("connection_ref") else None),
        "binding_evidence_ref": session.get("binding_evidence_ref"),
        "repository": baseline.get("repository"),
        "bound_head": baseline.get("observed_head"),
        "entry_action": entry_action,
        "connection_intent": connection_intent,
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
        "admission_connection_ref": admission_receipt.get("connection_ref"),
        "binding_level": session.get("binding_level") or ("EXACT" if session.get("connection_ref") == admission_receipt.get("connection_ref") else None),
        "binding_evidence_ref": session.get("binding_evidence_ref"),
        "repository": baseline.get("repository"),
        "status": "AUTHORIZED",
        "access_class": "GOVERNED_FUNCTION_EXPOSURE_ELIGIBLE",
        "bound_head": baseline.get("observed_head"),
        "entry_action": entry_action,
        "connection_intent": connection_intent,
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
        next_step="GSCC_PRE_GSE_QUALIFICATION",
        allowed_surface=list(QUALIFICATION_SURFACE),
        envelope_digest=_canonical_digest(envelope),
    )
    store.put(idempotency_key, receipt)
    return receipt


ISSUE_ADMISSION_PREFIX = "/gscc-admission "
AUTHORIZED_ISSUE_ASSOCIATIONS = frozenset({"OWNER", "MEMBER", "COLLABORATOR"})
MAX_ISSUE_ADMISSION_PAYLOAD_CHARS = 8192


def _ingress_denial(reason_code: str, now: datetime, **extra: Any) -> dict[str, Any]:
    result = {
        "schema": RECEIPT_SCHEMA,
        "status": "ADMISSION_DENIED",
        "reason_code": reason_code,
        "repository_access": "NOT_YET_GRANTED",
        "invocation_authority_granted": False,
        "mutation_authority_granted": False,
        "provider_private_identity_inferred": False,
        "replay": False,
        "evaluated_at": now.astimezone(timezone.utc).isoformat(),
    }
    result.update(extra)
    return result


def evaluate_issue_comment_admission(
    event: dict[str, Any],
    *,
    expected_issue_number: int,
    store: InMemoryAdmissionStore | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if not isinstance(event, dict):
        return _ingress_denial("ADMISSION_INGRESS_EVENT_INVALID", now)

    issue = event.get("issue") if isinstance(event.get("issue"), dict) else {}
    if issue.get("number") != expected_issue_number:
        return _ingress_denial(
            "ADMISSION_INGRESS_ISSUE_MISMATCH",
            now,
            transport="GITHUB_ISSUE_COMMENT",
        )

    comment = event.get("comment") if isinstance(event.get("comment"), dict) else {}
    association = str(comment.get("author_association") or "")
    if association not in AUTHORIZED_ISSUE_ASSOCIATIONS:
        return _ingress_denial(
            "ADMISSION_INGRESS_ACTOR_NOT_AUTHORIZED",
            now,
            transport="GITHUB_ISSUE_COMMENT",
        )

    comment_id = comment.get("id")
    if comment_id in (None, ""):
        return _ingress_denial(
            "ADMISSION_INGRESS_COMMENT_ID_REQUIRED",
            now,
            transport="GITHUB_ISSUE_COMMENT",
        )

    body = str(comment.get("body") or "")
    if not body.startswith(ISSUE_ADMISSION_PREFIX):
        return _ingress_denial(
            "ADMISSION_INGRESS_PREFIX_REQUIRED",
            now,
            transport="GITHUB_ISSUE_COMMENT",
            transport_event_ref=f"issue-comment:{comment_id}",
        )

    raw = body[len(ISSUE_ADMISSION_PREFIX):].strip()
    if not raw:
        return _ingress_denial(
            "ADMISSION_INGRESS_PAYLOAD_REQUIRED",
            now,
            transport="GITHUB_ISSUE_COMMENT",
            transport_event_ref=f"issue-comment:{comment_id}",
        )
    if len(raw) > MAX_ISSUE_ADMISSION_PAYLOAD_CHARS:
        return _ingress_denial(
            "ADMISSION_INGRESS_PAYLOAD_TOO_LARGE",
            now,
            transport="GITHUB_ISSUE_COMMENT",
            transport_event_ref=f"issue-comment:{comment_id}",
        )

    try:
        envelope = json.loads(raw)
    except json.JSONDecodeError:
        return _ingress_denial(
            "ADMISSION_INGRESS_JSON_INVALID",
            now,
            transport="GITHUB_ISSUE_COMMENT",
            transport_event_ref=f"issue-comment:{comment_id}",
        )
    if not isinstance(envelope, dict):
        return _ingress_denial(
            "ADMISSION_INGRESS_JSON_OBJECT_REQUIRED",
            now,
            transport="GITHUB_ISSUE_COMMENT",
            transport_event_ref=f"issue-comment:{comment_id}",
        )

    repository = event.get("repository") if isinstance(event.get("repository"), dict) else {}
    event_repository = repository.get("full_name")
    target = envelope.get("target") if isinstance(envelope.get("target"), dict) else {}
    if event_repository and target.get("repository") != event_repository:
        return _ingress_denial(
            "ADMISSION_INGRESS_REPOSITORY_MISMATCH",
            now,
            transport="GITHUB_ISSUE_COMMENT",
            transport_event_ref=f"issue-comment:{comment_id}",
        )

    result = evaluate_admission(envelope, store=store, now=now)
    user = comment.get("user") if isinstance(comment.get("user"), dict) else {}
    result.update(
        transport="GITHUB_ISSUE_COMMENT",
        transport_event_ref=f"issue-comment:{comment_id}",
        transport_issue_number=expected_issue_number,
        transport_author_login=user.get("login"),
        transport_author_association=association,
    )
    return result

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

    issue_comment = sub.add_parser("issue-comment")
    issue_comment.add_argument("--event-path", required=True)
    issue_comment.add_argument("--expected-issue-number", required=True, type=int)
    issue_comment.add_argument("--output")
    issue_comment.add_argument("--require-preauthorized", action="store_true")

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

    if args.command == "issue-comment":
        event = json.loads(Path(args.event_path).read_text(encoding="utf-8"))
        result = evaluate_issue_comment_admission(
            event,
            expected_issue_number=args.expected_issue_number,
        )
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