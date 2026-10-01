# LOCAL GOVERNED ENTRY — Repository-local agent entry point

## Role

The central control plane prepares repositories. The local control plane governs work **inside** an initialized target repository.

```text
Governed-Repository-Template
  = CENTRAL / inter-repository control plane

Generated governed repository
  = LOCAL / intra-repository control plane
```

## First agent after bootstrap

When the repository is initialized and `NEXT_ACTION = DISCOVER_PROJECT_BASELINE`, the first local request enters `FIRST_AGENT_BOOTSTRAP`.

The local control plane asks one question at a time:

1. agent identity;
2. provider;
3. connection intent;
4. project mission;
5. in-scope / out-of-scope;
6. project profile or explicit defer;
7. architecture status and notes;
8. infrastructure status;
9. external systems;
10. constraints;
11. first concrete project objective;
12. explicit business baseline approval;
13. choose whether to continue repository technical setup;
14. choose whether to bind the repository to MCP;
15. choose MCP transport and non-secret connection profile;
16. define MCP discovery scope, domain strategy and initial runtime-mutation policy as configuration intent;
17. build and present the read-only MCP discovery plan;
18. explicitly approve that discovery execution; configuration answers alone never authorize network execution;
19. verify/provision only the credentials required for the approved discovery path;
20. run read-only MCP discovery for project/server/domain/write-context facts;
21. choose the domain intent from explicit choices after the production server is known;
22. if needed, choose an observed existing domain or parent domain from that server;
23. choose a suggested domain label/name or explicitly request a custom value;
24. derive the domain binding and the future capability/authority requirements without executing them;
25. choose the governed work model;
26. approve the technical setup and access matrix.

After the two approvals, the local workflow:

```text
REOBSERVE_REMOTE_HEAD
→ REQUIRE_EXPECTED_HEAD_MATCH
→ WRITE_PROJECT_CONTEXT
→ WRITE_ARCHITECTURE_BASELINE
→ UPDATE_PROJECT_PROFILE
→ RECORD_LOCAL_ENTRY_RECEIPT
→ CREATE_FIRST_AGENT_SESSION
→ CLOSE_WORK-DISCOVER-001
→ CREATE_FIRST_PROJECT_WORK_ITEM
→ UPDATE_CANONICAL_MEMORY / STATUS / NEXT_ACTION
→ VALIDATE_GOVERNANCE
→ COMMIT
→ PUSH
→ LOCAL_HANDOFF_READY
```

## Subsequent agents

After the first baseline is complete, local requests use `NORMAL_GOVERNED_ENTRY`. They resolve identity, provider, connection intent, local entry action and requested objective, then return a handoff pointing at the current repository state and `NEXT_ACTION`.

## Invocation

Manual issue: use the `Governed Local Entry` issue form.

Machine invocation:

```json
{
  "event_type": "governed_local_start",
  "client_payload": {
    "objective": "Describe why the agent is entering the repository",
    "agent": "ChatGPT",
    "provider": "github-connected-agent"
  }
}
```

The mere act of viewing a GitHub repository does not generate a GitHub event. A GitHub-connected agent must therefore invoke this local entry endpoint before governed work.

### Actor authorization

Issue creation and issue-comment commands are accepted only when both conditions hold:

- GitHub reports `OWNER`, `MEMBER` or `COLLABORATOR` association; and
- a fresh GitHub repository permission lookup reports `admin`, `maintain` or `write`.

Read/triage-only members or collaborators cannot advance the governed state, expose the direct MCP token to discovery, mint an SSH OIDC certificate, or trigger the baseline write.


## MCP-aware setup

When MCP binding is selected, the repository fails closed until the required Actions secret/variables exist.

Direct MCP mode uses the governed MCP endpoint captured during setup (optionally overridden by `GOVERNED_MCP_URL`) and the `GOVERNED_MCP_AUTH_TOKEN` repository secret.

SSH fallback uses no persistent private-key secret. The workflow requests `id-token: write`, generates an ephemeral Ed25519 keypair on the runner, exchanges GitHub OIDC plus the public key for a short-lived MCP-signed OpenSSH certificate, pins the authenticated S1 host key, and executes only the server-side read-only force-command gateway. Arbitrary remote shell is forbidden.

The first MCP discovery is read-only: `ping`, `get_project_context`, `list_domains_s1`, `list_domains_s2`, and `get_write_tools_context`.

A new repository never receives MCP write authority merely because discovery succeeded. MCP project registration and explicit authority are separate gates.

## Regulatory / AfricaFunds governed flow

The reusable model is versioned in `.governance/workflow-model.json`: read authorities, observe GitHub, observe runtime when relevant, reconcile, verify exact HEAD, single writer, implement, verify/regression, persist, commit, verify remote, deploy only if authorized, verify production, then continue.

### Central control-plane machine start

The central control plane can start a new local entry on an already initialized repository through:

```text
/governed-local-start
{"target_repository":"owner/repo","expected_head":"<40-char-sha>","objective":"<objective>"}
```

The central GitHub App verifies the target HEAD, dispatches `governed_local_start`, and the target workflow creates **and initializes** the new local-entry issue in the same dispatch.

This path does not weaken the human issue/comment authorization gate. It is a distinct machine path authenticated by the central GitHub App and exact-HEAD bound.

## Adaptive preparation contract

The local questionnaire is an adaptive preparation engine, not a fixed form and not an execution grant.

```text
ANSWER / OBSERVED FACT
→ enrich PROJECT MODEL
→ derive RESOURCE REQUIREMENTS
→ classify EXISTING / UNKNOWN / PLANNED / TO_CREATE / TO_CONFIGURE / TO_VERIFY
→ derive prepared work-items + dependencies + authority requirements
→ existing LOOP_ENGINEERING executes only when the item becomes READY and its authority gates pass
```

For an existing repository, already observed fresh facts are reused and only missing owner decisions or unresolved facts are asked. For a new repository, more questions are required because fewer resources exist. No parallel task engine or governance model is introduced.

## Signed SSH profile recovery

When an approved SSH or BOTH discovery reaches the authenticated MCP SSH certificate broker, the signed broker response is factual read-only evidence for the actual SSH target profile.

If the configured `ssh_connection_profile` differs from the signed broker `host / port / username`, discovery must not loop blindly. The local entry reopens `Q_SSH_PROFILE_RECOVERY`, exposes the observed non-secret profile, preserves the failed/direct evidence in bounded history, and requires a corrected profile.

Because the SSH target is part of the approved discovery plan, correcting it is a material plan change: the previous `mcp_discovery_approved` answer is invalidated and the corrected read-only plan must be approved again before network execution.

## BOTH transport semantics — dual-ready smart routing

`BOTH` does **not** mean “execute DIRECT and SSH together”.

It means both transport paths are prepared as available governed routes:

```text
BOTH
├── DIRECT_MCP_TOKEN
└── SSH / GitHub OIDC ephemeral certificate
```

For one operation, the router selects one route according to current capability, credential/readiness and failure state. The default read-only discovery policy prefers DIRECT when it is ready and uses SSH when DIRECT is unavailable or fails. The alternate route is not executed merely to prove that both exist.

Therefore:

- simultaneous DIRECT+SSH execution is not required;
- one successful selected route satisfies the current read-only discovery;
- fallback use is a normal governed route selection, not automatically a degraded discovery;
- readiness of the alternate route is tracked independently;
- a newly available alternate route does not invalidate already successful discovery evidence;
- independent dual-route attestation may still be performed when a specific gate explicitly requires it.

For legacy `BOTH` evidence where DIRECT already passed and the run failed only because the old engine subsequently forced SSH, the authorized DIRECT success can be reused. The SSH path remains configured as an alternate route whose readiness can be attested separately.

## Fresh project: production server before domain

For a fresh project with no existing infrastructure binding, successful read-only discovery does not jump directly to a domain decision.

The order is:

```text
DISCOVERY
→ observed server candidates
→ OWNER production-server choice
→ reuse domain inventory from selected server
→ domain planning
→ remaining setup
```

An observed server is a candidate, not an owner decision. Selecting `S1`, `S2`, another/new server, or deferring the choice enriches the project model but grants no runtime mutation authority.

When a server is selected, the next domain question reuses the already-authorized discovery evidence for that server instead of rerunning the same discovery.

## Fresh project: progressive domain decision chain

After a concrete production server is selected, domain planning is no longer a single free-form object.

```text
PRODUCTION_SERVER
→ DOMAIN_INTENT
→ server-scoped observed choices
→ parent/existing-domain choice when applicable
→ label/name choice
→ derive binding
→ derive future operation requirements
```

Domain intent choices are:

- `REUSE_EXISTING_DOMAIN`
- `CREATE_SUBDOMAIN`
- `CREATE_NEW_ROOT_DOMAIN`
- `CREATE_CHILD_DOMAIN`
- `NO_PUBLIC_DOMAIN`
- `DECIDE_LATER`

For `CREATE_SUBDOMAIN` / `CREATE_CHILD_DOMAIN`, the parent choices come from the already-authorized inventory of the selected server. Parent candidates prefer observed root/parent domains rather than presenting every nested hostname as a parent.

The label question proposes reusable choices such as `ekyc`, `kyc`, `identity`, `verify`, plus `OTHER_CUSTOM` and `DECIDE_LATER`.

A choice automatically derives a structured `domain_binding` where possible and prepares the corresponding execution intent/capabilities. For example, a subdomain prepares `CREATE_SUBDOMAIN` with `WEB_HOSTING_CHANGE + DOMAIN_DNS_CHANGE + TLS_CHANGE`.

This preparation **never grants execution authority** and never mutates DNS, Plesk/vhosts, TLS or the server.
