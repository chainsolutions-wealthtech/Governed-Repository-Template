#!/usr/bin/env python3
from __future__ import annotations
import base64, copy, json

PROVIDERS=["CHATGPT","CLAUDE","CODEX","GITHUB_COPILOT","HUMAN","OTHER"]
INTENTS=["OBSERVE","CONTEXT_INTAKE","INFORMATION_INTAKE","WORK_REQUEST","CODE_CHANGE","REVIEW","INFRASTRUCTURE"]
PROFILES=["generic","application","chainsolutions-fullstack-web","data-platform","DEFER"]
ARCH=["NEW_EMPTY_PROJECT","EXISTING_CODE_TO_DISCOVER","KNOWN_ARCHITECTURE"]
INFRA=["NO_INFRASTRUCTURE_YET","UNKNOWN_TO_DISCOVER","KNOWN_TO_VERIFY"]
LOCAL_ACTIONS=["CONTINUE_GOVERNED_WORK","MAP_EXISTING_PROJECT","LAB_EVOLUTION"]

def q(i,f,t,choices=None,typ="string"):
    d={"kind":"QUESTION","id":i,"field":f,"text":t,"required":True,"response_type":typ}
    if choices is not None:d["choices"]=choices
    return d

def new_request(request_id,repository,head_sha,first_agent_required,initial_context=None):
    mode="FIRST_AGENT_BOOTSTRAP" if first_agent_required else "NORMAL_GOVERNED_ENTRY"
    s={"schema_version":"1.0.0","request_id":request_id,"repository":repository,"mode":mode,
       "status":"REQUEST_CREATED","phase":"START","revision":1,"expected_head_sha":head_sha,
       "answers":{},"next_request":None,"baseline_package":None,"handoff":None,"hold_reason":None}
    if initial_context:s["answers"]["initial_context"]=initial_context
    return refresh(s)

def reqs(s):
    base=[q("Q_AGENT","agent_identity","Quel agent se connecte au repository ?"),
          q("Q_PROVIDER","provider","Quel provider exécute cet agent ?",PROVIDERS),
          q("Q_INTENT","connection_intent","Quelle est l'intention immédiate de cette connexion ?",INTENTS)]
    if s["mode"]=="FIRST_AGENT_BOOTSTRAP":
        base += [
          q("Q_MISSION","project_mission","Quelle est la mission exacte de ce projet ?"),
          q("Q_SCOPE","project_scope","Définis le périmètre avec in_scope et out_of_scope.",typ="object"),
          q("Q_PROFILE","project_profile","Quel profil technique faut-il sélectionner ou différer ?",PROFILES),
          q("Q_ARCH","architecture_status","Quel est l'état architectural initial ?",ARCH),
          q("Q_ARCH_NOTES","architecture_notes","Décris ce qui est déjà connu de l'architecture. Écris UNKNOWN si rien n'est encore observé."),
          q("Q_INFRA","infrastructure_status","Quel est l'état initial de l'infrastructure ?",INFRA),
          q("Q_EXTERNAL","external_systems","Liste les systèmes externes déjà connus; [] si aucun.",typ="array"),
          q("Q_CONSTRAINTS","constraints","Liste les contraintes initiales connues; [] si aucune.",typ="array"),
          q("Q_FIRST_WORK","first_work_objective","Quelle est la première chose concrète à faire après la baseline ?"),
        ]
    else:
        base += [
          q("Q_LOCAL_ACTION","local_entry_action","Quelle action locale faut-il accomplir ?",LOCAL_ACTIONS),
          q("Q_OBJECTIVE","requested_objective","Quel est l'objectif exact de cette intervention ?"),
        ]
    return base

def validate(field,v):
    if field in {"agent_identity","project_mission","architecture_notes","first_work_objective","requested_objective"} and (not isinstance(v,str) or not v.strip()): return "non-empty text required"
    if field=="provider" and v not in PROVIDERS:return "invalid provider"
    if field=="connection_intent" and v not in INTENTS:return "invalid intent"
    if field=="project_profile" and v not in PROFILES:return "invalid profile"
    if field=="architecture_status" and v not in ARCH:return "invalid architecture status"
    if field=="infrastructure_status" and v not in INFRA:return "invalid infrastructure status"
    if field=="local_entry_action" and v not in LOCAL_ACTIONS:return "invalid local action"
    if field=="project_scope":
        if not isinstance(v,dict) or not isinstance(v.get("in_scope"),list) or not isinstance(v.get("out_of_scope"),list):return "project_scope requires in_scope/out_of_scope arrays"
    if field in {"external_systems","constraints"} and not isinstance(v,list):return "array required"
    if field=="baseline_approved" and not isinstance(v,bool):return "boolean required"
    return None

def build_package(s):
    a=s["answers"]
    return {"repository":s["repository"],"baseline_subject_head":s["expected_head_sha"],
      "agent_identity":a["agent_identity"],"provider":a["provider"],"connection_intent":a["connection_intent"],
      "project_mission":a["project_mission"],"project_scope":a["project_scope"],"project_profile":a["project_profile"],
      "architecture_status":a["architecture_status"],"architecture_notes":a["architecture_notes"],
      "infrastructure_status":a["infrastructure_status"],"external_systems":a["external_systems"],
      "constraints":a["constraints"],"first_work_objective":a["first_work_objective"]}

def refresh(s):
    s["next_request"]=None
    for r in reqs(s):
        if r["field"] not in s["answers"]:
            s["status"]="WAITING_FOR_ANSWER";s["phase"]=r["id"];s["next_request"]=r;return s
    if s["mode"]=="FIRST_AGENT_BOOTSTRAP":
        if s["baseline_package"] is None:s["baseline_package"]=build_package(s)
        if "baseline_approved" not in s["answers"]:
            s["status"]="WAITING_FOR_BASELINE_APPROVAL";s["phase"]="BASELINE_APPROVAL"
            s["next_request"]={"kind":"PLAN_APPROVAL","id":"Q_BASELINE_APPROVAL","field":"baseline_approved",
              "text":"Approuves-tu cette baseline afin qu'elle soit écrite dans le repository ?","required":True,
              "response_type":"boolean","plan":copy.deepcopy(s["baseline_package"])}
            return s
        if s["answers"]["baseline_approved"] is False:
            s["status"]="HOLD_FOR_REVIEW";s["phase"]="BASELINE_APPROVAL";s["hold_reason"]="baseline not approved";return s
        s["status"]="APPLYING_BASELINE";s["phase"]="APPLY_BASELINE"
        s["next_request"]={"kind":"APPLY_BASELINE","id":"APPLY_BASELINE","text":"Apply approved first-agent baseline.","expected_head_sha":s["expected_head_sha"]}
        return s
    s["status"]="LOCAL_HANDOFF_READY";s["phase"]="HANDOFF"
    s["handoff"]={"status":"LOCAL_HANDOFF_READY","repository":s["repository"],"expected_head_sha":s["expected_head_sha"],
      "agent_identity":s["answers"]["agent_identity"],"provider":s["answers"]["provider"],
      "connection_intent":s["answers"]["connection_intent"],"local_entry_action":s["answers"]["local_entry_action"],
      "requested_objective":s["answers"]["requested_objective"]}
    s["next_request"]={"kind":"HANDOFF","id":"LOCAL_HANDOFF_READY","handoff":copy.deepcopy(s["handoff"]),"text":"Local governed entry complete."}
    return s

def answer(s,field,value):
    s=copy.deepcopy(s)
    if (s.get("next_request") or {}).get("field")!=field:raise ValueError(f"unexpected field {field}")
    err=validate(field,value)
    if err:raise ValueError(err)
    s["answers"][field]=value;s["revision"]+=1
    return refresh(s)

def complete_baseline(s,new_head,session_id):
    s=copy.deepcopy(s)
    if (s.get("next_request") or {}).get("kind")!="APPLY_BASELINE":raise ValueError("baseline not awaiting apply")
    s["status"]="LOCAL_HANDOFF_READY";s["phase"]="HANDOFF";s["revision"]+=1
    s["handoff"]={"status":"LOCAL_HANDOFF_READY","repository":s["repository"],"baseline_commit_sha":new_head,
      "session_id":session_id,"next_action":"EXECUTE_FIRST_PROJECT_WORK_ITEM","first_work_objective":s["answers"]["first_work_objective"]}
    s["next_request"]={"kind":"HANDOFF","id":"LOCAL_HANDOFF_READY","text":"First-agent baseline committed.","handoff":copy.deepcopy(s["handoff"])}
    return s

def encode_state(s):
    return base64.urlsafe_b64encode(json.dumps(s,separators=(",",":"),ensure_ascii=False).encode()).decode().rstrip("=")
def decode_state(v):
    return json.loads(base64.urlsafe_b64decode((v+"="*((4-len(v)%4)%4)).encode()).decode())
