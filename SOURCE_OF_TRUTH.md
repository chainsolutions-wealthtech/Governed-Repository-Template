# SOURCE_OF_TRUTH — Hiérarchie des autorités

## Principe

Le dépôt versionné est la mémoire persistante du projet.

## Hiérarchie

1. politiques de sécurité, lois et autorités externes applicables ;
2. décisions explicites du propriétaire et ADR versionnés ;
3. contrats, schémas et spécifications canoniques ;
4. code et migrations exécutables ;
5. tests et preuves machine ;
6. `STATUS.md` pour l'état courant ;
7. `SUIVI.md` / `WORK_LOG.md` pour l'historique ;
8. `TODO.md` pour le restant ;
9. `NEXT_ACTION.md` pour l'action unique à reprendre ;
10. conversations et notes non versionnées : contexte seulement.

## Contradiction

Une contradiction est enregistrée et résolue explicitement. Aucun agent ne choisit silencieusement l'interprétation la plus pratique.

## Template source/control-plane authority

When `.template-source` exists, the repository has two deliberately separate state surfaces:

1. distributed client templates at the repository root and generic `.governance/` paths;
2. live source/control-plane state under `docs/control-plane/` and `.governance/control-plane-state/`.

For the source repository's own work, the source/control-plane state is authoritative for current program, tasks, checkpoint, handoff and next action. Root template placeholders are not evidence that the source repository is uninitialized.

The source-only memory must be removed from instantiated clients during initialization. If it survives in a client, governance validation must fail.

GitHub issues remain orchestration/evidence surfaces and do not outrank versioned source/control-plane authorities.

## Machine-readable projections

Files under `.governance/` are structured projections used for deterministic automation, continuity and concurrency control.

They do not outrank the hierarchy above. They must be derived from, and remain reconcilable with, versioned decisions, contracts, code, tests and Git evidence.

If a machine projection contradicts a higher authority, the projection is stale or invalid and must be reconciled before writing.


## Intent projections

`.governance/project-profile.json`, `.governance/infrastructure-intent.json` and `.governance/connection-intent-policy.json` are projections, not higher authorities.

A planned technical profile never overrides discovered code or an ADR. An infrastructure intent never proves that a server or directory exists. A connection intent never grants authority.


## Entry workflow projections

`.governance/entry-action-policy.json` and `.governance/repository-scope-policy.json` are routing projections. They do not override existing project authorities, branch rules, repository ownership, or explicit permissions. A lab branch is never a second source of truth, and a target architecture is never an observed architecture.


## Control plane request state

A Governed Request issue is operational orchestration state, not the canonical truth of the target project.

The control plane may hold:
- answers;
- observations returned by the connected agent;
- preparatory execution plans;
- evidence;
- the final handoff.

After `HANDOFF_READY`, the target repository and its versioned authorities remain the source of truth for target work. A control-plane issue never outranks the target repository's code, ADRs, branch rules or validated state.


## Local entry operational state

A `[Governed Local Entry]` issue is orchestration state, not canonical project truth. Once the approved first-agent baseline is committed, the versioned repository files and machine projections become authoritative according to the normal hierarchy.

## Canonical source-memory roles

For the source control plane, authorities are separated by purpose:

- TARGET: `docs/control-plane/CANONICAL_ARCHITECTURE.md` and accepted invariants;
- CURRENT: `docs/control-plane/CURRENT_STATE.md`, current/checkpoint projections;
- EXECUTION: `PROGRAM.md`, `TASKS.md`, `NEXT_ACTION.md`;
- CONTINUITY: handoff, replay ledgers and agent activity;
- HISTORY: decisions, suivi, events, evidence and owner feedback.

Target architecture never overrides newer live Git evidence. Imported memory or historical snapshots cannot satisfy live approval or mutation authority.
