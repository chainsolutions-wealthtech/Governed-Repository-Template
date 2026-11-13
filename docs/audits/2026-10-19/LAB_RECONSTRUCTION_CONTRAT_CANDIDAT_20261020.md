# LAB de reconstruction GRT — contrat documentaire candidat

**Date :** 2026-10-20. **Depot exclusif :** `chainsolutions-wealthtech/Governed-Repository-Template`. **PR de travail :** #339, branche `audit/20261019-histoire-identites-stabilisation`. **Continuite parente existante :** `GRT-CONT-AUDIT-STABILISATION-20261019-001` (alias `GRT-AUDIT-STABILISATION`).

**STATUT : CANDIDAT_DOCUMENTAIRE — LAB NON CREE — NON ACTIVE — AUCUNE NOUVELLE IDENTITE OU AUTORITE.** Cette note n'est ni un `LAB.md` runtime, ni un `REGISTRY.json` canonique, ni un `POOL.json`, ni une `QUEUE.json` executable. Aucune reservation de slug, session, branche, issue, PR ou pool.

## Mandat et objectif

Preparer une experimentation isolee pour reconstruire, analyser, comparer et tester progressivement l'architecture, les registres et les comportements de `main`, sans le modifier. La memoire documentaire du HUB, la continuite d'audit et les autorites existantes restent distinctes. Le HUB ne devient pas un second `main`.

## Sources relues et mecanisme existant

- `00_DIRECT_OWNER_ENTRY.md` (Porte B), GitHub natif, sans creation GACR/F1 ; l'entree ne confere aucune autorite par le role.
- `00_LAB_ENTRY.md` (blob main `0448aa6562491dbb3cf0a0fb4a0c77f569cb00c0`) : mecanisme LAB gouverne, pas une nouvelle porte d'admission.
- `.github/workflows/lab-entry.yml` (blob main `85e2cb390574735ca1079fd41ea5bd1336f2e6fc`) : `workflow_dispatch` sur `main`, tests avant bootstrap, permissions contents/issues/PR/actions.
- `scripts/lab_entry_bootstrap.py` (blob main `79efa1782c9fe6997e4fe6ef3916d5c87c5e2f67`) : cree une issue, une branche `lab/<slug>`, une PR DRAFT, un registre, un pool et une queue de projection ; exige un evenement GitHub authentifie.
- `scripts/test_lab_entry_bootstrap.py` (blob main `36b776ab0d85fe835fe4d042b806a737f0387b1d`) : tests de refus d'identite/slug invalides, de doublons et de controles de non-promotion ; aucune execution de ces tests n'est revendiquee dans cette note.
- `docs/control-plane/NAMESPACE_WORK_REGISTRY.md` : source `CP-NAMESPACE-001`, aucune task list ou autorite parallele.

## Incompatibilite a resoudre avant creation

Le mandat courant de la PR #339 impose `NO_NEW_ISSUE`, `NO_NEW_PR`, `NO_MAIN_WRITE`, `DOCUMENTATION_ONLY`. Le bootstrap LAB standard cree precisement une issue, une branche et une PR et ne doit donc **pas** etre declenche dans cette mission. Ne pas contourner le bootstrap en simulant son succes ni en fabriquant ses fichiers runtime dans cette PR.

## Frontieres de gouvernance

1. Domaine A : admission et identites `GSCC → GSE → GACR`, sessions, claims, attestations, F1 ; aucune de ces autorites n'est derivee de cette note.
2. Domaine B : gouvernance du depot, programme GMC, Control Plane, GitHub, code, tests et PR ; aucune mutation de `main` ni du Control Plane.
3. Pont eventuel : liens typés, datés, preuves natives ; jamais equivalence automatique d'identite, de session, de permission ou de statut.
4. Les quatre slots standards ARCH/PLAN/CODE/REVIEW ne sont que des roles de modele ; aucun agent n'est affecte ici.
5. Le plan a 11 etapes du bootstrap standard n'est pas une nouvelle queue autoritative ; aucune execution, dispatch ou claim n'est autorise.

## Conditions minimales avant activation future

- Decision explicite du proprietaire sur le perimetre et sur l'eventuelle exception au mandat PR #339, ou nouvelle instruction distincte conforme aux autorites en vigueur.
- Relecture des registres LAB et continuities existants pour ecarter les collisions et reutiliser une identite deja creee si elle existe.
- Verification live de l'acteur GitHub, de ses permissions, du HEAD de `main`, des protections et du workflow cible.
- Accord sur le slug/objectif et sur l'isolation des experiences ; pas d'inference depuis `GRT-HUB-001` ou le nom de la mission.
- Tests fail-closed, CI, controles de non-regression, revue independante et checkpoints ; pas de promotion de ST01 ni de taches sans gate specifique.
- Si un LAB standard est finalement autorise, laisser le workflow existant creer ses vrais objets GitHub, puis consigner leurs identifiants et URLs natifs ; ne jamais les anticiper.

## Controle d'acceptation de ce contrat documentaire

**PASS documentaire seulement si** : publication sur la branche PR #339, fichier relu depuis GitHub, aucune autre branche/PR/issue creee, `main` non modifie par cette operation, aucun runtime modifie, aucune affirmation de creation LAB. **NON PROUVE** : activation LAB, admission GACR, recette multi-agent, execution des tests LAB ou CI du nouveau commit.

## NEXT_ACTION

Rechercher les LAB et continuities deja enregistres, examiner les collisions de noms et d'objets, puis preparer un arbitrage proprietaire sur le mode de creation. Conserver le present document comme contrat candidat dans la PR #339, sans promotion canonique implicite.
