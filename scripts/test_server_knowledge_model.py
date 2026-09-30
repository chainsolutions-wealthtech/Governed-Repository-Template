#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / ".governance" / "control-plane-state" / "server-knowledge-model.json"


def main() -> None:
    model=json.loads(PATH.read_text(encoding="utf-8"))

    if model.get("authority_id")!="CP-SERVER-KNOWLEDGE-001":
        raise SystemExit("SERVER_KNOWLEDGE_TEST_FAILED: authority")
    if model.get("execution_authority_granted") is not False:
        raise SystemExit("SERVER_KNOWLEDGE_TEST_FAILED: recipe knowledge granted authority")
    for key in ["secret_values_persisted","connection_credentials_persisted","exhaustive_filesystem_inventory_persisted"]:
        if model.get(key) is not False:
            raise SystemExit(f"SERVER_KNOWLEDGE_TEST_FAILED: unsafe persistence {key}")
    if model.get("bounded_project_paths_allowed") is not True:
        raise SystemExit("SERVER_KNOWLEDGE_TEST_FAILED: governed project paths must be modelable")

    domains={item["id"]:item for item in model.get("inventory_domains") or []}
    required={
        "SERVER_IDENTITY","HOSTING_STACK","NETWORK","DNS","TLS","DOMAINS_VHOSTS",
        "FILESYSTEM_LAYOUT","RUNTIMES","PORTS_SERVICES","DATABASES","GIT_DEPLOYMENT",
        "SECRETS_ENV","PROCESS_SCHEDULING","OBSERVABILITY","BACKUP_RECOVERY",
        "SECURITY_ACCESS","CAPACITY","PROJECT_MAPPINGS","MCP_SURFACES"
    }
    if required-set(domains):
        raise SystemExit("SERVER_KNOWLEDGE_TEST_FAILED: incomplete server inventory taxonomy")

    recipes={item["id"]:item for item in model.get("operation_recipes") or []}
    if len(recipes)<15:
        raise SystemExit("SERVER_KNOWLEDGE_TEST_FAILED: operation recipe seed too small")

    required_recipe_intents={
        "CREATE_PROJECT_DIRECTORY","CREATE_SUBDOMAIN","ALLOCATE_APPLICATION_PORT",
        "CONFIGURE_REVERSE_PROXY","PROVISION_TLS","CREATE_DATABASE",
        "BIND_REPOSITORY_TO_SERVER_PROJECT","DEPLOY_APPLICATION",
        "CONFIGURE_ENV_AND_SECRETS","CONFIGURE_PROCESS_OR_SERVICE",
        "CONFIGURE_BACKUP_AND_ROLLBACK","PRODUCTION_ATTESTATION"
    }
    intents={r["intent"] for r in recipes.values()}
    if required_recipe_intents-intents:
        raise SystemExit("SERVER_KNOWLEDGE_TEST_FAILED: missing core operation recipe")

    contract=set(model.get("operation_recipe_contract",{}).get("required_fields") or [])
    for rid,recipe in recipes.items():
        missing=contract-set(recipe)
        if missing:
            raise SystemExit(f"SERVER_KNOWLEDGE_TEST_FAILED: {rid} missing {sorted(missing)}")
        if not recipe.get("verify"):
            raise SystemExit(f"SERVER_KNOWLEDGE_TEST_FAILED: {rid} has no verification")
        if not recipe.get("rollback"):
            raise SystemExit(f"SERVER_KNOWLEDGE_TEST_FAILED: {rid} has no rollback")

    path_policy=model.get("path_knowledge_policy") or {}
    if "project_bound_deployment_path" not in path_policy.get("may_persist",[]):
        raise SystemExit("SERVER_KNOWLEDGE_TEST_FAILED: project path knowledge unavailable")
    if "unbounded_recursive_filesystem_inventory" not in path_policy.get("must_not_persist",[]):
        raise SystemExit("SERVER_KNOWLEDGE_TEST_FAILED: unbounded filesystem safety missing")

    subjects={item["id"]:item for item in model.get("server_subjects") or []}
    for sid in ["S1","S2"]:
        if sid not in subjects:
            raise SystemExit(f"SERVER_KNOWLEDGE_TEST_FAILED: {sid} missing")
        if subjects[sid].get("coordinates_persisted") is not False:
            raise SystemExit(f"SERVER_KNOWLEDGE_TEST_FAILED: {sid} coordinate leak")

    slices={item["id"]:item["status"] for item in model.get("next_incremental_slices") or []}
    if slices.get("KBI-04C")!="COLLECTOR_IMPLEMENTED_LIVE_INVENTORY_PENDING":
        raise SystemExit("SERVER_KNOWLEDGE_TEST_FAILED: collector status")
    if slices.get("KBI-04D")!="PERSISTENCE_ADAPTER_IMPLEMENTED_LIVE_INVENTORY_PENDING":
        raise SystemExit("SERVER_KNOWLEDGE_TEST_FAILED: inventory persistence status")
    for sid in ["KBI-04E","KBI-04F","KBI-04G"]:
        if slices.get(sid)!="PLANNED":
            raise SystemExit(f"SERVER_KNOWLEDGE_TEST_FAILED: {sid} must remain planned")

    print("SERVER_KNOWLEDGE_AND_RECIPES_TEST_PASS")


if __name__=="__main__":
    main()
