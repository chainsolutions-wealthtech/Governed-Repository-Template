# Reconciliation documentaire OP-01 a OP-06 — observation initiale

Date de consignation : 2026-10-20. Depot : `chainsolutions-wealthtech/Governed-Repository-Template`. Continuite de travail : `GRT-CONT-AUDIT-STABILISATION-20261019-001`. PR #339 : DRAFT / OPEN / NOT_MERGED.

> TRACE D'AUDIT NON CANONIQUE — DOCUMENTATION_ONLY. Aucun nouveau mandat, identite, session, claim, registre runtime, task READY, autorite ou decision proprietaire. Les OP-01..OP-06 sont des reperes de presentation et non des taches enregistrees.

## OP-01 — Baseline observee

- Porte B : `00_DIRECT_OWNER_ENTRY.md`, login authentifie `Wealthtechinnovations`, ID GitHub `94637590` ; permission native repository `admin=true`, `push=true`, `pull=true`.
- PR #339 : branche `audit/20261019-histoire-identites-stabilisation`, HEAD observe et reobserve avant cette ecriture `7d836698c15789f152de535251797897fc162db9` ; base `main` ; PR DRAFT, non fusionnee.
- Le SHA de `main` indique dans le checkpoint precedent est `0f8fc5c7fde5fa8ba012fc29dcfa020372016616` (observation historique du checkpoint, **non** nouvelle attestation live de main).
- Les fichiers de source `docs/control-plane/CURRENT_STATE.md`, `NEXT_ACTION.md`, `.governance/control-plane-state/checkpoint.json` et `handoff.json` ont ete lus sur la branche par defaut ; ils identifient `GMC-A / GMC-G01`, `GMC-01 IN_PROGRESS`, `CP-CHECKPOINT-20261007-023`, `CP-HANDOFF-20261007-023`, action `GMC_01_SEPARATE_GOVERNANCE_MODEL_FROM_APPLICATION_STRATEGIES`.

## OP-02 — Dernier checkpoint proprietaire

- PR #339 commentaire natif [#6281343664](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/339#issuecomment-6281343664), cree le 2026-10-20 01:42:16 UTC.
- Import integral atteste sur commit `7d836698c15789f152de535251797897fc162db9` ; prochaine action documentaire : revue du corpus, reconciliation V2 avec les autorites main, puis arbitrages separes ST01 et identite HUB. Pas de fusion automatique.
- Les checkpoints plus anciens `#6280913318` (25/412) et `#6280325412` (CI d'un SHA precedent) sont conserves comme historique, pas comme dernier etat.

## OP-03 — Corpus et provenance

- `HUB_CONSTRUCTION_MANIFEST_V01.json` : `total_source_files=412`, `files_published_in_pr=412`, `files_remaining=0`, `candidate_pieces=378`, `unique_piece_ids=378`, `relationships_in_local_candidate=1012`, `requirements=35`, `deliverables_proposed=20`, `sprints_proposed=16`.
- `construction-v2-source/README_IMPORT_STATUS.md` : annonce verification 412/412 empreintes Git blob SHA-1, 0 difference, 3 108 774 octets ; ce document et le checkpoint sont les sources de cette attestation historique. **Pas de nouveau recalcul exhaustif effectue dans cette passe**.
- Source ZIP annoncee : `GRT_Dossier_Directeur_Construction_V2_2026-10-16.zip`, SHA-256 `475c4f40d1648baec414871a929bbfc8062b2150574fb23e32b1fa6f3ab2935d`. Le ZIP unique n'est pas present dans GitHub ; les contenus individuels y sont declares publies.

## OP-04/05 — Correspondances et frontieres initiales

| Sujet | V2 candidat | Autorite existante / reference | Constat | Verification restante |
| --- | --- | --- | --- | --- |
| Programme de travail | 378 fiches `lots/*.md` | `NEXT_ACTION.md` : GMC-01 / GMC-G01 | CANDIDAT, aucune promotion automatique | Revue semantique fiche par fiche et correspondance au backlog |
| Contrat ST01 | `10_AVANT_PROJET_CONTRAT_DIRECTEUR_ST01.md` | Programme Global issue #288 et #292, selon dossier V2 | CANDIDAT_NON_APPROUVE | Decision proprietaire et preuves de gate |
| Autorite de construction | 20 livrables, 16 sprints, 1012 liens | Control Plane source, namespace et task registry | PROPOSITION, non task queue | Tester collisions, dependances et cardinalites |
| Admission et identite | P0 / GSCC / GSE / GACR / F1 hors perimetre V2 | `00_GSCC_ENTRY.md` et `00_DIRECT_OWNER_ENTRY.md` | FRONTIERE PRESERVEE dans la documentation | Comparaison contrats et mecanismes en lecture seule |
| Identite HUB | `hub_root_id: null` dans le manifeste | `HUB_CANONICAL_ROOT_IDENTITY_AND_OWNER_MANDATE.md` retient `GRT-HUB-001` documentaire ; `HUB_ROOT_IDENTITY_DECISION_PENDING.md` indique decision definitive en attente | DIVERGENCE DOCUMENTAIRE DE STATUT, pas preuve de collision runtime | Lire chronologie de decisions et obtenir arbitrage explicite si non tranche |
| Memoire PR #339 | Workspace de continuite documentaire | `PR339_WORKSPACE_CANONICAL_MEMORY_BOUNDARY.md` | DISTINCTE de la memoire source main | Construire crosswalk de provenance, sans base parallele |

## OP-06 — Registres : statut de verification

Le rapprochement exhaustif registre par registre n'est PAS termine. Aucun registre runtime n'a ete modifie. La prochaine passe doit lire `NAMESPACE_WORK_REGISTRY.md`, `namespace-work-registry.json`, `tasks.json`, les registres GACR, le manifeste de hashes et les fichiers `construction-v2-source/registres/*` ; comparer identifiants, statuts, provenance et proprietaires d'autorite. Ne pas confondre valeurs historiques, projections derivees et autorites live.

## Invariants et NEXT_ACTION

`DRAFT / DOCUMENTATION_ONLY / NO_RUNTIME_CHANGE / NO_NEW_ISSUE / NO_MAIN_WRITE / NO_AUTO_MERGE / OWNER_REVIEW_REQUIRED`.

NEXT_ACTION : achever OP-03 par recomptage independant des fichiers/hashes lorsque l'acces le permet, puis OP-04 a OP-06 avec matrice de correspondance source-par-source, tout en preservant les divergences HUB/ST01 pour decision proprietaire. Reobserver les deux HEAD et les checks de ce commit avant de declarer une validation CI.
