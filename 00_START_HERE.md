# 00_START_HERE — Point d'entrée obligatoire

> **PRECONDITION ABSOLUE**  
> `00_START_HERE.md` n'est applicable qu'après passage par `00_GSCC_ENTRY.md` puis validation/release du flux `GSCC → GSE → GACR`.
>
> Une simple lecture GitHub, y compris `get_repo` ou `fetch_file`, ne constitue pas une admission gouvernée.
>
> Si aucune preuve de release/handoff GSCC/GSE/GACR n'est disponible, arrêter ici et revenir à `00_GSCC_ENTRY.md`.


> Statut : `APPLICABLE`  
> Dépôt : `{{REPOSITORY}}`  
> Projet : `{{PROJECT_NAME}}`

## Source/control-plane special entry

If `.template-source` exists, this repository is the source/control plane itself. Before using the distributed project-state templates below, read the source-only authorities in this order:

1. `docs/control-plane/CURRENT_STATE.md`
2. `docs/control-plane/MASTER_SYSTEM_MAP.md`
3. `docs/control-plane/REQUIREMENTS_ROADMAP.md`
4. `docs/control-plane/CANONICAL_ARCHITECTURE.md`
5. `docs/control-plane/PROGRAM.md`
6. `docs/control-plane/TASKS.md`
7. `docs/control-plane/NEXT_ACTION.md`
8. `docs/control-plane/DECISIONS_LOG.md`
9. `docs/control-plane/SUIVI.md`
10. `docs/control-plane/CASE1_REPLAY_LEDGER.md`
11. `docs/control-plane/DATA_MODEL.md`
12. `docs/control-plane/AGENT_ACTIVITY_LOG.md`
13. `.governance/control-plane-state/current.json`
14. `.governance/control-plane-state/canonical-architecture.json`
15. `.governance/control-plane-state/checkpoint.json`
16. `.governance/control-plane-state/handoff.json`
17. `.governance/control-plane-state/tasks.json`
18. `.governance/control-plane-state/case1-replay.json`
19. `.governance/control-plane-state/agent-activity.json`

Reobserve `main` HEAD before any write and reconcile it with the source checkpoint. The root files containing template placeholders remain distributed client templates and are not the source repository's live project state.

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


## Reconstruction d'un agent déjà connu

Après une release valide, un agent peut reconstruire son contexte durable sans rejouer First Touch en utilisant la projection read-only :

`python3 scripts/gacr_agent_reconstruction.py --alias <ALIAS>`

ou les sélecteurs `--logical-agent-id` / `--session-id`.

Contrat complet :

`docs/control-plane/AGENT_RECONSTRUCTION_SKELETON.md`

La projection recompose `logical_agent_id → sessions → provider contexts → continuity bus → work/claims/dispatches → takeover/forensics → checkpoint/handoff`.

Elle ne remplace jamais l'identité de l'arrivée courante, ne renouvelle pas de lease et ne crée aucune autorité. Une nouvelle conversation/provider surface doit toujours être corrélée par le chemin canonique GSCC → GSE → GACR.

## Jonction après release

Après la release GSCC→GSE→GACR→F1, ne pas recréer First Touch, GSE ou GACR. Reprendre la même arrivée/session et suivre la carte maître :

`docs/control-plane/MASTER_SYSTEM_MAP.md`.

La jonction distingue obligatoirement rôle/type, authority snapshot, connection intent, entry purpose, work kind/case, entry action et mutation authority. Le routeur `entry_purpose` à deux étages reste `PLANNED_NOT_ACTIVE` tant que son gate RTE n'est pas validé ; utiliser jusque-là les politiques d'entry action et de connection intent réellement actives.
