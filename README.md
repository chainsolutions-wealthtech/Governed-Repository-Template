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
