#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from first_touch_expected_field_registry import CANONICAL_CONNECTION_FIELDS

UNAVAILABLE = "UNAVAILABLE"

ALIASES: dict[str, tuple[str, ...]] = {
    "agent.provider": ("provider",),
    "agent.model": ("model",),
    "agent.public_identity": ("actor",),
    "agent.direct_github_functions_used": ("direct_github_functions_used",),
    "agent.codex_used": ("codex_used", "negative.codex_used"),
    "agent.github_app_codex_used": ("github_app_codex_used", "negative.github_app_codex_used"),
    "client.locale": ("locale", "environment.locale"),
    "client.language": ("language", "environment.language"),
    "client.timezone": ("timezone", "environment.timezone"),
    "session.conversation_id": ("identity.conversation_id",),
    "session.conversation_ref": ("identity.conversation_ref",),
    "session.session_id": ("identity.session_id",),
    "session.session_ref": ("identity.session_ref",),
    "session.workspace_id": ("identity.workspace_id",),
    "session.workspace_name": ("identity.workspace_name",),
    "connection.connection_ref": ("identity.connection_ref",),
    "connection.transport_name": ("transport",),
    "connection.transport_type": ("transport_type",),
    "connection.transport_surface": ("transport_surface",),
    "connection.connector_name": ("connector_name",),
    "connection.connector_type": ("connector_type",),
    "connection.connector_version": ("connector_version",),
    "connection.direct_connector": ("direct_connector",),
    "connection.github_tool_surface": ("github_tool_surface",),
    "repository.full_name": ("repository",),
    "repository.id": ("repository_id",),
    "repository.owner": ("repository_owner",),
    "repository.owner_id": ("repository_owner_id",),
    "repository.owner_type": ("repository_owner_type",),
    "repository.visibility": ("repository_visibility",),
    "repository.default_branch": ("default_branch",),
    "repository.node_id": ("repository_observation.node_id",),
    "repository.name": ("repository_observation.name",),
    "repository.private": ("repository_observation.private",),
    "repository.archived": ("repository_observation.archived",),
    "repository.fork": ("repository_observation.fork",),
    "repository.master_branch": ("repository_observation.master_branch",),
    "repository.size": ("repository_observation.size",),
    "repository.clone_url": ("repository_observation.clone_url",),
    "repository.git_url": ("repository_observation.git_url",),
    "repository.html_url": ("repository_observation.html_url",),
    "repository.api_url": ("repository_observation.api_url",),
    "repository.commits_url": ("repository_observation.commits_url",),
    "repository.refs_url": ("repository_observation.refs_url",),
    "repository.created_at": ("repository_observation.created_at",),
    "repository.updated_at": ("repository_observation.updated_at",),
    "repository.pushed_at": ("repository_observation.pushed_at",),
    "repository.language": ("repository_observation.language",),
    "repository.topics": ("repository_observation.topics",),
    "repository.description": ("repository_observation.description",),
    "repository.is_template": ("repository_observation.is_template",),
    "repository.parent": ("repository_observation.parent",),
    "repository.source": ("repository_observation.source",),
    "repository.code_search_indexed": ("repository_observation.code_search_indexed",),
    "permissions.admin": ("capabilities.admin", "permissions.admin"),
    "permissions.maintain": ("capabilities.maintain", "permissions.maintain"),
    "permissions.pull": ("capabilities.pull", "permissions.pull"),
    "permissions.push": ("capabilities.push", "permissions.push"),
    "permissions.triage": ("capabilities.triage", "permissions.triage"),
    "git.branch": ("branch",),
    "git.head": ("observed_head",),
    "repository_state.observed_head": ("observed_head",),
    "repository_state.observed_branch": ("branch",),
    "timestamps.observed_at": ("observed_at",),
    "negative.codex_used": ("codex_used",),
    "negative.github_app_codex_used": ("github_app_codex_used",),
    "negative.codex_workspace_created": ("codex_workspace_created",),
    "negative.codex_task_created": ("codex_task_created",),
    "negative.repository_mutated": ("repository_mutated",),
    "negative.secret_accessed": ("secret_accessed",),
    "negative.token_exposed": ("token_exposed",),
    "negative.oauth_secret_exposed": ("oauth_secret_exposed",),
    "negative.private_key_exposed": ("private_key_exposed",),
    "negative.conversation_id_exposed": ("conversation_id_exposed",),
    "negative.session_id_exposed": ("session_id_exposed",),
    "negative.installation_id_exposed": ("installation_id_exposed",),
    "negative.client_id_exposed": ("client_id_exposed",),
    "negative.ip_exposed": ("ip_exposed",),
}


def _lookup(value: Any, dotted: str) -> tuple[bool, Any]:
    current = value
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _unwrap(value: Any) -> tuple[Any, str | None, str | None, str | None, str | None]:
    if isinstance(value, dict) and "value" in value and any(
        key in value for key in ("source", "confidence", "reason", "evidence_ref")
    ):
        return (
            value.get("value"),
            value.get("source"),
            value.get("confidence"),
            value.get("reason"),
            value.get("evidence_ref"),
        )
    return value, None, None, None, None


def build_field_evidence(envelope: dict[str, Any], observed_at: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field_id in CANONICAL_CONNECTION_FIELDS:
        candidates = (field_id, f"provider_context.{field_id}") + ALIASES.get(field_id, ())
        found = False
        raw: Any = None
        matched_path: str | None = None
        for path in candidates:
            present, candidate = _lookup(envelope, path)
            if present:
                found = True
                raw = candidate
                matched_path = path
                break

        if found:
            value, source, confidence, reason, evidence_ref = _unwrap(raw)
            unavailable = value in (None, "", "UNAVAILABLE", "UNKNOWN", "NOT_EXPOSED", "NOT_ACCESSIBLE")
            rows.append({
                "field_id": field_id,
                "value": UNAVAILABLE if unavailable else value,
                "status": "UNAVAILABLE" if unavailable else "OBSERVED",
                "source": source or ("not_exposed" if unavailable else "provider_envelope"),
                "confidence": confidence or "exact",
                "reason": reason or (
                    "provider_explicitly_reported_unavailable" if unavailable
                    else None
                ),
                "observed_at": observed_at,
                "evidence_ref": evidence_ref or (
                    f"provider-envelope:{matched_path}" if matched_path else None
                ),
            })
        else:
            rows.append({
                "field_id": field_id,
                "value": UNAVAILABLE,
                "status": "UNAVAILABLE",
                "source": "not_exposed",
                "confidence": "exact",
                "reason": "provider_envelope_did_not_supply_field",
                "observed_at": observed_at,
                "evidence_ref": None,
            })
    return rows
