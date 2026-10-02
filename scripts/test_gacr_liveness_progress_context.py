#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import gacr_agent_telemetry as telemetry
import governed_agent_continuity_relay as relay


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def assert_true(value, message: str) -> None:
    if not value:
        raise SystemExit("GACR_LIVENESS_PROGRESS_CONTEXT_TEST_FAILED: " + message)


def configure_paths(root: Path) -> None:
    telemetry.ROOT = root
    telemetry.GOV = root / ".governance"
    telemetry.TEMPLATE_SOURCE = False
    telemetry.SESSIONS_PATH = telemetry.GOV / "sessions" / "sessions.json"
    telemetry.CLAIMS_PATH = telemetry.GOV / "work" / "claims.json"
    telemetry.TAKEOVERS_PATH = telemetry.GOV / "agent-relay" / "takeovers.json"
    telemetry.BEACONS_PATH = telemetry.GOV / "agent-relay" / "beacons.json"
    telemetry.CORRELATIONS_PATH = telemetry.GOV / "agent-relay" / "correlations.json"
    telemetry.DISPATCHES_PATH = telemetry.GOV / "agent-relay" / "dispatches.json"
    telemetry.FORENSICS_PATH = telemetry.GOV / "agent-relay" / "forensics.json"
    telemetry.CONFIG_PATH = telemetry.GOV / "agent-relay" / "config.json"


def base_session(session_id: str, *, connection_ref: str, t0: datetime) -> dict:
    iso = lambda dt: dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "session_id": session_id,
        "agent_identity": session_id,
        "provider": "chatgpt",
        "provider_conversation_ref": None,
        "provider_conversation_ref_provenance": "UNAVAILABLE",
        "client_instance_id": session_id + "-client",
        "connection_ref": connection_ref,
        "repository": "owner/repo",
        "starting_head_sha": "a" * 40,
        "last_observed_head_sha": "a" * 40,
        "status": "ACTIVE",
        "created_at": iso(t0),
        "last_seen_at": iso(t0),
        "relay": {
            "process": "GACR",
            "state": "ACTIVE",
            "last_heartbeat_at": iso(t0),
            "lease_expires_at": iso(t0 + timedelta(seconds=1800)),
            "last_action": "REGISTER",
            "task_id": "TASK-1",
            "branch": "feature/a",
            "pull_request": 12,
        },
    }


def main() -> None:
    t0 = datetime(2026, 10, 2, 3, 0, 0, tzinfo=timezone.utc)
    os.environ["GITHUB_REPOSITORY"] = "owner/repo"

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        configure_paths(root)

        session_a = base_session("session-a", connection_ref="conn-a", t0=t0)
        write(telemetry.SESSIONS_PATH, {"schema_version": "1.0.0", "revision": 1, "sessions": [session_a]})
        write(telemetry.CLAIMS_PATH, {"schema_version": "1.0.0", "revision": 1, "claims": [{
            "session_id": "session-a",
            "work_item_id": "WORK-1",
            "collision_domains": ["gacr-test"],
            "status": "ACTIVE",
            "claimed_head_sha": "a" * 40,
            "claimed_at": t0.isoformat(),
            "released_at": None,
        }]})
        write(telemetry.TAKEOVERS_PATH, {"schema_version": "1.0.0", "revision": 0, "last_scan_at": None, "items": []})
        for path in [telemetry.BEACONS_PATH, telemetry.CORRELATIONS_PATH, telemetry.DISPATCHES_PATH, telemetry.FORENSICS_PATH]:
            write(path, {"schema_version": "1.0.0", "revision": 0, "items": []})
        write(telemetry.CONFIG_PATH, {
            "heartbeat_interval_seconds": 300,
            "suspected_stall_after_seconds": 900,
            "stalled_after_seconds": 1800,
            "progress_recency_seconds": 1800,
        })

        # TEST D — heartbeat/liveness alone must never imply work progress.
        heartbeat_at = (t0 + timedelta(seconds=60)).isoformat()
        telemetry.record_beacon(
            session=session_a,
            event_type="HEARTBEAT",
            source="CLIENT_EMITTER",
            observed_at=heartbeat_at,
        )
        signals = telemetry.session_signal_projection(
            "session-a",
            generated_at=(t0 + timedelta(seconds=120)).isoformat(),
        )
        assert_true(signals["liveness"]["state"] == "ACTIVE", "heartbeat should make liveness ACTIVE")
        assert_true(signals["progress"]["state"] == "NO_RECENT_PROGRESS_EVIDENCE", "heartbeat must not advance progress")
        assert_true(signals["last_activity_at"] == heartbeat_at, "last activity should reflect heartbeat")
        assert_true(signals["last_liveness_evidence_at"] == heartbeat_at, "liveness timestamp should reflect heartbeat")
        assert_true(signals["last_progress_at"] == "UNAVAILABLE", "heartbeat must not create last_progress_at")

        progress_at = (t0 + timedelta(seconds=180)).isoformat()
        telemetry.record_beacon(
            session=session_a,
            event_type="ACTION_TRACE",
            source="CLIENT_EMITTER",
            action_id="action-1",
            action_label="update governed artifact",
            action_phase="COMPLETED",
            outcome="PASS",
            written_head_sha="b" * 40,
            checkpoint_ref="CHK-GACR-TEST-1",
            evidence_ref="ci:gacr-test",
            observed_at=progress_at,
        )
        signals = telemetry.session_signal_projection(
            "session-a",
            generated_at=(t0 + timedelta(seconds=181)).isoformat(),
        )
        assert_true(signals["liveness"]["state"] == "ACTIVE", "progress evidence is also fresh activity")
        assert_true(signals["progress"]["state"] == "ADVANCING", "qualifying completed action should advance progress")
        assert_true(signals["last_progress_at"] == progress_at, "progress timestamp must be independent")
        assert_true(signals["progress"]["last_progress_evidence"]["class"] == "ACTION_COMPLETED", "progress class should be explicit")

        # TEST E — ambiguous repository activity remains canonical UNBOUND_ACTIVITY.
        session_b = base_session("session-b", connection_ref="conn-b", t0=t0)
        sessions_doc = json.loads(telemetry.SESSIONS_PATH.read_text(encoding="utf-8"))
        sessions_doc["sessions"].append(session_b)
        write(telemetry.SESSIONS_PATH, sessions_doc)

        ambiguous_at = (t0 + timedelta(seconds=300)).isoformat()
        ambiguous = telemetry.record_beacon(
            session=None,
            event_type="GITHUB_EVENT_ACTIVITY",
            source="GITHUB_ACTIONS",
            task_id="TASK-1",
            branch="feature/a",
            pull_request=12,
            observed_at=ambiguous_at,
        )
        telemetry.correlate_all()
        unbound = telemetry.unbound_activity_projection()
        item = next(x for x in unbound["items"] if x["observation_id"] == ambiguous["beacon_id"])
        assert_true(item["status"] == "UNBOUND", "ambiguous activity must remain UNBOUND")
        assert_true(item["correlation_level"] == "AMBIGUOUS", "correlation level must be preserved")
        assert_true(item["reconciled_session_id"] == "UNAVAILABLE", "no arbitrary session may be selected")

        pre_reconcile = telemetry.session_signal_projection(
            "session-a",
            generated_at=(t0 + timedelta(seconds=301)).isoformat(),
        )
        assert_true(pre_reconcile["last_activity_at"] != ambiguous_at, "unbound activity must not renew a candidate session")

        sessions_doc = json.loads(telemetry.SESSIONS_PATH.read_text(encoding="utf-8"))
        next(s for s in sessions_doc["sessions"] if s["session_id"] == "session-b")["relay"]["branch"] = "feature/other"
        write(telemetry.SESSIONS_PATH, sessions_doc)
        telemetry.correlate_all()
        reconciled = telemetry.unbound_activity_projection()
        reconciled_item = next(x for x in reconciled["items"] if x["observation_id"] == ambiguous["beacon_id"])
        assert_true(reconciled_item["status"] == "RECONCILED", "later deterministic evidence should reconcile the same activity")
        assert_true(reconciled_item["reconciled_session_id"] == "session-a", "reconciliation should bind deterministically")
        same = next(x for x in telemetry.unbound_activity_projection()["items"] if x["observation_id"] == ambiguous["beacon_id"])
        assert_true(same["reconciled_at"] == reconciled_item["reconciled_at"], "reconciliation must be idempotent")

        # Generic challenge semantics: response is observed-only, timeout never invents a cause.
        busy = telemetry.evaluate_liveness_challenge(
            session_id="session-a",
            challenge_id="challenge-1",
            response="BUSY",
            observed_at=(t0 + timedelta(seconds=360)).isoformat(),
        )
        assert_true(busy["status"] == "LIVENESS_CHALLENGE_ACK", "supported response should ACK")
        assert_true(busy["response"] == "BUSY", "challenge response must be preserved")
        timeout = telemetry.evaluate_liveness_challenge(
            session_id="session-a",
            challenge_id="challenge-2",
            response=None,
            observed_at=(t0 + timedelta(seconds=420)).isoformat(),
        )
        assert_true(timeout["status"] == "LIVENESS_CHALLENGE_TIMEOUT", "no response should produce timeout semantics")
        assert_true(timeout["cause"] == "UNAVAILABLE", "timeout must not invent browser/provider/network cause")

        # TEST F — one Agent Context aggregates existing stores with explicit UNAVAILABLE values.
        telemetry.build_interruption_forensics(
            "session-a",
            persist=True,
            generated_at=(t0 + timedelta(seconds=430)).isoformat(),
        )
        context = telemetry.agent_context(
            "session-a",
            generated_at=(t0 + timedelta(seconds=430)).isoformat(),
        )
        assert_true(context["repository"] == "owner/repo", "context repository")
        assert_true(context["task_id"] == "TASK-1", "context task")
        assert_true(context["branch"] == "feature/a", "context branch")
        assert_true(context["pull_request"] == 12, "context PR")
        assert_true(context["observed_head"] == "a" * 40, "observed head must remain distinct")
        assert_true(context["written_head"] == "b" * 40, "written head must come from qualifying evidence")
        assert_true(context["last_activity_at"] != context["last_progress_at"], "activity and progress timestamps must be distinct facts")
        assert_true(context["last_liveness_evidence_at"] != "UNAVAILABLE", "context liveness evidence")
        assert_true(context["progress_evidence"] != "UNAVAILABLE", "context progress evidence")
        assert_true(context["action_completed"]["action_id"] == "action-1", "completed action")
        assert_true(context["action_in_flight"] == "UNAVAILABLE", "unknown/open action must be explicit")
        assert_true(context["checkpoint"] == "CHK-GACR-TEST-1", "checkpoint")
        assert_true(context["provider_conversation_ref"] == "UNAVAILABLE", "provider ref must not be invented")
        assert_true(context["exact_head_reobservation_requirement"] is True, "exact-head reobservation remains mandatory")
        assert_true(isinstance(context["known_limitations"], list) and context["known_limitations"], "known limitations must be explicit")
        assert_true(context["takeover"]["eligible"] is False, "active session is not takeover-ready")

        # TEST G — quiet/suspected/stalled/takeover-ready is evidence-time driven; claim is preserved.
        stall_sessions = {"schema_version": "1.0.0", "revision": 0, "sessions": []}
        stall_claims = {"schema_version": "1.0.0", "revision": 0, "claims": []}
        stall_takeovers = {"schema_version": "1.0.0", "revision": 0, "last_scan_at": None, "items": []}
        config = {
            "heartbeat_interval_seconds": 300,
            "suspected_stall_after_seconds": 900,
            "stalled_after_seconds": 1800,
            "progress_recency_seconds": 1800,
            "external_conversation_reference": {"persist_full_url": False},
            "takeover": {"auto_offer_to_compatible_standby": True},
        }
        stalled, _ = relay.register_docs(
            config,
            stall_sessions,
            repository="owner/repo",
            agent="Stall-A",
            provider="chatgpt",
            provider_ref=None,
            provider_url=None,
            connection_ref="stall-a",
            observed_head="c" * 40,
            branch="feature/stall",
            task_id="TASK-STALL",
            pull_request=99,
            standby=False,
            timestamp=t0,
        )
        stall_claims["claims"].append({
            "session_id": stalled["session_id"],
            "work_item_id": "WORK-STALL",
            "collision_domains": ["gacr-stall"],
            "status": "ACTIVE",
            "claimed_head_sha": "c" * 40,
            "claimed_at": t0.isoformat(),
            "released_at": None,
        })

        write(telemetry.SESSIONS_PATH, stall_sessions)
        write(telemetry.CLAIMS_PATH, stall_claims)
        write(telemetry.TAKEOVERS_PATH, stall_takeovers)
        for path in [telemetry.BEACONS_PATH, telemetry.CORRELATIONS_PATH, telemetry.DISPATCHES_PATH, telemetry.FORENSICS_PATH]:
            write(path, {"schema_version": "1.0.0", "revision": 0, "items": []})
        quiet = telemetry.session_signal_projection(
            stalled["session_id"],
            generated_at=(t0 + timedelta(seconds=600)).isoformat(),
        )
        assert_true(quiet["liveness"]["state"] == "QUIET", "stale-but-pre-suspect evidence should project QUIET")

        relay.scan_docs(config, stall_sessions, stall_claims, stall_takeovers, timestamp=t0 + timedelta(seconds=1000))
        write(telemetry.SESSIONS_PATH, stall_sessions)
        suspected = telemetry.session_signal_projection(
            stalled["session_id"],
            generated_at=(t0 + timedelta(seconds=1000)).isoformat(),
        )
        assert_true(suspected["liveness"]["state"] == "SUSPECTED_STALL", "Watch suspected state must project directly")

        relay.scan_docs(config, stall_sessions, stall_claims, stall_takeovers, timestamp=t0 + timedelta(seconds=1900))
        write(telemetry.SESSIONS_PATH, stall_sessions)
        write(telemetry.TAKEOVERS_PATH, stall_takeovers)
        stalled_projection = telemetry.session_signal_projection(
            stalled["session_id"],
            generated_at=(t0 + timedelta(seconds=1900)).isoformat(),
        )
        assert_true(stalled_projection["liveness"]["state"] == "STALLED", "expired lease should project STALLED")
        assert_true(stall_claims["claims"][0]["status"] == "ACTIVE", "stall must not release active claim")
        forensics = telemetry.build_interruption_forensics(
            stalled["session_id"],
            persist=False,
            generated_at=(t0 + timedelta(seconds=1900)).isoformat(),
        )
        assert_true(forensics["cause"]["code"] == "UNOBSERVED_EXTERNAL_CAUSE", "stall must not invent external cause")
        stalled_context = telemetry.agent_context(
            stalled["session_id"],
            generated_at=(t0 + timedelta(seconds=1900)).isoformat(),
        )
        assert_true(stalled_context["takeover"]["eligible"] is True, "TAKEOVER_READY must be exposed separately from liveness")

    print("GACR_LIVENESS_PROGRESS_CONTEXT_TEST_PASS")


if __name__ == "__main__":
    main()
