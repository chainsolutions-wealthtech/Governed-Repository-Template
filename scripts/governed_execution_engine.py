#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import os
import re
import secrets
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp_repository_discovery import (
    SSH_BROKER_BASE_URL,
    request_ssh_certificate,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / ".governance" / "control-plane-state" / "execution-registry.json"
SNAPSHOT_PATH = ROOT / ".governance" / "control-plane-state" / "mcp-capability-snapshot.json"

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SECRET_NAME_RE = re.compile(r"^[A-Z0-9_]{1,128}$")
ENV_REF_RE = re.compile(r"^[A-Z][A-Z0-9_]{0,127}$")
OP_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{3,160}$")

FORBIDDEN_SECRET_KEYS = {
    "secret", "secret_value", "password", "token", "private_key",
    "authorization", "authorization_header", "credential_value",
}
SAFE_SECRET_REFERENCE_KEYS = {
    "secret_ref", "credential_ref", "token_ref", "private_key_ref",
    "source_ref", "value_ref",
}


class ExecutionError(RuntimeError):
    def __init__(self, code: str, detail: str | None = None):
        super().__init__(code if detail is None else f"{code}:{detail}")
        self.code = code
        self.detail = detail


class RuntimeSecretStore:
    """In-memory only. Values are never included in evidence."""

    def __init__(self) -> None:
        self._values: dict[str, str] = {}

    def put(self, key: str, value: str) -> None:
        if not key or not isinstance(value, str) or not value:
            raise ExecutionError("RUNTIME_SECRET_INVALID")
        self._values[key] = value

    def get(self, key: str) -> str:
        value = self._values.get(key)
        if not value:
            raise ExecutionError("RUNTIME_SECRET_NOT_FOUND", key)
        return value

    def clear(self) -> None:
        for key in list(self._values):
            self._values[key] = ""
        self._values.clear()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if lowered in FORBIDDEN_SECRET_KEYS and lowered not in SAFE_SECRET_REFERENCE_KEYS:
                out[key] = "***REDACTED***"
            elif any(marker in lowered for marker in ("password", "private_key", "bearer", "secret_value")):
                out[key] = "***REDACTED***"
            else:
                out[key] = redact(item)
        return out
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        if value.startswith(("ghp_", "github_pat_", "-----BEGIN PRIVATE KEY-----")):
            return "***REDACTED***"
        if len(value) > 4000:
            return value[:4000] + "...<truncated>"
    return value


def _walk_forbidden(obj: Any, path: str = "$") -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            lowered = str(key).lower()
            if lowered in FORBIDDEN_SECRET_KEYS and lowered not in SAFE_SECRET_REFERENCE_KEYS:
                if value not in (None, "", "***"):
                    raise ExecutionError("PACKAGE_CONTAINS_SECRET_VALUE", f"{path}.{key}")
            _walk_forbidden(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            _walk_forbidden(value, f"{path}[{idx}]")
    elif isinstance(obj, str):
        if obj.startswith(("ghp_", "github_pat_", "-----BEGIN PRIVATE KEY-----")):
            raise ExecutionError("PACKAGE_CONTAINS_SECRET_LIKE_MATERIAL", path)


def api_request(token: str, method: str, url: str, payload: dict | None = None, accept: str = "application/vnd.github+json") -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        url,
        method=method,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": accept,
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "governed-execution-engine",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read(262145)
            if len(raw) > 262144:
                raise ExecutionError("HTTP_RESPONSE_TOO_LARGE")
            return json.loads(raw.decode()) if raw else {}
    except urllib.error.HTTPError as exc:
        body = exc.read(4000).decode(errors="replace")
        raise ExecutionError("HTTP_REQUEST_FAILED", f"{method}:{exc.code}:{body[:1000]}") from exc
    except urllib.error.URLError as exc:
        raise ExecutionError("HTTP_REQUEST_UNREACHABLE", str(exc.reason)[:300]) from exc


def github_api(token: str, method: str, path: str, payload: dict | None = None) -> dict:
    return api_request(token, method, "https://api.github.com" + path, payload)


def current_repository_head(token: str, repository: str) -> str:
    repo = github_api(token, "GET", f"/repos/{repository}")
    branch = repo.get("default_branch") or "main"
    ref = github_api(token, "GET", f"/repos/{repository}/git/ref/heads/{urllib.parse.quote(branch, safe='')}")
    sha = (((ref.get("object") or {}).get("sha")) or "").lower()
    if not SHA_RE.fullmatch(sha):
        raise ExecutionError("TARGET_HEAD_UNAVAILABLE")
    return sha


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def mint_github_app_installation_token(parameters: dict, runtime: RuntimeSecretStore) -> dict:
    client_id = os.environ.get("GOVERNED_GITHUB_APP_CLIENT_ID")
    private_key = os.environ.get("GOVERNED_GITHUB_APP_PRIVATE_KEY")
    if not client_id or not private_key:
        raise ExecutionError("GITHUB_APP_SOURCE_CREDENTIAL_MISSING")

    now = int(time.time())
    header = _b64url(json.dumps({"alg": "RS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _b64url(json.dumps({"iat": now - 30, "exp": now + 540, "iss": client_id}, separators=(",", ":")).encode())
    signing_input = f"{header}.{payload}".encode()

    with tempfile.TemporaryDirectory(prefix="governed-app-jwt-") as td:
        key_path = Path(td) / "app.pem"
        key_path.write_text(private_key, encoding="utf-8")
        os.chmod(key_path, 0o600)
        completed = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", str(key_path)],
            input=signing_input,
            capture_output=True,
            check=False,
            timeout=15,
        )
        key_path.write_text("", encoding="utf-8")
        if completed.returncode != 0:
            raise ExecutionError("GITHUB_APP_JWT_SIGN_FAILED", completed.stderr.decode(errors="replace")[:300])
        signature = _b64url(completed.stdout)
    jwt = f"{header}.{payload}.{signature}"

    repository = parameters.get("repository")
    owner = parameters.get("target_owner")
    account_type = parameters.get("target_account_type", "ORGANIZATION")
    if repository:
        if not REPO_RE.fullmatch(repository):
            raise ExecutionError("GITHUB_TARGET_REPOSITORY_INVALID")
        install = github_api(jwt, "GET", f"/repos/{repository}/installation")
    elif owner:
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", owner):
            raise ExecutionError("GITHUB_TARGET_OWNER_INVALID")
        if account_type == "ORGANIZATION":
            install = github_api(jwt, "GET", f"/orgs/{owner}/installation")
        elif account_type == "PERSONAL_ACCOUNT":
            install = github_api(jwt, "GET", f"/users/{owner}/installation")
        else:
            raise ExecutionError("GITHUB_TARGET_ACCOUNT_TYPE_INVALID")
    else:
        raise ExecutionError("GITHUB_INSTALLATION_TARGET_REQUIRED")

    installation_id = install.get("id")
    if not isinstance(installation_id, int):
        raise ExecutionError("GITHUB_INSTALLATION_ID_MISSING")

    body: dict[str, Any] = {}
    permissions = parameters.get("permissions") or {}
    if permissions:
        body["permissions"] = permissions
    repositories = parameters.get("repositories")
    if repositories:
        body["repositories"] = repositories

    minted = github_api(jwt, "POST", f"/app/installations/{installation_id}/access_tokens", body)
    token = minted.get("token")
    if not isinstance(token, str) or len(token) < 20:
        raise ExecutionError("GITHUB_INSTALLATION_TOKEN_MISSING")
    runtime_key = parameters.get("runtime_secret_key") or "GITHUB_APP_INSTALLATION_TOKEN"
    runtime.put(runtime_key, token)
    return {
        "status": "PASS",
        "installation_id": installation_id,
        "expires_at": minted.get("expires_at"),
        "permissions": minted.get("permissions") or permissions,
        "repository_selection": minted.get("repository_selection"),
        "runtime_secret_key": runtime_key,
        "token_persisted": False,
    }


def resolve_secret_reference(ref: str, runtime: RuntimeSecretStore, generated: dict[str, str]) -> str:
    if not isinstance(ref, str):
        raise ExecutionError("SECRET_REFERENCE_INVALID")
    if ref.startswith("env:"):
        key = ref[4:]
        if not ENV_REF_RE.fullmatch(key):
            raise ExecutionError("SECRET_ENV_REFERENCE_INVALID")
        value = os.environ.get(key)
        if not value:
            raise ExecutionError("SECRET_ENV_REFERENCE_MISSING", key)
        return value
    if ref.startswith("runtime:"):
        return runtime.get(ref[8:])
    if ref.startswith("generated:"):
        spec = ref[10:] or "32"
        try:
            nbytes = int(spec)
        except ValueError as exc:
            raise ExecutionError("GENERATED_SECRET_SIZE_INVALID") from exc
        if not 16 <= nbytes <= 128:
            raise ExecutionError("GENERATED_SECRET_SIZE_OUT_OF_RANGE")
        if ref not in generated:
            generated[ref] = secrets.token_urlsafe(nbytes)
        return generated[ref]
    raise ExecutionError("SECRET_REFERENCE_SCHEME_UNSUPPORTED")


def _gh_env(token: str) -> dict:
    env = os.environ.copy()
    env["GH_TOKEN"] = token
    return env


def github_secret_metadata(token: str, repository: str, name: str, environment: str | None = None) -> dict:
    args = ["gh", "secret", "list", "--repo", repository, "--json", "name,updatedAt"]
    if environment:
        args.extend(["--env", environment])
    completed = subprocess.run(args, capture_output=True, text=True, env=_gh_env(token), timeout=30, check=False)
    if completed.returncode != 0:
        raise ExecutionError("GITHUB_SECRET_LIST_FAILED", (completed.stderr or completed.stdout)[:500])
    items = json.loads(completed.stdout or "[]")
    match = next((x for x in items if x.get("name") == name), None)
    return {
        "exists": bool(match),
        "name": name,
        "updated_at": match.get("updatedAt") if match else None,
        "environment": environment,
    }


def provision_github_secret(parameters: dict, runtime: RuntimeSecretStore, generated: dict[str, str]) -> dict:
    repository = parameters.get("repository")
    name = parameters.get("secret_name")
    environment = parameters.get("environment")
    if not isinstance(repository, str) or not REPO_RE.fullmatch(repository):
        raise ExecutionError("GITHUB_SECRET_REPOSITORY_INVALID")
    if not isinstance(name, str) or not SECRET_NAME_RE.fullmatch(name):
        raise ExecutionError("GITHUB_SECRET_NAME_INVALID")
    if environment is not None and not re.fullmatch(r"[A-Za-z0-9_. -]{1,128}", str(environment)):
        raise ExecutionError("GITHUB_ENVIRONMENT_NAME_INVALID")

    token_ref = parameters.get("github_token_ref", "env:GOVERNED_TARGET_TOKEN")
    token = resolve_secret_reference(token_ref, runtime, generated)
    value_ref = parameters.get("value_ref")
    value = resolve_secret_reference(value_ref, runtime, generated)

    before = github_secret_metadata(token, repository, name, environment)
    args = ["gh", "secret", "set", name, "--repo", repository, "--app", "actions"]
    if environment:
        args.extend(["--env", environment])
    completed = subprocess.run(
        args,
        input=value,
        text=True,
        capture_output=True,
        env=_gh_env(token),
        timeout=30,
        check=False,
    )
    value = ""
    if completed.returncode != 0:
        raise ExecutionError("GITHUB_SECRET_SET_FAILED", (completed.stderr or completed.stdout)[:500])
    after = github_secret_metadata(token, repository, name, environment)
    if not after["exists"]:
        raise ExecutionError("GITHUB_SECRET_VERIFY_FAILED")
    return {
        "status": "PASS",
        "repository": repository,
        "secret_name": name,
        "environment": environment,
        "before": before,
        "after": after,
        "value_read_back": False,
        "value_persisted": False,
        "rollback": "DELETE_IF_NEW;_NO_AUTOMATIC_RESTORE_IF_OVERWROTE_EXISTING_VALUE",
    }


def delete_github_secret(parameters: dict, runtime: RuntimeSecretStore, generated: dict[str, str]) -> dict:
    repository = parameters.get("repository")
    name = parameters.get("secret_name")
    environment = parameters.get("environment")
    if not isinstance(repository, str) or not REPO_RE.fullmatch(repository):
        raise ExecutionError("GITHUB_SECRET_REPOSITORY_INVALID")
    if not isinstance(name, str) or not SECRET_NAME_RE.fullmatch(name):
        raise ExecutionError("GITHUB_SECRET_NAME_INVALID")
    token = resolve_secret_reference(parameters.get("github_token_ref", "env:GOVERNED_TARGET_TOKEN"), runtime, generated)
    before = github_secret_metadata(token, repository, name, environment)
    args = ["gh", "secret", "delete", name, "--repo", repository, "--app", "actions"]
    if environment:
        args.extend(["--env", environment])
    completed = subprocess.run(args, capture_output=True, text=True, env=_gh_env(token), timeout=30, check=False)
    if completed.returncode != 0 and before["exists"]:
        raise ExecutionError("GITHUB_SECRET_DELETE_FAILED", (completed.stderr or completed.stdout)[:500])
    after = github_secret_metadata(token, repository, name, environment)
    if after["exists"]:
        raise ExecutionError("GITHUB_SECRET_REVOKE_VERIFY_FAILED")
    return {"status": "PASS", "before": before, "after": after, "value_read_back": False}


def mint_ephemeral_ssh_certificate(parameters: dict) -> dict:
    repository = parameters.get("repository")
    expected_head = parameters.get("expected_head")
    if not isinstance(repository, str) or not REPO_RE.fullmatch(repository):
        raise ExecutionError("SSH_CERT_REPOSITORY_INVALID")
    if not isinstance(expected_head, str) or not SHA_RE.fullmatch(expected_head):
        raise ExecutionError("SSH_CERT_EXPECTED_HEAD_INVALID")

    with tempfile.TemporaryDirectory(prefix="governed-ssh-cert-") as td:
        key_path = Path(td) / "id_ed25519"
        completed = subprocess.run(
            ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key_path)],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if completed.returncode != 0:
            raise ExecutionError("SSH_EPHEMERAL_KEYGEN_FAILED", completed.stderr[:300])
        public_key = key_path.with_suffix(".pub").read_text(encoding="utf-8").strip()
        cert = request_ssh_certificate(repository, expected_head, public_key)
        key_path.write_text("", encoding="utf-8")
        if cert.get("repository") != repository:
            raise ExecutionError("SSH_CERT_REPOSITORY_MISMATCH")
        if cert.get("mutationAllowed") is not False:
            raise ExecutionError("SSH_CERT_UNEXPECTED_MUTATION_AUTHORITY")
        return {
            "status": "PASS",
            "repository": repository,
            "host": cert.get("host"),
            "port": cert.get("port"),
            "username": cert.get("username"),
            "principal": cert.get("principal"),
            "fingerprint": cert.get("fingerprint"),
            "valid_for_seconds": cert.get("validForSeconds"),
            "mutation_allowed": False,
            "private_key_persisted": False,
            "certificate_persisted": False,
        }


class McpClient:
    def __init__(self, endpoint: str, token: str):
        if not endpoint.startswith("https://"):
            raise ExecutionError("MCP_ENDPOINT_INVALID")
        self.endpoint = endpoint
        self.token = token
        self.session: str | None = None
        self.counter = 1

    def _post(self, payload: dict) -> dict:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "governed-execution-engine",
        }
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        req = urllib.request.Request(self.endpoint, method="POST", headers=headers, data=json.dumps(payload).encode())
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                raw = response.read(1048577)
                if len(raw) > 1048576:
                    raise ExecutionError("MCP_RESPONSE_TOO_LARGE")
                self.session = response.headers.get("Mcp-Session-Id") or self.session
        except urllib.error.HTTPError as exc:
            body = exc.read(4000).decode(errors="replace")
            raise ExecutionError("MCP_HTTP_ERROR", f"{exc.code}:{body[:1000]}") from exc
        except urllib.error.URLError as exc:
            raise ExecutionError("MCP_UNREACHABLE", str(exc.reason)[:300]) from exc
        text = raw.decode(errors="replace").strip()
        if not text:
            return {}
        if text.startswith("{"):
            return json.loads(text)
        events = []
        for line in text.splitlines():
            if line.startswith("data:"):
                try:
                    events.append(json.loads(line[5:].strip()))
                except Exception:
                    pass
        return events[-1] if events else {"raw": text[:4000]}

    def initialize(self) -> None:
        result = self._post({
            "jsonrpc": "2.0",
            "id": self.counter,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "governed-execution-engine", "version": "1.0"},
            },
        })
        self.counter += 1
        if result.get("error"):
            raise ExecutionError("MCP_INITIALIZE_FAILED", json.dumps(redact(result.get("error")))[:800])
        try:
            self._post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        except Exception:
            pass

    def call_tool(self, name: str, arguments: dict) -> dict:
        if self.session is None:
            self.initialize()
        result = self._post({
            "jsonrpc": "2.0",
            "id": self.counter,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        })
        self.counter += 1
        if result.get("error"):
            raise ExecutionError("MCP_TOOL_ERROR", f"{name}:{json.dumps(redact(result.get('error')))[:800]}")
        return result


class CapabilityResolver:
    def __init__(self, snapshot: dict, package: dict):
        self.snapshot = snapshot
        self.package = package
        self.capability_map = snapshot.get("capability_map") or {}

    def candidate_tools(self, capability: str) -> list[dict]:
        return copy.deepcopy((self.capability_map.get(capability) or {}).get("candidate_tools") or [])

    def _project_scope_ok(self, candidate: dict) -> bool:
        scope = candidate.get("scope") or {}
        mode = scope.get("mode")
        project_ids = scope.get("project_ids") or []
        project_id = self.package.get("project_id")
        if mode in {None, "GENERIC", "MCP_SELF"}:
            return True
        if mode in {"PROJECT_REGISTRY_SCOPED", "PROJECT_SPECIFIC"}:
            return project_id in project_ids
        return False

    def validate_tool(self, capability: str, tool: str) -> dict:
        entry = self.capability_map.get(capability)
        if not entry:
            raise ExecutionError("MISSING_CAPABILITY", capability)
        if str(entry.get("availability", "")).startswith("NOT_EXPOSED"):
            raise ExecutionError("MISSING_CAPABILITY", capability)
        candidates = [c for c in self.candidate_tools(capability) if c.get("tool") == tool]
        if not candidates:
            raise ExecutionError("UNMAPPED_TOOL", f"{capability}:{tool}")
        candidate = next((c for c in candidates if self._project_scope_ok(c)), None)
        if candidate is None:
            raise ExecutionError("CAPABILITY_PROJECT_SCOPE_MISMATCH", f"{capability}:{tool}:{self.package.get('project_id')}")
        return candidate

    def resolve_required(self, required: list[str], steps: dict) -> dict:
        resolved: dict[str, dict] = {}
        bound = []
        for phase in ("preflight", "execute", "verify", "rollback"):
            for step in steps.get(phase) or []:
                cap = step.get("capability")
                tool = step.get("tool")
                if cap and tool:
                    candidate = self.validate_tool(cap, tool)
                    bound.append((cap, tool))
                    resolved.setdefault(cap, candidate)
        missing = []
        for capability in required:
            entry = self.capability_map.get(capability)
            if not entry or str(entry.get("availability", "")).startswith("NOT_EXPOSED"):
                missing.append(capability)
                continue
            if not any(cap == capability for cap, _ in bound):
                candidates = [c for c in self.candidate_tools(capability) if self._project_scope_ok(c)]
                if len(candidates) == 1:
                    resolved[capability] = candidates[0]
                else:
                    missing.append(capability)
        if missing:
            raise ExecutionError("MISSING_CAPABILITY_BINDING", ",".join(sorted(set(missing))))
        return resolved


def validate_package(package: dict, registry: dict) -> dict:
    _walk_forbidden(package)
    required = (registry.get("package_contract") or {}).get("required") or []
    missing = [key for key in required if key not in package]
    if missing:
        raise ExecutionError("PACKAGE_REQUIRED_FIELD_MISSING", ",".join(missing))
    if package.get("schema_version") != "1.0.0":
        raise ExecutionError("PACKAGE_SCHEMA_VERSION_UNSUPPORTED")
    if not OP_ID_RE.fullmatch(str(package.get("operation_id", ""))):
        raise ExecutionError("PACKAGE_OPERATION_ID_INVALID")
    intent = package.get("intent")
    spec = (registry.get("intents") or {}).get(intent)
    if not spec:
        raise ExecutionError("INTENT_NOT_REGISTERED", str(intent))
    authority = package.get("authority") or {}
    if spec.get("side_effecting"):
        if authority.get("approved") is not True:
            raise ExecutionError("EXECUTION_AUTHORITY_NOT_APPROVED")
        grants = set(authority.get("grants") or [])
        required_authority = spec.get("required_authority")
        if required_authority not in grants and "SCOPED_FULL_LIFECYCLE" not in grants:
            raise ExecutionError("EXECUTION_AUTHORITY_GRANT_MISSING", str(required_authority))
        if not authority.get("decision_ref"):
            raise ExecutionError("EXECUTION_AUTHORITY_DECISION_REF_MISSING")
    repository = package.get("repository")
    expected_head = package.get("expected_head")
    if repository is not None and not REPO_RE.fullmatch(str(repository)):
        raise ExecutionError("PACKAGE_REPOSITORY_INVALID")
    if expected_head is not None and not SHA_RE.fullmatch(str(expected_head)):
        raise ExecutionError("PACKAGE_EXPECTED_HEAD_INVALID")
    return spec


def _execution_steps(package: dict) -> dict:
    bindings = package.get("bindings") or {}
    steps = bindings.get("steps") or {}
    normalized = {}
    for phase in ("preflight", "execute", "verify", "rollback"):
        items = steps.get(phase) or []
        if not isinstance(items, list):
            raise ExecutionError("PACKAGE_STEPS_INVALID", phase)
        normalized[phase] = items
    return normalized


def _mcp_token(runtime: RuntimeSecretStore, generated: dict[str, str], package: dict) -> str:
    ref = (((package.get("bindings") or {}).get("credentials") or {}).get("MCP_AUTH_TOKEN") or {}).get("secret_ref")
    if ref:
        return resolve_secret_reference(ref, runtime, generated)
    value = os.environ.get("GOVERNED_MCP_AUTH_TOKEN")
    if not value:
        raise ExecutionError("MCP_AUTH_TOKEN_MISSING")
    return value


def run_mcp_steps(steps: list[dict], resolver: CapabilityResolver, package: dict, runtime: RuntimeSecretStore, generated: dict[str, str], evidence: list[dict]) -> None:
    if not steps:
        return
    endpoint = os.environ.get("GOVERNED_MCP_URL") or (package.get("parameters") or {}).get("mcp_endpoint")
    if not endpoint:
        raise ExecutionError("MCP_ENDPOINT_MISSING")
    client = McpClient(endpoint, _mcp_token(runtime, generated, package))
    for index, step in enumerate(steps):
        backend = step.get("backend", "MCP_DIRECT")
        if backend != "MCP_DIRECT":
            raise ExecutionError("STEP_BACKEND_UNSUPPORTED", str(backend))
        capability = step.get("capability")
        tool = step.get("tool")
        if not capability or not tool:
            raise ExecutionError("MCP_STEP_BINDING_INVALID", str(index))
        candidate = resolver.validate_tool(capability, tool)
        result = client.call_tool(tool, copy.deepcopy(step.get("arguments") or {}))
        evidence.append({
            "index": index,
            "backend": backend,
            "capability": capability,
            "tool": tool,
            "candidate_scope": candidate.get("scope"),
            "result": redact(result),
        })


def _target_token(runtime: RuntimeSecretStore, generated: dict[str, str], parameters: dict) -> str:
    ref = parameters.get("github_token_ref", "env:GOVERNED_TARGET_TOKEN")
    return resolve_secret_reference(ref, runtime, generated)


def verify_exact_head_if_required(package: dict, spec: dict, runtime: RuntimeSecretStore, generated: dict[str, str]) -> dict:
    repository = package.get("repository")
    expected = package.get("expected_head")
    if not repository or not expected:
        return {"required": False}
    if not spec.get("side_effecting"):
        return {"required": False}
    token = _target_token(runtime, generated, package.get("parameters") or {})
    actual = current_repository_head(token, repository)
    if actual != expected:
        raise ExecutionError("HEAD_MOVED", f"expected={expected},actual={actual}")
    return {"required": True, "repository": repository, "expected": expected, "actual": actual}


def compile_plan(package: dict, registry: dict, snapshot: dict) -> dict:
    spec = validate_package(package, registry)
    steps = _execution_steps(package)
    resolver = CapabilityResolver(snapshot, package)
    missing = []
    resolved = {}
    if spec.get("handler") == "MCP_RECIPE":
        try:
            resolved = resolver.resolve_required(spec.get("required_capabilities") or [], steps)
        except ExecutionError as exc:
            if exc.code in {"MISSING_CAPABILITY", "MISSING_CAPABILITY_BINDING", "CAPABILITY_PROJECT_SCOPE_MISMATCH"}:
                missing = [x for x in (exc.detail or "").split(",") if x]
            else:
                raise
    return {
        "operation_id": package["operation_id"],
        "intent": package["intent"],
        "handler": spec["handler"],
        "side_effecting": spec.get("side_effecting", False),
        "required_authority": spec.get("required_authority"),
        "required_capabilities": spec.get("required_capabilities") or [],
        "resolved_capabilities": redact(resolved),
        "missing_capabilities_or_bindings": sorted(set(missing)),
        "steps": redact(steps),
        "executable_now": not missing,
        "dry_run_default": True,
    }


def execute(package: dict, *, do_execute: bool, registry: dict, snapshot: dict) -> dict:
    started = utcnow()
    spec = validate_package(package, registry)
    plan = compile_plan(package, registry, snapshot)
    receipt = {
        "schema_version": "1.0.0",
        "authority_id": "CP-EXECUTION-001",
        "operation_id": package["operation_id"],
        "intent": package["intent"],
        "started_at": started,
        "mode": "EXECUTE" if do_execute else "DRY_RUN",
        "status": "PLANNED",
        "plan": plan,
        "preflight": [],
        "execute": [],
        "verification": [],
        "rollback": [],
        "failure_code": None,
        "secret_values_persisted": False,
    }
    if not do_execute:
        receipt["status"] = "READY" if plan["executable_now"] else "BLOCKED_MISSING_CAPABILITY"
        receipt["completed_at"] = utcnow()
        return receipt

    if not plan["executable_now"]:
        raise ExecutionError("MISSING_CAPABILITY_OR_BINDING", ",".join(plan["missing_capabilities_or_bindings"]))

    runtime = RuntimeSecretStore()
    generated: dict[str, str] = {}
    steps = _execution_steps(package)
    resolver = CapabilityResolver(snapshot, package)
    executed_side_effect = False

    try:
        head_evidence = verify_exact_head_if_required(package, spec, runtime, generated)
        receipt["preflight"].append({"exact_head": head_evidence})

        handler = spec["handler"]
        params = copy.deepcopy(package.get("parameters") or {})

        if handler == "PLAN_ONLY":
            receipt["preflight"].append({
                "credential_requirement": redact(params),
                "classification": "PLAN_ONLY_NO_SIDE_EFFECT",
            })

        elif handler == "GITHUB_APP_TOKEN":
            result = mint_github_app_installation_token(params, runtime)
            receipt["execute"].append(redact(result))
            executed_side_effect = True

        elif handler == "GITHUB_SECRET":
            result = provision_github_secret(params, runtime, generated)
            receipt["execute"].append(redact(result))
            executed_side_effect = True

        elif handler == "SSH_OIDC_CERT":
            result = mint_ephemeral_ssh_certificate(params)
            receipt["execute"].append(redact(result))

        elif handler == "MCP_RECIPE":
            resolver.resolve_required(spec.get("required_capabilities") or [], steps)
            run_mcp_steps(steps["preflight"], resolver, package, runtime, generated, receipt["preflight"])
            run_mcp_steps(steps["execute"], resolver, package, runtime, generated, receipt["execute"])
            executed_side_effect = bool(steps["execute"]) and spec.get("side_effecting", False)
            run_mcp_steps(steps["verify"], resolver, package, runtime, generated, receipt["verification"])

        elif handler == "CREDENTIAL_LIFECYCLE":
            credential_type = params.get("credential_type")
            if credential_type in {"GITHUB_ACTIONS_REPOSITORY_SECRET", "GITHUB_ACTIONS_ENVIRONMENT_SECRET"}:
                if package["intent"] == "ROTATE_CREDENTIAL":
                    result = provision_github_secret(params, runtime, generated)
                elif package["intent"] == "REVOKE_CREDENTIAL":
                    result = delete_github_secret(params, runtime, generated)
                else:
                    raise ExecutionError("CREDENTIAL_LIFECYCLE_INTENT_INVALID")
                receipt["execute"].append(redact(result))
                executed_side_effect = True
            else:
                resolver.resolve_required(spec.get("required_capabilities") or [], steps)
                run_mcp_steps(steps["preflight"], resolver, package, runtime, generated, receipt["preflight"])
                run_mcp_steps(steps["execute"], resolver, package, runtime, generated, receipt["execute"])
                executed_side_effect = bool(steps["execute"])
                run_mcp_steps(steps["verify"], resolver, package, runtime, generated, receipt["verification"])

        elif handler == "CREDENTIAL_VERIFY":
            credential_type = params.get("credential_type")
            if credential_type in {"GITHUB_ACTIONS_REPOSITORY_SECRET", "GITHUB_ACTIONS_ENVIRONMENT_SECRET"}:
                repository = params.get("repository")
                name = params.get("secret_name")
                environment = params.get("environment")
                token = _target_token(runtime, generated, params)
                result = github_secret_metadata(token, repository, name, environment)
                receipt["verification"].append(result)
                if not result["exists"]:
                    raise ExecutionError("CREDENTIAL_VERIFY_FAILED", f"{credential_type}:{name}")
            else:
                run_mcp_steps(steps["verify"], resolver, package, runtime, generated, receipt["verification"])
                if not steps["verify"]:
                    raise ExecutionError("CREDENTIAL_VERIFY_BINDING_REQUIRED", str(credential_type))
        else:
            raise ExecutionError("HANDLER_NOT_IMPLEMENTED", handler)

        receipt["status"] = "PASS"
        receipt["completed_at"] = utcnow()
        return redact(receipt)

    except Exception as exc:
        failure = exc if isinstance(exc, ExecutionError) else ExecutionError(type(exc).__name__, str(exc)[:500])
        receipt["failure_code"] = failure.code
        receipt["failure_detail"] = failure.detail

        if executed_side_effect and steps["rollback"]:
            try:
                run_mcp_steps(steps["rollback"], resolver, package, runtime, generated, receipt["rollback"])
                receipt["status"] = "FAILED_ROLLED_BACK"
            except Exception as rollback_exc:
                receipt["rollback"].append({
                    "status": "ERROR",
                    "error": str(rollback_exc)[:1000],
                })
                receipt["status"] = "FAILED_MANUAL_RECOVERY_REQUIRED"
        elif executed_side_effect:
            receipt["status"] = "FAILED_MANUAL_RECOVERY_REQUIRED"
        else:
            receipt["status"] = "FAILED_NO_SIDE_EFFECT_CONFIRMED"

        receipt["completed_at"] = utcnow()
        return redact(receipt)
    finally:
        runtime.clear()
        for key in list(generated):
            generated[key] = ""
        generated.clear()


def main() -> None:
    parser = argparse.ArgumentParser(description="Governed execution engine")
    parser.add_argument("--package", required=True, help="Path to reviewed secret-free execution package JSON")
    parser.add_argument("--execute", action="store_true", help="Actually execute. Default is dry-run.")
    parser.add_argument("--receipt", help="Optional receipt output path")
    args = parser.parse_args()

    package_path = Path(args.package).resolve()
    if ROOT not in package_path.parents and package_path != ROOT:
        raise SystemExit("PACKAGE_PATH_OUTSIDE_REPOSITORY")
    package = load_json(package_path)
    registry = load_json(REGISTRY_PATH)
    snapshot = load_json(SNAPSHOT_PATH)
    receipt = execute(package, do_execute=args.execute, registry=registry, snapshot=snapshot)
    output = json.dumps(redact(receipt), indent=2, ensure_ascii=False) + "\n"
    if args.receipt:
        receipt_path = Path(args.receipt).resolve()
        if ROOT not in receipt_path.parents:
            raise SystemExit("RECEIPT_PATH_OUTSIDE_REPOSITORY")
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(output, encoding="utf-8")
    print(output, end="")
    if receipt.get("status") not in {"PASS", "READY"}:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
