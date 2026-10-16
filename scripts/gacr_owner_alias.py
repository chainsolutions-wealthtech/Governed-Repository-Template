#!/usr/bin/env python3
"""Source GACR: audited OWNER_ASSIGNED alias on an existing canonical session.

Names do not attach conversations, mint identities, declare presence, grant roles
or lease/mutation authority. No additional registry is created.
"""
from __future__ import annotations

import copy
import re
from typing import Any

ALIAS = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{1,63}$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
OWNER = "Wealthtechinnovations"
CANONICAL_REPO = "chainsolutions-wealthtech/Governed-Repository-Template"


def assign_owner_alias(
    state: dict[str, Any],
    sessions: dict[str, Any],
    *,
    actor: str,
    association: str,
    continuity_id: str,
    coordination_issue: int,
    session_id: str,
    logical_agent_id: str,
    connection_ref: str,
    short_alias: str,
    observed_head: str,
    current_head: str,
    evidence_ref: str,
    arrival_issue: int,
    timestamp: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if actor != OWNER or association not in {"OWNER", "MEMBER", "COLLABORATOR"}:
        raise ValueError("OWNER_ALIAS_AUTHENTICATED_OWNER_REQUIRED")
    if not isinstance(short_alias, str) or not ALIAS.fullmatch(short_alias):
        raise ValueError("OWNER_ALIAS_FORMAT_INVALID")
    name = short_alias.upper()
    if (not isinstance(observed_head, str) or not SHA40.fullmatch(observed_head)
            or current_head != observed_head):
        raise ValueError("OWNER_ALIAS_HEAD_MOVED")
    if not isinstance(arrival_issue, int) or arrival_issue < 1:
        raise ValueError("OWNER_ALIAS_ARRIVAL_ISSUE_REQUIRED")
    if (not isinstance(evidence_ref, str)
            or not re.fullmatch(r"github-issue-comment:[1-9][0-9]*", evidence_ref)):
        raise ValueError("OWNER_ALIAS_GITHUB_EVIDENCE_REQUIRED")
    matching_sessions = [
        s for s in sessions.get("sessions", [])
        if s.get("session_id") == session_id
    ]
    if len(matching_sessions) != 1:
        raise ValueError("OWNER_ALIAS_EXACT_CANONICAL_SESSION_REQUIRED")
    session = matching_sessions[0]
    if (session.get("repository") != CANONICAL_REPO
            or (session.get("logical_agent_id") or session.get("agent_identity")) != logical_agent_id
            or session.get("connection_ref") != connection_ref
            or session.get("status") == "CLOSED"):
        raise ValueError("OWNER_ALIAS_SESSION_IDENTITY_MISMATCH")
    continuity = next(
        (x for x in state.get("items", []) if x.get("continuity_id") == continuity_id),
        None,
    )
    if (not continuity or continuity.get("repository") != CANONICAL_REPO
            or continuity.get("coordination_issue") != coordination_issue):
        raise ValueError("OWNER_ALIAS_CONTINUITY_NOT_FOUND")
    # Global ambiguity prevention: owner aliases must identify one logical ID
    # even across distinct continuities.
    for item in state.get("items", []):
        for record in item.get("logical_agents") or []:
            existing_name = record.get("human_alias")
            existing_id = record.get("logical_agent_id")
            if existing_name and str(existing_name).upper() == name:
                if existing_id != logical_agent_id:
                    raise ValueError("OWNER_ALIAS_COLLISION_OTHER_LOGICAL_AGENT")
                if record.get("human_alias_provenance") != "OWNER_ASSIGNED":
                    raise ValueError("OWNER_ALIAS_UNTRUSTED_EXISTING_PROVENANCE")
            if existing_id == logical_agent_id and existing_name:
                if str(existing_name).upper() != name:
                    raise ValueError("OWNER_ALIAS_EXISTING_NAME_CONFLICT")

    own = next(
        (g for g in continuity.get("logical_agents", []) if g.get("logical_agent_id") == logical_agent_id),
        None,
    )
    if own and own.get("human_alias") == name and own.get("human_alias_provenance") == "OWNER_ASSIGNED":
        return state, {
            "status": "OWNER_ALIAS_ALREADY_ASSIGNED", "alias": name,
            "session_id": session_id, "logical_agent_id": logical_agent_id,
            "grants_claim": False, "grants_write": False,
        }

    result = copy.deepcopy(state)
    item = next(x for x in result["items"] if x["continuity_id"] == continuity_id)
    group = next(
        (g for g in item.get("logical_agents", []) if g.get("logical_agent_id") == logical_agent_id),
        None,
    )
    if group is None:
        group = {
            "logical_agent_id": logical_agent_id,
            "logical_agent_id_provenance": "CANONICAL_GACR_SESSION_AGENT_IDENTITY",
            "projection_only": True,
            "grants_task_authority": False,
            "grants_claim": False,
            "grants_mutation_authority": False,
        }
        item.setdefault("logical_agents", []).append(group)
    group["human_alias"] = name
    group["human_alias_provenance"] = "OWNER_ASSIGNED"
    group["alias_evidence_ref"] = evidence_ref
    group["routing_evidence_ref"] = evidence_ref
    group["reference_session_ids"] = sorted(
        set(group.get("reference_session_ids") or []) | {session_id}
    )
    journal = {
        "event": "OWNER_ALIAS_ASSIGNED",
        "alias": name, "owner_actor": actor,
        "logical_agent_id": logical_agent_id,
        "canonical_session_id": session_id,
        "arrival_issue": arrival_issue,
        "connection_ref": connection_ref,
        "observed_head": observed_head,
        "evidence_ref": evidence_ref,
        "observed_at": timestamp,
        "grants_role": False,
        "grants_claim": False,
        "grants_write": False,
        "creates_session": False,
    }
    item.setdefault("owner_alias_history", []).append(journal)
    item["updated_at"] = timestamp
    result["revision"] = int(result.get("revision", 0)) + 1
    return result, {
        "status": "OWNER_ALIAS_ASSIGNED",
        "alias": name,
        "logical_agent_id": logical_agent_id,
        "session_id": session_id,
        "continuity_id": continuity_id,
        "history_ref": evidence_ref,
        "state_revision": result["revision"],
        "grants_role": False,
        "grants_claim": False,
        "grants_write": False,
    }
