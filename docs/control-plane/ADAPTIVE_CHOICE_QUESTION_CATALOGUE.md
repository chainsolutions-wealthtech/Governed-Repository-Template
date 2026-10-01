# ADAPTIVE CHOICE QUESTION CATALOGUE

Authority: `CP-ADAPTIVE-QUESTIONS-001`

Status: **PLANNING_ONLY_NOT_RUNTIME_BOUND**

This catalogue complements the existing CREATE / ADOPT / MAP / LAB flows. It does not introduce a parallel questionnaire engine or task engine.

## Core rule

```text
OBSERVE
→ REUSE FRESH FACTS
→ ASK ONLY WHAT IS STILL UNKNOWN OR REQUIRES AN OWNER DECISION
→ ONE CHOICE QUESTION AT A TIME
→ DERIVE REQUIREMENTS / PREPARE TASKS
→ EXECUTE LATER ONLY UNDER A SEPARATE AUTHORITY
```

Answers never grant execution authority. Existing projects are adopted differentially: `REUSE | ALIGN | CREATE | MIGRATE | VERIFY | RETIRE_IF_AUTHORIZED`.

## Why AfricaFunds is the reference example

AfricaFunds shows why an existing project must not restart from a blank questionnaire. Current evidence already identifies multiple repositories including `Wealthtechinnovations/api_opcv` and `Wealthtechinnovations/front_end_opcvm`, an S2 deployment, API/frontend paths, AfricaFunds domain surfaces, and MCP-visible project/runtime context.

Those facts are reused. The system should ask only ambiguous selections and owner decisions: preserve/align governance, reuse or change paths/domains/runtime/database/deployment, MCP posture, authority envelope, tests and rollback.

## Question sequence

All answers are choices. Dynamic choices are populated from observation when possible.

### 1. Identity and topology

1. `AQ-001 project_existence`: NEW | EXISTING | HYBRID | UNKNOWN_DISCOVER
2. `AQ-002 git_provider`: GITHUB | GITLAB | MULTI_PROVIDER | UNKNOWN_DISCOVER
3. `AQ-003 repository_topology`: SINGLE_REPOSITORY | MULTI_REPOSITORY | MONOREPO | UNKNOWN_DISCOVER
4. `AQ-004 repository_members`: observed repositories | DISCOVER_MORE | NONE_OF_THESE (multi-select)

### 2. Governance posture

5. `AQ-005 environment_scope`: observed environments | PRODUCTION | STAGING | DEVELOPMENT | MULTI_ENVIRONMENT | UNKNOWN_DISCOVER
6. `AQ-006 governance_adoption_posture`: PRESERVE_AND_COMPLETE | ALIGN_WITH_TARGET_MODEL | MIGRATE_LEGACY_INCREMENTALLY | MAP_ONLY_NO_CHANGE | DECIDE_LATER
7. `AQ-007 project_profile`: observed profiles | generic | application | chainsolutions-fullstack-web | data-platform | UNKNOWN_DISCOVER
8. `AQ-008 architecture_posture`: PRESERVE_EXISTING | ALIGN_INCREMENTALLY | MIGRATE_SELECTED_PARTS | TARGET_MODEL_ONLY_NO_CHANGE | DECIDE_LATER

### 3. Infrastructure

9. `AQ-009 server_binding_mode`: EXISTING_SINGLE | EXISTING_MULTI | NONE_PLAN_NEW | UNKNOWN_DISCOVER
10. `AQ-010 server_selection`: observed servers | PLAN_NEW_SERVER | DISCOVER_MORE | DECIDE_LATER
10N. `AQ-010N production_server_selection` (CREATE_NEW): observed servers | PLAN_NEW_SERVER | DECIDE_LATER. This owner choice is required before domain planning when no server binding exists.
11. `AQ-011 deployment_path_posture`: REUSE_OBSERVED_PATHS | ALIGN_EXISTING_PATHS | PLAN_NEW_PATHS | MAP_ONLY | DECIDE_LATER
12. `AQ-012 deployment_path_selection`: observed paths | DISCOVER_MORE | PLAN_NEW_PATH (multi-select)

### 4. Domain and network

13. `AQ-013 domain_posture`: REUSE_EXISTING | CREATE_NEW | REUSE_AND_ADD | NO_DOMAIN_REQUIRED | DECIDE_LATER
14. `AQ-014 domain_selection`: observed domains | NONE_OF_THESE | DISCOVER_MORE (multi-select)
15. `AQ-015 dns_tls_posture`: PRESERVE_IF_VALID | VERIFY_AND_COMPLETE | PLAN_NEW | MAP_ONLY | DECIDE_LATER

### 5. Runtime and data

16. `AQ-016 runtime_posture`: PRESERVE_RUNTIME | ALIGN_RUNTIME | MIGRATE_RUNTIME | MAP_ONLY | DECIDE_LATER
17. `AQ-017 runtime_selection`: observed runtimes/process managers | DISCOVER_MORE | NONE (multi-select)
18. `AQ-018 database_posture`: REUSE_EXISTING | CREATE_NEW | REUSE_AND_EXTEND | NO_DATABASE | DISCOVER_FIRST | DECIDE_LATER
19. `AQ-019 database_selection`: observed databases | NONE_OF_THESE | DISCOVER_MORE (multi-select)
20. `AQ-020 external_system_posture`: REUSE_EXISTING_INTEGRATIONS | VERIFY_AND_KEEP | REPLACE_SELECTED | ADD_NEW | NONE | DECIDE_LATER

### 6. Delivery and operations

21. `AQ-021 ci_cd_posture`: PRESERVE_IF_VALID | ALIGN_INCREMENTALLY | CREATE_IF_MISSING | MAP_ONLY | DECIDE_LATER
22. `AQ-022 deployment_strategy`: PRESERVE_OBSERVED | GIT_TO_SERVER_GOVERNED | CONTAINER_GOVERNED | PLESK_GOVERNED | NO_DEPLOYMENT | DECIDE_LATER
23. `AQ-023 observability_posture`: PRESERVE_EXISTING | VERIFY_AND_COMPLETE | ADD_MINIMUM_HEALTH | ADD_FULL_MONITORING | NONE | DECIDE_LATER
24. `AQ-024 backup_rollback_posture`: PRESERVE_EXISTING | VERIFY_AND_COMPLETE | REQUIRE_BEFORE_WRITE | NOT_APPLICABLE | DECIDE_LATER

### 7. MCP and access

25. `AQ-025 mcp_linkage`: REUSE_EXISTING_BINDING | CREATE_BINDING | VERIFY_EXISTING_BINDING | NO_MCP | DECIDE_LATER
26. `AQ-026 mcp_transport`: DIRECT_MCP_TOKEN | SSH | BOTH | NO_MCP
27. `AQ-027 mcp_scope`: PROJECT_ONLY | PROJECT_AND_RUNTIME | FULL_GOVERNED_MAPPING | NO_DISCOVERY | DECIDE_LATER

`BOTH` keeps the canonical dual-ready smart-routing meaning: configure both routes, select one route per operation, never require coupled execution.

### 8. Authority and security

28. `AQ-028 authority_envelope`: READ_ONLY | SCOPED_GIT_WRITE | SCOPED_RUNTIME_WRITE | SCOPED_DEPLOY | SCOPED_FULL_LIFECYCLE | PER_ACTION_APPROVAL | DECIDE_LATER
29. `AQ-029 secret_provisioning`: REUSE_EXISTING_SECURE_SOURCE | OIDC_OR_SHORT_LIVED_IDENTITY | GITHUB_OR_GITLAB_SECRET | SERVER_SECRET_STORE | NO_SECRET_REQUIRED | DECIDE_LATER
30. `AQ-030 data_classification`: PUBLIC | INTERNAL | CONFIDENTIAL | SENSITIVE_PERSONAL | REGULATED | MIXED | DECIDE_LATER
31. `AQ-031 compliance_profile`: NONE | PERSONAL_DATA | FINANCIAL_SERVICES | KYC_AML | PCI_LIKE | MULTI_PROFILE | DECIDE_LATER

### 9. Quality and execution

32. `AQ-032 test_posture`: PRESERVE_EXISTING_TESTS | ADD_UNIT_ONLY | ADD_UNIT_AND_INTEGRATION | ADD_FULL_E2E | MAP_ONLY | DECIDE_LATER
33. `AQ-033 gap_action_policy`: REUSE_ALIGN_CREATE_VERIFY | PREPARE_ONLY | PREPARE_AND_AUTO_EXECUTE_WITHIN_AUTHORITY | MAP_ONLY | DECIDE_LATER
34. `AQ-034 execution_timing`: PREPARE_ONLY_NOW | AUTO_WHEN_DEPENDENCIES_AND_AUTHORITY_READY | EXPLICIT_APPROVAL_PER_MUTATION | HOLD_ALL_EXECUTION

## AfricaFunds replay logic

Fresh observations can auto-resolve factual questions:

```text
project_existence   = EXISTING
git_provider        = GITHUB
repository_topology = MULTI_REPOSITORY
environment_scope   = PRODUCTION
server_binding_mode = EXISTING_SINGLE
server              = S2
```

The first useful owner question is then a choice over observed repositories:

```text
AQ-004 — Quels repositories observés appartiennent à AfricaFunds ?
[ ] Wealthtechinnovations/api_opcv
[ ] Wealthtechinnovations/front_end_opcvm
[ ] DISCOVER_MORE
[ ] NONE_OF_THESE
```

Then the next decision becomes:

```text
AQ-006 — Comment traiter la gouvernance existante ?
( ) PRESERVE_AND_COMPLETE
( ) ALIGN_WITH_TARGET_MODEL
( ) MIGRATE_LEGACY_INCREMENTALLY
( ) MAP_ONLY_NO_CHANGE
( ) DECIDE_LATER
```

The same pattern continues for paths, domains, runtime, database, CI/CD, MCP and authority.

## Incremental implementation plan

- `AQI-01` catalogue + invariants: implemented in this slice.
- `AQI-02` pure no-side-effect question planner: implemented in this slice.
- `AQI-03` unit/E2E fixture tests for NEW and EXISTING: implemented in this slice.
- `AQI-04` later bind selected questions into the existing local-entry state machine without replacing it.
- `AQI-05` later project derived requirements into the existing Loop Engineering task graph.
- `AQI-06` later add GitHub/GitLab dynamic-choice adapters.
- `AQI-07` later add AuthorityEnvelope-driven autonomous execution.
- `AQI-08` later cross-case E2E validate question reuse/no-regression behavior.

The existing CASE 1 unique executable task is not replaced by this planning work.

## Fresh-project infrastructure ordering

For a fresh project with no existing infrastructure binding, the canonical sequence is:

```text
read-only discovery
→ observed candidate servers
→ owner chooses production server
→ server-scoped domain choices
→ domain intent / later domain decomposition
→ derived resource/capability graph
```

A discovered server candidate is not auto-selected for a new project because the production target is an owner decision. The answer prepares the project model only and grants no mutation authority.
