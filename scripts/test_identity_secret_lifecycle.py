#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/".governance"/"control-plane-state"/"identity-secret-lifecycle.json"

def main():
    m=json.loads(PATH.read_text(encoding="utf-8"))
    if m.get("authority_id")!="CP-IDENTITY-SECRET-001":
        raise SystemExit("IDENTITY_SECRET_TEST_FAILED: authority")
    for k in ["execution_authority_granted","secret_values_persisted","private_keys_persisted","bearer_tokens_persisted"]:
        if m.get(k) is not False:
            raise SystemExit(f"IDENTITY_SECRET_TEST_FAILED: unsafe {k}")

    planes={p["id"] for p in m.get("planes") or []}
    if planes!={"GITHUB_PLANE","SERVER_PRODUCTION_PLANE"}:
        raise SystemExit("IDENTITY_SECRET_TEST_FAILED: two-plane model")

    types={c["id"]:c for c in m.get("credential_types") or []}
    required={
      "GITHUB_APP_INSTALLATION_TOKEN","GITHUB_ACTIONS_REPOSITORY_SECRET","GITHUB_OIDC_TOKEN",
      "MCP_AUTH_TOKEN","SSH_OIDC_EPHEMERAL_CERTIFICATE","SERVER_SERVICE_ACCOUNT",
      "APPLICATION_ENV_SECRET","DATABASE_CREDENTIAL","DNS_PROVIDER_TOKEN","TLS_PRIVATE_KEY"
    }
    if required-set(types):
        raise SystemExit("IDENTITY_SECRET_TEST_FAILED: missing credential types")
    for cid,c in types.items():
        for field in ["creation","retrieval","injection","verification","rotation","revocation","value_persistence"]:
            if not c.get(field):
                raise SystemExit(f"IDENTITY_SECRET_TEST_FAILED: {cid} missing {field}")

    if types["GITHUB_APP_INSTALLATION_TOKEN"]["lifecycle"]!="SHORT_LIVED":
        raise SystemExit("IDENTITY_SECRET_TEST_FAILED: GitHub App token must be short-lived")
    if types["SSH_OIDC_EPHEMERAL_CERTIFICATE"]["lifecycle"]!="EPHEMERAL":
        raise SystemExit("IDENTITY_SECRET_TEST_FAILED: SSH certificate must be ephemeral")
    if "FORBIDDEN" not in types["TLS_PRIVATE_KEY"]["value_persistence"]:
        raise SystemExit("IDENTITY_SECRET_TEST_FAILED: TLS key persistence")

    ops={o["id"]:o for o in m.get("lifecycle_operations") or []}
    if len(ops)<10:
        raise SystemExit("IDENTITY_SECRET_TEST_FAILED: lifecycle operations incomplete")
    intents={o["intent"] for o in ops.values()}
    for intent in [
      "MINT_GITHUB_APP_INSTALLATION_TOKEN","PROVISION_GITHUB_SECRET",
      "MINT_EPHEMERAL_SSH_CERTIFICATE","CREATE_OR_BIND_SERVER_APPLICATION_SECRET",
      "CREATE_DATABASE_CREDENTIAL","ROTATE_CREDENTIAL","REVOKE_CREDENTIAL",
      "VERIFY_SECRET_OR_CREDENTIAL_WITHOUT_READBACK"
    ]:
        if intent not in intents:
            raise SystemExit(f"IDENTITY_SECRET_TEST_FAILED: missing {intent}")

    serialized=PATH.read_text(encoding="utf-8")
    for leak in ["-----BEGIN PRIVATE KEY-----","ghp_","github_pat_","Bearer ey"]:
        if leak in serialized:
            raise SystemExit(f"IDENTITY_SECRET_TEST_FAILED: secret-like material {leak}")

    slices={x["id"]:x["status"] for x in m.get("future_incremental_slices") or []}
    for sid in ["KBI-04J","KBI-04K","KBI-04L","KBI-04M"]:
        if slices.get(sid)!="PLANNED":
            raise SystemExit(f"IDENTITY_SECRET_TEST_FAILED: {sid} must remain planned")

    print("IDENTITY_SECRET_LIFECYCLE_TEST_PASS")

if __name__=="__main__":
    main()
