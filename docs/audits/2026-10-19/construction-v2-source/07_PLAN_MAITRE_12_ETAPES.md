# Plan directeur — fabrication, planification, validation et livraison

**Frontière immuable** : le parcours P0 GSCC→GSE→GACR→Q12→F1→RELEASE existe déjà. Ce dossier n'en modifie ni les fichiers, ni les rôles, ni les autorisations. Tout agent reprend P0 selon le mécanisme réellement applicable, puis consomme les lots.

**Point de départ réel** : `GMC-01 / GMC-G01` est le travail unique `IN_PROGRESS` déclaré par `docs/control-plane/NEXT_ACTION.md`. Le premier sous-travail `GMC-G01-T01` reste `PLANNED` dans le blueprint. L'issue #288 pilote séparément le contrat directeur global `ST01` non validé. Les sprints proposés ne changent pas cette autorité.

| Ordre de conception | Action / livrable | Contrôle de passage |
|---:|---|---|
| 01 | Observer et réconcilier l'existant | HEAD, sources, cas, tâches, statuts et contradictions sourcés |
| 02 | Verrouiller ST01 — finalité, périmètre, NFR, critères globaux | Contrat directeur approuvé ; ST02 jamais engagé par inférence |
| 03 | Dresser la nomenclature des livrables du produit final | Exigence ↔ livrable, provenance et couverture sans trous silencieux |
| 04 | Décomposer en lots, tâches, sorties et composants | IDs canoniques réutilisés et nouveaux candidats dédoublonnés |
| 05 | Définir le contrat de chaque pièce | Entrées/sorties/conditions PASS-HOLD/référence de vérité |
| 06 | Construire le graphe des dépendances | Unicité, références résolues, cycles classés, critical path calculable sur durées réelles |
| 07 | Composer les sprints en tenant compte des ressources | Capacité connue, autorité connue, conflits exclus, pas de durées inventées |
| 08 | Qualifier agents/pools éligibles via P0 | Identité/session/role/authority/claim/lease réellement vérifiés |
| 09 | Fabriquer les pièces autorisées | Branche/commit/PR selon gouvernance, test unitaire et preuve exact-HEAD |
| 10 | Revoir et assembler les livrables | Revue indépendante, CI, contrats d'intégration et tests de régression |
| 11 | Déployer par portes staging → production | Attestation d'autorité, secrets protégés, backup, rollback, smoke/E2E |
| 12 | Accepter, livrer et reprendre | Version, preuves, release, checkpoint, handoff et next_action unique |

## Mode de planification de capacité

- Aucun sprint n'a encore de date, d'effort estimé, de vélocité mesurée ou de responsable assigné.
- Les lots suivent d'abord un **ordre de dépendances**. Une équipe peut préparer en parallèle des contrats ne consommant pas de livrables non validés.
- Ne démarrer l'exécution d'un lot que si : `CANONICAL_ID_RESOLVED ∧ SCOPE_QUALIFIED ∧ DEPENDENCIES_VALIDATED ∧ EVIDENCE_FRESH ∧ AUTHORITY_VALID ∧ CLAIM_NON_CONFLICTING ∧ HEAD_FRESH`.
- Le calcul du chemin critique est en **attente d'estimations et de ressources attestées** : ne pas inventer de dates ou d'effort.
- Une sortie DONE ne vaut pas acceptance du livrable parent. Clôture d'un sprint ≠ preuve de livraison.

## Portes de transfert

1. ST01 → architecture des sous-programmes : validation explicite du contrat directeur (#288/#292).
2. GMC-G01 → GMC-G02 : les artefacts G01, provenance et exit controls passent ; pas seulement le statut.
3. GMC-G19 : revue globale du modèle; ne pas proclamer 1.0.0 sans preuves.
4. RTE-012, ARCH-006 et IDN-006 : portes de dépendance avant CAP-001.
5. CAP-012 : tests de portabilité et fournisseur/référentiel distincts acceptés.
6. ARCH-008/009/010 et SAA : API, DB, UI seulement en aval des contrats applicables.
7. SAA-012 : recette préproduction, plan de migration, tests et rollback avant SAA-013.
8. SAA-013/014/015 : autorité de déploiement réelle, smoke PASS, sécurité et acceptation de release.

## Principes transverses

- Documents candidats seulement ; aucune nouvelle base canonique ni second routeur de contrôle.
- Un agent ne s'approprie jamais une identité d'un autre agent ou session.
- La consultation documentaire est permise avant admission ; elle ne confère ni droits, ni un statut `READY`.
- Un agent récupère une fiche par ID, revalide l'état, exécute dans son scope, rattache les preuves au même objet, produit un handoff et ferme son claim selon les règles existantes.
