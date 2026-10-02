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
- `R1-R6_BASELINE`: PRESERVED.
- `ORIGIN_REALIGNMENT_PLAN`: ACCEPTED.
- `REALIGNMENT_EXECUTION`: NOT YET DECLARED COMPLETE.
- `ULTIMATE_LIVE_ACCEPTANCE`: NOT YET PASSED.

## GACR next action

`GACR-OR-01_REOBSERVE_AND_ATTEST_R6_BASELINE`

This is the GACR programme next action only. It does not replace or modify the global programme next action.

The original-intent source is already captured, but the ordered realignment execution still starts by reobserving and attesting the exact current baseline before any implementation/gap-closure work is marked complete.

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
