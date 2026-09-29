# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_E_WAIT_MCP_INTAKE_201_TLS_REMEDIATION_THEN_RETRY_EKYC_DISCOVERY
STATE = BLOCKED_EXTERNAL_DEPENDENCY
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## Current verified state

- Template main: `7b8cf2193514efd8f3fe8ce635b0d21abfe53639`.
- Ekyc HEAD: `87c28f4fd4e36aa3d65cfc384309a054c1640e4c`.
- Ekyc Governance CI: `36621490571` PASS.
- Ekyc local-entry baseline/setup answers remain preserved.
- MCP retry run: `36621624763`.
- Blocker: public TLS certificate for `mcp.wealthtechinnovations.com` is expired.
- External intake: `Patricked-code/MCP#201`.

## Resume condition

Resume only after the MCP programme provides fresh evidence that the public TLS certificate is valid and both the public MCP endpoint and repository-SSH certificate broker are reachable over trusted TLS.

Then:

1. reobserve Template main and Ekyc exact HEAD;
2. re-read `Ekyc#1`;
3. retry the preserved read-only MCP discovery checkpoint;
4. if endpoint correction is requested, use the previously proven direct route `https://mcp.wealthtechinnovations.com/mcp`;
5. continue C1-13 chronologically only after discovery evidence is usable.

## Safety boundary

- Do not patch Ekyc.
- Do not mutate `Patricked-code/MCP` from this workstream; #201 is intake only.
- Do not bypass TLS verification.
- Do not weaken HTTPS, OIDC, SSH certificate, or exact-HEAD protections.
- Do not advance P12-S6 or GMC while P12-S5 is blocked.
