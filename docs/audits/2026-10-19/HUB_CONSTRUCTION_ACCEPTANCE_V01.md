# HUB ↔ Construction GRT — vérifications et portes V0.1

> PR #339 (DRAFT) — DOCUMENTARY_ONLY, NON_CANONICAL, NO_RUNTIME_CHANGE, NO_NEW_ISSUE, NO_MAIN_WRITE, NO_AUTO_MERGE.

## Contrôles accomplis

- Porte B `00_DIRECT_OWNER_ENTRY.md` explicitement sélectionnée ; acteur authentifié GitHub `Wealthtechinnovations` et permissions natives `push/admin` vérifiées lors de l'intervention.
- Contrat documentaire reliant HUB / PR #339, Programme Global / issue #288, Control Plane existant et construction V2.
- Index CSV vérifié : **378** lignes, **378** identifiants de pièces uniques, statut de snapshot et définition source.
- Manifeste présent avec provenance, archive candidate et empreinte SHA-256.
- Déploiement, runtime, portes GSCC/GSE/GACR/F1, registres d'autorité et branche `main` non modifiés par cette intervention.

## Ce qui n'est PAS prouvé ni livré

- L'archive `GRT_Dossier_Directeur_Construction_V2_2026-10-16.zip`, SHA-256 `475c4f40d1648baec414871a929bbfc8062b2150574fb23e32b1fa6f3ab2935d`, reste **LOCAL_ONLY**. Les contrats détaillés des 378 pièces ne sont pas accessibles dans GitHub par la seule présence de cet index.
- Le contrat directeur ST01 n'est pas validé par ce travail ; l'identité définitive du HUB n'est pas adoptée.
- Les états d'exécution, claims, sessions, permission, liveness, CI et déploiements ne peuvent jamais être déduits du dossier V2.
- Pas de seconde queue, de bus, de dispatcher ou de nouvelle machine d'état activés.

## Portes suivantes

1. Revalider le HEAD réel de `main`, l'état de #288, les contrats GMC et les identités actuellement attestées.
2. Contrôler la nomenclature V2 contre les définitions et états canoniques actuels ; classifier `EXISTING`, `PROPOSED`, `STALE`, `CONFLICT`.
3. Définir un stockage durable approuvé pour les 378 fiches détaillées et vérifier leur intégrité avant toute promesse de reprise complète.
4. Soumettre le contrat ST01 et l'identité racine HUB à décisions propriétaires **distinctes**.
5. Effectuer revue et CI de la PR #339 sur son **dernier SHA**, sans fusion automatique.
6. Avant toute tâche exécutable, vérifier le scope, les dépendances, les permissions natives et les contrôles/collisions existants.

## Règle de non-régression

`HUB_VIEW` = découverte / liens / mémoire documentaire.
`PROGRAMME_GLOBAL_288` = filiation de programme et décisions ST01.
`CONTROL_PLANE` / `GMC` = définitions et états de travail applicables.
`GSCC/GSE/GACR` = admission, identités, sessions, claims et preuves selon leurs autorités.
`DOOR_B` = entrée GitHub propriétaire authentifiée, sans création de session GACR.

Aucun de ces périmètres ne peut usurper une autre autorité à travers ce pont.
