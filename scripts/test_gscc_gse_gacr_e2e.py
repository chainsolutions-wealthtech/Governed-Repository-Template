#!/usr/bin/env python3
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from scripts.gscc import InMemoryTransport, SessionEndpoint
from scripts.gse.session_state_engine import reduce_event
from scripts.gscc_gacr import (
    DeterministicIdSource,
    GacrControlAdapter,
    control_response_to_gse_event,
)
from scripts.gscc_gacr.real_session_endpoint_adapter import GSCCSessionControlEndpoint


SESSION_ID = "session-e2e"
REPOSITORY = "chainsolutions-wealthtech/Governed-Repository-Template"
HEAD = "a" * 40
BASE_NOW = datetime.now(timezone.utc).replace(microsecond=0)


def _z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


T0 = _z(BASE_NOW - timedelta(minutes=3))
T1 = _z(BASE_NOW - timedelta(minutes=2))
T2 = _z(BASE_NOW - timedelta(minutes=1))
T3 = _z(BASE_NOW)
T4 = _z(BASE_NOW + timedelta(seconds=1))
T5 = _z(BASE_NOW + timedelta(seconds=2))
T6 = _z(BASE_NOW + timedelta(seconds=3))
T7 = _z(BASE_NOW + timedelta(seconds=4))
T8 = _z(BASE_NOW + timedelta(seconds=5))


class ManualClock:
    def __init__(self, value: str) -> None:
        self.value = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

    def __call__(self) -> datetime:
        return self.value

    def set(self, value: str) -> None:
        self.value = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def assert_true(value, message: str) -> None:
    if not value:
        raise AssertionError("GSCC_GSE_GACR_E2E_FAILED: " + message)


def as_gse_event(message, observed_at: str, event_id: str):
    return {
        "event_id": event_id,
        "message_id": message.message_id,
        "event_type": message.type,
        "observed_at": observed_at,
        "payload": dict(message.payload),
    }


def dispatch_query(control, bridge, clock, observed_at, command_type, twin, event_id):
    clock.set(observed_at)
    command = control.build_command(command_type, SESSION_ID)
    record = control.dispatch_command(command, bridge)
    assert_true(record["state"] == "COMPLETED", f"{command_type} must complete through real SessionEndpoint")
    assert_true(record["ack"] is not None, f"{command_type} must return correlated GSCC ACK")
    assert_true(record["response"] is not None, f"{command_type} must return safe control response")
    event = control_response_to_gse_event(record["response"], observed_at=observed_at, event_id=event_id)
    return record, event, reduce_event(twin, event)


def main() -> None:
    transport = InMemoryTransport()
    endpoint = SessionEndpoint(
        transport,
        source={
            "session_id": SESSION_ID,
            "client_instance_id": "client-e2e",
            "provider": "controlled-e2e",
        },
        target={"system": "gacr"},
        scope={
            "repository": REPOSITORY,
            "branch": "governance/gacr-int-audit-02-control-response-gse",
            "observed_head": HEAD,
            "task_id": "GACR-STEP-13B-PREP",
        },
        capabilities=[
            "COMMAND_RECEIVE",
            "CHALLENGE_RESPONSE",
            "STATUS_RESPONSE",
            "PROGRESS_REPORT",
            "CONTEXT_REPORT",
            "CHECKPOINT_REPORT",
        ],
    )

    attach = endpoint.attach(
        session_identity=SESSION_ID,
        repository=REPOSITORY,
        task="GACR-STEP-13B-PREP",
        branch="governance/gacr-int-audit-02-control-response-gse",
        observed_head=HEAD,
        last_action="integration-e2e",
        checkpoint="CHK-E2E-1",
        next_action="challenge-session",
    )["message"]
    heartbeat = endpoint.heartbeat(seq=1)["message"]
    progress = endpoint.progress(
        previous_phase="INTEGRATION",
        current_phase="CONTROL_E2E",
        completed_step_ref="GSCC_GSE_BINDING",
        next_step_ref="LIVENESS_CHALLENGE",
    )["message"]

    twin = None
    twin = reduce_event(twin, as_gse_event(attach, T0, "attach"))
    twin = reduce_event(twin, as_gse_event(heartbeat, T1, "heartbeat"))
    twin = reduce_event(twin, as_gse_event(progress, T2, "progress"))

    assert_true(twin["presence"]["state"] == "PRESENT", "first-touch session must be present")
    assert_true(twin["liveness"]["state"] == "ACTIVE", "heartbeat must establish active liveness")
    assert_true(twin["progress"]["state"] == "ADVANCING", "semantic progress must be independent and advancing")
    assert_true(twin["continuity"]["state"] == "SUFFICIENT", "session twin must contain sufficient resume context")

    clock = ManualClock(T3)
    control = GacrControlAdapter(
        clock=clock,
        id_source=DeterministicIdSource("e2e"),
        default_ttl_seconds=60,
    )
    bridge = GSCCSessionControlEndpoint(
        endpoint,
        transport,
        status={
            "current_state": "ACTIVE",
            "current_action": "inspect controlled status",
            "current_tool": "github",
            "observed_head": HEAD,
            "last_progress_at": T2,
            "blocker": "UNAVAILABLE",
        },
        progress={
            "last_progress_at": T2,
            "progress_marker": "GSCC_GSE_BINDING",
            "checkpoint_ref": "CHK-E2E-1",
            "work_item_ref": "GACR-STEP-13B-PREP",
        },
        context={
            "objective_ref": "GACR-PRE-13B",
            "current_phase": "CONTROL_RESPONSE_PROJECTION",
            "current_action": "project safe context",
            "last_checkpoint": "CHK-E2E-CONTEXT",
            "next_action": "prove checkpoint snapshot",
            "repository": REPOSITORY,
            "branch": "governance/gacr-int-audit-02-control-response-gse",
            "observed_head": HEAD,
        },
        checkpoint={
            "checkpoint_ref": "CHK-E2E-2",
            "current_action": "checkpoint snapshot",
            "observed_head": HEAD,
        },
    )

    issued = clock()
    command = control.build_command(
        "LIVENESS_CHALLENGE",
        SESSION_ID,
        payload={
            "challenge_id": "challenge-1",
            "nonce": "nonce-1",
            "issued_at": issued.isoformat(),
            "expires_at": (issued + timedelta(seconds=30)).isoformat(),
        },
    )
    record = control.dispatch_command(command, bridge)
    assert_true(record["state"] == "COMPLETED", "real GSCC endpoint challenge must complete")
    assert_true(record["ack"]["ack_status"] == "ACK", "GSCC ACK must correlate to control command")
    assert_true(record["response"]["response_type"] == "CHALLENGE_RESPONSE", "challenge response must return")
    assert_true(record["response"]["fresh_liveness"] is True, "first nonce must be fresh liveness")

    twin = reduce_event(
        twin,
        {
            "event_id": "challenge-response-1",
            "event_type": "CHALLENGE_RESPONSE",
            "observed_at": T3,
            "payload": {
                **record["response"],
                "delivery_state": "ACKNOWLEDGED",
            },
        },
    )
    assert_true(twin["control_channel"]["state"] == "REACHABLE", "challenge ACK must make control channel reachable")
    assert_true(twin["timestamps"]["last_liveness_evidence_at"] == T3, "fresh challenge must refresh liveness")

    clock.set(T4)
    issued = clock()
    replay_command = control.build_command(
        "LIVENESS_CHALLENGE",
        SESSION_ID,
        payload={
            "challenge_id": "challenge-2",
            "nonce": "nonce-1",
            "issued_at": issued.isoformat(),
            "expires_at": (issued + timedelta(seconds=30)).isoformat(),
        },
    )
    replay_record = control.dispatch_command(replay_command, bridge)
    assert_true(replay_record["response"]["replay"] is True, "duplicate nonce must be identified as replay")
    assert_true(replay_record["response"]["fresh_liveness"] is False, "replay must never be fresh liveness")

    twin = reduce_event(
        twin,
        {
            "event_id": "challenge-response-replay",
            "event_type": "CHALLENGE_RESPONSE",
            "observed_at": T4,
            "payload": {
                **replay_record["response"],
                "delivery_state": "ACKNOWLEDGED",
            },
        },
    )
    assert_true(twin["timestamps"]["last_liveness_evidence_at"] == T3, "replayed challenge must not refresh liveness")
    assert_true(twin["timestamps"]["last_progress_at"] == T2, "challenge traffic must not manufacture progress")

    baseline_liveness = twin["timestamps"]["last_liveness_evidence_at"]
    baseline_progress = twin["timestamps"]["last_progress_at"]

    status_record, status_event, twin = dispatch_query(
        control, bridge, clock, T5, "STATUS_REQUEST", twin, "status-response"
    )
    assert_true(status_record["response"]["response_type"] == "STATUS_RESPONSE", "STATUS response type")
    assert_true(status_event["event_type"] == "CONTEXT_UPDATE", "STATUS maps into canonical CONTEXT_UPDATE")
    assert_true(twin["context"]["last_action"] == "inspect controlled status", "STATUS enriches context")
    assert_true(twin["timestamps"]["last_liveness_evidence_at"] == baseline_liveness, "STATUS must not create liveness")
    assert_true(twin["timestamps"]["last_progress_at"] == baseline_progress, "STATUS must not create progress")

    context_record, context_event, twin = dispatch_query(
        control, bridge, clock, T6, "CONTEXT_REQUEST", twin, "context-response"
    )
    assert_true(context_record["response"]["response_type"] == "CONTEXT_RESPONSE", "CONTEXT response type")
    assert_true(context_event["event_type"] == "CONTEXT_UPDATE", "CONTEXT maps into canonical CONTEXT_UPDATE")
    assert_true(twin["context"]["last_action"] == "project safe context", "CONTEXT current action projected")
    assert_true(twin["context"]["next_action"] == "prove checkpoint snapshot", "CONTEXT next action projected")
    assert_true(twin["context"]["checkpoint"] == "CHK-E2E-CONTEXT", "CONTEXT checkpoint projected")
    assert_true(twin["timestamps"]["last_liveness_evidence_at"] == baseline_liveness, "CONTEXT must not create liveness")
    assert_true(twin["timestamps"]["last_progress_at"] == baseline_progress, "CONTEXT must not create progress")

    checkpoint_record, checkpoint_event, twin = dispatch_query(
        control, bridge, clock, T7, "CHECKPOINT_REQUEST", twin, "checkpoint-response"
    )
    assert_true(checkpoint_record["response"]["response_type"] == "CHECKPOINT_RESPONSE", "CHECKPOINT response type")
    assert_true(checkpoint_event["event_type"] == "CHECKPOINT", "CHECKPOINT maps into canonical CHECKPOINT")
    assert_true(twin["context"]["checkpoint"] == "CHK-E2E-2", "CHECKPOINT snapshot projected")
    assert_true(twin["timestamps"]["last_checkpoint_at"] == T7, "checkpoint observation timestamp projected")
    assert_true(twin["timestamps"]["last_liveness_evidence_at"] == baseline_liveness, "CHECKPOINT must not create liveness")
    assert_true(twin["timestamps"]["last_progress_at"] == baseline_progress, "CHECKPOINT snapshot must not create progress")

    progress_record, progress_event, twin = dispatch_query(
        control, bridge, clock, T8, "PROGRESS_REQUEST", twin, "progress-response"
    )
    assert_true(progress_record["response"]["response_type"] == "PROGRESS_RESPONSE", "PROGRESS response type")
    assert_true(progress_event["event_type"] == "PROGRESS", "PROGRESS response maps into canonical PROGRESS")
    assert_true(progress_event["payload"]["qualifying_progress"] is False, "progress snapshot is explicitly non-qualifying")
    assert_true(progress_event["payload"]["reported_last_progress_at"] == T2, "reported historical progress preserved")
    assert_true(twin["timestamps"]["last_liveness_evidence_at"] == baseline_liveness, "PROGRESS query must not create liveness")
    assert_true(twin["timestamps"]["last_progress_at"] == baseline_progress, "PROGRESS query must not create new progress")

    assert_true(twin["presence"]["state"] == "PRESENT", "safe control responses remain presence evidence")
    assert_true(twin["control_channel"]["state"] == "REACHABLE", "control channel remains reachable")
    assert_true(twin["continuity"]["state"] == "SUFFICIENT", "safe query responses preserve sufficient continuity")

    print({
        "status": "GSCC_GSE_GACR_CONTROLLED_E2E_PASS",
        "session_id": SESSION_ID,
        "presence": twin["presence"]["state"],
        "control_channel": twin["control_channel"]["state"],
        "last_liveness_evidence_at": twin["timestamps"]["last_liveness_evidence_at"],
        "last_progress_at": twin["timestamps"]["last_progress_at"],
        "status_response_to_gse": True,
        "progress_response_to_gse": True,
        "context_response_to_gse": True,
        "checkpoint_response_to_gse": True,
        "query_responses_created_false_liveness": False,
        "query_responses_created_false_progress": False,
        "replay_refreshed_liveness": False,
        "mutation_authority_granted": False,
        "fresh_provider_proof": False,
    })


if __name__ == "__main__":
    main()
