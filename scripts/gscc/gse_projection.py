from __future__ import annotations

from copy import deepcopy
from typing import Any

try:
    from scripts.gse.session_state_engine import new_session_twin, reduce_event
except ModuleNotFoundError:
    from gse.session_state_engine import new_session_twin, reduce_event

GSCC_GSE_PROJECTION_SCHEMA="gscc-gse-session-projection/v1"

def build_session_event(
    *,
    identity_id:str,
    event_type:str,
    observed_at:str,
    repository:str|None=None,
    branch:str|None=None,
    observed_head:str|None=None,
    task_id:str|None=None,
    claim_id:str|None=None,
    last_action:str|None=None,
    checkpoint:Any=None,
    next_action:str|None=None,
    event_id:str|None=None,
)->dict[str,Any]:
    if event_type not in {"SESSION_ATTACH","SESSION_RESUME"}:
        raise ValueError("GSCC GSE session projection requires SESSION_ATTACH or SESSION_RESUME")
    if not identity_id:
        raise ValueError("logical GSCC identity required")
    if not observed_at:
        raise ValueError("observed_at required")
    payload={"session_identity":identity_id}
    for key,value in {
        "repository":repository,
        "branch":branch,
        "observed_head":observed_head,
        "task":task_id,
        "claim":claim_id,
        "last_action":last_action,
        "checkpoint":checkpoint,
        "next_action":next_action,
    }.items():
        if value not in (None,"","UNAVAILABLE"):
            payload[key]=deepcopy(value)
    return {
        "event_id":event_id or f"gscc:{identity_id}:{event_type}:{observed_at}",
        "event_type":event_type,
        "observed_at":observed_at,
        "payload":payload,
    }

def apply_session_event(
    previous_twin:dict[str,Any]|None,
    *,
    identity_id:str,
    event_type:str,
    observed_at:str,
    repository:str|None=None,
    branch:str|None=None,
    observed_head:str|None=None,
    task_id:str|None=None,
    claim_id:str|None=None,
    last_action:str|None=None,
    checkpoint:Any=None,
    next_action:str|None=None,
    event_id:str|None=None,
)->dict[str,Any]:
    event=build_session_event(
        identity_id=identity_id,
        event_type=event_type,
        observed_at=observed_at,
        repository=repository,
        branch=branch,
        observed_head=observed_head,
        task_id=task_id,
        claim_id=claim_id,
        last_action=last_action,
        checkpoint=checkpoint,
        next_action=next_action,
        event_id=event_id,
    )
    twin=previous_twin or new_session_twin(identity_id)
    projected=reduce_event(twin,event,reference_time=observed_at)
    return {
        "schema":GSCC_GSE_PROJECTION_SCHEMA,
        "identity_id":identity_id,
        "event":event,
        "session_twin":projected,
        "gacr_required":False,
        "authority_granted":False,
    }
