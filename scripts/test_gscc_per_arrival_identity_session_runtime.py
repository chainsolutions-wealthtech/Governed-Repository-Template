#!/usr/bin/env python3
from __future__ import annotations

import json, sqlite3, tempfile
from datetime import datetime, timedelta
from pathlib import Path

from provider_first_tool_hook import build_envelope
from gscc_arrival_identity import mint
from gscc_persisted_entry_pipeline import run_pipeline
from gscc_session_runtime import prepare, control, release_f1, resolve_alias_binding_intent

REPO="chainsolutions-wealthtech/Governed-Repository-Template"
HEAD="a"*40
GITHUB={
 "id":1386478935,
 "repository_full_name":REPO,
 "owner":{"login":"chainsolutions-wealthtech","id":299685687},
 "permissions":{"admin":True,"maintain":True,"pull":True,"push":True,"triage":True},
 "default_branch":"main",
 "branch":"main",
 "head_sha":HEAD,
 "visibility":"public",
}

def base_envelope(alias=None):
    event={
      "provider":"chatgpt",
      "provider_product":"ChatGPT",
      "provider_family":"OpenAI",
      "transport":"chatgpt-github-direct",
      "repository":REPO,
      "runtime":"chatgpt-runtime",
      "surface":"text",
      "channel":"text",
      "execution_mode":"direct-tool",
      "model":"GPT-5.6 Sol",
      "connector_name":"GitHub",
      "connector_type":"native",
      "identity":{
        "conversation_ref":"UNAVAILABLE",
        "session_ref":"UNAVAILABLE",
        "connection_ref":"UNAVAILABLE",
      },
      "tool_name":"mcp__GitHub__create_issue",
      "operation":"pre_entry_runtime_transport",
      "category":"CONTROLLED_INGRESS",
      "success":True,
    }
    if alias:
        event["logical_agent_alias"]=alias
    return build_envelope(event)

def issue_event(issue_id,number):
    return {"repository":{"id":1386478935,"full_name":REPO},"issue":{"id":issue_id,"number":number}}

def pass_q9(db,runtime):
    d=runtime["dispatch"]; cmd=d["command"]; p=cmd["payload"]
    issued=datetime.fromisoformat(cmd["issued_at"].replace("Z","+00:00"))
    ack_at=(issued+timedelta(seconds=5)).isoformat()
    response_at=(issued+timedelta(seconds=10)).isoformat()
    ack={
      "event":"command_ack",
      "session_id":d["target_session_id"],
      "dispatch_id":d["dispatch_id"],
      "command_id":cmd["command_id"],
      "correlation_id":cmd["correlation_id"],
      "delivery_state":"ACKNOWLEDGED",
    }
    a=control(db,runtime["runtime_id"],ack,ack_at)
    assert a["state"]=="WAITING_Q9_RESPONSE",a
    resp={
      "event":"challenge_response",
      "session_id":d["target_session_id"],
      "dispatch_id":d["dispatch_id"],
      "command_id":cmd["command_id"],
      "correlation_id":cmd["correlation_id"],
      "challenge_id":p["challenge_id"],
      "nonce":p["nonce"],
      "challenge_status":"ACK",
    }
    return control(db,runtime["runtime_id"],resp,response_at)

def main():
    e1=mint(base_envelope("FORGE"),issue_event(9001,301),run_id="r1")
    e2=mint(base_envelope(),issue_event(9002,302),run_id="r2")
    e1_repeat=mint(base_envelope(),issue_event(9001,301),run_id="r3")
    assert e1["identity"]["connection_ref"] != e2["identity"]["connection_ref"]
    assert e1["identity"]["connection_ref"] == e1_repeat["identity"]["connection_ref"]
    assert e1["gscc_arrival"]["state_scope"] != e2["gscc_arrival"]["state_scope"]
    assert e1["gscc_arrival"]["state_scope"] == e1_repeat["gscc_arrival"]["state_scope"]
    assert e1["identity"]["connection_ref_origin"]=="GSCC_MINTED_GITHUB_ISSUE"
    assert e1["identity"]["conversation_ref"]=="UNAVAILABLE"

    with tempfile.TemporaryDirectory() as td:
        db=Path(td)/"state.sqlite"
        p1=run_pipeline(e1,GITHUB,db,run_id="arrival-1",observed_at="2026-10-07T00:59:00+00:00")
        p2=run_pipeline(e2,GITHUB,db,run_id="arrival-2",observed_at="2026-10-07T00:59:01+00:00")
        assert p1["classification"]=="FIRST_TOUCH",p1
        assert p2["classification"]=="FIRST_TOUCH",p2
        assert p1["identity_anchor_present"] is True
        assert p2["identity_anchor_present"] is True

        r1=prepare(db,"arrival-1",301)
        r2=prepare(db,"arrival-2",302)
        assert r1["runtime_id"] != r2["runtime_id"]
        g1=pass_q9(db,r1)
        g2=pass_q9(db,r2)
        assert g1["state"]=="GSE_VERIFIED_WAITING_GACR",g1
        assert g2["state"]=="GSE_VERIFIED_WAITING_GACR",g2
        assert g1["gacr_attach"]["connection_ref"] != g2["gacr_attach"]["connection_ref"]
        assert g1["gse_state"]["requested_logical_agent_alias"]=="FORGE",g1
        assert g1["gse_state"]["logical_agent_alias_resolution"]=="GACR_Q2_REQUIRED",g1
        assert g1["gacr_attach"]["logical_agent_alias"]=="FORGE",g1

        alias_binding=resolve_alias_binding_intent(
          {"sections":{"request":{"logical_agent_alias":"FORGE"}}},
          {"sessions":[
            {"session_id":"session-forge-old","agent_identity":"logical-forge","status":"STALLED","relay":{"state":"TAKEOVER_READY"},"provider":"chatgpt","connection_ref":"old","client_instance_id":"old-client","provider_contexts":[]},
            {"session_id":"session-forge-live","agent_identity":"logical-forge","status":"ACTIVE","relay":{"state":"ACTIVE"},"provider":"chatgpt","connection_ref":"live","client_instance_id":"live-client","provider_contexts":[]},
          ]},
          {"schema_version":"1.0.0","authority":"DERIVED_GACR_COORDINATION_PROJECTION","projection_only":True,"grants_task_authority":False,"grants_claim":False,"grants_mutation_authority":False,"revision":1,"items":[{
            "continuity_id":"GRT-CONT-ALIAS-TEST","repository":REPO,"coordination_issue":259,"projection_only":True,"participants":[],
            "logical_agents":[{"logical_agent_id":"logical-forge","human_alias":"FORGE","human_alias_provenance":"OWNER_ASSIGNED","reference_session_ids":["session-forge-old"],"session_ids":["session-forge-old","session-forge-live"],"provider_contexts":[],"projection_only":True,"grants_task_authority":False,"grants_claim":False,"grants_mutation_authority":False}],
          }]},
        )
        assert alias_binding["logical_agent_id"]=="logical-forge",alias_binding
        assert alias_binding["routing_status"]=="ROUTABLE_EXACT_SESSION",alias_binding
        assert alias_binding["resolved_target_session_id"]=="session-forge-live",alias_binding
        assert alias_binding["grants_mutation_authority"] is False

        # F1 release is bound to the same arrival, exact GACR session, grant and HEAD.
        gacr_session_id="session-final-release"
        grant={
          "schema":"gscc-access-grant/v1",
          "grant_id":"GSCC-GRANT-test-release",
          "status":"AUTHORIZED",
          "connection_ref":g1["gacr_attach"]["connection_ref"],
          "session_id":gacr_session_id,
          "bound_head":HEAD,
        }
        conn=sqlite3.connect(db)
        try:
            conn.execute(
              "UPDATE gscc_session_bindings SET gacr_session_id=?,binding_status='GACR_BOUND',binding_level='EXACT' WHERE arrival_ref=?",
              (gacr_session_id,e1["gscc_arrival"]["arrival_ref"]),
            )
            conn.execute(
              "UPDATE gscc_session_runtime SET state='READY_FOR_F1',access_grant_json=?,last_gate='Q12',next_gate='F1' WHERE runtime_id=?",
              (json.dumps(grant,sort_keys=True),r1["runtime_id"]),
            )
            conn.commit()
        finally:
            conn.close()
        receipt={
          "schema":"gscc-function-exposure-receipt/v1",
          "status":"VALIDATED",
          "reason_code":"EXPOSURE_VALIDATED",
          "exposable":True,
          "connection_ref":g1["gacr_attach"]["connection_ref"],
          "session_id":gacr_session_id,
          "access_grant_id":grant["grant_id"],
          "requested_head":HEAD,
          "tool_name":"github_get_repository_state",
          "surface":"read",
          "exposure_receipt":"GSCC-EXPOSURE-test-release",
          "route_authority":{"session_id":gacr_session_id},
        }
        released=release_f1(db,r1["runtime_id"],receipt,HEAD)
        assert released["state"]=="RELEASED_TO_NORMAL_GOVERNANCE",released
        assert released["start_here_status"]=="APPLICABLE",released
        assert released["last_gate"]=="00_START_HERE.md",released
        assert released["next_gate"] is None,released

        conn=sqlite3.connect(db)
        try:
            runtime_state=conn.execute(
              "SELECT state,last_gate,next_gate FROM gscc_session_runtime WHERE runtime_id=?",
              (r1["runtime_id"],),
            ).fetchone()
            assert runtime_state==("RELEASED_TO_NORMAL_GOVERNANCE","00_START_HERE.md",None),runtime_state
            routes=dict(conn.execute(
              "SELECT current_gate,route_status FROM gscc_gate_route_runs WHERE route_run_id IN (?,?)",
              (f"{r1['runtime_id']}:F1",f"{r1['runtime_id']}:00_START_HERE.md"),
            ).fetchall())
            assert routes=={"F1":"ADVANCED","00_START_HERE.md":"RELEASED"},routes
        finally:
            conn.close()

        p1c=run_pipeline(e1_repeat,GITHUB,db,run_id="arrival-1-cont",observed_at="2026-10-07T01:01:00+00:00")
        assert p1c["classification"]=="CONTINUATION",p1c

        conn=sqlite3.connect(db)
        try:
            arrivals=conn.execute("SELECT COUNT(*) FROM gscc_arrival_instances").fetchone()[0]
            identities=conn.execute("SELECT COUNT(*) FROM gscc_conversation_identities").fetchone()[0]
            twins=conn.execute("SELECT COUNT(*) FROM gse_session_twins").fetchone()[0]
            snapshots=conn.execute("SELECT COUNT(*) FROM gscc_first_touch_snapshots").fetchone()[0]
            assert arrivals==2,arrivals
            assert identities==2,identities
            assert twins==2,twins
            assert snapshots==2,snapshots
        finally:
            conn.close()

    print("GSCC_PER_ARRIVAL_IDENTITY_SESSION_RUNTIME_TEST_PASS")

if __name__=="__main__":
    main()
