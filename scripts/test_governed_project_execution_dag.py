#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

import governed_loop_execution_adapter as loop
import governed_project_execution_blueprint as bp
from governed_execution_engine import REGISTRY_PATH,SNAPSHOT_PATH,load_json
from governed_execution_package_compiler import SERVER_MODEL_PATH

REGISTRY=load_json(REGISTRY_PATH)
SNAPSHOT=load_json(SNAPSHOT_PATH)
SERVER_MODEL=load_json(SERVER_MODEL_PATH)


def ekyc_spec():
    return {
        "schema_version":"1.0.0",
        "blueprint_id":"BP-EKYC-TEST",
        "project_id":"ekyc",
        "repository":"Patricked-code/Ekyc",
        "expected_head":"a"*40,
        "server_id":"S2",
        "environment":"production",
        "authority":{
            "approved":True,
            "grants":["SCOPED_FULL_LIFECYCLE"],
            "scope":{"project_id":"ekyc","server_id":"S2","environment":"production"},
            "decision_ref":"OWNER-EKYC-TEST",
        },
        "github":{
            "environment":"production",
            "secrets":[
                {"name":"DATABASE_URL","value_ref":"generated:32","environment":"production"}
            ],
        },
        "domain":{
            "mode":"SUBDOMAIN",
            "parent_domain":"chainsolutions.fr",
            "label":"ekyc",
        },
        "runtime":{
            "requires_port":True,
            "reverse_proxy":True,
        },
        "database":{
            "required":True,
            "engine":"postgresql",
        },
        "application_secrets":["DATABASE_URL"],
    }


def inventory():
    return {
        "authority_id":"CP-SERVER-KNOWLEDGE-001",
        "servers":{
            "S2":{
                "DOMAINS_VHOSTS":{
                    "status":"KNOWN_CURRENT",
                    "facts":{"domains":["chainsolutions.fr"]},
                }
            }
        }
    }


def github_metadata():
    return {
        "repository_secrets":{"status":"KNOWN_CURRENT","items":[]},
        "environments":[
            {"name":"production","secrets":{"status":"KNOWN_CURRENT","items":[]}}
        ],
    }


def build():
    return bp.build_blueprint(
        ekyc_spec(),
        registry=REGISTRY,
        snapshot=SNAPSHOT,
        server_model=SERVER_MODEL,
        server_inventory=inventory(),
        github_metadata=github_metadata(),
    )


def assert_blueprint_derivation():
    result=build()
    if result["domain"]!="ekyc.chainsolutions.fr":
        raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: FQDN")
    ids=[n["node_id"] for n in result["nodes"]]
    required={
        "GITHUB-ENV","GITHUB-SECRET-01","SERVER-DIRECTORY","SERVER-PORT",
        "DOMAIN-CREATE","DOMAIN-PROXY","DOMAIN-TLS","DATABASE-CREATE",
        "DATABASE-CREDENTIAL","APP-SECRETS","REPOSITORY-BIND","SERVICE-CONFIG",
        "DEPLOY","OBSERVABILITY","BACKUP","ATTEST",
    }
    if required-set(ids):
        raise SystemExit(f"PROJECT_EXECUTION_DAG_TEST_FAILED: missing nodes {sorted(required-set(ids))}")
    domain=next(n for n in result["nodes"] if n["node_id"]=="DOMAIN-CREATE")
    if domain["package"]["parameters"].get("domain")!="ekyc.chainsolutions.fr":
        raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: subdomain package")
    if domain["compile_status"]!="BLOCKED":
        raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: subdomain must stay blocked on current MCP gaps")
    blockers=set(domain["blockers"])
    if not ({"WEB_HOSTING_CHANGE","DOMAIN_DNS_CHANGE","TLS_CHANGE"} & blockers):
        raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: missing subdomain capability gap")

    serialized=json.dumps(result)
    if "generated:32" not in serialized:
        raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: secret reference should persist")
    for leak in ["ghp_","github_pat_","-----BEGIN PRIVATE KEY-----"]:
        if leak in serialized:
            raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: secret-like leak")

    if result["status"]!="COMPILED_WITH_BLOCKERS":
        raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: expected blockers")
    if result["execution_authority_granted"] is not False:
        raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: blueprint granted authority")


def assert_loop_single_writer_and_dependencies():
    blueprint=build()
    state=loop.initialize_state(blueprint)
    evaluation=loop.evaluate(blueprint,state,registry=REGISTRY,snapshot=SNAPSHOT)
    if evaluation["status"]!="READY":
        raise SystemExit(f"PROJECT_EXECUTION_DAG_TEST_FAILED: loop initial status {evaluation['status']}")
    if evaluation["next_executable"]["node_id"]!="GITHUB-ENV":
        raise SystemExit(f"PROJECT_EXECUTION_DAG_TEST_FAILED: expected GITHUB-ENV first {evaluation['next_executable']}")
    if evaluation["single_writer_selection"] is not True:
        raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: no single writer")

    receipt={
        "operation_id":"GITHUB-ENV",
        "status":"PASS",
        "completed_at":"2026-10-01T00:00:00+00:00",
        "receipt_ref":"TEST:GITHUB-ENV",
    }
    state2=loop.apply_receipt(blueprint,state,receipt,expected_revision=0)
    if state2["revision"]!=1 or state2["nodes"]["GITHUB-ENV"]["status"]!="DONE":
        raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: receipt projection")
    evaluation2=loop.evaluate(blueprint,state2,registry=REGISTRY,snapshot=SNAPSHOT)
    if evaluation2["next_executable"]["node_id"]!="GITHUB-SECRET-01":
        raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: secret should unlock after environment")

    receipt2={
        "operation_id":"GITHUB-SECRET-01",
        "status":"PASS",
        "completed_at":"2026-10-01T00:01:00+00:00",
    }
    state3=loop.apply_receipt(blueprint,state2,receipt2,expected_revision=1)
    evaluation3=loop.evaluate(blueprint,state3,registry=REGISTRY,snapshot=SNAPSHOT)
    if evaluation3["next_executable"] is not None:
        raise SystemExit(f"PROJECT_EXECUTION_DAG_TEST_FAILED: should stop on current server capability gaps {evaluation3['next_executable']}")
    blocked_ids={item["node_id"] for item in evaluation3["blocked"]}
    if "SERVER-DIRECTORY" not in blocked_ids:
        raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: filesystem gap not surfaced")
    waiting_ids={item["node_id"] for item in evaluation3["waiting"]}
    if "REPOSITORY-BIND" not in blocked_ids and "REPOSITORY-BIND" not in waiting_ids:
        raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: repo binding not retained")

    try:
        loop.apply_receipt(blueprint,state3,{"operation_id":"GITHUB-SECRET-01","status":"PASS"},expected_revision=1)
    except loop.LoopBindingError as exc:
        if str(exc)!="LOOP_STATE_REVISION_MOVED":
            raise
    else:
        raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: stale revision accepted")


def assert_package_materialization_boundary():
    blueprint=build()
    state=loop.initialize_state(blueprint)
    evaluation=loop.evaluate(blueprint,state,registry=REGISTRY,snapshot=SNAPSHOT)
    with tempfile.TemporaryDirectory() as td:
        try:
            loop.materialize_next_package(evaluation,Path(td))
        except loop.LoopBindingError as exc:
            if str(exc)!="LOOP_PACKAGE_OUTPUT_OUTSIDE_GOVERNED_DIRECTORY":
                raise
        else:
            raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: package escaped governed directory")


def assert_secret_value_rejection():
    spec=ekyc_spec()
    spec["github"]["secrets"][0]["secret_value"]="plaintext"
    try:
        bp.build_blueprint(
            spec,registry=REGISTRY,snapshot=SNAPSHOT,server_model=SERVER_MODEL,
            server_inventory=inventory(),github_metadata=github_metadata(),
        )
    except bp.BlueprintError as exc:
        if not str(exc).startswith("BLUEPRINT_SECRET_VALUE_FORBIDDEN"):
            raise
    else:
        raise SystemExit("PROJECT_EXECUTION_DAG_TEST_FAILED: plaintext secret accepted")


def main():
    assert_blueprint_derivation()
    assert_loop_single_writer_and_dependencies()
    assert_package_materialization_boundary()
    assert_secret_value_rejection()
    print("PROJECT_EXECUTION_DAG_LOOP_TEST_PASS")


if __name__=="__main__":
    main()
