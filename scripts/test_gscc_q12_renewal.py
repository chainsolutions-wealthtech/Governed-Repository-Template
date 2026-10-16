#!/usr/bin/env python3
"""Q12 renewal guards: same persisted GSCC arrival, active GACR proof, no implicit RELEASE."""
from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from gscc_q12_renewal import renew_q12, MIGRATION

REPO = "chainsolutions-wealthtech/Governed-Repository-Template"
HEAD_OLD = "a" * 40
HEAD_NEW = "b" * 40
SESSION = "session-q12-original"
CONNECTION = "GSCC-CONN-q12-original"
RUNTIME = "GSCC-RUNTIME-q12-original"
ARRIVAL = "GSCC-ARRIVAL-q12-original"
IDENTITY = "GSCC-ID-q12-original"
NOW = datetime(2026, 10, 16, 10, 0, tzinfo=timezone.utc)


def iso(dt):
    return dt.isoformat()


class SameArrivalRenewalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.db = base / "entry.sqlite"
        self.spath = base / "sessions.json"
        self.dpath = base / "dispatches.json"
        self.cpath = base / "claims.json"
        self.tpath = base / "tasks.json"
        self.ppath = base / "policy.json"
        self.head = HEAD_NEW
        self.head_observations = 0

        self.previous = {
            "schema": "gscc-access-grant/v1", "grant_id": "GSCC-GRANT-original",
            "status": "AUTHORIZED", "admission_id": "GSCC-ADM-original",
            "session_id": SESSION, "connection_ref": CONNECTION,
            "repository": REPO, "bound_head": HEAD_OLD,
            "issued_at": iso(NOW - timedelta(minutes=15)),
            "expires_at": iso(NOW - timedelta(minutes=5)),
        }
        self.admission = {
            "schema": "gscc-admission-receipt/v1",
            "status": "PREAUTHORIZED", "admission_id": "GSCC-ADM-original",
            "connection_ref": CONNECTION, "repository": REPO,
            "requested_branch": "main",
        }
        self.sessions = {"sessions": [{
            "session_id": SESSION, "connection_ref": CONNECTION,
            "repository": REPO, "branch": "main", "status": "ACTIVE",
            "relay": {"state": "ACTIVE", "branch": "main",
                      "lease_expires_at": iso(NOW + timedelta(minutes=30))},
        }]}
        self.dispatches = {"items": [{
            "dispatch_id": "GSCC-CTRL-q12-fresh",
            "kind": "CONTROL_CHALLENGE", "status": "COMPLETED",
            "target_session_id": SESSION,
            "target_connection_ref": CONNECTION, "repository": REPO,
            "command": {"command_type": "LIVENESS_CHALLENGE",
                        "target_session_id": SESSION, "command_id": "GSCC-CMD-q12",
                        "issued_at": iso(NOW - timedelta(minutes=2)),
                        "expires_at": iso(NOW + timedelta(minutes=3)),
                        "payload": {"challenge_id": "GSCC-CH-q12"}},
            "ack": {"delivery_state": "ACKNOWLEDGED",
                    "evidence_ref": "github-issue-comment:100"},
            "response": {"fresh_liveness": True,
                         "observed_at": iso(NOW - timedelta(minutes=1)),
                         "evidence_ref": "github-issue-comment:101"},
        }]}
        self._save()

        conn = sqlite3.connect(self.db)
        try:
            conn.executescript("""
                CREATE TABLE gscc_arrival_instances (arrival_ref TEXT PRIMARY KEY);
                CREATE TABLE gscc_conversation_identities (identity_id TEXT PRIMARY KEY);
                CREATE TABLE gscc_observable_packets (packet_id TEXT PRIMARY KEY, packet_json TEXT);
                CREATE TABLE gscc_entry_pipeline_runs (
                    run_id TEXT PRIMARY KEY, packet_id TEXT, capture_id TEXT,
                    identity_id TEXT, classification TEXT, entry_status TEXT
                );
                CREATE TABLE gscc_session_bindings (
                    arrival_ref TEXT, identity_id TEXT, gacr_session_id TEXT,
                    connection_ref TEXT, binding_status TEXT, binding_level TEXT
                );
            """)
            conn.executescript((
                Path(__file__).resolve().parents[1] /
                ".governance/control-plane-db/011_gscc_session_runtime.sql"
            ).read_text(encoding="utf-8"))
            conn.execute("INSERT INTO gscc_arrival_instances VALUES (?)", (ARRIVAL,))
            conn.execute("INSERT INTO gscc_conversation_identities VALUES (?)", (IDENTITY,))
            packet = {"sections": {"github": {
                "repository_full_name": REPO, "branch": "main",
                "default_branch": "main",
            }}}
            conn.execute("INSERT INTO gscc_observable_packets VALUES (?,?)",
                         ("packet-q12", json.dumps(packet)))
            conn.execute("INSERT INTO gscc_entry_pipeline_runs VALUES (?,?,?,?,?,?)",
                         ("run-q12", "packet-q12", "capture-q12", IDENTITY,
                          "FIRST_TOUCH", "ENTRY_READY_FOR_Q1"))
            conn.execute(
                "INSERT INTO gscc_session_bindings VALUES (?,?,?,?,?,?)",
                (ARRIVAL, IDENTITY, SESSION, CONNECTION, "GACR_BOUND", "EXACT"),
            )
            conn.execute(
                "INSERT INTO gscc_session_runtime "
                "(runtime_id,run_id,arrival_ref,identity_id,capture_id,issue_number,"
                "connection_ref,state,admission_json,access_grant_json,last_gate,next_gate) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (RUNTIME, "run-q12", ARRIVAL, IDENTITY, "capture-q12", 284,
                 CONNECTION, "READY_FOR_F1", json.dumps(self.admission),
                 json.dumps(self.previous, sort_keys=True), "Q12", "F1"),
            )
            conn.commit()
        finally:
            conn.close()

    def _save(self):
        for path, data in (
            (self.spath, self.sessions), (self.dpath, self.dispatches),
            (self.cpath, {"revision": 0, "claims": []}),
            (self.tpath, {"revision": 0, "items": []}),
            (self.ppath, {"schema_version": "1.0.0"}),
        ):
            path.write_text(json.dumps(data), encoding="utf-8")

    def _github(self, url):
        if url.endswith("/branches/main"):
            self.head_observations += 1
            return {"name": "main", "commit": {"sha": self.head}}
        return {
            "id": 1386478935, "full_name": REPO,
            "default_branch": "main", "visibility": "public",
            "owner": {"login": "chainsolutions-wealthtech"},
            "permissions": {"pull": True},
        }

    def _harvest(self, *_args, **_kwargs):
        return {
            "session": {"status": "BOUND", "session_id": SESSION},
            "repository_baseline": {"status": "OBSERVED", "observed_head": self.head},
            "task": {"status": "NOT_REQUIRED"},
            "claim": {"status": "NOT_REQUIRED"},
            "access_policy": {"status": "ALLOW"},
        }

    def _grant(self, *_args, **kwargs):
        return {
            **self.previous, "grant_id": "GSCC-GRANT-renewed",
            "bound_head": kwargs.get("now") and self.head,
            "issued_at": iso(NOW), "expires_at": iso(NOW + timedelta(minutes=15)),
        }

    def renew(self):
        with patch("gscc_q12_renewal.harvest_qualification_evidence",
                   side_effect=self._harvest) as harvest, patch(
                "gscc_q12_renewal.evaluate_access_grant",
                side_effect=self._grant) as grant:
            result = renew_q12(
                self.db, RUNTIME, self.spath, self.dpath, HEAD_NEW,
                github_request_fn=self._github,
                claims_path=self.cpath, tasks_path=self.tpath,
                policy_path=self.ppath, now=NOW,
            )
            return result, harvest, grant

    def rejected(self, reason):
        with self.assertRaisesRegex(ValueError, reason):
            self.renew()
        with sqlite3.connect(self.db) as conn:
            state, grant = conn.execute(
                "SELECT state,access_grant_json FROM gscc_session_runtime "
                "WHERE runtime_id=?", (RUNTIME,),
            ).fetchone()
            self.assertEqual(state, "READY_FOR_F1")
            self.assertEqual(json.loads(grant), self.previous)
            row = conn.execute("SELECT COUNT(*) FROM gscc_q12_renewal_history").fetchone()
            self.assertEqual(row[0], 0)

    def test_01_expired_grant_requalified_same_arrival_and_history(self):
        result, harvest, grant = self.renew()
        self.assertEqual(result["status"], "REQUALIFIED")
        self.assertEqual(result["arrival_ref"], ARRIVAL)
        self.assertEqual(result["identity_id"], IDENTITY)
        self.assertEqual(result["session_id"], SESSION)
        self.assertFalse(result["authority_granted"])
        self.assertFalse(result["f1_released"])
        self.assertEqual(result["next_gate"], "F1")
        self.assertEqual(self.head_observations, 3)
        harvest.assert_called_once()
        grant.assert_called_once()
        with sqlite3.connect(self.db) as conn:
            stored = json.loads(conn.execute(
                "SELECT access_grant_json FROM gscc_session_runtime WHERE runtime_id=?",
                (RUNTIME,),
            ).fetchone()[0])
            self.assertEqual(stored["grant_id"], "GSCC-GRANT-renewed")
            record = conn.execute(
                "SELECT arrival_ref,identity_id,old_grant_json,new_grant_json,"
                "control_evidence_ref FROM gscc_q12_renewal_history",
            ).fetchone()
            self.assertEqual(record[:2], (ARRIVAL, IDENTITY))
            self.assertEqual(json.loads(record[2]), self.previous)
            self.assertEqual(json.loads(record[3]), stored)
            self.assertEqual(record[4], "github-issue-comment:101")

    def test_02_changed_head_refreshes_grant(self):
        self.previous["expires_at"] = iso(NOW + timedelta(minutes=10))
        self._set_old()
        result, _, _ = self.renew()
        self.assertEqual(result["bound_head"], HEAD_NEW)

    def test_03_expired_gacr_lease_denied(self):
        self.sessions["sessions"][0]["relay"]["lease_expires_at"] = iso(NOW - timedelta(seconds=1))
        self._save()
        self.rejected("GACR_LEASE_EXPIRED")

    def test_04_inactive_gacr_session_denied(self):
        self.sessions["sessions"][0]["status"] = "STALLED"
        self._save()
        self.rejected("GACR_SESSION_NOT_ACTIVE")

    def test_05_ambiguous_gacr_session_denied(self):
        self.sessions["sessions"].append(dict(self.sessions["sessions"][0]))
        self._save()
        self.rejected("UNIQUE_SAME_ARRIVAL")

    def test_06_mismatched_arrival_connection_denied(self):
        self.previous["connection_ref"] = "GSCC-CONN-another"
        self._set_old()
        self.rejected("PREVIOUS_GRANT_BINDING_MISMATCH")

    def test_07_missing_fresh_control_denied(self):
        self.dispatches["items"] = []
        self._save()
        self.rejected("FRESH_POST_GRANT_GACR_CONTROL_PROOF_REQUIRED")

    def test_08_replayed_control_denied(self):
        self.dispatches["items"][0]["response"]["replay"] = True
        self._save()
        self.rejected("FRESH_POST_GRANT_GACR_CONTROL_PROOF_REQUIRED")

    def test_09_old_pre_grant_challenge_denied(self):
        self.dispatches["items"][0]["command"]["issued_at"] = iso(NOW - timedelta(minutes=16))
        self._save()
        self.rejected("FRESH_POST_GRANT_GACR_CONTROL_PROOF_REQUIRED")

    def test_10_external_head_mismatch_denied(self):
        self.head = HEAD_OLD
        self.rejected("CURRENT_GITHUB_HEAD_MISMATCH")

    def test_11_q6_q7_incomplete_denied(self):
        original = self._harvest
        self._harvest = lambda *_a, **_kw: {
            **original(), "claim": {"status": "UNAVAILABLE"}
        }
        self.rejected("Q6_Q7_Q11_REVALIDATION_REQUIRED")

    def test_12_q11_policy_denied(self):
        original = self._harvest
        self._harvest = lambda *_a, **_kw: {
            **original(), "access_policy": {"status": "DENY"}
        }
        self.rejected("Q6_Q7_Q11_REVALIDATION_REQUIRED")

    def test_13_second_head_observation_moved_denied(self):
        original = self._github
        def moving(url):
            if url.endswith("/branches/main") and self.head_observations >= 1:
                self.head = "c" * 40
            return original(url)
        self._github = moving
        self.rejected("HEAD_MOVED_DURING_RENEWAL")

    def test_14_invalid_old_grant_not_renewable(self):
        self.previous["status"] = "WITHHELD"
        self._set_old()
        self.rejected("PREVIOUS_CANONICAL_ACCESS_GRANT_REQUIRED")

    def test_15_invalid_evidence_reference_rejected(self):
        self.dispatches["items"][0]["response"]["evidence_ref"] = "self-reported"
        self._save()
        self.rejected("FRESH_POST_GRANT_GACR_CONTROL_PROOF_REQUIRED")

    def test_16_fresh_grant_idempotent_without_new_grant(self):
        self.previous["bound_head"] = HEAD_NEW
        self.previous["expires_at"] = iso(NOW + timedelta(minutes=10))
        self._set_old()
        result, harvest, grant = self.renew()
        self.assertEqual(result["status"], "ALREADY_CURRENT")
        harvest.assert_not_called()
        grant.assert_not_called()

    def test_17_released_arrival_cannot_reenter_q12(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute(
                "UPDATE gscc_session_runtime SET state='RELEASED_TO_NORMAL_GOVERNANCE'"
            )
        self.rejected("READY_FOR_F1_SAME_ARRIVAL_REQUIRED")

    def test_18_no_second_first_touch_or_gacr_claim_generated(self):
        self.renew()
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute(
                "SELECT COUNT(*) FROM gscc_session_runtime"
            ).fetchone()[0], 1)
            self.assertEqual(conn.execute(
                "SELECT COUNT(*) FROM gscc_session_bindings"
            ).fetchone()[0], 1)
        self.assertEqual(json.loads(self.cpath.read_text())["claims"], [])

    def _set_old(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute(
                "UPDATE gscc_session_runtime SET access_grant_json=? WHERE runtime_id=?",
                (json.dumps(self.previous, sort_keys=True), RUNTIME),
            )


if __name__ == "__main__":
    unittest.main()
