# CANONICAL NAMESPACE AND WORK REGISTRY

Authority: `CP-NAMESPACE-001`

This authority prevents the governance programme from drifting into duplicate identifiers, parallel task lists or ambiguous multi-agent ownership.

It does **not** duplicate every task into another list.

The model is:

```text
NAMESPACE RULES
+
CANONICAL DEFINITION SOURCES
        ↓
DERIVED WORK/ID INDEX
        ↓
CI VALIDATION
```

The canonical task, decision, question, recipe and GMC sources remain where they already live.

## Additive rule

Every new item must extend existing lineage:

```text
GLOBAL ARCHITECTURE
→ PROGRAM
→ CASE / WORKSTREAM
→ PHASE
→ INTEGRATION SLOT
→ TASK
→ SUBTASK
```

New work must not silently create a parallel programme.

Before runtime binding, a new definition is expected to identify its parent/program, integration slot, dependencies and collision domain.

## Registered namespaces

The registry covers:

```text
CP-*                 canonical authorities
CP-CHECKPOINT-*      checkpoints
CP-HANDOFF-*         handoffs
CPD-*                decisions
SG-*                 self-governed historical tasks/packages
P12-S*               programme phases
C1-*                 CASE 1 tasks/subtasks
ARCH-*               architecture backlog
IDN-*                identity/session backlog
RTE-*                routing backlog
AQ-*                 adaptive questions
AQI-*                adaptive-question implementation
KBI-*                knowledge implementation
SRV-OP-*             server operation recipes
IDSEC-OP-*           identity/secret operation recipes
GMC-01..19           legacy GMC groups
GMC-G01..G19         GMC work packages
GMC-Gxx-Tyy          GMC atomic tasks
GMC-EXIT-*           GMC exit controls
GMA-*                Governance Model artifacts
EVREQ-*              evidence requirements
GACR-T-*              runtime takeover IDs
GACR-B-*              runtime Beacon IDs
GACR-C-*              runtime Correlator IDs
GACR-D-*              runtime Dispatcher/takeover wake IDs
GACR-W-*              runtime Work Offer IDs
GACR-F-*              runtime Interruption Forensics IDs
```

## Multi-agent behavior

This registry materially strengthens multi-agent work by giving every agent the same canonical namespace and semantic identity rules.

Before a mutable task is executed, the full collision model remains:

```text
ID / semantic collision
→ registry + CI

task ownership collision
→ session + claim

dependency collision
→ dependency-safe dispatch

write collision
→ single writer per collision domain

stale repository collision
→ exact HEAD guard

handoff ambiguity
→ checkpoint + structured handoff
```

Therefore `CP-NAMESPACE-001` is one necessary layer of collision prevention, not a replacement for claims, sessions or exact-HEAD reconciliation.

## Existing CPD-041 collision

A historical accidental duplicate decision identifier was found.

The decision “Domain planning is a server-scoped choice chain” is canonicalized to `CPD-047`.

Its semantic content is preserved. The old duplicate identifier is recorded in the registry reconciliation map rather than silently forgotten.

## Enforcement

The source-only validator fails closed when it finds:

- duplicate canonical decision definitions;
- duplicate task/question/implementation/recipe/GMC definition IDs;
- a canonical definition whose ID matches no registered namespace;
- overlapping namespace rules that would make a canonical ID ambiguous;
- duplicate canonical authority IDs.

Legacy missing lineage metadata is not retroactively made fatal in this first slice; future GMC-G02/G13 hardening can backfill it without destabilizing current work.


## GACR R8 runtime identifiers

`GACR-W-*` is the canonical runtime namespace for new-work offers created by the capacity-aware dispatcher.

It is distinct from:
- `GACR-D-*` takeover/wake dispatch records;
- canonical programme/task IDs such as `GMC-G01-T01`;
- claims, which remain the mutable ownership record.

Current authority chain includes `CP-AGENT-RELAY-001-R6`, `R7`, and `R8`. R8 adds F1/release and canonical-declaration gates before source-programme work offers.
