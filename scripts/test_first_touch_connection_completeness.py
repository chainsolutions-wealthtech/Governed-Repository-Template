#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "first_touch_connection_completeness.py"
OBS = ROOT / ".governance" / "control-plane-state" / "live-connection-6009181746-observed.json"

spec=importlib.util.spec_from_file_location("first_touch_connection_completeness",SCRIPT)
mod=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

def main():
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp)/"packet.json"
        packet=mod.build_packet(OBS,out)
        assert packet["expected_observation_count"] >= 1500, packet["expected_observation_count"]
        assert packet["complete_accounting"] is True
        assert packet["silent_missing_count"] == 0
        assert packet["live_value_count"] > 20
        assert packet["explicit_unavailable_count"] >= 2
        assert packet["status_counts"].get("SCHEMA_AVAILABLE",0) >= 800
        assert packet["status_counts"].get("REFERENCE_ONLY",0) >= 700
        assert packet["status_counts"].get("UNKNOWN",0) >= 1
        assert out.exists()
        print("FIRST_TOUCH_CONNECTION_COMPLETENESS_TEST_PASS")
        print(f"EXPECTED_OBSERVATIONS={packet['expected_observation_count']}")
        print(f"LIVE_VALUES={packet['live_value_count']}")
        print(f"EXPLICIT_UNAVAILABLE={packet['explicit_unavailable_count']}")
        print(f"SILENT_MISSING={packet['silent_missing_count']}")
        print(f"STATUS_COUNTS={packet['status_counts']}")

if __name__=="__main__":
    main()
