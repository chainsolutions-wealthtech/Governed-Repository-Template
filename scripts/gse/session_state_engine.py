#!/usr/bin/env python3
"""Pure deterministic Governed Session Engine (GSE). No transport or authority."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json

SCHEMA="gse-session-twin/v1"
EVENTS=set("SESSION_ATTACH SESSION_RESUME HEARTBEAT ACTIVITY_STARTED ACTIVITY_COMPLETED ACTIVITY_FAILED TOOL_STARTED TOOL_COMPLETED TOOL_FAILED PROGRESS BLOCKED CHECKPOINT CONTEXT_UPDATE INTERRUPTION CHALLENGE_RESPONSE COMMAND_ACK".split())
DELIVERY=set("CREATED QUEUED DISPATCHED DELIVERED ACKNOWLEDGED EXECUTING COMPLETED FAILED DECLINED EXPIRED CANCELLED NO_RESPONSE UNSUPPORTED".split())
BLOCK_CLASSES=set("WAITING_FOR_CI WAITING_FOR_USER WAITING_FOR_EXTERNAL_DEPENDENCY PERMISSION TOOL_FAILURE REPOSITORY_STATE DEPENDENCY UNKNOWN".split())

@dataclass(frozen=True)
class Policy:
    presence_fresh_seconds:int=900
    liveness_active_seconds:int=300
    liveness_quiet_seconds:int=900
    liveness_lost_seconds:int=1800
    activity_quiet_seconds:int=600
    progress_fresh_seconds:int=900
    control_ack_fresh_seconds:int=900
    control_unreachable_after_no_response:int=2
    suspected_blocked_failure_count:int=3
    history_limit:int=12
    dedupe_limit:int=512

def _dt(v):
    if isinstance(v,datetime): return v.astimezone(timezone.utc)
    if not v: return None
    try:return datetime.fromisoformat(str(v).replace("Z","+00:00")).astimezone(timezone.utc)
    except ValueError:return None

def _iso(v): return _dt(v).replace(microsecond=0).isoformat().replace("+00:00","Z")
def _newer(a,b):
    da,db=_dt(a),_dt(b)
    return _iso(db) if db and (not da or db>da) else a

def _age(now,stamp):
    d=_dt(stamp); return None if not d else max(0,(now-d).total_seconds())
def _hash(v): return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
def _dim(state,prov="UNKNOWN",at=None,**extra): return {"state":state,"provenance":prov,"evidence_at":at,**extra}

def new_session_twin(session_id=None):
    return {"schema":SCHEMA,"engine_version":"1.0.0","session_id":session_id,
      "identity":{"session_identity":session_id,"repository":None,"task":None,"claim":None,"branch":None,"observed_head":None},
      "context":{"last_action":None,"next_action":None,"checkpoint":None,"checkpoint_digest":None},
      "presence":_dim("UNKNOWN"),"liveness":_dim("UNKNOWN"),"activity":_dim("UNKNOWN"),"progress":_dim("UNKNOWN"),
      "blockage":_dim("UNKNOWN",blockage_class="UNKNOWN"),"loop":_dim("UNKNOWN",pattern=None),
      "control_channel":_dim("UNKNOWN",consecutive_no_response=0),"continuity":_dim("UNKNOWN",missing=[]),
      "timestamps":{k:None for k in "first_seen_at last_seen_at last_activity_at last_liveness_evidence_at last_challenge_response_at last_progress_at last_checkpoint_at last_control_ack_at".split()},
      "evidence":{"last_progress_evidence":None,"recent_actions":[],"recent_failures":[],"seen_event_keys":[],"applied_event_count":0,"ignored_duplicate_count":0,"out_of_order_event_count":0,"last_applied_event_at":None,"terminal_at":None},
      "policy":asdict(Policy())}

def normalize_event(event):
    typ=event.get("event_type") or event.get("type")
    if typ not in EVENTS: raise ValueError(f"unsupported GSE event_type: {typ!r}")
    at=_dt(event.get("observed_at") or event.get("timestamp"))
    if not at: raise ValueError("event observed_at must be ISO-8601")
    payload=event.get("payload") or {}
    if not isinstance(payload,dict): raise TypeError("event payload must be a mapping")
    key=("event:"+str(event["event_id"])) if event.get("event_id") else (("message:"+str(event["message_id"])) if event.get("message_id") else "digest:"+_hash([typ,_iso(at),payload]))
    return {"event_type":typ,"observed_at":_iso(at),"payload":deepcopy(payload),"event_key":key}

def _policy(twin,override=None):
    if override:return override
    allowed=Policy.__dataclass_fields__
    return Policy(**{k:v for k,v in (twin.get("policy") or {}).items() if k in allowed})

def _identity(t,p,at):
    aliases={"session_identity":["session_identity","session_id"],"repository":["repository"],"task":["task","task_id"],"claim":["claim","claim_id"],"branch":["branch"],"observed_head":["observed_head","head","HEAD"]}
    for dst,srcs in aliases.items():
        for src in srcs:
            if p.get(src) not in (None,""): t["identity"][dst]=p[src]; break
    t["session_id"]=t["session_id"] or t["identity"].get("session_identity")
    for k in ("last_action","next_action"):
        if p.get(k) is not None:t["context"][k]=p[k]
    if p.get("checkpoint") is not None:
        t["context"]["checkpoint"]=p["checkpoint"]; t["context"]["checkpoint_digest"]=_hash(p["checkpoint"]); t["timestamps"]["last_checkpoint_at"]=_newer(t["timestamps"]["last_checkpoint_at"],at)

def _signature(typ,p):
    sig={"action_type":p.get("action_type") or typ,"tool_name":p.get("tool_name"),"target":p.get("target"),"relevant_input_digest":p.get("relevant_input_digest") or (_hash(p["relevant_input"]) if p.get("relevant_input") is not None else None),"repository":p.get("repository"),"branch":p.get("branch"),"observed_head":p.get("observed_head") or p.get("head") or p.get("HEAD")}
    sig["digest"]=_hash(sig); return sig

def _qualifies(typ,p,t):
    if typ=="PROGRESS":
        if any(p.get(a)!=p.get(b) and p.get(b) is not None for a,b in [("previous_phase","current_phase"),("checkpoint_before","checkpoint_after"),("work_item_before","work_item_after")]) or p.get("completed_step_ref") or p.get("next_step_ref") or p.get("qualifying_progress") is True:return "SEMANTIC_PROGRESS"
    if typ in {"ACTIVITY_COMPLETED","TOOL_COMPLETED"}:
        if p.get("qualifying_progress") is True:return p.get("progress_class") or "ACTION_COMPLETED"
        old=t["identity"].get("observed_head"); new=p.get("written_head") or p.get("observed_head") or p.get("head")
        if old and new and old!=new:return "WRITTEN_HEAD_MOVEMENT"
        for k,c in [("commit_mutation","COMMIT_MUTATION"),("pull_request_mutation","PULL_REQUEST_MUTATION"),("work_item_advanced","WORK_ITEM_ADVANCED"),("checkpoint_advanced","CHECKPOINT_ADVANCED")]:
            if p.get(k):return c
    if typ=="CHECKPOINT" and p.get("checkpoint_advanced"):return "CHECKPOINT_ADVANCED"
    return None

def _pattern(ds):
    if len(ds)>=4 and len(set(ds[-4:]))==1:return "AAAA",4
    if len(ds)>=6 and ds[-6::2]==[ds[-6]]*3 and ds[-5::2]==[ds[-5]]*3 and ds[-6]!=ds[-5]:return "ABABAB",6
    if len(ds)>=9 and ds[-9:-6]==ds[-6:-3]==ds[-3:] and len(set(ds[-3:]))>1:return "ABCABCABC",9
    return None,0

def _derive_loop(t):
    if t["loop"]["state"]=="CONFIRMED_BY_EXPLICIT_SIGNAL":return t["loop"]
    a=t["evidence"]["recent_actions"]; pat,n=_pattern([x["signature"]["digest"] for x in a])
    if not pat:return _dim("NONE","DERIVED",pattern=None)
    w=a[-n:]; heads={x["observed_head"] for x in w if x["observed_head"]}; cps={x["checkpoint_digest"] for x in w if x["checkpoint_digest"]}; lp=_dt(t["timestamps"]["last_progress_at"]); start=_dt(w[0]["observed_at"])
    return _dim("SUSPECTED","DERIVED",w[-1]["observed_at"],pattern=pat) if (not lp or lp<start) and len(heads)<=1 and len(cps)<=1 else _dim("NONE","DERIVED",w[-1]["observed_at"],pattern=None)

def _derive_block(t,p):
    if t["blockage"]["state"]=="EXPLICITLY_BLOCKED":return t["blockage"]
    f=t["evidence"]["recent_failures"]
    if len(f)>=p.suspected_blocked_failure_count:
        tail=f[-p.suspected_blocked_failure_count:]; lp=_dt(t["timestamps"]["last_progress_at"]); start=_dt(tail[0]["observed_at"])
        if len({x["signature"] for x in tail})==1 and (not lp or lp<start) and t["liveness"]["state"] in {"ACTIVE","QUIET"}:return _dim("SUSPECTED_BLOCKED","INFERRED",tail[-1]["observed_at"],blockage_class="TOOL_FAILURE")
    return _dim("NOT_BLOCKED","DERIVED",blockage_class="UNKNOWN") if t["blockage"]["state"]=="UNKNOWN" else t["blockage"]

def _continuity(t):
    i,c,ts=t["identity"],t["context"],t["timestamps"]
    f={"session_identity":i.get("session_identity") or t.get("session_id"),"repository":i.get("repository"),"task":i.get("task"),"branch":i.get("branch"),"observed_head":i.get("observed_head"),"last_action":c.get("last_action"),"checkpoint":c.get("checkpoint"),"last_progress":ts.get("last_progress_at"),"next_action":c.get("next_action")}
    present={k for k,v in f.items() if v not in (None,"")}; core=set("session_identity repository task branch observed_head".split()); resume=set("last_action checkpoint last_progress next_action".split())
    state="UNKNOWN" if not present else ("SUFFICIENT" if core<=present and len(resume&present)>=2 else ("PARTIAL" if len(core&present)>=3 else "INSUFFICIENT"))
    return _dim(state,"DERIVED",t["timestamps"]["last_seen_at"],missing=[k for k in f if k not in present])

def evaluate_at(twin,reference_time,policy=None):
    t=deepcopy(twin); p=_policy(t,policy); now=_dt(reference_time)
    if not now:raise ValueError("reference_time must be ISO-8601")
    terminal=t["evidence"].get("terminal_at")
    if terminal:t["presence"]=_dim("TERMINAL","EXPLICIT",terminal); t["liveness"]=_dim("TERMINAL","EXPLICIT",terminal)
    else:
        age=_age(now,t["timestamps"]["last_seen_at"]); t["presence"]=_dim("UNKNOWN") if age is None else _dim("PRESENT" if age<=p.presence_fresh_seconds else "KNOWN_NOT_CURRENTLY_OBSERVED","OBSERVED" if age<=p.presence_fresh_seconds else "DERIVED",t["timestamps"]["last_seen_at"])
        age=_age(now,t["timestamps"]["last_liveness_evidence_at"])
        state="UNKNOWN" if age is None else ("ACTIVE" if age<=p.liveness_active_seconds else ("QUIET" if age<=p.liveness_quiet_seconds else ("SUSPECTED" if age<=p.liveness_lost_seconds else "LOST")))
        t["liveness"]=_dim(state,"OBSERVED" if state=="ACTIVE" else ("UNKNOWN" if state=="UNKNOWN" else "DERIVED"),t["timestamps"]["last_liveness_evidence_at"])
    if t["activity"]["state"]=="ACTIVE" and (_age(now,t["timestamps"]["last_activity_at"]) or 0)>p.activity_quiet_seconds:t["activity"]=_dim("QUIET","DERIVED",t["timestamps"]["last_activity_at"])
    if t["blockage"]["state"]=="EXPLICITLY_BLOCKED":t["progress"]=_dim("BLOCKED_IF_EXPLICITLY_OBSERVED","EXPLICIT",t["blockage"]["evidence_at"])
    else:
        age=_age(now,t["timestamps"]["last_progress_at"]); state=("UNKNOWN" if t["presence"]["state"]=="UNKNOWN" else "NO_RECENT_PROGRESS_EVIDENCE") if age is None else ("ADVANCING" if age<=p.progress_fresh_seconds else "STALE")
        t["progress"]=_dim(state,"OBSERVED" if state=="ADVANCING" else ("UNKNOWN" if state=="UNKNOWN" else "DERIVED"),t["timestamps"]["last_progress_at"])
    if t["control_channel"]["state"]=="REACHABLE" and (_age(now,t["timestamps"]["last_control_ack_at"]) or 0)>p.control_ack_fresh_seconds:t["control_channel"]=_dim("DEGRADED","DERIVED",t["timestamps"]["last_control_ack_at"],consecutive_no_response=t["control_channel"].get("consecutive_no_response",0))
    t["loop"]=_derive_loop(t); t["blockage"]=_derive_block(t,p); t["continuity"]=_continuity(t)
    if t["blockage"]["state"]=="EXPLICITLY_BLOCKED":t["progress"]=_dim("BLOCKED_IF_EXPLICITLY_OBSERVED","EXPLICIT",t["blockage"]["evidence_at"])
    return t

def reduce_event(previous,event,reference_time=None,policy=None):
    e=normalize_event(event); t=deepcopy(previous) if previous else new_session_twin(); p=_policy(t,policy); t["policy"]=asdict(p); E=t["evidence"]; ts=t["timestamps"]
    if e["event_key"] in E["seen_event_keys"]:E["ignored_duplicate_count"]+=1; return t
    at,typ,payload=e["observed_at"],e["event_type"],e["payload"]; last=E["last_applied_event_at"]
    older=bool(_dt(last) and _dt(at)<_dt(last)); E["out_of_order_event_count"]+=int(older); E["seen_event_keys"].append(e["event_key"]); E["seen_event_keys"][:]=E["seen_event_keys"][-p.dedupe_limit:]; E["applied_event_count"]+=1; E["last_applied_event_at"]=_newer(last,at)
    ts["first_seen_at"]=ts["first_seen_at"] or at; ts["last_seen_at"]=_newer(ts["last_seen_at"],at)
    if not older:_identity(t,payload,at)
    if typ in {"SESSION_ATTACH","SESSION_RESUME","HEARTBEAT"}:ts["last_liveness_evidence_at"]=_newer(ts["last_liveness_evidence_at"],at)
    if typ in {"SESSION_ATTACH","SESSION_RESUME"} and E.get("terminal_at") and _dt(at)>_dt(E["terminal_at"]):E["terminal_at"]=None
    if typ in {"ACTIVITY_STARTED","ACTIVITY_COMPLETED","ACTIVITY_FAILED","TOOL_STARTED","TOOL_COMPLETED","TOOL_FAILED"}:
        ts["last_activity_at"]=_newer(ts["last_activity_at"],at); ts["last_liveness_evidence_at"]=_newer(ts["last_liveness_evidence_at"],at); sig=_signature(typ,payload)
        E["recent_actions"].append({"event_key":e["event_key"],"observed_at":at,"signature":sig,"observed_head":payload.get("observed_head") or payload.get("head") or t["identity"].get("observed_head"),"checkpoint_digest":t["context"].get("checkpoint_digest")}); E["recent_actions"].sort(key=lambda x:x["observed_at"]); E["recent_actions"][:]=E["recent_actions"][-p.history_limit:]
        if not older:t["activity"]=_dim("ACTIVE" if typ in {"ACTIVITY_STARTED","TOOL_STARTED"} else "IDLE","OBSERVED",at)
        if typ in {"ACTIVITY_FAILED","TOOL_FAILED"}:E["recent_failures"].append({"observed_at":at,"signature":sig["digest"]}); E["recent_failures"][:]=sorted(E["recent_failures"],key=lambda x:x["observed_at"])[-p.history_limit:]
    pc=_qualifies(typ,payload,t)
    if pc and _newer(ts["last_progress_at"],at)!=ts["last_progress_at"]:
        ts["last_progress_at"]=at; E["last_progress_evidence"]={"event_key":e["event_key"],"class":pc,"observed_at":at,"semantic":{k:payload[k] for k in "previous_phase current_phase completed_step_ref next_step_ref checkpoint_before checkpoint_after work_item_before work_item_after".split() if payload.get(k) is not None}}
        if t["blockage"]["state"]=="EXPLICITLY_BLOCKED":t["blockage"]=_dim("NOT_BLOCKED","OBSERVED",at,blockage_class="UNKNOWN")
    if typ=="BLOCKED" and not older:
        bc=payload.get("blockage_class") or "UNKNOWN"; t["blockage"]=_dim("EXPLICITLY_BLOCKED","EXPLICIT",at,blockage_class=bc if bc in BLOCK_CLASSES else "UNKNOWN")
        if payload.get("loop_confirmed"):t["loop"]=_dim("CONFIRMED_BY_EXPLICIT_SIGNAL","EXPLICIT",at,pattern=payload.get("loop_pattern"))
    if typ=="CHECKPOINT" and not older:
        cp=payload.get("checkpoint") or payload.get("checkpoint_after")
        if cp is not None:t["context"]["checkpoint"]=cp; t["context"]["checkpoint_digest"]=_hash(cp); ts["last_checkpoint_at"]=_newer(ts["last_checkpoint_at"],at)
    if typ=="INTERRUPTION":
        ts["last_liveness_evidence_at"]=_newer(ts["last_liveness_evidence_at"],at)
        if payload.get("terminal") is True and not older:E["terminal_at"]=_newer(E.get("terminal_at"),at)
    if typ in {"CHALLENGE_RESPONSE","COMMAND_ACK"} and not older:
        state=payload.get("delivery_state") or ("ACKNOWLEDGED" if typ=="COMMAND_ACK" else None)
        if state and state not in DELIVERY:raise ValueError(f"unsupported delivery_state: {state!r}")
        if state=="UNSUPPORTED":t["control_channel"]=_dim("UNSUPPORTED","EXPLICIT",at,consecutive_no_response=0)
        elif state in {"NO_RESPONSE","EXPIRED"}:
            n=t["control_channel"].get("consecutive_no_response",0)+1; t["control_channel"]=_dim("UNREACHABLE" if n>=p.control_unreachable_after_no_response else "DEGRADED","OBSERVED",at,consecutive_no_response=n)
        elif state in {"ACKNOWLEDGED","EXECUTING","COMPLETED","DELIVERED"}:
            t["control_channel"]=_dim("REACHABLE","OBSERVED",at,consecutive_no_response=0); ts["last_control_ack_at"]=_newer(ts["last_control_ack_at"],at)
            if typ=="CHALLENGE_RESPONSE":ts["last_challenge_response_at"]=_newer(ts["last_challenge_response_at"],at); ts["last_liveness_evidence_at"]=_newer(ts["last_liveness_evidence_at"],at)
    return evaluate_at(t,reference_time or at,p)

def project(events,reference_time=None,session_id=None,policy=None):
    t=new_session_twin(session_id)
    for e in events:t=reduce_event(t,e,e.get("observed_at") or e.get("timestamp"),policy)
    return evaluate_at(t,reference_time,policy) if reference_time else t
