# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_12_J_C_A_RECONCILE_GMC_POST_MERGE_INTEGRITY
STATE = IN_PROGRESS
```

## Objective

Repair the generic Governance Model integrity defects discovered by the still-open post-merge review threads on Template PR #42 before any further mutation of the external CASE 1 pilot.

Observed canonical Template HEAD:

`2c70fc82aed4fa8f7eebb7f49b2573e6c57e9e59`

Parent CASE 1 objective:

`C1-12-J-C_RELEASE_AND_REUPGRADE_CASE1_PILOT`

## Required correction

1. make `groups[*].dependency_contract.artifact_dependencies` the canonical source for GMC artifact-consumer relationships;
2. reconcile both `produced_artifacts[*].consumed_by` and `knowledge_artifacts[*].consumed_by` to that source while preserving non-GMC future consumers;
3. verify exact reciprocity with global `ARTIFACT_DEPENDENCY` edges;
4. add a CI regression test that fails closed on future divergence;
5. advance `CP-GOVMODEL-001` from R1 to append/supersede revision R2 for CPD-028/CPD-029 semantics;
6. reconcile source current/checkpoint/handoff/task and relational-memory projections;
7. run Governance CI and require PASS;
8. merge and post-merge attest the correction;
9. only then restore `C1_12_J_C_RELEASE_AND_REUPGRADE_CASE1_PILOT` as the unique next action.

## Safety boundary

No direct patching or mutation of `Patricked-code/Gouvern` is permitted while this framework correction is open.

The GMC programme remains `PLANNING_ONLY`; this correction does not authorize GMC registry/schema/comparator/runtime implementation.
