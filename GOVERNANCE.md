# GOVERNANCE — Contrat supérieur du dépôt

> Dépôt : `{{REPOSITORY}}`  
> Projet : `{{PROJECT_NAME}}`  
> Propriétaire : `{{OWNER}}`

## Contrat

```text
CANONICAL_WORK_BRANCH = {{CANONICAL_BRANCH}}
FORCE_PUSH = FORBIDDEN
HISTORY_REWRITE = FORBIDDEN
IMPROVEMENT_ONLY = REQUIRED
ZERO_REGRESSION = REQUIRED
PERSISTENT_MEMORY = REQUIRED
LOOP_ENGINEERING = REQUIRED
READ_EXISTING_BEFORE_CREATE = REQUIRED
DOCUMENT_ROLE_ANALYSIS = REQUIRED
DELETE_WITHOUT_PROOF = FORBIDDEN
SIMPLIFY_WITH_INFORMATION_LOSS = FORBIDDEN
VERIFY_BEFORE_WRITE = REQUIRED
VERIFY_AFTER_WRITE = REQUIRED
NEW_BRANCH_CREATION = OWNER_EXPLICIT_ONLY
NORMAL_WORK_PR = PROJECT_DEFINED
```

## Autorité

En cas de contradiction :
1. sécurité, loi, politique supérieure et autorisation explicite ;
2. `SOURCE_OF_TRUTH.md` ;
3. décision durable la plus récente dans `docs/DECISIONS.md` / `docs/adr/` ;
4. règle la plus restrictive compatible avec les autorités supérieures ;
5. ne jamais trancher silencieusement une contradiction structurante.

## Amélioration sans régression

Une modification valide doit améliorer, corriger, renforcer, compléter, sécuriser, documenter ou rendre plus vérifiable l'existant.

Interdictions : réécrire l'histoire, forcer un push, remplacer silencieusement une décision, casser un contrat sans migration, supprimer un test pour faire passer une modification, inventer une validation, supprimer une information utile ou créer une source de vérité concurrente.

## Mémoire persistante

La mémoire du projet est versionnée dans le dépôt. Une conversation, un agent ou une session ne remplace jamais cette mémoire.

## États

`SPECIFIED → IMPLEMENTED → TESTED → CONFIGURED → ACTIVATED → DEPLOYED → PRODUCTION_VERIFIED`

Aucune étape ultérieure ne doit être déduite d'une étape antérieure sans preuve.

## Opérations sensibles

Toute opération irréversible, destructive, financière, réglementaire, juridique, de production, de secret, de permission élevée ou d'infrastructure critique exige l'autorité correspondante et les contrôles adaptés. Le template ne confère jamais cette autorisation.

<!-- GOVERNANCE_AUTOMATION_V2 -->
## Automation and coordination invariants

```text
OBSERVED_STATE_NE_ASSUMED_STATE = REQUIRED
HEAD_MOVED_RECONCILIATION = REQUIRED
SINGLE_WRITER_PER_COLLISION_DOMAIN = REQUIRED
UNKNOWN_PROVIDER_IDENTITY = NULL_NEVER_INVENT
INTAKE_NE_CANONICAL_MEMORY = REQUIRED
INTAKE_NE_WORK_ITEM = REQUIRED
CONTRADICTION = HOLD_FOR_REVIEW
AUTOMATION_FAIL_CLOSED = REQUIRED
RUNTIME_AUTHORITY_INFERENCE = FORBIDDEN
PLANNED_NE_IMPLEMENTED = REQUIRED
INFRASTRUCTURE_FACTS_REQUIRE_OBSERVATION = REQUIRED
CREDENTIALS_IN_REPOSITORY = FORBIDDEN
CONNECTION_INTENT_FAIL_CLOSED = REQUIRED
CONTEXT_INTAKE_NE_CODE_PERMISSION = REQUIRED
INTENT_NE_AUTHORITY = REQUIRED
```

The generic automation layer is a repository-local coordination projection. It does not create runtime locks, deployment authority, production permission or a second source of truth.


## Technical and infrastructure intent

The generic governance core does not assert a framework, database, server, domain or deployment merely because the repository exists.

A project profile may record planned defaults. Infrastructure may remain unknown, missing or unprovisioned. These are valid governed states.

`DIRECT_MCP` is the preferred governed server access transport when available. `SSH` is a fallback transport, not a source of authority. Any server mutation or provisioning still requires the relevant authorization.
