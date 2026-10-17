#!/usr/bin/env python3
"""Fail-closed, versioned rebaseline of the SAME GR-000302 before LAB creation.

This pure transition never creates a branch, grant, claim, session or WRITE right.
The caller must independently verify GitHub actor/HEAD/branch and control persistence.
"""
from __future__ import annotations

import copy
import re
from typing import Any

REPO = "chainsolutions-wealthtech/Governed-Repository-Template"
BRANCH = "lab/chainflow-live-poc"
REQUEST = "GR-000302"
OWNER = "Wealthtechinnovations"
OLD_HEAD = "e20b172b149a30ec8ece77c828e3c00614078d38"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
ASSOCIATIONS = frozenset({"OWNER", "MEMBER", "COLLABORATOR"})


def reconcile_stale_lab_plan(
    original: dict[str, Any], *, expected_revision: int,
    expected_head: str, observed_head: str, owner_actor: str,
    event_author: str, author_association: str, branch_absent: bool,
    observation_evidence: str, reason: str,
) -> dict[str, Any]:
    """Reopen only GR302/rev12/PREP-003 for fresh owner plan approval.

    Values describing GitHub observations are not credentials; the bridge MUST
    obtain them from authenticated webhook and fresh GitHub REST API calls.
    """
    s = original
    if (owner_actor != OWNER or event_author != OWNER or
            author_association not in ASSOCIATIONS):
        raise ValueError("GR302_OWNER_AUTHENTICATION_REQUIRED")
    if (type(expected_revision) is not int or expected_revision != 12 or
            s.get("revision") != expected_revision):
        raise ValueError("GR302_EXACT_REVISION_REQUIRED")
    if (not isinstance(expected_head, str) or not SHA40.fullmatch(expected_head)
            or observed_head != expected_head):
        raise ValueError("GR302_EXACT_CURRENT_HEAD_REQUIRED")
    if observed_head == OLD_HEAD:
        raise ValueError("GR302_NO_HEAD_CHANGE_TO_RECONCILE")
    if branch_absent is not True:
        raise ValueError("GR302_BRANCH_ABSENCE_REQUIRED")
    if (not isinstance(observation_evidence, str) or not re.fullmatch(
            r"github-(?:api-observation|issue-comment):[A-Za-z0-9_-]{4,100}",
            observation_evidence)):
        raise ValueError("GR302_OBSERVATION_EVIDENCE_REQUIRED")
    if not isinstance(reason, str) or not (15 <= len(reason.strip()) <= 1000):
        raise ValueError("GR302_REASON_REQUIRED")

    a = s.get("answers") or {}
    if (s.get("request_id") != REQUEST or s.get("status") != "EXECUTING_PREPARATION"
            or s.get("phase") != "PREP-003"
            or (s.get("next_request") or {}).get("kind") != "ACTION_REQUEST"
            or (s.get("next_request") or {}).get("action_id") != "PREP-003"
            or a.get("target_repository") != REPO or a.get("entry_action") != "LAB_EVOLUTION"
            or a.get("lab_branch_name") != BRANCH
            or a.get("lab_authority") is not True or a.get("plan_approved") is not True
            or s.get("handoff") is not None
            or s.get("preparation_reconciliation_history")):
        raise ValueError("GR302_EXACT_PENDING_PREP003_REQUIRED")
    p = s.get("execution_plan")
    if (not isinstance(p, list) or len(p) != 4
            or [(x.get("id"), x.get("status")) for x in p] != [
                ("PREP-001", "DONE"), ("PREP-002", "DONE"),
                ("PREP-003", "PENDING"), ("PREP-004", "PENDING")]
            or p[2].get("name") != "CREATE_LAB_BRANCH"
            or p[2].get("required_evidence", {}).get("base_head_sha") != OLD_HEAD
            or p[2].get("required_evidence", {}).get("branch") != BRANCH):
        raise ValueError("GR302_ORIGINAL_PLAN_MISMATCH")
    proofs = s.get("evidence") or []
    if (not isinstance(proofs, list) or
            [x.get("action_id") for x in proofs] != ["PREP-001", "PREP-002"] or
            any(x.get("result") != "PASS" for x in proofs)):
        raise ValueError("GR302_HISTORICAL_EVIDENCE_REQUIRED")

    result = copy.deepcopy(s)
    previous_plan = copy.deepcopy(result["execution_plan"])
    previous_answer = copy.deepcopy(result["answers"].get("target_observation"))
    check = {
        "id": "PREP-002R",
        "name": "RECONFIRM_LIVE_MAIN_AND_LAB_ABSENCE",
        "target": REPO,
        "status": "PENDING",
        "mutation_class": "READ_VERIFY",
        "instructions": "Freshly verify main HEAD and absent LAB; never create a branch.",
        "required_evidence": {
            "canonical_branch": "main",
            "canonical_head_sha": observed_head,
            "lab_branch": BRANCH,
            "lab_branch_absent": True,
        },
    }
    plan = result["execution_plan"]
    plan.insert(2, check)
    plan[3]["required_evidence"]["base_head_sha"] = observed_head
    result["answers"]["target_observation"] = {
        "exists": True, "default_branch": "main", "head_sha": observed_head,
        "governance_detected": True,
    }
    result["answers"].pop("plan_approved", None)
    result["revision"] += 1
    result["status"] = "WAITING_FOR_PLAN_APPROVAL"
    result["phase"] = "PLAN_APPROVAL"
    result["handoff"] = None
    result["hold_reason"] = None
    result["next_request"] = {
        "kind": "PLAN_APPROVAL", "id": "Q_GR302_RECONCILIATION_APPROVAL",
        "field": "plan_approved", "required": True, "response_type": "boolean",
        "text": "Approuver le plan GR302 réconcilié (PREP-002R et HEAD courant) ? Aucun droit WRITE accordé.",
        "plan": copy.deepcopy(plan),
    }
    item = {
        "id": f"GR302-PREP-RECONCILE-{result['revision']:06d}",
        "revision_before": expected_revision,
        "revision_after": result["revision"],
        "old_observation": previous_answer,
        "old_plan": previous_plan,
        "historical_evidence_preserved": copy.deepcopy(proofs),
        "observed_new_head": observed_head,
        "verified_lab_branch_absent": True,
        "observation_evidence": observation_evidence,
        "owner_actor": owner_actor,
        "owner_association": author_association,
        "reason": reason.strip(),
        "requires_new_owner_plan_approval": True,
        "grants_claim": False, "grants_write": False, "grants_lease": False,
        "creates_lab": False, "grants_merge_authority": False,
    }
    result.setdefault("preparation_reconciliation_history", []).append(item)
    result["gr302_reconciliation_pending"] = {
        "review_id": item["id"],
        "owner_plan_approval_required": True,
        "live_head_and_branch_recheck_required": True,
        "no_mutation_authority": True,
    }
    return result
