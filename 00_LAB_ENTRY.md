# 00_LAB_ENTRY — Entrée automatique de création d'un LAB

STATUS: GOVERNED_OWNER_WORKFLOW_CANDIDATE; activates only when merged into main with tested workflow. No new admission door.
This is a separate LAB creation workflow, not an implicit GSCC/GSE/GACR admission.

## Required inputs
One explicit authenticated entry, unique lowercase slug and objective.
GitHub Actions workflow_dispatch supplies real actor, event sender, repository
and main HEAD; do not accept a nickname in a prompt as permission proof.

## Minimum outputs of a single successful entry
- Stable development continuity ID, not a provider/session ID.
- Chronological machine registry with original author, issue, base HEAD,
  branch, pool, real PR number and event sequence.
- Isolated lab/slug branch, coordination issue and draft continuity PR.
- LAB.md memory/architecture/requirements and verifiable construction contract.
- Pool ID and four initial slots: ARCH, PLAN, CODE, REVIEW. Their identities
  are VACANT until authenticated; all may propose code subject to real
  GitHub native permission and scoped governance, not from pool metadata.
- Dependency-ordered 11-step staged QUEUE.json, pointing to the existing
  source task graph in .governance/control-plane-state/tasks.json and the
  existing scripts/gacr_capacity_dispatch.py dispatcher.
- Explicit governance CI workflow_dispatch for the new LAB.

## Invariants
LAB creation does not dispatch work, grant GACR claims, authorize merge,
release a live agent, create a real session ID or deploy anything.
Actual queue promotion depends on independent plan review, canonical work
graph state, dependencies and colliding claims. GMC-01 is never displaced.
Merge and deployment require independent approvals, tests and evidence.
Do not create a second task queue or GACR authority source.

## Usage
After approval and merge on main, use GitHub Actions:
LAB Entry - automatic canonical LAB creation -> Run workflow (main).
Supply slug (3-36 chars) and objective (12-1200 chars).
The workflow uses the allowlisted authenticated GitHub event sender,
the repository permissions of GitHub Actions and a fresh main HEAD.

For a ChatGPT agent, first follow valid existing Door A, or explicitly select
the GitHub-authenticated Door B; access to this file alone is not admission.
A direct GitHub operation outside Actions needs its own real authenticated
actor, permissions and proof and must not assert that this workflow executed.

## Recovery
Given just a development continuity ID, resolve the GitHub issue, branch and
registry; read the latest checkpoint, PR, CI and HEAD. Repeated slug fails
closed instead of overwriting an existing branch. An interrupted bootstrap
can be investigated through its issue and existing GitHub objects.

## Post-F1 voluntary LAB choice and GACR binding

A Door A agent with verified F1/RELEASE reaches `00_START_HERE.md`, chooses
`LAB_EVOLUTION`, and may prepare an isolated branch/LAB **without obtaining
a GACR dispatcher work offer or claim for its initial setup**. Door B continues
as a separate direct GitHub owner-authenticated entry. The LAB workflow is
an **owner-authenticated GitHub execution mechanism**, not a third door:
using `workflow_dispatch` does not synthesize GSCC/GSE/GACR/F1 evidence.

This bootstrap does not grant native repository permissions to any agent.
The actual GitHub executor must have the permissions needed for creating
a branch, issue and PR. The historical or new agent's role and identity
are independent of the GitHub owner executing this workflow.

A newly created `POOL.json` has a real, separate `pool_id`, **but it is
not operational GACR membership**: its `gacr_link_contract` remains
`REQUIRED_NOT_YET_ATTESTED` with null GACR continuity/agent/session IDs.
The pool cannot be declared GACR-bound until the existing
`gacr-sessions.json` and `gacr-continuities.json` attest the exact
agent, session, scope, evidence, role, permissions and chronology. Agent
slots can remain vacant. Do not create a parallel GACR registry or queue.

`QUEUE.json` is an ordered proposal `projection_only` and not a second
executable task queue. First LAB setup requires neither dispatcher offer
nor claim; promoted canonical tasks retain all dispatcher, exact HEAD,
collision and claim rules applicable to their subsequent execution.
