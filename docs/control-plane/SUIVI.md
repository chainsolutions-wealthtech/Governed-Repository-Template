# CONTROL PLANE SUIVI

Durable chronological history for the source/control-plane repository only.

## 2026-09-26 — Self-governance gap identified

Observed that the repository already distributes persistent-memory primitives to clients but its own root project-state files remain intentionally templated with placeholders.

Confirmed existing source history was primarily recoverable through Git, issues and conversation context rather than a dedicated source-only authority set.

Decision: introduce a separate source-only memory namespace instead of converting distributed root templates into source-project state.

## 2026-09-26 — CREATE_NEW_REPOSITORY pilot checkpoint

- Template reached V2.6.10.
- `Patricked-code/Gouvern` completed first-agent baseline.
- Pilot baseline commit: `23975e0435e63fb45d7436d1f23ce8ce0a450a5f`.
- Pilot local-entry state: `LOCAL_HANDOFF_READY`.
- DIRECT MCP discovery: PASS.
- SSH OIDC discovery: PASS.
- Domain binding intentionally remains `UNRESOLVED`.
- MCP/SSH write authority remained disabled.
- Canonical framework program #12 advanced to the second fresh repository E2E proof.

## 2026-09-26 — V2.7.0 started

Purpose: make the control-plane source self-governed while guaranteeing that its own historical state never becomes client project history.

## 2026-09-26 — V2.7.0 source/client boundary proven

- Governance CI run: `36258871067` — PASS.
- Source authority coherence validation: PASS.
- Bootstrap client simulation: PASS.
- `docs/control-plane/` removed from initialized client: PASS.
- `.governance/control-plane-state/` removed from initialized client: PASS.
- Next: merge V2.7.0 and attest resulting canonical main HEAD.

## 2026-09-26 — V2.7.0 merged and source state attested

- V2.7.0 merge subject HEAD: `d11b72956e68526edf9b17aec472163a4e49a585`.
- Self-governed control-plane memory: ACTIVE.
- Source/client memory separation: ACTIVE.
- Canonical program #12 released to resume at `STEP_4_SECOND_FRESH_REPOSITORY_E2E`.

## 2026-09-26 — Program #12 chronology reconciled

- Detected mismatch: source checkpoint summarized STEP 4 as the second fresh repository test.
- Canonical issue chronology retained a distinct STEP 4 for live `NORMAL_GOVERNED_ENTRY` proof on `Gouvern`.
- Reconciliation decision: preserve both gates; STEP 4 normal-entry proof must complete before STEP 5 fresh-repository E2E.
- No test or mutable target action was started while the contradiction was unresolved.

## 2026-09-26 — Canonical relational memory started

- Introduced a source-only relational memory model for all framework cases.
- Added reusable tables for cases, modes, phases, questions/options, activities, repositories/runs, answers, decisions, events, evidence, checkpoints, handoffs, owner feedback, intakes and artifacts.
- CASE 1 is the first populated replay dataset.
- Cases 2–4 are registered and will be progressively populated from their real tests.
- CI materializes an ephemeral SQLite database and validates relational consistency.
- The committed authority remains versioned SQL/JSON; no mutable binary database is committed.
- Future target: PostgreSQL-backed admin web application after all case/parcours semantics are validated.

## 2026-09-26 — V2.8.0 canonical relational memory merged

- Release HEAD: `4c8d16b5fc71df7923942c5658c21269a0051da3`.
- Relational schema + catalog + runtime seed merged.
- Governance CI database materialization: PASS.
- Active workflow checkpoint remains CASE 1 `C1-12` / normal-entry proof.
- No frontend implemented yet; application layer remains intentionally deferred.

## 2026-09-26 — C1-12 live normal-entry proof revealed new generic work

- Created `Patricked-code/Gouvern#3` for a subsequent-agent NORMAL_GOVERNED_ENTRY proof.
- Initial start was refused by the actor authorization gate; no governed state advanced.
- V2.8.1 / PR #25 added exact-HEAD machine local-entry start.
- Gouvern upgrade to V2.8.1 exposed client control-plane policy drift.
- V2.8.2 / PR #26 synchronized current client policy while preserving target-client role.
- Gouvern upgrade to V2.8.2 exposed bootstrap self-test contamination by instantiated project choices.
- V2.8.3 / PR #27 made bootstrap consistency fixtures portable.
- Gouvern is now at `3a1b7689be5aa38b4b6fdb6456526e618f9b0dd5`.
- Current client validation passes and bootstrap self-test passes.
- Remaining blocker: Governance CI run `36262734626` fails at `scripts/test_connection_intent.py` with `INTENT_SELFTEST_FAILED: unexpected work item`.
- C1-12 remains IN_PROGRESS. C1-13 is still locked.

