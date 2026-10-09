from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

try:
    from scripts.gse.session_state_engine import project
except ModuleNotFoundError:
    from gse.session_state_engine import project


SCHEMA = "gscc-gse-admission-state/v1"


def _parse(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _event(event_id: str, event_type: str, observed_at: str, **payload: Any) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "event_type": event_type,
        "observed_at": observed_at,
        "payload": payload,
    }



def project_pre_gacr_admission_gse_state(
    admission_receipt: dict[str, Any],
    repository_baseline: dict[str, Any],
    control_proof: dict[str, Any],
    *,
    requested_logical_agent_alias: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Project Q10 from GSCC evidence only, before durable GACR continuity."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    logical_identity = str(
        admission_receipt.get("connection_ref")
        or admission_receipt.get("admission_id")
        or ""
    )
    if not logical_identity:
        raise ValueError("GSCC logical connection identity required")

    repository = repository_baseline.get("repository") or admission_receipt.get("repository")
    branch = repository_baseline.get("requested_branch") or repository_baseline.get("default_branch")
    observed_head = repository_baseline.get("observed_head")
    observed_at = repository_baseline.get("observed_at") or admission_receipt.get("evaluated_at") or _iso(now)

    events = [
        _event(
            "admission-gscc-session-attach",
            "SESSION_ATTACH",
            str(observed_at),
            session_identity=logical_identity,
            repository=repository,
            branch=branch,
            observed_head=observed_head,
            last_action="GSCC_Q10_INITIAL_SESSION_STATE",
        )
    ]

    capabilities = control_proof.get("capabilities") if isinstance(control_proof, dict) else {}
    control = control_proof.get("control_channel") if isinstance(control_proof, dict) else {}
    control_verified = (
        isinstance(capabilities, dict)
        and capabilities.get("status") == "VERIFIED"
        and isinstance(control, dict)
        and control.get("status") == "VERIFIED"
        and control.get("state") == "REACHABLE"
        and bool(control.get("evidence_ref"))
    )
    control_at = control.get("observed_at") if isinstance(control, dict) else None
    if control_verified:
        events.append(
            _event(
                "admission-gscc-control-challenge-response",
                "CHALLENGE_RESPONSE",
                str(control_at or observed_at),
                delivery_state="ACKNOWLEDGED",
                replay=False,
                fresh_liveness=True,
                challenge_id=control.get("challenge_id"),
            )
        )

    events.sort(key=lambda event: _parse(event.get("observed_at")) or now)
    twin = project(events, reference_time=_iso(now), session_id=logical_identity)
    presence_state = (twin.get("presence") or {}).get("state") or "UNKNOWN"
    liveness_state = (twin.get("liveness") or {}).get("state") or "UNKNOWN"
    control_state = (twin.get("control_channel") or {}).get("state") or "UNKNOWN"
    alias = str(requested_logical_agent_alias or "").strip()
    if alias in {"", "UNAVAILABLE", "UNKNOWN", "NOT_EXPOSED", "NOT_ACCESSIBLE"}:
        alias = None

    result = {
        "schema": SCHEMA,
        "status": "GSE_ADMISSION_STATE_INCOMPLETE",
        "session_id": logical_identity,
        "logical_identity": logical_identity,
        "durable_gacr_session_required": False,
        "repository": repository,
        "branch": branch,
        "observed_head": observed_head,
        "presence": presence_state,
        "liveness": "VERIFIED" if liveness_state == "ACTIVE" else liveness_state,
        "activity": (twin.get("activity") or {}).get("state") or "UNKNOWN",
        "progress": (twin.get("progress") or {}).get("state") or "UNKNOWN",
        "control_reachability": "REACHABLE" if control_state == "REACHABLE" else control_state,
        "continuity": (twin.get("continuity") or {}).get("state") or "UNKNOWN",
        "requested_logical_agent_alias": alias,
        "logical_agent_alias_resolution": "GACR_Q2_REQUIRED" if alias else "NOT_REQUESTED",
        "logical_agent_alias_grants_authority": False,
        "timestamps": deepcopy(twin.get("timestamps") or {}),
        "evidence_ref": control.get("evidence_ref") if control_verified else None,
        "provenance": "GSE_DERIVED_FROM_GSCC_PRE_GACR",
        "source": "GSE_SESSION_STATE_ENGINE",
        "observed_at": _iso(now),
        "invocation_authority_granted": False,
        "mutation_authority_granted": False,
    }
    if (
        result["presence"] == "PRESENT"
        and result["liveness"] == "VERIFIED"
        and result["control_reachability"] == "REACHABLE"
        and result["evidence_ref"]
    ):
        result["status"] = "VERIFIED"
    material = deepcopy(result)
    result["projection_digest"] = _digest(material)
    return result


def project_admission_gse_state(
    session: dict[str, Any],
    control_proof: dict[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    session_id = str(session.get("session_id") or "")
    if not session_id:
        raise ValueError("canonical session_id required")

    relay = session.get("relay") if isinstance(session.get("relay"), dict) else {}
    branch = session.get("branch") or relay.get("branch")
    task_id = session.get("task_id") or relay.get("task_id")
    observed_head = session.get("last_observed_head") or session.get("last_observed_head_sha")
    repository = session.get("repository")

    created_at = (
        session.get("created_at")
        or session.get("last_seen_at")
        or session.get("observed_at")
        or _iso(now)
    )
    heartbeat_at = (
        session.get("last_heartbeat_at")
        or relay.get("last_heartbeat_at")
        or session.get("last_seen_at")
    )

    events = [
        _event(
            "admission-session-attach",
            "SESSION_ATTACH",
            str(created_at),
            session_identity=session_id,
            repository=repository,
            task=task_id,
            branch=branch,
            observed_head=observed_head,
            last_action="GSCC_ADMISSION_SESSION_BOUND",
        )
    ]
    if heartbeat_at and _parse(heartbeat_at):
        events.append(_event("admission-session-heartbeat", "HEARTBEAT", str(heartbeat_at)))

    capabilities = control_proof.get("capabilities") if isinstance(control_proof, dict) else {}
    control = control_proof.get("control_channel") if isinstance(control_proof, dict) else {}
    control_verified = (
        isinstance(capabilities, dict)
        and capabilities.get("status") == "VERIFIED"
        and isinstance(control, dict)
        and control.get("status") == "VERIFIED"
        and control.get("state") == "REACHABLE"
        and bool(control.get("evidence_ref"))
    )
    control_at = control.get("observed_at") if isinstance(control, dict) else None
    if control_verified and control_at and _parse(control_at):
        events.append(
            _event(
                "admission-control-challenge-response",
                "CHALLENGE_RESPONSE",
                str(control_at),
                delivery_state="ACKNOWLEDGED",
                replay=False,
                fresh_liveness=True,
                challenge_id=control.get("challenge_id"),
            )
        )

    # Canonical sources can be persisted in causal order that differs from
    # their observation timestamps (for example, a challenge response can
    # trigger a heartbeat a few seconds later). Feed GSE chronological evidence
    # so a valid control response is not discarded as out-of-order merely
    # because the derived heartbeat was appended first.
    events.sort(key=lambda event: _parse(event.get("observed_at")) or now)
    twin = project(events, reference_time=_iso(now), session_id=session_id)
    presence_state = (twin.get("presence") or {}).get("state") or "UNKNOWN"
    liveness_state = (twin.get("liveness") or {}).get("state") or "UNKNOWN"
    control_state = (twin.get("control_channel") or {}).get("state") or "UNKNOWN"

    result = {
        "schema": SCHEMA,
        "status": "GSE_ADMISSION_STATE_INCOMPLETE",
        "session_id": session_id,
        "repository": repository,
        "branch": branch,
        "observed_head": observed_head,
        "presence": presence_state,
        "liveness": "VERIFIED" if liveness_state == "ACTIVE" else liveness_state,
        "activity": (twin.get("activity") or {}).get("state") or "UNKNOWN",
        "progress": (twin.get("progress") or {}).get("state") or "UNKNOWN",
        "control_reachability": "REACHABLE" if control_state == "REACHABLE" else control_state,
        "continuity": (twin.get("continuity") or {}).get("state") or "UNKNOWN",
        "timestamps": deepcopy(twin.get("timestamps") or {}),
        "evidence_ref": control.get("evidence_ref") if control_verified else None,
        "provenance": "GSE_DERIVED",
        "source": "GSE_SESSION_STATE_ENGINE",
        "observed_at": _iso(now),
        "invocation_authority_granted": False,
        "mutation_authority_granted": False,
    }
    if (
        result["presence"] == "PRESENT"
        and result["liveness"] == "VERIFIED"
        and result["control_reachability"] == "REACHABLE"
        and result["evidence_ref"]
    ):
        result["status"] = "VERIFIED"
    material = deepcopy(result)
    result["projection_digest"] = _digest(material)
    return result
