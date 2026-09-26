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
16. verify required GitHub Actions secrets/variables;
17. run read-only MCP discovery for servers/domains/write context;
18. choose existing/new/unresolved domain binding;
19. choose the governed work model;
20. approve the technical setup and access matrix.

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

