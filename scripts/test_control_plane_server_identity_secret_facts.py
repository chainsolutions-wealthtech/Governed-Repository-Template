#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import tempfile
from datetime import timedelta
from pathlib import Path

import control_plane_server_identity_secret_facts as f
import control_plane_server_identity_secret_metadata as m
from governed_execution_engine import load_json

SNAPSHOT=load_json(f.SNAPSHOT_PATH)
IDENTITY=load_json(f.IDENTITY_MODEL_PATH)
INITIAL=load_json(f.STATE_PATH)


class FakeClient:
    def __init__(self, endpoint, token):
        self.endpoint=endpoint
        self.token=token
    def call_tool(self,name,args):
        if name=="scan_mcp_secrets_s1":
            return {
                "status":"PASS",
                "findings":[{"password":"NEVER-PERSIST","token":"NEVER-PERSIST"}],
                "message":"another-sensitive-string",
            }
        return {
            "status":"PASS",
            "processes":[{"env":{"SECRET":"NEVER-PERSIST"}}],
        }


def observation():
    plan=m.build_plan(SNAPSHOT,IDENTITY,["S1","S2"])
    result=m.collect_live(
        plan,
        client_factory=FakeClient,
        endpoint="https://mcp.example.test/mcp",
        token="TOKEN-MUST-NOT-PERSIST",
    )
    snapshot_time=f.timestamp(SNAPSHOT["observed_at"])
    result["observed_at"]=(snapshot_time+timedelta(seconds=1)).isoformat()
    return result


def assert_valid_persistence():
    f.validate_initial_or_persisted_state(INITIAL)
    obs=observation()
    state=f.persist(obs,copy.deepcopy(INITIAL),SNAPSHOT,IDENTITY)
    if state["revision"]!=1 or state["status"]!="PARTIAL_BOUNDED_METADATA":
        raise SystemExit("SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: revision/status")
    if len(state["facts"])!=17:
        raise SystemExit(f"SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: expected 17 facts got {len(state['facts'])}")
    if state["last_ingested_at"]!=obs["observed_at"]:
        raise SystemExit("SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: timestamp")
    serialized=json.dumps(state,sort_keys=True)
    for leak in [
        "NEVER-PERSIST","another-sensitive-string","TOKEN-MUST-NOT-PERSIST",
        "ghp_","github_pat_","-----BEGIN PRIVATE KEY-----",
    ]:
        if leak in serialized:
            raise SystemExit(f"SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: leaked {leak}")
    if state["secret_values_persisted"] is not False or state["raw_remote_payload_persisted"] is not False:
        raise SystemExit("SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: unsafe persistence flags")
    for fact in state["facts"]:
        if len(fact["known_from"]["observation_digest"])!=64:
            raise SystemExit("SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: provenance digest")
        if fact["fact_kind"]=="PROBE" and "response_digest" in fact["metadata"]:
            if len(fact["metadata"]["response_digest"])!=64:
                raise SystemExit("SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: probe digest")
    return obs,state


def assert_replay_and_contradiction(obs,state):
    replay=f.persist(copy.deepcopy(obs),copy.deepcopy(state),SNAPSHOT,IDENTITY)
    if replay!=state:
        raise SystemExit("SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: replay changed state")

    contradiction=copy.deepcopy(obs)
    contradiction["servers"]["S1"]["observations"][0]["response_digest"]="0"*64
    try:
        f.persist(contradiction,copy.deepcopy(state),SNAPSHOT,IDENTITY)
    except ValueError as exc:
        if str(exc)!="KBI_04K_FACTS_CONTRADICTED_REPLAY":
            raise
    else:
        raise SystemExit("SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: contradiction accepted")


def assert_source_recomputation(obs):
    tampered=copy.deepcopy(obs)
    tampered["servers"]["S1"]["mechanisms"][0]["status"]="MCP_CAPABILITY_AVAILABLE"
    try:
        f.persist(tampered,copy.deepcopy(INITIAL),SNAPSHOT,IDENTITY)
    except ValueError as exc:
        if str(exc)!="KBI_04K_FACTS_MECHANISM_SOURCE_MISMATCH":
            raise
    else:
        raise SystemExit("SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: mechanism tampering accepted")

    wrong_snapshot=copy.deepcopy(obs)
    wrong_snapshot["catalogue_digest"]="0"*64
    try:
        f.persist(wrong_snapshot,copy.deepcopy(INITIAL),SNAPSHOT,IDENTITY)
    except ValueError as exc:
        if str(exc)!="KBI_04K_FACTS_SNAPSHOT_MISMATCH":
            raise
    else:
        raise SystemExit("SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: wrong snapshot accepted")


def assert_older_observation(obs,state):
    older=copy.deepcopy(obs)
    older["observed_at"]=(f.timestamp(obs["observed_at"])-timedelta(seconds=1)).isoformat()
    # It must still be at/after the capability snapshot while being older than persisted state.
    if f.timestamp(older["observed_at"]) < f.timestamp(SNAPSHOT["observed_at"]):
        older["observed_at"]=SNAPSHOT["observed_at"]
    try:
        f.persist(older,copy.deepcopy(state),SNAPSHOT,IDENTITY)
    except ValueError as exc:
        if str(exc)!="KBI_04K_FACTS_OLDER_OBSERVATION":
            raise
    else:
        raise SystemExit("SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: older observation accepted")


def assert_file_revision_guard(obs):
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        inp=root/"observation.json"
        out=root/"facts.json"
        inp.write_text(json.dumps(obs),encoding="utf-8")
        out.write_text(json.dumps(INITIAL),encoding="utf-8")
        result=f.persist_file(inp,out,0)
        if result["revision"]!=1:
            raise SystemExit("SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: file persistence")
        try:
            f.persist_file(inp,out,0)
        except ValueError as exc:
            if str(exc)!="KBI_04K_FACTS_REVISION_MOVED":
                raise
        else:
            raise SystemExit("SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: stale revision accepted")


def assert_raw_payload_rejected(obs):
    unsafe=copy.deepcopy(obs)
    unsafe["raw_remote_payload_persisted"]=True
    try:
        f.persist(unsafe,copy.deepcopy(INITIAL),SNAPSHOT,IDENTITY)
    except ValueError as exc:
        if not str(exc).startswith("KBI_04K_FACTS_INPUT_UNSAFE"):
            raise
    else:
        raise SystemExit("SERVER_IDENTITY_SECRET_FACTS_TEST_FAILED: raw payload flag accepted")


def main():
    obs,state=assert_valid_persistence()
    assert_replay_and_contradiction(obs,state)
    assert_source_recomputation(obs)
    assert_older_observation(obs,state)
    assert_file_revision_guard(obs)
    assert_raw_payload_rejected(obs)
    print("SERVER_IDENTITY_SECRET_FACTS_TEST_PASS")


if __name__=="__main__":
    main()
