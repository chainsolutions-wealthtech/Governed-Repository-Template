# Décision propriétaire — deux domaines autonomes, pont contrôlé et grand LAB

**Date de consignation : 2026-10-19** · **Statut : cadrage propriétaire enregistré, implémentation à instruire** · **Dépôt exclusif :** `chainsolutions-wealthtech/Governed-Repository-Template` · **Fil :** PR #339 · **Continuité documentaire proposée :** `GRT-CONT-AUDIT-STABILISATION-20261019-001`.

## Décision et limites

Le propriétaire sépare formellement le travail en deux parties **indépendantes**, avec des registres, identités, événements, sessions, décisions et preuves propres. Un pont permet uniquement des références et rapprochements attestés. **Pas de refonte majeure ni de changement des autorités de production dans cette phase.**

### Domaine 1 — Pool GSCC / GSE / GACR

- Entrée et admission par `00_GSCC_ENTRY.md`, selon les phases, contrôles et gates réellement en vigueur.
- Les identités logiques, sessions, claims, tâches, dispatches, checkpoints et audits appartiennent à leurs sources d'autorité existantes.
- Respecter le processus complet ; ne pas inventer de First Touch, F1, RELEASE ou session ; ne pas dupliquer les registres GACR.
- Construire d'abord une cartographie vérifiable des capacités et identifiants déjà présents ; modifications seulement après autorisation distincte.

### Domaine 2 — Gouvernance / espace expérimental propriétaire

- Entrée propriétaire explicite via `00_DIRECT_OWNER_ENTRY.md` et permissions GitHub natives vérifiées ; aucune admission GACR implicite.
- Missions nommées, annuaire, historique des instructions, agents de travail, sessions traçables **de ce domaine**, artefacts, LAB et checkpoints.
- Grand LAB **candidat**, contenant des sous-LAB spécialisés ; `main` est la référence à observer et à comparer, non une cible à modifier automatiquement.
- Chaque expérimentation précise la baseline `main`, les écarts, les tests, le résultat et une proposition éventuelle de rapprochement ; aucun merge/release/refonte sans nouveau mandat et protections applicables.
- Réutiliser les mécanismes LAB et les conventions du dépôt après inspection ; pas de nouvelle porte d'admission, pas de queue concurrente.

### Pont de liaison — sans transfert d'autorité

Schéma logique cible, **non déployé** :

`bridge_link_id`, `source_domain`, `source_record_ref`, `target_domain`, `target_record_ref`, `relationship_type`, `evidence_url`, `verified_at_utc`, `status`.

Un lien `CORRELATES_WITH` / `REFERENCES` / `DERIVED_FROM` n'est jamais un claim, une permission, une admission ou une identité partagée. Les IDs de session et d'agent demeurent ceux de leurs autorités respectives. Liens non prouvés = `UNRESOLVED`.

## Annuaire cible de l'espace (à construire progressivement)

| Entrée logique | Domaine | Identité/registre source | Statut initial |
| --- | --- | --- | --- |
| `MISSION-AUDIT-HISTORIQUE` | Gouvernance expérimentale | PR #339, dossier `docs/audits/2026-10-19/` | EN COURS ; exhaustivité non attestée |
| `MISSION-RESOLVEUR-ROUTEUR` | Gouvernance expérimentale | Mandat propriétaire, PR #339 | À CONSTRUIRE / TESTER |
| `POOL-GSCC-GSE-GACR` | Domaine 1 | Sources GACR du dépôt | EXISTANT ; inventaire et rapprochement requis |
| `GRAND-LAB` | Domaine 2 | Pas encore d'ID LAB natif attesté | PROPOSÉ ; ne pas prétendre créé |
| `PONT-DOMAINE` | Liaison | Pas encore de registre de liens attesté | PROPOSÉ |

Les labels de cette table sont des **entrées d'annuaire documentaires**, non des identifiants runtime réservés.

## Exigence d'historique exhaustif

Constituer un corpus traçable de **chaque PR, issue, commentaire, commit, action et modification de code** depuis l'origine du dépôt jusqu'à une date de coupure explicite, puis poursuivre en incrémental. Pour chaque élément : ID GitHub natif, URL, auteur connu, date UTC, relation à l'instruction/mission, fichiers ou diff, contexte, décision, résultat, impacts, vérification, liens de causalité, état d'analyse `DISCOVERED / READ / UNDERSTOOD / CROSS_REFERENCED / VERIFIED`. Ne jamais confondre inventaire et lecture exhaustive.

## Ordre des travaux

1. Vérifier les sources de vérité et l'état live de `main`, des portes et des registres, sans écrire.
2. Dresser l'annuaire et les deux cartes de domaine, puis la matrice des correspondances autorisées.
3. Définir et tester le résolveur/routeur en isolation, sans droits implicites.
4. Définir le grand LAB et ses sous-LAB à partir des composants existants ; attendre mandat pour création.
5. Reconstruire l'historique GitHub complet avec preuves, état de couverture et checkpoints.
6. Comparer progressivement les expérimentations à `main` ; toute modification de `main` exige une instruction ultérieure explicite.

**Règle de conservation :** chaque instruction propriétaire nouvelle est enregistrée avec son statut et sa preuve dans le même fil canonique ; aucune suppression silencieuse de décisions antérieures. Cette note n'active aucun workflow, n'admet aucun agent et ne crée aucun LAB.
