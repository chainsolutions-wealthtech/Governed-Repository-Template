#!/usr/bin/env python3
"""Owner Door-A F1 safety and non-regression tests; no network or credentials."""
from __future__ import annotations

import json
import sqlite3
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import gscc_owner_f1 as owner

NOW = datetime(2026, 10, 16, 20, 30, tzinfo=timezone.utc)
REPO = "chainsolutions-wealthtech/Governed-Repository-Template"
HEAD = "a" * 40
OLD_HEAD = "b" * 40
RUNTIME = "GSCC-RUNTIME-owner-test"
CONNECTION = "GSCC-CONN-owner-test"
SESSION = "session-owner-test"
ADMISSION = "GSCC-ADM-owner-test"
ISSUE = 327


def event(login="Wealthtechinnovations"):
    user = {"login": login, "id": 94637590 if login == "Wealthtechinnovations" else 94637591}
    return {
        "action": "created",
        "issue": {"number": ISSUE, "user": dict(user)},
        "comment": {"id": 900001, "user": dict(user), "body": "/gscc-entry-response ..."},
        "sender": dict(user),
        "repository": {"full_name": REPO},
    }


def fake_github(url):
    if url.startswith("https://api.github.com/users/"):
        login = url.split("/")[-1]
        return {"login": login, "id": 94637590 if login == "Wealthtechinnovations" else 94637591}
    if url == "https://api.github.com/repos/" + REPO:
        return {"full_name": REPO, "id": 1386478935}
    if url == "https://api.github.com/repos/" + REPO + "/branches/main":
        return {"name": "main", "commit": {"sha": HEAD}}
    raise AssertionError(url)


def admission():
    return {
        "schema": "gscc-admission-receipt/v1", "status": "PREAUTHORIZED",
        "admission_id": ADMISSION, "connection_ref": CONNECTION,
        "repository": REPO,
        "admission_context": {"target": {"requested_branch": "main"}},
    }


def previous_grant():
    return {
        "schema": "gscc-access-grant/v1",
        "grant_id": "GSCC-GRANT-prior",
        "admission_id": ADMISSION,
        "session_id": SESSION,
        "connection_ref": CONNECTION,
        "repository": REPO,
        "status": "AUTHORIZED",
        "bound_head": OLD_HEAD,
        "issued_at": (NOW - timedelta(days=2)).isoformat(),
        "expires_at": (NOW - timedelta(days=1)).isoformat(),
        "allowed_authority_classes": ["READ_ONLY_DISCOVERY_AUTHORITY"],
        "constraints": {"direct_main_write": False},
        "invocation_authority_granted": False,
        "mutation_authority_granted": False,
    }


def session():
    return {
        "session_id": SESSION, "connection_ref": CONNECTION,
        "status": "ACTIVE", "repository": REPO,
        "relay": {"state": "ACTIVE", "lease_expires_at": "2026-10-15T00:00:00Z"},
    }


def make_db(path):
    with sqlite3.connect(path) as conn:
        conn.execute("""CREATE TABLE gscc_session_runtime
        (runtime_id TEXT PRIMARY KEY,run_id TEXT,arrival_ref TEXT,identity_id TEXT,
         capture_id TEXT,issue_number INTEGER,connection_ref TEXT,state TEXT,
         admission_json TEXT,capability_evidence_json TEXT,control_evidence_json TEXT,
         gse_state_json TEXT,qualification_evidence_json TEXT,access_grant_json TEXT,
         last_gate TEXT,next_gate TEXT,created_at TEXT,updated_at TEXT)""")
        conn.execute("""CREATE TABLE gscc_session_bindings
        (arrival_ref TEXT,identity_id TEXT,gacr_session_id TEXT,binding_status TEXT,
         binding_level TEXT,connection_ref TEXT)""")
        conn.execute("INSERT INTO gscc_session_runtime VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            RUNTIME, "run-owner", "arrival-owner", "identity-owner", "capture-owner",
            ISSUE, CONNECTION, "READY_FOR_F1", json.dumps(admission()),
            "{}", "{}", "{}", "{}", json.dumps(previous_grant()), "Q12", "F1",
            NOW.isoformat(), NOW.isoformat(),
        ))
        conn.execute("INSERT INTO gscc_session_bindings VALUES (?,?,?,?,?,?)", (
            "arrival-owner", "identity-owner", SESSION, "GACR_BOUND", "EXACT", CONNECTION,
        ))


def expect_failure(fn, code):
    try:
        fn()
    except ValueError as exc:
        assert code in str(exc), (code, str(exc))
    else:
        raise AssertionError("unexpected admission: " + code)


def test_github_event_provenance():
    for login in owner.OWNER_LOGINS:
        e = event(login)
        proof = owner.verify_owner_event(
            e, issue_number=ISSUE, repository=REPO, branch="main",
            current_head=HEAD, github_request_fn=fake_github, github_actor=login,
        )
        assert proof["status"] == "VERIFIED" and proof["actor_login"] == login
        assert proof["observed_head"] == HEAD
        grant = owner.issue_owner_grant(
            previous_grant(), admission=admission(),
            runtime={"connection_ref": CONNECTION}, session_id=SESSION,
            proof=proof, now=NOW,
        )
        assert grant["schema"] == "gscc-access-grant/v1"
        assert grant["bound_head"] == HEAD
        assert set(owner.OWNER_ROLES) == set(grant["allowed_agent_roles"])
        assert all(x in grant["allowed_native_github_operations"]
                   for x in ("create_branch", "create_file", "update_file", "create_pull_request"))
        assert grant["constraints"]["f1_admission_requires_claim"] is False
        assert grant["constraints"]["f1_admission_requires_work_lease"] is False
        assert grant["mutation_authority_granted"] is False
        assert grant["owner_permission_model"] == "NATIVE_GITHUB_PER_OPERATION_NOT_REPOSITORY_ROLE_ESCALATION"

    nonowner = event("not-an-owner")
    expect_failure(lambda: owner.verify_owner_event(nonowner, issue_number=ISSUE,
        repository=REPO, branch="main", current_head=HEAD,
        github_request_fn=fake_github, github_actor="not-an-owner"),
        "OWNER_F1_SIGNED_GITHUB_ACTOR_OR_ISSUE_BINDING_REQUIRED")

    for family, field, value in (
        ("sender", "login", "someone-else"),
        ("issue", "number", 999),
        ("repository", "full_name", "someone/else"),
        ("comment", "id", None),
    ):
        e = event()
        e[family][field] = value
        expect_failure(lambda e=e: owner.verify_owner_event(e, issue_number=ISSUE,
            repository=REPO, branch="main", current_head=HEAD,
            github_request_fn=fake_github, github_actor="Wealthtechinnovations"),
            "OWNER_F1_SIGNED_GITHUB_ACTOR_OR_ISSUE_BINDING_REQUIRED")

    e = event()
    e["issue"]["user"]["login"] = "someone-else"
    expect_failure(lambda: owner.verify_owner_event(e, issue_number=ISSUE,
        repository=REPO, branch="main", current_head=HEAD,
        github_request_fn=fake_github, github_actor="Wealthtechinnovations"),
        "OWNER_F1_DELEGATED_ARRIVAL_REQUIRES_EXPLICIT_OWNER_APPROVAL")
    expect_failure(lambda: owner.verify_owner_event(event(), issue_number=ISSUE,
        repository=REPO, branch="main", current_head=OLD_HEAD,
        github_request_fn=fake_github, github_actor="Wealthtechinnovations"),
        "OWNER_F1_EXACT_LIVE_HEAD_REQUIRED")


def test_existing_runtime_release():
    # Route persistence already has separate historical tests. This verifies
    # that the owner release uses the *same* F1 and START_HERE gate transitions.
    calls = []
    original = owner._route
    owner._route = lambda db, runtime, gate, outcome, evidence, identity: calls.append(
        (gate, outcome, evidence, identity))
    try:
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "runtime.sqlite"
            make_db(db)
            result = owner.release_owner_f1(
                db, RUNTIME, event(), HEAD,
                sessions={"sessions": [session()]},
                github_request_fn=fake_github,
                github_actor="Wealthtechinnovations", now=NOW,
            )
            assert result["state"] == "RELEASED_TO_NORMAL_GOVERNANCE"
            assert result["start_here_status"] == "APPLICABLE"
            assert result["gacr_session_id"] == SESSION
            assert result["owner_f1_receipt"]["status"] == "VERIFIED"
            assert result["owner_f1_receipt"]["session_id"] == SESSION
            assert result["owner_f1_receipt"]["head"] == HEAD
            assert result["release_evidence"]["f1_exposure_receipt"] is None
            assert [c[:2] for c in calls] == [
                ("F1", "F1_VERIFIED"), ("00_START_HERE.md", "RELEASED")]
            with sqlite3.connect(db) as conn:
                state, grant_json = conn.execute(
                    "SELECT state,access_grant_json FROM gscc_session_runtime "
                    "WHERE runtime_id=?", (RUNTIME,),
                ).fetchone()
                assert state == "RELEASED_TO_NORMAL_GOVERNANCE"
                grant = json.loads(grant_json)
                assert grant["grant_id"] == result["access_grant"]["grant_id"]
                assert grant["owner_actor_login"] == "Wealthtechinnovations"
            expect_failure(lambda: owner.release_owner_f1(
                db, RUNTIME, event(), HEAD, sessions={"sessions": [session()]},
                github_request_fn=fake_github, github_actor="Wealthtechinnovations",
                now=NOW), "OWNER_F1_EXISTING_READY_FOR_F1_RUNTIME_REQUIRED")
    finally:
        owner._route = original


def test_binding_and_status_safety():
    original = owner._route
    owner._route = lambda *args, **kwargs: None
    try:
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "runtime.sqlite"
            make_db(db)
            with sqlite3.connect(db) as conn:
                conn.execute("UPDATE gscc_session_bindings SET binding_level='AMBIGUOUS'")
            expect_failure(lambda: owner.release_owner_f1(
                db, RUNTIME, event(), HEAD, sessions={"sessions": [session()]},
                github_request_fn=fake_github, github_actor="Wealthtechinnovations",
                now=NOW), "OWNER_F1_CANONICAL_EXACT_GACR_BINDING_REQUIRED")
            with sqlite3.connect(db) as conn:
                conn.execute("UPDATE gscc_session_bindings SET binding_level='EXACT'")
            expect_failure(lambda: owner.release_owner_f1(
                db, RUNTIME, event(), HEAD, sessions={"sessions": [{**session(), "status": "STALLED"}]},
                github_request_fn=fake_github, github_actor="Wealthtechinnovations",
                now=NOW), "OWNER_F1_ACTIVE_CANONICAL_SESSION_REQUIRED")
            expect_failure(lambda: owner.release_owner_f1(
                db, RUNTIME, event(), OLD_HEAD, sessions={"sessions": [session()]},
                github_request_fn=fake_github, github_actor="Wealthtechinnovations",
                now=NOW), "OWNER_F1_EXACT_LIVE_HEAD_REQUIRED")
    finally:
        owner._route = original



def test_explicit_owner_approval_for_other_agent_is_non_privileged():
    approved = event()
    approved["issue"]["user"] = {"login": "external-code-agent", "id": 83552001}
    approved["comment"]["body"] = (
        '/gscc-owner-f1-approve {"runtime_id":"' + RUNTIME + '"}'
    )
    proof = owner.verify_owner_event(
        approved, issue_number=ISSUE, repository=REPO, branch="main",
        current_head=HEAD, github_request_fn=fake_github,
        github_actor="Wealthtechinnovations", runtime_id=RUNTIME,
    )
    assert proof["approval_mode"] == "EXPLICIT_OWNER_APPROVAL_FOR_OTHER_AGENT"
    assert proof["owner_created_issue"] is False
    grant = owner.issue_owner_grant(
        previous_grant(), admission=admission(),
        runtime={"connection_ref": CONNECTION, "identity_id": "GSCC-ID-delegate"},
        session_id=SESSION, proof=proof, now=NOW,
    )
    assert owner.OWNER_CLASS not in grant["allowed_authority_classes"]
    assert not grant["allowed_native_github_operations"]
    assert not grant["allowed_agent_roles"]
    assert grant.get("active_role") is None
    assert grant["constraints"]["direct_main_write"] is False
    assert grant["mutation_authority_granted"] is False
    assert grant["approved_subject_identity_id"] == "GSCC-ID-delegate"
    original = owner._route
    owner._route = lambda *args, **kwargs: None
    try:
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "runtime.sqlite"
            make_db(db)
            result = owner.release_owner_f1(
                db, RUNTIME, approved, HEAD,
                sessions={"sessions": [session()]},
                github_request_fn=fake_github,
                github_actor="Wealthtechinnovations", now=NOW,
            )
            assert result["start_here_status"] == "APPLICABLE"
            assert result["owner_f1_receipt"]["subject_identity_id"] == "identity-owner"
            assert result["owner_approval_mode"] == "EXPLICIT_OWNER_APPROVAL_FOR_OTHER_AGENT"
            assert result["access_grant"]["constraints"]["direct_main_write"] is False
            assert owner.OWNER_CLASS not in result["access_grant"]["allowed_authority_classes"]
    finally:
        owner._route = original

    no_approval = event()
    no_approval["issue"]["user"] = approved["issue"]["user"]
    expect_failure(lambda: owner.verify_owner_event(
        no_approval, issue_number=ISSUE, repository=REPO, branch="main",
        current_head=HEAD, github_request_fn=fake_github,
        github_actor="Wealthtechinnovations", runtime_id=RUNTIME,
    ), "OWNER_F1_DELEGATED_ARRIVAL_REQUIRES_EXPLICIT_OWNER_APPROVAL")
    invalid = {**approved, "comment": {
        **approved["comment"],
        "body": '/gscc-owner-f1-approve {"runtime_id":"other-runtime"}',
    }}
    expect_failure(lambda: owner.verify_owner_event(
        invalid, issue_number=ISSUE, repository=REPO, branch="main",
        current_head=HEAD, github_request_fn=fake_github,
        github_actor="Wealthtechinnovations", runtime_id=RUNTIME,
    ), "OWNER_F1_APPROVAL_RUNTIME_MISMATCH")
    forged_sender = {**approved, "sender": {"login": "external-code-agent", "id": 83552001}}
    expect_failure(lambda: owner.verify_owner_event(
        forged_sender, issue_number=ISSUE, repository=REPO, branch="main",
        current_head=HEAD, github_request_fn=fake_github,
        github_actor="Wealthtechinnovations", runtime_id=RUNTIME,
    ), "OWNER_F1_SIGNED_GITHUB_ACTOR_OR_ISSUE_BINDING_REQUIRED")
    not_owner = {**approved, "comment": {
        **approved["comment"], "user": {"login": "external-code-agent", "id": 83552001}
    }}
    expect_failure(lambda: owner.verify_owner_event(
        not_owner, issue_number=ISSUE, repository=REPO, branch="main",
        current_head=HEAD, github_request_fn=fake_github,
        github_actor="external-code-agent", runtime_id=RUNTIME,
    ), "OWNER_F1_SIGNED_GITHUB_ACTOR_OR_ISSUE_BINDING_REQUIRED")


def test_head_drift_one_safe_retry_and_other_arrival_unmodified():
    route_calls = []
    old_route = owner._route
    owner._route = lambda db, runtime, gate, outcome, evidence, identity: route_calls.append(gate)
    try:
        with tempfile.TemporaryDirectory() as td:
            this_arrival = Path(td) / "this.sqlite"
            other_arrival = Path(td) / "other.sqlite"
            make_db(this_arrival)
            make_db(other_arrival)
            result = owner.release_owner_f1_with_head_reconciliation(
                this_arrival, RUNTIME, event(), OLD_HEAD,
                sessions={"sessions": [session()]}, github_request_fn=fake_github,
                github_actor="Wealthtechinnovations", now=NOW,
            )
            assert result["state"] == "RELEASED_TO_NORMAL_GOVERNANCE"
            assert result["released_head"] == HEAD
            assert result["head_reconciliation"]["retry_count"] == 1
            assert result["head_reconciliation"]["scope"] == "SAME_ARRIVAL_ONLY"
            assert route_calls == ["F1", "00_START_HERE.md"]
            with sqlite3.connect(other_arrival) as conn:
                state, old_grant = conn.execute(
                    "SELECT state,access_grant_json FROM gscc_session_runtime"
                ).fetchone()
                assert state == "READY_FOR_F1"
                assert json.loads(old_grant)["bound_head"] == OLD_HEAD
    finally:
        owner._route = old_route


def test_invalid_identity_and_binding_not_retried_or_released():
    route_calls = []
    old_route = owner._route
    owner._route = lambda *args, **kwargs: route_calls.append(args[2])
    try:
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "denied.sqlite"
            make_db(db)
            requests = []
            def counted(url):
                requests.append(url)
                return fake_github(url)

            invalid = event()
            invalid["sender"]["login"] = "forged"
            expect_failure(lambda: owner.release_owner_f1_with_head_reconciliation(
                db, RUNTIME, invalid, HEAD,
                sessions={"sessions": [session()]}, github_request_fn=counted,
                github_actor="Wealthtechinnovations", now=NOW),
                "OWNER_F1_SIGNED_GITHUB_ACTOR_OR_ISSUE_BINDING_REQUIRED")
            assert requests == []
            with sqlite3.connect(db) as conn:
                conn.execute("UPDATE gscc_session_bindings SET binding_level='AMBIGUOUS'")
            expect_failure(lambda: owner.release_owner_f1_with_head_reconciliation(
                db, RUNTIME, event(), OLD_HEAD,
                sessions={"sessions": [session()]}, github_request_fn=counted,
                github_actor="Wealthtechinnovations", now=NOW),
                "OWNER_F1_CANONICAL_EXACT_GACR_BINDING_REQUIRED")
            assert requests == []
            with sqlite3.connect(db) as conn:
                assert conn.execute("SELECT state FROM gscc_session_runtime").fetchone()[0] == "READY_FOR_F1"
            assert route_calls == []
    finally:
        owner._route = old_route


def test_second_head_drift_fails_closed_without_loop():
    routes = []
    old_route = owner._route
    owner._route = lambda *args, **kwargs: routes.append(args[2])
    try:
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "moving.sqlite"
            make_db(db)
            n = []
            def moving(url):
                if url.endswith("/branches/main"):
                    n.append(url)
                    return {"name": "main", "commit": {"sha": HEAD if len(n) == 1 else ("c" * 40 if len(n) == 2 else "d" * 40)}}
                return fake_github(url)
            expect_failure(lambda: owner.release_owner_f1_with_head_reconciliation(
                db, RUNTIME, event(), OLD_HEAD,
                sessions={"sessions": [session()]}, github_request_fn=moving,
                github_actor="Wealthtechinnovations", now=NOW),
                "OWNER_F1_EXACT_LIVE_HEAD_REQUIRED")
            assert len(n) == 3, "original HEAD read, one reobserve, final HEAD validation"
            with sqlite3.connect(db) as conn:
                assert conn.execute("SELECT state FROM gscc_session_runtime").fetchone()[0] == "READY_FOR_F1"
            assert routes == []
    finally:
        owner._route = old_route


def test_f1_failed_step_persists_evidence_then_marks_job_red():
    path = Path(__file__).resolve().parents[1] / ".github/workflows/gscc-provider-first-touch-ingress.yml"
    src = path.read_text(encoding="utf-8")
    f1 = src.split("      - name: Auto-release verified GitHub owner F1", 1)[1]
    f1 = f1.split("      - name: Publish durable canonical owner F1", 1)[0]
    assert "continue-on-error: true" in f1
    persist = src.split("      - name: Persist resumed per-arrival runtime state", 1)[1]
    assert "always() && steps.q9.outcome == 'success'" in persist.split(
        "      - name: Upload resumed runtime evidence", 1)[0]
    assert "steps.owner_f1.outcome == 'failure'" in src
    assert "OWNER_F1_NOT_RELEASED_THIS_ARRIVAL_ONLY" in src
    assert "exit 1" in src.split("      - name: Preserve explicit failed outcome after checkpoint", 1)[1].split("  renew_q12:", 1)[0]


if __name__ == "__main__":
    test_github_event_provenance()
    test_existing_runtime_release()
    test_binding_and_status_safety()
    test_explicit_owner_approval_for_other_agent_is_non_privileged()
    test_head_drift_one_safe_retry_and_other_arrival_unmodified()
    test_invalid_identity_and_binding_not_retried_or_released()
    test_second_head_drift_fails_closed_without_loop()
    test_f1_failed_step_persists_evidence_then_marks_job_red()
    print("GSCC_OWNER_F1_AUTO_ADMISSION_REGRESSION_PASS")
