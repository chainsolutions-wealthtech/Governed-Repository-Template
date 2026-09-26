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

### C1-12 discovered sub-tasks

| ID | Task | Status | Evidence / next |
|---|---|---|---|
| C1-12-A | Create subsequent-agent proof issue on Gouvern | DONE | `Patricked-code/Gouvern#3` |
| C1-12-B | Prove initial actor authorization behavior is fail-closed | DONE | start refused; no governed state advanced |
| C1-12-C | Add exact-HEAD machine local-entry start | DONE | V2.8.1 / PR #25 |
| C1-12-D | Synchronize client control-plane policy on governed upgrade | DONE | V2.8.2 / PR #26 |
| C1-12-E | Make bootstrap consistency self-test portable on instantiated clients | DONE | V2.8.3 / PR #27 |
| C1-12-F | Diagnose `INTENT_SELFTEST_FAILED: unexpected work item` | IN_PROGRESS | failing Gouvern CI run `36262734626` |
| C1-12-G | Fix generic connection-intent self-test portability in template | PENDING | depends on C1-12-F |
| C1-12-H | Run template CI and release next compatible version if needed | PENDING | depends on C1-12-G |
| C1-12-I | Governed-upgrade Gouvern from exact HEAD `3a1b7689...` | PENDING | depends on C1-12-H |
| C1-12-J | Obtain all-green Gouvern Governance CI | PENDING | depends on C1-12-I |
| C1-12-K | Re-run Gouvern#3 through machine local-entry start | PENDING | depends on C1-12-J |
| C1-12-L | Verify mode = `NORMAL_GOVERNED_ENTRY` | PENDING | depends on C1-12-K |
| C1-12-M | Verify no first-agent baseline/session/work duplication | PENDING | depends on C1-12-L |
| C1-12-N | Persist normal-entry handoff + evidence | PENDING | depends on C1-12-M |
| C1-12-O | Mark C1-12 / STEP 4 DONE and unlock C1-13 | PENDING | depends on C1-12-N |
| C1-12-P | Reconcile canonical relational memory with completed C1-12 evidence | PENDING | depends on C1-12-O |

Current unique executable sub-task: `C1-12-F_DIAGNOSE_UNEXPECTED_WORK_ITEM`.
