#!/usr/bin/env python3
from __future__ import annotations

from gscc_entry_router import route


def main() -> None:
    first = route("ARRIVAL")
    assert first["target"] == "00_GSCC_ENTRY.md", first
    assert first["next_step"] == "R1_PROVIDER_CONTEXT", first
    assert first["execute_next_automatically"] is False, first

    after_entry = route("00_GSCC_ENTRY.md")
    assert after_entry["action"] == "RUN_PERSISTED_ENTRY_PIPELINE", after_entry
    assert after_entry["target"] == "scripts/gscc_persisted_entry_pipeline.py", after_entry
    assert after_entry["next_step"] == "Q1", after_entry
    assert after_entry["execute_next_automatically"] is False, after_entry

    blocked = route("00_GSCC_ENTRY.md", "ENTRY_BLOCKED")
    assert blocked["next_step"] == "BLOCK_UNRESOLVED", blocked

    stopped = route("BLOCK_UNRESOLVED")
    assert stopped["action"] == "STOP_FAIL_CLOSED", stopped
    assert stopped["next_step"] is None, stopped

    print("GSCC_ENTRY_ROUTER_TEST_PASS")


if __name__ == "__main__":
    main()
