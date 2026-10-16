#!/usr/bin/env python3
"""Owner-authenticated role intent in existing GACR continuity, not permission."""
from __future__ import annotations
import copy
import re

from gacr_owner_alias import OWNER, CANONICAL_REPO, SHA40

ALLOWED_ROLES={"CODE_AGENT","SUPERVISOR","INTAKER","REVIEWER"}
WORK_ITEMS=("GR-000302/PREP-003","GR-000302/PREP-004")


def assign_owner_role(
    state, sessions, *, actor, association, continuity_id, coordination_issue,
    session_id, logical_agent_id, connection_ref, agent_role, work_items,
    observed_head, current_head, evidence_ref, timestamp,
):
    if actor!=OWNER or association not in {"OWNER","MEMBER","COLLABORATOR"}:
        raise ValueError("OWNER_ROLE_AUTHENTICATION_REQUIRED")
    if agent_role not in ALLOWED_ROLES:
        raise ValueError("OWNER_ROLE_UNSUPPORTED")
    if not isinstance(work_items,list) or work_items!=list(WORK_ITEMS):
        raise ValueError("OWNER_ROLE_EXACT_WORK_SCOPE_REQUIRED")
    if not isinstance(observed_head,str) or not SHA40.fullmatch(observed_head) or observed_head!=current_head:
        raise ValueError("OWNER_ROLE_HEAD_MOVED")
    if not isinstance(evidence_ref,str) or not re.fullmatch(r"github-issue-comment:[1-9][0-9]*",evidence_ref):
        raise ValueError("OWNER_ROLE_GITHUB_EVIDENCE_REQUIRED")
    found=[s for s in sessions.get("sessions",[]) if s.get("session_id")==session_id]
    if len(found)!=1:
        raise ValueError("OWNER_ROLE_SESSION_MISSING")
    sess=found[0]
    if (sess.get("repository")!=CANONICAL_REPO
        or (sess.get("logical_agent_id") or sess.get("agent_identity"))!=logical_agent_id
        or sess.get("connection_ref")!=connection_ref
        or sess.get("status")=="CLOSED"):
        raise ValueError("OWNER_ROLE_CANONICAL_BINDING_MISMATCH")
    cont=next((x for x in state.get("items",[]) if x.get("continuity_id")==continuity_id),None)
    if not cont or cont.get("repository")!=CANONICAL_REPO or cont.get("coordination_issue")!=coordination_issue:
        raise ValueError("OWNER_ROLE_CONTINUITY_MISMATCH")
    targets=[g for g in cont.get("logical_agents",[]) if g.get("logical_agent_id")==logical_agent_id]
    if len(targets)!=1 or targets[0].get("human_alias")!="NOVA" or targets[0].get("human_alias_provenance")!="OWNER_ASSIGNED" or session_id not in (targets[0].get("reference_session_ids") or []):
        raise ValueError("OWNER_ROLE_OWNER_ALIAS_REQUIRED")
    current=targets[0]
    if current.get("owner_assigned_role"):
        if current["owner_assigned_role"]==agent_role and current.get("owner_work_items")==work_items:
            return state,{"status":"OWNER_ROLE_ALREADY_ASSIGNED","agent_role":agent_role,"grants_claim":False,"grants_write":False}
        raise ValueError("OWNER_ROLE_CONFLICTING_PREVIOUS_ASSIGNMENT")
    updated=copy.deepcopy(state)
    item=next(x for x in updated["items"] if x["continuity_id"]==continuity_id)
    logical=next(x for x in item["logical_agents"] if x["logical_agent_id"]==logical_agent_id)
    logical.update({
        "owner_assigned_role":agent_role,
        "owner_role_provenance":"OWNER_ASSIGNED",
        "owner_role_evidence_ref":evidence_ref,
        "owner_work_items":list(work_items),
    })
    item.setdefault("owner_role_history",[]).append({
        "event":"OWNER_ROLE_ASSIGNED",
        "logical_agent_id":logical_agent_id,
        "session_id":session_id,
        "owner_actor":actor,
        "agent_role":agent_role,
        "work_items":list(work_items),
        "evidence_ref":evidence_ref,
        "observed_head":observed_head,
        "at":timestamp,
        "grants_claim":False,
        "grants_lease":False,
        "grants_write":False,
        "emits_availability":False,
    })
    item["updated_at"]=timestamp
    updated["revision"]=int(updated.get("revision",0))+1
    return updated,{
        "status":"OWNER_ROLE_ASSIGNED",
        "agent_role":agent_role,
        "owner_work_items":list(work_items),
        "session_id":session_id,
        "logical_agent_id":logical_agent_id,
        "alias":"NOVA",
        "grants_claim":False,"grants_write":False,"grants_lease":False,
    }
