# Lot / pièce : DRAFT-LOAD-CONTRACT — Contrat de prise en charge d’un lot par un agent admis

> Dossier de planification, **non exécutable** ; référence source observée `638fcc51c77f2454990f239b8b8cca78bac8075b` le 2026-10-16.  
> Identité : **DRAFT_LOCAL_ONLY_NOT_CANONICAL** ; état source : **PROPOSED_NOT_REGISTERED** ; état du paquet : `DESIGN_ONLY_NO_EXECUTION`.  
> **Interdit de modifier P0 (GSCC/GSE/GACR/F1) ou `main` à partir de cette fiche.**

## Position canonique
- ID : `DRAFT-LOAD-CONTRACT`
- Type : `proposed_missing_specification`
- Parent : `CP-ARCH-001`
- Phase / chantier : `GAP`
- Dépendances à vérifier : Aucune dépendance déclarée dans le registre source.
- Source autoritative : https://github.com/chainsolutions-wealthtech/Governed-Repository-Template/blob/638fcc51c77f2454990f239b8b8cca78bac8075b/docs/control-plane/REQUIREMENTS_ROADMAP.md
- JSON pointer : `non applicable`
- Exigences candidates liées, **non validées** : `RQ-28`

## Objectif et frontières
Recevoir et contrôler un lot par ID, récupérer sources, preuves, claim, mission et point de reprise sans rejouer P0.

## Instructions de réalisation lorsque le lot devient gouverné
1. Établir le périmètre et la raison de l’écart à partir des autorités existantes.
2. Rechercher d’abord un objet canonique équivalent et son namespace; ne pas créer une source parallèle.
3. Formuler le contrat en version candidate, avec sources, dépendances, règles de test et conditions de reprise.
4. Présenter pour arbitrage et rattachement gouverné dans la tâche canonique existante.
5. Ne pas attribuer de claim ni statut READY sur la base du document de planification.

## Sorties vérifiables attendues
- `Contrat de prise en charge d’un lot par un agent admis — contrat proposé`

## Contrat d'acceptation
Revue propriétaire, rattachement au backlog canonique existant, et éventuelle création d’identité par mécanisme gouverné ultérieur.

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
