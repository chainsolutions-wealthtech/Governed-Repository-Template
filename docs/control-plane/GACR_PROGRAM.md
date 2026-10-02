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

`GACR_PRE_13B_CLOSE_INTEGRATION_AUDIT_FINDINGS`

Step 13B remains the next live acceptance gate, but its execution is temporarily blocked until the two bounded post-integration findings in `docs/control-plane/GACR_GSCC_GSE_INTEGRATION_AUDIT.md` are closed and re-attested from the then-current `main`.

The GSCC Core, GSE Session State Engine and GSCC↔GACR bidirectional-control integration are functionally integrated and green. PR #142 post-merge Governance CI `36968203836` passed the GSCC, GSE, control-harness, combined E2E and historical GACR regression suites; Relay run `36968203882` also passed. PR #143 durably attested these prerequisites without claiming fresh-provider acceptance.

A later canonical audit found two residual integration risks that must be closed before executing Step 13B:

1. `scripts/gscc_gacr/contract.py` still duplicates shared GSCC protocol constants already canonical in `scripts/gscc/protocol.py`; the integration layer must consume the canonical GSCC authority rather than maintain a second evolving copy.
2. The combined E2E proves `COMMAND_ACK` and `CHALLENGE_RESPONSE` projection into GSE, but the STATUS / PROGRESS / CONTEXT / CHECKPOINT control-response paths are not yet proven end-to-end through the canonical GSE input model.

A procedural deviation is also recorded: Worker A and Worker B were merged before all three worker PRs remained open for one final integration audit, contrary to the worker prompts. This is non-blocking because the subsequent dependency-ordered integration, full green CI and controlled PR #142 contained the runtime risk, but it remains part of the durable audit record.

No GACR step is rolled back. Step 13B is still `NOT_EXECUTED`; after the bounded remediation and full regression revalidation it may return to `NEXT_AUTHORIZED`. This programme remains independent of `P12-S6`, CASE 1, GMC and the global Control Plane programme.

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