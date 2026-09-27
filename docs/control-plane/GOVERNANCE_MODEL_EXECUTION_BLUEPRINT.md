# GOVERNANCE MODEL EXECUTION BLUEPRINT

> Parent authority: `CP-GOVMODEL-001`  
> Decision: `CPD-028`  
> Scope: `CONTROL_PLANE_SOURCE_ONLY`  
> Status: `PLANNING_ONLY`  
> Implementation authorized: **NO**

## 1. Operating rule

The 19 GMC identifiers are chronological **work packages/groups**, not atomic tasks.

```text
WORK PACKAGE
  → mission / objective
  → questions to resolve
  → source surfaces + search patterns
  → atomic tasks
  → intermediate results
  → validation
  → stored/versioned output
  → evidence
  → exit gate
  → downstream consumers
```

A downstream group is unlocked by **validated outputs + evidence**, not merely because the preceding group is marked DONE.

This blueprint is planning only. It does not authorize creating future registries, schemas, SQL migrations, comparator/applicability code, model loaders or case rewiring.

## 2. Shared research surface

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

Default research order: authorities/docs → machine state/policies/schemas → executable scripts/workflows → tests/CI → relational/runtime evidence → reconciliation.

Classification discipline: `OBSERVED_EXPLICIT`, `OBSERVED_IMPLICIT`, `DOCUMENTED_ONLY`, `IMPLEMENTED_ONLY`, `TESTED`, `PARTIAL`, `CONFLICTING`, `OBSOLETE`, `UNKNOWN`.

No `UNKNOWN` may be silently converted into a canonical fact.

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

---

## GMC-G01 — BOUNDARY — MODEL / CASE / RUNTIME / PROJECTION

**Legacy reference:** `GMC-01`  
**Phase:** `GMC-A`  
**Status:** `PLANNED / PLANNING_ONLY`

### Mission / objectif

Établir la frontière canonique entre le Governance Model central, les stratégies CREATE/ADOPT/MAP/LAB, le runtime d'exécution et les projections.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `CP-ARCH-001`
- `CP-GOVMODEL-001`
- `existing canonical memory`

### Où chercher

- `docs/control-plane/CANONICAL_ARCHITECTURE.md`
- `docs/control-plane/GOVERNANCE_MODEL_CATALOGUE.md`
- `.governance/control-plane-db/catalog.json`
- `.governance/control-plane-db/runtime-seed.json`
- `.governance/TEMPLATE_MANIFEST.json`
- `.governance/*policy*.json`

### Recherches ciblées

- `CREATE_NEW_REPOSITORY`
- `ADOPT_EXISTING_REPOSITORY`
- `MAP_EXISTING_PROJECT`
- `LAB_EVOLUTION`
- `SOURCE_ONLY`
- `CLIENT`
- `PROJECTION`
- `RUNTIME`

### Tâches atomiques

#### GMC-G01-T01 — Recenser toutes les autorités et artefacts de gouvernance connus.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G01-T02 — Classifier chaque artefact/règle en MODEL, APPLICATION_STRATEGY, RUNTIME_EXECUTION, PROJECTION ou UNRESOLVED.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G01-T03 — Inventorier les sémantiques communes enfermées ou dupliquées dans un seul cas.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G01-T04 — Cartographier la frontière source-control-plane versus surface distribuée aux clients.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G01-T05 — Séparer données de définition réutilisables et données d'exécution concrètes.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G01-T06 — Identifier contradictions, chevauchements et éléments sans propriétaire canonique.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G01-T07 — Produire MODEL_BOUNDARY_MATRIX avec provenance.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G01-T08 — Valider la matrice contre CP-ARCH-001, CP-GOVMODEL-001 et les décisions.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `MODEL_BOUNDARY_MATRIX`
- `MODEL_CLASSIFICATION_TAXONOMY`
- `UNRESOLVED_BOUNDARY_ITEMS`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Tous les artefacts inventoriés sont classifiés ou explicitement UNRESOLVED.
- Aucune sémantique commune connue n'est attribuée silencieusement à un seul cas.

### Conditions HOLD / BLOCKED

- Contradiction entre autorités sans règle de préséance.
- Artefact critique dont le rôle reste indéterminable.

### Réutilisé par

- `GMC-G02`
- `GMC-G03`
- `GMC-G12`
- `GMC-G18`

---

## GMC-G02 — METAMODEL — ANATOMIE, IDS ET CONTRATS COMMUNS

**Legacy reference:** `GMC-02`  
**Phase:** `GMC-A`  
**Status:** `PLANNED / PLANNING_ONLY`

### Mission / objectif

Définir le métamodèle canonique, les IDs stables, les champs communs, les références, la provenance, le versioning et la supersession.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G01 validated outputs`

### Où chercher

- `sorties GMC-G01`
- `.governance/control-plane-db/003_canonical_authorities.sql`
- `docs/control-plane/DATA_MODEL.md`
- `schemas/*.json`
- `.governance/control-plane-state/canonical-architecture.json`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G02-T01 — Définir les 18 types d'entités du modèle.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G02-T02 — Définir les namespaces et conventions d'IDs stables.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G02-T03 — Définir les métadonnées communes obligatoires.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G02-T04 — Définir les règles de références inter-registres et cardinalités.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G02-T05 — Définir lifecycle, dépréciation et supersession sans suppression silencieuse.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G02-T06 — Définir la version du Governance Model indépendamment du Template.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G02-T07 — Définir invariants de validation: IDs uniques, références résolues, provenance, no orphan.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G02-T08 — Produire des exemples minimaux valides pour chaque type.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `GOVERNANCE_MODEL_METAMODEL`
- `ID_NAMESPACE_CONTRACT`
- `COMMON_METADATA_CONTRACT`
- `REFERENCE_AND_SUPERSESSION_RULES`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Les 18 types disposent d'un contrat de structure.
- Les règles d'ID/version/provenance/supersession sont non ambiguës.
- Les références peuvent être validées mécaniquement.

### Conditions HOLD / BLOCKED

- Conflit de namespace non résolu.
- Règle commune incompatible avec une autorité historique sans décision.

### Réutilisé par

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

### Mission / objectif

Obtenir la liste exhaustive, normalisée, sourcée et non redondante des domaines du Governance Model.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G02 validated outputs`

### Où chercher

- `sorties G01/G02`
- `.governance/control-plane-state/canonical-architecture.json`
- `docs/control-plane/*`
- `.governance/*policy*.json`
- `scripts/*.py`
- `schemas/*.json`
- `.github/workflows/*`
- `.governance/control-plane-db/catalog.json`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G03-T01 — Recenser les domaines explicitement documentés.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T02 — Découvrir les domaines implicites dans policies/schemas/scripts/workflows.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T03 — Découvrir les domaines révélés par SQL, runtime objects et tests.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T04 — Fusionner les candidats en conservant toutes les provenances.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T05 — Normaliser synonymes, chevauchements et granularités.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T06 — Définir purpose, scope, exclusions et responsabilité de chaque domaine.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T07 — Attribuer statut IMPLEMENTED/PARTIAL/PLANNED/FUTURE.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T08 — Associer les capabilities candidates sans les finaliser.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G03-T09 — Contrôler qu'aucun élément majeur du modèle reste hors domaine sans justification.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `DOMAIN_REGISTRY_DATASET`
- `DOMAIN_CANDIDATE_LEDGER`
- `DOMAIN_COVERAGE_REPORT`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Chaque domaine a ID, purpose, scope, statut et provenance.
- Synonymes/chevauchements sont résolus ou HOLD.
- Tous les éléments majeurs sont couverts.

### Conditions HOLD / BLOCKED

- Domaine candidat sans preuve suffisante.
- Deux domaines incompatibles recouvrent la même responsabilité.

### Réutilisé par

- `GMC-G04`
- `GMC-G12`
- `GMC-G13`
- `GMC-G14`

---

## GMC-G04 — CAPABILITY REGISTRY

**Legacy reference:** `GMC-04`  
**Phase:** `GMC-B`  
**Status:** `PLANNED / PLANNING_ONLY`

### Mission / objectif

Construire le catalogue exhaustif des capabilities, rattachées aux domaines et décrites par leurs contrats fonctionnels, statut et applicabilité.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G03 validated outputs`

### Où chercher

- `DOMAIN_REGISTRY_DATASET`
- `.governance/control-plane-state/canonical-architecture.json`
- `docs/control-plane/TASKS.md`
- `.governance/control-plane-db/catalog.json`
- `scripts/*.py`
- `scripts/test_*.py`
- `.github/workflows/*`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G04-T01 — Importer les capabilities déclarées comme candidats.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T02 — Découvrir les capabilities implicites à partir des comportements et tests.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T03 — Dédupliquer par résultat fonctionnel et non par fichier.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T04 — Définir purpose, inputs, outputs, préconditions, postconditions et erreurs.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T05 — Définir statut et applicabilité MANDATORY/OPTIONAL/CONDITIONAL/NOT_APPLICABLE.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T06 — Rattacher chaque capability à son domaine.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T07 — Identifier dépendances préliminaires entre capabilities.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T08 — Associer composants/implémentations/tests candidats.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G04-T09 — Produire la revue de couverture et capabilities orphelines/non prouvées.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `CAPABILITY_REGISTRY_DATASET`
- `CAPABILITY_COVERAGE_REPORT`
- `CAPABILITY_APPLICABILITY_CANDIDATES`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Chaque capability a ID, domaine, contrat, statut, applicabilité et provenance.
- Aucune capability architecturale n'est acceptée sans preuve ou statut PLANNED.

### Conditions HOLD / BLOCKED

- Capability supposée sans source.
- Conflit entre définition et comportement réel.

### Réutilisé par

- `GMC-G05`
- `GMC-G13`
- `GMC-G14`
- `GMC-G18`

---

## GMC-G05 — COMPONENT REGISTRY

**Legacy reference:** `GMC-05`  
**Phase:** `GMC-B`  
**Status:** `PLANNED / PLANNING_ONLY`

### Mission / objectif

Décomposer les capabilities en composants fonctionnels réutilisables en séparant strictement concept et artefact d'implémentation.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G04 validated outputs`

### Où chercher

- `CAPABILITY_REGISTRY_DATASET`
- `scripts/*.py`
- `.governance/*policy*.json`
- `schemas/*.json`
- `.github/workflows/*`
- `.governance/control-plane-state/*.json`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G05-T01 — Décomposer chaque capability en responsabilités fonctionnelles minimales.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G05-T02 — Inspecter les artefacts actuels pour identifier les composants implicitement réalisés.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G05-T03 — Séparer COMPONENT et IMPLEMENTATION_ARTIFACT.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G05-T04 — Définir responsabilité, interfaces et contrats.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G05-T05 — Identifier composants partagés entre capabilities.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G05-T06 — Détecter doublons, chevauchements et composants manquants.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G05-T07 — Associer objets, contrôles, implémentations et tests candidats.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G05-T08 — Vérifier que chaque capability possède une décomposition ou un gap explicite.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `COMPONENT_REGISTRY_DATASET`
- `CAPABILITY_COMPONENT_MAP`
- `COMPONENT_GAP_REPORT`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Aucun composant n'est défini comme un simple chemin de fichier.
- Toutes les capabilities ont une décomposition ou un gap explicite.

### Conditions HOLD / BLOCKED

- Responsabilités impossibles à séparer à cause d'un couplage non documenté.
- Capability sans composant identifiable et sans gap accepté.

### Réutilisé par

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

### Mission / objectif

Construire le modèle de données conceptuel: objets, champs, types, cardinalités, contraintes, relations, mutabilité et autorité.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G05 validated outputs`

### Où chercher

- `COMPONENT_REGISTRY_DATASET`
- `schemas/*.json`
- `.governance/control-plane-state/*.json`
- `.governance/control-plane-db/001_schema.sql`
- `.governance/control-plane-db/002_agent_activity.sql`
- `.governance/control-plane-db/003_canonical_authorities.sql`
- `.governance/control-plane-db/runtime-seed.json`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G06-T01 — Inventorier les objets à partir des schemas, JSON et tables SQL.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T02 — Normaliser les objets équivalents représentés sous plusieurs formes.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T03 — Extraire champs, types, required/optional, valeurs permises et defaults.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T04 — Définir mutabilité, ownership/authority et nature canonical/derived/runtime.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T05 — Extraire les relations explicites et implicites.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T06 — Définir cardinalités et contraintes d'intégrité.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T07 — Conserver provenance précise vers schema/table/path/symbole.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T08 — Associer chaque objet aux composants/capabilities.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G06-T09 — Contrôler objets/champs/relations orphelins et divergences schema-code-SQL.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `OBJECT_REGISTRY_DATASET`
- `FIELD_REGISTRY_DATASET`
- `RELATIONSHIP_REGISTRY_DATASET`
- `OBJECT_MODEL_CONSISTENCY_REPORT`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Chaque objet/champ/relation a ID, définition, provenance et ownership.
- Cardinalités et contraintes connues sont explicites.
- Divergences schema-code-SQL sont résolues ou HOLD.

### Conditions HOLD / BLOCKED

- Deux autorités définissent différemment un même champ critique.
- Relation nécessaire mais cardinalité/ownership indéterminable.

### Réutilisé par

- `GMC-G07`
- `GMC-G08`
- `GMC-G13`
- `GMC-G15`

---

## GMC-G07 — STATE REGISTRY / STATE MACHINES

**Legacy reference:** `GMC-07`  
**Phase:** `GMC-C`  
**Status:** `PLANNED / PLANNING_ONLY`

### Mission / objectif

Identifier tous les objets stateful et normaliser leurs états avec sémantique, catégorie et preuve requise.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G06 validated outputs`

### Où chercher

- `OBJECT/FIELD datasets`
- `schemas/*.json`
- `.governance/control-plane-state/*.json`
- `.governance/work/*.json`
- `.governance/sessions/*.json`
- `.governance/control-plane-db/catalog.json`
- `.governance/control-plane-db/runtime-seed.json`
- `scripts/*.py`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G07-T01 — Identifier tous les objets possédant state/status/mode/phase.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G07-T02 — Extraire les valeurs déclarées par schemas et JSON.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G07-T03 — Extraire les états implicites dans branches conditionnelles et tests.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G07-T04 — Normaliser synonymes et distinguer état d'objet, phase et résultat de contrôle.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G07-T05 — Classer initial/intermediate/terminal/error/hold/unknown.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G07-T06 — Définir la sémantique exacte de chaque état.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G07-T07 — Définir evidence requirements/freshness pour déclarer l'état.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G07-T08 — Vérifier rattachement de chaque état à un objet et une machine cohérente.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `STATE_REGISTRY_DATASET`
- `STATE_MACHINE_CATALOGUE`
- `STATE_SEMANTICS_REPORT`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Tous les états observés sont normalisés ou conflict/obsolete.
- Chaque état possède objet, sémantique, catégorie et provenance.

### Conditions HOLD / BLOCKED

- Même nom d'état avec sémantiques incompatibles.
- État critique utilisé par le code sans autorité vérifiable.

### Réutilisé par

- `GMC-G08`
- `GMC-G10`
- `GMC-G11`
- `GMC-G15`

---

## GMC-G08 — TRANSITION REGISTRY

**Legacy reference:** `GMC-08`  
**Phase:** `GMC-C`  
**Status:** `PLANNED / PLANNING_ONLY`

### Mission / objectif

Formaliser toutes les transitions autorisées/interdites avec déclencheur, acteur, autorité, pré/postconditions, contrôles, preuve, échec et récupération.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G07 validated outputs`

### Où chercher

- `STATE_MACHINE_CATALOGUE`
- `scripts/*.py`
- `.github/workflows/*`
- `.governance/control-plane-db/catalog.json`
- `docs/control-plane/TASKS.md`
- `docs/control-plane/NEXT_ACTION.md`
- `docs/control-plane/CASE1_REPLAY_LEDGER.md`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G08-T01 — Recenser transitions explicites et codées.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T02 — Relier chaque transition à FROM/TO state IDs.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T03 — Définir trigger, actor/role et authority requirements.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T04 — Définir préconditions, action et postconditions.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T05 — Associer controls, gates et evidence types requis.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T06 — Définir failure state et recovery/reconciliation.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T07 — Cataloguer transitions interdites et fail-closed.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G08-T08 — Comparer documentation/code/tests et produire les gaps.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `TRANSITION_REGISTRY_DATASET`
- `FORBIDDEN_TRANSITION_CATALOGUE`
- `TRANSITION_GAP_REPORT`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Chaque transition a FROM/TO, trigger, authority, pre/postconditions et preuve.
- Transitions interdites explicites.
- Transitions critiques ont test ou gap enregistré.

### Conditions HOLD / BLOCKED

- Transition observée sans état source/cible déterminable.
- Désaccord non résolu entre code et autorité.

### Réutilisé par

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

### Mission / objectif

Construire le registre exhaustif des contrôles avec PASS/FAIL, portée, sévérité, comportement d'échec, preuve, implémentation et tests.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G08 validated outputs`

### Où chercher

- `docs/control-plane/*`
- `.governance/*policy*.json`
- `scripts/governance_agent.py`
- `scripts/*.py`
- `.github/workflows/*`
- `scripts/test_*.py`
- `docs/control-plane/DECISIONS_LOG.md`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G09-T01 — Extraire les contrôles explicites des autorités et décisions.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T02 — Extraire les contrôles des policies JSON et schemas.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T03 — Extraire les guards/validations du code.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T04 — Extraire les contrôles de Governance CI.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T05 — Relier les tests existants aux contrôles.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T06 — Dédupliquer et normaliser avec IDs stables.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T07 — Définir purpose, scope, severity, trigger, PASS, FAIL et failure behavior.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T08 — Associer evidence types, implementation IDs et test IDs candidats.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G09-T09 — Produire le rapport documented-only/implemented-only/untested/conflicting.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `CONTROL_REGISTRY_DATASET`
- `CONTROL_IMPLEMENTATION_TEST_MATRIX`
- `CONTROL_GAP_REPORT`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Chaque contrôle possède un contrat PASS/FAIL explicite.
- Chaque contrôle critique a provenance et comportement d'échec.
- Doublons normalisés sans perte de provenance.

### Conditions HOLD / BLOCKED

- Règle normative sans condition vérifiable.
- Contrôle critique code/autorité en conflit.

### Réutilisé par

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

### Mission / objectif

Formaliser les gates qui combinent les contrôles et déterminent ALLOW/STOP/HOLD pour les actions critiques.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G09 validated outputs`

### Où chercher

- `CONTROL_REGISTRY_DATASET`
- `TRANSITION_REGISTRY_DATASET`
- `bootstrap/entry/upgrade/adoption flows`
- `.github/workflows/*`
- `docs/control-plane/PROGRAM.md`
- `docs/control-plane/TASKS.md`
- `.governance/*policy*.json`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G10-T01 — Identifier les points de décision critiques.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T02 — Associer à chaque gate les control IDs requis.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T03 — Définir logique d'agrégation et ALLOW/STOP/HOLD.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T04 — Définir acteur/authority et approbations éventuelles.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T05 — Définir evidence requirements et freshness.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T06 — Définir failure/hold/recovery behavior.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T07 — Définir dépendances et ordre entre gates.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G10-T08 — Vérifier que les gates réutilisent les contrôles sans les redéfinir.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `GATE_REGISTRY_DATASET`
- `GATE_CONTROL_MATRIX`
- `GATE_SEQUENCE_MAP`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Tous les gates critiques ont une décision déterministe.
- Chaque gate référence des controls existants.
- Conditions HOLD/recovery explicites.

### Conditions HOLD / BLOCKED

- Gate dépend d'un contrôle non défini.
- Deux gates contradictoires gouvernent le même point.

### Réutilisé par

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

### Mission / objectif

Définir les types de preuves acceptables, formats, producteurs, sujets, fraîcheur, invalidation et liens aux controls/transitions/gates.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G10 validated outputs`

### Où chercher

- `.governance/control-plane-db/runtime-seed.json`
- `.governance/control-plane-db/001_schema.sql`
- `CI runs/commit SHAs/PRs/checkpoints/handoffs`
- `CONTROL/GATE/TRANSITION datasets`
- `docs/control-plane/DECISIONS_LOG.md`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G11-T01 — Inventorier les preuves concrètes déjà enregistrées.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T02 — Abstraire les evidence types réutilisables.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T03 — Définir format/schema de chaque evidence type.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T04 — Définir producer, subject, authority et freshness.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T05 — Définir invalidation/expiration.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T06 — Définir provenance et retention/replay.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T07 — Relier evidence types aux controls/transitions/gates.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T08 — Vérifier séparation Evidence Type vs Evidence Record.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G11-T09 — Produire la couverture et les gaps de preuve.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `EVIDENCE_TYPE_REGISTRY_DATASET`
- `EVIDENCE_REQUIREMENT_MATRIX`
- `EVIDENCE_GAP_REPORT`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Aucun evidence type ne contient une valeur spécifique à un run.
- Chaque control/gate critique connaît ses types de preuve.
- Freshness/invalidation explicite pour les preuves sensibles.

### Conditions HOLD / BLOCKED

- Preuve critique impossible à valider mécaniquement.
- Autorité de preuve indéterminée.

### Réutilisé par

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

### Mission / objectif

Relier bidirectionnellement chaque élément abstrait du modèle aux artefacts qui l'implémentent aujourd'hui et détecter artefacts orphelins ou éléments non implémentés.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G11 validated outputs`

### Où chercher

- `sorties G03-G11`
- `.governance/TEMPLATE_MANIFEST.json`
- `scripts/*.py`
- `schemas/*.json`
- `.github/workflows/*`
- `.governance/*.json`
- `.governance/control-plane-db/*`
- `tests/self-tests`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G12-T01 — Inventorier les artefacts d'implémentation.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T02 — Associer chaque élément modèle à ses artefacts actuels.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T03 — Enregistrer les relations many-to-many model↔artifact.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T04 — Définir type d'artefact, portée source/client, statut et version.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T05 — Relier chaque implémentation à ses tests/evidence producers.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T06 — Identifier artefacts orphelins.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T07 — Identifier éléments modèle sans implémentation et classer PLANNED/FUTURE/GAP.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T08 — Vérifier boundary source-only/distributed.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G12-T09 — Produire la matrice bidirectionnelle MODEL↔IMPLEMENTATION.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `IMPLEMENTATION_REGISTRY_DATASET`
- `MODEL_IMPLEMENTATION_MATRIX`
- `ORPHAN_ARTIFACT_REPORT`
- `UNIMPLEMENTED_MODEL_REPORT`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Chaque élément implémenté a une provenance d'artefact.
- Chaque artefact gouvernance a un rôle ou justification.
- Éléments non implémentés sont explicitement classés.

### Conditions HOLD / BLOCKED

- Artefact critique à responsabilité ambiguë.
- Implémentation observable contredit le modèle.

### Réutilisé par

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

### Mission / objectif

Construire le graphe complet des dépendances afin de calculer ordres de chargement, installation, vérification, réparation et intégration.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G12 validated outputs`

### Où chercher

- `phase_dependencies/task depends_on`
- `capability/component/object maps`
- `transitions/controls/gates`
- `scripts/config references`
- `SQL foreign keys`
- `case workflows`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G13-T01 — Collecter les dépendances explicites.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T02 — Ajouter les dépendances fonctionnelles entre model elements.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T03 — Classer HARD/CONDITIONAL/ORDERING/DATA/CONTROL/EVIDENCE/IMPLEMENTATION.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T04 — Construire le graphe orienté avec provenance par edge.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T05 — Détecter cycles et dépendances manquantes.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T06 — Calculer ordres topologiques load/install/validate/repair.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T07 — Identifier critical path et dépendances à fort impact.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T08 — Valider le graphe contre CREATE/ADOPT/MAP/LAB.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G13-T09 — Définir comportements en cas de cycle/unknown.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `DEPENDENCY_REGISTRY_DATASET`
- `GLOBAL_DEPENDENCY_GRAPH`
- `INSTALL_ORDER`
- `VALIDATION_ORDER`
- `REPAIR_ORDER`
- `DEPENDENCY_GAP_REPORT`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Toutes les dépendances ont source/type/direction.
- Cycles résolus ou HOLD.
- Ordres nécessaires calculables déterministiquement.

### Conditions HOLD / BLOCKED

- Cycle critique non résolu.
- Dépendance nécessaire sans cible stable.

### Réutilisé par

- `GMC-G14`
- `GMC-G16`
- `GMC-G17`
- `GMC-G18`

---

## GMC-G14 — SEMANTIC COMPARISON CONTRACT

**Legacy reference:** `GMC-14`  
**Phase:** `GMC-E`  
**Status:** `PLANNED / PLANNING_ONLY`

### Mission / objectif

Définir le contrat sémantique modèle↔repository qui classe un élément sans dépendre des noms de fichiers.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G13 validated outputs`

### Où chercher

- `datasets G03-G13`
- `ADOPT_EXISTING_REPOSITORY parcours/tests`
- `MAP_EXISTING_PROJECT parcours`
- `existing adoption self-test`
- `CP-ARCH-001 invariant semantic comparison`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G14-T01 — Définir le modèle d'observation d'un target repository.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T02 — Définir les clés de matching sémantique par type.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T03 — Formaliser les huit classifications et conditions.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T04 — Formaliser les actions REUSE/MAP_REUSE/EXTEND/ADD/HOLD/MIGRATE/DISCOVER/SKIP.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T05 — Définir résolution quand plusieurs classifications candidates existent.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T06 — Définir traitement UNKNOWN et recherches supplémentaires.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T07 — Définir interaction applicability/dependencies.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T08 — Définir le schéma ComparisonResult.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G14-T09 — Construire des cas d'exemple CREATE/ADOPT/MAP.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `COMPARISON_CONTRACT_SPEC`
- `COMPARISON_CLASSIFICATION_RULES`
- `COMPARISON_RESULT_MODEL`
- `ACTION_MAPPING`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Chaque classification a des critères déterministes.
- Matching jamais filename-only.
- UNKNOWN/CONFLICT conduisent à découverte/revue, jamais à une invention.

### Conditions HOLD / BLOCKED

- Deux classifications restent possibles avec la même preuve.
- Action risquerait d'écraser une implémentation mal comprise.

### Réutilisé par

- `GMC-G15`
- `GMC-G16`
- `GMC-G18`

---

## GMC-G15 — FIELD-LEVEL / FINE-GRAINED COMPARISON

**Legacy reference:** `GMC-15`  
**Phase:** `GMC-E`  
**Status:** `PLANNED / PLANNING_ONLY`

### Mission / objectif

Étendre la comparaison aux objets, champs, types, cardinalités, contraintes, lifecycle, authority, controls et tests.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G14 validated outputs`

### Où chercher

- `OBJECT/FIELD/RELATIONSHIP datasets`
- `STATE/TRANSITION datasets`
- `CONTROL/TEST/IMPLEMENTATION maps`
- `schemas/*.json`
- `SQL schema`
- `examples de repositories cibles`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G15-T01 — Définir matching exact, alias et équivalence sémantique des champs.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T02 — Définir matrice de compatibilité des types.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T03 — Définir règles enum exact/subset/superset/conflict.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T04 — Définir règles required/optional/default/nullability.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T05 — Définir règles cardinalité/relation compatibility.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T06 — Comparer contraintes, mutabilité, lifecycle et authority.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T07 — Définir comparaison control coverage et test coverage.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T08 — Définir remontée des différences fines vers PARTIAL/CONFLICT.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G15-T09 — Produire des exemples de comparaison fine avec classification attendue.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `FIELD_COMPARISON_RULES`
- `TYPE_COMPATIBILITY_MATRIX`
- `CONSTRAINT_COMPARISON_RULES`
- `FINE_GRAINED_GAP_MODEL`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Différences structurelles importantes remontent déterministiquement.
- Équivalences fonctionnelles reconnues malgré noms différents.
- Conflit d'autorité/contrainte critique ne peut pas être EQUIVALENT.

### Conditions HOLD / BLOCKED

- Compatibilité exige une interprétation métier indisponible.
- Alias supposé sans preuve.

### Réutilisé par

- `GMC-G16`
- `GMC-G18`
- `GMC-G19`

---

## GMC-G16 — CANONICAL REGISTRY MATERIALIZATION DESIGN

**Legacy reference:** `GMC-16`  
**Phase:** `GMC-F`  
**Status:** `PLANNED / PLANNING_ONLY`

### Mission / objectif

Transformer tous les datasets validés en conception complète de la représentation machine-readable, schemas, contrats, versioning et projection relationnelle existante, sans créer un second système.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G15 validated outputs`

### Où chercher

- `tous datasets G01-G15`
- `docs/control-plane/DATA_MODEL.md`
- `.governance/control-plane-db/001_schema.sql`
- `.governance/control-plane-db/002_agent_activity.sql`
- `.governance/control-plane-db/003_canonical_authorities.sql`
- `.governance/control-plane-db/catalog.json`
- `.governance/control-plane-db/runtime-seed.json`
- `.governance/control-plane-db/materialize.py`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G16-T01 — Définir l'arborescence cible .governance/governance-model.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T02 — Définir docs/governance-model et règles docs générées vs autorités manuelles.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T03 — Définir schemas/governance-model pour chaque registre et ComparisonResult.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T04 — Définir format de chaque registry JSON et références inter-registres.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T05 — Définir manifest model_id/model_version/status/registry pointers/contracts/releases.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T06 — Définir le plan de migration SQL additive governance_*.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T07 — Définir l'extension du materializer EXISTANT sans second materializer canonique.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T08 — Définir versioning modèle, release manifest, provenance et supersession.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T09 — Définir validations CI: schemas, IDs, refs, deps, model↔SQL parity, docs generation.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G16-T10 — Produire le plan d'implémentation ordonné, sans l'exécuter.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `REGISTRY_STORAGE_ARCHITECTURE`
- `SCHEMA_PLAN`
- `SQL_MIGRATION_PLAN`
- `MATERIALIZER_EXTENSION_PLAN`
- `MODEL_VERSIONING_PLAN`
- `CI_VALIDATION_PLAN`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Structure cible complètement spécifiée.
- Aucune duplication DB/materializer/source of truth.
- Tous datasets G03-G15 ont un emplacement prévu.

### Conditions HOLD / BLOCKED

- Conception crée une source canonique concurrente.
- Un registre n'a pas de schema ou projection prévue.

### Réutilisé par

- `GMC-G17`
- `GMC-G18`
- `future implementation`

---

## GMC-G17 — CONTROL PLANE CONSUMPTION DESIGN

**Legacy reference:** `GMC-17`  
**Phase:** `GMC-F`  
**Status:** `PLANNED / PLANNING_ONLY`

### Mission / objectif

Définir comment le Control Plane chargera, validera, versionnera et utilisera le Governance Model au cœur de ses décisions.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G16 validated outputs`

### Où chercher

- `REGISTRY_STORAGE_ARCHITECTURE`
- `scripts/governance_agent.py`
- `control-plane policies`
- `catalog.json`
- `runtime-seed.json`
- `session/work/checkpoint/handoff flows`
- `Governance CI`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G17-T01 — Identifier les entry points du Control Plane qui ont besoin du modèle.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T02 — Définir séquence load manifest → resolve version → load registries → validate.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T03 — Définir dependency/applicability resolution contract.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T04 — Définir fail-closed si manifest/schema/ref/dependency invalide.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T05 — Définir liaison model_version avec runs/sessions/evidence/comparisons.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T06 — Définir interfaces modèle ↔ catalogue de parcours existant.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T07 — Définir observabilité/evidence du chargement/validation.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T08 — Définir backward compatibility avec CASE 1 et clients existants.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G17-T09 — Définir matrice de tests nécessaire avant activation.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `CONTROL_PLANE_MODEL_CONSUMPTION_CONTRACT`
- `MODEL_LOAD_SEQUENCE`
- `FAIL_CLOSED_RULES`
- `BACKWARD_COMPATIBILITY_PLAN`
- `CONTROL_PLANE_TEST_MATRIX`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Control Plane dépend du modèle et non de fichiers ad hoc.
- Version du modèle utilisée par un run traçable.
- Non-régression des flux actuels prévue.

### Conditions HOLD / BLOCKED

- Nouveau loader contourne les autorités actuelles.
- Migration exige rupture non acceptée.

### Réutilisé par

- `GMC-G18`
- `GMC-G19`
- `future implementation`

---

## GMC-G18 — FOUR-CASE REBIND DESIGN

**Legacy reference:** `GMC-18`  
**Phase:** `GMC-F`  
**Status:** `PLANNED / PLANNING_ONLY`

### Mission / objectif

Définir comment CREATE, ADOPT, MAP et LAB consommeront le même Governance Model avec seulement des stratégies d'application différentes.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G17 validated outputs`

### Où chercher

- `CONTROL_PLANE_MODEL_CONSUMPTION_CONTRACT`
- `.governance/control-plane-db/catalog.json`
- `CASE1 replay/program`
- `adoption tests/docs`
- `project mapping docs`
- `LAB evolution docs`
- `comparison/applicability/dependency contracts`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G18-T01 — Construire le Common Case Adapter Contract.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T02 — Mapper CREATE: applicability → dependency order → instantiate → validate → attest.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T03 — Mapper ADOPT: observe → compare → gaps/conflicts → additive integration plan → verify.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T04 — Mapper MAP: observe → map → compare → gaps → evidence, avec NO WRITE.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T05 — Mapper LAB: baseline model → candidate → model-to-model compare → regression → release.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T06 — Définir outputs communs et spécifiques.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T07 — Définir write/authority/gate policies par stratégie.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T08 — Définir matrice de regression sur un même model_version.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T09 — Définir migration du catalog.json vers consommation du modèle sans perdre l'historique.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G18-T10 — Vérifier qu'aucun élément central n'est redéfini en doublon dans un cas.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `FOUR_CASE_CONSUMPTION_MAP`
- `COMMON_CASE_ADAPTER_CONTRACT`
- `CREATE_MODEL_BINDING`
- `ADOPT_MODEL_BINDING`
- `MAP_MODEL_BINDING`
- `LAB_MODEL_BINDING`
- `CROSS_CASE_REGRESSION_MATRIX`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Les quatre cas référencent les mêmes IDs modèle.
- Chaque divergence est une stratégie, pas une redéfinition.
- MAP read-only; ADOPT additive; CREATE/LAB partagent les mêmes registries.

### Conditions HOLD / BLOCKED

- Un cas exige une redéfinition incompatible.
- Une stratégie ne peut respecter les controls/gates communs.

### Réutilisé par

- `GMC-G19`
- `future case implementation/validation`

---

## GMC-G19 — GLOBAL VALIDATION / FIRST GOVERNANCE MODEL RELEASE

**Legacy reference:** `GMC-19`  
**Phase:** `GMC-G`  
**Status:** `PLANNED / PLANNING_ONLY`

### Mission / objectif

Assembler et valider tous les résultats, prouver cohérence/traçabilité/réutilisation cross-case et préparer la première release complète du Governance Model.

### Questions à résoudre

- Quelles connaissances sont explicitement autoritatives pour cet objectif ?
- Quelles connaissances ne sont qu'implicites dans code/tests/runtime ?
- Quels conflits, doublons, inconnus ou éléments obsolètes doivent être conservés comme tels ?
- Quel résultat versionné doit être produit pour débloquer les groupes aval ?

### Entrées / prérequis

- `GMC-G18 validated outputs`

### Où chercher

- `toutes sorties G01-G18`
- `CP-ARCH-001`
- `CP-GOVMODEL-001`
- `Governance CI/test matrix`
- `case E2E evidence`
- `implementation/test/dependency maps`
- `comparison examples/results`
- `canonical authority revisioning`

### Recherches ciblées

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

### Tâches atomiques

#### GMC-G19-T01 — Exécuter completeness review de tous les registries/contracts prévus.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T02 — Exécuter consistency review IDs/refs/dependencies/lifecycle/applicability.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T03 — Vérifier traçabilité source↔model↔implementation↔test/evidence.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T04 — Valider matrice cross-case CREATE/ADOPT/MAP/LAB.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T05 — Définir/valider model-to-model release diff et compatibilité.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T06 — Classer tous les gaps en BLOCKER/POST-1.0/FUTURE.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T07 — Préparer release manifest Governance Model 1.0.0 et mapping Template versions.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T08 — Définir attestation/evidence bundle/checkpoint/handoff/release gate.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T09 — N'autoriser 1.0.0 que si tous exit gates critiques PASS.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

#### GMC-G19-T10 — Préparer handoff PostgreSQL/API/Admin UI après stabilisation.

- **Method:** Observe → extract → preserve provenance → classify → reconcile across sources → record conflicts/unknowns → produce structured result.
- **Evidence:** source/path/ref, HEAD/version lorsque pertinent, justification de classification.
- **DONE:** Scope complete, provenance complete, conflicts explicit, no silent inference, output usable by next atomic task or group exit gate.
- **HOLD:** Critical contradiction, missing authority/provenance, or ambiguity that could create false canonical knowledge.

### Résultats / livrables attendus

- `GOVERNANCE_MODEL_COMPLETENESS_REPORT`
- `TRACEABILITY_MATRIX`
- `CROSS_CASE_VALIDATION_REPORT`
- `RELEASE_READINESS_REPORT`
- `GOVERNANCE_MODEL_1_0_0_RELEASE_PLAN`

### Destination canonique prévue

PLANNED Governance Model Registry / contracts / source-only authority as applicable; no target file is created by this planning task.

### Exit gate

- Aucun blocker critique ouvert.
- Traçabilité complète pour éléments critiques.
- Quatre cas consomment le même modèle avec evidence cross-case.
- Release gate 1.0.0 explicitement PASS.

### Conditions HOLD / BLOCKED

- Gap critique non résolu.
- Régression cross-case.
- Référence/contrôle/transition critique non testable ou non prouvée.

### Réutilisé par

- `future PostgreSQL projection`
- `Governance API`
- `Admin UI`
- `subsequent Governance Model releases`

---

## 4. Definition of Ready for future implementation

- Les sorties amont nécessaires existent et sont validées.
- Le HEAD courant est réobservé.
- Les autorités applicables sont chargées.
- La tâche d'implémentation est explicitement autorisée par la gouvernance.
- Les dépendances/collisions sont vérifiées.
- Le plan de non-régression et les preuves attendues sont connus.

## 5. Non-goals

Ce blueprint ne crée ni ne peuple les futurs `.governance/governance-model/registries/*.json`, `schemas/governance-model/*`, migration SQL, comparator, applicability engine, model loader ou rebinding CREATE/ADOPT/MAP/LAB.
