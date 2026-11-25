# Diagnostic de reutilisation LAB — decision candidate, sans activation

Date : 2026-10-20. Depot : `chainsolutions-wealthtech/Governed-Repository-Template`. Continuite documentaire `GRT-CONT-AUDIT-STABILISATION-20261019-001`. PR #339 DRAFT.

**VERDICT CANDIDAT : REUSE_DESIGN_ONLY / HOLD_ACTIVATION.** Ceci n'est pas une decision proprietaire d'activer un LAB. Aucun nouvel objet runtime, branche, issue, PR, session, agent, pool ou claim n'est cree.

## Preuves source sur main

- PR #330 fusionnee : `docs/labs/GRT-CONT-20261017-LABENTRY-001/REGISTRY.json`, blob `fb63cb3efb93a2328883aabb240bb28ec6dc01c6`. Continuite `GRT-CONT-20261017-LABENTRY-001`, issue #329, PR #330, branche `lab/lab-entry-minimum-20261017`. `state=SOURCE_BOOTSTRAP_MERGED_MAIN`, `activation=MERGED_OWNER_WORKFLOW_AVAILABLE_NOT_YET_LIVE_E2E`, `sessions=[]`, `work_claims=[]`. Prochaine action historique : `LIVE_OWNER_LAB_WORKFLOW_DISPATCH_TEST_AND_CANONICAL_GACR_BINDING_VERIFICATION`.
- `POOL.json`, blob `ad9cc28f19ef42d45f57829639f32d76ff627a09` : quatre slots ARCH/PLAN/CODE/REVIEW, tous `VACANT`, aucune session/identite ; `membership=SLOTS_RESERVED_UNBOUND`, liaison GACR `REQUIRED_NOT_YET_ATTESTED`.
- `QUEUE.json`, blob `5693aea8fc849c0faee9e44133af15e5e96a2d15` : 11 propositions, `STAGED_NO_CANONICAL_DISPATCH`, `projection_only=true`, `may_issue_claims=false`.
- `00_LAB_ENTRY.md`, `.github/workflows/lab-entry.yml`, `scripts/lab_entry_bootstrap.py` et ses tests existent sur main. Le workflow standard cree une branche, une issue et une PR ; non autorise par le mandat de la PR #339.

## Matrice de decision

| Option | Avantage | Collision/risque | Verdict documentaire |
| --- | --- | --- | --- |
| Reutiliser le design et les schemas | Conservation de la gouvernance et des tests | Ne pas importer l'identite du LAB historique | **RECOMMANDE** |
| Reprendre l'identite/pool du LAB #330 | Aucun avantage prouve pour la mission | Usurpation de continuite et confusion GACR | **REFUSE** |
| Executer `lab-entry.yml` maintenant | Creation automatisee d'objets GitHub | Nouvelle branche/issue/PR contre mandat #339 | **HOLD** |
| Inventer `LAB.md`, `POOL.json`, `REGISTRY.json` actifs dans #339 | Apparence de LAB | Autorite parallele sans preuves | **REFUSE** |
| Conserver le contrat candidat et poursuivre la reconciliation | Aucun risque de runtime | LAB non operationnel jusqu'a arbitrage | **AUTORISE DOCUMENTAIRE** |

## Separation et anti-regression

- Le LAB historique #330 et la continuite d'audit #339 sont deux objets distincts. Ne pas rebaptiser `GRT-CONT-20261017-LABENTRY-001` ni `GRT-POOL-20261017-LABENTRY-001`.
- L'issue Genesis #285, la continuite #282 et CHAINFLOW #301/#334 ne sont pas des autorisations pour notre LAB.
- Les droits GitHub de Porte B n'impliquent ni admission GSCC/GACR/F1, ni permission de modifier le Control Plane, ni claim.
- Ne pas changer `main`, les workflows, la queue canonique, les sessions ou les identites ; ne pas fusionner PR #339.

## Decision restant au proprietaire

Confirmer si le LAB de reconstruction doit rester un programme documentaire dans PR #339 ou, dans un mandat ulterieur distinct, etre cree par le workflow LAB natif. Dans le second cas, preciser l'objectif, le perimetre, les protections, les objets GitHub autorises, les preuves et les gates de revue. Ne pas supposer cette autorisation.

## NEXT_ACTION

Verifier les checks CI du HEAD de PR #339 apres publication, puis preparer un checkpoint d'arbitrage avec preuves exactes et limites. Le LAB demeure `DOCUMENTARY_CANDIDATE / NOT_ACTIVATED`.
