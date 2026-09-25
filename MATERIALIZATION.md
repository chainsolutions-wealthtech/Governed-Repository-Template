# MATERIALIZATION — GitHub Template Repository

## Target repository

- Organization: `chainsolutions-wealthtech`
- Name: `Governed-Repository-Template`
- Default branch: `main`
- GitHub template repository: `true`
- Force push: `forbidden`
- History rewrite: `forbidden`

## Source of truth

The organization blueprint is:

`chainsolutions-wealthtech/.github/repository-templates/governed-repository-template/`

The standalone GitHub template repository mirrors that blueprint at repository root.

## V2 automatic bootstrap

A repository created from the template contains `.template-source` and the V2 machine-governance state.

The preferred automatic path is:

```text
repository created from template
→ governance-auto-bootstrap event
→ initialize
→ validate
→ initialization commit
→ bootstrap receipt attestation
→ second validation
→ attestation commit
→ DISCOVER_PROJECT_BASELINE
```

Supported local workflow triggers are push/main, create, workflow_dispatch and repository_dispatch type `governance-bootstrap`.

For guaranteed organization-wide zero-touch creation, a trusted organization GitHub App/orchestrator should emit the repository_dispatch event after repository creation.

## Required checks

1. template source marker exists only in the template source/repository;
2. template profile has `template_source=true` and `initialized=false`;
3. template validation passes in source mode;
4. instantiated bootstrap removes `.template-source`;
5. instantiated profile becomes initialized;
6. bootstrap receipt and canonical memory are created;
7. V2 governance validation passes;
8. repository setting `is_template=true` remains enabled.
