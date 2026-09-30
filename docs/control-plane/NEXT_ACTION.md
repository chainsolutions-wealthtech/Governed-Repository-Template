# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_I_REQUEST_EKYC_CORRECTED_BOTH_DISCOVERY_APPROVAL
STATE = WAITING_FOR_OWNER_APPROVAL
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## C1-13-H complete

The central MCP capability memory is now canonical:

- capability-first framework PR #65 merged at `07b1f073c6ba5c9c5038efcd0f0e61c2271e73cf`; post-merge CI `36652171736` PASS;
- authority/project-scope PR #67 merged at `662072891a66046ca07bb7e356ed4bf2345a12be`; post-merge CI `36652640862` PASS;
- stale generated PRs #63 and #66 were closed unmerged after semantic QA;
- final live refresh run `36652696942`: PASS;
- canonical snapshot PR #68 CI `36652719422`: PASS;
- snapshot merge `6c293a809df15b85fe40685b3a0f6a3508e1ee4d`;
- post-merge Governance CI `36652771078`: PASS;
- live catalogue: 135 tools, 2 resources;
- planning model: `CASE → CAPABILITY → SURFACE → TOOL → AUTHORITY → PREPARED OPERATION`;
- question rule: `OBSERVE_AND_REUSE_BEFORE_ASK`.

## Ekyc exact return point

```text
repository = Patricked-code/Ekyc
HEAD = 4d552458afab32df12aaafd6c7290fab6246d96b
issue = Ekyc#1
revision = 38
status = WAITING_FOR_DISCOVERY_APPROVAL
phase = MCP_DISCOVERY_APPROVAL
current discovery = null
baseline = not applied
```

The discovery endpoint and SSH profile were corrected from authenticated evidence. Because the SSH target materially changed, the prior approval was invalidated by policy.

The next action is therefore one owner decision only: explicitly approve the corrected read-only BOTH discovery plan.

## Safety boundary

- Do not replay C1-13-H.
- Do not merge closed PR #63 or #66.
- Do not patch Ekyc directly.
- Do not mutate Patricked-code/MCP.
- Do not infer approval from earlier plans.
- P12-S6 and GMC remain downstream of P12-S5.
