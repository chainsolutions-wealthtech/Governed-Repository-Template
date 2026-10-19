# Hub canonique expérimental — décision d'architecture proposée

**Date de formulation :** 2026-10-19 (conversation propriétaire)  
**État :** PROPOSED / documentaire ; non déployé, non activé  
**Dépôt :** `chainsolutions-wealthtech/Governed-Repository-Template`  
**Ancrage de travail :** PR #339 ; continuité documentaire proposée `GRT-CONT-AUDIT-STABILISATION-20261019-001`.

## 1. Clarification essentielle : hub ≠ main

Le propriétaire décrit un **grand hub expérimental**, initialement vide comme structure de reconstruction, qui représente et cartographie progressivement **tout l'existant de `main`**. Le hub ne doit pas être confondu avec la branche `main` effective : `main` reste la référence de code et de gouvernance, non modifiée par la simple création du hub. Le nom oral « Everhassid » a été mentionné ; **orthographe, statut et identité définitive restent à confirmer explicitement**, sans fabriquer une autorité ou un identifiant final.

## 2. Deux domaines indépendants, pont explicite

**Domaine A — pool d'admission / identité** : GSCC → GSE → GACR, étapes et portes applicables, identités, sessions, preuves, historique, registres et règles propres. Ne pas contourner ni modifier le processus.

**Domaine B — hub de gouvernance / expérimentation** : inventaire du `main`, cartographie, annuaire, missions, instructions, analyses, sous-espaces, LAB, branches, code expérimental, tests, résultats, checkpoints et décisions. Registre autonome de **documentation du hub**, sans seconde source d'autorité GACR ou deuxième dispatcher.

**Pont A↔B** : références croisées explicites et attestées entre identité d'agent, session admise, acteur GitHub, mission, LAB, contribution, artefact et preuve. Les rôles et permissions GitHub effectifs restent distincts des identités GACR. La Porte B `00_DIRECT_OWNER_ENTRY.md` est une entrée authentifiée directe qui ne simule pas une admission Porte A.

## 3. Reconstruction progressive

1. Créer l'identité stable du hub après validation du nom, et l'annuaire des missions/continuités.
2. Inventorier chaque PR, issue, commentaire, commit, changement de code et action GitHub, en marquant `DISCOVERED / READ / ANALYZED / CROSS_LINKED / VERIFIED` ; ne pas qualifier d'exhaustif un inventaire partiel.
3. Cartographier les composants de `main`, leurs dépendances et continuités historiques ; associer preuves et versions exactes.
4. Pour chaque bloc, créer **sur instruction explicite** un LAB isolé qui reprend le code nécessaire et produit tests, preuves et propositions ; ne pas toucher au `main` par défaut.
5. Consolider les comparaisons entre LAB et `main`, vérifier les régressions et demander une décision spécifique avant toute intégration.

## 4. Journal des instructions et des réponses

Chaque instruction future doit avoir un identifiant de mission, une date UTC, un auteur vérifié ou non résolu, son texte/une référence de provenance, son statut, les réponses/décisions associées, les actions réellement effectuées, les preuves GitHub et un checkpoint. **Le contenu intégral des conversations passées n'est pas automatiquement archivé dans GitHub.** Les synthèses documentaires ne doivent pas prétendre remplacer un export exhaustif des messages et des réponses.

## 5. Invariants

- Pas de nouveau LAB, agent, session runtime, branche, PR ou issue sur la seule base de ce document.
- Pas de nouvelle autorité GACR, d'admission fictive ni de privilège implicite.
- Pas de réécriture ou restructuration de `main` sans mandat et tests distincts.
- Réutiliser les mécanismes natifs et registres existants, avec traçabilité anti-collision.
- Ne pas mélanger ce dépôt avec `Patricked-code/MCP`.

**Prochain arbitrage propriétaire :** confirmer le nom définitif du hub (notamment l'orthographe éventuelle d'« Everhassid »), puis choisir sa clé racine stable et son schéma de registre avant implémentation.
