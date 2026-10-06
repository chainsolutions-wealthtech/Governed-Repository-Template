#!/usr/bin/env python3
from __future__ import annotations

from gscc_entry_router import route


def main() -> None:
    first = route("ARRIVAL")
    assert first["target"] == "00_GSCC_ENTRY.md", first
    assert first["next_step"] == "R1_PROVIDER_CONTEXT", first
    assert first["execute_next_automatically"] is False, first

    after_entry = route("00_GSCC_ENTRY.md")
    assert after_entry["action"] == "REPORT_PROVIDER_CONTEXT", after_entry
    assert after_entry["next_step"] == "R2_ENTRY_CONTRACT", after_entry

    ready = route("R1_PROVIDER_CONTEXT", "ENTRY_READY_FOR_Q1")
    assert ready["next_step"] == "R3_Q1_HANDOFF", ready

    blocked = route("R1_PROVIDER_CONTEXT", "ENTRY_BLOCKED")
    assert blocked["next_step"] == "BLOCK_UNRESOLVED", blocked

    q1 = route("R2_ENTRY_CONTRACT", "READY_FOR_Q1")
    assert q1["next_step"] == "Q1", q1

    print("GSCC_ENTRY_ROUTER_TEST_PASS")


if __name__ == "__main__":
    main()
