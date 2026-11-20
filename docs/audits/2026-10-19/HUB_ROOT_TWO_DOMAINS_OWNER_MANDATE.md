# Mandat propriétaire — HUB racine, deux domaines indépendants et grand LAB

**Enregistré le 2026-10-19** · **Statut : cadrage documentaire / à implémenter progressivement** · **Dépôt :** `chainsolutions-wealthtech/Governed-Repository-Template` · **PR de rattachement :** [#339](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/339) · **Continuité documentaire proposée :** `GRT-CONT-AUDIT-STABILISATION-20261019-001`.

## 1. Instruction du propriétaire et portée

L'espace de travail doit devenir un **HUB racine permanent**, initialement presque vide, qui représente par références vérifiables l'ensemble du projet existant sur `main`. Son but est de comprendre, inventorier et reconstruire progressivement les domaines du projet en sous-espaces, missions, continuités et LAB, sans copie aveugle ni mutation immédiate de `main`. Le HUB n'est **pas** une nouvelle branche `main`, une autorité runtime ni un second control plane.

## 2. Deux parties séparées, avec pont explicite

**Domaine A — GSCC/GSE/GACR (pool d'admission et d'identité).** Respecter intégralement son processus existant, ses portes, contrôles, sessions, claims, autorisations, tâches et preuves. Il possède son propre registre d'identités, de sessions et d'événements. Une entrée directe Porte B n'est pas une admission Porte A et ne doit pas être convertie rétroactivement en First Touch ou F1.

**Domaine B — Gouvernance / architecture / missions / travaux.** Cartographier les mécanismes de gouvernance déjà présents dans le dépôt, puis constituer les missions, tâches, registres de livrables, décisions et expériences dans l'espace documentaire du HUB. Ce domaine ne remplace ni les règles de `main` ni le control plane existant.

**Pont A ↔ B.** Maintenir un registre de corrélation **référentiel** : ID source, type, identité prouvée, mission cible, preuve, date UTC, statut et contraintes. Ne pas fusionner les namespaces, attribuer de droits ou modifier les sources d'autorité au moyen du pont. Les changements d'autorité éventuels nécessitent un mandat distinct, les contrôles existants et des tests.

## 3. Grand LAB de reconstruction

Un LAB racine expérimental doit pouvoir contenir des sous-LAB et sous-espaces thématiques ; chaque branche, copie de référence, test et résultat doit être traçable. L'état `main` est observé par SHA, arbres Git, PR, issues, commits et checks. Le LAB **n'est pas créé par ce document**. Toute création future respecte le contrat LAB existant, les permissions natives et la validation du propriétaire ; pas de création automatique d'issue ou PR en dehors du mandat.

Cycle progressif : **observer → indexer → comprendre → comparer → concevoir → isoler en LAB → tester → évaluer l'écart avec main → proposer → autoriser séparément → intégrer si validé**.

## 4. Annuaire et mémoire canonique du HUB

Le HUB doit résoudre des noms stables et des IDs non ambigus pour :
- domaines, missions, sous-espaces, LAB, agents, sessions, tâches et dépendances ;
- instructions propriétaire (texte source ou preuve), décisions, événements, communications, audits et checkpoints ;
- PR, issues, commentaires, commits, diffs de code, actions/workflows, exécutions CI, releases, branches et SHA ;
- artefacts d'analyse, anomalies, rapprochements, tests et résultats.

Pour chaque objet : `canonical_id`, `type`, `parent_id`, `source_url`, `source_sha`, `first_seen_at_utc`, `last_verified_at_utc`, `status`, `owner_instruction_id`, `evidence`, `related_ids`, `checkpoint_id`. Un ID documentaire ne devient jamais une identité GACR ou une permission.

L'annuaire est **progressif et vérifiable** : `INVENTORIED` ≠ `READ` ≠ `UNDERSTOOD` ≠ `CROSS_REFERENCED` ≠ `VALIDATED`. Ne jamais annoncer l'exhaustivité de l'audit tant que chaque PR, issue, commentaire, commit et changement de code n'a pas été examiné individuellement et relié aux preuves. Les éléments non accessibles restent `UNVERIFIED`.

## 5. Reprise et journal de mission

À chaque nouvelle instruction : enregistrer la demande, son périmètre, le domaine, l'identité prouvée, la mission, les liens de preuve, les actions, les résultats et le checkpoint. Une conversation nouvelle peut demander `GRT-AUDIT-STABILISATION` et l'annuaire ; le rattachement automatique à une session runtime doit être construit et attesté, non supposé.

La première mission est **AUDIT-HISTORIQUE** ; d'autres missions (reconstitution du code, création de LAB, essais de gouvernance, etc.) seront ouvertes uniquement au fur et à mesure des instructions. La PR #339 reste le lieu unique du cadrage actuel.

## 6. Non-régression

Ne pas modifier `main`, les règles GSCC/GSE/GACR, les registres sources, le routeur d'admission, les permissions ou les workflows par ce seul cadrage. Les droits proviennent exclusivement de l'authentification et des autorisations natives. Ne pas confondre ce dépôt avec `Patricked-code/MCP`.

**Prochain travail soumis au mandat :** établir une cartographie complète des deux domaines et de leurs points de jonction existants, puis proposer la structure du HUB et du grand LAB avec un plan de tests et une matrice d'annuaire ; ne pas présumer de leur activation.
