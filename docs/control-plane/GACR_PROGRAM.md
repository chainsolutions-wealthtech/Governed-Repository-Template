# GACR PROGRAM

> Programme authority for Governed Agent Continuity Relay.
> This programme is distinct from `docs/control-plane/PROGRAM.md`, which governs the global Control Plane roadmap.

## Programme identity

- Programme: `GACR — Governed Agent Continuity Relay`
- Authority family: `CP-AGENT-RELAY-001`
- Original-intent authority: `docs/control-plane/GACR_ORIGINAL_INTENT.md`
- Current realignment authority: `docs/control-plane/GACR_ORIGIN_REALIGNMENT.md`
- Machine intent projection: `.governance/control-plane-state/gacr-original-intent.json`
- Machine realignment projection: `.governance/control-plane-state/gacr-origin-realignment.json`

## Separation from the global programme

```text
GLOBAL CONTROL PLANE PROGRAMME
!=
GACR PROGRAMME
```

They share repository governance and safety mechanisms, but neither programme's next action is the other's next action.

There is no dependency edge `P12-S6 → GACR`.

The owner may explicitly park the global programme while GACR advances.

## Preserved implemented baseline

Current GACR implementation includes R1-R6 family capabilities and evidence. Nothing in the origin realignment rolls those capabilities back.

## Historical evolution target

The original next evolution after the baseline was:

```text
BEACON
→ WATCH
→ CORRELATOR
→ DISPATCHER
```

with the Connection Envelope, connection fingerprint, explicit correlation confidence, optional Bridge and deterministic Agent Context described in `GACR_ORIGINAL_INTENT.md`.

Later R2-R6 work implemented many parts of that target. The realignment programme exists to compare the original intent against what is now implemented and close remaining gaps without regression.

## GACR realignment sequence

The mandatory 24-step sequence lives in `GACR_ORIGIN_REALIGNMENT.md`.

Current GACR programme state:

- `ORIGINAL_INTENT`: CANONICAL / RECORDED.
- `R1-R6_BASELINE`: PRESERVED / REOBSERVED / ATTESTED (`GACR-OR-01 = PASS`).
- `ORIGIN_REALIGNMENT_PLAN`: ACCEPTED.
- `REALIGNMENT_EXECUTION`: STEPS 1-12 CLOSED; STEP 13 IN PROGRESS; PRE-13B INTEGRATION REMEDIATION REQUIRED.
- `ULTIMATE_LIVE_ACCEPTANCE`: NOT YET PASSED.

## GACR next action

`REALIGNMENT_STEP_13B_RUN_REAL_FRESH_PROVIDER_AGENT_TEST`

Step 13B remains the next live acceptance gate, but its execution is temporarily blocked until the two bounded post-integration findings in `docs/control-plane/GACR_GSCC_GSE_INTEGRATION_AUDIT.md` are closed and re-attested from the then-current `main`.

The GSCC Core, GSE Session State Engine and GSCC↔GACR bidirectional-control integration are functionally integrated and green. PR #142 post-merge Governance CI `36968203836` passed the GSCC, GSE, control-harness, combined E2E and historical GACR regression suites; Relay run `36968203882` also passed. PR #143 durably attested these prerequisites without claiming fresh-provider acceptance.

A later canonical audit found two residual integration risks before Step 13B. Both are now CLOSED/PASS; G6 reconciliation is the remaining gate:

1. **CLOSED/PASS** — PR #147 removed the second shared protocol authority: `scripts/gscc_gacr/contract.py` now consumes canonical `scripts/gscc/protocol.py`; candidate and post-merge CI plus Relay are green.
2. **CLOSED/PASS** — PR #149 extends the real SessionEndpoint E2E so the combined path proves `COMMAND_ACK` and `CHALLENGE_RESPONSE` projection into GSE, but the STATUS / PROGRESS / CONTEXT / CHECKPOINT control-response paths are not yet proven end-to-end through the canonical GSE input model.

A procedural deviation is also recorded: Worker A and Worker B were merged before all three worker PRs remained open for one final integration audit, contrary to the worker prompts. This is non-blocking because the subsequent dependency-ordered integration, full green CI and controlled PR #142 contained the runtime risk, but it remains part of the durable audit record.

No GACR step is rolled back. Step 13B is still `NOT_EXECUTED`. Both bounded remediation findings are closed and G6 reconciliation CI `36971795607` passed, so Step 13B is now `NEXT_AUTHORIZED`. This programme remains independent of `P12-S6`, CASE 1, GMC and the global Control Plane programme.

## Completion condition

GACR may be declared origin-realigned only after the live acceptance scenario proves:

fresh agent not explicitly told to register with GACR
→ observable first-touch through an instrumented path
→ canonical session create/resume
→ safe liveness and progress evidence
→ controlled loss of fresh evidence
→ governed stall transition
→ second agent
→ deterministic stopping-point reconstruction
→ exact-HEAD reconciliation
→ governed takeover
→ continuation of the same work.

Until then, the programme status remains partial regardless of green unit tests.

### G6 reconciliation

- Current main reobserved before G6: `114c5397966a5c6ad7d8770298abd698929ecf8f`.
- GACR-INT-AUDIT-01: `CLOSED_PASS`.
- GACR-INT-AUDIT-02: `CLOSED_PASS`.
- G6 reconciliation PR #150 first full Governance CI: `36971795607 = PASS`.
- Shared protocol, GSE projection, combined E2E, historical GACR, governance integrity and authority boundaries all pass together.
- Step 13B is reauthorized as `NEXT_AUTHORIZED`.
- Fresh provider agent remains `NOT_EXECUTED`.
- Ultimate live acceptance remains `NOT_PASSED`.
