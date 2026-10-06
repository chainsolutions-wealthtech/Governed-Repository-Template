#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_SCRIPT = ROOT / "scripts" / "first_touch_expected_field_registry.py"
REGISTRY_PATH = ROOT / ".governance" / "control-plane-state" / "first-touch-expected-field-registry.json"

def load_registry_module():
    spec = importlib.util.spec_from_file_location("first_touch_expected_field_registry", REGISTRY_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

def build_packet(observation_path: Path, output_path: Path):
    mod = load_registry_module()
    mod.main()
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    observed = json.loads(observation_path.read_text(encoding="utf-8"))
    current = observed.get("fields", {})

    rows=[]
    for expected in registry["expected_observations"]:
        field_id=expected["field_id"]
        live=current.get(field_id)
        if live:
            status=live["status"]
            value=live.get("value")
            source=live.get("source")
        elif expected["source_kind"]=="TOOL_SCHEMA":
            status="SCHEMA_AVAILABLE"
            value=None
            source=expected["source_path"]
        elif expected["source_kind"]=="PROBE_REFERENCE":
            status="REFERENCE_ONLY"
            value=None
            source=expected["source_path"]
        else:
            status="UNKNOWN"
            value=None
            source="NO_LIVE_VALUE_OBSERVED"
        rows.append({
            **expected,
            "status":status,
            "value":value,
            "evidence_source":source,
        })

    counts=Counter(row["status"] for row in rows)
    silent=[row for row in rows if not row.get("status")]
    packet={
        "schema":"first-touch-connection-completeness/v1",
        "source_comment_id":observed["source_comment_id"],
        "request_id":observed["request_id"],
        "correlation_id":observed["correlation_id"],
        "connection_ref":observed["connection_ref"],
        "expected_observation_count":len(rows),
        "status_counts":dict(sorted(counts.items())),
        "silent_missing_count":len(silent),
        "complete_accounting":len(silent)==0,
        "live_value_count":sum(1 for row in rows if row["status"]=="OBSERVED"),
        "explicit_unavailable_count":sum(1 for row in rows if row["status"]=="UNAVAILABLE"),
        "rows":rows,
        "authority_granted":False,
    }
    output_path.write_text(json.dumps(packet,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    return packet

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--observation",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    packet=build_packet(Path(args.observation),Path(args.output))
    print(json.dumps({
        "status":"FIRST_TOUCH_CONNECTION_COMPLETENESS_BUILT",
        "expected_observation_count":packet["expected_observation_count"],
        "status_counts":packet["status_counts"],
        "silent_missing_count":packet["silent_missing_count"],
        "complete_accounting":packet["complete_accounting"],
    },indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
