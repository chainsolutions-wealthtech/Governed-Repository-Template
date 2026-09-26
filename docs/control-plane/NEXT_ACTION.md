# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = STEP_4_PROVE_NORMAL_GOVERNED_ENTRY_ON_GOUVERN
STATE = READY
```

## Objective

Use the already-baselined `Patricked-code/Gouvern` repository to prove a **subsequent** agent enters through `NORMAL_GOVERNED_ENTRY` rather than repeating `FIRST_AGENT_BOOTSTRAP`.

## Required evidence

1. reobserve exact `Gouvern/main` HEAD;
2. start a fresh local governed entry after first-agent completion;
3. verify mode = `NORMAL_GOVERNED_ENTRY`;
4. verify existing first-agent baseline/session/work state is preserved;
5. complete the normal-entry questionnaire/handoff without creating a new first-agent baseline;
6. verify CI remains green;
7. persist STEP 4 proof in source authorities.

## After STEP 4

Only then start STEP 5: the second fresh `CREATE_NEW_REPOSITORY` E2E proof.

## Do not

- skip directly to the fresh repository test;
- reset/replay the first-agent baseline on `Gouvern`;
- modify `Patricked-code/MCP`;
- infer write authority from MCP/SSH connectivity.
