#!/usr/bin/env python3
from __future__ import annotations

import json

import control_plane_server_identity_secret_metadata as m
from governed_execution_engine import SNAPSHOT_PATH, load_json

SNAPSHOT=load_json(SNAPSHOT_PATH)
IDENTITY=load_json(m.IDENTITY_MODEL_PATH)


class FakeClient:
    def __init__(self, endpoint, token):
        self.endpoint=endpoint
        self.token=token
    def call_tool(self,name,args):
        if name=="scan_mcp_secrets_s1":
            return {
                "status":"PASS",
                "findings":[
                    {"path":"secret.env","token":"TOP-SECRET-TOKEN","password":"TOP-SECRET-PASSWORD"}
                ],
                "summary":"sensitive free-form text",
            }
        return {
            "status":"PASS",
            "processes":[{"name":"app","environment":{"PASSWORD":"SHOULD-NOT-LEAK"}}],
        }


def main():
    plan=m.build_plan(SNAPSHOT,IDENTITY,["S1","S2"])
    if plan["mutation_authority_granted"] is not False:
        raise SystemExit("SERVER_IDENTITY_SECRET_TEST_FAILED: authority")
    if plan["secret_values_persisted"] is not False:
        raise SystemExit("SERVER_IDENTITY_SECRET_TEST_FAILED: secret persistence")

    s1=plan["servers"]["S1"]
    probes={x["tool"]:x for x in s1["probes"]}
    if probes["scan_mcp_secrets_s1"]["available"] is not True:
        raise SystemExit("SERVER_IDENTITY_SECRET_TEST_FAILED: S1 scan capability missing")
    if probes["scan_mcp_secrets_s1"]["surface"]!="read":
        raise SystemExit("SERVER_IDENTITY_SECRET_TEST_FAILED: S1 scan not read-only")

    s2=plan["servers"]["S2"]
    if any(x["tool"]=="scan_mcp_secrets_s1" for x in s2["probes"]):
        raise SystemExit("SERVER_IDENTITY_SECRET_TEST_FAILED: S1 scan leaked into S2")

    mechanisms={x["credential_type"]:x for x in s1["mechanisms"]}
    if mechanisms["SSH_OIDC_EPHEMERAL_CERTIFICATE"]["status"]!="RUNTIME_MINT_PATH_IMPLEMENTED":
        raise SystemExit("SERVER_IDENTITY_SECRET_TEST_FAILED: SSH OIDC lifecycle")
    if mechanisms["APPLICATION_ENV_SECRET"]["status"] not in {"MODELLED_CAPABILITY_GAP","MCP_CAPABILITY_AVAILABLE"}:
        raise SystemExit("SERVER_IDENTITY_SECRET_TEST_FAILED: app secret classification")

    live=m.collect_live(
        plan,
        client_factory=FakeClient,
        endpoint="https://mcp.example.test/mcp",
        token="THIS-TOKEN-MUST-NEVER-APPEAR",
    )
    rendered=json.dumps(live,sort_keys=True)
    for leak in [
        "THIS-TOKEN-MUST-NEVER-APPEAR",
        "TOP-SECRET-TOKEN",
        "TOP-SECRET-PASSWORD",
        "SHOULD-NOT-LEAK",
        "sensitive free-form text",
        "secret.env",
    ]:
        if leak in rendered:
            raise SystemExit(f"SERVER_IDENTITY_SECRET_TEST_FAILED: leaked {leak}")
    if live["raw_remote_payload_persisted"] is not False:
        raise SystemExit("SERVER_IDENTITY_SECRET_TEST_FAILED: raw payload persistence")

    observations={x["tool"]:x for x in live["servers"]["S1"]["observations"]}
    scan=observations["scan_mcp_secrets_s1"]
    if len(scan.get("response_digest",""))!=64:
        raise SystemExit("SERVER_IDENTITY_SECRET_TEST_FAILED: response digest")
    if scan.get("raw_payload_persisted") is not False:
        raise SystemExit("SERVER_IDENTITY_SECRET_TEST_FAILED: scan raw persistence")
    if scan.get("status")!="PASS":
        raise SystemExit("SERVER_IDENTITY_SECRET_TEST_FAILED: safe status extraction")

    print("SERVER_IDENTITY_SECRET_METADATA_TEST_PASS")


if __name__=="__main__":
    main()
