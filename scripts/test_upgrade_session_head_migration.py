#!/usr/bin/env python3
from __future__ import annotations

import copy

import control_plane_upgrade_local_entry as upgrade

OLD = "a" * 40
CURRENT = "b" * 40
NEW = "c" * 40


def make_issue(head: str, revision: int = 22) -> dict:
    state = {
        "schema_version": "1.1.0",
        "request_id": "LOCAL-TEST",
        "repository": "owner/repo",
        "mode": "FIRST_AGENT_BOOTSTRAP",
        "status": "MCP_CREDENTIAL_REQUIRED",
        "phase": "MCP_CREDENTIAL_GATE",
        "revision": revision,
        "expected_head_sha": head,
        "answers": {"project_mission": "preserve me"},
        "next_request": {"kind": "CREDENTIAL_GATE"},
        "baseline_package": {"project_mission": "preserve me"},
        "handoff": None,
        "hold_reason": None,
        "setup_package": None,
        "mcp_discovery": None,
        "credentials_verified": False,
    }
    marker = upgrade.encode_local_issue_state(state)
    return {
        "number": 7,
        "title": "[Governed Local Entry] Test",
        "body": f"Initial\n\n<!-- GOVERNED_LOCAL_ENTRY_STATE:{marker} -->\n",
    }


def run_case(messages: list[str]) -> tuple[list[dict], list[dict]]:
    patched = []
    comments = []
    issue = make_issue(OLD)

    def fake_gh(token, method, path, payload=None, allow_404=False):
        if method == "GET" and "/issues?state=open" in path:
            return [copy.deepcopy(issue)]
        if method == "GET" and "/compare/" in path:
            return {
                "status": "ahead",
                "merge_base_commit": {"sha": OLD},
                "commits": [{"commit": {"message": message}} for message in messages],
            }
        if method == "PATCH" and path.endswith("/issues/7"):
            patched.append(copy.deepcopy(payload))
            return {}
        if method == "POST" and path.endswith("/issues/7/comments"):
            comments.append(copy.deepcopy(payload))
            return {}
        raise AssertionError((method, path, payload))

    original = upgrade.gh
    upgrade.gh = fake_gh
    try:
        migrated = upgrade.migrate_open_local_entry_heads("token", "owner/repo", CURRENT, NEW)
    finally:
        upgrade.gh = original

    if messages and all(m.splitlines()[0].startswith(upgrade.UPGRADE_PREFIX) for m in messages):
        assert len(migrated) == 1
    else:
        assert migrated == []
    return patched, comments


def main() -> None:
    manifest = __import__("json").loads(
        (upgrade.ROOT / ".governance" / "TEMPLATE_MANIFEST.json").read_text(encoding="utf-8")
    )
    assert upgrade.current_template_version() == manifest["template_version"]

    patched, comments = run_case([
        "governance: upgrade repository-local setup to v2.6.3",
        "governance: upgrade repository-local setup to v2.6.4",
        "governance: upgrade repository-local setup to v2.6.5",
    ])
    assert len(patched) == 1
    assert len(comments) == 1
    state = upgrade.decode_local_issue_state(patched[0]["body"])
    assert state["expected_head_sha"] == NEW
    assert state["revision"] == 23
    assert state["answers"]["project_mission"] == "preserve me"
    assert state["baseline_package"]["project_mission"] == "preserve me"

    patched_bad, comments_bad = run_case([
        "governance: upgrade repository-local setup to v2.6.3",
        "feat: unrelated project mutation",
    ])
    assert patched_bad == []
    assert comments_bad == []

    source_config = {
        "host_issue_bridge": {"issue_number": 115},
        "gscc_function_exposure_gate": {
            "issue_number": 161,
            "issue_title": "[GSCC Admission Gate] Provider event ingress",
            "source_issue_number_distributed": False,
            "client_issue_strategy": "DISABLED_UNTIL_LOCAL_NUMBER_BOUND",
        },
    }
    target_config = {
        "host_issue_bridge": {"issue_number": 222},
        "gscc_function_exposure_gate": {
            "issue_number": 333,
            "issue_title": "[Local GSCC Function Exposure]",
            "source_issue_number_distributed": False,
            "client_issue_strategy": "LOCAL_NUMBER_BOUND",
        },
    }
    merged = upgrade.merge_relay_config_for_client(source_config, target_config)
    assert merged["gscc_function_exposure_gate"]["issue_number"] == 333
    assert merged["gscc_function_exposure_gate"]["issue_title"] == "[Local GSCC Function Exposure]"
    assert merged["gscc_function_exposure_gate"]["client_issue_strategy"] == "LOCAL_NUMBER_BOUND"
    assert merged["gscc_function_exposure_gate"]["source_issue_number_distributed"] is False

    unbound = upgrade.merge_relay_config_for_client(source_config, {})
    assert unbound["gscc_function_exposure_gate"]["issue_number"] is None
    assert unbound["gscc_function_exposure_gate"]["client_issue_strategy"] == "DISABLED_UNTIL_LOCAL_NUMBER_BOUND"

    legacy_unbound = upgrade.merge_relay_config_for_client(
        source_config,
        {
            "gscc_function_exposure_gate": {
                "issue_number": 161,
                "source_issue_number_distributed": False,
                "client_issue_strategy": "DISABLED_UNTIL_LOCAL_NUMBER_BOUND",
            }
        },
    )
    assert legacy_unbound["gscc_function_exposure_gate"]["issue_number"] is None
    assert legacy_unbound["gscc_function_exposure_gate"]["client_issue_strategy"] == "DISABLED_UNTIL_LOCAL_NUMBER_BOUND"

    source = open(upgrade.__file__, "r", encoding="utf-8").read()
    assert 'local.update({"repository":target,"status":"WAITING_FOR_FIRST_AGENT"' not in source
    assert 'existing_local=target_text(token,target,".governance/local-entry/state.json")' in source

    # The client upgrader must follow the current Template version rather than
    # silently freezing one historical release.
    assert 'current_template_version()' in source
    assert 'TEMPLATE_MANIFEST.json' in source
    assert 'LOCAL_SETUP_UPGRADE_APPLIED' in source
    assert 'LOCAL_SETUP_V2_8_3_UPGRADE_APPLIED' not in source
    assert '"message":"governance: upgrade repository-local setup to v2.8.3"' not in source
    assert "reconcile_both_smart_routing" in source
    assert "reconcile_setup_question_order" in source
    assert "reconcile_domain_question_order" in source
    assert "reconcile_existing_host_path_question_order" in source

    # The distributed local-entry self-test must not require source-only
    # control-plane files that are intentionally absent from client repositories.
    local_entry_test=(upgrade.ROOT / "scripts" / "test_local_governed_entry.py").read_text(encoding="utf-8")
    if 'if (ROOT/".template-source").exists():' not in local_entry_test:
        raise SystemExit("UPGRADE_SELFTEST_FAILED: client local-entry test must guard source-only control-plane assertions")

    # Governance Model state is source-only. The distributed integrity test
    # must explicitly skip client repositories that do not have .template-source.
    governance_model_test=(upgrade.ROOT / "scripts" / "test_governance_model_integrity.py").read_text(encoding="utf-8")
    if 'if not (ROOT/".template-source").exists():' not in governance_model_test:
        raise SystemExit("UPGRADE_SELFTEST_FAILED: client governance-model integrity test must skip source-only model state")

    # Client CI runs the Governance Model integrity script, so the upgrader
    # must distribute the current portable version rather than leave a stale copy.
    source=open(upgrade.__file__, "r", encoding="utf-8").read()
    static_block=source.split("static_paths=[",1)[1].split("]",1)[0]
    if '"scripts/test_governance_model_integrity.py"' not in static_block:
        raise SystemExit("UPGRADE_SELFTEST_FAILED: upgrader must distribute portable governance-model integrity test")

    # Portable client CI requires the generic intent runtime/test surface.
    for required in [
        '"scripts/governance_agent.py"',
        '"scripts/test_connection_intent.py"',
        '".governance/connection-intent-policy.json"',
        '".governance/entry-action-policy.json"',
        '"docs/CONNECTION_INTENT.md"',
        '"docs/ENTRY_ACTION_ROUTER.md"',
    ]:
        assert required in source, required

    # GSCC function-exposure hardening is part of the portable client runtime.
    static_block=source.split("static_paths=[", 1)[1].split("]", 1)[0]
    for required in [
        '"scripts/gscc/admission.py"',
        '"scripts/gscc/capability_projection.py"',
        '"scripts/gscc_function_exposure_gate.py"',
        '"scripts/test_gscc_function_exposure_gate.py"',
        '".github/workflows/gscc-function-exposure-gate.yml"',
    ]:
        assert required in static_block, required

    assert '".governance/gscc/mcp-capability-snapshot.json"' in source
    assert "build_portable_capability_projection" in source

    assert "merge_relay_config_for_client" in source
    assert "existing_gacr_config" in source

    # Existing clients need a distinct additive AGENTS contract marker so an
    # already-present Repository-local control-plane section does not suppress
    # the new first-attach route rules.
    for required in [
        "## GACR controlled host route",
        "CONTINUE_GOVERNED_WORK",
        "route-neutral",
        "Provider enrichment",
    ]:
        assert required in source, required

    manifest_categories=manifest["categories"]
    for portable in [
        "scripts/gscc/capability_projection.py",
        "scripts/gscc_function_exposure_gate.py",
        "scripts/test_gscc_function_exposure_gate.py",
        ".github/workflows/gscc-function-exposure-gate.yml",
    ]:
        assert portable in manifest_categories["automation"], portable
    for no_longer_source_only in [
        "scripts/gscc_function_exposure_gate.py",
        "scripts/test_gscc_function_exposure_gate.py",
        ".github/workflows/gscc-function-exposure-gate.yml",
    ]:
        assert no_longer_source_only not in manifest_categories["control_plane_source_only"], no_longer_source_only

    # Stateful client work/session stores must never be overwritten by upgrade.
    for forbidden in [
        '".governance/work/work-items.json"',
        '".governance/work/claims.json"',
        '".governance/sessions/sessions.json"',
        '".governance/canonical-memory/current.json"',
    ]:
        assert forbidden not in source.split("static_paths=[", 1)[1].split("]", 1)[0], forbidden

    print("UPGRADE_SESSION_HEAD_MIGRATION_SELFTEST_PASS")


if __name__ == "__main__":
    main()
