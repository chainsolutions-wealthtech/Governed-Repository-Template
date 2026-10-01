#!/usr/bin/env python3
from __future__ import annotations
import base64, copy, json, re

PROVIDERS=["CHATGPT","CLAUDE","CODEX","GITHUB_COPILOT","HUMAN","OTHER"]
INTENTS=["OBSERVE","CONTEXT_INTAKE","INFORMATION_INTAKE","WORK_REQUEST","CODE_CHANGE","REVIEW","INFRASTRUCTURE"]
PROFILES=["generic","application","chainsolutions-fullstack-web","data-platform","DEFER"]
ARCH=["NEW_EMPTY_PROJECT","EXISTING_CODE_TO_DISCOVER","KNOWN_ARCHITECTURE"]
INFRA=["NO_INFRASTRUCTURE_YET","UNKNOWN_TO_DISCOVER","KNOWN_TO_VERIFY"]
LOCAL_ACTIONS=["CONTINUE_GOVERNED_WORK","MAP_EXISTING_PROJECT","LAB_EVOLUTION"]
MCP_TRANSPORTS=["DIRECT_MCP_TOKEN","SSH","BOTH"]
MCP_SCOPES=["INFRASTRUCTURE_AND_DOMAIN_READONLY","FULL_GOVERNED_MAPPING"]
DOMAIN_STRATEGIES=["DISCOVER_EXISTING_THEN_PROPOSE","CREATE_NEW_AFTER_APPROVAL","NO_DOMAIN_YET"]
DOMAIN_INTENTS=["REUSE_EXISTING_DOMAIN","CREATE_SUBDOMAIN","CREATE_NEW_ROOT_DOMAIN","CREATE_CHILD_DOMAIN","NO_PUBLIC_DOMAIN","DECIDE_LATER"]
DOMAIN_LABEL_CHOICES=["ekyc","kyc","identity","verify","OTHER_CUSTOM","DECIDE_LATER"]
DOMAIN_ROOT_NAME_MODES=["CUSTOM_NAME","DISCOVER_AVAILABLE_NAMES","DECIDE_LATER"]
DEPLOYMENT_MOUNT_MODES=["HOST_ROOT","CREATE_PATH","REUSE_EXISTING_PATH","DECIDE_LATER"]
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
    if field=="production_server_selection":
        if not isinstance(v,str) or not v.strip():return "production_server_selection requires a non-empty choice"
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}",v):return "invalid production server selection"
    if field=="domain_intent" and v not in DOMAIN_INTENTS:return "invalid domain intent"
    if field=="domain_parent_selection":
        if v!="DECIDE_LATER" and (not isinstance(v,str) or not re.fullmatch(r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}",v)):return "invalid domain parent selection"
    if field=="domain_existing_selection":
        if v!="DECIDE_LATER" and (not isinstance(v,str) or not re.fullmatch(r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}",v)):return "invalid existing domain selection"
    if field=="domain_label_choice" and v not in DOMAIN_LABEL_CHOICES:return "invalid domain label choice"
    if field=="domain_label_custom":
        if not isinstance(v,str) or not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?",v):return "invalid custom domain label"
    if field=="domain_root_name_mode" and v not in DOMAIN_ROOT_NAME_MODES:return "invalid root domain mode"
    if field=="domain_root_name":
        if not isinstance(v,str) or not re.fullmatch(r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}",v):return "invalid root domain name"
    if field=="deployment_mount_mode" and v not in DEPLOYMENT_MOUNT_MODES:return "invalid deployment mount mode"
    if field=="deployment_path":
        if not isinstance(v,str) or not re.fullmatch(r"/[A-Za-z0-9._~-]+(?:/[A-Za-z0-9._~-]+)*",v):return "invalid deployment path"
    if field=="project_scope":
        if not isinstance(v,dict) or not isinstance(v.get("in_scope"),list) or not isinstance(v.get("out_of_scope"),list):return "project_scope requires in_scope/out_of_scope arrays"
    if field in {"external_systems","constraints"} and not isinstance(v,list):return "array required"
    if field in {"baseline_approved","setup_repository_now","link_mcp_server","mcp_discovery_approved","setup_approved"} and not isinstance(v,bool):return "boolean required"
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

def build_mcp_discovery_plan(s):
    a=s["answers"]
    transport=a.get("mcp_transport")
    plan={
      "operation":"READ_ONLY_MCP_DISCOVERY",
      "repository":s["repository"],
      "transport":transport,
      "endpoint":a.get("mcp_endpoint"),
      "ssh_connection_profile":copy.deepcopy(a.get("ssh_connection_profile")),
      "scope":a.get("mcp_discovery_scope"),
      "domain_strategy":a.get("domain_strategy"),
      "runtime_mutation_policy":a.get("runtime_mutation_policy"),
      "tools":["ping","get_project_context","list_domains_s1","list_domains_s2","get_write_tools_context"],
      "mutation_authority":False,
      "secret_value_exposure":False,
      "purpose":"OBSERVE_EXISTING_PROJECT_SERVER_DOMAIN_AND_CAPABILITY_STATE_BEFORE_GAP_ANALYSIS"
    }
    if transport=="BOTH":
        plan["configured_transports"]=["DIRECT_MCP_TOKEN","SSH"]
        plan["routing"]={
          "mode":"DUAL_READY_SMART_ROUTING",
          "initial_preference":"DIRECT_MCP_TOKEN",
          "fallback":"SSH",
          "fallback_condition":"PRIMARY_UNAVAILABLE_FAILED_OR_CAPABILITY_REQUIRES_ALTERNATE",
          "simultaneous_execution_required":False,
          "one_successful_route_satisfies_current_discovery":True
        }
    return plan

def credential_requirements(a):
    t=a.get("mcp_transport")
    req=[]
    if t=="DIRECT_MCP_TOKEN":
        req += [{"kind":"secret","name":"GOVERNED_MCP_AUTH_TOKEN"}]
    # BOTH prefers direct MCP when a token is available, but its secretless
    # OIDC SSH fallback is sufficient for initial read-only discovery.
    # SSH/BOTH never require a persistent repository SSH private-key secret.
    return req

def _discovery_tool_evidence(s,tool):
    evidence=s.get("mcp_discovery")
    if not isinstance(evidence,dict):return None
    candidates=[evidence,evidence.get("direct_mcp"),evidence.get("ssh_certificate")]
    for candidate in candidates:
        if not isinstance(candidate,dict):continue
        tools=candidate.get("tools")
        if isinstance(tools,dict) and isinstance(tools.get(tool),dict):
            return tools.get(tool)
    return None

def observed_server_choices(s):
    choices=[]
    for server_id in ("S1","S2"):
        item=_discovery_tool_evidence(s,f"list_domains_{server_id.lower()}")
        if isinstance(item,dict) and item.get("status") in {"PASS","PARTIAL"}:
            choices.append(server_id)
    return choices

def _collect_text(value,out):
    if isinstance(value,str):out.append(value);return
    if isinstance(value,list):
        for item in value:_collect_text(item,out)
        return
    if isinstance(value,dict):
        for item in value.values():_collect_text(item,out)

def observed_domains_for_server(s,server_id):
    item=_discovery_tool_evidence(s,f"list_domains_{str(server_id).lower()}")
    if not isinstance(item,dict):return []
    texts=[];_collect_text(item.get("result"),texts)
    domains=set()
    patterns=[
      r"/var/www/vhosts/system/([A-Za-z0-9.-]+\.[A-Za-z]{2,})(?:/|\s|$)",
      r"/var/www/vhosts/([A-Za-z0-9.-]+\.[A-Za-z]{2,})(?:/|\s|$)"
    ]
    for text in texts:
        for pattern in patterns:
            for domain in re.findall(pattern,text):
                domains.add(domain.lower())
    return sorted(domains)[:100]

def observed_parent_domains_for_server(s,server_id):
    domains=observed_domains_for_server(s,server_id)
    parents=[]
    for domain in domains:
        if any(domain.endswith("."+other) for other in domains if other!=domain):
            continue
        parents.append(domain)
    return sorted(parents)

def domain_operation_requirements(intent):
    if intent=="REUSE_EXISTING_DOMAIN":
        return {
          "intent":"VERIFY_EXISTING_DOMAIN_BINDING",
          "execution_intent":"PRODUCTION_ATTESTATION",
          "required_capabilities":["DOMAIN_WEB_OBSERVATION","SERVER_RUNTIME_OBSERVATION"],
          "required_authority":"READ_ONLY_DISCOVERY_AUTHORITY",
          "prepared_only":True,
          "execution_authority_granted":False
        }
    if intent in {"CREATE_SUBDOMAIN","CREATE_CHILD_DOMAIN"}:
        return {
          "intent":"CREATE_SUBDOMAIN",
          "execution_intent":"CREATE_SUBDOMAIN",
          "required_capabilities":["WEB_HOSTING_CHANGE","DOMAIN_DNS_CHANGE","TLS_CHANGE"],
          "required_authority":"SCOPED_WEB_AND_DNS_WRITE",
          "prepared_only":True,
          "execution_authority_granted":False
        }
    if intent=="CREATE_NEW_ROOT_DOMAIN":
        return {
          "intent":"CREATE_NEW_DOMAIN_BINDING",
          "execution_intent":"CREATE_NEW_DOMAIN_BINDING",
          "required_capabilities":["DOMAIN_REGISTRATION_OR_EXTERNAL_PROVISIONING","DOMAIN_DNS_CHANGE","WEB_HOSTING_CHANGE","TLS_CHANGE"],
          "required_authority":"SCOPED_WEB_AND_DNS_WRITE",
          "prepared_only":True,
          "execution_authority_granted":False
        }
    return {
      "intent":"NO_DOMAIN_MUTATION",
      "execution_intent":None,
      "required_capabilities":[],
      "required_authority":None,
      "prepared_only":True,
      "execution_authority_granted":False
    }

def derive_deployment_binding(s):
    a=s.get("answers") or {}
    if a.get("domain_intent")!="REUSE_EXISTING_DOMAIN":return None
    host=a.get("domain_existing_selection")
    if not host or host=="DECIDE_LATER":return None
    selected_server=a.get("production_server_selection")
    mode=a.get("deployment_mount_mode")
    if mode=="HOST_ROOT":
        return {
          "mode":"HOST_ROOT",
          "kind":"EXISTING_HOST_ROOT",
          "host":host,
          "path":"/",
          "server":selected_server
        }
    if mode in {"CREATE_PATH","REUSE_EXISTING_PATH"} and a.get("deployment_path"):
        return {
          "mode":mode,
          "kind":"EXISTING_HOST_PATH",
          "host":host,
          "path":a.get("deployment_path"),
          "server":selected_server
        }
    if mode=="DECIDE_LATER":
        return {
          "mode":"UNRESOLVED",
          "kind":"EXISTING_HOST_PATH",
          "host":host,
          "reason":"DECIDE_LATER",
          "server":selected_server
        }
    return None

def deployment_operation_requirements(binding):
    binding=binding or {}
    mode=binding.get("mode")
    if mode=="CREATE_PATH":
        return {
          "intent":"CONFIGURE_EXISTING_HOST_PATH_BINDING",
          "execution_intent":"CONFIGURE_REVERSE_PROXY",
          "required_capabilities":["WEB_HOSTING_CHANGE","SERVER_RUNTIME_OBSERVATION"],
          "required_authority":"SCOPED_WEB_WRITE",
          "prepared_only":True,
          "execution_authority_granted":False
        }
    if mode in {"HOST_ROOT","REUSE_EXISTING_PATH"}:
        return {
          "intent":"VERIFY_EXISTING_HOST_MOUNT",
          "execution_intent":"PRODUCTION_ATTESTATION",
          "required_capabilities":["DOMAIN_WEB_OBSERVATION","SERVER_RUNTIME_OBSERVATION"],
          "required_authority":"READ_ONLY_DISCOVERY_AUTHORITY",
          "prepared_only":True,
          "execution_authority_granted":False
        }
    return {
      "intent":"NO_DEPLOYMENT_PATH_MUTATION",
      "execution_intent":None,
      "required_capabilities":[],
      "required_authority":None,
      "prepared_only":True,
      "execution_authority_granted":False
    }

def derive_domain_binding(s):
    a=s.get("answers") or {}
    intent=a.get("domain_intent")
    selected_server=a.get("production_server_selection")
    if intent=="REUSE_EXISTING_DOMAIN":
        domain=a.get("domain_existing_selection")
        if domain:
            return {"mode":"EXISTING","kind":"EXISTING_DOMAIN","domain":domain,"server":selected_server}
    if intent in {"CREATE_SUBDOMAIN","CREATE_CHILD_DOMAIN"}:
        parent=a.get("domain_parent_selection")
        label=a.get("domain_label_choice")
        if label=="OTHER_CUSTOM":
            label=a.get("domain_label_custom")
        if parent and label and label!="DECIDE_LATER":
            return {
              "mode":"CREATE_NEW",
              "kind":"SUBDOMAIN" if intent=="CREATE_SUBDOMAIN" else "CHILD_DOMAIN",
              "domain":f"{label}.{parent}",
              "parent_domain":parent,
              "label":label,
              "server":selected_server
            }
    if intent=="CREATE_NEW_ROOT_DOMAIN":
        mode=a.get("domain_root_name_mode")
        if mode=="CUSTOM_NAME" and a.get("domain_root_name"):
            return {
              "mode":"CREATE_NEW",
              "kind":"ROOT_DOMAIN",
              "domain":a.get("domain_root_name"),
              "server":selected_server
            }
        if mode in {"DISCOVER_AVAILABLE_NAMES","DECIDE_LATER"}:
            return {
              "mode":"UNRESOLVED",
              "kind":"ROOT_DOMAIN",
              "reason":mode,
              "server":selected_server
            }
    if intent in {"NO_PUBLIC_DOMAIN","DECIDE_LATER"}:
        return {
          "mode":"UNRESOLVED",
          "kind":intent,
          "server":selected_server
        }
    return None

def reconcile_domain_question_order(s):
    s=copy.deepcopy(s)
    a=s.get("answers") or {}
    if (
      s.get("mode")=="FIRST_AGENT_BOOTSTRAP"
      and a.get("production_server_selection")
      and "domain_binding" not in a
      and "domain_intent" not in a
      and ((s.get("next_request") or {}).get("field")=="domain_binding" or s.get("phase")=="Q_DOMAIN_BINDING")
    ):
        s["setup_package"]=None
        s["hold_reason"]=None
        return refresh(s)
    return s

def reconcile_existing_host_path_question_order(s):
    s=copy.deepcopy(s)
    a=s.get("answers") or {}
    if (
      s.get("mode")=="FIRST_AGENT_BOOTSTRAP"
      and a.get("domain_intent")=="REUSE_EXISTING_DOMAIN"
      and a.get("domain_existing_selection") not in {None,"DECIDE_LATER"}
      and "deployment_binding" not in a
      and "deployment_mount_mode" not in a
      and (
        (s.get("next_request") or {}).get("field") in {"workflow_model","setup_approved"}
        or s.get("phase") in {"Q_WORKFLOW_MODEL","SETUP_APPROVAL"}
      )
    ):
        s["setup_package"]=None
        s["hold_reason"]=None
        return refresh(s)
    return s

def fresh_project_requires_production_server_choice(s):
    if s.get("mode")!="FIRST_AGENT_BOOTSTRAP":return False
    a=s.get("answers") or {}
    return (
      a.get("architecture_status")=="NEW_EMPTY_PROJECT"
      and a.get("infrastructure_status") in {"NO_INFRASTRUCTURE_YET","UNKNOWN_TO_DISCOVER"}
      and isinstance(s.get("mcp_discovery"),dict)
      and "domain_binding" not in a
    )

def reconcile_setup_question_order(s):
    s=copy.deepcopy(s)
    if fresh_project_requires_production_server_choice(s) and "production_server_selection" not in (s.get("answers") or {}):
        s["setup_package"]=None
        s["hold_reason"]=None
        return refresh(s)
    return s

def build_setup(s):
    a=s["answers"]; linked=a.get("link_mcp_server") is True
    plan={
      "setup_repository_now":a.get("setup_repository_now"),
      "link_mcp_server":linked,
      "workflow_model":a.get("workflow_model"),
      "deployment_binding":copy.deepcopy(a.get("deployment_binding")),
      "deployment_operation_requirements":deployment_operation_requirements(a.get("deployment_binding")),
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
          "optional_credentials":[{"kind":"secret","name":"GOVERNED_MCP_AUTH_TOKEN","purpose":"PREFERRED_DIRECT_MCP"}] if a.get("mcp_transport")=="BOTH" else [],
          "ssh_authentication":"GITHUB_OIDC_EPHEMERAL_CERTIFICATE" if a.get("mcp_transport") in {"SSH","BOTH"} else None,
          "routing_strategy":{
            "mode":"DUAL_READY_SMART_ROUTING",
            "configured_transports":["DIRECT_MCP_TOKEN","SSH"],
            "initial_preference":"DIRECT_MCP_TOKEN",
            "fallback":"SSH",
            "simultaneous_execution_required":False
          } if a.get("mcp_transport")=="BOTH" else None,
          "discovery_scope":a.get("mcp_discovery_scope"),"domain_strategy":a.get("domain_strategy"),
          "production_server_selection":a.get("production_server_selection"),
          "domain_intent":a.get("domain_intent"),
          "domain_binding":a.get("domain_binding"),
          "domain_operation_requirements":domain_operation_requirements(a.get("domain_intent")),
          "deployment_binding":copy.deepcopy(a.get("deployment_binding")),
          "deployment_operation_requirements":deployment_operation_requirements(a.get("deployment_binding")),
          "runtime_mutation_policy":a.get("runtime_mutation_policy"),
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

        if s.get("mcp_discovery") is None and "mcp_discovery_approved" not in s["answers"]:
            s["status"]="WAITING_FOR_DISCOVERY_APPROVAL";s["phase"]="MCP_DISCOVERY_APPROVAL"
            s["next_request"]={"kind":"PLAN_APPROVAL","id":"Q_MCP_DISCOVERY_APPROVAL","field":"mcp_discovery_approved",
              "text":"Le plan de découverte MCP en lecture seule est prêt. L'approuves-tu pour exécution maintenant ? La configuration exprimée jusque-là ne constitue pas une autorisation d'exécution.",
              "required":True,"response_type":"boolean","plan":build_mcp_discovery_plan(s)};return s
        if s.get("mcp_discovery") is None and s["answers"].get("mcp_discovery_approved") is False:
            s["status"]="HOLD_FOR_REVIEW";s["phase"]="MCP_DISCOVERY_APPROVAL";s["hold_reason"]="MCP discovery not approved";return s

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
        if fresh_project_requires_production_server_choice(s) and "production_server_selection" not in s["answers"]:
            observed=observed_server_choices(s)
            choices=observed+[x for x in ["PLAN_NEW_SERVER","DECIDE_LATER"] if x not in observed]
            s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_PRODUCTION_SERVER_SELECTION"
            s["next_request"]=q(
              "Q_PRODUCTION_SERVER_SELECTION","production_server_selection",
              "Aucun binding serveur n'est encore établi pour ce projet neuf. Sur quel serveur veux-tu préparer la production ?",
              choices,
              extra={"observed_servers":observed,"decision_kind":"OWNER_PRODUCTION_TARGET","execution_authority_granted":False}
            );return s
        selected=s["answers"].get("production_server_selection")
        domains=observed_domains_for_server(s,selected) if selected in {"S1","S2"} else []
        parents=observed_parent_domains_for_server(s,selected) if selected in {"S1","S2"} else []
        if "domain_binding" not in s["answers"] and "domain_intent" not in s["answers"]:
            s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_DOMAIN_INTENT"
            s["next_request"]=q(
              "Q_DOMAIN_INTENT","domain_intent",
              "Quel type de binding de domaine veux-tu préparer sur le serveur de production choisi ?",
              DOMAIN_INTENTS,
              extra={
                "selected_server":selected,
                "observed_domains":domains,
                "observed_parent_domains":parents,
                "mcp_discovery_reused":True,
                "decision_kind":"OWNER_DOMAIN_INTENT",
                "execution_authority_granted":False
              }
            );return s

        domain_intent=s["answers"].get("domain_intent")
        if "domain_binding" not in s["answers"] and domain_intent=="REUSE_EXISTING_DOMAIN" and "domain_existing_selection" not in s["answers"]:
            choices=domains+["DECIDE_LATER"]
            s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_DOMAIN_EXISTING_SELECTION"
            s["next_request"]=q(
              "Q_DOMAIN_EXISTING_SELECTION","domain_existing_selection",
              "Quel domaine déjà observé sur le serveur veux-tu rattacher au projet ?",
              choices,
              extra={"selected_server":selected,"execution_authority_granted":False}
            );return s

        if "domain_binding" not in s["answers"] and domain_intent in {"CREATE_SUBDOMAIN","CREATE_CHILD_DOMAIN"} and "domain_parent_selection" not in s["answers"]:
            choices=parents+["DECIDE_LATER"]
            s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_DOMAIN_PARENT_SELECTION"
            s["next_request"]=q(
              "Q_DOMAIN_PARENT_SELECTION","domain_parent_selection",
              "Sous quel domaine parent observé sur le serveur veux-tu préparer ce domaine ?",
              choices,
              extra={"selected_server":selected,"observed_parent_domains":parents,"execution_authority_granted":False}
            );return s

        if "domain_binding" not in s["answers"] and domain_intent in {"CREATE_SUBDOMAIN","CREATE_CHILD_DOMAIN"} and s["answers"].get("domain_parent_selection")!="DECIDE_LATER" and "domain_label_choice" not in s["answers"]:
            s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_DOMAIN_LABEL_CHOICE"
            s["next_request"]=q(
              "Q_DOMAIN_LABEL_CHOICE","domain_label_choice",
              "Quel label veux-tu préparer pour ce domaine ?",
              DOMAIN_LABEL_CHOICES,
              extra={
                "parent_domain":s["answers"].get("domain_parent_selection"),
                "suggested_fqdns":[f"{label}.{s['answers'].get('domain_parent_selection')}" for label in DOMAIN_LABEL_CHOICES if label not in {"OTHER_CUSTOM","DECIDE_LATER"}],
                "execution_authority_granted":False
              }
            );return s

        if "domain_binding" not in s["answers"] and domain_intent in {"CREATE_SUBDOMAIN","CREATE_CHILD_DOMAIN"} and s["answers"].get("domain_label_choice")=="OTHER_CUSTOM" and "domain_label_custom" not in s["answers"]:
            s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_DOMAIN_LABEL_CUSTOM"
            s["next_request"]=q(
              "Q_DOMAIN_LABEL_CUSTOM","domain_label_custom",
              "Quel label personnalisé veux-tu utiliser ?",
              typ="string",
              extra={"parent_domain":s["answers"].get("domain_parent_selection"),"execution_authority_granted":False}
            );return s

        if "domain_binding" not in s["answers"] and domain_intent=="CREATE_NEW_ROOT_DOMAIN" and "domain_root_name_mode" not in s["answers"]:
            s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_DOMAIN_ROOT_NAME_MODE"
            s["next_request"]=q(
              "Q_DOMAIN_ROOT_NAME_MODE","domain_root_name_mode",
              "Comment veux-tu déterminer le nom du nouveau domaine racine ?",
              DOMAIN_ROOT_NAME_MODES,
              extra={"selected_server":selected,"execution_authority_granted":False}
            );return s

        if "domain_binding" not in s["answers"] and domain_intent=="CREATE_NEW_ROOT_DOMAIN" and s["answers"].get("domain_root_name_mode")=="CUSTOM_NAME" and "domain_root_name" not in s["answers"]:
            s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_DOMAIN_ROOT_NAME"
            s["next_request"]=q(
              "Q_DOMAIN_ROOT_NAME","domain_root_name",
              "Quel nom de domaine racine veux-tu préparer ?",
              typ="string",
              extra={"selected_server":selected,"execution_authority_granted":False}
            );return s

        if "domain_binding" not in s["answers"]:
            binding=derive_domain_binding(s)
            if binding is None:
                if (
                  domain_intent in {"CREATE_SUBDOMAIN","CREATE_CHILD_DOMAIN"}
                  and s["answers"].get("domain_parent_selection")=="DECIDE_LATER"
                ):
                    binding={"mode":"UNRESOLVED","kind":domain_intent,"reason":"PARENT_DECIDE_LATER","server":selected}
                elif (
                  domain_intent in {"CREATE_SUBDOMAIN","CREATE_CHILD_DOMAIN"}
                  and s["answers"].get("domain_label_choice")=="DECIDE_LATER"
                ):
                    binding={"mode":"UNRESOLVED","kind":domain_intent,"reason":"LABEL_DECIDE_LATER","server":selected}
                elif domain_intent=="REUSE_EXISTING_DOMAIN" and s["answers"].get("domain_existing_selection")=="DECIDE_LATER":
                    binding={"mode":"UNRESOLVED","kind":"EXISTING_DOMAIN","reason":"DECIDE_LATER","server":selected}
            if binding is not None:
                s["answers"]["domain_binding"]=binding
            else:
                raise RuntimeError("DOMAIN_BINDING_DERIVATION_INCOMPLETE")

        if (
          domain_intent=="REUSE_EXISTING_DOMAIN"
          and s["answers"].get("domain_existing_selection") not in {None,"DECIDE_LATER"}
        ):
            if "deployment_mount_mode" not in s["answers"]:
                host=s["answers"].get("domain_existing_selection")
                s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_DEPLOYMENT_MOUNT_MODE"
                s["next_request"]=q(
                  "Q_DEPLOYMENT_MOUNT_MODE","deployment_mount_mode",
                  "Comment veux-tu monter l'application sur ce host existant ?",
                  DEPLOYMENT_MOUNT_MODES,
                  extra={
                    "host":host,
                    "examples":{
                      "HOST_ROOT":f"https://{host}/",
                      "CREATE_PATH":f"https://{host}/ekyc",
                      "REUSE_EXISTING_PATH":f"https://{host}/<chemin-existant>"
                    },
                    "decision_kind":"OWNER_DEPLOYMENT_MOUNT",
                    "execution_authority_granted":False
                  }
                );return s
            mount=s["answers"].get("deployment_mount_mode")
            if mount in {"CREATE_PATH","REUSE_EXISTING_PATH"} and "deployment_path" not in s["answers"]:
                host=s["answers"].get("domain_existing_selection")
                s["status"]="WAITING_FOR_SETUP_ANSWER";s["phase"]="Q_DEPLOYMENT_PATH"
                s["next_request"]=q(
                  "Q_DEPLOYMENT_PATH","deployment_path",
                  "Quel chemin HTTP veux-tu utiliser sur ce host ? Indique un chemin comme /ekyc.",
                  typ="string",
                  extra={
                    "host":host,
                    "mount_mode":mount,
                    "path_is_not_dns_name":True,
                    "execution_authority_granted":False
                  }
                );return s
            if "deployment_binding" not in s["answers"]:
                deployment=derive_deployment_binding(s)
                if deployment is None:
                    raise RuntimeError("DEPLOYMENT_BINDING_DERIVATION_INCOMPLETE")
                s["answers"]["deployment_binding"]=deployment

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
    request=s.get("next_request") or {}
    if request.get("field")!=field:raise ValueError(f"unexpected field {field}")
    err=validate(field,value)
    if err:raise ValueError(err)
    if request.get("id") in {"Q_MCP_ENDPOINT_RECOVERY","Q_SSH_PROFILE_RECOVERY"}:
        current=s.get("mcp_discovery")
        history=list(s.get("mcp_discovery_history") or [])[-4:]
        if isinstance(current,dict):
            history.append({
              "reason":"MCP_ENDPOINT_CORRECTION_AFTER_DISCOVERY_FAILURE" if request.get("id")=="Q_MCP_ENDPOINT_RECOVERY" else "SSH_PROFILE_CORRECTION_AFTER_SIGNED_BROKER_MISMATCH",
              "evidence":copy.deepcopy(current)
            })
        s["mcp_discovery_history"]=history
        s["mcp_discovery"]=None
        s["hold_reason"]=None
        s["answers"].pop("mcp_discovery_approved",None)
    s["answers"][field]=value;s["revision"]+=1
    return refresh(s)

def reconcile_legacy_discovery_authority(s):
    s=copy.deepcopy(s)
    if s.get("mode")!="FIRST_AGENT_BOOTSTRAP":
        return s
    a=s.get("answers") or {}
    if a.get("link_mcp_server") is not True or "mcp_discovery_approved" in a:
        return s
    request=s.get("next_request") or {}
    evidence=s.get("mcp_discovery")
    legacy=(s.get("phase")=="MCP_DISCOVERY" or request.get("kind")=="MCP_DISCOVERY" or isinstance(evidence,dict))
    if not legacy:
        return s
    if isinstance(evidence,dict):
        history=list(s.get("mcp_discovery_history") or [])[-4:]
        history.append({
          "reason":"DISCOVERY_EXECUTED_BEFORE_EXPLICIT_APPROVAL_GATE",
          "evidence":copy.deepcopy(evidence)
        })
        s["mcp_discovery_history"]=history
    s["mcp_discovery"]=None
    s["hold_reason"]=None
    s["revision"]=int(s.get("revision") or 0)+1
    return refresh(s)

def reconcile_both_smart_routing(s):
    s=copy.deepcopy(s)
    a=s.get("answers") or {}
    if s.get("mode")!="FIRST_AGENT_BOOTSTRAP" or a.get("mcp_transport")!="BOTH":
        return s
    if isinstance(s.get("mcp_discovery"),dict):
        return s

    endpoint=a.get("mcp_endpoint")
    for item in reversed(s.get("mcp_discovery_history") or []):
        evidence=item.get("evidence") if isinstance(item,dict) else None
        if not isinstance(evidence,dict):
            continue
        direct=evidence.get("direct_mcp")
        if (
            item.get("reason")=="SSH_PROFILE_CORRECTION_AFTER_SIGNED_BROKER_MISMATCH"
            and isinstance(direct,dict)
            and direct.get("status") in {"PASS","PARTIAL"}
            and evidence.get("endpoint")==endpoint
        ):
            selected={
              "transport":"BOTH",
              "endpoint":endpoint,
              "observed_at":evidence.get("observed_at"),
              "routing_mode":"DUAL_READY_SMART_ROUTING",
              "configured_transports":["DIRECT_MCP_TOKEN","SSH"],
              "routing_policy":"PREFER_DIRECT_WHEN_READY_ELSE_SSH_FALLBACK",
              "simultaneous_execution_required":False,
              "selected_transport":"DIRECT_MCP_TOKEN",
              "selection_reason":"REUSED_PREVIOUSLY_AUTHORIZED_DIRECT_ROUTE_EVIDENCE",
              "direct_mcp":copy.deepcopy(direct),
              "ssh_certificate":{
                "status":"CONFIGURED_NOT_ATTESTED",
                "reason":"ALTERNATE_ROUTE_PROFILE_CORRECTED_AFTER_PRIOR_DIRECT_SUCCESS"
              },
              "status":direct.get("status"),
              "degraded":direct.get("status")=="PARTIAL",
              "fallback_used":False,
              "alternate_transport_status":"CONFIGURED_NOT_ATTESTED",
              "reused_authorized_evidence":True
            }
            s["mcp_discovery"]=selected
            s["hold_reason"]=None
            s["revision"]=int(s.get("revision") or 0)+1
            return refresh(s)
    return s


def mark_credentials_verified(s):
    s=copy.deepcopy(s)
    if (s.get("next_request") or {}).get("kind")!="CREDENTIAL_GATE":raise ValueError("not at credential gate")
    s["credentials_verified"]=True;s["revision"]+=1
    return refresh(s)

def both_discovery_needs_refresh(s,direct_credential_available):
    # BOTH means both routes are configured for smart selection/fallback.
    # Availability of the alternate route must not invalidate a successful
    # current discovery or block setup merely to force dual execution.
    return False

def require_mcp_discovery_refresh(s,reason):
    s=copy.deepcopy(s)
    current=s.get("mcp_discovery")
    if not isinstance(current,dict):
        raise ValueError("no MCP discovery evidence to refresh")
    history=list(s.get("mcp_discovery_history") or [])[-4:]
    history.append({"reason":reason,"evidence":copy.deepcopy(current)})
    s["mcp_discovery_history"]=history
    s["mcp_discovery"]=None
    s["hold_reason"]=None
    s["revision"]+=1
    s=refresh(s)
    if (s.get("next_request") or {}).get("kind")!="MCP_DISCOVERY":
        raise ValueError("MCP discovery refresh did not reach discovery gate")
    s["next_request"]["refresh_reason"]=reason
    return s

def record_mcp_discovery(s,evidence):
    s=copy.deepcopy(s)
    if (s.get("next_request") or {}).get("kind")!="MCP_DISCOVERY":raise ValueError("not awaiting MCP discovery")
    s["mcp_discovery"]=evidence;s["hold_reason"]=None;s["revision"]+=1
    return refresh(s)

def record_mcp_discovery_failure(s,evidence):
    s=copy.deepcopy(s)
    if (s.get("next_request") or {}).get("kind")!="MCP_DISCOVERY":raise ValueError("not awaiting MCP discovery")
    code=str((evidence or {}).get("failure_code") or "MCP_DISCOVERY_FAILED")
    s["mcp_discovery"]=copy.deepcopy(evidence)
    s["hold_reason"]=code
    s["revision"]+=1
    if code.startswith("HTTP Error 404"):
        s["status"]="WAITING_FOR_SETUP_ANSWER"
        s["phase"]="Q_MCP_ENDPOINT_RECOVERY"
        s["next_request"]=q(
          "Q_MCP_ENDPOINT_RECOVERY",
          "mcp_endpoint",
          "La découverte MCP a reçu HTTP 404. Corrige ou confirme l'URL exacte du endpoint MCP avant de relancer la découverte.",
          extra={"last_failure":copy.deepcopy(evidence)}
        )
        return s
    if code=="SSH_PROFILE_MISMATCH" and isinstance((evidence or {}).get("observed_ssh_profile"),dict):
        observed=copy.deepcopy(evidence["observed_ssh_profile"])
        s["status"]="WAITING_FOR_SETUP_ANSWER"
        s["phase"]="Q_SSH_PROFILE_RECOVERY"
        s["next_request"]=q(
          "Q_SSH_PROFILE_RECOVERY",
          "ssh_connection_profile",
          "Le profil SSH configuré ne correspond pas au profil signé par le broker MCP. Utilise le profil observé et signé avant de relancer la découverte.",
          typ="object",
          extra={"last_failure":copy.deepcopy(evidence),"observed_ssh_profile":observed}
        )
        return s
    s["status"]="MCP_DISCOVERY_FAILED_RETRYABLE"
    s["phase"]="MCP_DISCOVERY"
    s["next_request"]={
      "kind":"MCP_DISCOVERY",
      "id":"MCP_DISCOVERY",
      "text":"Read-only MCP discovery failed. Retry after remediation with /local-execute.",
      "tools":["ping","get_project_context","list_domains_s1","list_domains_s2","get_write_tools_context"],
      "last_failure":copy.deepcopy(evidence)
    }
    return s

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
    s.setdefault("setup_package",None);s.setdefault("mcp_discovery",None);s.setdefault("mcp_discovery_history",[]);s.setdefault("credentials_verified",False)
    return s
