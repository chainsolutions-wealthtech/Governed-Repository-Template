#!/usr/bin/env python3
from __future__ import annotations

from gscc_entry_router import route


def main() -> None:
    first = route("ARRIVAL")
    assert first["target"] == "00_GSCC_ENTRY.md", first
    assert first["next_step"] == "R1_PROVIDER_CONTEXT", first
    assert first["execute_next_automatically"] is False, first

    after_entry = route("00_GSCC_ENTRY.md")
    assert after_entry["action"] == "BUILD_OBSERVABLE_PACKET", after_entry
    assert after_entry["next_step"] == "R2_FIRST_TOUCH_CLASSIFICATION", after_entry

    first_touch = route("R1_PROVIDER_CONTEXT", "FIRST_TOUCH")
    assert first_touch["next_step"] == "R3_ENTRY_CONTRACT", first_touch

    continuation = route("R1_PROVIDER_CONTEXT", "CONTINUATION")
    assert continuation["next_step"] == "R3_ENTRY_CONTRACT", continuation

    unresolved = route("R1_PROVIDER_CONTEXT", "UNRESOLVED_ENTRY")
    assert unresolved["next_step"] == "BLOCK_UNRESOLVED", unresolved

    ready = route("R2_FIRST_TOUCH_CLASSIFICATION", "ENTRY_READY_FOR_Q1")
    assert ready["next_step"] == "R4_Q1_HANDOFF", ready

    blocked = route("R2_FIRST_TOUCH_CLASSIFICATION", "ENTRY_BLOCKED")
    assert blocked["next_step"] == "BLOCK_UNRESOLVED", blocked

    q1 = route("R3_ENTRY_CONTRACT", "READY_FOR_Q1")
    assert q1["next_step"] == "Q1", q1

    print("GSCC_ENTRY_ROUTER_TEST_PASS")


if __name__ == "__main__":
    main()
