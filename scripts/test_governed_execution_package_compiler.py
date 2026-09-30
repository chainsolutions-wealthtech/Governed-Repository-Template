#!/usr/bin/env python3
from __future__ import annotations

import copy
import json

import governed_execution_package_compiler as c
from governed_execution_engine import load_json, REGISTRY_PATH, SNAPSHOT_PATH

REGISTRY=load_json(REGISTRY_PATH)
SNAPSHOT=load_json(SNAPSHOT_PATH)
SERVER_MODEL=load_json(c.SERVER_MODEL_PATH)

def request(intent, **kwargs):
    data={
        "schema_version":"1.0.0",
        "request_id":f"REQ-{intent}",
        "project_id":kwargs.pop("project_id","brvmchainsolution"),
        "intent":intent,
        "authority":{
            "approved":True,
            "grants":[REGISTRY["intents"][intent]["required_authority"]],
            "scope":{"project_id":kwargs.get("project_id","brvmchainsolution")},
            "decision_ref":"TEST-DECISION-001",
        },
    }
    data.update(kwargs)
    return data

def server_inventory():
    return {
        "authority_id":"CP-SERVER-KNOWLEDGE-001",
        "servers":{
            "S2":{
                "DOMAINS_VHOSTS":{
                    "status":"KNOWN_CURRENT",
                    "facts":{"domains":["chainsolutions.fr","africafunds.chainsolutions.fr"]},
                }
            }
        }
    }

def github_metadata(secret_names=None):
    return {
        "repository_secrets":{
            "status":"KNOWN_CURRENT",
            "items":[{"name":x} for x in (secret_names or [])],
        },
        "environments":[],
    }

def test_ekyc_subdomain_derivation_and_blockers():
    r=request(
        "CREATE_SUBDOMAIN",
        project_id="ekyc",
        server_id="S2",
        repository="Patricked-code/Ekyc",
        expected_head="a"*40,
        parent_domain="chainsolutions.fr",
        subdomain_label="ekyc",
    )
    out=c.compile_request(
        r, registry=REGISTRY, snapshot=SNAPSHOT, server_model=SERVER_MODEL,
        server_inventory=server_inventory(),
    )
    if out["package"]["parameters"].get("domain")!="ekyc.chainsolutions.fr":
        raise SystemExit("EXECUTION_PACKAGE_COMPILER_TEST_FAILED: Ekyc FQDN derivation")
    if out["status"]!="BLOCKED":
        raise SystemExit(f"EXECUTION_PACKAGE_COMPILER_TEST_FAILED: Ekyc subdomain should block on missing generic capability {out}")
    blockers=set(out.get("blockers") or [])
    if not ({"WEB_HOSTING_CHANGE","DOMAIN_DNS_CHANGE","TLS_CHANGE"} & blockers):
        raise SystemExit("EXECUTION_PACKAGE_COMPILER_TEST_FAILED: missing Ekyc capability blockers")
    if out["mcp_intake_required"] is not False:
        raise SystemExit("EXECUTION_PACKAGE_COMPILER_TEST_FAILED: compiler must not auto-create MCP intake")
    knowledge=[n for n in out["notes"] if n.get("code")=="PARENT_DOMAIN_OBSERVATION"]
    if not knowledge or knowledge[0].get("observed_on_server") is not True:
        raise SystemExit("EXECUTION_PACKAGE_COMPILER_TEST_FAILED: parent domain observation reuse")

def test_existing_s2_deploy_ready():
    r=request(
        "DEPLOY_APPLICATION",
        server_id="S2",
        repository="Wealthtechinnovations/BRVMCHAINSOLUTION",
        expected_head="b"*40,
        project_id="brvmchainsolution",
    )
    out=c.compile_request(r,registry=REGISTRY,snapshot=SNAPSHOT,server_model=SERVER_MODEL)
    if out["status"]!="READY":
        raise SystemExit(f"EXECUTION_PACKAGE_COMPILER_TEST_FAILED: known S2 project deploy should be READY {out}")
    steps=out["package"]["bindings"]["steps"]
    if [x["tool"] for x in steps["execute"]] != ["deploy_project_s2"]:
        raise SystemExit("EXECUTION_PACKAGE_COMPILER_TEST_FAILED: deploy binding")
    if [x["tool"] for x in steps["preflight"]] != ["git_status_project_s2"]:
        raise SystemExit("EXECUTION_PACKAGE_COMPILER_TEST_FAILED: deploy preflight")
    if [x["tool"] for x in steps["verify"]] != ["git_status_project_s2"]:
        raise SystemExit("EXECUTION_PACKAGE_COMPILER_TEST_FAILED: deploy verification")

def test_ekyc_not_silently_added_to_deploy_registry():
    r=request(
        "DEPLOY_APPLICATION",
        server_id="S2",
        repository="Patricked-code/Ekyc",
        expected_head="c"*40,
        project_id="ekyc",
    )
    out=c.compile_request(r,registry=REGISTRY,snapshot=SNAPSHOT,server_model=SERVER_MODEL)
    if out["status"]!="BLOCKED":
        raise SystemExit("EXECUTION_PACKAGE_COMPILER_TEST_FAILED: unknown Ekyc deployment registry should block")
    if "PROJECT_NOT_IN_CURRENT_MCP_DEPLOY_REGISTRY" not in out.get("blockers",[]):
        raise SystemExit("EXECUTION_PACKAGE_COMPILER_TEST_FAILED: missing registry blocker")

def test_s2_production_attestation_ready():
    r={
        "schema_version":"1.0.0",
        "request_id":"REQ-ATTEST",
        "project_id":"ekyc",
        "intent":"PRODUCTION_ATTESTATION",
        "server_id":"S2",
        "domain":"ekyc.chainsolutions.fr",
        "authority":{"approved":False,"grants":["READ_ONLY_DISCOVERY_AUTHORITY"],"scope":{"project_id":"ekyc"}},
    }
    out=c.compile_request(r,registry=REGISTRY,snapshot=SNAPSHOT,server_model=SERVER_MODEL)
    if out["status"]!="READY":
        raise SystemExit(f"EXECUTION_PACKAGE_COMPILER_TEST_FAILED: S2 attestation should be ready {out}")
    tools=[
        x["tool"]
        for phase in ("preflight","verify")
        for x in out["package"]["bindings"]["steps"][phase]
    ]
    for expected in ["check_disk_s2","docker_status_s2","pm2_status_s2","list_domains_s2","curl_domain"]:
        if expected not in tools:
            raise SystemExit(f"EXECUTION_PACKAGE_COMPILER_TEST_FAILED: missing {expected}")

def test_github_branch_package_ready():
    r=request(
        "GITHUB_CREATE_BRANCH",
        repository="owner/repo",
        expected_head="d"*40,
        parameters={"repository":"owner/repo","branch":"feature/test","source_sha":"d"*40},
    )
    out=c.compile_request(r,registry=REGISTRY,snapshot=SNAPSHOT,server_model=SERVER_MODEL)
    if out["status"]!="READY":
        raise SystemExit(f"EXECUTION_PACKAGE_COMPILER_TEST_FAILED: GitHub branch package {out}")

def test_secret_metadata_classification_without_value():
    r=request(
        "PROVISION_GITHUB_SECRET",
        repository="owner/repo",
        expected_head="e"*40,
        secret_name="API_TOKEN",
        value_ref="env:SOURCE_TOKEN",
    )
    out=c.compile_request(
        r,registry=REGISTRY,snapshot=SNAPSHOT,server_model=SERVER_MODEL,
        github_metadata=github_metadata(["API_TOKEN"]),
    )
    classes=[x for x in out["notes"] if x.get("kind")=="RESOURCE_CLASSIFICATION"]
    if not classes or classes[0].get("classification")!="ALIGN_OR_ROTATE":
        raise SystemExit("EXECUTION_PACKAGE_COMPILER_TEST_FAILED: existing secret classification")
    serialized=json.dumps(out)
    if "SOURCE_TOKEN_VALUE" in serialized:
        raise SystemExit("EXECUTION_PACKAGE_COMPILER_TEST_FAILED: secret value leak")
    if out["package"]["parameters"].get("value_ref")!="env:SOURCE_TOKEN":
        raise SystemExit("EXECUTION_PACKAGE_COMPILER_TEST_FAILED: secret reference not preserved")

def test_missing_expected_head_is_input_not_guess():
    r=request(
        "GITHUB_CREATE_BRANCH",
        repository="owner/repo",
        parameters={"repository":"owner/repo","branch":"feature/test","source_sha":"f"*40},
    )
    out=c.compile_request(r,registry=REGISTRY,snapshot=SNAPSHOT,server_model=SERVER_MODEL)
    if out["status"]!="NEEDS_INPUT" or "expected_head" not in out.get("missing_inputs",[]):
        raise SystemExit("EXECUTION_PACKAGE_COMPILER_TEST_FAILED: expected head must be explicit")

def test_invalid_subdomain_rejected():
    r=request(
        "CREATE_SUBDOMAIN",
        project_id="ekyc",
        server_id="S2",
        repository="Patricked-code/Ekyc",
        expected_head="a"*40,
        parent_domain="chainsolutions.fr",
        subdomain_label="../bad",
    )
    try:
        c.compile_request(r,registry=REGISTRY,snapshot=SNAPSHOT,server_model=SERVER_MODEL)
    except ValueError as exc:
        if str(exc)!="SUBDOMAIN_LABEL_INVALID":
            raise
    else:
        raise SystemExit("EXECUTION_PACKAGE_COMPILER_TEST_FAILED: invalid label accepted")

def main():
    test_ekyc_subdomain_derivation_and_blockers()
    test_existing_s2_deploy_ready()
    test_ekyc_not_silently_added_to_deploy_registry()
    test_s2_production_attestation_ready()
    test_github_branch_package_ready()
    test_secret_metadata_classification_without_value()
    test_missing_expected_head_is_input_not_guess()
    test_invalid_subdomain_rejected()
    print("GOVERNED_EXECUTION_PACKAGE_COMPILER_TEST_PASS")

if __name__=="__main__":
    main()
