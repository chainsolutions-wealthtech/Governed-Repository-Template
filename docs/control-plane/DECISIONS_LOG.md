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

### CPD-056 — Provider hosts may use a governed GitHub issue-comment ingress for GACR telemetry

- Date: 2026-10-02.
- GACR R1-R5 remains the generic continuity core.
- When a provider host cannot invoke `repository_dispatch` directly but can create GitHub issue comments, a configured dedicated issue may act as a transport adapter into the existing GACR runtime.
- The issue channel is telemetry ingress only; it is not a task queue, authority source or replacement execution engine.
- Accepted comments use schema `gacr-host-event/v1` after prefix `/gacr-host `.
- Only the configured issue and repository-authorized actor associations are accepted.
- Secret-like keys, raw transcript/prompt/response fields and oversized/unrecognized payloads fail closed.
- GitHub issue comment ID is the immutable ingress evidence/idempotency key; rerunning the same event must not duplicate state.
- The adapter reuses existing auto-attach, heartbeat, Beacon, Correlator and Interruption Forensics surfaces.
- It must never revive a genuinely `STALLED / TAKEOVER_READY` predecessor by bypassing exact-HEAD takeover reconciliation.
- Host telemetry never grants code, infrastructure or production mutation authority.
- Source runtime history remains isolated from distributed clients.

### CPD-057 — GACR future evolution is governed by the non-destructive Presence-First origin realignment plan

- Date: 2026-10-02.
- Owner correction: GACR R1-R6 contain useful continuity mechanisms, but the evolution drifted away from the original center of gravity.
- R1-R6 are preserved; no rollback, deletion or replacement is authorized by this decision.
- The primary future invariant is presence-first: a governed agent/conversation using an instrumentable repository-access surface must become observable to GACR from that interaction without needing to remember to explicitly invoke GACR.
- The canonical ordered plan is `docs/control-plane/GACR_ORIGIN_REALIGNMENT.md`, with machine projection `.governance/control-plane-state/gacr-origin-realignment.json`.
- The plan freezes a 24-operation order: preserve/reobserve R6; reconstruct original intent; map current implementation and gaps; identify drift; write acceptance tests before correction; introduce Presence Fabric; instrument controlled access; derive presence/activity; separate liveness from progress; add session interrogation/liveness challenge; reconcile unbound activity; reuse existing GACR components; then prove the fresh-agent/stall/second-agent exact-HEAD takeover/continuation scenario live.
- Liveness and progress are distinct. Heartbeat alone must never be promoted to proof of progress.
- Proprietary silent access that exposes no event or hook remains explicitly unobservable rather than being fabricated as observable.
- Safe GACR observability excludes cookies, tokens, secrets, raw transcript bodies and private reasoning.
- GACR origin realignment may not be declared complete until the live ultimate acceptance scenario passes.
- Registering this decision does not advance or replace `P12-S6_CLOSE_CREATE_NEW_REPOSITORY_CASE`.


### CPD-058 — GACR has its own programme authority and preserves the original two-limit stop point

- Date: 2026-10-02.
- GACR is a distinct technical programme inside the repository; it is not a chronological sub-step of the global Control Plane programme.
- Canonical GACR programme authority is `docs/control-plane/GACR_PROGRAM.md`.
- Canonical historical-intent authority is `docs/control-plane/GACR_ORIGINAL_INTENT.md`.
- The historical stop point records an operational GACR baseline followed by two external limits: richer automatic connection/session identification and actual relay/activation of compatible standby capacity.
- The intended additive architecture is `BEACON → WATCH → CORRELATOR → DISPATCHER`, preserving the existing GACR core.
- The original Connection Envelope, connection fingerprint, correlation confidence levels, optional Bridge/provider adapter, Agent Context and Dispatcher activation semantics are durable GACR requirements.
- Provider conversation identity is never invented. Missing provider-private data remains unknown while repository/task/branch/PR/HEAD/claim/action/evidence continuity may still be known.
- A global task such as `P12-S6` is not a functional dependency of GACR.
- Owner sequencing remains explicit: finish GACR first; return to the global programme only after owner OK.


### CPD-059 — GACR Step 2 formally revalidates canonical original intent

- Date: 2026-10-02.
- The canonical historical intent in `docs/control-plane/GACR_ORIGINAL_INTENT.md` is revalidated without rewrite.
- The two external limits, `BEACON → WATCH → CORRELATOR → DISPATCHER`, Connection Envelope, connection fingerprint, explicit correlation confidence, optional Bridge/provider adapter and Agent Context remain durable requirements.
- Provider-private facts remain unavailable when not supplied; no conversation identity may be invented.
- R1-R6 family behavior is preserved and no runtime/workflow/script/schema change is authorized by this gate.
- GACR remains distinct from the global programme; `P12-S6` is untouched and is not a dependency.
- Step 2 is closed; Step 3 gap-matrix formalization becomes the next authorized gate.


### CPD-060 — GACR Step 3 canonizes the original-intent gap matrix

- Date: 2026-10-02.
- After formal Step 2 revalidation, `docs/control-plane/GACR_INTENT_IMPLEMENTATION_GAP_MATRIX.md` becomes the canonical Step 3 `ORIGINAL_INTENT ↔ CURRENT_IMPLEMENTATION ↔ GAP` artifact.
- The matrix contains 28 requirement rows: 14 `COMPLETE`, 8 `PARTIAL`, 4 `MISSING`, and 2 `EXTERNAL_BOUNDARY`.
- The four missing requirements are the versioned `connection_fingerprint`, supported active liveness challenge, canonical `UNBOUND_ACTIVITY` lifecycle, and the ultimate live fresh-agent/stall/second-agent/exact-HEAD takeover/continuation acceptance chain.
- Partial areas include Presence-First, Correlator signal completeness, Dispatcher compatibility, optional Bridge execution, deterministic Agent Context, canonical Connection Envelope, independent LIVENESS/PROGRESS semantics, and unified session interrogation.
- This decision authorizes the matrix as analysis input only; it does not authorize corrective runtime implementation.
- Step 4 — R4-R6 center-of-gravity drift identification — is next. `P12-S6` and the global programme remain untouched.

### CPD-061 — Governed repository access requires admission, qualification and an Access Grant before function exposure

- Date: 2026-10-02.
- Owner rule: an authenticated GitHub identity is no longer sufficient, by itself, to expose governed repository functions to an agent.
- Canonical specification: `docs/control-plane/GSCC_ADMISSION_ACCESS_GATE.md`.
- The admission path is additive to the existing GSCC/GSE/GACR architecture and must not introduce a second session store, correlator, claim store, takeover engine or function-exposure authority.
- The existing GSCC Observable Arrival Gateway (`.github/workflows/gscc-observable-arrival.yml` + `scripts/gscc_observable_arrival.py`) is explicitly preserved. The admission/access layer sits above governed repository access and reuses the existing controlled arrival/SessionEndpoint/auto-attach chain rather than replacing it. GitHub-event-visible arrivals may still be observed first, but such observation is presence evidence only and never constitutes preauthorization or access authority.
- The canonical state distinction is `IDENTITY != ADMISSION != PREAUTHORIZATION != ACCESS AUTHORIZATION != FUNCTION EXPOSURE != MUTATION AUTHORITY`.
- A safe `gscc-admission-envelope/v1` must provide the required identity/client/session/connection/target/intent/continuity/capability facts, with explicit provenance and `UNAVAILABLE` for provider-private facts that are not exposed.
- Tokens, cookies, passwords, authorization headers, private keys, raw prompts, transcripts, raw tool arguments/results and private reasoning are forbidden from the admission plane.
- A valid initial dossier may yield only `PREAUTHORIZED`; preauthorization exposes a restricted qualification surface and does not expose arbitrary repository read/write functions.
- Qualification must establish the canonical session, required governance reads, current repository baseline, exact HEAD, task/claim/collision context, tested control capabilities, challenge/ACK evidence when required, and an initial GSE session state before access policy evaluation.
- An `Access Grant` makes the session eligible to request governed function exposure. It does not itself grant invocation or mutation authority.
- The existing `scripts/gscc_function_exposure_gate.py` and `.github/workflows/gscc-function-exposure-gate.yml` remain the sole canonical function-exposure authority. Their future route must require Admission Receipt and Access Grant validation before the existing session/HEAD/contract/authority/preflight/exposure checks.
- The raw MCP catalogue remains planning evidence only and is never the exposed function surface.
- A successor/takeover agent must complete its own admission and receive its own Access Grant; predecessor grants are not transferable.
- This requirement is `SPECIFIED / NOT_IMPLEMENTED`. Recording it grants no repository, mutation or production authority.
- Because this owner rule is stronger than the previously queued live function-exposure proof, Step 13B and the live `gscc_function_exposure_request` remain blocked until the admission/access gate is implemented tests-first and attested on current main.
- The global Control Plane programme is untouched: `P12-S6` remains its own unique global next action and is not advanced by this decision.


### CPD-062 — Canonical qualification evidence must be harvested, not trusted from the caller

- Date: 2026-10-02.
- The GSCC Admission Gate may accept safe host/provider facts at admission, but facts that GSCC can independently verify or resolve must be harvested from canonical authorities before an Access Grant is eligible.
- Repository identity, repository metadata, requested/default branch and exact HEAD are re-observed from GitHub.
- Session selection reuses the existing canonical admission→GACR session binding and existing GACR ConnectionEnvelope; no parallel correlator or session store is authorized.
- Governance reading is represented by bounded document-path/digest evidence tied to the observed repository state.
- Task and claim references are reconciled against canonical stores when present.
- Declared capabilities, control reachability, GSE state and access policy are not promoted to verified/allow states without canonical evidence. Missing evidence remains explicit and keeps qualification incomplete.
- Caller-provided `qualification_evidence_json` is not an authority source for the canonical qualification path.
- The canonical qualification bundle is identified as `gscc-qualification-evidence/v1`, records `GSCC_ADMISSION_HARVESTER` as its producer and carries an integrity digest. This digest is integrity evidence, not a credential and not a substitute for canonical-source observation.
- Provider-private identity remains supplied-only; unavailable values are not inferred.
- Admission, harvesting and Access Grant issuance continue to grant neither invocation nor mutation authority.
- PR #163 carries the tests-first implementation. Step 13B remains blocked until integration/post-merge proof and a real canonical admission flow are observed.
- The global Control Plane programme remains independent; P12-S6, CASE 1 and GMC are not advanced by this decision.


### CPD-063 — Admission control proof reuses the GACR Host Issue Bridge and baseline access defaults to read-only deny-by-default

- Date: 2026-10-02.
- GSCC admission capability verification must use an observable bidirectional proof, not client declaration alone.
- The existing GACR Host Issue Bridge and canonical `gacr-dispatches.json` are reused for the provider/host control proof. No parallel dispatcher, control store, session store or correlator is authorized.
- A liveness challenge is time bounded, non-authorizing and correlated by dispatch, command, correlation, challenge and nonce identities.
- A canonical minimum control proof requires an acknowledged command followed by a fresh, correlated challenge response. Replays, expired commands, responses before ACK and identity mismatches fail closed.
- The proof may verify `COMMAND_RECEIVE`, `COMMAND_ACK` and `CHALLENGE_RESPONSE`; it does not imply support for unrelated report capabilities.
- GSE admission state is projected on demand by the existing Session State Engine from canonical session/control evidence. No dedicated persistent GSE admission store is created.
- The canonical baseline admission policy defaults to DENY and may allow only `READ_ONLY_DISCOVERY_AUTHORITY` for the bounded read-only capability set after session, exact-HEAD, capability, control and GSE prerequisites are satisfied.
- Access Policy ALLOW is only eligibility for a bounded Access Grant. It is not function invocation authority. The existing Function Exposure Gate still requires function-specific authority evidence, and mutation-capable functions still require explicit mutation authority plus live preflight.
- PR #163 provides the tests-first candidate. Its controlled Q12 path is green, but real provider/host challenge proof on canonical main remains NOT_EXECUTED.
- Step 13B and ultimate live acceptance remain NOT_EXECUTED / NOT_PASSED.
- The global Control Plane programme remains independent; P12-S6, CASE 1 and GMC are untouched.

### CPD-064 — The draft GSCC Entry Context Gate is superseded by Admission + canonical qualification

- Date: 2026-10-05.
- Draft PR #157 introduced a separate `gscc-entry-context/v1` gate before CPD-061/062 were defined.
- Its core safety intent is retained: provider/host facts must be bounded and secretless, while repository facts that GSCC can verify must be independently observed.
- The canonical architecture now satisfies this intent through the stronger chain `AdmissionEnvelope → PREAUTHORIZED → canonical Harvester/Q1→Q12 → Access Grant → existing Function Exposure Gate`.
- No second entry receipt or parallel function-exposure prerequisite is authorized.
- Provider-private `agent_identity` is not promoted back to REQUIRED; unavailable provider-private identity remains explicitly unavailable.
- A host-declared `function_surface` is not access authority and must not constrain or broaden the canonical function catalogue. Requested capabilities are declarations; the canonical capability snapshot, Access Grant, route policy, authority evidence and per-function exposure receipt govern actual exposure.
- GitHub-verifiable repository/branch/HEAD facts are harvested from canonical GitHub state and are not trusted merely because the host supplied them.
- PR #157 is therefore `SUPERSEDED_BY_CPD_061_CPD_062_AND_PRS_159_163_175` and must be closed without merge.
- This decision changes no runtime authority, does not execute Step 13B, and does not advance P12-S6 / CASE 1 / GMC.

### CPD-065 — Queued GACR relay ingress reconciles to live default branch before BASE_HEAD capture

- Date: 2026-10-05.
- Live post-merge evidence showed that a `repository_dispatch` can be queued with an event HEAD that is already behind canonical main by the time its Relay job starts.
- This queue-age condition is not a real post-capture concurrency conflict and must not be conflated with one.
- `issue_comment` and `repository_dispatch` Relay ingress therefore reconcile to the current repository default branch immediately before `BASE_HEAD` capture and command execution.
- Event payload facts remain the observation source; reconciling the code/state checkout does not rewrite the event's observed identity or authority.
- The existing post-execution `HEAD_MOVED` comparison remains mandatory. A remote movement that occurs after `BASE_HEAD` capture still fails closed; no automatic rebase or replay of mutation/takeover authority is introduced.
- PR #177 implements and tests this rule. Post-merge downstream run `37386713402` proves the reconciled `repository_dispatch:gacr_auto-attach` path succeeds.
- This decision grants no new execution, mutation, claim-transfer or takeover authority and does not advance P12-S6.



### CPD-066 — Provider First Touch uses minimal signal and repository-owned enrichment

- Date: 2026-10-06.
- Decision: the provider/host emits only the minimum First Touch signal it alone can know or observe. The governed repository is authoritative for read-only enrichment of GitHub repository state before First Touch normalization.
- Repository-observable facts such as repository metadata, default branch, current HEAD, commit/tree metadata and Actions state are collected by the repository-side workflow and projected into the existing canonical field registry with explicit provenance.
- Provider-only identity/runtime/session facts remain provider-sourced or explicit `UNAVAILABLE`; the repository must never infer a conversation identity from GitHub actor + repository alone.
- Missing stable provider identity does not suppress capture. It yields an enriched `UNRESOLVED` capture and blocks Q1 until identity becomes strong/exact.
- Workflow-token permissions are evidence only for the workflow credential and must not be misrepresented as private scopes of the originating ChatGPT/GitHub connector.


### CPD-067 — First repository access response must carry the mandatory next-path directive

- Date: 2026-10-06.
- Owner requirement: the first governed repository access response presented to an agent/conversation must not expose repository metadata, permissions or GitHub access facts alone.
- The response surface that mediates the GitHub/API/GitHub-App result to the agent must also return an explicit mandatory next-step directive pointing to `/00_GSCC_ENTRY.md`.
- Canonical response semantics are:
  - preserve the underlying GitHub response facts such as repository identity, permissions, default branch and other safe metadata;
  - add a governance-entry directive with `required=true`, `priority=0`, `path=00_GSCC_ENTRY.md` and an instruction equivalent to `READ_BEFORE_ANY_OTHER_REPOSITORY_OPERATION`;
  - treat this directive as the first navigation instruction for governed admission;
  - do not treat a successful raw GitHub/API read as governed admission.
- This reuses the existing governed-response pattern already present in the control plane, where responses carry machine-readable routing such as `required_reads`, `next_request`, `allowed_next_operation` and handoff data.
- `00_GSCC_ENTRY.md` remains the repository authority that defines what provider/agent/runtime/session facts must be exposed, how unavailable fields are represented, and how GSCC admission continues.
- The response enrichment layer must not fabricate provider-private identifiers, expose secrets, or infer authority from repository metadata.
- This decision records the required contract only. It does not implement or attest the runtime response enrichment.
- No P12-S6, CASE 1, GMC, MCP, server or production state is advanced by this decision.

### CPD-068 — F1 validation releases an arrival to normal governance only through an exact correlated release

- Date: 2026-10-07.
- A successful F1 function-exposure evaluation is necessary but does not by itself silently transition an arrival into the normal governed workflow.
- The release must restore the same per-arrival runtime and validate the same `connection_ref`, canonical GACR session, Access Grant, F1 exposure receipt and current repository HEAD.
- The canonical transition is persisted as `F1_VERIFIED → 00_START_HERE.md / RELEASED`, with runtime state `RELEASED_TO_NORMAL_GOVERNANCE`.
- A stale, mismatched, non-exposable or differently bound F1 receipt fails closed.
- Live acceptance is proven by issue `#244`, session `session-5bba386248ac4d9c0e05f1a8`, F1 workflow `37550409710`, exposure receipt `GSCC-EXPOSURE-083cf0005955022e1c19d5b8d79264a170e9d9cc7bc898a251339e9b3b92b76f`, release workflow `37550477009` and release comment `6027880258`.
- Released exact HEAD: `f768268bf1a3f62c2e6741aecfba20d86545969c`.
- Provider-private conversation/session identifiers remained `UNAVAILABLE`; repository-controlled GSCC references do not impersonate provider identifiers.
- This closes IDN-006 and the temporary IDN lane. It does not execute or reorder the global programme. `P12-S6_CLOSE_CREATE_NEW_REPOSITORY_CASE` remains the unique next global action.



### CPD-069 — The LIVE-proven GSCC/GSE/GACR chain becomes a reusable capsule programme

- Date: 2026-10-07.
- The completed pre-entry chain `GSCC → GSE → GACR → F1 → RELEASED_TO_NORMAL_GOVERNANCE` is accepted as a reusable module candidate rather than a Template-only implementation detail.
- Canonical productization authority is `CP-CAPSULE-001` at `docs/control-plane/GSCC_GSE_GACR_REUSABLE_CAPSULE.md`.
- Canonical global backlog is `CAP-001..CAP-012`.
- Productization is extraction/packaging of already-proven semantics, not permission to redesign or weaken identity, admission, liveness, exact-HEAD, GACR, access, exposure or release gates.
- Provider-private identity remains supplied-only. Missing provider facts remain explicit `UNAVAILABLE`.
- Per-arrival state isolation, Q9 correlated liveness, Q10-before-Q2 ordering, canonical GACR durability, F1 actual-function validation and exact correlated release are mandatory portable invariants.
- Capsule 1.0.0 requires a clean second-repository LIVE proof and a second/generic provider transport adapter proof.
- Existing `IDN-013` and `RTE-013` remain downstream API/UI consumers rather than prerequisites for core capsule 1.0.0.
- This programme is dependency-bound behind `P12-S6`; registration does not change the current unique executable action `P12_S6_CLOSE_CREATE_NEW_REPOSITORY_CASE`.


### CPD-070 — Capsule productization is downstream of the global routing/model junction

- Date: 2026-10-07.
- Owner correction: the reusable capsule must not become a parallel programme released directly by P12-S6.
- P12-S6 closure continues to release GMC-A first.
- CAP-001 is dependency-bound by `GMC-19 + RTE-012 + ARCH-006 + IDN-006`.
- The reusable capsule ends at an exact F1-correlated release and hands the same arrival into the existing post-entry junction; it does not replace that router.
- Canonical junction dimensions are distinct: `IDENTITY != ROLE != AUTHORITY != CONNECTION_INTENT != ENTRY_PURPOSE != WORK_KIND_OR_CASE != ENTRY_ACTION != MUTATION_AUTHORITY`.
- Role/type uses the existing identity/session role model (`INTAKER / SUPERVISOR / CODE_AGENT / REVIEWER`) and never grants authority.
- Stage 1 purpose remains `WORK_ON_CONTROL_PLANE` vs `APPLY_GOVERNANCE_CASE`.
- Stage 2A remains `CODE_IMPLEMENTATION / EXECUTE_EXISTING_TASK / ADD_OR_ENRICH_INFORMATION`.
- Stage 2B remains exactly the four canonical cases: `CREATE_NEW_REPOSITORY / ADOPT_EXISTING_REPOSITORY / MAP_EXISTING_PROJECT / LAB_EVOLUTION`.
- Existing connection-intent and entry-action policies remain authoritative and separate. `CONTINUE_GOVERNED_WORK` is not a fifth structuring case.
- The post-release junction resolves or asks only missing fields and must not replay First Touch or create a second GACR session.
- CAP 1.0.0 must prove this exact handoff on a second repository and across a second/generic provider adapter.
- This reconciliation does not advance P12-S6, GMC, RTE, ARCH or CAP execution status.


### CPD-071 — Master system map and requirements/roadmap traceability

- Date: 2026-10-07.
- The platform now exposes one whole-system navigation map at `docs/control-plane/MASTER_SYSTEM_MAP.md`.
- A durable cahier-des-charges / traceability / roadmap synthesis is exposed at `docs/control-plane/REQUIREMENTS_ROADMAP.md`.
- These files are synthesis/navigation surfaces and are explicitly **not** parallel authorities.
- Normative ownership remains with CP-ARCH-001, PROGRAM/TASKS/NEXT_ACTION, DATA_MODEL, policies, decisions and runtime authorities.
- README, 00_START_HERE, AGENTS, CANONICAL_ARCHITECTURE, DATA_MODEL and the reusable capsule must all point to the same master map and requirements roadmap.
- Documentation status must distinguish `LIVE_PROVEN`, `IMPLEMENTED`, `PARTIAL`, `PLANNED_NOT_ACTIVE` and `FUTURE`; planned behavior must never be described as active.
- The Data Model must distinguish the LIVE GSCC/GSE/GACR identity/session chain from the broader normalized principal/agent/connection/session/role/authority registry that remains planned.
- Architecture authority advances to `CP-ARCH-001-R7`.
- CI must fail on link drift, architecture revision drift, silent activation of the two-stage purpose router, or CAP dependency drift.
- Global execution order is unchanged; `P12-S6` remains the unique executable task.


### CPD-072 — Deployable SaaS platform and autonomous administration cockpit

- Date: 2026-10-07.
- The Governed Repository Platform must be productized as a deployable SaaS-ready application, not only a repository/workflow framework.
- Canonical product authority: `CP-SAAS-001` at `docs/control-plane/SAAS_PLATFORM_PROGRAM.md`.
- Canonical product backlog: `SAA-001..SAA-015`.
- Target public deployment URL: `https://mcp.wealthtechinnovations.com/template`.
- The frontend target is a complete autonomous administration cockpit covering identity/session, GSCC/GSE/GACR, cases/runs/questions, programme/tasks/claims, evidence/decisions/audit, checkpoints/handoffs, repositories/integrations, knowledge/infrastructure and deployment operations.
- The backend target is a complete versioned REST/OpenAPI API with governed service/microservice boundaries, workers/event processing where justified and PostgreSQL runtime projection after its architectural gate.
- `ARCH-008`, `ARCH-009`, `ARCH-010`, `IDN-013` and `RTE-013` are architectural/API/UI prerequisites and are reused rather than duplicated.
- The UI/API cannot create governance authority. Authentication, role, authority, access grant, F1 exposure and mutation authority remain distinct.
- SaaS readiness requires tenant/workspace isolation before multi-tenant release.
- Production deployment requires live server/DNS/TLS/database observation and explicit governed mutation authority; this decision registers the target but grants no production mutation authority.
- Global execution ordering remains unchanged: `P12-S6` is still the unique executable task.


### CPD-073 — Close CREATE_NEW_REPOSITORY and release GMC-A

- Date: 2026-10-07.
- `CREATE_NEW_REPOSITORY` CASE 1 satisfies its validated exit.
- `P12-S1..P12-S6 = DONE`.
- `C1-14 = DONE`.
- Historical parent `C1-13-I-B` is reconciled as DONE because its decomposed path `C1-13-I-B-A..G` is complete through server choice, domain intent, workflow choice, setup approval, baseline and subsequent normal-entry proof.
- Gouvern normal governed entry is PASS with no first-agent/baseline/work duplication.
- Ekyc second fresh repository E2E is PASS with no target-specific repair in the accepted final path.
- The canonical CASE 1 relational run is closed as `DONE`, with `current_phase_id = null` and no active CASE 1 phase.
- External MCP dependencies remain external intake/history only; this closure performs no MCP implementation.
- No executable CASE 1 task remains orphaned.
- GMC-A is released.
- `GMC-01 / GMC-G01` becomes the unique current work package.
- Release mode is planning/knowledge extraction only. This decision does not grant Governance Model implementation mutation authority.
- The detailed GMC execution blueprint remains authoritative for work-package/atomic-task sequencing and evidence gates.


### CPD-074 — GACR capacity-aware parallel work dispatch

- Date: 2026-10-07.
- GACR advances to `CP-AGENT-RELAY-001-R7`.
- GACR must expose an explicit capacity pool for new parallel work without creating a second task engine.
- Silence never means idle/available.
- New-work eligibility requires explicit `AVAILABLE`/`WAITING` evidence or canonical `STANDBY`, sufficient liveness, no active claim/in-flight action, and compatibility with the work item.
- Explicit provider/runtime limitations are observed-only: `PROVIDER_RATE_LIMIT`, `PROVIDER_QUOTA_EXHAUSTED`, `CONTEXT_LIMIT`, `WAITING_FOR_INPUT`, `DEPENDENCY_BLOCKED`.
- Parallel planning reuses canonical work items, dependencies, claims, collision domains, capabilities, role and authority evidence.
- A `WORK_OFFER` grants no claim and no mutation authority.
- Acceptance produces only `ACCEPTED_PENDING_CLAIM`; canonical claim creation and exact-HEAD reconciliation remain mandatory before mutation.
- Existing takeover dispatch semantics remain separate under `dispatch_kind = TAKEOVER`.
- External webhook delivery remains takeover-only until an explicit work-offer bridge contract exists.
- The relay may refresh safe work offers on normal/scheduled GACR cycles.
- This cross-cutting GACR change does not alter the global programme; `GMC-01 / GMC-G01` remains the unique current work package.


### CPD-075 — GACR contextual continuous multi-agent task pool

- Date: 2026-10-07.
- GACR advances to authority revision `CP-AGENT-RELAY-001-R8`.
- R8 continuously derives dispatchable task projections from existing canonical task authorities; it does not create a second task truth.
- R7 explicit capacity semantics remain authoritative: silence is never treated as availability.
- Parallel task waves require non-overlapping collision domains and satisfied dependencies.
- Each offer carries a safe context packet containing canonical history/method/evidence/checkpoint/handoff references.
- A receiving agent must read referenced canonical history before mutable work.
- `WORK_OFFER` and acceptance do not grant mutation authority.
- Claim activation requires acceptance with observed HEAD, repository reobservation of the same exact HEAD, free collision domains and no existing active claim for the target session.
- A responsive interrupted agent may requeue only after leaving checkpoint, handoff and evidence references.
- Abrupt interruption remains under existing GACR liveness/forensics/takeover semantics and exact-HEAD reconciliation.
- Rate limit, quota exhaustion, context limit and blockers are accepted only when explicitly observed; they are never inferred from silence.
- Source Control Plane atomic tasks remain owned by their programme/blueprint authorities. Client work remains owned by `.governance/work/work-items.json`.
- R8 may coordinate `GMC-01/GMC-G01` but does not complete its atomic tasks or grant Governance Model implementation authority.
- Raw conversation content, transcripts and private/internal reasoning remain outside persisted task context.
