# ENTRY ACTION ROUTER — Mandatory first question for every agent

## Purpose

A connection must resolve the macro-scenario before mutable work can be selected.

The router asks:

> Quelle action principale cet agent vient-il accomplir ?

1. `CREATE_NEW_REPOSITORY` — create a new Git repository.
2. `ADOPT_EXISTING_REPOSITORY` — add compatible governance bricks to an existing repository without replacing existing content.
3. `MAP_EXISTING_PROJECT` — map the current project and/or design a target architecture without requiring code mutation.
4. `LAB_EVOLUTION` — evolve an existing project in an isolated laboratory branch/PR while keeping the canonical branch untouched until validated merge.
5. `CONTINUE_GOVERNED_WORK` — resume normal work already governed by the repository current NEXT_ACTION/work-items.

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


### CREATE_NEW_REPOSITORY sequence

This route is special and does not ask for a generic connection intent before creation.

```text
CREATE_NEW_REPOSITORY
→ choose owner:
   chainsolutions-wealthtech
   Wealthtechinnovations
   Patricked
→ provide repository name
→ CREATE_FROM_GOVERNED_TEMPLATE
→ verify zero-touch bootstrap
→ discover infrastructure/profile state
→ HANDOFF_READY
```

The selected owner plus repository name is the explicit creation instruction for this route. Creation uses the central governed template, private visibility by default, and no manually added README/gitignore/license.
