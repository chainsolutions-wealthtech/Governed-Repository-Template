# ENTRY ACTION ROUTER — Mandatory first question for every agent

## Purpose

A connection must resolve the macro-scenario before mutable work can be selected.

The router asks:

> Quelle action principale cet agent vient-il accomplir ?

1. `CREATE_NEW_REPOSITORY` — create a new Git repository.
2. `ADOPT_EXISTING_REPOSITORY` — add compatible governance bricks to an existing repository without replacing existing content.
3. `MAP_EXISTING_PROJECT` — map the current project and/or design a target architecture without requiring code mutation.
4. `LAB_EVOLUTION` — evolve an existing project in an isolated laboratory branch/PR while keeping the canonical branch untouched until validated merge.

If no action is supplied, the session is created/resumed with `entry_action = UNKNOWN`, returns the questionnaire, and mutable dispatch fails closed.

## Two-dimensional routing

Entry action and connection intent are distinct.

```text
ENTRY ACTION = macro workflow
CONNECTION INTENT = immediate purpose
AUTHORITY = separate permission gate
```

Examples:

- `ADOPT_EXISTING_REPOSITORY + OBSERVE` → adoption discovery only.
- `ADOPT_EXISTING_REPOSITORY + CODE_CHANGE` → still discovery-first; no mutation until the adoption plan is accepted.
- `MAP_EXISTING_PROJECT + REVIEW` → read-only architecture mapping.
- `LAB_EVOLUTION + CODE_CHANGE` → lab discovery first, branch/PR creation only after explicit project authority.
- `CREATE_NEW_REPOSITORY + WORK_REQUEST` → target owner/scope resolution and explicit create authority before creation.

No combination silently creates repositories, branches, PRs, servers, directories or deployments.
