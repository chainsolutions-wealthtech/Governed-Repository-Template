#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from gscc_gacr import (
    ControlValidationError,
    DeterministicIdSource,
    FakeSessionEndpoint,
    GacrControlAdapter,
)

LIVE_STORE_NAMES = (
    "gacr-sessions.json",
    "gacr-claims.json",
    "gacr-beacons.json",
    "gacr-correlations.json",
    "gacr-dispatches.json",
    "gacr-forensics.json",
    "gacr-takeovers.json",
)


class ManualClock:
    def __init__(self) -> None:
        self.value = datetime(2026, 10, 2, 5, 0, 0, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.value

    def advance(self, seconds: int) -> None:
        self.value += timedelta(seconds=seconds)


def assert_true(value, message: str) -> None:
    if not value:
        raise AssertionError("GSCC_GACR_CONTROL_TEST_FAILED: " + message)


def live_store_snapshot() -> dict[str, bytes | None]:
    base = ROOT / ".governance" / "control-plane-state"
    return {
        name: (base / name).read_bytes() if (base / name).exists() else None
        for name in LIVE_STORE_NAMES
    }


def adapter_fixture(*, scenarios=None):
    clock = ManualClock()
    adapter = GacrControlAdapter(
        clock=clock,
        id_source=DeterministicIdSource("test"),
        default_ttl_seconds=30,
    )
    endpoint = FakeSessionEndpoint(
        "session-a",
        scenarios=scenarios,
        status={
            "current_state": "ACTIVE",
            "current_action": "implement harness",
            "current_tool": "github",
            "observed_head": "a" * 40,
            "last_progress_at": "2026-10-02T04:59:00+00:00",
        },
        progress={
            "last_progress_at": "2026-10-02T04:59:00+00:00",
            "progress_marker": "tests-written",
            "checkpoint_ref": "CHK-GSCC-GACR-1",
            "work_item_ref": "GSCC-GACR-V1",
        },
        context={
            "objective_ref": "GSCC-GACR-BIDIRECTIONAL-V1",
            "current_phase": "IMPLEMENTATION",
            "current_action": "implement harness",
            "last_checkpoint": "CHK-GSCC-GACR-1",
            "next_action": "run tests",
            "repository": "chainsolutions-wealthtech/Governed-Repository-Template",
            "branch": "governance/gscc-gacr-bidirectional-control-v1",
            "observed_head": "a" * 40,
        },
        checkpoint={
            "checkpoint_ref": "CHK-GSCC-GACR-2",
            "current_action": "checkpointing",
            "observed_head": "a" * 40,
        },
        blocker={
            "blocked": True,
            "blocker_class": "TOOL_FAILURE",
            "blocker_ref": "tool:fixture",
        },
        handoff={
            "checkpoint_ref": "CHK-GSCC-GACR-2",
            "current_action": "prepare handoff",
            "observed_head": "a" * 40,
            "safe_context_ref": "context:fixture",
        },
        observed_head="a" * 40,
    )
    return clock, adapter, endpoint


def command(adapter, kind, *, payload=None, target="session-a", ttl=30, correlation_id=None):
    return adapter.build_command(
        kind,
        target,
        payload=payload,
        ttl_seconds=ttl,
        correlation_id=correlation_id,
    )


def assert_lifecycle(record, required):
    states = [item["state"] for item in record["history"]]
    cursor = 0
    for state in states:
        if cursor < len(required) and state == required[cursor]:
            cursor += 1
    assert_true(cursor == len(required), f"lifecycle missing {required}; got {states}")


def test_ping_and_identity():
    _, adapter, endpoint = adapter_fixture()
    cmd = command(adapter, "PING")
    required_identity = {
        "message_id",
        "correlation_id",
        "command_id",
        "target_session_id",
        "issued_at",
        "expires_at",
        "requires_ack",
    }
    assert_true(required_identity <= set(cmd), "PING command identity contract")
    result = adapter.dispatch_command(cmd, endpoint)
    assert_true(result["state"] == "COMPLETED", "PING must complete")
    assert_lifecycle(result, ["CREATED", "QUEUED", "DISPATCHED", "DELIVERED", "ACKNOWLEDGED", "COMPLETED"])
    assert_true(result["ack"]["command_id"] == cmd["command_id"], "PING ACK command correlation")
    assert_true(result["ack"]["target_session_id"] == "session-a", "PING exact target")
    assert_true(cmd["mutation_authority_granted"] is False, "control command never grants mutation authority")


def test_challenge_matrix_and_nonce_replay():
    for scenario in ["ACK", "BUSY", "IDLE", "CHECKPOINTING", "TERMINATING", "UNSUPPORTED"]:
        clock, adapter, endpoint = adapter_fixture(scenarios={"LIVENESS_CHALLENGE": scenario})
        payload = {
            "challenge_id": f"challenge-{scenario.lower()}",
            "nonce": f"nonce-{scenario.lower()}",
            "issued_at": clock().isoformat(),
            "expires_at": (clock() + timedelta(seconds=20)).isoformat(),
        }
        result = adapter.dispatch_command(command(adapter, "LIVENESS_CHALLENGE", payload=payload), endpoint)
        assert_true(result["response"]["challenge_status"] == scenario, f"challenge {scenario}")
        expected = "UNSUPPORTED" if scenario == "UNSUPPORTED" else "COMPLETED"
        assert_true(result["state"] == expected, f"challenge terminal {scenario}")

    clock, adapter, endpoint = adapter_fixture(scenarios={"LIVENESS_CHALLENGE": "NO_RESPONSE"})
    payload = {
        "challenge_id": "challenge-no-response",
        "nonce": "nonce-no-response",
        "issued_at": clock().isoformat(),
        "expires_at": (clock() + timedelta(seconds=20)).isoformat(),
    }
    cmd = command(adapter, "LIVENESS_CHALLENGE", payload=payload, ttl=10)
    result = adapter.dispatch_command(cmd, endpoint)
    assert_true(result["state"] == "DELIVERED", "NO_RESPONSE stays delivered until expiry")
    clock.advance(11)
    result = adapter.expire_command(cmd["command_id"])
    assert_true(result["state"] == "NO_RESPONSE", "NO_RESPONSE after delivery expiry")

    clock, adapter, endpoint = adapter_fixture()
    payload = {
        "challenge_id": "challenge-replay",
        "nonce": "nonce-replay",
        "issued_at": clock().isoformat(),
        "expires_at": (clock() + timedelta(seconds=20)).isoformat(),
    }
    first = adapter.dispatch_command(command(adapter, "LIVENESS_CHALLENGE", payload=payload), endpoint)
    assert_true(first["response"]["fresh_liveness"] is True, "first nonce is fresh")
    second_payload = dict(payload)
    second_payload["challenge_id"] = "challenge-replay-2"
    second = adapter.dispatch_command(command(adapter, "LIVENESS_CHALLENGE", payload=second_payload), endpoint)
    assert_true(second["response"]["replay"] is True, "nonce replay recognized")
    assert_true(second["response"]["fresh_liveness"] is False, "nonce replay is never fresh proof")


def test_expiry_duplicates_and_correlation():
    clock, adapter, endpoint = adapter_fixture()
    cmd = command(adapter, "PING", ttl=5)
    clock.advance(6)
    expired = adapter.dispatch_command(cmd, endpoint)
    assert_true(expired["state"] == "EXPIRED", "expired command must not execute")
    assert_true("EXECUTING" not in [x["state"] for x in expired["history"]], "expired command never executing")

    _, adapter, endpoint = adapter_fixture()
    cmd = command(adapter, "PING")
    first = adapter.dispatch_command(cmd, endpoint)
    second = adapter.dispatch_command(cmd, endpoint)
    assert_true(second["dispatch_count"] == 1, "duplicate command is not re-sent")
    assert_true(first["state"] == second["state"] == "COMPLETED", "duplicate command is idempotent")

    ack = dict(first["ack"])
    before = len(adapter.audit_trail(cmd["command_id"]))
    duplicate = adapter.record_external_ack(cmd["command_id"], ack)
    after = len(duplicate["history"])
    assert_true(after == before + 1, "duplicate ACK is audited idempotently")
    assert_true(duplicate["history"][-1]["detail"] == "DUPLICATE_ACK_IDEMPOTENT", "duplicate ACK detail")

    _, adapter, endpoint = adapter_fixture()
    bad_target_cmd = command(adapter, "PING", target="session-b")
    try:
        adapter.dispatch_command(bad_target_cmd, endpoint)
        raise AssertionError("wrong target accepted")
    except ControlValidationError:
        pass
    assert_true(endpoint.receive() is None, "wrong target command must not be consumed")

    _, adapter, endpoint = adapter_fixture()
    cmd = command(adapter, "PING", correlation_id="corr-a")
    result = adapter.dispatch_command(cmd, endpoint)
    bad_ack = dict(result["ack"])
    bad_ack["correlation_id"] = "corr-b"
    try:
        adapter.record_external_ack(cmd["command_id"], bad_ack)
        raise AssertionError("wrong correlation accepted")
    except ControlValidationError:
        pass
    assert_true(adapter.snapshot(cmd["command_id"])["state"] == "FAILED", "wrong correlation rejected")


def test_query_commands():
    _, adapter, endpoint = adapter_fixture()
    status = adapter.dispatch_command(command(adapter, "STATUS_REQUEST"), endpoint)
    assert_true(status["response"]["current_state"] == "ACTIVE", "STATUS_REQUEST state")
    assert_true(status["response"]["current_tool"] == "github", "STATUS_REQUEST tool")

    progress = adapter.dispatch_command(command(adapter, "PROGRESS_REQUEST"), endpoint)
    assert_true(progress["response"]["progress_marker"] == "tests-written", "PROGRESS_REQUEST marker")
    assert_true(progress["response"]["checkpoint_ref"] == "CHK-GSCC-GACR-1", "PROGRESS_REQUEST checkpoint")

    context = adapter.dispatch_command(command(adapter, "CONTEXT_REQUEST"), endpoint)
    assert_true(context["response"]["repository"].endswith("Governed-Repository-Template"), "CONTEXT_REQUEST repository")
    assert_true("raw_transcript" not in context["response"], "CONTEXT_REQUEST no transcript")

    checkpoint = adapter.dispatch_command(command(adapter, "CHECKPOINT_REQUEST"), endpoint)
    assert_true(checkpoint["response"]["checkpoint_ref"] == "CHK-GSCC-GACR-2", "CHECKPOINT_REQUEST response")
    assert_lifecycle(checkpoint, ["DELIVERED", "ACKNOWLEDGED", "EXECUTING", "COMPLETED"])

    for scenario, expected in [("FAILED", "FAILED"), ("DECLINED", "DECLINED"), ("EXPIRED", "EXPIRED")]:
        _, cp_adapter, cp_endpoint = adapter_fixture(scenarios={"CHECKPOINT_REQUEST": scenario})
        cp_result = cp_adapter.dispatch_command(command(cp_adapter, "CHECKPOINT_REQUEST"), cp_endpoint)
        assert_true(cp_result["state"] == expected, f"CHECKPOINT_REQUEST {scenario}")

    head = adapter.dispatch_command(command(adapter, "REOBSERVE_HEAD"), endpoint)
    assert_true(head["response"]["observed_head"] == "a" * 40, "REOBSERVE_HEAD response")
    assert_true(head["response"]["mutation_authority_granted"] is False, "REOBSERVE_HEAD grants no authority")

    blocker = adapter.dispatch_command(command(adapter, "REPORT_BLOCKER"), endpoint)
    assert_true(blocker["response"]["blocked"] is True, "REPORT_BLOCKER explicit blocked")
    assert_true(blocker["response"]["blocker_class"] == "TOOL_FAILURE", "REPORT_BLOCKER class")

    _, unknown_adapter, unknown_endpoint = adapter_fixture()
    unknown_endpoint.blocker_payload = {}
    unknown = unknown_adapter.dispatch_command(command(unknown_adapter, "REPORT_BLOCKER"), unknown_endpoint)
    assert_true(unknown["response"]["blocked"] == "UNAVAILABLE", "REPORT_BLOCKER must not fabricate unknown blocker")


def test_supervisor_instruction_matrix():
    for scenario, expected in [
        ("ACK", "COMPLETED"),
        ("FAILED", "FAILED"),
        ("DECLINED", "DECLINED"),
        ("EXPIRED", "EXPIRED"),
    ]:
        _, adapter, endpoint = adapter_fixture(scenarios={"SUPERVISOR_INSTRUCTION": scenario})
        cmd = command(adapter, "SUPERVISOR_INSTRUCTION", payload={"instruction_ref": f"instruction:{scenario.lower()}"})
        result = adapter.dispatch_command(cmd, endpoint)
        assert_true(result["state"] == expected, f"SUPERVISOR_INSTRUCTION {scenario}")
        if scenario == "ACK":
            assert_lifecycle(result, ["ACKNOWLEDGED", "EXECUTING", "COMPLETED"])

    clock, adapter, endpoint = adapter_fixture(scenarios={"SUPERVISOR_INSTRUCTION": "NO_RESPONSE"})
    cmd = command(adapter, "SUPERVISOR_INSTRUCTION", payload={"instruction_ref": "instruction:no-response"}, ttl=5)
    result = adapter.dispatch_command(cmd, endpoint)
    assert_true(result["state"] == "DELIVERED", "instruction no-response delivered")
    clock.advance(6)
    assert_true(adapter.expire_command(cmd["command_id"])["state"] == "NO_RESPONSE", "instruction no-response terminal")


def test_pause_resume_handoff_takeover_and_authority_boundary():
    _, adapter, endpoint = adapter_fixture()
    paused = adapter.dispatch_command(command(adapter, "PAUSE"), endpoint)
    assert_true(paused["response"]["paused"] is True, "PAUSE transport state")
    assert_true(paused["response"]["mutation_authority_granted"] is False, "PAUSE no mutation authority")
    resumed = adapter.dispatch_command(command(adapter, "RESUME"), endpoint)
    assert_true(resumed["response"]["paused"] is False, "RESUME transport state")
    assert_true(resumed["response"]["mutation_authority_granted"] is False, "RESUME no mutation authority")

    handoff = adapter.dispatch_command(command(adapter, "HANDOFF_PREPARE"), endpoint)
    assert_true(handoff["response"]["checkpoint_ref"] == "CHK-GSCC-GACR-2", "HANDOFF_PREPARE checkpoint")
    assert_true(handoff["response"]["session_closed"] is False, "HANDOFF_PREPARE does not close session")

    offer_payload = {
        "predecessor_session_id": "session-stalled",
        "may_write": False,
        "requires_exact_head_reconciliation": True,
        "requires_takeover_accept": True,
    }
    offer = adapter.dispatch_command(command(adapter, "TAKEOVER_OFFER", payload=offer_payload), endpoint)
    assert_true(offer["response"]["offer_received"] is True, "TAKEOVER_OFFER received")
    assert_true(offer["response"]["may_write"] is False, "TAKEOVER_OFFER may_write false")
    assert_true(offer["response"]["claim_transferred"] is False, "TAKEOVER_OFFER transfers no claim")
    assert_true(offer["response"]["requires_exact_head_reconciliation"] is True, "TAKEOVER exact-HEAD preserved")
    assert_true(offer["response"]["requires_takeover_accept"] is True, "TAKEOVER accept remains explicit")

    try:
        command(adapter, "TAKEOVER_OFFER", payload={
            "may_write": True,
            "requires_exact_head_reconciliation": True,
            "requires_takeover_accept": True,
        })
        raise AssertionError("unsafe TAKEOVER_OFFER accepted")
    except ControlValidationError:
        pass


def test_credential_boundary():
    _, adapter, _ = adapter_fixture()
    forbidden = [
        {"token": "x"},
        {"secret_value": "x"},
        {"authorization": "Bearer x"},
        {"cookie": "x"},
        {"browser_session": "x"},
        {"password": "x"},
        {"private_key": "x"},
        {"raw_transcript": "x"},
        {"private_reasoning": "x"},
    ]
    for payload in forbidden:
        try:
            command(adapter, "SUPERVISOR_INSTRUCTION", payload=payload)
            raise AssertionError(f"forbidden payload accepted: {payload}")
        except ControlValidationError:
            pass


def test_external_bridge_backward_compatibility():
    notifier = importlib.import_module("gacr_bridge_notifier")
    item = {
        "dispatch_id": "GACR-D-fixture",
        "target_session_id": "session-a",
        "target_client_instance_id": "client-a",
        "bridge_registration_ref": "bridge-a",
        "task_id": "TASK-1",
        "branch": "feature/a",
        "pull_request": 42,
        "takeover_id": "GACR-T-fixture",
        "stalled_session_id": "session-stalled",
    }
    payload = notifier.build_payload("owner/repo", item)
    assert_true(payload["event"] == "GACR_TAKEOVER_READY", "legacy bridge event unchanged")
    assert_true(payload["dispatch_id"] == "GACR-D-fixture", "legacy dispatch id unchanged")
    assert_true(payload["delivery"]["idempotency_key"] == "GACR-D-fixture", "legacy bridge idempotency unchanged")
    assert_true(payload["delivery"]["requires_context_fetch"] is True, "legacy context-fetch contract unchanged")
    assert_true(payload["delivery"]["may_write"] is False, "legacy bridge still grants no write")


def main():
    before = live_store_snapshot()

    test_ping_and_identity()
    test_challenge_matrix_and_nonce_replay()
    test_expiry_duplicates_and_correlation()
    test_query_commands()
    test_supervisor_instruction_matrix()
    test_pause_resume_handoff_takeover_and_authority_boundary()
    test_credential_boundary()
    test_external_bridge_backward_compatibility()

    after = live_store_snapshot()
    assert_true(before == after, "test harness must not mutate live GACR stores")

    print(json.dumps({
        "status": "GSCC_GACR_BIDIRECTIONAL_CONTROL_TEST_PASS",
        "live_gacr_state_touched": False,
        "exact_head_bypass": False,
        "claim_transfer_from_control_message": False,
        "fake_endpoint_is_live_provider_proof": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
