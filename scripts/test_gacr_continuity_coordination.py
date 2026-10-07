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

    first = c.declare_scope_docs(
        state, sessions, claims,
        repository="example/governed",
        continuity_id="GRT-CONT-DEMO-01",
        coordination_issue=259,
        coordination_state_ref="github-issue-comment:100",
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

    second = c.declare_scope_docs(
        state, sessions, claims,
        repository="example/governed",
        continuity_id="GRT-CONT-DEMO-01",
        coordination_issue=259,
        coordination_state_ref="github-issue-comment:100",
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
            coordination_state_ref="github-issue-comment:100",
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
        coordination_state_ref="github-issue-comment:200",
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
            coordination_state_ref="github-issue-comment:200",
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
    expect_error(
        lambda: c.declare_scope_docs(
            c.default_state(), sessions, claimed,
            repository="example/governed",
            continuity_id="GRT-CONT-CLAIM-01",
            coordination_issue=259,
            coordination_state_ref="github-issue-comment:300",
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

    expect_error(
        lambda: c.declare_scope_docs(
            c.default_state(), sessions, claims,
            repository="example/governed",
            continuity_id="GRT-CONT-STALE-01",
            coordination_issue=259,
            coordination_state_ref="github-issue-comment:400",
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

    expect_error(
        lambda: c.declare_scope_docs(
            c.default_state(), sessions, claims,
            repository="example/governed",
            continuity_id="GRT-CONT-RETURN-01",
            coordination_issue=259,
            coordination_state_ref="github-issue-comment:500",
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
        coordination_state_ref="github-issue-comment:600",
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
