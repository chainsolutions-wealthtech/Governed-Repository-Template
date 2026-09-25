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

## Machine-readable projections

Files under `.governance/` are structured projections used for deterministic automation, continuity and concurrency control.

They do not outrank the hierarchy above. They must be derived from, and remain reconcilable with, versioned decisions, contracts, code, tests and Git evidence.

If a machine projection contradicts a higher authority, the projection is stale or invalid and must be reconciled before writing.


## Intent projections

`.governance/project-profile.json`, `.governance/infrastructure-intent.json` and `.governance/connection-intent-policy.json` are projections, not higher authorities.

A planned technical profile never overrides discovered code or an ADR. An infrastructure intent never proves that a server or directory exists. A connection intent never grants authority.
