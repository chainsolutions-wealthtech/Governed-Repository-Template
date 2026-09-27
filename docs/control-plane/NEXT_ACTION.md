# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_B_MERGE_PR51_REUPGRADE_EKYC_RESUME_DISCOVERY
STATE = IN_PROGRESS
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## Objective

Complete the generic client-CI portability correction exposed by the governed Ekyc upgrade, redistribute the corrected local-entry surface through the official upgrader, then resume the already-preserved MCP discovery checkpoint.

## Live evidence

- Template PR #50 merge: `dbe0014784362393c8cfbb02ce7810d483cf2bb7`.
- Source post-merge Governance CI: `36295619581` PASS.
- Ekyc governed upgrade commit: `2ece8cff98258f7c40cf7b7383ceb5c026db9639`.
- Ekyc local-entry state migrated with answers preserved.
- Ekyc Governance CI: `36295714554` FAIL only at repository-local governed agent entry self-test.
- Failure: `FileNotFoundError: .github/workflows/governed-control-plane.yml`.
- Root cause: the client-distributed self-test referenced a source-only workflow that is intentionally excluded from clients.
- PR #51 TDD RED: `36295815960`.
- PR #51 functional GREEN: `36295850914`.

## Required sequence

1. finish canonical human/machine/relational reconciliation on PR #51;
2. require the final PR #51 HEAD Governance CI to be all-green;
3. reobserve Template `main` and PR #51 exact head;
4. merge PR #51 under exact-head guard;
5. require post-merge source Governance CI green;
6. reobserve `Patricked-code/Ekyc@2ece8cff98258f7c40cf7b7383ceb5c026db9639`;
7. redistribute the current Template local-entry surface using `/governed-upgrade-local-entry`;
8. require Ekyc Governance CI green on the new upgrade HEAD;
9. preserve `Ekyc#1` answers, revision history and the HTTP 404 evidence;
10. execute the existing MCP discovery gate once so the new 404 recovery logic reopens endpoint correction;
11. correct the endpoint to the previously verified direct MCP route `https://mcp.wealthtechinnovations.com/mcp`;
12. rerun read-only discovery and continue C1-13 only after PASS/non-degraded evidence.

## Safety boundary

- Do not add `governed-control-plane.yml` to a client repository.
- Do not patch Ekyc directly.
- Do not recreate Ekyc or its baseline.
- Do not discard prior discovery failure evidence.
- No scoped runtime mutation is authorized merely by the stored policy; each write still requires explicit approval.
- P12-S6 and GMC implementation remain blocked until P12-S5 completes.
