#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from typing import Protocol


class GACRWorkerAdapterV1(Protocol):
    """Integration seam for future Presence/Liveness Worker A/B APIs."""

    def first_touch(self) -> dict: ...
    def do_work(self) -> dict: ...
    def stop_controlled(self) -> dict: ...
    def get_context(self) -> dict: ...
    def reobserve_head(self) -> dict: ...
    def accept_takeover(self, package: dict) -> dict: ...
    def continue_work(self) -> dict: ...


def harness_spec() -> dict:
    return {
        "schema": "gacr-e2e-takeover-harness/v1",
        "worker_api_contract": "GACR_WORKER_ADAPTER_V1",
        "live_proof_status": "NOT_EXECUTED",
        "shared_integration_required": True,
        "shared_integration_note": (
            "SHARED_INTEGRATION_REQUIRED: bind this harness to the separately-owned "
            "Presence/Envelope Worker A and Liveness/Progress Worker B APIs after those "
            "surfaces are merged. This tranche does not own or emulate them."
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
            "bind real Worker A/B adapters before Steps 13-24 proof"
        )
    print(json.dumps(harness_spec(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
