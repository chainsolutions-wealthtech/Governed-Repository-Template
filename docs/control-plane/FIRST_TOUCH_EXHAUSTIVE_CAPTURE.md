# First-Touch Exhaustive Capture

Status: `NON_CANONICAL_OBSERVABILITY_MECHANISM`

## Purpose

Capture the broadest safe repository-side evidence available at the first observable GitHub interaction **before** GSCC, GSE or GACR interpretation.

The collector is intentionally non-decisional:

```text
FIRST OBSERVABLE GITHUB EVENT
        ↓
EXHAUSTIVE RAW CAPTURE
        ↓
GitHub Actions artifact
        ↓
existing GSCC Observable Arrival Gateway
        ↓
GSCC / GSE / GACR
```

The capture does not classify fields as GSCC, GSE or GACR data and does not remove unexpected ordinary fields.

## Capture surfaces

The current collector preserves:

- the complete GitHub event object after recursive sensitive-value redaction;
- observable GitHub/runner environment metadata;
- unexpected event fields without requiring a predefined schema;
- repository metadata returned by GitHub;
- repository permission information for the observed actor when available;
- the issue or pull request object associated with the event when available;
- the current workflow run and jobs when available;
- repository installation lookup result or its returned failure;
- repository Actions-permission lookup result or its returned failure.

Failed or unavailable API reads remain present as returned status/evidence rather than being silently omitted.

## Artifact

Each observable-arrival run uploads:

```text
first-touch-capture-<run_id>-<run_attempt>
└── first-touch-capture.json
```

Retention is currently 30 days.

The capture object uses:

```text
first-touch-exhaustive-capture/v1
```

and includes a deterministic `capture_id` and `capture_digest`.

## Safety boundary

Sensitive fields are not dropped from the structure. Their field presence is preserved while their value is replaced by a redaction marker.

The collector does not grant mutation authority, claim authority, takeover authority, function exposure or session routing authority.

It is evidence collection only.

## Current limitation

This workflow can capture only what the repository/GitHub Actions execution surface can observe or query.

Provider-private information that never reaches GitHub — for example a native ChatGPT/Codex conversation ID, provider-private workspace ID, or host-only tool catalogue — cannot be manufactured by this collector. A future provider/client adapter may add such observations when the provider genuinely exposes them.

That limitation does not alter the collector rule: everything safely observable on its execution surface is retained before later architectural selection.
