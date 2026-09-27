# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_12_K_RERUN_GOUVERN_ISSUE_3
STATE = IN_PROGRESS
```

## Objective

Resume the existing `Patricked-code/Gouvern#3` subsequent-agent proof through the machine local-entry path and prove `NORMAL_GOVERNED_ENTRY` without replaying `FIRST_AGENT_BOOTSTRAP`.

## Reconciled prerequisite evidence

The prior V2.8.6 pilot revalidation is already complete and must not be replayed:

- pilot repository: `Patricked-code/Gouvern`;
- exact pilot HEAD: `671774dfc8e8be8eac2b50d5fb8f0928591694b3`;
- Template version: `2.8.6`;
- upgrade commit: `governance: upgrade repository-local setup to v2.8.6`;
- Pilot Governance CI run: `36275524530`;
- CI conclusion: `SUCCESS`;
- `C1-12-J-C`: DONE;
- parent `C1-12-J`: DONE.

## Required sequence

1. reobserve `Patricked-code/Gouvern` main immediately before starting;
2. require the exact HEAD to remain `671774dfc8e8be8eac2b50d5fb8f0928591694b3` or reconcile any newer change before continuing;
3. resume the existing `Gouvern#3` objective through the governed machine local-entry start path;
4. require resulting mode `NORMAL_GOVERNED_ENTRY`;
5. verify the existing first-agent baseline/session/work authorities are preserved;
6. verify no duplicate first-agent baseline or first-agent session is created;
7. capture the resulting normal-entry handoff/evidence;
8. continue chronologically to `C1-12-L` only after K passes.

## Safety boundary

- Do not replay the V2.8.6 upgrade.
- Do not patch the pilot directly.
- Do not start STEP 5 / `P12-S5`.
- If a generic framework defect appears, stop pilot mutation and return the defect to the Template first.
- The GMC programme remains `PLANNING_ONLY` and dependency-bound behind CASE 1 closure.

## Framework correction discovered during C1-12-K

The first live machine-local-start attempt did not advance the pilot because the source Control Plane token lacked the GitHub permission required to create a repository dispatch event.

Correction evidence:
- corrective sub-task: `C1-12-K-A`;
- RED CI: `36292333079`;
- GREEN CI: `36292388479`;
- correction: local-start GitHub App token uses `Contents: write`.

After the correction is merged, the required action remains exactly `C1_12_K_RERUN_GOUVERN_ISSUE_3`. Reobserve the pilot HEAD before retrying. Do not replay V2.8.6.
