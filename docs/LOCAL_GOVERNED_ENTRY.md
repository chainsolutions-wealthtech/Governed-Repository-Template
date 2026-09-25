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
12. explicit baseline approval.

After approval, the local workflow:

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
