# GOVERNANCE — Contrat supérieur du dépôt

> Dépôt : `{{REPOSITORY}}`  
> Projet : `{{PROJECT_NAME}}`  
> Propriétaire : `{{OWNER}}`

## Contrat

```text
CANONICAL_WORK_BRANCH = {{CANONICAL_BRANCH}}
FORCE_PUSH = FORBIDDEN
HISTORY_REWRITE = FORBIDDEN
IMPROVEMENT_ONLY = REQUIRED
ZERO_REGRESSION = REQUIRED
PERSISTENT_MEMORY = REQUIRED
LOOP_ENGINEERING = REQUIRED
READ_EXISTING_BEFORE_CREATE = REQUIRED
DOCUMENT_ROLE_ANALYSIS = REQUIRED
DELETE_WITHOUT_PROOF = FORBIDDEN
SIMPLIFY_WITH_INFORMATION_LOSS = FORBIDDEN
VERIFY_BEFORE_WRITE = REQUIRED
VERIFY_AFTER_WRITE = REQUIRED
NEW_BRANCH_CREATION = OWNER_EXPLICIT_ONLY
NORMAL_WORK_PR = PROJECT_DEFINED
```

## Autorité

En cas de contradiction :
1. sécurité, loi, politique supérieure et autorisation explicite ;
2. `SOURCE_OF_TRUTH.md` ;
3. décision durable la plus récente dans `docs/DECISIONS.md` / `docs/adr/` ;
4. règle la plus restrictive compatible avec les autorités supérieures ;
5. ne jamais trancher silencieusement une contradiction structurante.

## Amélioration sans régression

Une modification valide doit améliorer, corriger, renforcer, compléter, sécuriser, documenter ou rendre plus vérifiable l'existant.

Interdictions : réécrire l'histoire, forcer un push, remplacer silencieusement une décision, casser un contrat sans migration, supprimer un test pour faire passer une modification, inventer une validation, supprimer une information utile ou créer une source de vérité concurrente.

## Mémoire persistante

La mémoire du projet est versionnée dans le dépôt. Une conversation, un agent ou une session ne remplace jamais cette mémoire.

## États

`SPECIFIED → IMPLEMENTED → TESTED → CONFIGURED → ACTIVATED → DEPLOYED → PRODUCTION_VERIFIED`

Aucune étape ultérieure ne doit être déduite d'une étape antérieure sans preuve.

## Opérations sensibles

Toute opération irréversible, destructive, financière, réglementaire, juridique, de production, de secret, de permission élevée ou d'infrastructure critique exige l'autorité correspondante et les contrôles adaptés. Le template ne confère jamais cette autorisation.
