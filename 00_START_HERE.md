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
16. `docs/AUTOMATION.md`
17. `docs/MULTI_AGENT_COORDINATION.md`
18. `docs/INFORMATION_INTAKE.md`
19. `docs/PROJECT_PROFILES.md`
20. `docs/INFRASTRUCTURE_BOOTSTRAP.md`
21. `docs/CONNECTION_INTENT.md`
22. `docs/ENTRY_ACTION_ROUTER.md`
23. `docs/EXISTING_REPOSITORY_ADOPTION.md`
24. `docs/PROJECT_MAPPING.md`
25. `docs/LAB_EVOLUTION.md`
26. `docs/REPOSITORY_SCOPES.md`
27. les spécifications, schémas, historiques, adaptateurs et preuves directement concernés ;
28. les derniers commits pertinents et l'état des contrôles/CI disponibles.

## Avant toute écriture

Dans un dépôt instancié, commencer par `python3 scripts/governance_agent.py observe`, puis `python3 scripts/governance_agent.py entry-actions`. Toute connexion doit résoudre son action d'entrée avant le dispatch mutable.

Les actions d'entrée sont : création d'un nouveau repository, adoption additive d'un repository existant, cartographie/architecture cible, lab branche/PR, ou poursuite d'un travail déjà gouverné.

Avant tout travail mutable, la session doit également résoudre son intention. Une intention `UNKNOWN`, `CONTEXT_INTAKE` ou `INFORMATION_INTAKE` ne peut pas être transformée silencieusement en permission de coder.


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


## Control plane central

Sur le repository source `chainsolutions-wealthtech/Governed-Repository-Template`, une nouvelle demande multi-repository doit commencer par le Governed Control Plane plutôt que par une écriture directe dans un repository cible.

Créer une issue `[Governed Request]` depuis le formulaire dédié. Le control plane pose ensuite une seule question ou requête d'action à la fois, construit le plan préparatoire, exige les preuves, puis émet `HANDOFF_READY`.

Dans un repository cible déjà remis par handoff, suivre la gouvernance locale normale : `observe → entry-actions → session-start → dispatch`.


## Local governed entry

Dans un repository cible initialisé, le point d'entrée préféré d'un agent est le workflow local décrit dans `docs/LOCAL_GOVERNED_ENTRY.md`. Le premier agent après bootstrap doit terminer `FIRST_AGENT_BOOTSTRAP` avant tout travail fonctionnel mutable.
