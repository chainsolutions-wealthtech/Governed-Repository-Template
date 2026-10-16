#!/usr/bin/env python3
"""Reconcile a stale, unapproved LAB creation plan with a pre-existing merged LAB.

This re-planning is strictly read-only. It neither creates branches nor approves
plans, F1 access, GACR identities, claims, leases or merge authority.
"""
from __future__ import annotations

import copy
import re
from typing import Any

from governed_request import SHA40, refresh

EXPECTED_REPO = "chainsolutions-wealthtech/Governed-Repository-Template"
EXPECTED_GR = "GR-000284"
EXPECTED_BRANCH = "lab/codeagent-gscc-f1-q12-renewal-284"
OWNER = "Wealthtechinnovations"
EXPECTED_PREP = (
    ("PREP-001", "RECONFIRM_CANONICAL_BASELINE"),
    ("PREP-002", "CAPTURE_LAB_BASELINE"),
    ("PREP-003", "CREATE_LAB_BRANCH"),
    ("PREP-004", "VERIFY_LAB_ISOLATION"),
)
ALLOWED_ASSOCIATIONS = frozenset(("OWNER", "MEMBER", "COLLABORATOR"))


def reconcile_existing_merged_lab(
    state: dict[str, Any],
    *,
    expected_revision: int,
    expected_main_head: str,
    live_main_head: str,
    owner_actor: str,
    author_association: str,
    branch_head: str,
    merged_pr: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    if (owner_actor != OWNER or author_association not in ALLOWED_ASSOCIATIONS):
        raise ValueError("LAB_PLAN_RECONCILE_OWNER_REQUIRED")
    if (not isinstance(expected_revision, int) or isinstance(expected_revision, bool)
            or expected_revision != state.get("revision")):
        raise ValueError("LAB_PLAN_RECONCILE_REVISION_DRIFT")
    for v in (expected_main_head, live_main_head, branch_head):
        if not isinstance(v, str) or not SHA40.fullmatch(v):
            raise ValueError("LAB_PLAN_RECONCILE_SHA_INVALID")
    if live_main_head != expected_main_head:
        raise ValueError("LAB_PLAN_RECONCILE_MAIN_HEAD_MOVED")
    if not isinstance(reason, str) or not (15 <= len(reason.strip()) <= 1000):
        raise ValueError("LAB_PLAN_RECONCILE_REASON_REQUIRED")
    answers = state.get("answers") or {}
    if (state.get("request_id") != EXPECTED_GR
            or answers.get("target_repository") != EXPECTED_REPO
            or answers.get("entry_action") != "LAB_EVOLUTION"
            or answers.get("lab_authority") is not True
            or answers.get("pr_required") is not True
            or answers.get("lab_branch_name") != EXPECTED_BRANCH
            or not state.get("hold_review_history")
            or not (state.get("hold_review_pending") or {}).get("no_write_grant")
            or state.get("status") != (
                "WAITING_FOR_PLAN_APPROVAL" if state.get("plan_reconciliation_history")
                else "PLAN_READY"
            )
            or state.get("phase") != "PLAN_APPROVAL"
            or (state.get("next_request") or {}).get("field") != "plan_approved"
            or "plan_approved" in answers
            or state.get("evidence")
            or state.get("handoff")):
        raise ValueError("LAB_PLAN_RECONCILE_UNAPPROVED_ORIGINAL_GR_REQUIRED")

    before = state.get("execution_plan")
    first_reconcile = not (state.get("plan_reconciliation_history") or [])
    if first_reconcile and (
        not isinstance(before, list) or len(before) != 4
        or any(
            not isinstance(item, dict)
            or (item.get("id"), item.get("name")) != expected
            or item.get("status") != "PENDING"
            for item, expected in zip(before, EXPECTED_PREP)
        )
    ):
        raise ValueError("LAB_PLAN_RECONCILE_OLD_CREATE_PLAN_REQUIRED")
    if not first_reconcile and (
        any(item.get("status") != "PENDING" for item in (before or []))
        or any(item.get("mutation_class") not in {"READ_VERIFY", "CONTROL_PLANE_PACKAGE"} for item in (before or []))
    ):
        raise ValueError("LAB_PLAN_RECONCILE_NO_PARTIAL_EXECUTION_ALLOWED")

    observation = answers.get("target_observation") or {}
    if (observation.get("exists") is not True
            or observation.get("default_branch") != "main"
            or not SHA40.fullmatch(str(observation.get("head_sha") or ""))):
        raise ValueError("LAB_PLAN_RECONCILE_CANONICAL_BASELINE_REQUIRED")
    if not isinstance(merged_pr, dict):
        raise ValueError("LAB_PLAN_RECONCILE_MERGED_PR_REQUIRED")
    pr_sha = merged_pr.get("merge_commit_sha")
    if (merged_pr.get("number") != 316
            or not merged_pr.get("merged_at")
            or (merged_pr.get("base") or {}).get("ref") != "main"
            or (merged_pr.get("head") or {}).get("ref") != EXPECTED_BRANCH
            or not isinstance(pr_sha, str) or not SHA40.fullmatch(pr_sha)):
        raise ValueError("LAB_PLAN_RECONCILE_PR316_PROVENANCE_REQUIRED")

    target = EXPECTED_REPO
    fresh = [
        {
            "id": "PREP-001", "name": "RECONFIRM_CANONICAL_BASELINE",
            "mutation_class": "READ_VERIFY", "target": target,
            "status": "PENDING",
            "instructions": "Observe le HEAD de main et vérifie les droits sans mutation.",
            "required_evidence": {"canonical_branch": "main", "canonical_head_sha": live_main_head},
        },
        {
            "id": "PREP-002", "name": "VERIFY_PRIOR_MERGED_PR",
            "mutation_class": "READ_VERIFY", "target": target,
            "status": "PENDING",
            "instructions": "Relis PR #316 fusionnée ; préserve l'historique sans reconstruire le LAB.",
            "required_evidence": {
                "prior_pr": 316, "merged": True, "merge_commit_sha": pr_sha,
            },
        },
        {
            "id": "PREP-003", "name": "REUSE_VERIFY_EXISTING_LAB_BRANCH",
            "mutation_class": "READ_VERIFY", "target": target,
            "status": "PENDING",
            "instructions": "Vérifie la branche historique existante ; ne la recrée ni ne la modifie.",
            "required_evidence": {
                "branch": EXPECTED_BRANCH, "branch_head_sha": branch_head,
                "existed_before_plan": True, "created_in_this_plan": False,
            },
        },
        {
            "id": "PREP-004", "name": "AUDIT_HISTORICAL_LAB_NO_NEW_WRITE",
            "mutation_class": "CONTROL_PLANE_PACKAGE", "target": target,
            "status": "PENDING",
            "instructions": "Atteste la corrélation branche/PR et le périmètre historique, sans nouveau LAB.",
            "required_evidence": {
                "prior_pr": 316, "prior_pr_merged": True,
                "branch": EXPECTED_BRANCH, "branch_head_sha": branch_head,
                "no_new_lab_created": True, "no_mutation_claimed": True,
            },
        },
    ]
    result = copy.deepcopy(state)
    result["revision"] = int(state["revision"]) + 1
    result["execution_plan"] = fresh
    result["next_request"] = None
    result["handoff"] = None
    result.setdefault("plan_reconciliation_history", []).append({
        "id": f"GR284-PLAN-RECONCILE-{result['revision']:06d}",
        "revision_before": state["revision"], "revision_after": result["revision"],
        "reason": reason.strip(),
        "owner_actor": owner_actor, "owner_association": author_association,
        "main_head_verified": live_main_head,
        "historical_branch": EXPECTED_BRANCH, "historical_branch_head": branch_head,
        "merged_pr": 316, "merged_pr_commit": pr_sha,
        "superseded_plan": copy.deepcopy(before),
        "revised_plan": copy.deepcopy(fresh),
        "requires_new_plan_approval": True,
        "grants_claim": False, "grants_write": False,
        "grants_merge_authority": False, "creates_lab": False,
    })
    result["plan_reconciliation_pending"] = {
        "prior_branch_audit_only": True,
        "new_owner_plan_approval_required": True,
        "no_mutation_authority": True,
        "merged_pr": 316,
    }
    result = refresh(result)
    if (result["status"] != "WAITING_FOR_PLAN_APPROVAL"
            or result["next_request"].get("field") != "plan_approved"):
        raise ValueError("LAB_PLAN_RECONCILE_PLAN_REAPPROVAL_REQUIRED")
    return result
