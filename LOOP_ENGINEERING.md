# LOOP_ENGINEERING — Méthode d'exécution continue

```text
DISCOVER
→ BASELINE
→ SELECT
→ IMPACT_ANALYSIS
→ IMPLEMENT_COMPATIBLY
→ VERIFY
→ REGRESSION_CHECK
→ CORRECT_IF_REQUIRED
→ VERIFY_AGAIN
→ PERSIST_STATE
→ COMMIT
→ VERIFY_REMOTE_STATE
→ SELECT_NEXT
```

## Règles

- continuer automatiquement les actions sûres, déterminées, réversibles et vérifiables ;
- ne pas refaire une étape déjà attestée ;
- ne pas inventer une réussite ;
- ne pas contourner un lock, une permission ou un gate ;
- arrêter uniquement sur décision humaine réelle, opération irréversible non autorisée, blocage externe, source indispensable manquante ou absence de nouvelle hypothèse vérifiable ;
- une prochaine action doit être unique, concrète et reprenable.
