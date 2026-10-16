#!/usr/bin/env python3
"""Versioned, fail-closed re-examination of one authority HOLD on the SAME governed request.

This does NOT grant LAB execution, claim, lease, merge rights or F1 RELEASE. It only
reopens the exact owner-authority question after fresh target-baseline reobservation.
"""
from __future__ import annotations

import copy
import re
from typing import Any

from governed_request import SHA40, refresh

OWNER_ACTOR = "Wealthtechinnovations"
ALLOWED_ASSOCIATIONS = frozenset({"OWNER", "MEMBER", "COLLABORATOR"})
MERGED_PR_REF = re.compile(r"^github-pr:([1-9][0-9]{0,7})$")


def reexamine_authority_hold(
    state: dict[str, Any],
    *,
    expected_revision: int,
    expected_head: str,
    observed_head: str,
    owner_actor: str,
    author_association: str,
    evidence_refs: list[str],
    reason: str,
) -> dict[str, Any]:
    """Reopen target HEAD observation, then request a NEW explicit LAB authority answer.

    The caller MUST verify the authenticated GitHub actor and merged PR evidence,
    using fresh GitHub API reads (see control_plane_issue_bridge.py).
    """
    if owner_actor != OWNER_ACTOR or author_association not in ALLOWED_ASSOCIATIONS:
        raise ValueError("HOLD_REVIEW_OWNER_AUTHENTICATION_REQUIRED")
    if (not isinstance(expected_revision, int) or isinstance(expected_revision, bool)
            or expected_revision < 1
            or expected_revision != state.get("revision")):
        raise ValueError("HOLD_REVIEW_STALE_REVISION")
    if not isinstance(expected_head, str) or not SHA40.fullmatch(expected_head):
        raise ValueError("HOLD_REVIEW_EXPECTED_HEAD_INVALID")
    if observed_head != expected_head:
        raise ValueError("HOLD_REVIEW_HEAD_MOVED")
    if not isinstance(reason, str) or not (15 <= len(reason.strip()) <= 1000):
        raise ValueError("HOLD_REVIEW_REASON_REQUIRED")
    if (not isinstance(evidence_refs, list)
            or not (1 <= len(evidence_refs) <= 8)
            or not all(isinstance(v, str) and MERGED_PR_REF.fullmatch(v) for v in evidence_refs)
            or len(set(evidence_refs)) != len(evidence_refs)):
        raise ValueError("HOLD_REVIEW_MERGED_PR_REFERENCES_REQUIRED")

    answers = state.get("answers") or {}
    if (state.get("status") != "HOLD_FOR_REVIEW"
            or state.get("phase") != "AUTHORITY"
            or state.get("hold_reason") != "lab branch/PR authority denied"
            or answers.get("entry_action") != "LAB_EVOLUTION"
            or answers.get("lab_authority") is not False
            or state.get("next_request") is not None
            or state.get("execution_plan")
            or state.get("evidence")
            or "plan_approved" in answers):
        raise ValueError("HOLD_REVIEW_AUTHORITY_ONLY_NO_PRIOR_EXECUTION")

    old_revision = state["revision"]
    new_state = copy.deepcopy(state)
    old_observation = copy.deepcopy(new_state["answers"].get("target_observation"))
    previous_hold = {
        "status": new_state["status"],
        "phase": new_state["phase"],
        "hold_reason": new_state["hold_reason"],
        "authority_answer": False,
        "target_observation": old_observation,
    }
    # No authority can be inherited from a HOLD. Invalidate only dependencies:
    # stale repo baseline and denied authority; preserve objective, branch and
    # all identity/continuity and original request references verbatim.
    new_state["answers"].pop("target_observation", None)
    new_state["answers"].pop("lab_authority", None)
    new_state["hold_reason"] = None
    new_state["handoff"] = None
    new_state["revision"] = old_revision + 1
    item = {
        "id": f"HOLD-REVIEW-{old_revision + 1:06d}",
        "request_id": state["request_id"],
        "revision_before": old_revision,
        "revision_after": old_revision + 1,
        "decision": "REOPEN_BASELINE_AND_OWNER_AUTHORITY_QUESTION",
        "previous": previous_hold,
        "owner_actor": owner_actor,
        "author_association": author_association,
        "verified_head": observed_head,
        "evidence_refs": list(evidence_refs),
        "reason": reason.strip(),
        "grants_lab_authority": False,
        "grants_mutation_authority": False,
        "grants_claim": False,
        "grants_merge_authority": False,
    }
    new_state.setdefault("hold_review_history", []).append(item)
    new_state["hold_review_pending"] = {
        "review_id": item["id"],
        "owner_authority_answer_required": True,
        "fresh_target_observation_required": True,
        "no_write_grant": True,
    }
    new_state = refresh(new_state)
    if (new_state["status"] != "WAITING_FOR_ANSWER"
            or (new_state.get("next_request") or {}).get("field") != "target_observation"):
        raise ValueError("HOLD_REVIEW_DID_NOT_REQUIRE_FRESH_BASELINE")
    return new_state
