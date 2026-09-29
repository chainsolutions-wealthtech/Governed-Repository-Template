# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_E_WAIT_MCP_INTAKE_201_TLS_REMEDIATION_THEN_RETRY_APPROVED_EKYC_DISCOVERY
STATE = BLOCKED_EXTERNAL_DEPENDENCY
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## Verified authorized attempt

- Template main: `5abb69efdd7c2776cae2fa97fb3f4169a278fe72`.
- Ekyc HEAD: `a6b0c99cc8d90a1d5cbaf4d6288d52b995e596c6`.
- Ekyc Governance CI: `36637639375` PASS.
- Owner explicitly approved the exact read-only discovery plan.
- Approval command: central issue #49 comment `5900168996`.
- Authorized target discovery run: `36638780542`.
- Ekyc#1 revision: `31`.
- `mcp_discovery_approved = true`.
- Discovery result: `SSL_CERTIFICATE_VERIFY_FAILED` because the public certificate is expired.
- Baseline application: SKIPPED.
- No MCP write, domain creation, server mutation, deployment or TLS bypass occurred.

## External dependency

`Patricked-code/MCP#201` remains open. The MCP programme independently confirmed the same public TLS blocker in its Governed Deploy #87 and records remediation as not complete.

## Resume rule

Once MCP#201 provides fresh evidence that the public TLS certificate and required broker route are restored, retry the **same already-approved read-only discovery plan** on the exact current Ekyc HEAD.

Do not infer any wider authority. If the discovery plan itself changes materially, return to the appropriate approval gate.

## Safety boundary

- No direct Ekyc patch.
- No MCP runtime mutation from this workstream.
- No TLS verification bypass.
- No baseline write before discovery completes and subsequent setup questions/approval are reached.
- P12-S6 and GMC remain blocked behind P12-S5.
