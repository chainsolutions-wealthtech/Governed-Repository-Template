# CONTROL PLANE DECISIONS LOG

Append-only durable decisions for the source/control-plane repository.

| ID | Date | Decision | Status |
|---|---|---|---|
| CPD-001 | 2026-09-26 | Separate source/control-plane memory from distributed project-state templates. | ACCEPTED |
| CPD-002 | 2026-09-26 | GitHub issues are orchestration/evidence surfaces; source-only versioned authorities carry durable control-plane continuity. | ACCEPTED |
| CPD-003 | 2026-09-26 | `Patricked-code/MCP` remains an external independently governed dependency; this framework workstream may observe it and create intakes, but must not implement MCP changes. | ACCEPTED |
| CPD-004 | 2026-09-26 | A meaningful control-plane work boundary must persist current state, tasks, next action and checkpoint/handoff before a new conversation/agent resumes. | ACCEPTED |
| CPD-005 | 2026-09-26 | Source-only control-plane memory must be removed during client initialization and must be CI-tested against leakage. | ACCEPTED |
| CPD-006 | 2026-09-26 | Root `STATUS.md`, `SUIVI.md`, `NEXT_ACTION.md`, `HANDOFF.md` and generic machine projections remain distributed client templates and are not repurposed as source history. | ACCEPTED |
| CPD-007 | 2026-09-26 | Canonical chronological gates must not be compressed: STEP 4 normal-entry proof on the pilot precedes STEP 5 fresh-repository E2E. | ACCEPTED |
| CPD-008 | 2026-09-26 | `CREATE_NEW_REPOSITORY` must adapt to owner choices: MCP linking is optional; if enabled, `DIRECT_MCP_TOKEN`, `SSH`, or `BOTH` may be selected. `BOTH` is never mandatory merely because the framework supports it. | ACCEPTED |
| CPD-009 | 2026-09-26 | Canonical control-plane memory gets a reusable relational projection shared by all structuring cases; Git-versioned SQL/JSON remain auditable authority while mutable DB binaries are not canonical. | ACCEPTED |
| CPD-010 | 2026-09-26 | Future admin web UI will consume the relational model only after all structuring cases/parcours are validated; no premature front-end will define workflow semantics. | ACCEPTED |
| CPD-011 | 2026-09-26 | Owner feedback, decisions, checkpoints, handoffs, evidence and intakes are first-class relational records so workflows can return/revalidate without erasing history. | ACCEPTED |
| CPD-012 | 2026-09-26 | Every meaningful agent work session must persist observed HEADs, claimed task, actions, evidence/results, defects discovered, remarks/proposals and next action; Git commits alone are insufficient as the agent-work ledger. | ACCEPTED |
| CPD-013 | 2026-09-26 | Newly discovered tasks/subtasks must enter the canonical task queue before later workflow progression, preserving dependencies and a single executable next action. | ACCEPTED |
| CPD-014 | 2026-09-26 | `docs/control-plane/CANONICAL_ARCHITECTURE.md` (`CP-ARCH-001`) is the source-only durable target-architecture authority for the Governed Repository Platform. It defines four structuring cases plus `CONTINUE_GOVERNED_WORK` as a post-case mode and must never be confused with live current state. | ACCEPTED |
| CPD-015 | 2026-09-26 | Canonical memory evolves by append/supersede/revalidate: durable event/history records coexist with current projections, and canonical authorities use monotone revision history rather than silent replacement. | ACCEPTED |
| CPD-016 | 2026-09-26 | Git-versioned governed authorities remain foundational; SQL/JSON materialization, future PostgreSQL, API and Admin UI are projections/control surfaces and may not silently become independent sources of truth. | ACCEPTED |
| CPD-017 | 2026-09-26 | Agent/task lineage follows Architecture → Program → Case/Workstream → Phase → Integration Slot → Task → Subtask; new intake, defects and owner changes enrich the existing program instead of replacing it with parallel work. | ACCEPTED |
| CPD-018 | 2026-09-26 | Workflow semantics and the four case paths must be validated before Governance API/PostgreSQL/Admin UI implementation; frontend remains intentionally downstream of case stabilization. | ACCEPTED |
| CPD-019 | 2026-09-26 | Canonical memory and relational projection evolve together: every durable structured change (owner feedback, decision, agent activity, task/program change, evidence, checkpoint, handoff, intake, artifact or authority revision) must be persisted in Git authorities and, when representable by the relational model, projected into the versioned database seed/event model in the same governed change or explicitly marked pending projection. | ACCEPTED |
| CPD-020 | 2026-09-26 | Agent entry identity must separate PRINCIPAL, AGENT, CONNECTION and SESSION. Authenticated account data and permission snapshots should be captured automatically when available, then used to create/resume a stable governed session before role/authority/routing. Ambiguity fails closed; identity or role never creates authority. | ACCEPTED |
| CPD-021 | 2026-09-26 | After identity/session resolution on the control-plane source, routing is two-stage: first choose `WORK_ON_CONTROL_PLANE` or `APPLY_GOVERNANCE_CASE`; then either choose the control-plane work kind (`CODE_IMPLEMENTATION`, `EXECUTE_EXISTING_TASK`, `ADD_OR_ENRICH_INFORMATION`) or choose exactly one of the four structuring cases. Human participation is limited to answers/explicit approvals required by governance; authorized technical execution is automated by the system. | ACCEPTED |
| CPD-022 | 2026-09-26 | `chainsolutions-wealthtech/Governed-Repository-Template` is the product/framework and sole target of framework evolution. Repositories such as `Patricked-code/Gouvern` are external pilot/validation fixtures for exercising governance cases; their project state may reveal generic defects but must never become the framework architecture, roadmap, canonical program, or implementation target. Generic defects are fixed in the Template first, then validated on pilots. | ACCEPTED |
| CPD-023 | 2026-09-26 | Governed client upgrades derive the release version from the Template manifest, synchronize only reusable/static governance runtime-test-policy surfaces required by the current client CI, preserve mutable client project/session/work/answer state, and make source-only CI steps skip cleanly on clients. A pilot must never be patched to compensate for an incomplete Template upgrade surface. | ACCEPTED |
| CPD-024 | 2026-09-26 | Any self-test that simulates a fresh template/bootstrap from an instantiated client must rebuild every bootstrap-influencing synthetic state (profile, project-profile, infrastructure, local-entry, MCP binding, access plan, workflow model, work-items, claims, sessions and canonical-memory pointer) inside the temporary fixture. Real client state is never rewritten, and subprocess failures must expose diagnostic stdout/stderr. | ACCEPTED |

| CPD-025 | 2026-09-27 | The central Governance Model is a first-class reusable authority distinct from CREATE/ADOPT/MAP/LAB. The four structuring cases consume the model and must not silently redefine generic governance semantics. | ACCEPTED |
| CPD-026 | 2026-09-27 | Governance Model cataloguing extends the existing Git-versioned SQL/JSON relational memory and existing materializer. No second canonical database, duplicate memory subsystem or competing source of truth may be introduced. | ACCEPTED |
| CPD-027 | 2026-09-27 | The Governance Model Catalogue completion programme is recorded now as dependency-bound canonical backlog. It preserves the current CASE 1 unique executable task; catalogue execution follows CASE 1 closure and is organized as GMC-01..GMC-19 / phases A..G, before cross-case industrialization and API/UI work. | ACCEPTED |

| CPD-028 | 2026-09-27 | The 19 GMC identifiers are chronological work packages/groups, not atomic tasks. Before any GMC implementation, each group must receive an execution blueprint defining mission, objective, questions to resolve, prerequisites, exact sources/paths/symbols/tests/decisions to inspect, search order/method, atomic tasks/subtasks, classification rules, expected findings, outputs, canonical storage destination, required evidence, validation, DONE/HOLD criteria, and downstream consumers. Results produced by one group become versioned inputs for later groups. This preparation is planning only and must not start implementation. | ACCEPTED |

| CPD-029 | 2026-09-27 | Governance Model work-package progression is output-driven, not status-driven. Every GMC group must model three dependency dimensions — TASK_DEPENDENCY, ARTIFACT_DEPENDENCY and EVIDENCE_DEPENDENCY. Group results become persistent, versioned knowledge artifacts with stable IDs, provenance, validation state, producer, downstream consumers and append/supersede/revalidate history. Each group has explicit exit controls. GMC-G19 must assemble the complete Governance Model and separately demonstrate model completeness, consistency, reference integrity, implementation traceability, test/evidence/dependency coverage, reusability and CREATE/ADOPT/MAP/LAB compatibility before Governance Model 1.0.0 may be released. This remains planning-only until separately authorized. | ACCEPTED |

### CPD-030 — Configuration intent never authorizes discovery execution

- Date: 2026-09-29.
- Decision: owner answers describing MCP linkage, transport, endpoint, discovery scope, domain strategy or runtime mutation policy enrich configuration only.
- They do not authorize credential provisioning or a network discovery call.
- A concrete read-only discovery plan must be presented and explicitly approved before execution.
- Material changes to that plan, including endpoint recovery, invalidate prior discovery approval.
- Legacy pre-approval discovery evidence is preserved in history and the state re-enters the approval gate.
- This is additive to the existing local-entry, authority, exact-HEAD and Loop Engineering model.

### CPD-031 — Adaptive questionnaire feeds the existing Loop Engineering

- Date: 2026-09-29.
- Decision: no new questionnaire engine, task engine or parallel governance source is introduced.
- CREATE/ADOPT/MAP/LAB reuse the common Governance Model and existing project memory.
- Fresh observed facts and prior owner answers are reused instead of being re-asked.
- Only unknown facts or owner decisions are requested one at a time.
- Answers/observations enrich the project/resource model, classify resources as existing/unknown/planned/to-create/to-configure/to-verify, and derive prepared work-items, dependencies and authority requirements.
- Those prepared work-items are executed later by the existing Loop Engineering when their dependencies and authority gates make them READY.

### CPD-032 — Signed MCP SSH broker profile is factual recovery evidence

- Date: 2026-09-30.
- Decision: when the authenticated MCP repository-SSH broker signs a certificate for a host/port/username that differs from the configured non-secret SSH profile, the signed profile is treated as observed factual evidence.
- The Template must reopen SSH-profile recovery instead of blindly retrying the same configuration.
- The prior discovery evidence is archived, the corrected profile becomes configuration, and prior discovery approval is invalidated because the target is a material plan element.
- This does not grant SSH write authority.

### CPD-033 — Persistent MCP capability image feeds existing Loop Engineering

- Date: 2026-09-30.
- Decision: the central Template will maintain a source-only, versioned last-known MCP capability snapshot.
- The snapshot is refreshable through authorized read-only discovery when missing, stale, contradicted or required by a pending operation.
- It captures non-secret MCP identity/protocol, servers, tools/resources and their declared read/write surfaces, observed evidence, freshness/provenance, plus derived case-to-capability and prepared-operation mappings.
- It is knowledge/planning authority only: it never grants mutation authority and never stores tokens, private keys or secret values.
- CREATE, ADOPT, MAP, LAB and CONTINUE consume this knowledge through the existing project model/work-items/Loop Engineering. No parallel governance or task engine is created.
- MCP-side changes are not requested merely to maintain this snapshot; no new MCP intake is created unless a concrete missing external capability later blocks an authorized action.
- Relational projection is explicitly pending the scheduled Governance Model integration rather than creating a parallel database.

### CPD-034 — Capability model precedes MCP tool selection and owner questions

- Date: 2026-09-30.
- Decision: the MCP snapshot is an implementation image, not the questionnaire and not the target Governance Model.
- The Control Plane first resolves the project need into a stable capability, then maps that capability to the currently exposed MCP surface.
- Existing repositories are observation-first: fresh Git/repository facts, persisted project facts, prior owner decisions and authorized MCP observations resolve fields before any owner question is emitted.
- A fresh resolved fact must not be re-asked.
- CREATE and ADOPT/MAP/CONTINUE use the same capability/question resolver; CREATE simply has fewer initially resolved facts.
- Case plans are ordered capability sequences, not bulk tool lists.
- A missing mutation capability produces a prepared scoped-capability requirement only when a concrete authorized project operation needs it; it does not automatically create an MCP intake.
- Tool presence never grants authority. Tool absence never authorizes inventing or bypassing a surface.
- Outputs continue into the existing project model, work-items and Loop Engineering.

### CPD-035 — BOTH is dual-ready smart routing, not coupled execution

- Date: 2026-09-30.
- Owner clarification: selecting `BOTH` means prepare/configure both DIRECT MCP and governed SSH so the system can use either intelligently; it does not mean both must execute together.
- One operation selects one route according to capability, readiness, credential availability and failure state.
- A successful selected route satisfies the current discovery unless a distinct gate explicitly requires dual-route attestation.
- Alternate-route readiness is tracked independently and does not downgrade a successful selected route.
- The framework must not force rediscovery merely because another configured route later becomes available.
- Legacy evidence from Ekyc where DIRECT passed but the old coupled engine then failed on SSH may reuse the already-authorized DIRECT PASS after generic framework migration; the corrected SSH route remains independently attestable.

### CPD-036 — Adaptive questions are choice-based and observation-first

- Date: 2026-09-30.
- New questionnaire logic must extend the existing CREATE / ADOPT / MAP / LAB and Loop Engineering model; no parallel engine.
- Questions are asked one at a time.
- Answers are choice-based by default. Values such as repositories, servers, domains, paths, runtimes and databases should be presented as dynamic choices derived from observation rather than requested as free-form text.
- Fresh factual observations are reused automatically and are not re-asked.
- Owner/business decisions remain explicit choices even when observations provide candidates.
- Every answer may classify, derive, prepare, schedule or gate future work, but never grants execution authority by itself.
- Long implementation is decomposed into small resumable slices with source-only unit/E2E tests before runtime binding.
- AfricaFunds is a worked ADOPT_EXISTING example only; generic logic must not hard-code AfricaFunds.

### CPD-037 — Reusable knowledge must prevent redundant discovery

- Date: 2026-09-30.
- The Control Plane must persist reusable knowledge so a new agent does not repeatedly rediscover the same stable project/server/provider/governance facts.
- Knowledge is layered by stability: target model, question/decision model, MCP capability semantics, provider knowledge, server-organization knowledge, project facts, owner decisions, candidate conventions and volatile operational evidence.
- Every reusable project fact must carry provenance and freshness semantics.
- Fresh current facts and prior owner decisions are reused before discovery or questioning.
- Volatile/action-sensitive facts are refreshed only when the pending operation requires current evidence or when contradiction/scope change invalidates stored knowledge.
- Observed cross-project conventions remain candidate patterns until explicitly promoted by governance; one project's layout never silently becomes a universal rule.
- Knowledge never grants execution authority and must not persist secret values or sensitive connection coordinates.
- This extends existing relational/canonical memory; it does not create a parallel runtime or database.

### CPD-038 — Server knowledge includes platform inventory and operational recipes

- Date: 2026-09-30.
- The Control Plane must understand S1/S2 as managed platforms, not merely as hosts.
- Durable server knowledge therefore contains both:
  1. structured inventory of organization/configuration/capabilities; and
  2. governed operation recipes describing how to create/configure/deploy/verify/rollback project resources.
- Inventory covers hosting, networking, DNS, TLS, vhosts, filesystem conventions, runtimes, ports, databases, Git/deployment, secrets metadata, scheduling, observability, backup/recovery, security/access, capacity, project mappings and MCP surfaces.
- Governed path templates and named project paths may be persisted when needed for planning/operation; unbounded filesystem dumps remain prohibited.
- Recipes never grant authority. Execution remains gated by capability, scoped authority, live preflight and existing Loop Engineering.
- Existing server conventions should be reused when valid before inventing a new layout.
- Detailed live S1/S2 inventory collection is a later bounded read-only slice, not part of this change.

### CPD-039 — GitHub and server credentials have a complete governed lifecycle

- Date: 2026-09-30.
- The governed platform has two operational planes: GitHub and server/production.
- A cross-cutting identity/credential/secret model links them.
- The Control Plane must know for every required action:
  - which identity performs it;
  - which credential type is required;
  - whether it can be reused, minted, created, rotated or revoked;
  - where the credential is securely sourced;
  - how it is injected;
  - how presence/scope are verified without secret-value readback;
  - how it is rotated and revoked.
- Provider-native and short-lived identities are preferred over persistent credentials.
- GitHub App installation tokens and GitHub OIDC are preferred patterns where supported.
- Server access should prefer ephemeral SSH certificates or scoped service identities.
- GitHub Actions secrets, server application secrets, database credentials, DNS credentials and TLS private keys are represented by references/metadata only.
- Credential possession never implies execution authority; mutations still require the existing scoped AuthorityEnvelope/gates.

### CPD-040 — One governed execution adapter for GitHub and production

- Date: 2026-09-30.
- The server recipes, identity/secret lifecycle and GitHub administration surfaces are now executable through one source-control-plane adapter: `CP-EXECUTION-001`.
- This adapter extends existing Loop Engineering; it does not introduce a parallel task engine.
- Execution is package-driven, dry-run by default and fail-closed.
- Side effects require explicit persisted authority and, when repository-scoped, an exact target HEAD.
- MCP steps must bind a capability to a tool present in the current canonical capability snapshot and their arguments must satisfy the live tool input contract.
- GitHub operations use explicit allowlisted endpoint builders; arbitrary GitHub URLs/methods are forbidden.
- Credentials are supplied only by runtime references/minting. Values are not serialized into packages or receipts.
- Every mutation path is structured as preflight → execute → verify → rollback/evidence.
- Missing generic MCP production capabilities remain explicit blockers. The Template must not create speculative/broad MCP intake merely because the executor supports the future intent.

### CPD-041 — Project knowledge compiles into executable packages without speculative capability widening

- Date: 2026-09-30.
- Project requirements, owner decisions and bounded GitHub/server observations must compile into the existing `CP-EXECUTION-001` package format before execution.
- The compiler reuses known observations first and derives deterministic facts such as a subdomain FQDN from selected parent + label.
- An MCP tool is auto-bound only when its live catalogue contract, capability classification and project scope unambiguously match the requested operation.
- A project not present in an existing MCP project allowlist is never silently added or treated as supported.
- Missing capabilities become explicit blockers in the package plan; this compiler does not create MCP intake automatically.
- GitHub secret metadata can classify CREATE versus ALIGN/ROTATE without reading the secret value.
- Existing CASE 1 chronology and owner domain-binding decision remain unchanged.

### CPD-042 — Project decisions compile into one governed execution DAG

- Date: 2026-10-01.
- Project-level owner decisions compile into a dependency-ordered graph of existing `CP-EXECUTION-001` intents rather than ad-hoc commands.
- The graph may contain GitHub, credential, server, domain, database, deployment, observability, backup and production-attestation nodes.
- Each node retains its own exact-head, authority, capability, credential and verification contract.
- Existing Loop Engineering remains the scheduler; the adapter releases at most one executable node at a time.
- A PASS receipt advances only the matching node and unlocks dependents monotonically; stale state revisions fail closed.
- Missing MCP capabilities remain explicit blockers and never trigger automatic intake creation.
- The Ekyc S2 + subdomain fixture is E2E dry-run proof only; no Ekyc mutation is included.

### CPD-043 — Server identity and secret knowledge is bounded metadata, never values

- Date: 2026-10-01.
- S1/S2 identity and secret-store knowledge is collected only through allowlisted read-only MCP surfaces.
- The persisted/returnable representation contains mechanism classifications, structural metadata and response digests only.
- Raw remote payloads, secret values, bearer tokens, passwords, private keys, environment values and server connection coordinates are never persisted.
- `scan_mcp_secrets_s1` is usable because its live catalogue contract is read-only and explicitly states that it does not display secret values.
- Absence of an equivalent S2 secret-scan surface is represented as `NOT_EXPOSED` / `UNKNOWN_DISCOVERABLE`; it is never inferred away.
- The mapper classifies each credential mechanism as runtime-mintable, capability-available, modelled-capability-gap or model-missing.
- This knowledge does not grant execution authority.

### CPD-044 — Safe server identity-secret metadata is persisted as canonical facts

- Date: 2026-10-01.
- Validated KBI-04K metadata may be persisted as canonical Control Plane facts only after source-model and MCP-snapshot reconciliation.
- Mechanism classifications are recomputed from `CP-IDENTITY-SECRET-001` and `CP-MCP-CAP-001`; incoming observations cannot invent a credential mechanism or capability.
- Persisted probe facts contain only safe status/shape/digest metadata. Raw MCP responses, secret values, passwords, bearer tokens, private keys and server connection coordinates remain forbidden.
- Persistence is revision-guarded and atomic; exact replay is idempotent, older observations and same-timestamp contradictions fail closed.
- Facts carry provenance and freshness classes:
  - credential mechanism classification → `EVENT_AND_NEED_BASED`;
  - read-only server probes → `LIVE_OR_BOUNDED_TTL`.
- The same validated facts are projected into canonical relational memory through `server_identity_secret_facts`.
- Persistence grants no execution authority.

### CPD-045 — Server identity-secret facts refresh through read-only observation and governed PR

- Date: 2026-10-01.
- KBI-04O operationalizes the already implemented KBI-04K collector and KBI-04N persistence adapter.
- The refresh is event/need based, not scheduled polling.
- It performs only allowlisted read-only MCP probes.
- The transient observation is written only to a runner-local restrictive temporary file and is deleted before persistence.
- Only validated status/shape/digest metadata may enter canonical state.
- Persistence is guarded by the exact current `server-identity-secret-facts.json` revision.
- A source-repository GitHub App token is minted only to create the governed branch/PR after validation.
- No MCP/server mutation, secret readback, raw payload persistence, server connection coordinate persistence or execution authority is introduced.

### CPD-046 — Fresh project production-server choice precedes domain planning

- Date: 2026-10-01.
- Owner correction: when a fresh project has no existing infrastructure binding, the system must choose the production server before asking how to create or bind a domain.
- Read-only discovery supplies server candidates and server-scoped domain inventory, but does not choose the production target on behalf of the owner.
- Canonical order:
  `DISCOVERY → PRODUCTION_SERVER_SELECTION → SERVER_SCOPED_DOMAIN_PLANNING → REMAINING_SETUP`.
- The production-server answer is a project decision only; it grants no runtime/server mutation authority.
- Once a server is selected, domain planning must reuse the already-authorized discovery evidence for that server rather than rediscovering the same inventory.
- Existing/adopted projects keep observation-first reuse semantics; this correction specifically closes the fresh-project sequencing gap without replacing the adaptive questionnaire or Loop Engineering.

### CPD-047 — Domain planning is a server-scoped choice chain

- Canonicalization note: this decision was initially introduced with the already-used identifier `CPD-041`. Its semantic content is preserved; only the canonical identifier is disambiguated under `CP-NAMESPACE-001`.

- Date: 2026-10-01.
- A fresh project first selects its production server.
- Domain planning then proceeds one owner choice at a time rather than requesting one free-form domain object.
- The domain intent is selected before parent/name details.
- Existing-domain and parent-domain options are populated from the already-authorized inventory of the selected server.
- Subdomain/child-domain label choices may use deterministic suggestions plus an explicit custom option.
- The resulting binding is derived automatically and future execution capabilities/authority requirements are prepared.
- Domain answers never authorize DNS, vhost, TLS or server mutations.
- Existing projects/states with an already answered `domain_binding` are preserved and must not be re-questioned merely because the questionnaire model evolved.

### CPD-048 — Canonical namespace and work registry prevents semantic ID collisions

- Date: 2026-10-01.
- Authority `CP-NAMESPACE-001` owns the canonical namespace and work-ID rules.
- The registry does not duplicate the task/programme catalogues; it derives identity validation from their existing canonical definition sources.
- Every new canonical identifier must match exactly one registered namespace.
- Duplicate canonical definitions fail CI and HOLD_FOR_REVIEW.
- New work must extend the existing architecture/programme lineage and declare parent/integration-slot metadata before runtime binding.
- Multi-agent collision prevention combines namespace uniqueness with existing sessions, claims, collision domains, dependency-safe dispatch, single-writer rules, exact-HEAD guards, checkpoints and handoffs.
- Historical collisions are preserved through explicit reconciliation/supersession rather than silent overwrite.

### CPD-049 — GACR provides governed agent continuity and failover

- Date: 2026-10-01.
- Authority `CP-AGENT-RELAY-001` defines **GACR — Governed Agent Continuity Relay**.
- GACR extends the existing session / claim / checkpoint / handoff model; it does not introduce a parallel task engine.
- Active agents carry heartbeat/lease metadata. Late agents become `SUSPECTED_STALL`; expired leases become `STALLED / TAKEOVER_READY`.
- A stall never silently releases an active mutable claim.
- A standby successor may receive a takeover offer, but mutable ownership transfers only after exact branch/HEAD reconciliation.
- External provider conversation IDs/URLs are correlation metadata only and are persisted only when explicitly supplied; provider IDs are never invented.
- Full external conversation URLs are not persisted by default; known provider URLs may be reconstructed from explicitly stored provider references.
- Scheduled supervision may detect and prepare takeover automatically, but GitHub cannot universally wake an arbitrary browser conversation. Provider/orchestrator wake-up remains an optional external integration.
- GACR contributes to the existing `IDN-004/005/006/010` and `RTE-008/012` objectives without marking those broader workstreams complete.

### CPD-050 — GACR source runtime memory is isolated from distributed client state

- Date: 2026-10-01.
- GACR keeps the Control Plane source's own agent/session continuity separate from runtime state distributed to governed client repositories.
- On the Template source, GACR sessions, claims and takeover queue live under `.governance/control-plane-state/gacr-*.json`.
- In initialized/adopted clients, GACR continues to use the repository-local `.governance/sessions`, `.governance/work/claims.json` and `.governance/agent-relay/takeovers.json` surfaces.
- The generic GACR configuration, automation, schemas and documentation remain distributed.
- Source agent/conversation history must never be copied into a client repository.
- This is a boundary correction to `CP-AGENT-RELAY-001`, not a new programme or task engine.

### CPD-051 — GACR Beacon, Correlator and Dispatcher make agent activity reconstructable

- Date: 2026-10-01.
- `CP-AGENT-RELAY-001-R2` extends GACR with three additive components:
  - **Beacon** captures safe connection/action telemetry from the agent and allowlisted GitHub context;
  - **Correlator** links beacons to governed sessions using explicit references first, then fail-closed multi-signal correlation;
  - **Dispatcher** converts a governed takeover offer into a target-specific wake/relay dispatch.
- Correlation levels are `EXACT / STRONG / PROBABLE / AMBIGUOUS / UNKNOWN`.
- Only `EXACT` and unique `STRONG` evidence may auto-select a session. Probable/ambiguous evidence never auto-binds.
- GitHub context is allowlisted; raw event payloads, tokens, secrets, cookies and authorization headers are never persisted.
- A session may carry an optional `client_instance_id`, agent role, declared capabilities, wake channels and opaque bridge registration reference.
- `GET agent-context` semantics aggregate session, claim, takeover, dispatch, beacons, correlations and repository HEAD for deterministic resume.
- An optional external bridge webhook can receive idempotent wake events. A wake event grants no write authority; exact-HEAD takeover acceptance remains mandatory.
- GitHub cannot infer a provider conversation URL that the provider/client never supplied. A client/browser bridge may submit that reference explicitly without exposing page content or cookies.
- This extends existing `IDN-002/004/005/006/008/010` and `RTE-008/012`; it is not a parallel programme.

### CPD-052 — GACR Interruption Forensics is an observed-evidence resume projection

- Date: 2026-10-01.
- `CP-AGENT-RELAY-001-R3` adds Interruption Forensics to the existing GACR chain.
- FORENSICS consumes sessions, claims/collision domains, takeovers, Beacon events, Correlator results and Dispatcher state; it does not introduce a parallel task engine or canonical database.
- Beacon may carry optional safe action-trace metadata: action ID/label/phase, tool name/call ID, outcome, written HEAD, checkpoint/evidence reference and an explicit interruption code.
- External interruption causes are observed-only. Missing provider/client evidence remains `UNOBSERVED_EXTERNAL_CAUSE`; GACR must never infer crash/timeout/network/tool failure from absence of heartbeat alone.
- An in-flight action may not be replayed blindly. Exact-HEAD reobservation and existing claim/authority gates remain mandatory.
- No independent lock store is created; claims + collision domains + exact-HEAD remain the canonical mutable-ownership model.
- This is cross-cutting hardening and does not replace or advance the programme-level priority `P12-S6`.

### CPD-053 — Governed arrivals auto-attach to GACR from the strongest observable anchor

- Date: 2026-10-02.
- `CP-AGENT-RELAY-001-R4` makes GACR attachment automatic for observable governed arrivals.
- A provider conversation ID/URL is optional correlation metadata, not a prerequisite for attachment.
- Source attachment priority is explicit client/provider metadata → fresh active Conversation Chronicle → GitHub Actions execution identity.
- A Chronicle anchor uses its durable `chronicle_id + current_session` pair and does not become business authority.
- Late explicit provider metadata enriches the same connection-bound session; session duplication on late binding is forbidden.
- Provider conflicts and ambiguous connection matches fail closed.
- Repository automation state-persistence pushes must not recursively auto-attach.
- Auto-attachment grants no mutation authority and preserves claims, collision domains, exact-HEAD reconciliation and existing takeover gates.
- This is cross-cutting GACR hardening and does not execute or replace `P12-S6`.

### CPD-054 — GACR client liveness uses a generic safe emitter with explicit provenance

- Date: 2026-10-02.
- `CP-AGENT-RELAY-001-R5` adds the generic client liveness and trace emitter.
- The emitter uses existing `repository_dispatch` events rather than introducing a parallel transport or task engine.
- `CLIENT_EMITTER` identifies the originating client even when GitHub Actions transports the event.
- Runtime transport credentials are process-environment inputs only and must never be copied into GACR payloads, events or repository state.
- Supported client operations are auto-attach, heartbeat, action/tool trace, explicit interruption signal, session resolution and wake polling.
- Interruption codes are emitted only for events actually observed by the client/host; silence alone never creates an interruption cause.
- Wake polling is informational and never auto-accepts takeover.
- Exact-HEAD reconciliation, claims, collision domains and authority checks remain unchanged.
- Hosts that cannot execute or invoke a client emitter remain partially observable; the system must not claim continuous client liveness in that case.
- This is cross-cutting GACR work and does not execute or replace `P12-S6`.

### CPD-055 — GACR internal transport is never an agent/session identity

- Date: 2026-10-02.
- Post-R5 attestation observation found that when the active Conversation Chronicle exceeded its freshness window, the `Governed Agent Continuity Relay` workflow itself was incorrectly accepted as a GitHub Actions attachment anchor.
- The resulting GitHub Actions session is a transport-classification defect, not a second user/agent conversation.
- The internal GACR workflow is therefore explicitly classified as transport/runtime infrastructure and may never create a governed agent session.
- When no explicit client, fresh Chronicle or external GitHub worker anchor is observable, push-triggered auto-attach returns a successful no-op `GACR_AUTO_ATTACH_SKIPPED` and may refresh derived correlations only.
- Stale Chronicle evidence is not made fresh artificially and is not used to fabricate liveness.
- A genuine external GitHub worker remains an eligible attachment anchor.
- Erroneously created transport sessions are preserved in history but closed/superseded; they are never silently deleted.
- CLOSED / HANDOFF_STALLED sessions are excluded from Correlator candidates.
- This corrective decision remains within `CP-AGENT-RELAY-001-R5` and does not alter `P12-S6`.
