#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path

from first_touch_field_block_gate import build_capture_database, load_catalog

def main():
    capture = {
        "schema": "first-touch-exhaustive-capture/v1",
        "capture_id": "FTC-test-block-gate",
        "observed_at": "2026-10-06T04:00:00+00:00",
        "repository": "acme/demo",
        "actor": "alice",
        "capture_digest": "digest",
        "github_event": {
            "sender": {"login": "alice", "id": 10},
            "repository": {"id": 20, "full_name": "acme/demo", "default_branch": "main"},
            "issue": {"number": 7},
        },
        "environment": {
            "GITHUB_EVENT_NAME": "issues",
            "GITHUB_REPOSITORY": "acme/demo",
            "GITHUB_ACTOR": "alice",
            "GITHUB_RUN_ID": "99",
            "GITHUB_SHA": "a" * 40,
        },
        "api_attempts": [
            {"name": "repository", "url": "https://api.github.com/repos/acme/demo", "http_status": 200,
             "response": {"id": 20, "full_name": "acme/demo", "permissions": {"pull": True}}},
            {"name": "repository_installation", "url": "https://api.github.com/repos/acme/demo/installation",
             "http_status": 403, "response": {"message": "not accessible"}},
        ],
        "mutation_authority_granted": False,
        "interpretation_applied": False,
    }

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "capture.json"
        target = Path(tmp) / "capture.sqlite"
        source.write_text(json.dumps(capture), encoding="utf-8")
        summary = build_capture_database(source, target, source_ref="unit-test")

        assert summary["all_nodes_preserved_in_B00"] is True
        assert summary["node_count"] > summary["terminal_value_count"]
        assert summary["membership_count"] >= summary["node_count"]

        conn = sqlite3.connect(target)
        try:
            blocks = conn.execute("SELECT COUNT(*) FROM first_touch_evidence_blocks").fetchone()[0]
            gates = conn.execute("SELECT COUNT(*) FROM first_touch_process_gates").fetchone()[0]
            assert blocks == 31, blocks
            assert gates == 17, gates

            node_count = conn.execute(
                "SELECT node_count FROM first_touch_capture_records WHERE capture_id='FTC-test-block-gate'"
            ).fetchone()[0]
            b00 = conn.execute(
                "SELECT COUNT(DISTINCT json_path) FROM first_touch_field_block_membership "
                "WHERE capture_id='FTC-test-block-gate' AND block_id='B00'"
            ).fetchone()[0]
            assert b00 == node_count, (b00, node_count)

            assert conn.execute(
                "SELECT COUNT(*) FROM first_touch_field_block_membership "
                "WHERE capture_id='FTC-test-block-gate' AND block_id='B02'"
            ).fetchone()[0] > 0
            assert conn.execute(
                "SELECT COUNT(*) FROM first_touch_field_block_membership "
                "WHERE capture_id='FTC-test-block-gate' AND block_id='B05'"
            ).fetchone()[0] > 0
            assert conn.execute(
                "SELECT COUNT(*) FROM first_touch_field_block_membership "
                "WHERE capture_id='FTC-test-block-gate' AND block_id='B06'"
            ).fetchone()[0] > 0
            assert conn.execute(
                "SELECT COUNT(*) FROM first_touch_field_block_membership "
                "WHERE capture_id='FTC-test-block-gate' AND block_id='B30'"
            ).fetchone()[0] > 0

            # Presence can make a gate ready for canonical validation, but cannot grant authority.
            g00 = conn.execute(
                "SELECT status FROM first_touch_gate_evaluations "
                "WHERE capture_id='FTC-test-block-gate' AND gate_id='G00'"
            ).fetchone()[0]
            assert g00 == "EVIDENCE_READY_FOR_CANONICAL_VALIDATION", g00

            q1 = conn.execute(
                "SELECT status FROM first_touch_gate_evaluations "
                "WHERE capture_id='FTC-test-block-gate' AND gate_id='Q1'"
            ).fetchone()[0]
            assert q1 != "EVIDENCE_READY_FOR_CANONICAL_VALIDATION", q1

            authority = conn.execute(
                "SELECT DISTINCT authority_effect FROM first_touch_process_gates"
            ).fetchall()
            assert authority == [("NONE",)], authority
        finally:
            conn.close()

    catalog = load_catalog()
    assert catalog["requirements"]["Q12"]
    assert catalog["requirements"]["F1"]
    print("FIRST_TOUCH_FIELD_BLOCK_GATE_TEST_PASS")

if __name__ == "__main__":
    main()
