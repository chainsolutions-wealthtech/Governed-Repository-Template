# Mandat propriétaire — espace canonique expérimental piloté pas à pas

**Statut : cadrage documentaire, non activé** · 2026-10-19 · continuité proposée `GRT-CONT-AUDIT-STABILISATION-20261019-001` · alias `GRT-AUDIT-STABILISATION` · [PR #339](https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/pull/339).

## Intention propriétaire exprimée

Cet espace est un **atelier expérimental permanent de consignes successives**, pas seulement un dossier d'audit. Le propriétaire y demande à son rythme : observer et cartographier l'existant ; déposer les résultats ; concevoir des outils ; ouvrir des LAB et sous-espaces ; coder en isolation ; créer ou reprendre des agents selon les autorités réelles ; comparer les résultats à `main` ; envisager ultérieurement une refonte de `main` **uniquement après décision distincte**. Ne pas pré-exécuter les étapes futures.

Toute instruction doit être consignée avec son état (`RECEIVED / ANALYZING / PROPOSED / APPROVED / EXECUTING / VERIFIED / BLOCKED / SUPERSEDED`), date, auteur prouvé ou non résolu, dépendances, portée, preuve GitHub, livrable, checkpoint et prochaine action. Les corrections et changements de mandat doivent être append-only ou versionnés, sans effacer l'historique.

## Séparation des trois couches

1. **Espace / mémoire / orchestration** : continuité, journal des instructions, registre des artefacts, sessions, agents, LAB, tâches, décisions, communications, preuves, checkpoints. Ce sont des index et liens vers les sources natives, pas un deuxième GACR ni un deuxième task dispatcher.
2. **Exécution directe Porte B** : `00_DIRECT_OWNER_ENTRY.md` sélectionné explicitement ; identité GitHub et permissions réelles vérifiées. Cette porte n'attribue aucun `GSCC-ID`, session GACR, F1 ou claim.
3. **Pont d'expérimentation vers Porte A** : étudier un mécanisme de corrélation prouvée entre acteur GitHub de Porte B, rôle, travaux, continuité et éventuelle identité GACR préexistante. Aucun rattachement automatique à une identité existante sans résolution non ambiguë, consentement, contrôles GSCC/GSE/GACR/Q12/F1 applicables et preuves ; pas de création fictive ou de bypass.

## Architecture cible à instruire progressivement

- **Racine canonique** : ID stable, alias, dépôt et état de reprise.
- **Instructions** : ID instruction, auteur, horodatage UTC, version, priorité, statut, autorisations et preuves.
- **Agents** : identité logique existante ou proposition, rôle, capacités, périmètre, propriétaire, provenance et autorité ; jamais « agent créé » sans acte vérifiable.
- **Sessions** : ID distinct par session effectivement admise, identité parent, entrée, preuve d'authentification, dernier heartbeat/checkpoint ; une conversation n'est pas automatiquement une session GACR.
- **LAB / sous-espaces** : ID, parent, objectif, branche, artefacts, dépendances, statut et lien aux mécanismes LAB existants.
- **Tâches et dispatch** : référencer la queue canonique du dépôt ; ne pas la doubler.
- **Mémoire / audit / événements / communication** : registres d'index, événements immuables, liens vers commits/PR/issues/commentaires, décisions, checkpoints, rapports et échecs.
- **Évolutions de main** : analyses d'écart et propositions séparées ; aucune fusion, déploiement, migration ou restructuration par simple appartenance à cet espace.

## Première étape autorisée par ce mandat

Documenter la matrice et vérifier les capacités réelles de résolution d'identité, de continuité, de sessions, de registres, de LAB et de porte B/A. Préparer un plan de raccordement sans modifier le contrôle d'accès ni les autorités en production. Attendre des instructions successives du propriétaire avant création de LAB, agent runtime, code exécutable ou modification de `main`.

## Condition de réussite de la reprise inter-conversations

Une nouvelle conversation connectée résout l'alias unique, charge les autorités et le dernier checkpoint, distingue instructions reçues/validées/exécutées, affiche le prochain pas et les droits GitHub effectivement vérifiés, et n'invente ni session ni historique non archivé. La reprise automatique complète reste **à développer et tester**.
