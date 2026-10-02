from __future__ import annotations

from copy import deepcopy
from typing import Any

from .contract import ControlValidationError, UNAVAILABLE, validate_safe_payload

SUPPORTED_CONTROL_RESPONSE_TYPES = frozenset({
    "STATUS_RESPONSE",
    "PROGRESS_RESPONSE",
    "CONTEXT_RESPONSE",
    "CHECKPOINT_RESPONSE",
})


def _available(value: Any) -> bool:
    return value not in (None, "", UNAVAILABLE)


def _copy_available(target: dict[str, Any], key: str, value: Any) -> None:
    if _available(value):
        target[key] = deepcopy(value)


def control_response_to_gse_event(
    response: dict[str, Any],
    *,
    observed_at: str,
    event_id: str | None = None,
) -> dict[str, Any]:
    """Map a safe control response into the existing canonical GSE event model.

    This adapter is intentionally projection-only:
    - it creates no second state engine;
    - non-liveness responses never emit HEARTBEAT/CHALLENGE_RESPONSE;
    - snapshot traffic never sets qualifying_progress=True;
    - reported progress timestamps are preserved as reported facts, not promoted
      to new progress evidence at response-observation time.
    """

    if not isinstance(response, dict):
        raise ControlValidationError("control response must be a mapping")
    validate_safe_payload(response)

    response_type = response.get("response_type")
    if response_type not in SUPPORTED_CONTROL_RESPONSE_TYPES:
        raise ControlValidationError(f"unsupported GSE control response: {response_type!r}")
    if not observed_at:
        raise ControlValidationError("observed_at is required")

    session_id = response.get("target_session_id")
    payload: dict[str, Any] = {
        "control_response_type": response_type,
        "control_snapshot": True,
    }
    _copy_available(payload, "session_identity", session_id)

    if response_type == "STATUS_RESPONSE":
        event_type = "CONTEXT_UPDATE"
        _copy_available(payload, "last_action", response.get("current_action"))
        _copy_available(payload, "observed_head", response.get("observed_head"))
        _copy_available(payload, "reported_current_state", response.get("current_state"))
        _copy_available(payload, "reported_current_tool", response.get("current_tool"))
        _copy_available(payload, "reported_last_progress_at", response.get("last_progress_at"))
        _copy_available(payload, "reported_blocker", response.get("blocker"))

    elif response_type == "CONTEXT_RESPONSE":
        event_type = "CONTEXT_UPDATE"
        _copy_available(payload, "repository", response.get("repository"))
        _copy_available(payload, "branch", response.get("branch"))
        _copy_available(payload, "observed_head", response.get("observed_head"))
        _copy_available(payload, "last_action", response.get("current_action"))
        _copy_available(payload, "next_action", response.get("next_action"))
        _copy_available(payload, "checkpoint", response.get("last_checkpoint"))
        _copy_available(payload, "reported_objective_ref", response.get("objective_ref"))
        _copy_available(payload, "reported_current_phase", response.get("current_phase"))

    elif response_type == "CHECKPOINT_RESPONSE":
        event_type = "CHECKPOINT"
        _copy_available(payload, "checkpoint", response.get("checkpoint_ref"))
        _copy_available(payload, "last_action", response.get("current_action"))
        _copy_available(payload, "observed_head", response.get("observed_head"))
        # Deliberately absent: checkpoint_advanced. A snapshot response is context,
        # not proof that a checkpoint advanced at response-observation time.

    else:  # PROGRESS_RESPONSE
        event_type = "PROGRESS"
        payload["qualifying_progress"] = False
        _copy_available(payload, "reported_last_progress_at", response.get("last_progress_at"))
        _copy_available(payload, "reported_progress_marker", response.get("progress_marker"))
        _copy_available(payload, "reported_checkpoint_ref", response.get("checkpoint_ref"))
        _copy_available(payload, "reported_work_item_ref", response.get("work_item_ref"))
        # Deliberately absent: phase transitions, completed_step_ref,
        # next_step_ref, checkpoint_advanced and work_item_advanced.

    message_id = response.get("message_id")
    return {
        "event_id": event_id or (f"control-response:{message_id}" if message_id else None),
        "message_id": message_id,
        "event_type": event_type,
        "observed_at": observed_at,
        "payload": payload,
    }
