#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATERIALIZER = ROOT / ".governance" / "control-plane-db" / "materialize.py"


def main():
    capture = {
        "schema": "first-touch-exhaustive-capture/v1",
        "capture_id": "FTC-test-001",
        "capture_digest": "digest-test",
        "observed_at": "2026-10-06T04:00:00+00:00",
        "repository": "acme/demo",
        "actor": "agent-a",
        "subject": {
            "event_name": "issues",
            "issue_number": 7,
        },
        "github_event": {
            "repository": {"id": 1, "full_name": "acme/demo"},
            "sender": {"login": "agent-a"},
            "unexpected": {"nested": [1, 2, None, False]},
        },
        "environment": {
            "GITHUB_EVENT_NAME": "issues",
            "GITHUB_RUN_ID": "99",
            "RUNNER_OS": "Linux",
        },
        "api_attempts": [
            {
                "name": "repository",
                "url": "https://api.github.com/repos/acme/demo",
                "http_status": 200,
                "response": {"id": 1, "full_name": "acme/demo"},
            },
            {
                "name": "installation",
                "url": "https://api.github.com/repos/acme/demo/installation",
                "http_status": 403,
                "response": {"message": "not available"},
            },
        ],
        "mutation_authority_granted": False,
        "interpretation_applied": False,
    }

    with tempfile.TemporaryDirectory(prefix="first-touch-db-test-") as tmp:
        tmp = Path(tmp)
        capture_path = tmp / "capture.json"
        db_path = tmp / "control-plane.sqlite"
        raw = json.dumps(capture, indent=2, sort_keys=True) + "\n"
        capture_path.write_text(raw, encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                str(MATERIALIZER),
                "--output",
                str(db_path),
                "--first-touch-capture",
                str(capture_path),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, (result.stdout, result.stderr)

        conn = sqlite3.connect(db_path)
        try:
            record = conn.execute(
                "SELECT capture_id,schema_id,path_count,terminal_value_count,api_attempt_count,"
                "mutation_authority_granted,interpretation_applied "
                "FROM first_touch_capture_records WHERE capture_id='FTC-test-001'"
            ).fetchone()
            assert record is not None, result.stdout
            assert record[0] == "FTC-test-001"
            assert record[1] == "first-touch-exhaustive-capture/v1"
            assert record[4] == 2
            assert record[5] == 0
            assert record[6] == 0

            root = conn.execute(
                "SELECT value_type,is_terminal FROM first_touch_capture_nodes "
                "WHERE capture_id='FTC-test-001' AND json_path='$'"
            ).fetchone()
            assert root == ("object", 0), root

            unexpected = conn.execute(
                "SELECT value_json FROM first_touch_capture_nodes "
                "WHERE capture_id='FTC-test-001' "
                "AND json_path='$.github_event.unexpected.nested[2]'"
            ).fetchone()
            assert unexpected == ("null",), unexpected

            boolean_value = conn.execute(
                "SELECT value_json,value_type FROM first_touch_capture_nodes "
                "WHERE capture_id='FTC-test-001' "
                "AND json_path='$.github_event.unexpected.nested[3]'"
            ).fetchone()
            assert boolean_value == ("false", "boolean"), boolean_value

            attempts = conn.execute(
                "SELECT attempt_ordinal,name,http_status FROM first_touch_capture_api_attempts "
                "WHERE capture_id='FTC-test-001' ORDER BY attempt_ordinal"
            ).fetchall()
            assert attempts == [
                (1, "repository", 200),
                (2, "installation", 403),
            ], attempts

            schema_version = conn.execute(
                "SELECT value FROM schema_meta WHERE key='schema_version'"
            ).fetchone()
            assert schema_version == ("1.6.0",), schema_version
        finally:
            conn.close()

    print("FIRST_TOUCH_CAPTURE_DB_TEST_PASS")


if __name__ == "__main__":
    main()
