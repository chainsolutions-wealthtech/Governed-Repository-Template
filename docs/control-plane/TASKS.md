# CONTROL PLANE TASKS

## Active work package — SG-20260926-001

Objective: V2.7.0 Self-Governed Control Plane.

| Task | Status | Dependency | Exit evidence |
|---|---|---|---|
| SG-001 Define source/client memory boundary | DONE | — | source-only namespace selected |
| SG-002 Create human source authorities | DONE | SG-001 | CURRENT_STATE/SUIVI/NEXT_ACTION/DECISIONS/TASKS/PROGRAM |
| SG-003 Create machine source projections | DONE | SG-002 | current/checkpoint/handoff/tasks JSON |
| SG-004 Enforce source-state validation | DONE | SG-003 | validator + Governance CI contract |
| SG-005 Prevent client leakage | IN_PROGRESS | SG-004 | directory removal + bootstrap self-test proof |
| SG-006 Release V2.7.0 and reconcile source checkpoint | PENDING | SG-005 | merged green release |
| SG-007 Resume framework program #12 | PENDING | SG-006 | second fresh CREATE_NEW_REPOSITORY E2E starts |

## Unique executable task

`SG-005_RUN_CI_AND_PROVE_CLIENT_NON_LEAK`

No later task may become executable before its dependency is complete.
