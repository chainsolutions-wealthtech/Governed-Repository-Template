# Lot / pièce : CREATE_NEW_REPOSITORY — Cas 1 — création et bootstrap

> Dossier de planification, **non exécutable** ; référence source observée `638fcc51c77f2454990f239b8b8cca78bac8075b` le 2026-10-16.  
> Identité : **PROPOSED_PLANNING_REFERENCE** ; état source : **DONE** ; état du paquet : `DESIGN_ONLY_NO_EXECUTION`.  
> **Interdit de modifier P0 (GSCC/GSE/GACR/F1) ou `main` à partir de cette fiche.**

## Position canonique
- ID : `CREATE_NEW_REPOSITORY`
- Type : `structuring_case`
- Parent : `CP-ARCH-001`
- Phase / chantier : `CASE`
- Dépendances à vérifier : `P12-S6`
- Source autoritative : https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/638fcc51c77f2454990f239b8b8cca78bac8075b/docs/control-plane/MASTER_SYSTEM_MAP.md
- JSON pointer : `non applicable`
- Exigences candidates liées, **non validées** : À établir par matrice validée.

## Objectif et frontières
Owner → nom → visibilité → autorité → génération Template → bootstrap → premier agent local → baseline → handoff → normal entry.

## Instructions de réalisation lorsque le lot devient gouverné
1. Owner
2. nom
3. visibilité
4. autorité
5. génération Template
6. bootstrap
7. premier agent local
8. baseline
9. handoff
10. normal entry.

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
