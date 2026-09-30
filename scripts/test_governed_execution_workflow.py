#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import governed_execution_workflow_bridge as bridge
from governed_execution_engine import load_json, REGISTRY_PATH

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/".github"/"workflows"/"governed-execution.yml"
REGISTRY=load_json(REGISTRY_PATH)


def pkg(intent, *, repository=None, environment=None, credential_type=None):
    spec=REGISTRY["intents"][intent]
    parameters={}
    if repository:
        parameters["repository"]=repository
    if environment:
        parameters["environment"]=environment
    if credential_type:
        parameters["credential_type"]=credential_type
    return {
        "intent":intent,
        "repository":repository,
        "parameters":parameters,
    },spec


def main():
    text=WORKFLOW.read_text(encoding="utf-8")
    required=[
        "workflow_dispatch:",
        "expected_source_head:",
        "GOVERNED_EXECUTION_REQUIRES_CANONICAL_MAIN",
        "persist-credentials: false",
        "id-token: write",
        "governed_execution_workflow_bridge.py",
        "governed_execution_engine.py",
        "--execute",
        "actions/create-github-app-token@v3",
        "GOVERNED_MCP_AUTH_TOKEN",
        "execution-receipts",
    ]
    for marker in required:
        if marker not in text:
            raise SystemExit(f"GOVERNED_EXECUTION_WORKFLOW_TEST_FAILED: missing {marker}")
    for forbidden in ["schedule:", "pull_request:", "push:"]:
        if forbidden in text.split("permissions:",1)[0]:
            raise SystemExit(f"GOVERNED_EXECUTION_WORKFLOW_TEST_FAILED: unsafe trigger {forbidden}")

    p,s=pkg("GITHUB_CREATE_BRANCH",repository="owner/repo")
    if bridge.token_class(p,s)!="GIT":
        raise SystemExit("GOVERNED_EXECUTION_WORKFLOW_TEST_FAILED: git token class")

    p,s=pkg("PROVISION_GITHUB_SECRET",repository="owner/repo")
    if bridge.token_class(p,s)!="SECRET_REPO":
        raise SystemExit("GOVERNED_EXECUTION_WORKFLOW_TEST_FAILED: repo secret token class")

    p,s=pkg("PROVISION_GITHUB_SECRET",repository="owner/repo",environment="production")
    if bridge.token_class(p,s)!="SECRET_ENV":
        raise SystemExit("GOVERNED_EXECUTION_WORKFLOW_TEST_FAILED: env secret token class")

    p,s=pkg("DEPLOY_APPLICATION",repository="owner/repo")
    if bridge.token_class(p,s)!="READ":
        raise SystemExit("GOVERNED_EXECUTION_WORKFLOW_TEST_FAILED: server mutation HEAD-read token class")

    p,s=pkg("MINT_EPHEMERAL_SSH_CERTIFICATE")
    if bridge.token_class(p,s)!="NONE":
        raise SystemExit("GOVERNED_EXECUTION_WORKFLOW_TEST_FAILED: OIDC cert should not require target token")

    if bridge.target_owner({"repository":"chainsolutions-wealthtech/example","parameters":{}})!="chainsolutions-wealthtech":
        raise SystemExit("GOVERNED_EXECUTION_WORKFLOW_TEST_FAILED: target owner derivation")

    if len(REGISTRY.get("intents") or {}) != 39:
        raise SystemExit("GOVERNED_EXECUTION_WORKFLOW_TEST_FAILED: expected 39 registered intents")

    print("GOVERNED_EXECUTION_WORKFLOW_TEST_PASS")


if __name__=="__main__":
    main()
