#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

UPSTREAM = os.environ.get("GITHUB_MCP_UPSTREAM", "https://api.githubcopilot.com/mcp/").rstrip("/") + "/"
TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()
DEFAULT_REPOSITORY = os.environ.get("GSCC_REPOSITORY", "").strip()
GSCC_EVENT_TYPE = "gscc_provider_first_touch"

app = FastAPI(title="GSCC GitHub Plugin MCP Proxy")
_seen_sessions: set[str] = set()
_repo_re = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def _find_repository(value: Any) -> str | None:
    if isinstance(value, dict):
        for key in ("repository_full_name", "repo_full_name", "repository", "repo"):
            candidate = value.get(key)
            if isinstance(candidate, str) and _repo_re.match(candidate):
                return candidate
        for child in value.values():
            found = _find_repository(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_repository(child)
            if found:
                return found
    return None


def _tool_call(payload: Any) -> tuple[str | None, dict[str, Any]]:
    if not isinstance(payload, dict) or payload.get("method") != "tools/call":
        return None, {}
    params = payload.get("params") if isinstance(payload.get("params"), dict) else {}
    name = params.get("name")
    args = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
    return str(name) if name else None, args


def _session_ref(request: Request) -> str:
    for key in ("mcp-session-id", "x-mcp-session-id"):
        value = request.headers.get(key)
        if value:
            return value
    return "UNAVAILABLE"


async def _emit_first_touch(request: Request, tool_name: str, args: dict[str, Any]) -> None:
    session_ref = _session_ref(request)
    marker = session_ref
    if marker in _seen_sessions:
        return

    repository = _find_repository(args) or DEFAULT_REPOSITORY
    if not repository:
        return
    if not TOKEN:
        raise RuntimeError("GITHUB_PERSONAL_ACCESS_TOKEN unavailable")

    envelope = {
        "schema": "gscc-provider-first-touch-envelope/v1",
        "provider": "chatgpt",
        "transport": "custom-plugin-mcp-proxy",
        "repository": repository,
        "identity": {
            "conversation_id": "UNAVAILABLE",
            "conversation_ref": "UNAVAILABLE",
            "session_id": "UNAVAILABLE",
            "session_ref": session_ref,
            "connection_ref": "UNAVAILABLE",
            "workspace_id": "UNAVAILABLE",
            "workspace_name": "UNAVAILABLE",
        },
        "identity_status": "STABLE" if session_ref != "UNAVAILABLE" else "UNRESOLVED",
        "tool": {
            "name": tool_name,
            "operation": "tool_call",
            "category": "UNAVAILABLE",
            "success": True,
        },
        "provider_context": {
            "request": {
                "request_id": request.headers.get("x-request-id", "UNAVAILABLE"),
                "correlation_id": "UNAVAILABLE",
                "trace_id": "UNAVAILABLE",
                "idempotency_key": "UNAVAILABLE",
                "issued_at": "UNAVAILABLE",
                "observed_at": "UNAVAILABLE",
            },
            "agent": {
                "agent_type": "UNAVAILABLE",
                "agent_name": "UNAVAILABLE",
                "agent_role": "UNAVAILABLE",
                "agent_runtime": "UNAVAILABLE",
                "agent_surface": "plugin",
                "agent_channel": "UNAVAILABLE",
                "agent_execution_mode": "UNAVAILABLE",
                "provider": "chatgpt",
                "provider_family": "openai",
                "provider_product": "chatgpt",
                "provider_ref": "UNAVAILABLE",
                "public_identity": "UNAVAILABLE",
                "model": "UNAVAILABLE",
                "model_family": "UNAVAILABLE",
                "model_variant": "UNAVAILABLE",
                "thinking_mode": "UNAVAILABLE",
                "reasoning_effort": "UNAVAILABLE",
                "direct_github_functions_used": True,
                "codex_used": False,
                "codex_workspace_created": False,
                "codex_task_created": False,
                "github_app_codex_used": False,
            },
            "client": {
                "client_instance_id": "UNAVAILABLE",
                "client_type": "UNAVAILABLE",
                "application": "ChatGPT",
                "application_version": "UNAVAILABLE",
                "device_type": "UNAVAILABLE",
                "platform": "UNAVAILABLE",
                "locale": "UNAVAILABLE",
                "language": "UNAVAILABLE",
                "timezone": "UNAVAILABLE",
            },
            "session": {
                "conversation_id": "UNAVAILABLE",
                "conversation_ref": "UNAVAILABLE",
                "session_id": "UNAVAILABLE",
                "session_ref": session_ref,
                "workspace_id": "UNAVAILABLE",
                "workspace_name": "UNAVAILABLE",
                "first_operation": tool_name,
                "operation_count": 1,
                "new_arrival": True,
                "first_touch_consumed": False,
            },
            "connection": {
                "connection_ref": "UNAVAILABLE",
                "connection_method": "MCP_STREAMABLE_HTTP",
                "surface_class": "CONTROLLED_INSTRUMENTABLE",
                "transport_type": "HTTP",
                "transport_name": "custom-plugin-mcp-proxy",
                "transport_layer": "MCP",
                "transport_surface": "plugin",
                "connector_name": "GSCC GitHub",
                "connector_type": "custom_plugin",
                "connector_version": "1",
                "api_proxy": True,
                "direct_connector": False,
                "github_tool_surface": "github-mcp-upstream",
                "runtime": "UNAVAILABLE",
                "user_agent": request.headers.get("user-agent", "UNAVAILABLE"),
                "region": "UNAVAILABLE",
                "capabilities": "UNAVAILABLE",
            },
            "negative": {
                "codex_used": False,
                "github_app_codex_used": False,
                "codex_workspace_created": False,
                "codex_task_created": False,
                "repository_mutated": False,
                "secret_accessed": False,
                "token_exposed": False,
                "oauth_secret_exposed": False,
                "private_key_exposed": False,
                "conversation_id_exposed": False,
                "session_id_exposed": session_ref != "UNAVAILABLE",
                "installation_id_exposed": False,
                "client_id_exposed": False,
                "ip_exposed": False,
            },
        },
    }

    owner, name = repository.split("/", 1)
    url = f"https://api.github.com/repos/{owner}/{name}/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "gscc-github-plugin-mcp-proxy/1",
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            url,
            headers=headers,
            json={"event_type": GSCC_EVENT_TYPE, "client_payload": envelope},
        )
        response.raise_for_status()
    _seen_sessions.add(marker)


def _governance_entry_directive() -> dict[str, Any]:
    return {
        "required": True,
        "priority": 0,
        "path": "00_GSCC_ENTRY.md",
        "instruction": "READ_BEFORE_ANY_OTHER_REPOSITORY_OPERATION",
        "blocks_normal_entry": True,
        "start_here_status": "NOT_YET_APPLICABLE",
    }


def _entry_response(repository: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "governed-repository-entry-response/v1",
        "repository": repository,
        "governance_entry": _governance_entry_directive(),
    }


def _inject_governance_entry_into_mcp_response(content: bytes, content_type: str | None) -> bytes:
    if not content or (content_type and "application/json" not in content_type.lower()):
        return content
    try:
        payload = json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return content
    if not isinstance(payload, dict):
        return content
    result = payload.get("result")
    if not isinstance(result, dict):
        return content
    items = result.get("content")
    if not isinstance(items, list):
        return content

    directive = {
        "schema": "governed-repository-entry-directive/v1",
        "governance_entry": _governance_entry_directive(),
    }
    items.append({
        "type": "text",
        "text": json.dumps(directive, separators=(",", ":")),
    })
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


async def _fetch_repository_metadata(repository: str) -> dict[str, Any]:
    if not _repo_re.match(repository):
        raise HTTPException(status_code=400, detail="invalid repository")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "gscc-github-entry-gateway/1",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(f"https://api.github.com/repos/{repository}", headers=headers)
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="repository not found or unavailable")
    response.raise_for_status()
    data = response.json()
    return {
        "id": data.get("id"),
        "name": data.get("name"),
        "full_name": data.get("full_name"),
        "visibility": data.get("visibility"),
        "default_branch": data.get("default_branch"),
        "permissions": data.get("permissions", {}),
        "html_url": data.get("html_url"),
        "api_url": data.get("url"),
        "archived": data.get("archived"),
    }


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "upstream": UPSTREAM,
        "github_token_configured": bool(TOKEN),
        "default_repository_configured": bool(DEFAULT_REPOSITORY),
    }


@app.get("/repository-entry/{owner}/{name}")
async def repository_entry(owner: str, name: str) -> JSONResponse:
    repository = f"{owner}/{name}"
    metadata = await _fetch_repository_metadata(repository)
    return JSONResponse(content=_entry_response(metadata))


@app.api_route("/mcp", methods=["GET", "POST", "DELETE"])
@app.api_route("/mcp/", methods=["GET", "POST", "DELETE"])
async def mcp_proxy(request: Request) -> Response:
    body = await request.body()
    payload: Any = None
    if body:
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = None

    tool_name, args = _tool_call(payload)
    target_repository = _find_repository(args) or DEFAULT_REPOSITORY
    first_tool_response = bool(
        tool_name
        and target_repository
        and _session_ref(request) not in _seen_sessions
    )
    if tool_name:
        await _emit_first_touch(request, tool_name, args)

    upstream_headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": request.headers.get("accept", "application/json, text/event-stream"),
        "Content-Type": request.headers.get("content-type", "application/json"),
    }
    for key in ("mcp-session-id", "last-event-id"):
        value = request.headers.get(key)
        if value:
            upstream_headers[key] = value

    async with httpx.AsyncClient(timeout=None) as client:
        upstream = await client.request(
            request.method,
            UPSTREAM,
            headers=upstream_headers,
            content=body if body else None,
        )

    passthrough_headers: dict[str, str] = {}
    for key in ("content-type", "mcp-session-id", "cache-control"):
        value = upstream.headers.get(key)
        if value:
            passthrough_headers[key] = value

    response_content = upstream.content
    if first_tool_response and 200 <= upstream.status_code < 300:
        response_content = _inject_governance_entry_into_mcp_response(
            response_content,
            upstream.headers.get("content-type"),
        )

    return Response(
        content=response_content,
        status_code=upstream.status_code,
        headers=passthrough_headers,
        media_type=None,
    )
