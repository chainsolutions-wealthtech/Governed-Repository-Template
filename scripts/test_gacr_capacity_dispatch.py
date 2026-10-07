#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gacr_capacity_dispatch", ROOT / "scripts" / "gacr_capacity_dispatch.py")
g = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = g
SPEC.loader.exec_module(g)


def assert_true(value, message: str) -> None:
    if not value:
        raise AssertionError(message)


def live_signal(state: str = "ACTIVE") -> dict:
    return {
        "liveness": {"state": state},
        "progress": {"state": "NO_RECENT_PROGRESS_EVIDENCE"},
    }


def session(session_id: str, *, capabilities=None, role="CODE_AGENT", relay_state="ACTIVE") -> dict:
    return {
        "session_id": session_id,
        "repository": "example/repo",
        "provider": "chatgpt",
        "client_instance_id": "client-" + session_id,
        "agent_role": role,
        "capabilities": capabilities or [],
        "authority_grants": [],
        "status": "ACTIVE",
        "relay": {"state": relay_state, "branch": "main"},
    }


def availability_beacon(session_id: str, state: str, reason: str = "WAITING_FOR_WORK") -> dict:
    return {
        "beacon_id": "b-" + session_id + "-" + state,
        "session_id": session_id,
        "observed_at": "2026-10-07T01:00:00+00:00",
        "event_type": "AVAILABILITY_UPDATE",
        "availability_state": state,
        "availability_reason_code": reason,
    }


def main() -> None:
    sessions = {"sessions": [session("s1", capabilities=["CODE"]), session("s2", capabilities=["REVIEW"], role="REVIEWER")]}
    empty_claims = {"claims": []}
    empty_correlations = {"items": []}

    available = g.session_capacity_projection(
        "s1",
        sessions_doc=sessions,
        claims_doc=empty_claims,
        beacons_doc={"items": [availability_beacon("s1", "AVAILABLE")]},
        correlations_doc=empty_correlations,
        signal_projection=live_signal(),
    )
    assert_true(available["availability_state"] == "AVAILABLE", "explicit available state preserved")
    assert_true(available["eligible_for_new_work"] is True, "explicit available live session eligible")

    silent = g.session_capacity_projection(
        "s1",
        sessions_doc=sessions,
        claims_doc=empty_claims,
        beacons_doc={"items": []},
        correlations_doc=empty_correlations,
        signal_projection=live_signal(),
    )
    assert_true(silent["availability_state"] == "UNKNOWN", "silence must not imply availability")
    assert_true(silent["eligible_for_new_work"] is False, "silent session not dispatch eligible")

    quota = g.session_capacity_projection(
        "s1",
        sessions_doc=sessions,
        claims_doc=empty_claims,
        beacons_doc={"items": [{
            "beacon_id": "b-quota",
            "session_id": "s1",
            "observed_at": "2026-10-07T01:01:00+00:00",
            "event_type": "INTERRUPTION_SIGNAL",
            "interruption_code": "PROVIDER_QUOTA_EXHAUSTED",
        }]},
        correlations_doc=empty_correlations,
        signal_projection=live_signal(),
    )
    assert_true(quota["availability_state"] == "QUOTA_BLOCKED", "quota signal blocks capacity")
    assert_true(quota["eligible_for_new_work"] is False, "quota-blocked agent not eligible")

    rate = g.session_capacity_projection(
        "s1",
        sessions_doc=sessions,
        claims_doc=empty_claims,
        beacons_doc={"items": [{
            "beacon_id": "b-rate",
            "session_id": "s1",
            "observed_at": "2026-10-07T01:02:00+00:00",
            "event_type": "INTERRUPTION_SIGNAL",
            "interruption_code": "PROVIDER_RATE_LIMIT",
        }]},
        correlations_doc=empty_correlations,
        signal_projection=live_signal(),
    )
    assert_true(rate["availability_state"] == "RATE_LIMITED", "rate-limit signal blocks capacity")

    busy = g.session_capacity_projection(
        "s1",
        sessions_doc=sessions,
        claims_doc={"claims": [{
            "claim_id": "claim-1",
            "session_id": "s1",
            "work_item_id": "W0",
            "status": "ACTIVE",
            "collision_domains": ["domain-0"],
        }]},
        beacons_doc={"items": [availability_beacon("s1", "AVAILABLE")]},
        correlations_doc=empty_correlations,
        signal_projection=live_signal(),
    )
    assert_true(busy["availability_state"] == "BUSY", "active claim overrides available signal")
    assert_true(busy["eligible_for_new_work"] is False, "claimed agent not eligible")

    pool = {
        "items": [
            {
                "session_id": "s1",
                "client_instance_id": "client-s1",
                "repository": "example/repo",
                "agent_role": "CODE_AGENT",
                "capabilities": ["CODE"],
                "authority_grants": [],
                "eligible_for_new_work": True,
            },
            {
                "session_id": "s2",
                "client_instance_id": "client-s2",
                "repository": "example/repo",
                "agent_role": "REVIEWER",
                "capabilities": ["REVIEW"],
                "authority_grants": [],
                "eligible_for_new_work": True,
            },
        ]
    }
    work = {
        "items": [
            {
                "work_item_id": "W1",
                "title": "code lane",
                "status": "READY",
                "priority": 100,
                "sequence": 1,
                "dependencies": [],
                "collision_domains": ["domain-a"],
                "required_capabilities": ["CODE"],
                "allowed_agent_roles": ["CODE_AGENT"],
            },
            {
                "work_item_id": "W2",
                "title": "same collision lane",
                "status": "READY",
                "priority": 90,
                "sequence": 2,
                "dependencies": [],
                "collision_domains": ["domain-a"],
            },
            {
                "work_item_id": "W3",
                "title": "review lane",
                "status": "READY",
                "priority": 80,
                "sequence": 3,
                "dependencies": [],
                "collision_domains": ["domain-b"],
                "required_capabilities": ["REVIEW"],
                "allowed_agent_roles": ["REVIEWER"],
            },
        ]
    }
    plan = g.parallel_work_dispatch_plan(work_doc=work, claims_doc=empty_claims, pool=pool)
    assigned = {item["work_item_id"]: item["target_session_id"] for item in plan["assignments"]}
    assert_true(assigned == {"W1": "s1", "W3": "s2"}, f"unexpected parallel assignments: {assigned}")
    blocked = next(item for item in plan["unassigned"] if item["work_item_id"] == "W2")
    assert_true(blocked["reason"] == "COLLISION_DOMAIN_BUSY", "same collision domain must not parallelize")
    assert_true(plan["write_authority_granted"] is False, "dispatch plan never grants write authority")
    assert_true(plan["claim_transfer_performed"] is False, "dispatch plan never creates/transfers claim")

    unscoped_plan = g.parallel_work_dispatch_plan(
        work_doc={"items": [{
            "work_item_id": "W-UNSCOPED",
            "status": "READY",
            "priority": 1,
            "sequence": 99,
            "dependencies": [],
            "collision_domains": ["domain-unscoped"],
        }]},
        claims_doc=empty_claims,
        pool=pool,
    )
    assert_true(not unscoped_plan["assignments"], "unscoped work must not auto-dispatch")
    assert_true(
        unscoped_plan["unassigned"][0]["reason"] == "WORK_COMPATIBILITY_SCOPE_UNDECLARED",
        "unscoped work fail-closed reason",
    )

    claimed_plan = g.parallel_work_dispatch_plan(
        work_doc={"items": [{
            "work_item_id": "W4",
            "status": "READY",
            "priority": 1,
            "sequence": 1,
            "dependencies": [],
            "collision_domains": ["domain-c"],
        }]},
        claims_doc={"claims": [{
            "claim_id": "claim-c",
            "session_id": "other",
            "work_item_id": "existing",
            "status": "ACTIVE",
            "collision_domains": ["domain-c"],
        }]},
        pool=pool,
    )
    assert_true(not claimed_plan["assignments"], "active collision-domain claim blocks assignment")
    assert_true(claimed_plan["unassigned"][0]["reason"] == "COLLISION_DOMAIN_BUSY", "claim collision reason")

    print("GACR_CAPACITY_PARALLEL_DISPATCH_TEST_PASS")


if __name__ == "__main__":
    main()
