# DEFINITION_OF_DONE

A work item is not done unless, when applicable:
- existing context and impacted files were read;
- baseline was captured;
- impact and regression risk were analyzed;
- implementation remained compatible or migration was explicit;
- tests and available validations passed;
- regressions introduced were corrected;
- limitations and blockers were recorded;
- persistent memory was synchronized;
- remote state was verified;
- the next action was updated or the objective was explicitly closed;
- no success, deployment, approval or external validation was invented.


## Control plane completion

A central governed request is complete only when either:

- it is explicitly held/stopped with a documented reason; or
- all approved preparatory actions have PASS evidence and the request emits `HANDOFF_READY`.

`PLAN_READY`, issue creation, repository discovery, branch creation, adoption planning or target architecture design alone do not constitute completion.
