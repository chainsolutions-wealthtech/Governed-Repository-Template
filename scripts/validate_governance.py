#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / ".governance"
PROFILE = GOV / "profile.json"
TEMPLATE_MARKER = ROOT / ".template-source"

REQUIRED = [
    "00_START_HERE.md",
    "GOVERNANCE.md",
    "AGENTS.md",
    "SOURCE_OF_TRUTH.md",
    "PROJECT_CONTEXT.md",
    "STATUS.md",
    "SUIVI.md",
    "TODO.md",
    "NEXT_ACTION.md",
    "LOOP_STATE.md",
    "CURRENT_ITERATION.md",
    "LOOP_ENGINEERING.md",
    "WORK_LOG.md",
    "HANDOFF.md",
    "CHANGELOG.md",
    "ASSUMPTIONS.md",
    "CONSTRAINTS.md",
    "RISKS.md",
    "DEPENDENCIES.md",
    "ACCEPTANCE_CRITERIA.md",
    "DEFINITION_OF_DONE.md",
    "docs/ARCHITECTURE.md",
    "docs/DECISIONS.md",
    "docs/AUTOMATION.md",
    "docs/MULTI_AGENT_COORDINATION.md",
    "docs/INFORMATION_INTAKE.md",
    "docs/PROJECT_PROFILES.md",
    "docs/INFRASTRUCTURE_BOOTSTRAP.md",
    "docs/CONNECTION_INTENT.md",
    "docs/ENTRY_ACTION_ROUTER.md",
    "docs/EXISTING_REPOSITORY_ADOPTION.md",
    "docs/PROJECT_MAPPING.md",
    "docs/LAB_EVOLUTION.md",
    "docs/REPOSITORY_SCOPES.md",
    "docs/CONTROL_PLANE.md",
    "docs/LOCAL_GOVERNED_ENTRY.md",
    ".governance/profile.json",
    ".governance/TEMPLATE_MANIFEST.json",
    ".governance/bootstrap-state.json",
    ".governance/canonical-memory/current.json",
    ".governance/work/work-items.json",
    ".governance/work/claims.json",
    ".governance/sessions/sessions.json",
    ".governance/intake/cursor.json",
    ".governance/project-profile.json",
    ".governance/infrastructure-intent.json",
    ".governance/connection-intent-policy.json",
    ".governance/entry-action-policy.json",
    ".governance/repository-scope-policy.json",
    ".governance/control-plane-policy.json",
    ".governance/repository-creation-executor.json",
    ".governance/local-entry-policy.json",
    ".governance/local-entry/state.json",
    ".governance/mcp-connection-policy.json",
    ".governance/mcp-binding.json",
    ".governance/access-plan.json",
    ".governance/workflow-model.json",
    "schemas/project-state.schema.json",
    "schemas/loop-state.schema.json",
    "schemas/next-action.schema.json",
    "schemas/bootstrap-receipt.schema.json",
    "schemas/session.schema.json",
    "schemas/work-item.schema.json",
    "schemas/work-claim.schema.json",
    "schemas/session-checkpoint.schema.json",
    "schemas/session-handoff.schema.json",
    "schemas/intake.schema.json",
    "schemas/project-profile.schema.json",
    "schemas/infrastructure-intent.schema.json",
    "schemas/connection-intent.schema.json",
    "schemas/entry-action.schema.json",
    "schemas/repository-scope.schema.json",
    "schemas/governed-request.schema.json",
    "schemas/execution-package.schema.json",
    "schemas/governed-handoff.schema.json",
    "schemas/local-entry-request.schema.json",
    "schemas/local-entry-receipt.schema.json",
    "schemas/mcp-binding.schema.json",
    "scripts/initialize_governance.py",
    "scripts/auto_bootstrap.py",
    "scripts/finalize_bootstrap.py",
    "scripts/governance_agent.py",
    "scripts/validate_governance.py",
    "scripts/test_bootstrap_consistency.py",
    "scripts/test_connection_intent.py",
    "scripts/adopt_existing_repository.py",
    "scripts/test_entry_action_router.py",
    "scripts/test_repository_adoption.py",
    "scripts/test_repository_scope.py",
    "scripts/governed_request.py",
    "scripts/control_plane_issue_bridge.py",
    "scripts/test_control_plane_request.py",
    "scripts/test_control_plane_issue_contract.py",
    "scripts/control_plane_create_repository.py",
    "scripts/test_repository_creation_executor.py",
    "scripts/local_governed_entry.py",
    "scripts/local_entry_issue_bridge.py",
    "scripts/local_entry_apply_baseline.py",
    "scripts/test_local_governed_entry.py",
    "scripts/mcp_repository_discovery.py",
    ".github/workflows/governed-local-entry.yml",
    ".github/ISSUE_TEMPLATE/governed-local-entry.yml",
    ".github/workflows/governance-ci.yml",
    ".github/workflows/governance-auto-bootstrap.yml",
]

PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
ATTESTATION_MODEL = "CHILD_COMMIT_ATTESTS_INITIALIZATION_COMMIT"
CONNECTION_INTENTS = {
    "OBSERVE",
    "CONTEXT_INTAKE",
    "INFORMATION_INTAKE",
    "WORK_REQUEST",
    "CODE_CHANGE",
    "REVIEW",
    "INFRASTRUCTURE",
    "UNKNOWN",
}
MUTABLE_INTENTS = {"WORK_REQUEST", "CODE_CHANGE", "INFRASTRUCTURE"}
ENTRY_ACTIONS = {
    "CREATE_NEW_REPOSITORY",
    "ADOPT_EXISTING_REPOSITORY",
    "MAP_EXISTING_PROJECT",
    "LAB_EVOLUTION",
    "CONTINUE_GOVERNED_WORK",
    "UNKNOWN",
}
ADOPTION_OPTIONAL_REQUIRED = {".github/workflows/governance-auto-bootstrap.yml"}
SOURCE_ONLY_REQUIRED = {
    ".github/workflows/governed-control-plane.yml",
    ".github/ISSUE_TEMPLATE/governed-request.yml",
    "docs/control-plane/CURRENT_STATE.md",
    "docs/control-plane/SUIVI.md",
    "docs/control-plane/NEXT_ACTION.md",
    "docs/control-plane/DECISIONS_LOG.md",
    "docs/control-plane/TASKS.md",
    "docs/control-plane/PROGRAM.md",
    "docs/control-plane/CASE1_REPLAY_LEDGER.md",
    ".governance/control-plane-state/current.json",
    ".governance/control-plane-state/checkpoint.json",
    ".governance/control-plane-state/handoff.json",
    ".governance/control-plane-state/tasks.json",
    ".governance/control-plane-state/case1-replay.json",
}
CONTROL_PLANE_REPOSITORY = "chainsolutions-wealthtech/Governed-Repository-Template"


def fail(message: str) -> None:
    raise SystemExit(f"GOVERNANCE_VALIDATION_FAILED: {message}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--bootstrap-attestation",
        action="store_true",
        help="Require the strict bootstrap-finalization invariants used by the zero-touch workflow.",
    )
    return p.parse_args()


def load(path: str) -> dict:
    try:
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {path}: {exc}")


def validate_policies(profile: dict) -> None:
    policies = profile.get("policies") or {}
    exact = {
        "force_push": "FORBIDDEN",
        "history_rewrite": "FORBIDDEN",
        "zero_regression": "REQUIRED",
        "verify_before_write": "REQUIRED",
        "verify_after_write": "REQUIRED",
        "observed_state_ne_assumed_state": "REQUIRED",
        "head_moved_reconciliation": "REQUIRED",
        "single_writer_per_collision_domain": "REQUIRED",
        "unknown_provider_identity": "NULL_NEVER_INVENT",
        "intake_ne_canonical_memory": "REQUIRED",
        "intake_ne_work_item": "REQUIRED",
        "contradiction": "HOLD_FOR_REVIEW",
        "automation_fail_closed": "REQUIRED",
        "runtime_authority_inference": "FORBIDDEN",
        "planned_ne_implemented": "REQUIRED",
        "infrastructure_facts_require_observation": "REQUIRED",
        "credentials_in_repository": "FORBIDDEN",
        "connection_intent_fail_closed": "REQUIRED",
        "context_intake_ne_code_permission": "REQUIRED",
        "intent_ne_authority": "REQUIRED",
        "entry_action_required": "REQUIRED",
        "entry_action_ne_intent": "REQUIRED",
        "entry_action_ne_authority": "REQUIRED",
        "existing_repository_adoption_additive": "REQUIRED",
        "lab_canonical_branch_protection": "REQUIRED",
        "personal_repository_scope_supported": "REQUIRED",
        "central_control_plane": "REQUIRED",
        "control_plane_request_state_external": "REQUIRED",
        "control_plane_target_mutation": "AGENT_AUTHORITY_REQUIRED",
        "control_plane_explicit_handoff": "REQUIRED",
        "control_plane_single_next_request": "REQUIRED",
        "repository_creation_executor": "REQUIRED",
        "repository_creation_visibility_explicit": "REQUIRED",
        "repository_creation_sequence": "OWNER_NAME_VISIBILITY_CREATE",
        "creator_credentials_in_git": "FORBIDDEN",
        "local_control_plane": "REQUIRED",
        "first_agent_baseline": "REQUIRED",
        "local_entry_head_guard": "REQUIRED",
        "local_entry_state_external_to_canonical_truth": "REQUIRED",
    }
    for key, expected in exact.items():
        if policies.get(key) != expected:
            fail(f"policy {key} must be {expected}, got {policies.get(key)!r}")


def validate_project_and_connection_intent(profile: dict, template_mode: bool) -> None:
    project_profile = load(".governance/project-profile.json")
    infrastructure = load(".governance/infrastructure-intent.json")
    intent_policy = load(".governance/connection-intent-policy.json")
    entry_policy = load(".governance/entry-action-policy.json")
    repository_scope = load(".governance/repository-scope-policy.json")
    creation_executor = load(".governance/repository-creation-executor.json")
    local_entry_policy = load(".governance/local-entry-policy.json")
    local_entry_state = load(".governance/local-entry/state.json")
    mcp_policy = load(".governance/mcp-connection-policy.json")
    mcp_binding = load(".governance/mcp-binding.json")
    access_plan = load(".governance/access-plan.json")
    workflow_model = load(".governance/workflow-model.json")
    sessions = load(".governance/sessions/sessions.json")

    if project_profile.get("selection_status") not in {"DISCOVERY_REQUIRED", "SELECTED", "HOLD_FOR_REVIEW"}:
        fail("invalid project-profile selection_status")
    selected = project_profile.get("selected_profile")
    profiles = project_profile.get("profiles") or {}
    if selected is not None and selected not in profiles:
        fail("selected project profile is not defined")
    if project_profile.get("organization_default_candidate") not in profiles:
        fail("organization default candidate is not defined")
    candidate = profiles.get("chainsolutions-fullstack-web") or {}
    stack = candidate.get("planned_stack") or {}
    if stack.get("backend", {}).get("runtime") != "Node.js":
        fail("Chainsolutions fullstack candidate must plan Node.js runtime")
    if stack.get("frontend", {}).get("framework") != "Next.js":
        fail("Chainsolutions fullstack candidate must plan Next.js frontend")
    if stack.get("database", {}).get("engine") != "PostgreSQL":
        fail("Chainsolutions fullstack candidate must plan PostgreSQL")
    if stack.get("backend", {}).get("status") != "PLANNED":
        fail("planned backend must not be represented as implemented")

    if infrastructure.get("server_access", {}).get("preferred") != "DIRECT_MCP":
        fail("direct MCP must be preferred server transport")
    if infrastructure.get("server_access", {}).get("fallback") != "SSH":
        fail("SSH must remain the governed fallback transport")
    if infrastructure.get("server_access", {}).get("credentials_in_repository") != "FORBIDDEN":
        fail("infrastructure intent must forbid repository credentials")
    if infrastructure.get("deployment_target", {}).get("provisioning_if_missing") != "PLANNED_REQUIRES_AUTHORITY":
        fail("missing deployment resources must require authority before provisioning")

    intents = intent_policy.get("intents") or {}
    if set(intents) != CONNECTION_INTENTS:
        fail("connection intent policy does not define the complete intent set")
    for name, rule in intents.items():
        expected_mutable = name in MUTABLE_INTENTS
        if bool(rule.get("may_dispatch_mutable_work")) != expected_mutable:
            fail(f"connection intent {name} mutable dispatch policy is invalid")
    if intents["UNKNOWN"].get("route") != "RESOLVE_CONNECTION_INTENT":
        fail("UNKNOWN connection intent must fail closed")
    if intents["CONTEXT_INTAKE"].get("may_dispatch_mutable_work") is not False:
        fail("context intake must never imply code permission")
    if intents["INFORMATION_INTAKE"].get("may_dispatch_mutable_work") is not False:
        fail("information intake must never imply code permission")

    actions = entry_policy.get("actions") or {}
    if set(actions) != ENTRY_ACTIONS:
        fail("entry action policy does not define the complete action set")
    if entry_policy.get("required_on_connection") is not True:
        fail("entry action must be required on connection")
    if actions["UNKNOWN"].get("initial_route") != "RESOLVE_ENTRY_ACTION":
        fail("UNKNOWN entry action must fail closed")
    if actions["ADOPT_EXISTING_REPOSITORY"].get("initial_mutable") is not False:
        fail("existing repository adoption must start read-only")
    if actions["MAP_EXISTING_PROJECT"].get("initial_mutable") is not False:
        fail("project mapping must start read-only")
    if actions["LAB_EVOLUTION"].get("initial_mutable") is not False:
        fail("lab evolution must start on discovery gate")
    if actions["CONTINUE_GOVERNED_WORK"].get("initial_mutable") is not True:
        fail("normal governed work continuity must remain available")

    scopes = repository_scope.get("supported_owner_scopes") or {}
    if scopes.get("ORGANIZATION", {}).get("supported") is not True:
        fail("organization repository scope must be supported")
    if scopes.get("PERSONAL_ACCOUNT", {}).get("supported") is not True:
        fail("personal account repository scope must be supported")
    if scopes.get("OTHER_AUTHORIZED_OWNER", {}).get("supported") is not True:
        fail("explicit other-owner scope must be supported")

    configured_targets = repository_scope.get("configured_creation_targets") or []
    actual_targets = {(item.get("owner"), item.get("scope")) for item in configured_targets}
    expected_targets = {
        ("chainsolutions-wealthtech", "ORGANIZATION"),
        ("Wealthtechinnovations", "PERSONAL_ACCOUNT"),
        ("Patricked-code", "PERSONAL_ACCOUNT"),
    }
    if actual_targets != expected_targets:
        fail("configured repository creation targets are invalid")
    creation_defaults = repository_scope.get("creation_defaults") or {}
    if creation_defaults.get("source_template") != CONTROL_PLANE_REPOSITORY:
        fail("repository creation must use the governed template source")
    if creation_defaults.get("visibility") != "ASK_AFTER_REPOSITORY_NAME":
        fail("repository creation visibility must be explicitly asked after repository name")
    if creation_defaults.get("initialize_from_template") is not True:
        fail("repository creation must initialize from template")
    if creation_defaults.get("add_manual_readme_gitignore_license") is not False:
        fail("repository creation must not add manual starter files")

    if creation_executor.get("executor") != "GITHUB_REST_GENERATE_FROM_TEMPLATE":
        fail("repository creation executor must use GitHub generate-from-template")
    if creation_executor.get("endpoint") != "POST /repos/chainsolutions-wealthtech/Governed-Repository-Template/generate":
        fail("repository creation executor endpoint is invalid")
    authentication = creation_executor.get("authentication") or {}
    if authentication.get("mode") != "GITHUB_APP_INSTALLATION_TOKEN_MINTED_PER_TARGET_OWNER":
        fail("repository creation executor authentication mode is invalid")
    if authentication.get("app_client_id_variable") != "GOVERNED_GITHUB_APP_CLIENT_ID":
        fail("repository creation executor client-id variable is invalid")
    if authentication.get("app_private_key_secret") != "GOVERNED_GITHUB_APP_PRIVATE_KEY":
        fail("repository creation executor private-key secret is invalid")
    if authentication.get("installation_token_environment") != "GOVERNED_CREATOR_TOKEN":
        fail("repository creation executor token environment is invalid")
    permissions = authentication.get("required_app_repository_permissions") or {}
    if permissions != {"administration": "write", "contents": "write", "workflows": "write"}:
        fail("repository creation executor permissions are invalid")
    installations = authentication.get("target_installations") or {}
    expected_installations = {
        "chainsolutions-wealthtech": ("chainsolutions-wealthtech", "ORGANIZATION"),
        "Wealthtechinnovations": ("Wealthtechinnovations", "PERSONAL_ACCOUNT"),
        "Patricked": ("Patricked-code", "PERSONAL_ACCOUNT"),
    }
    for label, expected in expected_installations.items():
        installation = installations.get(label) or {}
        actual = (installation.get("target_owner"), installation.get("account_type"))
        if actual != expected:
            fail(f"repository creation installation mapping invalid for {label}")
    if creation_executor.get("fail_closed") is not True:
        fail("repository creation executor must fail closed")

    if mcp_policy.get("role") != "REPOSITORY_TO_MCP_BINDING":
        fail("MCP connection policy role is invalid")
    if mcp_policy.get("direct_mcp", {}).get("token_secret") != "GOVERNED_MCP_AUTH_TOKEN":
        fail("MCP token secret contract is invalid")
    ssh_policy = mcp_policy.get("ssh", {})
    if ssh_policy.get("arbitrary_shell") != "FORBIDDEN":
        fail("MCP SSH fallback must forbid arbitrary shell")
    if ssh_policy.get("mode") != "GITHUB_OIDC_EPHEMERAL_CERTIFICATE":
        fail("MCP SSH fallback must use GitHub OIDC ephemeral certificates")
    if ssh_policy.get("persistent_private_key_secret") != "FORBIDDEN":
        fail("persistent repository SSH private keys must be forbidden")
    if ssh_policy.get("strict_host_key_checking") != "REQUIRED":
        fail("SSH fallback must require strict host key checking")
    certificate_max_seconds = ssh_policy.get("certificate_max_seconds")
    if not isinstance(certificate_max_seconds, int) or certificate_max_seconds < 1 or certificate_max_seconds > 600:
        fail("SSH certificate lifetime must be bounded to <= 600 seconds")
    if mcp_policy.get("fallback_transport") != "GITHUB_OIDC_EPHEMERAL_SSH_CERTIFICATE":
        fail("MCP fallback transport must be the ephemeral SSH certificate path")
    if access_plan.get("mcp", {}).get("write_activation") != "REQUIRES_MCP_PROJECT_REGISTRATION_AND_EXPLICIT_AUTHORITY":
        fail("MCP write activation must fail closed")
    if "REGULATORY_AFRICAFUNDS_GOVERNED_FLOW" not in (workflow_model.get("supported_models") or {}):
        fail("workflow model missing Regulatory/AfricaFunds governed flow")

    if local_entry_policy.get("role") != "REPOSITORY_LOCAL_CONTROL_PLANE":
        fail("local entry policy role is invalid")
    if "FIRST_AGENT_BOOTSTRAP" not in (local_entry_policy.get("modes") or {}):
        fail("local entry policy missing FIRST_AGENT_BOOTSTRAP")
    if "NORMAL_GOVERNED_ENTRY" not in (local_entry_policy.get("modes") or {}):
        fail("local entry policy missing NORMAL_GOVERNED_ENTRY")
    if local_entry_state.get("repository") != project_profile.get("repository"):
        fail("local entry state repository does not match project profile")
    if template_mode:
        if local_entry_state.get("status") != "WAITING_FOR_FIRST_AGENT":
            fail("template local entry state must start WAITING_FOR_FIRST_AGENT")
        if local_entry_state.get("first_agent_completed") is not False:
            fail("template local entry state must not be completed")
    elif local_entry_state.get("first_agent_completed") is True:
        receipt_path = ROOT / ".governance" / "local-entry" / "receipt.json"
        if not receipt_path.exists():
            fail("completed first-agent baseline requires local-entry receipt")
        local_receipt = load(".governance/local-entry/receipt.json")
        if local_receipt.get("repository") != profile.get("repository"):
            fail("local entry receipt repository mismatch")

    for session in sessions.get("sessions", []):
        intent = session.get("connection_intent")
        if intent not in CONNECTION_INTENTS:
            fail(f"session has invalid connection intent {intent!r}")
        provenance = session.get("connection_intent_provenance")
        if provenance not in {"PROVIDED_BY_CLIENT", "DEFAULT_UNKNOWN"}:
            fail("session connection intent provenance is invalid")
        entry_action = session.get("entry_action")
        if entry_action not in ENTRY_ACTIONS:
            fail(f"session has invalid entry action {entry_action!r}")
        entry_provenance = session.get("entry_action_provenance")
        if entry_provenance not in {"PROVIDED_BY_CLIENT", "DEFAULT_UNKNOWN"}:
            fail("session entry action provenance is invalid")

    if not template_mode:
        repository = profile.get("repository")
        if project_profile.get("repository") != repository:
            fail("project profile repository does not match governance profile")
        if infrastructure.get("repository") != repository:
            fail("infrastructure intent repository does not match governance profile")
        if infrastructure.get("github_binding", {}).get("repository") != repository:
            fail("infrastructure GitHub binding does not match governance profile")
        if mcp_binding.get("repository") != repository:
            fail("MCP binding repository does not match governance profile")
        if access_plan.get("repository") != repository:
            fail("access plan repository does not match governance profile")
        if workflow_model.get("repository") != repository:
            fail("workflow model repository does not match governance profile")
        target_owner = repository.split("/", 1)[0]
        if repository_scope.get("target_owner") not in {target_owner, None}:
            fail("repository scope target owner does not match repository")


def validate_control_plane(profile: dict, template_mode: bool) -> None:
    policy = load(".governance/control-plane-policy.json")
    if policy.get("control_plane_repository") != CONTROL_PLANE_REPOSITORY:
        fail("control plane repository binding is invalid")
    if policy.get("source_role") != "CENTRAL_GOVERNANCE_CONTROL_PLANE":
        fail("control plane source role is invalid")
    if policy.get("client_role_after_instantiation") != "GOVERNED_TARGET_CLIENT":
        fail("control plane client role is invalid")

    expected_source_only = {
        ".github/workflows/governed-control-plane.yml",
        ".github/ISSUE_TEMPLATE/governed-request.yml",
        "docs/control-plane",
        ".governance/control-plane-state",
    }
    if set(policy.get("source_only_paths") or []) != expected_source_only:
        fail("control plane source-only path contract is invalid")

    principles = set(policy.get("principles") or [])
    required_principles = {
        "CONTROL_PLANE_PREPARES_TARGET_WORK",
        "ONE_QUESTION_OR_ACTION_REQUEST_AT_A_TIME",
        "AGENT_RESPONSES_ADVANCE_STATE_MACHINE",
        "TARGET_MUTATION_REQUIRES_EXPLICIT_AUTHORITY",
        "TARGET_EVIDENCE_NE_ASSUMED_STATE",
        "CONTROL_PLANE_STATE_STAYS_OUT_OF_TEMPLATE_CONTENT",
        "HANDOFF_IS_EXPLICIT",
        "CROSS_REPOSITORY_MUTATION_ONLY_VIA_AUTHORIZED_EXECUTOR",
        "STANDARD_GITHUB_TOKEN_CANNOT_CREATE_TARGET_REPOSITORIES",
        "CREATOR_CREDENTIALS_STAY_OUTSIDE_GIT",
    }
    if not required_principles.issubset(principles):
        fail("control plane principles are incomplete")

    if template_mode:
        if policy.get("current_role") != "CENTRAL_GOVERNANCE_CONTROL_PLANE":
            fail("template source must be the central governance control plane")
        for relative in expected_source_only:
            if not (ROOT / relative).exists():
                fail(f"control plane source-only path is missing: {relative}")
        source_current = load(".governance/control-plane-state/current.json")
        source_checkpoint = load(".governance/control-plane-state/checkpoint.json")
        source_handoff = load(".governance/control-plane-state/handoff.json")
        source_tasks = load(".governance/control-plane-state/tasks.json")
        case1_replay = load(".governance/control-plane-state/case1-replay.json")
        if source_current.get("repository") != CONTROL_PLANE_REPOSITORY:
            fail("control-plane source current repository mismatch")
        if source_current.get("role") != "CENTRAL_GOVERNANCE_CONTROL_PLANE":
            fail("control-plane source current role mismatch")
        if source_current.get("unique_next_action") != source_handoff.get("unique_next_action"):
            fail("control-plane source next action/handoff mismatch")
        if source_checkpoint.get("next_action") != source_current.get("unique_next_action"):
            fail("control-plane source checkpoint next action mismatch")
        executable = [x for x in source_tasks.get("items", []) if x.get("status") == "IN_PROGRESS"]
        if len(executable) != 1:
            fail("control-plane source tasks must have exactly one IN_PROGRESS item")
        if source_tasks.get("unique_executable_item") != executable[0].get("id"):
            fail("control-plane source unique executable task mismatch")
        if case1_replay.get("case_id") != "CREATE_NEW_REPOSITORY":
            fail("CASE 1 replay ledger case id mismatch")
        if case1_replay.get("unique_next_action") != source_current.get("unique_next_action"):
            fail("CASE 1 replay ledger next action mismatch")
        if case1_replay.get("current_phase") not in {p.get("id") for p in case1_replay.get("phases", [])}:
            fail("CASE 1 replay current phase missing from phases")
        active_case_phases = [p for p in case1_replay.get("phases", []) if p.get("status") == "IN_PROGRESS"]
        if len(active_case_phases) != 1 or active_case_phases[0].get("id") != case1_replay.get("current_phase"):
            fail("CASE 1 replay must have exactly one active phase matching current_phase")
        source_docs = [
            "docs/control-plane/CURRENT_STATE.md",
            "docs/control-plane/SUIVI.md",
            "docs/control-plane/NEXT_ACTION.md",
            "docs/control-plane/DECISIONS_LOG.md",
            "docs/control-plane/TASKS.md",
            "docs/control-plane/PROGRAM.md",
            "docs/control-plane/CASE1_REPLAY_LEDGER.md",
        ]
        for relative in source_docs:
            text = (ROOT / relative).read_text(encoding="utf-8")
            if PLACEHOLDER.search(text):
                fail(f"control-plane source authority contains unresolved template placeholder: {relative}")

        workflow = (ROOT / ".github/workflows/governed-control-plane.yml").read_text(encoding="utf-8")
        workflow_requirements = [
            "github.repository == 'chainsolutions-wealthtech/Governed-Repository-Template'",
            "issues: write",
            "contents: read",
            "github.actor != 'github-actions[bot]'",
            "repository_dispatch:",
            "governed_request_start",
            "python3 scripts/control_plane_issue_bridge.py",
            "python3 scripts/control_plane_create_repository.py",
            "actions/create-github-app-token@v3",
            "GOVERNED_GITHUB_APP_CLIENT_ID",
            "GOVERNED_GITHUB_APP_PRIVATE_KEY",
            "GOVERNED_CREATOR_TOKEN",
            "permission-administration: write",
            "permission-contents: read",
        ]
        for fragment in workflow_requirements:
            if fragment not in workflow:
                fail(f"control plane workflow boundary missing: {fragment}")
    else:
        if policy.get("current_role") != "GOVERNED_TARGET_CLIENT":
            fail("instantiated/adopted repository must be a control plane client")
        if policy.get("client_repository") != profile.get("repository"):
            fail("control plane client repository does not match governance profile")
        for relative in expected_source_only:
            if (ROOT / relative).exists():
                fail(f"control plane source-only path leaked into target client: {relative}")


def validate_machine_state(profile: dict, template_mode: bool, require_bootstrap_attestation: bool = False) -> None:
    bootstrap = load(".governance/bootstrap-state.json")
    memory = load(".governance/canonical-memory/current.json")
    work = load(".governance/work/work-items.json")
    claims = load(".governance/work/claims.json")
    sessions = load(".governance/sessions/sessions.json")
    cursor = load(".governance/intake/cursor.json")

    if not isinstance(work.get("items"), list):
        fail("work-items.json items must be an array")
    if not isinstance(claims.get("claims"), list):
        fail("claims.json claims must be an array")
    if not isinstance(sessions.get("sessions"), list):
        fail("sessions.json sessions must be an array")
    if not isinstance(cursor.get("pending_intake_ids"), list):
        fail("intake cursor pending_intake_ids must be an array")

    ids = [item.get("work_item_id") for item in work["items"]]
    if len(ids) != len(set(ids)):
        fail("duplicate work item id")

    active_claim_domains: dict[str, str] = {}
    known_items = set(ids)
    for claim in claims["claims"]:
        if claim.get("work_item_id") not in known_items:
            fail(f"claim references unknown work item {claim.get('work_item_id')}")
        if claim.get("status") == "ACTIVE":
            for domain in claim.get("collision_domains", []):
                previous = active_claim_domains.get(domain)
                if previous and previous != claim.get("session_id"):
                    fail(f"collision domain {domain} has multiple active writers")
                active_claim_domains[domain] = claim.get("session_id")

    if int(cursor.get("reconciled_through_sequence", 0)) > int(cursor.get("latest_sequence", 0)):
        fail("intake reconciled sequence exceeds latest sequence")

    if template_mode:
        if bootstrap.get("status") != "TEMPLATE_SOURCE" or bootstrap.get("initialized") is not False:
            fail("template bootstrap state must remain TEMPLATE_SOURCE/uninitialized")
        if memory.get("freshness") != "TEMPLATE_SOURCE":
            fail("template canonical memory must remain TEMPLATE_SOURCE")
        return

    if bootstrap.get("initialized") is not True:
        fail("instantiated bootstrap state is not initialized")

    initialization_mode = profile.get("initialization_mode") or "TEMPLATE_BOOTSTRAP"
    bootstrap_status = bootstrap.get("status")

    if initialization_mode == "EXISTING_REPOSITORY_ADOPTION":
        if require_bootstrap_attestation:
            fail("bootstrap attestation mode is not applicable to existing-repository adoption")
        if bootstrap_status != "ADOPTED_EXISTING_REPOSITORY":
            fail("adopted repository bootstrap-state status is invalid")
        adoption_receipt_path = ROOT / ".governance" / "adoption-receipt.json"
        adoption_state_path = ROOT / ".governance" / "adoption" / "state.json"
        if not adoption_receipt_path.exists() or not adoption_state_path.exists():
            fail("adopted repository is missing adoption receipt/state")
        adoption_receipt = load(".governance/adoption-receipt.json")
        adoption_state = load(".governance/adoption/state.json")
        if adoption_receipt.get("repository") != profile.get("repository"):
            fail("adoption receipt repository does not match profile")
        if adoption_receipt.get("preservation_contract") != "NO_EXISTING_FILE_OVERWRITE":
            fail("adoption preservation contract is invalid")
        if adoption_state.get("existing_files_overwritten") != 0:
            fail("adoption state reports an existing file overwrite")
        if memory.get("freshness") != "ADOPTION_ATTESTED":
            fail("adopted repository canonical memory must be ADOPTION_ATTESTED")
        if memory.get("current_checkpoint") != "adoption":
            fail("adopted repository checkpoint must be adoption")
    else:
        receipt_path = ROOT / ".governance" / "bootstrap-receipt.json"
        if not receipt_path.exists():
            fail("instantiated repository is missing bootstrap receipt")
        receipt = load(".governance/bootstrap-receipt.json")
        if receipt.get("repository") != profile.get("repository"):
            fail("bootstrap receipt repository does not match profile")
        if receipt.get("initialized") is not True:
            fail("bootstrap receipt is not initialized")

        if bootstrap_status not in {"INITIALIZED_PENDING_ATTESTATION", "PASS"}:
            fail(f"unexpected instantiated bootstrap status {bootstrap_status!r}")

    if require_bootstrap_attestation:
        receipt = load(".governance/bootstrap-receipt.json")
        if bootstrap_status != "PASS":
            fail("strict bootstrap attestation requires bootstrap status PASS")
        initialization_sha = receipt.get("initialization_commit_sha")
        if not isinstance(initialization_sha, str) or not SHA40.fullmatch(initialization_sha):
            fail("strict bootstrap attestation requires a valid initialization_commit_sha")
        if receipt.get("validation") != "PASS":
            fail("strict bootstrap attestation requires receipt validation PASS")
        if receipt.get("attestation_subject_sha") != initialization_sha:
            fail("receipt attestation subject does not match initialization commit")
        if receipt.get("attestation_model") != ATTESTATION_MODEL:
            fail("receipt attestation model is invalid")
        if bootstrap.get("attested_initialization_commit_sha") != initialization_sha:
            fail("bootstrap-state attested initialization commit does not match receipt")
        if bootstrap.get("attestation_subject_sha") != initialization_sha:
            fail("bootstrap-state attestation subject does not match receipt")
        if bootstrap.get("attestation_model") != ATTESTATION_MODEL:
            fail("bootstrap-state attestation model is invalid")
        if memory.get("bootstrap_attestation_subject_sha") != initialization_sha:
            fail("canonical memory bootstrap attestation subject does not match receipt")
        if memory.get("attestation_model") != ATTESTATION_MODEL:
            fail("canonical memory attestation model is invalid")
        if memory.get("freshness") != "ATTESTED":
            fail("strict bootstrap attestation requires canonical memory freshness ATTESTED")
        if memory.get("current_checkpoint") != "bootstrap":
            fail("strict bootstrap attestation requires bootstrap checkpoint")

        status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
        required_status_fragments = [
            "> State: `GOVERNANCE_INITIALIZED_BASELINE_REQUIRED`",
            f"- Repository: `{profile.get('repository')}`",
            f"- Branch: `{profile.get('canonical_branch')}`",
            f"- Attested initialization commit: `{initialization_sha}`",
            "- Governance validation: `PASS`",
            "- Governance freshness: `ATTESTED`",
            f"- Next action: `{memory.get('next_action')}`",
        ]
        missing_status = [fragment for fragment in required_status_fragments if fragment not in status]
        if missing_status:
            fail("STATUS.md is not synchronized with bootstrap attestation: " + " | ".join(missing_status))

        next_action = (ROOT / "NEXT_ACTION.md").read_text(encoding="utf-8")
        expected_next_action = f"NEXT_ACTION = {memory.get('next_action')}"
        if expected_next_action not in next_action:
            fail("NEXT_ACTION.md does not match canonical memory after bootstrap attestation")

        loop_state = (ROOT / "LOOP_STATE.md").read_text(encoding="utf-8")
        required_loop_fragments = [
            f'"repository": "{profile.get("repository")}"',
            f'"canonical_branch": "{profile.get("canonical_branch")}"',
            f'"next_action": "{memory.get("next_action")}"',
            '"last_verification": "GOVERNANCE_BOOTSTRAP_ATTESTED"',
        ]
        missing_loop = [fragment for fragment in required_loop_fragments if fragment not in loop_state]
        if missing_loop:
            fail("LOOP_STATE.md is not synchronized with bootstrap attestation: " + " | ".join(missing_loop))

        work_log = (ROOT / "WORK_LOG.md").read_text(encoding="utf-8")
        if "- Result: `PASS`" not in work_log or "- Bootstrap attestation: `PASS`" not in work_log:
            fail("WORK_LOG.md does not record successful bootstrap attestation")

        suivi = (ROOT / "SUIVI.md").read_text(encoding="utf-8")
        required_suivi_fragments = [
            "- State: `GOVERNANCE_INITIALIZED_BASELINE_REQUIRED`",
            "- Bootstrap attestation: `PASS`",
            "- Next action: `DISCOVER_PROJECT_BASELINE`",
        ]
        missing_suivi = [fragment for fragment in required_suivi_fragments if fragment not in suivi]
        if missing_suivi:
            fail("SUIVI.md is not synchronized with bootstrap attestation: " + " | ".join(missing_suivi))

    if memory.get("repository") != profile.get("repository"):
        fail("canonical memory repository does not match profile")
    if memory.get("canonical_branch") != profile.get("canonical_branch"):
        fail("canonical memory branch does not match profile")
    if int(memory.get("canonical_revision", 0)) < 1:
        fail("canonical revision must be >= 1 after initialization")
    if int(memory.get("work_revision", 0)) < 1:
        fail("work revision must be >= 1 after initialization")
    if not memory.get("next_action"):
        fail("canonical memory next_action is required")


def validate_placeholders(relative_paths: list[str] | None = None) -> None:
    unresolved = []
    paths = [ROOT / p for p in relative_paths] if relative_paths is not None else list(ROOT.rglob("*"))
    for path in paths:
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix not in {".md", ".json", ".yml", ".yaml", ".txt"}:
            continue
        hits = sorted(set(PLACEHOLDER.findall(path.read_text(encoding="utf-8", errors="replace"))))
        if hits:
            unresolved.append(f"{path.relative_to(ROOT)}:{','.join(hits)}")
    if unresolved:
        fail("unresolved placeholders: " + " | ".join(unresolved))


def validate_python_automation() -> None:
    for relative in [
        "scripts/initialize_governance.py",
        "scripts/auto_bootstrap.py",
        "scripts/finalize_bootstrap.py",
        "scripts/governance_agent.py",
        "scripts/validate_governance.py",
        "scripts/test_bootstrap_consistency.py",
        "scripts/test_connection_intent.py",
        "scripts/adopt_existing_repository.py",
        "scripts/test_entry_action_router.py",
        "scripts/test_repository_adoption.py",
        "scripts/test_repository_scope.py",
        "scripts/governed_request.py",
        "scripts/control_plane_issue_bridge.py",
        "scripts/test_control_plane_request.py",
        "scripts/test_control_plane_issue_contract.py",
        "scripts/control_plane_create_repository.py",
        "scripts/test_repository_creation_executor.py",
        "scripts/local_governed_entry.py",
        "scripts/local_entry_issue_bridge.py",
        "scripts/local_entry_apply_baseline.py",
        "scripts/test_local_governed_entry.py",
        "scripts/mcp_repository_discovery.py",
    ]:
        path = ROOT / relative
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except SyntaxError as exc:
            fail(f"invalid Python automation {relative}: {exc}")


def main() -> None:
    args = parse_args()
    if not PROFILE.exists():
        fail("missing required file: .governance/profile.json")
    profile = load(".governance/profile.json")
    template_mode = TEMPLATE_MARKER.exists()
    adoption_mode = profile.get("initialization_mode") == "EXISTING_REPOSITORY_ADOPTION"
    required = [path for path in REQUIRED if not (adoption_mode and path in ADOPTION_OPTIONAL_REQUIRED)]
    if template_mode:
        required.extend(sorted(SOURCE_ONLY_REQUIRED))
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing:
        fail("missing required files: " + ", ".join(missing))

    validate_policies(profile)
    validate_python_automation()
    if template_mode:
        if profile.get("template_source") is not True:
            fail("template source marker exists but profile.template_source is not true")
        if profile.get("initialized") is not False:
            fail("template source must not be initialized")
        validate_project_and_connection_intent(profile, True)
        validate_control_plane(profile, True)
        validate_machine_state(profile, True, args.bootstrap_attestation)
        print("GOVERNANCE_VALIDATION_PASS: template source mode v2")
        return

    if profile.get("template_source") is True:
        fail("instantiated repository still marked as template_source")
    if profile.get("initialized") is not True:
        fail("instantiated repository is not initialized")
    if profile.get("repository") in {None, "", "TO_INITIALIZE"}:
        fail("repository not initialized")
    if profile.get("canonical_branch") in {None, "", "TO_INITIALIZE"}:
        fail("canonical_branch not initialized")

    if profile.get("initialization_mode") == "EXISTING_REPOSITORY_ADOPTION":
        adoption_receipt = load(".governance/adoption-receipt.json")
        validate_placeholders(adoption_receipt.get("added_files") or [])
    else:
        validate_placeholders()
    validate_project_and_connection_intent(profile, False)
    validate_control_plane(profile, False)
    validate_machine_state(profile, False, args.bootstrap_attestation)
    print("GOVERNANCE_VALIDATION_PASS: instantiated repository mode v2")


if __name__ == "__main__":
    main()
