# GOVERNED CONTROL PLANE — Central entry point

## Role

`chainsolutions-wealthtech/Governed-Repository-Template` is both the generic repository template and the central governance control plane.

An agent connected to GitHub can start a governed request here before entering a target repository.

```text
AGENT
  ↓
Governed-Repository-Template
  ↓
GOVERNED REQUEST
  ↓
one question / one targeted agent request at a time
  ↓
entry action + intent + target + observations + authority
  ↓
chronological preparation plan
  ↓
agent executes each requested preparatory action and returns evidence
  ↓
HANDOFF_READY
  ↓
agent enters the real target repository
```

## Central state

Interactive request state is persisted in a GitHub issue on the control-plane repository. It is not committed into the template source and therefore is not copied into generated repositories.

The issue workflow never mutates another repository by itself. It asks the connected agent to perform precise GitHub observations or authorized actions and return structured evidence.

## Entry actions

The control plane supports:

1. `CREATE_NEW_REPOSITORY`
2. `ADOPT_EXISTING_REPOSITORY`
3. `MAP_EXISTING_PROJECT`
4. `LAB_EVOLUTION`
5. `CONTINUE_GOVERNED_WORK`

## Conversation protocol

Create a Governed Request issue from the issue template.

The control plane responds with exactly one next question or one action request.

Answer questions with:

```text
/governed-answer
{"field":"<field>","value":<value>}
```

Return execution evidence with:

```text
/governed-evidence
{"action_id":"<id>","result":"PASS","evidence":{...}}
```

A failed action moves the request to `HOLD_FOR_REVIEW`. A successful full preparation produces a machine-readable handoff.

## Boundary

`CONTROL_PLANE_PREPARATION != TARGET_WORK`

The control plane resolves the workflow, gathers facts, enforces gates, creates the chronological preparation package and verifies evidence. The agent only starts normal work on the target when `HANDOFF_READY` is emitted.
