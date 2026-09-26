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

