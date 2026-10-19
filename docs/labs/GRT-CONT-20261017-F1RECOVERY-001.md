# LAB — reprise F1 isolée et nom d'agent facultatif

**Continuity development ID:** GRT-CONT-20261017-F1RECOVERY-001  
**Parent development continuity:** GRT-CONT-20261016-F1QUEUE-001  
**GitHub issue:** #331  
**Branch:** lab/f1-recovery-isolation-20261017  
**Verified creator:** Wealthtechinnovations  
**Initial main HEAD:** b3d7f623b443be6b0fe987dd2c527a6a4d4a53d0  
**Status:** LAB-ONLY / NOT-MERGED / NOT-DEPLOYED.

## Observed problems
- Owner F1 workflow failure could skip saving the newly updated per-arrival
  SQLite artifact and obscure same-arrival recovery.
- During GACR waiting and internal scans, the live canonical branch HEAD
  may change before an otherwise valid owner F1 check.
- Human-readable agent_name and logical_agent_alias must be optional.

## Implemented scoped fixes
1. An owner F1 step failure is now processed without preventing same-arrival
   persistence. The workflow reports failure on that arrival's issue and
   finally fails the job, instead of masking failure as success. No global
   GACR HOLD/lock/claim is created.
2. Only the pre-mutation error OWNER_F1_EXACT_LIVE_HEAD_REQUIRED can trigger
   a single native GitHub branch reobservation and single reattempt on the
   same runtime, session, signed actor and admission. A second HEAD move
   fails closed. Q12 is reissued for owner F1 from the canonical
   authorization only when other proofs pass; normal non-owner Q12 renewal
   remains unchanged.
3. Missing, blank and UNAVAILABLE alias normalize to no alias. GSCC's
   canonical identity is still established using real arrival evidence.
   Explicit alias of invalid type and unverified continuation alias
   remain rejected.

## Chronology
1. Read Door A/B and canonical F1/GACR/alias workflows on main.
2. Create issue #331 and isolated LAB branch.
3. Add scoped F1 retry, failure checkpoint logic and alias normalization.
4. Add negative tests for drift, identity mismatch, GACR binding mismatch,
   two independent arrival DBs, second drift and missing human name.
5. Verify CI; review diff and gate readiness before any merge.

## Gate and scope boundaries
This is NOT a live E2E admission attestation. Failure does not grant rights,
remove the existing session/role/collision gates or suppress GitHub's CI red
status. Any later merge requires separate explicit authorization.
