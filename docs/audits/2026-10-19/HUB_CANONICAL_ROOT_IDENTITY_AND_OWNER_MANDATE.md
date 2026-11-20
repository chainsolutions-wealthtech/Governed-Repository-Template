# HUB canonique racine — identité et mandat propriétaire

**Date de consignation : 2026-10-20** · **Statut : décision de nommage documentaire du HUB, activation technique non attestée** · **Dépôt exclusif :** `chainsolutions-wealthtech/Governed-Repository-Template` · **PR documentaire unique :** [#339](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/339).

## Identité racine retenue

- **Nom humain** : HUB canonique de reconstruction et de continuité.
- **Identifiant racine documentaire** : `GRT-HUB-001`.
- **Nature** : espace de pilotage et mémoire de travail, **pas** une branche `main`, un agent GACR, une session, un claim, un LAB actif ou une autorité d'écriture.
- **Mission enfant historique** : `GRT-CONT-AUDIT-STABILISATION-20261019-001` / alias `GRT-AUDIT-STABILISATION`.
- **Pointeur initial de mémoire** : `docs/audits/2026-10-19/` sur la PR #339 ; ce pointeur devra être pérennisé après fusion ou clôture de la PR, sans supposer une fusion.
- **Réserve** : vérifier collisions avec les identifiants existants avant inscription dans un registre machine. `GRT-HUB-001` est un identifiant documentaire retenu ici, pas encore un enregistrement runtime.

## Mandat propriétaire — instructions et décisions conservées

1. **Chaque instruction, réponse opérationnelle, décision, action et résultat doit être traçable**, daté, rattaché au HUB puis à une mission, avec liens natifs GitHub. Le contenu des conversations ChatGPT antérieures non archivé ne peut être déclaré intégralement capturé.
2. Le HUB est un **grand espace de projet**, initialement documentaire et minimal, à enrichir progressivement. Il représente une vue organisée de ce qui existe sur `main`, **sans être lui-même `main`**.
3. **Deux domaines indépendants** : (A) le processus d'entrée, d'identité et de continuité `GSCC → GSE → GACR`, avec ses propres registres, sessions, contrôles et gates ; (B) la gouvernance du dépôt, le code, l'architecture, les workflows, les PR/issues et les évolutions de `main`, avec ses propres registres.
4. Un **pont de corrélation attestée** pourra relier A et B par références et preuves, sans fusion des sources de vérité ni création d'autorités parallèles.
5. Prévoir un **grand LAB expérimental isolé** et, si nécessaire, des sous-LAB, pour analyser, reconstituer, tester et comparer progressivement le comportement de `main`. Aucune modification massive de `main` n'est autorisée par cette note.
6. Chaque mission reçoit un **identifiant, un nom, un état, un annuaire, une chronologie et des checkpoints**. Missions futures possibles : audit historique, reconstitution de code, cartographie, LAB, tests, rapprochement et restructuration proposée.
7. **Mission audit historique** : lire, comprendre et rapprocher individuellement **chaque PR, issue, commentaire, commit, action et modification de code** depuis l'origine jusqu'à la dernière observation. Distinguer `INDEXED`, `READ`, `ANALYZED`, `CORRELATED`, `VERIFIED`, `UNRESOLVED` ; ne pas présenter un inventaire comme une analyse exhaustive.
8. Prévoir un **résolveur et routeur de fonctions par nom** pour rejoindre le HUB depuis une nouvelle conversation ; chaque rattachement à une session canonique doit être attesté, avec authentification réelle, anti-collision et permissions natives. Le rattachement automatique et l'appel universel de fonctions **ne sont pas encore démontrés**.
9. **Porte B** `00_DIRECT_OWNER_ENTRY.md` sur sélection explicite et vérification GitHub réelle ; **Porte A** `00_GSCC_ENTRY.md` reste gouvernée ; `00_LAB_ENTRY.md` ne constitue pas une nouvelle porte d'admission. L'appartenance au HUB ne confère aucun droit.
10. Travail pas à pas sous instructions du propriétaire. **Pas de nouvelle PR/issue pour cet audit, pas de Codex, pas de merge ni de mutation du control plane par défaut.**

## Schéma d'annuaire cible (non instancié)

`GRT-HUB-001`
- `missions/` — mission audit (continuité enfant existante proposée), futures missions ;
- `domaines/gscc-gse-gacr/` — registre d'identités, sessions, claims, attestations et autorités existantes ;
- `domaines/governance-main/` — inventaire et compréhension du code, de l'architecture, des PR, issues, commits, actions ;
- `bridges/` — liens sourcés entre identités et objets de gouvernance, sans équivalence automatique ;
- `labs/` — expérimentation isolée et ses descendants, après décision explicite ;
- `instructions/` — consignes, versions, réponses, statuts et preuves ;
- `events/` — journal horodaté et append-only ;
- `checkpoints/` — état et prochaine action ;
- `directory/` — annuaire actualisé sur demande.

Ces chemins sont des **rubriques logiques**, non des dossiers GitHub tous créés.

## Prochain checkpoint

**État** : identité documentaire du HUB définie ; mission audit enfant rattachée conceptuellement ; aucune session GACR ni LAB créé ; aucun routeur activé.

**Prochaine action proposée** : inventorier les identifiants et registres existants, contrôler les collisions, bâtir l'annuaire initial et la matrice de corrélation des deux domaines, puis soumettre le design du résolveur et les tests de rattachement réel avant tout changement d'autorité.

**Règle de preuve** : une proposition enregistrée n'est pas une capacité runtime testée.
