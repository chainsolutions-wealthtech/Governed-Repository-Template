# CONTROL PLANE NEXT ACTION

```text
NEXT_ACTION = C1_13_I_A_FIX_BOTH_SMART_ROUTING_SEMANTICS
STATE = GENERIC_FRAMEWORK_CORRECTION
PARENT = P12_S5_SECOND_FRESH_REPOSITORY_E2E
```

## Owner correction

`BOTH` means **both transport paths are configured and available for intelligent selection**, not that DIRECT and SSH must execute together.

Canonical semantics:

```text
BOTH = DUAL_READY_SMART_ROUTING

operation
→ choose one appropriate ready route
   ├── DIRECT MCP
   └── SSH governed route
→ execute selected route
→ use alternate only if needed / selected / separately attested
```

A successful selected route satisfies the current operation. Alternate-route readiness is independent.

## Why this changes Ekyc

Ekyc run `36644247227` already produced an explicitly authorized `DIRECT MCP = PASS`. The old implementation then forced SSH in the same `BOTH` discovery and converted the whole run into `SSH_PROFILE_MISMATCH`.

That is now classified as a generic framework semantic defect, not a reason to ask the owner to approve another coupled discovery.

The Template correction must:

1. stop automatic DIRECT+SSH coupled execution for `BOTH`;
2. record route selection and fallback explicitly;
3. let one successful selected route satisfy discovery;
4. keep the alternate route configured with independent readiness;
5. stop forced rediscovery when an alternate route becomes available;
6. migrate legacy Ekyc state by reusing the already-authorized DIRECT PASS;
7. leave corrected SSH configured as an alternate route to attest only when needed.

## Exact Ekyc state before migration

```text
repository = Patricked-code/Ekyc
HEAD = 4d552458afab32df12aaafd6c7290fab6246d96b
issue = Ekyc#1
revision = 38
current discovery = null
historical run 36644247227:
  DIRECT = PASS
  SSH = SSH_PROFILE_MISMATCH
corrected SSH profile = persisted
baseline = not applied
```

No Ekyc-specific patch is authorized. Fix Template → test → merge → governed upgrade → verify migrated Ekyc state.

## Safety boundary

- Do not ask for redundant coupled-discovery approval.
- Do not patch Ekyc directly.
- Do not mutate Patricked-code/MCP.
- Do not weaken discovery authority.
- P12-S6 and GMC remain downstream of P12-S5.
