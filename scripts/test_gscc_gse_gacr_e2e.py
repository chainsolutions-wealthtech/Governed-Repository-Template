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
from scripts.gscc_gacr import DeterministicIdSource, GacrControlAdapter
from scripts.gscc_gacr.real_session_endpoint_adapter import GSCCSessionControlEndpoint


SESSION_ID = "session-e2e"
REPOSITORY = "chainsolutions-wealthtech/Governed-Repository-Template"
HEAD = "a" * 40
T0 = "2026-10-02T05:00:00Z"
T1 = "2026-10-02T05:01:00Z"
T2 = "2026-10-02T05:02:00Z"
T3 = "2026-10-02T05:03:00Z"
T4 = "2026-10-02T05:04:00Z"


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
            "branch": "governance/integrate-gscc-gse-gacr-control",
            "observed_head": HEAD,
            "task_id": "GACR-STEP-13B-PREP",
        },
        capabilities=["COMMAND_RECEIVE", "CHALLENGE_RESPONSE"],
    )

    attach = endpoint.attach(
        session_identity=SESSION_ID,
        repository=REPOSITORY,
        task="GACR-STEP-13B-PREP",
        branch="governance/integrate-gscc-gse-gacr-control",
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
    bridge = GSCCSessionControlEndpoint(endpoint, transport)

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
    assert_true(twin["progress"]["state"] != "ADVANCING" or twin["timestamps"]["last_progress_at"] == T2,
                "control traffic must not manufacture progress")

    print({
        "status": "GSCC_GSE_GACR_CONTROLLED_E2E_PASS",
        "session_id": SESSION_ID,
        "presence": twin["presence"]["state"],
        "control_channel": twin["control_channel"]["state"],
        "last_liveness_evidence_at": twin["timestamps"]["last_liveness_evidence_at"],
        "last_progress_at": twin["timestamps"]["last_progress_at"],
        "replay_refreshed_liveness": False,
        "mutation_authority_granted": False,
        "fresh_provider_proof": False,
    })


if __name__ == "__main__":
    main()
