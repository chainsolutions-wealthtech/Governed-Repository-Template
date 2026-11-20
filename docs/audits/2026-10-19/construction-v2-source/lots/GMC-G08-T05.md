# Lot / pièce : GMC-G08-T05 — Associer controls, gates et evidence types requis.

> Dossier de planification, **non exécutable** ; référence source observée `638fcc51c77f2454990f239b8b8cca78bac8075b` le 2026-10-16.  
> Identité : **EXISTING_CANONICAL_REFERENCE** ; état source : **PLANNED** ; état du paquet : `DESIGN_ONLY_NO_EXECUTION`.  
> **Interdit de modifier P0 (GSCC/GSE/GACR/F1) ou `main` à partir de cette fiche.**

## Position canonique
- ID : `GMC-G08-T05`
- Type : `atomic_task`
- Parent : `GMC-G08`
- Phase / chantier : `GMC-C`
- Dépendances à vérifier : `GMC-G08-T04`
- Source autoritative : https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/638fcc51c77f2454990f239b8b8cca78bac8075b/.governance/control-plane-state/governance-model-execution-blueprint.json
- JSON pointer : `/groups/7/atomic_tasks/4`
- Exigences candidates liées, **non validées** : À établir par matrice validée.

## Objectif et frontières
Accomplir exactement cette tâche du blueprint canonique; ne pas l’étendre à d’autres lots.

## Instructions de réalisation lorsque le lot devient gouverné
1. Réaliser uniquement: Associer controls, gates et evidence types requis.
2. Relever les documents, décisions, champs/symboles et preuves nécessaires depuis les sources canoniques du groupe.
3. Identifier les observations vérifiées, les lacunes et les contradictions sans les résoudre par supposition.
4. Produire le résultat intermédiaire référencé dans le blueprint et le relier aux artefacts du lot.
5. Appliquer les conditions de DONE/HOLD de la tâche et préparer la reprise par ID.

## Sorties vérifiables attendues
- `GMC-G08-T05-RESULT — résultat intermédiaire défini par le blueprint`

## Contrat d'acceptation
Provenance complète, résultat réutilisable, contradictions explicites et contrôle PASS.

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
