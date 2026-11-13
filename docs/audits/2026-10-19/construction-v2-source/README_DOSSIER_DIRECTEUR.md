# Dossier directeur de construction GRT — V2 / 16 octobre 2026

**Livraison** : documentation de construction, pas code projet ni intervention sur GitHub.

- Dépôt cible : `chainsolutions-wealthtech/Governed-Repository-Template`.
- Référence de lecture : `638fcc51c77f2454990f239b8b8cca78bac8075b` (les agents doivent revalider le HEAD avant tout acte).
- P0 / GSCC / GSE / GACR / F1 : **hors périmètre, inchangé**.
- Contrat directeur ST01 : `CANDIDAT_NON_APPROUVÉ` (#288 et #292).
- Point de travail réel : `GMC-01 / GMC-G01` d'après `NEXT_ACTION.md`, sans avance fictive.

## Contenu du paquet

- **378 fiches individuelles** (`lots/*.md`), dont 24 nouvelles fiches **candidates** de conception pour les cas ADOPT/MAP/LAB.
- **20 livrables de recette proposés** (`registres/livrables_proposes.json`), reliés par proposition aux exigences et aux travaux canoniques.
- **16 étapes/enveloppes de sprint candidates**, sans dates ni engagements (`registres/orchestration_chronologique_v2.json`).
- **35 exigences** du plan initial, reprises avec leurs statuts observés.
- **1012 liens typés** entre tâches, parents, exigences, artefacts et livrables proposés.
- **Contenu V1 préservé** avec 354 fiches, les namespaces, alias/historique et contrôles initiaux.

## Ordre de lecture par un agent de planification

1. `00_LIRE_EN_PREMIER.md` : provenance et frontière canonique.
2. `07_PLAN_MAITRE_12_ETAPES.md` : chronologie, conditions de déblocage.
3. `10_AVANT_PROJET_CONTRAT_DIRECTEUR_ST01.md` : objectif final et arbitrages ouverts.
4. `06_REGISTRE_DES_20_LIVRABLES.md` : livrables et portes de recette.
5. `01_SPRINTS_ET_CHRONOLOGIE.md` et `registres/orchestration_chronologique_v2.json` : enveloppes de planification.
6. `08_PROCEDURE_DE_PRISE_EN_CHARGE_AGENT.md` : protocole de retrait/restitution d'un lot.
7. `09_STRATEGIE_DEVELOPPEMENT_VALIDATION_DEPLOIEMENT.md` : tests, assembly, staging et release.
8. `11_MANIFESTE_CHAINE_DE_PREUVES.md` : événements, journaux, cas négatifs.
9. `12_CONSIGNES_INTEGRATION_GITHUB.md` : publication conditionnée aux vraies autorités.
10. `CONTROLES_QUALITE_V2.json` : audit mécanique de ce paquet, sans présumer de réussite produit.

## Règles à ne jamais violer

- N'importe quel agent ne peut **pas** se connecter à cette projection pour gagner de nouveaux droits. P0 s'exécute d'abord avec sa propre identité et session réelles.
- Aucun `DRAFT-*`, `SPR-DRAFT-*`, `DEL-DRAFT-*` n'est une identité enregistrée dans le système canonique.
- La lecture du paquet ne confère aucun claim, permission Git, droit de fusion ou accès serveur.
- Les livrables, sprints et tests proposés ne modifient pas les états `PLANNED`, `IN_PROGRESS`, `DONE` réels.
- Un `GMC-G##-T##` ou `GMC-G##` conserve son identité native ; les aliases `GMC-01..19` sont des liens, pas de nouvelles tâches.

## Frontières de complétude

Le paquet couvre les registres/documentations reconnus et formalise les étapes manquantes les plus visibles. Il ne prétend pas prouver une **décomposition exhaustive validée de toutes les fonctionnalités du produit** : celle-ci dépend de l'acceptation ST01, de la cartographie GMC et de la revue de la matrice des exigences/livrables. Les 24 fiches des cas sont candidates et ne remplacent pas un backlog canonique complet.
