# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_G_IMPLEMENT_SIGNED_SSH_PROFILE_RECOVERY
STATE = FRAMEWORK_CORRECTION_REQUIRED
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## Verified evidence

- Template main reobserved before correction: `f5ba27597f4fb8214233a69b30577fcddeae6193`.
- Ekyc HEAD: `a6b0c99cc8d90a1d5cbaf4d6288d52b995e596c6`.
- Owner reapproved the corrected `/mcp` read-only discovery plan.
- Governed Ekyc run: `36644247227`.
- Direct MCP: PASS.
- Endpoint: `https://mcp.wealthtechinnovations.com/mcp`.
- MCP protocol: `2025-06-18`.
- MCP server: `wealthtech_ssh_bridge 0.1.0`.
- Read-only probes PASS: `ping`, `get_project_context`, `list_domains_s1`, `list_domains_s2`, `get_write_tools_context`.
- SSH path: `SSH_PROFILE_MISMATCH`.
- Configured SSH profile: `mcp.wealthtechinnovations.com:22/root`.
- Signed broker profile: `212.227.212.33:22/root`.
- First-agent baseline: SKIPPED.
- Ekyc#1 revision after failure: `35`.

## Generic correction

1. Preserve the signed broker host/port/user as non-secret discovery evidence.
2. Reopen `Q_SSH_PROFILE_RECOVERY` instead of blind `/local-execute` retry.
3. Preserve direct MCP PASS evidence in failure history.
4. Correcting the SSH profile invalidates prior discovery approval because the plan materially changes.
5. After Template CI/merge, distribute V2.8.8 through the governed Ekyc upgrader.
6. Resume Ekyc only at SSH-profile recovery, then rebuild the read-only plan for explicit approval.

## Complementary follow-up already queued

`C1-13-H` will add a source-only persistent MCP capability snapshot to the Template: refreshable read-only inventory, tool/resource catalogue, case-to-capability mapping and prepared-operation model feeding the existing Loop Engineering. It does not create a parallel engine or MCP intake.

## Safety boundary

- Do not patch Ekyc directly.
- Do not mutate Patricked-code/MCP.
- Do not infer SSH profile correction as mutation authority.
- Do not execute a materially changed discovery plan without renewed approval.
- P12-S6 and GMC remain blocked behind P12-S5.
