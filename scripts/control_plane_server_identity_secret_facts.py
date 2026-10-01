#!/usr/bin/env python3
"""Persist bounded KBI-04K identity/secret metadata as reusable control-plane facts.

This adapter never contacts MCP. It validates an already collected read-only
observation, recomputes all mechanism classifications from canonical source
models, and atomically persists metadata/digests only.
"""
from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import json
import os
import re
import stat
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from control_plane_server_identity_secret_metadata import (
    IDENTITY_MODEL_PATH,
    SERVER_PROBES,
    build_plan,
)
from governed_execution_engine import ROOT, SNAPSHOT_PATH, load_json

STATE_PATH = ROOT / ".governance" / "control-plane-state" / "server-identity-secret-facts.json"
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_PROBE_STATUSES = {
    "PASS", "OK", "SUCCESS", "PARTIAL", "UNKNOWN", "EMPTY", "KNOWN_CURRENT",
    "NOT_FOUND", "NO_FINDINGS", "OBSERVED_RESPONSE", "NOT_EXPOSED",
    "UNSAFE_SURFACE_REJECTED", "OBSERVATION_FAILED",
}
SAFE_KINDS = {"OBJECT", "ARRAY", "STR", "STRING", "INT", "INTEGER", "FLOAT", "BOOL", "BOOLEAN", "NONETYPE", "NULL"}
MECHANISM_FRESHNESS = "EVENT_AND_NEED_BASED"
PROBE_FRESHNESS = "LIVE_OR_BOUNDED_TTL"


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("KBI_04K_FACTS_TIMESTAMP_INVALID")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise ValueError("KBI_04K_FACTS_TIMESTAMP_INVALID") from None
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError("KBI_04K_FACTS_TIMESTAMP_INVALID")
    return parsed


def digest(value: str) -> None:
    if not isinstance(value, str) or not DIGEST_RE.fullmatch(value):
        raise ValueError("KBI_04K_FACTS_DIGEST_INVALID")


def observation_digest(fact_id: str, metadata: dict, observed_at: str, source_digest: str) -> str:
    return hashlib.sha256(canonical({
        "fact_id": fact_id,
        "metadata": metadata,
        "observed_at": observed_at,
        "catalogue_digest": source_digest,
    }).encode("utf-8")).hexdigest()


def _assert_safe_scalar(value, path="$") -> None:
    if value is None or isinstance(value, (bool, int, float)):
        return
    if isinstance(value, str):
        lowered = value.lower()
        forbidden_markers = (
            "-----begin private key-----", "github_pat_", "ghp_", "bearer ",
            "password=", "token=", "secret=",
        )
        if any(marker in lowered for marker in forbidden_markers):
            raise ValueError(f"KBI_04K_FACTS_SECRET_LIKE_VALUE:{path}")
        if len(value) > 1000:
            raise ValueError(f"KBI_04K_FACTS_STRING_TOO_LONG:{path}")
        return
    raise ValueError(f"KBI_04K_FACTS_SCALAR_INVALID:{path}")


def assert_safe_metadata(value, path="$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).lower()
            if lowered in {"secret", "secret_value", "password", "token", "private_key", "authorization"}:
                raise ValueError(f"KBI_04K_FACTS_FORBIDDEN_KEY:{path}.{key}")
            assert_safe_metadata(item, f"{path}.{key}")
    elif isinstance(value, list):
        if len(value) > 200:
            raise ValueError(f"KBI_04K_FACTS_LIST_TOO_LONG:{path}")
        for index, item in enumerate(value):
            assert_safe_metadata(item, f"{path}[{index}]")
    else:
        _assert_safe_scalar(value, path)


def validate_initial_or_persisted_state(state: dict) -> None:
    expected = {
        "schema_version", "authority_id", "scope", "status", "revision", "last_ingested_at",
        "execution_authority_granted", "secret_values_persisted",
        "raw_remote_payload_persisted", "server_connection_coordinates_persisted", "facts",
    }
    if not isinstance(state, dict) or set(state) != expected:
        raise ValueError("KBI_04K_FACTS_STATE_SHAPE")
    if state["schema_version"] != "1.0.0" or state["authority_id"] != "CP-IDENTITY-SECRET-001":
        raise ValueError("KBI_04K_FACTS_STATE_AUTHORITY")
    if state["scope"] != "CONTROL_PLANE_SOURCE_ONLY":
        raise ValueError("KBI_04K_FACTS_STATE_SCOPE")
    for key in (
        "execution_authority_granted", "secret_values_persisted",
        "raw_remote_payload_persisted", "server_connection_coordinates_persisted",
    ):
        if state[key] is not False:
            raise ValueError(f"KBI_04K_FACTS_STATE_UNSAFE:{key}")
    if type(state["revision"]) is not int or state["revision"] < 0 or not isinstance(state["facts"], list):
        raise ValueError("KBI_04K_FACTS_STATE_REVISION")
    if state["revision"] == 0:
        if state["status"] != "NOT_COLLECTED" or state["last_ingested_at"] is not None or state["facts"]:
            raise ValueError("KBI_04K_FACTS_STATE_INITIAL")
        return
    if state["status"] != "PARTIAL_BOUNDED_METADATA" or not isinstance(state["last_ingested_at"], str):
        raise ValueError("KBI_04K_FACTS_STATE_STATUS")
    latest = timestamp(state["last_ingested_at"])
    seen = set()
    for fact in state["facts"]:
        required = {
            "fact_id", "server_id", "fact_kind", "subject_id", "status", "metadata",
            "freshness_class", "observed_at", "known_from", "last_attempt",
        }
        if not isinstance(fact, dict) or set(fact) != required:
            raise ValueError("KBI_04K_FACTS_FACT_SHAPE")
        if fact["fact_id"] in seen:
            raise ValueError("KBI_04K_FACTS_DUPLICATE")
        seen.add(fact["fact_id"])
        if fact["server_id"] not in {"S1", "S2"} or fact["fact_kind"] not in {"MECHANISM", "PROBE"}:
            raise ValueError("KBI_04K_FACTS_FACT_IDENTITY")
        if fact["freshness_class"] not in {MECHANISM_FRESHNESS, PROBE_FRESHNESS}:
            raise ValueError("KBI_04K_FACTS_FRESHNESS")
        assert_safe_metadata(fact["metadata"])
        if timestamp(fact["observed_at"]) > latest:
            raise ValueError("KBI_04K_FACTS_TIME_ORDER")
        for provenance in (fact["known_from"], fact["last_attempt"]):
            if not isinstance(provenance, dict):
                raise ValueError("KBI_04K_FACTS_PROVENANCE")
            digest(provenance.get("catalogue_digest"))
            digest(provenance.get("observation_digest"))
            timestamp(provenance.get("snapshot_observed_at"))
            timestamp(provenance.get("observed_at"))
            if provenance.get("collector_slice") != "KBI-04K":
                raise ValueError("KBI_04K_FACTS_PROVENANCE_SLICE")


def validate_probe(tool: str, probe: dict, plan_probe: dict) -> dict:
    if not isinstance(probe, dict) or probe.get("tool") != tool:
        raise ValueError("KBI_04K_FACTS_PROBE_TOOL")
    status = probe.get("status")
    if status not in SAFE_PROBE_STATUSES or probe.get("raw_payload_persisted") is not False:
        raise ValueError("KBI_04K_FACTS_PROBE_STATUS")
    safe_surface = (
        plan_probe.get("available") is True
        and plan_probe.get("surface") == "read"
        and plan_probe.get("authority_required") == "READ_ONLY_DISCOVERY_AUTHORITY"
    )
    if not plan_probe.get("available") and status != "NOT_EXPOSED":
        raise ValueError("KBI_04K_FACTS_PROBE_NOT_EXPOSED_MISMATCH")
    if plan_probe.get("available") and not safe_surface and status != "UNSAFE_SURFACE_REJECTED":
        raise ValueError("KBI_04K_FACTS_PROBE_UNSAFE_MISMATCH")

    compact = {"tool": tool, "status": status, "raw_payload_persisted": False}
    summary_fields = {"response_kind", "item_count", "top_level_keys", "response_digest"}
    present = summary_fields & set(probe)
    if present:
        if present != summary_fields or not safe_surface:
            raise ValueError("KBI_04K_FACTS_PROBE_SUMMARY_SHAPE")
        kind = probe["response_kind"]
        count = probe["item_count"]
        keys = probe["top_level_keys"]
        response_digest = probe["response_digest"]
        if not isinstance(kind, str) or kind not in SAFE_KINDS:
            # Python may report additional benign type names; only strict safe identifiers are allowed.
            if not re.fullmatch(r"[A-Z][A-Z0-9_]{0,31}", str(kind)):
                raise ValueError("KBI_04K_FACTS_PROBE_KIND")
        if type(count) is not int or not 0 <= count <= 100000:
            raise ValueError("KBI_04K_FACTS_PROBE_COUNT")
        if not isinstance(keys, list) or len(keys) > 32 or any(
            not isinstance(key, str) or len(key) > 128 for key in keys
        ):
            raise ValueError("KBI_04K_FACTS_PROBE_KEYS")
        digest(response_digest)
        compact.update({
            "response_kind": kind,
            "item_count": count,
            "top_level_keys": keys,
            "response_digest": response_digest,
        })
    elif status not in {"NOT_EXPOSED", "UNSAFE_SURFACE_REJECTED", "OBSERVATION_FAILED"}:
        raise ValueError("KBI_04K_FACTS_PROBE_SUMMARY_REQUIRED")
    assert_safe_metadata(compact)
    return compact


def normalize_observation(observation: dict, snapshot: dict, identity_model: dict) -> list[dict]:
    required = {
        "schema_version", "authority_id", "slice", "mode", "observed_at",
        "source_snapshot_observed_at", "catalogue_digest", "servers",
        "mutation_authority_granted", "secret_values_persisted",
        "raw_remote_payload_persisted", "server_connection_coordinates_persisted",
    }
    if not isinstance(observation, dict) or set(observation) != required:
        raise ValueError("KBI_04K_FACTS_INPUT_SHAPE")
    if (
        observation["schema_version"] != "1.0.0"
        or observation["authority_id"] != "CP-IDENTITY-SECRET-001"
        or observation["slice"] != "KBI-04K"
        or observation["mode"] != "READ_ONLY_METADATA_OBSERVATION"
    ):
        raise ValueError("KBI_04K_FACTS_INPUT_AUTHORITY")
    for key in (
        "mutation_authority_granted", "secret_values_persisted",
        "raw_remote_payload_persisted", "server_connection_coordinates_persisted",
    ):
        if observation[key] is not False:
            raise ValueError(f"KBI_04K_FACTS_INPUT_UNSAFE:{key}")
    observed = timestamp(observation["observed_at"])
    snapshot_time = timestamp(observation["source_snapshot_observed_at"])
    if observed < snapshot_time:
        raise ValueError("KBI_04K_FACTS_INPUT_TIME_ORDER")
    expected_digest = (snapshot.get("catalogue") or {}).get("catalogue_digest")
    if observation["source_snapshot_observed_at"] != snapshot.get("observed_at") or observation["catalogue_digest"] != expected_digest:
        raise ValueError("KBI_04K_FACTS_SNAPSHOT_MISMATCH")
    digest(observation["catalogue_digest"])
    if set(observation["servers"]) != {"S1", "S2"}:
        raise ValueError("KBI_04K_FACTS_SERVERS_REQUIRED")

    plan = build_plan(snapshot, identity_model, ["S1", "S2"])
    records = []
    for server_id in ("S1", "S2"):
        incoming_server = observation["servers"][server_id]
        if not isinstance(incoming_server, dict) or set(incoming_server) != {
            "mechanisms", "observations", "identity_secret_store_status"
        }:
            raise ValueError("KBI_04K_FACTS_SERVER_SHAPE")
        if incoming_server["identity_secret_store_status"] not in {"PARTIAL_BOUNDED_OBSERVATION", "UNKNOWN_DISCOVERABLE"}:
            raise ValueError("KBI_04K_FACTS_SERVER_STATUS")
        expected_mechanisms = plan["servers"][server_id]["mechanisms"]
        if incoming_server["mechanisms"] != expected_mechanisms:
            raise ValueError("KBI_04K_FACTS_MECHANISM_SOURCE_MISMATCH")
        for mechanism in expected_mechanisms:
            metadata = copy.deepcopy(mechanism)
            assert_safe_metadata(metadata)
            records.append({
                "fact_id": f"{server_id}:MECHANISM:{mechanism['credential_type']}",
                "server_id": server_id,
                "fact_kind": "MECHANISM",
                "subject_id": mechanism["credential_type"],
                "status": mechanism["status"],
                "metadata": metadata,
                "freshness_class": MECHANISM_FRESHNESS,
            })

        plan_probes = {item["tool"]: item for item in plan["servers"][server_id]["probes"]}
        observations = incoming_server["observations"]
        if not isinstance(observations, list) or {item.get("tool") for item in observations if isinstance(item, dict)} != set(plan_probes):
            raise ValueError("KBI_04K_FACTS_PROBE_SET")
        by_tool = {item["tool"]: item for item in observations}
        if len(by_tool) != len(observations):
            raise ValueError("KBI_04K_FACTS_PROBE_DUPLICATE")
        for tool, plan_probe in plan_probes.items():
            metadata = validate_probe(tool, by_tool[tool], plan_probe)
            records.append({
                "fact_id": f"{server_id}:PROBE:{tool}",
                "server_id": server_id,
                "fact_kind": "PROBE",
                "subject_id": tool,
                "status": metadata["status"],
                "metadata": metadata,
                "freshness_class": PROBE_FRESHNESS,
            })
    return records


def make_provenance(record: dict, observation: dict) -> dict:
    return {
        "collector_slice": "KBI-04K",
        "snapshot_observed_at": observation["source_snapshot_observed_at"],
        "catalogue_digest": observation["catalogue_digest"],
        "observed_at": observation["observed_at"],
        "observation_digest": observation_digest(
            record["fact_id"], record["metadata"], observation["observed_at"], observation["catalogue_digest"]
        ),
    }


def persist(observation: dict, state: dict, snapshot: dict, identity_model: dict) -> dict:
    validate_initial_or_persisted_state(state)
    records = normalize_observation(observation, snapshot, identity_model)
    observed = timestamp(observation["observed_at"])
    old = {item["fact_id"]: item for item in state["facts"]}
    if state["revision"] > 0 and observed < timestamp(state["last_ingested_at"]):
        raise ValueError("KBI_04K_FACTS_OLDER_OBSERVATION")

    next_facts = []
    replayed = 0
    for record in records:
        provenance = make_provenance(record, observation)
        previous = old.get(record["fact_id"])
        if previous and observation["observed_at"] == previous["last_attempt"]["observed_at"]:
            if (
                previous["last_attempt"]["observation_digest"] != provenance["observation_digest"]
                or previous["metadata"] != record["metadata"]
            ):
                raise ValueError("KBI_04K_FACTS_CONTRADICTED_REPLAY")
            replayed += 1
            next_facts.append(previous)
            continue
        next_facts.append({
            **record,
            "observed_at": observation["observed_at"],
            "known_from": provenance,
            "last_attempt": provenance,
        })

    if replayed == len(records) and state["revision"] > 0:
        return state
    if replayed:
        raise ValueError("KBI_04K_FACTS_MIXED_REPLAY")

    result = {
        "schema_version": "1.0.0",
        "authority_id": "CP-IDENTITY-SECRET-001",
        "scope": "CONTROL_PLANE_SOURCE_ONLY",
        "status": "PARTIAL_BOUNDED_METADATA",
        "revision": state["revision"] + 1,
        "last_ingested_at": observation["observed_at"],
        "execution_authority_granted": False,
        "secret_values_persisted": False,
        "raw_remote_payload_persisted": False,
        "server_connection_coordinates_persisted": False,
        "facts": sorted(next_facts, key=lambda item: item["fact_id"]),
    }
    validate_initial_or_persisted_state(result)
    return result


def persist_file(input_path: Path, output_path: Path, expected_revision: int) -> dict:
    if input_path.stat().st_size > 1_000_000:
        raise ValueError("KBI_04K_FACTS_INPUT_TOO_LARGE")
    observation = json.loads(input_path.read_text(encoding="utf-8"))
    snapshot = load_json(SNAPSHOT_PATH)
    identity_model = load_json(IDENTITY_MODEL_PATH)

    lock_fd = os.open(output_path.parent, os.O_RDONLY)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        mode = stat.S_IMODE(output_path.stat().st_mode)
        state = json.loads(output_path.read_text(encoding="utf-8"))
        if state.get("revision") != expected_revision:
            raise ValueError("KBI_04K_FACTS_REVISION_MOVED")
        result = persist(observation, state, snapshot, identity_model)
        if result != state:
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", dir=output_path.parent,
                    prefix=".identity-secret-facts-", delete=False
                ) as handle:
                    temporary = Path(handle.name)
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Persist validated KBI-04K safe metadata.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=STATE_PATH)
    parser.add_argument("--expected-revision", type=int, required=True)
    args = parser.parse_args()
    try:
        result = persist_file(args.input, args.output, args.expected_revision)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise SystemExit("KBI_04K_FACTS_FAILED") from None
    print(f"KBI_04K_FACTS_PERSISTED revision={result['revision']} facts={len(result['facts'])}")


if __name__ == "__main__":
    main()
