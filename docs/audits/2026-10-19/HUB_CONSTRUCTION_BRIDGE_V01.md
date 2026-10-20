# HUB ↔ Construction GRT — contrat de liaison documentaire V0.1

**Statut : `DESIGN_ONLY / PUBLISHED_IN_PR339_DRAFT / NOT_CANONICAL / NO_RUNTIME_AUTHORITY`.**
**Dépôt unique** : [`chainsolutions-wealthtech/Governed-Repository-Template`](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template) · **Espace documentaire** : [PR #339](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/339) · **Programme Global existant** : [issue #288](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/288).
**Baselines constatées à la préparation (20 octobre 2026)** : `main@0f8fc5c7fde5fa8ba012fc29dcfa020372016616`, `PR339@819a8b7ce055044ac2072b0f8363ae18192c5026`. **Archive de planification datée 16/10/2026** : `GRT_Dossier_Directeur_Construction_V2_2026-10-16.zip`, SHA-256 `475c4f40d1648baec414871a929bbfc8062b2150574fb23e32b1fa6f3ab2935d`.

## 1. Décision de structure : un seul système, plusieurs vues

Ce document **ne crée aucun deuxième Programme Global, hub runtime, contrôle d'accès, registre de tâches, moteur de dispatch, bus, queue, session ou source de vérité**. Le HUB de la PR #339 est un *point de navigation, de mémoire documentaire et de regroupement des missions*, et non une copie fonctionnelle de `main`. Son identité permanente est **EN ATTENTE DE DÉCISION** : `hub_root_id=null`. `GRT-HUB-ROOT-001` reste une **proposition**, jamais une identité adoptée.

Le dossier V2 contient **378 fiches candidates**, dont **342 références à des identifiants existants à la date du snapshot**, **32 identifiants locaux de proposition**, **4 références de planification proposées**, 20 livrables candidats, 16 enveloppes de sprint et 1012 relations typées. Ces volumes sont un inventaire local et **non une preuve d'approbation, d'exécution ou de couverture exhaustive de l'état GitHub présent**.

### Vue de filiation (liens, pas nouveaux parents runtime)

```text
GRT (main : source de vérité existante)
├─ Autorités P0 / Porte A et Porte B explicitement sélectionnée [DOMAINE IDENTITÉ]
└─ Programme Global déjà existant → issue #288 [DOMAINE GOUVERNANCE]
   ├─ CP-ARCH-001 / CP-NAMESPACE-001 / RQ-01..35 / TASKS / NEXT_ACTION
   ├─ GMC-A / GMC-G01 et autres programmes et cas existants
   └─ Vue documentaire du HUB expérimental → PR #339
      ├─ MISSION-AUDIT-001 / MISSION-CONTINUITE-002 (déjà documentées)
      └─ [MISSION CONSTRUCTION : PROPOSITION NON ENREGISTRÉE]
         └─ Dossier V2 : 378 FICHES CANDIDATES (références / index dérivé)
            ├─ références réelles de tâches/artefacts GMC/ARCH/IDN/RTE/CAP/SAA
            └─ spécifications, livrables et sprints locaux DRAFT
```

L'arbre est un **parcours de découverte**. Les véritables liens parent/enfant et états exécutables sont relus dans leurs autorités propres. Une tâche peut contribuer à plusieurs livrables et sprints ; ne pas forcer une hiérarchie exclusive.

## 2. Pont explicite des deux domaines

| Domaine source | Dans le HUB | Contrat de vérité |
| --- | --- | --- |
| **A — GSCC/GSE/GACR, admission, agents et sessions** | Références vers IDs/sessions/grants/événements réellement attestés | Jamais d'ID d'agent inventé ; jamais de droit dérivé du lien documentaire ; Porte A non modifiée |
| **B — Programme Global #288, CP-ARCH-001, tasks, modèles, cas, claims, CI** | Annuaire des programmes, missions, pièces, livrables et travaux candidats | Git/registre existants font foi ; le HUB ne possède pas la task queue |
| **Plan V2 du 16 octobre** | Index lecture seule `HUB_CONSTRUCTION_CROSSWALK_V01.csv` et archive candidate | Snapshot obsolescent ; consulter le registre live avant toute action ; `DESIGN_ONLY` |
| **Événements/Checkpoints/Decisions** | Pointeurs vers sources et preuves GitHub vérifiables | Indexer événements natifs, sans journaux d'autorité parallèles |

**Lien A↔B** = `REFERENCES`/`CORRELATES_WITH`/`DERIVED_FROM`, jamais `GRANTS_AUTHORITY`, `CLAIMS` ou `CREATES_SESSION`.

## 3. Contrat minimal de résolution d'une pièce

1. Rejoindre l'annuaire du HUB **en lecture seule**, résoudre l'alias et l'identité racine lorsqu'adoptée ; si nom ambigu ou ID en attente : `HUB_ID_PENDING` ou `AMBIGUOUS_ALIAS`.
2. Identifier mission / pièce par son **ID source**, pas par une position de sprint. Exemple `GMC-G01-T01`, référence officielle dans le blueprint GMC.
3. Lire la fiche candidate correspondante du paquet V2, puis **relire ses sources natives sur le HEAD GitHub actuel**, y compris définition, statut, parent, dépendances, décision, claim/lease, CI, preuves et dernier checkpoint. Marquer toute divergence `STALE/CONFLICT/UNVERIFIED`, pas `READY` par hypothèse.
4. Résoudre les liens de projet : exigences `RQ-*`, livrables proposés `DEL-DRAFT-*`, sprints proposés `SPR-DRAFT-*`, relations typées. Les entités `DRAFT-*` ne sont **ni des tâches runtime ni des identifiants officiels**.
5. Si l'agent souhaite seulement **lire**, afficher le dossier. S'il veut **agir**, contrôler d'abord la porte effectivement sélectionnée et ses preuves, les droits natifs, le scope de travail, la politique de branches, l'exact-HEAD et l'absence de collision ; sinon `HOLD`.
6. Après opération réellement autorisée : l'action, ses tests, son PR/commit et checkpoint doivent être écrits dans les **registres déjà applicables** ; le HUB met seulement ses références à jour.

**Règle de reprise** : `hub_alias → mission → piece_ref → canonical_definition → actual_state/evidence → first_unverified_instruction`. Une conversation sans preuve d'identité ne reçoit aucun claim sur une ancienne session.

## 4. Portes de cohérence et d'acceptation

- `GATE-0` : ne pas publier cette proposition sur GitHub sans voie A/F1 réellement libérée **ou** voie B explicitement demandée et contrôlée selon ses règles ; un outil GitHub disponible n'est pas une permission de contourner une entrée.
- `GATE-1` : lier le paquet au HUB seulement comme **pièce documentaire candidate** dans la PR #339, pas comme autorité runtime. Aucune nouvelle issue/PR.
- `GATE-2` : confronter la baseline V2 `638fcc51c77f2454990f239b8b8cca78bac8075b` avec l'état courant de `main` et le contrôle du Programme Global #288/ST01 (toujours en attente de validation au relevé).
- `GATE-3` : vérifier unicité IDs, résolutions de références, parents, dépendances, allers-retours avec exigence/livrable/sprint, provenance et fichiers sources.
- `GATE-4` : contrat ST01 validé par l'autorité réelle **avant** toute promotion de propositions en travaux ; sinon les pièces restent `DESIGN_ONLY`.
- `GATE-5` : CI et revue documentaire de PR #339, aucun merge automatique ; pas de modification du code runtime.

## 5. Découpage de l'intégration, sans duplication

**Lot documentaire D0** : ajouter à l'espace **existant** de PR #339 le présent contrat, son manifeste et l'index dérivé (pas les 378 contrats copiés sur une deuxième queue). Conserver le ZIP V2 et son SHA comme **source candidate** ; si le ZIP n'est pas publié dans un emplacement durable, marquer son accès `LOCAL_ONLY` et ne jamais prétendre qu'il est récupérable par un autre agent.

**Lot de réconciliation D1** : relecture des autorités `main`, rapprochement des 378 IDs et du statut des 132 travaux du snapshot, résolution de différences; documenter les IDs locaux non enregistrés.

**Lot de validation D2** : faire qualifier dans #288/#292 le contrat ST01. Les 20 livrables et 16 sprints sont des cibles à arbitrer, pas des unités de travail runtime déjà admissibles.

**Lot de consommation D3** (futur, soumis à mandat) : permettre au résolveur de la PR #339 de retourner `construction_summary`, `piece_details` et `next_governed_action` tirés des registres et preuves existants, avec statut explicite. Réutiliser le routeur et la mémoire, sans nouveau moteur de planification parallèle.

## 6. Source et limites

- [Architecture proposée du HUB](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/audit/20261019-histoire-identites-stabilisation/docs/audits/2026-10-19/HUB_CANONICAL_ARCHITECTURE_DECISION_PROPOSED.md)
- [Frontière mémoire HUB et projet](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/audit/20261019-histoire-identites-stabilisation/docs/audits/2026-10-19/PR339_WORKSPACE_CANONICAL_MEMORY_BOUNDARY.md)
- [Résolveur HUB read-only V1](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/audit/20261019-histoire-identites-stabilisation/docs/audits/2026-10-19/HUB_ENTRY_READ_ONLY_RESOLVER_V1_CONTRACT.md)
- [Annuaire des missions existantes](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/audit/20261019-histoire-identites-stabilisation/docs/audits/2026-10-19/CANONICAL_MISSION_DIRECTORY.md)
- [Architecture globale GRT](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/main/docs/control-plane/CANONICAL_ARCHITECTURE.md)
- [Programme Global ST01 #288](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/issues/288)
- [Blueprint GMC]( https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/main/.governance/control-plane-state/governance-model-execution-blueprint.json )

**Limites** : aucune adoption HUB ROOT, aucun registre de construction runtime, aucun système automatique de répartition, aucune preuve de disponibilité des sessions ou d'acceptation de ST01 créés par cette liaison documentaire. Ce texte n'inclut pas de transcription intégrale des conversations privées ; uniquement des faits sourcés et un projet de liaison.