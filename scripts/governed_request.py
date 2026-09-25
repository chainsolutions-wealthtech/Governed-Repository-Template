#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import copy
import json
import re
from typing import Any

CONTROL_PLANE_REPOSITORY = "chainsolutions-wealthtech/Governed-Repository-Template"
ENTRY_ACTIONS = [
    "CREATE_NEW_REPOSITORY",
    "ADOPT_EXISTING_REPOSITORY",
    "MAP_EXISTING_PROJECT",
    "LAB_EVOLUTION",
    "CONTINUE_GOVERNED_WORK",
]
CONNECTION_INTENTS = [
    "OBSERVE",
    "CONTEXT_INTAKE",
    "INFORMATION_INTAKE",
    "WORK_REQUEST",
    "CODE_CHANGE",
    "REVIEW",
    "INFRASTRUCTURE",
]
OWNER_SCOPES = ["ORGANIZATION", "PERSONAL_ACCOUNT", "OTHER_AUTHORIZED_OWNER"]
PROJECT_PROFILES = ["generic", "application", "chainsolutions-fullstack-web", "data-platform"]
LAB_PREFIXES = ("lab/", "claude/", "experiment/")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def question(qid: str, field: str, text: str, *, choices: list[Any] | None = None, response_type: str = "string") -> dict:
    result = {
        "kind": "QUESTION",
        "id": qid,
        "field": field,
        "text": text,
        "required": True,
        "response_type": response_type,
    }
    if choices is not None:
        result["choices"] = choices
    return result


def agent_request(qid: str, field: str, text: str, required_response: dict) -> dict:
    return {
        "kind": "AGENT_REQUEST",
        "id": qid,
        "field": field,
        "text": text,
        "required": True,
        "required_response": required_response,
    }


def action_request(action: dict) -> dict:
    return {
        "kind": "ACTION_REQUEST",
        "id": action["id"],
        "action_id": action["id"],
        "text": action["instructions"],
        "target": action.get("target"),
        "mutation_class": action["mutation_class"],
        "required_evidence": action["required_evidence"],
    }


def new_request(request_id: str, agent_identity: str | None, provider: str | None, initial_context: str | None = None) -> dict:
    state = {
        "schema_version": "1.0.0",
        "request_id": request_id,
        "control_plane_repository": CONTROL_PLANE_REPOSITORY,
        "status": "REQUEST_CREATED",
        "phase": "ENTRY_ACTION",
        "revision": 1,
        "agent": {
            "identity": agent_identity,
            "provider": provider,
        },
        "initial_context": initial_context,
        "answers": {},
        "execution_plan": [],
        "evidence": [],
        "next_request": None,
        "handoff": None,
        "hold_reason": None,
    }
    return refresh(state)


def validate_repository(value: Any) -> bool:
    return isinstance(value, str) and REPOSITORY_RE.fullmatch(value) is not None


def validate_observation(value: Any) -> str | None:
    if not isinstance(value, dict):
        return "target_observation must be an object"
    if value.get("exists") is not True:
        return "target repository must be observed as existing"
    if not value.get("default_branch"):
        return "target_observation.default_branch is required"
    head = value.get("head_sha")
    if not isinstance(head, str) or not SHA40.fullmatch(head):
        return "target_observation.head_sha must be a 40-character lowercase Git SHA"
    return None


def validate_answer(field: str, value: Any, state: dict) -> str | None:
    if field == "entry_action" and value not in ENTRY_ACTIONS:
        return "invalid entry action"
    if field == "connection_intent" and value not in CONNECTION_INTENTS:
        return "invalid connection intent"
    if field == "objective" and (not isinstance(value, str) or not value.strip()):
        return "objective must be non-empty text"
    if field == "target_scope" and value not in OWNER_SCOPES:
        return "invalid repository owner scope"
    if field == "target_owner" and (not isinstance(value, str) or not value.strip()):
        return "target_owner is required"
    if field == "repository_name" and (not isinstance(value, str) or "/" in value or not value.strip()):
        return "repository_name must be a repository name without owner"
    if field == "visibility" and value not in {"private", "public", "internal"}:
        return "visibility must be private, public or internal"
    if field == "project_type" and (not isinstance(value, str) or not value.strip()):
        return "project_type is required"
    if field == "project_profile" and value not in PROJECT_PROFILES:
        return "invalid project profile"
    if field in {"creation_authority", "adoption_authority", "mapping_write_authority", "lab_authority", "plan_approved"} and not isinstance(value, bool):
        return f"{field} must be boolean"
    if field == "infrastructure_preference" and value not in {"DISCOVER_AFTER_CREATION", "NO_SERVER_REQUIRED_YET", "KNOWN_TARGET_TO_VERIFY"}:
        return "invalid infrastructure preference"
    if field == "target_repository" and not validate_repository(value):
        return "target_repository must be owner/name"
    if field == "target_observation":
        return validate_observation(value)
    if field == "integration_strategy" and value not in {"DIRECT_CANONICAL_IF_AUTHORIZED", "EXISTING_BRANCH", "LAB_BRANCH"}:
        return "invalid integration strategy"
    if field == "mapping_scope" and value not in {"CURRENT_ONLY", "CURRENT_AND_TARGET"}:
        return "invalid mapping scope"
    if field == "target_architecture_requested" and not isinstance(value, bool):
        return "target_architecture_requested must be boolean"
    if field == "lab_branch_name":
        if not isinstance(value, str) or not value.startswith(LAB_PREFIXES):
            return "lab branch must start with lab/, claude/ or experiment/"
    if field == "pr_required" and not isinstance(value, bool):
        return "pr_required must be boolean"
    if field == "existing_next_action" and (not isinstance(value, str) or not value.strip()):
        return "existing_next_action is required"
    return None


def ordered_requirements(state: dict) -> list[dict]:
    a = state["answers"]
    requirements = [
        question(
            "Q_ENTRY_ACTION",
            "entry_action",
            "Quel est le scénario principal de cette demande ?",
            choices=ENTRY_ACTIONS,
        ),
        question(
            "Q_CONNECTION_INTENT",
            "connection_intent",
            "Quelle est l'intention immédiate de l'agent pour cette demande ?",
            choices=CONNECTION_INTENTS,
        ),
        question(
            "Q_OBJECTIVE",
            "objective",
            "Décris l'objectif exact à atteindre, sans supposer l'état actuel du repository cible.",
        ),
    ]
    action = a.get("entry_action")

    if action == "CREATE_NEW_REPOSITORY":
        requirements.extend([
            question("Q_TARGET_SCOPE", "target_scope", "Où le nouveau repository doit-il être créé ?", choices=OWNER_SCOPES),
            question("Q_TARGET_OWNER", "target_owner", "Quel est le propriétaire GitHub cible exact (organisation ou compte) ?"),
            question("Q_REPOSITORY_NAME", "repository_name", "Quel est le nom exact du nouveau repository ?"),
            question("Q_VISIBILITY", "visibility", "Quelle visibilité doit avoir le repository ?", choices=["private", "public", "internal"]),
            question("Q_PROJECT_TYPE", "project_type", "Quel type de projet doit être initialisé ?"),
            question("Q_PROJECT_PROFILE", "project_profile", "Quel profil technique doit être sélectionné ou utilisé comme point de départ ?", choices=PROJECT_PROFILES),
            question("Q_INFRASTRUCTURE", "infrastructure_preference", "Quel est l'état attendu de l'infrastructure à la création ?", choices=["DISCOVER_AFTER_CREATION","NO_SERVER_REQUIRED_YET","KNOWN_TARGET_TO_VERIFY"]),
            question("Q_CREATE_AUTHORITY", "creation_authority", "L'autorité explicite de créer ce repository dans ce scope est-elle confirmée ?", choices=[True, False], response_type="boolean"),
        ])
    elif action == "ADOPT_EXISTING_REPOSITORY":
        target = a.get("target_repository")
        requirements.extend([
            question("Q_TARGET_REPOSITORY", "target_repository", "Quel repository existant doit être adopté ?"),
            agent_request(
                "R_TARGET_OBSERVATION",
                "target_observation",
                f"Observe le repository cible {target or '<à résoudre>'} via GitHub avant toute écriture.",
                {
                    "exists": True,
                    "default_branch": "<branch>",
                    "head_sha": "<40-hex-sha>",
                    "governance_detected": "<boolean>",
                    "workflows_detected": "<integer-or-null>",
                    "notes": "<optional>",
                },
            ),
            question("Q_ADOPTION_STRATEGY", "integration_strategy", "Où l'adoption additive devra-t-elle être appliquée ?", choices=["DIRECT_CANONICAL_IF_AUTHORIZED","EXISTING_BRANCH","LAB_BRANCH"]),
            question("Q_ADOPTION_AUTHORITY", "adoption_authority", "L'autorité d'appliquer l'adoption additive après validation du plan est-elle confirmée ?", choices=[True, False], response_type="boolean"),
        ])
    elif action == "MAP_EXISTING_PROJECT":
        target = a.get("target_repository")
        requirements.extend([
            question("Q_TARGET_REPOSITORY", "target_repository", "Quel repository existant doit être cartographié ?"),
            agent_request(
                "R_TARGET_OBSERVATION",
                "target_observation",
                f"Observe le repository cible {target or '<à résoudre>'} via GitHub en lecture seule.",
                {
                    "exists": True,
                    "default_branch": "<branch>",
                    "head_sha": "<40-hex-sha>",
                    "governance_detected": "<boolean>",
                    "notes": "<optional>",
                },
            ),
            question("Q_MAPPING_SCOPE", "mapping_scope", "Quel niveau de cartographie est demandé ?", choices=["CURRENT_ONLY","CURRENT_AND_TARGET"]),
            question("Q_TARGET_ARCHITECTURE", "target_architecture_requested", "Une architecture cible doit-elle être proposée en plus de l'architecture observée ?", choices=[True, False], response_type="boolean"),
            question("Q_MAPPING_WRITE", "mapping_write_authority", "Le control plane peut-il préparer un handoff autorisant l'écriture des artefacts de cartographie dans le repo cible ?", choices=[True, False], response_type="boolean"),
        ])
    elif action == "LAB_EVOLUTION":
        target = a.get("target_repository")
        requirements.extend([
            question("Q_TARGET_REPOSITORY", "target_repository", "Quel repository existant doit évoluer en laboratoire ?"),
            agent_request(
                "R_TARGET_OBSERVATION",
                "target_observation",
                f"Observe le repository cible {target or '<à résoudre>'}, sa branche canonique et son HEAD exact.",
                {
                    "exists": True,
                    "default_branch": "<branch>",
                    "head_sha": "<40-hex-sha>",
                    "governance_detected": "<boolean>",
                    "branch_protection_known": "<boolean-or-null>",
                    "notes": "<optional>",
                },
            ),
            question("Q_LAB_BRANCH", "lab_branch_name", "Quel nom de branche laboratoire doit être utilisé ? Préfixes autorisés : lab/, claude/, experiment/."),
            question("Q_PR_REQUIRED", "pr_required", "Une pull request laboratoire est-elle requise ?", choices=[True, False], response_type="boolean"),
            question("Q_LAB_AUTHORITY", "lab_authority", "L'autorité explicite de créer/utiliser cette branche ou PR laboratoire est-elle confirmée ?", choices=[True, False], response_type="boolean"),
        ])
    elif action == "CONTINUE_GOVERNED_WORK":
        target = a.get("target_repository")
        requirements.extend([
            question("Q_TARGET_REPOSITORY", "target_repository", "Quel repository déjà gouverné doit être repris ?"),
            agent_request(
                "R_TARGET_OBSERVATION",
                "target_observation",
                f"Observe le repository gouverné {target or '<à résoudre>'}, sa branche canonique et son HEAD exact.",
                {
                    "exists": True,
                    "default_branch": "<branch>",
                    "head_sha": "<40-hex-sha>",
                    "governance_detected": True,
                    "next_action": "<observed NEXT_ACTION>",
                    "notes": "<optional>",
                },
            ),
            question("Q_EXISTING_NEXT_ACTION", "existing_next_action", "Quelle NEXT_ACTION ou quel work-item existant doit être repris après réconciliation du HEAD ?"),
        ])
    return requirements


def build_plan(state: dict) -> list[dict]:
    a = state["answers"]
    action = a["entry_action"]
    target = None
    if action == "CREATE_NEW_REPOSITORY":
        target = f"{a['target_owner']}/{a['repository_name']}"
        return [
            {
                "id": "PREP-001",
                "name": "CREATE_FROM_GOVERNED_TEMPLATE",
                "mutation_class": "TARGET_REPOSITORY_CREATE",
                "target": target,
                "status": "PENDING",
                "instructions": f"Crée {target} depuis {CONTROL_PLANE_REPOSITORY} avec scope {a['target_scope']}, visibilité {a['visibility']} et sans ajout manuel parasite.",
                "required_evidence": {"repository": target, "created": True, "initial_head_sha": "<40-hex-sha>"},
            },
            {
                "id": "PREP-002",
                "name": "VERIFY_ZERO_TOUCH_BOOTSTRAP",
                "mutation_class": "READ_VERIFY",
                "target": target,
                "status": "PENDING",
                "instructions": "Vérifie que le bootstrap zero-touch termine en PASS, que le HEAD distant est le commit d'attestation et que la version de template est celle attendue.",
                "required_evidence": {"bootstrap_success": True, "template_version": "<version>", "final_head_sha": "<40-hex-sha>", "run_id": "<id>"},
            },
            {
                "id": "PREP-003",
                "name": "DISCOVER_INITIAL_INFRASTRUCTURE_STATE",
                "mutation_class": "READ_DISCOVERY",
                "target": target,
                "status": "PENDING",
                "instructions": "Observe ou laisse explicitement non résolus serveur, domaine, répertoire, base et route d'accès MCP/SSH. N'invente aucun fait.",
                "required_evidence": {"server_status": "<status>", "directory_status": "<status>", "database_status": "<status>", "access_status": "<status>"},
            },
            {
                "id": "PREP-004",
                "name": "CAPTURE_TARGET_BASELINE",
                "mutation_class": "READ_VERIFY",
                "target": target,
                "status": "PENDING",
                "instructions": "Capture la branche par défaut et le HEAD exact après bootstrap comme baseline de handoff.",
                "required_evidence": {"default_branch": "<branch>", "head_sha": "<40-hex-sha>"},
            },
        ]

    target = a["target_repository"]
    if action == "ADOPT_EXISTING_REPOSITORY":
        return [
            {
                "id": "PREP-001",
                "name": "RECONFIRM_TARGET_BASELINE",
                "mutation_class": "READ_VERIFY",
                "target": target,
                "status": "PENDING",
                "instructions": "Réobserve le HEAD exact avant de construire le plan d'adoption et confirme qu'il correspond à la baseline approuvée.",
                "required_evidence": {"head_sha": a["target_observation"]["head_sha"], "default_branch": a["target_observation"]["default_branch"]},
            },
            {
                "id": "PREP-002",
                "name": "BUILD_ADOPTION_PLAN",
                "mutation_class": "READ_ANALYSIS",
                "target": target,
                "status": "PENDING",
                "instructions": "Exécute/analyse l'adoption en mode plan. Retourne le nombre ADD/REUSE/PRESERVE_EXISTING et tous les CONFLICT_HOLD_FOR_REVIEW.",
                "required_evidence": {"blocking_conflicts": [], "add_count": "<integer>", "preserve_count": "<integer>", "reuse_count": "<integer>"},
            },
            {
                "id": "PREP-003",
                "name": "APPLY_ADDITIVE_GOVERNANCE",
                "mutation_class": "TARGET_REPOSITORY_WRITE",
                "target": target,
                "status": "PENDING",
                "instructions": f"Applique uniquement le plan accepté selon {a['integration_strategy']}. Aucun fichier existant ne doit être écrasé.",
                "required_evidence": {"existing_files_overwritten": 0, "applied": True, "resulting_head_sha": "<40-hex-sha>"},
            },
            {
                "id": "PREP-004",
                "name": "VALIDATE_ADOPTED_TARGET",
                "mutation_class": "READ_VERIFY",
                "target": target,
                "status": "PENDING",
                "instructions": "Exécute la validation gouvernance et les contrôles projet disponibles. Toute régression bloque le handoff.",
                "required_evidence": {"governance_validation": "PASS", "project_checks": "<PASS-or-documented-baseline>", "head_sha": "<40-hex-sha>"},
            },
        ]

    if action == "MAP_EXISTING_PROJECT":
        steps = [
            {
                "id": "PREP-001",
                "name": "RECONFIRM_TARGET_BASELINE",
                "mutation_class": "READ_VERIFY",
                "target": target,
                "status": "PENDING",
                "instructions": "Réobserve le HEAD exact et la branche canonique avant cartographie.",
                "required_evidence": {"head_sha": a["target_observation"]["head_sha"], "default_branch": a["target_observation"]["default_branch"]},
            },
            {
                "id": "PREP-002",
                "name": "BUILD_CURRENT_ARCHITECTURE_MAP",
                "mutation_class": "READ_ANALYSIS",
                "target": target,
                "status": "PENDING",
                "instructions": "Cartographie l'architecture réellement observée : topologie, runtimes, API, données, jobs, auth, CI/CD, déploiement et gouvernance.",
                "required_evidence": {"current_architecture_ready": True, "unknowns": "<array>", "observed_head_sha": a["target_observation"]["head_sha"]},
            },
        ]
        if a.get("mapping_scope") == "CURRENT_AND_TARGET" or a.get("target_architecture_requested"):
            steps.append({
                "id": "PREP-003",
                "name": "BUILD_TARGET_ARCHITECTURE_AND_GAP",
                "mutation_class": "DESIGN_ANALYSIS",
                "target": target,
                "status": "PENDING",
                "instructions": "Conçois séparément l'architecture cible et le GAP_MAP. Ne transforme aucune cible en fait observé.",
                "required_evidence": {"target_architecture_ready": True, "gap_map_ready": True, "current_ne_target_preserved": True},
            })
        steps.append({
            "id": f"PREP-{len(steps)+1:03d}",
            "name": "PREPARE_MAPPING_HANDOFF",
            "mutation_class": "CONTROL_PLANE_PACKAGE",
            "target": target,
            "status": "PENDING",
            "instructions": "Prépare le paquet de cartographie pour le travail dans le repository cible, sans mutation si l'autorité d'écriture n'est pas accordée.",
            "required_evidence": {"mapping_package_ready": True, "write_authority": bool(a.get("mapping_write_authority"))},
        })
        return steps

    if action == "LAB_EVOLUTION":
        return [
            {
                "id": "PREP-001",
                "name": "RECONFIRM_CANONICAL_BASELINE",
                "mutation_class": "READ_VERIFY",
                "target": target,
                "status": "PENDING",
                "instructions": "Réobserve la branche canonique et son HEAD exact avant création du laboratoire.",
                "required_evidence": {"canonical_branch": a["target_observation"]["default_branch"], "canonical_head_sha": a["target_observation"]["head_sha"]},
            },
            {
                "id": "PREP-002",
                "name": "CAPTURE_LAB_BASELINE",
                "mutation_class": "CONTROL_PLANE_PACKAGE",
                "target": target,
                "status": "PENDING",
                "instructions": "Capture les tests, contraintes, documents d'autorité et risques nécessaires pour comparer le laboratoire à la vérité canonique.",
                "required_evidence": {"baseline_ready": True, "canonical_head_sha": a["target_observation"]["head_sha"], "checks_identified": "<array>"},
            },
            {
                "id": "PREP-003",
                "name": "CREATE_LAB_BRANCH",
                "mutation_class": "TARGET_BRANCH_CREATE",
                "target": target,
                "status": "PENDING",
                "instructions": f"Crée la branche laboratoire {a['lab_branch_name']} depuis le HEAD canonique observé. Ne modifie pas la branche canonique.",
                "required_evidence": {"branch": a["lab_branch_name"], "base_head_sha": a["target_observation"]["head_sha"], "created": True},
            },
            {
                "id": "PREP-004",
                "name": "VERIFY_LAB_ISOLATION",
                "mutation_class": "READ_VERIFY",
                "target": target,
                "status": "PENDING",
                "instructions": "Vérifie que le laboratoire pointe sur la baseline attendue et que la branche canonique n'a pas bougé du fait de la préparation.",
                "required_evidence": {"lab_branch": a["lab_branch_name"], "canonical_unchanged": True, "lab_ready": True},
            },
        ]

    if action == "CONTINUE_GOVERNED_WORK":
        return [
            {
                "id": "PREP-001",
                "name": "RECONFIRM_GOVERNED_TARGET",
                "mutation_class": "READ_VERIFY",
                "target": target,
                "status": "PENDING",
                "instructions": "Réobserve HEAD, NEXT_ACTION, work-items et gouvernance du repository avant reprise.",
                "required_evidence": {"head_sha": a["target_observation"]["head_sha"], "governance_valid": True, "next_action": a["existing_next_action"]},
            }
        ]
    raise ValueError(f"unsupported entry action: {action}")


def target_repository(state: dict) -> str | None:
    a = state["answers"]
    if a.get("entry_action") == "CREATE_NEW_REPOSITORY" and a.get("target_owner") and a.get("repository_name"):
        return f"{a['target_owner']}/{a['repository_name']}"
    return a.get("target_repository")


def authority_denied(state: dict) -> str | None:
    a = state["answers"]
    action = a.get("entry_action")
    if action == "CREATE_NEW_REPOSITORY" and a.get("creation_authority") is False:
        return "repository creation authority denied"
    if action == "ADOPT_EXISTING_REPOSITORY" and a.get("adoption_authority") is False:
        return "adoption authority denied"
    if action == "LAB_EVOLUTION" and a.get("lab_authority") is False:
        return "lab branch/PR authority denied"
    return None


def make_handoff(state: dict) -> dict:
    a = state["answers"]
    target = target_repository(state)
    action = a["entry_action"]
    expected_head = None
    branch = None
    for item in reversed(state["evidence"]):
        ev = item.get("evidence") or {}
        expected_head = ev.get("head_sha") or ev.get("final_head_sha") or ev.get("resulting_head_sha") or expected_head
        branch = ev.get("default_branch") or ev.get("lab_branch") or branch
    if branch is None:
        observation = a.get("target_observation") or {}
        branch = a.get("lab_branch_name") if action == "LAB_EVOLUTION" else observation.get("default_branch")
    if expected_head is None:
        observation = a.get("target_observation") or {}
        expected_head = observation.get("head_sha")

    next_operation = {
        "CREATE_NEW_REPOSITORY": "DISCOVER_PROJECT_BASELINE",
        "ADOPT_EXISTING_REPOSITORY": "CONTINUE_GOVERNED_WORK",
        "MAP_EXISTING_PROJECT": "APPLY_MAPPING_ARTIFACTS_OR_BEGIN_IMPLEMENTATION_IF_AUTHORIZED",
        "LAB_EVOLUTION": "BEGIN_LAB_EVOLUTION",
        "CONTINUE_GOVERNED_WORK": a.get("existing_next_action") or "RESUME_GOVERNED_WORK",
    }[action]

    return {
        "status": "HANDOFF_READY",
        "request_id": state["request_id"],
        "entry_action": action,
        "target_repository": target,
        "target_branch": branch,
        "expected_head_sha": expected_head,
        "allowed_next_operation": next_operation,
        "required_reads": [
            "00_START_HERE.md",
            "GOVERNANCE.md",
            "AGENTS.md",
            "SOURCE_OF_TRUTH.md",
            "NEXT_ACTION.md",
            "STATUS.md",
        ],
        "evidence_summary": copy.deepcopy(state["evidence"]),
        "constraints": [
            "REOBSERVE_HEAD_BEFORE_TARGET_WRITE",
            "NO_AUTHORITY_INFERENCE",
            "ZERO_REGRESSION",
            "PRESERVE_EXISTING_AUTHORITIES",
        ],
    }


def refresh(state: dict) -> dict:
    state["next_request"] = None
    state["handoff"] = state.get("handoff")
    state["hold_reason"] = state.get("hold_reason")

    denied = authority_denied(state)
    if denied:
        state["status"] = "HOLD_FOR_REVIEW"
        state["phase"] = "AUTHORITY"
        state["hold_reason"] = denied
        return state

    for requirement in ordered_requirements(state):
        if requirement["field"] not in state["answers"]:
            state["status"] = "WAITING_FOR_ANSWER"
            state["phase"] = requirement["id"]
            state["next_request"] = requirement
            return state

    if not state["execution_plan"]:
        state["execution_plan"] = build_plan(state)
        state["status"] = "PLAN_READY"
        state["phase"] = "PLAN_APPROVAL"
        state["next_request"] = {
            "kind": "PLAN_APPROVAL",
            "id": "Q_PLAN_APPROVAL",
            "field": "plan_approved",
            "text": "Le plan préparatoire chronologique ci-dessous est-il approuvé pour exécution par l'agent connecté ?",
            "required": True,
            "response_type": "boolean",
            "plan": copy.deepcopy(state["execution_plan"]),
        }
        return state

    if "plan_approved" not in state["answers"]:
        state["status"] = "WAITING_FOR_PLAN_APPROVAL"
        state["phase"] = "PLAN_APPROVAL"
        state["next_request"] = {
            "kind": "PLAN_APPROVAL",
            "id": "Q_PLAN_APPROVAL",
            "field": "plan_approved",
            "text": "Le plan préparatoire chronologique est-il approuvé ?",
            "required": True,
            "response_type": "boolean",
            "plan": copy.deepcopy(state["execution_plan"]),
        }
        return state

    if state["answers"].get("plan_approved") is False:
        state["status"] = "HOLD_FOR_REVIEW"
        state["phase"] = "PLAN_APPROVAL"
        state["hold_reason"] = "execution plan not approved"
        return state

    for action in state["execution_plan"]:
        if action["status"] != "DONE":
            state["status"] = "EXECUTING_PREPARATION"
            state["phase"] = action["id"]
            state["next_request"] = action_request(action)
            return state

    state["status"] = "HANDOFF_READY"
    state["phase"] = "HANDOFF"
    state["handoff"] = make_handoff(state)
    state["next_request"] = {
        "kind": "HANDOFF",
        "id": "HANDOFF_READY",
        "text": "La préparation gouvernée est terminée. L'agent peut maintenant entrer dans le repository cible en respectant le handoff.",
        "handoff": copy.deepcopy(state["handoff"]),
    }
    return state


def apply_answer(state: dict, field: str, value: Any) -> dict:
    state = copy.deepcopy(state)
    if state.get("status") in {"HANDOFF_READY", "CLOSED"}:
        raise ValueError("request is already ready/closed")
    current = state.get("next_request") or {}
    if current.get("field") != field:
        raise ValueError(f"unexpected answer field {field!r}; expected {current.get('field')!r}")
    error = validate_answer(field, value, state)
    if error:
        raise ValueError(error)
    state["answers"][field] = value
    state["revision"] = int(state.get("revision", 0)) + 1
    return refresh(state)


def apply_evidence(state: dict, action_id: str, result: str, evidence: dict) -> dict:
    state = copy.deepcopy(state)
    current = state.get("next_request") or {}
    if current.get("kind") != "ACTION_REQUEST" or current.get("action_id") != action_id:
        raise ValueError(f"unexpected evidence for {action_id!r}")
    if result != "PASS":
        state["status"] = "HOLD_FOR_REVIEW"
        state["phase"] = action_id
        state["hold_reason"] = f"preparatory action {action_id} returned {result}"
        state["evidence"].append({"action_id": action_id, "result": result, "evidence": evidence})
        state["revision"] += 1
        return state

    for action in state["execution_plan"]:
        if action["id"] == action_id:
            action["status"] = "DONE"
            break
    state["evidence"].append({"action_id": action_id, "result": result, "evidence": evidence})
    state["revision"] += 1
    return refresh(state)


def encode_state(state: dict) -> str:
    raw = json.dumps(state, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_state(value: str) -> dict:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return json.loads(base64.urlsafe_b64decode((value + padding).encode("ascii")).decode("utf-8"))


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    p = argparse.ArgumentParser(description="Governed Repository central control-plane state machine.")
    sub = p.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start")
    start.add_argument("--request-id", required=True)
    start.add_argument("--agent")
    start.add_argument("--provider")
    start.add_argument("--initial-context")

    answer = sub.add_parser("answer")
    answer.add_argument("--state-file", required=True)
    answer.add_argument("--field", required=True)
    answer.add_argument("--value-json", required=True)

    evidence = sub.add_parser("evidence")
    evidence.add_argument("--state-file", required=True)
    evidence.add_argument("--action-id", required=True)
    evidence.add_argument("--result", required=True)
    evidence.add_argument("--evidence-json", required=True)

    render = sub.add_parser("render")
    render.add_argument("--state-file", required=True)

    args = p.parse_args()

    if args.command == "start":
        state = new_request(args.request_id, args.agent, args.provider, args.initial_context)
    elif args.command == "answer":
        state = load_json(args.state_file)
        state = apply_answer(state, args.field, json.loads(args.value_json))
    elif args.command == "evidence":
        state = load_json(args.state_file)
        state = apply_evidence(state, args.action_id, args.result, json.loads(args.evidence_json))
    else:
        state = refresh(load_json(args.state_file))

    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
