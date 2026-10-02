# GACR GSCC / GSE Integration Canonical Audit

> Authority: GACR programme post-integration audit.
> Date: 2026-10-02.
> Scope: GSCC Core, GSE Session State Engine, GSCC↔GACR bidirectional control, and Step 13B readiness only.
> Global Control Plane / P12-S6 / CASE 1 / GMC are out of scope.

## Audit baseline

The audit was reobserved from canonical `main` at:

```text
8936a0f734d12cf5dbcd916c4d98fe4fef895aec
```

Relevant integration chain:

- GSCC Core worker PR #140 — merged.
- GSE worker PR #138, dependency integration PR #141 — merged.
- GSCC↔GACR worker PR #139 — closed without direct merge after divergence.
- Controlled integration PR #142 — merged at `feea5dfc9055c96c9a589889d96708b3fba353e2`.
- Integration attestation PR #143 — merged.
- PR #142 post-merge Governance CI `36968203836` — PASS.
- PR #142 post-merge GACR Relay `36968203882` — PASS.
- PR #143 Governance CI `36968463053` — PASS.

## Confirmed conforming areas

The audit confirms:

- `GSCC transports; GSE interprets; GACR governs continuity` remains the intended authority split.
- GSCC Core is versioned, secretless, capability-aware, idempotent and transport-abstracted.
- GSE keeps liveness, activity and progress independent.
- GSE does not own claims, exact-HEAD authority or takeover.
- The control harness keeps `COMMAND DELIVERY != MUTATION AUTHORITY`.
- `TAKEOVER_OFFER != TAKEOVER_ACCEPT`.
- `RESUME != WRITE_AUTHORITY`.
- `REOBSERVE_HEAD != CLAIM_TRANSFER`.
- Fake/control tests do not mutate canonical GACR runtime stores.
- Secret, cookie, token, transcript and private-reasoning payload boundaries are tested.
- Replayed liveness-challenge responses do not refresh fresh-liveness evidence.
- Historical GACR regression suites remain green.
- Fresh provider Step 13B has not been executed and ultimate live acceptance has not passed.

## Recorded procedural deviation

The worker instructions required all three worker PRs to remain unmerged until a supervised integration audit.

Worker A / GSCC and Worker B / GSE were merged before the three-worker integration point.

This is recorded as:

```text
PROCEDURAL_DEVIATION_RECORDED_NON_BLOCKING
```

It does not invalidate the integrated runtime because the repository then performed dependency-ordered reconciliation and PR #142 plus post-merge CI proved the combined state. It must nevertheless remain visible in the durable audit history.

## Closed finding GACR-INT-AUDIT-01 — duplicated shared protocol authority

`scripts/gscc/protocol.py` is the canonical GSCC protocol implementation.

However, `scripts/gscc_gacr/contract.py` still independently declares shared:

- `EVENTS`
- `COMMANDS`
- `DELIVERY_STATES`
- terminal states
- safe-payload restrictions

This creates a future drift risk.

Required remediation:

1. make the GSCC↔GACR integration layer derive/import shared protocol constants and validation from canonical `scripts/gscc/protocol.py`;
2. retain only genuinely adapter-specific control types locally;
3. preserve backward compatibility;
4. add a regression proving no second divergent shared protocol authority exists.

Closure evidence:

- remediation PR #147;
- candidate Governance CI `36970569867 = PASS`;
- merge `cbc87ef5f31c6c8190be3add44f446fdc316b6f2`;
- post-merge Governance CI `36970611124 = PASS`;
- post-merge GACR Relay `36970611145 = PASS`;
- current post-auto-attach main observed at `b7d0e3540747af21db9705fc333baeca1d74adef`;
- `scripts/gscc_gacr/contract.py` aliases canonical GSCC events/commands/delivery/terminal authority;
- control safe-payload validation delegates to canonical GSCC secretless policy;
- legacy control restrictions `browser_session`, `conversation_text`, and `page_content` were preserved by strengthening the canonical GSCC policy;
- CI regression proves the control aliases are the same canonical protocol objects and rejects a future duplicate declaration.

Status:

```text
CLOSED_PASS
```

## Closed finding GACR-INT-AUDIT-02 — incomplete control-response → GSE proof

The combined controlled E2E currently proves the real GSCC SessionEndpoint path for:

- `COMMAND_ACK`
- `CHALLENGE_RESPONSE`
- replay-safe liveness semantics.

The control harness separately proves:

- `STATUS_REQUEST`
- `PROGRESS_REQUEST`
- `CONTEXT_REQUEST`
- `CHECKPOINT_REQUEST`
- `REOBSERVE_HEAD`
- `REPORT_BLOCKER`
- `HANDOFF_PREPARE`
- other control lifecycle paths.

But STATUS / PROGRESS / CONTEXT / CHECKPOINT responses are not yet proven end-to-end through the canonical GSE input model.

Required remediation:

1. define one canonical additive mapping from those safe control responses into existing GSE events/projections;
2. do not create a second state engine;
3. do not manufacture liveness from a response that is not liveness evidence;
4. do not manufacture progress from status/context traffic;
5. prove the mapping in the combined E2E.

Closure evidence:

- remediation PR #149;
- candidate Governance CI `36971442096 = PASS`;
- merge `d831c29ea0943bd5015a757e303187fa505b5f1c`;
- post-merge Governance CI `36971501671 = PASS`;
- post-merge GACR Relay `36971501664 = PASS`;
- current post-auto-attach main observed at `114c5397966a5c6ad7d8770298abd698929ecf8f`;
- one canonical mapper `scripts/gscc_gacr/gse_projection.py` converts safe control snapshots into existing GSE events;
- real `SessionEndpoint.receive_commands()` path is proven for STATUS / PROGRESS / CONTEXT / CHECKPOINT;
- unit and combined E2E prove non-liveness responses do not refresh liveness;
- STATUS/CONTEXT/CHECKPOINT snapshots do not manufacture progress;
- PROGRESS query snapshots preserve reported facts but remain `qualifying_progress=false`;
- `UNAVAILABLE` values fail closed and do not overwrite known SessionTwin identity/context.

Status:

```text
CLOSED_PASS
```

## G6 reconciliation gate

Both blocking findings were reobserved CLOSED on current main `114c5397966a5c6ad7d8770298abd698929ecf8f`.

G6 reconciliation candidate PR #150 ran the complete Governance CI suite from that authority state:

- reconciliation CI `36971795607 = PASS`;
- canonical shared-contract gate = PASS;
- control-response → GSE projection gate = PASS;
- combined controlled E2E = PASS;
- historical GACR regressions = PASS;
- Governance validation = PASS;
- no claim, exact-HEAD, takeover or mutation authority moved out of GACR.

This satisfies the pre-authorization reconciliation gate. A fresh-provider test is still not evidence until it is executed separately.

## Step 13B decision

The prior integration attestation proved the infrastructure prerequisites functionally green, but this later canonical audit found two bounded integration risks.

Therefore:

```text
STEP 13B = NOT_EXECUTED
STEP 13B EXECUTION = NEXT_AUTHORIZED
ULTIMATE_LIVE_ACCEPTANCE = NOT_PASSED
```

This does not renumber or rewrite the frozen 24-step GACR realignment sequence.

Step 13B remains the next live acceptance gate.

## Mandatory next action

```text
REALIGNMENT_STEP_13B_RUN_REAL_FRESH_PROVIDER_AGENT_TEST
```

Exit gate:

1. GACR-INT-AUDIT-01 closed.
2. GACR-INT-AUDIT-02 closed.
3. GSCC tests PASS.
4. GSE tests PASS.
5. GSCC↔GACR control tests PASS.
6. Combined controlled E2E PASS.
7. Historical GACR regression PASS.
8. Governance validation PASS.
9. Current `main` reobserved.
10. Canonical programme state re-authorizes Step 13B as `NEXT_AUTHORIZED`.

Only then run a genuinely fresh provider agent for Step 13B. The remediation agent itself must never be reused as the fresh-provider acceptance subject.
