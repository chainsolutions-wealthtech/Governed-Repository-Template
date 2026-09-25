# NEXT_ACTION — Point de reprise unique

```text
NEXT_ACTION = INITIALIZE_PROJECT_GOVERNANCE
STATE = AUTOMATIC_OR_RECOVERY_REQUIRED
```

## Action

The preferred path is automatic: `.github/workflows/governance-auto-bootstrap.yml` initializes a repository instance when a supported GitHub event is received.

If automatic triggering is unavailable, use `workflow_dispatch` or the deterministic manual fallback `scripts/initialize_governance.py`.

## Automatic exit

After successful bootstrap, this file is rewritten to:

```text
NEXT_ACTION = DISCOVER_PROJECT_BASELINE
STATE = READY
```

## Done when

- no unresolved template placeholder remains;
- bootstrap receipt exists;
- canonical memory is initialized;
- governance validation is GREEN;
- project-profile and infrastructure-intent projections are present;
- `WORK-DISCOVER-001` is READY;
- next action is `DISCOVER_PROJECT_BASELINE`, including profile and infrastructure discovery.
