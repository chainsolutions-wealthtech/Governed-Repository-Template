#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.gse.session_state_engine import Policy, evaluate_at, new_session_twin, reduce_event

T0 = "2026-10-02T04:00:00Z"


def ev(event_id, event_type, at, **payload):
    return {"event_id": event_id, "event_type": event_type, "observed_at": at, "payload": payload}


class GSESessionStateEngineTests(unittest.TestCase):
    def attach(self):
        return reduce_event(None, ev(
            "e-attach", "SESSION_ATTACH", T0,
            session_identity="session-a", repository="owner/repo", task="TASK-1",
            branch="feature/a", observed_head="a" * 40,
        ))

    def test_heartbeat_liveness_not_progress(self):
        twin = self.attach()
        twin = reduce_event(twin, ev("e-hb", "HEARTBEAT", "2026-10-02T04:01:00Z"))
        self.assertEqual(twin["liveness"]["state"], "ACTIVE")
        self.assertEqual(twin["progress"]["state"], "NO_RECENT_PROGRESS_EVIDENCE")
        self.assertIsNone(twin["timestamps"]["last_progress_at"])

    def test_tool_activity_and_progress_can_coexist(self):
        twin = self.attach()
        twin = reduce_event(twin, ev("e-tool", "TOOL_STARTED", "2026-10-02T04:02:00Z", tool_name="edit", target="x.py"))
        twin = reduce_event(twin, ev("e-progress", "PROGRESS", "2026-10-02T04:02:30Z", previous_phase="A", current_phase="B"))
        self.assertEqual(twin["activity"]["state"], "ACTIVE")
        self.assertEqual(twin["progress"]["state"], "ADVANCING")

    def test_stale_heartbeat_projects_quiet_then_suspected_then_lost(self):
        twin = self.attach()
        twin = reduce_event(twin, ev("e-hb", "HEARTBEAT", "2026-10-02T04:01:00Z"))
        self.assertEqual(evaluate_at(twin, "2026-10-02T04:06:01Z")["liveness"]["state"], "QUIET")
        self.assertEqual(evaluate_at(twin, "2026-10-02T04:16:01Z")["liveness"]["state"], "SUSPECTED")
        self.assertEqual(evaluate_at(twin, "2026-10-02T04:31:01Z")["liveness"]["state"], "LOST")

    def test_challenge_ack_reachable(self):
        twin = self.attach()
        twin = reduce_event(twin, ev("e-ack", "CHALLENGE_RESPONSE", "2026-10-02T04:01:00Z", delivery_state="ACKNOWLEDGED"))
        self.assertEqual(twin["control_channel"]["state"], "REACHABLE")
        self.assertEqual(twin["timestamps"]["last_challenge_response_at"], "2026-10-02T04:01:00Z")

    def test_replayed_challenge_does_not_refresh_liveness(self):
        twin = self.attach()
        twin = reduce_event(
            twin,
            ev(
                "challenge-fresh",
                "CHALLENGE_RESPONSE",
                "2026-10-02T04:01:00Z",
                delivery_state="ACKNOWLEDGED",
                replay=False,
                fresh_liveness=True,
            ),
        )
        self.assertEqual(twin["timestamps"]["last_liveness_evidence_at"], "2026-10-02T04:01:00Z")
        twin = reduce_event(
            twin,
            ev(
                "challenge-replay",
                "CHALLENGE_RESPONSE",
                "2026-10-02T04:02:00Z",
                delivery_state="ACKNOWLEDGED",
                replay=True,
                fresh_liveness=False,
            ),
        )
        self.assertEqual(twin["timestamps"]["last_liveness_evidence_at"], "2026-10-02T04:01:00Z")
        self.assertEqual(twin["control_channel"]["state"], "REACHABLE")

    def test_challenge_unsupported_is_not_unreachable(self):
        twin = reduce_event(self.attach(), ev("e-uns", "CHALLENGE_RESPONSE", "2026-10-02T04:01:00Z", delivery_state="UNSUPPORTED"))
        self.assertEqual(twin["control_channel"]["state"], "UNSUPPORTED")

    def test_no_response_degrades_then_unreachable_without_crash_cause(self):
        twin = self.attach()
        twin = reduce_event(twin, ev("e-nr1", "CHALLENGE_RESPONSE", "2026-10-02T04:01:00Z", delivery_state="NO_RESPONSE"))
        self.assertEqual(twin["control_channel"]["state"], "DEGRADED")
        twin = reduce_event(twin, ev("e-nr2", "CHALLENGE_RESPONSE", "2026-10-02T04:02:00Z", delivery_state="NO_RESPONSE"))
        self.assertEqual(twin["control_channel"]["state"], "UNREACHABLE")
        serialized = str(twin)
        self.assertNotIn("BROWSER_CRASH", serialized)
        self.assertNotIn("PROVIDER_TIMEOUT", serialized)
        self.assertNotIn("NETWORK_FAILURE", serialized)

    def test_explicit_blocked(self):
        twin = reduce_event(self.attach(), ev("e-block", "BLOCKED", "2026-10-02T04:01:00Z", blockage_class="WAITING_FOR_CI"))
        self.assertEqual(twin["blockage"]["state"], "EXPLICITLY_BLOCKED")
        self.assertEqual(twin["blockage"]["provenance"], "EXPLICIT")
        self.assertEqual(twin["progress"]["state"], "BLOCKED_IF_EXPLICITLY_OBSERVED")

    def test_repeated_failures_may_suspect_blockage(self):
        twin = self.attach()
        twin = reduce_event(twin, ev("hb", "HEARTBEAT", "2026-10-02T04:01:00Z"))
        for i in range(3):
            twin = reduce_event(twin, ev(f"f{i}", "TOOL_FAILED", f"2026-10-02T04:0{i+2}:00Z", tool_name="pytest", target="suite", relevant_input_digest="same"))
        self.assertEqual(twin["blockage"]["state"], "SUSPECTED_BLOCKED")
        self.assertEqual(twin["blockage"]["provenance"], "INFERRED")

    def test_aaaa_loop_requires_no_progress_and_stable_repo(self):
        twin = self.attach()
        for i in range(4):
            twin = reduce_event(twin, ev(f"a{i}", "TOOL_COMPLETED", f"2026-10-02T04:0{i+1}:00Z", tool_name="read", target="same.txt", observed_head="a"*40))
        self.assertEqual(twin["loop"]["state"], "SUSPECTED")
        self.assertEqual(twin["loop"]["pattern"], "AAAA")

    def test_ababab_loop(self):
        twin = self.attach()
        for i, target in enumerate(["A", "B", "A", "B", "A", "B"], start=1):
            twin = reduce_event(twin, ev(f"ab{i}", "TOOL_COMPLETED", f"2026-10-02T04:{i:02d}:00Z", tool_name="read", target=target, observed_head="a"*40))
        self.assertEqual(twin["loop"]["state"], "SUSPECTED")
        self.assertEqual(twin["loop"]["pattern"], "ABABAB")

    def test_ababab_with_head_movement_is_not_loop(self):
        twin = self.attach()
        heads = ["a"*40, "a"*40, "b"*40, "b"*40, "c"*40, "c"*40]
        for i, (target, head) in enumerate(zip(["A", "B", "A", "B", "A", "B"], heads), start=1):
            twin = reduce_event(twin, ev(f"hm{i}", "TOOL_COMPLETED", f"2026-10-02T04:{i:02d}:00Z", tool_name="read", target=target, observed_head=head))
        self.assertEqual(twin["loop"]["state"], "NONE")

    def test_repeat_with_checkpoint_advancement_is_not_loop(self):
        twin = self.attach()
        for i in range(4):
            twin = reduce_event(twin, ev(f"cp{i}", "CHECKPOINT", f"2026-10-02T04:{i*2+1:02d}:00Z", checkpoint=f"cp-{i}", checkpoint_advanced=True))
            twin = reduce_event(twin, ev(f"r{i}", "TOOL_COMPLETED", f"2026-10-02T04:{i*2+2:02d}:00Z", tool_name="read", target="same.txt", observed_head="a"*40))
        self.assertEqual(twin["loop"]["state"], "NONE")

    def test_same_file_read_twice_not_loop(self):
        twin = self.attach()
        for i in range(2):
            twin = reduce_event(twin, ev(f"read{i}", "TOOL_COMPLETED", f"2026-10-02T04:0{i+1}:00Z", tool_name="read", target="same.txt"))
        self.assertEqual(twin["loop"]["state"], "NONE")

    def test_continuity_sufficient(self):
        twin = self.attach()
        twin = reduce_event(twin, ev("ctx", "CONTEXT_UPDATE", "2026-10-02T04:01:00Z", last_action="edit", next_action="test", checkpoint="cp-1"))
        twin = reduce_event(twin, ev("prog", "PROGRESS", "2026-10-02T04:02:00Z", completed_step_ref="S1"))
        self.assertEqual(twin["continuity"]["state"], "SUFFICIENT")

    def test_continuity_partial(self):
        twin = reduce_event(None, ev("partial", "SESSION_ATTACH", T0, session_identity="s", repository="r", task="t"))
        self.assertEqual(twin["continuity"]["state"], "PARTIAL")

    def test_continuity_insufficient(self):
        twin = reduce_event(None, ev("ins", "SESSION_ATTACH", T0, session_identity="s"))
        self.assertEqual(twin["continuity"]["state"], "INSUFFICIENT")

    def test_duplicate_event_is_idempotent(self):
        twin = self.attach()
        one = reduce_event(twin, ev("dup", "HEARTBEAT", "2026-10-02T04:01:00Z"))
        two = reduce_event(one, ev("dup", "HEARTBEAT", "2026-10-02T04:01:00Z"))
        self.assertEqual(two["timestamps"], one["timestamps"])
        self.assertEqual(two["evidence"]["applied_event_count"], one["evidence"]["applied_event_count"])
        self.assertEqual(two["evidence"]["ignored_duplicate_count"], one["evidence"]["ignored_duplicate_count"] + 1)

    def test_same_message_id_deduplicates(self):
        twin = self.attach()
        e1 = {"message_id":"m-1","event_type":"HEARTBEAT","observed_at":"2026-10-02T04:01:00Z","payload":{}}
        e2 = {"message_id":"m-1","event_type":"HEARTBEAT","observed_at":"2026-10-02T04:02:00Z","payload":{}}
        one = reduce_event(twin, e1)
        two = reduce_event(one, e2)
        self.assertEqual(two["timestamps"]["last_liveness_evidence_at"], "2026-10-02T04:01:00Z")

    def test_out_of_order_older_evidence_never_moves_freshness_backwards(self):
        twin = self.attach()
        twin = reduce_event(twin, ev("new", "HEARTBEAT", "2026-10-02T04:10:00Z"))
        twin = reduce_event(twin, ev("old", "HEARTBEAT", "2026-10-02T04:05:00Z"), reference_time="2026-10-02T04:10:00Z")
        self.assertEqual(twin["timestamps"]["last_liveness_evidence_at"], "2026-10-02T04:10:00Z")
        self.assertEqual(twin["evidence"]["out_of_order_event_count"], 1)

    def test_terminal_session_and_newer_resume(self):
        twin = self.attach()
        twin = reduce_event(twin, ev("term", "INTERRUPTION", "2026-10-02T04:05:00Z", terminal=True))
        self.assertEqual(twin["presence"]["state"], "TERMINAL")
        self.assertEqual(twin["liveness"]["state"], "TERMINAL")
        twin = reduce_event(twin, ev("resume", "SESSION_RESUME", "2026-10-02T04:06:00Z", session_identity="session-a"))
        self.assertEqual(twin["presence"]["state"], "PRESENT")
        self.assertEqual(twin["liveness"]["state"], "ACTIVE")

    def test_older_terminal_does_not_override_newer_resume(self):
        twin = self.attach()
        twin = reduce_event(twin, ev("resume2", "SESSION_RESUME", "2026-10-02T04:10:00Z"))
        twin = reduce_event(twin, ev("oldterm", "INTERRUPTION", "2026-10-02T04:05:00Z", terminal=True), reference_time="2026-10-02T04:10:00Z")
        self.assertNotEqual(twin["presence"]["state"], "TERMINAL")

    def test_activity_active_can_coexist_with_stale_progress(self):
        twin = self.attach()
        twin = reduce_event(twin, ev("p1", "PROGRESS", "2026-10-02T04:01:00Z", previous_phase="A", current_phase="B"))
        twin = reduce_event(twin, ev("a1", "TOOL_STARTED", "2026-10-02T04:20:00Z", tool_name="long", target="job"), reference_time="2026-10-02T04:20:00Z")
        self.assertEqual(twin["activity"]["state"], "ACTIVE")
        self.assertEqual(twin["progress"]["state"], "STALE")

    def test_progress_payload_does_not_persist_transcript_or_private_reasoning(self):
        twin = self.attach()
        twin = reduce_event(twin, ev("safe", "PROGRESS", "2026-10-02T04:01:00Z", previous_phase="A", current_phase="B", transcript="secret", private_reasoning="secret"))
        serialized = str(twin["evidence"]["last_progress_evidence"])
        self.assertNotIn("transcript", serialized)
        self.assertNotIn("private_reasoning", serialized)
        self.assertNotIn("secret", serialized)

    def test_gse_never_emits_authority_fields(self):
        twin = self.attach()
        forbidden = {"takeover_authorized", "claim_transferred", "write_authority_granted", "standby_assigned"}
        self.assertTrue(forbidden.isdisjoint(twin.keys()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
