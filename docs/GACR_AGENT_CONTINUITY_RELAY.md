# GACR — Governed Agent Continuity Relay

Authority: `CP-AGENT-RELAY-001`

GACR is the reusable governed process for keeping long-running multi-agent work resumable when one agent or conversation becomes unavailable, times out, stalls, or loses its client connection.

It extends the existing session / claim / checkpoint / handoff model. It is **not** a second task engine.

## Core model

```text
REGISTER / RESUME AGENT
→ SESSION
→ OPTIONAL EXTERNAL CONVERSATION REF
→ HEARTBEAT + LEASE
→ CLAIMED WORK
→ CHECKPOINTS / EVIDENCE
→ SUPERVISOR SCAN
   ├─ healthy            → continue
   ├─ suspected stall    → SUSPECTED_STALL
   └─ lease expired      → STALLED
                           ↓
                    TAKEOVER_READY
                           ↓
                 standby agent offered
                           ↓
              exact branch/HEAD reconciliation
                           ↓
                    ACCEPT TAKEOVER
                           ↓
                  transfer active claim
                           ↓
                     continue work
```

A stall never automatically releases an active claim. The old claim continues to block concurrent writers until a successor has re-observed the work branch / PR, reconciled the exact current HEAD, and explicitly accepts the takeover.

## External conversation references

GACR may associate a session with an external conversation reference, for example a ChatGPT conversation ID.

Rules:

- use only an identifier/URL actually supplied by the client, orchestrator or user;
- never invent an unavailable provider conversation ID;
- by default, persist the provider reference but not the full conversation URL;
- for known providers, the URL may be reconstructed on request from the stored reference;
- the canonical identity remains the governed session ID, not the external chat URL.

For ChatGPT, a supplied URL such as:

```text
https://chatgpt.com/c/<conversation-id>
```

is normalized to the provider conversation reference `<conversation-id>`.

## States

`ACTIVE` — working session with a live lease.

`STANDBY` — connected/prepared session that has no current mutable claim and can be offered a takeover.

`SUSPECTED_STALL` — heartbeat late but lease not yet expired.

`STALLED` — lease expired; no further mutable dispatch is allowed from the predecessor session.

`TAKEOVER_READY` — stalled session has a takeover queue item.

`HANDOFF_STALLED` — ownership was transferred after exact-state reconciliation.

`CLOSED` — normal terminal handoff.

## Multi-agent collision safety

GACR complements, rather than replaces:

- `CP-NAMESPACE-001` for semantic ID uniqueness;
- work claims for ownership;
- collision domains for single-writer guarantees;
- dependency-safe dispatch;
- exact-HEAD guards;
- checkpoints and handoffs.

A standby agent is never allowed to write simply because another agent is stale.

## Automatic supervision

The distributed workflow `.github/workflows/governed-agent-continuity-relay.yml` scans leases on a schedule.

The workflow can automatically:

- identify suspected/stalled agents;
- create/maintain a takeover queue;
- offer stalled work to a compatible standby session;
- persist the resulting coordination state with an exact-HEAD guarded commit.

It does **not** have a universal way to wake an arbitrary browser tab or ChatGPT conversation. A provider/orchestrator may consume GACR state or send `repository_dispatch` events, and any standby agent that reconnects can deterministically discover its offered takeover.

## Commands

```bash
python3 scripts/governed_agent_continuity_relay.py register ...
python3 scripts/governed_agent_continuity_relay.py heartbeat --session-id ...
python3 scripts/governed_agent_continuity_relay.py scan
python3 scripts/governed_agent_continuity_relay.py status
python3 scripts/governed_agent_continuity_relay.py identify --provider chatgpt --provider-ref ...
python3 scripts/governed_agent_continuity_relay.py takeover-plan --stalled-session-id ...
python3 scripts/governed_agent_continuity_relay.py takeover-accept ...
```

## Reuse in another project

GACR is part of the generic Template surface. A governed project receives the same config, workflow, script and state contract. The project retains its own sessions, claims, checkpoints and takeover queue.

No project-specific hard-coding is required.

## Source Control Plane versus client runtime state

GACR preserves the same source/client memory boundary as the rest of the framework:

```text
SOURCE CONTROL PLANE GACR MEMORY
!=
DISTRIBUTED CLIENT GACR STATE
```

On the Template source, runtime continuity is stored only in:

- `.governance/control-plane-state/gacr-sessions.json`
- `.governance/control-plane-state/gacr-claims.json`
- `.governance/control-plane-state/gacr-takeovers.json`

On an instantiated/adopted client repository, GACR uses that project's local session/claim/takeover stores.

Only the generic GACR code, schemas, configuration and workflow are distributed. A source conversation or source agent claim must never become client project state.
