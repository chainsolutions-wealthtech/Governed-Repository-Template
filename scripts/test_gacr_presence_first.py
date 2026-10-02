#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "gacr_auto_attach.py"
MODULE = ROOT / "scripts" / "gacr_auto_attach.py"

PROVENANCE_CLASSES = {
    "OBSERVABLE_BY_PLATFORM",
    "DECLARED_BY_AGENT_OR_CLIENT",
    "DERIVED_SAFE",
    "CORRELATED",
    "PROVIDER_PRIVATE_UNAVAILABLE",
}

CANONICAL_FIELDS = {
    "gacr_session_id",
    "client_instance_id",
    "provider",
    "agent_identity",
    "agent_type_or_model",
    "repository",
    "repository_id",
    "organization",
    "git_provider",
    "github_actor",
    "github_app_or_installation",
    "connection_method",
    "permissions",
    "capabilities",
    "entry_action",
    "connection_intent",
    "task_id",
    "claim_id",
    "branch",
    "base_branch",
    "HEAD",
    "PR",
    "workflow_run_id",
    "job_id",
    "run_attempt",
    "event_type",
    "delivery_or_correlation_id",
    "connected_at",
    "last_seen_at",
    "heartbeat_seq",
    "lease_expires_at",
    "provider_conversation_ref",
    "provider_conversation_url",
    "checkpoint",
    "last_action",
    "last_evidence",
    "connection_fingerprint",
}


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def setup_root(root: Path) -> None:
    (root / ".template-source").write_text("", encoding="utf-8")
    config = json.loads((ROOT / ".governance" / "agent-relay" / "config.json").read_text(encoding="utf-8"))
    write(root / ".governance" / "agent-relay" / "config.json", config)
    write(root / ".governance" / "work" / "work-items.json", {"schema_version": "1.0.0", "work_items": []})
    write(root / ".governance" / "control-plane-state" / "gacr-sessions.json", {"schema_version": "1.0.0", "revision": 0, "sessions": []})
    write(root / ".governance" / "control-plane-state" / "gacr-claims.json", {"schema_version": "1.0.0", "revision": 0, "claims": []})
    write(root / ".governance" / "control-plane-state" / "gacr-takeovers.json", {"schema_version": "1.0.0", "revision": 0, "last_scan_at": None, "items": []})
    for name in ["beacons", "correlations", "dispatches", "forensics"]:
        write(root / ".governance" / "control-plane-state" / f"gacr-{name}.json", {"schema_version": "1.0.0", "revision": 0, "items": []})


def run(env: dict, *args: str, expect: int = 0) -> subprocess.CompletedProcess:
    cp = subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, env=env, text=True, capture_output=True)
    if cp.returncode != expect:
        raise AssertionError(
            f"return={cp.returncode} expected={expect}\nstdout={cp.stdout}\nstderr={cp.stderr}"
        )
    return cp


def assert_true(value, message: str) -> None:
    if not value:
        raise AssertionError(message)


def load_module():
    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location("gacr_auto_attach_presence_test", MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError("unable to load gacr_auto_attach")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def controlled_args(
    *,
    connection_ref: str,
    client_instance_id: str,
    head: str,
    observed_at: str,
    provider: str = "other",
    provider_ref: str | None = None,
) -> list[str]:
    args = [
        "--agent", "fresh-agent",
        "--provider", provider,
        "--connection-ref", connection_ref,
        "--client-instance-id", client_instance_id,
        "--repository", "example/governed",
        "--repository-id", "12345",
        "--organization", "example",
        "--git-provider", "github",
        "--github-actor", "gateway-actor",
        "--connection-method", "repository-connector-wrapper",
        "--surface-class", "CONTROLLED_INSTRUMENTABLE",
        "--observed-head", head,
        "--branch", "feature/presence",
        "--base-branch", "main",
        "--event-type", "REPOSITORY_READ_ACTIVITY",
        "--delivery-correlation-id", "gateway-request-001",
        "--observed-at", observed_at,
        "--capability", "READ_REPOSITORY",
        "--source", "PRESENCE_FABRIC",
    ]
    if provider_ref:
        args.extend(["--provider-ref", provider_ref])
    return args


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_root(root)
        env = os.environ.copy()
        env["GACR_ROOT"] = str(root)
        env["GITHUB_REPOSITORY"] = "example/governed"

        # TEST A — FIRST TOUCH.
        # The controlled repository surface supplies connection metadata as part
        # of repository use. The fresh agent is not instructed to register,
        # send a Beacon, heartbeat, or /gacr-host command.
        first = json.loads(run(
            env,
            *controlled_args(
                connection_ref="gateway:instance-1",
                client_instance_id="gateway-client-1",
                head="a" * 40,
                observed_at="2026-10-02T02:00:00+00:00",
            ),
        ).stdout)
        assert_true(first["status"] == "CREATE", "TEST A: first controlled touch must CREATE")
        assert_true(first["presence_event"] == "PRESENCE_FIRST_TOUCH", "TEST A: first-touch evidence")
        assert_true(first["binding"]["state"] == "BOUND", "TEST A: deterministic first touch must bind")
        sid = first["session"]["session_id"]
        assert_true(first["connection_envelope"]["fields"]["gacr_session_id"]["value"] == sid, "TEST A: envelope carries created session")

        resumed = json.loads(run(
            env,
            *controlled_args(
                connection_ref="gateway:instance-1",
                client_instance_id="gateway-client-1",
                head="b" * 40,
                observed_at="2026-10-02T02:07:00+00:00",
            ),
        ).stdout)
        assert_true(resumed["status"] == "RESUME", "TEST A: repeated controlled touch must RESUME")
        assert_true(resumed["session"]["session_id"] == sid, "TEST A: resume same canonical session")
        assert_true(resumed["presence_event"] == "PRESENCE_RESUME", "TEST A: resume evidence")

        # TEST B — CONNECTION ENVELOPE.
        envelope = first["connection_envelope"]
        assert_true(envelope["schema"] == "gacr-connection-envelope/v1", "TEST B: canonical envelope version")
        assert_true(envelope["surface_class"] == "CONTROLLED_INSTRUMENTABLE", "TEST B: surface class")
        assert_true(CANONICAL_FIELDS <= set(envelope["fields"]), "TEST B: exhaustive canonical fields")
        for name in CANONICAL_FIELDS:
            field = envelope["fields"][name]
            assert_true(set(field) >= {"value", "provenance"}, f"TEST B: {name} has value/provenance")
            assert_true(field["provenance"] in PROVENANCE_CLASSES, f"TEST B: {name} provenance class")
        assert_true(envelope["fields"]["provider_conversation_ref"]["value"] == "UNAVAILABLE", "TEST B: provider ref absent stays UNAVAILABLE")
        assert_true(envelope["fields"]["provider_conversation_url"]["value"] == "UNAVAILABLE", "TEST B: provider URL absent stays UNAVAILABLE")
        assert_true(envelope["fields"]["agent_type_or_model"]["value"] == "UNAVAILABLE", "TEST B: model/type is never invented")
        assert_true(envelope["fields"]["permissions"]["value"] == "UNAVAILABLE", "TEST B: permissions are never invented")
        assert_true(
            envelope["fields"]["provider_conversation_ref"]["provenance"] == "PROVIDER_PRIVATE_UNAVAILABLE",
            "TEST B: unavailable provider identity is explicitly private/unavailable",
        )
        assert_true(
            envelope["fields"]["repository_id"]["provenance"] == "OBSERVABLE_BY_PLATFORM",
            "TEST B: repository identity is platform-observed",
        )
        assert_true(
            envelope["fields"]["client_instance_id"]["provenance"] == "DECLARED_BY_AGENT_OR_CLIENT",
            "TEST B: supplied client instance preserves declared provenance",
        )
        assert_true(
            envelope["fields"]["gacr_session_id"]["provenance"] == "CORRELATED",
            "TEST B: session binding provenance is correlated",
        )
        assert_true(
            envelope["fields"]["connection_fingerprint"]["provenance"] == "DERIVED_SAFE",
            "TEST B: fingerprint provenance is safe-derived",
        )

        mod = load_module()
        for forbidden in [
            {"authorization": "Bearer should-not-enter"},
            {"cookies": "session=secret"},
            {"raw_transcript": "private conversation"},
            {"prompt": "raw prompt"},
            {"private_reasoning": "hidden"},
        ]:
            try:
                mod.validate_presence_observation(forbidden)
                raise AssertionError(f"TEST B: forbidden observation accepted: {forbidden}")
            except ValueError:
                pass

        # TEST C — CONNECTION FINGERPRINT.
        fp = first["connection_fingerprint"]
        assert_true(fp.startswith("GACR-FP1-"), "TEST C: versioned fingerprint prefix")
        assert_true(resumed["connection_fingerprint"] == fp, "TEST C: later HEAD/time must not change instance fingerprint")
        assert_true(
            resumed["connection_envelope"]["fields"]["HEAD"]["value"] == "b" * 40,
            "TEST C: current HEAD may advance while identity stays frozen",
        )

        distinct = json.loads(run(
            env,
            *controlled_args(
                connection_ref="gateway:instance-2",
                client_instance_id="gateway-client-2",
                head="b" * 40,
                observed_at="2026-10-02T02:07:00+00:00",
            ),
        ).stdout)
        assert_true(distinct["status"] == "CREATE", "TEST C: distinct stable instance creates")
        assert_true(distinct["connection_fingerprint"] != fp, "TEST C: distinct instance fingerprint differs")

        same_client_new_connection = json.loads(run(
            env,
            *controlled_args(
                connection_ref="gateway:instance-3",
                client_instance_id="gateway-client-1",
                head="b" * 40,
                observed_at="2026-10-02T02:07:00+00:00",
            ),
        ).stdout)
        assert_true(
            same_client_new_connection["status"] == "CREATE",
            "TEST C: a shared client_instance_id must not collapse an explicitly distinct connection",
        )
        assert_true(
            same_client_new_connection["connection_fingerprint"] != fp,
            "TEST C: distinct connection under same client has distinct fingerprint",
        )

        with_provider = json.loads(run(
            env,
            *controlled_args(
                connection_ref="gateway:instance-provider",
                client_instance_id="gateway-client-provider",
                head="c" * 40,
                observed_at="2026-10-02T02:08:00+00:00",
                provider="chatgpt",
                provider_ref="conversation-explicit-123",
            ),
        ).stdout)
        assert_true(
            with_provider["connection_fingerprint"] != "conversation-explicit-123",
            "TEST C: fingerprint is not provider conversation identity",
        )
        assert_true(
            with_provider["connection_envelope"]["fields"]["provider_conversation_ref"]["value"] == "conversation-explicit-123",
            "TEST C: explicit provider ref is preserved separately",
        )

        # Deliberately corrupt the fixture into two equally plausible active
        # sessions for the same stable anchor. Presence binding must fail closed.
        sessions_path = root / ".governance" / "control-plane-state" / "gacr-sessions.json"
        sessions_doc = json.loads(sessions_path.read_text(encoding="utf-8"))
        original = next(s for s in sessions_doc["sessions"] if s["session_id"] == sid)
        duplicate = json.loads(json.dumps(original))
        duplicate["session_id"] = "session-deliberate-ambiguity"
        sessions_doc["sessions"].append(duplicate)
        write(sessions_path, sessions_doc)
        before_count = len(sessions_doc["sessions"])

        ambiguous = json.loads(run(
            env,
            *controlled_args(
                connection_ref="gateway:instance-1",
                client_instance_id="gateway-client-1",
                head="d" * 40,
                observed_at="2026-10-02T02:09:00+00:00",
            ),
        ).stdout)
        after_doc = json.loads(sessions_path.read_text(encoding="utf-8"))
        assert_true(ambiguous["status"] == "UNBOUND_ACTIVITY", "TEST C: ambiguity must become UNBOUND_ACTIVITY")
        assert_true(ambiguous["binding"]["state"] == "AMBIGUOUS", "TEST C: ambiguity is explicit")
        assert_true(ambiguous["binding"]["selected_session_id"] == "UNAVAILABLE", "TEST C: no arbitrary session selection")
        assert_true(len(after_doc["sessions"]) == before_count, "TEST C: ambiguity must not create another session")

    print("GACR_PRESENCE_ACCEPTANCE_TESTS_A_B_C_PASS")


if __name__ == "__main__":
    main()
