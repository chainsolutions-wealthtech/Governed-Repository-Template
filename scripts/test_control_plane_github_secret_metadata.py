#!/usr/bin/env python3
from __future__ import annotations

import json

from control_plane_github_secret_metadata import collect_github_metadata


def main():
    paths = []
    base = "/repos/chainsolutions-wealthtech/Governed-Repository-Template"
    responses = {
        base: {"full_name": "chainsolutions-wealthtech/Governed-Repository-Template", "default_branch": "main", "private": False, "token": "private-value"},
        base + "/actions/secrets?per_page=100&page=1": {"total_count": 1, "secrets": [{"name": "GOVERNED_MCP_AUTH_TOKEN", "created_at": "2026-09-29T00:00:00Z", "updated_at": "2026-09-30T00:00:00Z", "value": "private-value"}]},
        base + "/actions/organization-secrets?per_page=100&page=1": {"total_count": 0, "secrets": []},
        base + "/environments?per_page=100&page=1": {"total_count": 1, "environments": [{"name": "production", "reviewers": [{"token": "private-value"}]}]},
        base + "/environments/production/secrets?per_page=100&page=1": {"total_count": 1, "secrets": [{"name": "DEPLOY_CREDENTIAL", "updated_at": "2026-09-30T00:00:00Z", "value": "private-value"}]},
    }

    def get(path):
        paths.append(path)
        return responses[path]

    result = collect_github_metadata(
        "chainsolutions-wealthtech/Governed-Repository-Template", get,
        observed_at="2026-09-30T01:00:00+00:00",
    )
    assert all(path.startswith(base) and "?" not in path or "?per_page=100&page=1" in path for path in paths)
    assert len(paths) == 5 and all("/secrets/" not in path for path in paths)
    assert result["repository_secrets"]["status"] == "KNOWN_CURRENT"
    assert result["repository_secrets"]["items"] == [{"name": "GOVERNED_MCP_AUTH_TOKEN", "created_at": "2026-09-29T00:00:00Z", "updated_at": "2026-09-30T00:00:00Z"}]
    assert result["environments"][0]["secrets"]["items"][0]["name"] == "DEPLOY_CREDENTIAL"
    assert result["write_capability"] == "NOT_ATTESTED_BY_READ_PROBE"
    assert result["mutation_authority_granted"] is False
    assert "private-value" not in json.dumps(result)

    def denied(path):
        if "/secrets" in path:
            raise PermissionError("token is private-value")
        return responses[path]

    limited = collect_github_metadata(
        "chainsolutions-wealthtech/Governed-Repository-Template", denied,
        observed_at="2026-09-30T01:00:00+00:00",
    )
    assert limited["repository_secrets"]["status"] == "UNKNOWN_ACCESS_UNAVAILABLE"
    assert "private-value" not in json.dumps(limited)
    assert limited["environments"][0]["secrets"]["status"] == "UNKNOWN_ACCESS_UNAVAILABLE"

    def paged(path):
        if path == base:
            return responses[base]
        if "/actions/secrets?" in path:
            page = int(path.rsplit("=", 1)[1])
            return {"total_count": 101, "secrets": [{"name": f"SECRET_{page}_{n}"} for n in range(100 if page == 1 else 1)]}
        return responses[path]

    complete = collect_github_metadata(
        "chainsolutions-wealthtech/Governed-Repository-Template", paged,
        observed_at="2026-09-30T01:00:00+00:00",
    )
    assert complete["repository_secrets"]["status"] == "KNOWN_CURRENT"
    assert len(complete["repository_secrets"]["items"]) == 101

    try:
        collect_github_metadata("bad/repo/extra", get, observed_at="2026-09-30T01:00:00+00:00")
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe repository name accepted")
    print("CONTROL_PLANE_GITHUB_SECRET_METADATA_TEST_PASS")


if __name__ == "__main__":
    main()
