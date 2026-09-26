# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_12_G_FIX_GENERIC_INTENT_SELFTEST
STATE = IN_PROGRESS
```

## Objective

Fix the generic connection-intent self-test in the **framework product**:

`chainsolutions-wealthtech/Governed-Repository-Template`

Root cause already proven by C1-12-F:

```text
test_connection_intent.py
copied the executing repository's real work/session state
→ an instantiated client could carry WORK-PROJECT-001 READY
→ synthetic dispatch selected that real work item
→ test expected WORK-DISCOVER-001
→ INTENT_SELFTEST_FAILED: unexpected work item
```

## Required implementation

1. build an explicit synthetic template fixture inside `test_connection_intent.py`;
2. reset only self-test state: profile/template marker, work-items, claims, sessions and canonical-memory pointer;
3. keep real repository/project state untouched;
4. assert the synthetic bootstrap produces exactly `WORK-INIT-001 DONE` + `WORK-DISCOVER-001 READY`;
5. run full Template Governance CI;
6. release V2.8.4 only if all checks pass.

## Product / pilot boundary

- Product/framework implementation target: `chainsolutions-wealthtech/Governed-Repository-Template`.
- `Patricked-code/Gouvern` is a CASE 1 validation pilot only.
- Pilot validation happens only after the Template fix is merged.

## Do not

- patch project business state in `Gouvern`;
- use pilot work-items as framework truth;
- skip Template CI;
- advance C1-12 to normal-entry proof before V2.8.4 is validated.
