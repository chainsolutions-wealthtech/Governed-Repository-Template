# Matrice de filiation LAB / GACR / GitHub — premiere passe

Date : 2026-10-20. Depot : `chainsolutions-wealthtech/Governed-Repository-Template`. PR #339, continuite `GRT-CONT-AUDIT-STABILISATION-20261019-001`. **Document de reconciliation ; aucune admission, activation ou autorite attribuee.**

## Autorite de source

Lecture de `main:.governance/control-plane-state/gacr-continuities.json` : blob `1a04c086dff0a764a735d4de7a7234508adf6c67`, revision 177, 5 entrees. Le fichier declare `DERIVED_GACR_COORDINATION_PROJECTION`, `projection_only=true` et aucune autorite de tache, claim ou mutation. Les quantites d'agents ci-dessous sont des references documentaires et non des sessions live.

| Continuite documentee | Issue coordination | Agents logiques references | Lien LAB verifie |
| --- | ---: | ---: | --- |
| `GRT-CONT-20261007-2117-GMC01-DSP258-01` | #259 | 3 | Non atteste |
| `GRT-CONT-20261010-TEMOIN-POOLGEN-I282-01` | #282 | 2 | LAB Genesis propose via #285 ; activation non attestee |
| `GRT-CONT-20261012-PROGRAMME-GLOBAL-01` | #288 | 3 | Non atteste |
| `GRT-CONT-20261014-CHAINFLOW-POC-01` | #301 | 7 | Branche `lab/chainflow-gr302-reconcile-20261017` observee ; filiation formelle non attestee |
| `GRT-CONT-20261016-F1QUEUE-001` | #327 | 0 | Non atteste |

## Continuite actuelle

`GRT-CONT-AUDIT-STABILISATION-20261019-001` : espace documentaire PR #339 ; absent des cinq entrees de la projection consultee. Cela **n'invalide pas** son ancrage documentaire dans la PR et **ne cree pas** de session GACR. Contrat LAB candidat : `LAB_RECONSTRUCTION_CONTRAT_CANDIDAT_20261020.md`. Etat `DOCUMENTARY_CANDIDATE / NOT_ACTIVATED`.

## Branche, registre, statut : distinctions

- Une branche `lab/*` est un objet Git, pas un LAB complet ni un agent.
- L'issue #285 formule une demande Genesis ; elle n'est pas une preuve d'admission ni de permission.
- Recherche de code `GRT-CONT-LAB` sur la branche par defaut : zero resultat, sans garantie d'exhaustivite.
- Le chemin `docs/labs/README.md` n'a pas ete trouve sur main ni sur trois branches echantillonnees ; ce chemin n'est pas une liste canonique prouvee des LAB.
- Aucun `REGISTRY.json` LAB authentifie n'a ete identifie dans cette passe ; ne pas en deduire qu'il n'en existe pas.

## Collision et arbitrage

Ne pas reutiliser les identites Genesis, CHAINFLOW, F1QUEUE, GMC ou les slugs de branches existants. Ne pas lancer `lab-entry.yml` sous le mandat PR #339 : il creerait une nouvelle issue, branche et PR. Avant toute creation, rechercher les vrais objets LAB et leurs etats dans les branches, PR et issues ; rapprocher les sources GACR de session et la gouvernance Control Plane ; demander une decision proprietaire explicite sur le mode de creation et le perimetre.

## NEXT_ACTION

Verifier l'existence de LAB complets et de leurs vrais `REGISTRY.json` via les arbres Git et PR pertinents ; pour chaque candidat, relever identifiants, preuve de creation, HEAD, auteur, statut, issue/PR, liens GACR et limites. Conserver la PR #339 DRAFT et le LAB de reconstruction non active.
