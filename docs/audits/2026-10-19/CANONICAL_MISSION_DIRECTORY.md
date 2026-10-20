# Annuaire canonique des missions — espace expérimental GRT

**Établi le 2026-10-19 UTC · version documentaire 1 · PR #339 · pas d'activation runtime.**

## Résolution

- **Espace** : `GRT-AUDIT-STABILISATION` ; identifiant documentaire proposé `GRT-CONT-AUDIT-STABILISATION-20261019-001`.
- **Dépôt unique** : `chainsolutions-wealthtech/Governed-Repository-Template`.
- **Point d'entrée durable** : ce fichier et [README.md](README.md), [contrat de continuité](CANONICAL_CONTINUITY_PROPOSAL.md), [mandat expérimental](OWNER_EXPERIMENTAL_WORKSPACE_MANDATE.md).
- **Porte propriétaire** : `00_DIRECT_OWNER_ENTRY.md` **si explicitement sélectionnée**, authentification et droits réels obligatoires.
- **Règle** : « Donne-moi l'annuaire » signifie relire cet index **et** les registres/PR GitHub actuels, puis distinguer les missions documentées des entités runtime admises.

## Missions

| ID stable documentaire | Nom d'appel | Statut au 19 octobre | Objet | Dossier et preuve |
|---|---|---|---|---|
| `MISSION-AUDIT-001` | `MISSION AUDIT` | `IN_PROGRESS / PARTIALLY_VERIFIED` | Reconstitution chronologique de l'ensemble du dépôt, PR/issues, architecture, code, agents, sessions, décisions, anomalies, gouvernance et traces ; analyse des preuves, sans prétendre que les métadonnées suffisent à une revue de chaque diff. | [README](README.md), [PR et issues](GITHUB_HISTORY.md), [inventaire fichiers](FILE_INVENTORY.md), [architecture](ARCHITECTURE_CODE_CONTROL_MATRIX.md), [identités](CONTINUITIES_AND_IDENTITIES.md), [sessions](GACR_SESSIONS_FULL_INDEX.md), [beacons](GACR_BEACONS_FULL_INDEX.md), [commentaires](ISSUE_COMMENTS.md), [étude PR263](CASE_STUDY_PR263_SCOPE.md), [PR #339](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/339). |
| `MISSION-CONTINUITE-002` | `MISSION CONTINUITÉ` | `DESIGN_ONLY` | Résolution de l'espace, instructions successives, mémoire append-only, annuaire, reprise depuis une nouvelle conversation, corrélation contrôlée Porte B ↔ GSCC/GSE/GACR. | [contrat](CANONICAL_CONTINUITY_PROPOSAL.md), [mandat](OWNER_EXPERIMENTAL_WORKSPACE_MANDATE.md), présent annuaire. |

**Missions futures** : `MISSION-RECONSTITUTION-CODE`, `MISSION-LAB`, `MISSION-ARCHITECTURE` ne sont que des **noms de familles envisageables**. Aucun identifiant numéroté, mandat, agent ou LAB n'est créé par leur mention.

## Inventaire du dossier documentaire de la PR #339 (snapshot du 19 octobre)

1. `README.md` — rapport principal et limites de preuve.
2. `GITHUB_HISTORY.md` — **247 PR historiques** et **91 issues** inventoriées au snapshot initial ; métadonnées, pas preuve de revue intégrale de tous les diffs.
3. `FILE_INVENTORY.md` — 445 blobs de la baseline `main`, sans lecture sémantique garantie.
4. `CONTINUITIES_AND_IDENTITIES.md` — identités et continuités.
5. `ISSUE_COMMENTS.md` — index initial des commentaires.
6. `ALL_ISSUE_COMMENTS_01.md` à `ALL_ISSUE_COMMENTS_06.md` — annexes de commentaires.
7. `GACR_SESSIONS_FULL_INDEX.md` — index figé de 125 sessions.
8. `GACR_BEACONS_FULL_INDEX.md` — index figé de 680 beacons.
9. `ARCHITECTURE_CODE_CONTROL_MATRIX.md` — matrice de gouvernance et code.
10. `CASE_STUDY_PR263_SCOPE.md` — étude ciblée de portée.
11. `CANONICAL_CONTINUITY_PROPOSAL.md` — contrat de reprise proposé.
12. `OWNER_EXPERIMENTAL_WORKSPACE_MANDATE.md` — instructions du propriétaire pour l'atelier.
13. `CANONICAL_MISSION_DIRECTORY.md` — cet annuaire.

L'inventaire doit être **revalidé** contre les fichiers de la PR à chaque reprise ; des fichiers nouveaux peuvent apparaître et les PR/issues peuvent évoluer.

## Traces de chaque instruction et intervention à ajouter

Une nouvelle instruction doit être liée à : `mission_id`, `instruction_id`, texte original ou résumé fidèle, `received_at_utc` attesté, `source`, statut, livrable, liens commits/PR/commentaires, responsable prouvé, test et checkpoint. Ne jamais inventer des timestamps ni considérer une instruction discutée comme déjà exécutée. Les traces futures peuvent être archivées dans des journaux versionnés de mission, sans second registre d'autorité GACR.

## État et lacunes à ne pas masquer

- La **couverture des métadonnées** des 247 PR n'est pas une **analyse du contenu** de chacune. Il reste à extraire et classifier les diffs, reviews, commits, liens aux issues et décisions de chacune, par lots datés, et à identifier les écarts avec `main`.
- Les 247 PR et 91 issues sont un **snapshot historique** ; la PR #339 elle-même et tout événement postérieur exigent actualisation et pagination live.
- L'alias et les IDs des missions sont **documentaires**, non des identités GACR, claims, sessions ou grants.
- L'historique intégral de conversations ChatGPT non archivé dans GitHub n'est pas récupérable par simple identifiant.
- Toute création de LAB, agent, code ou restructuration de `main` reste une mission distincte à autoriser selon les permissions et gates effectifs.

## Commandes de reprise

- **« Reprends GRT-AUDIT-STABILISATION »** : résoudre espace, autorités, PR #339, dernier checkpoint.
- **« Reprends MISSION AUDIT »** : lire l'annuaire, les annexes historiques et le dernier lot vérifié ; poursuivre l'analyse sans rejouer.
- **« Donne-moi l'annuaire »** : lister les missions et leurs états, agents et sessions attestés, LAB réellement créés, registres, instructions et checkpoints.
- **« Reprends MISSION CONTINUITÉ »** : étudier le pont Porte B/GACR, sans admission ou permission fictive.

## Liaison candidate — construction GRT V2

**Statut : `PROPOSAL / DOCUMENTARY_ONLY / NOT_MISSION_ADMITTED`.** La construction V2 peut être recherchée depuis cet annuaire par le [contrat HUB ↔ Construction](HUB_CONSTRUCTION_BRIDGE_V01.md), l'[index des 378 pièces](HUB_CONSTRUCTION_CROSSWALK_V01.csv), le [manifeste](HUB_CONSTRUCTION_MANIFEST_V01.json) et les [critères de validation](HUB_CONSTRUCTION_ACCEPTANCE_V01.md). La filiation s'effectue par références au Programme Global **#288**, aux autorités du Control Plane et aux définitions GMC, jamais par une seconde Task Queue.

Le libellé **MISSION CONSTRUCTION** est un candidat fonctionnel sans ID de mission attribué, sans claim ni agent effectif. Les missions `MISSION-AUDIT-001` et `MISSION-CONTINUITE-002` restent inchangées. Les fiches détaillées ne sont pas encore publiées durablement dans GitHub ; leur source demeure `LOCAL_ONLY`. Tout consommateur doit revalider les états et les preuves live avant une action.
