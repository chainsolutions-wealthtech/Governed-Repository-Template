# Governed Repository Template

Template générique de gouvernance pour les dépôts de l'organisation `chainsolutions-wealthtech`.

## Objectif

Fournir dès la création d'un dépôt :
- un point d'entrée obligatoire ;
- une gouvernance explicite et machine-readable ;
- une mémoire projet persistante ;
- le Loop Engineering ;
- une discipline de non-régression ;
- une hiérarchie de sources de vérité ;
- un état courant, un historique, un TODO et une prochaine action uniques ;
- un handoff inter-agent ;
- des décisions ADR ;
- une CI de gouvernance ;
- un bootstrap déterministe.

Ce template transporte des **règles et des structures**, jamais l'historique d'un autre projet.

## Première utilisation

Après création d'un dépôt depuis ce template :

```bash
python3 scripts/initialize_governance.py --repository "chainsolutions-wealthtech/mon-projet" --project-name "Mon Projet" --project-type "application" --owner "@owner"
```

Puis compléter `PROJECT_CONTEXT.md`, `docs/ARCHITECTURE.md`, `ACCEPTANCE_CRITERIA.md` et `NEXT_ACTION.md`.

Le dépôt créé devient sa propre source de vérité. Le template ne doit jamais injecter une décision métier, une source réglementaire, un statut de production ou un historique appartenant à un autre projet.

<!-- GOVERNANCE_AUTOMATION_V2 -->
## Automatic initialization

The template includes `.github/workflows/governance-auto-bootstrap.yml`.

When started by a supported GitHub event in an instantiated repository, it automatically infers repository metadata, initializes governance, validates it, creates a bootstrap receipt and attests the initialization. Manual commands remain available as a deterministic recovery path.

## Multi-agent continuity

The repository includes a Git-only coordination layer:

- canonical-memory pointer and monotone revisions;
- exact-HEAD guard;
- agent sessions without invented provider identifiers;
- dependency/collision-safe work dispatch;
- structured checkpoints and handoff;
- new-information intake with contradiction hold-for-review.

See `docs/AUTOMATION.md`, `docs/MULTI_AGENT_COORDINATION.md` and `docs/INFORMATION_INTAKE.md`.


## Capability intent layer — V2.1

The template now separates governance from technical and infrastructure intent.

A newly created repository receives:

- `.governance/project-profile.json`: profile discovery and the optional `chainsolutions-fullstack-web` candidate;
- `.governance/infrastructure-intent.json`: server/domain/directory/database/MCP/SSH lifecycle, including resources that do not yet exist;
- `.governance/connection-intent-policy.json`: deterministic routing for agent connections.

The Chainsolutions full-stack candidate plans Node.js, Next.js + TypeScript and PostgreSQL without claiming that any of them are implemented or deployed.

Direct governed MCP access is the preferred server transport. SSH is a governed fallback. Secrets and credentials are never stored in repository governance.

A session intent is not an authorization. Context or information intake never grants code permission, and `UNKNOWN` fails closed for mutable dispatch.

See `docs/PROJECT_PROFILES.md`, `docs/INFRASTRUCTURE_BOOTSTRAP.md` and `docs/CONNECTION_INTENT.md`.


## V2.2 entry workflow layer

Every agent connection now resolves a macro entry action before mutable dispatch:

1. create a new repository;
2. adopt an existing repository additively;
3. map an existing project and/or design a target architecture;
4. evolve an existing project through an isolated lab branch or PR;
5. continue normal governed work.

The template supports organization and explicitly targeted personal-account repository scopes. Existing-project adoption is plan-first and preserves pre-existing project files by default.


## Central Governed Control Plane — V2.3

The template repository now acts as the central preparation/control plane for governed GitHub work.

Start a `[Governed Request]` issue on `chainsolutions-wealthtech/Governed-Repository-Template`. The control plane will:

1. resolve the macro entry action;
2. resolve connection intent;
3. identify/observe the target;
4. resolve owner scope and authority;
5. build a chronological preparatory execution package;
6. request one action/evidence item at a time;
7. stop on contradiction, denied authority or failed evidence;
8. emit an explicit `HANDOFF_READY` package before normal target work begins.

Generated/adopted repositories keep the central control-plane reference but are clients, not duplicate control planes.

## V2.6 governed repository connectivity

The current governed creation path includes:

- V2.6.0 — GitHub OIDC-issued ephemeral SSH certificates for read-only fallback;
- V2.6.1 — central-to-local GitHub App machine command transport;
- V2.6.2 — complete packaging of the machine-command target upgrader;
- V2.6.3 — automatic provisioning of the existing direct MCP Actions credential from the central control plane into a target repository under an exact-HEAD credential gate.

A newly governed repository therefore does not require a persistent SSH private key and, once the central control plane is configured, does not require the owner to manually copy the direct MCP token into each target repository.

Credential provisioning does not grant server WRITE authority. MCP project registration, scoped-write gates and explicit mutation approval remain separate controls.

## Source repository self-governance — V2.7

The template source is itself governed without converting distributed project-state templates into source history.

When `.template-source` exists:
- human source state lives under `docs/control-plane/`;
- machine checkpoint/handoff/task projections live under `.governance/control-plane-state/`;
- those paths are `SOURCE_ONLY`;
- client initialization removes them;
- Governance CI verifies both source completeness and client non-leakage.

This enables exact conversation/agent continuity through versioned Git state while preserving a clean generic template for newly generated repositories.

