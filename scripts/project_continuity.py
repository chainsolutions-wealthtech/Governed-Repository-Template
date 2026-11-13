"""Project identity projection. Not an MCP admission, registry write or deployment grant."""
from __future__ import annotations

import re

IDENTITY = "project_continuity"
OWNER_REPO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9_.-]{1,100}$")
REPOSITORY_ID = re.compile(r"^[1-9][0-9]{0,19}$")


def identity_from_github(repository_id: str | int) -> str:
    if type(repository_id) not in (int, str) or not REPOSITORY_ID.fullmatch(str(repository_id)):
        raise ValueError("PROJECT_CONTINUITY_REPOSITORY_ID_INVALID")
    return f"WT-PROJECT-GITHUB-{repository_id}"


def from_github(repository: str, repository_id: str | int) -> dict:
    if not isinstance(repository, str) or not OWNER_REPO.fullmatch(repository):
        raise ValueError("PROJECT_CONTINUITY_REPOSITORY_INVALID")
    return {
        "schema_version": "1.0.0",
        "project_continuity_id": identity_from_github(repository_id),
        "github_repository_id": str(repository_id),
        "github_repository": repository,
        "server_binding_status": "NOT_BOUND",
    }


def validate_projection(value: dict, repository: str, repository_id: str | int) -> dict:
    expected = from_github(repository, repository_id)
    if not isinstance(value, dict) or set(value) != set(expected) or any(
        value[key] != expected[key] for key in expected if key != "github_repository"
    ) or not isinstance(value.get("github_repository"), str):
        raise ValueError("PROJECT_CONTINUITY_PROJECTION_MISMATCH")
    return expected
