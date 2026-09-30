#!/usr/bin/env python3
"""Validate and persist bounded KBI-04C observations as KBI-04D source memory.

This is an offline projection. It neither invokes MCP nor authorizes a mutation.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import pathlib
import re
import stat
import tempfile
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
STATE = ROOT / ".governance/control-plane-state/server-inventory-facts.json"
SNAPSHOT = ROOT / ".governance/control-plane-state/mcp-capability-snapshot.json"
MODEL = ROOT / ".governance/control-plane-state/server-knowledge-model.json"
SLOTS = {
    "DOMAINS_VHOSTS": {"domains": "list_domains"},
    "RUNTIMES": {"docker_status": "docker_status", "pm2_status": "pm2_status"},
    "CAPACITY": {"disk": "check_disk"},
    "BACKUP_RECOVERY": {"backups": "list_backups"},
}
STATES = {"running", "stopped", "exited", "online", "offline", "errored", "error", "unknown"}
DOMAIN = re.compile(r"(?=.{4,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{1,62}$")
DIGEST = re.compile(r"[0-9a-f]{64}")
UNOBSERVED = {
    "SERVER_IDENTITY", "HOSTING_STACK", "NETWORK", "DNS", "TLS", "FILESYSTEM_LAYOUT",
    "PORTS_SERVICES", "DATABASES", "GIT_DEPLOYMENT", "SECRETS_ENV", "PROCESS_SCHEDULING",
    "OBSERVABILITY", "SECURITY_ACCESS", "PROJECT_MAPPINGS", "MCP_SURFACES",
}


def keys(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError("KBI_04D_INVALID_SHAPE")


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("KBI_04D_INVALID_TIMESTAMP")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise ValueError("KBI_04D_INVALID_TIMESTAMP") from None
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError("KBI_04D_INVALID_TIMESTAMP")
    return parsed


def digest(value):
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise ValueError("KBI_04D_INVALID_DIGEST")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def observation_hash(fact_id, source, observed_at, status, facts):
    return hashlib.sha256(canonical({
        "fact_id": fact_id, "source": source, "observed_at": observed_at,
        "status": status, "facts": facts,
    }).encode("utf-8")).hexdigest()


def source_from_provenance(provenance):
    return {
        "snapshot_authority_id": provenance["snapshot_authority_id"],
        "snapshot_observed_at": provenance["snapshot_observed_at"],
        "catalogue_digest": provenance["catalogue_digest"],
        "method": provenance["method"],
    }


def read_only_tool(snapshot, name, domain):
    catalogue = snapshot.get("catalogue") or {}
    matches = [item for item in catalogue.get("tools", []) if isinstance(item, dict) and item.get("name") == name]
    if len(matches) != 1:
        return False
    tool = matches[0]
    fields = tool.get("input_fields")
    if tool.get("surface") != "read" or tool.get("authority_required") != "READ_ONLY_DISCOVERY_AUTHORITY" or not isinstance(fields, list) or any(field.get("required") for field in fields if isinstance(field, dict)):
        return False
    capability_id = "DOMAIN_WEB_OBSERVATION" if domain == "DOMAINS_VHOSTS" else "SERVER_RUNTIME_OBSERVATION"
    capability = (snapshot.get("capability_map") or {}).get(capability_id) or {}
    candidates = [item for item in capability.get("candidate_tools", []) if isinstance(item, dict) and item.get("tool") == name]
    return capability.get("kind") == "OBSERVATION" and len(candidates) == 1 and candidates[0].get("surface") == "read" and candidates[0].get("authority_required") == "READ_ONLY_DISCOVERY_AUTHORITY" and (candidates[0].get("scope") or {}).get("mode") == "GENERIC"


def allowed_facts(slot, value):
    if not isinstance(value, dict):
        raise ValueError("KBI_04D_INVALID_FACTS")
    if slot == "domains":
        keys(value, {"domains"})
        domains = value["domains"]
        if not isinstance(domains, list) or len(domains) > 200 or any(
            not isinstance(name, str) or not DOMAIN.fullmatch(name) for name in domains
        ) or domains != sorted(set(domains)):
            raise ValueError("KBI_04D_INVALID_DOMAINS")
    elif slot in ("docker_status", "pm2_status"):
        count_field = "container_count" if slot == "docker_status" else "process_count"
        keys(value, {count_field, "states"})
        total, states = value[count_field], value["states"]
        if type(total) is not int or not 0 <= total <= 100000 or not isinstance(states, dict) or any(
            state not in STATES or type(count) is not int or count < 0 for state, count in states.items()
        ) or sum(states.values()) != total:
            raise ValueError("KBI_04D_INVALID_RUNTIME")
    elif slot == "disk":
        keys(value, {"max_disk_used_percent"})
        percent = value["max_disk_used_percent"]
        if type(percent) not in (int, float) or not math.isfinite(percent) or not 0 <= percent <= 100:
            raise ValueError("KBI_04D_INVALID_CAPACITY")
    elif slot == "backups":
        keys(value, {"backup_count"})
        count = value["backup_count"]
        if type(count) is not int or not 0 <= count <= 100000:
            raise ValueError("KBI_04D_INVALID_BACKUPS")
    else:
        raise ValueError("KBI_04D_UNKNOWN_SLOT")


def freshness(model):
    if model.get("authority_id") != "CP-SERVER-KNOWLEDGE-001":
        raise ValueError("KBI_04D_MODEL_AUTHORITY")
    domains = {item["id"]: item["freshness"] for item in model["inventory_domains"]}
    if any(domain not in domains for domain in SLOTS):
        raise ValueError("KBI_04D_MODEL_DOMAINS")
    return domains


def validate_provenance(value, *, attempt=False):
    fields = {"source_tool", "collector_slice", "snapshot_authority_id", "snapshot_observed_at",
              "catalogue_digest", "observation_digest", "method", "observed_at"}
    keys(value, fields | ({"status"} if attempt else set()))
    if value["source_tool"] not in {
        f"{tool}_{server.lower()}" for server in ("S1", "S2") for slots in SLOTS.values() for tool in slots.values()
    } or value["collector_slice"] != "KBI-04C" or value["snapshot_authority_id"] != "CP-MCP-CAP-001" or value["method"] != "LIVE_MCP_READ_ONLY_TOOL_INTERSECTION":
        raise ValueError("KBI_04D_INVALID_PROVENANCE")
    if attempt and value["status"] not in {"KNOWN_CURRENT", "UNKNOWN_DISCOVERABLE", "PARTIAL_BOUNDED"}:
        raise ValueError("KBI_04D_INVALID_ATTEMPT")
    timestamp(value["observed_at"])
    timestamp(value["snapshot_observed_at"])
    digest(value["catalogue_digest"])
    digest(value["observation_digest"])


def validate_inventory_state(state, model):
    """Validate persisted records before use by the relational materializer."""
    keys(state, {"schema_version", "authority_id", "scope", "status", "revision", "last_ingested_at",
                 "execution_authority_granted", "secret_values_persisted", "facts"})
    if state["schema_version"] != "1.0.0" or state["authority_id"] != "CP-SERVER-KNOWLEDGE-001" or state["scope"] != "CONTROL_PLANE_SOURCE_ONLY" or state["execution_authority_granted"] is not False or state["secret_values_persisted"] is not False:
        raise ValueError("KBI_04D_STATE_AUTHORITY")
    if type(state["revision"]) is not int or state["revision"] < 0 or not isinstance(state["facts"], list):
        raise ValueError("KBI_04D_STATE_REVISION")
    if state["revision"] == 0:
        if state["status"] != "NOT_COLLECTED" or state["last_ingested_at"] is not None or state["facts"]:
            raise ValueError("KBI_04D_STATE_INITIAL")
        return
    if state["status"] != "PARTIAL_BOUNDED_OBSERVATION" or not isinstance(state["last_ingested_at"], str):
        raise ValueError("KBI_04D_STATE_STATUS")
    latest = timestamp(state["last_ingested_at"])
    classes = freshness(model)
    expected = {f"{server}:{domain}:{slot}" for server in ("S1", "S2") for domain, slots in SLOTS.items() for slot in slots}
    if len(state["facts"]) != len(expected):
        raise ValueError("KBI_04D_STATE_COUNT")
    seen = set()
    for record in state["facts"]:
        keys(record, {"fact_id", "server_id", "domain_id", "slot", "status", "value",
                      "freshness_class", "observed_at", "known_from", "last_attempt"})
        server, domain, slot = record["server_id"], record["domain_id"], record["slot"]
        fact_id = f"{server}:{domain}:{slot}"
        if fact_id not in expected or record["fact_id"] != fact_id or fact_id in seen or record["freshness_class"] != classes[domain]:
            raise ValueError("KBI_04D_STATE_FACT_ID")
        seen.add(fact_id)
        attempt = record["last_attempt"]
        validate_provenance(attempt, attempt=True)
        if attempt["source_tool"] != f"{SLOTS[domain][slot]}_{server.lower()}" or timestamp(attempt["observed_at"]) != latest:
            raise ValueError("KBI_04D_STATE_ATTEMPT")
        if record["status"] not in {"KNOWN_CURRENT", "KNOWN_STALE", "UNKNOWN_DISCOVERABLE"}:
            raise ValueError("KBI_04D_STATE_FACT_STATUS")
        if record["status"] == "UNKNOWN_DISCOVERABLE":
            if record["value"] is not None or record["observed_at"] is not None or record["known_from"] is not None or attempt["status"] == "KNOWN_CURRENT":
                raise ValueError("KBI_04D_STATE_UNKNOWN")
        else:
            allowed_facts(slot, record["value"])
            validate_provenance(record["known_from"])
            if record["observed_at"] != record["known_from"]["observed_at"] or record["known_from"]["source_tool"] != attempt["source_tool"] or timestamp(record["observed_at"]) > latest:
                raise ValueError("KBI_04D_STATE_KNOWN")
            if record["known_from"]["observation_digest"] != observation_hash(
                fact_id, source_from_provenance(record["known_from"]), record["observed_at"],
                "KNOWN_CURRENT", record["value"],
            ):
                raise ValueError("KBI_04D_STATE_VALUE_DIGEST")
            if (record["status"] == "KNOWN_CURRENT") != (attempt["status"] == "KNOWN_CURRENT"):
                raise ValueError("KBI_04D_STATE_FRESHNESS")
            if record["status"] == "KNOWN_CURRENT" and record["known_from"] != {key: value for key, value in attempt.items() if key != "status"}:
                raise ValueError("KBI_04D_STATE_CURRENT_SOURCE")


def normalize_inventory(incoming, state, snapshot, model, *, now=None):
    validate_inventory_state(state, model)
    keys(incoming, {"schema_version", "authority_id", "slice", "status", "observed_at", "source",
                    "mutation_authority_granted", "secret_values_persisted", "servers", "unobserved_inventory_domains"})
    if incoming["schema_version"] != "1.0.0" or incoming["authority_id"] != "CP-SERVER-KNOWLEDGE-001" or incoming["slice"] != "KBI-04C" or incoming["status"] != "PARTIAL_BOUNDED_OBSERVATION" or incoming["mutation_authority_granted"] is not False or incoming["secret_values_persisted"] is not False:
        raise ValueError("KBI_04D_COLLECTOR_AUTHORITY")
    if not isinstance(incoming["unobserved_inventory_domains"], list) or set(incoming["unobserved_inventory_domains"]) != UNOBSERVED or len(incoming["unobserved_inventory_domains"]) != len(UNOBSERVED):
        raise ValueError("KBI_04D_UNOBSERVED_DOMAINS")
    keys(incoming["source"], {"snapshot_authority_id", "snapshot_observed_at", "catalogue_digest", "method"})
    source = incoming["source"]
    if snapshot.get("authority_id") != "CP-MCP-CAP-001" or source != {
        "snapshot_authority_id": snapshot["authority_id"],
        "snapshot_observed_at": snapshot["observed_at"],
        "catalogue_digest": snapshot["catalogue"]["catalogue_digest"],
        "method": "LIVE_MCP_READ_ONLY_TOOL_INTERSECTION",
    }:
        raise ValueError("KBI_04D_SNAPSHOT_MISMATCH")
    digest(source["catalogue_digest"])
    observed = timestamp(incoming["observed_at"])
    current = timestamp(now) if now is not None else datetime.now(timezone.utc)
    if observed < timestamp(source["snapshot_observed_at"]) or observed > current + timedelta(minutes=2):
        raise ValueError("KBI_04D_TIME_ORDER")
    keys(incoming["servers"], {"S1", "S2"})
    classes = freshness(model)
    old = {item["fact_id"]: item for item in state["facts"]}
    records = []
    replayed = 0
    for server in ("S1", "S2"):
        keys(incoming["servers"][server], SLOTS)
        for domain, slots in SLOTS.items():
            if domain == "RUNTIMES":
                keys(incoming["servers"][server][domain], slots)
            for slot, prefix in slots.items():
                item = (incoming["servers"][server][domain][slot] if domain == "RUNTIMES"
                        else incoming["servers"][server][domain])
                keys(item, {"status", "tool", "facts"})
                tool = f"{prefix}_{server.lower()}"
                if item["tool"] != tool or item["status"] not in {"KNOWN_CURRENT", "UNKNOWN_DISCOVERABLE", "PARTIAL_BOUNDED"}:
                    raise ValueError("KBI_04D_SLOT_AUTHORITY")
                if item["status"] == "UNKNOWN_DISCOVERABLE":
                    if item["facts"] != {}:
                        raise ValueError("KBI_04D_UNKNOWN_FACTS")
                else:
                    allowed_facts(slot, item["facts"])
                    if item["status"] == "KNOWN_CURRENT" and not read_only_tool(snapshot, tool, domain):
                        raise ValueError("KBI_04D_TOOL_NOT_READ_ONLY")
                fact_id = f"{server}:{domain}:{slot}"
                attempt = {
                    "source_tool": tool, "collector_slice": "KBI-04C",
                    "snapshot_authority_id": source["snapshot_authority_id"],
                    "snapshot_observed_at": source["snapshot_observed_at"],
                    "catalogue_digest": source["catalogue_digest"],
                    "method": source["method"], "observed_at": incoming["observed_at"],
                    "observation_digest": observation_hash(
                        fact_id, source, incoming["observed_at"], item["status"], item["facts"]),
                    "status": item["status"],
                }
                previous = old.get(fact_id)
                if previous:
                    previous_time = timestamp(previous["last_attempt"]["observed_at"])
                    if observed < previous_time:
                        raise ValueError("KBI_04D_OLDER_OBSERVATION")
                    if observed == previous_time:
                        if attempt != previous["last_attempt"]:
                            raise ValueError("KBI_04D_CONTRADICTED_OBSERVATION")
                        replayed += 1
                        records.append(previous)
                        continue
                known = item["status"] == "KNOWN_CURRENT"
                had_known = previous is not None and previous["known_from"] is not None
                record = {
                    "fact_id": fact_id, "server_id": server, "domain_id": domain, "slot": slot,
                    "status": "KNOWN_CURRENT" if known else "KNOWN_STALE" if had_known else "UNKNOWN_DISCOVERABLE",
                    "value": item["facts"] if known else previous["value"] if had_known else None,
                    "freshness_class": classes[domain],
                    "observed_at": incoming["observed_at"] if known else previous["observed_at"] if had_known else None,
                    "known_from": {key: value for key, value in attempt.items() if key != "status"} if known else previous["known_from"] if had_known else None,
                    "last_attempt": attempt,
                }
                records.append(record)
    if replayed == len(records):
        return state
    if replayed:
        raise ValueError("KBI_04D_MIXED_REPLAY")
    result = {
        "schema_version": "1.0.0", "authority_id": "CP-SERVER-KNOWLEDGE-001",
        "scope": "CONTROL_PLANE_SOURCE_ONLY", "status": "PARTIAL_BOUNDED_OBSERVATION",
        "revision": state["revision"] + 1, "last_ingested_at": incoming["observed_at"],
        "execution_authority_granted": False, "secret_values_persisted": False,
        "facts": sorted(records, key=lambda record: record["fact_id"]),
    }
    validate_inventory_state(result, model)
    return result


def persist_inventory(input_path, output_path, expected_revision, snapshot_path=SNAPSHOT, model_path=MODEL):
    if expected_revision < 0:
        raise ValueError("KBI_04D_REVISION_INVALID")
    if input_path.stat().st_size > 1024 * 1024:
        raise ValueError("KBI_04D_INPUT_TOO_LARGE")
    incoming = json.loads(input_path.read_text(encoding="utf-8"))
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    model = json.loads(model_path.read_text(encoding="utf-8"))
    # The directory lock serializes atomic replacements of the state file.
    lock_fd = os.open(output_path.parent, os.O_RDONLY)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        mode = stat.S_IMODE(output_path.stat().st_mode)
        state = json.loads(output_path.read_text(encoding="utf-8"))
        if state["revision"] != expected_revision:
            raise ValueError("KBI_04D_REVISION_MOVED")
        result = normalize_inventory(incoming, state, snapshot, model)
        if result != state:
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output_path.parent,
                                                 prefix=".server-inventory-", delete=False) as handle:
                    temporary = pathlib.Path(handle.name)
                    handle.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                os.chmod(temporary, mode)
                os.replace(temporary, output_path)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        return result
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, required=True, help="Saved KBI-04C JSON observation")
    parser.add_argument("--output", type=pathlib.Path, default=STATE)
    parser.add_argument("--expected-revision", type=int, required=True)
    args = parser.parse_args()
    try:
        result = persist_inventory(args.input, args.output, args.expected_revision)
    except (OSError, ValueError, KeyError, TypeError, OverflowError, json.JSONDecodeError) as exc:
        # Neither malformed input nor filesystem errors may expose raw remote material.
        raise SystemExit(f"KBI_04D_FAILED:{type(exc).__name__}") from None
    print(f"KBI_04D_PERSISTED revision={result['revision']} slots={len(result['facts'])}")


if __name__ == "__main__":
    main()
