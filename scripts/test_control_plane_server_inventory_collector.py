#!/usr/bin/env python3
from __future__ import annotations

import json

from control_plane_server_inventory_collector import collect_inventory, collection_plan


def envelope(value):
    return {"result": {"content": [{"type": "text", "text": json.dumps(value)}]}}


def fixture():
    names = [
        "list_domains", "docker_status", "pm2_status", "check_disk", "list_backups"
    ]
    tools = [
        {"name": f"{name}_{server.lower()}", "surface": "read", "input_fields": []}
        for server in ("S1", "S2") for name in names
    ]
    tools += [{"name": "deploy_project_s2", "surface": "scoped-write", "input_fields": []}]
    snapshot = {
        "authority_id": "CP-MCP-CAP-001",
        "observed_at": "2026-09-30T00:00:00+00:00",
        "catalogue": {"catalogue_digest": "catalogue-1", "tools": tools},
        "capability_map": {
            key: {
                "kind": "OBSERVATION",
                "candidate_tools": [{
                    "tool": item["name"], "surface": "read",
                    "authority_required": "READ_ONLY_DISCOVERY_AUTHORITY",
                    "scope": {"mode": "GENERIC"},
                } for item in tools if item["name"].startswith(prefixes)],
            }
            for key, prefixes in (
                ("DOMAIN_WEB_OBSERVATION", ("list_domains",)),
                ("SERVER_RUNTIME_OBSERVATION", ("docker_status", "pm2_status", "check_disk", "list_backups")),
            )
        },
    }
    live = [{"name": item["name"], "annotations": {"readOnlyHint": True}} for item in tools]
    return snapshot, live


def main():
    snapshot, live = fixture()
    plan = collection_plan(snapshot, live)
    assert len(plan) == 10 and all(item["status"] == "READY" for item in plan)
    assert "deploy_project_s2" not in {item["tool"] for item in plan}

    responses = {
        "list_domains_s1": {"domains": ["example.org", "https://bad.test/key=secret", "example.org"]},
        "list_domains_s2": {"domains": ["s2.example.org"]},
        "docker_status_s1": {"containers": [{"name": "private", "status": "running", "env": "secret"}]},
        "pm2_status_s1": {"apps": [{"name": "private", "status": "online", "token": "secret"}]},
        "check_disk_s1": {"filesystems": [{"mount": "/private", "used_percent": 81, "password": "secret"}]},
        "list_backups_s1": {"backups": [{"path": "/private/backup", "token": "secret"}]},
    }
    calls = []

    def invoke(name):
        calls.append(name)
        return envelope(responses.get(name, {"message": "unstructured secret"}))

    result = collect_inventory(snapshot, live, invoke, observed_at="2026-09-30T01:00:00+00:00")
    assert set(result["servers"]) == {"S1", "S2"}
    assert len(calls) == 10 and "deploy_project_s2" not in calls
    s1 = result["servers"]["S1"]
    assert s1["DOMAINS_VHOSTS"]["facts"] == {"domains": ["example.org"]}
    assert s1["DOMAINS_VHOSTS"]["status"] == "PARTIAL_BOUNDED"
    assert s1["RUNTIMES"]["docker_status"]["facts"] == {"container_count": 1, "states": {"running": 1}}
    assert s1["RUNTIMES"]["pm2_status"]["facts"] == {"process_count": 1, "states": {"online": 1}}
    assert s1["CAPACITY"]["facts"] == {"max_disk_used_percent": 81}
    assert s1["BACKUP_RECOVERY"]["facts"] == {"backup_count": 1}
    assert result["servers"]["S2"]["CAPACITY"]["status"] == "UNKNOWN_DISCOVERABLE"
    assert result["mutation_authority_granted"] is False
    serialized = json.dumps(result)
    for leak in ("unstructured secret", "confidential-data", "/private", "https://bad", "password"):
        assert leak not in serialized, leak

    def schema_error(name):
        return envelope({"error": "Bearer confidential-data", "domains": []}) if name == "list_domains_s2" else invoke(name)

    failed_domain = collect_inventory(snapshot, live, schema_error, observed_at="2026-09-30T01:00:00+00:00")
    assert failed_domain["servers"]["S2"]["DOMAINS_VHOSTS"]["status"] == "UNKNOWN_DISCOVERABLE"
    assert "confidential-data" not in json.dumps(failed_domain)

    snapshot["catalogue"]["tools"][1]["surface"] = "scoped-write"
    live[2]["annotations"]["readOnlyHint"] = False
    plan = collection_plan(snapshot, live)
    blocked = {item["tool"]: item["status"] for item in plan}
    assert blocked["docker_status_s1"] == "BLOCKED"
    assert blocked["pm2_status_s1"] == "BLOCKED"
    next(item for item in snapshot["capability_map"]["SERVER_RUNTIME_OBSERVATION"]["candidate_tools"] if item["tool"] == "docker_status_s2")["surface"] = "scoped-write"
    assert {item["tool"]: item["status"] for item in collection_plan(snapshot, live)}["docker_status_s2"] == "BLOCKED"
    calls.clear()
    result = collect_inventory(snapshot, live, invoke, observed_at="2026-09-30T01:00:00+00:00")
    assert "docker_status_s1" not in calls and "pm2_status_s1" not in calls
    assert result["servers"]["S1"]["RUNTIMES"]["docker_status"]["status"] == "UNKNOWN_DISCOVERABLE"

    def failing(name):
        raise RuntimeError("Bearer confidential-data")

    result = collect_inventory(snapshot, live, failing, observed_at="2026-09-30T01:00:00+00:00")
    assert "confidential-data" not in json.dumps(result)
    assert result["servers"]["S2"]["DOMAINS_VHOSTS"]["status"] == "UNKNOWN_DISCOVERABLE"
    print("CONTROL_PLANE_SERVER_INVENTORY_COLLECTOR_TEST_PASS")


if __name__ == "__main__":
    main()
