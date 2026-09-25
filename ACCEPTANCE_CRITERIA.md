# ACCEPTANCE_CRITERIA

## Repository governance

- [ ] Project initialized.
- [ ] Source-of-truth hierarchy explicit.
- [ ] Architecture documented.
- [ ] Baseline captured.
- [ ] CI / validation strategy defined.
- [ ] No unresolved placeholders.
- [ ] First project-specific acceptance criteria added.
- [ ] Project profile discovered or explicitly deferred without inventing implementation.
- [ ] Server/domain/directory/database state observed or left explicitly unresolved.
- [ ] Server access route resolved as direct MCP, SSH fallback, or unavailable.
- [ ] Agent connection intent resolved before mutable dispatch.

## Project acceptance

TO_INITIALIZE


## Central control plane acceptance

- [ ] Source template role is `CENTRAL_GOVERNANCE_CONTROL_PLANE`.
- [ ] Generated/adopted target role is `GOVERNED_TARGET_CLIENT`.
- [ ] Source-only workflow and issue form do not survive target initialization/adoption.
- [ ] `governed_request_start` creates a Governed Request issue on the source control plane.
- [ ] The request engine emits exactly one next question/action/handoff.
- [ ] Target mutation cannot begin before authority and plan approval.
- [ ] Invalid or missing evidence cannot advance the state machine.
- [ ] All five entry workflows can reach a valid `HANDOFF_READY`.
- [ ] The final handoff includes target repository, branch/HEAD when known, allowed next operation, evidence and constraints.
- [ ] Existing V2.0/V2.1/V2.2 regression tests remain GREEN.
