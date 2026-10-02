#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from scripts.gse.session_state_engine import reduce_event
from scripts.gscc_gacr import ControlValidationError, control_response_to_gse_event


T0 = "2026-10-02T05:00:00Z"
T1 = "2026-10-02T05:01:00Z"
T2 = "2026-10-02T05:02:00Z"


def assert_true(value, message: str) -> None:
    if not value:
        raise AssertionError("GSCC_GACR_GSE_PROJECTION_FAILED: " + message)


def base_twin():
    twin = reduce_event(None, {
        "event_id": "attach",
        "event_type": "SESSION_ATTACH",
        "observed_at": T0,
        "payload": {
            "session_identity": "session-a",
            "repository": "owner/repo",
            "task": "TASK-1",
            "branch": "feature/a",
            "observed_head": "a" * 40,
            "last_action": "work",
            "checkpoint": "CHK-1",
            "next_action": "continue",
        },
    })
    twin = reduce_event(twin, {
        "event_id": "progress",
        "event_type": "PROGRESS",
        "observed_at": T1,
        "payload": {
            "previous_phase": "A",
            "current_phase": "B",
            "completed_step_ref": "STEP-A",
            "next_step_ref": "STEP-B",
        },
    })
    return twin


def apply(twin, response, event_id):
    event = control_response_to_gse_event(response, observed_at=T2, event_id=event_id)
    return event, reduce_event(twin, event)


def main() -> None:
    twin = base_twin()
    baseline_liveness = twin["timestamps"]["last_liveness_evidence_at"]
    baseline_progress = twin["timestamps"]["last_progress_at"]

    status_event, status_twin = apply(twin, {
        "response_type": "STATUS_RESPONSE",
        "message_id": "status-msg",
        "target_session_id": "session-a",
        "current_state": "ACTIVE",
        "current_action": "inspect",
        "current_tool": "github",
        "observed_head": "a" * 40,
        "last_progress_at": T1,
        "blocker": "UNAVAILABLE",
    }, "status")
    assert_true(status_event["event_type"] == "CONTEXT_UPDATE", "STATUS must map to CONTEXT_UPDATE")
    assert_true(status_twin["context"]["last_action"] == "inspect", "STATUS current_action must enrich context")
    assert_true(status_twin["timestamps"]["last_liveness_evidence_at"] == baseline_liveness, "STATUS must not create liveness")
    assert_true(status_twin["timestamps"]["last_progress_at"] == baseline_progress, "STATUS must not create progress")

    context_event, context_twin = apply(twin, {
        "response_type": "CONTEXT_RESPONSE",
        "message_id": "context-msg",
        "target_session_id": "session-a",
        "repository": "owner/repo",
        "branch": "feature/a",
        "observed_head": "a" * 40,
        "current_action": "review",
        "next_action": "test",
        "last_checkpoint": "CHK-2",
        "objective_ref": "OBJ-1",
        "current_phase": "TEST",
    }, "context")
    assert_true(context_event["event_type"] == "CONTEXT_UPDATE", "CONTEXT must map to CONTEXT_UPDATE")
    assert_true(context_twin["context"]["last_action"] == "review", "CONTEXT action mapping")
    assert_true(context_twin["context"]["next_action"] == "test", "CONTEXT next action mapping")
    assert_true(context_twin["context"]["checkpoint"] == "CHK-2", "CONTEXT checkpoint mapping")
    assert_true(context_twin["timestamps"]["last_liveness_evidence_at"] == baseline_liveness, "CONTEXT must not create liveness")
    assert_true(context_twin["timestamps"]["last_progress_at"] == baseline_progress, "CONTEXT must not create progress")

    checkpoint_event, checkpoint_twin = apply(twin, {
        "response_type": "CHECKPOINT_RESPONSE",
        "message_id": "checkpoint-msg",
        "target_session_id": "session-a",
        "checkpoint_ref": "CHK-3",
        "current_action": "checkpointing",
        "observed_head": "a" * 40,
    }, "checkpoint")
    assert_true(checkpoint_event["event_type"] == "CHECKPOINT", "CHECKPOINT must map to CHECKPOINT")
    assert_true(checkpoint_twin["context"]["checkpoint"] == "CHK-3", "checkpoint response must enrich checkpoint context")
    assert_true(checkpoint_twin["timestamps"]["last_liveness_evidence_at"] == baseline_liveness, "CHECKPOINT snapshot must not create liveness")
    assert_true(checkpoint_twin["timestamps"]["last_progress_at"] == baseline_progress, "CHECKPOINT snapshot must not create progress")

    progress_event, progress_twin = apply(twin, {
        "response_type": "PROGRESS_RESPONSE",
        "message_id": "progress-msg",
        "target_session_id": "session-a",
        "last_progress_at": T1,
        "progress_marker": "STEP-B",
        "checkpoint_ref": "CHK-1",
        "work_item_ref": "TASK-1",
    }, "progress-snapshot")
    assert_true(progress_event["event_type"] == "PROGRESS", "PROGRESS response must map to PROGRESS")
    assert_true(progress_event["payload"]["qualifying_progress"] is False, "progress snapshot must be non-qualifying")
    assert_true(progress_event["payload"]["reported_last_progress_at"] == T1, "reported timestamp must be preserved")
    assert_true(progress_twin["timestamps"]["last_liveness_evidence_at"] == baseline_liveness, "PROGRESS snapshot must not create liveness")
    assert_true(progress_twin["timestamps"]["last_progress_at"] == baseline_progress, "PROGRESS snapshot must not create new progress")

    unavailable_event = control_response_to_gse_event({
        "response_type": "CONTEXT_RESPONSE",
        "message_id": "unavailable-msg",
        "target_session_id": "session-a",
        "repository": "UNAVAILABLE",
        "branch": "UNAVAILABLE",
        "observed_head": "UNAVAILABLE",
        "current_action": "UNAVAILABLE",
        "next_action": "UNAVAILABLE",
        "last_checkpoint": "UNAVAILABLE",
    }, observed_at=T2, event_id="unavailable")
    assert_true("repository" not in unavailable_event["payload"], "UNAVAILABLE repository must not overwrite known identity")
    assert_true("branch" not in unavailable_event["payload"], "UNAVAILABLE branch must not overwrite known identity")
    assert_true("observed_head" not in unavailable_event["payload"], "UNAVAILABLE head must not overwrite known identity")

    try:
        control_response_to_gse_event({
            "response_type": "TAKEOVER_OFFER_RECEIPT",
            "target_session_id": "session-a",
        }, observed_at=T2)
        raise AssertionError("unsupported response mapped into GSE")
    except ControlValidationError:
        pass

    print({
        "status": "GACR_INT_AUDIT_02_GSE_PROJECTION_UNIT_PASS",
        "status_no_false_liveness": True,
        "status_no_false_progress": True,
        "context_no_false_liveness": True,
        "context_no_false_progress": True,
        "checkpoint_snapshot_no_false_progress": True,
        "progress_snapshot_not_promoted": True,
        "unavailable_fails_closed": True,
    })


if __name__ == "__main__":
    main()
