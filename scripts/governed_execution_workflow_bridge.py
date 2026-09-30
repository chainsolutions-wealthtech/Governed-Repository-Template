#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from governed_execution_engine import (
    ROOT,
    REGISTRY_PATH,
    SNAPSHOT_PATH,
    compile_plan,
    load_json,
    validate_package,
)

ALLOWED_PREFIX = (ROOT / ".governance" / "control-plane-state" / "execution-packages").resolve()

TOKEN_CLASSES = {
    "PROVISION_GITHUB_SECRET": "SECRET_DYNAMIC",
    "ROTATE_CREDENTIAL": "CREDENTIAL",
    "REVOKE_CREDENTIAL": "CREDENTIAL",
    "VERIFY_SECRET_OR_CREDENTIAL_WITHOUT_READBACK": "CREDENTIAL",
    "GITHUB_CREATE_REPOSITORY_FROM_TEMPLATE": "ADMIN",
    "GITHUB_CREATE_BRANCH": "GIT",
    "GITHUB_UPSERT_FILE": "GIT",
    "GITHUB_CREATE_PULL_REQUEST": "GIT",
    "GITHUB_MERGE_PULL_REQUEST": "GIT",
    "GITHUB_CONFIGURE_BRANCH_PROTECTION": "ADMIN",
    "GITHUB_CONFIGURE_RULESET": "ADMIN",
    "GITHUB_CONFIGURE_WEBHOOK": "WEBHOOK",
    "GITHUB_CONFIGURE_ENVIRONMENT": "ENVIRONMENT",
    "GITHUB_SET_ACTIONS_VARIABLE": "VARIABLE",
    "GITHUB_DISPATCH_WORKFLOW": "ACTIONS",
    "GITHUB_CREATE_DEPLOYMENT": "DEPLOYMENT",
    "GITHUB_UPDATE_REPOSITORY_SETTINGS": "ADMIN",
    "GITHUB_ADD_COLLABORATOR": "ADMIN",
}

MCP_HANDLERS = {"MCP_RECIPE"}


def emit(name: str, value: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")
    else:
        print(f"{name}={value}")


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def target_owner(package: dict) -> str:
    params = package.get("parameters") or {}
    repository = package.get("repository") or params.get("repository")
    if repository:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", str(repository)):
            raise SystemExit("EXECUTION_BRIDGE_TARGET_REPOSITORY_INVALID")
        return str(repository).split("/", 1)[0]
    owner = params.get("target_owner")
    if owner and re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", str(owner)):
        return str(owner)
    return ""


def token_class(package: dict, spec: dict) -> str:
    intent = package["intent"]
    if intent in {"ROTATE_CREDENTIAL", "REVOKE_CREDENTIAL", "VERIFY_SECRET_OR_CREDENTIAL_WITHOUT_READBACK"}:
        credential_type = (package.get("parameters") or {}).get("credential_type")
        if credential_type == "GITHUB_ACTIONS_ENVIRONMENT_SECRET":
            return "SECRET_ENV"
        if credential_type == "GITHUB_ACTIONS_REPOSITORY_SECRET":
            return "SECRET_REPO"
        return "NONE"
    klass = TOKEN_CLASSES.get(intent, "NONE")
    if klass == "SECRET_DYNAMIC":
        return "SECRET_ENV" if (package.get("parameters") or {}).get("environment") else "SECRET_REPO"
    if klass == "NONE" and spec.get("side_effecting") and (
        package.get("repository") or (package.get("parameters") or {}).get("repository")
    ):
        return "READ"
    return klass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True)
    args = parser.parse_args()

    path = Path(args.package).resolve()
    try:
        path.relative_to(ALLOWED_PREFIX)
    except ValueError as exc:
        raise SystemExit("EXECUTION_PACKAGE_NOT_IN_GOVERNED_DIRECTORY") from exc
    if path.suffix != ".json" or not path.is_file():
        raise SystemExit("EXECUTION_PACKAGE_INVALID_PATH")

    package = load_json(path)
    registry = load_json(REGISTRY_PATH)
    snapshot = load_json(SNAPSHOT_PATH)
    spec = validate_package(package, registry)
    plan = compile_plan(package, registry, snapshot)

    handler = spec["handler"]
    steps = (((package.get("bindings") or {}).get("steps")) or {})
    has_mcp_steps = any(
        (step.get("backend", "MCP_DIRECT") == "MCP_DIRECT")
        for phase in ("preflight", "execute", "verify", "rollback")
        for step in (steps.get(phase) or [])
    )

    klass = token_class(package, spec)
    owner = target_owner(package)
    if klass != "NONE" and not owner:
        raise SystemExit("EXECUTION_BRIDGE_TARGET_OWNER_REQUIRED")

    emit("operation_id", package["operation_id"])
    emit("intent", package["intent"])
    emit("handler", handler)
    emit("target_owner", owner)
    emit("token_class", klass)
    emit("needs_target_token", bool_text(klass != "NONE"))
    emit("needs_mcp", bool_text(handler in MCP_HANDLERS or has_mcp_steps))
    emit("needs_oidc", bool_text(handler == "SSH_OIDC_CERT"))
    emit("needs_app_source", bool_text(handler == "GITHUB_APP_TOKEN"))
    emit("side_effecting", bool_text(bool(spec.get("side_effecting"))))
    emit("plan_executable", bool_text(bool(plan.get("executable_now"))))
    emit("missing_capabilities", ",".join(plan.get("missing_capabilities_or_bindings") or []))
    print(json.dumps(plan, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
