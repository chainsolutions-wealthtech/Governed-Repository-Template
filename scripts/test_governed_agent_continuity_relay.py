#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "governed_agent_continuity_relay.py"


def load_module():
    spec = importlib.util.spec_from_file_location("gacr", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise SystemExit("GACR_TEST_FAILED: unable to load module")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def base_config():
    return {
        "stalled_after_seconds": 1800,
        "suspected_stall_after_seconds": 900,
        "external_conversation_reference": {
            "persist_full_url": False,
        },
        "takeover": {
            "auto_offer_to_compatible_standby": True,
        },
    }


def empty_sessions():
    return {"schema_version": "1.0.0", "revision": 0, "sessions": []}


def empty_claims():
    return {"schema_version": "1.0.0", "revision": 0, "claims": []}


def empty_takeovers():
    return {"schema_version": "1.0.0", "revision": 0, "last_scan_at": None, "items": []}


def assert_true(value, message):
    if not value:
        raise SystemExit("GACR_TEST_FAILED: " + message)


def main():
    gacr = load_module()
    config = base_config()
    sessions = empty_sessions()
    claims = empty_claims()
    takeovers = empty_takeovers()
    t0 = datetime(2026, 10, 1, 18, 0, 0, tzinfo=timezone.utc)

    agent_a, resolution = gacr.register_docs(
        config,
        sessions,
        repository="owner/repo",
        agent="ChatGPT-A",
        provider="chatgpt",
        provider_ref=None,
        provider_url="https://chatgpt.com/c/6abe6ebe-3f98-83ed-b12e-2cf0f5b1e300",
        connection_ref=None,
        observed_head="a" * 40,
        branch="governance/p12-s6-close-case1",
        task_id="P12-S6",
        pull_request=96,
        standby=False,
        timestamp=t0,
    )
    assert_true(resolution == "CREATE", "agent A should be created")
    assert_true(
        agent_a["provider_conversation_ref"] == "6abe6ebe-3f98-83ed-b12e-2cf0f5b1e300",
        "ChatGPT conversation ID should be extracted from explicitly supplied URL",
    )
    assert_true("provider_conversation_url" not in agent_a, "full external URL should not persist by default")
    assert_true(
        gacr.reconstruct_url("chatgpt", agent_a["provider_conversation_ref"])
        == "https://chatgpt.com/c/6abe6ebe-3f98-83ed-b12e-2cf0f5b1e300",
        "ChatGPT URL should be reconstructable",
    )

    agent_b, _ = gacr.register_docs(
        config,
        sessions,
        repository="owner/repo",
        agent="ChatGPT-B",
        provider="chatgpt",
        provider_ref="standby-conversation-id",
        provider_url=None,
        connection_ref=None,
        observed_head="a" * 40,
        branch="main",
        task_id=None,
        pull_request=None,
        standby=True,
        timestamp=t0 + timedelta(seconds=1),
    )
    assert_true(agent_b["status"] == "STANDBY", "agent B should be standby")

    claims["claims"].append({
        "session_id": agent_a["session_id"],
        "work_item_id": "WORK-P12-S6",
        "collision_domains": ["control-plane-case1"],
        "status": "ACTIVE",
        "claimed_head_sha": "a" * 40,
        "claimed_at": gacr.iso(t0),
        "released_at": None,
    })

    changes = gacr.scan_docs(
        config,
        sessions,
        claims,
        takeovers,
        timestamp=t0 + timedelta(seconds=1000),
    )
    assert_true(agent_a["relay"]["state"] == "SUSPECTED_STALL", "late heartbeat should become suspected stall")
    assert_true(agent_a["status"] == "ACTIVE", "suspected stall must not release active session")
    assert_true(changes["stalled"] == [], "suspected stall should not be terminal")

    changes = gacr.scan_docs(
        config,
        sessions,
        claims,
        takeovers,
        timestamp=t0 + timedelta(seconds=1900),
    )
    assert_true(agent_a["relay"]["state"] == "TAKEOVER_READY", "expired lease should become takeover ready")
    assert_true(agent_a["status"] == "STALLED", "expired lease should mark top-level session stalled")
    assert_true(len(takeovers["items"]) == 1, "one takeover queue item should be created")
    takeover = takeovers["items"][0]
    assert_true(takeover["offered_to_session_id"] == agent_b["session_id"], "oldest compatible standby should be offered")
    assert_true(claims["claims"][0]["status"] == "ACTIVE", "stall detection must not silently release mutable claim")
    assert_true(claims["claims"][0]["session_id"] == agent_a["session_id"], "claim must remain with predecessor until accepted")

    gacr.scan_docs(
        config,
        sessions,
        claims,
        takeovers,
        timestamp=t0 + timedelta(seconds=2500),
    )
    assert_true(len(takeovers["items"]) == 1, "repeated scans must be idempotent for open takeover")

    try:
        gacr.heartbeat_docs(
            config,
            sessions,
            session_id=agent_a["session_id"],
            observed_head="b" * 40,
            action="RETURNED_LATE",
            evidence=None,
            timestamp=t0 + timedelta(seconds=2600),
        )
        raise SystemExit("GACR_TEST_FAILED: stalled predecessor heartbeat should fail")
    except ValueError:
        pass

    try:
        gacr.accept_takeover_docs(
            config,
            sessions,
            claims,
            takeovers,
            stalled_session_id=agent_a["session_id"],
            successor_session_id=agent_b["session_id"],
            reconciled_head_sha="b" * 40,
            actual_work_head_sha="c" * 40,
            timestamp=t0 + timedelta(seconds=2700),
        )
        raise SystemExit("GACR_TEST_FAILED: mismatched reconciled head should fail")
    except ValueError:
        pass

    result = gacr.accept_takeover_docs(
        config,
        sessions,
        claims,
        takeovers,
        stalled_session_id=agent_a["session_id"],
        successor_session_id=agent_b["session_id"],
        reconciled_head_sha="c" * 40,
        actual_work_head_sha="c" * 40,
        timestamp=t0 + timedelta(seconds=2800),
    )
    assert_true(result["status"] == "TAKEOVER_ACCEPTED", "takeover should succeed after exact-head reconciliation")
    assert_true(agent_a["relay"]["state"] == "HANDOFF_STALLED", "predecessor should be terminal after takeover")
    assert_true(agent_a["status"] == "CLOSED", "predecessor top-level session should close")
    assert_true(agent_b["relay"]["state"] == "ACTIVE", "successor should become active")
    assert_true(agent_b["relay"]["predecessor_session_id"] == agent_a["session_id"], "successor lineage should be preserved")
    assert_true(claims["claims"][0]["session_id"] == agent_b["session_id"], "active claim should transfer only after acceptance")
    assert_true(claims["claims"][0]["claimed_head_sha"] == "c" * 40, "transferred claim should use reconciled head")
    assert_true(takeover["status"] == "ACCEPTED", "takeover queue item should become accepted")

    try:
        gacr.heartbeat_docs(
            config,
            sessions,
            session_id=agent_a["session_id"],
            observed_head="c" * 40,
            action="LATE_RETURN",
            evidence=None,
            timestamp=t0 + timedelta(seconds=3000),
        )
        raise SystemExit("GACR_TEST_FAILED: predecessor must never resurrect after transferred takeover")
    except ValueError:
        pass

    upgrader=(ROOT/"scripts"/"control_plane_upgrade_local_entry.py").read_text(encoding="utf-8")
    for fragment in [
        "docs/GACR_AGENT_CONTINUITY_RELAY.md",
        ".governance/agent-relay/config.json",
        "scripts/governed_agent_continuity_relay.py",
        ".github/workflows/governed-agent-continuity-relay.yml",
        "existing_gacr_takeovers=target_text",
    ]:
        assert_true(fragment in upgrader, f"client upgrader missing GACR contract: {fragment}")

    workflow=(ROOT/".github"/"workflows"/"governed-agent-continuity-relay.yml").read_text(encoding="utf-8")
    for fragment in [
        "Governed Agent Continuity Relay",
        "cancel-in-progress: false",
        "GACR_NO_STATE_CHANGE",
    ]:
        assert_true(fragment in workflow, f"GACR workflow safety boundary missing: {fragment}")

    print("GACR_AGENT_CONTINUITY_RELAY_TEST_PASS")


if __name__ == "__main__":
    main()
