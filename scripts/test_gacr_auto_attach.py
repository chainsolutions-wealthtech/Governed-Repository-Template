#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "gacr_auto_attach.py"


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def run(env: dict, *args: str, expect: int = 0) -> subprocess.CompletedProcess:
    cp = subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, env=env, text=True, capture_output=True)
    if cp.returncode != expect:
        raise AssertionError(f"return={cp.returncode} expected={expect}\nstdout={cp.stdout}\nstderr={cp.stderr}")
    return cp


def assert_true(value, message: str) -> None:
    if not value:
        raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".template-source").write_text("", encoding="utf-8")
        config = json.loads((ROOT / ".governance" / "agent-relay" / "config.json").read_text(encoding="utf-8"))
        config["revision_authority_id"] = "CP-AGENT-RELAY-001-R4"
        config["auto_attachment"] = {
            "enabled": True,
            "chronicle_freshness_seconds": 3600,
            "provider_conversation_ref_required": False,
            "late_provider_binding_reuses_connection_session": True,
        }
        write(root / ".governance" / "agent-relay" / "config.json", config)
        write(root / ".governance" / "work" / "work-items.json", {"schema_version":"1.0.0","work_items":[]})
        write(root / ".governance" / "control-plane-state" / "gacr-sessions.json", {"schema_version":"1.0.0","revision":0,"sessions":[]})
        write(root / ".governance" / "control-plane-state" / "gacr-claims.json", {"schema_version":"1.0.0","revision":0,"claims":[]})
        write(root / ".governance" / "control-plane-state" / "gacr-takeovers.json", {"schema_version":"1.0.0","revision":0,"last_scan_at":None,"items":[]})
        for name in ["beacons","correlations","dispatches","forensics"]:
            write(root / ".governance" / "control-plane-state" / f"gacr-{name}.json", {"schema_version":"1.0.0","revision":0,"items":[]})

        chron_dir = root / ".governance" / "control-plane-state" / "conversation-chronicles"
        state_path = ".governance/control-plane-state/conversation-chronicles/CHAT-MEM-TEST.json"
        write(chron_dir / "current.json", {
            "schema_version":"1.0.0",
            "chronicle_id":"CHAT-MEM-TEST",
            "status":"ACTIVE",
            "state_path":state_path,
            "updated_at":{"value":"2099-01-01T00:00:00+00:00"},
        })
        write(root / state_path, {
            "schema_version":"1.0.0",
            "chronicle_id":"CHAT-MEM-TEST",
            "current_session":"SESSION-TEST",
            "status":"ACTIVE",
        })

        env = os.environ.copy()
        env["GACR_ROOT"] = str(root)
        env["GITHUB_REPOSITORY"] = "example/governed"
        first = json.loads(run(
            env,
            "--prefer-chronicle",
            "--observed-head", "a"*40,
            "--branch", "main",
            "--entry-action", "CONTINUE_GOVERNED_WORK",
            "--connection-intent", "OBSERVE",
        ).stdout)
        sid = first["session"]["session_id"]
        assert_true(first["status"] == "CREATE", "first attach creates")
        assert_true(first["identity_resolution"] == "NEW_LOGICAL_AGENT", "first attach creates a new logical agent")
        assert_true(first["attachment_source"] == "CONVERSATION_CHRONICLE", "chronicle selected")
        assert_true(first["session"]["connection_ref"] == "chronicle:CHAT-MEM-TEST:SESSION-TEST", "stable chronicle ref")
        assert_true(first["session"]["provider_conversation_ref"] is None, "conversation ref may be unavailable")
        assert_true(first["session"]["entry_action"] == "CONTINUE_GOVERNED_WORK", "create stores canonical entry action")
        assert_true(first["session"]["connection_intent"] == "OBSERVE", "create stores canonical connection intent")

        second = json.loads(run(
            env,
            "--prefer-chronicle",
            "--provider", "chatgpt",
            "--provider-ref", "conversation-123",
            "--connection-ref", "chronicle:CHAT-MEM-TEST:SESSION-TEST",
            "--client-instance-id", "chronicle:CHAT-MEM-TEST",
            "--observed-head", "a"*40,
            "--branch", "main",
        ).stdout)
        assert_true(second["status"] == "RESUME", "late provider binding resumes")
        assert_true(second["identity_resolution"] == "NEW_PROVIDER_CONTEXT_SAME_LOGICAL_AGENT", "late provider binding is a new provider context")
        assert_true(second["session"]["session_id"] == sid, "late binding must not duplicate session")
        assert_true(second["session"]["provider"] == "chatgpt", "provider promoted from other")
        assert_true(second["session"]["provider_conversation_ref"] == "conversation-123", "provider ref enriched")
        assert_true(second["session"]["entry_action"] == "CONTINUE_GOVERNED_WORK", "provider enrichment preserves canonical entry action")
        assert_true(second["session"]["connection_intent"] == "OBSERVE", "provider enrichment preserves canonical connection intent")

        rewrite = run(
            env,
            "--provider", "chatgpt",
            "--provider-ref", "conversation-123",
            "--connection-ref", "chronicle:CHAT-MEM-TEST:SESSION-TEST",
            "--observed-head", "a"*40,
            "--branch", "main",
            "--entry-action", "LAB_EVOLUTION",
            "--connection-intent", "CODE_CHANGE",
            expect=1,
        )
        assert_true("GACR_ROUTE_RECONCILIATION_REQUIRED" in rewrite.stderr, "route rewrite must fail closed")
        after_rewrite = json.loads((root / ".governance" / "control-plane-state" / "gacr-sessions.json").read_text())
        canonical = after_rewrite["sessions"][0]
        assert_true(canonical["entry_action"] == "CONTINUE_GOVERNED_WORK", "failed resume cannot mutate entry action")
        assert_true(canonical["connection_intent"] == "OBSERVE", "failed resume cannot mutate connection intent")

        third = json.loads(run(
            env,
            "--provider", "chatgpt",
            "--provider-ref", "conversation-123",
            "--connection-ref", "chronicle:CHAT-MEM-TEST:SESSION-TEST",
            "--observed-head", "b"*40,
            "--branch", "main",
        ).stdout)
        assert_true(third["status"] == "RESUME", "repeat attach resumes")
        assert_true(third["identity_resolution"] == "SAME_SESSION_RESUME", "repeat same context resumes same session")
        assert_true(len(third["session"]["provider_contexts"]) == 1, "same runtime surface enriches one provider context")
        assert_true(third["session"]["provider_contexts"][0]["provider_conversation_ref"] == "conversation-123", "provider context preserves provider ref")
        fourth = json.loads(run(
            env,
            "--provider", "chatgpt",
            "--provider-ref", "conversation-123",
            "--connection-ref", "chronicle:CHAT-MEM-TEST:SECOND-SURFACE",
            "--client-instance-id", "chronicle:CHAT-MEM-TEST-SECOND",
            "--observed-head", "b"*40,
            "--branch", "main",
        ).stdout)
        assert_true(fourth["status"] == "RESUME", "same provider conversation may resume through a new transport surface")
        assert_true(fourth["identity_resolution"] == "NEW_PROVIDER_CONTEXT_SAME_LOGICAL_AGENT", "new transport is a new provider context")
        assert_true(len(fourth["session"]["provider_contexts"]) == 2, "one session may preserve multiple provider contexts")
        assert_true(
            {item["connection_ref"] for item in fourth["session"]["provider_contexts"]}
            == {"chronicle:CHAT-MEM-TEST:SESSION-TEST", "chronicle:CHAT-MEM-TEST:SECOND-SURFACE"},
            "provider context history preserves both transport surfaces",
        )

        sessions = json.loads((root / ".governance" / "control-plane-state" / "gacr-sessions.json").read_text())
        beacons = json.loads((root / ".governance" / "control-plane-state" / "gacr-beacons.json").read_text())
        correlations = json.loads((root / ".governance" / "control-plane-state" / "gacr-correlations.json").read_text())
        assert_true(len(sessions["sessions"]) == 1, "one canonical session")
        assert_true(len(beacons["items"]) == 4, "each successful attach emits beacon")
        assert_true(any(x.get("selected_session_id") == sid for x in correlations["items"]), "correlator binds canonical session")


        # Once the Chronicle is stale, GACR's own workflow must never become
        # a second agent/session identity. The push bridge may skip cleanly.
        pointer_path = chron_dir / "current.json"
        stale_pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
        stale_pointer["updated_at"] = {"value":"2000-01-01T00:00:00+00:00"}
        write(pointer_path, stale_pointer)
        os.environ["GITHUB_ACTOR"] = "repo-actor"
        os.environ["GITHUB_WORKFLOW"] = "Governed Agent Continuity Relay"
        os.environ["GITHUB_RUN_ID"] = "999"
        os.environ["GITHUB_RUN_ATTEMPT"] = "1"
        os.environ["GITHUB_SHA"] = "c"*40
        before_sessions = json.loads((root / ".governance" / "control-plane-state" / "gacr-sessions.json").read_text())
        before_beacons = json.loads((root / ".governance" / "control-plane-state" / "gacr-beacons.json").read_text())
        skipped = json.loads(run(
            env | {
                "GITHUB_ACTOR":"repo-actor",
                "GITHUB_WORKFLOW":"Governed Agent Continuity Relay",
                "GITHUB_RUN_ID":"999",
                "GITHUB_RUN_ATTEMPT":"1",
                "GITHUB_SHA":"c"*40,
            },
            "--allow-unobservable-skip",
            "--observed-head", "c"*40,
            "--branch", "main",
        ).stdout)
        after_sessions = json.loads((root / ".governance" / "control-plane-state" / "gacr-sessions.json").read_text())
        after_beacons = json.loads((root / ".governance" / "control-plane-state" / "gacr-beacons.json").read_text())
        assert_true(skipped["status"] == "GACR_AUTO_ATTACH_SKIPPED", "internal workflow should skip")
        assert_true(skipped["attachment_created"] is False, "skip must not attach")
        assert_true(len(after_sessions["sessions"]) == len(before_sessions["sessions"]), "internal workflow must not create session")
        assert_true(len(after_beacons["items"]) == len(before_beacons["items"]), "internal workflow must not emit auto-attach beacon")

        # A fresh observable arrival that matches a stalled/takeover-ready
        # session must never resume or resurrect it. It is recorded as unbound
        # activity until the governed reconciliation/takeover path is used.
        stalled_sessions = json.loads(
            (root / ".governance" / "control-plane-state" / "gacr-sessions.json").read_text()
        )
        stalled_sessions["sessions"].append({
            "session_id": "session-stalled-observable",
            "agent_identity": "external-worker",
            "provider": "github-actions",
            "provider_conversation_ref": None,
            "connection_ref": "github-actions:example/governed:external-worker:stalled",
            "client_instance_id": "github-actor:external-worker",
            "repository": "example/governed",
            "starting_head_sha": "e" * 40,
            "last_observed_head_sha": "e" * 40,
            "status": "STALLED",
            "created_at": "2099-01-01T00:00:00+00:00",
            "last_seen_at": "2099-01-01T00:00:00+00:00",
            "capabilities": ["GACR_AUTO_ATTACH", "GACR_PRESENCE_FIRST"],
            "wake_channels": ["POLL_REPOSITORY"],
            "relay": {
                "process": "GACR",
                "state": "TAKEOVER_READY",
                "last_heartbeat_at": "2099-01-01T00:00:00+00:00",
                "lease_expires_at": "2099-01-01T00:30:00+00:00",
                "last_action": "STALL_DETECTED",
                "task_id": None,
                "branch": "main",
                "pull_request": None,
            },
            "surface_class": "GITHUB_EVENT_VISIBLE",
            "connection_method": "github-actions-event",
        })
        write(
            root / ".governance" / "control-plane-state" / "gacr-sessions.json",
            stalled_sessions,
        )
        before_stalled = json.loads(
            (root / ".governance" / "control-plane-state" / "gacr-sessions.json").read_text()
        )
        stalled_result = json.loads(run(
            env,
            "--agent", "external-worker",
            "--provider", "github-actions",
            "--connection-ref", "github-actions:example/governed:external-worker:stalled",
            "--client-instance-id", "github-actor:external-worker",
            "--repository", "example/governed",
            "--connection-method", "github-actions-event",
            "--surface-class", "GITHUB_EVENT_VISIBLE",
            "--observed-head", "f" * 40,
            "--branch", "main",
        ).stdout)
        after_stalled = json.loads(
            (root / ".governance" / "control-plane-state" / "gacr-sessions.json").read_text()
        )
        stalled_before = next(
            x for x in before_stalled["sessions"]
            if x["session_id"] == "session-stalled-observable"
        )
        stalled_after = next(
            x for x in after_stalled["sessions"]
            if x["session_id"] == "session-stalled-observable"
        )
        assert_true(stalled_result["status"] == "UNBOUND_ACTIVITY", "stalled match must become unbound activity")
        assert_true(stalled_result["identity_resolution"] == "UNRESOLVED_SURFACE", "stalled match remains unresolved")
        assert_true(stalled_result["binding"]["state"] == "UNBOUND", "stalled match must not remain bound")
        assert_true(
            stalled_result["binding"]["reason"] == "STALLED_SESSION_REQUIRES_GOVERNED_RECONCILIATION",
            "stalled match must require governed reconciliation",
        )
        assert_true(
            stalled_result["binding"]["candidate_session_ids"] == ["session-stalled-observable"],
            "stalled candidate identity must remain observable",
        )
        assert_true(stalled_after == stalled_before, "stalled canonical session must remain unchanged")
        assert_true(
            len(after_stalled["sessions"]) == len(before_stalled["sessions"]),
            "stalled arrival must not create a replacement session",
        )

        # A different GitHub workflow remains a valid external execution anchor.
        external = json.loads(run(
            env | {
                "GITHUB_ACTOR":"external-worker-fresh",
                "GITHUB_WORKFLOW":"External Governed Worker",
                "GITHUB_RUN_ID":"1000",
                "GITHUB_RUN_ATTEMPT":"1",
                "GITHUB_SHA":"d"*40,
            },
            "--observed-head", "d"*40,
            "--branch", "main",
        ).stdout)
        assert_true(external["status"] == "CREATE", "external GitHub worker may attach")
        assert_true(external["attachment_source"] == "GITHUB_ACTIONS", "external workflow source")

        conflict = run(
            env,
            "--provider", "claude",
            "--provider-ref", "claude-456",
            "--connection-ref", "chronicle:CHAT-MEM-TEST:SESSION-TEST",
            "--observed-head", "b"*40,
            "--branch", "main",
            expect=1,
        )
        assert_true("provider conflict" in (conflict.stderr + conflict.stdout), "provider conflict fails closed")

        print("GACR_AUTO_ATTACH_TEST_PASS")


if __name__ == "__main__":
    main()
