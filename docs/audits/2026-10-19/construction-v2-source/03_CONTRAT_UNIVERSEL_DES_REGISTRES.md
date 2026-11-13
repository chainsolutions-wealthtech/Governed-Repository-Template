# Contrat générique de registre de construction — projet candidat

Chaque objet de travail est une **identité stable**, distincte de l'agent qui l'exécute et de la session qui observe son état.

## Champs minimums
`work_id, kind, title, canonical_source, source_head, parent_links[], requirement_links[], deliverable_links[], dependency_links[], allowed_states, current_source_status, claimed_by_agent_ref (si réellement observé), session_ref (si exposé), authority_ref, requested_capabilities[], gates[], evidence_refs[], decisions[], checkpoints[], handoff_ref, next_action, revisions[]`.

## Liens et cardinalités
- `PARENT_OF`: 1:n usuel mais pas suffisant pour la traçabilité totale.
- `DEPENDS_ON`: n:n avec type HARD/CONDITIONAL/ORDERING/EVIDENCE/ARTIFACT.
- `IMPLEMENTS_REQUIREMENT`: n:n, provenance vérifiable.
- `PRODUCES_ARTIFACT`: n:n, version + producteur + preuve.
- `SCHEDULED_IN_SPRINT`: n:n, sans effet automatique sur statut de livrable.
- `PERFORMED_BY_AGENT`: n:n par **événements d'intervention observés**, pas attribution présumée.
- `VERIFIED_BY`: n:n avec vérificateur réellement identifié.
- `DELIVERED_IN_RELEASE`: n:n, acceptation explicite distincte de l'état de sprint.

## États et transitions
`PROPOSED/DRAFT → PLANNED → READY → ASSIGNED → IN_PROGRESS → VERIFYING → VALIDATED → DONE` illustratif ; variantes `BLOCKED/HOLD/REJECTED/SUPERSEDED/CANCELLED`. Ne **jamais** substituer ces états à une machine déjà canonique : GMC-G07/G08/G16 doit normaliser et déclarer la traduction.

## Sources d’autorité
Cibles : `CP-ARCH-001`, `CP-GOVMODEL-001`, `docs/control-plane/TASKS.md`, mémoire versionnée, décisions, schémas SQL existants. Il est interdit de créer une deuxième base canonique, un deuxième materializer ou un deuxième mécanisme GSCC/GACR.

## Modèle de prise en charge
L'agent possède déjà un dossier P0 reconnu → acquiert l'autorité de tâche par processus existant → récupère les références du lot → vérifie la fraîcheur → prend son claim si autorisé → réalise → prouve → handoff. Un ID de planification ne vaut jamais admission ni claim.
