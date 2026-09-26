# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_12_I_B_APPLY_CURRENT_TEMPLATE_TO_CASE1_PILOT
STATE = IN_PROGRESS
```

## Objective

Validate the current framework product through the governed upgrade path on the external CASE 1 pilot.

Product/framework:

`chainsolutions-wealthtech/Governed-Repository-Template`

Released product version:

`2.8.5`

External validation pilot:

`Patricked-code/Gouvern`

## Required sequence

1. reobserve exact pilot `main` HEAD;
2. invoke the central governed client-upgrade command under that exact HEAD;
3. verify the upgrade reports the current Template manifest version;
4. verify pilot project work-items/sessions/claims/business state are preserved;
5. verify pilot Governance CI is fully green;
6. if a new generic defect appears, return to the Template and insert a new framework task before any further pilot mutation.

## Boundary

```text
TEMPLATE RELEASE
→ GOVERNED PILOT UPGRADE
→ PILOT CI / EVIDENCE
→ EVIDENCE BACK TO TEMPLATE
```

Never patch pilot business state to satisfy framework validation.
