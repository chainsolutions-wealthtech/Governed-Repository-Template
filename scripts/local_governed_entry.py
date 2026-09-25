#!/usr/bin/env python3
from __future__ import annotations
import base64, copy, json

PROVIDERS=["CHATGPT","CLAUDE","CODEX","GITHUB_COPILOT","HUMAN","OTHER"]
INTENTS=["OBSERVE","CONTEXT_INTAKE","INFORMATION_INTAKE","WORK_REQUEST","CODE_CHANGE","REVIEW","INFRASTRUCTURE"]
PROFILES=["generic","application","chainsolutions-fullstack-web","data-platform","DEFER"]
ARCH=["NEW_EMPTY_PROJECT","EXISTING_CODE_TO_DISCOVER","KNOWN_ARCHITECTURE"]
INFRA=["NO_INFRASTRUCTURE_YET","UNKNOWN_TO_DISCOVER","KNOWN_TO_VERIFY"]
LOCAL_ACTIONS=["CONTINUE_GOVERNED_WORK","MAP_EXISTING_PROJECT","LAB_EVOLUTION"]
MCP_TRANSPORTS=["DIRECT_MCP_TOKEN","SSH","BOTH"]
MCP_SCOPES=["INFRASTRUCTURE_AND_DOMAIN_READONLY","FULL_GOVERNED_MAPPING"]
DOMAIN_STRATEGIES=["DISCOVER_EXISTING_THEN_PROPOSE","CREATE_NEW_AFTER_APPROVAL","NO_DOMAIN_YET"]
RUNTIME_POLICIES=["READ_ONLY_DISCOVERY","EXPLICIT_APPROVAL_FOR_SCOPED_WRITE"]
WORKFLOW_MODELS=["REGULATORY_AFRICAFUNDS_GOVERNED_FLOW","STANDARD_GOVERNED_FLOW"]

def q(i,f,t,choices=None,typ="string",extra=None):
    d={"kind":"QUESTION","id":i,"field":f,"text":t,"required":True,"response_type":typ}
    if choices is not None:d["choices"]=choices
    if extra:d.update(extra)
    return d

def new_request(request_id,repository,head_sha,first_agent_required,initial_context=None):
    mode="FIRST_AGENT_BOOTSTRAP" if first_agent_required else "NORMAL_GOVERNED_ENTRY"
    s={"schema_version":"1.1.0","request_id":request_id,"repository":repository,"mode":mode,
       "status":"REQUEST_CREATED","phase":"START","revision":1,"expected_head_sha":head_sha,
       "answers":{},"next_request":None,"baseline_package":None,"setup_package":None,
       "mcp_discovery":None,"credentials_verified":False,"handoff":None,"hold_reason":None}
    if initial_context:s["answers"]["initial_context"]=initial_context
    return refresh(s)

def baseline_reqs(s):
    return [
      q("Q_AGENT","agent_identity","Quel agent se connecte au repository ?"),
      q("Q_PROVIDER","provider","Quel provider exécute cet agent ?",PROVIDERS),
      q("Q_INTENT","connection_intent","Quelle est l'intention immédiate de cette connexion ?",INTENTS),
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

def normal_reqs():
    return [
      q("Q_AGENT","agent_identity","Quel agent se connecte au repository ?"),
      q("Q_PROVIDER","provider","Quel provider exécute cet agent ?",PROVIDERS),
      q("Q_INTENT","connection_intent","Quelle est l'intention immédiate de cette connexion ?",INTENTS),
      q("Q_LOCAL_ACTION","local_entry_action","Quelle action locale faut-il accomplir ?",LOCAL_ACTIONS),
      q("Q_OBJECTIVE","requested_objective","Quel est l'objectif exact de cette intervention ?"),
    ]

def validate(field,v):
    if field in {"agent_identity","project_mission","architecture_notes","first_work_objective","requested_objective","mcp_endpoint"} and (not isinstance(v,str) or not v.strip()): return "non-empty text required"
    if field=="provider" and v not in PROVIDERS:return "invalid provider"
    if field=="connection_intent" and v not in INTENTS:return "invalid intent"
    if field=="project_profile" and v not in PROFILES:return "invalid profile"
    if field=="architecture_status" and v not in ARCH:return "invalid architecture status"
    if field=="infrastructure_status" and v not in INFRA:return "invalid infrastructure status"
    if field=="local_entry_action" and v not in LOCAL_ACTIONS:return "invalid local action"
    if field=="mcp_transport" and v not in MCP_TRANSPORTS:return "invalid MCP transport"
    if field=="mcp_discovery_scope" and v not in MCP_SCOPES:return "invalid MCP discovery scope"
    if field=="domain_strategy" and v not in DOMAIN_STRATEGIES:return "invalid domain strategy"
    if field=="runtime_mutation_policy" and v not in RUNTIME_POLICIES:return "invalid runtime mutation policy"
    if field=="workflow_model" and v not in WORKFLOW_MODELS:return "invalid workflow model"
    if field=="project_scope":
        if not isinstance(v,dict) or not isinstance(v.get("in_scope"),list) or not isinstance(v.get("out_of_scope"),list):return "project_scope requires in_scope/out_of_scope arrays"
    if field in {"external_systems","constraints"} and not isinstance(v,list):return "array required"
    if field in {"baseline_approved","setup_repository_now","link_mcp_server","setup_approved"} and not isinstance(v,bool):return "boolean required"
    if field=="ssh_connection_profile":
        if not isinstance(v,dict) or not isinstance(v.get("host"),str) or not isinstance(v.get("user"),str):return "ssh_connection_profile requires host/user and optional port"
    if field=="domain_binding":
        if not isinstance(v,dict) or v.get("mode") not in {"EXISTING","CREATE_NEW","UNRESOLVED"}:return "domain_binding requires mode EXISTING/CREATE_NEW/UNRESOLVED"
        if v.get("mode") in {"EXISTING","CREATE_NEW"} and not isinstance(v.get("domain"),str):return "domain required"
    return None

def build_baseline(s):
    a=s["answers"]
    return {"repository":s["repository"],"baseline_subject_head":s["expected_head_sha"],
      "agent_identity":a["agent_identity"],"provider":a["provider"],"connection_intent":a["connection_intent"],
      "project_mission":a["project_mission"],"project_scope":a["project_scope"],"project_profile":a["project_profile"],
      "architecture_status":a["architecture_status"],"architecture_notes":a["architecture_notes"],
      "infrastructure_status":a["infrastructure_status"],"external_systems":a["external_systems"],
      "constraints":a["constraints"],"first_work_objective":a["first_work_objective"]}

def credential_requirements(a):
    t=a.get("mcp_transport")
    req=[]
    if t in {"DIRECT_MCP_TOKEN","BOTH"}:
        req += [{"kind":"variable","name":"GOVERNED_MCP_URL"},{"kind":"secret","name":"GOVERNED_MCP_AUTH_TOKEN"}]
    # SSH/BOTH use a GitHub OIDC-issued ephemeral certificate. No persistent
    # repository SSH private-key secret is permitted.
    return req

def build_setup(s):
    a=s["answers"]; linked=a.get("link_mcp_server") is True
    plan={
      "setup_repository_now":a.get("setup_repository_now"),
      "link_mcp_server":linked,
      "workflow_model":a.get("workflow_model"),
      "git_rights":{
        "read":["metadata","contents","commits","branches","pull requests","issues","actions/checks"],
        "governed_write":["contents","issues","pull requests","workflow files when explicitly required"],
        "forbidden":["force push","history rewrite","unreviewed destructive administration"]
      }
    }
    if linked:
        plan["mcp"]={
          "transport":a.get("mcp_transport"),"endpoint":a.get("mcp_endpoint"),
          "ssh_connection_profile":a.get("ssh_connection_profile"),
          "credential_requirements":credential_requirements(a),
          "ssh_authentication":"GITHUB_OIDC_EPHEMERAL_CERTIFICATE" if a.get("mcp_transport") in {"SSH","BOTH"} else None,
          "discovery_scope":a.get("mcp_discovery_scope"),"domain_strategy":a.get("domain_strategy"),
          "domain_binding":a.get("domain_binding"),"runtime_mutation_policy":a.get("runtime_mutation_policy"),
          "discovery_tools":["ping","get_project_context","list_domains_s1","list_domains_s2","get_write_tools_context"],
          "write_tools":"DISABLED_UNTIL_MCP_PROJECT_REGISTRATION_AND_EXPLICIT_AUTHORITY",
          "discovery_evidence":s.get("mcp_discovery")
        }
    return plan

def refresh(s):
    s["next_request"]=None
    reqs=baseline_reqs(s) if s["mode"]=="FIRST_AGENT_BOOTSTRAP" else normal_reqs()
    for r in reqs:
        if r["field"] not in s["answers"]:
            s["status"]="WAITING_FOR_ANSWER";s["phase"]=r["id"];s["next_request"]=r;return s
    if s["mode"]!="FIRST_AGENT_BOOTSTRAP":
        s["status"]="LOCAL_HANDOFF_READY";s["phase"]="HANDOFF"
        s["handoff"]={"status":"LOCAL_HANDOFF_READY","repository":s["repository"],"expected_head_sha":s["expected_head_sha"],
          "agent_identity":s["answers"]["agent_identity"],"provider":s["answers"]["provider"],
          "connection_intent":s["answers"]["connection_intent"],"local_entry_action":s["answers"]["local_entry_action"],
          "requested_objective":s["answers"]["requested_objective"]}
        s["next_request"]={"kind":"HANDOFF","id":"LOCAL_HANDOFF_READY","handoff":copy.deepcopy(s["handoff"]),"text":"Local governed entry complete."};return s

    if s["baseline_package"] is None:s["baseline_package"]=build_baseline(s)
    if "baseline_approved" not in s["answers"]:
        s["status"]="WAITING_FOR_BASELINE_APPROVAL";s["phase"]="BASELINE_APPROVAL"
        s["next_request"]={"kind":"PLAN_APPROVAL","id":"Q_BASELINE_APPROVAL","field":"baseline_approved",
          "text":"Approuves-tu cette baseline métier ? Le setup technique guidé continuera ensuite avant toute écriture finale.","required":True,
          "response_type":"boolean","plan":copy.deepcopy(s["baseline_package"])};return s
    if s["answers"]["baseline_approved"] is False:
        s["status"]="HOLD_FOR_REVIEW";s["phase"]="BASELINE_APPROVAL";s["hold_reason"]="baseline not approved";return s

    if "setup_repository_now" not in s["answers"]:
        s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_SETUP_NOW";s["next_request"]=q("Q_SETUP_NOW","setup_repository_now","Veux-tu poursuivre maintenant le setup technique guidé du repository ?",typ="boolean");return s
    if s["answers"]["setup_repository_now"] is False:
        s["setup_package"]={"setup_repository_now":False}
        s["status"]="APPLYING_BASELINE";s["phase"]="APPLY_BASELINE";s["next_request"]={"kind":"APPLY_BASELINE","id":"APPLY_BASELINE","text":"Apply approved business baseline.","expected_head_sha":s["expected_head_sha"]};return s

    if "link_mcp_server" not in s["answers"]:
        s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_LINK_MCP";s["next_request"]=q("Q_LINK_MCP","link_mcp_server","Veux-tu lier ce repository GitHub à ton serveur MCP afin de découvrir serveurs, domaines et capacités ?",typ="boolean");return s

    if s["answers"]["link_mcp_server"]:
        for r in [
          q("Q_MCP_TRANSPORT","mcp_transport","Quel transport veux-tu configurer pour le MCP ?",MCP_TRANSPORTS),
        ]:
            if r["field"] not in s["answers"]:s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]=r["id"];s["next_request"]=r;return s
        if "mcp_endpoint" not in s["answers"]:
            s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_MCP_ENDPOINT";s["next_request"]=q("Q_MCP_ENDPOINT","mcp_endpoint","Quelle est l'URL publique du endpoint MCP ? Aucun token ne doit être mis ici.");return s
        if s["answers"]["mcp_transport"] in {"SSH","BOTH"} and "ssh_connection_profile" not in s["answers"]:
            s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_SSH_PROFILE";s["next_request"]=q("Q_SSH_PROFILE","ssh_connection_profile","Indique uniquement host/user/port non secrets pour le fallback SSH.",typ="object");return s
        for r in [
          q("Q_MCP_SCOPE","mcp_discovery_scope","Quel niveau de découverte MCP veux-tu ?",MCP_SCOPES),
          q("Q_DOMAIN_STRATEGY","domain_strategy","Comment traiter le domaine du projet ?",DOMAIN_STRATEGIES),
          q("Q_RUNTIME_POLICY","runtime_mutation_policy","Quelle autorité runtime initiale accordes-tu ?",RUNTIME_POLICIES),
        ]:
            if r["field"] not in s["answers"]:s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]=r["id"];s["next_request"]=r;return s

        requirements=credential_requirements(s["answers"])
        if not s.get("credentials_verified") and requirements:
            s["status"]="MCP_CREDENTIAL_REQUIRED";s["phase"]="MCP_CREDENTIAL_GATE"
            s["next_request"]={"kind":"CREDENTIAL_GATE","id":"MCP_CREDENTIAL_GATE",
              "text":"Configure les secrets/variables Actions requis puis exécute /local-execute. Ne colle aucun secret dans l'issue.",
              "requirements":requirements};return s
        if not s.get("credentials_verified") and not requirements:
            s["credentials_verified"]=True
        if s.get("mcp_discovery") is None:
            s["status"]="MCP_DISCOVERY_REQUIRED";s["phase"]="MCP_DISCOVERY"
            s["next_request"]={"kind":"MCP_DISCOVERY","id":"MCP_DISCOVERY","text":"Run read-only MCP discovery.","tools":["ping","get_project_context","list_domains_s1","list_domains_s2","get_write_tools_context"]};return s
        if "domain_binding" not in s["answers"]:
            s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_DOMAIN_BINDING"
            s["next_request"]=q("Q_DOMAIN_BINDING","domain_binding","À partir de l'inventaire MCP, veux-tu joindre un domaine existant, demander un nouveau domaine, ou laisser ce point non résolu ?",typ="object",extra={"mcp_discovery":copy.deepcopy(s["mcp_discovery"])});return s

    if "workflow_model" not in s["answers"]:
        s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_WORKFLOW_MODEL";s["next_request"]=q("Q_WORKFLOW_MODEL","workflow_model","Quel flux de lecture et de travail veux-tu appliquer ?",WORKFLOW_MODELS);return s

    s["setup_package"]=build_setup(s)
    if "setup_approved" not in s["answers"]:
        s["status"]="WAITING_FOR_SETUP_APPROVAL";s["phase"]="SETUP_APPROVAL"
        s["next_request"]={"kind":"PLAN_APPROVAL","id":"Q_SETUP_APPROVAL","field":"setup_approved",
          "text":"Approuves-tu ce setup technique et cette matrice de droits avant matérialisation dans le repository ?","required":True,
          "response_type":"boolean","plan":copy.deepcopy(s["setup_package"])};return s
    if s["answers"]["setup_approved"] is False:
        s["status"]="HOLD_FOR_REVIEW";s["phase"]="SETUP_APPROVAL";s["hold_reason"]="technical setup not approved";return s

    s["status"]="APPLYING_BASELINE";s["phase"]="APPLY_BASELINE"
    s["next_request"]={"kind":"APPLY_BASELINE","id":"APPLY_BASELINE","text":"Apply approved business baseline and repository setup.","expected_head_sha":s["expected_head_sha"]};return s

def answer(s,field,value):
    s=copy.deepcopy(s)
    if (s.get("next_request") or {}).get("field")!=field:raise ValueError(f"unexpected field {field}")
    err=validate(field,value)
    if err:raise ValueError(err)
    s["answers"][field]=value;s["revision"]+=1
    return refresh(s)

def mark_credentials_verified(s):
    s=copy.deepcopy(s)
    if (s.get("next_request") or {}).get("kind")!="CREDENTIAL_GATE":raise ValueError("not at credential gate")
    s["credentials_verified"]=True;s["revision"]+=1
    return refresh(s)

def record_mcp_discovery(s,evidence):
    s=copy.deepcopy(s)
    if (s.get("next_request") or {}).get("kind")!="MCP_DISCOVERY":raise ValueError("not awaiting MCP discovery")
    s["mcp_discovery"]=evidence;s["revision"]+=1
    return refresh(s)

def complete_baseline(s,new_head,session_id):
    s=copy.deepcopy(s)
    if (s.get("next_request") or {}).get("kind")!="APPLY_BASELINE":raise ValueError("baseline not awaiting apply")
    s["status"]="LOCAL_HANDOFF_READY";s["phase"]="HANDOFF";s["revision"]+=1
    s["handoff"]={"status":"LOCAL_HANDOFF_READY","repository":s["repository"],"baseline_commit_sha":new_head,
      "session_id":session_id,"next_action":"EXECUTE_FIRST_PROJECT_WORK_ITEM","first_work_objective":s["answers"]["first_work_objective"],
      "setup":copy.deepcopy(s.get("setup_package"))}
    s["next_request"]={"kind":"HANDOFF","id":"LOCAL_HANDOFF_READY","text":"First-agent baseline and setup committed.","handoff":copy.deepcopy(s["handoff"])}
    return s

def encode_state(s):
    return base64.urlsafe_b64encode(json.dumps(s,separators=(",",":"),ensure_ascii=False).encode()).decode().rstrip("=")
def decode_state(v):
    s=json.loads(base64.urlsafe_b64decode((v+"="*((4-len(v)%4)%4)).encode()).decode())
    s.setdefault("setup_package",None);s.setdefault("mcp_discovery",None);s.setdefault("credentials_verified",False)
    return s
