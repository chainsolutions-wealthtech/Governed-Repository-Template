# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = P12_S6_CLOSE_CREATE_NEW_REPOSITORY_CASE
STATE = P12_S6_IN_PROGRESS
PARENT = CREATE_NEW_REPOSITORY_COMPLETION
```

## P12-S5 second fresh E2E — PASS

The fresh Ekyc lifecycle now satisfies its exit gate.

- setup approval: owner `true`, central comment `5936330817`;
- baseline materialization: Ekyc `3e889a2bdac78312ebcc7e31d1388ead65c9fceb`;
- repository state: `PROJECT_BASELINE_READY`;
- first-agent session preserved: `LOCAL-000001-S1`;
- first work item preserved: `WORK-PROJECT-001` / `READY`;
- subsequent normal entry: Ekyc#2 / `LOCAL-000002`;
- mode: `NORMAL_GOVERNED_ENTRY`;
- final normal-entry state: `LOCAL_HANDOFF_READY`, revision 6;
- Ekyc HEAD unchanged throughout normal-entry proof;
- no target-specific repair and no product work executed.

## Unique next action

Execute **P12-S6 — Close CREATE_NEW_REPOSITORY CASE 1**.

Closure must reconcile PROGRAM/CURRENT_STATE/TASKS/NEXT_ACTION/SUIVI/DECISIONS, record final Template and pilot evidence, preserve external MCP items as intakes only, prove there is no orphan CASE 1 task, and only then release GMC-A.

## Safety boundary

- Do not execute `WORK-PROJECT-001` during CASE 1 closure.
- Do not mutate S1/domain/DNS/Plesk/TLS.
- Do not modify `Patricked-code/MCP`.
- Do not start GMC-A before P12-S6 passes.


## Temporary owner-authorized IDN lane — 2026-10-07

This lane is explicitly authorized by the owner and is separate from the parked global programme action `P12-S6`.

Current IDN action:

`IDN_LIVE_PROVE_PER_ARRIVAL_SESSION_RUNTIME_THROUGH_Q12_THEN_F1`

Required order:
1. merge PR #229 only after all CI/workflow regressions are green;
2. create a fresh controlled First Touch arrival;
3. verify a unique GSCC-minted arrival identity is created without inventing a provider ID;
4. complete Q9 with correlated ACK then challenge response on that arrival's own issue;
5. verify Q10 creates that arrival's own GSE SessionTwin;
6. verify canonical GACR creates/binds exactly one durable session for the same connection_ref;
7. verify Q2/Q6/Q7/Q11/Q12;
8. test F1 only against the actual governed function requested;
9. release to `00_START_HERE.md` only after F1 succeeds.

Fail closed on ambiguous identity, duplicate active binding, stale/incorrect challenge, missing canonical GACR session, incomplete access policy/grant, or failed F1.
