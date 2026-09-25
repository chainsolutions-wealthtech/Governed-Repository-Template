# LAB EVOLUTION

Use a laboratory branch or PR when an existing project must evolve while the canonical branch remains the source of truth.

```text
OBSERVE CANONICAL HEAD
→ CAPTURE BASELINE
→ READ EXISTING GOVERNANCE / ARCHITECTURE / TESTS
→ DEFINE LAB SCOPE
→ OBTAIN EXPLICIT BRANCH/PR AUTHORITY
→ CREATE ISOLATED LAB BRANCH
→ IMPLEMENT ADDITIVELY
→ TEST / COMPARE / RECONCILE
→ OPEN OR UPDATE LAB PR
→ REVIEW NON-REGRESSION
→ MERGE ONLY WHEN ACCEPTED
→ ATTEST CANONICAL POST-MERGE STATE
```

The lab branch is never a second source of truth. Production state is not inferred from laboratory state, and intervening canonical work must be reconciled before merge.
