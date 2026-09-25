# INFORMATION_INTAKE — New information coherence

## Absolute distinction

```text
INTAKE != CANONICAL_MEMORY != WORK_ITEM
```

New information is evidence to evaluate. It is not canonical merely because an agent received it.

## Lifecycle

```text
RECEIVED
→ EVALUATED
→ RECONCILED | ARCHIVED_NO_EFFECT | HOLD_FOR_REVIEW | REJECTED
```

## Dispositions

- `DUPLICATE`
- `COMPLEMENT`
- `DECISION`
- `FINDING`
- `TASK`
- `CONTRADICTION`
- `MEMORY`
- `OUT_OF_SCOPE`

A contradiction always produces `HOLD_FOR_REVIEW` and has no automatic canonical or work effect.

## Monotone cursor

The intake cursor tracks:

- latest sequence;
- reconciled-through sequence;
- canonical revision;
- work revision;
- pending intake IDs;
- last reconciliation digest.

Sequence gaps never authorize skipping evidence.

## Knowledge freshness

Before a write, agents must consider:

- current HEAD;
- canonical revision;
- work revision.

HEAD drift always requires reconciliation. Knowledge revision drift requires reconciliation when it affects the selected work scope.
