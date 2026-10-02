# GACR Correlator / Dispatcher / Takeover Integration

> Programme: GACR only.
>
> Scope authority: CP-AGENT-RELAY-001 family.
>
> Branch: governance/gacr-correlator-dispatcher-integration.
>
> START_MAIN_HEAD: 652d7e3385c7efa05ee7b085adf22e4574485db5.
>
> Global programme, P12-S6, CASE 1 and GMC: OUT OF SCOPE / UNCHANGED.
>
> Ultimate live Steps 13-24: NOT EXECUTED by this tranche.

## Additive boundary

This tranche strengthens the existing R1-R6 chain. It reuses the canonical
GACR sessions, work claims, claim collision domains, work-item dependencies,
takeover queue, Beacon, Correlator, Forensics, Dispatcher and exact-HEAD
acceptance gate.

It does not create a second session store, claim engine, lock system,
dependency engine, task engine, authority engine or takeover database.

Presence/Envelope and Liveness/Progress remain separately owned surfaces.
Their future Worker APIs are integration dependencies, not implementations
owned by this tranche.

## Connection fingerprint

The operational namespace is:

    GACR-FP1-<sha256>

The fingerprint is a versioned correlation key. It is not a provider
conversation identifier and it never populates provider_conversation_ref.

The fingerprint builder uses allowlisted, frozen first-touch / connection
facts: repository key, safe actor or installation key, client_instance_id,
connection_ref, genuinely supplied provider ref when available, task/claim,
branch/PR, first observed HEAD and a bounded first-touch time bucket.

Current event HEAD and current observation timestamp are excluded so ordinary
work progress does not manufacture a new operational identity. Insufficient
stable entropy returns no fingerprint.

Canonical exhaustive ConnectionEnvelope production remains owned by the
Presence/Envelope tranche. This integration consumes a supplied fingerprint
or derives one only from safe facts already available to the existing GACR
session/Beacon path.

## Correlation rules

Correlation uses named categorical rules. A numeric score is not truth and
is not used by the canonical selection algorithm.

### EXACT

EXACT requires a consistent direct operational anchor resolving to one live
repository session:

- explicit session_id;
- genuinely supplied provider conversation ref;
- client_instance_id;
- connection_ref.

Conflicting direct anchors or a conflicting specific provider fail closed to
AMBIGUOUS.

### STRONG

STRONG requires a unique candidate and one of the declared multi-signal rules:

- connection_fingerprint plus compatible task/branch/PR/actor/installation/claim evidence;
- task + branch + PR;
- actor + installation + branch;
- workflow run + job + branch;
- claim + branch.

A fingerprint alone never becomes provider identity and never creates EXACT.

### PROBABLE

Context evidence supporting one candidate without satisfying a STRONG rule
remains PROBABLE. PROBABLE never selects a session.

### AMBIGUOUS

AMBIGUOUS is produced for conflicting direct facts, multiple STRONG
candidates, or multiple equally plausible PROBABLE candidates. It never
selects a session.

### UNKNOWN

UNKNOWN means the available evidence does not safely support a live repository
session. It never selects a session.

Every correlation records a named rule and reasons.
confidence.numeric_score is null.
Only EXACT and unique STRONG can set selected_session_id.

Non-selected activity is projected as UNBOUND_ACTIVITY. The full canonical
UNBOUND_ACTIVITY lifecycle remains a shared Presence integration surface; no
second queue is introduced here.

Terminal CLOSED and HANDOFF_STALLED sessions are excluded.

## Correlator signals

When actually available, the Correlator can consume:

- session ID and provider ref;
- client_instance_id and connection_ref;
- connection_fingerprint;
- repository and provider;
- actor and GitHub installation;
- task and claim/work item;
- branch and PR;
- observed and written HEAD;
- workflow/run/job metadata;
- bounded temporal compatibility.

Provider-private identity is not inferred from a fingerprint.

## Dispatcher compatibility

Every considered successor is classified:

- ELIGIBLE;
- INELIGIBLE;
- BLOCKED;
- AMBIGUOUS.

Compatibility checks reuse existing authorities and state:

1. same repository;
2. session state and relay state are STANDBY;
3. task/work scope is compatible;
4. candidate has no active conflicting claim;
5. existing work-item dependencies are DONE;
6. existing collision domains are free, excluding the stalled predecessor's
   own claim which remains held until acceptance;
7. required capabilities are present;
8. required authority evidence is present when the work contract requires it;
9. declared role/work scope constraints are satisfied;
10. wake capability affects delivery only, never write authority.

Missing required authority evidence is AMBIGUOUS. Explicitly absent required
capability or authority is INELIGIBLE. Dependency/collision/claim conflicts
are BLOCKED.

The compatibility record is evidence and a filter; it never grants write
authority.

## Deterministic selection

Eligible candidates are ordered deterministically by categorical facts:

1. exact target task binding;
2. exact target branch binding;
3. exact target PR binding;
4. creation time;
5. session ID.

The dispatch decision records all evaluations and
grants_write_authority=false.

## Dispatcher and takeover flow

    STALLED
    -> Correlator / Forensics context
    -> compatible standby search
    -> compatibility evaluation
    -> deterministic selection
    -> TAKEOVER OFFER
    -> takeover package
    -> exact branch HEAD reobservation
    -> acceptance if every gate passes
    -> claim transfer
    -> predecessor terminal
    -> activation/relay only through a real declared delivery capability

Repository polling is always usable as a repository-side discovery mode.
Repository dispatch and external bridge delivery are used only when
available/configured. Provider execution or browser activation remains an
external capability.

## Takeover package

The package is a derived projection over existing stores, not a new source of
truth. When available it carries:

- predecessor and successor candidate;
- repository;
- task/work item and active claims;
- branch and PR;
- observed and written HEAD;
- last activity and last progress evidence;
- action in flight and last completed action;
- checkpoint and evidence refs;
- Forensics resume point;
- collision domains;
- dependencies and their states;
- exact-HEAD requirement;
- known unknowns;
- provider conversation ref only when provenance proves it was genuinely
  supplied or extracted from an explicit provider URL.

The package states:

    may_write_before_takeover_accept = false
    claim_transfer_before_accept = false
    replay_policy = RECONCILE_BEFORE_REPLAY

## Exact-HEAD acceptance

Existing behavior is preserved:

1. fetch/reobserve the actual work branch;
2. obtain the remote HEAD;
3. compare it with the successor's reconciled HEAD;
4. mismatch rejects takeover;
5. exact match allows acceptance only if the remaining gates pass;
6. claims transfer only after acceptance;
7. predecessor becomes terminal;
8. a late predecessor heartbeat cannot resurrect ownership.

No takeover is accepted against an assumed HEAD.

## Test H and Correlator fixtures

The CI integration fixture proves:

1. Agent B discovers stalled Agent A;
2. B receives the stopping point;
3. exact HEAD is required;
4. mismatch fails;
5. exact match permits acceptance;
6. the claim remains on A until acceptance;
7. A becomes terminal after acceptance;
8. a late A heartbeat cannot regain ownership;
9. B continues the same task;
10. unresolved in-flight action is reconcile-before-replay.

Correlator fixtures cover EXACT, STRONG, PROBABLE, AMBIGUOUS, UNKNOWN,
multi-session same actor, same repository with different branches, different
client_instance_id, missing provider ref, fingerprint match, conflicting
provider evidence, terminal exclusion and unbound activity.

## Prepared E2E harness

scripts/gacr_e2e_takeover_harness.py freezes:

    Agent A first touch
    -> work
    -> liveness/progress
    -> controlled stop
    -> SUSPECTED_STALL
    -> STALLED
    -> TAKEOVER_READY
    -> Agent B context
    -> predecessor reconstruction
    -> exact HEAD
    -> takeover acceptance
    -> continuation

Adapter contract: GACR_WORKER_ADAPTER_V1.

SHARED_INTEGRATION_REQUIRED:
bind this harness to the separately-owned Presence/Envelope and
Liveness/Progress Worker APIs after those surfaces are merged.

The harness reports live_proof_status=NOT_EXECUTED and refuses a live claim
while those adapters are absent.

This tranche does not make GACR complete. Final completeness still requires
the ordered live Steps 13-24 proof.
