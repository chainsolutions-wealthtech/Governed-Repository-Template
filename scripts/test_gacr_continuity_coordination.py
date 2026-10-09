#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gacr_continuity_coordination as c
import gacr_host_issue_ingress as host


def assert_true(value, message: str) -> None:
    if not value:
        raise AssertionError(message)


def expect_error(fn, contains: str) -> None:
    try:
        fn()
    except Exception as exc:
        assert_true(contains in str(exc), f"expected {contains!r} in {exc!r}")
        return
    raise AssertionError(f"expected error containing {contains!r}")


def active_session(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "status": "ACTIVE",
        "relay": {"state": "ACTIVE"},
    }


def stalled_session(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "status": "STALLED",
        "relay": {"state": "TAKEOVER_READY"},
    }


def host_config() -> dict:
    return {
        "host_issue_bridge": {
            "enabled": True,
            "issue_number": 115,
            "allowed_author_associations": ["OWNER", "MEMBER", "COLLABORATOR"],
            "max_payload_chars": 8192,
        }
    }


def issue_event(payload: dict, comment_id: int = 9901) -> dict:
    return {
        "action": "created",
        "issue": {"number": 115, "title": "[GACR Host Bridge] Provider event ingress"},
        "comment": {
            "id": comment_id,
            "body": host.PREFIX + json.dumps(payload, separators=(",", ":")),
            "author_association": "MEMBER",
            "user": {"login": "agent-user"},
        },
        "sender": {"login": "agent-user"},
        "repository": {"full_name": "example/governed"},
    }


def main() -> None:
    head = "a" * 40

    def receipt(value: dict, continuity_id: str) -> str:
        return c.coordination_state_ref(value, continuity_id)
    sessions = {
        "sessions": [
            active_session("session-a"),
            active_session("session-b"),
            stalled_session("session-old"),
        ]
    }
    claims = {"claims": []}
    original_sessions = copy.deepcopy(sessions)
    original_claims = copy.deepcopy(claims)
    state = c.default_state()

    alias_state = c.default_state()
    alias_state["items"] = [{
        "continuity_id": "GRT-CONT-ALIAS-01",
        "repository": "example/governed",
        "coordination_issue": 259,
        "projection_only": True,
        "participants": [],
        "logical_agents": [
            {
                "logical_agent_id": "logical-forge",
                "logical_agent_id_provenance": "CANONICAL_GACR_SESSION_AGENT_IDENTITY",
                "human_alias": "FORGE",
                "human_alias_provenance": "OWNER_ASSIGNED",
                "alias_evidence_ref": "github-issue-comment:owner-forge",
                "routing_evidence_ref": "github-issue-comment:owner-routing",
                "reference_session_ids": ["session-forge-old"],
                "session_ids": ["session-forge-old"],
                "provider_contexts": [],
                "projection_only": True,
                "grants_task_authority": False,
                "grants_claim": False,
                "grants_mutation_authority": False,
            }
        ],
    }]
    alias_sessions = {
        "sessions": [
            {
                "session_id": "session-forge-old",
                "agent_identity": "logical-forge",
                "status": "STALLED",
                "provider": "chatgpt",
                "provider_conversation_ref": None,
                "connection_ref": "conn-forge-old",
                "client_instance_id": "client-forge-old",
                "provider_contexts": [{
                    "provider_context_id": "GACR-PC-aaaaaaaaaaaaaaaa",
                    "provider": "chatgpt",
                    "connection_ref": "conn-forge-old",
                    "provider_native_identity_status": "UNAVAILABLE",
                    "provider_private_values_invented": False,
                }],
                "relay": {"state": "TAKEOVER_READY"},
            },
            {
                "session_id": "session-forge-new",
                "agent_identity": "logical-forge",
                "status": "ACTIVE",
                "provider": "chatgpt",
                "provider_conversation_ref": None,
                "connection_ref": "conn-forge-new",
                "client_instance_id": "client-forge-new",
                "provider_contexts": [],
                "relay": {"state": "ACTIVE"},
            },
        ]
    }
    resolved_alias = c.resolve_logical_agent_alias_docs(
        alias_state,
        alias_sessions,
        alias="forge",
    )
    assert_true(resolved_alias["logical_agent_id"] == "logical-forge", "owner alias resolves canonical logical agent")
    assert_true(resolved_alias["human_alias"] == "FORGE", "alias normalization is stable")
    assert_true(
        [item["session_id"] for item in resolved_alias["sessions"]]
        == ["session-forge-new", "session-forge-old"],
        "cold-start alias resolution reconstructs all canonical sessions",
    )
    assert_true(resolved_alias["provider_context_count"] == 1, "provider context history follows the logical agent")
    assert_true(resolved_alias["routing_status"] == "ROUTABLE_EXACT_SESSION", "one active canonical session is alias-routable")
    assert_true(resolved_alias["resolved_target_session_id"] == "session-forge-new", "alias resolves exact active session")
    assert_true(resolved_alias["grants_mutation_authority"] is False, "alias resolution grants no authority")
    expect_error(
        lambda: c.resolve_logical_agent_alias_docs(alias_state, alias_sessions, alias="UNKNOWN"),
        "LOGICAL_AGENT_ALIAS_UNKNOWN",
    )
    ambiguous_alias_state = copy.deepcopy(alias_state)
    ambiguous_alias_state["items"][0]["logical_agents"].append({
        "logical_agent_id": "logical-other",
        "human_alias": "FORGE",
        "human_alias_provenance": "OWNER_ASSIGNED",
        "reference_session_ids": ["session-other"],
        "session_ids": ["session-other"],
        "provider_contexts": [],
        "projection_only": True,
        "grants_task_authority": False,
        "grants_claim": False,
        "grants_mutation_authority": False,
    })
    expect_error(
        lambda: c.resolve_logical_agent_alias_docs(ambiguous_alias_state, alias_sessions, alias="FORGE"),
        "LOGICAL_AGENT_ALIAS_AMBIGUOUS",
    )
    multiple_active_sessions = copy.deepcopy(alias_sessions)
    multiple_active_sessions["sessions"][0]["status"] = "ACTIVE"
    multiple_active_sessions["sessions"][0]["relay"]["state"] = "ACTIVE"
    ambiguous_route = c.resolve_logical_agent_alias_docs(alias_state,multiple_active_sessions,alias="FORGE")
    assert_true(ambiguous_route["routing_status"] == "AMBIGUOUS_ACTIVE_SESSIONS", "multiple active sibling sessions fail closed")
    assert_true(ambiguous_route["resolved_target_session_id"] is None, "ambiguous alias selects no session")

    first = c.declare_scope_docs(
        state, sessions, claims,
        repository="example/governed",
        continuity_id="GRT-CONT-DEMO-01",
        coordination_issue=259,
        coordination_state_ref=receipt(state, "GRT-CONT-DEMO-01"),
        session_id="session-a",
        declared_role="CODE_AGENT",
        scope_id="gmc-g01",
        work_mode="READ_ONLY",
        collision_domains=["gmc:g01:analysis"],
        observed_head=head,
        current_head=head,
        evidence_ref="github-issue-comment:101",
        timestamp="2026-10-07T20:00:00+00:00",
    )
    assert_true(first["status"] == "CONTINUITY_SCOPE_DECLARED", "first scope declared")
    assert_true(first["grants_mutation_authority"] is False, "scope grants no mutation authority")
    assert_true(first["participant"]["membership_state"] == "PERSISTENT", "continuity membership is durable")
    assert_true(first["accepted_coordination_state_ref"].startswith("GACR-CS-"), "current-state receipt accepted")
    assert_true(first["next_coordination_state_ref"] == receipt(state, "GRT-CONT-DEMO-01"), "next state receipt exposed")

    stale_receipt = first["accepted_coordination_state_ref"]
    expect_error(
        lambda: c.declare_scope_docs(
            state, sessions, claims,
            repository="example/governed",
            continuity_id="GRT-CONT-DEMO-01",
            coordination_issue=259,
            coordination_state_ref=stale_receipt,
            session_id="session-b",
            declared_role="CODE_AGENT",
            scope_id="dispatcher-stale-receipt",
            work_mode="READ_ONLY",
            collision_domains=["orchestration:258:stale-receipt"],
            observed_head=head,
            current_head=head,
            evidence_ref="github-issue-comment:101-stale",
            timestamp="2026-10-07T20:00:30+00:00",
        ),
        "STALE_COORDINATION_STATE_REF",
    )
    unrelated_ref = receipt(state, "GRT-CONT-OTHER-01")
    expect_error(
        lambda: c.declare_scope_docs(
            state, sessions, claims,
            repository="example/governed",
            continuity_id="GRT-CONT-DEMO-01",
            coordination_issue=259,
            coordination_state_ref=unrelated_ref,
            session_id="session-b",
            declared_role="CODE_AGENT",
            scope_id="dispatcher-unrelated-receipt",
            work_mode="READ_ONLY",
            collision_domains=["orchestration:258:unrelated-receipt"],
            observed_head=head,
            current_head=head,
            evidence_ref="github-issue-comment:101-unrelated",
            timestamp="2026-10-07T20:00:40+00:00",
        ),
        "STALE_COORDINATION_STATE_REF",
    )

    second = c.declare_scope_docs(
        state, sessions, claims,
        repository="example/governed",
        continuity_id="GRT-CONT-DEMO-01",
        coordination_issue=259,
        coordination_state_ref=receipt(state, "GRT-CONT-DEMO-01"),
        session_id="session-b",
        declared_role="CODE_AGENT",
        scope_id="dispatcher-258",
        work_mode="READ_ONLY",
        collision_domains=["orchestration:258:planning"],
        observed_head=head,
        current_head=head,
        evidence_ref="github-issue-comment:102",
        timestamp="2026-10-07T20:01:00+00:00",
    )
    assert_true(second["status"] == "CONTINUITY_SCOPE_DECLARED", "disjoint read-only parallel scope accepted")

    expect_error(
        lambda: c.declare_scope_docs(
            state, sessions, claims,
            repository="example/governed",
            continuity_id="GRT-CONT-DEMO-01",
            coordination_issue=259,
            coordination_state_ref=receipt(state, "GRT-CONT-DEMO-01"),
            session_id="session-b",
            declared_role="CODE_AGENT",
            scope_id="gmc-g01",
            work_mode="READ_ONLY",
            collision_domains=["gmc:g01:analysis"],
            observed_head=head,
            current_head=head,
            evidence_ref="github-issue-comment:103",
            timestamp="2026-10-07T20:02:00+00:00",
        ),
        "CONTINUITY_SCOPE_COLLISION",
    )

    write_state = c.default_state()
    c.declare_scope_docs(
        write_state, sessions, claims,
        repository="example/governed",
        continuity_id="GRT-CONT-WRITE-01",
        coordination_issue=259,
        coordination_state_ref=receipt(write_state, "GRT-CONT-WRITE-01"),
        session_id="session-a",
        declared_role="CODE_AGENT",
        scope_id="writer-a",
        work_mode="WRITE",
        collision_domains=["coordination:state"],
        observed_head=head,
        current_head=head,
        evidence_ref="github-issue-comment:201",
        timestamp="2026-10-07T20:03:00+00:00",
    )
    expect_error(
        lambda: c.declare_scope_docs(
            write_state, sessions, claims,
            repository="example/governed",
            continuity_id="GRT-CONT-WRITE-01",
            coordination_issue=259,
            coordination_state_ref=receipt(write_state, "GRT-CONT-WRITE-01"),
            session_id="session-b",
            declared_role="CODE_AGENT",
            scope_id="writer-b",
            work_mode="WRITE",
            collision_domains=["coordination:state"],
            observed_head=head,
            current_head=head,
            evidence_ref="github-issue-comment:202",
            timestamp="2026-10-07T20:04:00+00:00",
        ),
        "CONTINUITY_WRITER_COLLISION",
    )

    claimed = {
        "claims": [{
            "claim_id": "CLAIM-A",
            "session_id": "session-a",
            "status": "ACTIVE",
            "work_item_id": "WORK-A",
            "collision_domains": ["canonical:domain"],
        }]
    }
    claimed_state = c.default_state()
    expect_error(
        lambda: c.declare_scope_docs(
            claimed_state, sessions, claimed,
            repository="example/governed",
            continuity_id="GRT-CONT-CLAIM-01",
            coordination_issue=259,
            coordination_state_ref=receipt(claimed_state, "GRT-CONT-CLAIM-01"),
            session_id="session-b",
            declared_role="CODE_AGENT",
            scope_id="writer-b",
            work_mode="WRITE",
            collision_domains=["canonical:domain"],
            observed_head=head,
            current_head=head,
            evidence_ref="github-issue-comment:301",
            timestamp="2026-10-07T20:05:00+00:00",
        ),
        "FOREIGN_CANONICAL_CLAIM_COLLISION",
    )

    stale_state = c.default_state()
    expect_error(
        lambda: c.declare_scope_docs(
            stale_state, sessions, claims,
            repository="example/governed",
            continuity_id="GRT-CONT-STALE-01",
            coordination_issue=259,
            coordination_state_ref=receipt(stale_state, "GRT-CONT-STALE-01"),
            session_id="session-a",
            declared_role="CODE_AGENT",
            scope_id="stale",
            work_mode="READ_ONLY",
            collision_domains=["stale:test"],
            observed_head="b" * 40,
            current_head=head,
            evidence_ref="github-issue-comment:401",
            timestamp="2026-10-07T20:06:00+00:00",
        ),
        "HEAD_MOVED",
    )

    return_state = c.default_state()
    expect_error(
        lambda: c.declare_scope_docs(
            return_state, sessions, claims,
            repository="example/governed",
            continuity_id="GRT-CONT-RETURN-01",
            coordination_issue=259,
            coordination_state_ref=receipt(return_state, "GRT-CONT-RETURN-01"),
            session_id="session-old",
            declared_role="CODE_AGENT",
            scope_id="resume",
            work_mode="READ_ONLY",
            collision_domains=["resume:test"],
            observed_head=head,
            current_head=head,
            evidence_ref="github-issue-comment:501",
            timestamp="2026-10-07T20:07:00+00:00",
        ),
        "session must be ACTIVE",
    )

    yielded = c.yield_scope_docs(
        state, sessions,
        continuity_id="GRT-CONT-DEMO-01",
        session_id="session-a",
        scope_id="gmc-g01",
        observed_head=head,
        current_head=head,
        handoff_ref="github-issue-comment:600",
        evidence_ref="github-issue-comment:601",
        timestamp="2026-10-07T20:08:00+00:00",
    )
    assert_true(yielded["claims_changed"] is False, "yield never changes claims")
    assert_true(yielded["authority_transferred"] is False, "yield never transfers canonical authority")
    yielded_participant = next(p for p in state["items"][0]["participants"] if p["session_id"] == "session-a" and p["scope_id"] == "gmc-g01")
    assert_true(yielded_participant["membership_state"] == "PERSISTENT", "yield preserves durable membership identity")

    replacement = c.declare_scope_docs(
        state, sessions, claims,
        repository="example/governed",
        continuity_id="GRT-CONT-DEMO-01",
        coordination_issue=259,
        coordination_state_ref=receipt(state, "GRT-CONT-DEMO-01"),
        session_id="session-b",
        declared_role="CODE_AGENT",
        scope_id="gmc-g01",
        work_mode="READ_ONLY",
        collision_domains=["gmc:g01:analysis"],
        observed_head=head,
        current_head=head,
        evidence_ref="github-issue-comment:602",
        timestamp="2026-10-07T20:09:00+00:00",
    )
    assert_true(replacement["status"] == "CONTINUITY_SCOPE_DECLARED", "scope reusable after governed yield")

    assert_true(sessions == original_sessions, "coordination projection must not mutate canonical sessions")
    assert_true(claims == original_claims, "coordination projection must not mutate canonical claims")
    assert_true(state["projection_only"] is True, "state explicitly projection-only")
    assert_true(state["grants_task_authority"] is False, "state grants no task authority")

    host_payload = {
        "schema": host.SCHEMA,
        "event": "continuity_scope",
        "session_id": "session-a",
        "continuity_id": "GRT-CONT-DEMO-01",
        "coordination_issue": 259,
        "coordination_state_ref": "github-issue-comment:700",
        "scope_id": "gmc-g01",
        "work_mode": "READ_ONLY",
        "collision_domains": ["gmc:g01:analysis"],
        "observed_head": head,
    }
    parsed = host.parse_issue_comment_event(issue_event(host_payload), host_config())
    assert_true(parsed and parsed["continuity_id"] == "GRT-CONT-DEMO-01", "host parses continuity scope")

    missing_receipt = dict(host_payload)
    missing_receipt.pop("coordination_state_ref")
    expect_error(
        lambda: host.parse_issue_comment_event(issue_event(missing_receipt, comment_id=9902), host_config()),
        "coordination_state_ref",
    )

    yield_payload = {
        "schema": host.SCHEMA,
        "event": "continuity_yield",
        "session_id": "session-a",
        "continuity_id": "GRT-CONT-DEMO-01",
        "scope_id": "gmc-g01",
        "handoff_ref": "github-issue-comment:701",
        "observed_head": head,
    }
    parsed_yield = host.parse_issue_comment_event(issue_event(yield_payload, comment_id=9903), host_config())
    assert_true(parsed_yield and parsed_yield["handoff_ref"] == "github-issue-comment:701", "host parses continuity yield")

    print("GACR_CONTINUITY_COORDINATION_TESTS_PASS")


if __name__ == "__main__":
    main()
