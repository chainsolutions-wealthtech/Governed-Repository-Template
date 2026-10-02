#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from typing import Protocol


WORKER_A_CONTRACT = {
    "owner": "Presence/ConnectionEnvelope",
    "source_pr": 128,
    "module": "gacr_auto_attach",
    "apis": ["observe_presence", "build_connection_envelope", "bind_presence"],
}
WORKER_B_CONTRACT = {
    "owner": "Liveness/Progress/SessionContext",
    "source_pr": 127,
    "module": "gacr_agent_telemetry",
    "apis": ["worker_c_integration_projection", "interrogate_session", "session_signal_projection"],
}


class GACRWorkerAdapterV1(Protocol):
    """Adapter boundary over the separately-owned Worker A/B contracts."""

    def worker_a_first_touch(self) -> dict: ...
    def worker_a_controlled_stop(self) -> dict: ...
    def worker_b_context(self, session_id: str) -> dict: ...
    def reobserve_head(self, branch: str) -> dict: ...
    def accept_takeover(self, package: dict) -> dict: ...
    def continue_work(self) -> dict: ...


def harness_spec() -> dict:
    return {
        "schema": "gacr-e2e-takeover-harness/v1",
        "worker_api_contract": "GACR_WORKER_ADAPTER_V1",
        "shared_worker_contracts": {
            "worker_a": WORKER_A_CONTRACT,
            "worker_b": WORKER_B_CONTRACT,
        },
        "live_proof_status": "NOT_EXECUTED",
        "shared_integration_required": True,
        "shared_integration_note": (
            "SHARED_INTEGRATION_REQUIRED: reconcile PR #128 first, then bind Worker B "
            "PR #127 projections and this Worker C adapter without duplicating Presence/"
            "Envelope or Liveness/Progress ownership."
        ),
        "scenario_steps": [
            "AGENT_A_FIRST_TOUCH",
            "AGENT_A_WORK",
            "LIVENESS_PROGRESS",
            "CONTROLLED_STOP",
            "SUSPECTED_STALL",
            "STALLED",
            "TAKEOVER_READY",
            "AGENT_B_CONTEXT",
            "PREDECESSOR_RECONSTRUCTION",
            "EXACT_HEAD",
            "TAKEOVER_ACCEPT",
            "CONTINUATION",
        ],
        "required_assertions": {
            "presence_source": "WORKER_A_OBSERVE_PRESENCE",
            "session_context_source": "WORKER_B_WORKER_C_INTEGRATION_PROJECTION",
            "correlation": "FAIL_CLOSED_EXACT_OR_UNIQUE_STRONG_ONLY",
            "stall": "LEASE_EVIDENCE_NOT_PROVIDER_CAUSE",
            "claim_before_accept": "PREDECESSOR_RETAINS_OWNERSHIP",
            "head_mismatch": "REJECT",
            "head_exact": "ACCEPTANCE_MAY_PROCEED_IF_OTHER_GATES_PASS",
            "claim_after_accept": "TRANSFER_ONCE",
            "late_predecessor": "TERMINAL_NO_RESURRECTION",
            "in_flight_action": "RECONCILE_BEFORE_REPLAY",
            "wake": "ONLY_DECLARED_PROVIDER_OR_BRIDGE_CAPABILITY",
        },
        "ultimate_acceptance_gate": "STEPS_13_24_LIVE_PROOF_REQUIRED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepared GACR A→stall→B takeover harness")
    parser.add_argument("--describe", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.live:
        raise SystemExit(
            "GACR_E2E_LIVE_NOT_EXECUTED: SHARED_INTEGRATION_REQUIRED; "
            "merge/reconcile real Worker A/B APIs before Steps 13-24 proof"
        )
    print(json.dumps(harness_spec(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
