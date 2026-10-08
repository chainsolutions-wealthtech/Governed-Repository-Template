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


def session(session_id: str, *, capabilities=None, role="qualification-client", relay_state="ACTIVE", agent_identity=None) -> dict:
    return {
        "session_id": session_id,
        "agent_identity": agent_identity or ("agent-" + session_id),
        "repository": "example/repo",
        "provider": "chatgpt",
        "client_instance_id": "client-" + session_id,
        "agent_role": role,
        "capabilities": capabilities or [],
        "authority_grants": [],
        "status": "ACTIVE",
        "relay": {"state": relay_state, "branch": "main"},
    }


def release_beacon(
    session_id: str,
    *,
    role: str = "CODE_AGENT",
    purpose: str = "WORK_ON_CONTROL_PLANE",
    work_kind: str = "CODE_IMPLEMENTATION",
    observed_at: str = "2026-10-07T01:00:00+00:00",
) -> dict:
    return {
        "beacon_id": "b-" + session_id + "-f1",
        "session_id": session_id,
        "observed_at": observed_at,
        "event_type": "F1_RELEASED",
        "evidence_ref": "gscc-exposure:test",
        "agent_role": role,
        "agent_role_provenance": "DECLARED_BY_EVENT",
        "entry_purpose": purpose,
        "entry_purpose_provenance": "DECLARED_BY_EVENT",
        "work_kind": work_kind,
        "work_kind_provenance": "DECLARED_BY_EVENT",
        "capabilities": [],
        "capabilities_provenance": "SESSION_SNAPSHOT",
    }


def availability_beacon(
    session_id: str,
    state: str,
    reason: str = "WAITING_FOR_WORK",
    observed_at: str = "2026-10-07T01:01:00+00:00",
) -> dict:
    return {
        "beacon_id": "b-" + session_id + "-" + state + "-" + observed_at,
        "session_id": session_id,
        "observed_at": observed_at,
        "event_type": "AVAILABILITY_UPDATE",
        "availability_state": state,
        "availability_reason_code": reason,
    }


def interruption_beacon(session_id: str, code: str, observed_at: str) -> dict:
    return {
        "beacon_id": "b-" + session_id + "-" + code,
        "session_id": session_id,
        "observed_at": observed_at,
        "event_type": "INTERRUPTION_SIGNAL",
        "interruption_code": code,
    }


def main() -> None:
    sessions = {"sessions": [session("s1", capabilities=["CODE"]), session("s2", capabilities=["REVIEW"])]}
    empty_claims = {"claims": []}
    empty_correlations = {"items": []}

    released_available_beacons={"items":[release_beacon("s1"),availability_beacon("s1","AVAILABLE")]}
    available = g.session_capacity_projection(
        "s1",
        sessions_doc=sessions,
        claims_doc=empty_claims,
        beacons_doc=released_available_beacons,
        correlations_doc=empty_correlations,
        signal_projection=live_signal(),
    )
    assert_true(available["availability_state"] == "AVAILABLE", "explicit available state preserved")
    assert_true(available["f1_release_verified"] is True, "F1 release must be recognized")
    assert_true(available["agent_role"] == "CODE_AGENT", "declared canonical role overrides qualification role")
    assert_true(available["declared_work_profile"]["entry_purpose"] == "WORK_ON_CONTROL_PLANE", "entry purpose recorded")
    assert_true(available["eligible_for_new_work"] is True, "released explicitly available session eligible")
    assert_true(available["logical_agent_id"] == "agent-s1", "capacity projection uses canonical agent identity")

    pre_f1 = g.session_capacity_projection(
        "s1",
        sessions_doc=sessions,
        claims_doc=empty_claims,
        beacons_doc={"items":[availability_beacon("s1","AVAILABLE")]},
        correlations_doc=empty_correlations,
        signal_projection=live_signal(),
    )
    if g.TEMPLATE_SOURCE:
        assert_true(pre_f1["eligible_for_new_work"] is False, "pre-F1 source session cannot receive work")
        assert_true("F1_RELEASE_NOT_VERIFIED" in pre_f1["dispatch_blockers"], "pre-F1 blocker explicit")

    silent = g.session_capacity_projection(
        "s1",
        sessions_doc=sessions,
        claims_doc=empty_claims,
        beacons_doc={"items": [release_beacon("s1")]},
        correlations_doc=empty_correlations,
        signal_projection=live_signal(),
    )
    assert_true(silent["availability_state"] == "UNKNOWN", "F1 release alone must not imply availability")
    assert_true(silent["eligible_for_new_work"] is False, "silent session not dispatch eligible")

    quota = g.session_capacity_projection(
        "s1",
        sessions_doc=sessions,
        claims_doc=empty_claims,
        beacons_doc={"items": [
            release_beacon("s1"),
            availability_beacon("s1","AVAILABLE",observed_at="2026-10-07T01:01:00+00:00"),
            interruption_beacon("s1","PROVIDER_QUOTA_EXHAUSTED","2026-10-07T01:02:00+00:00"),
        ]},
        correlations_doc=empty_correlations,
        signal_projection=live_signal(),
    )
    assert_true(quota["availability_state"] == "QUOTA_BLOCKED", "quota signal blocks capacity")
    assert_true(quota["eligible_for_new_work"] is False, "quota-blocked agent not eligible")

    recovered = g.session_capacity_projection(
        "s1",
        sessions_doc=sessions,
        claims_doc=empty_claims,
        beacons_doc={"items": [
            release_beacon("s1"),
            interruption_beacon("s1","DEPENDENCY_BLOCKED","2026-10-07T01:02:00+00:00"),
            availability_beacon("s1","WAITING",observed_at="2026-10-07T01:03:00+00:00"),
        ]},
        correlations_doc=empty_correlations,
        signal_projection=live_signal(),
    )
    assert_true(recovered["availability_state"] == "WAITING", "new explicit availability clears older interruption")
    assert_true(recovered["eligible_for_new_work"] is True, "recovered released agent becomes eligible")

    rate = g.session_capacity_projection(
        "s1",
        sessions_doc=sessions,
        claims_doc=empty_claims,
        beacons_doc={"items": [
            release_beacon("s1"),
            availability_beacon("s1","AVAILABLE",observed_at="2026-10-07T01:01:00+00:00"),
            interruption_beacon("s1","PROVIDER_RATE_LIMIT","2026-10-07T01:02:00+00:00"),
        ]},
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
        beacons_doc=released_available_beacons,
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
        "source":"TEST",
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

    same_agent_pool = {
        "items": [
            {
                "session_id": "same-a",
                "logical_agent_id": "logical-shared",
                "client_instance_id": "client-same-a",
                "repository": "example/repo",
                "agent_role": "CODE_AGENT",
                "capabilities": ["CODE"],
                "authority_grants": [],
                "eligible_for_new_work": True,
                "active_claim_count": 0,
                "in_flight_action": None,
            },
            {
                "session_id": "same-b",
                "logical_agent_id": "logical-shared",
                "client_instance_id": "client-same-b",
                "repository": "example/repo",
                "agent_role": "CODE_AGENT",
                "capabilities": ["CODE"],
                "authority_grants": [],
                "eligible_for_new_work": True,
                "active_claim_count": 0,
                "in_flight_action": None,
            },
        ]
    }
    same_agent_work = {
        "source": "TEST",
        "items": [
            {
                "work_item_id": "LW1",
                "status": "READY",
                "priority": 100,
                "sequence": 1,
                "dependencies": [],
                "collision_domains": ["logical-domain-a"],
                "required_capabilities": ["CODE"],
                "allowed_agent_roles": ["CODE_AGENT"],
            },
            {
                "work_item_id": "LW2",
                "status": "READY",
                "priority": 90,
                "sequence": 2,
                "dependencies": [],
                "collision_domains": ["logical-domain-b"],
                "required_capabilities": ["CODE"],
                "allowed_agent_roles": ["CODE_AGENT"],
            },
        ],
    }
    same_agent_plan = g.parallel_work_dispatch_plan(
        work_doc=same_agent_work,
        claims_doc=empty_claims,
        pool=same_agent_pool,
    )
    assert_true(len(same_agent_plan["assignments"]) == 1, "two sessions of one logical agent must not create two automatic capacity units")
    assert_true(
        same_agent_plan["assignments"][0]["target_logical_agent_id"] == "logical-shared",
        "assignment preserves logical-agent trace",
    )
    logical_blocked = next(item for item in same_agent_plan["unassigned"] if item["work_item_id"] == "LW2")
    assert_true(logical_blocked["reason"] == "NO_COMPATIBLE_AVAILABLE_AGENT", "second logical-agent slot must be unavailable")
    assert_true(
        all(
            "LOGICAL_AGENT_OFFER_CAPACITY_REACHED" in evaluation["reasons"]
            for evaluation in logical_blocked["evaluations"]
        ),
        "all sibling sessions must share one default logical-agent offer ceiling",
    )

    pending_offer_dispatches = {
        "items": [{
            "dispatch_id": "GACR-W-existing-logical",
            "dispatch_kind": "WORK_OFFER",
            "status": "READY",
            "target_session_id": "same-a",
            "target_logical_agent_id": "logical-shared",
            "capacity_key": "logical-agent:logical-shared",
            "work_item_id": "LW-PENDING",
        }]
    }
    pending_offer_plan = g.parallel_work_dispatch_plan(
        work_doc={
            "source": "TEST",
            "items": [{
                "work_item_id": "LW-PENDING-NEXT",
                "status": "READY",
                "priority": 1,
                "sequence": 1,
                "dependencies": [],
                "collision_domains": ["logical-domain-pending-next"],
                "required_capabilities": ["CODE"],
                "allowed_agent_roles": ["CODE_AGENT"],
            }],
        },
        claims_doc=empty_claims,
        pool=same_agent_pool,
        dispatches_doc=pending_offer_dispatches,
    )
    assert_true(
        not pending_offer_plan["assignments"],
        "persisted pending offer must consume shared logical-agent capacity across dispatch runs",
    )
    pending_blocked = pending_offer_plan["unassigned"][0]
    assert_true(
        all(
            "LOGICAL_AGENT_OFFER_CAPACITY_REACHED" in evaluation["reasons"]
            for evaluation in pending_blocked["evaluations"]
        ),
        "pending sibling offer blocks every session surface of the same logical agent",
    )
    assert_true(
        pending_offer_plan["pending_offer_capacity_counts"]
        == {"logical-agent:logical-shared": 1},
        "planner exposes pending logical-agent offer occupancy",
    )

    duplicate_pending_work_plan = g.parallel_work_dispatch_plan(
        work_doc={
            "source": "TEST",
            "items": [{
                "work_item_id": "LW-PENDING",
                "status": "READY",
                "priority": 1,
                "sequence": 1,
                "dependencies": [],
                "collision_domains": ["logical-domain-duplicate-work"],
                "required_capabilities": ["CODE"],
                "allowed_agent_roles": ["CODE_AGENT"],
            }],
        },
        claims_doc=empty_claims,
        pool={
            "items": [
                {
                    **same_agent_pool["items"][0],
                    "session_id": "other-agent-session",
                    "logical_agent_id": "logical-other",
                    "client_instance_id": "client-other-agent",
                }
            ]
        },
        dispatches_doc=pending_offer_dispatches,
    )
    assert_true(
        not duplicate_pending_work_plan["assignments"],
        "same work item cannot be offered to a second logical agent while an offer is pending",
    )
    assert_true(
        duplicate_pending_work_plan["unassigned"][0]["reason"] == "OFFER_ALREADY_PENDING",
        "duplicate work offer rejection is explicit",
    )

    cancelled_offer_plan = g.parallel_work_dispatch_plan(
        work_doc={
            "source": "TEST",
            "items": [{
                "work_item_id": "LW-AFTER-CANCEL",
                "status": "READY",
                "priority": 1,
                "sequence": 1,
                "dependencies": [],
                "collision_domains": ["logical-domain-after-cancel"],
                "required_capabilities": ["CODE"],
                "allowed_agent_roles": ["CODE_AGENT"],
            }],
        },
        claims_doc=empty_claims,
        pool=same_agent_pool,
        dispatches_doc={
            "items": [{
                **pending_offer_dispatches["items"][0],
                "status": "CANCELLED",
            }]
        },
    )
    assert_true(
        len(cancelled_offer_plan["assignments"]) == 1,
        "terminal/cancelled offer must release logical-agent offer capacity",
    )

    same_agent_claimed = g.parallel_work_dispatch_plan(
        work_doc={
            "source": "TEST",
            "items": [{
                "work_item_id": "LW3",
                "status": "READY",
                "priority": 1,
                "sequence": 1,
                "dependencies": [],
                "collision_domains": ["logical-domain-c"],
                "required_capabilities": ["CODE"],
                "allowed_agent_roles": ["CODE_AGENT"],
            }],
        },
        claims_doc={"claims": [{
            "claim_id": "logical-existing-claim",
            "session_id": "same-a",
            "work_item_id": "LW0",
            "status": "ACTIVE",
            "collision_domains": ["unrelated-logical-domain"],
        }]},
        pool=same_agent_pool,
    )
    assert_true(not same_agent_claimed["assignments"], "active claim on one sibling session consumes shared logical-agent capacity")
    assert_true(
        all(
            "LOGICAL_AGENT_OFFER_CAPACITY_REACHED" in evaluation["reasons"]
            for evaluation in same_agent_claimed["unassigned"][0]["evaluations"]
        ),
        "sibling session cannot bypass logical-agent capacity through a new chat/runtime",
    )

    original_read_json = g.read_json
    original_write_json = g.write_json
    original_session_capacity_projection = g.session_capacity_projection
    original_agent_pool_projection = g.agent_pool_projection
    original_template_source = g.TEMPLATE_SOURCE
    try:
        accept_store = {
            "schema_version": "1.0.0",
            "revision": 0,
            "items": [
                {
                    "dispatch_id": "GACR-W-accept-target",
                    "dispatch_kind": "WORK_OFFER",
                    "status": "READY",
                    "target_session_id": "same-a",
                    "work_item_id": "LW-ACCEPT",
                },
                {
                    "dispatch_id": "GACR-W-accept-sibling",
                    "dispatch_kind": "WORK_OFFER",
                    "status": "READY",
                    "target_session_id": "same-b",
                    "work_item_id": "LW-OTHER",
                },
            ],
        }
        accept_claims = {"claims": []}
        def fake_read(path, default=None):
            if path == g.DISPATCHES_PATH:
                return accept_store
            if path == g.CLAIMS_PATH:
                return accept_claims
            return default or {}
        g.read_json = fake_read
        g.write_json = lambda path, value: None
        g.session_capacity_projection = lambda session_id: {
            "availability_state": "AVAILABLE",
            "eligible_for_new_work": True,
        }
        g.agent_pool_projection = lambda: same_agent_pool
        g.TEMPLATE_SOURCE = False
        try:
            g.accept_work_offer("GACR-W-accept-target", "same-a")
        except ValueError as exc:
            assert_true(
                "another pending work offer" in str(exc),
                f"sibling pending offer rejection should be explicit: {exc}",
            )
        else:
            raise AssertionError("accept must fail when sibling session already owns pending logical-agent offer")

        accept_store["items"] = [accept_store["items"][0]]
        accept_claims["claims"] = [{
            "claim_id": "sibling-active-claim",
            "session_id": "same-b",
            "work_item_id": "LW-CLAIMED",
            "status": "ACTIVE",
            "collision_domains": ["other-domain"],
        }]
        try:
            g.accept_work_offer("GACR-W-accept-target", "same-a")
        except ValueError as exc:
            assert_true(
                "active canonical claim" in str(exc),
                f"sibling active claim rejection should be explicit: {exc}",
            )
        else:
            raise AssertionError("accept must fail when sibling session already owns active logical-agent claim")
    finally:
        g.read_json = original_read_json
        g.write_json = original_write_json
        g.session_capacity_projection = original_session_capacity_projection
        g.agent_pool_projection = original_agent_pool_projection
        g.TEMPLATE_SOURCE = original_template_source

    claimed_plan = g.parallel_work_dispatch_plan(
        work_doc={"source":"TEST","items": [{
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

    if g.TEMPLATE_SOURCE:
        canonical=g.canonical_work_document()
        assert_true(canonical["source"]=="CONTROL_PLANE_CANONICAL_TASK_GRAPH", "source control plane must use canonical graph")
        assert_true(canonical["global_task_id"]=="GMC-01", f"unexpected global task: {canonical}")
        assert_true(canonical["work_package_id"]=="GMC-G01", f"unexpected work package: {canonical}")
        ready=[x for x in canonical["items"] if x["status"]=="READY"]
        assert_true([x["work_item_id"] for x in ready]==["GMC-G01-T01"], f"only GMC-G01-T01 should be ready: {ready}")
        assert_true(all(x["work_item_id"]!="WORK-INIT-001" for x in canonical["items"]), "source queue must exclude bootstrap WORK-INIT-001")
        assert_true(ready[0]["allowed_agent_roles"]==["CODE_AGENT"], "GMC atomic task must target code agent lane")
        assert_true(ready[0]["implementation_authorized"] is False, "planning-only task must not imply implementation authority")

    print("GACR_CAPACITY_PARALLEL_DISPATCH_TEST_PASS")


if __name__ == "__main__":
    main()
