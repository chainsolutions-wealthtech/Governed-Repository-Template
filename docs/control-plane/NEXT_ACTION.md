# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_12_I_A_FIX_DYNAMIC_CLIENT_UPGRADER
STATE = IN_PROGRESS
```

## Objective

Fix the **framework product** so the governed client upgrade mechanism can actually distribute the current Template release safely before any external pilot mutation.

Product repository:

`chainsolutions-wealthtech/Governed-Repository-Template`

## Newly discovered generic defects

1. `scripts/control_plane_upgrade_local_entry.py` is hard-coded to V2.8.3.
2. Its distribution surface does not include `scripts/test_connection_intent.py`, so the V2.8.4 fix cannot reach a client.
3. The copied client Governance CI contains a source-only control-plane database materialization step even though clients correctly do not contain `.governance/control-plane-db`.

## Required product fix

1. derive upgrade version from `.governance/TEMPLATE_MANIFEST.json`;
2. remove version-specific status/comment/commit hard-coding;
3. distribute the generic connection-intent runtime/test surface required by client CI;
4. keep project work-items, sessions, answers and business state untouched;
5. make the source-only database materialization CI step skip cleanly on clients;
6. add regression assertions covering the upgrade contract;
7. obtain full Template Governance CI before external validation.

## Product / pilot rule

No pilot mutation is allowed until this Template task is complete.

```text
DISCOVER GENERIC DISTRIBUTION GAP
→ FIX TEMPLATE
→ TEMPLATE CI / RELEASE
→ ONLY THEN VALIDATE PILOT
```
