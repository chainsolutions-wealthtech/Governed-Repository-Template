# CONTROL PLANE TASKS

## Completed work package — SG-20260926-001

Objective: V2.7.0 Self-Governed Control Plane.

| Task | Status | Evidence |
|---|---|---|
| SG-001 Define source/client memory boundary | DONE | source-only namespace selected |
| SG-002 Create human source authorities | DONE | `docs/control-plane/*` |
| SG-003 Create machine source projections | DONE | `.governance/control-plane-state/*` |
| SG-004 Enforce source-state validation | DONE | Governance validation contract |
| SG-005 Prevent client leakage | DONE | CI/bootstrap non-leak proof |
| SG-006 Release V2.7.0 and reconcile source checkpoint | DONE | release subject `d11b72956e68526edf9b17aec472163a4e49a585` |
| SG-007 Resume framework program #12 | DONE | program authority restored |

## Active program — CREATE_NEW_REPOSITORY_COMPLETION

| Task | Status | Dependency | Exit evidence |
|---|---|---|---|
| P12-S1 MCP connectivity-choice contract completion | DONE | — | optional MCP linkage + DIRECT/SSH/BOTH choice contract tests + pilot evidence |
| P12-S2 Gouvern MCP discovery | DONE | P12-S1 | PASS/non-degraded discovery |
| P12-S3 Setup approval + APPLY_BASELINE | DONE | P12-S2 | baseline commit + first-agent handoff |
| P12-S4 Prove subsequent NORMAL_GOVERNED_ENTRY on Gouvern | IN_PROGRESS | P12-S3 | live normal-entry handoff, no baseline reset |
| P12-S5 Second fresh repository E2E | PENDING | P12-S4 | clean uninterrupted lifecycle |
| P12-S6 Close CASE 1 and release next macro case | PENDING | P12-S5 | reconciled final evidence |

## Unique executable task

`P12-S4_PROVE_NORMAL_GOVERNED_ENTRY_ON_GOUVERN`

No later task may become executable before its dependency is complete.
