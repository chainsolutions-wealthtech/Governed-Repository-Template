# GACR Original Intent ↔ Current Implementation ↔ Gap Matrix

> Programme: GACR — Governed Agent Continuity Relay
>
> Role: GACR ORIGINAL INTENT / GAP ANALYST
>
> Analysis baseline: main@6a32debcc96d7c33b421dc901c514f79a4d05104
>
> OR-01 authority: PASS
>
> Artifact status: PREPARED_ANALYSIS / FORMAL_STEP_3_GATE_BLOCKED_UNTIL_STEP_2_FORMAL_GATE_CLOSE
>
> This artifact is intentionally analysis-only. It does not modify runtime, workflows, scripts, schemas, state stores, claims, locks, or the global Control Plane programme. It MUST NOT be read as GACR-OR-02 DONE or GACR-OR-03 DONE while docs/control-plane/GACR_PROGRAM.md still names REALIGNMENT_STEP_2_FORMAL_GATE_REVALIDATE_EXISTING_GACR_ORIGINAL_INTENT as the next GACR gate.

## 1. Scope and evidence boundary

This matrix compares the canonical historical intent in docs/control-plane/GACR_ORIGINAL_INTENT.md with the R1-R6 implementation frozen and reobserved by docs/control-plane/GACR_R6_BASELINE_ATTESTATION.md.

It deliberately separates four kinds of proof:

- SOURCE_FILES: implementation or authority surfaces that exist in the repository.
- RUNTIME_EVIDENCE: persisted GACR state or executable behavior visible in current source state.
- TEST_EVIDENCE: unit/integration/CI coverage.
- LIVE_EVIDENCE: a real repository/provider-host observation already attested.
- Absence of live evidence does not erase a tested implementation, but it prevents a CI-only capability from being described as live-proven.
- Silence never proves browser crash, provider timeout, network failure, or another provider-private cause.
- A provider conversation identifier or URL is never invented.
- A connection fingerprint, once implemented, is operational correlation metadata and NEVER a provider conversation ID.

Current authoritative stopping point:

- GACR-OR-01 = PASS.
- R1-R6 / R5-A / R6-A / R6-B / R6-C are preserved.
- Step 2 formal revalidation of the already-canonical original intent remains open.
- This document prepares step 3 material but does not close step 3.
- Presence-First corrective implementation is not authorized by this artifact.
- P12-S6 and the global programme are out of scope.

## 2. Executive gap map

| REQUIREMENT_ID | ORIGINAL_INTENT | CURRENT_IMPLEMENTATION | SOURCE_FILES | RUNTIME_EVIDENCE | TEST_EVIDENCE | LIVE_EVIDENCE | STATUS | GAP | REQUIRED_CORRECTION | ACCEPTANCE_TEST |
|---|---|---|---|---|---|---|---|---|---|---|
| GACR-OI-001 | Governed work continuity must survive loss of a provider conversation/tab/client. | Canonical governed session, heartbeat/lease, claims, takeover state, forensics, checkpoint/evidence references and exact-HEAD gates persist independently of a chat URL. | docs/GACR_AGENT_CONTINUITY_RELAY.md; scripts/governed_agent_continuity_relay.py; scripts/gacr_agent_telemetry.py | gacr-sessions.json revision 10; canonical session session-68c97d4bb1ef71c86444de12; provider_conversation_ref is null while continuity state remains reconstructible. | test_governed_agent_continuity_relay.py; test_gacr_agent_telemetry.py | R6-C preserved same canonical session while provider became chatgpt and native conversation ref remained unavailable. | COMPLETE | No core continuity gap. Full ultimate takeover continuation still has its own acceptance gap in GACR-OI-028. | Preserve existing session/claim/checkpoint/exact-HEAD model. | Remove provider conversation metadata from a fixture and prove task/branch/HEAD/action/evidence/resume context remains reconstructible. |
| GACR-OI-002 | Presence-First: first observable repository interaction through an instrumentable path should make an agent/session observable without explicit GACR registration. | R4 auto-attach uses explicit client metadata, fresh Conversation Chronicle, or eligible external GitHub Actions identity; R5/R6 add explicit emitter/host ingress. There is no general Presence Fabric in front of all controlled access paths. | GACR_ORIGIN_REALIGNMENT.md; gacr_auto_attach.py; gacr_workflow_bridge.py | AUTO_ATTACH session and Beacon exist; push may skip when no external anchor is observable. | test_gacr_auto_attach.py; host/client tests | R4 live AUTO_ATTACH was proven, but ultimate fresh-agent presence-from-first-touch was not run. | PARTIAL | Current center of gravity is event/anchor attachment, not a canonical presence observation layer for every controlled instrumentable access surface. | Introduce an additive Presence Fabric that converts first observable access/activity into safe Presence/Activity evidence and CREATE/RESUME without requiring a GACR-specific call. | Fresh agent is instructed only to do governed repository work; its first controlled repository interaction creates/resumes a canonical GACR presence/session with no explicit register instruction. |
| GACR-OI-003 | Governed arrival should attach without requiring provider conversation URL/ID. | Auto-attach does not require provider ref; late provider binding enriches the same connection-bound session; internal GACR transport is excluded. | gacr_auto_attach.py; governed_agent_continuity_relay.py; config.json | connection_ref + client_instance_id anchor canonical session; provider ref may remain null. | test_gacr_auto_attach.py | R4 and R6-C live evidence prove one session and no duplicate on provider enrichment. | COMPLETE | No correction to R4 attachment semantics; it becomes an input behind Presence Fabric. | Repeat attach and late provider enrichment; assert identical session_id and no duplicate active session. |
| GACR-OI-004 | BEACON records safe connection/action telemetry and enough operational metadata to support reconstruction. | Beacon persists allowlisted session/provider/client/repository/task/branch/PR/HEAD/action/tool/checkpoint/evidence plus nested safe GitHub context and a context digest. | gacr_agent_telemetry.py; gacr-telemetry.schema.json | gacr-beacons.json revision 13 with 13 preserved Beacons. | test_gacr_agent_telemetry.py; auto-attach/host tests | R4/R6 Beacons live-proven, including AUTO_ATTACH, HEARTBEAT, ACTION and HOST_HEARTBEAT_RECEIPT. | COMPLETE | Beacon itself exists and is live-proven; canonical exhaustive Connection Envelope is a separate gap. | Validate secret exclusion, deterministic dedupe, safe event context and real persisted Beacon from a controlled host event. |
| GACR-OI-005 | WATCH provides heartbeat, lease, SUSPECTED_STALL, STALLED and TAKEOVER_READY behavior without inventing interruption cause. | Core relay scan implements thresholds; scheduled workflow invokes scan; claims remain held on stall. | governed_agent_continuity_relay.py; governed-agent-continuity-relay.yml; config.json | heartbeat/lease fields persisted; current source has no live stalled item. | test_governed_agent_continuity_relay.py | Scheduled WATCH surface runs; exact-HEAD concurrent-state persistence failed closed in run 36948763070. Stall transition itself is CI-proven, not current-live. | COMPLETE | WATCH core is implemented. Continuous host heartbeat availability is provider/deployment dependent and handled separately. | Drive a controlled lease through ACTIVE → SUSPECTED_STALL → STALLED/TAKEOVER_READY and verify claim remains active. |
| GACR-OI-006 | CORRELATOR combines session, actor/app, repository, task/claim, branch, PR, HEAD, workflow/activity and provider conversation metadata when actually known. | Correlator scores session_id/provider_ref/client_instance_id/connection_ref exactly, then branch/PR/task/HEAD/GitHub actor. Terminal sessions are excluded. No canonical fingerprint exists and github_actor is not reliably projected into session records. | gacr_agent_telemetry.py; session.schema.json; gacr-telemetry.schema.json | gacr-correlations.json revision 14; canonical R6 correlations EXACT; historical transport Beacon remains PROBABLE/unselected. | test_gacr_agent_telemetry.py | Exact live correlation exists for canonical session. | PARTIAL | Correlation engine works, but intended signal set is incomplete: no fingerprint; app/installation/workflow identifiers are not first-class scoring inputs; github_actor session-side population is incomplete; claim/collision-domain signal is not part of scoring. | Extend correlation only after canonical envelope/fingerprint work; preserve fail-closed behavior and explicit provenance. | Fixtures exercise exact, unique strong, probable, ambiguous and unknown with actor/app/task/branch/PR/HEAD/fingerprint signals; only exact and unique strong may auto-bind. |
| GACR-OI-007 | Correlation quality must be explicit: EXACT / STRONG / PROBABLE / AMBIGUOUS / UNKNOWN; uncertainty must not become provider identity. | Implemented exactly; selected_session_id is set only for unique EXACT and STRONG. PROBABLE/AMBIGUOUS/UNKNOWN do not auto-bind. | gacr_agent_telemetry.py; gacr-telemetry.schema.json; config.json | Persisted correlations contain EXACT and PROBABLE examples. | test_gacr_agent_telemetry.py explicitly covers STRONG and AMBIGUOUS fail-closed behavior. | Canonical live R6 session is EXACT; historical transport evidence is non-selected PROBABLE. | COMPLETE | No status-model gap. | Assert no provider_conversation_ref mutation occurs as a consequence of any correlation level, including EXACT. |
| GACR-OI-008 | DISPATCHER should select compatible standby capacity, create takeover offers and prepare wake/relay without granting mutation authority. | Dispatcher creates target-specific records and delivery modes; POLL_REPOSITORY is default; repository dispatch/external bridge are optional; may_write_before_takeover_accept=false. | gacr_agent_telemetry.py; gacr_bridge_notifier.py; gacr-bridge-contract.schema.json | gacr-dispatches.json currently empty. | test_gacr_agent_telemetry.py covers target selection/delivery/no-write. | No current live dispatch or external wake. | PARTIAL | Target compatibility is currently much narrower than historical intent: same repository + STANDBY state, rather than full authority/capabilities/collision domains/dependencies evaluation. No live end-to-end dispatch. | Add deterministic compatibility evaluation using existing authority/claim/collision/dependency primitives; do not create a parallel lock/task model. | Multiple standby fixtures differ by authority/capability/collision/dependency compatibility; only eligible successor is offered, and no write occurs before takeover acceptance. |
| GACR-OI-009 | Optional provider/client Bridge enriches identity and can receive/relay wake where provider capability exists. | Safe bridge contract, notifier, bridge_registration_ref, client emitter and R6 issue ingress exist. External bridge webhook may be configured. | docs/GACR_BRIDGE_CONTRACT.md; gacr_bridge_notifier.py; gacr_client_emitter.py; gacr_host_issue_ingress.py; bridge schema | External bridge config reports browser wake not implemented; latest observed run skipped external bridge because not configured. | telemetry/client/host tests | R6 host ingress is event-driven live-proven; outbound external wake is not live-proven. | PARTIAL | Repository-side contract is present, but provider/browser wake/focus/API worker execution depends on an external adapter and configuration. | Keep bridge optional; implement/configure only provider-specific adapter capabilities that actually exist. | Configured test bridge receives one idempotent dispatch, fetches context, and cannot mutate until exact-HEAD takeover acceptance. |
| GACR-OI-010 | True wake/activation of an arbitrary proprietary browser conversation should occur only where provider/orchestrator exposes such a capability. | Repository can prepare dispatch and poll/notify; it cannot universally wake an arbitrary silent browser tab. | GACR_ORIGINAL_INTENT.md; GACR_BRIDGE_CONTRACT.md; config.json | outbound_browser_wakeup_implemented=false. | Contract/dispatcher tests only. | Not proven for browser wake. | EXTERNAL_BOUNDARY | This is not safely solvable from GitHub alone when the provider exposes no execution/wake surface. | Treat unsupported provider wake as explicit capability absence; continue to support takeover by another governed agent. | Provider fixture with no wake API remains safely takeover-ready without fabricated wake success; programmable provider fixture may activate through its documented API. |
| GACR-OI-011 | GET agent-context philosophy: an arriving agent should obtain deterministic session, work, peers, claims/collision state, checkpoint/evidence, liveness and next safe action. | context command aggregates session, active claims, takeovers, dispatches, recent Beacons/correlations, forensics and repository HEAD/branch. It is CLI/workflow semantics, not an HTTP GET endpoint, and does not yet explicitly project full peer/collision/next-safe-action semantics. | gacr_agent_telemetry.py; GACR_AGENT_CONTINUITY_RELAY.md | Context can be computed from canonical stores. | test_gacr_agent_telemetry.py | CI-proven; no distinct live Agent Context acceptance artifact. | PARTIAL | Aggregate exists but is not yet the full deterministic interrogation contract envisioned by original intent. | Define a canonical read-only Agent Context response contract over existing stores, including identity/provenance, peer statuses, active collision domains, resume point and next safe action. | Query context for active, standby and stalled fixtures; output is deterministic, source-backed, read-only and sufficient to resume safely. |
| GACR-OI-012 | Full canonical Connection Envelope should distinguish observable, declared and unavailable data and provide one exhaustive arrival/activity representation. | Data exists across session, Beacon nested GitHub context, relay and Forensics, but not one canonical exhaustive envelope. Several target fields are absent or only semantically approximated. | GACR_ORIGINAL_INTENT.md; session.schema.json; gacr-telemetry.schema.json; relay/telemetry scripts | Current session + Beacons jointly cover many, not all, target fields. | Existing tests cover components, not exhaustive envelope field contract. | Live R6 proves many fields, not exhaustive envelope completeness. | PARTIAL | Missing one versioned envelope contract; missing/partial fields include agent model/type, canonical git_provider, connection_method, real permissions, claim_id, heartbeat_seq, job_id, explicit connected_at, and others detailed below. | Define one additive safe envelope schema/projection using provenance per field; reuse existing stores/values; do not create a parallel continuity database. | Field-by-field acceptance verifies defined/collected/validated/persisted/correlated status, provenance, redaction and UNKNOWN/UNAVAILABLE behavior. |
| GACR-OI-013 | connection_fingerprint should strengthen operational correlation when native provider conversation reference is unavailable. | No connection_fingerprint field, formula, schema, persisted projection or correlation rule exists. context_digest/dedupe_key and connection_ref are different mechanisms and MUST NOT be relabeled as fingerprint. | GACR_ORIGINAL_INTENT.md; gacr_agent_telemetry.py; gacr_auto_attach.py | No fingerprint in session/Beacon/correlation state. | No fingerprint test. | No live fingerprint proof. | MISSING | Historical candidate inputs exist partially, but no canonical normalized/versioned formula or collision semantics exist. | Define a versioned deterministic hash over allowlisted normalized inputs with provenance and bounded timestamp context. Fingerprint must never populate or impersonate provider_conversation_ref. | Same operational connection yields stable fingerprint under defined bounds; independent fixtures do not collide; collision/insufficient evidence fails closed; provider ref remains null when unavailable. |
| GACR-OI-014 | LIVENESS and PROGRESS are independent dimensions; heartbeat must never be promoted to proof of work progress. | Liveness lives in heartbeat/lease/state; progress-like evidence exists as ACTION_TRACE, written HEAD, checkpoint/evidence and forensics action projection. There is no independent canonical progress state/evidence model and no formal anti-conflation projection. | GACR_ORIGIN_REALIGNMENT.md; relay.py; gacr_agent_telemetry.py; client emitter | Current persisted heartbeat and action evidence are separate facts but not modeled as two canonical dimensions. | Tests cover heartbeat and action traces independently. | R6 has both heartbeat and action events, but no formal liveness-vs-progress acceptance. | PARTIAL | Data separation exists de facto; semantics are not yet canonicalized as LIVENESS_STATE and PROGRESS_STATE/evidence. | Add independent derived dimensions without replacing WATCH; heartbeat updates liveness only; progress requires action/result/HEAD/checkpoint/evidence signals. | Heartbeats with no progress keep liveness healthy while progress becomes quiet/stale; action completion advances progress; neither dimension overwrites the other. |
| GACR-OI-015 | Session interrogation should let GACR inspect a known session deterministically. | Read-only context and forensics commands interrogate repository-known session state. No unified interrogation command/contract with challenge status exists. | gacr_agent_telemetry.py; GACR_AGENT_CONTINUITY_RELAY.md | Static persisted state is queryable. | telemetry tests | CI only. | PARTIAL | Repository-state interrogation exists; active endpoint/session interrogation semantics from realignment step 10 are not complete. | Canonicalize read-only interrogation result with evidence timestamps, endpoint capability and UNKNOWN when no active endpoint exists. | Interrogate repository-only session and challenge-capable session; results clearly distinguish stored state from fresh target response. |
| GACR-OI-016 | Active liveness challenge should be supported where a target endpoint can answer. | No challenge request/nonce/response command, state or test exists. | No current runtime implementation. | None. | None. | None. | MISSING | Heartbeat is passive input; there is no active, replay-safe challenge protocol. | Add optional challenge semantics only for registered endpoints that declare support; nonce/idempotency/expiry required; no response becomes UNKNOWN/NO_RESPONSE, not a fabricated failure cause. | Supported endpoint echoes governed challenge proof within expiry; stale/replayed response rejected; unsupported endpoint returns UNSUPPORTED rather than false dead/alive claim. |
| GACR-OI-017 | UNBOUND_ACTIVITY should preserve repository activity that cannot yet be safely attributed to a GACR session. | Correlator can output PROBABLE/AMBIGUOUS/UNKNOWN with selected_session_id=null, but there is no canonical UNBOUND_ACTIVITY queue/state/reconciliation lifecycle. | gacr_agent_telemetry.py; GACR_ORIGIN_REALIGNMENT.md | Historical transport Beacon is non-selected PROBABLE, demonstrating unbound-like evidence without canonical classification. | Correlator ambiguity tests. | Non-selected evidence exists; UNBOUND_ACTIVITY itself not live-proven. | MISSING | Unattributed activity is present only implicitly as a non-selected correlation. | Add a derived UNBOUND_ACTIVITY classification/reconciliation surface over existing Beacon/correlation stores; never auto-bind uncertain evidence. | Unknown/ambiguous activity appears as UNBOUND; later exact evidence reconciles it idempotently to one session while conflicts remain unbound. |
| GACR-OI-018 | Stall detection must be lease/evidence based and preserve claims; silence must not be labeled as a specific provider failure. | Implemented. Forensics reports UNOBSERVED_EXTERNAL_CAUSE absent explicit interruption signal. | relay.py; gacr_agent_telemetry.py; config.json | Lease/stall metadata and Forensics classification persist. | core relay + telemetry tests | Current source has no live stalled item; observed-only cause policy is live represented in Forensics. | COMPLETE | No correction to stall/cause safety semantics. | Silence drives governed state transition only; cause remains UNOBSERVED_EXTERNAL_CAUSE unless explicit signal exists. |
| GACR-OI-019 | Governed takeover must preserve ownership until an eligible successor reobserves state and explicitly accepts transfer. | Takeover queue, standby offer, acceptance and claim transfer are implemented; predecessor becomes HANDOFF_STALLED after transfer. | relay.py; gacr-state.schema.json | Current takeover and claim stores are empty. | core relay tests cover claim preservation and transfer. | CI-proven only for actual takeover; no current live takeover. | COMPLETE | Core takeover authority model is complete; Dispatcher compatibility and ultimate live E2E remain separate gaps. | Claim remains with predecessor through stall/offer and transfers only after valid successor acceptance. |
| GACR-OI-020 | Exact branch/HEAD reconciliation is mandatory before mutable takeover and stale persistence must fail closed. | accept_takeover compares reconciled HEAD with actual work HEAD; workflow persistence compares captured base with remote HEAD before push. | relay.py; governed-agent-continuity-relay.yml | Takeover contract stores last/reconciled HEAD fields. | core relay test rejects mismatched HEAD and accepts exact HEAD. | Scheduled run 36948763070 refused stale persistence with HEAD_MOVED. | COMPLETE | No correction to exact-HEAD invariant. | Concurrent advance between observation and mutation causes deterministic refusal; refreshed exact HEAD is required before retry. |
| GACR-OI-021 | Continuity must work when provider conversation ref/URL is unknown. | Canonical session identity uses governed session/connection anchors; provider ref is optional; full URL is not persisted by default. | relay.py; auto_attach.py; GACR_BRIDGE_CONTRACT.md | canonical session provider=chatgpt, provider_conversation_ref=null/UNAVAILABLE, while branch/HEAD/action/evidence remain known. | core/auto-attach/host tests | R6-C live provider enrichment preserved same session with no native conversation ref. | COMPLETE | No gap. | Provider ref/url omitted throughout fresh attach and resume; continuity and exact correlation via safe governed anchors still work. |
| GACR-OI-022 | Provider-private facts never transmitted to GACR remain unavailable rather than inferred. | UNAVAILABLE provenance and observed-only interruption policy exist; explicit URL/ref normalization only uses supplied data. | relay.py; telemetry.py; config.json | provider ref null/UNAVAILABLE in canonical state; Forensics cause UNOBSERVED_EXTERNAL_CAUSE. | auto-attach/forensics tests | R6-C live state demonstrates unavailable native conversation ref. | COMPLETE | No correction; preserve fail-closed unknown semantics. | Absence of provider-private ID, URL or crash cause cannot produce a synthesized value under any correlation path. |
| GACR-OI-023 | Source/client isolation: Source Control Plane GACR runtime memory must remain isolated from distributed client runtime state. | Source uses control-plane-state/gacr-*.json; clients use repository-local sessions/work/agent-relay paths; R6 source issue number is not distributed. | relay.py; telemetry.py; workflow; upgrader; docs | Source state contains source-only canonical session; generic client stores remain distinct. | core/host workflow/upgrader tests | Boundary correction and R6-B portability live-attested. | COMPLETE | No correction; preserve path/identity separation. | Generate/adopt client and assert no source session, claim, Beacon, issue number or source conversation coordinate is copied. |
| GACR-OI-024 | Internal GACR transport is infrastructure, never an agent/session identity. | Internal workflow is explicitly excluded as GitHub anchor; historical bad session preserved CLOSED/SUPERSEDED and excluded from Correlator. | gacr_auto_attach.py; gacr_agent_telemetry.py; config.json | session-cb22a4ed0d9e29eba5383f5d is terminal/superseded. | test_gacr_auto_attach.py; telemetry tests | Post-R5-A live push skipped attachment with no new session/Beacon. | COMPLETE | No correction. | Stale Chronicle + only internal workflow activity yields GACR_AUTO_ATTACH_SKIPPED and zero new agent session. |
| GACR-OI-025 | Safe observability excludes secrets, tokens, cookies, raw transcript bodies and private reasoning. | Beacon and host/client payload validators reject forbidden key/value classes; raw GitHub payload is not persisted. | gacr_agent_telemetry.py; gacr_client_emitter.py; gacr_host_issue_ingress.py; config.json | Persisted Beacons contain allowlisted GitHub metadata only. | telemetry/client/host tests | R6 live Beacons show safe operational metadata without transcript/cookies/tokens. | COMPLETE | No correction; new Presence/Envelope work must reuse this boundary. | Secret-like/transcript fields fail closed; accepted envelope persists only allowlisted operational facts. |
| GACR-OI-026 | Dispatcher/provider wake should never imply mutation authority. | Dispatch record marks exact-HEAD required and may_write_before_takeover_accept=false; client wake poll is informational. | telemetry.py; client emitter; bridge contract | dispatch store empty now. | dispatcher/client tests | Not live-proven because no live dispatch. | COMPLETE | No authority-model gap. | Receiving READY/ACTIVATED wake without accepted takeover cannot mutate claimed work. |
| GACR-OI-027 | Provider host liveness may be continuous only if the host actually runs/invokes an emitter or equivalent adapter. | R5 emitter can daemon-heartbeat; R6 ChatGPT bridge is event-driven GitHub issue-comment ingress. Current host has no proven always-running daemon. | gacr_client_emitter.py; gacr_host_issue_ingress.py; config.json | continuous_background_heartbeat_proven=false. | client emitter daemon test | R6 event-driven host proof only. | EXTERNAL_BOUNDARY | A silent proprietary host cannot be made continuously observable solely by repository code. | Capability declaration differentiates CONTINUOUS, EVENT_DRIVEN and UNSUPPORTED host modes; no unsupported host is reported continuously live. |
| GACR-OI-028 | Ultimate live acceptance: fresh agent → observable first-touch → session → real work → liveness/progress → controlled loss → stall → second agent → reconstruct stop point → exact-HEAD takeover → continuation. | Individual R1-R6 components exist, but the whole scenario has not been run live as one acceptance chain. | GACR_ORIGIN_REALIGNMENT.md; R6 baseline attestation | No single persisted acceptance chain covering all stages. | Component tests only; Presence-First acceptance tests are a future step. | Baseline attestation explicitly states the ultimate scenario has not been run. | MISSING | Final system-level proof is absent and must remain the completion gate. | Execute the exact 13–24 sequence from the realignment plan with two fresh governed agents and retain time-ordered evidence for every transition. |

## 3. Canonical three-category data model

These categories are normative for future Presence/Envelope/fingerprint work. Every field should carry either direct provenance or an explicit unavailable state. No category authorizes collection of cookies, tokens, secrets, raw transcript bodies or private reasoning.

| CATEGORY | SOURCE | CONFIDENCE | PERSISTENCE AUTORISÉE | UTILISATION POUR CORRÉLATION | POSSIBILITÉ D’INFÉRENCE | COMPORTEMENT SI INFORMATION MANQUANTE |
|---|---|---|---|---|---|---|
| OBSERVABLE_BY_PLATFORM | Facts directly emitted by GitHub/Git or another controlled instrumented surface: repository and repository ID, owner/org, actor/app when exposed, ref/branch, SHA, PR, workflow/run/attempt/job metadata, event type, timestamps, immutable delivery/evidence IDs, controlled gateway/connector observations. | HIGH for direct immutable identifiers and event facts; MEDIUM where a platform field is contextual rather than identity-bearing. | Yes, only allowlisted operational metadata with provenance and bounded retention consistent with repository governance. Raw event payloads and secret-bearing headers are forbidden. | Yes. May be used as deterministic or weighted correlation evidence. Platform observability alone must not be promoted to native provider conversation identity. | Only deterministic derivations from the observed fields are allowed, for example normalized ref or a versioned fingerprint. Motive, private provider state and failure cause are not inferable. | Persist UNKNOWN/UNAVAILABLE or create UNBOUND_ACTIVITY when activity is real but attribution is not safe. Never fabricate a missing value. |
| DECLARED_BY_AGENT_OR_CLIENT | Explicit values supplied by an agent/client/bridge/orchestrator: provider, model/type when available, agent role, capabilities, task/goal, connection intent, client_instance_id, provider conversation ref/URL, bridge registration reference, active/standby declaration, explicit interruption code. | HIGH that the value was declared; not automatically HIGH that the provider independently attested it. Provenance MUST remain DECLARED/SUPPLIED. | Yes for allowlisted operational declarations. Provider URL should not be persisted by default; normalize/store reference when policy permits. Never persist credentials, cookies, transcript bodies or private reasoning. | Yes. Unique stable explicit references can support EXACT correlation. Conflicts must fail closed. A declaration cannot override contradictory stronger platform evidence silently. | Do not infer an undeclared provider-private value. Safe normalization of an explicitly supplied URL into its reference is allowed. | Leave null/UNAVAILABLE with provenance. Continue continuity using governed session/repository/task/branch/HEAD/evidence anchors. |
| PROVIDER_PRIVATE_UNAVAILABLE | Native provider facts that the provider/client did not transmit: internal conversation ID/URL, private execution state, hidden browser lifecycle, private model state, provider-side crash/timeout reason, private reasoning. | NONE / UNAVAILABLE inside GACR unless later explicitly supplied through an authorized adapter. | Persist only the unavailable/unknown provenance marker, never a synthesized value. | Cannot be a positive correlation signal while unavailable. Other governed evidence may correlate the session operationally without identifying the provider conversation. | FORBIDDEN. Fingerprint, actor, branch, timing or GitHub activity may never be rebranded as provider-private identity. | Keep UNAVAILABLE/UNKNOWN. Do not block reconstructible continuity; do not assert provider identity/cause/liveness beyond evidence. |

### 3.1 Classification examples

- repository_id from a GitHub event: OBSERVABLE_BY_PLATFORM.
- GITHUB_RUN_ID / run_attempt: OBSERVABLE_BY_PLATFORM.
- client_instance_id supplied by a client bridge: DECLARED_BY_AGENT_OR_CLIENT.
- provider=chatgpt explicitly emitted by the host: DECLARED_BY_AGENT_OR_CLIENT.
- provider conversation reference not exposed by ChatGPT host: PROVIDER_PRIVATE_UNAVAILABLE.
- browser crash inferred only from heartbeat silence: forbidden inference; cause remains PROVIDER_PRIVATE_UNAVAILABLE / UNOBSERVED_EXTERNAL_CAUSE.
- connection_fingerprint: when implemented, it is a DERIVED OPERATIONAL CORRELATION VALUE from allowlisted inputs; it is not a fourth provider-identity category and never becomes provider_conversation_ref.

## 4. Connection Envelope field-by-field audit

Legend:

- YES: canonical behavior/field is implemented for that dimension.
- PARTIAL: an equivalent or nested value exists, but not as the canonical exhaustive envelope field or not for all sources.
- CONDITIONAL: only present when the upstream platform/client actually supplies it.
- NO: not implemented for that dimension.
- LIVE-NULL: live path proved correct unavailable/null handling, not a non-null value.

| FIELD | DEFINED? | COLLECTED? | VALIDATED? | PERSISTED? | CORRELATED? | TESTED? | LIVE_PROVEN? | CURRENT IMPLEMENTATION / GAP |
|---|---|---|---|---|---|---|---|---|
| gacr_session_id | YES | YES | YES | YES | YES | YES | YES | Runtime name is session_id rather than gacr_session_id; canonical governed identity is nevertheless implemented and live. A future envelope should expose the canonical alias explicitly. |
| client_instance_id | YES | YES | PARTIAL | YES | YES | YES | YES | Client/Chronicle value is persisted and is an EXACT signal. Validation is mostly structural/string rather than provider-scoped identity validation. |
| provider | YES | YES | YES | YES | YES | YES | YES | Core CLI enforces provider choices; provider ref match can be EXACT. Live provider is chatgpt. |
| agent_identity | YES | YES | YES | YES | NO | YES | YES | Persisted in session and Beacon. Current Correlator does not score agent_identity. |
| agent_type/model | YES | NO | NO | NO | NO | NO | NO | agent_role exists but is not equivalent to model/type. Canonical model/type field is missing. |
| repository | YES | YES | YES | YES | YES | YES | YES | Primary repository partition/gate for sessions and correlation. |
| repository_id | YES | YES | PARTIAL | YES | NO | PARTIAL | YES | Captured in nested safe GitHub event/environment context; no first-class canonical envelope field or correlation rule. |
| organization | YES | YES | PARTIAL | YES | NO | PARTIAL | YES | GitHub owner login/ID are captured nested; canonical organization field is not normalized across git providers. |
| git_provider | YES | PARTIAL | NO | PARTIAL | NO | NO | PARTIAL | GitHub is inferable from controlled GitHub context/server URL, but there is no explicit canonical git_provider value/provenance in the envelope. |
| github_actor | YES | YES | PARTIAL | YES | PARTIAL | PARTIAL | YES | Beacon captures GITHUB_ACTOR; session schema permits github_actor, but current registration paths do not reliably populate it, making GITHUB_ACTOR_MATCH largely dormant. |
| github_app/installation | YES | CONDITIONAL | PARTIAL | CONDITIONAL | NO | PARTIAL | LIVE-NULL | installation_id is allowlisted when GitHub supplies it; current R6 live samples have null. No canonical GitHub App identity object. |
| connection_method | YES | PARTIAL | NO | PARTIAL | NO | PARTIAL | YES | source/transport values such as CLIENT_EMITTER, GITHUB_ACTIONS, EXPLICIT_CLIENT and issue-comment ingress approximate method, but no canonical normalized connection_method field exists. |
| permissions/capabilities | YES | PARTIAL | PARTIAL | PARTIAL | NO | YES | PARTIAL | Declared agent capabilities are stored; actual effective GitHub/provider permissions are not dynamically captured as envelope permissions. |
| entry_action | YES | NO | YES | PARTIAL | NO | PARTIAL | LIVE-NULL | Session schema defines it, but current GACR register/auto-attach paths initialize UNKNOWN/DEFAULT_UNKNOWN and expose no direct collection parameter. |
| connection_intent | YES | NO | YES | PARTIAL | NO | PARTIAL | LIVE-NULL | Same gap as entry_action: canonical enum exists but GACR arrival path currently persists UNKNOWN by default. |
| task_id | YES | CONDITIONAL | PARTIAL | YES | YES | YES | LIVE-NULL | Supported in register/Beacon/relay and scored by Correlator. Current canonical source session has null task_id. |
| claim_id | YES | NO | NO | NO | NO | NO | NO | Existing canonical claim model uses session_id + work_item_id + collision_domains and has no claim_id field. Envelope may need a derived/stable claim reference or explicit mapping without replacing the claim model. |
| branch | YES | YES | PARTIAL | YES | YES | YES | YES | Persisted in relay/Beacon; branch match contributes score. |
| base_branch | YES | CONDITIONAL | PARTIAL | PARTIAL | NO | PARTIAL | PARTIAL | GitHub PR safe context captures base_ref nested when a PR event exists; no top-level canonical base_branch in session/Beacon. |
| HEAD | YES | YES | YES | YES | YES | YES | YES | starting_head_sha, last_observed_head_sha and Beacon observed_head_sha exist; HEAD contributes correlation and exact-HEAD safety. |
| PR | YES | CONDITIONAL | PARTIAL | YES | YES | YES | LIVE-NULL | Supported as pull_request in relay/Beacon and correlation; canonical current source session has null PR. |
| workflow_run_id | YES | CONDITIONAL | PARTIAL | YES | NO | PARTIAL | YES | GITHUB_RUN_ID persisted nested in safe GitHub context; not first-class or scored. |
| job_id | YES | NO | NO | NO | NO | NO | NO | Current safe context captures GITHUB_JOB, which is a job name/key, not a canonical GitHub numeric job_id. |
| run_attempt | YES | CONDITIONAL | PARTIAL | YES | NO | PARTIAL | YES | GITHUB_RUN_ATTEMPT persisted nested; not first-class or scored. |
| event_type | YES | YES | YES | YES | NO | YES | YES | Required Beacon field and live-proven. |
| delivery/correlation id | YES | PARTIAL | PARTIAL | YES | YES | YES | YES | GACR correlation_id/dispatch_id and issue-comment evidence IDs exist. A generic upstream delivery/correlation ID field is not unified; dispatch itself lacks current live instance. |
| connected_at | YES | PARTIAL | PARTIAL | YES | NO | YES | YES | session.created_at is the semantic connection timestamp; no explicit connected_at alias/provenance in canonical envelope. |
| last_seen_at | YES | YES | YES | YES | NO | YES | YES | Session field is implemented and live. |
| heartbeat_seq | YES | NO | NO | NO | NO | NO | NO | No monotonic heartbeat sequence is present. Dedupe keys/run attempts are not a heartbeat sequence. |
| lease_expires_at | YES | YES | YES | YES | NO | YES | YES | Canonical WATCH field in relay state. |
| provider_conversation_ref | YES | CONDITIONAL | YES | CONDITIONAL | YES | YES | LIVE-NULL | Explicitly supplied/normalized only. Live R6-C correctly proves null/UNAVAILABLE, not a non-null provider ref. |
| provider_conversation_url | YES | CONDITIONAL | YES | NO_BY_POLICY | NO | YES | NO | Full URL is accepted only if supplied and is not persisted by default. Known provider URL may be reconstructed from an explicitly stored ref. This privacy-minimizing policy is intentional. |
| checkpoint | YES | CONDITIONAL | PARTIAL | YES | NO | YES | YES | Implemented as checkpoint_ref in Beacon/Forensics; live refs CHK-R6-LIVE-001, CHK-R6B-LIVE-001, CHK-R6C-LIVE-001. |
| last_action | YES | YES | PARTIAL | YES | NO | YES | YES | Relay last_action plus action trace/Forensics projections. |
| last_evidence | YES | CONDITIONAL | PARTIAL | YES | NO | YES | YES | Relay last_evidence / Beacon evidence_ref / Forensics last_evidence_ref. |

### 4.1 Envelope conclusion

The Connection Envelope is PARTIAL, not MISSING:

- Many target facts are already collected safely.
- They are fragmented across session, relay, Beacon.github, Correlator and Forensics.
- The missing correction is primarily canonicalization + provenance + a few genuinely absent fields, not wholesale reinvention.
- A future envelope MUST reuse existing values and stores; it must not become a second continuity database.
- Raw provider URL, cookies, tokens, authorization headers, transcript text and private reasoning remain out of bounds.
- Provider-private unknowns must stay unavailable.

## 5. connection_fingerprint audit

Canonical historical candidate inputs:

provider + repository + actor/GitHub App + task + branch + PR + first observed HEAD + connection method + client_instance_id + bounded timestamp context → connection_fingerprint

Hard invariant:

> connection_fingerprint is NOT a provider conversation ID, provider conversation reference, provider conversation URL, or substitute for any of them.

| OBJECT | DEFINED? | COLLECTED? | VALIDATED? | PERSISTED? | CORRELATED? | TESTED? | LIVE_PROVEN? | STATUS |
|---|---|---|---|---|---|---|---|---|
| connection_fingerprint | YES — historical intent only | NO — no canonical field/formula | NO | NO | NO | NO | NO | MISSING |

### 5.1 Fingerprint input readiness

| INPUT | CURRENT READINESS | NOTE |
|---|---|---|
| provider | READY | Session/Beacon field. |
| repository | READY | Session/Beacon field and correlation partition. |
| actor / GitHub App | PARTIAL | Actor observed in Beacon; session-side actor not reliably populated. Installation ID is conditional; App identity is incomplete. |
| task | READY_CONDITIONAL | task_id exists when supplied. |
| branch | READY | Session/Beacon field. |
| PR | READY_CONDITIONAL | Supported when present. |
| first observed HEAD | READY | starting_head_sha exists. |
| connection method | PARTIAL | Source/transport exists but no canonical normalized field. |
| client_instance_id | READY_CONDITIONAL | Present when client/Chronicle supplies it. |
| bounded timestamp context | PARTIAL | created_at/observed_at exist, but no canonical bucket/window rule is defined. |

### 5.2 Required fingerprint correction

A safe future fingerprint should have at minimum:

- fingerprint_version;
- normalization_version;
- hash algorithm;
- explicit ordered input list;
- per-input provenance;
- rule for null/unknown inputs;
- bounded timestamp rule;
- deterministic canonical serialization;
- no secrets/raw transcript/private reasoning;
- collision/ambiguity behavior;
- explicit rule that a fingerprint can strengthen operational session correlation only;
- explicit prohibition on populating provider_conversation_ref or provider_conversation_url from a fingerprint.

context_digest, dedupe_key, stable session ID and connection_ref are existing useful mechanisms, but none is the historical connection_fingerprint contract. They must not be renamed after the fact to claim the requirement complete.

## 6. Correlation behavior audit

Current deterministic behavior:

| CONDITION | CURRENT RESULT | AUTO-BIND? | GAP |
|---|---|---:|---|
| Unique explicit session_id/provider_conversation_ref/client_instance_id/connection_ref match | EXACT | YES | Core behavior complete. |
| Unique score >= 7 from non-exact signals | STRONG | YES | Core behavior complete, but signal set is incomplete. |
| Score >= 4 but below strong threshold | PROBABLE | NO | Complete fail-closed behavior. |
| Equal top candidates with score >= 4 | AMBIGUOUS | NO | Complete fail-closed behavior. |
| No sufficient candidate | UNKNOWN | NO | Complete fail-closed behavior. |
| Provider conversation identity unavailable | Operational session may still correlate; provider identity remains unavailable | NEVER synthesize provider identity | Correct current behavior. |
| Fingerprint available | Not implemented | N/A | Future additive signal, never provider identity. |
| Unbound activity | Implicit as non-selected correlation only | NO | Canonical UNBOUND_ACTIVITY lifecycle missing. |

## 7. Liveness / progress / interrogation state

### 7.1 Current liveness evidence

Implemented:

- last_seen_at;
- last_heartbeat_at;
- lease_expires_at;
- ACTIVE / SUSPECTED_STALL / STALLED / TAKEOVER_READY states;
- scheduled scan;
- explicit client/provider-host heartbeat transport;
- explicit interruption signal when actually observed.

Not proven:

- an always-running background heartbeat from the current ChatGPT host.

### 7.2 Current progress evidence

Implemented as raw evidence, not a distinct canonical progress dimension:

- action_id;
- action_label;
- action_phase;
- tool_name / tool_call_id;
- outcome;
- written_head_sha;
- checkpoint_ref;
- evidence_ref;
- last completed/in-flight action projection.

Gap:

- no independent PROGRESS state/clock/freshness policy;
- no canonical rule saying a heartbeat updates liveness but not progress;
- no Presence/Activity layer that converts all controlled repository activity into progress-relevant evidence.

### 7.3 Session interrogation

Available now:

- context --session-id;
- forensics --session-id;
- repository/session/claim/takeover/Beacon/correlation/dispatch/forensics aggregation.

Missing:

- one canonical interrogation contract distinguishing stored state from fresh endpoint observation;
- challenge capability discovery;
- active liveness nonce/challenge/response;
- explicit NO_RESPONSE / UNSUPPORTED semantics.

## 8. Drift-relevant observations for the next formal step

This section records observations only. It MUST NOT be interpreted as formal completion of realignment step 4 while step 2/step 3 gates remain open.

1. R4-R6 successfully improved auto-attachment, client emission and provider-host ingress.
2. Those additions still depend on explicit events/anchors supplied by Chronicle, repository_dispatch, issue_comment, workflow execution, or explicit client metadata.
3. They do not yet establish one primary Presence Fabric that treats first controlled repository access/activity as the system entry point.
4. The current runtime has strong continuity after attachment, but incomplete discovery of presence before/at first observable access.
5. The current telemetry can represent action evidence, but liveness and progress are not first-class independent dimensions.
6. Correlator already fails closed correctly, but lacks the planned fingerprint and canonical UNBOUND_ACTIVITY lifecycle.
7. Dispatcher exists, but compatibility evaluation is narrower than original intent.
8. Provider-specific wake remains correctly outside the repository-only boundary when the provider exposes no programmable wake surface.

## 9. Correction queue for successor agents

This is an analysis-derived correction queue, not authorization to implement before the frozen gates permit it.

| ORDER_AFTER_GATES | CORRECTION | WHY NEEDED | MUST PRESERVE |
|---:|---|---|---|
| 1 | Canonical Presence/Activity observation contract | Presence-First is the main realignment gap. | R1-R6 history, safe observability, internal-transport exclusion. |
| 2 | Canonical exhaustive Connection Envelope projection/schema | Existing fields are fragmented and several are absent. | Existing session/Beacon/Forensics stores; no parallel DB. |
| 3 | Versioned connection_fingerprint | Historical target is entirely absent. | Provider ref remains observed/supplied-only; ambiguity fails closed. |
| 4 | Independent LIVENESS and PROGRESS projections | Heartbeat must not equal progress. | WATCH thresholds and observed-only cause policy. |
| 5 | Session interrogation + optional liveness challenge | Stored context is not the same as fresh endpoint response. | Read-only context authority; no mutation from challenge. |
| 6 | UNBOUND_ACTIVITY reconciliation | Real activity can exist without safe attribution. | Correlator levels and no auto-bind for probable/ambiguous. |
| 7 | Dispatcher compatibility expansion | Current standby selection is repository/state only. | Existing claims, collision domains, authority gates, dependencies, exact HEAD. |
| 8 | Agent Context completion | Resume view should expose deterministic peer/collision/next-safe-action semantics. | Existing canonical stores as sources of truth. |
| 9 | Tests-before-correction and final live E2E | Component green tests are not enough to declare origin realignment complete. | Frozen 24-step order and ultimate live completion gate. |

## 10. Acceptance scenarios that should become tests before corrective code

These are specifications only.

### AC-PRESENCE-001 — fresh agent first-touch

Given a fresh governed agent with no GACR registration instruction, when it performs a first repository operation through an instrumented controlled access path, then GACR records safe Presence/Activity evidence and deterministically CREATEs or RESUMEs one canonical session.

### AC-ENVELOPE-001 — complete provenance

Given a controlled GitHub/agent event, every canonical envelope field is either populated with provenance or explicitly UNKNOWN/UNAVAILABLE. No secret, cookie, token, raw transcript or private reasoning can enter the envelope.

### AC-FINGERPRINT-001 — operational fingerprint without provider impersonation

Given no native provider conversation reference, two observations belonging to the same bounded operational connection produce the same versioned fingerprint. The fingerprint may strengthen session correlation but provider_conversation_ref remains null. Ambiguous/colliding evidence does not auto-bind.

### AC-LP-001 — liveness without progress

Given periodic heartbeat and no action/HEAD/checkpoint/evidence advancement, liveness remains healthy while progress independently becomes quiet/stale. GACR must not report progress from heartbeat alone.

### AC-CHALLENGE-001 — optional liveness challenge

A challenge-capable endpoint responds to a nonce within expiry and proves fresh endpoint liveness. Replay is rejected. An unsupported endpoint returns UNSUPPORTED. Silence returns NO_RESPONSE/UNKNOWN, not a fabricated crash cause.

### AC-UNBOUND-001 — unbound activity reconciliation

Activity with insufficient attribution becomes UNBOUND_ACTIVITY. A later exact anchor reconciles it idempotently. Probable/ambiguous evidence never silently binds it.

### AC-DISPATCH-001 — compatibility-safe standby selection

With multiple standbys, Dispatcher evaluates repository, authority, capabilities, collision domains and dependencies. Only compatible capacity receives the offer. Wake does not grant mutation authority.

### AC-TAKEOVER-001 — exact-HEAD ownership transfer

A stalled predecessor retains claims. A successor cannot accept takeover against a stale HEAD. After exact reobservation and valid authority gates, ownership transfers once and predecessor cannot resume mutable work.

### AC-E2E-001 — ultimate live GACR acceptance

Execute, as one live chain:

fresh agent not explicitly told to register with GACR
→ first observable governed repository interaction
→ canonical session create/resume
→ real governed work
→ independent liveness and progress evidence
→ controlled loss of fresh evidence
→ SUSPECTED_STALL
→ STALLED / TAKEOVER_READY
→ second governed agent presence
→ deterministic predecessor stopping-point reconstruction
→ exact branch/HEAD reobservation
→ governed takeover acceptance
→ continuation of the same work
→ retained evidence proving every transition.

GACR origin realignment MUST remain incomplete until this exact live chain passes.

## 11. Current evidence snapshot used by this audit

Baseline facts reobserved or inherited from the authoritative OR-01 attestation:

- main audit base: 6a32debcc96d7c33b421dc901c514f79a4d05104.
- OR-01: PASS.
- canonical source session: session-68c97d4bb1ef71c86444de12.
- canonical provider: chatgpt.
- provider conversation ref: null, provenance UNAVAILABLE.
- historical internal transport session: session-cb22a4ed0d9e29eba5383f5d, CLOSED/SUPERSEDED.
- source sessions revision: 10.
- Beacons revision: 13.
- Correlator revision: 14.
- Forensics revision: 4.
- source claims: empty.
- source takeovers: empty.
- source dispatches: empty.
- OR-01 candidate Governance CI: 36954021583 PASS.
- OR-01 attestation PR: #123 merged as 3ebf1e962b7c176a7b9e2eaf44d0842feda8345d.
- post-merge Governance CI: 36954073273 PASS.
- post-merge GACR run: 36954073285 PASS.
- R6 live issue-comment evidence includes 5943461065, 5943497457, 5943559595 and 5943592733.
- exact-HEAD stale persistence guard was observed in scheduled run 36948763070.
- ultimate fresh-agent/stall/second-agent/takeover/continuation acceptance remains not run.

## 12. Formal gate note

This document answers the analytical question ORIGINAL_INTENT ↔ CURRENT_IMPLEMENTATION ↔ GAP and is designed so a successor can identify real corrections without redoing the R1-R6 audit.

However, as of main@6a32debcc96d7c33b421dc901c514f79a4d05104:

- GACR-OR-01 is PASS.
- docs/control-plane/GACR_PROGRAM.md still names the step-2 formal revalidation gate as the next action.
- .governance/control-plane-state/gacr-program.json still marks step_2 = FORMAL_GATE_NOT_YET_EXECUTED.
- step_3 remains formally BLOCKED_UNTIL_STEP_2_FORMAL_GATE_CLOSED.

Therefore:

- this artifact is PREPARED;
- GACR-OR-02 is NOT marked DONE here;
- GACR-OR-03 is NOT marked DONE here;
- no corrective implementation is started here;
- no runtime/workflow/script/schema/state is changed here;
- no global programme or P12-S6 state is changed here.
