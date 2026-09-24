# 00_START_HERE — Point d'entrée obligatoire

> Statut : `APPLICABLE`  
> Dépôt : `{{REPOSITORY}}`  
> Projet : `{{PROJECT_NAME}}`

## Ordre de lecture obligatoire

1. `00_START_HERE.md`
2. `GOVERNANCE.md`
3. `README.md`
4. `AGENTS.md`
5. `SOURCE_OF_TRUTH.md`
6. `PROJECT_CONTEXT.md`
7. `STATUS.md`
8. `SUIVI.md`
9. `TODO.md`
10. `NEXT_ACTION.md`
11. `LOOP_STATE.md`
12. `CURRENT_ITERATION.md`
13. `LOOP_ENGINEERING.md`
14. `docs/DECISIONS.md`
15. `docs/ARCHITECTURE.md`
16. les spécifications, schémas, historiques, adaptateurs et preuves directement concernés ;
17. les derniers commits pertinents et l'état des contrôles/CI disponibles.

## Avant toute écriture

- confirmer le dépôt et la branche courante ;
- relever le HEAD courant ;
- lire les documents concernés avant de créer ou remplacer ;
- rechercher le travail existant ;
- établir une baseline ;
- distinguer défaut préexistant et régression introduite ;
- analyser l'impact ;
- inscrire le travail dans la boucle active ;
- vérifier les autorisations et les opérations irréversibles.

## Principe de modification

`RÉUTILISER → CORRIGER → RENFORCER → ÉTENDRE → MIGRER COMPATIBLEMENT`

## Fin d'intervention

Mettre à jour les documents d'état réellement concernés, exécuter les contrôles disponibles, persister les preuves, vérifier le remote et définir une prochaine action unique si le travail continue.
