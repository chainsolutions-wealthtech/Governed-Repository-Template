# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_12_I_VALIDATE_V2_8_4_ON_CASE1_PILOT
STATE = IN_PROGRESS
```

## Objective

Validate the **released framework product V2.8.4** on an external CASE 1 pilot without treating the pilot as the implementation target.

Product/framework:

`chainsolutions-wealthtech/Governed-Repository-Template`

Current external pilot:

`Patricked-code/Gouvern`

## Required sequence

1. reobserve exact pilot HEAD;
2. apply the governed Template V2.8.4 upgrade to the pilot;
3. verify pilot Governance CI is fully green, including `scripts/test_connection_intent.py`;
4. do not modify pilot business work-items to satisfy framework tests;
5. if CI is green, resume the existing subsequent-agent proof;
6. verify `NORMAL_GOVERNED_ENTRY` with no first-agent baseline/session/work duplication;
7. persist evidence back into the Template control-plane memory.

## Product / pilot boundary

The Template is the product. The pilot is evidence only.

```text
FRAMEWORK FIX
→ TEMPLATE CI
→ RELEASE
→ PILOT VALIDATION
→ EVIDENCE BACK TO TEMPLATE
```

## Do not

- implement generic framework changes directly in the pilot;
- promote pilot project state into framework truth;
- modify `Patricked-code/MCP`;
- advance C1-13 before the normal-entry proof is complete.
