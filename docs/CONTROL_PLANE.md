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


## Direct agent invocation

An agent with GitHub permission on the control-plane repository may start a request without manually opening an issue by sending a repository dispatch:

```json
{
  "event_type": "governed_request_start",
  "client_payload": {
    "objective": "Describe the governed objective",
    "agent": "ChatGPT / Claude / Codex / human",
    "provider": "github-connected-agent",
    "title": "Optional concise title"
  }
}
```

The source-only workflow creates the `[Governed Request]` issue. The issue-opened event then initializes the governed state machine and asks the first question.

The dispatch does not authorize target creation or target mutation. It only opens the governed preparation workflow.


## New repository creation sequence

`CREATE_NEW_REPOSITORY` is intentionally shorter than the other workflows.

After the entry action is selected, the control plane asks only:

1. where to create the repository:
   - `chainsolutions-wealthtech`;
   - `Wealthtechinnovations`;
   - `Patricked` (GitHub owner canonique: `Patricked-code`);
2. the exact repository name;
3. whether the repository is `private` or `public`.

These explicit selections are the creation instruction for this workflow. The control plane then emits and automatically attempts `CREATE_FROM_GOVERNED_TEMPLATE`; it does not ask for a generic connection intent, project stack or infrastructure before creation.

Creation contract:
- source: `chainsolutions-wealthtech/Governed-Repository-Template`;
- visibility: explicitly selected by the user;
- no manually added README, gitignore or license;
- full template content inherited;
- zero-touch bootstrap expected immediately after creation;
- project profile and infrastructure discovery continue inside the generated repository.

The source control plane contains a GitHub REST creation executor. It calls `POST /repos/chainsolutions-wealthtech/Governed-Repository-Template/generate` only after owner, name and visibility are resolved.

Creator authority is fail-closed and uses one central GitHub App installed on all three target owners.

Control-plane configuration:
- Actions variable `GOVERNED_GITHUB_APP_CLIENT_ID`;
- Actions secret `GOVERNED_GITHUB_APP_PRIVATE_KEY`.

At runtime, `actions/create-github-app-token@v3` mints a short-lived installation token for the selected canonical owner:
- `chainsolutions-wealthtech`;
- `Wealthtechinnovations`;
- `Patricked-code`.

The App installations must grant at least repository `Administration: write` and `Contents: read` and should cover all repositories for these creation scopes. Installation tokens are not stored in Git or Actions secrets and are revoked by the action after the job.

If the App credentials are missing, the App is not installed on the selected owner, or the installation lacks the required permissions, PREP-001 remains pending and no PASS evidence is fabricated. After fixing authority, `/governed-execute` retries the executor.
