# Inventaire de collision LAB — premiere passe documentaire

Date : 2026-10-20. Depot : `chainsolutions-wealthtech/Governed-Repository-Template`. Continuite : `GRT-CONT-AUDIT-STABILISATION-20261019-001`. PR #339. **READ-ONLY INVENTORY; NO LAB CREATED; NO RUNTIME CLAIM**.

## Sources GitHub observees

- Recherche de branches sur le depot, terme `lab`, premier resultat de 12 noms ; cette recherche ne constitue pas un inventaire de tous les objets LAB et ne prouve pas leur activation.
- Recherche de code `GRT-CONT-LAB` sur la branche par defaut : zero resultat dans cette recherche, **non** preuve d'absence de registre LAB.
- Recherche d'issues `LAB` : issue #285 `GENESIS LAB BUILDER`, avec continuite distincte `GRT-CONT-20261010-TEMOIN-POOLGEN-I282-01`, gouvernance en attente dans la demande ; aucun droit LAB cree par cette issue seule.
- `00_LAB_ENTRY.md`, `.github/workflows/lab-entry.yml`, `scripts/lab_entry_bootstrap.py`, `scripts/test_lab_entry_bootstrap.py` relus : le bootstrap normal cree branche, issue et PR DRAFT ; incompatible avec mandat documentaire unique de PR #339 sans nouvelle autorisation.

## Branches trouvees par recherche `lab`

- `lab/chainflow-gr302-reconcile-20261017`
- `lab/codeagent-gscc-f1-q12-renewal-284`
- `lab/direct-owner-entry-smoke-20261016`
- `lab/direct-owner-f1queue-20261016`
- `lab/f1-recovery-isolation-20261017`
- `lab/forge-gacr-supervision-validator-hotfix`
- `lab/forge-gacr-validator-order-hotfix`
- `lab/forge-gscc-alias-bind-hotfix-273`
- `lab/gacr-continuity-coordination-grt-cont-20261007`
- `lab/lab-entry-minimum-20261017`
- `lab/q12-same-arrival-renewal-284`
- `fix/post-f1-agent-choice-branch-lab-20261017`

**Interpretation :** les noms de branches ne sont ni des identites LAB canoniques, ni des preuves de sessions GACR, ni une permission de reutilisation. La derniere branche n'a pas le prefixe `lab/`.

## Risques de collision observes

| Domaine | Constat | Mesure anti-regression |
| --- | --- | --- |
| GENESIS | Issue #285 rattachee a une continuite historique distincte | Ne pas usurper le LAB Genesis ni son eventuel agent |
| CHAINFLOW | Branche `lab/chainflow-gr302-reconcile-20261017` | Ne pas reutiliser son slug ou son perimetre sans lire ses autorites |
| F1/GACR | Plusieurs branches de tests, isolation, correction | Ne pas assimiler branche a grant/session/claim |
| LAB bootstrap | Workflow standard cree issue/branche/PR | Ne pas executer dans le mandat PR #339 |
| GRT audit | Contrat LAB candidat deja dans PR #339 | Aucun slug ni identite LAB attribue ; documenter sans activation |

## Limites et prochaine action

Inventaire initial non exhaustif : lire les fichiers `docs/labs/*/REGISTRY.json` existants s'ils existent, les issues et PR pertinentes, les continuites GACR et les registres de gouvernance ; distinguer branche de test, LAB reel, proposition et LAB ferme. Comparer slug, owner, parent, scope, etats et preuves natives. Avant toute activation, exiger arbitrage proprietaire explicite sur la coexistence avec la PR #339.

**Invariants :** `DOCUMENTATION_ONLY / NO_NEW_BRANCH / NO_NEW_ISSUE / NO_NEW_PR / NO_MAIN_WRITE / NO_GACR_IMPERSONATION / NO_AUTO_MERGE`.
