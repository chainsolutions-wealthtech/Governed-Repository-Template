# Chaîne de preuves vérifiable — aucune progression sans attestation

Chaque objet possède au moins `id, kind, parent_ref, authority_ref, source_ref, status_source, dependencies[], expected_outputs[], acceptance_controls[], evidence_refs[], history[], checkpoint_ref, next_action`.

## Un changement de statut est un événement gouverné

```text
EVENT(work_id, previous_status, proposed_status, actor_identity,
      agent_session, authority_snapshot, observed_head, claim_ref,
      evidence_ref[], decision_ref, control_results[], occurred_at)
→ VALIDATE_ID + VALIDATE_AUTHORITY + VALIDATE_DEPENDENCIES + VALIDATE_EVIDENCE
→ APPLY_CANONICAL_TRANSITION_IF_ALLOWED
→ APPEND_HISTORY + MATERIALIZE_PROJECTION
→ CHECKPOINT + HANDOFF
```

Ce flux est une **spécification cible** ; ne pas le confondre avec un moteur implémenté.

## Invariants de reconstruction

- Remonter `TASK → PARENT/GROUP → LIVRABLE → REQUIREMENT → PROGRAMME`, ou signaler la relation candidate non validée.
- Descendre `PROGRAMME → CAPABILITIES/DELIVERABLES → TASKS → ACTIONS → EVIDENCE` avec provenance.
- `SPRINT` peut contenir plusieurs tâches et une tâche peut apparaître dans plusieurs fenêtres de planification, sans modifier l'identité de la tâche.
- `CLAIM/AGENT/SESSION` sont des événements d'affectation et de travail ; pas des parents identitaires permanents de la tâche.
- Un conflit de version, un producteur inconnu, une validation absente ou un endpoint futur non identifié produisent `UNRESOLVED`/`HOLD`, jamais une preuve inventée.
- Tous les `DEL-DRAFT-*` et `DRAFT-CASE-*` nécessitent la résolution de leur identité avant toute affectation.

## Scénarios de recette indispensables

| ID local | Test cible | Preuve d'acceptation |
|---|---|---|
| `QA-DRAFT-01` | Charger une tâche par ID avec parent et sources | References et versions résolues |
| `QA-DRAFT-02` | Deux agents essaient claim conflictuel | Refus du claim concurrent ou équivalent gouverné |
| `QA-DRAFT-03` | Aucun F1/claim mutable | Refus d'écriture, aucune mutation |
| `QA-DRAFT-04` | Déconnexion au milieu d'une tâche | Handoff et reprise à la première étape non attestée |
| `QA-DRAFT-05` | HEAD déplacé avant commit | Revalidation ou HOLD, jamais écrasement silencieux |
| `QA-DRAFT-06` | Contrat sortant incomplet | Parent non validé malgré DONE enfant |
| `QA-DRAFT-07` | Sprint clos sans livrable terminé | Livrable reste OPEN/équivalent |
| `QA-DRAFT-08` | Source de relation orpheline | FAIL ou UNKNOWN explicite, pas de lien fictif |
| `QA-DRAFT-09` | Déploiement sans backup/rollback | STOP/HOLD |
| `QA-DRAFT-10` | Revenir de RELEASE à artefact et exigences | Traçabilité ascendante/descendante bidirectionnelle |

**Tous ces tests restent `NOT_EXECUTED_PLANNED` ; rien dans le présent paquet ne prétend un résultat PASS runtime.**
