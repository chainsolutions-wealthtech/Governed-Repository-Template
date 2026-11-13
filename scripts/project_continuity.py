"""Project identity projection. Not an MCP admission, registry write or deployment grant."""
from __future__ import annotations

import re

IDENTITY = "project_continuity"
OWNER_REPO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9_.-]{1,100}$")
REPOSITORY_ID = re.compile(r"^[1-9][0-9]{0,19}$")
REQUEST_ID = re.compile(r"^GR-[0-9]{6,12}$")
GRT_REPOSITORY_ID = "1386478935"


def project_identity_from_request(request_id: str) -> str:
    if not isinstance(request_id, str) or not REQUEST_ID.fullmatch(request_id):
        raise ValueError("PROJECT_CONTINUITY_REQUEST_ID_INVALID")
    return f"WT-PROJECT-GRT-{GRT_REPOSITORY_ID}-{request_id}"


def normalized_github_id(repository_id: str | int) -> str:
    if type(repository_id) not in (int, str) or not REPOSITORY_ID.fullmatch(str(repository_id)):
        raise ValueError("PROJECT_CONTINUITY_REPOSITORY_ID_INVALID")
    return str(repository_id)


def from_github(repository: str, repository_id: str | int, *, request_id: str) -> dict:
    if not isinstance(repository, str) or not OWNER_REPO.fullmatch(repository):
        raise ValueError("PROJECT_CONTINUITY_REPOSITORY_INVALID")
    return {
        "schema_version": "1.0.0",
        "project_continuity_id": project_identity_from_request(request_id),
        "source_request_id": request_id,
        "github_repository_id": normalized_github_id(repository_id),
        "github_repository": repository,
        "server_binding_status": "NOT_BOUND",
    }


def validate_projection(value: dict, repository: str, repository_id: str | int) -> dict:
    if not isinstance(value, dict):
        raise ValueError("PROJECT_CONTINUITY_PROJECTION_MISMATCH")
    expected = from_github(repository, repository_id, request_id=value.get("source_request_id"))
    if not isinstance(value, dict) or set(value) != set(expected) or any(
        value[key] != expected[key] for key in expected if key != "github_repository"
    ) or not isinstance(value.get("github_repository"), str):
        raise ValueError("PROJECT_CONTINUITY_PROJECTION_MISMATCH")
    return expected
