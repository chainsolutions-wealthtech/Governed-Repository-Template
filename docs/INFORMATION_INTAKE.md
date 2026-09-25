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


## Connection intent boundary

A session used to contribute context or information should declare `CONTEXT_INTAKE` or `INFORMATION_INTAKE`.

These intents route to intake and cannot dispatch mutable work.

```text
CONTEXT_INTAKE != CODE_PERMISSION
INFORMATION_INTAKE != CODE_PERMISSION
```

If the same conversation later requests code, the session intent must be explicitly reconciled to a mutable intent such as `WORK_REQUEST` or `CODE_CHANGE`; the change in intent still does not grant any higher authority.
