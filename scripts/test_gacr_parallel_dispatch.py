#!/usr/bin/env python3
from __future__ import annotations

import unittest

import gacr_parallel_dispatch as scheduler


def session(session_id: str, *, role: str = "CODE_AGENT", status: str = "ACTIVE", relay_state: str = "ACTIVE", capabilities=None):
    return {
        "session_id": session_id,
        "agent_identity": f"agent-{session_id}",
        "provider": "chatgpt",
        "agent_role": role,
        "status": status,
        "capabilities": capabilities or ["CODE_AGENT"],
        "wake_channels": ["POLL_REPOSITORY"],
        "relay": {
            "state": relay_state,
            "last_heartbeat_at": "2026-10-07T01:00:00+00:00",
        },
    }


def beacon(session_id: str, *, workload_state=None, interruption_code=None, blocker_code=None, capacity_slots=None, max_parallel_tasks=None):
    return {
        "beacon_id": f"beacon-{session_id}-{workload_state or interruption_code or 'base'}",
        "session_id": session_id,
        "observed_at": "2026-10-07T01:01:00+00:00",
        "agent_role": "CODE_AGENT",
        "capabilities": ["CODE_AGENT"],
        "workload_state": workload_state,
        "interruption_code": interruption_code,
        "blocker_code": blocker_code,
        "capacity_slots": capacity_slots,
        "max_parallel_tasks": max_parallel_tasks,
    }


class AvailabilityTests(unittest.TestCase):
    def test_explicit_idle_code_agent_is_available(self):
        s = session("s1")
        result = scheduler.classify_agent(
            s,
            {"items": [beacon("s1", workload_state="IDLE")]},
            {"claims": []},
            {"items": []},
        )
        self.assertEqual(result["scheduler_state"], "AVAILABLE")
        self.assertTrue(result["eligible_for_new_work"])
        self.assertEqual(result["availability_provenance"], "EXPLICIT_BEACON")

    def test_waiting_for_work_is_available(self):
        s = session("s1")
        result = scheduler.classify_agent(
            s,
            {"items": [beacon("s1", workload_state="WAITING_FOR_WORK")]},
            {"claims": []},
            {"items": []},
        )
        self.assertEqual(result["scheduler_state"], "AVAILABLE")
        self.assertTrue(result["eligible_for_new_work"])

    def test_rate_limited_agent_is_not_eligible(self):
        s = session("s1")
        b = beacon("s1", workload_state="RATE_LIMITED", blocker_code="PROVIDER_RATE_LIMIT")
        b["retry_after_at"] = "2026-10-07T02:00:00+00:00"
        result = scheduler.classify_agent(s, {"items": [b]}, {"claims": []}, {"items": []})
        self.assertEqual(result["scheduler_state"], "LIMITED")
        self.assertFalse(result["eligible_for_new_work"])
        self.assertEqual(result["retry_after_at"], "2026-10-07T02:00:00+00:00")

    def test_explicit_waiting_input_is_not_eligible(self):
        s = session("s1")
        result = scheduler.classify_agent(
            s,
            {"items": [beacon("s1", workload_state="WAITING_FOR_INPUT", blocker_code="WAITING_FOR_INPUT")]},
            {"claims": []},
            {"items": []},
        )
        self.assertEqual(result["scheduler_state"], "WAITING")
        self.assertFalse(result["eligible_for_new_work"])

    def test_active_claim_makes_agent_active(self):
        s = session("s1")
        claims = {"claims": [{"claim_id": "c1", "session_id": "s1", "status": "ACTIVE", "work_item_id": "T1"}]}
        result = scheduler.classify_agent(s, {"items": []}, claims, {"items": []})
        self.assertEqual(result["scheduler_state"], "ACTIVE")
        self.assertFalse(result["eligible_for_new_work"])

    def test_alive_without_explicit_idle_is_not_auto_eligible(self):
        s = session("s1")
        result = scheduler.classify_agent(s, {"items": []}, {"claims": []}, {"items": []})
        self.assertEqual(result["scheduler_state"], "UNCONFIRMED_AVAILABLE")
        self.assertFalse(result["eligible_for_new_work"])

    def test_idle_challenge_is_explicit_availability(self):
        s = session("s1")
        dispatch = {
            "target_session_id": "s1",
            "dispatch_id": "d1",
            "response": {"challenge_status": "IDLE", "observed_at": "2026-10-07T01:02:00+00:00"},
        }
        result = scheduler.classify_agent(s, {"items": []}, {"claims": []}, {"items": [dispatch]})
        self.assertEqual(result["scheduler_state"], "AVAILABLE")
        self.assertTrue(result["eligible_for_new_work"])
        self.assertEqual(result["availability_provenance"], "EXPLICIT_CHALLENGE_RESPONSE")

    def test_stalled_agent_is_not_eligible(self):
        s = session("s1", status="STALLED", relay_state="TAKEOVER_READY")
        result = scheduler.classify_agent(
            s,
            {"items": [beacon("s1", workload_state="IDLE")]},
            {"claims": []},
            {"items": []},
        )
        self.assertEqual(result["scheduler_state"], "STALLED")
        self.assertFalse(result["eligible_for_new_work"])


class DispatchPlanTests(unittest.TestCase):
    def stores(self, sessions, tasks, beacons=None, claims=None, dispatches=None):
        return {
            "sessions": {"sessions": sessions},
            "task_store": {"items": tasks},
            "beacons": {"items": beacons or []},
            "claims": {"claims": claims or []},
            "dispatches": {"items": dispatches or []},
        }

    def plan(self, stores, *, explicit=None, auto=True):
        return scheduler.plan_dispatch(
            sessions=stores["sessions"],
            beacons=stores["beacons"],
            claims=stores["claims"],
            dispatches=stores["dispatches"],
            task_store=stores["task_store"],
            explicit_task_ids=explicit,
            auto=auto,
        )

    def test_auto_mode_requires_dispatch_policy_enabled(self):
        stores = self.stores(
            [session("s1")],
            [{"id": "T1", "status": "PLANNED", "depends_on": []}],
            [beacon("s1", workload_state="IDLE")],
        )
        plan = self.plan(stores)
        self.assertEqual(plan["assignments"], [])

    def test_explicit_task_can_be_planned_without_auto_flag(self):
        stores = self.stores(
            [session("s1")],
            [{"id": "T1", "status": "PLANNED", "depends_on": []}],
            [beacon("s1", workload_state="IDLE")],
        )
        plan = self.plan(stores, explicit=["T1"], auto=False)
        self.assertEqual(len(plan["assignments"]), 1)
        self.assertEqual(plan["assignments"][0]["task_id"], "T1")
        self.assertFalse(plan["assignments"][0]["grants_mutation_authority"])

    def test_unresolved_dependency_blocks_dispatch(self):
        stores = self.stores(
            [session("s1")],
            [
                {"id": "T0", "status": "PLANNED", "depends_on": []},
                {"id": "T1", "status": "PLANNED", "depends_on": ["T0"], "dispatch_policy": {"enabled": True}},
            ],
            [beacon("s1", workload_state="IDLE")],
        )
        plan = self.plan(stores)
        self.assertEqual(plan["assignments"], [])
        ev = next(x for x in plan["task_evaluations"] if x["task_id"] == "T1")
        self.assertIn("UNRESOLVED_DEPENDENCIES", ev["reasons"])

    def test_active_collision_domain_blocks_dispatch(self):
        stores = self.stores(
            [session("s1")],
            [{
                "id": "T1",
                "status": "PLANNED",
                "depends_on": [],
                "dispatch_policy": {"enabled": True, "collision_domains": ["domain-A"]},
            }],
            [beacon("s1", workload_state="IDLE")],
            claims=[{
                "claim_id": "c1", "session_id": "other", "status": "ACTIVE",
                "work_item_id": "OTHER", "collision_domains": ["domain-A"],
            }],
        )
        plan = self.plan(stores)
        self.assertEqual(plan["assignments"], [])
        ev = plan["task_evaluations"][0]
        self.assertIn("ACTIVE_COLLISION_DOMAIN", ev["reasons"])

    def test_two_non_colliding_tasks_can_dispatch_to_two_agents(self):
        stores = self.stores(
            [session("s1"), session("s2")],
            [
                {
                    "id": "T1", "status": "PLANNED", "depends_on": [],
                    "dispatch_policy": {"enabled": True, "collision_domains": ["domain-A"]},
                },
                {
                    "id": "T2", "status": "PLANNED", "depends_on": [],
                    "dispatch_policy": {"enabled": True, "collision_domains": ["domain-B"]},
                },
            ],
            [
                beacon("s1", workload_state="IDLE"),
                beacon("s2", workload_state="WAITING_FOR_WORK"),
            ],
        )
        plan = self.plan(stores)
        self.assertEqual(len(plan["assignments"]), 2)
        self.assertEqual({x["target_session_id"] for x in plan["assignments"]}, {"s1", "s2"})

    def test_same_collision_domain_serializes_planned_assignments(self):
        stores = self.stores(
            [session("s1"), session("s2")],
            [
                {
                    "id": "T1", "status": "PLANNED", "depends_on": [],
                    "dispatch_policy": {"enabled": True, "collision_domains": ["same"]},
                },
                {
                    "id": "T2", "status": "PLANNED", "depends_on": [],
                    "dispatch_policy": {"enabled": True, "collision_domains": ["same"]},
                },
            ],
            [beacon("s1", workload_state="IDLE"), beacon("s2", workload_state="IDLE")],
        )
        plan = self.plan(stores)
        self.assertEqual(len(plan["assignments"]), 1)
        blocked = [x for x in plan["task_evaluations"] if not x["ready"]]
        self.assertEqual(len(blocked), 1)
        self.assertIn("PLANNED_COLLISION_DOMAIN", blocked[0]["reasons"])

    def test_required_capability_filters_agents(self):
        stores = self.stores(
            [session("s1", capabilities=["CODE_AGENT"]), session("s2", capabilities=["CODE_AGENT", "SQL"])],
            [{
                "id": "T1", "status": "PLANNED", "depends_on": [],
                "dispatch_policy": {"enabled": True, "required_capabilities": ["SQL"]},
            }],
            [beacon("s1", workload_state="IDLE"), beacon("s2", workload_state="IDLE")],
        )
        stores["beacons"]["items"][1]["capabilities"] = ["CODE_AGENT", "SQL"]
        plan = self.plan(stores)
        self.assertEqual(plan["assignments"][0]["target_session_id"], "s2")

    def test_open_dispatch_prevents_duplicate_offer(self):
        stores = self.stores(
            [session("s1")],
            [{
                "id": "T1", "status": "PLANNED", "depends_on": [],
                "dispatch_policy": {"enabled": True},
            }],
            [beacon("s1", workload_state="IDLE")],
            dispatches=[{
                "schema": "gacr-work-dispatch/v1",
                "status": "OFFERED",
                "task_id": "T1",
                "target_session_id": "s1",
            }],
        )
        plan = self.plan(stores)
        self.assertEqual(plan["assignments"], [])
        self.assertIn("OPEN_DISPATCH_EXISTS", plan["task_evaluations"][0]["reasons"])


class BridgeContractTests(unittest.TestCase):
    def test_repository_dispatch_heartbeat_preserves_workload_fields(self):
        root = scheduler.ROOT
        bridge = (root / "scripts" / "gacr_workflow_bridge.py").read_text(encoding="utf-8")
        relay = (root / "scripts" / "governed_agent_continuity_relay.py").read_text(encoding="utf-8")
        for field in (
            "workload_state", "blocker_code", "capacity_slots",
            "max_parallel_tasks", "retry_after_at",
        ):
            self.assertIn(f"payload.get('{field}')", bridge)
        for flag in (
            "--workload-state", "--blocker-code", "--capacity-slots",
            "--max-parallel-tasks", "--retry-after-at",
        ):
            self.assertIn(flag, relay)
        self.assertIn("workload_state=a.workload_state", relay)
        self.assertIn("capacity_slots=a.capacity_slots", relay)
        self.assertIn("retry_after_at=a.retry_after_at", relay)

    def test_relay_workflow_runs_safe_auto_dispatch(self):
        workflow = (scheduler.ROOT / ".github" / "workflows" / "governed-agent-continuity-relay.yml").read_text(encoding="utf-8")
        self.assertIn("gacr_parallel_dispatch.py dispatch --auto --persist-roster", workflow)
        self.assertIn("gacr-agent-roster.json", workflow)
        self.assertIn("agent-relay/roster.json", workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
