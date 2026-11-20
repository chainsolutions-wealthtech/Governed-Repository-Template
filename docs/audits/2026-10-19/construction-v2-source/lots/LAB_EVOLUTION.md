# Lot / pièce : LAB_EVOLUTION — Cas 4 — laboratoire gouverné

> Dossier de planification, **non exécutable** ; référence source observée `638fcc51c77f2454990f239b8b8cca78bac8075b` le 2026-10-16.  
> Identité : **PROPOSED_PLANNING_REFERENCE** ; état source : **PLANNED** ; état du paquet : `DESIGN_ONLY_NO_EXECUTION`.  
> **Interdit de modifier P0 (GSCC/GSE/GACR/F1) ou `main` à partir de cette fiche.**

## Position canonique
- ID : `LAB_EVOLUTION`
- Type : `structuring_case`
- Parent : `CP-ARCH-001`
- Phase / chantier : `CASE`
- Dépendances à vérifier : `GMC-G18`
- Source autoritative : https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/638fcc51c77f2454990f239b8b8cca78bac8075b/docs/control-plane/MASTER_SYSTEM_MAP.md
- JSON pointer : `non applicable`
- Exigences candidates liées, **non validées** : À établir par matrice validée.

## Objectif et frontières
Observer HEAD → baseline → scope LAB → autorité → branche → travail isolé → CI → PR → review → fusion gouvernée → attestation.

## Instructions de réalisation lorsque le lot devient gouverné
1. Observer HEAD
2. baseline
3. scope LAB
4. autorité
5. branche
6. travail isolé
7. CI
8. PR
9. review
10. fusion gouvernée
11. attestation.

## Sorties vérifiables attendues
- `Case contract`
- `Run and evidence`
- `Case handoff`

## Contrat d'acceptation
La phase de conception ne vaut ni validation E2E ni droit de mutation.

## Vérifications
- ID source présent dans la source canonique ou déclaré DRAFT si nouveau
- Dépendances et parent résolus ou explicitement en attente
- Sorties identifiées par référence et version
- Critères de sortie appliqués par preuve et non par simple état DONE
- Aucune altération de GSCC/GSE/GACR/F1 ou du MAIN par le dossier de planification

## Pièces de preuve à rattacher
- `source_file`
- `source_ref`
- `source_head_at_observation`
- `decisions_and_approvals_when_applicable`
- `output_artifacts_or_explicit_gap`
- `validation_result`
- `checkpoint_ref`
- `handoff_ref`

## Conditions HOLD / arrêt
- Identité/rattachement ambigu
- Contradiction d’autorités
- Dépendance ou preuve indispensable manquante
- HEAD déplacé avant une future mutation
- Autorité d’exécution absente

## Registre d'état / historique / reprise
- État de ce paquet : `DESIGN_ONLY_NO_EXECUTION`.
- Le statut d'exécution réel doit être lu dans la source canonique **au moment de la reprise** ; il n'est pas dérivé de cette fiche.
- `logical_agent_id`, `session_id`, `claim_id`, `approval_ref`, `lease`, `execution_status` : **UNASSIGNED / NOT_OBSERVED** dans ce paquet.
- Aucun changement de statut opérationnel sans preuve, événement et gate autorisé.
- Après interruption : Recharger la source et l’état actuels par ID ; vérifier le HEAD et les preuves ; reprendre la première instruction non validée sans réémettre les actions déjà prouvées.
- Handoff minimal : `piece_id`, `canonical_source`, `observed_head`, `last_verified_action`, `evidence_refs`, `blockers`, `next_action`, `handoff_ref`.

## Frontière d'exécution
Ce plan n'attribue aucune capacité. L'agent entrant arrive par le **P0 actuel inchangé** ; seulement après validation de sa propre admission/autorité, il peut rechercher ce lot dans le registre, vérifier claim/dependencies/HEAD, puis demander/exécuter les actions dans son périmètre.
