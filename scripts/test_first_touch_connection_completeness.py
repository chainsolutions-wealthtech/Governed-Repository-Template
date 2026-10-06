#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
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
        root=Path(tmp)

        # Historical live overlay regression for comment 6009181746.
        out=root/"packet-observed.json"
        packet=mod.build_packet(OBS,out)
        assert packet["expected_observation_count"] == packet["canonical_field_count"]
        assert packet["canonical_field_count"] >= 60
        assert packet["complete_accounting"] is True
        assert packet["silent_missing_count"] == 0
        assert packet["live_value_count"] > 20
        assert packet["explicit_unavailable_count"] >= 2
        assert packet["reference_inventory_evaluated"] is False
        assert packet["reference_inventory_is_gate_input"] is False
        assert packet["unknown_count"] >= 1

        # Generic runtime path: consume the First Touch JSON directly.
        capture={
            "schema":"first-touch-exhaustive-capture/v1",
            "capture_id":"FTC-generic-live",
            "observed_at":"2026-10-06T04:30:00+00:00",
            "repository":"chainsolutions-wealthtech/Governed-Repository-Template",
            "actor":"Wealthtechinnovations",
            "subject":{"event_name":"issue_comment","issue_number":161},
            "github_event":{
                "repository":{
                    "id":1386478935,
                    "node_id":"R_kgDOUqP9Vw",
                    "full_name":"chainsolutions-wealthtech/Governed-Repository-Template",
                    "default_branch":"main",
                    "owner":{"login":"chainsolutions-wealthtech","id":299685687},
                },
                "sender":{"login":"Wealthtechinnovations","id":94637590},
                "issue":{"number":161},
                "installation":{"id":145098929},
            },
            "environment":{
                "GITHUB_EVENT_NAME":"issue_comment",
                "GITHUB_REPOSITORY":"chainsolutions-wealthtech/Governed-Repository-Template",
                "GITHUB_REPOSITORY_ID":"1386478935",
                "GITHUB_REPOSITORY_OWNER":"chainsolutions-wealthtech",
                "GITHUB_REPOSITORY_OWNER_ID":"299685687",
                "GITHUB_ACTOR":"Wealthtechinnovations",
                "GITHUB_ACTOR_ID":"94637590",
                "GITHUB_REF_NAME":"main",
                "GITHUB_SHA":"a"*40,
                "GITHUB_RUN_ID":"123",
                "GITHUB_RUN_ATTEMPT":"1",
            },
            "api_attempts":[
                {"name":"repository","http_status":200,"response":{"id":1386478935,"full_name":"chainsolutions-wealthtech/Governed-Repository-Template","default_branch":"main","visibility":"public"}},
                {"name":"actor_repository_permission","http_status":200,"response":{"permission":"admin"}},
            ],
            "mutation_authority_granted":False,
            "interpretation_applied":False,
        }
        capture_path=root/"capture.json"
        capture_path.write_text(json.dumps(capture),encoding="utf-8")
        generic_out=root/"packet-generic.json"
        generic=mod.build_packet(None,generic_out,capture_path=capture_path)
        assert generic["expected_observation_count"] == generic["canonical_field_count"]
        assert generic["canonical_field_count"] >= 60
        assert generic["complete_accounting"] is True
        assert generic["silent_missing_count"] == 0
        assert generic["capture_id"] == "FTC-generic-live"
        assert generic["capture_terminal_value_count"] > 20
        assert generic["captured_live_node_count"] == generic["capture_terminal_value_count"]
        assert generic["total_accounted_items"] > generic["expected_observation_count"]
        assert generic["live_value_count"] >= 5

        print("FIRST_TOUCH_CONNECTION_COMPLETENESS_TEST_PASS")
        print(f"CANONICAL_FIELDS={packet['canonical_field_count']}")
        print(f"LIVE_VALUES={packet['live_value_count']}")
        print(f"EXPLICIT_UNAVAILABLE={packet['explicit_unavailable_count']}")
        print(f"SILENT_MISSING={packet['silent_missing_count']}")
        print(f"STATUS_COUNTS={packet['status_counts']}")
        print(f"GENERIC_CAPTURE_TERMINALS={generic['capture_terminal_value_count']}")
        print(f"GENERIC_TOTAL_ACCOUNTED={generic['total_accounted_items']}")

if __name__=="__main__":
    main()
