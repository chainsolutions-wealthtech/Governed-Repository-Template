# AGENTS — Règles pour tout agent, humain ou automatisation

Ce fichier s'applique à toute intervention sur `{{REPOSITORY}}`.

## Démarrage obligatoire

1. lire `00_START_HERE.md` et l'ordre de lecture ;
2. confirmer dépôt, branche, HEAD et état du worktree ;
3. lire les fichiers directement concernés ;
4. rechercher les travaux existants ;
5. établir la baseline et les risques ;
6. vérifier les permissions et contraintes ;
7. sélectionner une action compatible avec `NEXT_ACTION.md`.

## Continuité

Il est interdit de recommencer le projet sans décision documentée, dupliquer une autorité existante, changer un contrat stable sans migration, supprimer une preuve utile ou contourner un gate de sécurité ou d'approbation.

## Zéro régression

Avant modification : identifier consommateurs, dépendances, données, contrats, tests et sorties affectés.

Après modification : exécuter les contrôles disponibles, comparer à la baseline, corriger toute régression introduite, puis vérifier à nouveau.

## Handoff

Toute interruption doit laisser le dépôt reprenable par un autre agent uniquement à partir des autorités versionnées, sans dépendre de la mémoire de la conversation.

<!-- GOVERNANCE_AUTOMATION_V2 -->
## Machine pre-write observation

In an initialized repository, run:

```bash
python3 scripts/governance_agent.py observe
```

before selecting mutable work.

When multiple agents cooperate, create/resume a governed repository session and dispatch only dependency-safe, collision-safe work. A `HEAD_MOVED` result forbids writing until intervening changes are reconciled.

New information must be registered/reconciled through the intake model. A contradiction is held for review and never becomes canonical automatically.


## Connection intent

When starting or resuming a governed session, classify the purpose of the connection before mutable dispatch.

Example:

```bash
python3 scripts/governance_agent.py session-start \
  --agent "<agent>" \
  --provider "<provider>" \
  --connection-ref "<ref>" \
  --intent CODE_CHANGE
```

Use `CONTEXT_INTAKE` or `INFORMATION_INTAKE` when the connection exists to add context or evidence rather than to code. `UNKNOWN` is the safe default and blocks mutable dispatch until resolved.

An intent never grants infrastructure, production, secret, financial, legal or destructive authority.


## Mandatory entry action

Before mutable dispatch, resolve the macro workflow:

```bash
python3 scripts/governance_agent.py entry-actions
```

Then start/resume the session with `--entry-action`.

The structural actions are `CREATE_NEW_REPOSITORY`, `ADOPT_EXISTING_REPOSITORY`, `MAP_EXISTING_PROJECT`, and `LAB_EVOLUTION`. `CONTINUE_GOVERNED_WORK` preserves normal work on an already governed repository.

`ADOPT_EXISTING_REPOSITORY` and `MAP_EXISTING_PROJECT` start read-only. `LAB_EVOLUTION` cannot dispatch mutable work from the canonical branch. Missing entry action fails closed.
