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
            "--entry-action", "LAB_EVOLUTION",
            "--connection-intent", "CODE_CHANGE",
        ).stdout)
        assert_true(second["status"] == "RESUME", "late provider binding resumes")
        assert_true(second["session"]["session_id"] == sid, "late binding must not duplicate session")
        assert_true(second["session"]["provider"] == "chatgpt", "provider promoted from other")
        assert_true(second["session"]["provider_conversation_ref"] == "conversation-123", "provider ref enriched")
        assert_true(second["session"]["entry_action"] == "CONTINUE_GOVERNED_WORK", "resume cannot rewrite canonical entry action")
        assert_true(second["session"]["connection_intent"] == "OBSERVE", "resume cannot rewrite canonical connection intent")

        third = json.loads(run(
            env,
            "--provider", "chatgpt",
            "--provider-ref", "conversation-123",
            "--connection-ref", "chronicle:CHAT-MEM-TEST:SESSION-TEST",
            "--observed-head", "b"*40,
            "--branch", "main",
        ).stdout)
        assert_true(third["status"] == "RESUME", "repeat attach resumes")
        sessions = json.loads((root / ".governance" / "control-plane-state" / "gacr-sessions.json").read_text())
        beacons = json.loads((root / ".governance" / "control-plane-state" / "gacr-beacons.json").read_text())
        correlations = json.loads((root / ".governance" / "control-plane-state" / "gacr-correlations.json").read_text())
        assert_true(len(sessions["sessions"]) == 1, "one canonical session")
        assert_true(len(beacons["items"]) == 3, "each attach emits beacon")
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

        # A different GitHub workflow remains a valid external execution anchor.
        external = json.loads(run(
            env | {
                "GITHUB_ACTOR":"external-worker",
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
