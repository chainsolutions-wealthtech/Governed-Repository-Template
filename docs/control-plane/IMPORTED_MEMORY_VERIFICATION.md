# IMPORTED MEMORY VERIFICATION — CP-ARCH-001

## Scope

User-selected external memory sources reviewed on 2026-09-26:

1. `Texte collé(20260926-204542).txt`
2. `GOVERNED_REPOSITORY_PLATFORM_CANONICAL_MEMORY_V2.8.3(1).md`
3. `GOVERNED_REPOSITORY_PLATFORM_CANONICAL_MEMORY_V2.8.3(1).pdf`

## Canonical-memory-verifier contract

The `canonical-memory-verifier` skill requires a native imported-memory bundle with `bundle.json` and a declared `sources/` set before it can truthfully emit `VERIFIED`.

The supplied attachments were individual files, not a native verifier bundle. Therefore no synthetic `VERIFIED` result is asserted.

The verifier invariants are nevertheless applied to integration:

- imported memory cannot satisfy live approval;
- source provenance is explicit;
- historical authority remains historical evidence;
- live repository observation outranks stale snapshot values;
- supersession/revision must be explicit;
- ambiguous or contradictory current values require reconciliation rather than silent selection.

## Source integrity

```text
TXT
sha256 = 48f42b55b285a18d9a137b63b5e2c6d9d67e4e46934239ee6a77c2a0db1c0b37
role   = integration analysis / proposed implementation

Markdown
sha256 = 53453ce9e7c5edeae0d18ca0539c56bfd84230c829979255164409e3db5799db
role   = primary target-architecture snapshot

PDF
sha256 = 3cc21586cb7562e23005b8d51737a08c2fe62a0df4344af646ea41a4ee7f3368
role   = derived presentation representation
```

## Snapshot boundary

The supplied architecture snapshot observed:

```text
repository = chainsolutions-wealthtech/Governed-Repository-Template
head       = 892f793a0202cb4f69169001821014f47db45c3f
version    = 2.8.3
```

It is not treated as the live repository state after later merges.

Live state must be reobserved from GitHub before mutable work.

## Integration result

Compatible durable architecture was distilled into:

- `docs/control-plane/CANONICAL_ARCHITECTURE.md`
- authority ID `CP-ARCH-001`
- machine projection `.governance/control-plane-state/canonical-architecture.json`
- relational revision/event registry via `003_canonical_authorities.sql`

Snapshot-specific live values were not allowed to overwrite newer current-state/task/checkpoint evidence.

## Approval rule

```text
IMPORTED MEMORY != LIVE APPROVAL
```

Any future mutation still requires the normal control-plane authority, exact-HEAD and validation gates.
