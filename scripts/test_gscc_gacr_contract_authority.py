#!/usr/bin/env python3
from __future__ import annotations

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from scripts.gscc import protocol as canonical
from scripts.gscc_gacr import contract
from scripts.gscc_gacr.contract import ControlValidationError


def assert_true(value, message: str) -> None:
    if not value:
        raise AssertionError("GSCC_GACR_CONTRACT_AUTHORITY_FAILED: " + message)


def main() -> None:
    assert_true(contract.EVENTS is canonical.EVENT_TYPES, "EVENTS must alias canonical EVENT_TYPES")
    assert_true(contract.COMMANDS is canonical.COMMAND_TYPES, "COMMANDS must alias canonical COMMAND_TYPES")
    assert_true(
        contract.DELIVERY_STATES is canonical.DELIVERY_STATES,
        "DELIVERY_STATES must alias canonical GSCC DELIVERY_STATES",
    )
    assert_true(
        contract.TERMINAL_STATES is canonical.TERMINAL_DELIVERY_STATES,
        "TERMINAL_STATES must alias canonical terminal delivery states",
    )

    source = inspect.getsource(contract)
    for forbidden_declaration in (
        "EVENTS = (",
        "COMMANDS = (",
        "DELIVERY_STATES = (",
        "TERMINAL_STATES = {",
        "FORBIDDEN_KEY_FRAGMENTS =",
        "FORBIDDEN_EXACT_KEYS =",
    ):
        assert_true(
            forbidden_declaration not in source,
            f"duplicate shared protocol declaration remains: {forbidden_declaration}",
        )

    # Prove both directions of compatibility:
    # - raw_prompt existed only in the canonical GSCC policy;
    # - browser_session / conversation_text / page_content were historical
    #   control restrictions and must now be enforced by the canonical policy.
    for forbidden_key in ("raw_prompt", "browser_session", "conversation_text", "page_content"):
        try:
            contract.validate_safe_payload({forbidden_key: "must-never-cross-control"})
            raise AssertionError(f"unsafe payload was accepted: {forbidden_key}")
        except ControlValidationError:
            pass

    canonical_commands_before = canonical.COMMAND_TYPES
    assert_true(
        contract.COMMANDS is canonical_commands_before,
        "control contract must remain bound to canonical command authority",
    )

    print({
        "status": "GACR_INT_AUDIT_01_CONTRACT_AUTHORITY_PASS",
        "single_shared_protocol_authority": "scripts/gscc/protocol.py",
        "events_alias": True,
        "commands_alias": True,
        "delivery_states_alias": True,
        "terminal_states_alias": True,
        "safe_payload_delegated": True,
    })


if __name__ == "__main__":
    main()
