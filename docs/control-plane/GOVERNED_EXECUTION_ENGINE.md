# GOVERNED EXECUTION ENGINE

Authority: `CP-EXECUTION-001`

The Control Plane now has one governed execution adapter for GitHub and production/server operations.

It extends the existing Loop Engineering model. It is **not** a second task engine.

## Execution chain

```text
reviewed project decision / task
→ secret-free execution package
→ exact source HEAD
→ exact target HEAD when repository-scoped
→ authority grant
→ capability resolution
→ credential reference resolution
→ preflight
→ execute
→ verify
→ rollback when safe
→ redacted receipt
```

Dry-run is the default.

## Registered intents

### Server / production — 15

- CREATE_PROJECT_DIRECTORY
- CREATE_SUBDOMAIN
- CREATE_NEW_DOMAIN_BINDING
- ALLOCATE_APPLICATION_PORT
- CONFIGURE_REVERSE_PROXY
- PROVISION_TLS
- CREATE_DATABASE
- BIND_REPOSITORY_TO_SERVER_PROJECT
- DEPLOY_APPLICATION
- CONFIGURE_ENV_AND_SECRETS
- CONFIGURE_PROCESS_OR_SERVICE
- CONFIGURE_SCHEDULED_JOB
- CONFIGURE_OBSERVABILITY
- CONFIGURE_BACKUP_AND_ROLLBACK
- PRODUCTION_ATTESTATION

### Identity / secrets — 10

- DISCOVER_CREDENTIAL_REQUIREMENT
- MINT_GITHUB_APP_INSTALLATION_TOKEN
- PROVISION_GITHUB_SECRET
- MINT_EPHEMERAL_SSH_CERTIFICATE
- CREATE_OR_BIND_SERVER_APPLICATION_SECRET
- CREATE_DATABASE_CREDENTIAL
- CREATE_DNS_AUTOMATION_CREDENTIAL
- ROTATE_CREDENTIAL
- REVOKE_CREDENTIAL
- VERIFY_SECRET_OR_CREDENTIAL_WITHOUT_READBACK

### GitHub administration / delivery — 14

- GITHUB_CREATE_REPOSITORY_FROM_TEMPLATE
- GITHUB_CREATE_BRANCH
- GITHUB_UPSERT_FILE
- GITHUB_CREATE_PULL_REQUEST
- GITHUB_MERGE_PULL_REQUEST
- GITHUB_CONFIGURE_BRANCH_PROTECTION
- GITHUB_CONFIGURE_RULESET
- GITHUB_CONFIGURE_WEBHOOK
- GITHUB_CONFIGURE_ENVIRONMENT
- GITHUB_SET_ACTIONS_VARIABLE
- GITHUB_DISPATCH_WORKFLOW
- GITHUB_CREATE_DEPLOYMENT
- GITHUB_UPDATE_REPOSITORY_SETTINGS
- GITHUB_ADD_COLLABORATOR

Total: **39 intents**.

## GitHub execution

GitHub operations are implemented with explicit builders. A package cannot supply an arbitrary URL or HTTP method.

The engine builds the known endpoint, validates the parameters, executes with an ephemeral target-owner GitHub App token and performs a post-operation verification.

Examples:

```text
GITHUB_CREATE_BRANCH
→ exact repository HEAD guard
→ POST governed ref
→ GET ref
→ SHA must match
```

```text
GITHUB_MERGE_PULL_REQUEST
→ exact repository HEAD guard
→ read PR
→ PR head SHA must equal approved SHA
→ merge
→ re-read PR
→ merged=true
```

Secrets use `gh secret set` with values supplied only from runtime secret references. The value is never read back or written to a receipt.

## Server execution

Server operations execute through the current MCP capability surface.

Each MCP step in a package declares:

```json
{
  "backend": "MCP_DIRECT",
  "capability": "DEPLOYMENT_RUNTIME_CHANGE",
  "tool": "deploy_project_s2",
  "arguments": {
    "project": "brvmchainsolution"
  }
}
```

Before network execution the engine checks:

1. the capability exists in the latest canonical MCP snapshot;
2. the tool is a candidate for that capability;
3. its project scope matches;
4. all required arguments match the live MCP tool contract;
5. mutation authority is present;
6. an explicit execute step is versioned in the package.

No mutation is auto-selected merely because one MCP tool exists.

## Current MCP coverage

The execution engine is complete, but **the current MCP implementation does not yet expose every generic server mutation capability**.

For example, the latest canonical capability snapshot still marks generic:

- SERVER_FILESYSTEM_CHANGE
- WEB_HOSTING_CHANGE
- TLS_CHANGE

as not exposed.

Other future recipe requirements such as DOMAIN_DNS_CHANGE, DATABASE_CHANGE, SECRET_PROVISIONING, SERVER_RUNTIME_CHANGE, SERVER_SCHEDULER_CHANGE, OBSERVABILITY_CHANGE and BACKUP_RECOVERY_CHANGE also need explicit MCP capability surfaces before the corresponding generic recipe can execute.

This is not bypassed.

The engine returns a machine-readable `MISSING_CAPABILITY` / `MISSING_CAPABILITY_BINDING` result. A later governed process can then prepare a bounded MCP capability request only when that operation is actually needed.

Existing project-scoped surfaces such as `deploy_project_s2` can already be bound when the project is in the MCP allowlist.

## Credentials

Credential values never belong in execution packages.

Allowed references include:

```text
env:GOVERNED_MCP_AUTH_TOKEN
env:AN_AUTHORIZED_SECRET
runtime:MINTED_GITHUB_APP_TOKEN
generated:32
```

Generated values exist only in process memory.

The execution receipt contains metadata and verification evidence, not credential values.

## Central workflow

`.github/workflows/governed-execution.yml` is manual-only.

It requires:

- canonical `main`;
- exact expected source HEAD;
- a package committed under
  `.governance/control-plane-state/execution-packages/`;
- dry-run validation first;
- explicit `execute=true` for side effects.

The workflow mints the least relevant GitHub App token class it can derive from the intent and provides OIDC/MCP credentials only at runtime.

No arbitrary JSON is accepted from the workflow UI.

## Execution packages

Schema:

`schemas/governed-execution-package.schema.json`

A mutation package contains an explicit authority block and may reference an exact target repository HEAD.

Example shape:

```json
{
  "schema_version": "1.0.0",
  "operation_id": "PROJECT-DEPLOY-001",
  "intent": "DEPLOY_APPLICATION",
  "project_id": "project-id",
  "repository": "owner/repository",
  "expected_head": "40-hex-sha",
  "server_id": "S2",
  "authority": {
    "approved": true,
    "grants": ["SCOPED_DEPLOY"],
    "scope": {"project_id": "project-id", "server_id": "S2"},
    "decision_ref": "OWNER-DECISION-ID"
  },
  "parameters": {},
  "bindings": {
    "capabilities": {},
    "credentials": {
      "MCP_AUTH_TOKEN": {"secret_ref": "env:GOVERNED_MCP_AUTH_TOKEN"}
    },
    "steps": {
      "preflight": [],
      "execute": [],
      "verify": [],
      "rollback": []
    }
  }
}
```

A package with a plaintext token/password/private key is rejected.

## Failure semantics

Typical fail-closed results:

- EXECUTION_AUTHORITY_NOT_APPROVED
- EXECUTION_AUTHORITY_GRANT_MISSING
- HEAD_MOVED
- MISSING_CAPABILITY
- MISSING_CAPABILITY_BINDING
- UNMAPPED_TOOL
- CAPABILITY_PROJECT_SCOPE_MISMATCH
- MCP_TOOL_ARGUMENT_REQUIRED
- MCP_TOOL_ARGUMENT_UNKNOWN
- MCP_TOOL_ARGUMENT_ENUM
- PACKAGE_CONTAINS_SECRET_VALUE

If a mutation happened and verification then fails, configured rollback steps run. If rollback also fails or is not safely available, the receipt becomes `FAILED_MANUAL_RECOVERY_REQUIRED`.

## Ekyc implication

When Ekyc decisions later resolve production server/domain/runtime, the system can generate execution packages for the entire GitHub + production chain.

If Ekyc selects S2 + a new subdomain, the domain/vhost/TLS/filesystem recipes will remain blocked until the corresponding generic MCP capabilities are exposed. The engine already knows exactly which capabilities are missing; it must not create broad or speculative MCP intake.

## No-regression boundary

- existing Loop Engineering remains canonical;
- current CASE 1 chronology remains canonical;
- Ekyc is not mutated by this implementation;
- Patricked-code/MCP is not modified;
- execution is source-control-plane only;
- missing MCP capabilities remain explicit blockers rather than shortcuts.

## Knowledge-driven package compiler

`scripts/governed_execution_package_compiler.py` converts a project requirement into the existing secret-free execution package.

It consumes:
- the execution registry;
- the canonical MCP capability snapshot;
- the server operation model;
- optional transient S1/S2 inventory from KBI-04C;
- optional transient GitHub secret metadata from KBI-04J.

The compiler may derive deterministic facts and bindings, but it never grants authority and never creates broad MCP intake.

Current deterministic bindings include:
- an already registered S2 project → `deploy_project_s2` with `git_status_project_s2` preflight/verification;
- S1/S2 production attestation → bounded read-only disk/runtime/domain probes.

For an unregistered project such as the current fresh Ekyc case, deployment remains blocked with `PROJECT_NOT_IN_CURRENT_MCP_DEPLOY_REGISTRY` until a governed registration capability exists or is explicitly provided.

## P1 — Réexamen versionné de HOLD_FOR_REVIEW sur la même demande GR

Cette capacité ne transforme **jamais** un accord de maintenance propriétaire, un compte GitHub disposant de `push`, ni une PR fusionnée en autorisation GACR, claim de travail, lease, admission GSCC ou droit de fusion.

Un HOLD d'autorité LAB précédemment refusé peut être **réexaminé sur la même issue gouvernée**, sans nouvelle GR et sans effacement du refus, uniquement si :
- l'état machine live reste `HOLD_FOR_REVIEW`, phase `AUTHORITY`, `lab_authority=false`, raison `lab branch/PR authority denied` ;
- aucun plan préparatoire ni preuve d'exécution préexistante n'exige de réconciliation supplémentaire ;
- la commande provient du compte propriétaire `Wealthtechinnovations`, avec auteur de commentaire et sender GitHub correspondants, ainsi qu'une association validée par l'événement GitHub ;
- la révision attendue correspond à la révision actuellement relue depuis l'issue et le HEAD fourni correspond à l'observation fraîche `main` ;
- une à huit références `github-pr:<numéro>` sont vérifiées **fusionnées sur `main`** par appels GitHub authentifiés.

Syntaxe de la commande **sur l'issue d'origine** :

```text
/governed-review-hold {"expected_revision":9,"expected_head":"<SHA40 ACTUEL>","evidence_refs":["github-pr:316","github-pr:317","github-pr:318"],"reason":"Réexamen propriétaire après corrections fusionnées et vérifiées."}
```

La transition ajoute un élément immuable dans `hold_review_history` (ancienne révision, refus et baseline, acteur, HEAD, PR de preuve, justification). Elle supprime **uniquement de la projection courante** le précédent `lab_authority=false` et la baseline périmée ; la phase suivante est une **nouvelle observation HEAD** `target_observation`, validée également par l'API GitHub, puis une nouvelle réponse propriétaire explicite à `lab_authority`. Les réponses d'autorité et d'approbation du plan exigent également l'auteur propriétaire authentifié. Le refus original demeure présent dans l'historique.

**Ce mécanisme n'exécute aucune étape PREP, n'affecte aucun agent, n'accorde aucun claim, n'ouvre aucun LAB, ne déploie rien et ne crée pas de droit de fusion.** Les opérations mutantes exigent toujours l'assignation gouvernée, le claim unique, l'état HEAD frais, le grant et les contrôles distincts selon le périmètre. Un refus répété revient à HOLD et conserve la première décision. Si l'issue a changé de révision/HEAD, la commande échoue sans réécrire l'état.

Règle d'exploitation : ne jamais envoyer une valeur `lab_authority=true` sans preuve d'une nouvelle réponse authentifiée du propriétaire ; une remise en questionnaire n'est pas un déblocage automatique.

## GR-000284 — Supersession d'un plan LAB périmé lorsqu'une branche est déjà fusionnée

Le réexamen P1 du HOLD sur la demande originale peut conduire à un plan préparatoire devenu inexécutable : par exemple, PREP-003 demande de créer une branche qui **existe déjà** et dont la PR a été fusionnée. Une preuve `created=true` émise aujourd'hui serait fausse. La création à nouveau ou la réécriture forcée est interdite.

La commande sur **la même issue gouvernée** est :

```text
/governed-reconcile-plan {"expected_revision":12,"expected_head":"<HEAD-main-observé>","reason":"Plan original devenu périmé ; branche historique et PR fusionnée à réutiliser en lecture seule."}
```

Seul le propriétaire GitHub authentifié `Wealthtechinnovations` est admis pour cette transition. Avant mutation du marqueur d'issue, le moteur relit la révision exacte, `main`, la branche historique `lab/codeagent-gscc-f1-q12-renewal-284` et **PR #316 fusionnée sur main** via GitHub. La voie est limitée à GR-000284, phase `PLAN_READY / PLAN_APPROVAL`, absence d'approbation du plan et de toute exécution. Elle exige que l'ancienne décision de refus reste dans `hold_review_history` et que le réexamen ait reçu une nouvelle réponse propriétaire `lab_authority=true`. Une deuxième réconciliation est admise uniquement avant toute approbation/exécution, si `main` a avancé.

L'ancien plan, ses exigences et sa révision ne sont jamais écrasés historiquement : `plan_reconciliation_history` reçoit une supersession versionnée (ancien plan complet, nouveau plan, HEAD et PR/branche attestés, acteur, justification et interdiction d'autorité). Le nouveau plan a quatre étapes **en lecture seule** : confirmer HEAD, vérifier PR #316, vérifier la branche **déjà existante**, contrôler la corrélation et l'absence de nouvelle écriture. Aucun `TARGET_BRANCH_CREATE` n'y figure.

Après cette transition, `plan_approved` demeure absent : une **nouvelle approbation propriétaire explicite** est requise. Les preuves de chacune des étapes doivent correspondre aux lectures GitHub fraîches du HEAD, de la branche et de la PR, et à la forme exacte de l'étape courante. Le Handoff n'autorise jamais `BEGIN_LAB_EVOLUTION` pour cette branche historique ; il oriente vers la **vérification LIVE Q12/F1 d'une arrivée réelle**, sous session GACR et grant distincts. Une approbation ou des tests unitaires ne peuvent ni créer claim/lease, ni simuler challenge/receipt, ni libérer F1.

Cette réparation sur #284 est **distincte** de la demande expérimentale CHAINFLOW #302 et de sa branche cible `lab/chainflow-live-poc`.
