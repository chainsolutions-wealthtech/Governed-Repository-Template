# Governed Repository Template

Template générique de gouvernance pour les dépôts de l'organisation `chainsolutions-wealthtech`.

## Objectif

Fournir dès la création d'un dépôt :
- un point d'entrée obligatoire ;
- une gouvernance explicite et machine-readable ;
- une mémoire projet persistante ;
- le Loop Engineering ;
- une discipline de non-régression ;
- une hiérarchie de sources de vérité ;
- un état courant, un historique, un TODO et une prochaine action uniques ;
- un handoff inter-agent ;
- des décisions ADR ;
- une CI de gouvernance ;
- un bootstrap déterministe.

Ce template transporte des **règles et des structures**, jamais l'historique d'un autre projet.

## Première utilisation

Après création d'un dépôt depuis ce template :

```bash
python3 scripts/initialize_governance.py --repository "chainsolutions-wealthtech/mon-projet" --project-name "Mon Projet" --project-type "application" --owner "@owner"
```

Puis compléter `PROJECT_CONTEXT.md`, `docs/ARCHITECTURE.md`, `ACCEPTANCE_CRITERIA.md` et `NEXT_ACTION.md`.

Le dépôt créé devient sa propre source de vérité. Le template ne doit jamais injecter une décision métier, une source réglementaire, un statut de production ou un historique appartenant à un autre projet.
