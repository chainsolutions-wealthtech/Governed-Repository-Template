# MATERIALIZATION — GitHub Template Repository

## Target repository

- Organization: `chainsolutions-wealthtech`
- Name: `Governed-Repository-Template`
- Default branch: `main`
- GitHub template repository: `true`
- Visibility: owner decision at creation time
- Initialize with README: `false` (the blueprint already contains one)
- Additional branch creation: `false` during materialization
- Force push: `forbidden`
- History rewrite: `forbidden`

## Source of truth

Copy the complete contents of:

`chainsolutions-wealthtech/.github/repository-templates/governed-repository-template/`

to the repository root without carrying the parent `repository-templates/` path.

The source commit must be recorded in the first commit message of the materialized template.

## Required post-materialization checks

1. root contains `00_START_HERE.md`, `GOVERNANCE.md`, `AGENTS.md`, `SOURCE_OF_TRUTH.md`;
2. `.template-source` is present in the template repository;
3. `.governance/profile.json` has `template_source=true` and `initialized=false`;
4. `python3 scripts/validate_governance.py` returns PASS in template-source mode;
5. `.github/workflows/governance-ci.yml` is enabled;
6. repository setting `is_template=true` is confirmed through GitHub repository settings/API;
7. no Regulatory/UMOA/BCEAO/CENTIF/OPCVM project state is present.

## Instantiated repository bootstrap

After creating a new project from the GitHub template, run:

```bash
python3 scripts/initialize_governance.py \
  --repository "chainsolutions-wealthtech/<repo>" \
  --project-name "<project name>" \
  --project-type "<project type>" \
  --owner "<owner>"
```

The bootstrap removes `.template-source`, resolves placeholders and changes the governance profile into instance mode.
