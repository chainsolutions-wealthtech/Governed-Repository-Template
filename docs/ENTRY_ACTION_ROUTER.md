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

**Important :** après un F1/RELEASE valide, choisir une action ne nécessite **pas** qu'une tâche ait déjà été attribuée. La session n'est pas automatiquement orientée vers GACR Dispatch : les cas de découverte, de création d'une branche/LAB et de planification sont des voies distinctes. Le dispatcher R7/R8 reste optionnel pour l'entrée, et ses offres/claims ne concernent que le travail gouverné qui lui est soumis.

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
- `LAB_EVOLUTION` après F1 → branch/LAB setup sur le HEAD observé, **sans offre ni claim GACR Dispatch préalable**. Vérification obligatoire des permissions GitHub réelles de l'exécuteur, de l'autorisation du périmètre et des protections de branche. Une mutation de contenu ultérieure respecte séparément l'ownership des tâches et les règles de collision.
- `CONTINUE_GOVERNED_WORK` → l'agent peut explicitement rejoindre l'attribution GACR et son flux offre → acceptation → claim ; cela n'est pas imposé aux autres scénarios.
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
→ choose visibility: private / public
→ CREATE_FROM_GOVERNED_TEMPLATE via authorized GitHub executor
→ verify zero-touch bootstrap
→ discover infrastructure/profile state
→ HANDOFF_READY
```

The selected owner, repository name and explicit visibility are the creation instruction for this route. Creation uses the central governed template and no manually added README/gitignore/license. The display choice `Patricked` resolves to GitHub owner `Patricked-code`.
