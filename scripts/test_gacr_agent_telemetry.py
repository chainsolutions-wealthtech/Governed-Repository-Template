#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "gacr_agent_telemetry.py"
NOTIFIER_PATH = ROOT / "scripts" / "gacr_bridge_notifier.py"


def load_module():
    spec = importlib.util.spec_from_file_location("gacr_agent_telemetry", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise SystemExit("GACR_TELEMETRY_TEST_FAILED: unable to load module")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod



def load_notifier():
    spec = importlib.util.spec_from_file_location("gacr_bridge_notifier", NOTIFIER_PATH)
    if spec is None or spec.loader is None:
        raise SystemExit("GACR_TELEMETRY_TEST_FAILED: unable to load notifier")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write(path: Path, value: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def assert_true(value, message):
    if not value:
        raise SystemExit("GACR_TELEMETRY_TEST_FAILED: " + message)


def main():
    g = load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        g.ROOT = root
        g.GOV = root / ".governance"
        g.SESSIONS_PATH = g.GOV / "sessions" / "sessions.json"
        g.CLAIMS_PATH = g.GOV / "work" / "claims.json"
        g.TAKEOVERS_PATH = g.GOV / "agent-relay" / "takeovers.json"
        g.BEACONS_PATH = g.GOV / "agent-relay" / "beacons.json"
        g.CORRELATIONS_PATH = g.GOV / "agent-relay" / "correlations.json"
        g.DISPATCHES_PATH = g.GOV / "agent-relay" / "dispatches.json"
        g.FORENSICS_PATH = g.GOV / "agent-relay" / "forensics.json"

        session_a = {
            "session_id": "session-a",
            "agent_identity": "ChatGPT-A",
            "provider": "chatgpt",
            "provider_conversation_ref": "conv-a",
            "client_instance_id": "client-a",
            "connection_ref": "conn-a",
            "repository": "owner/repo",
            "status": "ACTIVE",
            "created_at": "2026-10-01T20:00:00+00:00",
            "last_observed_head_sha": "a" * 40,
            "github_actor": "actor-a",
            "relay": {
                "process": "GACR",
                "state": "ACTIVE",
                "task_id": "TASK-1",
                "branch": "feature/a",
                "pull_request": 12,
                "last_heartbeat_at": "2026-10-01T20:00:00+00:00",
                "lease_expires_at": "2026-10-01T20:30:00+00:00",
            },
        }
        session_b = {
            "session_id": "session-b",
            "agent_identity": "ChatGPT-B",
            "provider": "chatgpt",
            "provider_conversation_ref": "conv-b",
            "client_instance_id": "client-b",
            "repository": "owner/repo",
            "status": "STANDBY",
            "created_at": "2026-10-01T20:01:00+00:00",
            "last_observed_head_sha": "a" * 40,
            "wake_channels": ["POLL_REPOSITORY", "REPOSITORY_DISPATCH", "EXTERNAL_BRIDGE"],
            "bridge_registration_ref": "bridge-b",
            "relay": {
                "process": "GACR",
                "state": "STANDBY",
                "task_id": None,
                "branch": "main",
                "pull_request": None,
                "last_heartbeat_at": "2026-10-01T20:01:00+00:00",
                "lease_expires_at": "2026-10-01T20:31:00+00:00",
            },
        }
        write(g.SESSIONS_PATH, {"schema_version":"1.0.0","revision":2,"sessions":[session_a,session_b]})
        write(g.CLAIMS_PATH, {"schema_version":"1.0.0","revision":1,"claims":[{
            "session_id":"session-a","work_item_id":"WORK-1","status":"ACTIVE",
            "collision_domains":["domain-a"],"claimed_head_sha":"a"*40
        }]})
        write(g.TAKEOVERS_PATH, {"schema_version":"1.0.0","revision":1,"last_scan_at":None,"items":[{
            "takeover_id":"GACR-T-123456789abc",
            "stalled_session_id":"session-a",
            "offered_to_session_id":"session-b",
            "accepted_by_session_id":None,
            "status":"OFFERED",
            "created_at":"2026-10-01T20:40:00+00:00",
            "task_id":"TASK-1",
            "branch":"feature/a",
            "pull_request":12,
            "last_observed_head_sha":"a"*40
        }]})
        for path in [g.BEACONS_PATH,g.CORRELATIONS_PATH,g.DISPATCHES_PATH,g.FORENSICS_PATH]:
            write(path, {"schema_version":"1.0.0","revision":0,"items":[]})

        os.environ["GITHUB_REPOSITORY"] = "owner/repo"
        os.environ["GITHUB_ACTOR"] = "actor-a"
        os.environ["GITHUB_SHA"] = "a" * 40
        os.environ["GITHUB_REF_NAME"] = "feature/a"

        beacon = g.record_beacon(
            session=session_a,
            event_type="REGISTER",
            provider_url="https://chatgpt.com/c/conv-a",
        )
        assert_true(beacon["beacon_id"].startswith("GACR-B-"), "beacon id")
        assert_true(beacon["provider_conversation_ref"] == "conv-a", "provider ref preserved")
        assert_true("provider_url" not in beacon, "full provider URL must not persist in beacon")
        assert_true(beacon["github"]["environment"]["GITHUB_ACTOR"] == "actor-a", "safe GitHub actor captured")

        result = g.correlate_all()
        assert_true(result["changed"] == 1, "first correlation should be written")
        correlations = json.loads(g.CORRELATIONS_PATH.read_text(encoding="utf-8"))["items"]
        assert_true(correlations[0]["level"] == "EXACT", "explicit session beacon should correlate EXACT")
        assert_true(correlations[0]["selected_session_id"] == "session-a", "exact session selected")

        # A canonical session may preserve multiple provider/runtime contexts.
        # An exact beacon from a secondary stored context must still correlate
        # to that session rather than becoming a false explicit-anchor conflict.
        sessions_doc = json.loads(g.SESSIONS_PATH.read_text(encoding="utf-8"))
        stored_a = next(x for x in sessions_doc["sessions"] if x["session_id"] == "session-a")
        stored_a["provider_contexts"] = [
            {
                "provider_context_id": "GACR-PC-aaaaaaaaaaaaaaaa",
                "provider": "chatgpt",
                "provider_conversation_ref": "conv-a",
                "client_instance_id": "client-a",
                "connection_ref": "conn-a",
                "provider_private_values_invented": False,
            },
            {
                "provider_context_id": "GACR-PC-bbbbbbbbbbbbbbbb",
                "provider": "chatgpt",
                "provider_conversation_ref": "conv-a",
                "client_instance_id": "client-a-secondary",
                "connection_ref": "conn-a-secondary",
                "provider_private_values_invented": False,
            },
        ]
        write(g.SESSIONS_PATH, sessions_doc)
        secondary = g.record_beacon(
            session=stored_a,
            event_type="AUTO_ATTACH",
            provider="chatgpt",
            provider_ref="conv-a",
            client_instance_id="client-a-secondary",
            connection_ref="conn-a-secondary",
        )
        g.correlate_all()
        secondary_corr = next(
            x for x in json.loads(g.CORRELATIONS_PATH.read_text(encoding="utf-8"))["items"]
            if x["beacon_id"] == secondary["beacon_id"]
        )
        assert_true(secondary_corr["level"] == "EXACT", "secondary provider context remains exact")
        assert_true(secondary_corr["selected_session_id"] == "session-a", "secondary context selects canonical session")

        # The same historical runtime/provider anchor on two distinct canonical
        # sessions is ambiguous and must fail closed rather than select either.
        collision_sessions = json.loads(g.SESSIONS_PATH.read_text(encoding="utf-8"))
        collision_a = next(x for x in collision_sessions["sessions"] if x["session_id"] == "session-a")
        collision_b = next(x for x in collision_sessions["sessions"] if x["session_id"] == "session-b")
        shared_context = {
            "provider": "chatgpt",
            "provider_conversation_ref": None,
            "client_instance_id": "collision-client",
            "connection_ref": "collision-connection",
            "provider_private_values_invented": False,
        }
        collision_a.setdefault("provider_contexts", []).append({
            **shared_context,
            "provider_context_id": "GACR-PC-cccccccccccccccc",
        })
        collision_b.setdefault("provider_contexts", []).append({
            **shared_context,
            "provider_context_id": "GACR-PC-dddddddddddddddd",
        })
        write(g.SESSIONS_PATH, collision_sessions)
        collision_beacon = g.record_beacon(
            session=None,
            event_type="OBSERVED_GITHUB_ACTIVITY",
            provider="chatgpt",
            client_instance_id="collision-client",
            connection_ref="collision-connection",
            source="GITHUB_ACTIONS",
        )
        g.correlate_all()
        collision_corr = next(
            x for x in json.loads(g.CORRELATIONS_PATH.read_text(encoding="utf-8"))["items"]
            if x["beacon_id"] == collision_beacon["beacon_id"]
        )
        assert_true(collision_corr["level"] == "AMBIGUOUS", "cross-session historical context collision must be ambiguous")
        assert_true(collision_corr["selected_session_id"] is None, "ambiguous historical context must select no session")
        assert_true(
            set(collision_corr["candidate_session_ids"]) == {"session-a", "session-b"},
            "both conflicting canonical sessions must remain visible as candidates",
        )

        anonymous = g.record_beacon(
            session=None,
            event_type="OBSERVED_GITHUB_ACTIVITY",
            provider="chatgpt",
            task_id="TASK-1",
            branch="feature/a",
            pull_request=12,
            source="GITHUB_ACTIONS",
        )
        result = g.correlate_all()
        anon_corr = next(x for x in json.loads(g.CORRELATIONS_PATH.read_text(encoding="utf-8"))["items"] if x["beacon_id"] == anonymous["beacon_id"])
        assert_true(anon_corr["level"] == "STRONG", "branch+PR+task evidence should correlate STRONG")
        assert_true(anon_corr["selected_session_id"] == "session-a", "strong correlation selects unique candidate")

        dispatch = g.dispatch_open_takeovers()
        assert_true(dispatch["changed"] == 1, "takeover should produce one dispatch")
        item = dispatch["items"][0]
        assert_true(item["target_session_id"] == "session-b", "standby target")
        assert_true(set(item["delivery_modes"]) == {"POLL_REPOSITORY","REPOSITORY_DISPATCH","EXTERNAL_BRIDGE"}, "all declared delivery modes")
        assert_true(item["may_write_before_takeover_accept"] is False, "dispatch must not grant write")

        recovery_b = g.session_recovery_packet("session-b", generated_at="2026-10-01T20:10:00+00:00")
        assert_true(recovery_b["schema"] == "gacr-session-recovery-packet/v1", "recovery packet schema")
        assert_true(recovery_b["addressability"]["provider"] == "chatgpt", "provider recovered")
        assert_true(recovery_b["addressability"]["provider_conversation_ref"] == "conv-b", "provider conversation ref recovered")
        assert_true(recovery_b["addressability"]["bridge_registration_ref"] == "bridge-b", "bridge ref recovered")
        assert_true(
            set(recovery_b["addressability"]["transport_candidates"]) == {"POLL_REPOSITORY", "REPOSITORY_DISPATCH", "EXTERNAL_BRIDGE"},
            "recovery packet preserves observable transports",
        )
        assert_true(recovery_b["addressability"]["targetable_via_observed_transport"] is True, "session addressable through observed transport")
        assert_true(recovery_b["addressability"]["freeform_message_delivery"]["status"] == "NOT_VERIFIED", "wake transport must not be mistaken for prompt transport")
        assert_true(recovery_b["next_gate"]["may_send_freeform_message_without_verified_transport"] is False, "prompt delivery fails closed")
        assert_true(recovery_b["addressability"]["grants_mutation_authority"] is False, "recovery packet grants no mutation authority")

        notifier = load_notifier()
        bridge_payload = notifier.build_payload("owner/repo", item)
        assert_true(bridge_payload["dispatch_id"] == item["dispatch_id"], "bridge dispatch id")
        assert_true(bridge_payload["delivery"]["idempotency_key"] == item["dispatch_id"], "bridge idempotency key")
        assert_true(bridge_payload["delivery"]["may_write"] is False, "bridge wake must not grant write")
        assert_true(notifier.eligible([item]) == [item], "ready external dispatch should be bridge-eligible")

        context = g.agent_context("session-b")
        assert_true(context["session"]["session_id"] == "session-b", "context resolves session")
        assert_true(len(context["dispatches"]) == 1, "context includes dispatch offer")


        g.record_beacon(session=session_a,event_type="ACTION_TRACE",action_id="action-1",action_label="update TASKS",action_phase="STARTED",tool_name="GitHub.update_file",tool_call_id="tool-1",observed_at="2026-10-01T20:10:00+00:00")
        g.record_beacon(session=session_a,event_type="ACTION_TRACE",action_id="action-1",action_label="update TASKS",action_phase="COMPLETED",tool_name="GitHub.update_file",tool_call_id="tool-1",outcome="PASS",written_head_sha="b"*40,checkpoint_ref="CP-CHECKPOINT-20261001-999",evidence_ref="ci:123",observed_at="2026-10-01T20:11:00+00:00")
        g.record_beacon(session=session_a,event_type="ACTION_TRACE",action_id="action-2",action_label="open PR",action_phase="STARTED",tool_name="GitHub.create_pull_request",tool_call_id="tool-2",observed_at="2026-10-01T20:12:00+00:00")
        sessions_doc=json.loads(g.SESSIONS_PATH.read_text(encoding="utf-8"))
        persisted_a=next(x for x in sessions_doc["sessions"] if x["session_id"]=="session-a")
        persisted_a["status"]="STALLED"; persisted_a["relay"]["state"]="TAKEOVER_READY"; persisted_a["relay"]["last_action"]="STALL_DETECTED"
        persisted_a["relay"]["stalled_at"]="2026-10-01T20:40:00+00:00"; persisted_a["relay"]["lease_expires_at"]="2026-10-01T20:30:00+00:00"
        write(g.SESSIONS_PATH,sessions_doc)
        report=g.build_interruption_forensics("session-a",persist=True,generated_at="2026-10-01T20:41:00+00:00")
        assert_true(report["forensic_id"].startswith("GACR-F-"),"forensics id")
        assert_true(report["classification"]=="LEASE_EXPIRED_STALL","forensics classification")
        assert_true(report["cause"]["status"]=="UNOBSERVED","external cause must not be invented")
        assert_true(report["actions"]["last_action_started"]["action_id"]=="action-2","last started")
        assert_true(report["actions"]["last_action_completed"]["action_id"]=="action-1","last completed")
        assert_true(report["actions"]["last_tool_call"]["tool_call_id"]=="tool-2","last tool call")
        assert_true(report["actions"]["in_flight_action"]["action_id"]=="action-2","in-flight action")
        assert_true(report["work"]["last_written_head_sha"]=="b"*40,"last written head")
        assert_true(report["resume_point"]["checkpoint_ref"]=="CP-CHECKPOINT-20261001-999","checkpoint")
        assert_true(report["resume_point"]["requires_exact_head_reobservation"] is True,"exact-head required")
        assert_true(report["resume_point"]["may_replay_in_flight_action_without_reconciliation"] is False,"blind replay forbidden")
        g.record_beacon(session=session_a,event_type="INTERRUPTION_SIGNAL",interruption_code="PROVIDER_TIMEOUT",observed_at="2026-10-01T20:40:30+00:00")
        observed=g.build_interruption_forensics("session-a",persist=True,generated_at="2026-10-01T20:42:00+00:00")
        assert_true(observed["cause"]["status"]=="OBSERVED","explicit interruption observed")
        assert_true(observed["cause"]["code"]=="PROVIDER_TIMEOUT","explicit cause preserved")
        assert_true(len(json.loads(g.FORENSICS_PATH.read_text(encoding="utf-8"))["items"])==1,"one current forensic projection")

        assert_true(
            g.provider_ref_from_url("chatgpt","https://chatgpt.com/c/6abe6ebe-3f98-83ed-b12e-2cf0f5b1e300")
            == "6abe6ebe-3f98-83ed-b12e-2cf0f5b1e300",
            "ChatGPT URL should normalize to conversation ref",
        )

        try:
            g.assert_secretless({"github_token":"should-never-persist"})
            raise SystemExit("GACR_TELEMETRY_TEST_FAILED: forbidden telemetry key accepted")
        except ValueError:
            pass


        terminal = json.loads(json.dumps(session_a))
        terminal["status"] = "CLOSED"
        terminal.setdefault("relay", {})["state"] = "CLOSED"
        score, reasons, exact = g.correlation_score(beacon, terminal)
        assert_true(score < 0 and reasons == [] and exact is False, "terminal session must be excluded from correlation")

        # A connection-scoped issue anchor is more specific than a client instance
        # that legitimately hosts multiple concurrent issue connections.
        shared_client_a = json.loads(json.dumps(session_a))
        shared_client_a["session_id"] = "session-shared-issue-183"
        shared_client_a["provider_conversation_ref"] = None
        shared_client_a["client_instance_id"] = "shared-client"
        shared_client_a["connection_ref"] = "issue:183"
        shared_client_a["relay"]["task_id"] = None
        shared_client_a["relay"]["branch"] = "main"
        shared_client_a["relay"]["pull_request"] = None
        shared_client_b = json.loads(json.dumps(shared_client_a))
        shared_client_b["session_id"] = "session-shared-issue-184"
        shared_client_b["connection_ref"] = "issue:184"
        sessions_doc = json.loads(g.SESSIONS_PATH.read_text(encoding="utf-8"))
        sessions_doc["sessions"].extend([shared_client_a, shared_client_b])
        write(g.SESSIONS_PATH, sessions_doc)

        issue_scoped = g.record_beacon(
            session=None,
            event_type="AUTO_ATTACH",
            provider=None,
            client_instance_id="shared-client",
            connection_ref="issue:184",
            branch="main",
            source="CLIENT_EMITTER",
        )
        g.correlate_all()
        issue_corr = next(
            x for x in json.loads(g.CORRELATIONS_PATH.read_text(encoding="utf-8"))["items"]
            if x["beacon_id"] == issue_scoped["beacon_id"]
        )
        assert_true(
            issue_corr["level"] == "EXACT",
            "issue-scoped connection_ref must outrank a shared client_instance_id",
        )
        assert_true(
            issue_corr["selected_session_id"] == "session-shared-issue-184",
            "issue-scoped connection_ref must select the matching session",
        )
        assert_true(
            "CONNECTION_REF_EXACT" in issue_corr["reasons"],
            "issue-scoped correlation must retain connection-ref evidence",
        )

        # A second indistinguishable session must make heuristic correlation ambiguous.
        session_c = json.loads(json.dumps(session_a))
        session_c["session_id"] = "session-c"
        session_c["provider_conversation_ref"] = "conv-c"
        session_c["client_instance_id"] = "client-c"
        session_c["connection_ref"] = "conn-c"
        session_c["github_actor"] = None
        sessions_doc = json.loads(g.SESSIONS_PATH.read_text(encoding="utf-8"))
        sessions_doc["sessions"].append(session_c)
        write(g.SESSIONS_PATH, sessions_doc)

        os.environ.pop("GITHUB_ACTOR", None)

        ambiguous = g.record_beacon(
            session=None,
            event_type="AMBIGUOUS_ACTIVITY",
            provider=None,
            task_id="TASK-1",
            branch="feature/a",
            pull_request=12,
            source="LOCAL_AGENT",
        )
        g.correlate_all()
        amb_corr = next(x for x in json.loads(g.CORRELATIONS_PATH.read_text(encoding="utf-8"))["items"] if x["beacon_id"] == ambiguous["beacon_id"])
        assert_true(amb_corr["level"] == "AMBIGUOUS", "equal strong candidates must fail closed as AMBIGUOUS")
        assert_true(amb_corr["selected_session_id"] is None, "ambiguous evidence must not auto-bind")

    print("GACR_AGENT_TELEMETRY_TEST_PASS")


if __name__ == "__main__":
    main()
