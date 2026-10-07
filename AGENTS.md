# AGENTS — Règles pour tout agent, humain ou automatisation

> **PRIORITÉ ABSOLUE D'ENTRÉE**  
> Avant toute autre instruction de ce fichier, lire `/00_GSCC_ENTRY.md`.  
> Ce chemin est prioritaire sur `00_START_HERE.md` et sur toute opération de travail gouverné.


Ce fichier s'applique à toute intervention sur `{{REPOSITORY}}`.

## Démarrage obligatoire

0. lire et satisfaire `00_GSCC_ENTRY.md`; aucun agent ou nouvelle conversation ne peut entrer directement par `00_START_HERE.md`;
1. après release/handoff GSCC → GSE → GACR, lire `00_START_HERE.md`, puis `docs/control-plane/MASTER_SYSTEM_MAP.md` pour la vue de bout en bout et `docs/control-plane/REQUIREMENTS_ROADMAP.md` pour l'état des exigences ;
2. confirmer dépôt, branche, HEAD et état du worktree ;
3. lire les fichiers directement concernés ;
4. rechercher les travaux existants ;
5. établir la baseline et les risques ;
6. vérifier les permissions et contraintes ;
7. sélectionner une action compatible avec `NEXT_ACTION.md`.

## Continuité

Il est interdit de recommencer le projet sans décision documentée, dupliquer une autorité existante, changer un contrat stable sans migration, supprimer une preuve utile ou contourner un gate de sécurité ou d'approbation.

## Zéro régression

Avant modification : identifier consommateurs, dépendances, données, contrats, tests et sorties affectés.

Après modification : exécuter les contrôles disponibles, comparer à la baseline, corriger toute régression introduite, puis vérifier à nouveau.

## Handoff

Toute interruption doit laisser le dépôt reprenable par un autre agent uniquement à partir des autorités versionnées, sans dépendre de la mémoire de la conversation.

<!-- GOVERNANCE_AUTOMATION_V2 -->
## Machine pre-write observation

In an initialized repository, run:

```bash
python3 scripts/governance_agent.py observe
```

before selecting mutable work.

When multiple agents cooperate, create/resume a governed repository session and dispatch only dependency-safe, collision-safe work. A `HEAD_MOVED` result forbids writing until intervening changes are reconciled.

New information must be registered/reconciled through the intake model. A contradiction is held for review and never becomes canonical automatically.


## Connection intent

When starting or resuming a governed session, classify the purpose of the connection before mutable dispatch.

Example:

```bash
python3 scripts/governance_agent.py session-start \
  --agent "<agent>" \
  --provider "<provider>" \
  --connection-ref "<ref>" \
  --intent CODE_CHANGE
```

Use `CONTEXT_INTAKE` or `INFORMATION_INTAKE` when the connection exists to add context or evidence rather than to code. `UNKNOWN` is the safe default and blocks mutable dispatch until resolved.

An intent never grants infrastructure, production, secret, financial, legal or destructive authority.


## Mandatory entry action

Before mutable dispatch, resolve the macro workflow:

```bash
python3 scripts/governance_agent.py entry-actions
```

Then start/resume the session with `--entry-action`.

The structural actions are `CREATE_NEW_REPOSITORY`, `ADOPT_EXISTING_REPOSITORY`, `MAP_EXISTING_PROJECT`, and `LAB_EVOLUTION`. `CONTINUE_GOVERNED_WORK` preserves normal work on an already governed repository.

`ADOPT_EXISTING_REPOSITORY` and `MAP_EXISTING_PROJECT` start read-only. `LAB_EVOLUTION` cannot dispatch mutable work from the canonical branch. Missing entry action fails closed.


## Central control plane entry

When the task begins before a target repository is prepared, start from `chainsolutions-wealthtech/Governed-Repository-Template` using a Governed Request issue.

The control plane owns the preparation sequence. Answer only the current question or perform only the current requested preparatory action. Return structured evidence before expecting the next step.

Do not start normal target-repository work until the control plane emits `HANDOFF_READY`. After handoff, reobserve the handed-off target HEAD before any write.


## Repository-local control plane

After central handoff, start local work through a `[Governed Local Entry]` issue or `repository_dispatch: governed_local_start`. The first agent is routed through `FIRST_AGENT_BOOTSTRAP`; later agents are routed through `NORMAL_GOVERNED_ENTRY`. Do not bypass a pending first-agent baseline.

## GACR — continuité et relève des agents

À chaque arrivée observable sur un repository gouverné, rattache ou reprends la connexion dans **GACR — Governed Agent Continuity Relay**. L'attachement ne dépend pas de la disponibilité d'une référence de conversation fournisseur ; cette référence enrichit la session lorsqu'elle est réellement observable.

Si une référence de conversation fournisseur est réellement disponible, transmets-la ; ne l'invente jamais.

Exemple actif :

```bash
python3 scripts/governed_agent_continuity_relay.py register \
  --agent "<agent>" \
  --provider chatgpt \
  --provider-ref "<conversation-id>" \
  --task-id "<task>" \
  --branch "<branch>"
```

Un agent de secours peut se déclarer avec `--standby`.

Les actions `session-start`, `dispatch`, `checkpoint` et `handoff` renouvellent automatiquement le lease GACR lorsqu'elles passent par `governance_agent.py`. Pour une longue opération sans action gouvernée intermédiaire, émettre un heartbeat GACR.

Si une session devient `STALLED / TAKEOVER_READY`, aucun agent ne doit reprendre son claim par simple supposition. La relève exige la lecture du checkpoint, de la branche/PR, puis une réconciliation exact-HEAD avant `takeover-accept`.

### GACR Agent Context

On long-running or multi-agent work, GACR Beacon records safe connection/action telemetry automatically through governed agent actions.

Before resuming offered/stalled work, inspect:

```bash
python3 scripts/gacr_agent_telemetry.py context --session-id <session-id>
```

Use a provider conversation reference or URL only when it is actually available from the client/orchestrator. Never infer one from unrelated GitHub evidence.

If a client bridge is available, it may register `client_instance_id`, `bridge_registration_ref` and wake channels. External wake events never bypass claim, authority or exact-HEAD checks.

### GACR R5 client liveness

A governed agent/client must keep its GACR session live independently of repository mutations when its host/orchestrator exposes a persistent client execution surface. If the host cannot run or invoke the emitter, that limitation must remain explicit rather than being reported as continuous liveness.

When the host/orchestrator can run a client process, use the distributed emitter:

```bash
python3 scripts/gacr_client_emitter.py daemon \
  --repository "<owner/repo>" \
  --session-id "<gacr-session-id>" \
  --client-instance-id "<client-instance-id>"
```

The emitter sends heartbeat metadata through the existing GACR repository-dispatch contract. Runtime transport credentials are read from the client environment only and are never written into GACR payloads or repository state.

Hosts should emit action traces around material work:

```bash
python3 scripts/gacr_client_emitter.py trace --repository "<owner/repo>" --session-id "<id>" --action-phase STARTED --action-id "<id>" --action-label "<label>"
python3 scripts/gacr_client_emitter.py trace --repository "<owner/repo>" --session-id "<id>" --action-phase COMPLETED --action-id "<id>" --outcome PASS
```

Only explicitly observed interruption signals may be emitted. Silence alone remains a WATCH/FORENSICS observation, never a fabricated failure cause.

Wake polling can surface a takeover offer but does not accept it. Exact-HEAD reconciliation and the existing claim/authority gates remain mandatory.

## GACR R6 provider-host issue bridge

When a provider host cannot invoke GitHub `repository_dispatch` directly but can create GitHub issue comments, the configured GACR host issue is the governed fallback transport.

For this Template source, the configured ingress is issue `#115`. Read `.governance/agent-relay/config.json` rather than hard-coding that number in reusable client logic.

A host event uses one JSON object after the exact prefix `/gacr-host `:

```text
/gacr-host {"schema":"gacr-host-event/v1","event":"attach","connection_ref":"<stable-connection-ref>","client_instance_id":"<stable-client-instance>","provider":"chatgpt","observed_head":"<sha>","entry_action":"CONTINUE_GOVERNED_WORK","connection_intent":"OBSERVE"}
```

Required behavior for hosts using this fallback:

- emit an `attach`, `heartbeat`, `action`, or explicitly observed `interrupt` event without waiting for a human reminder;
- reuse the same `connection_ref` / `client_instance_id` for the same conversation/client instance;
- on first controlled attach, supply the canonical GACR `entry_action` and `connection_intent` when they are known; for read-only continuation this may be `CONTINUE_GOVERNED_WORK` + `OBSERVE`;
- treat GACR session route and GSCC Admission intent as distinct vocabularies: Admission values such as `REPOSITORY_ACCESS` / `READ_ONLY_DISCOVERY` never resolve an `UNKNOWN` GACR session route;
- never use later provider enrichment to change or resolve an existing session route; route changes require the normal governed session/reconciliation path;
- use provider references only when actually available;
- never include transcript bodies, prompts, responses, cookies, authorization headers, tokens, passwords, private keys or secret values;
- treat the GitHub comment ID as the immutable ingress evidence/idempotency key;
- do not infer interruption causes from silence;
- do not treat host telemetry as execution authority;
- after a stalled/takeover state, obey the existing exact-HEAD reconciliation path instead of using the bridge to bypass takeover safety.

The bridge auto-attaches or resolves the GACR session, renews the lease for heartbeat/action events, records a safe Beacon, refreshes Correlator and Interruption Forensics, and persists state through the existing GACR workflow.


## Séparation des dimensions de jonction

Après release de la capsule, ne jamais confondre :

`IDENTITY != ROLE != AUTHORITY != CONNECTION_INTENT != ENTRY_PURPOSE != WORK_KIND_OR_CASE != ENTRY_ACTION != MUTATION_AUTHORITY`.

Ne rejoue pas First Touch et ne recrée pas une session GACR si l'arrivée courante est déjà corrélée. Résous ou demande uniquement la première dimension réellement manquante. Tant que le routeur `entry_purpose` reste `PLANNED_NOT_ACTIVE`, n'invente pas son activation : applique les routes actives documentées par les policies existantes.
