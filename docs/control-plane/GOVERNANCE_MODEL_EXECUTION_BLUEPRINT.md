# GOVERNANCE MODEL EXECUTION BLUEPRINT

> Parent authority: `CP-GOVMODEL-001`  
> Decisions: `CPD-028`, `CPD-029`  
> Scope: `CONTROL_PLANE_SOURCE_ONLY`  
> Status: `PLANNING_ONLY`  
> Implementation authorized: **NO**

## 1. Core operating model

The 19 GMC identifiers are chronological **work packages/groups**, not atomic tasks. Each group is a knowledge-production stage.

```text
PROGRAM
└── PHASE
    └── WORK PACKAGE / GROUP
        ├── PURPOSE
        ├── OBJECTIVE
        ├── INPUTS
        ├── PREREQUISITES
        ├── TASK
        │   ├── ACTION
        │   ├── METHOD
        │   ├── CONTROL
        │   ├── EVIDENCE
        │   └── INTERMEDIATE RESULT
        ├── EXPECTED RESULTS
        ├── PERSISTENT ARTIFACTS
        ├── EXIT CONTROLS
        ├── EXIT GATE
        └── CONSUMED BY
```

A downstream work package is unlocked only when all three dependency dimensions are satisfied:

```text
TASK_DEPENDENCY
+ ARTIFACT_DEPENDENCY
+ EVIDENCE_DEPENDENCY
= DOWNSTREAM UNLOCK
```

A simple `DONE` flag is never sufficient. Required artifacts must exist, be validated, be sufficiently complete for the consumer, and carry provenance.

## 2. Knowledge artifact rule

Results are planned as persistent knowledge objects. A work package produces versioned artifacts with stable IDs, producer, validation state, provenance requirement and downstream consumers. Atomic task results are intermediate by default and are promoted only after group validation.

## 3. Chronology

```text
P12-S6
→ GMC-G01 → GMC-G02
→ GMC-G03 → GMC-G04 → GMC-G05 → GMC-G06
→ GMC-G07 → GMC-G08 → GMC-G09 → GMC-G10 → GMC-G11
→ GMC-G12 → GMC-G13
→ GMC-G14 → GMC-G15
→ GMC-G16 → GMC-G17 → GMC-G18
→ GMC-G19
```

## 4. Shared research surface

- `docs/control-plane/CANONICAL_ARCHITECTURE.md`
- `docs/control-plane/GOVERNANCE_MODEL_CATALOGUE.md`
- `docs/control-plane/DATA_MODEL.md`
- `docs/control-plane/PROGRAM.md`
- `docs/control-plane/TASKS.md`
- `docs/control-plane/DECISIONS_LOG.md`
- `docs/control-plane/SUIVI.md`
- `docs/control-plane/CASE1_REPLAY_LEDGER.md`
- `.governance/control-plane-state/*.json`
- `.governance/control-plane-db/*.sql`
- `.governance/control-plane-db/catalog.json`
- `.governance/control-plane-db/runtime-seed.json`
- `.governance/control-plane-db/materialize.py`
- `.governance/TEMPLATE_MANIFEST.json`
- `.governance/*policy*.json`
- `.governance/work/*.json`
- `.governance/sessions/*.json`
- `.governance/canonical-memory/*.json`
- `schemas/*.json`
- `scripts/*.py`
- `.github/workflows/*.yml`
- `.github/workflows/*.yaml`

---

## GMC-G01 — BOUNDARY — MODEL / CASE / RUNTIME / PROJECTION

**Legacy reference:** `GMC-01`  
**Phase:** `GMC-A`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Éviter de mélanger la définition réutilisable du modèle avec les stratégies de cas, l'état runtime ou les projections techniques.

### OBJECTIVE

Établir la frontière canonique entre le Governance Model central, les stratégies CREATE/ADOPT/MAP/LAB, le runtime d'exécution et les projections.

### INPUTS

- `CP-ARCH-001`
- `CP-GOVMODEL-001`
- `existing canonical memory`

### PREREQUISITES

- P12-S6 has a validated exit before real execution of GMC-G01.
- CP-ARCH-001 and CP-GOVMODEL-001 are readable and reconciled.
- Exact current main HEAD is reobserved at execution time.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `P12-S6` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- No produced GMC artifact prerequisite; this group starts from canonical authorities and CASE 1 closure.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G01-PROVENANCE-COMPLETE`
- `EVREQ-G01-OUTPUTS-VALIDATED`
- `EVREQ-G01-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `docs/control-plane/CANONICAL_ARCHITECTURE.md`
- `docs/control-plane/GOVERNANCE_MODEL_CATALOGUE.md`
- `.governance/control-plane-db/catalog.json`
- `.governance/control-plane-db/runtime-seed.json`
- `.governance/TEMPLATE_MANIFEST.json`
- `.governance/*policy*.json`

### SEARCH PATTERNS

- `CREATE_NEW_REPOSITORY`
- `ADOPT_EXISTING_REPOSITORY`
- `MAP_EXISTING_PROJECT`
- `LAB_EVOLUTION`
- `SOURCE_ONLY`
- `CLIENT`
- `PROJECTION`
- `RUNTIME`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G01-T01 — Recenser toutes les autorités et artefacts de gouvernance connus.

- **ACTION:** Recenser toutes les autorités et artefacts de gouvernance connus.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G01-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G01-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G01-T02 — Classifier chaque artefact/règle en MODEL, APPLICATION_STRATEGY, RUNTIME_EXECUTION, PROJECTION ou UNRESOLVED.

- **ACTION:** Classifier chaque artefact/règle en MODEL, APPLICATION_STRATEGY, RUNTIME_EXECUTION, PROJECTION ou UNRESOLVED.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G01-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G01-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G01-T03 — Inventorier les sémantiques communes enfermées ou dupliquées dans un seul cas.

- **ACTION:** Inventorier les sémantiques communes enfermées ou dupliquées dans un seul cas.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G01-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G01-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G01-T04 — Cartographier la frontière source-control-plane versus surface distribuée aux clients.

- **ACTION:** Cartographier la frontière source-control-plane versus surface distribuée aux clients.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G01-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G01-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G01-T05 — Séparer données de définition réutilisables et données d'exécution concrètes.

- **ACTION:** Séparer données de définition réutilisables et données d'exécution concrètes.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G01-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G01-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G01-T06 — Identifier contradictions, chevauchements et éléments sans propriétaire canonique.

- **ACTION:** Identifier contradictions, chevauchements et éléments sans propriétaire canonique.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G01-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G01-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G01-T07 — Produire MODEL_BOUNDARY_MATRIX avec provenance.

- **ACTION:** Produire MODEL_BOUNDARY_MATRIX avec provenance.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G01-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G01-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G01-T08 — Valider la matrice contre CP-ARCH-001, CP-GOVMODEL-001 et les décisions.

- **ACTION:** Valider la matrice contre CP-ARCH-001, CP-GOVMODEL-001 et les décisions.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G01-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G01-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `MODEL_BOUNDARY_MATRIX`
- `MODEL_CLASSIFICATION_TAXONOMY`
- `UNRESOLVED_BOUNDARY_ITEMS`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-MODEL-BOUNDARY-MATRIX — MODEL_BOUNDARY_MATRIX
- type: `MATRIX`
- produced_by: `GMC-G01`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G02`, `GMC-G03`, `GMC-G12`, `GMC-G18`

#### GMA-MODEL-CLASSIFICATION-TAXONOMY — MODEL_CLASSIFICATION_TAXONOMY
- type: `MODEL`
- produced_by: `GMC-G01`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G02`, `GMC-G03`, `GMC-G12`, `GMC-G18`

#### GMA-UNRESOLVED-BOUNDARY-ITEMS — UNRESOLVED_BOUNDARY_ITEMS
- type: `KNOWLEDGE_ARTIFACT`
- produced_by: `GMC-G01`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G02`, `GMC-G03`, `GMC-G12`, `GMC-G18`

### EXIT CONTROLS

#### GMC-EXIT-G01-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G01-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G01-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Tous les artefacts inventoriés sont classifiés ou explicitement UNRESOLVED.
- Aucune sémantique commune connue n'est attribuée silencieusement à un seul cas.

### FAILURE / HOLD CONDITIONS

- Contradiction entre autorités sans règle de préséance.
- Artefact critique dont le rôle reste indéterminable.

### OUTPUTS / CONSUMED BY

- `GMC-G02`
- `GMC-G03`
- `GMC-G12`
- `GMC-G18`

---

## GMC-G02 — METAMODEL — ANATOMIE, IDS ET CONTRATS COMMUNS

**Legacy reference:** `GMC-02`  
**Phase:** `GMC-A`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Donner une grammaire commune et stable à toutes les connaissances qui seront extraites dans les groupes suivants.

### OBJECTIVE

Définir le métamodèle canonique, les IDs stables, les champs communs, les références, la provenance, le versioning et la supersession.

### INPUTS

- `GMC-G01 validated outputs`

### PREREQUISITES

- GMC-G01 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G01` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-MODEL-BOUNDARY-MATRIX` — MODEL_BOUNDARY_MATRIX; producer: `GMC-G01`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-MODEL-CLASSIFICATION-TAXONOMY` — MODEL_CLASSIFICATION_TAXONOMY; producer: `GMC-G01`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G02-PROVENANCE-COMPLETE`
- `EVREQ-G02-OUTPUTS-VALIDATED`
- `EVREQ-G02-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `sorties GMC-G01`
- `.governance/control-plane-db/003_canonical_authorities.sql`
- `docs/control-plane/DATA_MODEL.md`
- `schemas/*.json`
- `.governance/control-plane-state/canonical-architecture.json`

### SEARCH PATTERNS

- `*_id`
- `schema_version`
- `status`
- `source_ref`
- `supersedes`
- `revision`
- `version`
- `provenance`
- `required`
- `enum`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G02-T01 — Définir les 18 types d'entités du modèle.

- **ACTION:** Définir les 18 types d'entités du modèle.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G02-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G02-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G02-T02 — Définir les namespaces et conventions d'IDs stables.

- **ACTION:** Définir les namespaces et conventions d'IDs stables.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G02-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G02-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G02-T03 — Définir les métadonnées communes obligatoires.

- **ACTION:** Définir les métadonnées communes obligatoires.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G02-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G02-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G02-T04 — Définir les règles de références inter-registres et cardinalités.

- **ACTION:** Définir les règles de références inter-registres et cardinalités.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G02-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G02-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G02-T05 — Définir lifecycle, dépréciation et supersession sans suppression silencieuse.

- **ACTION:** Définir lifecycle, dépréciation et supersession sans suppression silencieuse.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G02-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G02-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G02-T06 — Définir la version du Governance Model indépendamment du Template.

- **ACTION:** Définir la version du Governance Model indépendamment du Template.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G02-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G02-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G02-T07 — Définir invariants de validation: IDs uniques, références résolues, provenance, no orphan.

- **ACTION:** Définir invariants de validation: IDs uniques, références résolues, provenance, no orphan.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G02-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G02-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G02-T08 — Produire des exemples minimaux valides pour chaque type.

- **ACTION:** Produire des exemples minimaux valides pour chaque type.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G02-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G02-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `GOVERNANCE_MODEL_METAMODEL`
- `ID_NAMESPACE_CONTRACT`
- `COMMON_METADATA_CONTRACT`
- `REFERENCE_AND_SUPERSESSION_RULES`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-GOVERNANCE-MODEL-METAMODEL — GOVERNANCE_MODEL_METAMODEL
- type: `MODEL`
- produced_by: `GMC-G02`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G03`, `GMC-G04`, `GMC-G05`, `GMC-G06`, `GMC-G07`, `GMC-G08`, `GMC-G09`, `GMC-G10`, `GMC-G11`, `GMC-G16`

#### GMA-ID-NAMESPACE-CONTRACT — ID_NAMESPACE_CONTRACT
- type: `CONTRACT`
- produced_by: `GMC-G02`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G03`, `GMC-G04`, `GMC-G05`, `GMC-G06`, `GMC-G07`, `GMC-G08`, `GMC-G09`, `GMC-G10`, `GMC-G11`, `GMC-G16`

#### GMA-COMMON-METADATA-CONTRACT — COMMON_METADATA_CONTRACT
- type: `CONTRACT`
- produced_by: `GMC-G02`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G03`, `GMC-G04`, `GMC-G05`, `GMC-G06`, `GMC-G07`, `GMC-G08`, `GMC-G09`, `GMC-G10`, `GMC-G11`, `GMC-G16`

#### GMA-REFERENCE-AND-SUPERSESSION-RULES — REFERENCE_AND_SUPERSESSION_RULES
- type: `CONTRACT`
- produced_by: `GMC-G02`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G03`, `GMC-G04`, `GMC-G05`, `GMC-G06`, `GMC-G07`, `GMC-G08`, `GMC-G09`, `GMC-G10`, `GMC-G11`, `GMC-G16`

### EXIT CONTROLS

#### GMC-EXIT-G02-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G02-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G02-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Les 18 types disposent d'un contrat de structure.
- Les règles d'ID/version/provenance/supersession sont non ambiguës.
- Les références peuvent être validées mécaniquement.

### FAILURE / HOLD CONDITIONS

- Conflit de namespace non résolu.
- Règle commune incompatible avec une autorité historique sans décision.

### OUTPUTS / CONSUMED BY

- `GMC-G03`
- `GMC-G04`
- `GMC-G05`
- `GMC-G06`
- `GMC-G07`
- `GMC-G08`
- `GMC-G09`
- `GMC-G10`
- `GMC-G11`
- `GMC-G16`

---

## GMC-G03 — DOMAIN REGISTRY

**Legacy reference:** `GMC-03`  
**Phase:** `GMC-B`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Établir les grandes responsabilités fonctionnelles du modèle afin d'organiser toute la connaissance aval.

### OBJECTIVE

Obtenir la liste exhaustive, normalisée, sourcée et non redondante des domaines du Governance Model.

### INPUTS

- `GMC-G02 validated outputs`

### PREREQUISITES

- GMC-G02 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G02` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-GOVERNANCE-MODEL-METAMODEL` — GOVERNANCE_MODEL_METAMODEL; producer: `GMC-G02`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-ID-NAMESPACE-CONTRACT` — ID_NAMESPACE_CONTRACT; producer: `GMC-G02`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-MODEL-BOUNDARY-MATRIX` — MODEL_BOUNDARY_MATRIX; producer: `GMC-G01`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G03-PROVENANCE-COMPLETE`
- `EVREQ-G03-OUTPUTS-VALIDATED`
- `EVREQ-G03-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `sorties G01/G02`
- `.governance/control-plane-state/canonical-architecture.json`
- `docs/control-plane/*`
- `.governance/*policy*.json`
- `scripts/*.py`
- `schemas/*.json`
- `.github/workflows/*`
- `.governance/control-plane-db/catalog.json`

### SEARCH PATTERNS

- `authority`
- `identity`
- `session`
- `entry`
- `routing`
- `memory`
- `work`
- `claim`
- `intake`
- `architecture`
- `infrastructure`
- `validation`
- `evidence`
- `handoff`
- `bootstrap`
- `adoption`
- `mapping`
- `audit`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G03-T01 — Recenser les domaines explicitement documentés.

- **ACTION:** Recenser les domaines explicitement documentés.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G03-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G03-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T02 — Découvrir les domaines implicites dans policies/schemas/scripts/workflows.

- **ACTION:** Découvrir les domaines implicites dans policies/schemas/scripts/workflows.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G03-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G03-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T03 — Découvrir les domaines révélés par SQL, runtime objects et tests.

- **ACTION:** Découvrir les domaines révélés par SQL, runtime objects et tests.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G03-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G03-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T04 — Fusionner les candidats en conservant toutes les provenances.

- **ACTION:** Fusionner les candidats en conservant toutes les provenances.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G03-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G03-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T05 — Normaliser synonymes, chevauchements et granularités.

- **ACTION:** Normaliser synonymes, chevauchements et granularités.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G03-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G03-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T06 — Définir purpose, scope, exclusions et responsabilité de chaque domaine.

- **ACTION:** Définir purpose, scope, exclusions et responsabilité de chaque domaine.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G03-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G03-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T07 — Attribuer statut IMPLEMENTED/PARTIAL/PLANNED/FUTURE.

- **ACTION:** Attribuer statut IMPLEMENTED/PARTIAL/PLANNED/FUTURE.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G03-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G03-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T08 — Associer les capabilities candidates sans les finaliser.

- **ACTION:** Associer les capabilities candidates sans les finaliser.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G03-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G03-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T09 — Contrôler qu'aucun élément majeur du modèle reste hors domaine sans justification.

- **ACTION:** Contrôler qu'aucun élément majeur du modèle reste hors domaine sans justification.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G03-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G03-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `DOMAIN_REGISTRY_DATASET`
- `DOMAIN_CANDIDATE_LEDGER`
- `DOMAIN_COVERAGE_REPORT`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-DOMAIN-REGISTRY — DOMAIN_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G03`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G04`, `GMC-G12`, `GMC-G13`, `GMC-G14`

#### GMA-DOMAIN-CANDIDATE-LEDGER — DOMAIN_CANDIDATE_LEDGER
- type: `KNOWLEDGE_ARTIFACT`
- produced_by: `GMC-G03`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G04`, `GMC-G12`, `GMC-G13`, `GMC-G14`

#### GMA-DOMAIN-COVERAGE-REPORT — DOMAIN_COVERAGE_REPORT
- type: `REPORT`
- produced_by: `GMC-G03`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G04`, `GMC-G12`, `GMC-G13`, `GMC-G14`

### EXIT CONTROLS

#### GMC-EXIT-G03-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G03-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G03-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Chaque domaine a ID, purpose, scope, statut et provenance.
- Synonymes/chevauchements sont résolus ou HOLD.
- Tous les éléments majeurs sont couverts.

### FAILURE / HOLD CONDITIONS

- Domaine candidat sans preuve suffisante.
- Deux domaines incompatibles recouvrent la même responsabilité.

### OUTPUTS / CONSUMED BY

- `GMC-G04`
- `GMC-G12`
- `GMC-G13`
- `GMC-G14`

---

## GMC-G04 — CAPABILITY REGISTRY

**Legacy reference:** `GMC-04`  
**Phase:** `GMC-B`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Décrire ce que la gouvernance sait faire, indépendamment de la manière technique dont ces capacités sont implémentées.

### OBJECTIVE

Construire le catalogue exhaustif des capabilities, rattachées aux domaines et décrites par leurs contrats fonctionnels, statut et applicabilité.

### INPUTS

- `GMC-G03 validated outputs`

### PREREQUISITES

- GMC-G03 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G03` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-DOMAIN-REGISTRY` — DOMAIN_REGISTRY_DATASET; producer: `GMC-G03`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-GOVERNANCE-MODEL-METAMODEL` — GOVERNANCE_MODEL_METAMODEL; producer: `GMC-G02`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G04-PROVENANCE-COMPLETE`
- `EVREQ-G04-OUTPUTS-VALIDATED`
- `EVREQ-G04-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `DOMAIN_REGISTRY_DATASET`
- `.governance/control-plane-state/canonical-architecture.json`
- `docs/control-plane/TASKS.md`
- `.governance/control-plane-db/catalog.json`
- `scripts/*.py`
- `scripts/test_*.py`
- `.github/workflows/*`

### SEARCH PATTERNS

- `CAPABILITY_`
- `bootstrap`
- `resume`
- `dispatch`
- `claim`
- `reconcile`
- `validate`
- `adopt`
- `map`
- `upgrade`
- `intake`
- `attest`
- `handoff`
- `routing`
- `authority`
- `session`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G04-T01 — Importer les capabilities déclarées comme candidats.

- **ACTION:** Importer les capabilities déclarées comme candidats.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G04-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G04-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T02 — Découvrir les capabilities implicites à partir des comportements et tests.

- **ACTION:** Découvrir les capabilities implicites à partir des comportements et tests.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G04-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G04-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T03 — Dédupliquer par résultat fonctionnel et non par fichier.

- **ACTION:** Dédupliquer par résultat fonctionnel et non par fichier.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G04-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G04-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T04 — Définir purpose, inputs, outputs, préconditions, postconditions et erreurs.

- **ACTION:** Définir purpose, inputs, outputs, préconditions, postconditions et erreurs.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G04-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G04-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T05 — Définir statut et applicabilité MANDATORY/OPTIONAL/CONDITIONAL/NOT_APPLICABLE.

- **ACTION:** Définir statut et applicabilité MANDATORY/OPTIONAL/CONDITIONAL/NOT_APPLICABLE.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G04-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G04-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T06 — Rattacher chaque capability à son domaine.

- **ACTION:** Rattacher chaque capability à son domaine.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G04-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G04-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T07 — Identifier dépendances préliminaires entre capabilities.

- **ACTION:** Identifier dépendances préliminaires entre capabilities.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G04-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G04-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T08 — Associer composants/implémentations/tests candidats.

- **ACTION:** Associer composants/implémentations/tests candidats.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G04-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G04-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T09 — Produire la revue de couverture et capabilities orphelines/non prouvées.

- **ACTION:** Produire la revue de couverture et capabilities orphelines/non prouvées.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G04-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G04-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `CAPABILITY_REGISTRY_DATASET`
- `CAPABILITY_COVERAGE_REPORT`
- `CAPABILITY_APPLICABILITY_CANDIDATES`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-CAPABILITY-REGISTRY — CAPABILITY_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G04`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G05`, `GMC-G13`, `GMC-G14`, `GMC-G18`

#### GMA-CAPABILITY-COVERAGE-REPORT — CAPABILITY_COVERAGE_REPORT
- type: `REPORT`
- produced_by: `GMC-G04`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G05`, `GMC-G13`, `GMC-G14`, `GMC-G18`

#### GMA-CAPABILITY-APPLICABILITY-CANDIDATES — CAPABILITY_APPLICABILITY_CANDIDATES
- type: `KNOWLEDGE_ARTIFACT`
- produced_by: `GMC-G04`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G05`, `GMC-G13`, `GMC-G14`, `GMC-G18`

### EXIT CONTROLS

#### GMC-EXIT-G04-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G04-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G04-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Chaque capability a ID, domaine, contrat, statut, applicabilité et provenance.
- Aucune capability architecturale n'est acceptée sans preuve ou statut PLANNED.

### FAILURE / HOLD CONDITIONS

- Capability supposée sans source.
- Conflit entre définition et comportement réel.

### OUTPUTS / CONSUMED BY

- `GMC-G05`
- `GMC-G13`
- `GMC-G14`
- `GMC-G18`

---

## GMC-G05 — COMPONENT REGISTRY

**Legacy reference:** `GMC-05`  
**Phase:** `GMC-B`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Décomposer les capacités en unités fonctionnelles réutilisables et comparables entre repositories.

### OBJECTIVE

Décomposer les capabilities en composants fonctionnels réutilisables en séparant strictement concept et artefact d'implémentation.

### INPUTS

- `GMC-G04 validated outputs`

### PREREQUISITES

- GMC-G04 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G04` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-CAPABILITY-REGISTRY` — CAPABILITY_REGISTRY_DATASET; producer: `GMC-G04`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-CAPABILITY-APPLICABILITY-CANDIDATES` — CAPABILITY_APPLICABILITY_CANDIDATES; producer: `GMC-G04`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G05-PROVENANCE-COMPLETE`
- `EVREQ-G05-OUTPUTS-VALIDATED`
- `EVREQ-G05-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `CAPABILITY_REGISTRY_DATASET`
- `scripts/*.py`
- `.governance/*policy*.json`
- `schemas/*.json`
- `.github/workflows/*`
- `.governance/control-plane-state/*.json`

### SEARCH PATTERNS

- `manager`
- `router`
- `validator`
- `registry`
- `resolver`
- `bootstrap`
- `dispatcher`
- `claim`
- `session`
- `authority`
- `reconciler`
- `adapter`
- `materializer`
- `upgrader`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G05-T01 — Décomposer chaque capability en responsabilités fonctionnelles minimales.

- **ACTION:** Décomposer chaque capability en responsabilités fonctionnelles minimales.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G05-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G05-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G05-T02 — Inspecter les artefacts actuels pour identifier les composants implicitement réalisés.

- **ACTION:** Inspecter les artefacts actuels pour identifier les composants implicitement réalisés.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G05-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G05-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G05-T03 — Séparer COMPONENT et IMPLEMENTATION_ARTIFACT.

- **ACTION:** Séparer COMPONENT et IMPLEMENTATION_ARTIFACT.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G05-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G05-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G05-T04 — Définir responsabilité, interfaces et contrats.

- **ACTION:** Définir responsabilité, interfaces et contrats.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G05-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G05-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G05-T05 — Identifier composants partagés entre capabilities.

- **ACTION:** Identifier composants partagés entre capabilities.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G05-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G05-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G05-T06 — Détecter doublons, chevauchements et composants manquants.

- **ACTION:** Détecter doublons, chevauchements et composants manquants.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G05-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G05-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G05-T07 — Associer objets, contrôles, implémentations et tests candidats.

- **ACTION:** Associer objets, contrôles, implémentations et tests candidats.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G05-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G05-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G05-T08 — Vérifier que chaque capability possède une décomposition ou un gap explicite.

- **ACTION:** Vérifier que chaque capability possède une décomposition ou un gap explicite.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G05-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G05-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `COMPONENT_REGISTRY_DATASET`
- `CAPABILITY_COMPONENT_MAP`
- `COMPONENT_GAP_REPORT`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-COMPONENT-REGISTRY — COMPONENT_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G05`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G06`, `GMC-G09`, `GMC-G12`, `GMC-G13`, `GMC-G14`

#### GMA-CAPABILITY-COMPONENT-MAP — CAPABILITY_COMPONENT_MAP
- type: `KNOWLEDGE_ARTIFACT`
- produced_by: `GMC-G05`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G06`, `GMC-G09`, `GMC-G12`, `GMC-G13`, `GMC-G14`

#### GMA-COMPONENT-GAP-REPORT — COMPONENT_GAP_REPORT
- type: `REPORT`
- produced_by: `GMC-G05`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G06`, `GMC-G09`, `GMC-G12`, `GMC-G13`, `GMC-G14`

### EXIT CONTROLS

#### GMC-EXIT-G05-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G05-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G05-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Aucun composant n'est défini comme un simple chemin de fichier.
- Toutes les capabilities ont une décomposition ou un gap explicite.

### FAILURE / HOLD CONDITIONS

- Responsabilités impossibles à séparer à cause d'un couplage non documenté.
- Capability sans composant identifiable et sans gap accepté.

### OUTPUTS / CONSUMED BY

- `GMC-G06`
- `GMC-G09`
- `GMC-G12`
- `GMC-G13`
- `GMC-G14`

---

## GMC-G06 — OBJECT / FIELD / RELATIONSHIP MODEL

**Legacy reference:** `GMC-06`  
**Phase:** `GMC-B`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Rendre les structures gouvernées comparables jusqu'aux objets, champs, relations et contraintes.

### OBJECTIVE

Construire le modèle de données conceptuel: objets, champs, types, cardinalités, contraintes, relations, mutabilité et autorité.

### INPUTS

- `GMC-G05 validated outputs`

### PREREQUISITES

- GMC-G05 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G05` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-COMPONENT-REGISTRY` — COMPONENT_REGISTRY_DATASET; producer: `GMC-G05`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-COMMON-METADATA-CONTRACT` — COMMON_METADATA_CONTRACT; producer: `GMC-G02`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G06-PROVENANCE-COMPLETE`
- `EVREQ-G06-OUTPUTS-VALIDATED`
- `EVREQ-G06-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `COMPONENT_REGISTRY_DATASET`
- `schemas/*.json`
- `.governance/control-plane-state/*.json`
- `.governance/control-plane-db/001_schema.sql`
- `.governance/control-plane-db/002_agent_activity.sql`
- `.governance/control-plane-db/003_canonical_authorities.sql`
- `.governance/control-plane-db/runtime-seed.json`

### SEARCH PATTERNS

- `id`
- `status`
- `state`
- `type`
- `required`
- `enum`
- `properties`
- `references`
- `depends_on`
- `source_ref`
- `authority`
- `created_at`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G06-T01 — Inventorier les objets à partir des schemas, JSON et tables SQL.

- **ACTION:** Inventorier les objets à partir des schemas, JSON et tables SQL.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G06-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G06-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T02 — Normaliser les objets équivalents représentés sous plusieurs formes.

- **ACTION:** Normaliser les objets équivalents représentés sous plusieurs formes.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G06-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G06-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T03 — Extraire champs, types, required/optional, valeurs permises et defaults.

- **ACTION:** Extraire champs, types, required/optional, valeurs permises et defaults.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G06-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G06-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T04 — Définir mutabilité, ownership/authority et nature canonical/derived/runtime.

- **ACTION:** Définir mutabilité, ownership/authority et nature canonical/derived/runtime.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G06-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G06-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T05 — Extraire les relations explicites et implicites.

- **ACTION:** Extraire les relations explicites et implicites.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G06-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G06-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T06 — Définir cardinalités et contraintes d'intégrité.

- **ACTION:** Définir cardinalités et contraintes d'intégrité.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G06-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G06-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T07 — Conserver provenance précise vers schema/table/path/symbole.

- **ACTION:** Conserver provenance précise vers schema/table/path/symbole.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G06-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G06-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T08 — Associer chaque objet aux composants/capabilities.

- **ACTION:** Associer chaque objet aux composants/capabilities.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G06-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G06-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T09 — Contrôler objets/champs/relations orphelins et divergences schema-code-SQL.

- **ACTION:** Contrôler objets/champs/relations orphelins et divergences schema-code-SQL.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G06-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G06-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `OBJECT_REGISTRY_DATASET`
- `FIELD_REGISTRY_DATASET`
- `RELATIONSHIP_REGISTRY_DATASET`
- `OBJECT_MODEL_CONSISTENCY_REPORT`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-OBJECT-REGISTRY — OBJECT_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G06`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G07`, `GMC-G08`, `GMC-G13`, `GMC-G15`

#### GMA-FIELD-REGISTRY — FIELD_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G06`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G07`, `GMC-G08`, `GMC-G13`, `GMC-G15`

#### GMA-RELATIONSHIP-REGISTRY — RELATIONSHIP_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G06`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G07`, `GMC-G08`, `GMC-G13`, `GMC-G15`

#### GMA-OBJECT-MODEL-CONSISTENCY-REPORT — OBJECT_MODEL_CONSISTENCY_REPORT
- type: `REPORT`
- produced_by: `GMC-G06`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G07`, `GMC-G08`, `GMC-G13`, `GMC-G15`

### EXIT CONTROLS

#### GMC-EXIT-G06-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G06-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G06-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Chaque objet/champ/relation a ID, définition, provenance et ownership.
- Cardinalités et contraintes connues sont explicites.
- Divergences schema-code-SQL sont résolues ou HOLD.

### FAILURE / HOLD CONDITIONS

- Deux autorités définissent différemment un même champ critique.
- Relation nécessaire mais cardinalité/ownership indéterminable.

### OUTPUTS / CONSUMED BY

- `GMC-G07`
- `GMC-G08`
- `GMC-G13`
- `GMC-G15`

---

## GMC-G07 — STATE REGISTRY / STATE MACHINES

**Legacy reference:** `GMC-07`  
**Phase:** `GMC-C`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Rendre explicites les lifecycles et états que le système manipule ou revendique.

### OBJECTIVE

Identifier tous les objets stateful et normaliser leurs états avec sémantique, catégorie et preuve requise.

### INPUTS

- `GMC-G06 validated outputs`

### PREREQUISITES

- GMC-G06 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G06` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-OBJECT-REGISTRY` — OBJECT_REGISTRY_DATASET; producer: `GMC-G06`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-FIELD-REGISTRY` — FIELD_REGISTRY_DATASET; producer: `GMC-G06`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-RELATIONSHIP-REGISTRY` — RELATIONSHIP_REGISTRY_DATASET; producer: `GMC-G06`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G07-PROVENANCE-COMPLETE`
- `EVREQ-G07-OUTPUTS-VALIDATED`
- `EVREQ-G07-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `OBJECT/FIELD datasets`
- `schemas/*.json`
- `.governance/control-plane-state/*.json`
- `.governance/work/*.json`
- `.governance/sessions/*.json`
- `.governance/control-plane-db/catalog.json`
- `.governance/control-plane-db/runtime-seed.json`
- `scripts/*.py`

### SEARCH PATTERNS

- `state`
- `status`
- `mode`
- `phase`
- `READY`
- `ACTIVE`
- `IN_PROGRESS`
- `DONE`
- `BLOCKED`
- `FAILED`
- `PENDING`
- `UNKNOWN`
- `HOLD`
- `ATTESTED`
- `VERIFIED`
- `SUPERSEDED`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G07-T01 — Identifier tous les objets possédant state/status/mode/phase.

- **ACTION:** Identifier tous les objets possédant state/status/mode/phase.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G07-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G07-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G07-T02 — Extraire les valeurs déclarées par schemas et JSON.

- **ACTION:** Extraire les valeurs déclarées par schemas et JSON.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G07-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G07-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G07-T03 — Extraire les états implicites dans branches conditionnelles et tests.

- **ACTION:** Extraire les états implicites dans branches conditionnelles et tests.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G07-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G07-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G07-T04 — Normaliser synonymes et distinguer état d'objet, phase et résultat de contrôle.

- **ACTION:** Normaliser synonymes et distinguer état d'objet, phase et résultat de contrôle.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G07-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G07-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G07-T05 — Classer initial/intermediate/terminal/error/hold/unknown.

- **ACTION:** Classer initial/intermediate/terminal/error/hold/unknown.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G07-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G07-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G07-T06 — Définir la sémantique exacte de chaque état.

- **ACTION:** Définir la sémantique exacte de chaque état.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G07-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G07-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G07-T07 — Définir evidence requirements/freshness pour déclarer l'état.

- **ACTION:** Définir evidence requirements/freshness pour déclarer l'état.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G07-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G07-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G07-T08 — Vérifier rattachement de chaque état à un objet et une machine cohérente.

- **ACTION:** Vérifier rattachement de chaque état à un objet et une machine cohérente.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G07-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G07-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `STATE_REGISTRY_DATASET`
- `STATE_MACHINE_CATALOGUE`
- `STATE_SEMANTICS_REPORT`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-STATE-REGISTRY — STATE_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G07`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G08`, `GMC-G10`, `GMC-G11`, `GMC-G15`

#### GMA-STATE-MACHINE-CATALOGUE — STATE_MACHINE_CATALOGUE
- type: `CATALOGUE`
- produced_by: `GMC-G07`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G08`, `GMC-G10`, `GMC-G11`, `GMC-G15`

#### GMA-STATE-SEMANTICS-REPORT — STATE_SEMANTICS_REPORT
- type: `REPORT`
- produced_by: `GMC-G07`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G08`, `GMC-G10`, `GMC-G11`, `GMC-G15`

### EXIT CONTROLS

#### GMC-EXIT-G07-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G07-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G07-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Tous les états observés sont normalisés ou conflict/obsolete.
- Chaque état possède objet, sémantique, catégorie et provenance.

### FAILURE / HOLD CONDITIONS

- Même nom d'état avec sémantiques incompatibles.
- État critique utilisé par le code sans autorité vérifiable.

### OUTPUTS / CONSUMED BY

- `GMC-G08`
- `GMC-G10`
- `GMC-G11`
- `GMC-G15`

---

## GMC-G08 — TRANSITION REGISTRY

**Legacy reference:** `GMC-08`  
**Phase:** `GMC-C`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Rendre exécutables et vérifiables les changements d'état, workflows, échecs et mécanismes de récupération.

### OBJECTIVE

Formaliser toutes les transitions autorisées/interdites avec déclencheur, acteur, autorité, pré/postconditions, contrôles, preuve, échec et récupération.

### INPUTS

- `GMC-G07 validated outputs`

### PREREQUISITES

- GMC-G07 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G07` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-STATE-REGISTRY` — STATE_REGISTRY_DATASET; producer: `GMC-G07`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-STATE-MACHINE-CATALOGUE` — STATE_MACHINE_CATALOGUE; producer: `GMC-G07`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G08-PROVENANCE-COMPLETE`
- `EVREQ-G08-OUTPUTS-VALIDATED`
- `EVREQ-G08-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `STATE_MACHINE_CATALOGUE`
- `scripts/*.py`
- `.github/workflows/*`
- `.governance/control-plane-db/catalog.json`
- `docs/control-plane/TASKS.md`
- `docs/control-plane/NEXT_ACTION.md`
- `docs/control-plane/CASE1_REPLAY_LEDGER.md`

### SEARCH PATTERNS

- `from`
- `to`
- `transition`
- `next`
- `depends_on`
- `unlock`
- `resume`
- `reconcile`
- `rollback`
- `retry`
- `STOP`
- `HOLD`
- `DENY`
- `HEAD_MOVED`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G08-T01 — Recenser transitions explicites et codées.

- **ACTION:** Recenser transitions explicites et codées.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G08-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G08-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T02 — Relier chaque transition à FROM/TO state IDs.

- **ACTION:** Relier chaque transition à FROM/TO state IDs.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G08-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G08-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T03 — Définir trigger, actor/role et authority requirements.

- **ACTION:** Définir trigger, actor/role et authority requirements.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G08-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G08-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T04 — Définir préconditions, action et postconditions.

- **ACTION:** Définir préconditions, action et postconditions.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G08-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G08-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T05 — Associer controls, gates et evidence types requis.

- **ACTION:** Associer controls, gates et evidence types requis.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G08-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G08-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T06 — Définir failure state et recovery/reconciliation.

- **ACTION:** Définir failure state et recovery/reconciliation.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G08-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G08-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T07 — Cataloguer transitions interdites et fail-closed.

- **ACTION:** Cataloguer transitions interdites et fail-closed.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G08-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G08-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T08 — Comparer documentation/code/tests et produire les gaps.

- **ACTION:** Comparer documentation/code/tests et produire les gaps.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G08-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G08-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T09 — Inventorier et normaliser les workflows qui orchestrent les transitions et phases.

- **ACTION:** Inventorier et normaliser les workflows qui orchestrent les transitions et phases.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G08-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G08-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T10 — Construire le Failure Registry à partir des états/branches d'échec observés.

- **ACTION:** Construire le Failure Registry à partir des états/branches d'échec observés.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G08-T10-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G08-T10-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T11 — Construire le Recovery Registry à partir des mécanismes resume/reconcile/retry/repair.

- **ACTION:** Construire le Recovery Registry à partir des mécanismes resume/reconcile/retry/repair.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G08-T11-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G08-T11-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `TRANSITION_REGISTRY_DATASET`
- `FORBIDDEN_TRANSITION_CATALOGUE`
- `TRANSITION_GAP_REPORT`
- `WORKFLOW_REGISTRY_DATASET`
- `FAILURE_REGISTRY_DATASET`
- `RECOVERY_REGISTRY_DATASET`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-TRANSITION-REGISTRY — TRANSITION_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G08`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G09`, `GMC-G10`, `GMC-G11`, `GMC-G13`, `GMC-G15`

#### GMA-FORBIDDEN-TRANSITION-CATALOGUE — FORBIDDEN_TRANSITION_CATALOGUE
- type: `CATALOGUE`
- produced_by: `GMC-G08`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G09`, `GMC-G10`, `GMC-G11`, `GMC-G13`, `GMC-G15`

#### GMA-TRANSITION-GAP-REPORT — TRANSITION_GAP_REPORT
- type: `REPORT`
- produced_by: `GMC-G08`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G09`, `GMC-G10`, `GMC-G11`, `GMC-G13`, `GMC-G15`

#### GMA-WORKFLOW-REGISTRY — WORKFLOW_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G08`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G09`, `GMC-G10`, `GMC-G11`, `GMC-G13`, `GMC-G15`

#### GMA-FAILURE-REGISTRY — FAILURE_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G08`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G09`, `GMC-G10`, `GMC-G11`, `GMC-G13`, `GMC-G15`

#### GMA-RECOVERY-REGISTRY — RECOVERY_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G08`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G09`, `GMC-G10`, `GMC-G11`, `GMC-G13`, `GMC-G15`

### EXIT CONTROLS

#### GMC-EXIT-G08-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G08-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G08-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Chaque transition a FROM/TO, trigger, authority, pre/postconditions et preuve.
- Transitions interdites explicites.
- Transitions critiques ont test ou gap enregistré.

### FAILURE / HOLD CONDITIONS

- Transition observée sans état source/cible déterminable.
- Désaccord non résolu entre code et autorité.

### OUTPUTS / CONSUMED BY

- `GMC-G09`
- `GMC-G10`
- `GMC-G11`
- `GMC-G13`
- `GMC-G15`

---

## GMC-G09 — CONTROL REGISTRY

**Legacy reference:** `GMC-09`  
**Phase:** `GMC-C`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Centraliser toutes les règles contrôlables qui protègent la gouvernance et leur sémantique PASS/FAIL.

### OBJECTIVE

Construire le registre exhaustif des contrôles avec PASS/FAIL, portée, sévérité, comportement d'échec, preuve, implémentation et tests.

### INPUTS

- `GMC-G08 validated outputs`

### PREREQUISITES

- GMC-G08 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G08` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-TRANSITION-REGISTRY` — TRANSITION_REGISTRY_DATASET; producer: `GMC-G08`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-FORBIDDEN-TRANSITION-CATALOGUE` — FORBIDDEN_TRANSITION_CATALOGUE; producer: `GMC-G08`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-WORKFLOW-REGISTRY` — WORKFLOW_REGISTRY_DATASET; producer: `GMC-G08`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-FAILURE-REGISTRY` — FAILURE_REGISTRY_DATASET; producer: `GMC-G08`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-RECOVERY-REGISTRY` — RECOVERY_REGISTRY_DATASET; producer: `GMC-G08`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G09-PROVENANCE-COMPLETE`
- `EVREQ-G09-OUTPUTS-VALIDATED`
- `EVREQ-G09-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `docs/control-plane/*`
- `.governance/*policy*.json`
- `scripts/governance_agent.py`
- `scripts/*.py`
- `.github/workflows/*`
- `scripts/test_*.py`
- `docs/control-plane/DECISIONS_LOG.md`

### SEARCH PATTERNS

- `MUST`
- `MUST NOT`
- `REQUIRED`
- `FORBIDDEN`
- `ALLOW`
- `DENY`
- `STOP`
- `FAIL`
- `fail closed`
- `exact HEAD`
- `authority`
- `collision`
- `dependency`
- `secret`
- `force push`
- `UNKNOWN`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G09-T01 — Extraire les contrôles explicites des autorités et décisions.

- **ACTION:** Extraire les contrôles explicites des autorités et décisions.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G09-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G09-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T02 — Extraire les contrôles des policies JSON et schemas.

- **ACTION:** Extraire les contrôles des policies JSON et schemas.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G09-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G09-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T03 — Extraire les guards/validations du code.

- **ACTION:** Extraire les guards/validations du code.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G09-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G09-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T04 — Extraire les contrôles de Governance CI.

- **ACTION:** Extraire les contrôles de Governance CI.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G09-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G09-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T05 — Relier les tests existants aux contrôles.

- **ACTION:** Relier les tests existants aux contrôles.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G09-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G09-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T06 — Dédupliquer et normaliser avec IDs stables.

- **ACTION:** Dédupliquer et normaliser avec IDs stables.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G09-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G09-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T07 — Définir purpose, scope, severity, trigger, PASS, FAIL et failure behavior.

- **ACTION:** Définir purpose, scope, severity, trigger, PASS, FAIL et failure behavior.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G09-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G09-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T08 — Associer evidence types, implementation IDs et test IDs candidats.

- **ACTION:** Associer evidence types, implementation IDs et test IDs candidats.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G09-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G09-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T09 — Produire le rapport documented-only/implemented-only/untested/conflicting.

- **ACTION:** Produire le rapport documented-only/implemented-only/untested/conflicting.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G09-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G09-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `CONTROL_REGISTRY_DATASET`
- `CONTROL_IMPLEMENTATION_TEST_MATRIX`
- `CONTROL_GAP_REPORT`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-CONTROL-REGISTRY — CONTROL_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G09`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G10`, `GMC-G11`, `GMC-G12`, `GMC-G13`, `GMC-G14`, `GMC-G15`

#### GMA-CONTROL-IMPLEMENTATION-TEST-MATRIX — CONTROL_IMPLEMENTATION_TEST_MATRIX
- type: `MATRIX`
- produced_by: `GMC-G09`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G10`, `GMC-G11`, `GMC-G12`, `GMC-G13`, `GMC-G14`, `GMC-G15`

#### GMA-CONTROL-GAP-REPORT — CONTROL_GAP_REPORT
- type: `REPORT`
- produced_by: `GMC-G09`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G10`, `GMC-G11`, `GMC-G12`, `GMC-G13`, `GMC-G14`, `GMC-G15`

### EXIT CONTROLS

#### GMC-EXIT-G09-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G09-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G09-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Chaque contrôle possède un contrat PASS/FAIL explicite.
- Chaque contrôle critique a provenance et comportement d'échec.
- Doublons normalisés sans perte de provenance.

### FAILURE / HOLD CONDITIONS

- Règle normative sans condition vérifiable.
- Contrôle critique code/autorité en conflit.

### OUTPUTS / CONSUMED BY

- `GMC-G10`
- `GMC-G11`
- `GMC-G12`
- `GMC-G13`
- `GMC-G14`
- `GMC-G15`

---

## GMC-G10 — GATE REGISTRY

**Legacy reference:** `GMC-10`  
**Phase:** `GMC-C`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Centraliser les points de décision qui combinent contrôles et autorités pour autoriser, stopper ou mettre en attente une action.

### OBJECTIVE

Formaliser les gates qui combinent les contrôles et déterminent ALLOW/STOP/HOLD pour les actions critiques.

### INPUTS

- `GMC-G09 validated outputs`

### PREREQUISITES

- GMC-G09 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G09` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-CONTROL-REGISTRY` — CONTROL_REGISTRY_DATASET; producer: `GMC-G09`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-CONTROL-IMPLEMENTATION-TEST-MATRIX` — CONTROL_IMPLEMENTATION_TEST_MATRIX; producer: `GMC-G09`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G10-PROVENANCE-COMPLETE`
- `EVREQ-G10-OUTPUTS-VALIDATED`
- `EVREQ-G10-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `CONTROL_REGISTRY_DATASET`
- `TRANSITION_REGISTRY_DATASET`
- `bootstrap/entry/upgrade/adoption flows`
- `.github/workflows/*`
- `docs/control-plane/PROGRAM.md`
- `docs/control-plane/TASKS.md`
- `.governance/*policy*.json`

### SEARCH PATTERNS

- `gate`
- `precondition`
- `ALLOW`
- `STOP`
- `HOLD`
- `approval`
- `before write`
- `dispatch`
- `bootstrap`
- `adoption`
- `merge`
- `attestation`
- `deployment`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G10-T01 — Identifier les points de décision critiques.

- **ACTION:** Identifier les points de décision critiques.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G10-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G10-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T02 — Associer à chaque gate les control IDs requis.

- **ACTION:** Associer à chaque gate les control IDs requis.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G10-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G10-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T03 — Définir logique d'agrégation et ALLOW/STOP/HOLD.

- **ACTION:** Définir logique d'agrégation et ALLOW/STOP/HOLD.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G10-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G10-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T04 — Définir acteur/authority et approbations éventuelles.

- **ACTION:** Définir acteur/authority et approbations éventuelles.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G10-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G10-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T05 — Définir evidence requirements et freshness.

- **ACTION:** Définir evidence requirements et freshness.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G10-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G10-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T06 — Définir failure/hold/recovery behavior.

- **ACTION:** Définir failure/hold/recovery behavior.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G10-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G10-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T07 — Définir dépendances et ordre entre gates.

- **ACTION:** Définir dépendances et ordre entre gates.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G10-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G10-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T08 — Vérifier que les gates réutilisent les contrôles sans les redéfinir.

- **ACTION:** Vérifier que les gates réutilisent les contrôles sans les redéfinir.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G10-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G10-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T09 — Consolider le Authority Registry utilisé par les gates, contrôles et transitions.

- **ACTION:** Consolider le Authority Registry utilisé par les gates, contrôles et transitions.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G10-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G10-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `GATE_REGISTRY_DATASET`
- `GATE_CONTROL_MATRIX`
- `GATE_SEQUENCE_MAP`
- `AUTHORITY_REGISTRY_DATASET`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-GATE-REGISTRY — GATE_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G10`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G11`, `GMC-G13`, `GMC-G14`, `GMC-G17`, `GMC-G18`

#### GMA-GATE-CONTROL-MATRIX — GATE_CONTROL_MATRIX
- type: `MATRIX`
- produced_by: `GMC-G10`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G11`, `GMC-G13`, `GMC-G14`, `GMC-G17`, `GMC-G18`

#### GMA-GATE-SEQUENCE-MAP — GATE_SEQUENCE_MAP
- type: `KNOWLEDGE_ARTIFACT`
- produced_by: `GMC-G10`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G11`, `GMC-G13`, `GMC-G14`, `GMC-G17`, `GMC-G18`

#### GMA-AUTHORITY-REGISTRY — AUTHORITY_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G10`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G11`, `GMC-G13`, `GMC-G14`, `GMC-G17`, `GMC-G18`

### EXIT CONTROLS

#### GMC-EXIT-G10-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G10-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G10-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Tous les gates critiques ont une décision déterministe.
- Chaque gate référence des controls existants.
- Conditions HOLD/recovery explicites.

### FAILURE / HOLD CONDITIONS

- Gate dépend d'un contrôle non défini.
- Deux gates contradictoires gouvernent le même point.

### OUTPUTS / CONSUMED BY

- `GMC-G11`
- `GMC-G13`
- `GMC-G14`
- `GMC-G17`
- `GMC-G18`

---

## GMC-G11 — EVIDENCE MODEL

**Legacy reference:** `GMC-11`  
**Phase:** `GMC-C`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Définir quelles preuves sont acceptables pour affirmer qu'un contrôle, état, transition ou gate est réellement satisfait.

### OBJECTIVE

Définir les types de preuves acceptables, formats, producteurs, sujets, fraîcheur, invalidation et liens aux controls/transitions/gates.

### INPUTS

- `GMC-G10 validated outputs`

### PREREQUISITES

- GMC-G10 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G10` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-GATE-REGISTRY` — GATE_REGISTRY_DATASET; producer: `GMC-G10`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-GATE-CONTROL-MATRIX` — GATE_CONTROL_MATRIX; producer: `GMC-G10`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-AUTHORITY-REGISTRY` — AUTHORITY_REGISTRY_DATASET; producer: `GMC-G10`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G11-PROVENANCE-COMPLETE`
- `EVREQ-G11-OUTPUTS-VALIDATED`
- `EVREQ-G11-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `.governance/control-plane-db/runtime-seed.json`
- `.governance/control-plane-db/001_schema.sql`
- `CI runs/commit SHAs/PRs/checkpoints/handoffs`
- `CONTROL/GATE/TRANSITION datasets`
- `docs/control-plane/DECISIONS_LOG.md`

### SEARCH PATTERNS

- `evidence`
- `proof`
- `attestation`
- `PASS`
- `CI`
- `run_id`
- `sha`
- `subject_head`
- `observed_at`
- `freshness`
- `valid`
- `expires`
- `source_ref`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G11-T01 — Inventorier les preuves concrètes déjà enregistrées.

- **ACTION:** Inventorier les preuves concrètes déjà enregistrées.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G11-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G11-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T02 — Abstraire les evidence types réutilisables.

- **ACTION:** Abstraire les evidence types réutilisables.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G11-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G11-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T03 — Définir format/schema de chaque evidence type.

- **ACTION:** Définir format/schema de chaque evidence type.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G11-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G11-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T04 — Définir producer, subject, authority et freshness.

- **ACTION:** Définir producer, subject, authority et freshness.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G11-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G11-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T05 — Définir invalidation/expiration.

- **ACTION:** Définir invalidation/expiration.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G11-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G11-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T06 — Définir provenance et retention/replay.

- **ACTION:** Définir provenance et retention/replay.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G11-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G11-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T07 — Relier evidence types aux controls/transitions/gates.

- **ACTION:** Relier evidence types aux controls/transitions/gates.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G11-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G11-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T08 — Vérifier séparation Evidence Type vs Evidence Record.

- **ACTION:** Vérifier séparation Evidence Type vs Evidence Record.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G11-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G11-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T09 — Produire la couverture et les gaps de preuve.

- **ACTION:** Produire la couverture et les gaps de preuve.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G11-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G11-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `EVIDENCE_TYPE_REGISTRY_DATASET`
- `EVIDENCE_REQUIREMENT_MATRIX`
- `EVIDENCE_GAP_REPORT`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-EVIDENCE-TYPE-REGISTRY — EVIDENCE_TYPE_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G11`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G12`, `GMC-G14`, `GMC-G15`, `GMC-G17`, `GMC-G18`, `GMC-G19`

#### GMA-EVIDENCE-REQUIREMENT-MATRIX — EVIDENCE_REQUIREMENT_MATRIX
- type: `MATRIX`
- produced_by: `GMC-G11`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G12`, `GMC-G14`, `GMC-G15`, `GMC-G17`, `GMC-G18`, `GMC-G19`

#### GMA-EVIDENCE-GAP-REPORT — EVIDENCE_GAP_REPORT
- type: `REPORT`
- produced_by: `GMC-G11`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G12`, `GMC-G14`, `GMC-G15`, `GMC-G17`, `GMC-G18`, `GMC-G19`

### EXIT CONTROLS

#### GMC-EXIT-G11-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G11-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G11-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Aucun evidence type ne contient une valeur spécifique à un run.
- Chaque control/gate critique connaît ses types de preuve.
- Freshness/invalidation explicite pour les preuves sensibles.

### FAILURE / HOLD CONDITIONS

- Preuve critique impossible à valider mécaniquement.
- Autorité de preuve indéterminée.

### OUTPUTS / CONSUMED BY

- `GMC-G12`
- `GMC-G14`
- `GMC-G15`
- `GMC-G17`
- `GMC-G18`
- `GMC-G19`

---

## GMC-G12 — CURRENT IMPLEMENTATION MAP

**Legacy reference:** `GMC-12`  
**Phase:** `GMC-D`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Relier le modèle abstrait à l'implémentation et aux tests actuels pour assurer une traçabilité bidirectionnelle.

### OBJECTIVE

Relier bidirectionnellement chaque élément abstrait du modèle aux artefacts qui l'implémentent aujourd'hui et détecter artefacts orphelins ou éléments non implémentés.

### INPUTS

- `GMC-G11 validated outputs`

### PREREQUISITES

- GMC-G11 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G11` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-DOMAIN-REGISTRY` — DOMAIN_REGISTRY_DATASET; producer: `GMC-G03`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-CAPABILITY-REGISTRY` — CAPABILITY_REGISTRY_DATASET; producer: `GMC-G04`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-COMPONENT-REGISTRY` — COMPONENT_REGISTRY_DATASET; producer: `GMC-G05`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-OBJECT-REGISTRY` — OBJECT_REGISTRY_DATASET; producer: `GMC-G06`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-FIELD-REGISTRY` — FIELD_REGISTRY_DATASET; producer: `GMC-G06`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-RELATIONSHIP-REGISTRY` — RELATIONSHIP_REGISTRY_DATASET; producer: `GMC-G06`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-STATE-REGISTRY` — STATE_REGISTRY_DATASET; producer: `GMC-G07`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-TRANSITION-REGISTRY` — TRANSITION_REGISTRY_DATASET; producer: `GMC-G08`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-WORKFLOW-REGISTRY` — WORKFLOW_REGISTRY_DATASET; producer: `GMC-G08`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-CONTROL-REGISTRY` — CONTROL_REGISTRY_DATASET; producer: `GMC-G09`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-GATE-REGISTRY` — GATE_REGISTRY_DATASET; producer: `GMC-G10`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-AUTHORITY-REGISTRY` — AUTHORITY_REGISTRY_DATASET; producer: `GMC-G10`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-EVIDENCE-TYPE-REGISTRY` — EVIDENCE_TYPE_REGISTRY_DATASET; producer: `GMC-G11`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-FAILURE-REGISTRY` — FAILURE_REGISTRY_DATASET; producer: `GMC-G08`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-RECOVERY-REGISTRY` — RECOVERY_REGISTRY_DATASET; producer: `GMC-G08`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G12-PROVENANCE-COMPLETE`
- `EVREQ-G12-OUTPUTS-VALIDATED`
- `EVREQ-G12-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `sorties G03-G11`
- `.governance/TEMPLATE_MANIFEST.json`
- `scripts/*.py`
- `schemas/*.json`
- `.github/workflows/*`
- `.governance/*.json`
- `.governance/control-plane-db/*`
- `tests/self-tests`

### SEARCH PATTERNS

- `path`
- `artifact`
- `schema`
- `workflow`
- `script`
- `test`
- `source-only`
- `client`
- `distributed`
- `manifest`
- `implementation`
- `covers`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G12-T01 — Inventorier les artefacts d'implémentation.

- **ACTION:** Inventorier les artefacts d'implémentation.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G12-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G12-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T02 — Associer chaque élément modèle à ses artefacts actuels.

- **ACTION:** Associer chaque élément modèle à ses artefacts actuels.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G12-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G12-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T03 — Enregistrer les relations many-to-many model↔artifact.

- **ACTION:** Enregistrer les relations many-to-many model↔artifact.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G12-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G12-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T04 — Définir type d'artefact, portée source/client, statut et version.

- **ACTION:** Définir type d'artefact, portée source/client, statut et version.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G12-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G12-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T05 — Relier chaque implémentation à ses tests/evidence producers.

- **ACTION:** Relier chaque implémentation à ses tests/evidence producers.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G12-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G12-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T06 — Identifier artefacts orphelins.

- **ACTION:** Identifier artefacts orphelins.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G12-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G12-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T07 — Identifier éléments modèle sans implémentation et classer PLANNED/FUTURE/GAP.

- **ACTION:** Identifier éléments modèle sans implémentation et classer PLANNED/FUTURE/GAP.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G12-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G12-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T08 — Vérifier boundary source-only/distributed.

- **ACTION:** Vérifier boundary source-only/distributed.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G12-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G12-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T09 — Produire la matrice bidirectionnelle MODEL↔IMPLEMENTATION.

- **ACTION:** Produire la matrice bidirectionnelle MODEL↔IMPLEMENTATION.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G12-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G12-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T10 — Construire le Test Registry et relier chaque test aux éléments modèle qu'il couvre.

- **ACTION:** Construire le Test Registry et relier chaque test aux éléments modèle qu'il couvre.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G12-T10-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G12-T10-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `IMPLEMENTATION_REGISTRY_DATASET`
- `MODEL_IMPLEMENTATION_MATRIX`
- `ORPHAN_ARTIFACT_REPORT`
- `UNIMPLEMENTED_MODEL_REPORT`
- `TEST_REGISTRY_DATASET`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-IMPLEMENTATION-REGISTRY — IMPLEMENTATION_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G12`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G13`, `GMC-G14`, `GMC-G15`, `GMC-G16`, `GMC-G19`

#### GMA-MODEL-IMPLEMENTATION-MATRIX — MODEL_IMPLEMENTATION_MATRIX
- type: `MATRIX`
- produced_by: `GMC-G12`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G13`, `GMC-G14`, `GMC-G15`, `GMC-G16`, `GMC-G19`

#### GMA-ORPHAN-ARTIFACT-REPORT — ORPHAN_ARTIFACT_REPORT
- type: `REPORT`
- produced_by: `GMC-G12`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G13`, `GMC-G14`, `GMC-G15`, `GMC-G16`, `GMC-G19`

#### GMA-UNIMPLEMENTED-MODEL-REPORT — UNIMPLEMENTED_MODEL_REPORT
- type: `REPORT`
- produced_by: `GMC-G12`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G13`, `GMC-G14`, `GMC-G15`, `GMC-G16`, `GMC-G19`

#### GMA-TEST-REGISTRY — TEST_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G12`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G13`, `GMC-G14`, `GMC-G15`, `GMC-G16`, `GMC-G19`

### EXIT CONTROLS

#### GMC-EXIT-G12-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G12-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G12-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Chaque élément implémenté a une provenance d'artefact.
- Chaque artefact gouvernance a un rôle ou justification.
- Éléments non implémentés sont explicitement classés.

### FAILURE / HOLD CONDITIONS

- Artefact critique à responsabilité ambiguë.
- Implémentation observable contredit le modèle.

### OUTPUTS / CONSUMED BY

- `GMC-G13`
- `GMC-G14`
- `GMC-G15`
- `GMC-G16`
- `GMC-G19`

---

## GMC-G13 — GLOBAL DEPENDENCY GRAPH

**Legacy reference:** `GMC-13`  
**Phase:** `GMC-D`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Rendre calculables l'ordre de chargement, d'installation, de validation et de réparation du modèle.

### OBJECTIVE

Construire le graphe complet des dépendances afin de calculer ordres de chargement, installation, vérification, réparation et intégration.

### INPUTS

- `GMC-G12 validated outputs`

### PREREQUISITES

- GMC-G12 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G12` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-IMPLEMENTATION-REGISTRY` — IMPLEMENTATION_REGISTRY_DATASET; producer: `GMC-G12`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-MODEL-IMPLEMENTATION-MATRIX` — MODEL_IMPLEMENTATION_MATRIX; producer: `GMC-G12`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-TEST-REGISTRY` — TEST_REGISTRY_DATASET; producer: `GMC-G12`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G13-PROVENANCE-COMPLETE`
- `EVREQ-G13-OUTPUTS-VALIDATED`
- `EVREQ-G13-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `phase_dependencies/task depends_on`
- `capability/component/object maps`
- `transitions/controls/gates`
- `scripts/config references`
- `SQL foreign keys`
- `case workflows`

### SEARCH PATTERNS

- `depends_on`
- `requires`
- `references`
- `before`
- `after`
- `prerequisite`
- `foreign key`
- `import`
- `load`
- `unlock`
- `requires_control`
- `requires_evidence`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G13-T01 — Collecter les dépendances explicites.

- **ACTION:** Collecter les dépendances explicites.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G13-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G13-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T02 — Ajouter les dépendances fonctionnelles entre model elements.

- **ACTION:** Ajouter les dépendances fonctionnelles entre model elements.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G13-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G13-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T03 — Classer HARD/CONDITIONAL/ORDERING/DATA/CONTROL/EVIDENCE/IMPLEMENTATION.

- **ACTION:** Classer HARD/CONDITIONAL/ORDERING/DATA/CONTROL/EVIDENCE/IMPLEMENTATION.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G13-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G13-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T04 — Construire le graphe orienté avec provenance par edge.

- **ACTION:** Construire le graphe orienté avec provenance par edge.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G13-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G13-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T05 — Détecter cycles et dépendances manquantes.

- **ACTION:** Détecter cycles et dépendances manquantes.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G13-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G13-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T06 — Calculer ordres topologiques load/install/validate/repair.

- **ACTION:** Calculer ordres topologiques load/install/validate/repair.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G13-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G13-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T07 — Identifier critical path et dépendances à fort impact.

- **ACTION:** Identifier critical path et dépendances à fort impact.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G13-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G13-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T08 — Valider le graphe contre CREATE/ADOPT/MAP/LAB.

- **ACTION:** Valider le graphe contre CREATE/ADOPT/MAP/LAB.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G13-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G13-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T09 — Définir comportements en cas de cycle/unknown.

- **ACTION:** Définir comportements en cas de cycle/unknown.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G13-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G13-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `DEPENDENCY_REGISTRY_DATASET`
- `GLOBAL_DEPENDENCY_GRAPH`
- `INSTALL_ORDER`
- `VALIDATION_ORDER`
- `REPAIR_ORDER`
- `DEPENDENCY_GAP_REPORT`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-DEPENDENCY-REGISTRY — DEPENDENCY_REGISTRY_DATASET
- type: `REGISTRY`
- produced_by: `GMC-G13`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G14`, `GMC-G16`, `GMC-G17`, `GMC-G18`

#### GMA-GLOBAL-DEPENDENCY-GRAPH — GLOBAL_DEPENDENCY_GRAPH
- type: `GRAPH`
- produced_by: `GMC-G13`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G14`, `GMC-G16`, `GMC-G17`, `GMC-G18`

#### GMA-INSTALL-ORDER — INSTALL_ORDER
- type: `ORDER`
- produced_by: `GMC-G13`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G14`, `GMC-G16`, `GMC-G17`, `GMC-G18`

#### GMA-VALIDATION-ORDER — VALIDATION_ORDER
- type: `ORDER`
- produced_by: `GMC-G13`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G14`, `GMC-G16`, `GMC-G17`, `GMC-G18`

#### GMA-REPAIR-ORDER — REPAIR_ORDER
- type: `ORDER`
- produced_by: `GMC-G13`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G14`, `GMC-G16`, `GMC-G17`, `GMC-G18`

#### GMA-DEPENDENCY-GAP-REPORT — DEPENDENCY_GAP_REPORT
- type: `REPORT`
- produced_by: `GMC-G13`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G14`, `GMC-G16`, `GMC-G17`, `GMC-G18`

### EXIT CONTROLS

#### GMC-EXIT-G13-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G13-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G13-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Toutes les dépendances ont source/type/direction.
- Cycles résolus ou HOLD.
- Ordres nécessaires calculables déterministiquement.

### FAILURE / HOLD CONDITIONS

- Cycle critique non résolu.
- Dépendance nécessaire sans cible stable.

### OUTPUTS / CONSUMED BY

- `GMC-G14`
- `GMC-G16`
- `GMC-G17`
- `GMC-G18`

---

## GMC-G14 — SEMANTIC COMPARISON CONTRACT

**Legacy reference:** `GMC-14`  
**Phase:** `GMC-E`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Permettre une comparaison sémantique fiable entre le modèle et un repository cible, ainsi qu'une résolution explicite de l'applicabilité.

### OBJECTIVE

Définir le contrat sémantique modèle↔repository qui classe un élément sans dépendre des noms de fichiers.

### INPUTS

- `GMC-G13 validated outputs`

### PREREQUISITES

- GMC-G13 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G13` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-DEPENDENCY-REGISTRY` — DEPENDENCY_REGISTRY_DATASET; producer: `GMC-G13`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-GLOBAL-DEPENDENCY-GRAPH` — GLOBAL_DEPENDENCY_GRAPH; producer: `GMC-G13`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-DOMAIN-REGISTRY` — DOMAIN_REGISTRY_DATASET; producer: `GMC-G03`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-CAPABILITY-REGISTRY` — CAPABILITY_REGISTRY_DATASET; producer: `GMC-G04`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-COMPONENT-REGISTRY` — COMPONENT_REGISTRY_DATASET; producer: `GMC-G05`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-CONTROL-REGISTRY` — CONTROL_REGISTRY_DATASET; producer: `GMC-G09`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-GATE-REGISTRY` — GATE_REGISTRY_DATASET; producer: `GMC-G10`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G14-PROVENANCE-COMPLETE`
- `EVREQ-G14-OUTPUTS-VALIDATED`
- `EVREQ-G14-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `datasets G03-G13`
- `ADOPT_EXISTING_REPOSITORY parcours/tests`
- `MAP_EXISTING_PROJECT parcours`
- `existing adoption self-test`
- `CP-ARCH-001 invariant semantic comparison`

### SEARCH PATTERNS

- `PRESENT_EXACT`
- `PRESENT_EQUIVALENT`
- `PRESENT_PARTIAL`
- `ABSENT`
- `CONFLICT`
- `OBSOLETE`
- `UNKNOWN`
- `NOT_APPLICABLE`
- `REUSE`
- `EXTEND`
- `DISCOVER`
- `HOLD`
- `MIGRATE`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G14-T01 — Définir le modèle d'observation d'un target repository.

- **ACTION:** Définir le modèle d'observation d'un target repository.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G14-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G14-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T02 — Définir les clés de matching sémantique par type.

- **ACTION:** Définir les clés de matching sémantique par type.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G14-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G14-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T03 — Formaliser les huit classifications et conditions.

- **ACTION:** Formaliser les huit classifications et conditions.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G14-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G14-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T04 — Formaliser les actions REUSE/MAP_REUSE/EXTEND/ADD/HOLD/MIGRATE/DISCOVER/SKIP.

- **ACTION:** Formaliser les actions REUSE/MAP_REUSE/EXTEND/ADD/HOLD/MIGRATE/DISCOVER/SKIP.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G14-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G14-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T05 — Définir résolution quand plusieurs classifications candidates existent.

- **ACTION:** Définir résolution quand plusieurs classifications candidates existent.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G14-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G14-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T06 — Définir traitement UNKNOWN et recherches supplémentaires.

- **ACTION:** Définir traitement UNKNOWN et recherches supplémentaires.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G14-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G14-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T07 — Définir interaction applicability/dependencies.

- **ACTION:** Définir interaction applicability/dependencies.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G14-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G14-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T08 — Définir le schéma ComparisonResult.

- **ACTION:** Définir le schéma ComparisonResult.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G14-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G14-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T09 — Construire des cas d'exemple CREATE/ADOPT/MAP.

- **ACTION:** Construire des cas d'exemple CREATE/ADOPT/MAP.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G14-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G14-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T10 — Formaliser l'Applicability Contract réutilisable par CREATE/ADOPT/MAP/LAB.

- **ACTION:** Formaliser l'Applicability Contract réutilisable par CREATE/ADOPT/MAP/LAB.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G14-T10-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G14-T10-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `COMPARISON_CONTRACT_SPEC`
- `COMPARISON_CLASSIFICATION_RULES`
- `COMPARISON_RESULT_MODEL`
- `ACTION_MAPPING`
- `APPLICABILITY_CONTRACT_SPEC`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-COMPARISON-CONTRACT — COMPARISON_CONTRACT_SPEC
- type: `CONTRACT`
- produced_by: `GMC-G14`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G15`, `GMC-G16`, `GMC-G18`

#### GMA-COMPARISON-CLASSIFICATION-RULES — COMPARISON_CLASSIFICATION_RULES
- type: `CONTRACT`
- produced_by: `GMC-G14`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G15`, `GMC-G16`, `GMC-G18`

#### GMA-COMPARISON-RESULT-MODEL — COMPARISON_RESULT_MODEL
- type: `MODEL`
- produced_by: `GMC-G14`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G15`, `GMC-G16`, `GMC-G18`

#### GMA-ACTION-MAPPING — ACTION_MAPPING
- type: `KNOWLEDGE_ARTIFACT`
- produced_by: `GMC-G14`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G15`, `GMC-G16`, `GMC-G18`

#### GMA-APPLICABILITY-CONTRACT — APPLICABILITY_CONTRACT_SPEC
- type: `CONTRACT`
- produced_by: `GMC-G14`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G15`, `GMC-G16`, `GMC-G18`

### EXIT CONTROLS

#### GMC-EXIT-G14-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G14-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G14-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Chaque classification a des critères déterministes.
- Matching jamais filename-only.
- UNKNOWN/CONFLICT conduisent à découverte/revue, jamais à une invention.

### FAILURE / HOLD CONDITIONS

- Deux classifications restent possibles avec la même preuve.
- Action risquerait d'écraser une implémentation mal comprise.

### OUTPUTS / CONSUMED BY

- `GMC-G15`
- `GMC-G16`
- `GMC-G18`

---

## GMC-G15 — FIELD-LEVEL / FINE-GRAINED COMPARISON

**Legacy reference:** `GMC-15`  
**Phase:** `GMC-E`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Permettre de détecter les équivalences et divergences fines jusque dans les champs, contraintes, lifecycle, contrôles et tests.

### OBJECTIVE

Étendre la comparaison aux objets, champs, types, cardinalités, contraintes, lifecycle, authority, controls et tests.

### INPUTS

- `GMC-G14 validated outputs`

### PREREQUISITES

- GMC-G14 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G14` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-COMPARISON-CONTRACT` — COMPARISON_CONTRACT_SPEC; producer: `GMC-G14`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-COMPARISON-RESULT-MODEL` — COMPARISON_RESULT_MODEL; producer: `GMC-G14`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-OBJECT-REGISTRY` — OBJECT_REGISTRY_DATASET; producer: `GMC-G06`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-FIELD-REGISTRY` — FIELD_REGISTRY_DATASET; producer: `GMC-G06`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-RELATIONSHIP-REGISTRY` — RELATIONSHIP_REGISTRY_DATASET; producer: `GMC-G06`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-CONTROL-REGISTRY` — CONTROL_REGISTRY_DATASET; producer: `GMC-G09`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-TEST-REGISTRY` — TEST_REGISTRY_DATASET; producer: `GMC-G12`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-APPLICABILITY-CONTRACT` — APPLICABILITY_CONTRACT_SPEC; producer: `GMC-G14`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G15-PROVENANCE-COMPLETE`
- `EVREQ-G15-OUTPUTS-VALIDATED`
- `EVREQ-G15-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `OBJECT/FIELD/RELATIONSHIP datasets`
- `STATE/TRANSITION datasets`
- `CONTROL/TEST/IMPLEMENTATION maps`
- `schemas/*.json`
- `SQL schema`
- `examples de repositories cibles`

### SEARCH PATTERNS

- `alias`
- `equivalent`
- `type`
- `enum`
- `required`
- `optional`
- `cardinality`
- `constraint`
- `lifecycle`
- `authority`
- `covers`
- `control`
- `test`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G15-T01 — Définir matching exact, alias et équivalence sémantique des champs.

- **ACTION:** Définir matching exact, alias et équivalence sémantique des champs.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G15-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G15-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T02 — Définir matrice de compatibilité des types.

- **ACTION:** Définir matrice de compatibilité des types.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G15-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G15-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T03 — Définir règles enum exact/subset/superset/conflict.

- **ACTION:** Définir règles enum exact/subset/superset/conflict.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G15-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G15-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T04 — Définir règles required/optional/default/nullability.

- **ACTION:** Définir règles required/optional/default/nullability.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G15-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G15-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T05 — Définir règles cardinalité/relation compatibility.

- **ACTION:** Définir règles cardinalité/relation compatibility.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G15-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G15-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T06 — Comparer contraintes, mutabilité, lifecycle et authority.

- **ACTION:** Comparer contraintes, mutabilité, lifecycle et authority.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G15-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G15-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T07 — Définir comparaison control coverage et test coverage.

- **ACTION:** Définir comparaison control coverage et test coverage.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G15-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G15-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T08 — Définir remontée des différences fines vers PARTIAL/CONFLICT.

- **ACTION:** Définir remontée des différences fines vers PARTIAL/CONFLICT.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G15-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G15-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T09 — Produire des exemples de comparaison fine avec classification attendue.

- **ACTION:** Produire des exemples de comparaison fine avec classification attendue.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G15-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G15-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `FIELD_COMPARISON_RULES`
- `TYPE_COMPATIBILITY_MATRIX`
- `CONSTRAINT_COMPARISON_RULES`
- `FINE_GRAINED_GAP_MODEL`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-FIELD-COMPARISON-RULES — FIELD_COMPARISON_RULES
- type: `CONTRACT`
- produced_by: `GMC-G15`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G16`, `GMC-G18`, `GMC-G19`

#### GMA-TYPE-COMPATIBILITY-MATRIX — TYPE_COMPATIBILITY_MATRIX
- type: `MATRIX`
- produced_by: `GMC-G15`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G16`, `GMC-G18`, `GMC-G19`

#### GMA-CONSTRAINT-COMPARISON-RULES — CONSTRAINT_COMPARISON_RULES
- type: `CONTRACT`
- produced_by: `GMC-G15`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G16`, `GMC-G18`, `GMC-G19`

#### GMA-FINE-GRAINED-GAP-MODEL — FINE_GRAINED_GAP_MODEL
- type: `MODEL`
- produced_by: `GMC-G15`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G16`, `GMC-G18`, `GMC-G19`

### EXIT CONTROLS

#### GMC-EXIT-G15-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G15-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G15-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Différences structurelles importantes remontent déterministiquement.
- Équivalences fonctionnelles reconnues malgré noms différents.
- Conflit d'autorité/contrainte critique ne peut pas être EQUIVALENT.

### FAILURE / HOLD CONDITIONS

- Compatibilité exige une interprétation métier indisponible.
- Alias supposé sans preuve.

### OUTPUTS / CONSUMED BY

- `GMC-G16`
- `GMC-G18`
- `GMC-G19`

---

## GMC-G16 — CANONICAL REGISTRY MATERIALIZATION DESIGN

**Legacy reference:** `GMC-16`  
**Phase:** `GMC-F`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Définir comment les connaissances validées seront stockées une seule fois, validées par schemas et projetées dans la base existante.

### OBJECTIVE

Transformer tous les datasets validés en conception complète de la représentation machine-readable, schemas, contrats, versioning et projection relationnelle existante, sans créer un second système.

### INPUTS

- `GMC-G15 validated outputs`

### PREREQUISITES

- GMC-G15 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G15` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-DOMAIN-REGISTRY` — DOMAIN_REGISTRY_DATASET; producer: `GMC-G03`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-CAPABILITY-REGISTRY` — CAPABILITY_REGISTRY_DATASET; producer: `GMC-G04`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-COMPONENT-REGISTRY` — COMPONENT_REGISTRY_DATASET; producer: `GMC-G05`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-OBJECT-REGISTRY` — OBJECT_REGISTRY_DATASET; producer: `GMC-G06`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-FIELD-REGISTRY` — FIELD_REGISTRY_DATASET; producer: `GMC-G06`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-RELATIONSHIP-REGISTRY` — RELATIONSHIP_REGISTRY_DATASET; producer: `GMC-G06`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-STATE-REGISTRY` — STATE_REGISTRY_DATASET; producer: `GMC-G07`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-TRANSITION-REGISTRY` — TRANSITION_REGISTRY_DATASET; producer: `GMC-G08`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-WORKFLOW-REGISTRY` — WORKFLOW_REGISTRY_DATASET; producer: `GMC-G08`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-CONTROL-REGISTRY` — CONTROL_REGISTRY_DATASET; producer: `GMC-G09`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-GATE-REGISTRY` — GATE_REGISTRY_DATASET; producer: `GMC-G10`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-AUTHORITY-REGISTRY` — AUTHORITY_REGISTRY_DATASET; producer: `GMC-G10`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-EVIDENCE-TYPE-REGISTRY` — EVIDENCE_TYPE_REGISTRY_DATASET; producer: `GMC-G11`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-FAILURE-REGISTRY` — FAILURE_REGISTRY_DATASET; producer: `GMC-G08`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-RECOVERY-REGISTRY` — RECOVERY_REGISTRY_DATASET; producer: `GMC-G08`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-IMPLEMENTATION-REGISTRY` — IMPLEMENTATION_REGISTRY_DATASET; producer: `GMC-G12`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-TEST-REGISTRY` — TEST_REGISTRY_DATASET; producer: `GMC-G12`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-DEPENDENCY-REGISTRY` — DEPENDENCY_REGISTRY_DATASET; producer: `GMC-G13`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-APPLICABILITY-CONTRACT` — APPLICABILITY_CONTRACT_SPEC; producer: `GMC-G14`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-COMPARISON-CONTRACT` — COMPARISON_CONTRACT_SPEC; producer: `GMC-G14`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-FIELD-COMPARISON-RULES` — FIELD_COMPARISON_RULES; producer: `GMC-G15`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G16-PROVENANCE-COMPLETE`
- `EVREQ-G16-OUTPUTS-VALIDATED`
- `EVREQ-G16-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `tous datasets G01-G15`
- `docs/control-plane/DATA_MODEL.md`
- `.governance/control-plane-db/001_schema.sql`
- `.governance/control-plane-db/002_agent_activity.sql`
- `.governance/control-plane-db/003_canonical_authorities.sql`
- `.governance/control-plane-db/catalog.json`
- `.governance/control-plane-db/runtime-seed.json`
- `.governance/control-plane-db/materialize.py`

### SEARCH PATTERNS

- `migration`
- `schema`
- `materialize`
- `catalog`
- `seed`
- `authority`
- `revision`
- `manifest`
- `registry`
- `release`
- `version`
- `source_ref`
- `supersedes`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G16-T01 — Définir l'arborescence cible .governance/governance-model.

- **ACTION:** Définir l'arborescence cible .governance/governance-model.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G16-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G16-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T02 — Définir docs/governance-model et règles docs générées vs autorités manuelles.

- **ACTION:** Définir docs/governance-model et règles docs générées vs autorités manuelles.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G16-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G16-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T03 — Définir schemas/governance-model pour chaque registre et ComparisonResult.

- **ACTION:** Définir schemas/governance-model pour chaque registre et ComparisonResult.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G16-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G16-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T04 — Définir format de chaque registry JSON et références inter-registres.

- **ACTION:** Définir format de chaque registry JSON et références inter-registres.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G16-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G16-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T05 — Définir manifest model_id/model_version/status/registry pointers/contracts/releases.

- **ACTION:** Définir manifest model_id/model_version/status/registry pointers/contracts/releases.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G16-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G16-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T06 — Définir le plan de migration SQL additive governance_*.

- **ACTION:** Définir le plan de migration SQL additive governance_*.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G16-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G16-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T07 — Définir l'extension du materializer EXISTANT sans second materializer canonique.

- **ACTION:** Définir l'extension du materializer EXISTANT sans second materializer canonique.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G16-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G16-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T08 — Définir versioning modèle, release manifest, provenance et supersession.

- **ACTION:** Définir versioning modèle, release manifest, provenance et supersession.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G16-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G16-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T09 — Définir validations CI: schemas, IDs, refs, deps, model↔SQL parity, docs generation.

- **ACTION:** Définir validations CI: schemas, IDs, refs, deps, model↔SQL parity, docs generation.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G16-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G16-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T10 — Produire le plan d'implémentation ordonné, sans l'exécuter.

- **ACTION:** Produire le plan d'implémentation ordonné, sans l'exécuter.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G16-T10-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G16-T10-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `REGISTRY_STORAGE_ARCHITECTURE`
- `SCHEMA_PLAN`
- `SQL_MIGRATION_PLAN`
- `MATERIALIZER_EXTENSION_PLAN`
- `MODEL_VERSIONING_PLAN`
- `CI_VALIDATION_PLAN`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-REGISTRY-STORAGE-ARCHITECTURE — REGISTRY_STORAGE_ARCHITECTURE
- type: `REGISTRY`
- produced_by: `GMC-G16`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G17`, `GMC-G18`, `future implementation`

#### GMA-SCHEMA-PLAN — SCHEMA_PLAN
- type: `PLAN`
- produced_by: `GMC-G16`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G17`, `GMC-G18`, `future implementation`

#### GMA-SQL-MIGRATION-PLAN — SQL_MIGRATION_PLAN
- type: `PLAN`
- produced_by: `GMC-G16`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G17`, `GMC-G18`, `future implementation`

#### GMA-MATERIALIZER-EXTENSION-PLAN — MATERIALIZER_EXTENSION_PLAN
- type: `PLAN`
- produced_by: `GMC-G16`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G17`, `GMC-G18`, `future implementation`

#### GMA-MODEL-VERSIONING-PLAN — MODEL_VERSIONING_PLAN
- type: `PLAN`
- produced_by: `GMC-G16`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G17`, `GMC-G18`, `future implementation`

#### GMA-CI-VALIDATION-PLAN — CI_VALIDATION_PLAN
- type: `PLAN`
- produced_by: `GMC-G16`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G17`, `GMC-G18`, `future implementation`

### EXIT CONTROLS

#### GMC-EXIT-G16-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G16-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G16-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Structure cible complètement spécifiée.
- Aucune duplication DB/materializer/source of truth.
- Tous datasets G03-G15 ont un emplacement prévu.

### FAILURE / HOLD CONDITIONS

- Conception crée une source canonique concurrente.
- Un registre n'a pas de schema ou projection prévue.

### OUTPUTS / CONSUMED BY

- `GMC-G17`
- `GMC-G18`
- `future implementation`

---

## GMC-G17 — CONTROL PLANE CONSUMPTION DESIGN

**Legacy reference:** `GMC-17`  
**Phase:** `GMC-F`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Faire du Governance Model la référence chargée et validée par le Control Plane avant toute décision gouvernée.

### OBJECTIVE

Définir comment le Control Plane chargera, validera, versionnera et utilisera le Governance Model au cœur de ses décisions.

### INPUTS

- `GMC-G16 validated outputs`

### PREREQUISITES

- GMC-G16 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G16` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-REGISTRY-STORAGE-ARCHITECTURE` — REGISTRY_STORAGE_ARCHITECTURE; producer: `GMC-G16`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-SCHEMA-PLAN` — SCHEMA_PLAN; producer: `GMC-G16`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-SQL-MIGRATION-PLAN` — SQL_MIGRATION_PLAN; producer: `GMC-G16`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-MATERIALIZER-EXTENSION-PLAN` — MATERIALIZER_EXTENSION_PLAN; producer: `GMC-G16`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-MODEL-VERSIONING-PLAN` — MODEL_VERSIONING_PLAN; producer: `GMC-G16`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-CI-VALIDATION-PLAN` — CI_VALIDATION_PLAN; producer: `GMC-G16`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G17-PROVENANCE-COMPLETE`
- `EVREQ-G17-OUTPUTS-VALIDATED`
- `EVREQ-G17-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `REGISTRY_STORAGE_ARCHITECTURE`
- `scripts/governance_agent.py`
- `control-plane policies`
- `catalog.json`
- `runtime-seed.json`
- `session/work/checkpoint/handoff flows`
- `Governance CI`

### SEARCH PATTERNS

- `load`
- `manifest`
- `version`
- `dispatch`
- `validate`
- `authority`
- `session`
- `run`
- `model_version`
- `fail closed`
- `entry`
- `router`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G17-T01 — Identifier les entry points du Control Plane qui ont besoin du modèle.

- **ACTION:** Identifier les entry points du Control Plane qui ont besoin du modèle.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G17-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G17-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T02 — Définir séquence load manifest → resolve version → load registries → validate.

- **ACTION:** Définir séquence load manifest → resolve version → load registries → validate.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G17-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G17-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T03 — Définir dependency/applicability resolution contract.

- **ACTION:** Définir dependency/applicability resolution contract.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G17-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G17-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T04 — Définir fail-closed si manifest/schema/ref/dependency invalide.

- **ACTION:** Définir fail-closed si manifest/schema/ref/dependency invalide.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G17-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G17-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T05 — Définir liaison model_version avec runs/sessions/evidence/comparisons.

- **ACTION:** Définir liaison model_version avec runs/sessions/evidence/comparisons.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G17-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G17-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T06 — Définir interfaces modèle ↔ catalogue de parcours existant.

- **ACTION:** Définir interfaces modèle ↔ catalogue de parcours existant.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G17-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G17-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T07 — Définir observabilité/evidence du chargement/validation.

- **ACTION:** Définir observabilité/evidence du chargement/validation.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G17-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G17-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T08 — Définir backward compatibility avec CASE 1 et clients existants.

- **ACTION:** Définir backward compatibility avec CASE 1 et clients existants.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G17-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G17-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T09 — Définir matrice de tests nécessaire avant activation.

- **ACTION:** Définir matrice de tests nécessaire avant activation.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G17-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G17-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `CONTROL_PLANE_MODEL_CONSUMPTION_CONTRACT`
- `MODEL_LOAD_SEQUENCE`
- `FAIL_CLOSED_RULES`
- `BACKWARD_COMPATIBILITY_PLAN`
- `CONTROL_PLANE_TEST_MATRIX`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-CONTROL-PLANE-MODEL-CONSUMPTION-CONTRACT — CONTROL_PLANE_MODEL_CONSUMPTION_CONTRACT
- type: `CONTRACT`
- produced_by: `GMC-G17`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G18`, `GMC-G19`, `future implementation`

#### GMA-MODEL-LOAD-SEQUENCE — MODEL_LOAD_SEQUENCE
- type: `MODEL`
- produced_by: `GMC-G17`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G18`, `GMC-G19`, `future implementation`

#### GMA-FAIL-CLOSED-RULES — FAIL_CLOSED_RULES
- type: `CONTRACT`
- produced_by: `GMC-G17`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G18`, `GMC-G19`, `future implementation`

#### GMA-BACKWARD-COMPATIBILITY-PLAN — BACKWARD_COMPATIBILITY_PLAN
- type: `PLAN`
- produced_by: `GMC-G17`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G18`, `GMC-G19`, `future implementation`

#### GMA-CONTROL-PLANE-TEST-MATRIX — CONTROL_PLANE_TEST_MATRIX
- type: `MATRIX`
- produced_by: `GMC-G17`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G18`, `GMC-G19`, `future implementation`

### EXIT CONTROLS

#### GMC-EXIT-G17-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G17-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G17-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Control Plane dépend du modèle et non de fichiers ad hoc.
- Version du modèle utilisée par un run traçable.
- Non-régression des flux actuels prévue.

### FAILURE / HOLD CONDITIONS

- Nouveau loader contourne les autorités actuelles.
- Migration exige rupture non acceptée.

### OUTPUTS / CONSUMED BY

- `GMC-G18`
- `GMC-G19`
- `future implementation`

---

## GMC-G18 — FOUR-CASE REBIND DESIGN

**Legacy reference:** `GMC-18`  
**Phase:** `GMC-F`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Faire consommer le même modèle à CREATE, ADOPT, MAP et LAB sans dupliquer la connaissance commune.

### OBJECTIVE

Définir comment CREATE, ADOPT, MAP et LAB consommeront le même Governance Model avec seulement des stratégies d'application différentes.

### INPUTS

- `GMC-G17 validated outputs`

### PREREQUISITES

- GMC-G17 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G17` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-CONTROL-PLANE-MODEL-CONSUMPTION-CONTRACT` — CONTROL_PLANE_MODEL_CONSUMPTION_CONTRACT; producer: `GMC-G17`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-MODEL-LOAD-SEQUENCE` — MODEL_LOAD_SEQUENCE; producer: `GMC-G17`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-BACKWARD-COMPATIBILITY-PLAN` — BACKWARD_COMPATIBILITY_PLAN; producer: `GMC-G17`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-APPLICABILITY-CONTRACT` — APPLICABILITY_CONTRACT_SPEC; producer: `GMC-G14`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-COMPARISON-CONTRACT` — COMPARISON_CONTRACT_SPEC; producer: `GMC-G14`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-GLOBAL-DEPENDENCY-GRAPH` — GLOBAL_DEPENDENCY_GRAPH; producer: `GMC-G13`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G18-PROVENANCE-COMPLETE`
- `EVREQ-G18-OUTPUTS-VALIDATED`
- `EVREQ-G18-NO-UNRESOLVED-CRITICAL-BLOCKER`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `CONTROL_PLANE_MODEL_CONSUMPTION_CONTRACT`
- `.governance/control-plane-db/catalog.json`
- `CASE1 replay/program`
- `adoption tests/docs`
- `project mapping docs`
- `LAB evolution docs`
- `comparison/applicability/dependency contracts`

### SEARCH PATTERNS

- `CREATE_NEW_REPOSITORY`
- `ADOPT_EXISTING_REPOSITORY`
- `MAP_EXISTING_PROJECT`
- `LAB_EVOLUTION`
- `instantiate`
- `compare`
- `apply`
- `read-only`
- `candidate`
- `release`
- `integration plan`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G18-T01 — Construire le Common Case Adapter Contract.

- **ACTION:** Construire le Common Case Adapter Contract.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G18-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G18-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T02 — Mapper CREATE: applicability → dependency order → instantiate → validate → attest.

- **ACTION:** Mapper CREATE: applicability → dependency order → instantiate → validate → attest.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G18-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G18-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T03 — Mapper ADOPT: observe → compare → gaps/conflicts → additive integration plan → verify.

- **ACTION:** Mapper ADOPT: observe → compare → gaps/conflicts → additive integration plan → verify.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G18-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G18-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T04 — Mapper MAP: observe → map → compare → gaps → evidence, avec NO WRITE.

- **ACTION:** Mapper MAP: observe → map → compare → gaps → evidence, avec NO WRITE.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G18-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G18-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T05 — Mapper LAB: baseline model → candidate → model-to-model compare → regression → release.

- **ACTION:** Mapper LAB: baseline model → candidate → model-to-model compare → regression → release.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G18-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G18-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T06 — Définir outputs communs et spécifiques.

- **ACTION:** Définir outputs communs et spécifiques.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G18-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G18-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T07 — Définir write/authority/gate policies par stratégie.

- **ACTION:** Définir write/authority/gate policies par stratégie.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G18-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G18-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T08 — Définir matrice de regression sur un même model_version.

- **ACTION:** Définir matrice de regression sur un même model_version.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G18-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G18-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T09 — Définir migration du catalog.json vers consommation du modèle sans perdre l'historique.

- **ACTION:** Définir migration du catalog.json vers consommation du modèle sans perdre l'historique.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G18-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G18-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T10 — Vérifier qu'aucun élément central n'est redéfini en doublon dans un cas.

- **ACTION:** Vérifier qu'aucun élément central n'est redéfini en doublon dans un cas.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G18-T10-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G18-T10-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `FOUR_CASE_CONSUMPTION_MAP`
- `COMMON_CASE_ADAPTER_CONTRACT`
- `CREATE_MODEL_BINDING`
- `ADOPT_MODEL_BINDING`
- `MAP_MODEL_BINDING`
- `LAB_MODEL_BINDING`
- `CROSS_CASE_REGRESSION_MATRIX`
- `INTEGRATION_CONTRACT_SPEC`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-FOUR-CASE-CONSUMPTION-MAP — FOUR_CASE_CONSUMPTION_MAP
- type: `KNOWLEDGE_ARTIFACT`
- produced_by: `GMC-G18`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G19`, `future case implementation/validation`

#### GMA-COMMON-CASE-ADAPTER-CONTRACT — COMMON_CASE_ADAPTER_CONTRACT
- type: `CONTRACT`
- produced_by: `GMC-G18`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G19`, `future case implementation/validation`

#### GMA-CREATE-MODEL-BINDING — CREATE_MODEL_BINDING
- type: `MODEL`
- produced_by: `GMC-G18`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G19`, `future case implementation/validation`

#### GMA-ADOPT-MODEL-BINDING — ADOPT_MODEL_BINDING
- type: `MODEL`
- produced_by: `GMC-G18`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G19`, `future case implementation/validation`

#### GMA-MAP-MODEL-BINDING — MAP_MODEL_BINDING
- type: `MODEL`
- produced_by: `GMC-G18`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G19`, `future case implementation/validation`

#### GMA-LAB-MODEL-BINDING — LAB_MODEL_BINDING
- type: `MODEL`
- produced_by: `GMC-G18`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G19`, `future case implementation/validation`

#### GMA-CROSS-CASE-REGRESSION-MATRIX — CROSS_CASE_REGRESSION_MATRIX
- type: `MATRIX`
- produced_by: `GMC-G18`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G19`, `future case implementation/validation`

#### GMA-INTEGRATION-CONTRACT — INTEGRATION_CONTRACT_SPEC
- type: `CONTRACT`
- produced_by: `GMC-G18`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `GMC-G19`, `future case implementation/validation`

### EXIT CONTROLS

#### GMC-EXIT-G18-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G18-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G18-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Les quatre cas référencent les mêmes IDs modèle.
- Chaque divergence est une stratégie, pas une redéfinition.
- MAP read-only; ADOPT additive; CREATE/LAB partagent les mêmes registries.

### FAILURE / HOLD CONDITIONS

- Un cas exige une redéfinition incompatible.
- Une stratégie ne peut respecter les controls/gates communs.

### OUTPUTS / CONSUMED BY

- `GMC-G19`
- `future case implementation/validation`

---

## GMC-G19 — GLOBAL VALIDATION / FIRST GOVERNANCE MODEL RELEASE

**Legacy reference:** `GMC-19`  
**Phase:** `GMC-G`  
**Status:** `PLANNED / PLANNING_ONLY`

### PURPOSE

Assembler toutes les connaissances produites, démontrer leur cohérence et préparer la première release complète et attestée du Governance Model.

### OBJECTIVE

Assembler et valider tous les résultats, prouver cohérence/traçabilité/réutilisation cross-case et préparer la première release complète du Governance Model.

### INPUTS

- `GMC-G18 validated outputs`

### PREREQUISITES

- GMC-G18 has a VALIDATED_EXIT.
- All artifact dependencies are in VALIDATED state and sufficiently complete for this group.
- All evidence dependencies are present.
- No unresolved critical blocker is carried from upstream.

### DEPENDENCY CONTRACT

#### TASK_DEPENDENCY
- `GMC-G18` must reach `VALIDATED_EXIT`.

#### ARTIFACT_DEPENDENCY
- `GMA-FOUR-CASE-CONSUMPTION-MAP` — FOUR_CASE_CONSUMPTION_MAP; producer: `GMC-G18`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-COMMON-CASE-ADAPTER-CONTRACT` — COMMON_CASE_ADAPTER_CONTRACT; producer: `GMC-G18`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-INTEGRATION-CONTRACT` — INTEGRATION_CONTRACT_SPEC; producer: `GMC-G18`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-CREATE-MODEL-BINDING` — CREATE_MODEL_BINDING; producer: `GMC-G18`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-ADOPT-MODEL-BINDING` — ADOPT_MODEL_BINDING; producer: `GMC-G18`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-MAP-MODEL-BINDING` — MAP_MODEL_BINDING; producer: `GMC-G18`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-LAB-MODEL-BINDING` — LAB_MODEL_BINDING; producer: `GMC-G18`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.
- `GMA-CROSS-CASE-REGRESSION-MATRIX` — CROSS_CASE_REGRESSION_MATRIX; producer: `GMC-G18`; required state: `VALIDATED`; completeness: `SUFFICIENT_FOR_CONSUMER_SCOPE`.

#### EVIDENCE_DEPENDENCY
- `EVREQ-G19-PROVENANCE-COMPLETE`
- `EVREQ-G19-OUTPUTS-VALIDATED`
- `EVREQ-G19-NO-UNRESOLVED-CRITICAL-BLOCKER`
- `EVREQ-G19-MODEL-COMPLETENESS-PASS`
- `EVREQ-G19-MODEL-CONSISTENCY-PASS`
- `EVREQ-G19-REFERENCE-INTEGRITY-PASS`
- `EVREQ-G19-IMPLEMENTATION-TRACEABILITY-PASS`
- `EVREQ-G19-TEST-COVERAGE-PASS`
- `EVREQ-G19-EVIDENCE-COVERAGE-PASS`
- `EVREQ-G19-DEPENDENCY-INTEGRITY-PASS`
- `EVREQ-G19-REUSABILITY-PASS`
- `EVREQ-G19-CREATE-COMPATIBILITY-PASS`
- `EVREQ-G19-ADOPT-COMPATIBILITY-PASS`
- `EVREQ-G19-MAP-COMPATIBILITY-PASS`
- `EVREQ-G19-LAB-COMPATIBILITY-PASS`

**Unlock rule:** `ALL_TASK_DEPENDENCIES_SATISFIED_AND_ALL_REQUIRED_ARTIFACTS_VALIDATED_AND_ALL_REQUIRED_EVIDENCE_PRESENT_AND_EXIT_CONTROLS_PASS`

### QUESTIONS TO RESOLVE

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### WHERE TO LOOK

- `toutes sorties G01-G18`
- `CP-ARCH-001`
- `CP-GOVMODEL-001`
- `Governance CI/test matrix`
- `case E2E evidence`
- `implementation/test/dependency maps`
- `comparison examples/results`
- `canonical authority revisioning`

### SEARCH PATTERNS

- `coverage`
- `orphan`
- `unresolved`
- `conflict`
- `gap`
- `PASS`
- `attest`
- `release`
- `version`
- `supersedes`
- `traceability`
- `case`
- `regression`

### SEARCH ORDER

- authorities/docs
- machine state/policies/schemas
- executable scripts/workflows
- tests/CI
- relational/runtime evidence

### TASKS / ACTIONS

Each task is planning-only until future execution is separately authorized.

#### GMC-G19-T01 — Exécuter completeness review de tous les registries/contracts prévus.

- **ACTION:** Exécuter completeness review de tous les registries/contracts prévus.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G19-T01-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G19-T01-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T02 — Exécuter consistency review IDs/refs/dependencies/lifecycle/applicability.

- **ACTION:** Exécuter consistency review IDs/refs/dependencies/lifecycle/applicability.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G19-T02-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G19-T02-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T03 — Vérifier traçabilité source↔model↔implementation↔test/evidence.

- **ACTION:** Vérifier traçabilité source↔model↔implementation↔test/evidence.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G19-T03-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G19-T03-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T04 — Valider matrice cross-case CREATE/ADOPT/MAP/LAB.

- **ACTION:** Valider matrice cross-case CREATE/ADOPT/MAP/LAB.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G19-T04-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G19-T04-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T05 — Définir/valider model-to-model release diff et compatibilité.

- **ACTION:** Définir/valider model-to-model release diff et compatibilité.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G19-T05-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G19-T05-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T06 — Classer tous les gaps en BLOCKER/POST-1.0/FUTURE.

- **ACTION:** Classer tous les gaps en BLOCKER/POST-1.0/FUTURE.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G19-T06-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G19-T06-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T07 — Préparer release manifest Governance Model 1.0.0 et mapping Template versions.

- **ACTION:** Préparer release manifest Governance Model 1.0.0 et mapping Template versions.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G19-T07-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G19-T07-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T08 — Définir attestation/evidence bundle/checkpoint/handoff/release gate.

- **ACTION:** Définir attestation/evidence bundle/checkpoint/handoff/release gate.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G19-T08-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G19-T08-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T09 — N'autoriser 1.0.0 que si tous exit gates critiques PASS.

- **ACTION:** N'autoriser 1.0.0 que si tous exit gates critiques PASS.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G19-T09-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G19-T09-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T10 — Préparer handoff PostgreSQL/API/Admin UI après stabilisation.

- **ACTION:** Préparer handoff PostgreSQL/API/Admin UI après stabilisation.
- **METHOD:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **CONTROL:** `GMC-G19-T10-CONTROL`
  - PASS: Task scope is complete; provenance is complete; conflicts/unknowns are explicit; no silent inference; task result is usable by the next task or exit gate.
  - FAIL: `HOLD_TASK_AND_RECORD_BLOCKER`
- **EVIDENCE:** `source path/ref`, `subject HEAD/version when relevant`, `classification rationale`
- **INTERMEDIATE RESULT:** `GMC-G19-T10-RESULT`; persistent by default: **NO**; promotion requires group validation.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### EXPECTED RESULTS

- `GOVERNANCE_MODEL_COMPLETENESS_REPORT`
- `TRACEABILITY_MATRIX`
- `CROSS_CASE_VALIDATION_REPORT`
- `RELEASE_READINESS_REPORT`
- `GOVERNANCE_MODEL_1_0_0_RELEASE_PLAN`
- `RELEASE_CONTRACT_SPEC`
- `FINAL_GOVERNANCE_MODEL_ASSEMBLY`

### PERSISTENT KNOWLEDGE ARTIFACTS

#### GMA-GOVERNANCE-MODEL-COMPLETENESS-REPORT — GOVERNANCE_MODEL_COMPLETENESS_REPORT
- type: `REPORT`
- produced_by: `GMC-G19`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `future PostgreSQL projection`, `Governance API`, `Admin UI`, `subsequent Governance Model releases`

#### GMA-TRACEABILITY-MATRIX — TRACEABILITY_MATRIX
- type: `MATRIX`
- produced_by: `GMC-G19`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `future PostgreSQL projection`, `Governance API`, `Admin UI`, `subsequent Governance Model releases`

#### GMA-CROSS-CASE-VALIDATION-REPORT — CROSS_CASE_VALIDATION_REPORT
- type: `REPORT`
- produced_by: `GMC-G19`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `future PostgreSQL projection`, `Governance API`, `Admin UI`, `subsequent Governance Model releases`

#### GMA-RELEASE-READINESS-REPORT — RELEASE_READINESS_REPORT
- type: `REPORT`
- produced_by: `GMC-G19`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `future PostgreSQL projection`, `Governance API`, `Admin UI`, `subsequent Governance Model releases`

#### GMA-GOVERNANCE-MODEL-1-0-0-RELEASE-PLAN — GOVERNANCE_MODEL_1_0_0_RELEASE_PLAN
- type: `PLAN`
- produced_by: `GMC-G19`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `future PostgreSQL projection`, `Governance API`, `Admin UI`, `subsequent Governance Model releases`

#### GMA-RELEASE-CONTRACT — RELEASE_CONTRACT_SPEC
- type: `CONTRACT`
- produced_by: `GMC-G19`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `future PostgreSQL projection`, `Governance API`, `Admin UI`, `subsequent Governance Model releases`

#### GMA-FINAL-GOVERNANCE-MODEL-ASSEMBLY — FINAL_GOVERNANCE_MODEL_ASSEMBLY
- type: `MODEL`
- produced_by: `GMC-G19`
- planned initial version: `v1`
- status: `PLANNED`
- validation_state: `NOT_YET_PRODUCED`
- persistent knowledge object: `true`
- provenance required: `true`
- supersession: `APPEND_SUPERSEDE_REVALIDATE`
- consumed_by: `future PostgreSQL projection`, `Governance API`, `Admin UI`, `subsequent Governance Model releases`

### EXIT CONTROLS

#### GMC-EXIT-G19-ARTIFACTS-PRESENT
- purpose: Verify every declared work-package output artifact exists as a planned/validated knowledge object.
- PASS: all declared output artifacts exist and are addressable by stable artifact_id
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G19-PROVENANCE-COMPLETE
- purpose: Prevent unsourced knowledge from becoming canonical.
- PASS: every normalized item in output artifacts carries required provenance or an explicit UNKNOWN/HOLD classification
- FAIL: `HOLD_WORK_PACKAGE`

#### GMC-EXIT-G19-VALIDATION-PASS
- purpose: Ensure outputs satisfy the group's exit criteria.
- PASS: all exit criteria pass and no critical contradiction is unresolved
- FAIL: `HOLD_WORK_PACKAGE`

### EXIT CRITERIA

- Aucun blocker critique ouvert.
- Traçabilité complète pour éléments critiques.
- Quatre cas consomment le même modèle avec evidence cross-case.
- Release gate 1.0.0 explicitement PASS.

### FAILURE / HOLD CONDITIONS

- Gap critique non résolu.
- Régression cross-case.
- Référence/contrôle/transition critique non testable ou non prouvée.

### OUTPUTS / CONSUMED BY

- `future PostgreSQL projection`
- `Governance API`
- `Admin UI`
- `subsequent Governance Model releases`

---

## 5. FINAL GOVERNANCE MODEL — GMC-G19 ASSEMBLY CONTRACT

GMC-G19 does not pass because G01..G18 are merely marked DONE. It must assemble and validate the complete model.

### Required model components

- `DOMAIN_REGISTRY`
- `CAPABILITY_REGISTRY`
- `COMPONENT_REGISTRY`
- `OBJECT_REGISTRY`
- `FIELD_REGISTRY`
- `RELATIONSHIP_REGISTRY`
- `STATE_REGISTRY`
- `TRANSITION_REGISTRY`
- `WORKFLOW_REGISTRY`
- `CONTROL_REGISTRY`
- `GATE_REGISTRY`
- `AUTHORITY_REGISTRY`
- `EVIDENCE_TYPE_REGISTRY`
- `FAILURE_REGISTRY`
- `RECOVERY_REGISTRY`
- `IMPLEMENTATION_REGISTRY`
- `TEST_REGISTRY`
- `DEPENDENCY_REGISTRY`
- `APPLICABILITY_CONTRACT`
- `COMPARISON_CONTRACT`
- `INTEGRATION_CONTRACT`
- `RELEASE_CONTRACT`

### Required demonstrations

- `MODEL_COMPLETENESS = PASS`
- `MODEL_CONSISTENCY = PASS`
- `REFERENCE_INTEGRITY = PASS`
- `IMPLEMENTATION_TRACEABILITY = PASS`
- `TEST_COVERAGE = PASS`
- `EVIDENCE_COVERAGE = PASS`
- `DEPENDENCY_INTEGRITY = PASS`
- `REUSABILITY = PASS`
- `CREATE_COMPATIBILITY = PASS`
- `ADOPT_COMPATIBILITY = PASS`
- `MAP_COMPATIBILITY = PASS`
- `LAB_COMPATIBILITY = PASS`

### Release rule

`GOVERNANCE_MODEL_1_0_0_FORBIDDEN_UNTIL_ALL_REQUIRED_DEMONSTRATIONS_PASS_AND_REQUIRED_ARTIFACTS_ARE_VALIDATED`

## 6. Definition of Ready for future implementation

- Upstream task dependencies have validated exits.
- Required artifacts exist in validated state and are sufficiently complete for the consumer.
- Required evidence dependencies are satisfied.
- Exit controls have passed.
- Exact current main HEAD is reobserved.
- Applicable authorities are loaded and reconciled.
- The implementation task is separately authorized by governance.
- Non-regression proof expectations are known.

## 7. Non-goals

This blueprint still does **not** implement the future registries, schemas, SQL migration, comparator, applicability engine, model loader or CREATE/ADOPT/MAP/LAB rebinding.


## 8. Projection reciprocity invariant

Artifact dependencies have one canonical machine source:

`groups[*].dependency_contract.artifact_dependencies`.

For every artifact, the GMC work-package consumers recorded in both produced-artifact metadata and the global knowledge-artifact registry are derived from that source. Global `ARTIFACT_DEPENDENCY` edges must represent exactly the same `artifact → consumer work package` relationships with the same producer.

External/future consumers are metadata, not current work-package dependency edges.

The governance CI regression test `scripts/test_governance_model_integrity.py` verifies dependency-contract ↔ dependency-edge reciprocity, artifact producer identity, both consumer projections, uniqueness, and catalogue revision consistency.

Any divergence fails closed before downstream work may be unlocked.
