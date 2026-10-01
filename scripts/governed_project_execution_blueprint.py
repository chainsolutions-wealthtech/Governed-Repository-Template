#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any

from governed_execution_engine import ROOT, REGISTRY_PATH, SNAPSHOT_PATH, load_json
from governed_execution_package_compiler import (
    SERVER_MODEL_PATH,
    compile_request,
)

SPEC_VERSION="1.0.0"
REPO_RE=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA_RE=re.compile(r"^[0-9a-f]{40}$")
ID_RE=re.compile(r"^[A-Za-z0-9_.-]{1,128}$")
DOMAIN_RE=re.compile(r"^(?=.{4,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{1,62}$")
LABEL_RE=re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")

FORBIDDEN_VALUE_KEYS={"secret","secret_value","password","token","private_key","credential_value"}


class BlueprintError(ValueError):
    pass


def _reject_secret_values(value: Any, path="$") -> None:
    if isinstance(value,dict):
        for key,item in value.items():
            lowered=str(key).lower()
            if lowered in FORBIDDEN_VALUE_KEYS and not lowered.endswith("_ref") and item not in (None,"","***"):
                raise BlueprintError(f"BLUEPRINT_SECRET_VALUE_FORBIDDEN:{path}.{key}")
            _reject_secret_values(item,f"{path}.{key}")
    elif isinstance(value,list):
        for idx,item in enumerate(value):
            _reject_secret_values(item,f"{path}[{idx}]")
    elif isinstance(value,str):
        if value.startswith(("ghp_","github_pat_","-----BEGIN PRIVATE KEY-----")):
            raise BlueprintError(f"BLUEPRINT_SECRET_LIKE_VALUE_FORBIDDEN:{path}")


def validate_spec(spec:dict)->None:
    _reject_secret_values(spec)
    if spec.get("schema_version")!=SPEC_VERSION:
        raise BlueprintError("BLUEPRINT_SPEC_VERSION_UNSUPPORTED")
    project_id=spec.get("project_id")
    repository=spec.get("repository")
    expected_head=spec.get("expected_head")
    server_id=spec.get("server_id")
    if not isinstance(project_id,str) or not ID_RE.fullmatch(project_id):
        raise BlueprintError("BLUEPRINT_PROJECT_ID_INVALID")
    if not isinstance(repository,str) or not REPO_RE.fullmatch(repository):
        raise BlueprintError("BLUEPRINT_REPOSITORY_INVALID")
    if not isinstance(expected_head,str) or not SHA_RE.fullmatch(expected_head):
        raise BlueprintError("BLUEPRINT_EXPECTED_HEAD_INVALID")
    if server_id not in {"S1","S2"}:
        raise BlueprintError("BLUEPRINT_SERVER_ID_INVALID")
    authority=spec.get("authority")
    if not isinstance(authority,dict):
        raise BlueprintError("BLUEPRINT_AUTHORITY_REQUIRED")
    if not isinstance(authority.get("grants"),list):
        raise BlueprintError("BLUEPRINT_AUTHORITY_GRANTS_INVALID")
    if authority.get("approved") not in {True,False}:
        raise BlueprintError("BLUEPRINT_AUTHORITY_APPROVED_INVALID")

    domain=spec.get("domain") or {}
    mode=domain.get("mode","NONE")
    if mode not in {"NONE","SUBDOMAIN","NEW_DOMAIN","EXISTING"}:
        raise BlueprintError("BLUEPRINT_DOMAIN_MODE_INVALID")
    if mode=="SUBDOMAIN":
        if not DOMAIN_RE.fullmatch(str(domain.get("parent_domain") or "")):
            raise BlueprintError("BLUEPRINT_PARENT_DOMAIN_INVALID")
        if not LABEL_RE.fullmatch(str(domain.get("label") or "")):
            raise BlueprintError("BLUEPRINT_SUBDOMAIN_LABEL_INVALID")
    elif mode in {"NEW_DOMAIN","EXISTING"}:
        if not DOMAIN_RE.fullmatch(str(domain.get("domain") or "")):
            raise BlueprintError("BLUEPRINT_DOMAIN_INVALID")

    github=spec.get("github") or {}
    for secret in github.get("secrets") or []:
        if not isinstance(secret,dict) or not secret.get("name") or not secret.get("value_ref"):
            raise BlueprintError("BLUEPRINT_GITHUB_SECRET_REFERENCE_INVALID")
        if not str(secret.get("value_ref")).startswith(("env:","runtime:","generated:")):
            raise BlueprintError("BLUEPRINT_GITHUB_SECRET_REFERENCE_SCHEME_INVALID")

    database=spec.get("database") or {}
    if database.get("required") is True and not database.get("engine"):
        raise BlueprintError("BLUEPRINT_DATABASE_ENGINE_REQUIRED")


def _authority_for(spec:dict,intent:str,registry:dict)->dict:
    intent_spec=registry["intents"][intent]
    base=copy.deepcopy(spec["authority"])
    grants=list(base.get("grants") or [])
    required=intent_spec.get("required_authority")
    if intent_spec.get("side_effecting") and required not in grants and "SCOPED_FULL_LIFECYCLE" not in grants:
        base["approved"]=False
    base.setdefault("scope",{})
    base["scope"].setdefault("project_id",spec["project_id"])
    base["scope"].setdefault("server_id",spec["server_id"])
    return base


def _request(spec:dict,registry:dict,node_id:str,intent:str,**kwargs)->dict:
    request={
        "schema_version":"1.0.0",
        "request_id":node_id,
        "operation_id":node_id,
        "project_id":spec["project_id"],
        "intent":intent,
        "repository":spec["repository"],
        "expected_head":spec["expected_head"],
        "server_id":spec["server_id"],
        "environment":spec.get("environment","production"),
        "authority":_authority_for(spec,intent,registry),
        "decision_ref":(spec.get("authority") or {}).get("decision_ref"),
    }
    request.update(copy.deepcopy(kwargs))
    return request


def _fqdn(spec:dict)->str|None:
    d=spec.get("domain") or {}
    if d.get("mode")=="SUBDOMAIN":
        return f"{d['label']}.{d['parent_domain']}".lower()
    if d.get("mode") in {"NEW_DOMAIN","EXISTING"}:
        return str(d.get("domain")).lower()
    return None


def derive_nodes(spec:dict,registry:dict)->list[dict]:
    validate_spec(spec)
    nodes=[]
    def add(node_id,intent,deps=None,**kwargs):
        nodes.append({
            "node_id":node_id,
            "intent":intent,
            "depends_on":list(deps or []),
            "request":_request(spec,registry,node_id,intent,**kwargs),
        })

    github=spec.get("github") or {}
    gh_env=github.get("environment")
    if gh_env:
        add("GITHUB-ENV","GITHUB_CONFIGURE_ENVIRONMENT",environment=gh_env,
            parameters={"repository":spec["repository"],"environment":gh_env})
    for idx,secret in enumerate(github.get("secrets") or [],1):
        node=f"GITHUB-SECRET-{idx:02d}"
        params={
            "repository":spec["repository"],
            "secret_name":secret["name"],
            "value_ref":secret["value_ref"],
        }
        if secret.get("environment") or gh_env:
            params["environment"]=secret.get("environment") or gh_env
        add(node,"PROVISION_GITHUB_SECRET",deps=["GITHUB-ENV"] if gh_env else [],parameters=params,
            secret_name=secret["name"],value_ref=secret["value_ref"],
            environment=params.get("environment"))

    add("SERVER-DIRECTORY","CREATE_PROJECT_DIRECTORY")

    runtime=spec.get("runtime") or {}
    if runtime.get("requires_port",True):
        add("SERVER-PORT","ALLOCATE_APPLICATION_PORT",deps=["SERVER-DIRECTORY"])

    domain=spec.get("domain") or {}
    fqdn=_fqdn(spec)
    domain_root=[]
    if domain.get("mode")=="SUBDOMAIN":
        add("DOMAIN-CREATE","CREATE_SUBDOMAIN",deps=["SERVER-DIRECTORY"],
            parent_domain=domain["parent_domain"],subdomain_label=domain["label"])
        domain_root=["DOMAIN-CREATE"]
    elif domain.get("mode")=="NEW_DOMAIN":
        add("DOMAIN-CREATE","CREATE_NEW_DOMAIN_BINDING",deps=["SERVER-DIRECTORY"],domain=fqdn)
        domain_root=["DOMAIN-CREATE"]
    elif domain.get("mode")=="EXISTING":
        domain_root=[]

    if fqdn and runtime.get("reverse_proxy",True):
        deps=list(domain_root)
        if runtime.get("requires_port",True):
            deps.append("SERVER-PORT")
        backend=runtime.get("backend_target") or "DERIVE_FROM_ALLOCATED_PORT"
        add("DOMAIN-PROXY","CONFIGURE_REVERSE_PROXY",deps=deps,domain=fqdn,backend_target=backend)
        add("DOMAIN-TLS","PROVISION_TLS",deps=["DOMAIN-PROXY"],domain=fqdn)

    database=spec.get("database") or {}
    if database.get("required"):
        add("DATABASE-CREATE","CREATE_DATABASE",deps=["SERVER-DIRECTORY"],
            database_engine=database["engine"])
        add("DATABASE-CREDENTIAL","CREATE_DATABASE_CREDENTIAL",deps=["DATABASE-CREATE"],
            database_engine=database["engine"])

    secret_deps=[n["node_id"] for n in nodes if n["node_id"].startswith("GITHUB-SECRET-")]
    if database.get("required"):
        secret_deps.append("DATABASE-CREDENTIAL")
    app_secret_required=bool(spec.get("application_secrets")) or bool(secret_deps)
    if app_secret_required:
        add("APP-SECRETS","CONFIGURE_ENV_AND_SECRETS",deps=secret_deps)

    bind_deps=["SERVER-DIRECTORY"]
    add("REPOSITORY-BIND","BIND_REPOSITORY_TO_SERVER_PROJECT",deps=bind_deps)

    service_deps=["REPOSITORY-BIND"]
    if runtime.get("requires_port",True):
        service_deps.append("SERVER-PORT")
    if app_secret_required:
        service_deps.append("APP-SECRETS")
    add("SERVICE-CONFIG","CONFIGURE_PROCESS_OR_SERVICE",deps=service_deps)

    deploy_deps=["SERVICE-CONFIG"]
    if database.get("required"):
        deploy_deps.append("DATABASE-CREATE")
    if fqdn:
        deploy_deps.append("DOMAIN-TLS" if runtime.get("reverse_proxy",True) else domain_root[0] if domain_root else "REPOSITORY-BIND")
    add("DEPLOY","DEPLOY_APPLICATION",deps=sorted(set(deploy_deps)))

    add("OBSERVABILITY","CONFIGURE_OBSERVABILITY",deps=["DEPLOY"])
    add("BACKUP","CONFIGURE_BACKUP_AND_ROLLBACK",deps=["DEPLOY"] + (["DATABASE-CREATE"] if database.get("required") else []))
    attest_deps=["DEPLOY","OBSERVABILITY","BACKUP"]
    add("ATTEST","PRODUCTION_ATTESTATION",deps=attest_deps,domain=fqdn)

    return nodes


def validate_dag(nodes:list[dict])->None:
    ids={n["node_id"] for n in nodes}
    if len(ids)!=len(nodes):
        raise BlueprintError("BLUEPRINT_DUPLICATE_NODE")
    for node in nodes:
        unknown=set(node["depends_on"])-ids
        if unknown:
            raise BlueprintError("BLUEPRINT_UNKNOWN_DEPENDENCY:"+",".join(sorted(unknown)))
    visiting=set()
    done=set()
    by_id={n["node_id"]:n for n in nodes}
    def visit(node_id):
        if node_id in done:return
        if node_id in visiting:raise BlueprintError("BLUEPRINT_CYCLE")
        visiting.add(node_id)
        for dep in by_id[node_id]["depends_on"]:visit(dep)
        visiting.remove(node_id);done.add(node_id)
    for node_id in ids:visit(node_id)


def build_blueprint(spec:dict,*,registry:dict,snapshot:dict,server_model:dict,
                    server_inventory:dict|None=None,github_metadata:dict|None=None)->dict:
    nodes=derive_nodes(spec,registry)
    validate_dag(nodes)
    compiled=[]
    for node in nodes:
        result=compile_request(
            node["request"],
            registry=registry,
            snapshot=snapshot,
            server_model=server_model,
            server_inventory=server_inventory,
            github_metadata=github_metadata,
        )
        compiled.append({
            "node_id":node["node_id"],
            "intent":node["intent"],
            "depends_on":node["depends_on"],
            "compile_status":result["status"],
            "blockers":copy.deepcopy(result.get("blockers") or []),
            "missing_inputs":copy.deepcopy(result.get("missing_inputs") or []),
            "required_inventory":copy.deepcopy(result.get("required_inventory") or []),
            "package":copy.deepcopy(result["package"]),
            "notes":copy.deepcopy(result.get("notes") or []),
        })
    blocked=sum(1 for n in compiled if n["compile_status"] not in {"READY"})
    ready=sum(1 for n in compiled if n["compile_status"]=="READY")
    return {
        "schema_version":"1.0.0",
        "authority_id":"CP-EXECUTION-001",
        "blueprint_id":spec.get("blueprint_id") or f"BP-{spec['project_id']}",
        "project_id":spec["project_id"],
        "repository":spec["repository"],
        "expected_head":spec["expected_head"],
        "server_id":spec["server_id"],
        "environment":spec.get("environment","production"),
        "domain":_fqdn(spec),
        "status":"COMPILED_READY" if blocked==0 else "COMPILED_WITH_BLOCKERS",
        "node_count":len(compiled),
        "ready_count":ready,
        "blocked_count":blocked,
        "nodes":compiled,
        "execution_authority_granted":False,
        "secret_values_persisted":False,
        "notes":[
            "Blueprint compilation does not grant execution authority.",
            "Each node keeps its own authority package and exact-head guard.",
            "Blocked MCP capabilities stay explicit; no intake is created automatically.",
        ],
    }


def main():
    parser=argparse.ArgumentParser(description="Compile project decisions into a governed execution DAG.")
    parser.add_argument("--spec",type=Path,required=True)
    parser.add_argument("--server-inventory",type=Path)
    parser.add_argument("--github-metadata",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    result=build_blueprint(
        load_json(args.spec),
        registry=load_json(REGISTRY_PATH),
        snapshot=load_json(SNAPSHOT_PATH),
        server_model=load_json(SERVER_MODEL_PATH),
        server_inventory=load_json(args.server_inventory) if args.server_inventory else None,
        github_metadata=load_json(args.github_metadata) if args.github_metadata else None,
    )
    rendered=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
    if args.output:
        out=args.output.resolve()
        if ROOT not in out.parents:raise SystemExit("BLUEPRINT_OUTPUT_OUTSIDE_REPOSITORY")
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(rendered,encoding="utf-8")
    print(rendered,end="")


if __name__=="__main__":
    main()
