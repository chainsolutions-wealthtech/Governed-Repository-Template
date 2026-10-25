# PROGRAMME ISOLÉ GRT — REGISTRE 2 : GOUVERNANCE ET MÉMOIRE

**Projection documentaire / pas une seconde autorité**. Parent `GRT-CONT-AUDIT-STABILISATION-20261019-001` ; PR #339 DRAFT, branche `audit/20261019-histoire-identites-stabilisation`. Ce registre accompagne le registre Identification et les autorités du control plane ; ne modifie ni `main`, ni les tâches GACR.

## Gouvernances à garder distinctes
1. **Identité/admission** : Porte A `GSCC → GSE → GACR → F1`, ou Porte B explicitement choisie avec authentification GitHub réelle. Aucune perméabilité automatique des permissions, sessions et claims.
2. **Gouvernance du dépôt** : `00_START_HERE.md`, `GOVERNANCE.md`, `AGENTS.md`, `docs/control-plane/CURRENT_STATE.md`, `MASTER_SYSTEM_MAP.md`, `TASKS.md`, `NEXT_ACTION.md`, `DECISIONS_LOG.md`, `.governance/control-plane-state/*.json` ; HEAD, CI, PR et règles de branche.
3. **Programme expérimental documentaire** : inventaire, audit, mémoire, architecture existante/cible, tâches candidates, checkpoints ; ne devient pas une autorité runtime.

## Relevé des PR de la plage 300–339 — métadonnées vérifiées
| PR | Sujet résumé | Statut observé |
|---|---|---|
| #316 | F1 harvester | MERGED |
| #317 | Namespace dispatch | MERGED |
| #318 | Renouvellement Q12 | MERGED |
| #319 | HOLD review | MERGED |
| #320 | Réconciliation plan LAB | MERGED |
| #322 | CODE_AGENT Q9 | MERGED |
| #323 | Alias NOVA | MERGED |
| #324 | Rôle NOVA | MERGED |
| #326 | Porte B | MERGED |
| #328 | F1QUEUE RTE-014 | MERGED |
| #330 | LABENTRY | MERGED |
| #332 | Recovery F1 | MERGED |
| #333 | Owner F1 | MERGED |
| #334 | CHAINFLOW PREP-003 | OPEN, non fusionnée |
| #335 | Choix post-F1 | MERGED |
| #339 | Audit historique | OPEN, DRAFT |

**Couverture** : ces 16 PR ont été consultées au niveau titre, état et début de description via GitHub direct. Les autres numéros de l'intervalle ne sont pas des PR confirmées par l'API PR ; il faut rechercher et lire leurs issues lorsqu'elles existent. Ni patches complets ni conversations/reviews complets analysés pour les 16 PR : `INVENTORIED`, pas `VERIFIED_SEMANTIC_AUDIT`. Statuts datés, à réobserver.

## Journal canonique documentaire des instructions
Pour chaque instruction future, conserver append-only : source vérifiable (ou null), texte original si accessible ou résumé fidèle, acteur GitHub vérifié, porte, interprétation distincte, décision owner-confirmed/proposed/superseded, liens vers PR/issue/commit, candidats tâches, dépendances, risques, tests, checkpoint. **L'historique ChatGPT complet n'est pas archivé automatiquement.** Les commentaires/commits GitHub constituent la mémoire effectivement persistée.

## Backlog historique non exécutable
| Ref locale | Tâche candidate | État |
|---|---|---|
| HIST-01 | Lire intégralement PR 300–339 réelles : corps, patches, commits, reviews, commentaires, issues associées | INVENTORY_PARTIAL / ANALYSIS_PENDING |
| HIST-02 | Corréler identités, sessions, alias, continuités, Porte A/B sans collision | PLANNED |
| HIST-03 | Corréler décisions, gouvernance, LAB, tâches et preuves | PLANNED |
| HIST-04 | Étendre l'audit chronologique à toutes les PR historiques | PLANNED |
| HIST-05 | Dessiner architecture réelle et écarts vers cible | PLANNED |
| HIST-06 | Définir et tester un rattachement idempotent multi-conversations | DESIGN_ONLY |
| HIST-07 | Mandater ultérieurement un agent LAB pour essais hors main | NOT_AUTHORIZED |

Les références HIST-* sont **des repères locaux documentaires**, non des IDs de tâches du control plane ni des claims GACR. Aucune exécution automatique.

## Invariants et transmission
- Un seul dossier de travail : PR #339 ; aucun nouveau LAB, branche, PR ou issue par cette opération.
- `main` est la référence à observer, pas la cible des expérimentations ; aucun merge automatique.
- Éviter duplications et effacements ; conserver les corrections en événements append-only.
- Pour un agent entrant : lire `00_DIRECT_OWNER_ENTRY.md` uniquement si explicitement choisi, authentifier, lire `00_START_HERE.md`, puis ces deux registres et les autorités live, reprendre le dernier checkpoint.
- À chaque lot : produire une fiche PR avec ID, source, statut, fichiers touchés, décisions, preuves, interactions, risques, tâches candidates, niveau de validation ; mettre à jour les index et checkpoint.

## État exact
Deux registres documentaires créés pour organiser un **programme isolé en conception** ; pas de nouvelle identité, session, agent, LAB, moteur, runtime, ni permission. Prochaine étape : analyse sémantique PR par PR et issues associées, par lots, avant toute conception technique irréversible.
